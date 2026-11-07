# MMV、活动 likelihood 与协方差：下载后复核

2026-10-24。阅读本地原文、当前代码和已归档负结果；没有运行接收机、训练或更改算法。本笔记补充上一轮 `mmv_activity_notes.md`，特别纠正“全矩阵 Onsager 尚未尝试”及“当前协方差为 256×256”这两种可能误读。

## 1. 本次证据与阅读覆盖

页码均为下列本地 PDF 页码，不是期刊印刷页码；各文件在 `../papers/`，对应逐页文本在 `../text/`。没有把“打开全文”写成“逐项重证全部定理”。

| 文件 / 文献 | 细读内容与定位 | 可用于项目的内容；适用边界 |
|---|---|---|
| `06_liu2018_massive_mimo.pdf`；Liang Liu, Wei Yu, *Massive Connectivity with Massive MIMO—Part I: Device Activity Detection and Channel Estimation*, IEEE TSP 2018；[原文 v2](https://arxiv.org/pdf/1706.06438v2) | 模型和 AMP/SE pp4–6，(6)、(11)、(13)–(29)；检测与信道误差 pp7–10；Appendix A–B pp11–12 的高斯混合及各向同性推导。附录 C–G 的误检渐近证明未逐行重证。 | 先写完整矩阵 `Σ`，随后由各向同性 BG 先验和 MMSE 推断证明 `Σ=τ²I`，不是取迹即可保证白化。定理使用 iid 复高斯导频和大系统极限。p8 Theorem 4 的大天线渐近还涉及正信道增益及其下界，不能直接解释有限强相关弱用户。 |
| `08_djelouat2021_correlated_amp.pdf`；Hamza Djelouat, Leatile Marata, Markus Leinonen, Hirley Alves, Markku Juntti, *User Activity Detection and Channel Estimation of Spatially Correlated Channels via AMP in Massive MTC*, Asilomar 2021；[原文 v1](https://arxiv.org/pdf/2112.04295v1) | 5 页正文全部；核心 p3 (8)–(13)，活动误差 p3–4，仿真 pp4–5。另渲染 p3 核对公式。 | 接受有色高斯等效噪声，同时修改条件均值、活动证据和矩阵 SE。已知空间先验 `R_i`、随机复 Bernoulli 导频。仿真固定 SNR=10 dB，且平均增益归一，不能当作本项目 −4 dB 弱用户修复的数值证据。 |
| `07_hannak2018_mmv.pdf`；Gabor Hannak, Alessandro Perelli, Norbert Goertz, Gerald Matz, Mike E. Davies, *Performance Analysis of Approximate Message Passing for Distributed Compressed Sensing*, IEEE JSTSP 2018；[原文 v2](https://arxiv.org/pdf/1712.04893v2) | 正文模型/算法/联合对角化 pp2–5；各向异性及成像例子 pp6–9；Appendix A–B pp9–10；Appendix D Lemma 2 p12。Replica 附录 C 读其假设和结果，未独立复现 replica 计算。 | Algorithm 1、(9)–(11) 是矩阵 Onsager / SE；Algorithm 2、Theorem 1 是同步变换先验和 MMSE 的等变性。Appendix D 的 `Cov(x|r)=J_MMSE(r)Σ` 要求真实条件均值。不能用它把任意网络的风险预测直接换成 Jacobian。 |
| `09_kunde2026_complex_amp.pdf`；Vishnu Teja Kunde, Alessandro Mirri, Jean-Francois Chamberland, Enrico Paolini, *Complex Approximate Message Passing with Non-separable Denoising*, 2026 preprint；[原文 v1](https://arxiv.org/pdf/2604.21115v1) | Assumption 8 及主结论 pp9–11，§III-C p12 (18)–(21)、Remark 14，Appendix B pp24–27；引言、应用及结论已读。Appendix A 的全部极限证明未逐行重证。渲染 p12 核对符号。 | 非可分复网络可使用 Wirtinger Jacobian 的块部分迹，但需要完整当前映射导数；其理论仍是 iid `CN(0,1/n)` 感知矩阵。p17 明确把 structured sensing / partial DFT / OTFS 扩展列为后续工作。 |
| `10_djelouat2024_hierarchical_ep.pdf`；Hamza Djelouat, Mikko J. Sillanpää, Markus Leinonen, Markku Juntti, *Hierarchical MTC User Activity Detection and Channel Estimation with Unknown Spatial Covariance*；期刊 IEEE TWC 23(10):14620–14636, 2024，DOI [10.1109/TWC.2024.3417612](https://doi.org/10.1109/TWC.2024.3417612) | **本地是 2023 年 v1 预印本，31 页，不是 2024 最终版**：[原文](https://arxiv.org/pdf/2310.10204v1)。模型/EP/EM pp7–16，ADMM pp17–21，仿真 pp21–26，结论/Appendix A–B pp27–28 已读；参考文献仅核相关条目。渲染 pp12–14 核对疑点。 | 学习的是物理先验协方差，cavity 通过 Gaussian quotient 消除本站贡献；不等于经验误差协方差学习。先验利用簇活动和协方差信息；发射功率反比于平均增益以减少用户增益差异。其 SNR 扫描为 10–26 dB，不能外推成本项目低 SNR 证据。 |

终稿获取记录：[Oulu 2024 最终版](https://oulurepo.oulu.fi/bitstream/handle/10024/51494/nbnfioulu-202408165465.pdf?isAllowed=y&sequence=1) 在本次 urllib（含浏览器 UA）、web.open 及同机构旧地址均返回 403，IEEE PDF 入口返回 418；未下载出有效 `10b`，故无该文件 SHA/页数可报。没有用预印本替冒最终版。

## 2. 当前代码到底保存了哪些协方差

代码定位：`src/algorithm/STMP/linear.py:32,52`，`denoiser.py:75,119,179`，`iterations.py:18,68,73,78,129`，`gaussian.py:26`，`src/configs/final/STMP.json:15`。

`pack` 把 `[用户,天线,行,列]=[40,16,16,16]` 变为 `X∈C^(640×256)`；`A0∈C^(16×640)`。但是 `SpatialLinear` 当前只保存**公共 16×16 天线协方差**。每用户非线性输出先对 16×16 个行列位置取平均，再跨 40 用户平均，冻结 `isotropic` 配置又取迹为 `vI16`。

| 数学对象 | 当前代码对象 / 状态 | 不可混淆之处 |
|---|---|---|
| 活跃物理信道先验 `R_k=Cov(H_k|a_k=1)` | 隐含在物理训练样本及 first score；没有显式逐用户 `R_k` 参数 | `prior_cov` 只是线性模块的输入 Gaussian 消息参数，并不是这里的物理先验 `R_k`。Djelouat EM 学的是这一类物理先验。 |
| 条件后验中心协方差 `Cov(H_k|r_k,a_k=1)` | 以 `conditional_spatial_covariance=τ_k I16` 近似 | second 的实际训练目标与精确中心协方差之间有条件，见下文；空间之外的相关性已被压缩。 |
| 含零用户的联合后验中心协方差 | `state.spatial_covariance = p τ I16 + p(1−p) μ μᴴ/256`，随后在 `iterations` 池化 | 第二项是活动不确定性，不能省略；但用近似均值和风险代入后，不再自动是精确 Bayesian covariance。 |
| query 的实际误差协方差 `Cov(r−x)` 以及误差与信号的相关性 | `v` 是线性模块按其 Gaussian 工作模型计算的 cavity 参数；没有运行时真值误差协方差 | `trace(v)` 校准不能证明误差白、Gaussian、与信号独立，也不证明逐用户增益是 1。 |
| Gaussian site / extrinsic 协方差 | `out_v`，下一轮的 `prior_cov`；denoiser 内另有 site variance | 是精度相减后得到的辅助消息参数。即使正定，也不能直接当成真实反馈误差协方差，或物理信道先验。 |
| 观测域剩余干扰协方差 `S_{−k}` | 当前没有显式逐用户完整矩阵；公共协方差进入 SVD 线性更新 | 若采用用户 leave-one-out 线性更新，它由其他输入 site 因子的协方差构造；不是把输出后验协方差原样改名后相加。 |

另需区分两种同为 256×256 的候选：MMV Onsager 的特征轴是 `(天线,信道行)`；按每个信道行求用户 block-cavity 时，观测协方差轴是 `(帧,天线)`，用户输出协方差轴是 `(用户内列,天线)`。维度相同不代表可相互替用。

**由训练代码直接推导的限定。** `src/training/scores/direct_objectives.py:11–16` 有

`b_scaled = sqrt(v_real) sθ(r) + (r−H)/sqrt(v_real) = (μθ(r)−H)/sqrt(v_real)`。

因为 second loss 对全样本 trace 平均后再平方，理想标量读出是冻结 first 的条件风险

\[
\tau_\theta(r)=D^{-1}\mathbb E[\|H-\mu_\theta(r)\|^2\mid r]
=D^{-1}\operatorname{tr}\operatorname{Cov}(H\mid r)
 +D^{-1}\|\mu_\theta(r)-\mathbb E[H\mid r]\|^2.
\]

上式用一致的复维度/RMS 单位。只有 first 为真实条件均值时第二项为零。因此“second 训练正确”不等于“其读出能不加条件地替换后验协方差或 Onsager Jacobian”。这不是证明当前 second 有 bug；是其有限精度 first 绑定目标应如何解释。

`gaussian_extrinsic` 的精度相减代数在所用 Gaussian 参数下正确，但先对 generalized eigenvalues 截断，之后做的是调整后的 Gaussian quotient。`moment_damp` 线性插值均值与协方差**参数**；它不是实际混合误差的协方差公式，后者还包含跨轮协方差。已有这些操作不能作为实际独立 AWGN 的证明。

## 3. 文献给出的可移植非线性接口

Djelouat 2021 p3 (8)–(13) 和 Liu–Yu p5 (18)–(21)、Appendix A 的共同结构是

\[
r=x+e,\quad e\sim\mathcal{CN}(0,\Sigma),\qquad
x\mid a=1\sim\mathcal{CN}(0,R),\quad x\mid a=0=0.
\]

不要求 `Σ` 与 `R` 对易。用一致列向量约定，可独立推得

\[
\ell(r)=\log\frac{\rho}{1-\rho}
+\log\frac{|\Sigma|}{|R+\Sigma|}
+r^H[\Sigma^{-1}-(R+\Sigma)^{-1}]r,
\quad p=\operatorname{sigmoid}\ell,
\]
\[
\mu=R(R+\Sigma)^{-1}r,\quad
C=R-R(R+\Sigma)^{-1}R,
\quad D(r)=p\mu,\quad C_{\rm joint}=pC+p(1-p)\mu\mu^H.
\]

关键不是单独增加一个协方差矩阵，而是**条件均值、活动 evidence、中心协方差用同一 query 模型**。高斯 `R` 公式只能作为解析参考；本项目完整物理信道先验不是高斯，不宜无验证地用这个分类器替代已有 learned classifier。

若今后允许 colored-noise 独立训练，当前 `src/training/STMP/auxiliary.py:63` 已有正确的 AWGN 双类训练原则：正负类用同一个方差分布、独立噪声抽样。推广应保留该原则：

\[
r_+=H+Lz_+,\qquad r_-=Lz_-,\qquad LL^H=\Sigma,
\]

正负类共用同一 `Σ` 采样律（不把类别信息泄露到 `Σ`），first/second/activity 使用匹配的噪声条件、归一化、坐标和 first 特征。真实目标是

\[
\logit p(a=1\mid r,\Sigma)
=\logit\rho+\log\!\int p_H(h)\,\mathcal{CN}(r;h,\Sigma)dh
-\log\mathcal{CN}(r;0,\Sigma).
\]

只改 `trace(Σ)` 标签、只校准阈值、或只替换 second 都没有把这整个 likelihood 改正确。若只重训 activity 而冻结 first，它可以重新学习该 first 特征下的分类，但 first 本身的信道均值仍可能失配，不能宣称完成整体匹配。

Hannak Theorem 1 的 `T` 变换同时改变先验与 MMSE 映射；`Tr` 的噪声变白时，信号也变为 `TH`。除非先验与网络具有所需等变性，否则不能 `Tr → 原冻结网络 → T^{-1}` 就称等价。选择 `T` 为数据依赖估计时，独立 Gaussian 的条件还需另审。它的 BG 对角 SE 保持来自对称性，不能推广到任意 frozen score。

这条“先构造一个与具体迭代无关的高斯噪声族，并训练匹配先验模块”的方向，区别于固定十层真实轨迹展开；但是它已经放松“严格保持现有 AWGN 三网络不变”的约束，报告必须明说。

## 4. 正确矩阵 Onsager 及已经存在的负证据

沿用项目 `Y=A X+W`，`A∈C^(Q×N)`、`X,R,D∈C^(N×B)`，此处 `Q=16,N=640,B=256`。明确索引比照抄论文的转置约定可靠：

\[
R_t=X_t+A^H Z_t,\quad X_{t+1}=D_t(R_t),\qquad
(B_t)_{ab}=\frac1Q\sum_{i=1}^{N}
\frac{\partial D_{t,ib}}{\partial R_{t,ia}},\qquad
Z_{t+1}=Y-AX_{t+1}+Z_tB_t.
\]

复偏导为 Wirtinger `∂/∂R`；对 query 求导时固定该轮提供的噪声参数。上式是对应行对角 Jacobian 块的部分迹，保留全部跨特征 `a,b`，并非所有跨行导数的总和。非可分用户映射仍可依赖其全部行列；只是在部分迹时取对应输入/输出行。

若 `D=p_k μ_k`，导数必须含 `p_k ∂μ_k + μ_k ∂p_k`，且 `p_k` 通过 first 特征依赖 `r` 的链式项不能漏。合成映射 `D(R)=RC` 应给 `B=(N/Q)C=40C`，不是 `Cᴴ`；`D(R)=conj(R)C` 的 Wirtinger `∂/∂R` 为零。Kunde p12 (20)–(21) 的 Jacobian/转置排法需与具体右乘约定一起解释；这些明确索引可避免混用。

这并不是本项目尚未尝试的首选修复。已读归档根目录
`archive/result_legacy_20261023/layout_20261021/before/docs/history/results/` 下：

- `proposed_amp_20261015/REPORT.md`：完整 **256×256 复矩阵 Onsager**，包含完整 `pF` 链和跨特征依赖；合成复线性/共轭测试、活动链测试通过。四个条件均在第 2–3 次 query 越过训练支持；更完整的用户内基导数诊断仍越界。故不能把失败归结为“过去只做了标量散度”。
- `ldamp_score_swap_20261015/REPORT.md`：保存默认 L-DAMP 的实际 query 后替换 score，并使用自动微分全 256×256 Onsager（非有限差分误差）；四条闭环仍失败。同一 query 的标量 MSE/方差比约 0.9914–1.0048，冻结 score 仍明显不如原 DnCNN，说明 trace 校准不能代表完整噪声适配。
- `proposed_amp_damping_20261015/REPORT.md`：以完整历史一致公式同步阻尼 `x,z` 和 Onsager memory，`β=0.5,0.2,0.1` 均不能完成；小步长延缓越界。它不支持“再补一个 β 就能恢复 AWGN”。
- `proposed_awgn_20261014/REPORT.md`：空间协方差更新并补加 Gaussian 噪声到最大特征值，使部分白度/相关指标改善，但噪声增加约 5.85–10.01 dB，性能及支持失败未修复。不能只以白度改善定义成功。
- `proposed_mean_feedback_20261012/user_scalar_pilot/REPORT.md`：逐用户 second + 逐用户标量反馈/线性 query 对小样本没有稳定优势，弱用户 query 幅度系数仍约 0.61–0.75；标量 user-specific 并未自动恢复信号方向。

**版本边界：这些负结果使用 20261015 或更早权重，与当前 20261018/19 冻结 first/second/activity 不同。** 它们排除“从未试过/简单补项便有理论保证”的叙述，不证明当前版本任何矩阵方法都无效。Kunde 的 iid 矩阵定理不能为固定 16×640 AFDM 添加无条件保证。

## 5. 用户 Gaussian cavity：可核对的公式及平方块边界

下面是从 Gaussian 积分独立推导的工作模型；不是对 Djelouat 预印本有疑点公式的机械转录。设

\[
y=\sum_k B_k x_k+n,\quad n\sim\mathcal{CN}(0,\sigma^2I),
\qquad q^N_k(x_k)\propto\mathcal{CN}(x_k;m_k,V_k).
\]

`q^N_k` 是输入的 Gaussian site 因子。若使用正定 `V_k`，Gaussian 线性模块的**完整**后验为

\[
P=(\sigma^{-2}B^HB+\operatorname{blockdiag}(V_k^{-1}))^{-1},
\quad \hat x=P[\sigma^{-2}B^Hy+\operatorname{blockdiag}(V_k^{-1})m].
\]

取其 marginal block `P_kk, xhat_k` 后去掉本站：

\[
J_k=P_{kk}^{-1}-V_k^{-1},\quad
h_k=P_{kk}^{-1}\hat x_k-V_k^{-1}m_k,\quad
C_k=J_k^{-1},\quad r_k=C_kh_k.
\]

等价地先积分其他 site：

\[
y_{-k}=y-\sum_{j\ne k}B_jm_j,\qquad
S_{-k}=\sigma^2I+\sum_{j\ne k}B_jV_jB_j^H,
\]
\[
J_k=B_k^HS_{-k}^{-1}B_k,\qquad
h_k=B_k^HS_{-k}^{-1}y_{-k}.
\]

这是避免 double counting 的具体操作：先 Gaussian product 更新，再从 marginal 中除去输入本站，或等价地 leave-one-out 积分。不应将已经含本次 `y` 的 nonlinear posterior 均值/协方差直接当成新的独立先验，再声称本次 LMMSE 是 fresh evidence。Gaussian quotient 消除工作模型中的本站因子，但不证明有限 loopy 迭代和历次消息在真实数据下独立。

非正交导频使完整 posterior 的跨用户块通常不为零，不能因输入 site 分解就把完整 posterior 也当成精确 block-diagonal。实际 EP 可允许某些 site 精度非正而总后验仍 proper；当前实现通过截断保证正定，是一种限制后的近似，不能直接套用所有 EP 结论。

**本项目一个很强的边界。** 每用户 `A_k` 是 16×16；在其满秩、要求整个用户块响应为单位阵的条件下，按每个信道行有 `B_k=A_k⊗I16`，也是方阵。此时

\[
(B_k^HS_{-k}^{-1}B_k)^{-1}B_k^HS_{-k}^{-1}=B_k^{-1},
\]
\[
\boxed{\ r_k=B_k^{-1}y_{-k},\qquad
C_k=B_k^{-1}S_{-k}B_k^{-H}.\ }
\]

所以完整块无偏时，协方差权重不再改变 query **均值**；它改变误差统计和匹配 likelihood，均值改善主要来自其他用户的 `m_j`。小奇异值会放大噪声。若 `A_k` 奇异则无法用这个完整左逆达到单位块响应。当前公共迹归一化和旧逐用户 scalar 候选都不等于这个全块约束，不能混为一谈。

该公式适合作为基准核对“弱用户增益衰减是从何种压缩出现”的来源，而不是承诺它必定提高性能。全块输出通常跨用户内列/天线相关；严格 AWGN 冻结网络无法自动接收它。若只保持 `16×16` 或标量 covariance，必须说明丢弃了哪些相关性。利用相同模型结构可以按信道行解 256 维块，不必盲目建立 4096 维用户矩阵，但前提也是所用 site 的重复结构。

## 6. 原文公式疑点：只说明证据范围，不据此否定整篇算法

本地渲染图位于 `../page_checks/08_djelouat2021_correlated_amp_p3.png`、`10_djelouat2024_hierarchical_ep_p12.png` 至 `p14.png`、`09_kunde2026_complex_amp_p12.png`。以下均在原 PDF 图像中可见，不是 OCR 造成。

- Djelouat 2021 p3 (7) 的 Onsager 导数项按印刷式没有残差矩阵乘子，与该页声明的 `Z` 维度不相容；实现应以完整矩阵 AMP 递推重新确定。p3 (11) 的协方差乘法顺序也不应在 `R,Σ` 不对易时盲抄，稳妥 Gaussian 条件协方差是上面的 `R−R(R+Σ)^{-1}R`。
- Djelouat 2023v1 p13 (15) 明确称 `Σbar_1` 为用户 block-diagonal，(16) 却令其逆为 `ΘᴴΘ/σ²`；一般非正交导频的 Gram 含跨用户块，两句不能同时精确成立。p14 (23) 的均值公式含对向量括号求逆；(20) 的混合协方差系数印为 `1/(G a)−1`，而从同页 `p=a/G` 独立计算应为 `(1−p)/p=G/a−1`（当使用已加权均值表示时）。
- 以上不等于实验结果无效或没有实现正确版本；它意味着本地预印本不足以作为逐行复制的实现规范。最终期刊版尚未取得，不能声称终稿也保留这些问题。

## 7. 值得优先参考的两个模块

**优先 1：统一 query likelihood、条件均值与活动不确定性。** 参考 Liu–Yu Appendix A、Djelouat 2021 (8)–(13)、Hannak Lemma 2，首先明确非线性模块接受的统计模型。如果放松 frozen 约束，可将独立训练分布由 `H+AWGN` 扩展为受控 Gaussian covariance 族，并对 first/second/activity 保持一致条件；这个提案不依赖指定十层轨迹，但需要训练新的独立候选。严格 frozen 路线则必须在接口外实现足够接近原 AWGN 且不过度增加噪声的 query；上述论文没有现成保证适用于当前固定 AFDM。

**优先 2：以精确 Gaussian block-cavity 作为线性消息的代数参考。** 参考 EP 的 cavity/quotient 原则，但用上一节独立、维度一致的公式，核对全块响应、逐用户 covariance 与当前公共迹投影的关系。它更适合先作为定位压缩偏差的参考，而非直接取代主线；尤其保留 `Q=P=16` 时无偏均值退化为逆矩阵、噪声可能放大的边界。旧逐用户 scalar 负结果使“仅从公共方差改为逐用户方差”优先级较低。

完整复矩阵 Onsager 是选择 AMP 外循环后的必要 bookkeeping，不能排在这两项之前作为尚未尝试的主要修复。历史全矩阵、自动微分、同步阻尼的失败已经提示：当前问题的关键不能仅用“缺少 Onsager”概括。
