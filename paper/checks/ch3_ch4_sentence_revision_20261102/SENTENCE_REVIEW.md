# 第三、四章逐句对照

当前正文共核对 43 个文字单元、119 个句子单元；调整 67 个，保留 52 个。每项都与本轮正式源码核对。公式引出语按句子单元记录，公式本身不在文字替换范围。

下列记录分别标明语言表达、技术依据和本文适配。术语或短搭配的出处不等于整句来自该论文。保留的句子也列出核对结果。

## ch3-P01

段落任务：从第二章后验引出线性估计与联合去噪的迭代分工。
衔接：承接观测似然与两类先验；引出两部分之间的信息交换，下一节具体推导线性后验。

### ch3-P01-S01 · 保留

当前句：
> The posterior in \eqref{eq:working-posterior} combines the observation likelihood with the channel and activity priors.

斟酌：保留。准确承接第二章后验分解，没有多余技术承诺。

- 依据：Current manuscript; existing equations and definitions；Current Chapter III and referenced Chapter II definitions。
  支持层次：本文既有定义、假设或直接公式解释；不登记为外文原句，也不据此宣称原创性。；只检查本句与当前公式相符；不借来源文献补入本文未采用的模型条件。

### ch3-P01-S02 · 修改

原句：
> Following the turbo message-passing framework in \cite{cai2026}, we separate their contributions into linear estimation and joint denoising, as shown in Fig.~\ref{fig:receiver-structure}.

改后：
> Following the turbo message-passing framework in \cite{cai2026}, we formulate the inference as iterations between linear estimation and joint denoising, as shown in Fig.~\ref{fig:receiver-structure}.

斟酌：把笼统的 separate their contributions 改为迭代推断关系，使本段先提出论证对象；保留 Cai 框架归属。

- 依据：Cai et al., arXiv:2506.00581v2；PDF p.5, Section III opening and III-A。
  支持层次：保留原有论证结构与归属；文字结合 Shen 的信息交换句式作必要重述。；本文图为框架图，未照搬 Cai 因子图的节点命名；第三章不引入具体网络模块名称。
  已读摘录／定位：`TMP interprets the message updates on the factor graph in Fig. 2 as iterations between two modules`
- 依据：Shen et al., LEO Satellite-Enabled Random Access with Large Differential Delay and Doppler Shift；PDF p.5, Section III opening; PDF p.6, III-A, paragraph after (20)。
  支持层次：采用信息在估计部分之间迭代交换的句式与段落任务；并非整句最小替换。；本文仍只有线性估计与联合去噪；不引入 Shen 的三模块、GAMP、EM、数据检测或逐元素 BGM/MRF 先验。
  已读摘录／定位：`the soft information is exchanged iteratively among them by careful scheduling`

### ch3-P01-S03 · 保留

当前句：
> Linear estimation combines the received pilots with a Gaussian input message to estimate $\mathbf X$.

斟酌：保留。输入、目标与线性估计的任务已清楚，无需为换词改写。

- 依据：Cai et al., arXiv:2506.00581v2；PDF p.5, Section III opening and III-A。
  支持层次：保留原有论证结构与归属；文字结合 Shen 的信息交换句式作必要重述。；本文图为框架图，未照搬 Cai 因子图的节点命名；第三章不引入具体网络模块名称。
  已读摘录／定位：`TMP interprets the message updates on the factor graph in Fig. 2 as iterations between two modules`
- 依据：Wei et al.；PDF p.2, III-B, (5)-(8)。
  支持层次：仅核对线性后验估计的术语与公式引出关系，具体全矩阵表达为本文既有公式。；Wei 式(6)-(7)要求行正交；不能据此给本文相位旋转后的矩阵套用行正交简式。
  已读摘录／定位：`the linear MMSE estimate`

### ch3-P01-S04 · 保留

当前句：
> Joint denoising uses the channel prior $q_{\rm tr}$ and activity prior $\rho$ to estimate each $X_k=\alpha_kH_k$.

斟酌：保留。两类先验与设备联合信道的关系准确，不能改成 Shen 的逐元素稀疏先验。

- 依据：Cai et al., arXiv:2506.00581v2；PDF p.5, Section III opening and III-A。
  支持层次：保留原有论证结构与归属；文字结合 Shen 的信息交换句式作必要重述。；本文图为框架图，未照搬 Cai 因子图的节点命名；第三章不引入具体网络模块名称。
  已读摘录／定位：`TMP interprets the message updates on the factor graph in Fig. 2 as iterations between two modules`

### ch3-P01-S05 · 修改

原句：
> The two estimates are exchanged through Gaussian extrinsic messages obtained by expectation propagation \cite{minka2001}.

改后：
> Information is exchanged between the two estimators through Gaussian extrinsic messages based on expectation propagation \cite{minka2001}.

斟酌：把“交换两个估计”改为“交换外信息”，采用 Shen/Wei 对信息流的常用表达；EP 归属仍保留。

- 依据：Shen et al., LEO Satellite-Enabled Random Access with Large Differential Delay and Doppler Shift；PDF p.5, Section III opening; PDF p.6, III-A, paragraph after (20)。
  支持层次：采用信息在估计部分之间迭代交换的句式与段落任务；并非整句最小替换。；本文仍只有线性估计与联合去噪；不引入 Shen 的三模块、GAMP、EM、数据检测或逐元素 BGM/MRF 先验。
  已读摘录／定位：`the soft information is exchanged iteratively among them by careful scheduling`
- 依据：Wei et al., Learned Score-Based Turbo Message Passing for Channel Recovery From Spatially Compressed Measurements；PDF p.2, III-B, before (9)-(10); PDF p.3, III-C, after (12)。
  支持层次：采用移除输入信息、把外信息传给另一估计部分的完整搭配与衔接关系。；Wei 的可训练展开参数、残差方差和右旋转不变条件均不移植；本文公式仍是现有 EP Gaussian quotient。
  已读摘录／定位：`removes the incoming prior information and generates the prior of Module B`

## ch3-P02

段落任务：把 Gaussian 输入消息与观测似然相乘，给出线性后验矩。
衔接：落实开篇的线性估计任务；紧接式后解释共享方差及全矩阵适用条件。

### ch3-P02-S01 · 修改

原句：
> The input to linear estimation is a Gaussian message from joint denoising.

改后：
> The linear estimator receives a Gaussian message from joint denoising.

斟酌：以 linear estimator 为主语，直接承接框架图中的估计部分。

- 依据：Wei et al., Learned Score-Based Turbo Message Passing for Channel Recovery From Spatially Compressed Measurements；PDF p.2, III-B, before (9)-(10); PDF p.3, III-C, after (12)。
  支持层次：采用移除输入信息、把外信息传给另一估计部分的完整搭配与衔接关系。；Wei 的可训练展开参数、残差方差和右旋转不变条件均不移植；本文公式仍是现有 EP Gaussian quotient。
  已读摘录／定位：`removes the incoming prior information and generates the prior of Module B`

### ch3-P02-S02 · 修改

原句：
> Its mean matrix is denoted by $\mathbf X^{\rm pri}\in\mathbb C^{KN\times MN}$ and the covariance of each column by $\gamma\I_{KN}$, with $\gamma>0$.

改后：
> This message has mean matrix $\mathbf X^{\rm pri}\in\mathbb C^{KN\times MN}$ and per-column covariance $\gamma\I_{KN}$, with $\gamma>0$.

斟酌：将分散的 mean matrix is denoted by 改为一处完整消息参数说明；维数、公共方差和正性条件全部不变。

- 依据：Current manuscript; existing equations and definitions；Current Chapter III and referenced Chapter II definitions。
  支持层次：本文既有定义、假设或直接公式解释；不登记为外文原句，也不据此宣称原创性。；只检查本句与当前公式相符；不借来源文献补入本文未采用的模型条件。
- 依据：Cai et al., arXiv:2506.00581v2；PDF p.5, III-A, (6)-(9); PDF p.6, (10)-(11)。
  支持层次：相同的 Gaussian likelihood/message 乘积及外信息商关系；维数、矩阵和均值符号按本文既有定义。；Cai 的简化线性均值/方差并不直接等于本文全矩阵公式；仅沿用 Gaussian 更新与共享标量方差的理论关系。
  已读摘录／定位：`the product of two Gaussian pdfs, which is also a Gaussian pdf`

### ch3-P02-S03 · 修改

原句：
> For each column, multiplying this message by the likelihood in \eqref{eq:working-posterior} gives a Gaussian posterior.

改后：
> For each column, the product of this message and the likelihood in \eqref{eq:working-posterior} gives a Gaussian posterior.

斟酌：突出 Gaussian 消息与似然的乘积这一推导依据，保持每列计算条件。

- 依据：Cai et al., arXiv:2506.00581v2；PDF p.5, III-A, (6)-(9); PDF p.6, (10)-(11)。
  支持层次：相同的 Gaussian likelihood/message 乘积及外信息商关系；维数、矩阵和均值符号按本文既有定义。；Cai 的简化线性均值/方差并不直接等于本文全矩阵公式；仅沿用 Gaussian 更新与共享标量方差的理论关系。
  已读摘录／定位：`the product of two Gaussian pdfs, which is also a Gaussian pdf`

### ch3-P02-S04 · 修改

原句：
> The corresponding mean matrix and per-column covariance are \cite[Sec.~III-A]{cai2026}:

改后：
> The posterior mean matrix and per-column covariance are given by \cite[Sec.~III-A]{cai2026}:

斟酌：补出 posterior 并用 given by 自然引出公式，避免 corresponding 的泛指。

- 依据：Wei et al.；PDF p.2, III-B, (5)-(8)。
  支持层次：仅核对线性后验估计的术语与公式引出关系，具体全矩阵表达为本文既有公式。；Wei 式(6)-(7)要求行正交；不能据此给本文相位旋转后的矩阵套用行正交简式。
  已读摘录／定位：`the linear MMSE estimate`
- 依据：Cai et al., arXiv:2506.00581v2；PDF p.5, III-A, (6)-(9); PDF p.6, (10)-(11)。
  支持层次：相同的 Gaussian likelihood/message 乘积及外信息商关系；维数、矩阵和均值符号按本文既有定义。；Cai 的简化线性均值/方差并不直接等于本文全矩阵公式；仅沿用 Gaussian 更新与共享标量方差的理论关系。
  已读摘录／定位：`the product of two Gaussian pdfs, which is also a Gaussian pdf`

## ch3-P03

段落任务：解释平均后验方差及保留全矩阵公式的模型原因。
衔接：承接线性后验式；为下段用平均方差构造 Gaussian 外信息作准备。

### ch3-P03-S01 · 修改

原句：
> The scalar $t_{\rm L}$ averages the posterior variance over the $KN$ coefficients in a column.

改后：
> Here, $t_{\rm L}$ is the average posterior variance of the $KN$ coefficients in each column.

斟酌：让 t_L 的定义直接落在平均后验方差，而不是用标量作 averages 的施事。

- 依据：Cai et al., arXiv:2506.00581v2；PDF p.5, III-A, paragraph before (7); PDF p.7, III-B3, (37)-(38)。
  支持层次：已有完整术语与由协方差/方差到共享标量的叙述关系。；本文先保留空间协方差，再对设备和天线平均；平均指标和维数不是 Cai 原式的逐项复制。
  已读摘录／定位：`a shared scalar variance`
- 依据：Current manuscript; existing equations and definitions；Current Chapter III and referenced Chapter II definitions。
  支持层次：本文既有定义、假设或直接公式解释；不登记为外文原句，也不据此宣称原创性。；只检查本句与当前公式相符；不借来源文献补入本文未采用的模型条件。

### ch3-P03-S02 · 修改

原句：
> In our model, the phase rotations in $\widehat{\mathbf A}$ can destroy the row orthogonality of the pilots.

改后：
> The phase rotations in $\widehat{\mathbf A}$ need not preserve the row orthogonality of the pilot matrix.

斟酌：以 need not preserve 表达原有“可能破坏”条件，不强化成必然不正交；去除 In our model 的重复引导。

- 依据：Current manuscript; existing equations and definitions；Current Chapter III and referenced Chapter II definitions。
  支持层次：本文既有定义、假设或直接公式解释；不登记为外文原句，也不据此宣称原创性。；只检查本句与当前公式相符；不借来源文献补入本文未采用的模型条件。

### ch3-P03-S03 · 修改

原句：
> We therefore retain the full matrix in these expressions; the partial-orthogonality simplification used in \cite[Sec.~III-A]{cai2026} does not generally apply.

改后：
> We therefore use the full matrix expressions above; the simplified updates in \cite[Sec.~III-A]{cai2026} require partial orthogonality.

斟酌：让保留全矩阵公式的结论与简式所需条件直接相接，减少否定性辩护口吻。

- 依据：Cai et al., arXiv:2506.00581v2；PDF p.5, III-A, (6)-(9); PDF p.6, (10)-(11)。
  支持层次：相同的 Gaussian likelihood/message 乘积及外信息商关系；维数、矩阵和均值符号按本文既有定义。；Cai 的简化线性均值/方差并不直接等于本文全矩阵公式；仅沿用 Gaussian 更新与共享标量方差的理论关系。
  已读摘录／定位：`the product of two Gaussian pdfs, which is also a Gaussian pdf`
- 依据：Wei et al.；PDF p.2, III-B, (5)-(8)。
  支持层次：仅核对线性后验估计的术语与公式引出关系，具体全矩阵表达为本文既有公式。；Wei 式(6)-(7)要求行正交；不能据此给本文相位旋转后的矩阵套用行正交简式。
  已读摘录／定位：`the linear MMSE estimate`

## ch3-P04

段落任务：由 Gaussian 后验近似除去输入信息，得到线性外信息。
衔接：先给协方差近似，再给商关系；随后说明按设备重排后的接收对象。

### ch3-P04-S01 · 保留

当前句：
> For message exchange, the posterior covariance is approximated by $t_{\rm L}\I_{KN}$ \cite{ma2015,cai2026}.

斟酌：保留。明确 scalar covariance approximation 的位置和现有引用。

- 依据：Cai et al., arXiv:2506.00581v2；PDF p.5, III-A, paragraph before (7); PDF p.7, III-B3, (37)-(38)。
  支持层次：已有完整术语与由协方差/方差到共享标量的叙述关系。；本文先保留空间协方差，再对设备和天线平均；平均指标和维数不是 Cai 原式的逐项复制。
  已读摘录／定位：`a shared scalar variance`

### ch3-P04-S02 · 修改

原句：
> Dividing the Gaussian posterior with this covariance by the input message removes the information supplied by joint denoising \cite{minka2001}.

