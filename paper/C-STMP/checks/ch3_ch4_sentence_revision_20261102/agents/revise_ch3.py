import json
import re
import textwrap
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / 'agents'
input_text = (AGENTS / 'ch3_input.tex').read_text(encoding='utf-8')
paragraphs = [p for p in json.loads((ROOT / 'INPUT_PARAGRAPHS.json').read_text(encoding='utf-8')) if p['group'] == 'ch3']


def norm(s):
    return re.sub(r'\s+', ' ', s).strip()


def sentences(s):
    s = norm(s).replace('Sec.~', 'Sec§~').replace('Secs.~', 'Secs§~')
    return [x.replace('Sec§~', 'Sec.~').replace('Secs§~', 'Secs.~') for x in re.split(r'(?<=[.!?])\s+', s)]


def wrap_sentence(s):
    protected = re.sub(r'\$[^$]*\$', lambda m: m.group().replace(' ', '\ue001'), s)
    return textwrap.fill(protected, width=76, break_long_words=False, break_on_hyphens=False).replace('\ue001', ' ')


# A missing entry means the original sentence has been read and retained.
changes = {
    (1, 2): r'Following the turbo message-passing framework in \cite{cai2026}, we formulate the inference as iterations between linear estimation and joint denoising, as shown in Fig.~\ref{fig:receiver-structure}.',
    (1, 5): r'Information is exchanged between the two estimators through Gaussian extrinsic messages based on expectation propagation \cite{minka2001}.',
    (2, 1): r'The linear estimator receives a Gaussian message from joint denoising.',
    (2, 2): r'This message has mean matrix $\mathbf X^{\rm pri}\in\mathbb C^{KN\times MN}$ and per-column covariance $\gamma\I_{KN}$, with $\gamma>0$.',
    (2, 3): r'For each column, the product of this message and the likelihood in \eqref{eq:working-posterior} gives a Gaussian posterior.',
    (2, 4): r'The posterior mean matrix and per-column covariance are given by \cite[Sec.~III-A]{cai2026}:',
    (3, 1): r'Here, $t_{\rm L}$ is the average posterior variance of the $KN$ coefficients in each column.',
    (3, 2): r'The phase rotations in $\widehat{\mathbf A}$ need not preserve the row orthogonality of the pilot matrix.',
    (3, 3): r'We therefore use the full matrix expressions above; the simplified updates in \cite[Sec.~III-A]{cai2026} require partial orthogonality.',
    (4, 2): r'Dividing this Gaussian approximation by the incoming message removes the information supplied by joint denoising \cite{minka2001}.',
    (6, 2): r'Following \cite[Sec.~III-B]{cai2026}, we first derive the channel estimate under the active hypothesis and the posterior activity probability, and then combine them to estimate $X_k$.',
    (6, 4): r'This Gaussian input message corresponds to the local observation model',
    (7, 1): r'Under the active hypothesis $\alpha_k=1$, \eqref{eq:pseudo-awgn} is an AWGN observation of the channel.',
    (7, 2): r'Combining its likelihood with the prior $q_{\rm tr}$ gives the normalized conditional posterior $\pi_v(dH\mid R)$:',
    (9, 2): r'The conditional mean is the MMSE channel estimate under the active hypothesis, and the covariance describes the corresponding estimation uncertainty.',
    (9, 3): r'These moments are evaluated under the full channel prior, preserving the dependence among the entries of $H_k$ in the posterior calculation.',
    (10, 2): r'Marginalizing the channel under the active hypothesis yields the likelihood $q_{1,v}$, whereas $q_{0,v}$ is the Gaussian noise density under the inactive hypothesis:',
    (12, 1): r'Thus, the posterior activity probability is determined by the two likelihoods and the activity prior.',
    (13, 2): r'The posterior mean and covariance follow by averaging the conditional channel moments over these hypotheses:',
    (15, 1): r'To obtain the spatial covariance, we rearrange $\mu_k$ into $\mathbf U_k\in\mathbb C^{M\times N^2}$, with one row for each antenna.',
    (15, 2): r'Averaging the resulting covariance over the $N^2$ channel positions gives',
    (16, 1): r'The scalar posterior variance is then obtained by averaging its trace over devices and antennas:',
    (17, 1): r'To form the extrinsic message, we use a Gaussian approximation with mean $\widehat X_k$ and common variance $\overline t_X$.',
    (18, 2): r'Its means are collected into $\mathbf X^{\rm pri}$, and $\gamma_{\rm out}$ supplies the input variance for the next linear estimation step.',
    (19, 1): r'The message updates above require the conditional channel moments in \eqref{eq:conditional-channel-integrals} and the activity probability in \eqref{eq:local-activity}.',
    (19, 2): r'With the full channel prior, these integrals generally do not admit closed-form expressions.',
    (19, 3): r'Section~\ref{sec:learning} develops methods for learning approximations to these quantities from channel samples, and Section~\ref{sec:overall} incorporates them into the complete receiver algorithm.',
}

