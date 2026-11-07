# 第六、七章复审意见

**2026-11-04 后续状态：作者已确认修改，VI01–VI07、VII01–VII02 全部完成。** 两版 PDF 已更新，13/14 页，43 篇参考文献；以下候选和“未修改”描述保留为本轮审阅时的历史记录，不再视为待处理。见[实施与核验](../checks/chapters_vi_vii_language_selected_20261104/README.md)。

日期：2026-11-04。对象：当前 GP-MP-C 稿件第 VI、VII 章，两版共享正文；图 6 已恢复六算法、已知相位、每档 1000 场景。使用 pre-submission-reviewer 与 humanizer，仅审阅和记录，没有修改正文、图表或 PDF。

## 结论与范围

未发现新增的 Critical/Major 级模型、公式或结构问题。现有实验顺序能够从去噪、活动概率计算进入整机性能和跨信道评估，第七章也回收了多帧表示、有效信道先验和接收机三项工作，整体结构可以保留。

建议处理六处小修，其中第六章五处均已在上一轮候选中记录，第七章新增一处比较对象澄清；另有三项可选。这里的六处建议不等于六个新研究问题，也不表示原文都有语法错误。优先级最高的是 VI02 的搭配、VI04 的重复和 VII01 的比较对象。

图 7 的 C1 仍按既有决定留待最终图表核定；本轮没有重新定级、选择处置或认为该项已经解决。新的相位和 SBL 预算实验按作者安排后补，不作为当前阶段的新增缺陷。此结论不是整篇论文已可最终投稿的认证。

## 建议小修

沿用上一轮 VI01–VI07 编号，避免同一事项重复计数。

| 编号 | 位置与当前原文 | 判断及建议写法 |
|---|---|---|
| VI01 | [VI-A1，L68](../sections/06_simulation_results.tex:68)：Training and validation use … channels from disjoint scenes, four per scene before multiplication by … | 一句话同时交代样本数、形状、场景划分和每场景数量，尾部修饰较挤。建议：We use 50,000 clean 16×16×16 channels for training and 5,000 for validation, drawn from disjoint sets of scenes. Each scene provides four channel samples before multiplication by α_k. 数值和取样阶段保持。这是句子负担问题，不是悬垂分词或语法硬错。 |
| VI02 | [VI-A1，L87](../sections/06_simulation_results.tex:87)：We then freeze the denoiser and train the classifier from random initialization by 式 (31) | by an equation 搭配不自然，实际使用的是损失函数。建议：We then freeze the denoiser and train the classifier from random initialization using the loss in 式 (31), with batch size 32, … 原引用键 eq:classifier-loss 保持。 |
| VI03 | [VI-A3，L167](../sections/06_simulation_results.tex:167)：Their default damping factors are 0.2 and 0.4. | 上文可以推知顺序，但显式对应更清楚。建议：The default damping factors for GP-MP and GP-MP-C are 0.2 and 0.4, respectively. 仅涉及默认值，不改变设备数实验的特殊设置。 |
| VI04 | [VI-D2，L318](../sections/06_simulation_results.tex:318)：GP-MP-C achieves the lowest NMSE and achieves lower AER than GP-MP. | 第二个 achieves 重复。建议：GP-MP-C achieves the lowest NMSE and a lower AER than GP-MP. 比较范围保持。 |
| VI05 | [VI-E，L370](../sections/06_simulation_results.tex:370)：Figure … compares the training profile D with profiles A, B, and C without retraining. | 图比较的是各剖面下的性能。建议：Figure … compares channel-estimation performance on the training profile D and on profiles A, B, and C without retraining. 不改变“不重训”条件。 |
| VII01 | [VII，L16–19](../sections/07_conclusion.tex:16)：… improved channel estimation and activity detection over the white-noise-trained baseline, reduced pilot requirements at the evaluated accuracy target, and channel-estimation gains across the tested NTN-TDL profiles without retraining. | 最后一项没有明确比较对象，可能被理解为仍相对前面的白噪声基线。建议将最后一项改成：and lower NMSE than the four sparse-recovery baselines across the tested NTN-TDL profiles without retraining. 这是比较对象澄清，不判定原句已经明确声称错误结论。 |

VI01 对应 skill 语法参考 G4 的句子复杂度检查；VI02 对应第 7 节的不自然搭配；VI04 属于局部冗余。VI03、VI05、VII01 属于指代及比较对象精度，不编造语法规则编号。

VII01 的证据：四个稀疏恢复基线在 D/A/B/C、六档 SNR 共 24 个点上均高于 GP-MP-C 的 NMSE。GP-MP 在 A 的 6 dB 和 B 的部分高 SNR 点更低，所以最后一项不宜隐含“相对 GP-MP 在全部剖面、全部 SNR 都更好”。当前 VI-E 已明确限定四个稀疏恢复基线，因此只需让结论沿用相同对象，无需新增逐点讨论。B 的 4 dB 差仅约 0.003 dB，不将这一数值差异描述成显著优势。

