# 专业表达与句型语料

2026-10-18：按作者偏好，当前修订优先采用[原文句式依据](corpus_sentence_patterns.md)中已定位的通用句式。下表保留此前的论证功能分类，实际落笔以原文同类表达为先。

来源定位见每个ID对应的[文献卡](style_cards)与[清单](corpus_manifest.md)。下列骨架及示例为本稿重新编写的表达，不是原文整句摘录；方括号表示应替换的数学对象。每项写的是可复用论证功能，不机械重复固定开头。

| 功能 | 可复用句型（自拟骨架） | 本稿使用示例 | 依据 |
|---|---|---|---|
| 建立通信场景 | We consider [link] with [terminals/receiver]. | We consider a grant-free uplink from K single-antenna terminals to a LEO satellite. | C02 II；C08 II-A；C10 II-A |
| 引入符号与维度 | Let [symbol] denote [quantity], where [index/dimension]. | Let D=MN² denote the number of complex channel coefficients per terminal. | C07 III-A；C10 II-C |
| 把结构写成模型条件 | Under [physical condition], [quantity] is shared by [components]. | All paths of a terminal share a spatial response and a Doppler shift. | C10 II-B/C；C05 II-A |
| 从逐样本到矩阵 | Stacking [observations] gives [matrix equation]. | Stacking the pilot observations gives Y=AX+W. | C08 III首段(11)；C10 II/III |
| 明确恢复对象 | Given [observations and known quantities], the receiver estimates [unknowns]. | Given Y, A, σ², and ρ, the receiver estimates the effective channels and activities. | C05 II-C；C08 III |
| 定义后验均值 | The MMSE estimate is the conditional mean [formula]. | The target estimate is the mean under the working posterior. | C08 III-B(13)；C09 III-C(19) |
| 给模块接口 | The [module] takes [input] and returns [statistics]. | The nonlinear estimator takes a Gaussian query and returns channel and activity moments. | C01 III；C06 III-C |
| 引出条件更新 | Conditioning [distribution] on [observation] yields [equation]. | Gaussian conditioning yields the linear estimate and covariance. | C01 III-A；C11 IV-A/B |
| 高斯外信息 | Dividing [posterior approximation] by [incoming message] gives [output]. | Dividing out the incoming Gaussian message gives the extrinsic query. | C01 III；Minka技术来源 |
| 解释混合矩 | The first term accounts for [effect], and the second for [effect]. | The second covariance term accounts for uncertain activity. | C01 III-B；C09 III-C |
| 指定学习对象 | We parameterize [target function] by [network] and minimize [loss]. | We parameterize the perturbed channel score by Sθ. | C03 III-A；C12 §4.1 |
| 把恒等式转成损失 | Using [identity], [objective] can be written as [equivalent form]. | The trace loss can be written as regression on the denoising error. | C01 IV；C13 §4.2 |
| 区分有限与理想目标 | For fixed [estimator], the minimizer is [conditional statistic]. | For fixed Fθ, the optimal scalar readout is its conditional mean squared error. | C13 Theorem4.1/Corollary4.2；本项目推导 |
| 简短证明最优解 | Differentiating the conditional risk with respect to [variable] gives [equation]. | The derivative of the conditional BCE risk is sigmoid(z)−ηtr. | C14 §3/4.2；本项目直接推导 |
| 说明先验修正 | Subtracting [training odds] and adding [target odds] yields [probability]. | The training class prior is removed before incorporating the access prior. | C14 §3(6)–(8) |
| 安排离线训练 | We first train [module], then fix its parameters while training [dependent module]. | The channel mean network is fixed when training the error network and activity classifier. | C01 IV-C；C03 III；C13 §5.1 |
| 表达停止规则 | Iteration stops when [statistics] satisfy [criterion] for [window]. | Iteration stops after estimate, message, and decision stability persist. | C08 Algorithm1；C01 V |
| 解释复杂度 | The dominant cost is [operation], requiring O([dimensions]) operations. | Multiplication by the effective pilot operator costs O(QKMN²). | C04 V-E；C06 IV-B；本实现计数 |

## 使用原则

保留标准词：posterior mean、conditional covariance、extrinsic message、denoising score matching、density ratio、binary cross-entropy、damping、computational complexity。具体出处和本稿含义见术语表。对本文自定义的共享误差平均、支持区间接受规则、停止统计量直接给公式和功能；不额外命名算法或缩写。

必要限定句只出现在首次定义处；不把每段写成“不是……而是……”。避免 repeatedly using in this section、it is worth noting、it should be emphasized、comprehensive framework、seamlessly integrates 等填充表达。结果未完成前，方法章不使用性能优越性陈述。

