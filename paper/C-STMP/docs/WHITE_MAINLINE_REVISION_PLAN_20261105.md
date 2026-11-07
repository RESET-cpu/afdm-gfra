# 白噪声版本作为主方法时的论文修订建议

## 2026-11-05 最新讨论：先验、去噪器、方差的数学衔接

**已采用：** 作者随后逐字确认中文三句，要求“就用这个吧”。已同步到中英文摘要和引言第二项贡献；第一、第三点保持，两版 PDF 已更新。下文“候选／尚未写入”保留讨论时点含义，现以[采用记录](../checks/second_contribution_adopted_20261105/README.md)为准。

作者在上一轮修改后进一步指出，第二点应按“学习信道先验 → 去噪器 → 通过数学关系计算方差 → 一、二阶得分模型的训练依赖与额外开销”组织。本轮核对原文后形成以下候选，尚未写入 TeX/PDF；其优先级高于下文旧候选和上一轮将“不确定性量化”作为主要衔接的写法。

> We learn a score-based generative channel prior directly from multiantenna AFDM effective-channel samples with fractional delays and Doppler shifts, without imposing sparse or grid-aligned channel assumptions. Using Tweedie's formula to relate the score function to the posterior mean, we construct a channel denoiser based on the learned prior. We then exploit the relation between conditional-mean derivatives and posterior covariance to estimate the average posterior variance required for message passing. This avoids the dependence of second-order score learning on first-order score estimates and the additional training and storage required by a separate second-order model.

来源与适用范围：Huang 期刊版引言贡献 (i)，PDF p.1／印刷 p.2949，支持直接学习 AFDM 有效信道及避免稀疏网格假设；Cai v2 §IV-A、式 (44)、PDF p.8，明确 Tweedie's formula 对得分函数与 MMSE 去噪的联系；Dytso 正式版 §III Proposition 1、式 (17)、PDF p.3／印刷 p.1885，以及 Manor–Michaeli §3.2／式 (11)、PDF pp.4–5，支持条件均值导数与后验协方差关系。Cai v2 §IV-C、式 (52)–(54)、PDF p.9，支持二阶训练目标依赖一阶得分估计的具体含义。

“耦合”只作为上述训练依赖的中文解释，不另造方法名称，也不暗示蔡文必须联合反向传播；蔡文允许顺序训练或同时训练并阻断二阶目标到一阶网络的梯度。“额外开销”限定为独立二阶模型的训练和参数存储，不泛化为整体训练量、总参数量或推理耗时已减少。去噪器导数仍需额外前向调用。该顺序是论述逻辑，不表示本文先训练得分网络再另训去噪器；实际实现仍采用第四章的等价去噪参数化与训练目标。核心数学关系沿用文献，不写为本文新定理。

**最新状态（2026-11-05）：** 作者在阶段性配对比较后授权开始修改正文。本轮已修改摘要、引言相关动机和第二项贡献、第四至第五章及结论，并同步训练设置和实验归属；第二、三章及引言第一、第三项贡献保持。下文“仅讨论”“尚未修改”等均为此前阶段记录。白噪声 1000 场景实验仍在运行，既有有色图表未替换，冻结主线未切换。见[实施与核验](../checks/white_mainline_revision_20261105/README.md)。

日期：2026-11-05。作者要求提前考虑有色训练退出主线后正文的修改位置和写法。本文件是候选修订清单，尚未修改论文正文、公式、图表或模型绑定；默认保留现有标量消息接口。是否正式采用白噪声版本，等待同结构、同精度、每档 1000 场景的对照完成后决定。