sources = {
    'shen_structure': {
        'literature': 'Shen et al., LEO Satellite-Enabled Random Access with Large Differential Delay and Doppler Shift',
        'location': 'PDF p.5, Section III opening; PDF p.6, III-A, paragraph after (20)',
        'read_excerpt': 'the soft information is exchanged iteratively among them by careful scheduling',
        'support_level_zh': '采用信息在估计部分之间迭代交换的句式与段落任务；并非整句最小替换。',
        'adaptation_boundary_zh': '本文仍只有线性估计与联合去噪；不引入 Shen 的三模块、GAMP、EM、数据检测或逐元素 BGM/MRF 先验。',
    },
    'shen_mean': {
        'literature': 'Shen et al.',
        'location': 'PDF p.7, III-A ending before (21)',
        'read_excerpt': 'obtained as the means of their respective estimated posterior distributions',
        'support_level_zh': '采用由后验均值得到 MMSE 估计的技术叙述关系；协方差与本文活动条件仍来自本文公式。',
        'adaptation_boundary_zh': 'Shen 讨论近似后验下的 H 和 W；本文此处是给定活动状态的完整信道条件后验，不借用其能量检测器。',
    },
    'wei_extrinsic': {
        'literature': 'Wei et al., Learned Score-Based Turbo Message Passing for Channel Recovery From Spatially Compressed Measurements',
        'location': 'PDF p.2, III-B, before (9)-(10); PDF p.3, III-C, after (12)',
        'read_excerpt': 'removes the incoming prior information and generates the prior of Module B',
        'support_level_zh': '采用移除输入信息、把外信息传给另一估计部分的完整搭配与衔接关系。',
        'adaptation_boundary_zh': 'Wei 的可训练展开参数、残差方差和右旋转不变条件均不移植；本文公式仍是现有 EP Gaussian quotient。',
    },
    'wei_mean': {
        'literature': 'Wei et al.',
        'location': 'PDF p.2, III-B, (5)-(8)',
        'read_excerpt': 'the linear MMSE estimate',
        'support_level_zh': '仅核对线性后验估计的术语与公式引出关系，具体全矩阵表达为本文既有公式。',
        'adaptation_boundary_zh': 'Wei 式(6)-(7)要求行正交；不能据此给本文相位旋转后的矩阵套用行正交简式。',
    },
    'cai_structure': {
        'literature': 'Cai et al., arXiv:2506.00581v2',
        'location': 'PDF p.5, Section III opening and III-A',
        'read_excerpt': 'TMP interprets the message updates on the factor graph in Fig. 2 as iterations between two modules',
        'support_level_zh': '保留原有论证结构与归属；文字结合 Shen 的信息交换句式作必要重述。',
        'adaptation_boundary_zh': '本文图为框架图，未照搬 Cai 因子图的节点命名；第三章不引入具体网络模块名称。',
    },
    'cai_gaussian': {
        'literature': 'Cai et al., arXiv:2506.00581v2',
        'location': 'PDF p.5, III-A, (6)-(9); PDF p.6, (10)-(11)',
        'read_excerpt': 'the product of two Gaussian pdfs, which is also a Gaussian pdf',
        'support_level_zh': '相同的 Gaussian likelihood/message 乘积及外信息商关系；维数、矩阵和均值符号按本文既有定义。',
        'adaptation_boundary_zh': 'Cai 的简化线性均值/方差并不直接等于本文全矩阵公式；仅沿用 Gaussian 更新与共享标量方差的理论关系。',
    },
    'cai_scalar': {
        'literature': 'Cai et al., arXiv:2506.00581v2',
        'location': 'PDF p.5, III-A, paragraph before (7); PDF p.7, III-B3, (37)-(38)',
        'read_excerpt': 'a shared scalar variance',
        'support_level_zh': '已有完整术语与由协方差/方差到共享标量的叙述关系。',
        'adaptation_boundary_zh': '本文先保留空间协方差，再对设备和天线平均；平均指标和维数不是 Cai 原式的逐项复制。',
    },
    'cai_channel': {
        'literature': 'Cai et al., arXiv:2506.00581v2',
        'location': 'PDF pp.6-7, III-B1, (16)-(23)',
        'read_excerpt': 'conditioning on the active case',
        'support_level_zh': '相同的活动条件下信道后验、条件矩与 AWGN 去噪任务；不将本文公式冒充 Cai 原式。',
        'adaptation_boundary_zh': '本文以完整 q_tr 表示信道分布，局部 Gaussian 模型为消息近似；不声称实际有限维误差已被证明独立同分布。',
    },
    'cai_channel_activity': {
        'literature': 'Cai et al., arXiv:2506.00581v2',
        'location': 'PDF p.6, III-B opening; PDF p.7, III-B2-3, (28)-(38)',
        'read_excerpt': 'The outputs from these two sub-modules are then combined',
        'support_level_zh': '保留条件信道估计和活动概率分别推导、随后合成联合估计的原有论证基础。',
        'adaptation_boundary_zh': '本文活动后验用完整信道先验的边缘似然；不复用 Cai 的 Gaussian 外信息活动近似公式。',
    },
    'cai_mixture': {
        'literature': 'Cai et al., arXiv:2506.00581v2',
        'location': 'PDF p.7, III-B3, (32)-(38)',
        'read_excerpt': 'the expression inside the Gaussian projection operator is a Bernoulli-Gaussian pdf',
        'support_level_zh': 'Bernoulli-Gaussian 后验近似的术语与从后验计算均值/方差的关系。',
        'adaptation_boundary_zh': '本文先写一般条件矩的恒等式，再作 Gaussian 近似；不把一般恒等式说成以 Gaussian 信道先验为必要条件。',
    },
    'ding_probability': {
        'literature': 'Ding et al., DOI 10.1109/TVT.2026.3729877',
        'location': 'PDF pp.3-4, III-B, Step 3, (14)-(16)',
        'read_excerpt': 'the likelihood ratio between the nonzero and zero components',
        'support_level_zh': '相同的两个假设/混合分量的似然证据与后验概率关系；只借鉴叙述任务。',
        'adaptation_boundary_zh': 'Ding 的非零分量为稀疏系数行；本文为整个设备的活动状态。本文不移植其层次 spike-and-slab 先验、GNN 或后验概率公式。',
    },
    'ding_moments': {
        'literature': 'Ding et al., DOI 10.1109/TVT.2026.3729877',
        'location': 'PDF p.4, III-B, Step 4, (18a)-(18b)',
        'read_excerpt': 'Based on the approximate posterior distribution in (14), an MMSE estimator is employed',
        'support_level_zh': '采用从混合后验到均值/方差的段落任务关系；不整句移植其算法步骤格式。',
        'adaptation_boundary_zh': 'Ding 式(18a)带阻尼且先验为 Gaussian 分量；本文一般条件矩及空间协方差仍是本文既有推导，不引入其逐元素先验。',
    },
    'huang_full': {
        'literature': 'Huang et al., Prior-Agnostic AFDM Channel Estimation',
        'location': 'PDF p.3, III-A, paragraph after (6)',
        'read_excerpt': 'without imposing sparsity assumptions',
        'support_level_zh': '仅辅助核对完整 AFDM 有效信道估计这一技术对象，当前后验依赖性结论来自本文 q_tr 定义。',
        'adaptation_boundary_zh': 'Huang 不提供本文设备活动、协方差或后验因子结构；不能从其完整信道估计措辞推出本文信道元素独立性。',
    },
    'xu_posterior': {
        'literature': 'Xu et al., DOI 10.1109/TCOMM.2025.3628748',
        'location': 'IV-A, printed p.7, before (53); sources/xu_reading.md XU-2',
        'read_excerpt': 'See XU-2 in sources/xu_reading.md (not repeated).',
        'support_level_zh': '采用 Bayes 后验引出句的常规搭配；从后验定义进入矩计算的顺序相近。',
        'adaptation_boundary_zh': '仅已读网页索引文字，未核对原页图像；Xu 是已知信道下有限星座检测，不提供本文条件信道后验公式。',
    },
    'xu_moments': {
        'literature': 'Xu et al., DOI 10.1109/TCOMM.2025.3628748',
        'location': 'IV-B, printed pp.7-8, before (60); sources/xu_reading.md XU-1',
        'read_excerpt': 'See XU-1 in sources/xu_reading.md (not repeated).',
        'support_level_zh': '仅采用均值与协方差的完整搭配及 posterior→moments→cavity 的推导次序。',
        'adaptation_boundary_zh': '本文矩积分、平均尺度及 Gaussian 消息商由本文公式确定，不引入 Xu 的有限星座或逐符号独立假设。',
    },
    'cai_integrals': {
        'literature': 'Cai et al., arXiv:2506.00581v2',
        'location': 'PDF p.7, III-B1, paragraph after (23); PDF p.8, IV opening',
        'read_excerpt': 'due to the complicated and high-dimensional integrals',
        'support_level_zh': '保留一般先验下条件矩积分难计算、转入学习章节的论证关系。',
        'adaptation_boundary_zh': '本文在此还需要活动边缘似然；第三章只指出需求，不提前引入密度比学习或具体网络实现。',
    },
    'own': {
        'literature': 'Current manuscript; existing equations and definitions',
        'location': 'Current Chapter III and referenced Chapter II definitions',
        'read_excerpt': None,
        'support_level_zh': '本文既有定义、假设或直接公式解释；不登记为外文原句，也不据此宣称原创性。',
        'adaptation_boundary_zh': '只检查本句与当前公式相符；不借来源文献补入本文未采用的模型条件。',
    },
}