改后：
> Dividing this Gaussian approximation by the incoming message removes the information supplied by joint denoising \cite{minka2001}.

斟酌：明确作商的是 Gaussian 近似，并采用 Wei 的 removing incoming information 任务表达；不是直接相除原始非 Gaussian 后验。

- 依据：Wei et al., Learned Score-Based Turbo Message Passing for Channel Recovery From Spatially Compressed Measurements；PDF p.2, III-B, before (9)-(10); PDF p.3, III-C, after (12)。
  支持层次：采用移除输入信息、把外信息传给另一估计部分的完整搭配与衔接关系。；Wei 的可训练展开参数、残差方差和右旋转不变条件均不移植；本文公式仍是现有 EP Gaussian quotient。
  已读摘录／定位：`removes the incoming prior information and generates the prior of Module B`
- 依据：Cai et al., arXiv:2506.00581v2；PDF p.5, III-A, (6)-(9); PDF p.6, (10)-(11)。
  支持层次：相同的 Gaussian likelihood/message 乘积及外信息商关系；维数、矩阵和均值符号按本文既有定义。；Cai 的简化线性均值/方差并不直接等于本文全矩阵公式；仅沿用 Gaussian 更新与共享标量方差的理论关系。
  已读摘录／定位：`the product of two Gaussian pdfs, which is also a Gaussian pdf`

### ch3-P04-S03 · 保留

当前句：
> The resulting extrinsic variance and mean are

斟酌：保留。简洁引出两个外信息参数。

- 依据：Cai et al., arXiv:2506.00581v2；PDF p.5, III-A, (6)-(9); PDF p.6, (10)-(11)。
  支持层次：相同的 Gaussian likelihood/message 乘积及外信息商关系；维数、矩阵和均值符号按本文既有定义。；Cai 的简化线性均值/方差并不直接等于本文全矩阵公式；仅沿用 Gaussian 更新与共享标量方差的理论关系。
  已读摘录／定位：`the product of two Gaussian pdfs, which is also a Gaussian pdf`

## ch3-P05

段落任务：连接线性外信息矩阵与按设备处理的联合去噪输入。
衔接：将前式的均值和公共方差传至下一节，不加入新算法或网络名称。

### ch3-P05-S01 · 保留

当前句：
> Reorganizing $\mathbf R_{\rm L}$ by device gives the tensor inputs to joint denoising, with common variance $v_{\rm L}$.

斟酌：保留。按设备重排是本文维数关系，已有一句足够说明上下节连接。

- 依据：Current manuscript; existing equations and definitions；Current Chapter III and referenced Chapter II definitions。
  支持层次：本文既有定义、假设或直接公式解释；不登记为外文原句，也不据此宣称原创性。；只检查本句与当前公式相符；不借来源文献补入本文未采用的模型条件。
- 依据：Cai et al., arXiv:2506.00581v2；PDF pp.6-7, III-B1, (16)-(23)。
  支持层次：相同的活动条件下信道后验、条件矩与 AWGN 去噪任务；不将本文公式冒充 Cai 原式。；本文以完整 q_tr 表示信道分布，局部 Gaussian 模型为消息近似；不声称实际有限维误差已被证明独立同分布。
  已读摘录／定位：`conditioning on the active case`

## ch3-P06

段落任务：说明 X=αH 的联合后验为何按信道条件矩与活动概率展开。
衔接：承接 Gaussian 外信息，明确局部观察模型；顺次进入信道、活动和联合估计三个小节。

### ch3-P06-S01 · 保留

当前句：
> The relation $X_k=\alpha_kH_k$ couples the channel and device activity.

斟酌：保留。此等式是分开推导信道与活动后验的直接动机。

- 依据：Current manuscript; existing equations and definitions；Current Chapter III and referenced Chapter II definitions。
  支持层次：本文既有定义、假设或直接公式解释；不登记为外文原句，也不据此宣称原创性。；只检查本句与当前公式相符；不借来源文献补入本文未采用的模型条件。
- 依据：Cai et al., arXiv:2506.00581v2；PDF p.6, III-B opening; PDF p.7, III-B2-3, (28)-(38)。
  支持层次：保留条件信道估计和活动概率分别推导、随后合成联合估计的原有论证基础。；本文活动后验用完整信道先验的边缘似然；不复用 Cai 的 Gaussian 外信息活动近似公式。
  已读摘录／定位：`The outputs from these two sub-modules are then combined`

### ch3-P06-S02 · 修改

原句：
> Following \cite[Sec.~III-B]{cai2026}, we calculate the channel estimate conditioned on activity and the activity probability separately, then combine them to estimate $X_k$.

改后：
> Following \cite[Sec.~III-B]{cai2026}, we first derive the channel estimate under the active hypothesis and the posterior activity probability, and then combine them to estimate $X_k$.

斟酌：将 conditioned on activity 明确为 active hypothesis，并明确 activity probability 是 posterior；次序和 Cai 引用不变。

- 依据：Cai et al., arXiv:2506.00581v2；PDF p.6, III-B opening; PDF p.7, III-B2-3, (28)-(38)。
  支持层次：保留条件信道估计和活动概率分别推导、随后合成联合估计的原有论证基础。；本文活动后验用完整信道先验的边缘似然；不复用 Cai 的 Gaussian 外信息活动近似公式。
  已读摘录／定位：`The outputs from these two sub-modules are then combined`

### ch3-P06-S03 · 保留

当前句：
> Let $R_k$ and $v$ denote the input mean and variance.

斟酌：保留。输入记号在首次使用处就地定义。

- 依据：Current manuscript; existing equations and definitions；Current Chapter III and referenced Chapter II definitions。
  支持层次：本文既有定义、假设或直接公式解释；不登记为外文原句，也不据此宣称原创性。；只检查本句与当前公式相符；不借来源文献补入本文未采用的模型条件。

### ch3-P06-S04 · 修改

原句：
> The Gaussian input message defines the local observation model

改后：
> This Gaussian input message corresponds to the local observation model

斟酌：用 corresponds to 说明 Gaussian 消息的局部观察解释，避免把有限维真实误差的精确 AWGN 性质作为新结论。

- 依据：Cai et al., arXiv:2506.00581v2；PDF pp.6-7, III-B1, (16)-(23)。
  支持层次：相同的活动条件下信道后验、条件矩与 AWGN 去噪任务；不将本文公式冒充 Cai 原式。；本文以完整 q_tr 表示信道分布，局部 Gaussian 模型为消息近似；不声称实际有限维误差已被证明独立同分布。
  已读摘录／定位：`conditioning on the active case`

## ch3-P07

段落任务：在活动条件下由 likelihood 与完整信道 prior 构造后验。
衔接：从局部模型限定 α=1；随后对该正规化后验积分得到条件矩。

### ch3-P07-S01 · 修改

原句：
> Conditioned on $\alpha_k=1$, \eqref{eq:pseudo-awgn} describes the channel observed in AWGN.

改后：
> Under the active hypothesis $\alpha_k=1$, \eqref{eq:pseudo-awgn} is an AWGN observation of the channel.

斟酌：将较拗口的 describes the channel observed 改为直接的 AWGN observation；活动条件仍在句首。

- 依据：Cai et al., arXiv:2506.00581v2；PDF pp.6-7, III-B1, (16)-(23)。
  支持层次：相同的活动条件下信道后验、条件矩与 AWGN 去噪任务；不将本文公式冒充 Cai 原式。；本文以完整 q_tr 表示信道分布，局部 Gaussian 模型为消息近似；不声称实际有限维误差已被证明独立同分布。
  已读摘录／定位：`conditioning on the active case`

### ch3-P07-S02 · 修改

原句：
> Its likelihood and the prior $q_{\rm tr}$ determine the conditional posterior $\pi_v(dH\mid R)$, normalized to integrate to one:

改后：
> Combining its likelihood with the prior $q_{\rm tr}$ gives the normalized conditional posterior $\pi_v(dH\mid R)$:

斟酌：用 combining likelihood with prior 直接引出后验，以 normalized 保留原句积分为一的定义，减少重复解释；Xu 只支持引出方式。

- 依据：Xu et al., DOI 10.1109/TCOMM.2025.3628748；IV-A, printed p.7, before (53); sources/xu_reading.md XU-2。
  支持层次：采用 Bayes 后验引出句的常规搭配；从后验定义进入矩计算的顺序相近。；仅已读网页索引文字，未核对原页图像；Xu 是已知信道下有限星座检测，不提供本文条件信道后验公式。
  已读摘录／定位：`See XU-2 in sources/xu_reading.md (not repeated).`
- 依据：Cai et al., arXiv:2506.00581v2；PDF pp.6-7, III-B1, (16)-(23)。
  支持层次：相同的活动条件下信道后验、条件矩与 AWGN 去噪任务；不将本文公式冒充 Cai 原式。；本文以完整 q_tr 表示信道分布，局部 Gaussian 模型为消息近似；不声称实际有限维误差已被证明独立同分布。
  已读摘录／定位：`conditioning on the active case`
- 依据：Current manuscript; existing equations and definitions；Current Chapter III and referenced Chapter II definitions。
  支持层次：本文既有定义、假设或直接公式解释；不登记为外文原句，也不据此宣称原创性。；只检查本句与当前公式相符；不借来源文献补入本文未采用的模型条件。

## ch3-P08

段落任务：引出刚定义的后验的均值与协方差积分。
衔接：公式的被积分分布唯一；下一段解释 MMSE 含义和后续近似符号。

### ch3-P08-S01 · 保留

当前句：
> The conditional mean and covariance are

斟酌：保留。均值与协方差是充分且已核对的固定搭配，无需扩写。

- 依据：Xu et al., DOI 10.1109/TCOMM.2025.3628748；IV-B, printed pp.7-8, before (60); sources/xu_reading.md XU-1。
  支持层次：仅采用均值与协方差的完整搭配及 posterior→moments→cavity 的推导次序。；本文矩积分、平均尺度及 Gaussian 消息商由本文公式确定，不引入 Xu 的有限星座或逐符号独立假设。
  已读摘录／定位：`See XU-1 in sources/xu_reading.md (not repeated).`
- 依据：Cai et al., arXiv:2506.00581v2；PDF pp.6-7, III-B1, (16)-(23)。
  支持层次：相同的活动条件下信道后验、条件矩与 AWGN 去噪任务；不将本文公式冒充 Cai 原式。；本文以完整 q_tr 表示信道分布，局部 Gaussian 模型为消息近似；不声称实际有限维误差已被证明独立同分布。
  已读摘录／定位：`conditioning on the active case`

## ch3-P09

段落任务：解释条件矩的估计含义、完整先验依赖性及近似记号。
衔接：承接两项积分，不把完整信道先验改为逐元素因子先验；随后补上尚未确定的活动后验。

### ch3-P09-S01 · 保留

当前句：
> Here $m=m(R,v)$ in the covariance integral.

斟酌：保留。说明积分内 m 的自变量，避免缩写歧义。

- 依据：Current manuscript; existing equations and definitions；Current Chapter III and referenced Chapter II definitions。
  支持层次：本文既有定义、假设或直接公式解释；不登记为外文原句，也不据此宣称原创性。；只检查本句与当前公式相符；不借来源文献补入本文未采用的模型条件。

### ch3-P09-S02 · 修改

原句：
> The conditional mean is the MMSE channel estimate under the active hypothesis; the covariance describes its estimation uncertainty.

改后：
> The conditional mean is the MMSE channel estimate under the active hypothesis, and the covariance describes the corresponding estimation uncertainty.

斟酌：将分号关系连成与同一后验对应的均值和协方差，保留 MMSE 条件和不确定性含义。

- 依据：Shen et al.；PDF p.7, III-A ending before (21)。
  支持层次：采用由后验均值得到 MMSE 估计的技术叙述关系；协方差与本文活动条件仍来自本文公式。；Shen 讨论近似后验下的 H 和 W；本文此处是给定活动状态的完整信道条件后验，不借用其能量检测器。
  已读摘录／定位：`obtained as the means of their respective estimated posterior distributions`
- 依据：Cai et al., arXiv:2506.00581v2；PDF pp.6-7, III-B1, (16)-(23)。
  支持层次：相同的活动条件下信道后验、条件矩与 AWGN 去噪任务；不将本文公式冒充 Cai 原式。；本文以完整 q_tr 表示信道分布，局部 Gaussian 模型为消息近似；不声称实际有限维误差已被证明独立同分布。
  已读摘录／定位：`conditioning on the active case`

### ch3-P09-S03 · 修改

原句：
> Both depend on the full channel prior, so the dependence among the entries of $H_k$ is retained in the posterior calculation.

改后：
> These moments are evaluated under the full channel prior, preserving the dependence among the entries of $H_k$ in the posterior calculation.

斟酌：把 both 的指代明确为 these moments，保持完整先验下的 posterior calculation，不添加元素独立假设。

- 依据：Current manuscript; existing equations and definitions；Current Chapter III and referenced Chapter II definitions。
  支持层次：本文既有定义、假设或直接公式解释；不登记为外文原句，也不据此宣称原创性。；只检查本句与当前公式相符；不借来源文献补入本文未采用的模型条件。
- 依据：Huang et al., Prior-Agnostic AFDM Channel Estimation；PDF p.3, III-A, paragraph after (6)。
  支持层次：仅辅助核对完整 AFDM 有效信道估计这一技术对象，当前后验依赖性结论来自本文 q_tr 定义。；Huang 不提供本文设备活动、协方差或后验因子结构；不能从其完整信道估计措辞推出本文信道元素独立性。
  已读摘录／定位：`without imposing sparsity assumptions`

### ch3-P09-S04 · 保留

当前句：
> We denote the approximations to $m(R_k,v)$ and $\tr\bm\Sigma_H(R_k,v)/D$ by $\mu_k$ and $t_k$, respectively.

斟酌：保留。两个近似符号的定义完整，并且在后文首次使用前给出。

- 依据：Current manuscript; existing equations and definitions；Current Chapter III and referenced Chapter II definitions。
  支持层次：本文既有定义、假设或直接公式解释；不登记为外文原句，也不据此宣称原创性。；只检查本句与当前公式相符；不借来源文献补入本文未采用的模型条件。

## ch3-P10

段落任务：在活动与非活动假设下分别得到观察边缘似然。
衔接：活动情形对信道边缘化、非活动情形只有噪声；给下一段的 Bayes 公式提供两项 likelihood。

### ch3-P10-S01 · 保留

当前句：
> Activity detection compares the hypotheses $R_k=W_k$ and $R_k=H_k+W_k$.

斟酌：保留。两个活动假设明确，与后面两项密度逐一对应。

