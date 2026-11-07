# 已预补偿卫星随机接入的前导码检测：已有覆盖与可研究的问题

调研截止：2026-11-05。本文讨论独立选题，不变更现有 AFDM-GFRA 稿件、模型或实验主线；按用户要求，不评估工作量与研究周期。

## 摘要

本文考察保留普通前导码、终端已进行时间和频率预补偿时，卫星有授权随机接入的前导码检测是否仍有研究价值。主范围是 NR 四步竞争随机接入中的 Msg1，以 NB-IoT NPRACH、地面蜂窝接入和不依赖 GNSS 的卫星接入为相邻证据。公开文献已经覆盖非正交前导的干扰消除、频偏下的统计检测与峰验证、卫星前导碰撞检测及人数估计，并将检测结果用于后续接入控制。因此，“普通 ZC + 卫星 + 异步 + 学习检测”不是足够具体的创新。仍值得研究的是：在真实补偿误差、用户间功率不平衡及受阵列几何约束的信道条件下，如何可靠地区分弱用户、同前导碰撞和单用户产生的多个响应，并给出可用的定时估计。本文提出两项有文献依据的研究假设，同时指出它们尚须通过强基线比较才能确认为创新点。

## 1. 问题范围与调研方法

本文沿用讨论中的 GBRA，指先发送随机接入前导、再获得上行授权的接入流程，具体分析 NR 四步竞争随机接入。Msg1 在获得该次接入的上行授权之前发送，因此“后续数据有授权”不意味着前导已经完全同步。免竞争随机接入、免授权数据传输与这里的任务不同。

调研回答三个问题：

1. UE 已预补偿后，还剩什么值得检测器处理的不同步？
2. 传统、模型驱动、学习与碰撞检测分别已经做到什么程度？
3. 保持现有前导码时，哪些改进值得继续，哪些已明显重复？

检索从规范、传统检测、学习与碰撞处理三个视角独立展开，随后补查近远效应、空间相关、多星合作和最新论文版本。纳入 16 篇代表性研究作为主要或相邻证据，另登记 1 篇只完成作者元数据核验的高度相关论文。范围以截至本日期可检索的公开资料为准，不声称穷尽所有数据库。

优先核对出版社、官方规范、作者预印本及机构库。全文证据用于判断模型假设；仅取得摘要的文献，只用于确认其研究主题与明确宣称的贡献。“未见报告”不等于“原文没有做”。详细版本与证据边界见[核查记录](../../reference/reviews/ntn_gbra_preamble_20261105/VERIFICATION.md)。

## 2. 预补偿后的问题应怎样定义

### 2.1 从原始传播差异转向残余误差

需要分清三个条件：

| 条件 | 接收端面对的主要时频不确定性 | 是否属于本文默认场景 |
|---|---|---|
| 无个体补偿，或只补偿公共部分 | 波束内用户几何差异仍可很大 | 相邻场景 |
| UE 基于自身位置与卫星信息做个体补偿 | 位置、星历、时钟、跟踪和实现误差造成的残余量 | 是 |
| 已完成接入并进行闭环跟踪 | 调度、更新间隔与跟踪误差 | 相邻场景 |

因此，不能一方面假设有效的 UE 个体预补偿，另一方面直接把补偿前的毫秒级差分时延和数十 kHz 多普勒作为正常残余输入。需要从误差来源推导残余范围；超出该范围的情形应标为补偿失效或压力测试。

