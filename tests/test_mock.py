"""离线测试：用合成数据替代 OpenAlex，跑通 oa_citenet 全流程。"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import oa_citenet as oc

FIELDS = {
    "Computer Science": ["Computer Vision and Pattern Recognition", "Artificial Intelligence"],
    "Engineering": ["Control and Systems Engineering", "Aerospace Engineering"],
    "Earth and Planetary Sciences": ["Earth-Surface Processes"],
}
KW = ["spatial reasoning", "multi-robot", "UAV", "SLAM", "remote sensing", "reinforcement learning",
      "visual servoing", "geo-localization", "VLA", "3D reconstruction"]


class MockClient:
    calls = 0
    cost_usd = 0.0

    def __init__(self, n=3000, seed=0):
        rnd = random.Random(seed)
        self.db = {}
        ids = [f"W{100000 + i}" for i in range(n)]
        for i, wid in enumerate(ids):
            field = rnd.choice(list(FIELDS))
            sub = rnd.choice(FIELDS[field])
            year = 1990 + i * 36 // n
            older = ids[:i]
            refs = []
            if older:
                k = rnd.randint(5, 40)
                # 偏好依附：老论文和同领域论文更容易被引
                pool = rnd.sample(older, min(len(older), k * 3))
                pool.sort(key=lambda x: (self.db[x]["_field"] == field) + rnd.random(), reverse=True)
                refs = pool[:k]
            topic = f"{sub} topic {rnd.randint(1, 4)}"
            self.db[wid] = {
                "id": f"https://openalex.org/{wid}", "doi": f"https://doi.org/10.9999/{wid.lower()}",
                "display_name": f"Paper {wid} on {sub}", "publication_year": year,
                "cited_by_count": 0, "type": "article",
                "referenced_works": [f"https://openalex.org/{r}" for r in refs],
                "primary_topic": {"display_name": topic, "subfield": {"display_name": sub},
                                  "field": {"display_name": field},
                                  "domain": {"display_name": "Physical Sciences"}},
                "topics": [{"display_name": topic}],
                "keywords": [{"display_name": k} for k in rnd.sample(KW, 3)],
                "concepts": [{"display_name": sub, "level": 1, "score": 0.6}],
                "_field": field,
            }
        for w in self.db.values():
            for r in w["referenced_works"]:
                self.db[oc.short_id(r)]["cited_by_count"] += 1

    def get_one(self, kind, value):
        self.calls += 1
        if kind == "openalex":
            return self.db.get(value)
        if kind == "doi":
            return next((w for w in self.db.values() if w["doi"].endswith(value)), None)
        return next((w for w in self.db.values() if value.lower() in w["display_name"].lower()), None)

    def get_many(self, ids):
        self.calls += (len(ids) + 99) // 100
        self.cost_usd += 0.0001 * ((len(ids) + 99) // 100)
        return [self.db[i] for i in ids if i in self.db]

    def get_many_by_doi(self, dois):
        return []


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "mock_out")
    client = MockClient()
    out.mkdir(parents=True, exist_ok=True)
    (out / "seeds.txt").write_text("# —— 空间智能 ——\nW102990\n10.9999/w102985\n[遥感]\nPaper W102970\nW102960\n", encoding="utf-8")
    args = oc.parse_args(["--seeds-file", str(out / "seeds.txt"),
                          "--depth", "3", "--keep", "300", "200", "120", "--out", str(out)])
    s = oc.run(args, client=client)
    assert s["nodes"] > 300 and s["edges"] > 500, s
    for f in ["nodes.csv", "edges.csv", "core_papers.csv", "bridge_papers.csv", "layer_topics.csv",
              "field_matrix.csv", "group_bridges.csv", "direct_shared.csv", "group_pairs.csv", "core_specific.csv", "graph.html", "vosviewer.json", "graph.gexf", "summary.json"]:
        assert (out / f).stat().st_size > 0, f
    print("OK")
