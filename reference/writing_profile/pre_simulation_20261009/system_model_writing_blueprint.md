# 第二章论证蓝图

## II. System Model

2026-10-09，用户确认以 Shen 的“物理链路—传输—问题表述”组织第二章。当前正文位于 [02_system_model.tex](../../../paper/sections/02_system_model.tex)。该结构是本稿的组织选择，不作为期刊通用规定。

| 小节 | 段落顺序 | 文献依据 | 数学保护点 |
|---|---|---|---|
| 章首概述 | 免授权卫星上行、UPA、接入块与活动状态 | C05 §II开头；C01 §II-A | 非空条件ρ=p/[1−(1−p)^K]及块内不变假设 |
| A. Terrestrial-Satellite Link Model | 位置与Doppler；公共时延补偿；路径时延；UPA响应 | C05 §II-A标题与展开；C10 §II-A–C | RF、Doppler、UPA符号一致；共同空间响应假设 |
| B. Transmission Scheme | DAFT/CPP；连续波形；分数延迟算子；整数极限；完整H张量；导频与已知帧间相位；逐坐标接收关系；矩阵观测模型 | C05 §II-B；C02 §II式(1)–(5)及§III-A；C07 §II-B/III；Huang Eq.(5) | 完整延迟进入CPP相位；H含MN²坐标；A为Q×KN、Y为Q×MN、X为KN×MN；公开输入四项 |
| C. Problem Formulation | 归一化单位；候选信道分布；工作先验/后验；MMSE与活动判决目标 | C05 §II-C；C01 §II-B；C08 §III-B(13)–(17) | 物理条件先验与独立边缘近似只解释一次；高斯似然和delta约束完整 |

主文解释“为何需要这些变量/算子”；给所有符号尺寸。信号SNR的具体设置、数据量、网络尺寸留给VI准备记录。II结束时读者能独立确定未知量、已知量和估计目标。本次结构调整保留全部公式、符号、引用、模型假设和限定；III–V正文不变。章节核对材料见 [literature/section_structure_20261009/](../../reviews/section_structure_20261009)。
