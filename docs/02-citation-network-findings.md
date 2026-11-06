# 引用网络分析结果

运行日期：2026-10-29。数据来源 OpenAlex，缺参考文献的预印本用 Semantic Scholar 补。以下数字都来自 `tools/` 下两个脚本的实际输出。

## 1. 设置

- 种子：`seeds/seeds_example.txt`，23 篇，分为四个方向：空间智能、多机协作、遥感与空中导航、侦察运载指认
- 命令：`python tools/oa_citenet.py --seeds-file seeds/seeds_example.txt --depth 2 --s2-fallback --out d2_v2`
- 规模：第 1 层候选 648 篇、保留 401 篇；第 2 层候选 12234 篇、保留 480 篇；最终 **901 个节点、8100 条边**
- 花费：全部运行加起来不到 0.1 美元

## 2. 方法演进

| 版本 | 做法 | 问题 |
| --- | --- | --- |
| v1 | 入度、PageRank；按 OpenAlex 的 field 统计跨领域 | 核心文献被 ResNet、ImageNet 这类万能经典占满；field 太粗，几乎全是 Computer Science / Engineering |
| v2 | 按种子方向统计"能沿引用链追溯到哪些方向"；特异性 = 图内被引 / log10(全库被引) | 两层之后几乎所有论文都能追溯到所有方向，区分不开 |
| v3（当前） | **方向画像**：种子是独热向量，每篇论文的画像 = 直接引用它的上一层论文画像的平均；特异性 = 图内被引 / √全库被引；桥梁分 = 画像均衡度 × 特异性 | — |

## 3. 每个方向的"根"

去掉万能经典后，排名靠前的文献几乎都只属于一个方向：

| 方向 | 代表文献 |
| --- | --- |
| 空间智能 | A Multi-stage Linear Approach to SfM (2012)、Robust Rotation and Translation Estimation (2007)、RelPose (2022)、Pixel-Perfect SfM (2021) |
| 遥感与空中导航 | Vision-and-Language Navigation (2018)、Speaker-Follower (2018)、Self-Monitoring Navigation Agent (2019) |
| 多机协作 | Cooperative Manipulation and Transportation with Aerial Robots (2010) |
| 侦察运载指认 | 系留无人机视觉伺服、系留供电多旋翼、磁性物体空中抓取（均 2017） |

## 4. 方向之间的关联

| 方向对 | 关联度 | 直接共引 |
| --- | --- | --- |
| 空间智能 × 遥感与空中导航 | 41.1 | 2（SfM Revisited、SegFormer） |
| 侦察运载指认 × 多机协作 | 32.2 | 4 |
| 多机协作 × 空间智能 | 21.1 | 2（RT-1、GPT-4 Technical Report） |
| 侦察运载指认 × 空间智能 | 17.6 | 0 |
| 侦察运载指认 × 遥感与空中导航 | 15.3 | 0 |
| 多机协作 × 遥感与空中导航 | 14.3 | 1（ResNet） |

关联度 = 所有非种子论文在两个方向上画像份额的较小值之和。

**桥梁论文（画像均衡 × 特异性）前几名**：AI2-THOR、Matterport3D、Curless & Levoy 体素融合 (1996)、SayCan、Habitat、Vocabulary Tree、SfM Revisited、TUM RGB-D、ORB-SLAM、PTAM。

**读法**
1. 四个方向的共同语言是几何（SLAM、三维重建），其次是具身仿真平台和语言落地。
2. "给另一台机器人提供视野"的论文和现代空间智能（VLM、换位推理、VGGT）之间没有直接共引。
3. 多机协作和遥感之间最弱。

## 5. 最短引用路径验证（`tools/oa_connect.py`）

Inciteful 的 Literature Connector 当时检索不可用（底层 OpenAlex 搜索失败），所以自己实现了一个：从两端同时沿"引用 / 被引"扩展，相遇后列出全部最短路径；再剔除全库被引 ≥ 20000 的论文重找一次。

| | A 组 | B 组 |
| --- | --- | --- |
| 端点 | Aerial-Ground collaborative sensing: Third-Person view for teleoperation (2018) ↔ Thinking in Space (2025) | University-1652 (2020) ↔ Marsupial Walking-and-Flying Robotic Deployment (2022) |
| 最短路径 | 4 步，15 条 | 4 步，3 条 |
| 去掉万能经典后 | 仍为 4 步，多条 | 只剩 1 条 |
| 主要通道 | 空地点云配准 → 3DMatch / SLAM 综述 → SpatialVLM、FAST-EQA；空地协作 → Ego4D → Thinking in Space | Cross-View Image Matching (2017) ← 多机器人搜救综述 (2020) ← 核环境机器人生态 (2023) |
| 判断 | 有空白，2026 年 Cambrian-P、FAST-EQA 开始填 | 空白最大，选为方向 ① |

## 6. 局限

- OpenAlex 参考文献有缺失：Where2comm、Marsupial 在库里为空，S2 也没补上，B 组终点一侧只能靠施引文献扩展，空白可能被高估。
- 种子与分组是主观选择。
- 连接器只扩展到 4 步、启发式剪枝，"未连通"只代表搜索范围内未找到。
- 科幻与游戏素材只用于提出猜想，无法用引用网络检验。