source_keys = {
    1: [['own'], ['cai_structure','shen_structure'], ['cai_structure','wei_mean'], ['cai_structure'], ['shen_structure','wei_extrinsic']],
    2: [['wei_extrinsic'], ['own','cai_gaussian'], ['cai_gaussian'], ['wei_mean','cai_gaussian']],
    3: [['cai_scalar','own'], ['own'], ['cai_gaussian','wei_mean']],
    4: [['cai_scalar'], ['wei_extrinsic','cai_gaussian'], ['cai_gaussian']],
    5: [['own','cai_channel']],
    6: [['own','cai_channel_activity'], ['cai_channel_activity'], ['own'], ['cai_channel']],
    7: [['cai_channel'], ['xu_posterior','cai_channel','own']],
    8: [['xu_moments','cai_channel']],
    9: [['own'], ['shen_mean','cai_channel'], ['own','huang_full'], ['own']],
    10: [['own','ding_probability'], ['ding_probability','own']],
    11: [['own'], ['xu_posterior','ding_probability','own']],
    12: [['ding_probability','own'], ['own']],
    13: [['own'], ['ding_moments','xu_moments','own']],
    14: [['own','ding_moments'], ['own','cai_mixture'], ['cai_mixture','ding_moments']],
    15: [['own'], ['own']],
    16: [['own','cai_scalar']],
    17: [['cai_mixture','wei_extrinsic'], ['own'], ['wei_extrinsic','cai_gaussian']],
    18: [['own'], ['wei_extrinsic','shen_structure']],
    19: [['own','cai_integrals'], ['cai_integrals'], ['own','cai_integrals']],
}