- 依据：Current manuscript; existing equations and definitions；Current Chapter III and referenced Chapter II definitions。
  支持层次：本文既有定义、假设或直接公式解释；不登记为外文原句，也不据此宣称原创性。；只检查本句与当前公式相符；不借来源文献补入本文未采用的模型条件。
- 依据：Ding et al., DOI 10.1109/TVT.2026.3729877；PDF pp.3-4, III-B, Step 3, (14)-(16)。
  支持层次：相同的两个假设/混合分量的似然证据与后验概率关系；只借鉴叙述任务。；Ding 的非零分量为稀疏系数行；本文为整个设备的活动状态。本文不移植其层次 spike-and-slab 先验、GNN 或后验概率公式。
  已读摘录／定位：`the likelihood ratio between the nonzero and zero components`

### ch3-P10-S02 · 修改

原句：
> Integrating over the channel in the active case gives $q_{1,v}$, while the inactive likelihood $q_{0,v}$ is the Gaussian noise density:

改后：
> Marginalizing the channel under the active hypothesis yields the likelihood $q_{1,v}$, whereas $q_{0,v}$ is the Gaussian noise density under the inactive hypothesis:

斟酌：采用 marginalizing 的标准概率推导表达，使 active/inactive 两项 likelihood 对称呈现；不是移植 Ding 的具体稀疏行模型。

- 依据：Ding et al., DOI 10.1109/TVT.2026.3729877；PDF pp.3-4, III-B, Step 3, (14)-(16)。
  支持层次：相同的两个假设/混合分量的似然证据与后验概率关系；只借鉴叙述任务。；Ding 的非零分量为稀疏系数行；本文为整个设备的活动状态。本文不移植其层次 spike-and-slab 先验、GNN 或后验概率公式。
  已读摘录／定位：`the likelihood ratio between the nonzero and zero components`
- 依据：Current manuscript; existing equations and definitions；Current Chapter III and referenced Chapter II definitions。
  支持层次：本文既有定义、假设或直接公式解释；不登记为外文原句，也不据此宣称原创性。；只检查本句与当前公式相符；不借来源文献补入本文未采用的模型条件。

## ch3-P11

段落任务：指出活动 likelihood 的正规化作用并给出活动后验。
衔接：把信道后验的积分与活动检验连接起来；后段解释概率意义和 p_k 近似记号。

### ch3-P11-S01 · 保留

当前句：
> The active likelihood $q_{1,v}$ also normalizes the channel posterior in \eqref{eq:active-channel-posterior}.

斟酌：保留。连接活动边缘 likelihood 与上一节 posterior 正规化，避免两段推导脱节。

- 依据：Current manuscript; existing equations and definitions；Current Chapter III and referenced Chapter II definitions。
  支持层次：本文既有定义、假设或直接公式解释；不登记为外文原句，也不据此宣称原创性。；只检查本句与当前公式相符；不借来源文献补入本文未采用的模型条件。

### ch3-P11-S02 · 保留

当前句：
> With prior activity probability $\rho$, Bayes' rule gives

斟酌：保留。Bayes 公式引出已经自然且准确。

- 依据：Xu et al., DOI 10.1109/TCOMM.2025.3628748；IV-A, printed p.7, before (53); sources/xu_reading.md XU-2。
  支持层次：采用 Bayes 后验引出句的常规搭配；从后验定义进入矩计算的顺序相近。；仅已读网页索引文字，未核对原页图像；Xu 是已知信道下有限星座检测，不提供本文条件信道后验公式。
  已读摘录／定位：`See XU-2 in sources/xu_reading.md (not repeated).`
- 依据：Ding et al., DOI 10.1109/TVT.2026.3729877；PDF pp.3-4, III-B, Step 3, (14)-(16)。
  支持层次：相同的两个假设/混合分量的似然证据与后验概率关系；只借鉴叙述任务。；Ding 的非零分量为稀疏系数行；本文为整个设备的活动状态。本文不移植其层次 spike-and-slab 先验、GNN 或后验概率公式。
  已读摘录／定位：`the likelihood ratio between the nonzero and zero components`
- 依据：Current manuscript; existing equations and definitions；Current Chapter III and referenced Chapter II definitions。
  支持层次：本文既有定义、假设或直接公式解释；不登记为外文原句，也不据此宣称原创性。；只检查本句与当前公式相符；不借来源文献补入本文未采用的模型条件。

## ch3-P12

段落任务：解释活动后验依赖两项 likelihood 与活动 prior，并定义近似。
衔接：避免只说观察解释程度而省略 prior；连接随后联合估计对 p_k 的使用。

### ch3-P12-S01 · 修改

原句：
> Thus, the posterior activity probability depends on how well the observation is explained by each hypothesis.

改后：
> Thus, the posterior activity probability is determined by the two likelihoods and the activity prior.

斟酌：把 how well the observation is explained 改为式中明确存在的 likelihood 和 prior，表达更精确而不加技术内容。

- 依据：Ding et al., DOI 10.1109/TVT.2026.3729877；PDF pp.3-4, III-B, Step 3, (14)-(16)。
  支持层次：相同的两个假设/混合分量的似然证据与后验概率关系；只借鉴叙述任务。；Ding 的非零分量为稀疏系数行；本文为整个设备的活动状态。本文不移植其层次 spike-and-slab 先验、GNN 或后验概率公式。
  已读摘录／定位：`the likelihood ratio between the nonzero and zero components`
- 依据：Current manuscript; existing equations and definitions；Current Chapter III and referenced Chapter II definitions。
  支持层次：本文既有定义、假设或直接公式解释；不登记为外文原句，也不据此宣称原创性。；只检查本句与当前公式相符；不借来源文献补入本文未采用的模型条件。

### ch3-P12-S02 · 保留

当前句：
> Let $p_k$ denote the approximation to $p^\star(R_k,v)$ used in the joint estimate below.

斟酌：保留。给后续联合估计提供近似 p_k，未提前讲密度比实现。

- 依据：Current manuscript; existing equations and definitions；Current Chapter III and referenced Chapter II definitions。
  支持层次：本文既有定义、假设或直接公式解释；不登记为外文原句，也不据此宣称原创性。；只检查本句与当前公式相符；不借来源文献补入本文未采用的模型条件。

## ch3-P13

段落任务：对活动状态平均条件矩，得到一般联合均值与协方差。
衔接：合并前两节结果，先给一般恒等式；后段再解释两项协方差并作 Gaussian 近似。

### ch3-P13-S01 · 保留

当前句：
> Under the two activity hypotheses, $X_k$ is either zero or equal to $H_k$.

斟酌：保留。先交代活动条件下的 X_k，再求联合矩，顺序正确。

- 依据：Current manuscript; existing equations and definitions；Current Chapter III and referenced Chapter II definitions。
  支持层次：本文既有定义、假设或直接公式解释；不登记为外文原句，也不据此宣称原创性。；只检查本句与当前公式相符；不借来源文献补入本文未采用的模型条件。

### ch3-P13-S02 · 修改

原句：
> Averaging the conditional channel moments over these hypotheses gives

改后：
> The posterior mean and covariance follow by averaging the conditional channel moments over these hypotheses:

斟酌：明确下式给出 posterior mean/covariance，使本节从活动概率自然进入联合矩；conditional moments 包括计算协方差所需的二阶矩。

- 依据：Ding et al., DOI 10.1109/TVT.2026.3729877；PDF p.4, III-B, Step 4, (18a)-(18b)。
  支持层次：采用从混合后验到均值/方差的段落任务关系；不整句移植其算法步骤格式。；Ding 式(18a)带阻尼且先验为 Gaussian 分量；本文一般条件矩及空间协方差仍是本文既有推导，不引入其逐元素先验。
  已读摘录／定位：`Based on the approximate posterior distribution in (14), an MMSE estimator is employed`
- 依据：Xu et al., DOI 10.1109/TCOMM.2025.3628748；IV-B, printed pp.7-8, before (60); sources/xu_reading.md XU-1。
  支持层次：仅采用均值与协方差的完整搭配及 posterior→moments→cavity 的推导次序。；本文矩积分、平均尺度及 Gaussian 消息商由本文公式确定，不引入 Xu 的有限星座或逐符号独立假设。
  已读摘录／定位：`See XU-1 in sources/xu_reading.md (not repeated).`
- 依据：Current manuscript; existing equations and definitions；Current Chapter III and referenced Chapter II definitions。
  支持层次：本文既有定义、假设或直接公式解释；不登记为外文原句，也不据此宣称原创性。；只检查本句与当前公式相符；不借来源文献补入本文未采用的模型条件。

## ch3-P14

段落任务：解释信道与活动两类不确定性，并引入联合混合后验近似。
衔接：不把一般条件矩恒等式等同于 Gaussian 信道假设；为矩阵化空间协方差提供近似矩。

### ch3-P14-S01 · 保留

当前句：
> The first covariance term represents channel uncertainty under the active hypothesis.

斟酌：保留。直观解释一般条件协方差的第一项，不依赖 Gaussian 先验。

- 依据：Current manuscript; existing equations and definitions；Current Chapter III and referenced Chapter II definitions。
  支持层次：本文既有定义、假设或直接公式解释；不登记为外文原句，也不据此宣称原创性。；只检查本句与当前公式相符；不借来源文献补入本文未采用的模型条件。
- 依据：Ding et al., DOI 10.1109/TVT.2026.3729877；PDF p.4, III-B, Step 4, (18a)-(18b)。
  支持层次：采用从混合后验到均值/方差的段落任务关系；不整句移植其算法步骤格式。；Ding 式(18a)带阻尼且先验为 Gaussian 分量；本文一般条件矩及空间协方差仍是本文既有推导，不引入其逐元素先验。
  已读摘录／定位：`Based on the approximate posterior distribution in (14), an MMSE estimator is employed`

### ch3-P14-S02 · 保留

当前句：
> The second accounts for uncertainty in whether the device is active \cite[Secs.~III-C--III-D]{liu2018}, \cite[Sec.~III-B]{cai2026}.

斟酌：保留。解释第二项活动不确定性，原有技术引用不因借鉴表达而更换。

- 依据：Current manuscript; existing equations and definitions；Current Chapter III and referenced Chapter II definitions。
  支持层次：本文既有定义、假设或直接公式解释；不登记为外文原句，也不据此宣称原创性。；只检查本句与当前公式相符；不借来源文献补入本文未采用的模型条件。
- 依据：Cai et al., arXiv:2506.00581v2；PDF p.7, III-B3, (32)-(38)。
  支持层次：Bernoulli-Gaussian 后验近似的术语与从后验计算均值/方差的关系。；本文先写一般条件矩的恒等式，再作 Gaussian 近似；不把一般恒等式说成以 Gaussian 信道先验为必要条件。
  已读摘录／定位：`the expression inside the Gaussian projection operator is a Bernoulli-Gaussian pdf`

### ch3-P14-S03 · 保留

当前句：
> Approximating the active-channel posterior by a Gaussian with mean $\mu_k$ and covariance $t_k\I_D$ gives the Bernoulli--Gaussian approximation

斟酌：保留。先说明活动条件分量的 Gaussian 近似，再明确联合分布为 Bernoulli--Gaussian；两个层次必要，无需仅为换词改写。

- 依据：Cai et al., arXiv:2506.00581v2；PDF p.7, III-B3, (32)-(38)。
  支持层次：Bernoulli-Gaussian 后验近似的术语与从后验计算均值/方差的关系。；本文先写一般条件矩的恒等式，再作 Gaussian 近似；不把一般恒等式说成以 Gaussian 信道先验为必要条件。
  已读摘录／定位：`the expression inside the Gaussian projection operator is a Bernoulli-Gaussian pdf`
- 依据：Ding et al., DOI 10.1109/TVT.2026.3729877；PDF p.4, III-B, Step 4, (18a)-(18b)。
  支持层次：采用从混合后验到均值/方差的段落任务关系；不整句移植其算法步骤格式。；Ding 式(18a)带阻尼且先验为 Gaussian 分量；本文一般条件矩及空间协方差仍是本文既有推导，不引入其逐元素先验。
  已读摘录／定位：`Based on the approximate posterior distribution in (14), an MMSE estimator is employed`

## ch3-P15

段落任务：将按设备的联合协方差表示为空间协方差矩阵。
衔接：先说明 U_k 的重排意义，再对信道位置平均；下一段进一步得到消息传递用的标量。

### ch3-P15-S01 · 修改

原句：
> For the spatial covariance, write the entries of $\mu_k$ as $\mathbf U_k\in\mathbb C^{M\times N^2}$, with one row for each antenna.

改后：
> To obtain the spatial covariance, we rearrange $\mu_k$ into $\mathbf U_k\in\mathbb C^{M\times N^2}$, with one row for each antenna.

斟酌：用 rearrange 表明 U_k 是 μ_k 的重排而非新物理量，保持每个天线一行的定义。

- 依据：Current manuscript; existing equations and definitions；Current Chapter III and referenced Chapter II definitions。
  支持层次：本文既有定义、假设或直接公式解释；不登记为外文原句，也不据此宣称原创性。；只检查本句与当前公式相符；不借来源文献补入本文未采用的模型条件。

### ch3-P15-S02 · 修改

原句：
> Averaging the covariance over the $N^2$ channel positions gives

改后：
> Averaging the resulting covariance over the $N^2$ channel positions gives

斟酌：补出 resulting，明确此处平均上一段联合后验的协方差而非仅活动条件协方差。

- 依据：Current manuscript; existing equations and definitions；Current Chapter III and referenced Chapter II definitions。
  支持层次：本文既有定义、假设或直接公式解释；不登记为外文原句，也不据此宣称原创性。；只检查本句与当前公式相符；不借来源文献补入本文未采用的模型条件。

## ch3-P16

段落任务：由空间协方差的 trace 平均得到共享后验方差。
衔接：承接 C_X,k，保留设备及天线两级平均；为外信息商提供公共方差。

### ch3-P16-S01 · 修改

原句：
> Averaging its trace over devices and antennas gives the scalar posterior variance

改后：
> The scalar posterior variance is then obtained by averaging its trace over devices and antennas:

斟酌：以 scalar posterior variance 为主语，并用 then 承接空间协方差；平均范围完全保留。

- 依据：Current manuscript; existing equations and definitions；Current Chapter III and referenced Chapter II definitions。
  支持层次：本文既有定义、假设或直接公式解释；不登记为外文原句，也不据此宣称原创性。；只检查本句与当前公式相符；不借来源文献补入本文未采用的模型条件。
- 依据：Cai et al., arXiv:2506.00581v2；PDF p.5, III-A, paragraph before (7); PDF p.7, III-B3, (37)-(38)。
  支持层次：已有完整术语与由协方差/方差到共享标量的叙述关系。；本文先保留空间协方差，再对设备和天线平均；平均指标和维数不是 Cai 原式的逐项复制。
  已读摘录／定位：`a shared scalar variance`

