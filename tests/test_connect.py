"""离线测试 oa_connect：在 MockClient 上加一个处理 cites: 过滤的 _get。"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import oa_citenet as oc
import oa_connect as conn
from test_mock import MockClient


class MockClient2(MockClient):
    def __init__(self):
        super().__init__(n=3000, seed=1)
        self.citers = {}
        for wid, w in self.db.items():
            for r in w["referenced_works"]:
                self.citers.setdefault(oc.short_id(r), []).append(wid)
        # 造几篇"万能经典"
        for wid in ["W100000", "W100001", "W100003"]:
            self.db[wid]["cited_by_count"] = 50000

    def _get(self, path, params):
        self.calls += 1
        f = params["filter"]
        wid = f.split(":")[1]
        rs = sorted((self.db[c] for c in self.citers.get(wid, [])), key=lambda w: -w["cited_by_count"])
        page = params.get("page", 1)
        return {"results": rs[(page - 1) * 100: page * 100]}


if __name__ == "__main__":
    out = sys.argv[1]
    paths, paths2 = conn.run(["W102999", "W100500", "--out", out, "--frontier-cap", "60"], client=MockClient2())
    assert paths, "no path"
    assert (Path(out) / "paths.html").exists() and (Path(out) / "paths.csv").exists()
    print("OK", len(paths[0]) - 1, "hops")