## 可选项

| 编号 | 位置 | 可选处理 |
|---|---|---|
| VI06 | [VI-A，L15](../sections/06_simulation_results.tex:15)：For Q≤KN, select distinct DFT rows | 可改为 we select，与实验叙述一致。原祈使句成立，不必强制全文统一时态。 |
| VI07 | [VI-A2，L113](../sections/06_simulation_results.tex:113)：a matrix extension of the scalar preconditioning … | 可补入此前已核实的矩阵预条件直接来源 Inflationary Flows 附录 B.1；当前引用并非凭空、公式没有新发现的错误。出处对应见[既有核查](DAMPING_AND_FORMULA_PROTOTYPES_20261104.md:69)。 |
| VII02 | [VII，L9–12](../sections/07_conclusion.tex:9)：Based on this model, we learned … without imposing …, with colored Gaussian noise used … | 可在 assumptions 后断句，后接 We used colored Gaussian noise to account for correlations in denoiser-input errors. 保留假设边界和训练动机；不把 without … 当成 AI 套话删除。 |

第七章末句是温和的应用意义总结，可以保留；没有必要为了 Humanizer 强行删除所有总结句。结论使用过去时回顾本工作可以接受，不按 skill 的默认模板机械改成现在完成时，也不强加未来工作段落。

## 图文与结论核对

| 内容 | 核对结果 |
|---|---|
| 六算法 SNR 数据和设置 | 图 6 六种接收配置均为已知相位、每点 1000 场景；旧估计相位曲线及正文对应结果句已撤出，未发现残留版本矛盾。 |
| SNR 的 NMSE 比较 | 六点均为 GP-MP-C 最低，比 GP-MP 低约 0.41–1.87 dB。现稿表述成立。 |
| SNR 的 AER 比较 | 六点均低于 GP-MP。−4 dB 的 Off-grid SBL 为 0.435%，GP-MP-C 为 0.455%，所以保留 lower AER than GP-MP，不能扩大成 all-SNR lowest AER。 |
| 独立去噪 | 有色训练版本在低 SNR 改善，现稿限定 low SNR 正确；不扩写成整个范围始终优于白噪声训练。 |
| 活动概率消融 | Table II 的分 SNR 和汇总报告维持已核定版本；正文没有把迭代上限统计误写成所有算法都不收敛。 |
| 单场景收敛 | 保留 In this example，描述所示曲线，不推导平均时间或所有场景的速度结论。 |
| 设备数 | 只复用 C1 既有状态，不重开讨论。该处“所有点最低”等最终表述仍随图 7 定稿处理。 |
| 活动概率 | 保存数据支持所有方法随负载变大而退化，GP-MP-C 的 NMSE 最低，相对 GP-MP 的差距增大。 |
| 导频帧数 | 已评估档位中，GP-MP-C 首次达到 −14 dB 为 Q=24，GP-MP 为 Q=32，25% 减少成立；原文保留 evaluated counts 和 fixed per-frame energy。 |
| 跨信道 | 现稿 VI-E 的 four sparse-recovery baselines 有数据支持。第七章建议显式沿用这个比较对象。 |
| 结论三项贡献 | 与前文多帧表示、先验学习及接收机对应，结构无需重写；保留评估目标、已测试剖面和无需重训的范围限定。 |

## 语言与版面

已完整扫描这两章的词表与破折号。仅 VI-A2 L146 的 yielding one logit per device 命中机械词表；它描述网络实际输出，没有夸张或空泛附加含义，不单独列为缺陷。两章没有连接句子的 em dash，没有新增必改的 AI 套话。数学区间和 delay--Doppler 的连接号不按句间破折号处理。

本轮检查了当前第 8 页，并复用同一 PDF 哈希对应的第 9–12 页预览进行图文核对。图 4–10 均为矢量 PDF；已知的第 9 图轴范围、图例风格和九条去噪曲线均沿用作者已批准的选择，不机械套用“图例不得多于六项”等规则。

第六章式 (41)–(43) 引用有效，第七章没有编号公式；两章引用键有效。此前两版已成功编译，本轮没有源码修改，不重复编译。保护稿件、图表和 PDF 共 31 项哈希保持。

本轮是当前两章的逻辑、证据、语言和格式复审，没有重新开展全领域新颖性检索、全书目查新或新增训练/推断；不据此给整篇论文打分。

[数据核对](../checks/chapters_vi_vii_review_20261104/EVIDENCE.json) · [静态检查与保护记录](../checks/chapters_vi_vii_review_20261104/CHECKS.json) · [前次第六章分节分析](CHAPTER_VI_SIX_METHOD_REVIEW_20261104.md)