purposes = {
    1: ('从第二章后验引出线性估计与联合去噪的迭代分工。', '承接观测似然与两类先验；引出两部分之间的信息交换，下一节具体推导线性后验。'),
    2: ('把 Gaussian 输入消息与观测似然相乘，给出线性后验矩。', '落实开篇的线性估计任务；紧接式后解释共享方差及全矩阵适用条件。'),
    3: ('解释平均后验方差及保留全矩阵公式的模型原因。', '承接线性后验式；为下段用平均方差构造 Gaussian 外信息作准备。'),
    4: ('由 Gaussian 后验近似除去输入信息，得到线性外信息。', '先给协方差近似，再给商关系；随后说明按设备重排后的接收对象。'),
    5: ('连接线性外信息矩阵与按设备处理的联合去噪输入。', '将前式的均值和公共方差传至下一节，不加入新算法或网络名称。'),
    6: ('说明 X=αH 的联合后验为何按信道条件矩与活动概率展开。', '承接 Gaussian 外信息，明确局部观察模型；顺次进入信道、活动和联合估计三个小节。'),
    7: ('在活动条件下由 likelihood 与完整信道 prior 构造后验。', '从局部模型限定 α=1；随后对该正规化后验积分得到条件矩。'),
    8: ('引出刚定义的后验的均值与协方差积分。', '公式的被积分分布唯一；下一段解释 MMSE 含义和后续近似符号。'),
    9: ('解释条件矩的估计含义、完整先验依赖性及近似记号。', '承接两项积分，不把完整信道先验改为逐元素因子先验；随后补上尚未确定的活动后验。'),
    10: ('在活动与非活动假设下分别得到观察边缘似然。', '活动情形对信道边缘化、非活动情形只有噪声；给下一段的 Bayes 公式提供两项 likelihood。'),
    11: ('指出活动 likelihood 的正规化作用并给出活动后验。', '把信道后验的积分与活动检验连接起来；后段解释概率意义和 p_k 近似记号。'),
    12: ('解释活动后验依赖两项 likelihood 与活动 prior，并定义近似。', '避免只说观察解释程度而省略 prior；连接随后联合估计对 p_k 的使用。'),
    13: ('对活动状态平均条件矩，得到一般联合均值与协方差。', '合并前两节结果，先给一般恒等式；后段再解释两项协方差并作 Gaussian 近似。'),
    14: ('解释信道与活动两类不确定性，并引入联合混合后验近似。', '不把一般条件矩恒等式等同于 Gaussian 信道假设；为矩阵化空间协方差提供近似矩。'),
    15: ('将按设备的联合协方差表示为空间协方差矩阵。', '先说明 U_k 的重排意义，再对信道位置平均；下一段进一步得到消息传递用的标量。'),
    16: ('由空间协方差的 trace 平均得到共享后验方差。', '承接 C_X,k，保留设备及天线两级平均；为外信息商提供公共方差。'),
    17: ('以联合均值和公共方差形成 Gaussian 近似并计算外信息。', '与线性部分外信息商呼应；使用 b 简写已有方差比，下一段说明回传。'),
    18: ('给出正有限外信息方差条件，并闭合迭代。', '保留 0<b<1 的实际数学条件；把消息重新作为下一轮线性估计输入。'),
    19: ('指出一般先验积分的求解需求并过渡到第四、五章。', '先回顾第三章仍需要计算的量，再指出积分困难；第四章学习这些量、第五章整合接收机。'),
}

