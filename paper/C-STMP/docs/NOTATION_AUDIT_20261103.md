# 当前全文变量、名称出处与一致性核查

日期：2026-11-03。对象：检查时 `main.tex` 实际载入的第 I–VI 章、附录 A–C、Algorithm 1、表格与三张方法图。未将停用的第二阶训练附录、旧稿、STMP/DU 稿件或代码内部变量算进当前论文。本文保留修改前的检查结果、行号与建议。

**后续状态：重名修复和必要定义已实施，新增符号表已按作者最新要求撤回。** 当前呈现方式见[回退记录](../checks/notation_inline_only_20261103/REVISION_NOTES.md)；具体改名、允许保留的局部复用及公式核验见[原实施记录](../checks/notation_cai_shen_20261103/REVISION_NOTES.md)。下文的“未定义”“建议”“尚未修改”等均描述核查时版本，不再作为当前待办清单。

## 结论

目前不能说“所有变量名称均逐字来自现有论文，且全文没有重复”。

1. 主要物理量、后验量、得分函数、外信息及密度比等概念有文献依据。具体字母、维度、下标和本文辅助量有相当部分是本稿定义，不是原论文的原符号。这种适配本身合理，不能为追求“全部有出处”而虚报来源。
2. 有明确的跨章节重名：`L`、`R`、`G`、`xi`、`tau` 和向量 `h_k`。其中 `h_k` 的两个对象维度也不同，应优先区分。
3. 有首次定义不完整、索引约定没有接通、同义量使用两个名称的问题。需要补定义和统一，不需要改变模型或重跑实验。
4. 字母相同不自动构成错误。例如天线数 `M` 与带下标的预条件矩阵、函数参数与局部求和下标，应结合字体、完整上下标、对象类型和作用域判断。下列清单分别列出实际重名与可接受复用，不以机械字符计数制造问题。

## 出处核查应如何理解

采用四种判定：**文献概念**（名称及技术含义有来源）、**本文适配**（沿文献概念，改记号或推广对象）、**本文定义**（为本文公式、设置或评价定义的辅助量）、**书目外来源**（已找到论文用例，但不是当前参考文献条目）。后两者不是自动不合格；不能将它们登记为“原论文已有同名同定义”。

| 本文记号或名称 | 原文对应与定位 | 核查结论 |
|---|---|---|
| `K,M,N,alpha_k,H_k,X_k`；活动概率 `rho`；导频 `P_{qkn}` | Cai v2 §II-A、Table I、式 (1)–(4)，PDF p.4：使用 `K,M,N,alpha_k,H_k,X_k`，活动先验用 `lambda`，导频用 `q_{ktn}`，导频时隙数用 `T`。 | 部分同字母；本文 AFDM 张量维度、`rho,P,Q` 等是适配。不能说本文的整个符号表照搬 Cai。 |
| `N,L` 表示 OTFS 子载波数、时隙数 | Shen §II-B、式 (2)–(10)，PDF p.4：原文对应 `M,N`。 | 明确改记为本文 `N,L`，以便保留 `M` 表示天线数。 |
| `F_A,c_1,c_2,N_CPP,varphi_n,G(d,nu;g)` | Bemani §II-B、III-A/B；连续波形见 Bemani 博士论文 §3.1.1，式 (3.7)、(3.9)，印刷 pp.26–27。Ding §II 与 Huang §II/IV 提供调制及卫星信道用词。 | 变换、CPP、调制参数是文献概念；`F_A`、多周期扩展、本文路径矩阵及其参数排列为本文记号/推导。 |
| `X_L,t_L,R_L,v_L,gamma,mu_k,t_k` | Cai §III-A/B、Table I：原文以 A/B 模块下的 `pri/post/ext` 均值、方差组织消息。 | 后验均值/方差、外信息均值/方差有来源；本文这组简记不是 Cai 的原符号。 |
| `m_R,P_R,J_m,Sigma,tau^star` | Dytso §I 式 (3)、§IV Proposition 1 式 (22)，PDF pp.2、5：原文使用 `E[X\|Y=y]`、噪声协方差 `K_N`、条件协方差和 Jacobian。 | 本文实数展开、输出行/输入列 Jacobian、除以复坐标数 `D` 是明确适配；原文不能证明这些字母逐字沿用。 |
| `z_phi,ell_k,p_k,pi_tr,a` | Menon–Ong §2.2、§3 式 (6)–(8)、§4.2 式 (16)–(17)，PDF pp.2–3：原文用 `eta` 表示类别后验、`pi` 表示类别先验、`r=p/q` 表示密度比。 | 密度比与分类后验的联系有来源；本文的 logit 网络、AFDM 输入及字母是适配。 |
| `E_k,c_k` 对应 Gaussian site | Vehtari §2.1，PDF pp.5–6，式 (1)及其后的 site 定义与更新。 | site 概念有出处；本文信道先验的各向同性形式、均值/方差参数及更新保留规则为本文定义。 |
| `B_Sigma,K_Sigma,O_Sigma` | Karras §5 式 (7)及 Table 1：原文为标量 `c_in,c_skip,c_out`。 | 协方差矩阵推广及这三个矩阵名称是本文适配；正文已经说明 extend，归属合理。 |
| `d_k,nu_k,b_k,J_k` 的前端优化 | O'Leary–Rust §1 式 (2)–(3)；Shen §III-C 说明相位更新所用的相关估计思路。 | variable projection 是已有方法；本文 AFDM 响应、候选搜索和参数符号不是该文原模型。 |
| `L,lambda_i,bar lambda_j,g_j,r_s` 的 MDL 估计 | Nadakuditi–Edelman §II-A 式 (5)–(7)，印刷 pp.2626–2627。 | 样本协方差、特征值和尾部均值有来源；此处 `L=QN` 是本文选的字母，恰与 OTFS 的 `L` 冲突。 |
| `E_p` 的 pilot energy | 当前 VI-A 第 35 行再次使用此名称。Cai p.4 的对应名称是 transmit power budget。Tang 等 *Pilot-Based Sensing With OFDM and AFDM: A Resource-Matched Performance Comparison* 摘要确有 pilot energy，现有旧审计另记 §III-A。 | **书目外来源**；不是自造名词，但不能归给 Cai 或声称本稿已有书目已覆盖。第二章旧审计曾通过直接公式处理此项，不能将那个局部处理当作第六章也已通过。 |
| `kappa,eta,b,w_k,zeta,L_s,L_d,d_var` | Cai §V-B1 支持 damping；本文 V-B、VI-A 给出具体更新和停止条件。 | 更新/阈值的具体组合及符号为本文定义。没有必要替这些辅助量编造“论文原名”。 |

