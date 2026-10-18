## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: validate（本地执行）
- Origin Date: 2026-10-14
- Verification Status: ANALYZED
- Version Label: ldamp_paper_audit_v1
- 范围：当前 L-DAMP baseline 的设计适配与训练；未审计 Proposed，也未完整复现原论文曲线。

# L-DAMP 原论文、作者代码与当前实现对照

**设计适配和训练都需要修正。** 已经确认的是：当前去噪训练结果不合格，而且真实接收机查询误差与训练白噪声分布存在很大的协方差差异。尚未证明的是：某一个新的 Onsager 公式或网络结构能解决全部问题。此前将重点放在初始化和 BatchNorm 的排查不够，必须先补上观测模型与去噪分布的对照。

## 原始材料

已下载并检查三篇完整作者稿，PDF 结构检查均通过，关键公式和网络图已渲染核对。页码均指本地 PDF 页码。

| 材料 | 本地全文 | 核对位置 |
|---|---|---|
| He 等，Deep Learning-based Channel Estimation for Beamspace mmWave Massive MIMO Systems，WCL 2018，作者稿 v2 | [PDF](../../references/ldamp_review_20261014/he2018_ldamp.pdf) · [原始链接](https://arxiv.org/pdf/1802.01290v2) | pp.1–2 §II；p.2 式(4)–(8)；p.3 Fig.3、§IV-A；p.4 Fig.5–6 |
| Metzler–Mousavi–Baraniuk，Learned D-AMP，2017，作者稿 v4 | [PDF](../../references/ldamp_review_20261014/metzler2017_learned_damp.pdf) · [原始链接](https://arxiv.org/pdf/1704.06625v4) | p.5 §3；pp.6–7 §4，尤其 Finding 1；pp.7–8 §5 |
| Zhang 等，Beyond a Gaussian Denoiser，DnCNN 作者稿 v1，2016（期刊论文 2017） | [PDF](../../references/ldamp_review_20261014/zhang2017_dncnn.pdf) · [原始链接](https://arxiv.org/pdf/1608.03981v1) | §III 残差学习；p.6 §IV-A 训练设置 |

另下载 [He 作者仓库](https://github.com/hehengtao/LDAMP_based-Channel-estimation) 的完整 Packages.7z，提取其中信道生成和 DnCNN 训练代码。固定提交为 `2b5c135e79482b7c317165732b9a797de5e2bd33`；压缩包包含十套 20 层权重，但本轮没有运行 MATLAB 权重。同时核对 Rice D-AMP 和 DnCNN 作者仓库的训练实现。URL、版本、SHA256 和已读文件见 [SOURCES.json](SOURCES.json)，原压缩包目录见 [HE_PACKAGES_INDEX.json](../../references/ldamp_review_20261014/HE_PACKAGES_INDEX.json)。

## 设计：原算法的条件不能直接移用

| 对照项 | 原文 / 作者代码 | 当前项目 | 判断 |
|---|---|---|---|
| 信道与卷积轴 | He §II、Fig.3：单用户实数二维波束域信道，单输入输出通道；§IV 为 64×64 | 每用户 16×16×16 复数 AFDM 信道，实虚组成 32 通道，卷积沿 AFDM 两轴 | 改变了网络使用的空间结构；多通道本身不等于错误，但不是原文已经验证的表示 |
| 观测结构 | He 为单用户；Metzler Finding 1 使用独立随机矩阵等条件 | 40 用户共用导频，16×640 算子重复用于 256 个天线×输出坐标 | 标量状态演化及标量 Onsager 不能仅凭形式一致就宣称适用 |
| 测量比 | He Fig.5–6 检查 0.05、0.1、0.2 | 16/640 = 0.025 | 更困难的恢复区间，需要自己的接收机验证 |
| 去噪误差模型 | Metzler §3：各噪声水平的 AWGN 去噪问题 | 训练用独立复 AWGN；真实第一轮查询已有很强的跨天线相关性 | 已有直接的分布不匹配证据，见下一节 |

当前线性模型可按坐标重排写成

\[
\bar Y=A\bar X+\bar W,\qquad
A\in\mathbb C^{16\times640},\quad
\bar X\in\mathbb C^{640\times256}.
\]

因此全向量算子是 \(I_{256}\otimes A\)（相差坐标置换），不是整个未知向量上的独立随机矩阵。DnCNN 又同时混合天线和 AFDM 坐标。`core.py` 中把全实 Jacobian 的迹除以全实观测数，确实实现了所选择的标量更新，但此前的稠密实矩阵单元测试只证明**代码与这套更新的代数一致**，没有证明它是上述联合去噪问题的正确 AMP 扩展。

作为相关原始依据，Chen–Sohrabi–Yu 的 [ICASSP 2018 论文](https://www.comm.utoronto.ca/~weiyu/2018_ICASSP_massive_connectivity.pdf) §3.1，PDF p.2 式(2)–(4)，在多测量向量模型中保留行向量导数及噪声协方差矩阵；随后在其特定先验下才简化为标量方差。该文的逐行去噪器和高斯矩阵也不同于本项目，不能直接复制其公式作为已完成修复。

## 新诊断：总方差准确，不等于误差是白噪声

使用已有开发校准集的 8 个物理场景，在 −4、0、6 dB 各检查一次，共 24 份记录。每个场景跨 SNR 复用。只计算第一次去噪前的

\[
q^0=A^Hy,\quad e^0=q^0-H_{\rm masked}/s_H,\quad
\widehat v=\operatorname{mean}|y|^2.
\]

真值仅用于离线测量误差，没有输入接收机、选网或训练。沿用户及 AFDM 坐标采样、中心化后得到跨天线经验协方差 \(C\)，报告 \(\|C-\operatorname{diag}C\|_F^2/\|C\|_F^2\)。对照为同尺寸、同经验平均功率的独立复 AWGN。

| 指标 | 中位数 | 24 份记录范围 |
|---|---:|---:|
| 实际误差的跨天线协方差非对角能量占比 | 76.10% | 46.66%–90.50% |
| 匹配 AWGN 对照，同一指标 | 0.1465% | 0.1150%–0.1772% |
| 实际误差的 AFDM 输出轴协方差非对角能量占比 | 23.15% | 11.13%–44.95% |
| 匹配 AWGN 对照，同一指标 | 0.1434% | 0.1114%–0.1715% |
| 实际误差均方值 / 残差估计方差 | 0.9980 | 0.9888–1.0116 |

这说明用一个标量选噪声段能匹配总功率，却遗漏了当前场景中明显的相关结构。该现象出现在任何神经网络调用之前，不能归因于某个去噪器先产生了错误输出。它支持“接收机查询与训练分布不匹配”的判断，但不单独证明所有迭代的误差分布，也不证明相关性是失败的唯一原因。

可复现结果见 [QUERY_COVARIANCE_REPRODUCED.json](QUERY_COVARIANCE_REPRODUCED.json)。[诊断脚本](../../experiments/ldamp_repair_20261014/audit_query_covariance.py) 记录输入哈希和对照随机种子，采用不调用 BLAS 矩阵乘法的独立张量收缩；实际协方差指标与首轮计算最大差为 1.44×10⁻¹⁵。首轮 [结果](INITIAL_QUERY_COVARIANCE.json) 及 [交叉检查](COVARIANCE_CROSSCHECK.json) 均保留。新旧 AWGN 对照随机种子不同，所以其小数略有变化。

```sh
.venv/bin/python experiments/ldamp_repair_20261014/audit_query_covariance.py --output NEW_OUTPUT.json
```

## 训练：有明确失败，也有不能误判的部分

**五个已选网络中三个训练验证结果劣于零估计，这是已经确认的质量问题。** 高三段的 MSE/零估计 MSE 约为 3.29、34.32、303.16。最高段输出残留大量噪声，而非仅差一个小幅超参数优化。详见 [原权重复核](../ldamp_diagnosis_20261014/EXISTING_BASELINE_AUDIT.json) 和 [完整诊断](../ldamp_diagnosis_20261014/REPORT.md)。

作者信道版训练代码和项目的主要差异如下。这些差异是要控制的变量；没有逐项消融前，不把任何一项称为已经证实的唯一原因。

| 项目 | He 作者压缩包 | 当前正式配方 |
|---|---|---|
| 信号尺度 | `channel_gen.m:28`、`rescaleImage.m:3`：逐样本 min–max 到 [0,1] | 有符号复信道；训练总体固定尺度，再按噪声段固定缩放 |
| 活动分布 | 一个用户的信道，不含 90% 非活跃样本 | p=0.1 活动混合，90% 目标为零 |
| 噪声区间与采样 | `Demo_Train.m:7`、`DnCNN_train.m:395`：十个标准差区间，区间内逐样本均匀采样 σ，再除 255 | 五个复方差区间；区间内对数均匀采样方差，实虚各占一半 |
| 初始化与 BatchNorm | `DnCNN_init.m:16–45`：显式卷积权重尺度、较小的 BN 仿射初值与指定统计初值 | 原正式训练采用 PyTorch 模块默认初始化；后续恒等初始化及固定统计是开发对照 |
| 优化 | `Demo_Train.m:23–35`：Adam，batch 256、两个子批次，最多 50 个学习率条目；验证停滞降学习率 | Adam，batch 64，每段最多 30 轮；原旧模型未通过最低质量核验就被安装 |

其中三点不能混淆：

1. **分别训练去噪器有原文依据。** Metzler §3 明确列出 denoiser-by-denoiser training，因此“没有端到端训练”本身不是实现错误。
2. **当前损失与残差学习代数等价。** 若网络输出清洁估计 \(q-F_\theta(q)\)，则 \(\|q-F_\theta(q)-h\|^2=\|F_\theta(q)-(q-h)\|^2\)。不能将以清洁信道计算 MSE 误判为监督目标反了。数值优化是否容易是另一问题。
3. **不能把固定 BN 统计当作作者配方。** 作者 `bnormLearningRate=0` 仍通过 `DnCNN_train.m:328–336` 更新统计量；代码里的零不是“冻结统计”。此外 DnCNN 原论文的 SGD 和 He 的 Adam 是不同层次的配方，不能据前者断言当前使用 Adam 错误。

高噪声且大部分样本不活跃时，零估计可以接近最优；因此只比零估计好一点不代表学到了有用接收机。已有最高段修复对照最终选中训练前的线性初值，随后完整开发校准误差仍比零估计高 8.7%，所以尚无成功修复的证据。全部试验和不利结果继续保留。

## 原始代码也需要解释，不能直接全盘照搬

He 原文 §II 的随机符号矩阵尺度，与作者 `Demos/LDAMP_SNR.m:41` 的高斯矩阵尺度不同。该演示还默认调用 BM3D、20 次 AMP、17 层网络配置；信道训练脚本则明确生成 20 层 DnCNN。原仓库自称提供部分代码，下载完成不等于已经复现论文。当前单位列范数的代数检查没有暴露简单缩放错误，不能因原文一个尺度表达就直接改动正式接收机。

作者 `channel_gen.m` 确实用每个干净信道的极值生成归一化训练目标；演示也在合成测量前缩放信道。该做法定义的是其模拟问题。我们的物理观测已经给定，不应读取测试真值的极值再变换观测。改变归一化必须明确尺度获取方式及训练/推断一致性。

## 修正顺序

1. **先建立忠实的小规模参考。** 对齐单通道、作者信道生成/尺度、噪声采样、初始化和 BN 语义，检查单独 AWGN 去噪及独立随机观测下的完整 L-DAMP。逐项登记剩余差异，成功后才有可用的迁移参照。
2. **再核对当前观测模型的扩展。** 明确多天线、多输出及用户块联合去噪对应的误差协方差和 Onsager 项；把本轮第一轮查询诊断扩展至迭代过程。是否需要矩阵形式的校正或其他迭代框架须有推导及受控结果，不能先改名或假定正确。
3. **最后逐项加入当前信道表示与活动先验。** 将表示、活动混合、噪声分布和训练配方分开检查。训练去噪有效后，仍需新场景接收机验证及统一比较；开发集结果不替代独立评估。

当前状态继续是 `FAILED_RECEIVER_VALIDATION`。本轮下载和对照没有替换主线权重，也没有把未通过的试验标为成功；长期续训尚不能解决已确认的设计分布差异。

## 统计与复现范围

本轮是来源核查和探索性诊断。8 个场景的三个 SNR 不是 24 个独立物理场景；同场景内坐标用于经验协方差，不作为独立实验重复。没有报告 p 值或总体置信区间，也没有声称已经复现原论文性能。协方差数值重算通过；完整论文复现未执行，报告总体状态为 ANALYZED。

11/11 方法学检查已覆盖：

| 检查 | 本轮处理 |
|---|---|
| Simpson's paradox | 保留逐场景、逐 SNR 记录；实际相关指标最小值仍远高于 AWGN 对照最大值 |
| Ecological fallacy | 不从聚合数值推出所有用户或未来场景均成立 |
| Berkson's paradox | 使用预先生成的全部 8 个校准场景；SNR 子集明确为探索性诊断 |
| Collider bias | 未按估计表现筛选或条件化场景 |
| Base rate neglect | 原 10.65% AER 对应全部漏检；明确比较恒定不活跃判决 |
| Regression to the mean | 不把不同场景上的旧/新 NMSE 差当作配对提升 |
| Survivorship bias | 失败训练、校准和数值警告全部保留，无删样本 |
| Look-elsewhere effect | 报告所有开发训练对照；没有从多个试验挑选“显著”结论 |
| Garden of forking paths | 后续方案受前序结果影响，按开发过程记录，不称预注册验证 |
| Correlation != causation | 协方差不匹配是实测事实；它对最终失败的单独因果贡献尚未隔离 |
| Reverse causality | 第一轮误差在网络调用前计算，可排除由当前去噪输出造成；未扩展为唯一病因断言 |

术语定位同步于 [TERMINOLOGY.md](../../docs/TERMINOLOGY.md)。