## ch3-P17

段落任务：以联合均值和公共方差形成 Gaussian 近似并计算外信息。
衔接：与线性部分外信息商呼应；使用 b 简写已有方差比，下一段说明回传。

### ch3-P17-S01 · 修改

原句：
> The feedback uses a Gaussian approximation with mean $\widehat X_k$ and common variance $\overline t_X$.

改后：
> To form the extrinsic message, we use a Gaussian approximation with mean $\widehat X_k$ and common variance $\overline t_X$.

斟酌：把工程式 feedback 改为理论任务 form the extrinsic message，连接前述后验矩与 Gaussian 商。

- 依据：Cai et al., arXiv:2506.00581v2；PDF p.7, III-B3, (32)-(38)。
  支持层次：Bernoulli-Gaussian 后验近似的术语与从后验计算均值/方差的关系。；本文先写一般条件矩的恒等式，再作 Gaussian 近似；不把一般恒等式说成以 Gaussian 信道先验为必要条件。
  已读摘录／定位：`the expression inside the Gaussian projection operator is a Bernoulli-Gaussian pdf`
- 依据：Wei et al., Learned Score-Based Turbo Message Passing for Channel Recovery From Spatially Compressed Measurements；PDF p.2, III-B, before (9)-(10); PDF p.3, III-C, after (12)。
  支持层次：采用移除输入信息、把外信息传给另一估计部分的完整搭配与衔接关系。；Wei 的可训练展开参数、残差方差和右旋转不变条件均不移植；本文公式仍是现有 EP Gaussian quotient。
  已读摘录／定位：`removes the incoming prior information and generates the prior of Module B`

### ch3-P17-S02 · 保留

当前句：
> Let $b=\overline t_X/v$.

斟酌：保留。b 是外信息公式的局部简写，不引入实现截断。

- 依据：Current manuscript; existing equations and definitions；Current Chapter III and referenced Chapter II definitions。
  支持层次：本文既有定义、假设或直接公式解释；不登记为外文原句，也不据此宣称原创性。；只检查本句与当前公式相符；不借来源文献补入本文未采用的模型条件。

### ch3-P17-S03 · 保留

当前句：
> Dividing this approximation by the incoming Gaussian message, as in \eqref{eq:linear-extrinsic}, gives

斟酌：保留。明确与线性部分同一外信息构造，避免再次重复推导。

- 依据：Wei et al., Learned Score-Based Turbo Message Passing for Channel Recovery From Spatially Compressed Measurements；PDF p.2, III-B, before (9)-(10); PDF p.3, III-C, after (12)。
  支持层次：采用移除输入信息、把外信息传给另一估计部分的完整搭配与衔接关系。；Wei 的可训练展开参数、残差方差和右旋转不变条件均不移植；本文公式仍是现有 EP Gaussian quotient。
  已读摘录／定位：`removes the incoming prior information and generates the prior of Module B`
- 依据：Cai et al., arXiv:2506.00581v2；PDF p.5, III-A, (6)-(9); PDF p.6, (10)-(11)。
  支持层次：相同的 Gaussian likelihood/message 乘积及外信息商关系；维数、矩阵和均值符号按本文既有定义。；Cai 的简化线性均值/方差并不直接等于本文全矩阵公式；仅沿用 Gaussian 更新与共享标量方差的理论关系。
  已读摘录／定位：`the product of two Gaussian pdfs, which is also a Gaussian pdf`

## ch3-P18

段落任务：给出正有限外信息方差条件，并闭合迭代。
衔接：保留 0<b<1 的实际数学条件；把消息重新作为下一轮线性估计输入。

### ch3-P18-S01 · 保留

当前句：
> For $0<b<1$, this message has a finite, positive variance.

斟酌：保留。该条件直接保证下一轮 Gaussian 消息方差有效，不作额外防御扩写。

- 依据：Current manuscript; existing equations and definitions；Current Chapter III and referenced Chapter II definitions。
  支持层次：本文既有定义、假设或直接公式解释；不登记为外文原句，也不据此宣称原创性。；只检查本句与当前公式相符；不借来源文献补入本文未采用的模型条件。

### ch3-P18-S02 · 修改

原句：
> Reorganizing its means into $\mathbf X^{\rm pri}$ and using $\gamma_{\rm out}$ as the input variance closes the iteration.

改后：
> Its means are collected into $\mathbf X^{\rm pri}$, and $\gamma_{\rm out}$ supplies the input variance for the next linear estimation step.

斟酌：采用外信息作为下一轮输入的自然衔接，替换抽象的 closes the iteration；参数意义不变。

- 依据：Wei et al., Learned Score-Based Turbo Message Passing for Channel Recovery From Spatially Compressed Measurements；PDF p.2, III-B, before (9)-(10); PDF p.3, III-C, after (12)。
  支持层次：采用移除输入信息、把外信息传给另一估计部分的完整搭配与衔接关系。；Wei 的可训练展开参数、残差方差和右旋转不变条件均不移植；本文公式仍是现有 EP Gaussian quotient。
  已读摘录／定位：`removes the incoming prior information and generates the prior of Module B`
- 依据：Shen et al., LEO Satellite-Enabled Random Access with Large Differential Delay and Doppler Shift；PDF p.5, Section III opening; PDF p.6, III-A, paragraph after (20)。
  支持层次：采用信息在估计部分之间迭代交换的句式与段落任务；并非整句最小替换。；本文仍只有线性估计与联合去噪；不引入 Shen 的三模块、GAMP、EM、数据检测或逐元素 BGM/MRF 先验。
  已读摘录／定位：`the soft information is exchanged iteratively among them by careful scheduling`

## ch3-P19

段落任务：指出一般先验积分的求解需求并过渡到第四、五章。
衔接：先回顾第三章仍需要计算的量，再指出积分困难；第四章学习这些量、第五章整合接收机。

### ch3-P19-S01 · 修改

原句：
> Evaluating these updates requires the conditional channel moments in \eqref{eq:conditional-channel-integrals} and the activity probability in \eqref{eq:local-activity}.

改后：
> The message updates above require the conditional channel moments in \eqref{eq:conditional-channel-integrals} and the activity probability in \eqref{eq:local-activity}.

斟酌：明确所指是前述 message updates，避免空泛 evaluating these updates；保留两个公式定位。

- 依据：Current manuscript; existing equations and definitions；Current Chapter III and referenced Chapter II definitions。
  支持层次：本文既有定义、假设或直接公式解释；不登记为外文原句，也不据此宣称原创性。；只检查本句与当前公式相符；不借来源文献补入本文未采用的模型条件。
- 依据：Cai et al., arXiv:2506.00581v2；PDF p.7, III-B1, paragraph after (23); PDF p.8, IV opening。
  支持层次：保留一般先验下条件矩积分难计算、转入学习章节的论证关系。；本文在此还需要活动边缘似然；第三章只指出需求，不提前引入密度比学习或具体网络实现。
  已读摘录／定位：`due to the complicated and high-dimensional integrals`

### ch3-P19-S02 · 修改

原句：
> The underlying integrals over the full channel prior generally have no closed-form expressions.

改后：
> With the full channel prior, these integrals generally do not admit closed-form expressions.

斟酌：采用 do not admit closed-form expressions 的数学陈述，保持 generally 的论断强度。

- 依据：Cai et al., arXiv:2506.00581v2；PDF p.7, III-B1, paragraph after (23); PDF p.8, IV opening。
  支持层次：保留一般先验下条件矩积分难计算、转入学习章节的论证关系。；本文在此还需要活动边缘似然；第三章只指出需求，不提前引入密度比学习或具体网络实现。
  已读摘录／定位：`due to the complicated and high-dimensional integrals`

### ch3-P19-S03 · 修改

原句：
> Section~\ref{sec:learning} develops methods for learning these quantities from channel samples, and Section~\ref{sec:overall} incorporates them into the complete receiver algorithm.

改后：
> Section~\ref{sec:learning} develops methods for learning approximations to these quantities from channel samples, and Section~\ref{sec:overall} incorporates them into the complete receiver algorithm.

斟酌：补出 approximations，与 μ_k、t_k、p_k 一致；不把学习估计写成精确恢复一般积分。

- 依据：Current manuscript; existing equations and definitions；Current Chapter III and referenced Chapter II definitions。
  支持层次：本文既有定义、假设或直接公式解释；不登记为外文原句，也不据此宣称原创性。；只检查本句与当前公式相符；不借来源文献补入本文未采用的模型条件。
- 依据：Cai et al., arXiv:2506.00581v2；PDF p.7, III-B1, paragraph after (23); PDF p.8, IV opening。
  支持层次：保留一般先验下条件矩积分难计算、转入学习章节的论证关系。；本文在此还需要活动边缘似然；第三章只指出需求，不提前引入密度比学习或具体网络实现。
  已读摘录／定位：`due to the complicated and high-dimensional integrals`

## ch4_ab-P01

段落任务：承接 III 的后验积分计算需求，预告 score 学习和活动密度比。
衔接：由积分目标进入 IV-A 的观测与后验矩关系。

### ch4_ab-P01-S01 · 修改

原句：
> The conditional channel moments in \eqref{eq:conditional-channel-integrals} involve integrals over the full channel prior.

改后：
> The conditional channel moments in \eqref{eq:conditional-channel-integrals} require integration over the full channel prior.

斟酌：用 require integration 直接指出后验矩的计算需求，保留完整先验。

- 依据：本文既有第三／四／六章；当前输入及交叉引用。
  支持层次：本文定义／推导／衔接；不宣称外部原句；本文特有条件及段落路线由现有公式核对；没有在已读 Shen、Xu、Huang、Ding、Wei 中找到同一技术句时不强行配母本。

### ch4_ab-P01-S02 · 修改

原句：
> Score-based representations of these moments allow them to be obtained from a learned denoising function \cite[Sec.~IV-A]{cai2026}.

改后：
> These moments can be expressed in terms of score functions and estimated by learning a channel denoiser \cite[Sec.~IV-A]{cai2026}.

斟酌：明确 score 函数、后验矩和学习去噪器三者的关系，去掉 them 连续指代。

- 依据：Cai et al., arXiv:2506.00581v2；PDF p.8；IV 开篇。
  支持层次：原段关系／技术陈述；保留由后验积分转向 score 表示的论证任务；本文在一般实协方差下推导，不把此处文字登记为从其他论文逐句最小替换。
  已读摘录／定位：`we introduce score-based representations of (22) and (23) to circumvent the intractable high-dimensional integrals involved in posterior message calculation`

### ch4_ab-P01-S03 · 修改

原句：
> We establish these relations and derive a training objective that includes colored Gaussian perturbations.

改后：
> We first derive these relations and the corresponding training objective under colored Gaussian perturbations.

斟酌：用 first 与后一句 then 标明章节自然次序，colored Gaussian 条件不变。

- 依据：本文既有第三／四／六章；当前输入及交叉引用。
  支持层次：本文定义／推导／衔接；不宣称外部原句；本文特有条件及段落路线由现有公式核对；没有在已读 Shen、Xu、Huang、Ding、Wei 中找到同一技术句时不强行配母本。

### ch4_ab-P01-S04 · 修改

原句：
> The activity probability in \eqref{eq:local-activity} is then obtained by learning the density ratio between the two activity hypotheses.

改后：
> We then learn the density ratio between the two activity hypotheses to obtain the activity probability in \eqref{eq:local-activity}.

斟酌：主动句把方法与尚需求得的活动概率连起来，不引入模块名。

- 依据：本文既有第三／四／六章；当前输入及交叉引用。
  支持层次：本文定义／推导／衔接；不宣称外部原句；本文特有条件及段落路线由现有公式核对；没有在已读 Shen、Xu、Huang、Ding、Wei 中找到同一技术句时不强行配母本。

## ch4_ab-P02

段落任务：给出活跃假设下的一般高斯扰动及实表示。
衔接：先确定观测变量和噪声协方差，下一段才定义边缘密度。

### ch4_ab-P02-S01 · 保留

当前句：
> Consider the channel observation under the active hypothesis in \eqref{eq:pseudo-awgn}.

斟酌：原句直接承接第三章活跃假设，保留。

- 依据：本文既有第三／四／六章；当前输入及交叉引用。
  支持层次：本文定义／推导／衔接；不宣称外部原句；本文特有条件及段落路线由现有公式核对；没有在已读 Shen、Xu、Huang、Ding、Wei 中找到同一技术句时不强行配母本。

### ch4_ab-P02-S02 · 修改

原句：
> To include correlated perturbations, let $\mathbf h_{\mathbb R}\in\mathbb R^{2D}$ concatenate the real and imaginary parts of $\vect(H)$, with $H\sim q_{\rm tr}$.

改后：
> For a complex-valued channel sample $H\sim q_{\rm tr}$, we stack the real and imaginary parts of $\vect(H)$ in $\mathbf h_{\mathbb R}\in\mathbb R^{2D}$.

斟酌：以 complex-valued channel sample 为清楚主语，H 取自 q_tr 的分布关系作为样本条件；采用 Huang 同一实／复训练语境的搭配，未将分布关系当作复数对象。

- 依据：Huang et al., Prior-Agnostic AFDM Channel Estimation；PDF p.3；III-A, (7) 后实／复训练段。
  支持层次：采用同任务完整搭配／必要句式适配；采用 Huang 的 complex-valued 和 real–imaginary representation 技术搭配，以本文样本 H~q_tr 为对象并堆叠为 2D 维实向量；不宣称 Since 原句只作变量替换，不复制 RefineNet、双通道形状、扩散采样或原文复高斯缩放。
  已读摘录／定位：`Since the AFDM effective channel matrix is complex-valued, we adopt a two-channel real–imaginary representation`

### ch4_ab-P02-S03 · 修改

原句：
> For an independent proper complex Gaussian perturbation with covariance $C\succ0$, the real observation is

改后：
> To allow for correlated errors, we consider an independent proper complex Gaussian perturbation with covariance $C\succ0$, giving the real observation

斟酌：把相关误差动机放回一般协方差的引入句，独立、proper complex Gaussian 与正定条件全部保留。

- 依据：本文既有第三／四／六章；当前输入及交叉引用。
  支持层次：本文定义／推导／衔接；不宣称外部原句；本文特有条件及段落路线由现有公式核对；没有在已读 Shen、Xu、Huang、Ding、Wei 中找到同一技术句时不强行配母本。

## ch4_ab-P03