MFLE、GPJD、GP-MP-CCD 是作者批准的本文名称，**不是已有论文的完整原名**。既有批准记录见 `TERMINOLOGY.md` 的 2026-10-31 模块命名记录及 2026-11-01 复核记录。此处只澄清来源，不将已批准名称重新列为必须删除项。

## 优先区分的重名

以下位置按本次源文件行号记录。建议写法尚未应用；改名后的符号仍属于本文定义。

| 记号 | 当前两个含义及位置 | 影响与最小建议 |
|---|---|---|
| `$\mathbf h_k$` | [II-A:44](../sections/02_system_model.tex:44)：`h_k(t_c,tau)` 是 M 维物理信道冲激响应；[A-A:16](../sections/appendix_parameter_estimation.tex:16)：`h_k(d,nu)` 是 QN 维候选导频响应。 | 相同字体、设备下标和二元函数形式，却不是同一个向量。前端改为 `$\mathbf h_k^{\mathrm p}(d,\nu)$`，并明确维度。 |
| `$L$` | [II-B:207](../sections/02_system_model.tex:207)、附录 B：OTFS 每帧的 OFDM 符号数；[A-C:98](../sections/appendix_parameter_estimation.tex:98)：`L=QN` 个空间观测样本。 | 两个全局计数不应同名。保留 OTFS 的 L，将噪声估计样本数改为 `$N_{\rm s}=QN$`。 |
| `$R$` | [III-B:79](../sections/03_bayesian_receiver_design.tex:79)、IV、VI：去噪输入；[VI-A:100](../sections/06_simulation_results.tex:100)：生成协方差因子的矩阵。 | 第六章同时用两者，区分不够直观。协方差因子统一用粗体 `$\mathbf R_{\rm a},\mathbf R_{\rm c}$`，生成式用 `$\mathbf R_{\rm corr}$` 或直接对两个因子分别写定义。 |
| `$G$` | [VI-A:104](../sections/06_simulation_results.tex:104)：16×4 随机矩阵；[B-B:58](../sections/appendix_afdm_channel_model.tex:58)：前缀采样点数。另有 II-B 的粗体路径算子 `$\mathbf G(d,\nu;g)$`。 | 前两者为完全相同的斜体记号，第三者靠粗体区分。前缀长度改用 `$N_{\rm pre}$`；训练随机矩阵可写 `$\mathbf Z_{\rm tr}$`。 |
| `$\xi$` | [II-B:145](../sections/02_system_model.tex:145)：时间 `xi T_s` 的无量纲参数；[VI-A:100](../sections/06_simulation_results.tex:100)：协方差随机混合系数。 | 无联系的实参数重名。训练混合系数改为 `$\xi_{\rm corr}$` 即可。 |
| `$\tau$` | [II-A:44](../sections/02_system_model.tex:44)：物理信道的时延自变量；[V-A:41](../sections/05_overall_algorithm.tex:41)：汇总并截底后的条件方差。 | 时间与归一化信道方差的量纲不同。裸方差记号可写 `$\tau_{\rm post}$`；`tau_raw,tau_min,tau^star,hat tau` 的关联应在符号表说明。无需因此改动所有路径时延。 |

