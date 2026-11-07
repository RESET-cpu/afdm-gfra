# 版本、来源和判断边界

核查日期：2026-11-05。本次为文献调研，没有进行仿真、训练、方法复现或实际系统测试。用户明确要求不评估工作量。

## 检索方法

三个独立视角为：官方规范与补偿误差、传统及模型驱动检测、学习检测与碰撞处理。综合后补查功控误差、空间相关、同前导碰撞、多星协作，以及最新期刊版本。搜索使用公开网络检索；判断依据优先采用规范、出版社、作者预印本与作者所属机构页面。不是覆盖全部数据库的系统综述，不以搜索未命中证明不存在相关研究。

代表性检索组合：NTN PRACH precompensation residual timing frequency error；satellite grant-based random access preamble detection；preamble collision power control imperfect；preamble collision spatial correlation NTN；PRACH collision multipath frequency offset joint detection；satellite random access near-far preamble；Intersatellite Cooperation for Early Preamble Collision Detection；Mirage Detector；Model-Consistency-Based PRACH Peak Validation。

## 影响结论的版本核查

1. [Lee 等 arXiv:2512.07053v3](https://arxiv.org/html/2512.07053v3)，2026-06-02。不能以 v1 缺少频偏实验为依据立题；v3 Fig.12 已测试最大残余频偏 250 Hz。全文未明确给出该误差的抽样分布和用户间相关性。§V 的开环功控目标与整体 SNR 扫描，不能替代用户间功控误差的独立验证；未见明确阵列几何/空间协方差，不据此断言作者采用独立天线。
2. [Alarcón-Martín 等完整预印本](https://arxiv.org/html/2512.03096v1)与[正式出版记录](https://ieeexplore.ieee.org/abstract/document/11493644)：TWC 25:15565–15581, 2026，DOI 10.1109/TWC.2026.3684221。技术判断定位于预印本 §III、§VI–VII；完美开环功控、时间对齐及平坦 Rayleigh 是原文明示条件。未逐字对比付费正式版全文。
3. [Khaleghi–Lucidarme 正式论文](https://www.mdpi.com/2079-9292/15/13/2798)，Electronics 15(13):2798, 2026。早期稿全文与正式网页相关章节交叉核对；正式版 §6.2 明确限制于候选峰验证，强重叠多用户联合处理超出范围。正式结果也没有显示所有信道/SNR 下都优于最大幅度判决，故不作普遍优越性结论。
4. [Mirage 作者接受稿与机构记录](https://orbilu.uni.lu/handle/10993/68160)，2026。采用 DOI 10.1109/OJCOMS.2026.3679839；作者稿首页另有未更新的 DOI 字段，不沿用。40 UE 实验含每对 3 dB 功率差；128 UE 示例将同 root 用户放在帧的不同部分，不能将其等同于 128 个完全重叠同前导用户的分离。正文承认紧密重叠可能与多径混淆。其协议描述不作为 3GPP 规范条款的替代依据。
5. [Li Zhen 等作者接受稿入口](https://openresearch.surrey.ac.uk/esploro/outputs/journalArticle/Clustering-NN-Based-CFO-Estimation-Using-Random/99830666402346)：WCL 13(3):587–591, 2024，DOI 10.1109/LWC.2023.3333810。原文第一作者写 Li Zhen。§II–IV 覆盖单用户大范围 CFO 估计；整数 CFO 估计后的 fractional CFO 不能混称为完整 GNSS 预补偿后的残余频偏。
6. [Lin 的 NPRACH 残余误差论文正式摘要](https://scholars.ncu.edu.tw/en/publications/estimation-of-residual-frequency-and-time-errors-on-nprach-in-non/)，JIOT 12(15):29961–29974, 2025，DOI 10.1109/JIOT.2025.3569434。早期预印本强调二维相关器；正式摘要明确为完成前导检测后的 rake 接收机与残余时频误差联合估计。本报告按正式摘要限定任务，不把早期摘要扩写成完整碰撞消解。

## 摘要级证据的使用限制

Mirage 的直接全文核查集中在作者稿 pp.1–4、19–22，并结合搜索索引中的相关段落；并非逐页完整精读。对 40/128 UE 设置及紧密重叠限制的判断定位在 §V-E/F，不能扩写为已复原其全部算法。

- Jeong–Hong 2023 TSPD、Jeong–Lee–Hong 2025 MT-eCD、Jeong–Yun 2026 ISC-eCD：出版社或作者机构摘要足以确认方法主题和已有覆盖；不足以断言原文完全没有某类功控、信道或残余误差实验。
- Jang 等 2021 蜂窝随机接入学习框架、Wang 等 2017 空间信息网多用户检测：原始机构/出版社摘要作为历史先例，不能据此完整复现其接收机。
- 只有取得作者稿或正式全文并核对相关章节时，才对模型假设和明确排除范围作具体判断。

## 不作为主线直接证据的研究

- NPRACH 跳频检测与 NR ZC PRACH 的观测结构不同；前者只能提供相邻领域方法与反例，不能原样横向比较数值。
- GNSS-independent / 仅公共补偿条件下的大差分时延，不等于 UE 已完成个体时间预补偿后的残余时延。
- 连接态闭环同步的硬件/过星验证，不证明 Msg1 多用户碰撞检测也完成了实际部署验证。
- AFDM、OTFS、HFM 和前导波形重设计不列为此次建议主线。
- 同前导、同残余时频参数、未知任意复信道下的不可区分示例是报告内的直接数学推导，不冒称已发表的新定理，也不据此否定有统计先验的碰撞分类性能。

## 判断纪律

“未见报告”与“作者没有做”分开；“可研究”与“已证明创新”分开；数值均标明其来源和定义；标准测试误差、终端精度要求和实际误差分布分开。没有声称新接收机已获得性能收益，也没有将论文中的 oracle 信息当成实际可用输入。

## 官方规范定位

- [TS 38.300 v17.6.0](https://www.etsi.org/deliver/etsi_ts/138300_138399/138300/17.06.00_60/ts_138300v170600p.pdf)：§16.14.2.1–2，pp.178–180，UE 预补偿、有效辅助信息及停止发射条件；§9.2.6，pp.96–98，随机接入流程。
- [TS 38.211 v17.6.0](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/17.06.00_60/ts_138211v170600p.pdf)：§6.3.3.1，p.47，ZC 前导构造；§6.3.3.2，pp.53–54，配置 PRACH 发送资源。
- [TS 38.101-5 v17.6.0](https://www.etsi.org/deliver/etsi_ts/138100_138199/13810105/17.06.00_60/ts_13810105v170600p.pdf)：§6.4.1，p.19，载频精度 ±0.1 ppm，1 ms 测量区间；Annex A.4，p.42，相关条件。
- [TS 38.108 v17.6.0](https://www.etsi.org/deliver/etsi_ts/138100_138199/138108/17.06.00_60/ts_138108v170600p.pdf)：§8.4，pp.52–53，PRACH 虚警、检测、定时容差与测试 CFO。NTN-TDLA100-200 中的 200 与另外列出的 200 Hz CFO 定义不同，不能合并。
- [TS 38.331 v17.6.0](https://www.etsi.org/deliver/etsi_ts/138300_138399/138331/17.06.00_60/ts_138331v170600p.pdf)：EphemerisInfo，pp.602–603；NTN-Config，pp.689–691。星历字段量化步长不是实际位置/速度误差保证；ntn-UlSyncValidityDuration 不是强制 GNSS 更新周期。

Lee v3 的约 10 Hz 引用链指向 MediaTek, UE Time and Frequency Synchronisation for IoT NTN, R1-2100601, RAN1 #104e, 2021。此为公司贡献文稿；原 ZIP 未取得。报告不把 10 Hz 写成统一规范要求或通用实际误差分布。
