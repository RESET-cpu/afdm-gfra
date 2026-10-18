# AFDM 基线的定义与论文依据

当前默认基线为 SOMP、GAMP-SBL（标识 `gamp_sbl_zhang2023_complex`），采用 [current_baseline_suite.json](../configs/current_baseline_suite.json) 和[冻结门限](../configs/current_baseline_thresholds.json)。OAMP已[归档](../archive/oamp_mmv_20261008/README.md)；EM-BG-AMP和Ding GNN-ASPL的来源、实现与待完成资格见 [BASELINE_REVISION.md](BASELINE_REVISION.md)。下文保留SOMP、GAMP及归档OAMP的公式和历史核验，论文算法与项目设置分别记录。

最新[SOMP/OAMP原文专项复核](../results/somp_oamp_reaudit_20261008/REPORT.md)未发现SOMP核心错误；OAMP的线性和联合行后验与当前工作模型一致，但没有实现完整矩阵OAMP-MMV。另已复现非空低SNR输入的非正能量初值退化：方差落到1e−20后输出近零，增加迭代仍未恢复。这一问题未出现在既有34个AFDM资格输入中，不能将既有有界资格扩展为任意低SNR适用。两个原生OAMP场景的长预算补充、21项相关检查及完整不利控制均保留；现用求解器、配方和门限未改。

整数网格资格阶段的三方法采用共同的16个整数时延点和5个整数Doppler点，每用户80个原子。GAMP采用Zhang Algorithm 1的全步精度更新及绝对均值停止，保留0.2均值/消息阻尼和共同已知噪声。34个既有开发输入、102条原生输出通过文件和指标复核，GAMP的544个天线列全部达到论文停止条件。本次保留SOMP/GAMP的原设置及68条输出证据，网格和历史结果见 [BASELINE_GRID.md](BASELINE_GRID.md)。

旧0.25时延步长、9个Doppler点及GAMP相对状态配方完整保留于 [旧配置](../results/baseline_integer_grid_20261008/PREVIOUS_SUITE.json)和[原资格记录](BASELINE_QUALIFICATION.md)。单独的 [gamp_ding_paper.json](../configs/gamp_ding_paper.json)仍保留原细网格与Ding式(27)读出，用于重放此前检查；当前suite取其GAMP求解器，活动判决统一使用完整H能量和新网格的独立校准门限。

与Ding的引用关系：Ding第5页§IV-B的GAMP-SBL明确引用第6页参考文献[8]Zhang 2023；其对比算法列表没有OAMP。Ding在该段列出BOMP，但部分正文与图又使用SOMP名称；当前SOMP依据下表Tropp Algorithm 3.1实现，不能据名称混用认定与Ding的BOMP相同。OAMP依据Ma–Ping框架及Ying卫星JADCE文献作本项目适配。原文见 [Ding PDF](../Learning_Sparsity_Pattern_An_Adaptive_Joint_Detection_for_AFDM_Grant-Free_System_in_LEO_Satellites_Communication.pdf)。

## 论文、原文定位与实现

