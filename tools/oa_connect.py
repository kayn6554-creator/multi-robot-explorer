#!/usr/bin/env python3
"""
oa_connect.py —— 找两篇论文之间的最短引用路径（自制版 Inciteful Literature Connector）。

做法：从 A、B 两端同时扩展，每篇论文的邻居 = 它的参考文献 + 引用它的论文（按被引数取前 N 篇），
两边相遇后列出所有最短路径；再把"万能经典"（全库被引 ≥ --generic-cap）剔掉重找一次。
如果剔掉以后路径明显变长或者断开，说明这两个圈子之间确实缺少专门的桥梁论文。

用法：
  python tools/oa_connect.py arXiv:1807.03051 arXiv:2412.14171 --out conn_A
  python tools/oa_connect.py "University-1652: A Multi-view ..." W4280532325 --out conn_B
费用：每扩展一篇论文约 1–2 次批量调用（$0.0001/次），默认设置下一次连接通常不到 $0.05。
"""
from __future__ import annotations

import argparse
import csv
import math
import os
import sys
from pathlib import Path

import networkx as nx

sys.path.insert(0, str(Path(__file__).resolve().parent))
import oa_citenet as oc


def get_citers(client, wid: str, pages: int) -> list[dict]:
    out = []
    for p in range(1, pages + 1):
        res = client._get("/works", {"filter": f"cites:{wid}", "per_page": 100, "page": p,
                                     "sort": "cited_by_count:desc", "select": oc.SELECT})
        rs = res.get("results") or []
        out.extend(rs)
        if len(rs) < 100:
            break
    return out


class Explorer:
    def __init__(self, client, cite_pages: int, generic_cap: int, log=print):
        self.c, self.cite_pages, self.generic_cap, self.log = client, cite_pages, generic_cap, log
        self.meta: dict[str, dict] = {}
        self.G = nx.DiGraph()  # 施引 -> 被引
        self.expanded: set[str] = set()

    def add_meta(self, works: list[dict]):
        for w in works:
            n = oc.slim(w, -1)
            if n["id"] and n["id"] not in self.meta:
                self.meta[n["id"]] = n
                self.G.add_node(n["id"])

    def expand(self, ids: list[str]) -> set[str]:
        """展开一批论文，返回新发现的邻居。"""
        new = set()
        need_refs = []
        for wid in ids:
            if wid in self.expanded:
                continue
            self.expanded.add(wid)
            for r in self.meta[wid]["refs"]:
                self.G.add_edge(wid, r)
                new.add(r)
                if r not in self.meta:
                    need_refs.append(r)
            citers = get_citers(self.c, wid, self.cite_pages)
            self.add_meta(citers)
            for w in citers:
                cid = oc.short_id(w["id"])
                self.G.add_edge(cid, wid)
                new.add(cid)
        if need_refs:
            self.add_meta(self.c.get_many(sorted(set(need_refs))))
        return {n for n in new if n in self.meta}

    def generic(self, n: str) -> bool:
        return self.meta.get(n, {}).get("cited_by_count", 0) >= self.generic_cap


def connect(client, a: str, b: str, max_hops: int, frontier_cap: int, cite_pages: int,
            generic_cap: int, log=print) -> tuple[Explorer, str, str]:
    ex = Explorer(client, cite_pages, generic_cap, log)
    ends = []
    for s in (a, b):
        kind, val = oc.classify_seed(s)
        w = client.get_one(kind, val)
        if not w:
            sys.exit(f"找不到论文：{s}")
        ex.add_meta([w])
        ends.append(oc.short_id(w["id"]))
        log(f"[端点] {ends[-1]} {w.get('publication_year')} {(w.get('display_name') or '')[:70]}")
    A, B = ends
    dist = {A: {A: 0}, B: {B: 0}}
    frontier = {A: [A], B: [B]}
    for step in range(max_hops):
        U = ex.G.to_undirected()
        if nx.has_path(U, A, B):
            break
        # 先扩展规模较小的一侧；万能经典不展开（它们邻居太多，会把图撑爆）
        side = A if len(frontier[A]) <= len(frontier[B]) else B
        todo = [n for n in frontier[side] if not ex.generic(n)]
        todo.sort(key=lambda n: ex.meta[n]["cited_by_count"], reverse=True)
        todo = todo[:frontier_cap]
        found = ex.expand(todo)
        d0 = step + 1
        nxt = [n for n in found if n not in dist[side]]
        for n in nxt:
            dist[side][n] = d0
        frontier[side] = nxt
        log(f"[扩展] 从{'起点' if side == A else '终点'}一侧展开 {len(todo)} 篇，新发现 {len(nxt)} 篇，"
            f"图中共 {ex.G.number_of_nodes()} 篇")
    return ex, A, B