## 定义、同义量及索引问题

| 项目 | 当前状况 | 建议 |
|---|---|---|
| `$\mathcal T$` 与场景索引 i | [VI-A:249](../sections/06_simulation_results.tex:249) 直接用于 NMSE/AER；前句说 evaluated scenes，但未显式把集合赋名。i 此前是迭代序号。 | 写明 T 为当前评价点的场景索引集合；评价样本用另一局部索引，如 e。跨条件汇总时说明集合元素为场景–条件对，避免把复用场景误数成独立场景。 |
| `$L_z,\delta$` | [IV-C:172–183](../sections/04_generative_priors.tex:172) 直接出现在随机迹估计式；VI-A 才给 `L_z=1,delta=10^-2`，未在首次出现处说明计数及步长。 | 在公式前定义 `L_z` 为随机方向数、正数 delta 为有限差分步长；步长可写 `$\delta_{\rm FD}$`，区别于 Dirac delta。 |
| `$\delta_0(dX_k)$` | [III-B3:170](../sections/03_bayesian_receiver_design.tex:170) 用于零点概率质量；第二章只定义了 `delta(.)` 为 Dirac delta function。 | 补一句这里为零点的 Dirac 概率测度。两种写法相关但对象/记法不完全相同，不能说第二章已完整定义。 |
| `$\theta,\phi$` | IV 中先后用于网络与损失下标，但没有直接说明分别为去噪器、分类器可训练参数。 | 各网络首次出现时补定义即可；无需给参数字母另找论文出处。 |
| `$\epsilon_{\rm mach}$` | [A-C:109](../sections/appendix_parameter_estimation.tex:109) 用作特征值下限，无显式定义。 | 说明所用数值精度下的机器精度。不要与 IV 的随机向量 epsilon 或 V 的裁剪 epsilon 混同。 |
| Algorithm 1 的裸 `$P$` | [V-A:86](../sections/05_overall_algorithm.tex:86) 写 pilot tensor P；此前仅定义 `P_qkn` 与矩阵粗体 P。 | 直接写 `{P_qkn}`，或补 `P=[P_qkn]` 的维度。不能默认裸 P 就等于粗体矩阵 P。 |
| `$\widehat P_H$` 与 `$P_{\rm tr}$` | [V-A:77](../sections/05_overall_algorithm.tex:77) 为训练平均 `$\lVert H\rVert_F^2/D$`；[VI-B:277](../sections/06_simulation_results.tex:277) 为 normalized training-channel power。文本未交代两者关系。 | 目前描述指向同一类统计量。若同一训练集/归一化，则统一符号；若不同估计或样本集，写出区别。本次未据名称相近就断言运行时两个数值必相等。 |
| `vec` 的张量顺序 | III 开始使用 `vec(H)`；IV、VI 指定协方差按 antenna–output–input 排列，但 Notation 未显式定义哪个下标变化最快。 | 给出 `[vec(H_k)]_{mN^2+rN+n}=H_kmrn`（零基编号），再定义实部/虚部堆叠。这样可直接核对 Kronecker 因子的次序。此式是建议约定，写入前需与实现对齐。 |
| 矩阵列编号 | II 的元素式用 `mN+r`（0 到 MN−1），后验因子用 `j=1,...,MN` 并称第 j 列。 | 属于可转换的两套编号，尚不能据此判定计算公式错误；应明确 `j=mN+r+1`，或统一所有列下标起点。 |
| 矩阵/张量字体 | 大部分二维矩阵为粗体，但训练 `C,R_a,R_c,G` 用普通斜体；H/X/R/E 为三阶张量，mu 为张量均值。Notation 未说明这套约定。 | 至少统一协方差矩阵字体，并说明张量的记号约定。不要把普通字体 G 的矩阵与标量重名问题留给读者猜测。 |
| `clip`、单位虚数 j 等运算符 | logit/sigmoid 已在 IV-D 显式定义；clip 在 V-B 给出调用范围，但无函数定义，j 未在 Notation 说明。 | 在统一 Notation 中简写裁剪定义和 `j^2=-1`，无须分别增加技术引用。 |