段落任务：用固定 C 的边缘密度给出 Tweedie 条件均值。
衔接：下一段解释 score 修正与 III 的白噪声特例。

### ch4_ab-P03-S01 · 保留

当前句：
> At fixed $C$, let $q_{\bm\Sigma}^{\mathbb R}$ denote the density of $\mathbf u$.

斟酌：密度是在固定 C 下定义，此条件不可省略，保留。

- 依据：本文既有第三／四／六章；当前输入及交叉引用。
  支持层次：本文定义／推导／衔接；不宣称外部原句；本文特有条件及段落路线由现有公式核对；没有在已读 Shen、Xu、Huang、Ding、Wei 中找到同一技术句时不强行配母本。

### ch4_ab-P03-S02 · 修改

原句：
> Tweedie's formula gives \cite{efron2011,dytso2021}

改后：
> The conditional mean is given by Tweedie's formula \cite{efron2011,dytso2021}

斟酌：先点明此式给出 conditional mean，再引用 Tweedie，读者无需由公式自行猜测估计对象。

- 依据：Cai et al., arXiv:2506.00581v2；PDF p.8；IV-A, (43)–(44) 及式后说明。
  支持层次：技术陈述；Cai 此处为复白噪声标量方差；本文一般正定实协方差及因子 1/2 由本文实表示与现有 Dytso 引用承担，未移植 Cai 的复梯度约定。
  已读摘录／定位：`Tweedie’s formula bridges MMSE denoising and the score of the perturbed data distribution through a simple equation`

## ch4_ab-P04

段落任务：解释一阶 score 的含义及均值公式与第三章的对应。
衔接：由一阶矩自然转入相应二阶矩。

### ch4_ab-P04-S01 · 保留

当前句：
> The gradient $\nabla_{\mathbf u}\log q_{\bm\Sigma}^{\mathbb R}$ is the first-order score function.

斟酌：score 的标准定义简洁准确，不为词语变化而改写。

- 依据：Cai et al., arXiv:2506.00581v2；PDF p.8；IV-A, (43)–(44) 及式后说明。
  支持层次：技术陈述；Cai 此处为复白噪声标量方差；本文一般正定实协方差及因子 1/2 由本文实表示与现有 Dytso 引用承担，未移植 Cai 的复梯度约定。
  已读摘录／定位：`Tweedie’s formula bridges MMSE denoising and the score of the perturbed data distribution through a simple equation`

### ch4_ab-P04-S02 · 修改

原句：
> It determines the correction to the noisy observation needed for MMSE denoising.

改后：
> In \eqref{eq:tweedie-mean}, this score gives the correction from the noisy observation to the MMSE estimate.

斟酌：借 Wei correction 的同任务表达，明确修正的起点和终点；精确 MMSE 关系仍来自本稿 Tweedie 式。

- 依据：Wei et al., Learned Score-Based Turbo Message Passing for Channel Recovery From Spatially Compressed Measurements；PDF p.3；III-C, (11) 前。
  支持层次：采用同任务搭配／技术对象关联；只借 noisy observation 经 score correction 得到 mean 的表述；Wei 的式(11)含训练校准系数，不能用来证明本文精确 MMSE 关系。本文未新增 Tweedie-form 命名，也未引入校准系数。
  已读摘录／定位：`the score network refines the channel mean through a Tweedie-form correction`
- 依据：Cai et al., arXiv:2506.00581v2；PDF p.8；IV-A, (43)–(44) 及式后说明。
  支持层次：技术陈述；Cai 此处为复白噪声标量方差；本文一般正定实协方差及因子 1/2 由本文实表示与现有 Dytso 引用承担，未移植 Cai 的复梯度约定。
  已读摘录／定位：`Tweedie’s formula bridges MMSE denoising and the score of the perturbed data distribution through a simple equation`

### ch4_ab-P04-S03 · 保留

当前句：
> For $C=v\I_D$, \eqref{eq:tweedie-mean} gives the real representation of the conditional mean in \eqref{eq:conditional-channel-integrals}.

斟酌：白噪声特例与第三章条件均值的对应准确，保留。

- 依据：本文既有第三／四／六章；当前输入及交叉引用。
  支持层次：本文定义／推导／衔接；不宣称外部原句；本文特有条件及段落路线由现有公式核对；没有在已读 Shen、Xu、Huang、Ding、Wei 中找到同一技术句时不强行配母本。

## ch4_ab-P05

段落任务：给出条件协方差与二阶 score 的关系。
衔接：下一段归纳两条矩公式的共同用途。

### ch4_ab-P05-S01 · 保留

当前句：
> The conditional covariance $\mathbf P_{\mathbb R}=\operatorname{Cov}(\mathbf h_{\mathbb R} \mid\mathbf u,C)$ is similarly related to the second-order score \cite{dytso2021}, \cite[Sec.~IV-A]{cai2026}:

斟酌：已能自然由均值过渡到协方差，保留；没有把 second-order score 术语偷换成网络实现。

- 依据：Cai et al., arXiv:2506.00581v2；PDF p.8；IV-A, (45) 及式后说明。
  支持层次：术语／技术陈述；只据此说明 second-order score 与 Hessian 的关系；本文一般 Sigma 左右乘顺序保持现有式，不将本文方差求法说成 Cai 的二阶网络。
  已读摘录／定位：`is the Hessian of the log-density function, referred to as the second-order score function`

## ch4_ab-P06

段落任务：说明导数关系避免后验积分，并引出学习。
衔接：先学习一阶 score 和均值，随后从同一均值函数计算方差。

### ch4_ab-P06-S01 · 保留

当前句：
> Here the second-order score is the Hessian of the log density.

斟酌：Hessian 的术语解释准确简洁，保留。

- 依据：Cai et al., arXiv:2506.00581v2；PDF p.8；IV-A, (45) 及式后说明。
  支持层次：术语／技术陈述；只据此说明 second-order score 与 Hessian 的关系；本文一般 Sigma 左右乘顺序保持现有式，不将本文方差求法说成 Cai 的二阶网络。
  已读摘录／定位：`is the Hessian of the log-density function, referred to as the second-order score function`

### ch4_ab-P06-S02 · 修改

原句：
> Equations~\eqref{eq:tweedie-mean} and \eqref{eq:tweedie-covariance} express the channel moments through derivatives of the perturbed channel density, avoiding direct evaluation of the posterior integrals.

改后：
> Equations~\eqref{eq:tweedie-mean} and \eqref{eq:tweedie-covariance} thus relate the channel moments to derivatives of the perturbed channel density without evaluating the posterior integrals.

斟酌：thus 承接刚给出的两条公式；把 avoiding 分词换成明确无须计算积分的关系。

- 依据：Cai et al., arXiv:2506.00581v2；PDF p.8；IV 开篇。
  支持层次：原段关系／技术陈述；保留由后验积分转向 score 表示的论证任务；本文在一般实协方差下推导，不把此处文字登记为从其他论文逐句最小替换。
  已读摘录／定位：`we introduce score-based representations of (22) and (23) to circumvent the intractable high-dimensional integrals involved in posterior message calculation`
- 依据：Cai et al., arXiv:2506.00581v2；PDF p.8；IV-A, (43)–(44) 及式后说明。
  支持层次：技术陈述；Cai 此处为复白噪声标量方差；本文一般正定实协方差及因子 1/2 由本文实表示与现有 Dytso 引用承担，未移植 Cai 的复梯度约定。
  已读摘录／定位：`Tweedie’s formula bridges MMSE denoising and the score of the perturbed data distribution through a simple equation`

### ch4_ab-P06-S03 · 保留

当前句：
> We next learn the first-order score from channel samples and use the resulting mean function to calculate the required variance.

斟酌：原句已经按学习 score、所得均值函数、由此计算方差的顺序衔接；保留，避免把学习近似写成取得精确条件均值。

- 依据：本文既有第三／四／六章；当前输入及交叉引用。
  支持层次：本文定义／推导／衔接；不宣称外部原句；本文特有条件及段落路线由现有公式核对；没有在已读 Shen、Xu、Huang、Ding、Wei 中找到同一技术句时不强行配母本。

## ch4_ab-P07

段落任务：定义待学习 score 及加权 score matching 目标。
衔接：下一段揭示未知边缘 score 使该目标无法直接计算。

### ch4_ab-P07-S01 · 保留

当前句：
> Let $S_\theta(\mathbf u,C)$ approximate the first-order score.

斟酌：原句以 Let 简洁引入待学习 score，避免与两句之后 We use 重复启动，按最小必要修改原则保留。

- 依据：Huang et al., Prior-Agnostic AFDM Channel Estimation；PDF p.3；III-A, (7) 前后。
  支持层次：同任务句式；本文参数化到均值函数，其精确关系来自本稿 Tweedie 等式；Huang 的直接 score 网络不能支持本稿的 reparameterization 等价证明。省略号省去原文 RefineNet 架构。
  已读摘录／定位：`we parameterize the score function ... with learnable weights θ`

### ch4_ab-P07-S02 · 修改

原句：
> For a given perturbation covariance, score matching minimizes the difference between this function and the score of $q_{\bm\Sigma}^{\mathbb R}$.

改后：
> For each fixed covariance $C$, score matching minimizes the squared difference between $S_\theta(\mathbf u,C)$ and the score of $q_{\bm\Sigma}^{\mathbb R}$.

斟酌：明确固定 C 和 squared difference，与随后加权平方损失一致，避免模糊的 this function 指代。

- 依据：Cai et al., arXiv:2506.00581v2；PDF p.8；IV-B, (46)–(48)。
  支持层次：原段关系／技术陈述；先写未知边缘 score 的目标，再写已知条件高斯 score 的目标；本文 Sigma 加权是既有适配，非 Cai 原式。摘录中的数学为文字化表示。
  已读摘录／定位：`Eqn. (46) cannot be directly used as the loss function since ... does not have an analytical form.`

### ch4_ab-P07-S03 · 保留

当前句：
> We use the covariance-weighted objective

斟酌：加权属于本文既有训练设定，简洁引入原公式即可。

- 依据：本文既有第三／四／六章；当前输入及交叉引用。
  支持层次：本文定义／推导／衔接；不宣称外部原句；本文特有条件及段落路线由现有公式核对；没有在已读 Shen、Xu、Huang、Ding、Wei 中找到同一技术句时不强行配母本。

## ch4_ab-P08

段落任务：由已知条件高斯 score 得到可计算 DSM 目标。
衔接：下一段说明两目标的等价与最优性条件。

### ch4_ab-P08-S01 · 修改

原句：
> The unknown score prevents direct evaluation of this objective.

改后：
> This objective cannot be evaluated directly because the score of $q_{\bm\Sigma}^{\mathbb R}$ is unknown.

斟酌：把未知量明确为边缘密度的 score，直接交代不能计算目标的原因。

- 依据：Cai et al., arXiv:2506.00581v2；PDF p.8；IV-B, (46)–(48)。
  支持层次：原段关系／技术陈述；先写未知边缘 score 的目标，再写已知条件高斯 score 的目标；本文 Sigma 加权是既有适配，非 Cai 原式。摘录中的数学为文字化表示。
  已读摘录／定位：`Eqn. (46) cannot be directly used as the loss function since ... does not have an analytical form.`

### ch4_ab-P08-S02 · 保留

当前句：
> However, the Gaussian perturbation in \eqref{eq:colored-query} has the known conditional score $-\bm\Sigma^{-1}(\mathbf u-\mathbf h_{\mathbb R})$.

斟酌：已知条件高斯 score 是 DSM 转换的关键，原句及全部矩阵乘法保持。

- 依据：Cai et al., arXiv:2506.00581v2；PDF p.8；IV-B, (46)–(48)。
  支持层次：原段关系／技术陈述；先写未知边缘 score 的目标，再写已知条件高斯 score 的目标；本文 Sigma 加权是既有适配，非 Cai 原式。摘录中的数学为文字化表示。
  已读摘录／定位：`Eqn. (46) cannot be directly used as the loss function since ... does not have an analytical form.`
- 依据：本文既有第三／四／六章；当前输入及交叉引用。
  支持层次：本文定义／推导／衔接；不宣称外部原句；本文特有条件及段落路线由现有公式核对；没有在已读 Shen、Xu、Huang、Ding、Wei 中找到同一技术句时不强行配母本。

### ch4_ab-P08-S03 · 修改

原句：
> Denoising score matching replaces the unknown score by this conditional score \cite{vincent2011}, giving

改后：
> Using this conditional score, denoising score matching \cite{vincent2011} gives the objective

斟酌：承接已知 conditional score 引出目标；等价关系仍由随后独立段落说明，不把逐样本替换写成逐点恒等。

- 依据：Cai et al., arXiv:2506.00581v2；PDF p.8；IV-B, (46)–(48)。
  支持层次：原段关系／技术陈述；先写未知边缘 score 的目标，再写已知条件高斯 score 的目标；本文 Sigma 加权是既有适配，非 Cai 原式。摘录中的数学为文字化表示。
  已读摘录／定位：`Eqn. (46) cannot be directly used as the loss function since ... does not have an analytical form.`

## ch4_ab-P09

段落任务：说明目标等价范围及无限制函数空间最优解。
衔接：为下一段以均值函数作等价参数化奠定基础。

### ch4_ab-P09-S01 · 保留

当前句：
> The two objectives differ by a term independent of $\theta$.

斟酌：两目标相差与参数无关项是严谨等价说明，保留。

- 依据：Cai et al., arXiv:2506.00581v2；PDF p.8；IV-B, (46)–(48) 后。
  支持层次：技术陈述；Cai 后续明确网络表示能力条件；本文继续保留固定 C、总体目标及 unrestricted 函数空间，不声称有限网络必达精确 score。目标差常数和加权均值最优性依本文既有推导。
  已读摘录／定位：`The equivalence is in the sense that (46) and (47) share the same optimal solution`
- 依据：本文既有第三／四／六章；当前输入及交叉引用。
  支持层次：本文定义／推导／衔接；不宣称外部原句；本文特有条件及段落路线由现有公式核对；没有在已读 Shen、Xu、Huang、Ding、Wei 中找到同一技术句时不强行配母本。

### ch4_ab-P09-S02 · 保留

当前句：
> At each fixed $C$, both are minimized by $\nabla_{\mathbf u}\log q_{\bm\Sigma}^{\mathbb R}$ over unrestricted score functions.

斟酌：固定 C 和 unrestricted score functions 限定决定最优性含义，保留。

- 依据：Cai et al., arXiv:2506.00581v2；PDF p.8；IV-B, (46)–(48) 后。
  支持层次：技术陈述；Cai 后续明确网络表示能力条件；本文继续保留固定 C、总体目标及 unrestricted 函数空间，不声称有限网络必达精确 score。目标差常数和加权均值最优性依本文既有推导。
  已读摘录／定位：`The equivalence is in the sense that (46) and (47) share the same optimal solution`

