# 多机器人协作探索报告：空间智能 × 科幻 × 游戏

Oct 23, 2026 · @Regulus

## 开场

多机器人协作里最值得研究的，可能是那台不干活的：它的工作是把另一台机器人面对的世界改造成对方熟悉的样子——换个视角、给个参考系、指一个点、扶稳工件、把地面调平。

"一台机器人的视野为另一台提供调整"只是其中视野这一支。这份报告把机器人之间能交换的东西拆成 10 种原语，以空间智能为主线、学习策略为辅，展开 8 条桥接猜想，最后收成 3 个能做的课题。素材覆盖论文与综述、行业新闻、军事报道（只取机制层）、论坛讨论和游戏设定。

**认知标签**：【已证实】有实验或同行评审支撑；【前沿】预印本或单篇结果；【推演】基于现有结果的外推；【虚构】来自作品或游戏，现实中无依据。

**关于军事材料**：只借用"运载、中继、指认与执行分离"这类分工机制，全部转译到民用具身任务，不讨论武器或打击。

## 协作原语：一台机器人能给另一台什么

研究最密的是参考系、地图和任务规划三层；视野辅助"服务人"已经成熟，"服务策略"刚起步；指认和经验共享几乎空白【推演】。

| 原语 | 一台给另一台的东西 | 代表工作或案例 | 成熟度 |
| --- | --- | --- | --- |
| 视野 | 第三人称视角、遮挡补全 | [Senft 2022 无人机视角辅助遥操作](https://arxiv.org/abs/2208.04391v1)；[Gawel 2018 飞行器给地面机器人第三视角](https://nccr-robotics.ch/?p=11011)；[AV-ALOHA](https://arxiv.org/pdf/2409.17435) | 服务人：已证实；服务策略：前沿 |
| 参考系 | 相对位姿、共享坐标 | [空地跨模态相对定位](https://arxiv.org/abs/2511.06749v1)；[VGGT](https://openaccess.thecvf.com/content/CVPR2025/html/Wang_VGGT_Visual_Geometry_Grounded_Transformer_CVPR_2025_paper.html)；[多智能体 MASt3R-SLAM](https://arxiv.org/abs/2511.19031v1) | 已证实到前沿 |
| 地图与先验 | 俯视图、可通行性 | [空地大范围语义探索](https://arxiv.org/html/2405.07169v1)；[Trailblazer](https://arxiv.org/html/2505.09739v2) | 已证实 |
| 身体与平台 | 着陆台、运载、递工具 | [四足调平躯干接无人机](https://arxiv.org/pdf/2509.21571)；[ANYmal 驮无人机](https://arxiv.org/pdf/2205.05477)；[Flying Toolbox](https://www.lboro.ac.uk/media-centre/press-releases/2025/september/flying-toolbox/) | 前沿 |
| 力 | 共同搬运、协同施力 | [decPLM](https://arxiv.org/abs/2509.14342v1)；[四足团队力闭合搬运](https://arxiv.org/abs/2510.00682) | 前沿 |
| 能量与运力 | 运送、充电、回收 | [能耗约束的空地探索](https://arxiv.org/pdf/2603.22507) | 前沿 |
| 通信 | 选择性分享、中继 | [Where2comm](https://arxiv.org/abs/2209.12836v1) | 已证实 |
| 指认 | "看这里"、目标标记 | [Kemp 2008 激光笔指认](https://www.doi.org/10.1145/1349822.1349854)（人对机器人） | 人对机：已证实；机对机：推演 |
| 经验 | 跨机数据、失败记录 | [RoboExo 腕部视角转第三视角](https://neurips.cc/virtual/2026/poster/154097)；[VADER 求助](https://arxiv.org/pdf/2405.16021) | 前沿 |
| 意图与计划 | 任务分配、协商 | [COHERENT](https://arxiv.org/abs/2409.15146v3)；[CLiMRS](https://arxiv.org/abs/2602.06967)；[Gemini Robotics ER 2](https://blog.google/innovation-and-ai/models-and-research/google-deepmind/gemini-robotics-er-2/) | 前沿 |
|  |  |  |  |
|  |  |  |  |

## 前沿速写·空间智能

当前多模态大模型最弱的空间能力——换位思考和跨视角一致性——恰好是多机协作最需要的能力。

### 换位思考是公认短板

- [VSI-Bench](https://arxiv.org/abs/2412.14171v1)（CVPR 2025，Fei-Fei Li、谢赛宁组）：5000 多个问答、288 段真实室内视频。空间推理是主要瓶颈，思维链等语言推理技巧无效，但让模型显式画出认知地图能提升距离判断【已证实】。含义：认知地图可以成为机器人之间交换的中间表示。
- [ViewSpatial-Bench](https://arxiv.org/html/2505.21500v1)：模型擅长相机视角下的判断，换到"别人的参考系"就失灵；用多视角数据微调后整体提升 46.24%【前沿】。
- [OmniSpatial](https://alphaxiv.org/overview/2506.03135v2)：最强模型比人低 30 多个百分点，换位思考题占 37%；用新视角合成生成多视角拼图辅助推理，换位题提升明显【前沿】。
- [SCOPE](https://preview.aclanthology.org/ingest-acl/2026.acl-long.1514/)（ACL 2026）：2.01 万道跨视角一致性问答测了 26 个模型，归纳出两个根本缺陷【前沿】。

### 多机器人协同空间推理刚有基准

- [Seeing Together / CoopSR](https://www.alphaxiv.org/abs/2605.18431.md)（2026.05）：多台机器人同步第一视角视频的协同问答，11.4 万道题、19 类，外加两台宇树四足在动捕间采的 2326 道真实题。零样本模型多在 31%–42%；微调 Qwen2.5-VL-7B 从 33.5% 提到 66.7%，其方法到 70.55%；推理时去掉一台机器人的视频，准确率掉到 53.29%【前沿】。训练时用真值位姿当特权信息、测试时不需要位姿，这个设计可以直接借鉴。
- [Cosmic](https://arxiv.org/html/2603.27183v1)：对比 250 段人与人对话，人靠精确、信息密集的空间描述快速对齐；模型智能体话多、浅，建不出一致的共享地图【前沿】。
- [用对话对齐世界模型](https://docshare.wps.com/document/embodied-multi-agent-coordination-by-aligning-world-models-through-dialogue/81651/_payload.json)（2026）：给 PARTNR 加对话通道，用观测收敛度、信息新颖度、是否建模对方所知三个指标衡量"真对齐"还是"表面协调"【前沿】。

### 前馈三维模型可能替代跨机标定

- [VGGT](https://openaccess.thecvf.com/content/CVPR2025/html/Wang_VGGT_Visual_Geometry_Grounded_Transformer_CVPR_2025_paper.html)（CVPR 2025 最佳论文）：从一张到几百张图直接输出相机参数、深度、点图和点轨迹，不到一秒，不需要几何后优化【已证实】。含义：两台机器人的图像丢进去，相对位姿可能直接出来。
- [多智能体单目稠密 SLAM](https://arxiv.org/abs/2511.19031v1)把 MASt3R-SLAM 扩到多机；但[另一项工作](https://arxiv.org/pdf/2602.02430)指出 MASt3R 给出的相对位姿尺度经常不一致，需要单独优化回环尺度【前沿】。

### 世界模型从"一个人的梦"走向"共享的梦"

- World Labs 的 Marble 于 2025 年 11 月开放，2026 年 1 月推出 World API，2 月融资 10 亿美元，7 月收购 SceniX 并明确指向机器人方向（[官网](https://worldlabs.ai/)、[融资公告](https://www.worldlabs.ai/blog/funding-2026)）【前沿】。
- [Gemini Robotics ER 2](https://blog.google/innovation-and-ai/models-and-research/google-deepmind/gemini-robotics-er-2/)（2026.07.30）把多机器人协作列为核心能力，演示中人形机器人和双臂机器人靠共享语义理解交接任务【前沿】。
- [ShareVerse](https://arxiv.org/pdf/2603.02697)、MultiWorld 做多智能体一致的视频世界模型；自动驾驶综述 [MAEAD](https://arxiv.org/pdf/2606.13840) 把方向概括为"从 V2X 信息交换到共享世界模型"【前沿】。
- 视角转换生成：[RoboExo](https://neurips.cc/virtual/2026/poster/154097)（NeurIPS 2026）把腕部视频生成为第三人称视频，6 个任务上 VLA 平均成功率提升 30%【前沿】。

## 前沿速写·多机器人具身协作

这条线两头热、中间冷：上层任务规划（LLM 分工）和底层控制（协同搬运、对接）都很活跃，中间"一台机器人的感知如何直接进入另一台的策略"几乎没人做【推演】。

### 上层：异构团队的任务规划

- [COHERENT](https://arxiv.org/abs/2409.15146v3)（ICRA 2025）：LLM 给无人机、机器狗、机械臂分解分配任务，100 个长程任务的基准和代码已开源【前沿】。之后 [CLiMRS](https://arxiv.org/abs/2602.06967) 做动态分组协商，[DynaHMRC](https://arxiv.org/pdf/2606.14882) 做去中心化和执行中的动态变化【前沿】。
- [TZPP](https://arxiv.org/pdf/2603.21723)（2026）：宇树 G1 人形负责协调，Go2 四足在多模态大模型引导下探路，号称零训练、零先验、零仿真【前沿】。
- [RoboFactory](https://openaccess.thecvf.com/content/ICCV2025/html/Qin_RoboFactory_Exploring_Embodied_Agent_Collaboration_with_Compositional_Constraints_ICCV_2025_paper.html)（ICCV 2025）：首个具身多智能体操作基准，用逻辑、空间、时间三类组合约束自动生成多臂协作数据【已证实】。

### 中层：协同感知与通信

- [Where2comm](https://arxiv.org/abs/2209.12836v1)（NeurIPS 2022）：每个智能体生成空间置信图，只发"别人缺、自己有"的区域；在 OPV2V 上通信量降低 10 万倍以上仍优于基线，数据集里包含无人机【已证实】。这是"选择性分享视野"最成熟的范式。
- [AirCopBench](https://arxiv.org/abs/2511.11025v2)（AAAI 2026）：1.46 万道多无人机协同感知题，专门考遮挡、模糊等退化条件下的协同决策，现有模型普遍吃力【前沿】。

### 下层：空地协同与物理协作

- 空地协同早期范式：ETH 的 Fankhauser 等让无人机用单目相机建地图和高程图，腿足机器人在这张图上定位、按可通行性规划（[报道](https://boingboing.net/2015/10/19/a-flying-drone-and-a-walking-r.html)）【已证实】。知乎上一篇空地协同综述指出，多数工作仍停在"地面机器人用空中地图导航"，配合并不紧密（[知乎](https://zhuanlan.zhihu.com/p/4817783163)）。
- [空地跨模态相对定位](https://arxiv.org/abs/2511.06749v1)：地面车用激光、相机、IMU 做局部 BA 求与无人机的相对位姿，只传关键点和描述子，带宽压到 0.3 Mbps 以下【前沿】。
- [Flying Toolbox](https://www.lboro.ac.uk/media-centre/press-releases/2025/september/flying-toolbox/)（Nature 2025，西湖大学与拉夫堡大学）：一架无人机在另一架作业无人机上方近距离悬停、空中递工具，作者比作"护士给外科医生递器械"，克服了上下叠飞的下洗气流【已证实】。
- 浙大团队的[微型无人机集群](https://techxplore.com/news/2022-05-drone-swarms-autonomously-thick-forest.html)（Science Robotics 2022）：十架手掌大小的无人机不靠 GPS 穿越竹林【已证实】。

### 第三视角辅助

- [Gawel 等 SSRR 2018](https://nccr-robotics.ch/?p=11011)：一架飞行器在无 GPS 环境按需给多台地面机器人提供第三人称视角，供遥操作【已证实】。
- [Senft 等 IROS 2022](https://arxiv.org/abs/2208.04391v1)：无人机自动选视角并补偿自身位姿误差，同样服务人类操作员【已证实】。
- 单机主动视觉：[AV-ALOHA](https://arxiv.org/pdf/2409.17435) 用一条专门拿相机的臂学找视角，[BAVO-Bench](https://arxiv.org/pdf/2609.37292)（2026）专测遮挡后靠移动相机恢复可见性【前沿】。

## 前沿速写·遥感测绘与跨视角定位

遥感能给多机协作的最大礼物是共享参考系：一张俯视图可以同时是卫星、无人机和地面机器人的公共坐标。

- **跨视角地理定位**：把无人机或地面照片匹配到卫星图上求位置，常用数据集有 CVUSA、CVACT、VIGOR（街景对卫星）、University-1652（地面、无人机、卫星三源）和 SUES-200（无人机对卫星）（[综述](https://www.cjig.cn/en/article/doi/10.11834/jig.230585)）【已证实】。难点在于无人机斜视图往往横跨多块卫星切片，[2026 年的工作](https://arxiv.org/html/2604.01747v1)开始用三维几何感知把检索、对齐、位姿估计合成端到端【前沿】。
- **航测先验服务地面机器人**：[空地大范围探索系统](https://arxiv.org/html/2405.07169v1)里，无人机在线生成正射图、高程图和语义图，地面车直接拿来做全局规划【已证实】。[Trailblazer](https://arxiv.org/html/2505.09739v2) 用卫星影像加航空 LiDAR 学越野代价图；CMU AirLab 用卫星图自动标注可行路径，蒸馏进第一人称图像的远距离可通行性预测，离线指标提升 10% 以上，人工接管更少（[论文](https://arxiv.org/pdf/2607.17984)）【前沿】。
- **空中视觉语言导航**：[OpenFly](https://arxiv.org/abs/2502.18041v6) 有 18 个场景、10 万条轨迹，是目前最大的空中 VLN 基准之一；[CityNav](https://arxiv.org/pdf/2406.14240) 基于真实城市点云；中科院空天院等十余家单位发了 AeroVerse 综述（[知乎解读](https://zhuanlan.zhihu.com/p/1971188476746641861)）【前沿】。
- **遥感大模型与智能体**：视觉语言地理基础模型已有[专门综述](https://arxiv.org/html/2406.09385v1)；[OmniEarth](https://arxiv.org/abs/2603.09471) 设 28 个细粒度任务，现有模型在复杂地理任务上仍明显不足【前沿】。IEEE JSTARS 正在征稿"Foundation Models and Agents in Earth Observation"专刊，主题明确包括具身智能中的多智能体协同感知（如无人机群），截稿 2026 年 12 月 31 日（[征稿启事](https://www.grss-ieee.org/wp-content/uploads/2026/08/JSTARS_CfP_Foundation-Models-and-Agents-in-Earth-Observation.pdf)）。
- **无人机建数字孪生**：[UAVTwin](https://arxiv.org/pdf/2504.02158) 用无人机图像训练 3D 高斯泼溅做数字孪生；Niantic Spatial 与 Spexi 在 2026 年 6 月展示了用标准化航拍网络做工业级高斯泼溅孪生（[博客](https://nianticspatial.com/blog/spexi-quality)）【前沿】。含义：无人机先飞一圈建出的模型，可以成为地面机器人的"仿真器+地图"二合一。

## 新闻、军事机制与论坛脑洞

战场上已经把"运载、中继、侦察、执行"拆到不同机体上，这套分工方式本身值得借鉴；以下只记机制，转译后的民用版本写在每条后面。

- **母舰**：俄乌战场报道中，母舰无人机一边运送小型无人机，一边充当图像和控制信号的空中中继（[EurAsian Times](https://www.eurasiantimes.com/1st-time-in-ukraine-war-russia-unleashes/)）；大型"母舰"无人机也在 2024 年珠海航展亮相；美国公司在测试用平流层气球当无人机母舰和通信中继（[TWZ](https://www.twz.com/news-features/aerostar-high-altitude-balloons-being-turned-into-drone-motherships.md)）。民用转译：机器狗驮无人机进楼，无人机前出探查，机器狗留在门口当中继。
- **光纤系留**：光纤遥控无人机不发射无线信号，因此不受干扰，代价是线缆碰到树枝就会断（[Al Jazeera](https://aljazeera.com/news/2026/4/29/how-hezbollahs-fibre-optic-drones-test-israels-sophisticated-radar-system)）。机制是"用物理连接换通信可靠"。民用转译：室内或地下作业的系留无人机，线缆路径本身要和遮挡物一起规划——[2019 年的系留无人机视觉辅助工作](https://arxiv.org/pdf/1904.00078)已经在规划时考虑绳缆与障碍物的接触点。
- **蜂群战术游戏化**：DARPA 的 OFFSET 项目设想由 250 架以上小型空中与地面无人系统组成的蜂群，并搭建一个基于物理的"蜂群战术游戏"，让玩家探索、演化、评估战术，再通过社区交流战术（[DARPA](https://www.darpa.mil/work-with-us/offensive-swarm-enabled-tactics)）。媒体直接称其为"安德的游戏式控制器"（[Defense One](https://defenseone.com/technology/2016/12/wanted-military-enders-game-controller-urban-robot-swarms/133758)）。民用转译：用多人游戏众包异构机器人团队的协作示教数据（见猜想 8）。
- **西点军校现代战争研究所的一篇评论**：未来的蜂群会是大小、载荷不同的混编体，像"一盒乐高"，其中就举了飞行机器人和步行机器人协作的例子；还提到通信被压制时可以改用环境线索协调（[MWI](https://mwi.westpoint.edu/era-drone-swarm-coming-need-ready/)）。后一点和群体机器人的"痕迹协调"（stigmergy）是同一个思路。
- **论坛与民间**：Reddit 机器人版有用户设想太阳能基站加无人机识别野狗、用警笛非致命驱赶，以保护家畜和澳洲野犬（[讨论帖](https://twt.omada.cafe/r/robotics/comments/16amwkm/join_raskrobotics_our_communitys_qa_subreddit/mtokccz/?context=3)）；早在 2015 年，ETH 的四足机器人 StarlETH 背上就系着一架小无人机，被媒体称为"天上的眼睛"（[Popular Science](https://www.popsci.com/watch-drone-land-on-robot-dog/)）。论坛里能找到的高质量脑洞不多，中文社区讨论主要集中在综述解读和产业新闻，这一块素材偏薄。

## 虚构镜像：科幻与游戏

游戏里最有用的不是设定本身，而是设计者为了好玩悄悄删掉的难点——那些"作弊"正好对应现实中的研究空白。以下设定都标【虚构】，对应的猜想编号见下一节。

| 作品 | 设定 | 押注的机制 | 设计者删掉的难点 | 猜想 |
| --- | --- | --- | --- | --- |
| 《星际争霸》 | 隐形侦察单位 Observer 只负责提供视野，全军视野实时共享 | 感知是团队公共资源 | 跨机外参、时间同步、视角对策略是否有用 | 1 |
| 《刺客信条》 | 爬上高处"同步"，揭开周边地图 | 一次高空俯视等于解锁局部地图 | 俯视图与地面视角之间的跨视角匹配 | 2 |
| 《Arma 3》 | 一人用激光指示器标点，另一人据点执行 | 指认者与执行者分离，标记点是公共坐标 | 标记点在执行者视角下是否可见 | 3 |
| 《幽灵行动：荒野》 | 无人机标记的目标对全队持续显示 | 传"标记"比传"画面"省得多 | 标记会随时间漂移，需要持续更新 | 3 |
| 《三体》 | 智子监视地球，同时干扰被观测的实验 | 观察者本身会改变被观察的东西 | 无（作品恰好点破了它） | 4 |
| 《攻壳机动队 SAC》 | Tachikoma 每天同步记忆，却仍然各自长出个性 | 经验可以跨个体无损迁移 | 不同本体、不同视角之间的经验转换 | 5 |
| 《双人成行》 | 一人往墙上钉钉子，另一人用锤子挂在钉子上荡过去 | 一方制造可供性，另一方利用 | 接口由关卡设计师预制，现实里要辅助者自己学 | 6 |
| 《彩虹六号：围攻》 | 进攻前先派侦察小车摸清目标位置 | 先派最便宜的去看，再决定主力怎么进 | 侦察要花多少时间才划算 | 7 |
| 《安德的游戏》 | 少年以为在打模拟游戏，实际在指挥真实舰队 | 人只需给意图，系统负责执行 | 游戏物理与真实物理的差距 | 8 |
| 莱姆《无敌号》（冷门） | 无中枢的微型机械聚成云，连探险队的巨型战车也败给了它 | 协作可以完全靠涌现，不需要语言和规划者 | 复杂操作任务能否靠涌现完成 | 反向视角 |

## 桥接猜想

八条猜想分别落在视野、参考系、指认、观察代价、换位思考、物理辅助、信息价值和数据来源上，前五条以空间智能为主，后三条偏学习与策略。每条都标了能用组里现有硬件做的最小实验。

### 猜想 1：给观察者做 StandReady——视角服务策略，不服务人

- **来源**：Senft 2022 × CoopSR × 《星际争霸》Observer × 你在复现的 StandReady（StandReady 预测执行者站哪，这里改成预测观察者站哪）。
- **猜想**：观察者（无人机、夹着相机的第二台臂或机器狗）学一个站位打分器，输入执行者当前观测和任务，输出观察者位姿；奖励来自执行者策略的成功率，或动作不确定性（扩散策略多次采样的方差、VLA 动作熵）的下降。外参不再离线标定，直接把两台机器人的图像交给 VGGT 一类前馈模型求相对位姿【推演】。
- **前提与差距**：①执行者要能接受会动的第三视角——[Vantage](https://arxiv.org/html/2506.12261v2) 指出固定视角训练的策略在相机移动时很快失效，这是最大的坎；②前馈模型的位姿精度和尺度够不够要实测，MASt3R 的尺度不一致问题是警示；③只靠无人机自身 VIO 大约厘米级，精细操作要毫米级，差约一个数量级【推演，量级估计】；④我没搜到"以执行者置信度为奖励训练另一台机器人站位"的工作，不代表没有，开工前要再查【待核实】。
- **最小实验**：RoboCasa 或 ManiSkill3 里一台固定臂加一个自由浮动相机（位姿加噪声模拟无人机），比较固定第三视角、几何可见性最优视角、策略感知视角三组的成功率；真机先用第二台臂夹相机代替无人机。几周。

### 猜想 2：一张俯视图当公共坐标——"同步点"即服务

- **来源**：跨视角地理定位 × 空地相对定位 × VGGT × 《刺客信条》同步点。
- **猜想**：任务开始时无人机升空"同步"，拍一组俯视和斜视图，现场生成正射图或高斯泼溅模型；之后每台地面机器人（狗、人形、移动臂）不跑联合 SLAM，只用自己的第一视角去和这张图做跨视角匹配，直接得到公共坐标系下的位姿。室内版本就是在天花板高度悬停一次。这张图还能当仿真器用，在上面渲染"队友看到的画面"（接猜想 5）【推演】。
- **前提与差距**：①低空斜视与地面平视之间的匹配比无人机对卫星更难，地面视角遮挡多；②场景变化后图会过期，需要按需重新"同步"；③通信只需传一次地图加稀疏特征，[空地相对定位工作](https://arxiv.org/abs/2511.06749v1)已把带宽压到 0.3 Mbps 以下，比持续传视频低一个数量级以上【推演】。
- **最小实验**：在实验楼或校园一角，无人机拍 200–400 张图建模；Go2 沿三条路线走，用第一视角图像对模型定位，以 RTK 或动捕为真值，比较定位误差、首次定位耗时和带宽；对照组是两机联合 SLAM。

### 猜想 3：机器之间的激光笔——指认而不传图

- **来源**：[Kemp 2008 激光指认](https://www.doi.org/10.1145/1349822.1349854) × Where2comm × Cosmic × 《Arma 3》《幽灵行动：荒野》的标记机制。
- **猜想**：观察者不把画面发给执行者，而是直接在物体上打一个激光点或投一个图案，执行者用腕部相机找到点就抓。物理标记"活在世界里"，两台机器人之间不需要共享坐标、不需要标定，几乎不占带宽，是空间对齐问题最省事的解法之一【推演】。进阶版是在共享地图里放稀疏三维锚点，相当于游戏里的标记。
- **前提与差距**：Kemp 的系统在 3 米内误差很低，但那是人指给机器人看；机器人对机器人时，点必须同时落在执行者视野里，强光、反光表面和遮挡都会让点丢失。另一个开放问题是语义：一个点说不清"抓把手"还是"抓杯身"，可能需要"点加一句话"或"点加一条姿态线段"。
- **最小实验**：一台臂或无人机挂廉价绿色激光模块当指认者，另一台臂按点抓取；对比激光点、图像框加标定转换、纯语言描述三种指认方式的抓取成功率、延迟和通信量。几周，硬件成本很低。

### 猜想 4：观察者效应——观察者本身就是干扰

- **来源**：《三体》智子 × Senft 2022 的遮挡与碰撞目标 × Flying Toolbox 对下洗气流的处理。
- **猜想**：无人机贴近机械臂观察时会改变它观察的东西：下洗气流吹动轻物体，机身遮光，机身出现在执行者相机里成为干扰物，让执行者策略的输入分布偏移。所以"好视角"要加一项"侵入代价"，执行者策略也要在"队友入镜"的数据上训练【推演】。
- **前提与差距**：Senft 已把遮挡和碰撞写进视角优化目标，但没有量化"观察者入镜"对学习型策略的影响；Flying Toolbox 说明近距离下洗气流可以被克服，但需要专门的控制设计。
- **最小实验**：拿一个现成的抓取或插孔策略，让另一台机器人进入执行者相机画面（真机或仿真渲染），测成功率下降多少；再用"队友入镜"数据增强微调，看能补回多少。成本最低，适合当其他猜想的前置实验。

### 猜想 5：想象队友看到什么——共享几何底座上的换位思考

- **来源**：ViewSpatial 与 OmniSpatial（模型不会换位，新视角合成能帮上忙）× CoopSR（去掉一台机器人掉 17 个点）× RoboExo × 《攻壳机动队》Tachikoma 的记忆同步。
- **猜想**：不必实时传对方的视频。只要有一张共享三维模型（猜想 2 的产物）和对方的位姿，就能渲染出"队友此刻大概看到什么"，用来做三件事：①回答"B 能不能看到那扇门"这类换位问题；②判断对方的观测里缺什么，只补那一块，相当于 Where2comm 的三维版；③把一台机器人的经验转成另一台视角下的训练样本，算是 Tachikoma 式"经验同步"在几何层面的半步实现【推演】。
- **前提与差距**：渲染只代表静态场景，运动物体、刚被拿走的东西都不在图里；ViewSpatial 用多视角数据微调后提升 46.24%，说明换位能力可以训练出来，但那是问答不是动作，从"答对"到"做对"之间还没有基准。
- **最小实验**：无人机在实验室建高斯泼溅模型，两只 Go2 跑 CoopSR 式协同问答，对比三种输入——只用自己的视角、加对方真实视频、加从模型渲染的对方视角——的准确率和带宽。再进一步，把渲染视角用于机械臂策略的数据增强，看能否接近 RoboExo 的收益。

### 猜想 6：帮手不干活，帮手改造对方的世界

- **来源**：《双人成行》的钉子与锤子 × [四足调平躯干接无人机](https://arxiv.org/pdf/2509.21571) × Flying Toolbox 空中递工具 × decPLM。
- **猜想**：对接那篇里的四足已经在做这件事：它调整自己的姿态，把无人机降落从难任务变成简单任务。推广开来，辅助机器人通过扶住、翻转、递送工件或顶开门，把工件和环境调到执行者策略的"舒适区"，执行者本身不用改。猜想 1 优化执行者的视觉输入，这一条优化执行者的物理输入，两者可以统一成"辅助者塑造执行者的输入分布"【推演】。
- **前提与差距**：辅助者得知道执行者擅长什么，也就是一张能力地图；对接论文的"躯干保持水平"是手写目标，要通用化只能靠学习，或者对执行者做黑盒查询。
- **最小实验**：仿真里放两台独立的臂。执行者是预训练的插孔或抓取策略，在某些物体位姿下成功率低；辅助臂先把物体重新摆放再交出去，用 CEM 或贝叶斯优化搜索摆放位姿，目标函数就是执行者成功率。对照组是随机摆放和人工规则。

### 猜想 7：先派最便宜的去看——侦察的信息价值

- **来源**：《彩虹六号：围攻》的侦察小车 × [TZPP](https://arxiv.org/pdf/2603.21723)（狗探路、人形协调）× ANYmal 按需放飞无人机 × [能耗约束的放飞与回收](https://arxiv.org/pdf/2603.22507)。
- **猜想**：把"什么时候值得先侦察、侦察多久"当成可学习的决策。侦察者（无人机或小型机器狗）的奖励是它带回的信息为执行者省下的时间和提高的成功率，减去侦察本身的耗时和电量。和猜想 1 的区别在于：猜想 1 是执行中的同步辅助，这一条是执行前的信息采购【推演】。
- **前提与差距**：跨机器人、跨时间的功劳分配很难，侦察的好处往往几分钟后才体现；现有的放飞决策多是规则或优化方法，学习型的"侦察预算"我只找到零星工作【待核实】。
- **最小实验**：在 Habitat 或 Isaac Sim 里做"找到并取回目标物"的任务，配一台慢而强的移动操作平台和一架快而弱的无人机，比较从不侦察、总是先侦察、学习何时侦察三种策略的总耗时与成功率。

### 猜想 8：安德计划——用游戏众包异构团队的协作数据

- **来源**：《安德的游戏》× DARPA OFFSET 的蜂群战术游戏 × RoboFactory 的自动数据生成。
- **猜想**：异构协作缺的是示教数据——一个人很难同时遥操一条臂、一只狗和一架无人机。把它做成多人在线游戏：每个玩家操控一台机器人，在物理仿真里合作完成任务，对局日志就是多智能体示教数据，玩家发明的配合套路就是候选协作原语。游戏为了平衡被迫加的"作弊"，比如共享视野、零延迟通信，正好标出了现实中最难的环节【推演】。
- **前提与差距**：玩家会钻仿真物理的漏洞，数据要过滤；从游戏动作到真机控制仍有仿真到现实的鸿沟；RoboFactory 已能用约束自动生成数据，人类数据的增益要和它正面比较。
- **最小实验**：在 ManiSkill3 或 Isaac Sim 上做一个 2–3 人的网页小游戏，一条臂、一只狗、一架无人机合作把物体搬到指定位置；收 100 局，训练多智能体扩散策略，与自动生成的数据对比。几周到两个月。

## 反向视角：如果科幻都猜错了

最可能"不像科幻"的形态是：一个共享的几何底座（地图或三维模型）、极稀疏的消息（一个坐标、一张置信图、一个激光点）、加上各自的本地策略。它看起来更像基础设施，而不像一支会讨论的团队【推演】。

- **"机器人开会"的想象可能是误导**。COHERENT、CLiMRS 这一路让 LLM 智能体用自然语言协商，但 Cosmic 的对比显示，人类靠精确、信息密集的空间描述就能快速对齐，模型却话多而浅。真正有用的协作消息可能是坐标和点，而不是句子；Where2comm 用置信图把通信量降了五个数量级，就是这个方向的证据。
- **《无敌号》式的群体也许更近**。未来不一定是"一只狗、一架无人机、一条臂"的精英小队，也可能是一群便宜、同构、靠物理隐式协调的机器。decPLM 只靠接触、不靠显式通信就完成了协同抬举；群体机器人的痕迹协调研究，比如 [S-MADRL](https://arxiv.org/abs/2510.03592v1) 用虚拟信息素让多达 8 个智能体自组织分工，[LARS](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12431334/) 用投影让机器人通过环境间接交流，都在这个方向上。
- **游戏让人低估了视野的代价**。游戏里视野共享是免费的，标记永不漂移，队友也不会挡住彼此的镜头。现实中这三件事各是一个研究问题（猜想 1、3、4）。
- **军事叙事让人高估了空中的权重**。无人机抢眼，但在大多数空地系统里，载荷、算力和续航都在地面机器人身上；更合理的分工可能是"地面是大脑和电池，空中只是一次性的眼睛"。

## 现实约束

前面所有猜想共享同一组硬限制，其中标定同步和评测缺失是最先会卡住的两项。

- **物理**：小型无人机续航通常在十几到三十分钟量级【推演】；下洗气流会吹动轻物体，贴近机械臂飞行有碰撞风险；室内定位依赖动捕或可靠的视觉惯性里程计。
- **标定与同步**：跨机外参和时间戳要在运动中持续估计；前馈三维模型能省掉离线标定，但尺度一致性仍需验证。
- **数据**：多机真实数据极少——CoopSR 的真实测试集只有两只四足、13 个场景、约 1.75 小时；视频 token 随机器人数量线性增长，模型推理成本也跟着涨。
- **通信**：视频流的带宽和延迟会直接拖累闭环操作；楼内、地下的遮挡让中继成为刚需。
- **评测**：缺少"一台机器人帮另一台"的标准基准。BAVO-Bench 是单机主动视觉，CoopSR 是问答而非动作，RoboFactory 是同构多臂。这既是约束，也是机会。
- **安全与双重用途**：多机近距离作业有碰撞风险，现场需要急停和人工监督；多台机器人的第一视角视频涉及隐私，协同感知也可能被用于监视，CoopSR 作者在论文里专门提示了这一点。本报告的军事材料只取分工机制，不涉及武器用途。

## 可以变成研究的问题

如果只挑一个起步，建议先用一周做猜想 4 的"队友入镜"前置实验拿到第一组数，再进入问题 1；问题 2、3 更偏空间智能，适合作为中长期方向。

### 问题 1：策略感知的辅助视角（对应猜想 1、4）

- **研究问题**：给定一个固定的视觉运动策略，另一台机器人应该停在哪里，才能让该策略成功率最高，同时对辅助者自身的位姿误差和"入镜干扰"鲁棒？
- **方法**：以执行者的动作不确定性为奖励（扩散策略采样方差或 VLA 动作熵）；站位打分网络结构借鉴 StandReady；外参用 VGGT 一类前馈模型在线估计。基线为固定相机、Senft 式几何目标、随机视角。
- **环境与硬件**：RoboCasa（你已在搭）、ManiSkill3；真机先用一台臂夹相机当观察者，再换成无人机。
- **体量与去向**：一篇 IROS 或 ICRA 级工作。IROS 截稿通常在每年 3 月初，以官网为准。

### 问题 2：机器人之间如何"指"给对方看（对应猜想 3、5）

- **研究问题**：在不共享标定的前提下，一台机器人要把"这个东西"传达给另一台机器人，用物理标记、共享地图锚点、图像框还是语言，哪种在准确率、带宽和延迟之间最优？能否学一个策略按场景自动选择指认方式？
- **方法**：构建跨本体指认基准（臂到臂、无人机到狗、狗到人形），执行者须把标记解析到自己的参考系并完成抓取或导航；指认方式作为离散动作学习。
- **环境与硬件**：仿真用 ManiSkill3 或 Habitat 批量生成；真机用组里现有的臂、狗、无人机和人形，激光模块成本很低。
- **体量与去向**：基准加方法，适合 CoRL 或 IROS，空间智能含量最高的一个。

### 问题 3：共享几何底座上的协同空间推理（对应猜想 2、5）

- **研究问题**：无人机现场构建的三维模型，能否让地面机器人团队在不传视频的情况下完成跨视角定位和换位推理，并把"答对问题"延伸到"做对动作"？
- **方法**：无人机建高斯泼溅模型或 VGGT 点图；地面机器人跨视角定位后，渲染队友视角输入多模态模型；在 CoopSR 式问答之上增加动作任务，例如"让看得见门的那台去开门"。
- **环境与硬件**：[CoopSR 已公开的代码](https://www.alphaxiv.org/abs/2605.18431.md)可作起点（EgoTeam 数据是否全部公开待确认），真实场景用 Go2 加无人机采集。
- **体量与去向**：遥感方向可投 IEEE JSTARS"地球观测中的基础模型与智能体"专刊（截稿 2026 年 12 月 31 日），机器人方向可投 IROS 或 RA-L。

## 参考文献

**空间智能与跨视角**

- [Thinking in Space / VSI-Bench（CVPR 2025）](https://arxiv.org/abs/2412.14171v1)
- [ViewSpatial-Bench](https://arxiv.org/html/2505.21500v1)
- [OmniSpatial](https://alphaxiv.org/overview/2506.03135v2)
- [SCOPE（ACL 2026）](https://preview.aclanthology.org/ingest-acl/2026.acl-long.1514/)
- [Seeing Together / CoopSR](https://www.alphaxiv.org/abs/2605.18431.md)
- [Cosmic：通过交流构建共享空间模型](https://arxiv.org/html/2603.27183v1)
- [Embodied Multi-Agent Coordination by Aligning World Models Through Dialogue](https://docshare.wps.com/document/embodied-multi-agent-coordination-by-aligning-world-models-through-dialogue/81651/_payload.json)
- [Sentinel：城市尺度协同空间推理](https://www.emergentmind.com/papers/2605.26239)
- [多模态空间推理综述](https://huggingface.co/papers/2510.25760)
- [VGGT（CVPR 2025）](https://openaccess.thecvf.com/content/CVPR2025/html/Wang_VGGT_Visual_Geometry_Grounded_Transformer_CVPR_2025_paper.html)
- [多智能体单目稠密 SLAM](https://arxiv.org/abs/2511.19031v1)、[基于 3D 基础模型的去中心化协同 SLAM 回环](https://arxiv.org/pdf/2602.02430)
- [RoboExo（NeurIPS 2026）](https://neurips.cc/virtual/2026/poster/154097)、[Exo2EgoPolicy（ECCV 2026）](https://cdn.amazon.science/3c/ef/f447e82542a28ce8fdf0629a7e9d/eccv26-exo2ego-final-camera-ready-camera-ready.pdf)
- [ShareVerse](https://arxiv.org/pdf/2603.02697)、[MAEAD 综述](https://arxiv.org/pdf/2606.13840)
- [World Labs](https://worldlabs.ai/)、[World Labs 2026 融资](https://www.worldlabs.ai/blog/funding-2026)、[Gemini Robotics ER 2](https://blog.google/innovation-and-ai/models-and-research/google-deepmind/gemini-robotics-er-2/)

**多机器人具身协作**

- [COHERENT（ICRA 2025）](https://arxiv.org/abs/2409.15146v3)、[CLiMRS](https://arxiv.org/abs/2602.06967)、[DynaHMRC](https://arxiv.org/pdf/2606.14882)、[TZPP](https://arxiv.org/pdf/2603.21723)
- [RoboFactory（ICCV 2025）](https://openaccess.thecvf.com/content/ICCV2025/html/Qin_RoboFactory_Exploring_Embodied_Agent_Collaboration_with_Compositional_Constraints_ICCV_2025_paper.html)
- [Where2comm（NeurIPS 2022）](https://arxiv.org/abs/2209.12836v1)、[AirCopBench（AAAI 2026）](https://arxiv.org/abs/2511.11025v2)
- [空地跨模态相对定位](https://arxiv.org/abs/2511.06749v1)、[空地大范围语义探索](https://arxiv.org/html/2405.07169v1)
- [ANYmal 驮无人机 marsupial 系统](https://arxiv.org/pdf/2205.05477)、[四足与无人机在复杂地形对接](https://arxiv.org/pdf/2509.21571)、[能耗约束的空地协同探索](https://arxiv.org/pdf/2603.22507)
- [decPLM 多四足协同搬运](https://arxiv.org/abs/2509.14342v1)、[四足团队共享物体操作](https://arxiv.org/abs/2510.00682)
- [Flying Toolbox（Nature 2025）](https://www.lboro.ac.uk/media-centre/press-releases/2025/september/flying-toolbox/)、[浙大微型无人机集群（Science Robotics 2022）](https://techxplore.com/news/2022-05-drone-swarms-autonomously-thick-forest.html)
- [Senft 等 IROS 2022](https://arxiv.org/abs/2208.04391v1)、[系留无人机视觉辅助](https://arxiv.org/pdf/1904.00078)、[Gawel 等 SSRR 2018](https://nccr-robotics.ch/?p=11011)
- [AV-ALOHA](https://arxiv.org/pdf/2409.17435)、[BAVO-Bench](https://arxiv.org/pdf/2609.37292)、[Vantage](https://arxiv.org/html/2506.12261v2)
- [VADER](https://arxiv.org/pdf/2405.16021)、[Kemp 等 HRI 2008 激光指认](https://www.doi.org/10.1145/1349822.1349854)
- [S-MADRL 痕迹协调](https://arxiv.org/abs/2510.03592v1)、[LARS 投影增强现实](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12431334/)

**遥感测绘**

- [跨视角图像地理定位综述（中国图象图形学报）](https://www.cjig.cn/en/article/doi/10.11834/jig.230585)、[三维几何感知的无人机跨视角定位](https://arxiv.org/html/2604.01747v1)
- [Trailblazer](https://arxiv.org/html/2505.09739v2)、[卫星可通行性先验蒸馏（CMU AirLab）](https://arxiv.org/pdf/2607.17984)
- [OpenFly](https://arxiv.org/abs/2502.18041v6)、[CityNav](https://arxiv.org/pdf/2406.14240)、[AeroVerse 综述解读（知乎）](https://zhuanlan.zhihu.com/p/1971188476746641861)
- [视觉语言地理基础模型综述](https://arxiv.org/html/2406.09385v1)、[OmniEarth](https://arxiv.org/abs/2603.09471)、[JSTARS 专刊征稿](https://www.grss-ieee.org/wp-content/uploads/2026/08/JSTARS_CfP_Foundation-Models-and-Agents-in-Earth-Observation.pdf)
- [UAVTwin](https://arxiv.org/pdf/2504.02158)、[Niantic Spatial × Spexi](https://nianticspatial.com/blog/spexi-quality)

**新闻与论坛**

- [母舰无人机兼作中继（EurAsian Times）](https://www.eurasiantimes.com/1st-time-in-ukraine-war-russia-unleashes/)、[平流层气球母舰（TWZ）](https://www.twz.com/news-features/aerostar-high-altitude-balloons-being-turned-into-drone-motherships.md)
- [光纤无人机（Al Jazeera）](https://aljazeera.com/news/2026/4/29/how-hezbollahs-fibre-optic-drones-test-israels-sophisticated-radar-system)
- [DARPA OFFSET](https://www.darpa.mil/work-with-us/offensive-swarm-enabled-tactics)、[Defense One 报道](https://defenseone.com/technology/2016/12/wanted-military-enders-game-controller-urban-robot-swarms/133758)、[西点 MWI 评论](https://mwi.westpoint.edu/era-drone-swarm-coming-need-ready/)
- [空地协同综述（知乎）](https://zhuanlan.zhihu.com/p/4817783163)、[StarlETH 背着无人机（Popular Science）](https://www.popsci.com/watch-drone-land-on-robot-dog/)、[Reddit r/robotics 讨论](https://twt.omada.cafe/r/robotics/comments/16amwkm/join_raskrobotics_our_communitys_qa_subreddit/mtokccz/?context=3)