## 可以保留或低成本改善的局部复用

这些不等同于前表的高优先级冲突。

| 记号 | 判断 |
|---|---|
| `$p,\rho,\pi_{\rm tr},p_k$` | 分别是名义活动概率、条件非空后的边缘概率、分类训练先验、接收端后验概率。VI-A 和 IV-D 已区分，**不应为了统一字母合并**。 |
| `$\sigma^2,v,\gamma,t_k,\overline t_X$` | 分别为物理噪声方差、去噪输入方差、反馈先验方差、条件信道方差、活动混合后的平均方差。不是同义重复；现有公式有定义。 |
| `$H_k,X_k,\mu_k,\widehat X_k$` | 物理有效信道、活动乘信道、条件均值、联合均值的区别必要；III 已给出 `X_k=alpha_k H_k` 与 `hat X_k=p_k mu_k`。 |
| `$m(R,v)$` 与天线下标 m | 函数和下标的作用域明确，可保留。若整理符号表，写全函数而非只列字母 m。 |
| `$\mathbf U_k$` 与 SVD 的 `$\mathbf U$` | 有无 k 下标且定义不同；不是完全相同符号。给 SVD 因子加 svd 下标可提高检索性，但无需列为数学错误。 |
| `$b$` | III/V 为方差比，附录 B 为 OTFS Doppler bin，IV 的 sigmoid 定义又把它作哑元。前两种意义不相关，建议把 OTFS 下标写成 `b_D`；函数定义哑元不必逐个改名。 |
| `$\zeta_n(w)$` 与 `$\zeta$` | 波形中的取整函数与停止历史权重，完整符号不同。停止权重可加 hist 下标；不需动波形公式。 |
| `$s,s_i,s_{qk}[t]$` | 归一化尺度、奇异值、时域信号；完整符号已区分。优先给奇异值增加明确的序号范围，避免 i 与迭代序号并用造成误读。 |
| `$d,d_k,d_{k\ell},d_{\rm var}$` | 连续归一化时延、前端候选时延、OTFS 整数时延、停止残差。附录 B 已写 integer-delay grid，不能把 d 强行解释为处处同一种取值域。停止残差有专用下标，可保留。 |
| `$g,g_q,g_{k\ell},g_j,g_\theta$` | 分别为起始采样位置、帧起点、路径增益、特征值几何均值、网络主干。完整函数/下标可区分；其中附录 A 的 `g_j` 最宜改为 `g_j^eig`，减少与帧起点族混淆。 |
| `$c_1,c_2,c_k,c_{kn}$` | 调制参数、site 方差、导频列置换索引。不是同一完整符号，但宜在表中分别列清类型，不能把 c_k 误读为调制参数。 |
| `$\phi,\phi_{kn},\varphi_n$` | 分类网络参数、导频随机相位、波形函数。phi 与 varphi 是不同字形，不能机械认作完全重名；仍应补网络参数定义。 |
| `$\lambda,\lambda_i$` | 波长与协方差特征值；物理/谱分析两处局部定义均明确。可保留，不应把 Cai 原活动先验 lambda 再引入本稿。 |
| i、j、k、ell、n、r、q、t 等下标 | 求和/局部下标允许复用。重点修正“迭代 i 与评价 i”“0/1 基列编号”的阅读衔接，而非给每个求和号强行分配全新字母。 |
| EP 后缀 | 第六章明确解释为 estimated phases，但本稿同时使用 expectation propagation，后者在文献中通用缩写正是 EP。属于缩写层面的误读风险；可用图例括注 estimated phases。未改作者已确定的曲线标签。 |

## 全文符号族登记

下表覆盖本次活动源文件中的量、函数和辅助记号，合并同一对象的分量、设备/迭代下标及估计形式。这里的中文释义用于检查对象，**不是声称正文已经使用这些完整英文名称**。文献编号见末尾；“自定”表示符号/操作为本文定义，不表示技术概念无出处。