## ch4_ab-P10

段落任务：把 score 参数化为均值函数并得到原有均值损失。
衔接：下一段解释该损失中的期望及最优均值。

### ch4_ab-P10-S01 · 修改

原句：
> To obtain the channel estimate directly, we parameterize the score through a mean function $f_\theta(\mathbf u,C)$ as $S_\theta=\bm\Sigma^{-1}(f_\theta-\mathbf u)$.

改后：
> To obtain the channel estimate directly, we parameterize the score as $S_\theta=\bm\Sigma^{-1}(f_\theta-\mathbf u)$, where $f_\theta(\mathbf u,C)$ is a mean function.

斟酌：先写参数化等式，再就近解释 f_theta，减少 through ... as 的绕行；仍是均值参数化而非新网络结构。

- 依据：Huang et al., Prior-Agnostic AFDM Channel Estimation；PDF p.3；III-A, (7) 前后。
  支持层次：同任务句式；本文参数化到均值函数，其精确关系来自本稿 Tweedie 等式；Huang 的直接 score 网络不能支持本稿的 reparameterization 等价证明。省略号省去原文 RefineNet 架构。
  已读摘录／定位：`we parameterize the score function ... with learnable weights θ`
- 依据：本文既有第三／四／六章；当前输入及交叉引用。
  支持层次：本文定义／推导／衔接；不宣称外部原句；本文特有条件及段落路线由现有公式核对；没有在已读 Shen、Xu、Huang、Ding、Wei 中找到同一技术句时不强行配母本。

### ch4_ab-P10-S02 · 保留

当前句：
> Substituting this relation into \eqref{eq:denoising-score-objective} gives the training loss

斟酌：代入上式得到相同 loss 的衔接清楚，保留。

- 依据：本文既有第三／四／六章；当前输入及交叉引用。
  支持层次：本文定义／推导／衔接；不宣称外部原句；本文特有条件及段落路线由现有公式核对；没有在已读 Shen、Xu、Huang、Ding、Wei 中找到同一技术句时不强行配母本。

## ch4_ab-P11

段落任务：明确训练平均的对象和条件均值最优性。
衔接：随后从理想目标进入训练扰动分布的选择。

### ch4_ab-P11-S01 · 修改

原句：
> The expectation averages clean channels, perturbation covariances, and Gaussian noise.

改后：
> The expectation is taken over the clean channels, perturbation covariances, and Gaussian noise.

斟酌：采用期望范围的常用说明句，避免 averages 后直接罗列不同数学对象。

- 依据：Shen et al., LEO Satellite-Enabled Random Access with Large Differential Delay and Doppler Shift；PDF p.11；IV-A2, (61) 后。
  支持层次：常规期望说明句式；仅为期望运算范围的语法参照；本文积分变量是干净信道、协方差和高斯噪声，与 Shen 的符号检测交叉熵样本不同，不是相同损失或原句最小替换。
  已读摘录／定位：`the expectation is calculated over Θ`

### ch4_ab-P11-S02 · 保留

当前句：
> For each fixed $C$, the conditional mean $\mathbf m_{\mathbb R}(\mathbf u,C)$ minimizes this loss over unrestricted mean functions.

斟酌：总体函数空间中的条件均值最优性是必要含义，保留。

- 依据：Cai et al., arXiv:2506.00581v2；PDF p.8；IV-B, (46)–(48) 后。
  支持层次：技术陈述；Cai 后续明确网络表示能力条件；本文继续保留固定 C、总体目标及 unrestricted 函数空间，不声称有限网络必达精确 score。目标差常数和加权均值最优性依本文既有推导。
  已读摘录／定位：`The equivalence is in the sense that (46) and (47) share the same optimal solution`
- 依据：本文既有第三／四／六章；当前输入及交叉引用。
  支持层次：本文定义／推导／衔接；不宣称外部原句；本文特有条件及段落路线由现有公式核对；没有在已读 Shen、Xu、Huang、Ding、Wei 中找到同一技术句时不强行配母本。

### ch4_ab-P11-S03 · 保留

当前句：
> Thus, training with \eqref{eq:first-loss} also learns the first-order score through the above parameterization.

斟酌：明确均值训练与 score 学习的关系，且紧接已说明的条件，保留。

- 依据：本文既有第三／四／六章；当前输入及交叉引用。
  支持层次：本文定义／推导／衔接；不宣称外部原句；本文特有条件及段落路线由现有公式核对；没有在已读 Shen、Xu、Huang、Ding、Wei 中找到同一技术句时不强行配母本。

## ch4_ab-P12

段落任务：由迭代噪声变化和可能的相关误差引出多噪声有色训练。
衔接：把具体采样参数留给实验节，再说明在线实际输入条件。

### ch4_ab-P12-S01 · 修改

原句：
> The denoiser must accommodate different input noise levels during message passing.

改后：
> During message passing, the denoiser receives observations with different noise variances.

斟酌：从迭代中的实际输入引出多噪声训练，去掉 must accommodate 的操作指南语气。

- 依据：Cai et al., arXiv:2506.00581v2；PDF p.9；IV-B, (49) 前。
  支持层次：原段关系／完整搭配；仅支持跨多个训练噪声水平的动机；相关误差、Kronecker 协方差及在线白噪声是本文设置。
  已读摘录／定位：`the score-based MMSE denoiser is required to operate effectively across a range of noise levels`

### ch4_ab-P12-S02 · 保留

当前句：
> We therefore train over a range of perturbation variances, as in \cite[Sec.~IV-B]{cai2026}.

斟酌：多噪声水平训练与蔡文继承关系已有正确引用，保留。

- 依据：Cai et al., arXiv:2506.00581v2；PDF p.9；IV-B, (49) 前。
  支持层次：原段关系／完整搭配；仅支持跨多个训练噪声水平的动机；相关误差、Kronecker 协方差及在线白噪声是本文设置。
  已读摘录／定位：`the score-based MMSE denoiser is required to operate effectively across a range of noise levels`

### ch4_ab-P12-S03 · 修改

原句：
> In the finite-dimensional multi-frame model, the input errors can also be correlated.

改后：
> The input errors in the finite-dimensional multi-frame model can also be correlated.

斟酌：将主语 input errors 前置；can 保持相关性是可能出现的情况而非已测量事实。

- 依据：本文既有第三／四／六章；当前输入及交叉引用。
  支持层次：本文定义／推导／衔接；不宣称外部原句；本文特有条件及段落路线由现有公式核对；没有在已读 Shen、Xu、Huang、Ding、Wei 中找到同一技术句时不强行配母本。

### ch4_ab-P12-S04 · 修改

原句：
> To include such errors in training, we use colored perturbations with covariance $C=v(R_{\rm a}\otimes\I_N\otimes R_{\rm c})$ in antenna--output--input order and condition the network on $C$ \cite[Sec.~III-B]{shastri2022}.

改后：
> To account for this correlation, we corrupt clean channel samples with colored Gaussian noise of covariance $C=v(R_{\rm a}\otimes\I_N\otimes R_{\rm c})$ in antenna--output--input order and condition the network on $C$ \cite[Sec.~III-B]{shastri2022}.

斟酌：采用 Huang 同一训练动作中的 corrupt clean channel ... Gaussian noise 搭配，必要替换为本文有色协方差和条件输入；不移植扩散采样。

- 依据：Huang et al., Prior-Agnostic AFDM Channel Estimation；PDF p.3；III-A, (7) 后训练样本段。
  支持层次：采用同任务完整搭配并作必要适配；保留向干净信道加入高斯噪声的训练动作，本文改为 correlated Gaussian noise 和 C 条件输入；Huang 只有白噪声，不能登记为本文有色训练技术来源。省略号仅省去公式变量。
  已读摘录／定位：`we corrupt the clean channel realizations ... from the training set by adding complex Gaussian noise at the specific level`
- 依据：本文既有第三／四／六章；当前输入及交叉引用。
  支持层次：本文定义／推导／衔接；不宣称外部原句；本文特有条件及段落路线由现有公式核对；没有在已读 Shen、Xu、Huang、Ding、Wei 中找到同一技术句时不强行配母本。

### ch4_ab-P12-S05 · 保留

当前句：
> The covariance factors and the sampling law for $v$ are specified in Section~\ref{sec:training-settings}.

斟酌：实验节定位明确，保留。

- 依据：本文既有第三／四／六章；当前输入及交叉引用。
  支持层次：本文定义／推导／衔接；不宣称外部原句；本文特有条件及段落路线由现有公式核对；没有在已读 Shen、Xu、Huang、Ding、Wei 中找到同一技术句时不强行配母本。

## ch4_ab-P13

段落任务：将实输出重新组成复均值函数，并明确白噪声在线查询。
衔接：IV-C 继续从该均值函数导出所需方差。

### ch4_ab-P13-S01 · 保留

当前句：
> Reshaping the real and imaginary outputs of $f_\theta$ defines the complex mean map $F_\theta(R,C)$.

斟酌：实／复输出到 F_theta 的定义必要且清楚，保留。

- 依据：Huang et al., Prior-Agnostic AFDM Channel Estimation；PDF p.3；III-A, (7) 后实／复训练段。
  支持层次：借用同任务句式／完整搭配；改为本文 vect(H) 的 2D 维堆叠；不复制 RefineNet、双通道形状、扩散采样或原文复高斯缩放。这里只说明实表示，不能由此推出 colored noise。
  已读摘录／定位：`Since the AFDM effective channel matrix is complex-valued, we adopt a two-channel real–imaginary representation`
- 依据：本文既有第三／四／六章；当前输入及交叉引用。
  支持层次：本文定义／推导／衔接；不宣称外部原句；本文特有条件及段落路线由现有公式核对；没有在已读 Shen、Xu、Huang、Ding、Wei 中找到同一技术句时不强行配母本。

### ch4_ab-P13-S02 · 修改

原句：
> For the scalar-variance message in \eqref{eq:pseudo-awgn}, this map is evaluated at $C=v\I_D$.

改后：
> For the scalar-variance message in \eqref{eq:pseudo-awgn}, we evaluate $F_\theta$ at $C=v\I_D$.

斟酌：直接指明在线计算的是 F_theta 并保留 C=vI，不让有色训练被误读为有色在线消息。

- 依据：本文既有第三／四／六章；当前输入及交叉引用。
  支持层次：本文定义／推导／衔接；不宣称外部原句；本文特有条件及段落路线由现有公式核对；没有在已读 Shen、Xu、Huang、Ding、Wei 中找到同一技术句时不强行配母本。

### ch4_ab-P13-S03 · 保留

当前句：
> The network architecture and preconditioning are given in Section~\ref{sec:network-settings}.

斟酌：架构和预条件化仍留在实验设置节，保留引用。

- 依据：本文既有第三／四／六章；当前输入及交叉引用。
  支持层次：本文定义／推导／衔接；不宣称外部原句；本文特有条件及段落路线由现有公式核对；没有在已读 Shen、Xu、Huang、Ding、Wei 中找到同一技术句时不强行配母本。

## ch4_cd-P01

段落任务：从联合后验所需的条件方差出发，对已有均值恒等式求导得到协方差和标量方差。
衔接：承接 IV-B 已学习的均值，下一段解释 trace 的复数归一化，不提替代二阶网络。

### ch4_cd-P01-S01 · 修改

原句：
> The joint posterior moments in \eqref{eq:exact-local-moments} require the channel variance as well as its mean.

改后：
> The joint posterior moments in \eqref{eq:exact-local-moments} require both the conditional channel mean and variance.

斟酌：用 both ... and ... 将本节目标与上一节均值并列，补明 conditional，未改变估计对象。

- 依据：本稿既有公式与条件；III-B eq:exact-local-moments；IV-A eq:tweedie-mean/eq:tweedie-covariance。
  支持层次：本文推导与段落承接；只说明本文已定义的条件矩；不是 Shen、Xu、Huang、Ding 或 Wei 的原句最小替换。

### ch4_cd-P01-S02 · 保留

当前句：
> Differentiating \eqref{eq:tweedie-mean} with respect to $\mathbf u$ at fixed $C$ gives the output-by-input Jacobian $\mathbf J_m=\partial\mathbf m_{\mathbb R}/\partial\mathbf u =\I_{2D}+\bm\Sigma\nabla_{\mathbf u}^2 \log q_{\bm\Sigma}^{\mathbb R}(\mathbf u)$.

斟酌：固定 C、output-by-input Jacobian 及逐项求导方向均必要，现句已直接清楚，不为换词改动。

- 依据：本稿既有公式与条件；III-B eq:exact-local-moments；IV-A eq:tweedie-mean/eq:tweedie-covariance。
  支持层次：本文推导与段落承接；只说明本文已定义的条件矩；不是 Shen、Xu、Huang、Ding 或 Wei 的原句最小替换。
- 依据：Dytso, Poor, and Shamai (2021)；PDF p.2章节概述中的短摘录；p.5，§IV，Prop.1，式(22)；p.6式(25)。
  支持层次：技术陈述：Gaussian 扰动下均值导数与协方差关系；原文 Jacobian 约定与本文转置；本文采用 output-by-input，故 P=J_m Sigma，Sigma 在右。固定 C、复数实表示和除以复维度 D 是本文适配。
  已读摘录／定位：`the Jacobian of the conditional expectation to the conditional variance`

### ch4_cd-P01-S03 · 修改

原句：
> Multiplying by $\bm\Sigma$ on the right and using \eqref{eq:tweedie-covariance} yields \cite[Prop.~1]{dytso2021}

改后：
> Right-multiplying by $\bm\Sigma$ and using \eqref{eq:tweedie-covariance}, we obtain \cite[Prop.~1]{dytso2021}

斟酌：把矩阵右乘操作紧邻已有公式，保持协方差左右乘顺序及出处。

- 依据：Dytso, Poor, and Shamai (2021)；PDF p.2章节概述中的短摘录；p.5，§IV，Prop.1，式(22)；p.6式(25)。
  支持层次：技术陈述：Gaussian 扰动下均值导数与协方差关系；原文 Jacobian 约定与本文转置；本文采用 output-by-input，故 P=J_m Sigma，Sigma 在右。固定 C、复数实表示和除以复维度 D 是本文适配。
  已读摘录／定位：`the Jacobian of the conditional expectation to the conditional variance`
- 依据：本稿既有公式与条件；III-B eq:exact-local-moments；IV-A eq:tweedie-mean/eq:tweedie-covariance。
  支持层次：本文推导与段落承接；只说明本文已定义的条件矩；不是 Shen、Xu、Huang、Ding 或 Wei 的原句最小替换。

