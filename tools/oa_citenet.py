#!/usr/bin/env python3
"""
oa_citenet.py —— 用 OpenAlex 建多层参考文献网络，找核心文献和跨领域桥梁论文。

流程：
  种子（DOI / arXiv ID / OpenAlex ID / 标题）
  -> 第 1 层：种子的参考文献
  -> 第 2 层：第 1 层的参考文献（剪枝）
  -> 第 3 层（可选，剪枝更狠）
  -> networkx 有向图（施引 -> 被引）：入度、PageRank、介数、Louvain 社区
  -> 每层主题/关键词分布、领域 x 领域引用矩阵、跨领域枢纽论文
  -> pyvis 交互 HTML、VOSviewer JSON、GEXF（Gephi）、CSV

注意：OpenAlex 自 2026-02-13 起要求 API key（免费）。不带 key 每天只有 $0.10 额度，
带 key 是 $1/天。按 ID 单篇查询免费；批量过滤每 1000 次调用 $0.10，每次最多 100 条，
所以本脚本一律用 100 个 ID 一批的过滤查询，3 层几千篇的图花费通常不到 $0.01。
key 获取：https://openalex.org/settings/api ，设置环境变量 OPENALEX_API_KEY。

用法示例：
  python tools/oa_citenet.py --seeds 10.1109/CVPR52734.2025.00499 arXiv:2412.14171 \
      --depth 2 --out out_spatial
  python tools/oa_citenet.py --seeds-file seeds.txt --depth 3 --keep 300 120 --s2-fallback
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import math
import os
import re
import sys
import time
from pathlib import Path

import networkx as nx

OA_BASE = "https://api.openalex.org"
S2_BASE = "https://api.semanticscholar.org/graph/v1"
SELECT = ("id,doi,title,display_name,publication_year,cited_by_count,"
          "referenced_works,primary_topic,topics,keywords,concepts,type")


# ---------------------------------------------------------------- 工具函数
def short_id(x: str | None) -> str | None:
    """'https://openalex.org/W123' -> 'W123'"""
    if not x:
        return None
    return x.rstrip("/").split("/")[-1]


def norm_doi(s: str) -> str:
    s = s.strip()
    s = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:)", "", s, flags=re.I)
    return s.lower()


def classify_seed(s: str) -> tuple[str, str]:
    s = s.strip()
    if re.fullmatch(r"W\d+", s, flags=re.I) or "openalex.org/W" in s:
        return "openalex", short_id(s).upper()
    m = re.match(r"^(arxiv:|https?://arxiv\.org/abs/)(\d{4}\.\d{4,5})(v\d+)?$", s, flags=re.I)
    if m:
        return "doi", f"10.48550/arxiv.{m.group(2)}"
    if re.match(r"^(https?://(dx\.)?doi\.org/|doi:)?10\.\d{4,9}/\S+$", s, flags=re.I):
        return "doi", norm_doi(s)
    return "title", s


# ---------------------------------------------------------------- OpenAlex 客户端
class OpenAlexClient:
    def __init__(self, api_key: str | None, cache_dir: Path, sleep: float = 0.12):
        import requests  # 延迟导入，方便离线测试
        self.requests = requests
        self.session = requests.Session()
        self.api_key = api_key
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.sleep = sleep
        self.cost_usd = 0.0
        self.calls = 0

    def _get(self, path: str, params: dict | None = None) -> dict:
        params = dict(params or {})
        key = hashlib.md5((path + json.dumps(params, sort_keys=True)).encode()).hexdigest()
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            return json.loads(cache_file.read_text(encoding="utf-8"))
        if self.api_key:
            params["api_key"] = self.api_key
        for attempt in range(8):
            try:
                r = self.session.get(OA_BASE + path, params=params, timeout=60)
            except self.requests.exceptions.RequestException as e:
                # 代理/VPN 断开、超时等网络错误：等一会儿重试；报错信息里不带 URL，避免泄露 key
                wait = min(2 ** attempt, 60)
                print(f"[网络] {type(e).__name__}，{wait} 秒后重试（第 {attempt + 1}/8 次）")
                time.sleep(wait)
                continue
            if r.status_code == 200:
                data = r.json()
                self.calls += 1
                self.cost_usd += float((data.get("meta") or {}).get("cost_usd") or 0)
                cache_file.write_text(json.dumps(data), encoding="utf-8")
                time.sleep(self.sleep)
                return data
            if r.status_code == 404:
                return {}
            if r.status_code in (429, 500, 502, 503, 504):
                remaining = r.headers.get("X-RateLimit-Remaining")
                if r.status_code == 429 and remaining is not None and float(remaining) <= 0:
                    sys.exit("OpenAlex 今日额度已用完（429）。设置 OPENALEX_API_KEY 或明天再跑；已抓数据都在缓存里。")
                time.sleep(2 ** attempt)
                continue
            sys.exit(f"OpenAlex 返回 HTTP {r.status_code}（{path}）。已抓数据都在缓存里，可直接重跑。")
        sys.exit(f"OpenAlex 连续 8 次请求失败（{path}），请检查网络或代理。已抓数据都在缓存里，重跑会接着往下走。")

    def get_one(self, kind: str, value: str) -> dict | None:
        if kind == "openalex":
            d = self._get(f"/works/{value}", {"select": SELECT})
        elif kind == "doi":
            d = self._get(f"/works/doi:{value}", {"select": SELECT})
        else:  # 标题：search 计费 $0.001/次
            res = self._get("/works", {"search": value, "per_page": 1, "select": SELECT})
            d = (res.get("results") or [None])[0]
        return d or None

    def get_many(self, ids: list[str]) -> list[dict]:
        out = []
        for i in range(0, len(ids), 100):
            chunk = ids[i:i + 100]
            res = self._get("/works", {"filter": "openalex:" + "|".join(chunk),
                                       "per_page": 100, "select": SELECT})
            out.extend(res.get("results") or [])
        return out

    def get_many_by_doi(self, dois: list[str]) -> list[dict]:
        out = []
        for i in range(0, len(dois), 50):  # DOI 较长，50 一批避免 URL 过长
            chunk = dois[i:i + 50]
            res = self._get("/works", {"filter": "doi:" + "|".join(chunk),
                                       "per_page": 100, "select": SELECT})
            out.extend(res.get("results") or [])
        return out


def s2_reference_dois(doi_or_arxiv: str, api_key: str | None, requests_mod) -> list[str]:
    """OpenAlex 参考文献为空时（常见于 arXiv 预印本），用 Semantic Scholar 补。"""
    pid = f"DOI:{doi_or_arxiv}"
    m = re.match(r"10\.48550/arxiv\.(.+)", doi_or_arxiv)
    if m:
        pid = f"ARXIV:{m.group(1)}"
    headers = {"x-api-key": api_key} if api_key else {}
    dois, offset = [], 0
    while True:
        for attempt in range(5):
            r = requests_mod.get(f"{S2_BASE}/paper/{pid}/references",
                                 params={"fields": "externalIds", "limit": 1000, "offset": offset},
                                 headers=headers, timeout=60)
            if r.status_code == 429:
                time.sleep(2 ** attempt + 1)
                continue
            break
        if r.status_code != 200:
            return dois
        js = r.json()
        for item in js.get("data") or []:
            ext = (item.get("citedPaper") or {}).get("externalIds") or {}
            if ext.get("DOI"):
                dois.append(norm_doi(ext["DOI"]))
            elif ext.get("ArXiv"):
                dois.append(f"10.48550/arxiv.{ext['ArXiv']}".lower())
        if js.get("next") is None:
            return dois
        offset = js["next"]
        time.sleep(1.1)


# ---------------------------------------------------------------- 元数据整理
def slim(w: dict, layer: int) -> dict:
    pt = w.get("primary_topic") or {}
    return {
        "id": short_id(w.get("id")),
        "doi": w.get("doi"),
        "title": w.get("display_name") or w.get("title") or "",
        "year": w.get("publication_year"),
        "cited_by_count": w.get("cited_by_count") or 0,
        "type": w.get("type"),
        "layer": layer,
        "refs": [short_id(x) for x in (w.get("referenced_works") or [])],
        "topic": pt.get("display_name"),
        "subfield": (pt.get("subfield") or {}).get("display_name"),
        "field": (pt.get("field") or {}).get("display_name"),
        "domain": (pt.get("domain") or {}).get("display_name"),
        "topics": [t.get("display_name") for t in (w.get("topics") or [])],
        "keywords": [k.get("display_name") for k in (w.get("keywords") or [])],
        "concepts": [c.get("display_name") for c in (w.get("concepts") or [])
                     if (c.get("level") or 0) >= 1 and (c.get("score") or 0) >= 0.3],
    }


# ---------------------------------------------------------------- 分层扩展 + 剪枝
def expand(client, seeds: list[str], depth: int, keep: list[int], per_parent: int,
           min_cites: int, relevance: float, s2_fallback: bool, s2_key: str | None,
           log=print, seed_groups: list[str] | None = None) -> dict[str, dict]:
    nodes: dict[str, dict] = {}
    seed_groups = seed_groups or ["default"] * len(seeds)

    # 第 0 层：种子
    for s, grp in zip(seeds, seed_groups):
        kind, val = classify_seed(s)
        w = client.get_one(kind, val)
        if not w:
            log(f"[警告] 找不到种子：{s}")
            continue
        n = slim(w, 0)
        if not n["refs"] and s2_fallback and n["doi"]:
            dois = s2_reference_dois(norm_doi(n["doi"]), s2_key, client.requests)
            found = client.get_many_by_doi(dois) if dois else []
            n["refs"] = [short_id(x["id"]) for x in found]
            log(f"[S2 补参考文献] {n['title'][:60]}… -> {len(n['refs'])} 篇")
        n["seed_group"] = grp
        nodes[n["id"]] = n
        log(f"[种子] {n['id']} {n['year']} {n['title'][:70]}  refs={len(n['refs'])}  field={n['field']}")

    seed_subfields = collections.Counter(n["subfield"] for n in nodes.values() if n["subfield"])
    seed_topics = set(t for n in nodes.values() for t in n["topics"])
    frontier = list(nodes)

    for layer in range(1, depth + 1):
        cap = keep[min(layer - 1, len(keep) - 1)]
        # 统计候选：被本层 frontier 引用几次（局部共引）
        local = collections.Counter()
        parents = collections.defaultdict(list)
        for pid in frontier:
            for r in nodes[pid]["refs"]:
                if r and r not in nodes:
                    local[r] += 1
                    parents[r].append(pid)
        if not local:
            break
        # 第 1 层通常不大，全取元数据；更深层先按局部共引次数预筛，控制请求量
        cand_ids = [c for c, _ in local.most_common(max(cap * 6, 600))] if layer > 1 else list(local)
        metas = {short_id(w["id"]): slim(w, layer) for w in client.get_many(cand_ids)}

        def score(cid: str) -> float:
            m = metas[cid]
            s = math.log1p(local[cid]) * 2.0 + math.log1p(m["cited_by_count"]) * 0.5
            if relevance and seed_topics:
                overlap = len(seed_topics & set(m["topics"])) / max(1, len(m["topics"]))
                s += relevance * (overlap + (0.5 if m["subfield"] in seed_subfields else 0))
            return s

        ok = [c for c in metas if metas[c]["cited_by_count"] >= min_cites or local[c] >= 2]
        ranked = sorted(ok, key=score, reverse=True)
        chosen = set(ranked[:cap])
        # 每个父节点保底保留 per_parent 篇，防止某个小领域被整体剪掉
        by_parent = collections.defaultdict(list)
        for c in ok:
            for p in parents[c]:
                by_parent[p].append(c)
        for p, cs in by_parent.items():
            for c in sorted(cs, key=score, reverse=True)[:per_parent]:
                chosen.add(c)
        for c in chosen:
            n = metas[c]
            n["local_cocited"] = local[c]
            nodes[c] = n
        log(f"[第 {layer} 层] 候选 {len(local)} 篇，取元数据 {len(metas)}，保留 {len(chosen)}")
        frontier = list(chosen)
    return nodes


# ---------------------------------------------------------------- 图与指标
def build_graph(nodes: dict[str, dict]) -> nx.DiGraph:
    G = nx.DiGraph()
    for nid, n in nodes.items():
        G.add_node(nid, **{k: v for k, v in n.items() if k != "refs"})
    for nid, n in nodes.items():
        for r in n["refs"]:
            if r in nodes and r != nid:
                G.add_edge(nid, r)  # 施引 -> 被引
    return G


def analyze(G: nx.DiGraph) -> dict:
    pr = nx.pagerank(G, alpha=0.85) if G.number_of_edges() else {n: 0 for n in G}
    UG = G.to_undirected()
    k = min(500, G.number_of_nodes())
    btw = nx.betweenness_centrality(UG, k=k, seed=42) if k > 2 else {n: 0 for n in G}
    comms = nx.community.louvain_communities(UG, seed=42) if G.number_of_edges() else [set(G)]
    comm_of = {n: i + 1 for i, c in enumerate(sorted(comms, key=len, reverse=True)) for n in c}
    for n in G:
        citing_fields = {G.nodes[u].get("field") for u in G.predecessors(n)} - {None}
        G.nodes[n].update(
            in_degree=G.in_degree(n), out_degree=G.out_degree(n),
            pagerank=pr.get(n, 0), betweenness=btw.get(n, 0),
            community=comm_of.get(n, 0), n_citing_fields=len(citing_fields),
            citing_fields="; ".join(sorted(citing_fields)),
        )
    return {"pagerank": pr, "betweenness": btw, "communities": comms}


def group_reach(G: nx.DiGraph) -> list[str]:
    """给每篇论文算"方向画像"：直接引用它的论文各属于哪个方向，取平均。

    种子是独热向量；第 L 层论文的画像 = 引用它的上一层论文画像的平均。
    这样 ResNet 这类被各方向都引用的论文画像会很"混"，而某方向独有的文献画像很"纯"。
    """
    groups = sorted({d.get("seed_group") or "default" for _, d in G.nodes(data=True) if d["layer"] == 0})
    gi = {g: i for i, g in enumerate(groups)}
    prof: dict[str, list[float]] = {}
    for n in sorted(G, key=lambda x: G.nodes[x]["layer"]):
        d = G.nodes[n]
        if d["layer"] == 0:
            v = [0.0] * len(groups)
            v[gi[d.get("seed_group") or "default"]] = 1.0
        else:
            preds = [p for p in G.predecessors(n) if G.nodes[p]["layer"] < d["layer"] and p in prof]
            preds = preds or [p for p in G.predecessors(n) if p in prof]
            v = [sum(prof[p][k] for p in preds) / max(len(preds), 1) for k in range(len(groups))]
        prof[n] = v
        # 第 1 层：被哪些方向的种子"直接"引用（最可靠的方向信号）
        direct = sorted({G.nodes[p].get("seed_group") or "default"
                         for p in G.predecessors(n) if G.nodes[p]["layer"] == 0})
        d["direct_seed_groups"] = "; ".join(direct)
        d["n_direct_groups"] = len(direct)
        shares = {g: v[gi[g]] for g in groups}
        d["group_profile"] = "; ".join(f"{g} {s:.0%}" for g, s in sorted(shares.items(), key=lambda x: -x[1]) if s >= 0.05)
        main = [g for g, s in shares.items() if s >= 0.15]
        d["groups"] = "; ".join(sorted(main))
        d["n_groups"] = len(main)
        ent = -sum(s * math.log(s) for s in v if s > 0)
        d["balance"] = round(ent / math.log(len(groups)), 3) if len(groups) > 1 else 0.0
        # 特异性：图内被引 / sqrt(全库被引)。ResNet 全库 23 万次，会被明显压下去
        d["specificity"] = round(d.get("in_degree", 0) / math.sqrt((d.get("cited_by_count") or 0) + 1), 3)
        d["bridge_score"] = round(d["balance"] * d["specificity"], 3)
        d["_prof"] = v
    return groups


def group_pairs(G: nx.DiGraph, groups: list[str], top: int = 8) -> list[dict]:
    rows = []
    gi = {g: i for i, g in enumerate(groups)}
    for i, a in enumerate(groups):
        for b in groups[i + 1:]:
            scored = []
            affinity = 0.0
            for n, d in G.nodes(data=True):
                if d["layer"] == 0:
                    continue
                m = min(d["_prof"][gi[a]], d["_prof"][gi[b]])
                affinity += m
                if m >= 0.15 and d["in_degree"] >= 2:
                    scored.append((m * d["specificity"], n))
            scored.sort(reverse=True)
            direct = [n for n, d in G.nodes(data=True)
                      if a in d.get("direct_seed_groups", "").split("; ")
                      and b in d.get("direct_seed_groups", "").split("; ")]
            rows.append({"group_a": a, "group_b": b,
                         "affinity": round(affinity, 1),
                         "n_direct_shared": len(direct),
                         "direct_shared": " | ".join(f"{G.nodes[n]['title'][:70]} ({G.nodes[n].get('year')})"
                                                     for n in direct),
                         "top_shared": " | ".join(f"{G.nodes[n]['title'][:70]} ({G.nodes[n].get('year')})"
                                                  for _, n in scored[:top])})
    return rows


def layer_stats(G: nx.DiGraph, top: int = 15) -> list[dict]:
    rows = []
    layers = sorted({d["layer"] for _, d in G.nodes(data=True)})
    for L in layers:
        ns = [d for _, d in G.nodes(data=True) if d["layer"] == L]
        for facet in ("field", "subfield", "topic"):
            c = collections.Counter(d.get(facet) for d in ns if d.get(facet))
            for name, cnt in c.most_common(top):
                rows.append({"layer": L, "facet": facet, "name": name, "count": cnt,
                             "share": round(cnt / len(ns), 3)})
        for facet in ("keywords", "concepts"):
            c = collections.Counter(x for d in ns for x in d.get(facet, []))
            for name, cnt in c.most_common(top):
                rows.append({"layer": L, "facet": facet, "name": name, "count": cnt,
                             "share": round(cnt / len(ns), 3)})
    return rows


def field_matrix(G: nx.DiGraph, level: str = "field") -> tuple[list[str], dict]:
    m = collections.Counter()
    for u, v in G.edges():
        a, b = G.nodes[u].get(level) or "Unknown", G.nodes[v].get(level) or "Unknown"
        m[(a, b)] += 1
    names = sorted({a for a, _ in m} | {b for _, b in m})
    return names, m


# ---------------------------------------------------------------- 导出
def write_csv(path: Path, rows: list[dict], fields: list[str]):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:  # utf-8-sig 让 Excel 正常显示中文
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


PALETTE = ["#4269d0", "#efb118", "#ff725c", "#6cc5b0", "#3ca951", "#ff8ab7",
           "#a463f2", "#97bbf5", "#9c6b4e", "#9498a0"]


def export_pyvis(G: nx.DiGraph, path: Path, max_nodes: int, color_by: str):
    from pyvis.network import Network
    keepn = sorted(G, key=lambda n: G.nodes[n]["pagerank"], reverse=True)[:max_nodes]
    H = G.subgraph(set(keepn) | {n for n in G if G.nodes[n]["layer"] == 0})
    groups = collections.Counter(H.nodes[n].get(color_by) for n in H)
    color = {g: PALETTE[i % len(PALETTE)] for i, (g, _) in enumerate(groups.most_common())}
    prs = [H.nodes[n]["pagerank"] for n in H] or [1]
    lo, hi = min(prs), max(prs) or 1
    net = Network(height="900px", width="100%", directed=True, bgcolor="#ffffff",
                  cdn_resources="in_line", select_menu=False, filter_menu=False)
    # 预先算布局并关闭物理模拟：几百个节点时浏览器打开即显示，不会卡在稳定过程
    pos = nx.spring_layout(H.to_undirected(), seed=42, iterations=150,
                           k=1.5 / math.sqrt(max(len(H), 1)))
    for n in H:
        d = H.nodes[n]
        size = 8 + 32 * ((d["pagerank"] - lo) / (hi - lo + 1e-12)) ** 0.5
        title = (f"{d['title']}\n{d.get('year')} | 第{d['layer']}层 | 被引 {d['cited_by_count']}\n"
                 f"入度 {d['in_degree']} | PageRank {d['pagerank']:.4f}\n"
                 f"领域 {d.get('field')} / {d.get('subfield')}\n"
                 f"被 {d['n_citing_fields']} 个领域引用：{d['citing_fields']}")
        label = (d["title"][:28] + "…") if d["in_degree"] >= 3 or d["layer"] == 0 else " "
        net.add_node(n, label=label, title=title, size=size,
                     color=color.get(d.get(color_by), "#9498a0"),
                     shape="star" if d["layer"] == 0 else "dot",
                     group=str(d.get(color_by)),
                     x=float(pos[n][0]) * 1200, y=float(pos[n][1]) * 1200, physics=False)
    for u, v in H.edges():
        net.add_edge(u, v, color="rgba(150,150,150,0.25)", arrows="to", width=0.5)
    net.toggle_physics(False)
    # 不用 net.save_graph：它在 Windows 上按 GBK 写文件，遇到 © 等字符会报 UnicodeEncodeError
    path.write_text(net.generate_html(), encoding="utf-8")
    # 在页面左上角加图例：颜色 = 分组，星形 = 种子，大小 = PageRank
    legend = "".join(f'<div><span style="display:inline-block;width:10px;height:10px;'
                     f'border-radius:50%;background:{c};margin-right:6px"></span>{g}</div>'
                     for g, c in color.items())
    box = (f'<div style="position:fixed;top:10px;left:10px;z-index:9;background:rgba(255,255,255,.92);'
           f'padding:8px 10px;border:1px solid #ddd;border-radius:6px;font:12px sans-serif;max-width:320px">'
           f'<b>颜色：{color_by}</b>{legend}<div style="margin-top:4px;color:#666">'
           f'星形 = 种子；节点大小 = PageRank；悬停看详情</div></div>')
    html = path.read_text(encoding="utf-8").replace("<body>", "<body>" + box, 1)
    path.write_text(html, encoding="utf-8")


def export_vosviewer(G: nx.DiGraph, path: Path):
    pos = nx.spring_layout(G.to_undirected(), seed=42, iterations=200) if len(G) else {}
    fields = sorted({G.nodes[n].get("field") or "Unknown" for n in G})
    items = []
    for i, n in enumerate(G):
        d = G.nodes[n]
        items.append({
            "id": n,
            "label": (d["title"][:60] or n),
            "description": f"{d.get('year')} · {d.get('field')} / {d.get('subfield')} · 第{d['layer']}层",
            "url": f"https://openalex.org/{n}",
            "x": round(float(pos[n][0]) * 10, 4), "y": round(float(pos[n][1]) * 10, 4),
            "cluster": min(int(d["community"]) or 1, 1000),
            "weights": {"Citations (in graph)": d["in_degree"],
                        "Citations (OpenAlex)": d["cited_by_count"]},
            "scores": {"Year": d.get("year") or 0, "PageRank x1000": round(d["pagerank"] * 1000, 4),
                       "Layer": d["layer"], "Citing fields": d["n_citing_fields"]},
        })
    links = [{"source_id": u, "target_id": v, "strength": 1} for u, v in G.edges()]
    path.write_text(json.dumps({"network": {"items": items, "links": links}},
                               ensure_ascii=False, indent=1), encoding="utf-8")


def export_gexf(G: nx.DiGraph, path: Path):
    H = nx.DiGraph()
    for n, d in G.nodes(data=True):
        H.add_node(n, **{k: ("; ".join(v) if isinstance(v, list) else ("" if v is None else v))
                         for k, v in d.items()})
    H.add_edges_from(G.edges())
    nx.write_gexf(H, str(path))


# ---------------------------------------------------------------- 主程序
def run(args, client=None, log=print) -> dict:
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    seeds = list(args.seeds or [])
    seed_groups = ["cli"] * len(seeds)
    if args.seeds_file:
        # 分组写法：单独一行 [空间智能]，或 # —— 空间智能 ——；其后的种子都归入这个方向
        cur = "default"
        for l in Path(args.seeds_file).read_text(encoding="utf-8-sig").splitlines():
            l = l.strip()
            m = re.match(r"^\[(.+)\]$", l) or re.match(r"^#\s*[—-]+\s*(.+?)\s*[—-]+\s*$", l)
            if m:
                cur = m.group(1).strip()
            elif l and not l.startswith("#"):
                seeds.append(l)
                seed_groups.append(cur)
    if not seeds:
        sys.exit("没有种子。用 --seeds 或 --seeds-file。")
    if client is None:
        key = os.environ.get("OPENALEX_API_KEY")
        if not key:
            log("[提示] 未设置 OPENALEX_API_KEY，只有每天 $0.10 的免费额度，小图够用，大图会 429。")
        client = OpenAlexClient(key, out / "cache")

    nodes = expand(client, seeds, args.depth, args.keep, args.per_parent, args.min_cites,
                   args.relevance, args.s2_fallback, os.environ.get("S2_API_KEY"), log,
                   seed_groups=seed_groups)
    G = build_graph(nodes)
    analyze(G)
    groups = group_reach(G)
    log(f"[图] {G.number_of_nodes()} 个节点，{G.number_of_edges()} 条边，方向：{', '.join(groups)}")

    pairs = group_pairs(G, groups)
    for n in G:  # 方向画像转成可读字段后，去掉内部向量
        v = G.nodes[n].pop("_prof")
        G.nodes[n]["main_group"] = groups[max(range(len(v)), key=lambda k: v[k])] if any(v) else "unknown"

    cols = ["id", "layer", "year", "title", "doi", "cited_by_count", "in_degree", "out_degree",
            "pagerank", "specificity", "bridge_score", "balance", "group_profile", "main_group",
            "direct_seed_groups", "n_direct_groups", "groups", "n_groups", "seed_group",
            "betweenness", "community", "domain", "field", "subfield", "topic",
            "n_citing_fields", "citing_fields"]
    rows = [{**G.nodes[n], "id": n} for n in G]
    write_csv(out / "nodes.csv", rows, cols)
    write_csv(out / "edges.csv", [{"source": u, "target": v} for u, v in G.edges()],
              ["source", "target"])
    core = sorted((r for r in rows if r["layer"] > 0),
                  key=lambda r: (r["in_degree"], r["pagerank"]), reverse=True)[:args.top]
    write_csv(out / "core_papers.csv", core, cols)
    bridges = sorted((r for r in rows if r["n_citing_fields"] >= 2),
                     key=lambda r: (r["n_citing_fields"], r["betweenness"]), reverse=True)[:args.top]
    write_csv(out / "bridge_papers.csv", bridges, cols)
    # 方向之间的桥：方向画像均衡（balance 高）× 特异性高（不是万能经典）
    gbridges = sorted((r for r in rows if r["layer"] > 0 and r["n_groups"] >= 2 and r["in_degree"] >= 3),
                      key=lambda r: r["bridge_score"], reverse=True)[:args.top]
    write_csv(out / "group_bridges.csv", gbridges, cols)
    # 直接共引：被 ≥2 个方向的种子"直接"引用的文献，最可信的桥
    direct = sorted((r for r in rows if r.get("n_direct_groups", 0) >= 2),
                    key=lambda r: (r["n_direct_groups"], r["specificity"]), reverse=True)
    write_csv(out / "direct_shared.csv", direct, cols)
    specific = sorted((r for r in rows if r["layer"] > 0 and r["in_degree"] >= 3),
                      key=lambda r: r["specificity"], reverse=True)[:args.top]
    write_csv(out / "core_specific.csv", specific, cols)
    write_csv(out / "group_pairs.csv", pairs,
              ["group_a", "group_b", "affinity", "n_direct_shared", "direct_shared", "top_shared"])
    write_csv(out / "layer_topics.csv", layer_stats(G), ["layer", "facet", "name", "count", "share"])
    names, m = field_matrix(G, args.matrix_level)
    with open(out / "field_matrix.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow([f"施引 \\ 被引 ({args.matrix_level})"] + names)
        for a in names:
            w.writerow([a] + [m.get((a, b), 0) for b in names])

    export_pyvis(G, out / "graph.html", args.html_max, args.color_by)
    export_vosviewer(G, out / "vosviewer.json")
    export_gexf(G, out / "graph.gexf")
    with open(out / "openalex_ids.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(G.nodes))

    summary = {"nodes": G.number_of_nodes(), "edges": G.number_of_edges(),
               "api_calls": getattr(client, "calls", None),
               "cost_usd": round(getattr(client, "cost_usd", 0.0), 5),
               "top_core": [(r["id"], r["title"][:60], r["in_degree"]) for r in core[:10]],
               "top_bridges": [(r["id"], r["title"][:60], r["citing_fields"]) for r in bridges[:10]]}
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    log("\n核心文献（图内被引最多）：")
    for r in core[:10]:
        log(f"  {r['in_degree']:>4}  {r['year']}  {r['title'][:70]}")
    log("\n去掉万能经典后的核心文献（图内被引 / √全库被引）：")
    for r in specific[:10]:
        log(f"  {r['specificity']:>6}  图内{r['in_degree']:>3} / 全库{r['cited_by_count']:>6}  {r['year']}  "
            f"{r['title'][:55]}  [{r['group_profile']}]")
    log("\n直接共引（被 ≥2 个方向的种子直接引用）：")
    for r in direct[:15]:
        log(f"  {r['year']}  {r['title'][:60]}  [{r['direct_seed_groups']}]")
    log("\n方向之间的桥（画像均衡 × 特异性）：")
    for r in gbridges[:12]:
        log(f"  {r['bridge_score']:>6}  {r['year']}  {r['title'][:55]}  [{r['group_profile']}]")
    log("\n方向两两关联：")
    for p in pairs:
        log(f"  {p['group_a']} × {p['group_b']}: 关联度 {p['affinity']}，直接共引 {p['n_direct_shared']} 篇")
    log(f"\n输出目录：{out.resolve()}  |  API 调用 {summary['api_calls']} 次，约 ${summary['cost_usd']}")
    return summary


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="OpenAlex 多层参考文献网络")
    p.add_argument("--seeds", nargs="*", help="DOI / arXiv:xxxx.xxxxx / W123 / 标题（标题要加引号）")
    p.add_argument("--seeds-file", help="每行一个种子，# 开头为注释")
    p.add_argument("--depth", type=int, default=2, choices=[1, 2, 3])
    p.add_argument("--keep", type=int, nargs="+", default=[400, 300, 150],
                   help="每层最多保留的节点数，例如 --keep 400 300 150")
    p.add_argument("--per-parent", type=int, default=3, help="每篇父论文至少保留几篇参考文献")
    p.add_argument("--min-cites", type=int, default=5, help="只被引用一次的候选，其 OpenAlex 被引数下限")
    p.add_argument("--relevance", type=float, default=1.0, help="与种子主题重合度的剪枝权重，0 关闭")
    p.add_argument("--s2-fallback", action="store_true", help="种子无参考文献时用 Semantic Scholar 补")
    p.add_argument("--top", type=int, default=50)
    p.add_argument("--html-max", type=int, default=400, help="HTML 图最多画多少个节点（按 PageRank）")
    p.add_argument("--color-by", default="main_group", choices=["main_group", "groups", "field", "subfield", "domain", "community", "layer"])
    p.add_argument("--matrix-level", default="field", choices=["domain", "field", "subfield"])
    p.add_argument("--out", default="citenet_out")
    return p.parse_args(argv)


if __name__ == "__main__":
    run(parse_args())
