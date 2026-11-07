# STMP 论文下载后的阅读与可借鉴环节

日期：2026-10-24。配套：[全文索引](../../../reference/reviews/stmp_message_awgn_review_20261024/README.md)、[逐文件下载记录](../../../reference/reviews/stmp_message_awgn_review_20261024/DOWNLOAD_MANIFEST.json)、[修订后的调研](STMP_MESSAGE_AWGN_REVIEW_20261024.md)。

**判断：最值得继续设计的是 D-GEC 的成套消息接口与独立有色噪声条件训练。OAMP-MMV 可帮助明确消息增益和协方差，但不能直接给现有 STMP 加一个矩阵修正就获得保证。FIRE、完整矩阵 Onsager、简单历史融合已有本项目负结果，应先解释这些失败，再提出有实质区别的候选。**

这是相关方法、假设、公式和实验段落的定向细读，不是对全部附录逐页审稿。下载版、核读范围、页码及具体操作分别记录于四份笔记：[基础与展开](../../../reference/reviews/stmp_message_awgn_review_20261024/notes/download_followup_foundations.md)、[有色噪声](../../../reference/reviews/stmp_message_awgn_review_20261024/notes/download_followup_colored.md)、[MMV 与活动](../../../reference/reviews/stmp_message_awgn_review_20261024/notes/download_followup_mmv.md)、[记忆与正交化](../../../reference/reviews/stmp_message_awgn_review_20261024/notes/download_followup_memory.md)。本轮只下载、阅读及核对既有代码/结果，没有训练、批量实验或算法修改。

## 1 对上一轮建议的补充纠正

重新查阅迁移后的历史目录发现，上一轮对已试方法的覆盖不完整。下面三项不能再当作尚未尝试的直接修复。历史权重和当前冻结模型不同，不能将旧失败当作当前版本所有实现必然失败的证明。

| 已做过的工作 | 历史证据 | 对下一步的限制 |
|---|---|---|
| 完整复数 \(256\times256\) 矩阵 Onsager，含 \(p(r)\mu(r)\) 的活动概率导数、跨列依赖 | [2026-10-15 完整 AMP 报告](../../../archive/result_legacy_20261023/layout_20261021/before/docs/history/results/proposed_amp_20261015/REPORT.md)：四个开发条件均在 1–2 个有效迭代后超出方差支持；首轮判全部 40 用户活跃，四条件合计 142 个虚警 | “从标量换成矩阵 Jacobian”本身已做过。OAMP-MMV 的增益/协方差联合表示与其不同，但需要写出完整接口，不能仅换名称 |
| 完整 FIRE 适配与 DD-VAMP；不只是一次 oracle 补噪 | [2026-10-14 报告](../../../archive/result_legacy_20261023/layout_20261021/before/docs/history/results/proposed_uniform_inference_20261014/REPORT.md)：FIRE 残差型多次支持超界；二阶网络方差替代可产生近零输出；DD-VAMP 亦有失败 | 先检查 posterior 与 extrinsic 是否混用、方差估计和观测噪声依赖；原样补噪/改阻尼没有新增依据 |
| 最近三轮的公开残差融合及误差协方差分解 | [2026-10-15 历史协方差报告](../../../archive/result_legacy_20261023/layout_20261021/before/docs/history/results/proposed_memory_requirements_20261015/REPORT.md)：26 个相关窗口中 14 个真实反馈 MSE 上升，最大 +4.1703 dB；最大权重范数约 \(1.16\times10^5\) | 误差不只来自矩阵求逆；残差目标会受反馈—观测噪声相关影响。该试验是离线融合，**不是完整 MAMP 的否定实验** |

最新冻结模型的查询诊断仍支持“标量误差功率不是充分描述”：失败富集样本中 13 个 −4 dB 漏检用户，即便换成实测 MSE 标签仍为 0/13，而同信道重新抽 AWGN 的两类功率匹配分支各为 97/104。它同时改变了多项误差属性，并有失败筛选和重新抽噪的影响；不能把这个差异全归因于有色协方差。[原始检查](../../../result/snr_comparison/data/low_snr_query_check_20261024/REPORT.json)

## 2 最值得参考：D-GEC 的成套接口

[D-GEC，PDF pp.11–16](../../../reference/literature/shastri2022_dgec.pdf) §III-A/B、式(28)–(41)、Algorithm 2，处理的是**分组精度、分组 Jacobian、对应线性估计和有色噪声去噪器的整体配合**。

把其标量组内操作写为

\[
\alpha_{i,g}=\frac{1}{d_g}\operatorname{tr}J_{f_i,gg},\qquad
\eta_{i,g}=\frac{\gamma_{i,g}}{\alpha_{i,g}},\qquad
\gamma_{j,g}=\eta_{i,g}-\gamma_{i,g},
\]
\[
r_{j,g}=\frac{f_i(r_i)_g-\alpha_{i,g}r_{i,g}}{1-\alpha_{i,g}}.
\]

这里 \(g\) 是组，\(\gamma\) 是精度，不能与当前阻尼参数混淆。这些式子明确了该配套设计，不表示它们在任意失配网络下均有正精度或收敛保证。