## ch4_cd-P02

段落任务：解释 trace/D 和白噪声特例，明确同一均值函数给出所需方差。
衔接：由精确关系自然进入学习均值及有限差分近似。

### ch4_cd-P02-S01 · 修改

原句：
> The trace sums real and imaginary variances, so division by $D$ gives the variance per complex coordinate.

改后：
> The trace includes the variances of the real and imaginary components; division by $D$ therefore gives the variance per complex coordinate.

斟酌：明确迹中求和的对象是实虚分量方差，保留复维度 D，避免读成除以 2D。

- 依据：Huang et al. (2026)；PDF p.3，§III-A，式(7)后的实虚表示段。
  支持层次：完整搭配及相关表示方式；非方差公式来源；Huang 支持把复信道实部和虚部分开表示；trace/D 与 v/(2D) 的因子是本稿由 Sigma=v I_(2D)/2 推导，不能归于 Huang。
  已读摘录／定位：`a two-channel real–imaginary representation`
- 依据：本稿既有公式与条件；III-B eq:exact-local-moments；IV-A eq:tweedie-mean/eq:tweedie-covariance。
  支持层次：本文推导与段落承接；只说明本文已定义的条件矩；不是 Shen、Xu、Huang、Ding 或 Wei 的原句最小替换。

### ch4_cd-P02-S02 · 保留

当前句：
> At $C=v\I_D$, this reduces to $\tau^\star=v\operatorname{div}\mathbf m_{\mathbb R}/(2D)$.

斟酌：白噪声特例和 1/(2D) 因子准确且简洁，保留。

- 依据：Dytso, Poor, and Shamai (2021)；PDF p.2章节概述中的短摘录；p.5，§IV，Prop.1，式(22)；p.6式(25)。
  支持层次：技术陈述：Gaussian 扰动下均值导数与协方差关系；原文 Jacobian 约定与本文转置；本文采用 output-by-input，故 P=J_m Sigma，Sigma 在右。固定 C、复数实表示和除以复维度 D 是本文适配。
  已读摘录／定位：`the Jacobian of the conditional expectation to the conditional variance`
- 依据：本稿既有公式与条件；III-B eq:exact-local-moments；IV-A eq:tweedie-mean/eq:tweedie-covariance。
  支持层次：本文推导与段落承接；只说明本文已定义的条件矩；不是 Shen、Xu、Huang、Ding 或 Wei 的原句最小替换。

### ch4_cd-P02-S03 · 修改

原句：
> Thus, the scalar variance required by the receiver can be obtained from derivatives of the same conditional-mean function.

改后：
> Thus, the required conditional variance can be computed from derivatives of the conditional mean.

斟酌：压缩 can be obtained from derivatives of the same ...，明确量为 conditional variance，自然承接而不作网络对比。

- 依据：Dytso, Poor, and Shamai (2021)；PDF p.2章节概述中的短摘录；p.5，§IV，Prop.1，式(22)；p.6式(25)。
  支持层次：技术陈述：Gaussian 扰动下均值导数与协方差关系；原文 Jacobian 约定与本文转置；本文采用 output-by-input，故 P=J_m Sigma，Sigma 在右。固定 C、复数实表示和除以复维度 D 是本文适配。
  已读摘录／定位：`the Jacobian of the conditional expectation to the conditional variance`
- 依据：本稿既有公式与条件；III-B eq:exact-local-moments；IV-A eq:tweedie-mean/eq:tweedie-covariance。
  支持层次：本文推导与段落承接；只说明本文已定义的条件矩；不是 Shen、Xu、Huang、Ding 或 Wei 的原句最小替换。

## ch4_cd-P03

段落任务：用学习均值和随机双侧差分计算所需导数迹。
衔接：先给近似对象，再给随机探针和估计式，下一段交代固定条件。

### ch4_cd-P03-S01 · 修改

原句：
> We approximate this quantity by replacing the exact mean with $f_\theta$ and estimating its derivative trace through Monte Carlo finite differences \cite[Sec.~V-B]{metzler2014}.

改后：
> We estimate this trace using Monte Carlo finite differences \cite[Sec.~V-B]{metzler2014}, with $f_\theta$ in place of the conditional mean.

斟酌：引文紧跟 Monte Carlo finite differences，使 Metzler 只支撑导数迹估计方法；随后单独说明本文以 f_theta 近似条件均值，避免技术归属混淆。

- 依据：Metzler, Maleki, and Baraniuk (2014)；PDF p.18，§V-B，式(21)及随后平均估计段。
  支持层次：技术思路与原段关系：导数难直接计算→随机扰动→平均；原文使用标准 Gaussian 探针及单侧差分；本文用独立随机符号、Sigma^(1/2) 加权及双侧差分。这些是本文已存适配，不能声称为原文公式。
  已读摘录／定位：`a good approximation of the divergence can be obtained`
- 依据：本稿既有 eq:derivative-trace；IV-C，随机探针定义及双侧有限差分式。
  支持层次：本文定义、代数适配；E[zz^T]=I_(2D)、w=Sigma^(1/2)z、L_z 个独立探针、双侧差分和按 D 归一化全部保留。

### ch4_cd-P03-S02 · 修改

原句：
> For independent random sign vectors $\mathbf z_\ell$ with $\E[\mathbf z_\ell\mathbf z_\ell^{\mathsf T}]=\I_{2D}$, set $\mathbf w_\ell=\bm\Sigma^{1/2}\mathbf z_\ell$.

改后：
> Let $\mathbf z_\ell$ be independent random sign vectors with $\E[\mathbf z_\ell\mathbf z_\ell^{\mathsf T}]=\I_{2D}$, and define $\mathbf w_\ell=\bm\Sigma^{1/2}\mathbf z_\ell$.

斟酌：将操作式 set 改为连贯数学定义句，随机符号、独立性及加权关系逐项不变。

- 依据：本稿既有 eq:derivative-trace；IV-C，随机探针定义及双侧有限差分式。
  支持层次：本文定义、代数适配；E[zz^T]=I_(2D)、w=Sigma^(1/2)z、L_z 个独立探针、双侧差分和按 D 归一化全部保留。

### ch4_cd-P03-S03 · 修改

原句：
> The estimate is

改后：
> The resulting estimate is

斟酌：补 resulting 明确下式由刚定义的探针与差分构成；仅是本稿公式引出语，不冒称文献母句。

- 依据：本稿既有 eq:derivative-trace；IV-C，随机探针定义及双侧有限差分式。
  支持层次：本文定义、代数适配；E[zz^T]=I_(2D)、w=Sigma^(1/2)z、L_z 个独立探针、双侧差分和按 D 归一化全部保留。

## ch4_cd-P04

段落任务：说明有限差分的求导对象、固定协方差和在线使用条件。
衔接：结束方差估计，为活动概率这一剩余后验量让出主线。

### ch4_cd-P04-S01 · 修改

原句：
> Both evaluations hold $C$ fixed and differentiate the complete mean map, including the preconditioning in \eqref{eq:mean-preconditioning}.

改后：
> The finite differences in \eqref{eq:derivative-trace} hold $C$ fixed and act on the complete mean map, including the preconditioning in \eqref{eq:mean-preconditioning}.

斟酌：将不够准确的“two evaluations differentiate”改为“finite differences act on”；所求完整均值及固定 C 条件不变。

- 依据：本稿既有 eq:derivative-trace 与 eq:mean-preconditioning；IV-C 与 VI-A2。
  支持层次：本文实现条件和公式引用；导数作用于完整均值映射，固定噪声条件 C；不是只对网络残差或预条件前的输出求导。

### ch4_cd-P04-S02 · 修改

原句：
> Evaluating \eqref{eq:derivative-trace} at $C=v\I_D$ supplies the conditional variance estimates for the message updates.

改后：
> The conditional variance estimates used in message passing are then obtained by setting $C=v\I_D$.

斟酌：承接前句差分式，自然给出在线白噪声取值；不把训练有色条件写成在线全协方差推断。

- 依据：本稿既有接收机和实验设置；V sec:overall；VI sec:receiver-settings。
  支持层次：本文交叉引用；保留在线白噪声条件 C=v I_D 及有限差分设置位置，不移植其他文献的接收机。

### ch4_cd-P04-S03 · 保留

当前句：
> Their use in the receiver is described in Section~\ref{sec:overall}, and the finite-difference settings are given in Section~\ref{sec:receiver-settings}.

斟酌：两项交叉引用有明确对象，保留已有实现与有限差分设置位置。

- 依据：本稿既有接收机和实验设置；V sec:overall；VI sec:receiver-settings。
  支持层次：本文交叉引用；保留在线白噪声条件 C=v I_D 及有限差分设置位置，不移植其他文献的接收机。

## ch4_cd-P05

段落任务：由已获得的条件信道矩转到活动概率，并写为先验对数赔率加似然比。
衔接：先指出所需概率，再给两个假设，随后引出比值的学习。

### ch4_cd-P05-S01 · 修改

原句：
> The preceding calculations provide the conditional channel mean and variance.

改后：
> Having obtained the conditional channel mean and variance, we next consider the activity probability.

斟酌：将已完成的信道矩计算直接作为转向活动概率的前提，减少先总结再重新起句的停顿。

- 依据：本稿既有活动后验和似然；III-B eq:query-densities/eq:local-activity；IV-D eq:activity-log-odds。
  支持层次：本文公式的等价改写与段落承接；完整先验积分、active/inactive 两假设、rho 的 Bayes 校正均维持原义；此处 log-odds 形式不是 Shen、Ding 的原式。

### ch4_cd-P05-S02 · 修改

原句：
> The remaining quantity for joint estimation is the activity probability, which depends on the likelihoods of the active and inactive hypotheses.

改后：
> This probability depends on the likelihoods under the active and inactive hypotheses.

斟酌：前句已提出下一目标，此句只保留两假设似然关系，避免再次复述 remaining quantity。

- 依据：Ding et al. (2026)；PDF pp.3–4，§III-B，式(14)–(16)及式(16)后的跨页句。
  支持层次：同任务的技术关系与完整搭配：两假设似然比→后验概率；Ding 使用解析 Bernoulli–Gaussian 稀疏先验；本稿为完整信道先验边缘化后学习密度比。只借鉴概率与两假设关系，不把其稀疏支持概率等同于本稿分类学习。
  已读摘录／定位：`the likelihood ratio between the nonzero and zero components`
- 依据：本稿既有活动后验和似然；III-B eq:query-densities/eq:local-activity；IV-D eq:activity-log-odds。
  支持层次：本文公式的等价改写与段落承接；完整先验积分、active/inactive 两假设、rho 的 Bayes 校正均维持原义；此处 log-odds 形式不是 Shen、Ding 的原式。

### ch4_cd-P05-S03 · 修改

原句：
> Rewriting \eqref{eq:local-activity} gives

改后：
> Taking the log odds of \eqref{eq:local-activity} gives

斟酌：明确 rewriting 的具体数学操作，与下式 log posterior odds 的对象一致。

- 依据：本稿既有活动后验和似然；III-B eq:query-densities/eq:local-activity；IV-D eq:activity-log-odds。
  支持层次：本文公式的等价改写与段落承接；完整先验积分、active/inactive 两假设、rho 的 Bayes 校正均维持原义；此处 log-odds 形式不是 Shen、Ding 的原式。
- 依据：Menon and Ong (2016)；PDF p.3，§4.2，式(16)–(17)及 logistic-loss 例。
  支持层次：技术陈述：分类概率、训练类先验与密度比；本稿采用 0/1 标签及 logit，并以 (R,v) 为输入。任意有限网络只给出估计；精确关系限于总体风险、无限制 logits 的最优解。
  已读摘录／定位：`Bayes-optimal scorer`

## ch4_cd-P06

段落任务：指出主动似然积分未知，但活动更新只需要两似然的比值。
衔接：从需估计的对象引出二元分类，下一段构造对应样本。

### ch4_cd-P06-S01 · 保留

当前句：
> The inactive likelihood $q_{0,v}$ is known, whereas $q_{1,v}$ involves the channel integral in \eqref{eq:query-densities}.

斟酌：已准确区分已知 inactive likelihood 和需积分 active likelihood，保留。

- 依据：本稿既有活动后验和似然；III-B eq:query-densities/eq:local-activity；IV-D eq:activity-log-odds。
  支持层次：本文公式的等价改写与段落承接；完整先验积分、active/inactive 两假设、rho 的 Bayes 校正均维持原义；此处 log-odds 形式不是 Shen、Ding 的原式。

### ch4_cd-P06-S02 · 保留

当前句：
> Only their ratio is needed in \eqref{eq:activity-log-odds}.

斟酌：简洁说明当前公式只需比值，是引出分类学习的关键，不添加额外防御。

- 依据：本稿既有活动后验和似然；III-B eq:query-densities/eq:local-activity；IV-D eq:activity-log-odds。
  支持层次：本文公式的等价改写与段落承接；完整先验积分、active/inactive 两假设、rho 的 Bayes 校正均维持原义；此处 log-odds 形式不是 Shen、Ding 的原式。
- 依据：Menon and Ong (2016)；PDF p.3，§4.2，式(16)–(17)及 logistic-loss 例。
  支持层次：技术陈述：分类概率、训练类先验与密度比；本稿采用 0/1 标签及 logit，并以 (R,v) 为输入。任意有限网络只给出估计；精确关系限于总体风险、无限制 logits 的最优解。
  已读摘录／定位：`Bayes-optimal scorer`

### ch4_cd-P06-S03 · 修改

原句：
> We estimate this ratio directly by binary classification \cite{menon2016}, using samples from the full channel prior.

改后：
> We learn this density ratio through binary classification using samples from the full channel prior \cite{menon2016}.

斟酌：将密度比、分类方式和完整信道样本连成一个目标句，Menon 仍为技术出处。

- 依据：Menon and Ong (2016)；PDF p.3，§4.2，式(16)–(17)及 logistic-loss 例。
  支持层次：技术陈述：分类概率、训练类先验与密度比；本稿采用 0/1 标签及 logit，并以 (R,v) 为输入。任意有限网络只给出估计；精确关系限于总体风险、无限制 logits 的最优解。
  已读摘录／定位：`Bayes-optimal scorer`
- 依据：本稿既有分类训练分布；IV-D eq:classifier-loss 之前；III-B eq:query-densities。
  支持层次：本文定义与相同条件分布的核对；pi_tr=1/2；active 为 H+W、inactive 为 W；W 为白 Gaussian 噪声并独立于 H；两类 v 采用同一采样律。不得改成有色分类训练。

## ch4_cd-P07