def rank_paths(ex: Explorer, U: nx.Graph, A: str, B: str, k: int) -> list[list[str]]:
    try:
        paths = list(nx.all_shortest_paths(U, A, B))
    except nx.NetworkXNoPath:
        return []
    # 路径越"专门"越好：中间节点全库被引的对数和越小越好
    paths.sort(key=lambda p: sum(math.log10(ex.meta.get(n, {}).get("cited_by_count", 0) + 10) for n in p[1:-1]))
    return paths[:k]


def describe(ex: Explorer, path: list[str]) -> list[str]:
    lines = []
    for i, n in enumerate(path):
        m = ex.meta.get(n, {})
        arrow = ""
        if i + 1 < len(path):
            nxt = path[i + 1]
            arrow = "  引用→" if ex.G.has_edge(n, nxt) else "  ←被引用"
        tag = " [万能经典]" if ex.generic(n) else ""
        lines.append(f"    {m.get('year')}  {m.get('title', n)[:70]}  (全库被引 {m.get('cited_by_count')}){tag}{arrow}")
    return lines


def run(argv=None, client=None, log=print):
    p = argparse.ArgumentParser(description="两篇论文之间的最短引用路径")
    p.add_argument("a")
    p.add_argument("b")
    p.add_argument("--max-hops", type=int, default=6, help="最多扩展几轮")
    p.add_argument("--frontier-cap", type=int, default=150, help="每轮最多展开几篇")
    p.add_argument("--cite-pages", type=int, default=1, help="每篇论文取几页施引文献（每页 100 篇）")
    p.add_argument("--generic-cap", type=int, default=20000, help="全库被引 ≥ 该值视为万能经典")
    p.add_argument("--top", type=int, default=10)
    p.add_argument("--out", default="connect_out")
    args = p.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    if client is None:
        client = oc.OpenAlexClient(os.environ.get("OPENALEX_API_KEY"), out / "cache")

    ex, A, B = connect(client, args.a, args.b, args.max_hops, args.frontier_cap,
                       args.cite_pages, args.generic_cap, log)
    U = ex.G.to_undirected()
    paths = rank_paths(ex, U, A, B, args.top)
    U2 = U.subgraph([n for n in U if not ex.generic(n) or n in (A, B)])
    paths2 = rank_paths(ex, U2, A, B, args.top)

    report = []
    if paths:
        report.append(f"\n最短路径：{len(paths[0]) - 1} 步，共 {len(list(nx.all_shortest_paths(U, A, B)))} 条，"
                      f"以下按\"越专门越靠前\"列出前 {len(paths)} 条")
        for i, pth in enumerate(paths, 1):
            report.append(f"  路径 {i}:")
            report += describe(ex, pth)
    else:
        report.append("\n在当前扩展范围内没有连通。可加大 --max-hops 或 --frontier-cap。")
    if paths2:
        report.append(f"\n去掉万能经典（全库被引 ≥ {args.generic_cap}）后：最短 {len(paths2[0]) - 1} 步")
        for i, pth in enumerate(paths2[:5], 1):
            report.append(f"  路径 {i}:")
            report += describe(ex, pth)
    else:
        report.append(f"\n去掉万能经典后：在当前范围内不连通 —— 两个圈子之间缺少专门的桥梁论文。")
    for line in report:
        log(line)

    with open(out / "paths.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["set", "path_no", "step", "id", "year", "title", "cited_by_count", "generic"])
        for name, ps in (("all", paths), ("no_generic", paths2)):
            for i, pth in enumerate(ps, 1):
                for j, n in enumerate(pth):
                    m = ex.meta.get(n, {})
                    w.writerow([name, i, j, n, m.get("year"), m.get("title"), m.get("cited_by_count"), ex.generic(n)])
    (out / "report.txt").write_text("\n".join(report), encoding="utf-8")

    # 小图：所有展示路径的并集
    nodes = {n for pth in paths + paths2 for n in pth}
    if nodes:
        H = ex.G.subgraph(nodes).copy()
        for n in H:
            m = ex.meta.get(n, {})
            H.nodes[n].update(title=m.get("title", n), year=m.get("year"), cited_by_count=m.get("cited_by_count", 0),
                              layer=0 if n in (A, B) else 1, pagerank=1 if n in (A, B) else 0.3,
                              in_degree=3, n_citing_fields=0, citing_fields="",
                              kind="端点" if n in (A, B) else ("万能经典" if ex.generic(n) else "桥梁论文"),
                              field=m.get("field"), subfield=m.get("subfield"))
        oc.export_pyvis(H, out / "paths.html", 200, "kind")
    log(f"\n结果：{(out / 'report.txt').resolve()}、paths.csv、paths.html  |  "
        f"API 调用 {getattr(client, 'calls', '?')} 次，约 ${round(getattr(client, 'cost_usd', 0), 4)}")
    return paths, paths2


if __name__ == "__main__":
    run()