### 物理模型、导频与观测

| 符号族 | 含义/类型 | 首次定义与来源状态 |
|---|---|---|
| K、k；M、M_y、M_z、m、n_y、n_z | 设备及阵列数量/索引 | II、II-A；Cai/Shen/Li 概念，索引与坐标适配。 |
| L_k、ell；g_kell | 路径数、路径索引、复路径增益 | II-A 信道式后；Shen II-A。 |
| h_k(t_c,tau) | 连续物理信道冲激响应，M 维 | II-A；Li II-B/Shen II-A，当前共同 Doppler 模型适配。重名见前表。 |
| t_c、tau、tau_kell、tilde tau_kell、tau_c | 时间、时延自变量、差分/传播/公共时延 | II-A；Shen/Li。时间原点为自定。 |
| nu_k、nu | 设备共同 Doppler 及单路径算子参数 | II-A/B；Huang IV，单位由 `nu T_s` 明确。 |
| a_k；mu_y,k、mu_z,k；lambda；d_y、d_z、d_v | 阵列响应、方向余弦、波长、阵元间距 | II-A 阵列式后；Shen/Li；v 在该处仅为方向集合哑元。 |
| Q、q；N、n、r；t | AFDM 帧/子载波数及发射、接收、离散时间索引 | II-B；Huang/Ding，范围与排列自定。 |
| P_qkn、p_qk、粗体 P | 导频元素、向量、Q×KN 矩阵 | II-B；Cai/Arvinte 概念；排布自定。算法裸 P 定义需补。 |
| E_p | 每设备每帧导频向量平方范数 | II-B 定义、VI-A 称 pilot energy；书目外用词证据见前表。 |
| s_qk[t]、粗体 s_qk | 时域发送信号、N 维向量 | II-B；Ding II，AFDM 公式适配。 |
| F_A、c_1、c_2 | DAFT 矩阵及调制参数 | II-B；Bemani/Ding/Huang。 |
| T_s、Delta f、N_CPP、T_frame | 采样间隔、子载波间隔、前缀长度、帧时长 | II-B；Ding/Huang/Bemani，含 CPP 时长自定。 |
| <x>_N、x、floor | 非负模 N 余数及其运算 | II-B 明确定义；纯数学记号，不照抄 Shen 的居中余数。 |
| varphi_n(xi)、xi、w_xi、zeta_n(w)、w | 连续波形、时间参数、余数及取整辅助函数 | II-B；Bemani 博士论文波形依据，延拓与辅助符号自定。 |
| H_k^(q)、H_k、H_kmrn | M×N×N 有效信道及分量 | II-B；effective channel 概念有出处，张量定义自定。 |
| 粗体 G(d,nu;g)、D_nu,g、B_d；d、g | 单路径 AFDM 算子、两个因子、延时/起点参数 | II-B 路径算子式；文献变换/波形基础上的自定表示。 |
| g_q、beta_k、A_qkn、粗体 A、hat A | 各帧起点、跨帧相位、含相位的导频与估计矩阵 | II-B/C；Shen 提供 phase rotation 概念；当前关系与符号自定。 |
| alpha_k、rho、X_k、X_kmrn | 活动指示、活动先验、活动与信道的乘积 | II-C；Cai II-A，rho 为改记。 |
| Y_q、Y_qmr、粗体 Y；W_q、W_qmr、粗体 W | 逐帧及堆叠的接收信号/物理噪声 | II-C；Cai II-A；维度和索引为 AFDM 适配。 |
| sigma^2、hat sigma^2 | 物理复噪声方差及其估计 | II-C、V-B、附录 A；与 v 明确区分。 |
| 粗体 X；x_j、y_j、j | 堆叠未知矩阵及第 j 列 | II-C；Cai；零基元素与一基列序号需接通。 |
| q_tr、q(·\|Y)、p(y_j\|x_j)、p(X_k\|H_k,alpha_k)、p(alpha_k) | 信道先验、联合后验、似然、约束、活动因子 | II-C；Cai II-B 的概念；q/p 的选择自定。 |
| X_k^MMSE、p_k^Bayes | 全局 MMSE 与活动后验目标 | II-C；Cai；与后续局部近似量区分。 |

### 推断与学习

