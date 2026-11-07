# 当前稿变量形式与公式呈现审查

日期：2026-11-04。状态：**本表保留修改前审查；作者随后已授权实施，当前结果见 [修订与逐式出处](FORMULA_PROVENANCE_20261104.md)**。作者要求先于语言润色检查变量大小写、字体、上下标、公式来源及表达是否多余。

## 结论与范围

这次重点不是再查有没有给每个符号补定义，而是检查符号体系和公式呈现是否本来就过于繁复。上一轮语言建议表暂缓，全部仍未实施。

主要建议是：压缩第二章式 (13) 的元素排列说明；考虑用设备矩阵块统一接收机中的信道表示；区分 AFDM 的 c1/c2 与第五章的 ck；精简不必要的后验测度名称、一次性辅助量及恒为零的训练先验校正项。不能把“不是参考论文的同一个字母或逐字公式”自动判为错误，也不能用参考文献的引用替本文适配背书。

已检查当前第二至六章、Algorithm 1、附录 A–C 中的变量和公式，并登记当前 61 个编号公式。标题、引言和结论涉及的符号也结合相应定义检查。来源核对深度不同：本轮重新读了 Cai §I-C、II、III 的相关段落，Shen §II-C 的矩阵组织，以及 Dytso 正式版 §I-B、II–III；其余来源使用现有逐式出处记录，未声称重新证明了所有公式。附录 A 的相位方案仍按既有 M4 工作安排处理。

此前 [NOTATION_AUDIT_20261103.md](NOTATION_AUDIT_20261103.md) 是修改前审查，其重名修复已有实施记录。本表只针对当前版本，不重开已经完成的 L/R/G/xi/h 等问题。作者已撤回正文符号表，本次不建议恢复该表。

## 第二章 entries 段的具体判断

当前 [第二章第 253 行](D:/afdm-gfra/paper/sections/02_system_model.tex:253) 写的是 `entries`，意思是矩阵元素；不是 `entire`。其后式 (13) 用四行等式逐一说明 Y、W、A、X 的元素排列。

**这组排列等式是正确的，但可以不作为独立编号公式保留在正文。** 它没有在当前源稿其他位置被交叉引用。需要保留的是“怎样从每帧、每设备的量组成观测矩阵”的定义，不必保持四行扁平索引的展示形式。

