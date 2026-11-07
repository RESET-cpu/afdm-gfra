# 第三至第五章逐段核对：是否基于 Cai 原文作最小增删替换

**结论：不是。当前 49 个正文段落中，没有整段能够确认属于“保留 Cai 原段句序与主要措辞、只作必要增删替换”。** 当前版本采用了蔡文的分章逻辑和若干共同推导，但正文包含大量重新组织的表述，以及技术方案变化所需的新增内容。

上一轮完成的是通用框架、后验量学习、具体算法的内容归位，不能将其报告为逐段原文最小改写。前两轮保存的逐段对应表也属于论述任务与公式的映射，不能作为逐句底稿记录。

原文：[Cai v2](D:/afdm-gfra/reference/literature/cai2026_stmp_v2.pdf)，arXiv:2506.00581v2，第三至第五章，PDF 第 5–11 页。当前稿：第三章第 4–5 页、第四章第 5–6 页、第五章第 6–8 页。表内 Cai 页码和公式编号均属于原文。

## 核对口径

- **A：可确认原文最小增删替换。** 可找到具体原段，句序、主要句式和各句作用保持，变化限于必要变量、模型或技术条件适配。当前没有整段满足这一判定。
- **B：有对应论述，但已重新表述。** 共用同一推导或段落任务，当前做了明显压缩、合并、移位或句法重写。
- **C：技术适配或多处内容重组。** 与 Cai 存在对应基础，但当前改变了估计量、假设、计算路径，或混入本文方法及其他来源，不能把整段作为原段小改。
- **D：本文新增论述。** 在核对的 Cai III–V 中没有可支撑该段的对应底稿；部分采用其他已引用文献。这里的“新增”只指相对蔡文的内容差异，不等于已证明原创性。

正文段落按 LaTeX 空行划分；连续公式及紧接的解释归入同一段，章节标题、框图和算法框单列。短的 where/with 解释段也计入，没有因段落较短而省略。具体源码、段落文本和版本哈希保存在 EVIDENCE.json。

| 章节 | 正文段数 | A 最小替换 | B 对应后重写 | C 技术适配/重组 | D 新增论述 |
|---|---:|---:|---:|---:|---:|
| 第3章 | 15 | 0 | 5 | 8 | 2 |
| 第4章 | 17 | 0 | 1 | 6 | 10 |
| 第5章 | 17 | 0 | 2 | 6 | 9 |
| 合计 | 49 | 0 | 8 | 20 | 21 |

分类用于说明每段没有满足最小改写的主要原因；不是相似度评分，也不把任何通用短语的重合当成整段底稿证据。

## 第3章逐段结果