| 符号族 | 含义/类型 | 首次定义与来源状态 |
|---|---|---|
| X^pri、X_k^pri、gamma | 反馈的 Gaussian 均值与每坐标方差 | III-A；Cai III-A，本文简记。 |
| X_L、Sigma_L、t_L | 线性后验均值、每列协方差、平均方差 | III-A；Cai III-A，本文维度。 |
| R_L、R_L,k、v_L | 线性外信息均值与方差 | III-A；Cai/Ma/Minka。 |
| R_k、R、v、W_k、D=MN^2 | 去噪输入、等效噪声及复坐标数 | III-B；Cai AWGN 观测概念，本文尺寸与简记。 |
| pi_v(dH\|R)、H、dH | 活动条件下的信道后验及积分变量/测度 | III-B1；条件后验概念，记法自定。 |
| m(R,v)、Sigma_H(R,v)、mu_k、t_k | 理想条件均值/协方差及近似均值/标量方差 | III-B1；Cai 后验矩概念，近似关系已定义。 |
| q_1,v、q_0,v、p^star(R,v)、p_k | 两假设密度、理想及近似局部活动概率 | III-B2；Bayes 关系与 Cai 概念；完整记号自定。 |
| tilde q_k、delta_0、hat X_k | Bernoulli–Gaussian 近似及联合均值 | III-B3；Cai/Liu；delta_0 需补定义。 |
| U_k、C_X,k、bar t_X | 条件均值的矩阵重排、空间协方差、平均方差 | III-B3；混合矩概念有出处，重排与平均自定。 |
| b、gamma_out、X_k,out | 方差比、Gaussian 外信息方差及均值 | III-B3；Cai/Minka 的消息相除；b 是自定简记。 |
| h_R、u、C、Sigma、粗体 epsilon | 实表示、复/实扰动协方差、标准实 Gaussian 向量 | IV-A；复实展开及本文记号；Dytso 条件均值基础。 |
| q_Sigma^R、m_R、P_R、J_m | 实密度、条件均值、条件协方差、均值 Jacobian | IV-A/C；Dytso/Efron/Cai，记号与 Jacobian 布局适配。 |
| S_theta、f_theta、F_theta、F_k、theta | 得分估计、实/复均值网络及输出、参数 | IV-B/D；Cai/Vincent 的得分匹配概念；三个函数之间关系已给，theta 需明说。 |
| L_SM、L_DSM、L_ch | 得分匹配、去噪得分匹配及信道训练目标 | IV-B；Vincent/Cai；矩阵权重及归一化适配。 |
| R_a、R_c | 天线维和输入坐标维的协方差因子 | IV-B 引出、VI-A 生成；Shastri 支持相关噪声/条件信息思路，具体 Kronecker 分布自定。 |
| tau^star、z_ell、w_ell、Delta_ell f_theta、hat tau_theta | 理想条件方差、随机方向、有限差分、估计量 | IV-C；Dytso/Metzler；方向分布、中央差分和符号自定。 |
| L_z、delta | 方向数、有限差分步长 | IV-C 使用、VI-A 给值；首次定义需补。 |
| a、pi_tr、z_phi、z^star、phi、L_act | 分类标签、训练先验、logit、最优 logit、网络参数及损失 | IV-D；Menon 关系；本文标签/输入/网络自定，phi 需明说。 |
| ell_k、logit、sigmoid | 对数密度比及两函数 | IV-D；Menon 的赔率关系，经本稿对数参数化；两个函数已显式定义。 |

### 算法、实验与附录