reasons = {
    (1, 1): '保留。准确承接第二章后验分解，没有多余技术承诺。',
    (1, 2): '把笼统的 separate their contributions 改为迭代推断关系，使本段先提出论证对象；保留 Cai 框架归属。',
    (1, 3): '保留。输入、目标与线性估计的任务已清楚，无需为换词改写。',
    (1, 4): '保留。两类先验与设备联合信道的关系准确，不能改成 Shen 的逐元素稀疏先验。',
    (1, 5): '把“交换两个估计”改为“交换外信息”，采用 Shen/Wei 对信息流的常用表达；EP 归属仍保留。',
    (2, 1): '以 linear estimator 为主语，直接承接框架图中的估计部分。',
    (2, 2): '将分散的 mean matrix is denoted by 改为一处完整消息参数说明；维数、公共方差和正性条件全部不变。',
    (2, 3): '突出 Gaussian 消息与似然的乘积这一推导依据，保持每列计算条件。',
    (2, 4): '补出 posterior 并用 given by 自然引出公式，避免 corresponding 的泛指。',
    (3, 1): '让 t_L 的定义直接落在平均后验方差，而不是用标量作 averages 的施事。',
    (3, 2): '以 need not preserve 表达原有“可能破坏”条件，不强化成必然不正交；去除 In our model 的重复引导。',
    (3, 3): '让保留全矩阵公式的结论与简式所需条件直接相接，减少否定性辩护口吻。',
    (4, 1): '保留。明确 scalar covariance approximation 的位置和现有引用。',
    (4, 2): '明确作商的是 Gaussian 近似，并采用 Wei 的 removing incoming information 任务表达；不是直接相除原始非 Gaussian 后验。',
    (4, 3): '保留。简洁引出两个外信息参数。',
    (5, 1): '保留。按设备重排是本文维数关系，已有一句足够说明上下节连接。',
    (6, 1): '保留。此等式是分开推导信道与活动后验的直接动机。',
    (6, 2): '将 conditioned on activity 明确为 active hypothesis，并明确 activity probability 是 posterior；次序和 Cai 引用不变。',
    (6, 3): '保留。输入记号在首次使用处就地定义。',
    (6, 4): '用 corresponds to 说明 Gaussian 消息的局部观察解释，避免把有限维真实误差的精确 AWGN 性质作为新结论。',
    (7, 1): '将较拗口的 describes the channel observed 改为直接的 AWGN observation；活动条件仍在句首。',
    (7, 2): '用 combining likelihood with prior 直接引出后验，以 normalized 保留原句积分为一的定义，减少重复解释；Xu 只支持引出方式。',
    (8, 1): '保留。均值与协方差是充分且已核对的固定搭配，无需扩写。',
    (9, 1): '保留。说明积分内 m 的自变量，避免缩写歧义。',
    (9, 2): '将分号关系连成与同一后验对应的均值和协方差，保留 MMSE 条件和不确定性含义。',
    (9, 3): '把 both 的指代明确为 these moments，保持完整先验下的 posterior calculation，不添加元素独立假设。',
    (9, 4): '保留。两个近似符号的定义完整，并且在后文首次使用前给出。',
    (10, 1): '保留。两个活动假设明确，与后面两项密度逐一对应。',
    (10, 2): '采用 marginalizing 的标准概率推导表达，使 active/inactive 两项 likelihood 对称呈现；不是移植 Ding 的具体稀疏行模型。',
    (11, 1): '保留。连接活动边缘 likelihood 与上一节 posterior 正规化，避免两段推导脱节。',
    (11, 2): '保留。Bayes 公式引出已经自然且准确。',
    (12, 1): '把 how well the observation is explained 改为式中明确存在的 likelihood 和 prior，表达更精确而不加技术内容。',
    (12, 2): '保留。给后续联合估计提供近似 p_k，未提前讲密度比实现。',
    (13, 1): '保留。先交代活动条件下的 X_k，再求联合矩，顺序正确。',
    (13, 2): '明确下式给出 posterior mean/covariance，使本节从活动概率自然进入联合矩；conditional moments 包括计算协方差所需的二阶矩。',
    (14, 1): '保留。直观解释一般条件协方差的第一项，不依赖 Gaussian 先验。',
    (14, 2): '保留。解释第二项活动不确定性，原有技术引用不因借鉴表达而更换。',
    (14, 3): '保留。先说明活动条件分量的 Gaussian 近似，再明确联合分布为 Bernoulli--Gaussian；两个层次必要，无需仅为换词改写。',
    (15, 1): '用 rearrange 表明 U_k 是 μ_k 的重排而非新物理量，保持每个天线一行的定义。',
    (15, 2): '补出 resulting，明确此处平均上一段联合后验的协方差而非仅活动条件协方差。',
    (16, 1): '以 scalar posterior variance 为主语，并用 then 承接空间协方差；平均范围完全保留。',
    (17, 1): '把工程式 feedback 改为理论任务 form the extrinsic message，连接前述后验矩与 Gaussian 商。',
    (17, 2): '保留。b 是外信息公式的局部简写，不引入实现截断。',
    (17, 3): '保留。明确与线性部分同一外信息构造，避免再次重复推导。',
    (18, 1): '保留。该条件直接保证下一轮 Gaussian 消息方差有效，不作额外防御扩写。',
    (18, 2): '采用外信息作为下一轮输入的自然衔接，替换抽象的 closes the iteration；参数意义不变。',
    (19, 1): '明确所指是前述 message updates，避免空泛 evaluating these updates；保留两个公式定位。',
    (19, 2): '采用 do not admit closed-form expressions 的数学陈述，保持 generally 的论断强度。',
    (19, 3): '补出 approximations，与 μ_k、t_k、p_k 一致；不把学习估计写成精确恢复一般积分。',
}