| 当前段落及位置 | 段首定位 | Cai 对应位置 | 判定 | 具体核对 |
|---|---|---|---|---|
| [3-01](D:/afdm-gfra/paper/C-STMP/sections/03_bayesian_receiver_design.tex:6) · 章首 | The posterior in [公式/引用] combines the observation likelihood with the channel and activity priors. Follow… | III 开篇，p.5 | B | 沿用了线性估计与先验去噪的分工；当前先从后验因子关系起笔，删去了 sum-product、因子图节点和 turbo decoding 的解释，并把 EP 放在结尾。句序和句法已重写。 |
| [3-02](D:/afdm-gfra/paper/C-STMP/sections/03_bayesian_receiver_design.tex:44) · Linear Estimation | The input to linear estimation is a Gaussian message from joint denoising. Its mean matrix is denoted by … | III-A，式(6)–(8)，p.5 | C | 把原文初始化节点消息、形成 belief、配平方及标量投影的数段压成一段；当前直接给完整矩阵均值和协方差，原文给部分正交条件下的简式。既有重写，也有模型适配。 |
| [3-03](D:/afdm-gfra/paper/C-STMP/sections/03_bayesian_receiver_design.tex:66) · Linear Estimation | The scalar $t_{\rm L}$ averages the posterior variance over the $KN$ coefficients in a column. In our mod… | 对照 III-A 式(7)–(8)，p.5；V-C 式(66)，p.11 | D | 相位旋转可能破坏行正交性、因此保留完整矩阵，是针对本文 AFDM 观测矩阵新增的解释；Cai 对应处采用部分正交假设，没有这段论述。 |
| [3-04](D:/afdm-gfra/paper/C-STMP/sections/03_bayesian_receiver_design.tex:73) · Linear Estimation | For message exchange, the posterior covariance is approximated by $t_{\rm L}\I_{KN}$ [公式/引用]. Dividing th… | III-A，式(6)后的标量投影及式(9)–(11)，pp.5–6 | B | 把原文两处的协方差近似与 Gaussian 相除合成一段，并新增消除输入信息的解释；共享公式关系，但不是逐句小改。 |
| [3-05](D:/afdm-gfra/paper/C-STMP/sections/03_bayesian_receiver_design.tex:86) · Linear Estimation | Reorganizing $\mathbf R_{\rm L}$ by device gives the tensor inputs to joint denoising, with common varian… | III-A，式(11)后的消息传递段，p.6 | B | 对应原文消息作为 B 输入的功能；当前改成按设备重排张量的一句，省去因子图流向与输入等式。是压缩重述，无法确认原句最小替换。 |
| [3-06](D:/afdm-gfra/paper/C-STMP/sections/03_bayesian_receiver_design.tex:92) · Joint Channel Estimation and Activity Detection | The relation $X_k=\alpha_kH_k$ couples the channel and device activity. Following [公式/引用], we calculate t… | III-B 开篇、式(12)–(14)、式(20)，p.6 | C | 保留先信道、再活动、最后合成的顺序；将原文后面出现的 AWGN 解释提前，用带活动变量的设备级模型代替分块消息推导。论证位置和数学对象均有调整。 |
| [3-07](D:/afdm-gfra/paper/C-STMP/sections/03_bayesian_receiver_design.tex:109) · Channel Estimation | Conditioned on $\alpha_k=1$, [公式/引用] describes the channel observed in AWGN. Its likelihood and the prior… | III-B1，式(15)–(23)，pp.6–7 | C | 当前直接从活跃条件后验出发，合并了 Cai 关于非归一化项、Gaussian 投影、后验积分和 AWGN 去噪解释的多个段落；当前保留完整条件协方差，再定义设备级近似量，句子不是原文小改。 |
| [3-08](D:/afdm-gfra/paper/C-STMP/sections/03_bayesian_receiver_design.tex:138) · Activity Detection | Activity detection compares the hypotheses $R_k=W_k$ and $R_k=H_k+W_k$. Integrating over the channel in t… | III-B2，式(28)–(31)，p.7 | C | Cai 用信道 Gaussian 外信息计算活动概率，随后给二值判决；当前定义完整先验积分的活跃似然、说明归一化作用，再写 Bayes 概率。这是实质性替换，不能归为仅换变量。 |
| [3-09](D:/afdm-gfra/paper/C-STMP/sections/03_bayesian_receiver_design.tex:165) · Joint Estimation and Extrinsic Message | Under the two activity hypotheses, $X_k$ is either zero or equal to $H_k$. Averaging the conditional chan… | III-B3，式(32)、(35)–(36)，p.7 | C | 原文先投影 Bernoulli–Gaussian belief，再给均值和逐元素方差；当前先对两个活动假设求全期望与全协方差。推导形式、顺序和协方差对象都不同。 |
| [3-10](D:/afdm-gfra/paper/C-STMP/sections/03_bayesian_receiver_design.tex:178) · Joint Estimation and Extrinsic Message | The first covariance term represents channel uncertainty under the active hypothesis. The second accounts… | III-B3，式(32)、(35)–(37)，p.7 | C | 当前新增两个协方差项的含义解释，再引出 Bernoulli–Gaussian 近似；Cai 在投影前先识别该混合分布。是重排和解释性增写。 |
| [3-11](D:/afdm-gfra/paper/C-STMP/sections/03_bayesian_receiver_design.tex:194) · Joint Estimation and Extrinsic Message | For the spatial covariance, write the entries of $\mu_k$ as $\mathbf U_k\in\mathbb C^{M\times N^2}$, with… | 对照 III-B3，式(36)–(38)，p.7 | D | 当前构造 M×M 空间协方差并沿 N² 个信道位置平均；Cai 对应段给逐元素方差及逐列标量平均，没有当前空间协方差段。 |
| [3-12](D:/afdm-gfra/paper/C-STMP/sections/03_bayesian_receiver_design.tex:204) · Joint Estimation and Extrinsic Message | Averaging its trace over devices and antennas gives the scalar posterior variance | III-B3，式(38)及其解释，p.7 | C | 两处都用平均方差，但当前对设备和天线取全局平均，Cai 保留逐列方差。当前句子很短，也不能据此认定存在原句底稿关系。 |
| [3-13](D:/afdm-gfra/paper/C-STMP/sections/03_bayesian_receiver_design.tex:215) · Joint Estimation and Extrinsic Message | The feedback uses a Gaussian approximation with mean $\widehat X_k$ and common variance $\overline t_X$. … | III-B3，式(39)–(42)，pp.7–8 | B | 共享 Gaussian 后验除以输入消息的运算；当前引入 b 并把节点消息语言改成 Gaussian 反馈近似的解释，整段为重新表述。 |
| [3-14](D:/afdm-gfra/paper/C-STMP/sections/03_bayesian_receiver_design.tex:225) · Joint Estimation and Extrinsic Message | For $0<b<1$, this message has a finite, positive variance. Reorganizing its means into $\mathbf X^{\rm pr… | III 结尾，式(42)后的反馈段，p.8 | C | 反馈成为下一轮输入与原文相同；当前增写 0<b<1 的条件，并用矩阵重排闭合迭代。原文则给两组输入/外信息等式并引向 Algorithm 1。 |
| [3-15](D:/afdm-gfra/paper/C-STMP/sections/03_bayesian_receiver_design.tex:229) · Joint Estimation and Extrinsic Message | Evaluating these updates requires the conditional channel moments in [公式/引用] and the activity probability… | III-B1，式(22)–(23)后，p.7；IV 开篇，p.8 | B | 保留高维积分难算、后文引入学习的论证任务，但将原文分散的衔接移到章末，并加入活动概率。这是跨段重组。 |

## 第4章逐段结果

| 当前段落及位置 | 段首定位 | Cai 对应位置 | 判定 | 具体核对 |
|---|---|---|---|---|
| [4-01](D:/afdm-gfra/paper/C-STMP/sections/04_generative_priors.tex:4) · 章首 | The message updates in Section~[公式/引用] require the conditional channel mean, conditional variance, and po… | IV 开篇，p.8 | C | 原文引出均值和方差的 score 表示及 DSM；当前改为条件均值、均值导数方差和密度比活动估计三条路径。第三条及具体方差路径来自本文方案。 |
| [4-02](D:/afdm-gfra/paper/C-STMP/sections/04_generative_priors.tex:16) · Conditional Mean and Denoising Score Matching | Consider first the conditional mean in [公式/引用]. Following the connection between MMSE denoising and score… | IV-A，式(43)及式(44)引出段，p.8 | C | 原文从各列共用标量噪声方差出发；当前引入 2D 维实表示、一般协方差 C 及其复到实转换。不是更换符号即可得到的段落。 |
| [4-03](D:/afdm-gfra/paper/C-STMP/sections/04_generative_priors.tex:35) · Conditional Mean and Denoising Score Matching | At fixed $C$, let $q_{\bm\Sigma}^{\mathbb R}$ denote the density of $\mathbf u$. Tweedie's formula gives … | IV-A，式(44)前，p.8 | C | 共享引出 Tweedie 公式的任务；当前新增固定 C 的密度定义，并使用一般协方差的实坐标公式。原句的经验 Bayes 和先验形式说明没有保留。 |
| [4-04](D:/afdm-gfra/paper/C-STMP/sections/04_generative_priors.tex:45) · Conditional Mean and Denoising Score Matching | For $C=v\I_D$, this is the real representation of the conditional mean in [公式/引用]. The posterior integral… | IV-A，式(44)后的解释，p.8 | B | 都把后验均值解释为观测加 score 修正；当前先说明 C=vI 特例，再用两句概括原文多句解释，属于压缩重述。 |
| [4-05](D:/afdm-gfra/paper/C-STMP/sections/04_generative_priors.tex:50) · Conditional Mean and Denoising Score Matching | Although the score in [公式/引用] is unknown, pairs of clean and perturbed channels can be generated from $q_… | IV-B，式(46)–(48)引出段，p.8 | C | Cai 先提出未知 score 的匹配目标，再转 DSM；当前直接参数化条件均值并给协方差加权误差损失。目标参数化与论证顺序均已改变。 |
| [4-06](D:/afdm-gfra/paper/C-STMP/sections/04_generative_priors.tex:62) · Conditional Mean and Denoising Score Matching | The expectation averages clean channels, covariances, and perturbations. At every fixed $C$, the unrestri… | IV-B，式(47)–(49)及解释，pp.8–9 | C | 原文说明 score matching 与 DSM 的最优解等价、代入条件 score、组合噪声等级；当前先给条件均值最优解，再通过重参数化说明与加权 DSM 的关系。属于本文损失对应推导。 |
| [4-07](D:/afdm-gfra/paper/C-STMP/sections/04_generative_priors.tex:74) · Conditional Mean and Denoising Score Matching | Conditioning on $C$ makes this construction applicable to a family of perturbation covariances [公式/引用]. T… | 对照 IV-B，式(49)，p.9；V-B1，pp.9–10 | D | 协方差条件、有色 Kronecker 扰动及在线 C=vI 的组合不在 Cai 这些段落中。Cai 的多噪声等级和有限维失配讨论只能提供部分背景，不能充当当前整段底稿。 |
| [4-08](D:/afdm-gfra/paper/C-STMP/sections/04_generative_priors.tex:94) · Variance from Conditional-Mean Derivatives | The conditional mean also determines the channel uncertainty needed by [公式/引用]. For $\mathbf P_{\mathbb R… | 对照 IV-A 式(45)，p.8；IV-C 式(50)–(54)，p.9 | D | Cai 用二阶 score 并训练另一网络；当前采用均值 Jacobian 与协方差的恒等式，明确引自 Dytso。计算路径不同，不能登记为蔡文原段小改。 |
| [4-09](D:/afdm-gfra/paper/C-STMP/sections/04_generative_priors.tex:106) · Variance from Conditional-Mean Derivatives | The trace sums real and imaginary variances, so division by $D$ gives the variance per complex coordinate… | 对照 IV-C，式(53)前，p.9 | D | Cai 说明只需匹配二阶 score 的迹；当前说明实/复方差归一化和均值散度。只共享需要一个方差标量的目标，具体论述是新增。 |
| [4-10](D:/afdm-gfra/paper/C-STMP/sections/04_generative_priors.tex:112) · Variance from Conditional-Mean Derivatives | We approximate this quantity by replacing the exact mean with $f_\theta$ and estimating its derivative tr… | 对照 IV-C，p.9；无当前有限差分段 | D | 随机符号探针、协方差加权方向和中心有限差分是当前方差估计方法，引用 Metzler；Cai 在此训练二阶 score 网络，没有对应的逐句底稿。 |
| [4-11](D:/afdm-gfra/paper/C-STMP/sections/04_generative_priors.tex:130) · Variance from Conditional-Mean Derivatives | Both evaluations hold $C$ fixed and differentiate the complete mean map, including the preconditioning in… | 对照 IV-C，p.9；无当前计算说明 | D | 固定 C、对完整预条件均值映射求导以及无需额外方差网络，均服务于本文实现；Cai 对应实现依赖第二个 score 网络。 |
| [4-12](D:/afdm-gfra/paper/C-STMP/sections/04_generative_priors.tex:142) · Activity Detection via Density Ratio Estimation | To obtain the activity probability, rewrite [公式/引用] as The remaining quantity is the density ratio $q_{1,… | 对照 III-B2，式(30)，p.7；IV 无对应小节 | D | Bayes log odds 与二分类密度比学习是本文引入的活动估计路径。Cai 使用解析 Gaussian 活动似然，未在第四章学习分类器。 |
| [4-13](D:/afdm-gfra/paper/C-STMP/sections/04_generative_priors.tex:155) · Activity Detection via Density Ratio Estimation | To construct the two classes, draw $a\in\{0,1\}$ with $\Pr(a=1)=\pi_{\rm tr}=1/2$. For $a=1$, generate $R… | III–V 无对应的分类样本及交叉熵训练段 | D | 两类样本、训练先验 1/2、同噪声采样分布、分类特征和交叉熵目标均为当前方案的训练定义。 |
| [4-14](D:/afdm-gfra/paper/C-STMP/sections/04_generative_priors.tex:173) · Activity Detection via Density Ratio Estimation | At the population optimum over unrestricted logits, this loss recovers the training posterior log odds: | III–V 无对应的分类最优 logit 段 | D | 当前说明二分类总体最优解的后验 log odds；Cai 第四章讨论 score matching 的最优解，二者不能因都谈最优性而视为原句对应。 |
| [4-15](D:/afdm-gfra/paper/C-STMP/sections/04_generative_priors.tex:181) · Activity Detection via Density Ratio Estimation | Subtracting the training prior log odds therefore estimates the log density ratio [公式/引用]. With $F_k=F_\t… | 对照 III-B2 式(30)，p.7；无训练先验校正段 | D | 减去训练先验 log odds、恢复密度比再加入在线活动先验，采用当前所引 Menon 的关系；不是蔡文解析活动概率公式的变量替换。 |
| [4-16](D:/afdm-gfra/paper/C-STMP/sections/04_generative_priors.tex:193) · Activity Detection via Density Ratio Estimation | where $\logit a=\log[a/(1-a)]$ and $\sigmoid b=(1+e^{-b})^{-1}$. The activity prior $\rho$ enters through… | III–V 无对应的 logit/sigmoid 定义段 | D | 当前定义两个函数，并说明学习密度比与在线活动先验的关系。Cai 对应概率式没有这组定义和训练先验分离步骤。 |
| [4-17](D:/afdm-gfra/paper/C-STMP/sections/04_generative_priors.tex:198) · Activity Detection via Density Ratio Estimation | The classifier uses the observation together with $F_k$, so its features include the channel estimate obt… | IV-C 结尾冻结一阶网络的训练说明，p.9；V-A，p.9 | C | 先训练后冻结的顺序与 Cai 有局部对应，但蔡文冻结一阶 score 网络以训练二阶 score；当前冻结均值网络训练活动分类器，并新增确定性特征保持最优 logit 关系的说明。整段不能称最小改写。 |

## 第5章逐段结果

| 当前段落及位置 | 段首定位 | Cai 对应位置 | 判定 | 具体核对 |
|---|---|---|---|---|
| [5-01](D:/afdm-gfra/paper/C-STMP/sections/05_overall_algorithm.tex:7) · Overall Algorithm | Substituting the estimators developed in Section~[公式/引用] into the framework of Section~[公式/引用] yields GP-… | V-A，式(55)–(56)及 Fig.3 的引出段，p.9 | C | 都把学习结果接入 TMP，但当前增加算法名称展开及 MFLE/GPJD 与第三章的对应，并接入分类器和均值导数方差。句序及混合算法组成均有变化。 |
| [5-02](D:/afdm-gfra/paper/C-STMP/sections/05_overall_algorithm.tex:18) · Overall Algorithm | For a Gaussian input $(R_k,v)$, the denoiser gives $F_k=F_\theta(R_k,v\I_D)$, and the classifier gives $p… | V-A，式(55)–(56)，p.9；III-B1，式(23)，p.7 | C | Cai 用一阶和二阶 score 网络读出均值及逐列方差；当前用均值网络、导数迹和分类器，并给全设备共用方差及下限。不能作为原文均值/方差段的小改。 |
| [5-03](D:/afdm-gfra/paper/C-STMP/sections/05_overall_algorithm.tex:32) · Overall Algorithm | To represent the learned channel moments in Gaussian messages, we use a site approximation to the channel… | III-B1，式(24)–(27)，p.7 | B | 高斯后验除以输入似然与蔡文信道外信息关系对应；当前将它移入第五章，改用 site 概念和 Vehtari 引文，并重新解释参数意义。保留的是运算关系。 |
| [5-04](D:/afdm-gfra/paper/C-STMP/sections/05_overall_algorithm.tex:44) · Overall Algorithm | Combining the site with the current input then yields | III-B3，式(33)–(34)，p.7 | B | 恢复条件均值、方差的公式与蔡文 Gaussian 合并关系对应；当前这一句为新的简短引导语，原文通过 where 直接解释式(32)。公式等价不证明句子来自原句最小替换。 |
| [5-05](D:/afdm-gfra/paper/C-STMP/sections/05_overall_algorithm.tex:51) · Overall Algorithm | For an accepted update, these expressions recover $\mu_k=F_k$ and $t_k=\tau$, so the site transmits the l… | 对照 III-B1，式(26)–(27)，p.7；无当前接受规则 | D | 训练方差范围、0<τ<v 接受条件、否则保留旧 site，是本文更新规则；不能由 Cai 的外信息公式推出其已采用相同实现。 |
| [5-06](D:/afdm-gfra/paper/C-STMP/sections/05_overall_algorithm.tex:57) · Overall Algorithm | The resulting iteration couples channel estimation and activity detection through both the mean and covar… | V-A，Fig.3 后的混合算法与跨设置适用性段，p.9；Algorithms 1/2，pp.8/10 | C | 当前融合联合矩耦合解释、按设备共享网络、跨 K/Q 复用和具体初始化。Cai 讨论混合结构、跨活动/导频/SNR 设置及可选活动先验 EM，没有当前这一整段初始化与迭代说明。 |
| [5-07](D:/afdm-gfra/paper/C-STMP/sections/05_overall_algorithm.tex:125) · Parameter Estimation and Numerical Implementation | The preceding posterior calculations use a fixed observation matrix $\widehat{\mathbf A}$ and physical no… | III–V 无对应的相位及噪声前端估计段 | D | variable projection 相位估计、MDL 秩选择、尾部特征值噪声估计及固定前端输出，是本稿针对观测模型的内容。 |
| [5-08](D:/afdm-gfra/paper/C-STMP/sections/05_overall_algorithm.tex:139) · Parameter Estimation and Numerical Implementation | The input variance $v$ in the local model [公式/引用] describes the uncertainty after linear estimation. Its … | 对照 V-A 提及活动先验 EM，p.9；无当前输入方差推导 | D | 当前固定近似后验，最小化期望 Gaussian 负对数似然以更新局部输入方差；Cai 在该处提到的是活动先验失配的 EM。被估计参数及推导不同。 |
| [5-09](D:/afdm-gfra/paper/C-STMP/sections/05_overall_algorithm.tex:155) · Parameter Estimation and Numerical Implementation | The residual measures the error of the posterior mean, while $\overline t_X$ accounts for the remaining c… | III–V 无当前 v_tar 与 κ 更新段 | D | 残差加后验方差的解释、缩放系数 κ 及其更新是本文方案；不能因存在阻尼权重就归为 Cai 的消息阻尼段。 |
| [5-10](D:/afdm-gfra/paper/C-STMP/sections/05_overall_algorithm.tex:166) · Parameter Estimation and Numerical Implementation | The current $v^{(i)}$ is used for both joint denoising and the extrinsic update; the updated scale enters… | III–V 无当前 κ 的跨迭代时序说明 | D | 当前 v 用于本轮、更新尺度用于下一轮，是本文新增方差校正的时序定义。 |
| [5-11](D:/afdm-gfra/paper/C-STMP/sections/05_overall_algorithm.tex:169) · Parameter Estimation and Numerical Implementation | The channel prior and online observations use the same fixed normalization. If $s$ is the root mean squar… | V-B1，式(57)–(58)，pp.9–10；V-B2，式(59)–(65)，p.10 | C | 阻尼关系与原文相近，但归一化不同：当前采用训练集统一 RMS，Cai 对各训练样本归一化并在推断时估计输入尺度。当前把两部分合成一段，绝非仅改符号。 |
| [5-12](D:/afdm-gfra/paper/C-STMP/sections/05_overall_algorithm.tex:184) · Parameter Estimation and Numerical Implementation | For numerical evaluation of [公式/引用], we replace $b=\overline t_X/v$ by $b=\clip(\overline t_X/v,\varepsil… | V-B1，式(57)–(58)，p.10 | C | 末尾反馈阻尼与原文对应；前面 b 的裁剪和用 bv 代替后验方差是当前数值处理，整段为新增内容与共有关系的组合。 |
| [5-13](D:/afdm-gfra/paper/C-STMP/sections/05_overall_algorithm.tex:200) · Parameter Estimation and Numerical Implementation | The first input and feedback messages are used without damping. Outside the training variance range, the … | 对照 Algorithm 2 的停止条件，p.10；无当前回退规则 | D | 首轮不阻尼、越出训练范围时保留 site 并回退到解析活动证据、已接受 site 的停止检查均是本文具体实现；不能把通用停止语句当成整段出处。 |
| [5-14](D:/afdm-gfra/paper/C-STMP/sections/05_overall_algorithm.tex:211) · Computational Complexity Analysis | The observation matrix is fixed within a transmission block, so its thin singular value decomposition (SV… | 对照 V-C，式(66)后的快速计算说明，p.11 | D | Cai 基于部分正交 DFT 导频使用 FFT/IFFT；当前固定一般观测矩阵并复用薄 SVD。计算方法和表达均为本文适配。 |
| [5-15](D:/afdm-gfra/paper/C-STMP/sections/05_overall_algorithm.tex:224) · Computational Complexity Analysis | with $\mathbf R_{\rm L}=\mathbf X^{\rm pri} +(\mathbf X_{\rm L}-\mathbf X^{\rm pri})/f_{\rm L}$. For $Q\l… | V-C，复杂度段，p.11 | C | 都统计矩阵运算与网络前向代价；当前新增前端、SVD、空间协方差、2L_z 次导数评估及分类器代价，公式不能从蔡文 FFT 复杂度只换维度得到。 |
| [5-16](D:/afdm-gfra/paper/C-STMP/sections/05_overall_algorithm.tex:244) · Computational Complexity Analysis | For $I$ iterations, the total online complexity is bounded by | 对照 V-C 末尾每轮复杂度，p.11 | D | 当前把一次性前端代价与 I 轮迭代相加给总复杂度；Cai 对应段只给其每轮复杂度。通用引导句不构成可确认的原文段落来源。 |
| [5-17](D:/afdm-gfra/paper/C-STMP/sections/05_overall_algorithm.tex:250) · Computational Complexity Analysis | where $C_{\rm phase}=0$ for supplied phases. The derivative-based variance estimate contributes the $2L_z… | 对照 V-C，p.11；无当前存储复杂度段 | D | 当前解释相位已知时的代价、导数额外调用以及消息和协方差存储规模；Cai 对应段没有这些项目。 |

## 框图、标题和算法框的补充核对

第三章标题与 Cai 的第三章标题相同，线性估计、信道估计和活动检测也是共有术语。这些一致不能证明正文段落为最小替换。当前 Fig.1 是两部分外信息交换框图；Cai Fig.2（p.5）是含变量节点、因子节点及向量/矩阵重排的因子图。当前图形及图注均为重新制作。

当前 Algorithm 1 参照了蔡文的迭代结构，但其输入、网络计算、更新规则和输出对应本文方案。逐步核对如下：

| 当前算法内容 | Cai 对应位置 | 核对结果 |
|---|---|---|
| 输入、输出及标题 | Algorithm 1（p.8）、Algorithm 2（p.10） | 当前输入另含导频张量、可用相位、活动先验及训练网络，输出还包含概率；算法名称也不同。 |
| 步骤 1：前端、初始化、SVD、随机探针 | Algorithm 2 的输入与迭代前部分 | Cai 没有当前相位/噪声前端、SVD 和块固定随机探针步骤。 |
| 步骤 2：有限次数 for 循环 | Algorithm 2 的 repeat/until | 共享迭代控制功能，写法与停止组织已改。 |
| 步骤 3：MFLE、阻尼及 κ 缩放 | Algorithm 2，第 4–7 行 | 线性外信息与阻尼有对应；当前 SVD、首轮分支和 κ 缩放是额外内容。 |
| 步骤 4：GPJD、导数迹、分类器、site 接受 | Algorithm 2，第 8–14 行 | 当前替换了二阶 score 网络与解析活动检测，并加入方差下限和接受条件。 |
| 步骤 5：越出训练范围的回退 | 无对应步骤 | 当前新增。 |
| 步骤 6：条件矩、联合估计、空间协方差 | Algorithm 2，第 15 行；III-B3 式(33)–(38) | 共同的联合矩关系仍在，但当前空间协方差和条件量的取得方式不同。 |
| 步骤 7：κ 更新、裁剪及反馈阻尼 | Algorithm 2，第 16–17 行 | 外信息及阻尼有对应；κ 更新与裁剪为当前实现增加。 |
| 步骤 8：停止检查及 break | Algorithm 2，第 18 行 | 只有通用停止功能相同，当前还检查估计与已接受 site 的稳定。 |
| 步骤 9：恢复尺度、概率和阈值判决 | Algorithm 2，第 19 行；V-B2 式(64)–(65) | 共享输出判决与尺度恢复目的；当前统一 RMS 尺度、输出内容和阈值约定不同。 |

## 最需要区分的两类情况

**可以对应共同推导、但文字已经重写的部分**：III 的开篇、Gaussian 消息相乘与相除、消息传递及迭代闭合；IV-A 对 Tweedie 均值的解释；V 的 Gaussian 合并和阻尼。这些段落不能因为公式相似或引用了 Cai，就报告为逐句最小替换。

**由于技术方案不同，需要另写或明确替换的部分**：IV 的协方差条件训练、均值导数方差、分类密度比；V 的相位/噪声前端、site 接受与回退、κ 更新及 SVD 复杂度。这些内容应当明确标出实际来源和与蔡文的差别。

例如，Cai V-B2 使用逐样本功率归一化和推断时的尺度估计；当前使用训练集统一 RMS。两者不能仅因小节都涉及 normalization，就认定是原文变量替换。

若继续以逐段对应为写作要求，应先对每一段固定“对应原段—共享技术关系—必要技术变化”，把 B 类中的重组与 C/D 类的方案差异分开处理；当前这份稿不能标为已经完成该要求。

本轮只核对并保存报告，正文及 PDF 均未修改。