| 符号族 | 含义/类型 | 首次定义与来源状态 |
|---|---|---|
| hat tau_k、tau_raw、tau、tau_min | 单设备估计、汇总、截底及下限 | V-A；从 IV 方差得到，汇总/阈值/符号自定。 |
| E_k、c_k | Gaussian site 均值、方差 | V-A；Vehtari/Minka 概念，形式自定。 |
| hat P_H | 初始化用的训练信道平均功率 | V-A；直接数学定义，与 P_tr 的关系待统一。 |
| i、I、I_min、I_max；hat alpha_k | 迭代序号/次数及活动判决 | V-A 算法、V-C、VI-A；自定范围与阈值。 |
| tilde v、v_tar、bar v、kappa、eta | 方差候选、目标、阻尼后方差、比率、权重 | V-B；Vila/Cai 支持估计/阻尼概念，具体更新自定。 |
| s | 训练信道均方根归一化尺度 | V-B；自定，VI-A 给值。归一化后沿用原符号已有明确说明。 |
| epsilon、clip | 方差比裁剪下限与算子 | V-B；操作自定，建议补显式函数定义。 |
| 粗体 U、V、s_i、f_L | SVD 因子/奇异值及线性更新比例 | V-C；SVD 通用记号，f_L 自定；U 与 U_k 可区分。 |
| C_phase、C_theta、C_phi、C_iter | 相位、网络、单次迭代的计算量 | V-C；由操作数量定义，无需冒称文献原变量。 |
| r_q、c_kn、phi_kn | 导频 DFT 行、列置换、随机相位 | VI-A；本文导频构造的辅助量。 |
| p、Y_0、SNR_dB、f_c | 名义活动概率、无噪观测、接收 SNR、载频 | VI-A/表 I；定义清楚，p 与 rho 不可合并。 |
| 普通字体 R、G、xi | 训练相关矩阵、随机因子、混合系数 | VI-A；自定采样分布，存在前表的重名。 |
| B_Sigma、K_Sigma、O_Sigma、sigma_d^2、sigma_d、g_theta | 输入/跳连/输出预条件矩阵、名义实方差与主干网络 | VI-A；Karras 标量形式推广，非原矩阵定义。 |
| v_min、v_max、ell_k^G | 训练方差范围与 Gaussian site 的对数密度比 | VI-A；范围及公式自定，和学习密度比 ell_k 有明确区别。 |
| d_var^(i)、w_k^(i)、zeta、L_s、L_d | 停止残差、活动历史与稳定窗口 | VI-A；本文停止规则，不是文献算法名称。 |
| T（花体）、X_ik、alpha_ik、H_ik、hat X_ik | 评价集合及场景维度的量 | VI-A 指标式；集合及场景索引首次定义需补。 |
| NMSE_dB、AER、N_MD、N_FA | 评价指标、漏检与虚警数 | VI-A；Cai/Shen 指标概念；本文汇总方式由公式指定。 |
| P_tr | 独立去噪 Gaussian 基线的归一化训练功率 | VI-B；与 hat P_H 的关系未交代。 |
| Y_s、G_0(d,nu)、h_k(d,nu) | 前端观测重排、去掉固定相位的算子、导频响应 | A-A；自定 AFDM 构造，h_k 重名。 |
| d_k、nu_k、b_k、Z_k、J_k | 候选路径参数、天线增益、剩余观测、目标函数 | A-A；O'Leary 支持消去线性参数，具体符号自定。 |
| beta、nu_j、nu_max、hat nu_k、hat beta_k | 相位候选、Doppler 候选、搜索界及最终估计 | A-A；由相位关系自定，nu_max 与 VI 的支持范围应明确对应。 |
| L=QN、hat R_y、y_qr | 噪声估计样本数、样本协方差、空间样本 | A-C；Nadakuditi 所述 MDL 基础，L 与 OTFS 重名。 |
| lambda_i、bar lambda_j、g_j、hat r_s、epsilon_mach | 协方差特征值、尾部均值、估计秩、机器精度 | A-C；MDL 公式基础有出处，符号/数值下限自定。 |
| G_rn、zeta_tn、Omega_d、Pi_l、l、粗体 s | 路径矩阵分量、整数时延展开的辅助量/置换 | B-A；由 II 波形推导；泛型序列及移位 l 局部定义。 |
| L、B、G、Q_A、Q_O、T_block、N_obs | OTFS 时隙、带宽、共同前缀长度、匹配帧数/时长/观测数 | II-B、B-B；Shen 模型按本文资源约束改记；L/G 重名。 |
| H_kmbdr^O、b、d、r、h_k^d[d]、d_kell、tilde g_kell | 共同 Doppler 条件下的 OTFS 表示及分量 | B-B；Shen 式 (9) 在本文约束下的展开，维度/相位约定已说明。 |
| Pi_L(x)、x、t | OTFS 有限 Fourier 和及局部哑元 | B-B；Shen 的 Pi_N 改记，并与粗体移位置换区分。 |
| F_N、F_L、Lambda_c、c | DFT 与 chirp 对角矩阵 | B-C；Bemani 式 (16)；c 为该函数的局部参数。 |
| C_FFT(n)、C_A、粗体 S、X_DD | 变换乘法计数、AFDM 成本、时域/延迟–Doppler 符号矩阵 | B-C；计数符号自定，矩阵消去依据 Xu §II 式 (1)、(4)–(5)。 |

附录 C 未增加独立数学变量族，沿用 K、Q、p、rho、迭代/阻尼设置及指标。三张方法图的网络与消息符号均能对应 II–V；系统图的 x、y、z、O 是坐标轴及原点标签。因子图采用 j=1,...,MN 的列序号，因而同样需要上述零基/一基映射说明。