TS 38.300 v17.6.0 §16.14.2.1–2 将有效 GNSS 位置、星历与 Common TA 作为该版本 NTN 上行预补偿的前提；已知相关信息无效时要求停止发射直至恢复。因此，“辅助信息已失效仍持续发送”不能当成这个规范下的正常工作状态。TS 38.211 v17.6.0 §6.3.3.2 则规定 PRACH 的配置发送时域资源。[TS 38.300，pp.178–180](https://www.etsi.org/deliver/etsi_ts/138300_138399/138300/17.06.00_60/ts_138300v170600p.pdf)；[TS 38.211，pp.53–54](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/17.06.00_60/ts_138211v170600p.pdf)

以残余频偏为例，归一化量为

\[
\epsilon_k=\frac{\Delta f_{\mathrm{res},k}}{\Delta f_{\mathrm{PRACH}}}.
\]

同样的 200 Hz，对 1.25 kHz 和 15 kHz 的 PRACH 子载波间隔分别是 0.16 和约 0.0133。这只是单位换算，说明频偏数值必须与所用格式一起报告。

TS 38.101-5 v17.6.0 §6.4.1 的 ±0.1 ppm 是相对理想预补偿参考的 UE 载频精度要求；在 2 GHz 下换算为 ±200 Hz，但不能直接解释为接收端所有残余误差之和的统计分布。TS 38.108 v17.6.0 §8.4 的 PRACH 测试另给出 200 Hz 频偏条件。规范测试、器件精度和现场误差分布是三个不同对象。[UE 射频要求](https://www.etsi.org/deliver/etsi_ts/138100_138199/13810105/17.06.00_60/ts_13810105v170600p.pdf)；[卫星接入节点要求](https://www.etsi.org/deliver/etsi_ts/138100_138199/138108/17.06.00_60/ts_138108v170600p.pdf)

在此定义下，值得研究的是配置接入机会内的残余不同步，而不是默认采用任意时刻到包的无时隙模型。是否跨接入机会泄漏，需要由所选格式、保护时间和补偿误差共同决定。

### 2.2 五种结果不能互相替代

| 结果 | 接收机回答的问题 |
|---|---|
| 前导存在检测 | 某个前导是否被发送 |
| 定时/频偏估计 | 所检出信号还需要多少同步修正 |
| 碰撞检测或人数估计 | 同一前导是否有多个发送者，可能有几个 |
| UE 身份识别 | 发送者具体是谁 |
| 接入成功 | 后续授权与消息交换是否完成 |

竞争前导来自公共集合，前导索引本身不唯一标识 UE。检测出同一前导有两个发送者，也不自动得到两个可分别寻址的 UE。额外候选的物理层可检测性、RAR 的表达方式和 Msg3 是否成功，需要分别论证。Lee 等的方案正是同时设计检测和后续发送规则，而非仅提高一个相关峰检测概率。[Lee 等，§III–IV](https://arxiv.org/html/2512.07053v3)

## 3. 文献按接收机任务分类

| 主任务 | 代表工作 | 已建立的研究基础 |
|---|---|---|
| 检出前导并抑制干扰 | Wang 2017；Jeong 2023；Alarcón-Martín 2026 | 多用户干扰消除、频偏下的统计门限与峰处理 |
| 处理到达窗口与候选峰歧义 | Mirage 2026；Khaleghi 2026 | 动态观测窗口、多假设检测、模型与残差验证 |
| 检测碰撞及其对接入的影响 | Jang 2021；Jeong 2025；Lee v3；Jeong–Yun 2026 | 学习分类、多门限、碰撞人数和多星观测 |
| 相邻场景中的同步与学习 | Li Zhen 2024；Mohammadi 2021；Chougrani 2022；Lin 2025 两篇；Aït Aoudia 2022；Zhu 2024 | CFO 估计、空间合并、NPRACH 时频估计、无 GNSS 接入 |

这里按主要输出分类；一篇工作可能同时涉及多个输出。是否解决“完全重叠同前导用户的分离”需要另查，不能由“multiuser”一词直接推断。

## 4. 传统与模型驱动方法已经覆盖到哪里

表中条件用于解释适用边界，不是把所有边界都当作现成创新点。

| 工作 | 已核实的内容 | 对本选题的约束 |
|---|---|---|
| Wang、Ren、Wu，SINC 2016 / 出版 2017 | EIPIC 针对空间信息网 LTE 随机接入的多用户干扰和近远效应；采用信号重构与并行消除。原始摘要已核 | “卫星前导 + 干扰消除 + 近远效应”早有研究，不能只增加 SIC/PIC |
| Jeong、Hong，TVT 2023，TSPD | 两阶段重构、消除和迭代检测非正交前导，并分析检测性能。原始摘要已核 | 非正交 ZC 的卫星检测已有直接基线 |
| Alarcón-Martín 等，TWC 2026 | 多用户、多 root、多天线及重复发送；分析 PDP 分布，按 CFO 相关峰结构与跨 root 干扰设计检测。全文 §III 明示理想开环功控、时间对齐和平坦 Rayleigh | 不能把 CFO 感知门限或伪峰抑制本身作为新点；残余定时、多径及功率差异的联合影响仍需单独验证 |
| Georganaki 等，Mirage，OJCOMS 2026 | 动态观测窗口与多假设检测，面向无定位信息、大差分时延及多用户；实验含部分重叠和功率差 | 已覆盖“扩大窗口做异步多用户检测”；主要动机与完整 UE 个体预补偿不同 |
| Khaleghi、Lucidarme，Electronics 2026 | 根据 TA/CFO 候选，以模型投影和残差验证相关峰；正式版 §6.2 明确强重叠多用户联合处理超出范围 | “利用模型剔除 CFO 伪峰”已有先例；多用户叠加与单用户模型失配的区别值得进一步研究 |

来源：[Wang 等](https://link.springer.com/chapter/10.1007/978-981-10-4403-8_10)；[TSPD](https://yonsei.elsevierpure.com/en/publications/two-stage-preamble-detector-for-leo-satellite-based-ntn-iot-rando/)；[CFO-Robust Detection 全文](https://arxiv.org/html/2512.03096v1)；[Mirage 作者稿](https://orbilu.uni.lu/handle/10993/68160)；[Model-Consistency-Based Peak Validation](https://www.mdpi.com/2079-9292/15/13/2798)。

这些工作的差别比“传统算法还是 AI”更关键：Alarcón-Martín 等重点建立可分析的检测统计量，Mirage 处理跨窗口到达造成的响应歧义，Khaleghi–Lucidarme 验证一个发送者引出的多个候选。它们都可作为候选接收机的组成部分或对照，但任务和假设并不相同。

Mirage 尤其不能被简单归为“只测无碰撞”：其 40 UE 测试包含成对重叠及 3 dB 差异；另一方面，128 UE 示例中相同 root 的用户分置帧的不同部分，作者亦讨论紧密重叠与多径的混淆。这支持研究分辨条件，却不能支持“已有方法没有考虑多用户”的论述。[Mirage，§V-E/F](https://orbilu.uni.lu/bitstream/10993/68160/1/Mirage_Detector_A_Reliable_Multiuser_Preamble_Detector_for_6G-NTN.pdf)

## 5. 碰撞检测和学习方法已经覆盖到哪里

| 工作 | 已经做了什么 | 核查后保留的边界 |
|---|---|---|
| Jang 等，TWC 2021 | 学习前导及 TA 分类，用于蜂窝碰撞处理，并评价接入性能 | 地面相邻先例；本轮只核原始摘要 |
| Jeong、Lee、Hong，TVT 2025，MT-eCD | 利用 NTN LoS 特性、多门限和多 root 前导提前检测碰撞 | 直接 NTN 先例；仅据摘要不能判断全部残余误差设置 |
| Lee 等，arXiv:2512.07053v3，2026-06-02 | UE 时间/频率预补偿，短 ZCZ，多天线相关特征输入 CNN，估计碰撞人数，再辅助 Msg3 发送；Fig.12 含最大残余频偏 250 Hz | 与本问题最直接重合；全文未见阵列几何、空间协方差及逐用户功控误差的专项联合验证，不能据此声称其实际不鲁棒 |
| Jeong、Yun，TAES 2026 / online 2025，ISC-eCD | 利用服务卫星与邻星接收的 RTT 差提前判断碰撞，并设计 ZCZ | 增加多星观测信息也有先例；原始摘要已核 |

来源：[Jang 等](https://repository.sutd.edu.sg/esploro/outputs/journalArticle/Deep-Learning-Based-Cellular-Random-Access-Framework/9911076409846)；[MT-eCD](https://ieeexplore.ieee.org/document/10938640/)；[Lee v3 全文](https://arxiv.org/html/2512.07053v3)；[ISC-eCD](https://ieeexplore.ieee.org/document/11251216/)。

Lee v3 已展示双用户响应分离、相长合并和相消等情况，因此不能批评它只认识两个分离峰。可以提出、但尚未得到实验回答的问题是：其判断在多大程度上依赖已训练的功率、信道和空间统计？保持碰撞人数不变而改变这些统计时，错误是否集中于某些可解释的条件？这比给模型增加一个新的 SNR 曲线更接近研究问题。

其正文还援引约 10 Hz 的残余频偏，但引用的是 MediaTek 的 RAN1 会议贡献 R1-2100601。本次未取得该贡献原文，不能将此数值提升为通用 3GPP 规范要求；250 Hz 在本文仅作为该论文采用的压力测试上限。

另有 Li Zhen 等 2025 年 TITS 的轻量 Transformer 碰撞检测与负载估计论文。作者元数据已核，出版社全文和原始摘要未取得，因此只列为必须补读的重合风险，不对其模型缺口作结论。[作者发表记录](https://sites.google.com/view/dr-chinmay-chakraborty/publications/journals)

## 6. 相邻领域排除了哪些宽泛创新

| 相邻研究 | 能支持的判断 | 不能直接移植的地方 |
|---|---|---|
| Li Zhen 等，WCL 2024 | NTN 中利用 PDP 结构、聚类与神经网络估计 CFO 已有工作 | 其单用户大 CFO 设置，不等于完整预补偿后的多用户残余误差问题 |
| Mohammadi 等，WSA 2021 | 用学习方法做空间/时间相干合并已经存在 | 地面阵列和信道条件不自动覆盖卫星共角度 LoS |
| Chougrani 等，JIOT 2022 | 保留 NPRACH 波形进行 NTN 前导检测与上行同步已有基础 | NPRACH 跳频结构不同于 NR ZC PRACH |
| Lin，JIOT 2025，统一 RA | 公共时延/频偏补偿、匹配滤波器组及联合最大似然框架已有工作 | 无 GNSS / 公共补偿条件，与 UE 个体预补偿不同 |
| Lin，JIOT 2025，残余误差估计 | 正式摘要明确在完成 NPRACH 检测后，以 rake/相关器组联合估计残余时频误差 | 不能当成同前导碰撞已经消解 |
| Aït Aoudia 等，GLOBECOM 2022 | 学习 NPRACH 活动检测、ToA 和 CFO 的联合输出已有公开实现 | 原文明示无 hopping-pattern 碰撞假设 |
| Zhu、Sun、Peng，TVT 2024 | 无 GNSS 的 TA 估计、预补偿和前导设计已有研究 | 修改前导结构，不属于本文默认的现有前导接收机改进 |

来源：[Clustering-NN](https://openresearch.surrey.ac.uk/esploro/outputs/journalArticle/Clustering-NN-Based-CFO-Estimation-Using-Random/99830666402346)；[Blind Coherent Detection](https://arxiv.org/html/2110.02738v1)；[Chougrani 等](https://arxiv.org/html/2101.08079v2)；[Lin：统一 RA](https://scholars.ncu.edu.tw/en/publications/a-unified-random-access-procedure-for-an-nb-iot-protocol-in-nonte/)；[Lin：残余误差](https://scholars.ncu.edu.tw/en/publications/estimation-of-residual-frequency-and-time-errors-on-nprach-in-non/)；[Aït Aoudia 等](https://arxiv.org/html/2205.10805v2)；[Zhu 等](https://arxiv.org/html/2404.08960v1)。

上述对照意味着，联合输出检测/时延/频偏、增加天线学习合并或引入更精细搜索，本身都不是足够的创新。需要解释在目标观测条件下究竟增加了什么有效信息，或消除了哪一种既有接收机的系统性错误。[NVIDIA 的 NPRACH 代码](https://github.com/NVlabs/nprach_synch)可帮助核查联合学习方法，但不能作为 NR 波形不经适配的直接数值基线。

## 7. 综合判断：真正值得处理的矛盾

预补偿改善同步，却也可能缩小同前导用户之间的时延与频偏差异。前者帮助检测，后者可能减少碰撞分辨可利用的信息。这是一个依赖信道和接收观测的条件性判断，不能推成“预补偿越准，性能必然越差”。

用一个最简单的例子说明信息边界：两个用户发送相同前导，残余时延、频偏完全相同，其复增益未知，则

\[
y(t)=h_1s(t-\tau)e^{j2\pi\nu t}
     h_2s(t-\tau)e^{j2\pi\nu t}+w(t)
     =(h_1+h_2)s(t-\tau)e^{j2\pi\nu t}+w(t).
\]

如果允许单用户具有任意未知复增益，这个观测也可以由一个用户产生；多天线下，把增益换成任意未知信道向量，仍有同样问题。这是上述模型的直接推导，不是新提出的定理。统计信道或功率先验仍可能支持概率分类，但不能据此获得所有参数下的确定性用户计数保证。

因此，应优先问：真实的残余时延差、频偏差、阵列角度差和多径结构，在什么条件下提供足够信息？功控误差是否使一个强用户与两个弱用户的统计特征混淆？检测器能否在可分辨时改善，在不可分辨时避免高置信误判？

这个问题同时连接了 Lee 的碰撞分类、Mirage 的到达分离和 Khaleghi 的候选验证，但尚未由“把三个模块接起来”自动解决。方法贡献必须来自明确的观测模型、判决统计量或估计机制。

## 8. 两项值得验证的研究方向

### 8.1 优先方向：功率不平衡和残余不同步下的同前导碰撞检测

建议工作题目：

**《面向预补偿 LEO 卫星随机接入的同前导碰撞检测与残余定时估计》**

这里的核心研究问题是：在保持现有 ZC 前导和预补偿机制时，能否在功率不平衡、强相关 LoS 和多径响应共同存在的条件下，更可靠地判断一个前导对应一个还是多个发送者，并给出可信的定时结果？

可以从以下操作构造方法，而不预先给组合起新名称：

1. 保留各天线、各个已有重复段的复相关结果，建立一个用户多径与多个用户叠加的候选模型。只能使用实际格式具有的重复；新增重复属于资源改变。
2. 把未知接收功率、残余时频误差和允许的信道参数放入估计或积分过程，不固定为每个 UE 完全等功率，也不把真实活跃人数作为输入。
3. 联合比较候选能否解释主要响应与剩余响应；避免仅凭峰个数或总能量决定人数。单用户允许的多径范围必须有物理依据，否则其自由度可吸收另一个用户。
4. 输出前导存在、碰撞判断和相应定时可信度；对无法支持精确人数的观测，不把硬分类准确率当成唯一目标。

上面是研究方案，尚无仿真结果。GLRT、最大似然、贝叶斯估计、神经网络及信号重构都是既有工具，创新要落在：候选模型如何区分两类响应、哪些信息真正有用，以及如何在失配下控制漏碰撞和假碰撞。

**最近的对照必须包含 Lee v3 和 MT-eCD；涉及复相关/空间合并时还应对照 Mohammadi 的思路。** 不能只与固定相关门限相比。需要先检验功控、空间统计和残余误差变化是否确实造成既有方法的实质退化；如果没有，选题的这一动机就不成立。

### 8.2 如果重点是“检出每个前导”：弱用户检测与 CFO 伪峰联合处理

建议工作题目：

**《残余时频偏差与多用户干扰下的卫星 PRACH 检测》**

需要聚焦的错误是：强用户的相关副响应、跨 root 干扰或不准确的干扰重构，掩盖弱用户，或者让检测器把真实弱峰删除。单纯增加非理想功控或换 NTN 信道只能构成测试条件。

一个可检验的方案是：同时估计残余频偏与有效干扰统计；在验证强用户候选后再重构其完整响应；通过包含弱用户的联合假设检验决定是否保留弱峰，避免只按强峰周围固定距离规则删除候选。门限应在实际搜索空间与干扰条件下校准，不能用已知真实干扰功率实现一个不可部署的优势。

最近对照是 Alarcón-Martín 2026、TSPD、Mirage 以及候选验证方法。Mirage 已有功率差和重叠测试，Wang 2017 已处理近远效应，因此创新必须进一步具体到错误来源、判决机制及有代表性的剩余工作区间。

两条方向可以共享前端，但对应指标不同：第一条关心同一前导是否碰撞，第二条关心不同候选的存在检测及定时。不要在同一条性能曲线中混合计分。

### 8.3 暂不宜作为核心贡献的表述

| 宽泛表述 | 判断 |
|---|---|
| 将 CNN 用于预补偿 NTN 前导检测/碰撞人数估计 | 直接重合已有研究 |
| 增加残余 CFO 后重新训练 | Lee v3 已有残余 CFO 测试；必须进一步解释新错误机制 |
| 将相关门限改为自适应门限、GLRT 或加入 SIC | 相应工具和直接应用已广泛存在 |
| 用更多天线、学习合并权重 | 需证明实际阵列提供新的可分辨信息 |
| 多星接收辅助碰撞检测 | ISC-eCD 已有直接先例 |
| 从 NPRACH 联合同步换成 NR PRACH | 波形迁移需要新的推导和实质结果，名称变化不是创新 |
| 保留完整预补偿假设，却用未补偿的大时延/大频偏制造优势 | 模型不自洽；只能另定义补偿失效场景 |

## 9. 什么证据足以决定继续研究

### 9.1 先建立可比的评估条件

固定前导格式、带宽、时长、重复数、可用前导数量、接收天线数与发射能量。改变资源或 RAR/Msg3 规则的方案单独比较。设置正常补偿、较差补偿与补偿失效三类条件；后者的收益不能替代正常条件下的价值。

至少分开检查无碰撞、不同前导干扰、相同前导两个及以上用户。连续改变用户间时延差、频偏差、功率比和角度差，而不是只改变总体 SNR。阵列相关性应从阵列几何或有依据的信道模型产生；不能默认卫星接收端能获得每个天线的独立数字基带观测。

所有接收器获得同一组可用信息。真实 CFO、真实信道、真实用户数或真实误差分布只允许作为明确标记的 oracle 对照。

### 9.2 指标要回答接入接收机的问题

| 指标 | 必须交代的定义 |
|---|---|
| 检测率和漏检率 | 是否同时要求前导正确与定时误差合格 |
| 虚警率 | 噪声条件下整个接入机会的虚警，还是有其他用户时对未发送前导的误报 |
| 碰撞漏报/误报 | 分别以真实多用户和真实单用户为条件，不能混作普通噪声虚警 |
| 人数估计 | 各人数的混淆矩阵，特别是把碰撞判为单用户 |
| 定时/频偏误差 | 同时给正确关联后的误差及漏检/错关联比例，避免只对成功样本报很小 RMSE |
| 接入收益 | 若声称减少接入时延，需包括 RAR/Msg3 的可执行规则和失败重试 |
| 复杂度 | 相同搜索域和硬件条件下的运算量或时间 |

TS 38.108 的 PRACH 正确检测要求包括正确前导及最强路径定时误差条件；不能只计“某个位置超过门限”。其噪声虚警要求与在强干扰条件下误检另一个前导也应分别验证。[TS 38.108，§8.4](https://www.etsi.org/deliver/etsi_ts/138100_138199/138108/17.06.00_60/ts_138108v170600p.pdf)

### 9.3 继续或收缩选题的依据

值得继续的证据是：在有出处的残余误差区间、相同资源和相同虚警目标下，强基线出现稳定且可解释的错误；改进能针对该机制降低漏检、错误定时或碰撞漏报，并在分布变化后保留收益。

应收缩或更换动机的证据是：增益只在不合理的大残差、额外天线/能量、已知真值参数、明显较弱的基线或协议无法使用的输出上出现；或者所谓多用户可分辨性完全来自训练时固定的用户功率。

这不是给选题额外设置形式要求，而是决定“研究问题成立”和“算法曲线变好”是否指向同一件事。

## 10. 对三个问题的回答

**RQ1：有残余异步，但应按补偿后的误差建模。** GBRA 不消除 Msg1 的同步需求；有效的个体预补偿却会改变问题量级，不能直接沿用无补偿的大差分场景。

**RQ2：已有工作相当具体。** 研究已推进到多用户干扰处理、时频估计、候选峰验证、碰撞人数以及后续接入收益，普通前导和学习检测都有直接先例。

**RQ3：仍有值得研究的问题，但不能仅凭场景命名确认创新。** 优先考察同前导碰撞在功率、空间和残余同步条件变化下的可分辨性与可靠判决；若只做常规存在检测，则聚焦弱用户与伪峰/干扰的联合处理。两者都需要先找出强基线在真实条件下尚未解决的具体错误。

我的建议是保留“普通前导 + UE 预补偿”的系统边界，把问题收紧到上述第一项；若不处理碰撞，则选择第二项并明确其检测对象。无需为形成课题而强行引入 AFDM，也不应在验证前宣称已经找到文献空白。

## 参考文献与阅读入口

1. Q. Wang, G. Ren, J. Wu, “Multiuser Detection for LTE Random Access in MTC-Oriented Space Information Networks,” SINC 2016, CCIS 688, pp.104–116, 2017. DOI 10.1007/978-981-10-4403-8_10。[出版社](https://link.springer.com/chapter/10.1007/978-981-10-4403-8_10)
2. J. Jeong, D. Hong, “Two-Stage Preamble Detector for LEO Satellite-Based NTN IoT Random Access,” IEEE TVT 72(11), pp.14443–14455, 2023. DOI 10.1109/TVT.2023.3285875。[作者机构](https://yonsei.elsevierpure.com/en/publications/two-stage-preamble-detector-for-leo-satellite-based-ntn-iot-rando/)
3. D. Alarcón-Martín et al., “CFO-Robust Detection for 5G PRACH Under Fading Channels: Analytical Modeling and Performance Evaluation,” IEEE TWC 25, pp.15565–15581, 2026. DOI 10.1109/TWC.2026.3684221。[正式记录](https://ieeexplore.ieee.org/abstract/document/11493644)；[作者全文](https://arxiv.org/html/2512.03096v1)
4. A. Georganaki et al., “Mirage Detector: A Reliable Multiuser Preamble Detector for 6G-NTN,” IEEE OJCOMS, 2026. DOI 10.1109/OJCOMS.2026.3679839。[作者稿与机构记录](https://orbilu.uni.lu/handle/10993/68160)
5. H. Khaleghi, T. Lucidarme, “Model-Consistency-Based PRACH Peak Validation Under Large Carrier Frequency Offsets,” Electronics 15(13), 2798, 2026. DOI 10.3390/electronics15132798。[正式全文](https://www.mdpi.com/2079-9292/15/13/2798)
6. H. S. Jang et al., “Deep Learning-Based Cellular Random Access Framework,” IEEE TWC 20(11), pp.7503–7518, 2021. DOI 10.1109/TWC.2021.3085303。[作者机构](https://repository.sutd.edu.sg/esploro/outputs/journalArticle/Deep-Learning-Based-Cellular-Random-Access-Framework/9911076409846)
7. J. Jeong, H. Lee, D. Hong, “Enhanced Early Preamble Collision Detector for LEO Satellite-Based NTN IoT Random Access,” IEEE TVT 74(8), pp.12496–12511, 2025. DOI 10.1109/TVT.2025.3554531。[出版社](https://ieeexplore.ieee.org/document/10938640/)
8. H. Lee et al., “Random Access for LEO Satellite Communication Systems via Deep Learning,” arXiv:2512.07053, 2025；采用 v3，2026-06-02。当前核验为预印本。[全文](https://arxiv.org/html/2512.07053v3)
9. J. Jeong, S. Yun, “Intersatellite Cooperation for Early Preamble Collision Detection in NTN IoT Random Access,” IEEE TAES 62, pp.2151–2165, 2026，online 2025-11-18. DOI 10.1109/TAES.2025.3634485。[出版社](https://ieeexplore.ieee.org/document/11251216/)
10. Li Zhen et al., “Clustering-NN-Based CFO Estimation Using Random Access Preambles for 5G Non-Terrestrial Networks,” IEEE WCL 13(3), pp.587–591, 2024. DOI 10.1109/LWC.2023.3333810。[作者稿入口](https://openresearch.surrey.ac.uk/esploro/outputs/journalArticle/Clustering-NN-Based-CFO-Estimation-Using-Random/99830666402346)
11. J. Mohammadi et al., “Blind Coherent Preamble Detection via Neural Networks,” WSA 2021, pp.1–6。[作者全文](https://arxiv.org/html/2110.02738v1)
12. H. Chougrani et al., “NB-IoT Random Access for Nonterrestrial Networks: Preamble Detection and Uplink Synchronization,” IEEE JIOT 9(16), pp.14913–14927, 2022. DOI 10.1109/JIOT.2021.3123376。[作者全文](https://arxiv.org/html/2101.08079v2)
13. J.-C. Lin, “A Unified Random Access Procedure for an NB-IoT Protocol in Nonterrestrial and Terrestrial Networks,” IEEE JIOT 12(3), pp.3424–3440, 2025. DOI 10.1109/JIOT.2024.3481064。[作者机构](https://scholars.ncu.edu.tw/en/publications/a-unified-random-access-procedure-for-an-nb-iot-protocol-in-nonte/)
14. J.-C. Lin, “Estimation of Residual Frequency and Time Errors on NPRACH in Nonterrestrial Networks,” IEEE JIOT 12(15), pp.29961–29974, 2025. DOI 10.1109/JIOT.2025.3569434。[正式摘要与元数据](https://scholars.ncu.edu.tw/en/publications/estimation-of-residual-frequency-and-time-errors-on-nprach-in-non/)
15. F. Aït Aoudia et al., “Deep Learning-Based Synchronization for Uplink NB-IoT,” GLOBECOM 2022, pp.1478–1483. DOI 10.1109/GLOBECOM48099.2022.10001353。[作者页面](https://research.nvidia.com/publication/2022-12_deep-learning-based-synchronization-uplink-nb-iot)；[全文](https://arxiv.org/html/2205.10805v2)
16. J. Zhu, Y. Sun, M. Peng, “Timing Advance Estimation in Low Earth Orbit Satellite Networks,” IEEE TVT, 2024. DOI 10.1109/TVT.2023.3325328。[作者全文](https://arxiv.org/html/2404.08960v1)

补读条目（仅作者元数据已核，不作为全文缺口证据）：Li Zhen et al., “A Lightweight Transformer-Based Collision Detection and Load Estimation Scheme for Massive Random Access in 6G Satellite-Ground Integrated Vehicular Networks,” IEEE TITS 26(10), pp.17638–17652, 2025. DOI 10.1109/TITS.2025.3527073。[作者记录](https://sites.google.com/view/dr-chinmay-chakraborty/publications/journals)；[出版社入口](https://ieeexplore.ieee.org/document/10847604/)。

本地资料：[研究问题与范围](D:/afdm-gfra/reference/reviews/ntn_gbra_preamble_20261105/BRIEF.md)；[版本和证据核查](D:/afdm-gfra/reference/reviews/ntn_gbra_preamble_20261105/VERIFICATION.md)。未开展实验；报告中的研究方案和性能预期均待验证。