review = []
candidate = input_text
paragraph_report = []
for pindex, p in enumerate(paragraphs, 1):
    old_sentences = sentences(p['text'])
    assert len(old_sentences) == len(source_keys[pindex]), (pindex, old_sentences)
    new_sentences = []
    for sindex, old in enumerate(old_sentences, 1):
        new = changes.get((pindex, sindex), old)
        assert (pindex, sindex) in reasons
        new_sentences.append(new)
        review.append({
            'paragraph_id': p['id'],
            'sentence_id': f"{p['id']}-S{sindex:02}",
            'original': old,
            'revised': new,
            'decision': 'retain' if old == new else 'revise',
            'reason_zh': reasons[(pindex, sindex)],
            'paragraph_purpose_zh': purposes[pindex][0],
            'continuity_zh': purposes[pindex][1],
            'source': [sources[key] for key in source_keys[pindex][sindex-1]],
        })
    replacement = '\n'.join(wrap_sentence(s) for s in new_sentences)
    assert candidate.count(p['text']) == 1, p['id']
    candidate = candidate.replace(p['text'], replacement, 1)
    assert Counter(re.findall(r'\$[^$]*\$', p['text'])) == Counter(re.findall(r'\$[^$]*\$', replacement)), p['id']
    paragraph_report.append({
        'paragraph_id': p['id'],
        'purpose_zh': purposes[pindex][0],
        'continuity_zh': purposes[pindex][1],
        'sentence_count': len(old_sentences),
        'revised_count': sum(a != b for a,b in zip(old_sentences,new_sentences)),
    })

