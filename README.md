# Multi-Robot Explorer

多机器人协作方向的一次探索性研究：先用前沿论文 × 科幻 × 游戏发散出猜想，再用 OpenAlex 引用网络量化各研究方向之间的关联、找出空白，最后落到一个课题草案 **Fly Once, Localize All**（现场无人机建模，为异构地面机器人提供共享坐标系）。

仓库里有两部分：可复用的文献网络工具，以及这次探索的报告和结论。

## 目录

```
tools/
  oa_citenet.py      多层参考文献网络：剪枝扩展、PageRank、方向画像、跨方向桥梁论文、导出
  oa_connect.py      两篇论文之间的最短引用路径（自制版 Inciteful Literature Connector）
seeds/
  seeds_example.txt  四个方向、23 篇种子（本次主结果用的）
  seeds_3groups.txt  初版三个方向
tests/               离线测试（合成数据，不联网）
docs/
  01-exploration-report.md        发散报告：协作原语、前沿速写、科幻与游戏镜像、8 条桥接猜想
  02-citation-network-findings.md 引用网络分析结果与最短路径验证
  03-fly-once-proposal.md         课题草案
  board/fly-once-board.html       汇总看板（浏览器直接打开）
```

## 快速开始

```bash
pip install -r requirements.txt
```

OpenAlex 从 2026-02-13 起需要 API key（免费，在 https://openalex.org/settings/api 获取）。不带 key 每天只有 $0.10 额度。

```powershell
# Windows PowerShell
$env:OPENALEX_API_KEY="你的key"
```
```bash
# macOS / Linux
export OPENALEX_API_KEY=你的key
```

### 建引用网络

```bash
python tools/oa_citenet.py --seeds-file seeds/seeds_example.txt --depth 2 --s2-fallback --out out/d2
```

种子文件每行一个，支持 DOI、`arXiv:2412.14171`、OpenAlex `W123…` 或标题；用 `[方向名]` 分组。

常用参数：

| 参数 | 作用 |
| --- | --- |
| `--depth 1/2/3` | 扩展层数 |
| `--keep 400 300 150` | 每层最多保留节点数 |
| `--per-parent 3` | 每篇父论文至少保留几篇参考文献 |
| `--relevance 1.0` | 与种子主题重合度的剪枝权重，0 关闭 |
| `--s2-fallback` | 种子在 OpenAlex 无参考文献时用 Semantic Scholar 补 |
| `--color-by main_group` | HTML 图的着色依据 |

输出（在 `--out` 目录）：

| 文件 | 内容 |
| --- | --- |
| `core_specific.csv` | 去掉万能经典后的核心文献（图内被引 / √全库被引） |
| `direct_shared.csv` | 被 ≥2 个方向的种子直接引用的文献 |
| `group_bridges.csv` | 方向之间的桥（画像均衡 × 特异性） |
| `group_pairs.csv` | 方向两两关联度 |
| `core_papers.csv` / `bridge_papers.csv` | 按入度 / 按 OpenAlex 领域的原始排名 |
| `layer_topics.csv`、`field_matrix.csv` | 每层主题分布、领域 × 领域引用矩阵 |
| `graph.html` | pyvis 交互图 |
| `vosviewer.json`、`graph.gexf` | 给 VOSviewer / Gephi |
| `nodes.csv`、`edges.csv` | 全部节点和边 |

所有请求缓存在 `out/.../cache/`，重跑不重复计费。

### 找两篇论文之间的路径

```bash
python tools/oa_connect.py W2949187488 W4413144646 --out out/conn_A
```

输出最短路径，以及剔除万能经典（全库被引 ≥ `--generic-cap`，默认 20000）后的路径。剔除后路径变长或断开，说明两个圈子之间缺少专门的桥梁论文。

### 测试

```bash
python tests/test_mock.py out/mock
python tests/test_connect.py out/mock_conn
```

## 主要结论

- 四个方向（空间智能、多机协作、遥感与空中导航、侦察运载指认）唯一的共同语言是几何：SLAM 和三维重建。
- "给另一台机器人提供视野"的工作和现代空间智能（VLM、换位推理、VGGT）没有直接共引。
- 遥感跨视角定位与空地机器人协同之间空白最大：最短路径 4 步、仅 3 条，去掉万能经典后只剩 1 条。
- 由此提出课题 Fly Once, Localize All，详见 `docs/03-fly-once-proposal.md`。

## 注意

- 不要把 API key 写进代码或提交到仓库；报错日志外发前先删掉其中的 key。
- OpenAlex 对 arXiv 预印本的参考文献覆盖不全，同一论文可能有 arXiv 版和会议版两条记录。
- 报告中【推演】【虚构】标注的内容是设想，不是结论。

## License

MIT