当前接口的对应位置是：

| 当前代码 | 当前行为 | 真正借鉴时要改变什么 |
|---|---|---|
| [denoiser.py](../../../src/algorithm/STMP/denoiser.py) | 要求各向同性 cavity；三网络基本条件量是一个 \(v\) | 给完整非线性模块一个已定义的结构化噪声模型，而非只把输入 \(v\) 改成向量 |
| [moments.py](../../../src/algorithm/STMP/moments.py) 与 denoiser | 二阶输出先平均，再跨用户平均 | 区分条件风险、后验中心协方差和完整均值映射 Jacobian；不能继续把同一标量用于所有用途 |
| [iterations.py](../../../src/algorithm/STMP/iterations.py) | 用户空间矩先共享，冻结配置再作迹投影 | 分组信息需在来回两方向保留；逐用户平均功率与用户内天线相关是不同层次 |
| [linear.py](../../../src/algorithm/STMP/linear.py) | 支持共享的 \(16\times16\) 天线协方差 | 根据选定协方差结构重新匹配线性模块；目前不支持任意用户、坐标分组精度 |
| [gaussian.py](../../../src/algorithm/STMP/gaussian.py) | 由矩代理进行 Gaussian 外信息除法 | 明确采用矩匹配还是实际映射的分组灵敏度，并核对两者的一致性 |

MRI 的小波分组不能直接移植为 AFDM 的任意分组。应先确认实际误差可由哪一种低维协方差描述。D-GEC 式(36)后的 Gaussian 性依据是实验，原文明确严格分析有待研究；我们也不能把它作为固定 AFDM 的定理。

## 3 corr+corr 可以保留模块化训练，但三个输出都要匹配

D-GEC §III-B 的 **corr+corr** 将带噪信号与独立的同协方差噪声样本共同送入去噪器；D-VDAMP §2.3 则把各子带标准差作为网络条件。这两者都不是保持原 AWGN 权重完全不变。

针对本项目，可以研究以下**候选训练任务**，它不是原文已经给出的 JADCE 算法：

\[
C\sim q(C),\qquad r=aH+n,\qquad
n,n_{\rm aux}\mid C\stackrel{\rm ind}{\sim}\mathcal{CN}(0,C).
\]

正负类使用相同的 \(C\) 分布，分别学习信道条件均值、活动概率及所需不确定性/灵敏度。各轮可以共享同一模块，训练数据可以直接由干净信道和合成 Gaussian 噪声生成，因此与固定十层轨迹上的联合微调仍是两条路线。

需要先解决的实际问题有三个：

1. 当前失配是否主要能由 \(C\) 表示？若存在条件均值偏差、信号方向收缩或非 Gaussian 干扰，仅提供 \(C\) 不够。
2. 部署时 \(\widehat C\) 如何由公开输入获得？若由查询或活动反馈估计，它可能携带活动信息；独立抽 \(C\) 的训练未自动匹配真实联合分布。
3. 后验矩与外信息如何一致？当前第二网络的标量风险不是完整矩阵 Jacobian。可沿 D-GEC 使用实际完整映射的分组导数，或另行定义矩学习目标；不能两者混用而不检查。

对活动检测，[Djelouat 2021，p.3 式(8)–(11)](../../../reference/literature/djelouat2021_correlated_amp.pdf) 提供了直接启发：Gaussian 活跃先验协方差 \(R_k\) 与查询噪声协方差 \(C\) 共同进入证据，

\[
\operatorname{logit}p_k=\operatorname{logit}\rho
-\log\det(I+C^{-1}R_k)
+r_k^H[C^{-1}-(C+R_k)^{-1}]r_k .
\]

因此 trace 相同的两种噪声可能给出不同的活动概率。但我们的物理信道先验不是这个 Gaussian 模型；该公式适合作机制参考或明确标记的参数模型对照，不应直接替换冻结分类器后宣称正确。

## 4 OAMP-MMV 值得借鉴的是“增益与协方差一起记”

[OAMP-MMV，pp.5–6](../../../reference/literature/cheng2023_oamp_mmv.pdf) 式(15)–(18)、(28)–(34) 用

\[
\widehat X=X\Theta+Z
\]

区分矩阵信号增益 \(\Theta\) 和误差 \(Z\)。矩阵 Gram–Schmidt 修正后，输出增益一般并非单位矩阵。若要送给当前单位增益 AWGN 网络，需要额外归一化并变换协方差；近奇异增益会放大噪声。这不是将矩阵散度直接送入现有 Gaussian 外信息函数。

当前 pack 后 \(X\) 是 \(640\times256\)，256 列包含 16 个天线坐标与 16 个信道行坐标 \(n_r\)；当前共享天线协方差则是 \(16\times16\)。论文的列间矩阵、物理天线矩阵、用户块矩阵不能混作一个对象。只用 \(16\times256\) 观测残差按行估计完整列协方差，其秩至多 16。