本次沿用[已确认的条件性论述方案](REVIEW_DECISIONS.md#colored-training-null-gain-20261104)，以及[写作规范](WRITING_GUIDE.md)和[术语依据](TERMINOLOGY.md)。这是作者主动要求的主线调整分析，不重新评判已经处理完毕的语言问题。

## 作者最新限定 本轮只讨论引言第二项贡献

作者随后明确：摘要及引言第一、第三项贡献不用动，重点是结合 Huang 和 Cai 的表述重写第二项，说明本文如何省去 Cai 的一、二阶网络配套训练。此要求覆盖下文旧清单的本轮执行范围。旧的逐章建议仅作为历史候选保留，不再作为摘要或第一、第三项贡献的修改任务；当前 TeX 和 PDF 仍未改动。

建议第二项依次承担三个任务：直接学习多天线 AFDM 有效信道；由同一个条件均值去噪器及其输入导数获得均值和近似方差；说明由此省去独立二阶得分网络及其依赖一阶估计构造目标的训练。

Huang 的依据为[期刊原文](../../../reference/literature/huang2026.pdf)：摘要和引言贡献 (i)，印刷 p.2949；§III-A，式 (7)，印刷 p.2951，直接对 AFDM 有效信道进行得分学习，避免预设稀疏或网格对齐的信道假设。§III-B，式 (8)–(10) 使用后验采样进行信道估计。本文继承前一种学习对象和动机，将其用于多天线、多帧 JADCE；不能把 Huang 已有的直接有效信道学习本身重新宣称为本文首创。

Cai 的依据为 [v2 §IV-A–C，式 (44)–(54)](https://arxiv.org/html/2506.00581v2#S4)：分别学习一、二阶得分以计算均值和方差；式 (52)–(53) 的二阶监督使用已学习的一阶得分输出。式 (54) 后允许先固定一阶网络再训练二阶网络，也允许同时训练但阻断二阶目标向一阶网络反向传播。因此可以说二阶训练依赖一阶估计，不能说原算法强制采用唯一的串行训练流程。

第二项候选英文如下，尚未写入稿件：

> We learn a score-based generative prior directly from multiantenna AFDM effective-channel samples with fractional delays and Doppler shifts, without imposing sparse or grid-aligned channel assumptions. We parameterize the learned model as a conditional-mean denoiser and approximate the average posterior variance required for message passing from its input derivatives. This construction removes the need to train a separate second-order score network using targets derived from a first-order score estimate.

第一句沿用现稿学习对象和 Huang 的论述含义；第二句是本实现对均值导数恒等式的使用；第三句针对 Cai 的具体训练依赖。相关引用可分别接在学习对象、导数恒等式和 Cai 对照处，不将整段称为任何一篇文献原段的直接替换。

这里省去的是信道均值/方差部分的第二个网络；活动密度比分类器继续存在。均值网络自身的输入导数误差仍会影响方差近似，因此不扩写为消除一阶误差传播、保证后验一致性或必然提高精度和速度。该设计差别不依赖有色训练，是否有额外性能收益则由对应实验说明。

## 修改范围和主要判断

需要区分两个选择。仅降低有色训练的贡献地位，可以继续如实报告使用有色权重的既有实验；如果把白噪声训练版本 GP-MP 设为正文默认方法，就必须同时调整训练说明、公式记号、权重对应关系和实验归属。下面按第二种选择给出完整清单，第一种选择只采用其中的动机和贡献修改，不把历史训练事实改成白噪声。

建议保留的研究主线是：多帧 AFDM 有效信道建模；学习条件均值并由其输入导数构造平均后验方差反馈；学习活动与非活动假设的密度比，将这些量纳入消息传递完成 JADCE。系统建模仍是第一项贡献。方差恒等式和密度比学习有既有文献来源，贡献应落在接收机的具体构造、整合和验证。

RefineNet 骨干沿用已有结构。与 STMP 的设计差别应具体写成均值输出参数化、预条件、导数方差计算和接收机更新，避免将其笼统称为新网络架构。省去独立二阶网络意味着减少对应训练和参数存储；有限差分仍需额外去噪器调用，不能据此直接宣称推理更快或估计更准。密度比的收益由独立活动消融支持；当前 STMP 适配基线也含密度比分类器，其整机差距不能再次全部归因于这一模块。

## 按正文位置修改

行号对应本次读取的现稿；正式修改时以段落和公式标签为准。

| 位置 | 现稿内容 | 建议修改 |
|---|---|---|
| [题目、关键词](../main.tex:33) | 标题为生成模型辅助的 GNSS-independent MIMO-AFDM GFRA，未以有色训练命名 | 保留。无需为了切换训练扰动重写题目或系统定位。 |
| [英文摘要](../main.tex:57)及[中文摘要](../sections/00_abstract_zh.md) | 用有限维误差失配引出有色协方差训练 | 删除这条因果叙述，补入同一个条件均值网络提供均值、通过输入导数近似方差的说明；保留多帧模型、两个模块、密度比活动估计。候选句见下文。 |
| [引言 STMP 段](../sections/01_introduction.tex:77) | 从白噪声假设局限直接转向有色训练动机 | 保留对 STMP 一、二阶网络的客观介绍；将重点转为如何提供每轮所需的信道矩和活动证据。有限维 AWGN 近似局限可在第三章近似说明处简短保留，不再作为本文通过有色训练解决的问题。 |
| [贡献第 1 项](../sections/01_introduction.tex:101) | 多帧 AFDM、固定有效信道维度、帧间相位 | 保留。它不依赖训练噪声的颜色。 |
| [贡献第 2 项](../sections/01_introduction.tex:110) | 学习有效信道先验，并以有色噪声缓解失配 | 保留直接学习有效信道的前半部分；后半部分改为条件均值输出及导数方差反馈，明确不训练独立二阶网络。 |
| [贡献第 3 项](../sections/01_introduction.tex:117) | MFLE/GPJD、密度比、整机性能 | 保留接收机集成和密度比；最终性能句以白噪声版本实际完成的实验范围重写。不能提前沿用全部导频和跨信道结论。 |
| [第二章](../sections/02_system_model.tex) | AFDM 系统、物理噪声、有效信道、后验模型 | 保留。本次不改变物理噪声，也不改变相位和信道模型。 |
| [第三章线性估计](../sections/03_bayesian_receiver_design.tex:25) | 完整线性后验协方差及迹平均、标量外信息 | 保留，包括 `eq:linear-variance` 中的矩阵协方差。退出有色训练不等于删除全部协方差公式；标量化是消息近似。 |
| [第三章联合估计](../sections/03_bayesian_receiver_design.tex:62) | 局部 AWGN 模型、活动密度、混合矩、标量反馈 | 保留。天线后验协方差 `eq:joint-spatial-covariance` 仍有用途，与训练协方差 C 是不同对象。 |
| [第四章 A](../sections/04_generative_priors.tex:12) | 一般 C 和实协方差 Sigma 下的 Tweedie 关系 | 正文直接采用 C=vI、Sigma=(v/2)I；均值和方差关系仍保留，简化为下文的标量噪声形式。一般矩阵表达可留在既有内部推导中。 |
| [第四章 B](../sections/04_generative_priors.tex:61) | 协方差加权得分匹配、均值输出训练、有色因子采样 | 将网络条件写为 v，保留与得分匹配的关系；损失保留实际的 1/v 权重。删除正文中的随机相关因子训练段，将有色采样设置移至训练噪声消融说明。 |
| [第四章 C](../sections/04_generative_priors.tex:113) | 条件均值导数、随机方向中央差分 | 保留并作为关键设计展开。保留原随机方向的 sqrt(v/2) 缩放和差分步长定义，避免文字简化引入不同的数值估计器。 |
| [第四章 D](../sections/04_generative_priors.tex:149) | 白噪声查询下的分类密度比、先验修正 | 原理和训练类别构造保留；仅将 F(R,vI) 统一简写为 F(R,v)，并绑定白噪声去噪器对应的分类器。 |
| [第五章名称及图 3](../sections/05_overall_algorithm.tex:7) | CGP-MP 为主，GP-MP 为白噪声变体；图注强调有色训练 | 若正式切换，GP-MP 成为主方法，CGP-MP 留作有色训练消融。MFLE/GPJD 名称保留。图 3 使用的实际去噪样例须注明模型，或换成白噪声版本的已保存样例。 |
| [第五章算法及实现](../sections/05_overall_algorithm.tex:26) | 标量 site、混合矩、局部方差更新、阻尼、SVD 和复杂度 | 更新网络记号与算法名；推断步骤保持。复杂度中的 1+2L_z 次去噪器调用继续保留，不能改成每轮只调用一次网络。 |
| [第六章网络条件和预条件](../sections/06_simulation_results.tex:118) | 条件包含 R_a-I、R_c-I，采用矩阵预条件 | 写明白噪声版本的两个因子恒为 I，协方差偏差输入恒为零，有效可变条件为 log(v)/5；把预条件写成其标量特例。结构表中的层宽和卷积骨干无需因此改变。 |
| [第六章训练设置](../sections/06_simulation_results.tex:160) | 200 轮去噪器、随机有色因子、100 轮分类器 | 保留实际训练轮数、样本、优化器和选模规则；默认扰动写成 CN(0,vI)，v 的对数采样范围保持。明确分类器使用对应冻结均值网络训练。 |
| [第六章比较对象](../sections/06_simulation_results.tex:183) | CGP-MP、CGP-MP-EP、STMP 等 | 根据实际完成结果定义 GP-MP 和有色变体。STMP 仍明确是已有密度比活动模块的适配基线；不得为突出本文贡献而写回 Cai 的原始活动公式。 |
| [第六章全部结果](../sections/06_simulation_results.tex:257) | 图 4–10、表 III 及相关文字来自既有配置 | 逐项处理权重归属，见后面的实验对应表。新 SNR 对照不能代替其他条件的验证，也不能只把所有 CGP-MP 标签替换成 GP-MP。 |
| [结论](../sections/07_conclusion.tex:9) | 有色噪声处理相关误差、主方法性能及泛化 | 删除有色训练的作用断言，补入均值导数方差和密度比；仅保留新主方法实际验证过的性能范围。 |
| [完整稿附录](../sections/appendix_evaluation_protocol.tex:4) | 配置差异、相位版、阻尼和停止统计 | 按最终模型绑定更新。已有历史批次的设置和局限继续归属于原配置，不随主方法改名抹去。相位估计附录的数学推导本身保留。 |

## 可先讨论的候选英文

以下是局部候选句，不是已完成的论文修订，也不预写未完成实验的结果。

**摘要中替换有色训练动机的两句：**

> We train a conditional-mean denoiser and approximate the posterior variance required for message passing from its input derivatives. This construction avoids training a separate second-order score network.

中文对应：训练条件均值去噪器，并由其输入导数近似计算消息传递所需的后验方差，从而省去独立二阶得分网络的训练。

这两句可接在现稿直接学习 AFDM 有效信道先验之后。后面的 MFLE/GPJD 与密度比描述仍能自然衔接。摘要最后的性能句要等待默认方法及对应证据确定；本轮不补数字。

**引言 STMP 段的建议组织：**

保留第一部分介绍 STMP 通过一阶与二阶网络提供均值和方差。随后用一句话明确本文的设计选择：

> In our receiver, the conditional mean and the approximate posterior variance are obtained from a single learned denoiser, with the variance computed from its input derivatives.

接回现稿关于高斯矩匹配不保证边缘似然准确的讨论，再引出密度比活动估计。不要增加“Cai 必须有完美的一阶网络，而本文不需要”或“本文消除了误差传播”等结论。导数方差仍依赖网络导数的准确性。

**第二项贡献的候选替换：**

> We learn a conditional-mean denoiser directly from multiantenna AFDM effective-channel samples with fractional delays and Doppler shifts, without imposing sparse or grid-aligned channel assumptions. Using the relation between conditional-mean derivatives and posterior covariance, we approximate the average posterior variance required for message passing without training a separate second-order score network.

这里的关系引用 Dytso 等，具体有限差分估计继承现稿与 Metzler 等的依据。该恒等式本身不是本文新提出的理论。已有得分参数化和去噪训练关系仍保留在第四章，题目中的 generative-model-aided 不因改为白噪声训练而失去对应内容。

**第三项贡献保留的核心：**

> We develop a message-passing JADCE receiver that combines multi-frame linear estimation with learned channel denoising. A density-ratio estimator provides the activity evidence, which is combined with the prior activity probability to form posterior activity probabilities. The two modules exchange Gaussian extrinsic messages to jointly detect active devices and estimate their channels.

MFLE/GPJD 可按当前已经定义的缩写继续使用。最后的实验总结另写，取决于最终完成的比较，避免把其他模型的结果写到该段。

**结论中替换有色训练作用的候选句：**

> The receiver obtained channel mean estimates and approximate variance feedback from the learned denoiser, while a density-ratio estimator supplied the activity evidence.

主结果继续按作者已确定的“主要趋势加一个有依据的解释或代表性数字”写法组织，不逐点报数，不把小幅训练消融差异扩写成普遍鲁棒性优势。

## 第四章和预条件公式的具体简化

以下是将现稿公式代入 C=vI 的结果。D 是复坐标数，实表示有 2D 个坐标，因而每个实坐标的噪声方差是 v/2。

**观测和条件均值：**

\[
\mathbf u=\mathbf h_{\mathbb R}+\sqrt{v/2}\,\boldsymbol\epsilon,
\qquad \boldsymbol\epsilon\sim\mathcal N(0,I_{2D}),
\]
\[
\mathbf m_{\mathbb R}(\mathbf u,v)
=\mathbf u+\frac v2\nabla_{\mathbf u}\log q_v^{\mathbb R}(\mathbf u).
\]

如果保留二阶得分关系作背景，可写成
\(P_{\mathbb R}=(v/2)I+(v^2/4)\nabla^2\log q_v^{\mathbb R}\)。这里后验协方差 P 本身一般仍非标量；标量的是噪声协方差。实际反馈只使用其平均迹。

**均值网络和损失：**

\[
\mathbf s_\theta(\mathbf u,v)=\frac2v
\bigl[\mathbf f_\theta(\mathbf u,v)-\mathbf u\bigr],
\qquad
\mathcal L_{\rm ch}=\mathbb E\left[
\frac{\|\mathbf f_\theta(\mathbf u,v)-\mathbf h_{\mathbb R}\|^2}{Dv}
\right].
\]

因此应写为带噪声方差权重的均方误差训练。将其改成不加权 MSE 会改变跨噪声水平的训练权重，不属于本次记号简化。

**导数方差：**

\[
\tau^\star(\mathbf u,v)=\frac{v}{2D}
\operatorname{div}_{\mathbf u}\mathbf m_{\mathbb R}(\mathbf u,v).
\]

使用学习网络和有限随机方向后是近似量。保持现稿实现，可继续定义 \(w_\ell=\sqrt{v/2}z_\ell\)，并写

\[
\widehat\tau_\theta=
\frac{1}{2\delta_{\rm FD}DL_z}\sum_{\ell=1}^{L_z}
w_\ell^{\mathsf T}\left[
f_\theta(u+\delta_{\rm FD}w_\ell,v)
-f_\theta(u-\delta_{\rm FD}w_\ell,v)
\right].
\]

固定 v 求输入导数；不要把方差采样、预条件的变化或外层方差更新一同求导。随机方向数量、复维归一化和差分步长均与现有接收机一致。

**预条件：**

将第六章 `eq:mean-preconditioning` 的 \(\sigma_d^2=1/2\)、\(\Sigma=(v/2)I\) 代入，得到

\[
f_\theta(u,v)=\frac{1}{1+v}u
+\sqrt{\frac{v}{2(1+v)}}\,
g_\theta\!\left(\sqrt{\frac{2}{1+v}}u,v\right).
\]

g 的条件编码仍为 log(v)/5。现有白噪声权重复用了同样的条件网络尺寸，协方差偏差输入恒为零；可以用上述有效函数表达它，但不能在复现表中声称已经删除条件分支或减少参数数量。删除冗余输入层属于另外的实现变更，本次不需要。

以上简化不影响密度比目标、活动先验修正、线性迹平均、site 更新、联合混合矩和外信息公式。

## 实验结果与新主方法的对应关系

当前独立批次 [white_preconditioned_matched_fp32_1000_snr_20261105](../../../result/snr_comparison/data/white_preconditioned_matched_fp32_1000_snr_20261105/PLAN.json)评估白噪声权重与其配套分类器，采用已知相位、估计噪声、原标量接口，六档 SNR 每档 1000 场景；其范围不是整篇论文全部设置。旧 TF32 配置结果不能与这一批混合。

| 现稿证据 | 切换白噪声默认方法后的处理 |
|---|---|
| 图 4 独立 AWGN 去噪 | 需要白噪声均值网络在对应保存样本上的结果，或将原有色曲线保留为明确标注的比较对象。主 SNR 实验不能代替独立去噪。 |
| 图 5 单场景 NMSE 收敛 | 使用与指定场景和模型一致的逐轮 NMSE；此前展示的相对变化停止指标图不是这张 NMSE 图。 |
| 图 6 已知相位主 SNR | 正在运行的白噪声对照可在完成核验后提供 GP-MP 曲线；保留 CGP-MP 作为训练消融有助于解释主线选择。 |
| 图 6 估计相位曲线 | 现有 CGP-MP-EP 使用有色权重。新的已知相位白噪声批次不产生 GP-MP-EP 结果；可保留原名称，不能直接改名。相位前端本身可复用。 |
| 图 7 导频帧数 | “25% 更少导频帧”属于原模型及原测试帧数，不能预先迁移到白噪声版本。 |
| 图 8 设备数、图 9 活动率、图 10 跨信道 | 现有结果继续属于原配置。白噪声版本若承担这些结论，需要对应的配对评价；原有阻尼选择和历史记录继续保留。 |
| 表 III 密度比消融 | 现有 354 场景比较可作为已标明配置的模块证据保留。若要直接称为白噪声主方法的活动模块消融，需要对应白噪声权重与配套分类器下的比较。 |
| 图 3 去噪示例 | 说明保存样例对应哪个模型，或用新主方法实际预测替换；不能只改图中文字。 |

这些是论文结果归属的依赖说明，不是自动启动以上实验的安排。完整 SNR 消融后，可以选择保留有色方法作为已充分评估的配置而仅降低贡献措辞，也可以确认白噪声为默认方法后分阶段补齐需要保留的结论。

有色训练消融无明显优势时，结果段应如实给出差异大小及其适用设置，将有色训练作为被检验的训练选择保留。不能把“没有观察到明确收益”写成等效性已经证实，也不能通过删除不利结果形成没有做过该实验的印象。尚未完成的统计不预写为零增益。

## 依据和实施顺序

1. 术语和理论沿用 [TERMINOLOGY.md](TERMINOLOGY.md)：Cai 的一、二阶网络及标量接口对应 [§III-A、§IV-B–C](https://arxiv.org/html/2506.00581v2#S4)；条件均值导数和后验协方差对应 [Dytso 等 §IV，Proposition 1，式 (22)，PDF p.5](https://arxiv.org/pdf/2104.01883)；分类概率与密度比对应 [Menon–Ong §4.2，式 (17)](https://proceedings.mlr.press/v48/menon16.pdf)。没有提出新的方法名称或更改共用术语。
2. 预条件简式是将现稿矩阵表达代入白噪声条件得到；现稿的 Karras §5 和 Inflationary Flows 附录 B.1 依据沿用[公式原型记录](DAMPING_AND_FORMULA_PROTOTYPES_20261104.md)。数值实现已对照 [model.py](../../../src/training/colored_preconditioned_20261024/model.py) 与 [operators.py](../../../src/training/colored_preconditioned_20261024/operators.py)。不能将这个白噪声特例另称为新的预条件理论。
3. 先讨论本清单中的摘要、引言动机和贡献安排；等 SNR 配对结果核验后决定最终训练方案。正文若正式切换，再统一第四章公式、第六章训练说明、第五章名称和图示。
4. 最后按实际模型逐图更新结果及结论，并同步完整稿评估附录、中文摘要和名称记录。`main_full.tex` 引入同一个 `main.tex`，不需要维护第二份独立正文。内部 C-STMP 目录和历史批次名称无需随展示名迁移。

本轮交付仅包括上述建议和局部候选文字，未生成修订版摘要或全文，未编译或改写两份 PDF，未启动新训练或推断。现有主线和实验继续保持其真实模型身份。
