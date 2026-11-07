# 有色噪声网络：条件接口与输出目标的论文/官方代码核对

日期：2026-10-24。ARS bounded literature worker；采用定向叙述性核读，非系统综述。仅下载和读取论文、作者代码与当前训练代码；未修改训练、启停进程或运行性能实验。结论中的“项目推导/建议”不属于原论文已验证结果。

## 判断

**现有证据支持先重新设计协方差条件接口，而不是立即换掉 NCSN/RefineNet 主干。** D-GEC 的 corr+corr 本来就是在现有 DNN 上增加噪声统计输入；D-VDAMP 则保留 DnCNN 基本结构、把已知子带标准差送进每一层。两者均没有证明当前 AFDM 必须采用某个新主干，也没有验证“1025→64 全局条件”足够。当前接口还有一个可明确写出的信息压缩限制，见第 5 节。

DRUNet 可以作为后续主干对照，但其原版只处理标量 AWGN 条件、采用 L1 重建训练；换成它不会自动解决随机复协方差的表示问题，原训练目标也不能直接照搬到条件均值/score 网络。

## 1 核读来源与版本

| 论文 | 实际阅读范围、下载版 | 关键问题 |
|---|---|---|
| S. K. Shastri, R. Ahmad, C. A. Metzler, P. Schniter, *Denoising Generalized Expectation-Consistent Approximation for MR Image Recovery*, arXiv:2206.05049v2 | [原文](https://arxiv.org/pdf/2206.05049v2)；[已有本地 PDF](../../literature/shastri2022_dgec.pdf)，§III-B pp.15–16，式(38)–(41)；§IV-A pp.17–18，Table I | 任意已知协方差的辅助样本接口；实验实际只覆盖特定小波协方差族 |
| C. A. Metzler, G. Wetzstein, *D-VDAMP: Denoising-Based Approximate Message Passing for Compressive MRI*, arXiv:2010.13211v1，ICASSP 2021 | [原文](https://arxiv.org/pdf/2010.13211v1)；[已有本地 PDF](../../literature/metzler2020_dvdamp.pdf)，§2.3 p.3；§3 pp.3–4、Table 1 | 每层额外输入固定小波基下 13 个标准差 |
| K. Zhang, W. Zuo, L. Zhang, *FFDNet: Toward a Fast and Flexible Solution for CNN based Image Denoising*, TIP 2018，arXiv:1710.04026v2 | [原文](https://arxiv.org/pdf/1710.04026v2)；[本地 PDF](../../literature/zhang2018_ffdnet_v2.pdf)，§III-A/B pp.3–4，§III-F pp.5–6，§IV-A pp.6–7、式(5) | 噪声图拼接、RGB 协方差扩展、直接预测 clean signal |
| K. Zhang, Y. Li, W. Zuo, L. Zhang, L. Van Gool, R. Timofte, *Plug-and-Play Image Restoration with Deep Denoiser Prior*, arXiv:2008.13751v2（2021-07-12 作者稿） | [原文](https://arxiv.org/pdf/2008.13751v2)；[本地 PDF](../../literature/zhang2021_dpir_v2.pdf)，Fig.1 p.3，§3.1–3.2 p.4 | DRUNet 的标量噪声图、残差 U-Net、L1 训练 |

新下载 PDF 的逐页文本在 `text/zhang2018_ffdnet_v2.txt` 和 `text/zhang2021_dpir_v2.txt`；已有两篇沿用前次下载及分页文本。下面是选择性细读，不声称读完全部附录。

## 2 论文事实与官方实现

### 2.1 D-GEC / corr+corr

**论文事实。** §III-B 从任意 DNN denoiser 出发，例举 DnCNN、UNet、RNN。在输入 `u=x+n` 外，加 K 份具有相同协方差的独立噪声样本。式(39)–(40)描述给定协方差时的独立抽样；训练时协方差也随样本变化，式(41)对信号噪声与辅助噪声同时取期望。实验使用 L2 损失及 bias-free DnCNN，K=1 在其 MRI 设置中足够。

原文 pp.15–16 还讨论了 D-VDAMP 的接口：图像域 CNN 接收小波域标准差，但未显式知道小波变换，作者认为这可能解释部分设置下的差表现。Table I 对相同类型 DnCNN 的条件方式作比较；它支持“条件表达值得单独改”，不证明对任意随机旋转协方差，单份辅助样本足够。

**官方代码核实。** 论文 p.18 直接给出作者仓库 [corr-plus-corr](https://github.com/Saurav-K-Shastri/corr-plus-corr)。本次读取 commit `9329042d410edff48c07d9b321ecaccbcddb4176`（2022-10-02）：

- [`Denoiser_Experiments/models/dncnn_cn.py#L10-L72`](https://github.com/Saurav-K-Shastri/corr-plus-corr/blob/9329042d410edff48c07d9b321ecaccbcddb4176/Denoiser_Experiments/models/dncnn_cn.py#L10-L72)：默认 20 层、64 feature channels、两输入通道；第一通道是 noisy image，第二是 auxiliary noise；最后输出一个通道，返回 `y[:,0]-out`，即去噪图像而非 score。
- [`train_BF_CNN_corr_p_corr_image_denoiser.py#L109-L123`](https://github.com/Saurav-K-Shastri/corr-plus-corr/blob/9329042d410edff48c07d9b321ecaccbcddb4176/Denoiser_Experiments/train_and_data_generation/train_BF_CNN_corr_p_corr_image_denoiser.py#L109-L123)：先按 `db1, level=1` 生成输入与辅助样本，再以 clean image 为目标做 MSE。
- [`utils/transform.py#L261-L290`](https://github.com/Saurav-K-Shastri/corr-plus-corr/blob/9329042d410edff48c07d9b321ecaccbcddb4176/Denoiser_Experiments/utils/transform.py#L261-L290)：各子带分别抽独立噪声；输入污染与辅助样本是两次独立抽样，绝不能把训练实际注入的同一份噪声泄漏给网络。
- 复 MRI 实现有一个重要细节：[`fastMRI_corr_plus_corr/utils/noise_model.py#L43-L59`](https://github.com/Saurav-K-Shastri/corr-plus-corr/blob/9329042d410edff48c07d9b321ecaccbcddb4176/fastMRI_corr_plus_corr/utils/noise_model.py#L43-L59) 生成复噪声，却只把辅助噪声的实部放入第三输入通道；[`models/dncnn_cpc.py#L53-L65`](https://github.com/Saurav-K-Shastri/corr-plus-corr/blob/9329042d410edff48c07d9b321ecaccbcddb4176/fastMRI_corr_plus_corr/models/dncnn_cpc.py#L53-L65) 返回前两信号通道减去预测残差。这适用于其固定实小波基、实虚部同统计的噪声设置，不能不加检查地复制到本项目一般复 Hermitian C。

**项目推断。** 可保留 RefineNet，给 trunk 增加同坐标辅助噪声通道，训练 `n_aux|C~CN(0,C)`。当前 32 个 real-packed signal channels 对应 K=1 时增加 32 个辅助通道，是一种候选实现，不是论文已验证的 AFDM 参数。有限 K 只是协方差的随机表征，不等于把完整 C 无损告诉网络；若 C 本来精确已知，不必为了照抄 corr+corr 丢弃确定性 C 信息。训练只有 `(r,n_aux)` 时，理想 L2 解是 `E[h|r,n_aux]`，一般不等于 `E[h|r,C]`；后者才是给定 C 的精确条件均值。论文方法是有效的工程近似，不能拔高成有限 K 的充分性定理。

### 2.2 D-VDAMP

**论文事实。** p.3 §2.3 使用 modified DnCNN：每个卷积层均读入 13 个空间常数通道，内容是固定四尺度 Haar 小波的 13 个子带标准差。论文训练四个不同噪声范围的网络，而不是一个覆盖任意协方差的网络。§3 主要重建实验使用实值 MRI；复杂信道是额外适配。

**官方代码核实。** 作者网站链接的 [Intelligent-Sensing/D-VDAMP](https://github.com/Intelligent-Sensing/D-VDAMP)，commit `0405a68dc386324b94890d9cea102f2f26d4d1b4`（2021-06-08）：

- [`train/model.py#L14-L57`](https://github.com/Intelligent-Sensing/D-VDAMP/blob/0405a68dc386324b94890d9cea102f2f26d4d1b4/train/model.py#L14-L57)：`std_channels=13`；第一、中间、最后卷积层都 concatenate 标准差图；`return x-noise`。
- [`train/solve.py#L49-L56`](https://github.com/Intelligent-Sensing/D-VDAMP/blob/0405a68dc386324b94890d9cea102f2f26d4d1b4/train/solve.py#L49-L56)：MSE 比较去噪输出与 clean image。

**项目推断。** 它证明“沿用 CNN 主干、改条件接口”有直接先例，但当前 C 的特征向量每样本随机变化。只提供 eigenvalues/13 类统计量或复制常数条件图，不能告诉网络未知的方向；固定 Haar 基下的低维条件与随机 Ra/Rc 不是同一个难度。每层拼接条件也不自动优于现有归一化调制，需做同主干、同数据、同目标的对照。

### 2.3 FFDNet

**论文事实。** §III-A 把四个下采样子图与 noise-level map 拼接；卷积输出直接重建 clean image，区别于 DnCNN 的噪声残差学习。§III-F 认为其条件任务下两种参数化最终表现接近，非残差形式是选择而非必要性定理。§IV-A 式(5)是 clean-target L2。§III-B 明确提出多通道 degradation map 可描述 RGB 的 3D Gaussian 协方差。

**官方代码核实。** [cszn/FFDNet](https://github.com/cszn/FFDNet)，commit `e787f46df2f374ff3591186706229cb9a0591fea`（2021-10-09）：

- [`TrainingCodes/FFDNet_TrainingCodes_v1.0/model_init_FFDNet_gray.m#L19-L24`](https://github.com/cszn/FFDNet/blob/e787f46df2f374ff3591186706229cb9a0591fea/TrainingCodes/FFDNet_TrainingCodes_v1.0/model_init_FFDNet_gray.m#L19-L24) 的 `SubP` 后接 `concat`，再进第一卷积。
- [`Demo_multivariate_Gaussian_noise.m`](https://github.com/cszn/FFDNet/blob/e787f46df2f374ff3591186706229cb9a0591fea/Demo_multivariate_Gaussian_noise.m)：加载 `FFDNet_3D_RGB.mat`，从 3×3 对称 RGB covariance 抽取六个参数，广播为条件通道。代码取逐元素平方根并显式要求 covariance 元素非负；这不是一般矩阵平方根，也不能原样套用复数或有负相关的协方差。
- [`utilities/vl_ffdnet_matlab.m`](https://github.com/cszn/FFDNet/blob/e787f46df2f374ff3591186706229cb9a0591fea/utilities/vl_ffdnet_matlab.m) 的 concat 分支把各参数变成 feature map 后拼接。

**项目推断。** “FFDNet 只有标量条件”不够准确；“FFDNet 已解决任意高维 colored noise”同样错误。它支持把统计参数直接作为网络输入的设计思想；六维 RGB 同像素相关与本项目跨 16 天线、跨 16 输入列的复相关相差很大。多参数输入应保留物理轴与复数实嵌入的含义，不能随意把协方差两维当成信道的两个空间维。

### 2.4 DRUNet / DPIR

**论文事实。** p.4 §3.1 保留 noise-level map 输入，主干为四尺度 residual U-Net，channels 为 64/128/256/512，卷积无 bias。§3.2 以 AWGN 训练：条件图全填 σ，损失为 L1，而非 L2。该文没有随机 full covariance conditioning。

**官方代码核实。** [cszn/DPIR](https://github.com/cszn/DPIR)，commit `15bca3fcc1f3cc51a1f99ccf027691e278c19354`（2022-11-21）：[`main_dpir_denoising.py#L92-L94`](https://github.com/cszn/DPIR/blob/15bca3fcc1f3cc51a1f99ccf027691e278c19354/main_dpir_denoising.py#L92-L94) 建 `UNetRes(in_nc=n_channels+1,out_nc=n_channels)`；[L122–129](https://github.com/cszn/DPIR/blob/15bca3fcc1f3cc51a1f99ccf027691e278c19354/main_dpir_denoising.py#L122-L129) 加 AWGN、拼接 σ map；[`models/network_unet.py#L64-L127`](https://github.com/cszn/DPIR/blob/15bca3fcc1f3cc51a1f99ccf027691e278c19354/models/network_unet.py#L64-L127) 的 UNetRes 最后返回图像输出，没有外层 `input-noise` 读出。该仓库读取范围内没有训练代码；L1 事实来自论文，不能声称本轮核验了其训练执行。

**项目推断。** 直接换 DRUNet 仍需设计 C 接口，而且 L1 的 Bayes 解是分量条件中位数，并非一般条件均值。若目标仍是 Tweedie 条件均值/score，需要保留相应 MSE/DSM 目标；图像观感或 PSNR 排名不能替代这项一致性。其去除 bias/normalization 的结构选择可以单独比较，不足以证明本项目 InstanceNorm++ 有错。

## 3 官方代码留存

所有核读代码均从以上 commit 的 `raw.githubusercontent.com` 下载，只作资料。存放在 `code/<owner_repo>/<original_path>`；同级 `*_commit.json` 记录仓库、branch、SHA、提交时间，`*_tree.json` 为 GitHub API 文件树。另保留 D-GEC 仓库 commit `8b2a78ef4ee1d0f9e650d7549adc9cb5ea9dcfc3`（2022-10-02）的 metadata 与所读文件。没有 clone 新 Git 工作区，没有执行第三方训练/推理代码。

## 4 输出目标：论文中的 denoiser 不等于原封不动的 score 网络

以下为项目代数。采用当前 real-packed 表示，令 `Σ=real_embedding(C)/2`，`r=h+e`。代码的 posterior mean 和损失为

\[
\widehat\mu=r+\Sigma s_\theta(r,C),\qquad
\mathcal L=\frac1d\|\Sigma^{1/2}s_\theta+\Sigma^{-1/2}(r-h)\|^2
=\frac1d\|\Sigma^{-1/2}(\widehat\mu-h)\|^2.
\]

给定精确 C，这一正定加权平方误差与普通 clean-target MSE 的无限容量点态最优解均为 `E[h|r,C]`；有限模型、跨 C 的参数共享和优化权重不同，所以不能把它们的学习曲线视作等价。若改为直接输出 μ，仍可用上式损失并在需要时计算 `s=Σ^{-1}(μ-r)`；这是输出参数化改动，不要求主干改变。若输出白化 noise/residual，也需把对应 Σ 因子与目标一起写清。

0.394 与 0.101 这两个数来自任务上下文，本笔记未重算。即使 loss 公式形式一致，有色与白色采样下 Bayes 风险、方向加权和优化难度均不同，且 17 epoch 仍是中途状态。该差距值得调查，但不能据此宣布“网络结构失败”或要求有色训练必须达到 AWGN 的同一个 loss。

## 5 当前 64 维条件：有明确的信息压缩疑点，但未定位全部训练损失来源

**代码事实。** `src/training/colored_score_20261024/noise.py` 的 condition 返回 `log(v)/5` 和两个 `R-I` 的完整实/虚 entries，共 1025 个数；`model.py` 将原 Linear 扩为 1025→64，而 `src/networks/score.py:47–58` 后续仍为 64→64。所有归一化层共享该 64 维编码，再生成每通道系数；`normalization.py` 的 `ConditionalInstanceNorm2dPlus` 对空间位置广播这些系数。扩展条件列初始为零以复用原初始化，不意味着这些列以后没有梯度。

**项目推导。** 对 generic full-rank G，复 Hermitian rank-4 PSD 的自由度为 `2mr-r²=112`（m=16,r=4；可由 G 的 128 个实参数扣除 U(4) 的 16 个冗余自由度得到）。trace 归一化减一、再加入独立 α 增一，因此每个 Ra/Rc 的一般内部区域有 112 个实自由度。两因子 trace 固定，另加 v，总计 225；即使固定 v 也有 224。

所以当前连续 64 维编码不可能在整个 covariance family 上无损一一表示这些条件。1025 中有 Hermitian 冗余，但去除冗余后维度仍远高于 64。对任意更大的后端主干，只要全部条件仍经过同一 64 维瓶颈，这项信息丢失不会被主干容量自动补回。

这不是“loss≥某数”的下界，也不证明真实物理先验需要全部自由度。观测 r 本身可以带统计信息，任务也可能只需要部分 C 信息。不过最简单的 Gaussian prior 对照已说明一般精确 score 依赖矩阵方向：`s*(r,C)=-(Ω+Σ)^{-1}r`，同一条件编码对应不同 Σ 时通常不能同时精确表示。当前外部 posterior 读出乘 Σ 并不让 score trunk 重新获得已经丢失的条件信息。

此外，全局逐通道调制并非理论上完全不能实现相关噪声处理；卷积及非线性可把不同调制组合起来。合理疑点是表达和学习效率，不应写成“FiLM/条件归一化不能混合坐标”的绝对断言。现有 RefineNet 已有多尺度与大感受野，不能仅凭噪声相关就推断必须换 Transformer。

## 6 对下一步设计的约束性建议（未实施）

1. **先比较条件接口。** 保留主干与目标，研究不经单个 64 维瓶颈的确定性协方差输入，或逐层接入保持足够信息的因子编码。D-VDAMP/FFDNet 给出“条件直接进入特征层”的先例，但如何表达当前复矩阵是项目设计。简单加宽可作为对照，不能承诺达到某宽度就足够。
2. **把 corr+corr 作为明确的候选接口。** 保持实际污染与辅助噪声条件独立，辅助样本采用本项目完整 proper complex C；可保留精确矩阵条件。K=1/多样本的代价及有效性需单独判断，不能把 MRI 的 K=1 结果外推为本任务充分性。
3. **输出参数化单独比较。** 直接 clean mean、noise residual 或 score 都可以建立正确关系；条件均值目标宜保持 L2/匹配 DSM，不把 DRUNet 的 L1 原样搬来。保持损失定义、数据、初始化、预算可比，才能归因于接口或主干。
4. **主干替换排在接口验证之后。** 若协方差信息充分且条件使用得到验证，现有主干仍持续落后，再比较 residual U-Net 等。若替换同时改变接口、目标、数据与训练预算，就无法知道是哪一项改进起作用。

这些是研究顺序，不是新训练授权，也没有给出任何 AFDM 性能保证。所查论文的有色噪声大多在固定小波基内变化；当前两个独立随机方向的协方差族明显更广。应将“是否需要整个随机族”和“在既定族中如何表达条件”分开，不能为了得到较低 loss 偷换已授权的训练分布。
