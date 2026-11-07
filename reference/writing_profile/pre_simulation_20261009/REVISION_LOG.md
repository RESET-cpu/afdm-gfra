# II–V初稿改写记录

## 2026-10-09：分章节 LaTeX 项目与第二章重排

用户确认第二章采用三个小节，并要求独立论文文件夹。当前入口为 [main.tex](../../../paper/main.tex)，正文在 [sections/](../../../paper/sections)，文献在 [references.bib](../../../paper/STMP/references.bib)。原稿、写作语料和本地参考论文已集中于 `paper/`。

| 段落组 | 调整 | 依据 | 保留内容 |
|---|---|---|---|
| 第二章章首 | 系统概述及活动分布置于A之前 | 用户确认；Shen §II开头的场景概述 | 原场景、非空活动分布及边缘公式逐字保留 |
| II-A | 以Terrestrial-Satellite Link Model统领几何、时延、Doppler和阵列 | Shen §II-A原始标题 | 原几何、RF约定、路径延迟和UPA段落及公式 |
| II-B | 以Transmission Scheme串联波形、信道算子、导频和观测 | Shen §II-B；Ding §II信号链 | 全部原段落与公式按原顺序保留，合并小节边界 |
| II-C | 使用Problem Formulation标题承接估计目标 | Shen §II-C；Cai §II-B的贝叶斯表述 | 工作先验、近似说明、后验与判决目标 |
| III–V | 按章拆成文件 | 用户要求 | 正文逐字保留，仅统一文件末尾空白 |
| 参考文献 | 12条原引用转换为BibTeX，另收录语料中的6篇 | 原稿及已核对语料清单 | 原引用键、正文引用顺序与已有元数据 |

检查见 [structure_check.json](../../../paper/checks/structure_check.json)：59个编号公式、全部原标签和引用保留，无未定义引用；编译状态另记于 [compilation.json](../../../paper/checks/compilation.json)。

## 此前的单文件初稿改写记录

2026-10-09。以下记录对应拆分前的单文件版本；此前快照及SHA256见source_snapshot/，拆分前完整稿位于 [history/](../../../paper/history/phase4_sections_20261008)。

| 段落组 | 改写与组织 | 语料证据 | 保留的技术内容 |
|---|---|---|---|
| II-A 接入与活动 | 场景、块假设、活动边缘按依赖顺序引入 | C02 II；C08 II-A | 原activity-generation与geometry标签 |
| II-A 几何与阵列 | 合并RF/多普勒符号解释；阵列式后说明未知量 | C10 II-B/C | 原正相位约定、未归一化UPA、共同方向与Doppler |
| II-B 波形到算子 | 先给连续基，再给延迟采样；长式换行 | C07 III-A–D；Huang技术依据 | 原DAFT、跨周期CPP、连续延迟与整数极限全部保留 |
| II-C 观测 | 导频、帧间相位、张量索引、MMV矩阵相接 | C08 III；C05 II-B/C | Y/A/X形状、已知有效相位、公开噪声、相干叠加SNR |
| II-D 后验 | 在一个段落交代工作先验近似；随后直接给目标 | C08 III-B；C01 II/III | 物理条件联合先验与独立边缘的区别 |
| III-A 线性模块 | 输入高斯、条件矩、外信息、SVD按计算依赖排列 | C01 III-A；C11 IV-B | 原linear系列标签；正精度条件 |
| III-B 局部推断 | 补上显式局部后验和精确混合矩，再接有限网络接口 | C09 III-C；C01 III-B | 新local-posterior/local-activity/exact-local-moments；旧site和联合矩 |
| III-C 反馈 | 单独组织平均迹、方差比和外信息；解释clipping的量 | C01 III；C06 III-C | 原非线性外信息方程 |
| IV-A score均值 | 按扰动密度、Tweedie、损失、读数展开 | C03 III-A；C12 §4.1 | 原v/2系数；实方差改记v_R避免与物理ν混用 |
| IV-B 条件误差 | 把有限均值的条件MSE解释集中为一段推导 | C01 IV-C；C13 §4.2 | 原平均后平方、风险分解；补显式共享误差目标 |
| IV-C 活动密度比 | 给BCE点态最优解和一次先验修正 | C14 §3/4.2 | 同一噪声律、完整R、冻结均值特征、先验odds关系 |
| IV-D 训练 | 写输入/输出、数据生成和训练依赖；配置数值移出 | C02 III-C；C03 III；C04 VI-A | 完整R/F特征；log v/5改写log v/c_v，c_v=5移入VI准备 |
| V-A 调度 | 完整伪代码只引用公式；说明支持范围与site保留 | C05 III-B；C04 V-D；C08 Algorithm1 | 当前分类器使用当前查询；越界高斯回退；输出缩放 |
| V-B 停止 | 使用当前实现的分离门限、独立计数和硬判决窗口 | C01 V-B；项目iterations/denoiser源码 | 没有把历史单一门限写成现行规则；η、ζ及门限用符号 |
| V-C 成本 | 按实际SVD、空间矩阵运算及3网络调用计数 | C04 V-E；C06 IV-B | 原复杂度量级；不借用特定DFT结构的FFT成本 |

数学变化均为等价重排、显式补出已存在推导、无冲突符号替换，或将已有固定设置写成在VI赋值的参数。原52个方程标签全部保留；正文新增7个带标签方程。以静态检查文件的计数为准。旧的手工6a/8a/25a标签改为连续自动编号，Markdown从同一TeX源生成。

文字自查按对象、操作、结论逐段检查：未写性能领先或实验已完成的句子；模型近似集中说明；没有复制参考论文的长句。术语表中的标准词沿用原文；当前共享误差和停止操作用公式描述。