出处层次如下：Cai §II-A 式 (4) 使用分块拼接来定义整体导频和未知矩阵；Shen §II-C 式 (14) 后用文字交代元素对应，再以式 (15) 收集多帧。当前四行 AFDM 索引式是本稿适配，不是两篇论文已有的四行原式。旧逐句记录也实际只为引出句找到句式依据。来源：[Cai §II-A](https://arxiv.org/html/2506.00581v2#S2.SS1)、[Shen 本地原文](D:/afdm-gfra/reference/literature/shen2025.pdf)，PDF p.5。

一个可审阅的候选方式是：先将每个设备的信道块定义为 **N×MN 矩阵**，然后采用

\[
\mathbf A=[\mathbf A_1,\ldots,\mathbf A_K],\qquad
\mathbf X=[\mathbf X_1^{\mathsf T},\ldots,\mathbf X_K^{\mathsf T}]^{\mathsf T},
\]
\[
\mathbf Y=\sum_{k=1}^K\mathbf A_k\mathbf X_k+\mathbf W
=\mathbf A\mathbf X+\mathbf W.
\]

这里 A_k 为 Q×N，X_k 为 N×MN；Y、W 为 Q×MN。**当前稿的 X_k 是 M×N×N 张量，所以这不是把上述公式直接粘贴进去就完成了。** 必须把设备块定义、第三章均值/协方差、网络输入重排、算法框和图中记号一起核对。

为避免正文重新塞入另一组复杂公式，具体排列可在推导文档交代：令每根天线的 AFDM 信道矩阵行、列分别为接收、发射索引；设备矩阵按各天线信道矩阵的转置横向拼接。它的第 (n,mN+r) 个元素就是当前 H_kmrn。每帧观测按 Y_q 的转置作列向量化后转为行向量。因此，设备矩阵的标准列向量化恰好等于当前定义的 n 最快、r 次之、m 最慢的张量展开。这是本文排列关系的代数核对，不是直接沿用 Cai 的维度。

如果本轮只做很小的修改，也可以暂时保留张量对象，将式 (13) 改为紧随式 (12) 的简短定义或移至附录。这能压缩正文，但尚未解决全文张量与矩阵记号的组织问题。

## 当前审查表

“建议调整”是有明确收益的候选方案；“可精简”不是错误；“保留并注明适配”表示不能因参考论文没有完全相同的式子而删除。下表记录提出建议时的状态；后续授权及实施以本页开头链接的修订记录为准。

| 编号 | 位置与当前形式 | 核查判断 | 建议处理与边界 |
|---|---|---|---|
| A01 | II，式 (11)–(13)：分量观测、Y=AX+W、四行 entries | 式 (13) 正确，但独立编号使排列细节占据与模型主式相同的篇幅；当前没有其他交叉引用。 | **建议压缩**：正文保留观测主式和必要块定义，逐元素排列移到简短说明或推导材料。不能把定义信息全部删除。 |
| A02 | II–V：普通体 H_k、X_k、R_k、E_k 是三阶张量，粗体 X、R_L 是矩阵 | 张量与矩阵都已给出各自含义，不能直接判为公式错误；但在接收机推导中频繁切换形式，读者负担较大。 | **建议作为统一方案审阅**：接收机采用 N×MN 的设备矩阵块并用粗体，物理分量及网络三维输入在需要处重排。若保留张量，就明确同一套张量字体，不能只把几处字母加粗。 |
| A03 | II：P_qkn、A_qkn、H_kmrn、X_kmrn、Y_qmr、W_qmr 都是标量，但用普通大写 | Cai 用普通小写表示标量、粗体大小写区分向量和矩阵；当前符号没有执行这一整套约定。大写标量本身不构成数学错误。 | **随 A02 统一**：优先用矩阵元素记法或小写分量；不要另保留一套无用途的大写标量别名。P/A 的具体字母属于本文适配，不宣称是 Cai 原符号。 |
| A04 | II 式 (3)–(8) 的 c1,c2；V 式 (40)–(41) 的 c_k | c1/c2 是固定啁啾参数，c_k 是随设备/迭代变化的 site 方差；k=1,2 时完整符号也相同。此次当前稿确实仍存在。 | **建议区分**：保留 AFDM 文献中的 c1,c2；site 方差可采用 Cai 的 ext 方差标记，例如 tau_k^ext。设备下标和 site 保留规则是本文适配，不能照搬原文所有下标。 |
| A05 | II 的 t_{rm c}、tau_c；各章 pri/post/ext、tr、FD 等说明性标签 | 同样表示说明性标签的 c 字体不一致；变量索引与说明性标签不应混为一类。 | **建议统一同类标签**：如 common-delay 标签 c 使用直立体；k/q/m/n/r/i 等变量索引保持斜体。不按机械规则将所有下标一律改直立。 |
| A06 | III–V：m(R,v)、mu_k、F_k、Xhat_k 与 t_k、tau^post、tbar_X | 这些名称较多，但分别表示理想条件均值、site 条件均值、网络输出、活动混合均值及不同方差，不能全当同义量。尤其拒绝更新或保留旧 site 时，mu_k 不必等于 F_k。 | **建议统一类型和角色表达**，并保留必要区别。矩阵方案下，可把条件信道均值按 Cai 的 H^post 形式标记，网络输出仍独立表示；不通过合并 F_k/mu_k 偷改算法。 |
| A07 | II 式 (14) 写 q_tr(H_k)，III 式 (20)/(22) 又写 q_tr(dH) | 原先验允许集中于低维结构，未必有全空间普通密度；q_tr(H) 与 q_tr(dH) 之间缺少明确的密度/概率分布约定。 | **建议统一表达层次**：优先以信道分布和条件期望表达，必要时用对 H 分布的期望写边缘似然。不要仅为了模仿 Cai，把所有测度写成未经保证存在的普通密度。 |
| A08 | III 式 (20)–(21)、(24)：pi_v(dH\|R)、tilde q_k(dX)、delta_0(dX) | 数学写法可以成立，不能称为自造概念；但多引入一组后验名称及测度说明，与正文所需均值/方差相比偏重。 | **可精简**：参照 Cai 式 (22)–(23) 的条件期望/方差表达，直接给所需统计量；混合分布可用活动两情形及混合矩说明。完整测度推导保留在研究文档，原有工作模型和高斯近似条件必须留下。 |
| A09 | II 式 (15)、III 式 (23)：X_k^MMSE、p_k^Bayes、p^star、p_k | 全局贝叶斯目标、局部理想概率和实际估计确实不同；Bayes 这一说明性上标是本稿选择，不是必须来自文献的专名。 | **可精简呈现**：全局目标可行内说明，避免专门建立只使用一次的符号层级；理想与近似的区别仍须保留，不能全部换成同一个 p_k。 |
| A10 | IV 式 (36)–(38)：pi_tr=1/2，但后面一直减 logit(pi_tr) | 在当前两类先验相等的设定下，logit(pi_tr)=0。当前推导正确，但实际公式保留了一个恒零校正项。 | **可精简**：当前设定下写 z*=log(q1/q0)，接收端 p_k=sigmoid(logit(rho)+z_phi(...))；一般先验校正关系可一句交代。不把 rho 与训练先验合并，不改变训练方式。 |
| A11 | V 式 (39)：tau_raw 仅用于随后的 max | 是合法辅助变量，但仅出现于这一处定义链；没有独立物理或算法角色。 | **可合并**：tau^post=max{K^(-1)sum_k hat tau_k,tau_min}，减少一个名字。随机迹估计中的方向和步长仍有实际作用，不能一并删去。 |
| A12 | II 式 (9)：beta 的 floor 包裹公式 | 目的是在 [-pi,pi) 选相位代表值，不是额外信道机制；本稿展开正确。 | **可压缩**成 beta_k≡2pi nu_k T_frame (mod 2pi)，beta_k∈[-pi,pi)，或行内解释。保留相位等价与取值区间，不能无说明改相位搜索变量。 |
| A13 | IV 式 (28)–(34)：实/复协方差、2D、1/2、J_m、tau^star | 这些适配由实虚堆叠和方差定义产生。形式与 Cai 的复数表述不同有实际原因。 | **保留关键关系**。实数域已经明确后可局部缩短重复的 R 标签，但不能删 Sigma 的 1/2 或把每复坐标平均的分母 D 随意改成 2D。 |
| A14 | III 式 (16)–(18)；V 式 (47)：一般矩阵 LMMSE 与 SVD 形式 | Cai 的简化更新利用其特定导频结构；本稿含设备相位后的 A 不自动继承 P 的行正交。现有一般矩阵形式有必要。 | **保留公式，核对来源层次**：Gaussian conditioning 是依据；矩阵尺寸、平均迹及 SVD 化是本文适配。不能为了“公式与 Cai 一样”换成其特殊标量增益式。 |
| A15 | IV 式 (33)：P_R=J_m Sigma，与 Dytso 原文左右次序不同 | Dytso 正式版的 Jacobian 用输入行/输出列；本稿用输出行/输入列。转置约定不同，不能按外观判错。 | **保留当前乘法次序**，必要时给 J_ij=partial m_i/partial u_j 的局部约定。正式版来源为 §III Prop.1 式 (17)、PDF p.3/印刷 p.1885；旧记录的作者稿 §IV 式 (22)/p.5 属另一版本。正文引用 Prop.1 本身正确。 |
| A16 | II 式 (5)–(10)、附录 B：长 CPP、连续分数时延、跨帧关系 | 文献提供 AFDM/CPP/连续波形基础，但本稿多周期延拓、共同每设备 Doppler 及矩阵排列不是参考论文逐字原式。 | **保留必要模型适配并准确归属**。纯展开可放附录，不能退回只适用于整数时延或短前缀的公式以追求表面相同。此次未重新完成全部波形/相位实现验证。 |
| A17 | VI 式 (52)：B_Sigma、K_Sigma、O_Sigma 三个预条件矩阵 | Karras 原文是标量 c_in/c_skip/c_out；当前矩阵形式是本文推广，现稿已有 extend 说明。 | **保留并注明适配**。三个矩阵承担不同操作，不因原文没有这些字母就删除；也不把它们登记为 Karras 的原矩阵或原符号。 |
| A18 | VI 式 (49)–(55) 及附录 A：导频构造、SNR、相关噪声采样、指标与相位目标 | 既有概念、本文定义和本文推导并存，不能要求全部在同一篇参考论文找到同形公式。 | **按用途保留**，只处理实际歧义、定义缺失或不必要展开。相位方案随现有工作定稿，不借本次记号检查重开实验要求。 |

## 可保留的记号区别

- p、rho、pi_tr、p_k 分属名义活动率、接收端先验、训练类先验、后验概率。A10 只利用已设定的 pi_tr=1/2 化简，不合并其他概率。
- sigma^2 是物理噪声方差，v 是去噪输入方差，gamma 是线性模块输入方差；它们不是大小写风格问题，不应统一成同一个变量。
- 物理信道 H、活动加权信道 X、网络输出 F、条件均值 mu、活动加权估计 Xhat 的区别保留。
- hats/stars、pri/post/ext 等可为本文需要定义，不要求所有组合逐字出现在文献。检查标准是作用一致、必要、首次说明清楚，而非“组合是否曾经印在某篇论文”。
- 共轭转置 H 与普通转置 T 不能互换；由设备块拼接的写法使用 T 两次并不引入共轭。
- 已完成的重名修正和作者批准的模块名称保持；不恢复之前被作者撤掉的正文符号表。

## 已完成的核验与限制

小尺寸代数核验覆盖：张量求和/设备块乘法、矩阵列向量化次序、LMMSE 两种均值表达、SVD 平均迹及外信息、非对易协方差下的 Jacobian 右乘关系、线性均值函数的中央差分迹、活动混合空间协方差和相位包裹。12 项残差最大约为 1.74e-14，见[核验记录](../checks/notation_formula_review_20261104/VALIDATION.json)。使用的是明确标记的小尺寸合成代数例子，不是新接收机实验，也不能代替一般性证明或算法性能验证。

来源重新读取与沿用的边界：

| 来源 | 本轮实际核对 | 用途 |
|---|---|---|
| [Cai 原文](https://arxiv.org/html/2506.00581v2)、[正式版 PDF](D:/afdm-gfra/reference/literature/cai2026.pdf) | §I-C 字体约定；§II-A 式 (2)–(4)、§II-B 式 (5)；§III-A/B，含 (18)–(27)、(32) | 分块表示、后验表达、pri/post/ext、条件均值与方差；不是本文 AFDM 维度及全部适配公式的原文证明。 |
| [Shen PDF](D:/afdm-gfra/reference/literature/shen2025.pdf) | §II-C 式 (14)–(15) 及相邻矩阵元素/多帧拼接文字，PDF p.5 | 元素解释与块表示的组织方式；本文四行式 (13) 不是原式。 |
| [Dytso 正式版 PDF](D:/afdm-gfra/reference/literature/dytso2023_conditional_mean_published.pdf) | §I-B 式 (9) Jacobian 定义、§II Theorem 1 式 (15)、§III Proposition 1 式 (17)，PDF p.3 | 明确转置约定及正式版定位，不能与旧作者稿页码混用。 |
| Bemani、Huang、Ding、Menon、Karras、Vehtari、Vincent、Ma、Metzler 等 | 沿用本稿已有逐式来源和历史核验记录；此次没有重新逐页检查全部原文 | 用于来源分类与适配边界，不据此声称所有公式都经过本轮独立证明。 |

26 个稿件、书目、图形及 PDF 文件与审查前一致。没有改正文、公式、图表、代码、配置、权重或实验结果，没有编译论文或运行训练/接收机批次。

后续顺序建议：先选定设备矩阵/张量的表达方案，再整理符号和精简公式，最后处理语言。A01 与 A02 有关联；A04 可独立处理。以上均是可审核的建议，不视为作者已批准修改。

## 当前编号公式逐项登记

以下按当前源稿和 main.aux 定位；“来源/作用”是审查分类，只有上文声明的项目做了本轮原文或代数复核，不代表对每条式子完成了新的独立证明。

| 式号 | 当前位置 | 来源／作用 | 处理判断 |
|---|---|---|---|
| (1) | [eq:physical-channel](D:/afdm-gfra/paper/sections/02_system_model.tex:47) | 物理信道/阵列；Shen/Huang/Li 基础，本稿共同 Doppler 条件 | 保留 |
| (2) | [eq:upa](D:/afdm-gfra/paper/sections/02_system_model.tex:65) | 物理信道/阵列；Shen/Huang/Li 基础，本稿共同 Doppler 条件 | 保留 |
| (3) | [eq:afdm-time-signal](D:/afdm-gfra/paper/sections/02_system_model.tex:107) | AFDM 调制与 DAFT；Ding/Bemani，本文符号 | 保留，随字体方案统一 |
| (4) | [eq:daft](D:/afdm-gfra/paper/sections/02_system_model.tex:123) | AFDM 调制与 DAFT；Ding/Bemani，本文符号 | 保留，随字体方案统一 |
| (5) | [eq:cpp](D:/afdm-gfra/paper/sections/02_system_model.tex:139) | CPP 与连续波形；Bemani/Huang 基础及本文延拓 | A16：保留适配边界 |
| (6) | [eq:continuous-waveform](D:/afdm-gfra/paper/sections/02_system_model.tex:150) | CPP 与连续波形；Bemani/Huang 基础及本文延拓 | A16：保留适配边界 |
| (7) | [eq:channel](D:/afdm-gfra/paper/sections/02_system_model.tex:166) | 有效信道/路径算子；本文物理模型推导 | A02/A16：保留，整理类型 |
| (8) | [eq:path-operator-system](D:/afdm-gfra/paper/sections/02_system_model.tex:179) | 有效信道/路径算子；本文物理模型推导 | A02/A16：保留，整理类型 |
| (9) | [eq:twc-frame-channel](D:/afdm-gfra/paper/sections/02_system_model.tex:195) | 跨帧关系与相位代表值；本文推导 | A12：相位包裹可简写 |
| (10) | [eq:effective-pilot](D:/afdm-gfra/paper/sections/02_system_model.tex:203) | 相位并入导频的定义 | A01/A02：与设备块定义接通 |
| (11) | [eq:observation-tensor](D:/afdm-gfra/paper/sections/02_system_model.tex:239) | 分量观测、MMV、元素排列；Cai/Shen 组织方式与本文维度 | A01–A03：压缩和统一 |
| (12) | [eq:mmv](D:/afdm-gfra/paper/sections/02_system_model.tex:248) | 分量观测、MMV、元素排列；Cai/Shen 组织方式与本文维度 | A01–A03：压缩和统一 |
| (13) | [eq:mmv-indexing](D:/afdm-gfra/paper/sections/02_system_model.tex:262) | 分量观测、MMV、元素排列；Cai/Shen 组织方式与本文维度 | A01–A03：压缩和统一 |
| (14) | [eq:working-posterior](D:/afdm-gfra/paper/sections/02_system_model.tex:296) | Bayes 因子分解；Cai 框架、本文工作先验 | A07：明确分布记法 |
| (15) | [eq:targets](D:/afdm-gfra/paper/sections/02_system_model.tex:313) | 全局贝叶斯估计目标 | A09：可行内化，区别理想/近似 |
| (16) | [eq:linear-mean](D:/afdm-gfra/paper/sections/03_bayesian_receiver_design.tex:40) | Gaussian conditioning 和外信息；Cai/Ma/Minka 基础 | A14：保留一般矩阵形式 |
| (17) | [eq:linear-variance](D:/afdm-gfra/paper/sections/03_bayesian_receiver_design.tex:44) | Gaussian conditioning 和外信息；Cai/Ma/Minka 基础 | A14：保留一般矩阵形式 |
| (18) | [eq:linear-extrinsic](D:/afdm-gfra/paper/sections/03_bayesian_receiver_design.tex:57) | Gaussian conditioning 和外信息；Cai/Ma/Minka 基础 | A14：保留一般矩阵形式 |
| (19) | [eq:pseudo-awgn](D:/afdm-gfra/paper/sections/03_bayesian_receiver_design.tex:77) | 局部 AWGN 工作模型；Cai 框架 | 保留，区别于真实迭代误差 |
| (20) | [eq:active-channel-posterior](D:/afdm-gfra/paper/sections/03_bayesian_receiver_design.tex:89) | 活动条件后验、条件矩的定义 | A07/A08：可用期望/方差精简 |
| (21) | [eq:conditional-channel-integrals](D:/afdm-gfra/paper/sections/03_bayesian_receiver_design.tex:98) | 活动条件后验、条件矩的定义 | A07/A08：可用期望/方差精简 |
| (22) | [eq:query-densities](D:/afdm-gfra/paper/sections/03_bayesian_receiver_design.tex:115) | 两假设边缘似然与 Bayes 活动概率 | A07/A09：保留所需区别 |
| (23) | [eq:local-activity](D:/afdm-gfra/paper/sections/03_bayesian_receiver_design.tex:121) | 两假设边缘似然与 Bayes 活动概率 | A07/A09：保留所需区别 |
| (24) | [eq:mixture](D:/afdm-gfra/paper/sections/03_bayesian_receiver_design.tex:139) | Bernoulli–Gaussian 近似与联合均值；Cai/Liu 基础 | A08：测度式可精简，混合含义保留 |
| (25) | [eq:joint-spatial-covariance](D:/afdm-gfra/paper/sections/03_bayesian_receiver_design.tex:149) | 活动混合后的空间协方差与平均方差；本文排列及平均 | 保留；小尺寸恒等式已核对 |
| (26) | [eq:joint-average-variance](D:/afdm-gfra/paper/sections/03_bayesian_receiver_design.tex:159) | 活动混合后的空间协方差与平均方差；本文排列及平均 | 保留；小尺寸恒等式已核对 |
| (27) | [eq:nonlinear-extrinsic](D:/afdm-gfra/paper/sections/03_bayesian_receiver_design.tex:170) | Gaussian 消息相除；本文简记 | 保留 b 与裁剪用途 |
| (28) | [eq:colored-query](D:/afdm-gfra/paper/sections/04_generative_priors.tex:27) | 复高斯噪声的实数表示 | A13：保留 1/2 与 2D |
| (29) | [eq:tweedie-mean](D:/afdm-gfra/paper/sections/04_generative_priors.tex:38) | Tweedie 均值/协方差关系；本文实数及有色协方差表示 | A13/A15：保留条件与乘法顺序 |
| (30) | [eq:tweedie-covariance](D:/afdm-gfra/paper/sections/04_generative_priors.tex:54) | Tweedie 均值/协方差关系；本文实数及有色协方差表示 | A13/A15：保留条件与乘法顺序 |
| (31) | [eq:denoising-score-objective](D:/afdm-gfra/paper/sections/04_generative_priors.tex:73) | DSM 及均值重参数化损失；Vincent/Cai 基础、本文权重 | 保留训练目标，非文献逐字公式 |
| (32) | [eq:first-loss](D:/afdm-gfra/paper/sections/04_generative_priors.tex:87) | DSM 及均值重参数化损失；Vincent/Cai 基础、本文权重 | 保留训练目标，非文献逐字公式 |
| (33) | [eq:mean-derivative-variance](D:/afdm-gfra/paper/sections/04_generative_priors.tex:123) | 条件均值导数与中央差分迹；Dytso/Metzler 基础及本文估计 | A13/A15：保留精确/近似区别 |
| (34) | [eq:derivative-trace](D:/afdm-gfra/paper/sections/04_generative_priors.tex:146) | 条件均值导数与中央差分迹；Dytso/Metzler 基础及本文估计 | A13/A15：保留精确/近似区别 |
| (35) | [eq:activity-log-odds](D:/afdm-gfra/paper/sections/04_generative_priors.tex:158) | Bayes 对数赔率、交叉熵、理想 logit 与实际活动概率 | A10：可使用已确定的平衡训练条件简化 |
| (36) | [eq:classifier-loss](D:/afdm-gfra/paper/sections/04_generative_priors.tex:179) | Bayes 对数赔率、交叉熵、理想 logit 与实际活动概率 | A10：可使用已确定的平衡训练条件简化 |
| (37) | [eq:ideal-logit](D:/afdm-gfra/paper/sections/04_generative_priors.tex:186) | Bayes 对数赔率、交叉熵、理想 logit 与实际活动概率 | A10：可使用已确定的平衡训练条件简化 |
| (38) | [eq:activity-probability](D:/afdm-gfra/paper/sections/04_generative_priors.tex:198) | Bayes 对数赔率、交叉熵、理想 logit 与实际活动概率 | A10：可使用已确定的平衡训练条件简化 |
| (39) | [eq:pooled-variance](D:/afdm-gfra/paper/sections/05_overall_algorithm.tex:30) | 方差汇总与下限；本文数值规则 | A11：可去掉一次性 tau_raw |
| (40) | [eq:site-update](D:/afdm-gfra/paper/sections/05_overall_algorithm.tex:41) | Gaussian site 除法/乘法；EP 基础与本文保留规则 | A04/A06：区分 c_k，不合并 F_k 与 mu_k |
| (41) | [eq:conditional-moments](D:/afdm-gfra/paper/sections/05_overall_algorithm.tex:48) | Gaussian site 除法/乘法；EP 基础与本文保留规则 | A04/A06：区分 c_k，不合并 F_k 与 mu_k |
| (42) | [eq:noise-estimation](D:/afdm-gfra/paper/sections/05_overall_algorithm.tex:116) | 样本协方差/噪声谱估计；Wax/Nadakuditi 基础 | 保留，非新算法命名 |
| (43) | [eq:query-variance-target](D:/afdm-gfra/paper/sections/05_overall_algorithm.tex:130) | 期望负对数似然目标与尺度阻尼；Vila 思路、本文更新 | 保留，不能宣称原论文同式 |
| (44) | [eq:query-variance-update](D:/afdm-gfra/paper/sections/05_overall_algorithm.tex:138) | 期望负对数似然目标与尺度阻尼；Vila 思路、本文更新 | 保留，不能宣称原论文同式 |
| (45) | [eq:input-damping](D:/afdm-gfra/paper/sections/05_overall_algorithm.tex:151) | 消息阻尼；Cai 思路、本文作用对象 | 保留迭代与角色区别 |
| (46) | [eq:output-damping](D:/afdm-gfra/paper/sections/05_overall_algorithm.tex:165) | 消息阻尼；Cai 思路、本文作用对象 | 保留迭代与角色区别 |
| (47) | [eq:linear-fraction](D:/afdm-gfra/paper/sections/05_overall_algorithm.tex:190) | 线性模块 SVD 等价式；本文代数 | A14：恒等式已核对 |
| (48) | [eq:iteration-complexity](D:/afdm-gfra/paper/sections/05_overall_algorithm.tex:208) | 当前运算步骤的复杂度计数 | 保留；未重新审计全部实现代价 |
| (49) | [eq:pilot](D:/afdm-gfra/paper/sections/06_simulation_results.tex:25) | 部分 DFT 导频构造；本文索引及能量 | 保留定义，不要求参考论文同形 |
| (50) | [eq:snr](D:/afdm-gfra/paper/sections/06_simulation_results.tex:36) | 接收信号功率定义 SNR | 保留评价定义 |
| (51) | [eq:simulation-colored-covariance](D:/afdm-gfra/paper/sections/06_simulation_results.tex:87) | 训练相关噪声随机协方差族 | 保留本文采样定义 |
| (52) | [eq:mean-preconditioning](D:/afdm-gfra/paper/sections/06_simulation_results.tex:129) | Karras 标量预条件的协方差矩阵推广 | A17：保留并注明适配 |
| (53) | [eq:gaussian-evidence](D:/afdm-gfra/paper/sections/06_simulation_results.tex:189) | Gaussian site 模型的解析似然比 | 保留，区别于学习先验的精确密度 |
| (54) | [eq:simulation-nmse](D:/afdm-gfra/paper/sections/06_simulation_results.tex:221) | NMSE/AER 的本稿汇总定义 | 保留样本范围与分母 |
| (55) | [eq:simulation-aer](D:/afdm-gfra/paper/sections/06_simulation_results.tex:229) | NMSE/AER 的本稿汇总定义 | 保留样本范围与分母 |
| (B.1) | [eq:path-entry-expansion](D:/afdm-gfra/paper/sections/appendix_afdm_channel_model.tex:14) | 由正文连续波形推得的展开及整数时延形式 | 保留推导归属；不自动替换为短前缀公式 |
| (B.2) | [eq:integer-operator](D:/afdm-gfra/paper/sections/appendix_afdm_channel_model.tex:25) | 由正文连续波形推得的展开及整数时延形式 | 保留推导归属；不自动替换为短前缀公式 |
| (B.3) | [eq:integer-prefix-phase](D:/afdm-gfra/paper/sections/appendix_afdm_channel_model.tex:28) | 由正文连续波形推得的展开及整数时延形式 | 保留推导归属；不自动替换为短前缀公式 |
| (A.1) | [frontend:eq:phase-atom](D:/afdm-gfra/paper/sections/appendix_parameter_estimation.tex:20) | 相位响应、拟合目标、消去线性增益；AFDM 本文构造/O’Leary 基础 | 随既有相位工作定稿，本轮不改方案 |
| (A.2) | [frontend:eq:phase-fit](D:/afdm-gfra/paper/sections/appendix_parameter_estimation.tex:34) | 相位响应、拟合目标、消去线性增益；AFDM 本文构造/O’Leary 基础 | 随既有相位工作定稿，本轮不改方案 |
| (A.3) | [frontend:eq:phase-variable-projection](D:/afdm-gfra/paper/sections/appendix_parameter_estimation.tex:49) | 相位响应、拟合目标、消去线性增益；AFDM 本文构造/O’Leary 基础 | 随既有相位工作定稿，本轮不改方案 |
