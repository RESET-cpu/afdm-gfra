# 引言

低轨（LEO）卫星能够将物联网（IoT）连接扩展至地面网络覆盖范围之外的区域。大量终端间歇发送短分组的业务特征，使免授权随机接入（GFRA）成为卫星物联网的一种适用接入方式：活跃终端无需预先获得上行授权即可发送信号 [Shen2025]。在导频资源有限的条件下，接收机需要从非正交导频的叠加信号中识别活跃终端并估计其信道，由此形成联合活动检测与信道估计（JADCE）问题 [Liu2018]。在 LEO 上行链路中，卫星运动及覆盖区域内不同终端的传播距离差异，会引入用户相关的时延和多普勒频移，进一步增加导频接收的难度。

Release 17 的新无线电非地面网络（NR-NTN）框架假设终端具备全球导航卫星系统（GNSS）能力。终端利用自身的 GNSS 位置、卫星星历及公共定时提前信息，完成上行定时和频率预补偿 [3GPP38300，第 16.14.1 和 16.14.2.2 节]。对于低成本、电池供电的物联网终端，GNSS 信号获取及相关补偿过程会增加硬件和能耗需求 [Shen2025]，因此有必要研究不依赖终端 GNSS 辅助的 GFRA 方案。在本文考虑的场景中，系统补偿公共参考时延，剩余的差分时延和多普勒频移由卫星接收机处理。这些偏移可能分别超过一个符号周期和一个子载波间隔，因而需要在信号模型中予以保留 [Shen2025]。

面向双弥散信道的波形已被用于卫星随机接入。Shen 等提出基于扩频的多帧正交时频空（OTFS）传输方案，并设计联合设备识别、信道估计与符号检测接收机，以处理大差分时延和多普勒频移 [Shen2025]。仿射频分复用（AFDM）通过离散仿射傅里叶变换（DAFT）提供了另一种方案，其啁啾参数可根据信道的时延和多普勒扩展进行选择 [Bemani2023]。针对 AFDM 低轨卫星 GFRA，Ding 等利用图神经网络学习时延–多普勒网格节点之间的相关性，并据此细化用于 JADCE 的稀疏先验 [Ding2026]。

信道表示方式决定了接收机能够利用哪些相关性。离散时延–多普勒表示通过预设网格上的路径系数描述信道；分数时延和分数多普勒会使一条物理路径的贡献扩散至多个网格点，从而降低预设支撑的准确性 [Shen2025; Huang2026]。另一种方式是直接估计 AFDM 等效信道 [Huang2026]。在多天线系统中，每个终端的等效信道由一组共享路径时延、多普勒频移和阵列响应的矩阵组成。这些物理参数使矩阵元素之间以及接收天线之间具有相关性。学习其联合分布，可以在不预设离散路径支撑的情况下，将这些相关性用于信道估计。

基于得分的生成模型通过学习高斯扰动信道样本概率密度的对数梯度来表征信道先验。Arvinte 和 Tamir 将该类模型用于多输入多输出（MIMO）信道估计，并在推断时进行后验采样 [Arvinte2023]。针对 LEO AFDM 链路，Huang 等学习等效信道的得分函数，并采用似然退火 Langevin 动力学进行推断 [Huang2026]。为将生成先验用于 JADCE，Cai 等在 MIMO 正交频分复用（OFDM）系统中结合信道去噪与消息传递（MP）[Cai2026]。该接收机利用一阶和二阶得分网络，在每次迭代中获得信道矩估计，从而避免在线执行反向扩散采样。

在不依赖终端 GNSS 辅助的 AFDM 上行链路中，观测模型还需要考虑导频帧之间累积的未知相位增量。帧间相位增量影响感知矩阵，而帧内时延和多普勒效应包含在等效信道中。联合恢复终端活动状态与信道，还需要区分活跃和非活跃假设的依据。本文结合学习得到的信道矩与用于活动检测的密度比，使 MP 接收机能够利用完整多天线 AFDM 信道块的联合分布进行信道估计和活动检测。

本文研究面向不依赖终端 GNSS 辅助的多用户 MIMO-AFDM 卫星物联网的生成模型辅助免授权随机接入，其中单天线终端与配备均匀平面阵列（UPA）的 LEO 卫星通信。主要贡献如下。

1. 建立包含连续路径时延和多普勒频移的多帧 AFDM 上行模型。啁啾周期前缀（CPP）覆盖差分传播时延，模型将帧间相位演化与参考帧等效信道分离。通过堆叠接收导频，得到用于联合活动检测与完整多天线信道估计的多用户观测模型。

2. 设计用于 JADCE 的生成模型辅助 MP 接收机。线性估计器处理多用户导频观测，非线性去噪器结合学习得到的信道先验与终端活动模型。两个模块通过迭代交换外信息均值和方差，更新信道估计与活动概率。帧间相位增量与噪声方差在 MP 迭代前由接收导频估计。

3. 将完整多天线 AFDM 等效信道的学习先验引入非线性去噪器。利用两个得分网络获得信道均值估计和标量误差估计；另行训练分类器，估计活跃与非活跃观测之间的密度比 [Menon2016]，据此计算信道估计和输出消息所需的活动概率。给出相应的训练目标、消息调度及接收机计算复杂度。

在 500 个独立物理场景上的数值比较表明，在所测试的 −4～8 dB 信噪比（SNR）范围内，所提接收机的信道估计误差低于四种基线接收机，并在 −2～8 dB 范围内取得更低的活动检测错误率。

本文其余部分安排如下：第二节介绍系统模型与问题表述；第三节推导接收机；第四节介绍学习目标；第五节给出完整算法并分析其复杂度；第六节和第七节分别给出数值结果与结论。

## 引用对应

本对照稿使用作者–年份标记，正式引用编号以英文论文 PDF 为准。

- [Shen2025](https://arxiv.org/html/2412.20806v1)：LEO Satellite-Enabled Random Access With Large Differential Delay and Doppler Shift。
- [Liu2018](https://arxiv.org/abs/1706.06438)：Massive Connectivity With Massive MIMO—Part I: Device Activity Detection and Channel Estimation。
- [3GPP38300](https://www.etsi.org/deliver/etsi_ts/138300_138399/138300/17.02.00_60/ts_138300v170200p.pdf)：3GPP TS 38.300，V17.2.0，Release 17，第 16.14.1、16.14.2.2 节。
- [Bemani2023](https://arxiv.org/html/2204.12798v2)：Affine Frequency Division Multiplexing for Next Generation Wireless Communications。
- [Ding2026](https://doi.org/10.1109/TVT.2026.3729877)：Learning Sparsity Pattern: An Adaptive Joint Detection for AFDM Grant-Free System in LEO Satellites Communication。
- [Huang2026](https://doi.org/10.1109/LWC.2026.3689601)：Prior-Agnostic AFDM Channel Estimation for High-Mobility LEO Satellite Communications Using Diffusion Models。
- [Arvinte2023](https://arxiv.org/abs/2204.07122)：MIMO Channel Estimation Using Score-Based Generative Models。
- [Cai2026](https://arxiv.org/html/2506.00581v2)：Joint Activity Detection and Channel Estimation for Massive Connectivity: Where Message Passing Meets Score-Based Generative Priors。
- [Menon2016](https://proceedings.mlr.press/v48/menon16.html)：Linking Losses for Density Ratio and Class-Probability Estimation。