通用运算记号另包括 CN、N（正态分布花体）、E、Pr、Cov、Var 的相关表达、I、0、R/C 数域、Z/N+、复共轭转置 H、转置 T、范数、迹、diag、vec、Re/Im、gradient、Hessian、div、Kronecker 积、指示函数、O(·)、argmin、min/max、log/exp、floor、mod、pi 常数。它们不是待寻找新“方法名”的变量；按本文定义及通用数学用法处理。不要把 LaTeX 宏名 `relu`（展开为 Re，且不是当前新增算法变量）当成正文的 ReLU 网络。

## 来源与证据边界

- **Cai v2**：本轮直接复查本地 `reference/reviews/stmp_message_awgn_review_20261024/main_sources/cai2026_stmp_v2.txt` 的 §II/Table I，并结合既有 III–V 逐式记录。原文：[2506.00581v2](https://arxiv.org/html/2506.00581v2)。
- **Shen**：本轮直接复查 `reference/reviews/section_structure_20261009/shen.txt` 的 §II-B 和式 (7)–(10)。原文：[2412.20806v1](https://arxiv.org/html/2412.20806v1)。
- **Ding、Huang、Li、Bemani、Arvinte**：名称依据复用已逐项核对的 [第二章清单](CHAPTER_II_NAMES_AUDIT.md)、[已实施修订](../checks/ch2_named_expressions_revision_20261101/REVISION_NOTES.md) 和本稿 `TERMINOLOGY.md`；本轮重新读取当前定义，未把旧清单的历史“待核”项原样算作当前问题。连续波形依据：[Bemani 博士论文](https://www.eurecom.eu/publication/7447/download/comsys-publi-7447.pdf)，§3.1.1。
- **Dytso**：本轮直接核对 [作者稿](https://arxiv.org/pdf/2104.01883) §I、§IV Proposition 1 式 (22)，PDF pp.2、5。原文 Jacobian 布局与本文不同，本文已显式定义输出行/输入列；不能仅按乘法左右次序宣告公式冲突。
- **Menon–Ong**：本轮直接核对 [PMLR 原文](https://proceedings.mlr.press/v48/menon16.pdf) §2.2、§3、§4.2，PDF pp.2–3。本文 `a=0/1` 与原文正负标签相适配。
- **Vehtari**：本轮直接核对 [JMLR 原文](https://www.jmlr.org/papers/volume21/18-817/18-817.pdf) §2.1，PDF pp.5–6，式 (1)及 site 定义。
- **Karras**：本轮直接核对本地 `reference/literature/karras2022_edm.pdf`，Table 1（PDF p.3）、§5。原文：[2206.00364](https://arxiv.org/abs/2206.00364)。
- **O'Leary–Rust**：本轮直接核对 [作者稿](https://www.cs.umd.edu/users/oleary/software/varpro.pdf) §1，式 (2)–(3)，PDF p.2。
- **Nadakuditi–Edelman**：本轮直接核对 [作者稿](https://math.mit.edu/~edelman/publications/sample_eigenvalue.pdf) §II-A，式 (5)–(7)，PDF pp.2–3。
- **Tang**：本轮核对 [作者摘要](https://arxiv.org/abs/2610.23420) 中 pilot energy 用例；其 §III-A 的更细页码来自既有第二章审计，不冒称本轮重新读过该 PDF。此文不在当前 `references.bib` 中。
- **Metzler、Vincent、Efron、Liu、Ma、Minka、Vila、Shastri、Xu**：复用当前正文相应引文及 `TERMINOLOGY.md` 已记录的章节/公式依据；此次不把全部历史文献重新逐字比对当成已完成工作。

本次完成的是当前全文的符号含义、定义位置、来源归属和重名检查；**不将“概念有依据”换算为“所有完整英文搭配均已在同一参考论文逐字出现”**。新提出的记号仅为建议，没有将其登记为文献的既有命名，也没有据此改变研究结论。

## 文件核验

本轮只新增本报告并补文档索引/术语记录。没有改写 `.tex`、图、书目、PDF、代码、配置、权重或实验结果；没有执行训练、批量实验或论文重编译。

检查时 `main.tex` SHA-256：`98cbcc826d6cfed4e7527adf4a82f0dde79f277135ede65b77b33e26da08da8d`。

检查时 `main.pdf` SHA-256：`b01b54da05fba5a1f8cf3b578c448575df0d9377a3261adcf2d2ec21a6842e09`。