还有一个本项目特有的代数限制：每用户 \(A_k\in\mathbb C^{16\times16}\)。**若它满秩**，要求线性处理对本用户全块无偏 \(L_kA_k=I\)，则必有 \(L_k=A_k^{-1}\)，均值成为

\[
r_k=A_k^{-1}\left(y-\sum_{j\ne k}A_jm_j\right).
\]

在这个特例，干扰协方差权重不再改变该线性均值，只影响误差统计及后续推断；病态 \(A_k\) 还会放大噪声。这个推导不表示已经检查所有实际块满秩或条件数，也不表示不能改善干扰消除。它说明不能预先承诺“矩阵 LMMSE 加全块去偏”一定优于现有迹归一化。

## 5 FIRE 最需要参考的是适用对象和假设

[FIRE，pp.4–6](../../../reference/literature/bendel2025_fire.pdf) 式(11)、(14)–(15) 对 **Gaussian 后验线性估计** 补噪。用复数记号写为

\[
K=\nu A^H(\nu AA^H+\sigma_y^2I)^{-1},\qquad
\widehat x=\bar x+K(y-A\bar x),\qquad
C_{\rm post}=(A^HA/\sigma_y^2+I/\nu)^{-1}.
\]

它再加独立噪声 \(c\sim\mathcal{CN}(0,\tau I-C_{\rm post})\)，要求补噪协方差半正定。相比之下，当前 isotropic STMP 的外信息查询是

\[
r_{\rm ext}=\bar x+\frac{K}{\phi}(y-A\bar x),\qquad
\phi=\operatorname{tr}(KA)/d.
\]

**两者均值与误差协方差都不同，不能直接把 FIRE 的 \(C_{\rm post}\) 当作 STMP 外信息误差协方差。** 在 FIRE 的工作模型中，\(\bar x-x\) 为各向同性 Gaussian，且独立于观测噪声。实际重复使用同一个 \(y\) 后，误差协方差一般还含反馈与观测噪声的交叉项；条件偏差也不能靠独立零均值补噪去掉。

旧 FIRE 适配某个开发条件的初轮 MSE/标签约 0.991、空间二阶矩最大特征值占比约 0.068，表面已接近 \(1/16\)，却有误差沿信号投影约 −0.971，随后趋于近零输出。这直接提醒我们检查信号相关性，不能只看“白”与“方差对”。该数值来自旧权重小样本，不能代替当前冻结模型的验证。

另一个文献反例是 [D-VDAMP，p.4 Table 2](../../../reference/literature/metzler2020_dvdamp.pdf)：1/8 采样、5 dB 测量 SNR 下其 PSNR 为 25.0 dB，而 PnP-ADMM(BM3D) 为 27.8 dB；作者解释密度补偿会放大噪声。这是 MRI 结果，不能外推数值，但清楚说明**更符合误差模型不保证低 SNR 性能更好**。

## 6 Memory AMP 与展开各能提供什么

[SS-MAMP，p.8 式(40)](../../../reference/literature/liu2023_ssmamp.pdf) 的典型充分统计量融合权重为

\[
w=\frac{V^{-1}\mathbf1}{\mathbf1^HV^{-1}\mathbf1}.
\]

这里 \(V\) 是符合其模型的跨轮误差协方差。它不是“从观测残差估一个 Gram 矩阵就可用”的通用保证；奇异情形、原始 MAMP 正交条件及估计偏差都需处理。当前历史负结果已经指出公开残差估计的交叉项问题，因此该方向暂不优先。

[LDAMP，pp.5–7](../../../reference/literature/metzler2017_ldamp.pdf) 明确区分端到端、逐层、独立去噪器三类训练；[L-STMP，pp.2–3](../../../reference/literature/wei_yuan_2026_lstmp_v1.pdf) 进一步训练层内校准量和 score 权重。可以参考其逐步加层与多层辅助损失，但 L-STMP 是单用户 NMSE 目标，式(6)还要求行正交观测，不能原样搬成当前 JADCE 的检测方案。

十层展开继续处理实际有限层推断的联合适配；模块化 STMP 可以处理可描述的条件噪声族及消息一致性。二者可以共享预训练先验，但不需要有相同训练数据生成方式和优化目标。

## 7 阅读顺序与下一步范围

建议先读 **D-GEC → Djelouat 相关信道 AMP → OAMP-MMV → FIRE**，然后用 D-Turbo-CS、MAMP/SS-MAMP、LDAMP/L-STMP 对照外信息、历史关系和训练目标。其余论文用于核对前提与边界。

下一步若继续研究，应先用现有冻结查询及独立样本比较条件偏差、中心协方差、信号依赖和跨轮依赖，判断哪一种模型能解释失配。只有协方差模型得到支持后，再设计有色条件模块；若主要是单位响应或条件偏差问题，单独扩展 \(C\) 不充分。这里没有承诺任一路线已能恢复当前漏检。

本笔记由 AI 辅助查阅和整理。文献结论、项目代数推导、历史观察与待验证建议在文中分别标记；未增加实验结果或将他人 MRI/随机导频结果当成 AFDM 性能证明。术语定位同步记录于 [TERMINOLOGY.md](TERMINOLOGY.md)。