段落任务：定义与两假设一致的白噪声分类训练样本和交叉熵目标。
衔接：按样本、分布、损失递进，下一段分析其总体最优解。

### ch4_cd-P07-S01 · 修改

原句：
> To construct the two classes, draw $a\in\{0,1\}$ with $\Pr(a=1)=\pi_{\rm tr}=1/2$.

改后：
> The training data contain two classes with equal prior probability, $\Pr(a=1)=\pi_{\rm tr}=1/2$, where $a\in\{0,1\}$.

斟酌：把 draw 命令改为训练分布的叙述；类先验、a 的取值完整保留。借鉴 Shen 先构造训练数据再讲损失的段落任务。

- 依据：Shen et al. (2025)；PDF p.11，§IV-A2，数据集构造段及式(60)–(61)。
  支持层次：同任务的段落顺序及短搭配：样本构造→网络输出→交叉熵；Shen 为有限星座数据检测，本稿为二元活动分类；不得移植其符号先验、CNN 标签、真后验表述或数据筛选规则。
  已读摘录／定位：`the cross entropy is utilized as the loss function`
- 依据：本稿既有分类训练分布；IV-D eq:classifier-loss 之前；III-B eq:query-densities。
  支持层次：本文定义与相同条件分布的核对；pi_tr=1/2；active 为 H+W、inactive 为 W；W 为白 Gaussian 噪声并独立于 H；两类 v 采用同一采样律。不得改成有色分类训练。

### ch4_cd-P07-S02 · 修改

原句：
> For $a=1$, generate $R=H+W$ with $H\sim q_{\rm tr}$; for $a=0$, generate $R=W$.

改后：
> For $a=1$, the observation is $R=H+W$ with $H\sim q_{\rm tr}$; for $a=0$, it is $R=W$.

斟酌：从操作清单式 generate 改为两类观测的平行定义，条件模型不变。

- 依据：本稿既有分类训练分布；IV-D eq:classifier-loss 之前；III-B eq:query-densities。
  支持层次：本文定义与相同条件分布的核对；pi_tr=1/2；active 为 H+W、inactive 为 W；W 为白 Gaussian 噪声并独立于 H；两类 v 采用同一采样律。不得改成有色分类训练。

### ch4_cd-P07-S03 · 修改

原句：
> In both classes, $\vect(W)\sim\CN(\mathbf0,v\I_D)$ independently of $H$, and $v$ has the same sampling law.

改后：
> The noise satisfies $\vect(W)\sim\CN(\mathbf0,v\I_D)$ independently of $H$, and both classes use the same sampling law for $v$.

斟酌：将两类同一 v 采样律表述为共同训练条件，保留白噪声与信道独立性。

- 依据：本稿既有分类训练分布；IV-D eq:classifier-loss 之前；III-B eq:query-densities。
  支持层次：本文定义与相同条件分布的核对；pi_tr=1/2；active 为 H+W、inactive 为 W；W 为白 Gaussian 噪声并独立于 H；两类 v 采用同一采样律。不得改成有色分类训练。

### ch4_cd-P07-S04 · 修改

原句：
> The resulting class-conditional densities are precisely those in \eqref{eq:query-densities}.

改后：
> The resulting class-conditional densities are therefore those in \eqref{eq:query-densities}.

斟酌：用 therefore 连接刚定义的样本与第三章似然；移除多余程度词 precisely，不降低相同分布的结论。

- 依据：本稿既有分类训练分布；IV-D eq:classifier-loss 之前；III-B eq:query-densities。
  支持层次：本文定义与相同条件分布的核对；pi_tr=1/2；active 为 H+W、inactive 为 W；W 为白 Gaussian 噪声并独立于 H；两类 v 采用同一采样律。不得改成有色分类训练。
- 依据：本稿既有活动后验和似然；III-B eq:query-densities/eq:local-activity；IV-D eq:activity-log-odds。
  支持层次：本文公式的等价改写与段落承接；完整先验积分、active/inactive 两假设、rho 的 Bayes 校正均维持原义；此处 log-odds 形式不是 Shen、Ding 的原式。

### ch4_cd-P07-S05 · 修改

原句：
> We learn a logit by minimizing the binary cross-entropy loss

改后：
> The classifier logit is learned by minimizing the binary cross-entropy loss

斟酌：采用训练目标承接网络输出的常规论文表述；保留 logit 而不误写为直接监督真实密度比。

- 依据：Shen et al. (2025)；PDF p.11，§IV-A2，数据集构造段及式(60)–(61)。
  支持层次：同任务的段落顺序及短搭配：样本构造→网络输出→交叉熵；Shen 为有限星座数据检测，本稿为二元活动分类；不得移植其符号先验、CNN 标签、真后验表述或数据筛选规则。
  已读摘录／定位：`the cross entropy is utilized as the loss function`
- 依据：Menon and Ong (2016)；PDF p.3，§4.2，式(16)–(17)及 logistic-loss 例。
  支持层次：技术陈述：分类概率、训练类先验与密度比；本稿采用 0/1 标签及 logit，并以 (R,v) 为输入。任意有限网络只给出估计；精确关系限于总体风险、无限制 logits 的最优解。
  已读摘录／定位：`Bayes-optimal scorer`

## ch4_cd-P08

段落任务：给出无限制 logits 下总体交叉熵的最优输出。
衔接：准确保留最优性条件，为去除训练先验做准备。

### ch4_cd-P08-S01 · 保留

当前句：
> At the population optimum over unrestricted logits, this loss recovers the training posterior log odds:

斟酌：population optimum 与 unrestricted logits 是精确结论的关键条件，原句精确自然，保留。

- 依据：Menon and Ong (2016)；PDF p.3，§4.2，式(16)–(17)及 logistic-loss 例。
  支持层次：技术陈述：分类概率、训练类先验与密度比；本稿采用 0/1 标签及 logit，并以 (R,v) 为输入。任意有限网络只给出估计；精确关系限于总体风险、无限制 logits 的最优解。
  已读摘录／定位：`Bayes-optimal scorer`

## ch4_cd-P09

段落任务：从 classifier logit 中去除训练先验，代入接收机 Bayes 更新。
衔接：密度比与接收机活动概率通过同一等价公式衔接。

### ch4_cd-P09-S01 · 保留

当前句：
> Subtracting the training prior log odds therefore estimates the log density ratio \cite[Sec.~4.2]{menon2016}.

斟酌：训练先验 log odds 的相减操作、估计性质与 Menon 技术归属准确，保留。

- 依据：Menon and Ong (2016)；PDF p.3，§4.2，式(16)–(17)及 logistic-loss 例。
  支持层次：技术陈述：分类概率、训练类先验与密度比；本稿采用 0/1 标签及 logit，并以 (R,v) 为输入。任意有限网络只给出估计；精确关系限于总体风险、无限制 logits 的最优解。
  已读摘录／定位：`Bayes-optimal scorer`
- 依据：本稿既有活动后验和似然；III-B eq:query-densities/eq:local-activity；IV-D eq:activity-log-odds。
  支持层次：本文公式的等价改写与段落承接；完整先验积分、active/inactive 两假设、rho 的 Bayes 校正均维持原义；此处 log-odds 形式不是 Shen、Ding 的原式。

### ch4_cd-P09-S02 · 修改

原句：
> With $F_k=F_\theta(R_k,v\I_D)$, substitution into \eqref{eq:activity-log-odds} gives the receiver activity probability

改后：
> With $F_k=F_\theta(R_k,v\I_D)$, inserting this estimate into \eqref{eq:activity-log-odds} gives the receiver activity probability

斟酌：补出 substitution 的对象 this estimate，直接承接上一句得到的 log density ratio。

- 依据：本稿既有活动后验和似然；III-B eq:query-densities/eq:local-activity；IV-D eq:activity-log-odds。
  支持层次：本文公式的等价改写与段落承接；完整先验积分、active/inactive 两假设、rho 的 Bayes 校正均维持原义；此处 log-odds 形式不是 Shen、Ding 的原式。
- 依据：Menon and Ong (2016)；PDF p.3，§4.2，式(16)–(17)及 logistic-loss 例。
  支持层次：技术陈述：分类概率、训练类先验与密度比；本稿采用 0/1 标签及 logit，并以 (R,v) 为输入。任意有限网络只给出估计；精确关系限于总体风险、无限制 logits 的最优解。
  已读摘录／定位：`Bayes-optimal scorer`

## ch4_cd-P10

段落任务：定义标准函数并说明 receiver prior 与 learned ratio 的关系。
衔接：结束概率推导，下一段说明输入和训练方式。

### ch4_cd-P10-S01 · 保留

当前句：
> where $\logit a=\log[a/(1-a)]$ and $\sigmoid b=(1+e^{-b})^{-1}$.

斟酌：标准函数定义无需为改写而换写，也不增加新名称。

- 依据：本稿既有 logit/sigmoid 定义；Menon and Ong (2016)；IV-D eq:activity-probability 后；Menon PDF p.3，§4.2 logistic-loss 例。
  支持层次：标准函数与技术对应；现有定义保留；只保留标准 logit 和 sigmoid 定义及本文活动先验校正，不新增学习目标或先验。
  已读摘录／定位：`with the logistic loss`

### ch4_cd-P10-S02 · 保留

当前句：
> The activity prior $\rho$ enters through this Bayes correction, separately from the learned density ratio.

斟酌：准确概括 receiver prior 与 learned ratio 的分工，保留 Bayes 校正并不主张新的技术结论。

- 依据：本稿既有活动后验和似然；III-B eq:query-densities/eq:local-activity；IV-D eq:activity-log-odds。
  支持层次：本文公式的等价改写与段落承接；完整先验积分、active/inactive 两假设、rho 的 Bayes 校正均维持原义；此处 log-odds 形式不是 Shen、Ding 的原式。
- 依据：Menon and Ong (2016)；PDF p.3，§4.2，式(16)–(17)及 logistic-loss 例。
  支持层次：技术陈述：分类概率、训练类先验与密度比；本稿采用 0/1 标签及 logit，并以 (R,v) 为输入。任意有限网络只给出估计；精确关系限于总体风险、无限制 logits 的最优解。
  已读摘录／定位：`Bayes-optimal scorer`

## ch4_cd-P11

段落任务：说明估计特征、分阶段训练、确定性特征的总体关系及最终输出用途。
衔接：与第三章所需近似量对齐，同时交代在线网络固定，不扩展为算法操作清单。

### ch4_cd-P11-S01 · 修改

原句：
> The classifier uses the observation together with $F_k$, so its features include the channel estimate obtained from the learned prior.

改后：
> The classifier takes the observation together with $F_k$ as input, incorporating the channel estimate obtained from the learned prior.

斟酌：采用 Shen 的估计统计量进入检测网络这一关系，保留本文观测和信道均值两类输入，未照搬其符号检测内容。

- 依据：Shen et al. (2025)；PDF p.10，§IV-A1；p.11，§IV-B。
  支持层次：原段关系：由估计结果组成检测网络输入；Shen 将后验均值/不确定性组成符号检测特征；本稿输入为观测及冻结均值映射输出。仅采用关系与表达，不移植模型、性能判断。
  已读摘录／定位：`exploit this statistical information`
- 依据：本稿既有分类训练分布；IV-D eq:classifier-loss 之前；III-B eq:query-densities。
  支持层次：本文定义与相同条件分布的核对；pi_tr=1/2；active 为 H+W、inactive 为 W；W 为白 Gaussian 噪声并独立于 H；两类 v 采用同一采样律。不得改成有色分类训练。

### ch4_cd-P11-S02 · 修改

原句：
> We first train the denoiser and then hold it fixed while training the classifier.

改后：
> The denoiser is trained first and then kept fixed during classifier training.

斟酌：采用 Ding 已核实 kept fixed 搭配叙述先后训练，清楚交代冻结对象；不移植其后续联合解冻。

- 依据：Ding et al. (2026)；PDF p.4，§III-C，分阶段训练首段。
  支持层次：完整搭配和局部训练叙述顺序；Ding 随后还会联合优化既有层；本稿先训 denoiser、再冻结它训 classifier，并在线全部固定。不能把两种训练方案说成相同。
  已读摘录／定位：`with parameters of other layers kept fixed`
- 依据：本稿既有分类训练分布；IV-D eq:classifier-loss 之前；III-B eq:query-densities。
  支持层次：本文定义与相同条件分布的核对；pi_tr=1/2；active 为 H+W、inactive 为 W；W 为白 Gaussian 噪声并独立于 H；两类 v 采用同一采样律。不得改成有色分类训练。

### ch4_cd-P11-S03 · 修改

原句：
> The frozen denoiser output is a deterministic function of $R$ and $v$, which preserves the population relation in \eqref{eq:ideal-logit}.

改后：
> The denoiser output is a deterministic function of $R$ and $v$, so the population relation in \eqref{eq:ideal-logit} remains valid.

斟酌：用 so 说明确定性附加特征与总体关系之间的因果；不将该关系推广为有限网络性能保证。

- 依据：本稿分类器输入与 Menon and Ong (2016) 的总体风险关系；IV-D eq:classifier-loss/eq:ideal-logit；Menon PDF p.3，§4.2式(16)。
  支持层次：本文推论；完整保留 R,v 为分类器输入时，附加它们的确定性函数不会改变条件后验。该确定性特征结论不是 Menon 的原句，且不扩展为有限网络训练必达最优。

### ch4_cd-P11-S04 · 保留

当前句：
> Together, the denoiser, its derivative estimate, and the classifier provide approximations to the channel moments and activity probability required in Section~\ref{sec:joint-denoising}.

斟酌：概括三种计算提供第三章所需近似量，approximation 强度恰当，保留。

- 依据：本稿已建立的均值、方差和活动估计；IV-B–D；III-B sec:joint-denoising。
  支持层次：本文总结与交叉引用；始终写为 approximations；两个训练网络与一个均值导数估计不变；不命名 MFLE/GPJD。

### ch4_cd-P11-S05 · 保留

当前句：
> Both networks remain fixed during online inference.

斟酌：在线网络保持固定是模型条件，短句已清楚，不作无益替换。

- 依据：本稿既有分类训练分布；IV-D eq:classifier-loss 之前；III-B eq:query-densities。
  支持层次：本文定义与相同条件分布的核对；pi_tr=1/2；active 为 H+W、inactive 为 W；W 为白 Gaussian 噪声并独立于 H；两类 v 采用同一采样律。不得改成有色分类训练。
- 依据：本稿既有接收机和实验设置；V sec:overall；VI sec:receiver-settings。
  支持层次：本文交叉引用；保留在线白噪声条件 C=v I_D 及有限差分设置位置，不移植其他文献的接收机。

