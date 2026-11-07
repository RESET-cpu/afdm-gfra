# MAMP / SS-MAMP / LM-OAMP / OAMP-MMV 全文补读与下载缺口

记录日期：2026-10-24。范围：只读论文与项目记录；未运行推断或训练，未修改算法。下文 PDF 页码对应本目录 `papers/` 中固定的作者稿版本，并非期刊排版页码。公式是原文操作的转写；明确标为“项目推断”的部分不属于原文定理。

## 1. Cheng 2021：未取得全文，不能记为已读

Yiyao Cheng, Lei Liu, Li Ping, **Orthogonal AMP for Massive Access in Channels With Spatial and Temporal Correlations**, IEEE JSAC 39(3):726–740, March 2021；在线发表 2020-08-24，DOI [10.1109/JSAC.2020.3018799](https://doi.org/10.1109/JSAC.2020.3018799)，IEEE 文献号 9174826。

本轮未获得该文 PDF，因此没有创建 `papers/22_cheng2021_massive_access.pdf`，也不能提供其正文公式定位。下列是访问记录，表示这些入口在本次环境下没有提供全文，不表示全球不存在开放稿。

| 入口 | 实际结果 |
|---|---|
| [CityU 作者机构记录](https://scholars.cityu.edu.hk/en/publications/orthogonal-amp-for-massive-access-in-channels-with-spatial-and-te/) | 有书目信息、摘要和 DOI；未发现开放 PDF 链接 |
| [Lei Liu 作者主页研究列表](https://sites.google.com/site/leihomepage/research) | 对应条目只链接 IEEE；未发现该文作者稿 |
| [OpenAlex DOI 查询](https://api.openalex.org/works/https://doi.org/10.1109/JSAC.2020.3018799) | HTTP 200；`is_oa=false`、`oa_status=closed`、`oa_url=null`、`any_repository_has_fulltext=false`；只有 publisher location |
| [Semantic Scholar DOI 查询](https://api.semanticscholar.org/graph/v1/paper/DOI:10.1109/JSAC.2020.3018799?fields=title,openAccessPdf,url) | HTTP 200；`openAccessPdf.url` 为空 |
| [Crossref DOI 查询](https://api.crossref.org/works/10.1109/JSAC.2020.3018799) | HTTP 200；提供 IEEE VOR PDF 链接，未提供作者稿 |
| [IEEE landing](https://ieeexplore.ieee.org/document/9174826/) / DOI 重定向 | urllib 请求最终为 HTTP 202、空 HTML，非 PDF |
| [IEEE stamp](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=9174826) | HTTP 418 |
| [IEEE stampPDF](https://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&arnumber=9174826) | HTTP 418 |
| [Crossref 给出的 PDF](http://xplorestaging.ieee.org/ielx7/49/9357432/09174826.pdf?arnumber=9174826) | HTTP 418；同地址 HTTPS 也为 418 |
| [IEEE ielx7 PDF](https://ieeexplore.ieee.org/ielx7/49/9357432/09174826.pdf?arnumber=9174826) | HTTP 418 |
| [DBLP 条目](https://dblp.org/rec/journals/jsac/ChengLP21.html) | 返回挑战页面，未继续绕过 |

补查完整标题、DOI、IEEE 号，以及 Lei Liu 公开 GitHub 仓库，未找到可确认属于这篇论文的开放 PDF。Cheng 的 CityU 博士论文链接会进入版权确认/验证码页面；没有将博士论文或下面的 2023 论文替代为 2021 原文。2021 的摘要只能支持“研究空间/时间相关、采用 group Gram-Schmidt orthogonalization”的概述，不能用它支持具体实现公式。

## 2. 已补读原文及真正可迁移的操作

### 2.1 Memory AMP：要修的是有记忆处理器的正交关系，不能只加历史权重

Lei Liu, Shunqi Huang, Brian M. Kurkoski, **Memory AMP**, IEEE TIT 68(12):8015–8039, 2022。
[作者稿 v7](https://arxiv.org/pdf/2012.10861v7)；本地 [PDF](../../../literature/liu2022_memory_amp.pdf)。

**原文依据。** §III-A pp.6–7，式(20)、(22)要求当前输出误差与相应历史输入误差正交；只满足相邻两步正交，一般不足以保证有记忆算法的 Gaussian 等效描述。§III-B p.7，式(25)、(30)给出线性构造：

\[
\widehat\gamma_t=Q_ty+\sum_iP_{t,i}x_i,\quad
\gamma_t=\frac{\widehat\gamma_t-\sum_i p_{t,i}x_i}{\epsilon_t},\quad
\epsilon_t=N^{-1}\operatorname{tr}(Q_tA),\quad p_{t,i}=N^{-1}\operatorname{tr}(P_{t,i}).
\]

§III-C p.8，式(32)、(34)–(35)对非线性处理器作

\[
\phi_t=\bigl(\widehat\phi_t(R_t)-R_tu_t\bigr)/\epsilon_t^\phi,
\qquad u_t=(G_t^HG_t)^{-1}G_t^H\widehat\phi_t(R_t),
\]

其中 `G_t=[r_1-x,...,r_t-x]` 是真实输入误差。其可微、Gaussian 条件下可用各历史输入的期望偏导数表示 `u_t`，但直接计算真实 `G_t` 是 oracle 操作。若原型仅依赖最新 `r_t`，旧输入的偏导数本来就是零；不能为了“引入 memory”而随意添加旧输入系数并声称仍满足原构造。

§IV-A p.9，式(37)–(38)使用 `B=λ†I−AAᴴ`、`rhat_t=θ_t B rhat_(t−1)+ξ_t(y−Ax_t)` 和全部历史迹校正，避免每轮 LMMSE 求逆。原文一般采用 2 或 3 个非零阻尼权重，但这只是完整构造中的选择，并非脱离条件的短历史修复原则。

**代码映射。** 当前 `linear.py:49` 的 `SpatialLinear` 已缓存小型 A 的 SVD，并用各天线协方差特征模的 `fraction` 实现迹归一化（`:63–75`）；增加 memory 意味着替换完整线性递推和系数系统，而非给 `iterations.py:69` 的均值再做一次加权。非线性原型应是含活动概率的完整 `F(r)=p(r)μ(r)`；只求条件信道网络 `μ` 的导数遗漏了活动链式项。

**项目推断与优先级。** 保留网络权重是可能的，但这是外循环重构。A 的实际行数仅 16，当前缓存 SVD 便宜，MAMP 的“降低线性求逆开销”优势很有限。完整 MAMP 尚未因历史实验而被否定，但应列低优先级研究，不是现成修复。§II-B p.4 的 iid 信号、右酉不变/Haar 矩阵及大系统条件，以及 Lemma 4 p.7 的可分 Lipschitz 非线性条件，都没有自动覆盖当前重复块算子和联合网络。

尤其不能要求非线性反馈 `F−H` 本身白 Gaussian、独立于 H 后才称算法正确。论文的 Gaussian 替代变量用于相应状态演化；非线性模块输出的实际分布不必等于这些替代变量。真正要匹配冻结 AWGN 网络的是其**输入 query**及配套噪声标签，而非所有方向的消息都强制同分布。

### 2.2 SS-MAMP：可靠协方差是先决条件，已有残差融合负结果必须纳入

Lei Liu, Shunqi Huang, Yuzhi Yang, Zhaoyang Zhang, Brian M. Kurkoski, **Sufficient-Statistic Memory AMP**，作者稿 v4，2023-06-30（初稿 2021；不与三作者的 ISIT 短文混同）。
[原文](https://arxiv.org/pdf/2112.15327v4)；本地 [PDF](../../../literature/liu2023_ssmamp.pdf)。

**原文依据。** §IV-A p.8，Lemma 11、式(40)对共同单位增益 Gaussian 观测 `z_i=x+n_i`、已知联合误差协方差 V 给出充分统计量。以通常列向量 Hermitian 协方差约定转写为

\[
w=V^{-1}{\bf1}/({\bf1}^HV^{-1}{\bf1}),\qquad s=w^Hz,\qquad
v_s=({\bf1}^HV^{-1}{\bf1})^{-1}.
\]

§V-B pp.10–11，Theorem 1、式(61)–(65)不是从任意迭代器出发：原始 MAMP 必须已满足式(9)的正交性，再对两个方向使用协方差加权，才得到定理中的保正交、收敛和不劣性质。p.7 Lemma 9、式(35)，以及 p.10 式(55)–(56)处理奇异历史的方法是选有效输入子集、重复消息不增加信息。给逆矩阵随意加正则是另一个近似，不能继续无条件引用原不劣结论。p.13 Remark 6 明确说明有限尺寸下 iid Gaussian 性质与有关推论不严格成立。

**代码映射。** 若要替换 `iterations.py:69` 或 `:86` 的两条阻尼路径，至少要各自保留历史均值、跨轮误差协方差及有意义的信号增益描述。仅保存各轮标量 `v_t` 不能恢复非对角 `V_ij`。即使 `MSE/v≈1`，也没有得到跨轮误差协方差。若 query 是 `a_i H+e_i`，`Σw_i=1` 也不保证合成消息单位信号增益；信号依赖偏差并不由该权重公式消除。

**重要的本项目已有负结果。** [20261015 memory requirements 报告](../../../../archive/result_legacy_20261023/layout_20261021/before/docs/history/results/proposed_memory_requirements_20261015/REPORT.md) 已完成四条旧候选重放和 26 个三轮窗口的离线残差融合。26 个相关窗口中 14 个反馈 MSE 上升，最大增加 4.1703 dB，最大权重范数约 `1.16e5`；并不只是求逆精度问题。旧权重和旧候选的数字只约束该实现，不能当成当前冻结权重的新结果。

该报告使用 `e_i=F_i−H`、`Z_i=Y−AF_i=N−Ae_i` 精确展开了残差协方差估计的偏差：算子投影误差、反馈与同一观测噪声的交叉项、有限样本噪声功率偏差。四个旧条件的交叉项大于其余单项。这意味着不能用 `ZᴴZ−噪声项` 自动得到可信的历史误差 V；直接最小化历史残差还可能拟合观测噪声。

**项目推断与优先级。** “缓存 2–3 轮，残差估计 V，套逆协方差公式”已经不应作为新修复推荐。只有在新的独立证据表明能可靠估计所需协方差和增益后，才值得恢复这一候选。当前若使用真值计算 V，只能衡量历史组合的 oracle 空间；即使 oracle 改善，也不能省略无真值估计这一真正难点。小型 A0=16×640、用户内部 16×16 块耦合、低秩空间信道均不被增加历史长度解决。

### 2.3 Takeuchi LM-OAMP：区分参数阻尼与均值误差协方差，不将旧审计重命名为 bug

Keigo Takeuchi, **On the Convergence of Orthogonal/Vector AMP: Long-Memory Message-Passing Strategy**，作者稿 v2，2022-04-22，初稿 2021。
[原文](https://arxiv.org/pdf/2111.05522v2)；本地 [PDF](../../../literature/takeuchi2022_long_memory.pdf)。

**原文依据。** §III-C p.6 式(27)–(28)、§III-D p.7 式(44)–(45)把均值的历史线性组合与两重求和的交叉协方差相配。§IV-B Example 2 p.9 式(63)–(74)推导指数均值阻尼下的跨轮协方差递推，并与式(75)–(78)的一维启发式精度/方差阻尼区分。对两条真实误差向量，均值组合的精确代数为

\[
C_{mix}=(1-\beta)^2C_{old}+\beta^2C_{new}
 +\beta(1-\beta)(C_{old,new}+C_{new,old}).
\]

而当前 `moment_damp` (`iterations.py:18–25`) 对高斯消息的均值参数和协方差参数分别作算术插值。其传递的协方差参数未必等于混合均值的真实误差协方差，这是工作近似，不是本次发现的代码错误。20261015 temporal/history 工作已经审计过有关恒等式和估计障碍。

**项目推断与优先级。** 当前终态选中失败 query 的 `MSE/v` 中位数约 0.995，本身并不支持把方差参数修正当成主要收益来源；也不排除跨轮依赖或条件失配。可借鉴的是**诊断应保留交叉项**，而非“把 β 改平方便可修好”。即使均值当轮不变，修改 v 会改变后续网络输入和闭环轨迹，仍需作为独立候选评估。

此外，原文 §I-B、§VI 的有限维数值讨论提示 LM-OAMP 需要更大系统，较小系统上可劣于启发式阻尼。其 Assumptions 1–5 的右正交不变矩阵、iid 先验和正则性假设也未覆盖本项目固定 AFDM。完整 LM-OAMP 替换应低优先级；不能从收敛性定理推断当前活动检测改善。

### 2.4 Cheng 2023 OAMP-MMV：矩阵误差正交必须同时追踪增益，不能简化成“标量换矩阵”

Yiyao Cheng, Lei Liu, Shansuo Liang, Jonathan H. Manton, Li Ping, **Orthogonal AMP for Problems With Multiple Measurement Vectors and/or Multiple Transforms**, IEEE TSP 71:4423–4440, 2023，DOI 10.1109/TSP.2023.3327609。
[作者稿 v1](https://arxiv.org/pdf/2304.08038v1)；本地 [PDF](../../../literature/cheng2023_oamp_mmv.pdf)。以下式号来自 14 页 v1，不能标作期刊 18 页版式号。

**原文依据。** §III-B p.5 式(15)–(18)使用 `Xhat=XΘ+Z`、`E[XᵀZ]=0` 的 Gram–Schmidt 表示，状态包含矩阵信号增益 Θ 和列间误差协方差 Σ。§III-F p.6 式(31)–(34)给出

\[
X^{out}=\widehat\psi(X^{in})-X^{in}\Delta,\qquad
\Delta=\{E[(Z^{in})^TZ^{in}]\}^{-1}E[(Z^{in})^T\widehat\psi(X^{in})].
\]

这是原文实数约定。对本项目复数、非复解析网络应明确使用对应复数协方差/伪协方差表示，或者转为实坐标；不能只把每个转置机械替成共轭转置而忽略 improper 误差。§III-E p.6 式(28)–(30)允许通过相关 Gaussian 输入的 Monte Carlo 计算模块的矩阵增益及协方差响应；这为独立局部校准提供参考，但校准输入匹配真实 query 是另一个需要验证的条件。

§III-D p.5 Assumption 18 要求每个实验开始独立抽取 Haar V，实验内固定；处理器满足 PIID-separable 且独立于 V。Theorem 19 的结论允许同一行不同 MMV 列联合相关 Gaussian，**不要求所有列独立**。本项目 256 MMV 列增加了观测列数，并没有把重复的 A0 变成全维 Haar 变换。

**代码映射和必须保留的差别。** `MMVLinear.pack` (`linear.py:32`) 把 `[K,M,N,P]` 排成 `[KP,MN]`；本工况是 640×256，256=16 天线×16 输出坐标，不是 256 根天线。完整 MMV 校正是 256×256；只在天线轴保留 16×16 矩阵是有物理解释的降维近似，但省略其他列间依赖，不能称完整 OAMP-MMV。原型仍是完整 `pμ`。

`gaussian_extrinsic` (`gaussian.py:26–37`) 已支持 16×16 Gaussian 协方差计算；这不等同于任意学习映射的矩阵 GSO。更关键的是，减去 `RΔ` 后的信号增益通常不是 I。以行矩阵约定作**项目代数推断**：如果 `R=HΘ_in+E`、`F=HΘ_F+E_F`，那么

\[
F-R\Delta=H(\Theta_F-\Theta_{in}\Delta)+(E_F-E\Delta).
\]

要把它转成当前线性模块的单位增益伪观测，还需在增益矩阵可逆时右乘 `B^{-1}`，其中 `B=Θ_F−Θ_inΔ`，并把误差协方差更新为 `B^{-H}Σ_{out}B^{-1}`。这一步可能放大噪声，近奇异/不可逆的 B 也不是罕见可忽略边界。仅替换一个散度系数没有完成这个接口。

当前 `denoiser.py:89` 明确拒绝非各向同性 cavity。故保留网络权重而追踪一般矩阵消息仍需解决接口：在网络前强制补噪成为各向同性有已知功率代价；任意白化会同时改变信道先验；改为依赖 covariance 的网络则属于新的模块训练路线。矩阵 GSO 本身只消除指定二阶交叉相关，既不自动白化，也不消除所有信号依赖偏差。

**不能忽略的旧实现。** [20261015 AMP 报告](../../../../archive/result_legacy_20261023/layout_20261021/before/docs/history/results/proposed_amp_20261015/REPORT.md) 已实现完整 256×256 复数矩阵 Onsager、含活动链式项的完整 pF 差分，合成代数核验通过，但四个旧开发条件无阻尼外循环均越过方差支持。这里的 AMP Onsager 与 OAMP-MMV 的矩阵 GSO 不是同一算法，旧失败不能证明后者必失败；也不能再把“完整矩阵校正”本身当未尝试的新概念。

**项目推断与优先级。** 最值得保留的是矩阵**增益与误差协方差分开诊断**，以及用局部 Gaussian 条件响应检验完整 `pμ` 接口。部署级矩阵重构仍需先解决可估计性、输出增益和网络 cavity 支持范围，优先级低于有明确缺口的局部接口分析。不能保证 16×16 或 256×256 校正一定优于旧标量方案。

## 3. 对“如何修复”的更新判断

这些文献支持将目标表述为“使送入冻结先验模块的 query 及其条件参数匹配模块训练分布”，并不支持“增加 memory / 矩阵维度 / 正交一次就能把当前消息变成 H+独立 AWGN”。

| 可借鉴工作 | 是否改网络 | 与旧标量方法的实质差别 | 本轮判断 |
|---|---|---|---|
| 分别估计 query 的信号增益、条件残差与跨轮矩 | 不改 | 检查平均 MSE/迹看不出的结构，而非再找一个方差倍率 | 诊断价值高；只用真值时必须标 oracle |
| 按 SS-MAMP 做历史协方差加权 | 可冻结 | 使用跨轮非对角矩且要求单位增益/正交结构 | 已有朴素残差融合负结果；缺可靠无真值协方差前不推荐直接接入 |
| 完整 MAMP / LM-OAMP 外循环 | 可冻结，但模块须符合接口条件 | 整体记忆递推及正交系数共同设计 | 实质新实现，理论不能直接覆盖 AFDM；低优先级 |
| OAMP-MMV 式矩阵 GSO 加增益/协方差传递 | 权重可先冻结；query 若有色则旧网络接口不支持 | 不止矩阵散度，还需一致的增益归一化和 covariance 更新 | 已有矩阵 Onsager 失败限制，须与旧实现逐项比较；不可列成轻量必然修复 |
| 为低维 covariance 条件训练独立先验模块 | 改网络输入/训练分布，但不必展开接收机 | 模块训练使用合成条件噪声而非按十层真实迭代反传 | 概念上区别于十层展开，但独立 C 训练不自动覆盖由 query/活动估出的内生 C；属于另一路线，非本次已完成方法 |

另外，[FIRE / DD-VAMP 历史报告](../../../../archive/result_legacy_20261023/layout_20261021/before/docs/history/results/proposed_uniform_inference_20261014/REPORT.md) 已记录本项目适配失败。FIRE 有误差功率/标签接近 1、空间未中心化二阶矩接近各向同性、但信号方向负投影严重并最终全部漏检的旧例子。它清楚表明“功率正确+二阶白”不足以保证活动检测所需的条件分布；不能重新把补噪白化当未试过的新答案。旧数值不直接量化当前权重的问题，但限制了可合理推荐的动作。

若后续做同协方差 Gaussian 对照，应同时说明中心化协方差/二阶矩的区别，并分离或保留均值、信号增益与条件依赖。以新 Gaussian 误差替换真实误差同时改变多个因素，不能由性能改善推出唯一因果。选中失败样本还受筛选与新噪声重采样影响，必须与独立样本分开解释。

本轮实际产出是以上来源和操作边界，不包含新性能结果。2021 JSAC 原文仍是唯一明确未取得的文献，不以邻近论文补齐“已读全文”状态。