blocks_re = re.compile(r'\\begin\{(figure|align|equation)\}.*?\\end\{\1\}', re.S)
old_blocks = [m.group() for m in blocks_re.finditer(input_text)]
new_blocks = [m.group() for m in blocks_re.finditer(candidate)]
assert old_blocks == new_blocks
headings_re = re.compile(r'\\(?:section|subsection|subsubsection)\{[^}]+\}')
assert headings_re.findall(input_text) == headings_re.findall(candidate)
labels_re = re.compile(r'\\label\{[^}]+\}')
assert labels_re.findall(input_text) == labels_re.findall(candidate)
citations_re = re.compile(r'\\cite(?:\[[^\]]*\])*\{[^}]+\}')
assert Counter(citations_re.findall(input_text)) == Counter(citations_re.findall(candidate))
assert not re.search(r'\b(MFLE|GPJD)\b', candidate)

(AGENTS / 'ch3_proposed.tex').write_text(candidate, encoding='utf-8')
(AGENTS / 'ch3_review.json').write_text(json.dumps(review, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
(AGENTS / 'ch3_paragraphs.json').write_text(json.dumps(paragraph_report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
summary = {
    'paragraphs': len(paragraphs),
    'sentence_units': len(review),
    'revised': sum(r['decision']=='revise' for r in review),
    'retained': sum(r['decision']=='retain' for r in review),
    'protected_blocks': len(old_blocks),
    'math_figure_blocks_exact': old_blocks == new_blocks,
    'inline_math_multiset_per_paragraph_unchanged': True,
    'headings_unchanged': True,
    'labels_unchanged': True,
    'citations_unchanged': True,
    'new_module_names': False,
    'official_section_edited': False,
    'scope_note_zh': '逐句人工审读，19个文字单元全部记录；其中包括以公式结尾的引出句。使用同任务文献搭配与句式，不宣称每句都是外文原句的最小替换。',
}
(AGENTS / 'ch3_validation.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps(summary, ensure_ascii=False, indent=2))