| 方法 | 核实的主要论文 | 原文定位与代码 |
|---|---|---|
| SOMP | J. A. Tropp, A. C. Gilbert, M. J. Strauss, “Algorithms for simultaneous sparse approximation. Part I: Greedy pursuit,” *Signal Processing*, 86(3), 572–588, 2006. DOI [10.1016/j.sigpro.2005.05.030](https://doi.org/10.1016/j.sigpro.2005.05.030) | [作者预印本](https://tropp.caltech.edu/papers/TGS05-Algorithms-Simultaneous-I-preprint.pdf)：§2.2 p.4，Algorithm 3.1 pp.6–7、§3.2 p.7；[somp.py](../src/afdm_jadcedd/algorithm/baselines/somp.py) |
| OAMP-MMV | Junjie Ma, Li Ping, “Orthogonal AMP,” *IEEE Access*, 5, 2020–2033, 2017. DOI [10.1109/ACCESS.2017.2653119](https://doi.org/10.1109/ACCESS.2017.2653119) | [arXiv v3](https://arxiv.org/pdf/1602.06509v3)：§III-A式(14)–(15) p.3，§III-C式(19)–(20) p.4，§IV-B式(38)–(39) p.6、Appendix C pp.11–12；[common_rate_oamp.py](../src/afdm_jadcedd/algorithm/baselines/common_rate_oamp.py)、[common.py](../src/afdm_jadcedd/algorithm/baselines/common.py) |
| GAMP-SBL | X. Zhang, P. Fan, L. Hao, X. Quan, “Generalized Approximate Message Passing Based Bayesian Learning Detectors for Uplink Grant-Free NOMA,” *IEEE TVT*, 72(11), 15057–15061, 2023. DOI [10.1109/TVT.2023.3280919](https://doi.org/10.1109/TVT.2023.3280919) | [本地论文](../references/zhang2023_gamp_sbl_grant_free_noma.pdf)：p.15058式(3)–(4)、(8)–(10)，p.15059式(11)–(19)、Algorithm 1；[gamp_zhang2023.py](../src/afdm_jadcedd/algorithm/baselines/gamp_zhang2023.py)、[ding.py](../src/afdm_jadcedd/algorithm/baselines/ding.py) |

OAMP-MMV 还有直接卫星 JADCE 文献依据：K. Ying et al., “Quasi-Synchronous Random Access for Massive MIMO-Based LEO Satellite Constellations,” [arXiv:2304.04484v1 §III-B式(10)–(25)、Algorithm 1](https://arxiv.org/html/2304.04484v1#S3.SS2)。当前实现采用 Ma–Ping 线性/外信息结构及下述共同支撑后验，不逐项复现 Ying 的参数学习、活动判决或后续 AoA 信道重构。共同率初始化参照 Vila–Schniter [§III-D式(70)–(71)](https://arxiv.org/pdf/1207.3107)，使用已知噪声和天线平均是项目适配。

OAMP的MMV矩阵形式还核对[Cheng等 arXiv:2304.08038v1，§III-F印刷p.6式(31)–(34)](https://arxiv.org/pdf/2304.08038v1)，其正交化系数为跨测量向量的矩阵。Ying参考文献[11]所引Cheng–Liu–Ping JSAC2021的题名与MMV/GGSO范围已核实于作者机构摘要，正文公式本轮未取得；不可用这一元数据核查代替全文实现核查。

## 共同输入与完整信道

只接收 `observation`、`operator`、`noise_variance`、`activity_prior`。当前算子含仿真真实 Doppler 构造的已知跨帧相位，噪声是生成分布的复方差 \(\sigma^2=E|w|^2\)。这是共同 oracle 仿真信息条件。推断不读取真活动、真信道、真路径或真实方向；真值只在推断完成后离线评分。

设 DD 网格矩阵为 \(G_g[r,n]\)，公开算子为 \(P_{qkn}\)，则物理字典为

\[
\Phi_{(q,r),(k,g)}=\sum_nP_{qkn}G_g[r,n],\quad b_{kg}=\|\Phi_{:,(k,g)}\|_2,\quad A=\Phi\operatorname{diag}(b)^{-1}.
\]

SOMP、OAMP 求归一化系数 \(X\)，完整输出为 \(\widehat H_{kmrn}=\sum_gX_{(k,g),m}G_g[r,n]/b_{kg}\)。GAMP 使用原始 \(\Phi\) 与物理系数 \(Z\)，输出为 \(\sum_gZ_{(k,g),m}G_g[r,n]\)。两种路径均满足字典前向观测与完整信道再投影的恒等式。尺度选择改变先验参数含义，不能将归一化系数直接当物理系数。实现见 [dictionary.py](../src/afdm_jadcedd/system/dictionary.py)。

现用网格覆盖一个折叠时延周期，时延样本为0至15；Doppler为子载波间隔30 kHz的整数倍−2至2，即−60、−30、0、30、60 kHz，覆盖真实±41 kHz范围。三方法共同采用80个原子，物理生成仍使用分数时延和Doppler。当前 \(2Nc_1\) 为整数时，

\[
G(d+\ell N,\nu)=e^{j2\pi c_1(2\ell Nd+\ell^2N^2)}G(d,\nu).
\]

单位模标量可收入未知复增益，因而周期折叠适用于完整信道合成；这不是绝对物理时延的唯一识别。有限网格仍近似连续路径。完整信道不按活动判决清零，也不按真支撑重估。

## SOMP

每轮选 \(\arg\max_j\sum_m|(A^HR)_{jm}|\)，即 Algorithm 3.1 的相关绝对值之和。两次正交化构造已选列的基，残差为 \((I-QQ^H)Y\)，最终在所选支撑对全部天线求 LS。原文已使用复数字典，共轭与此相关范数属于原算法。

项目以 \(\|R\|_F^2\le\sigma^2LM\) 停止（加相对能量数值下限），最多64个原子。残差/预算停止类型有§3.2依据，具体噪声倍数、64及DD网格是项目设置。`MAX_ATOMS` 不能解释为噪声标准已满足。

可用独立方向耗尽时也使用`MAX_ATOMS`标签，可能尚未接受64个原子；以实际`iterations`及残差解释结果。重复列控制确认这一状态含义问题，未发现相应投影或LS错误。

## OAMP-MMV

工作先验对系数行共享 Bernoulli 变量：\(s_i\sim\mathrm{Bernoulli}(\rho)\)，\(X_i|s_i=1\sim\mathcal{CN}(0,\gamma I_M)\)。全部天线似然联合计算行活动概率，因此当前 OAMP 确实是 MMV。\(\rho\) 是字典系数行激活率，不是用户活动概率。

线性模块为去相关 LMMSE：

\[
\widetilde W=vA^H(vAA^H+\sigma^2I)^{-1},\quad W=\frac{n\widetilde W}{\operatorname{tr}(\widetilde WA)},\quad R=D+W(Y-AD),\quad
\tau=\frac{v\|I-WA\|_F^2+\sigma^2\|W\|_F^2}{n}.
\]

\(n\) 是系数维数，\(v,\tau\) 为方差；实现保留欠定零空间项。由完整行复高斯密度直接推得

\[
\operatorname{logit}\pi_i=\operatorname{logit}\rho-M\log(1+\gamma/\tau)+\frac{\gamma\|R_i\|^2}{\tau(\tau+\gamma)},\quad c_i=\frac{\gamma R_i}{\gamma+\tau},\quad c_v=\frac{\gamma\tau}{\gamma+\tau},
\]

\[
\mu_i=\pi_ic_i,\quad V_i=\pi_ic_vI_M+\pi_i(1-\pi_i)c_ic_i^H,\quad q=\frac{\sum_i\operatorname{tr}V_i}{nM}.
\]

外信息为 \(D_{next}=(\mu-(q/\tau)R)/(1-q/\tau)\)、\(v_{next}=(q^{-1}-\tau^{-1})^{-1}\)，对应式(38)–(39)的迹结构。EM 为 \(\rho_{next}=n^{-1}\sum_i\pi_i\)、\(\gamma_{next}=\sum_{i,m}\pi_i(|c_{im}|^2+c_v)/(M\sum_i\pi_i)\)。对 \(D,v\) 作0.2插值，后验均值与共同参数全步更新。

这里0.2为新状态权重；[Ying固定commit源码第155–156行](https://raw.githubusercontent.com/kekeyingBIT/LEO/c9b715df7931af949f59ead7361fc82836eb27ea/Perfect%20Backhaul/csAlg/gmmv_oamp_app2.m)的`damp`为旧状态权重，数值相同不表示同一阻尼设置。当前\(q\)仅保留行后验协方差的平均迹，用一个共同方差更新外信息；各向同性工作模型的总体平均可缩减为标量，但有限平均协方差一般非对角，不能称为Cheng完整矩阵MMV算法的复现。

当前能量初值\(p_0=(\|Y\|_F^2/M-L\sigma^2)/\|A\|_F^2\)。非正时\(\gamma_0,v_0\)被置于1e−20，会导致近零输出稳定；16个−10/−20 dB非空CN控制中有6例触发，首例100轮通过输出停止且600轮仍不恢复。既有34个AFDM输入初值均正。此风险及后续尺度合理正初值的验证需要单独处理，不能用更长预算或停止成功替代。

各向同性激活协方差没有编码真实阵列方向或严格秩一，这是基线先验近似。有限 AFDM 字典不自动满足 Ma–Ping 大系统随机矩阵理论条件；经验 \(q\ge\tau\) 时明确失败，不能裁剪后宣称成功。

最多8000轮；至少100轮，系数相对变化连续10轮小于1e−6，且系数在50轮窗口内每10轮采样的最大相对变化小于1e−4。`COEFFICIENT_AND_WINDOW_STOP` 只认证这个输出稳定条件；共同率、方差与外信息的诊断保留。`MAX_ITERATIONS` 不等同全状态收敛。

## GAMP-SBL

Zhang Algorithm 1 每轮一次 GAMP 后更新精度，当前保持单循环。每个天线观测列独立求解，不共享行精度，不能称为共同支撑MMV GAMP。复数方差传播用 \(|\Phi|^2\)，均值回传用 \(\Phi^H\)。

对 \(x_j|\alpha_j\sim\mathcal{CN}(0,\alpha_j^{-1})\) 和 Gamma(shape,rate) 超先验，由 CN 的 \(\log\alpha_j-\alpha_j|x_j|^2\) 项独立推导：

\[
\alpha_j^{target}=\frac{a}{|m_j^{raw}|^2+v_j+b},\quad
\gamma^{target}=\frac{L+c-1}{\sum_l(|y_l-\bar u_l|^2+v_l^u)+d}.
\]

Zhang 印刷式(15)–(19)含实高斯1/2因子，与前文 CN 模型不一致；这里是明确的复数修正。印刷平方也不能替代模平方或共轭。给定噪声模式固定 \(\gamma=1/\sigma^2\)，跳过噪声学习。系数方差按列接收能量初始化，不使用标签或真实活跃数量。

消息及均值均0.2阻尼；标量后验方差不阻尼，精度全步更新采用同一标量去噪器的raw成对均值与方差，即\(\alpha^{next}=\alpha^{target}\)。这是Zhang Algorithm 1的单次GAMP与精度交替流程。均值/消息阻尼属于项目数值适配，其结构参照Rangan [Algorithm 1第8–13行、§II-B](https://arxiv.org/html/1402.3210)及Al-Shoukairi–Schniter–Rao [Table I A3/A4/A7/A8](https://arxiv.org/html/1703.03044)。源码允许分别设置`mean_damping`、`message_damping`与`learning_damping`；现用实际权重为0.2、0.2、1.0。

每个天线列检查\(\|m^{t+1}-m^t\|_2^2\le10^{-6}\)（平方和，不除以系数维数），达到后保存该列并停止，最多2000轮。这个绝对均值准则取自Zhang p.15059 Algorithm 1；具体预算、初始化和阻尼为项目设置。34个开发输入的全部544列在该准则下停止，见[当前检查报告](../results/baseline_integer_grid_20261008/REPORT.md)。复数修正及Ding引用关系见[DING_GAMP_ALIGNMENT.md](DING_GAMP_ALIGNMENT.md)。

原8000轮相对状态/窗口配方及其预算敏感性属于历史实验，见[原资格记录](BASELINE_QUALIFICATION.md)，不再作为当前GAMP默认设置。

## 活动判决与评分

三个方法共同用 \(e_k=\mathrm{mean}|\widehat H_k|^2\)、\(\hat a_k=1[e_k>t]\)。按方法独立校准，校准与确认数据分开，冻结后不根据确认标签重拟合。这是项目读出，不把数值门限归给原论文。

Ding 2026 [第4页式(27)](https://doi.org/10.1109/TVT.2026.3729877)的相对系数能量读出保留为历史模式及诊断。它来自 Ding 提出的方法；第5页§IV-B所引 GAMP-SBL 是 Zhang 2023。当前完整信道能量有共同物理解释，包含相干原子交叉项，通常与系数块能量不同。

原生输出和轨迹保存 SHA256、给定噪声、停止状态、警告与配方。评分包括所有漏检用户和迭代上限输出：AER汇总 MD+FA 再除候选用户总数；NMSE先累加误差/信号能量再取dB。有失败则报告失败及可用范围，不能以成功子集替代完整面板。场景以至少一用户活跃为条件，公开先验是条件边缘；见 [EXPERIMENT_PROTOCOL.md](EXPERIMENT_PROTOCOL.md)。
