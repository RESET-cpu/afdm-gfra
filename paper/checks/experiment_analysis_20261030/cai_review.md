# Cai 实验论证方式与本稿改写建议

审读对象：`reference/literature/cai2026.pdf`，正式期刊版本，16 页；本稿 `sections/06_simulation_results.tex`。以下建议只依据已保存实验与当前公式，不需要补跑实验。新算法名称为 GP-CCD-MP-DRE。

## 1. Cai 实际如何分析

- VI-B，PDF 第 11–12 页、期刊页 3585–3586、Fig. 4：先单独评估均值去噪器，建立后续整体接收机比较的基础；比较的重点是学习先验、显式连续参数估计与有额外路径信息的参考之间的关系，并联系实现成本。其“接近 genie”的判断只适用于其结果；本稿去噪曲线距 genie 仍明显，不能照搬。
- VI-C，PDF 第 12 页、期刊页 3586、Fig. 5：分别看最终精度、达到稳定区间的迭代速度和瞬态反弹；用户数增加后比较曲线变化；对第二轮反弹的解释明确标为推测，并联系早期功率估计与网络输入尺度的偏差。本稿没有相应轨迹诊断，不应把这一原因直接套入。
- VI-C，PDF 第 12–13 页、期刊页 3586–3587、Fig. 6：不仅指出领先，还分析 TMP-EM 不同子块数的曲线交叉，进而讨论模型精细程度随噪声水平的取舍。最可借鉴的是抓住“曲线为什么变形/交叉”的问题，而不是套用原因。
- VI-C，PDF 第 13 页、期刊页 3587、Fig. 7：把检测与信道估计串成论证，解释同一活动先验下更准的信道估计如何经消息传递改善检测。本稿可解释活动概率和联合均值的耦合，但不能声称本地 STMP 没有学习分类器，或把全部检测增益独归 DRE。
- VI-C，PDF 第 13 页、期刊页 3587、Figs. 8–10：把固定 NMSE 目标转成可支持用户数，观察增长斜率，再把短导频处更大的优势转成导频开销意义。不是逐点介绍所有数值。
- VI-C，PDF 第 13–14 页、期刊页 3587–3588、Figs. 11–13：每项额外实验对应一个明确问题：换信道、换测量矩阵、减少训练样本；结论回答该问题。其因果措辞仍需独立判断，本稿不应把没有消融支持的解释写成已证明的原因。

## 2. 当前稿的具体不足

1. 大部分小节采用“图展示什么—谁最好—报两个数—说明有效”的重复顺序，没有把本节要验证的假设放在前面。
2. 去噪小节尚未充分使用 Gaussian shrinkage 与全张量去噪的区别；不能由一张综合比较图单独确证低 SNR 增益来自有色训练。
3. 收敛小节把 60 与 85 两个停止点作为主要论据，而 60 是人为设置的下限；轨迹进入平稳区间的快慢更有信息。
4. SNR 小节遗漏了两类基线的斜率差异及 NMSE/AER 排名不一致的意义，最后一句低 SNR AER 例外显得像孤立免责。
5. 导频小节的 Q=8 主要揭示配置稳定性；不能把该点 43 dB 量级的差异当成普通稳态精度增益。应把 Q>=16 的精度趋势和目标导频门槛作为主要论点。
6. 运行来源、收敛例外、调参历史应保留一次，但应集中到评价协议，避免挤占曲线分析。这个调整并不等于删除不利结果或记录。

## 3. 可替换的原创英文讨论

以下是分析段落草案；设置、公式、图和图注原则上保持原稿。根代理可根据整章衔接再压缩。

### Channel Denoising Performance

The denoising experiment examines whether the learned prior captures channel structure beyond average coefficient power. In Fig.~\ref{fig:cstmp-denoising}, the Gaussian-prior estimator applies only scalar shrinkage, whereas both neural estimators use the full channel tensor. At $0$~dB, the colored-trained estimator achieves $-17.98$~dB NMSE, compared with $-2.98$~dB for Gaussian shrinkage. This difference supports the use of a structured channel prior in the subsequent joint receiver. The learned estimators also continue to improve at high SNR, while the sparse-recovery curves flatten under their adopted representations and settings. Thus, additional observation accuracy can be translated into more accurate channel estimates without first fitting the effective channel to the prescribed dictionary.

The two neural estimators exhibit different strengths across noise levels. Colored training yields a $2.11$~dB advantage at $-10$~dB, but the ordering reverses at high SNR. Its benefit is therefore concentrated in the regime with greater input uncertainty. Neither learned curve approaches the genie reference, whose additional path information removes uncertainty that the denoisers must resolve from the noisy channel alone.

### Convergence Behavior

The trajectories in Fig.~\ref{fig:cstmp-convergence} distinguish the initial adjustment of the exchanged messages from the subsequent refinement of the channel estimate. Both receivers exhibit an early NMSE increase, so their iterations are not monotone in channel error. GP-CCD-MP-DRE then approaches its final value by approximately $30$ iterations, whereas STMP continues to improve over a substantially longer interval. Their final NMSEs are $-13.85$ and $-11.79$~dB, respectively. The former stops at the imposed minimum of $60$ iterations; this stopping count should therefore not be interpreted as the number required to reach its nearly stationary estimate. The result illustrates the behavior of the complete update schedules, including their different damping and variance updates, for this paired scene.

### Effect of SNR

The SNR sweep tests how effectively each receiver converts more accurate observations into improved channel and activity estimates. GP-CCD-MP-DRE and STMP continue to reduce NMSE throughout the range, whereas the improvements of the dictionary-based baselines become smaller at higher SNR. Together with the direct denoising results, this behavior indicates the value of modeling the effective-channel distribution beyond the adopted sparse representations. The proposed receiver's advantage over STMP decreases from $1.87$~dB at $-4$~dB to $0.41$~dB at $6$~dB, showing that its largest benefit occurs when the observations are least informative.

The AER curves provide a complementary view of this trend. The proposed receiver's reduction in detection errors relative to STMP is mainly due to fewer missed active terminals. Such gains are relevant to channel NMSE because the activity probability weights the conditional channel estimate in \eqref{eq:exact-local-moments}. Nevertheless, detection and estimation rankings need not coincide: at $-4$~dB, off-grid SBL has slightly lower AER but appreciably higher NMSE. Correctly classifying a terminal does not by itself ensure an accurate estimate of its channel coefficients.

### Effect of Pilot-Frame Count

Increasing $Q$ supplies additional linear measurements of the same channel and reduces the uncertainty passed from MFLE to GPJD. Figure~\ref{fig:cstmp-pilots} shows that the resulting gains are largest when pilot resources are scarce and diminish as $Q$ increases. For $Q\geq16$, the NMSE advantage over STMP decreases from $1.57$~dB at $Q=16$ to $0.51$~dB at $Q=48$. On the evaluated grid, GP-CCD-MP-DRE reaches $-14$~dB NMSE with $24$ frames, whereas STMP requires $32$ frames, corresponding to a $25\%$ reduction in pilot-frame count. At $Q=48$, their AERs coincide while a channel-estimation gap remains, indicating that further channel refinement is possible after most activity errors have been removed.

The $Q=8$ point additionally exposes a limitation of the retained STMP schedule: $462$ of its $500$ runs reach the iteration limit, compared with two runs of the proposed receiver. All outputs are included. The large separation at this point therefore reflects the behavior of the configured iterations as well as their estimation accuracy; the pilot-saving comparison above is based on the range where both receivers converge in all evaluated scenes.

## 4. 数值与机制核验

| Item | Evidence |
|---|---|
| Denoising values | `result/channel_denoising/figures/narrow_paper_20261026/PLOT_DATA.json`: colored at 0 dB −17.9829, Gaussian −2.9755; white minus colored at −10 dB = 2.1110 dB; colored at 30 dB −39.2184, genie −61.2916 |
| Convergence | `result/snr_comparison/figures/convergence_current_paper_20261026/PLOT_DATA.json`: proposed iteration 30 −13.7810 vs final −13.8537; STMP iteration 30 −9.0778 vs final −11.7877 at 85 |
| SNR gap | `result/snr_comparison/figures/full_grid_final_20261026/PLOT_DATA.json`: gains 1.8681 dB at −4 and 0.4091 dB at +6; at 0 dB misses 81→42, false alarms 0→1 |
| Low-SNR ranking distinction | Same source at −4 dB: off-grid SBL AER 0.00435 vs proposed 0.00455, NMSE −5.7987 vs −9.8550 |
| Pilot values | `result/pilot_frames/figures/full_grid_final_20261026/PLOT_DATA.json`: gains 1.5661 dB at Q16 and 0.5099 dB at Q48; proposed Q24 −14.4704, STMP Q32 −14.4062; both Q48 AER 0.0001 |
| Iteration-limit counts | Same pilot source Q8: STMP 462/500, proposed 2/500; all STMP/proposed runs Q16–48 satisfy native convergence |
| Joint estimator structure | Chapter III `eq:exact-local-moments`: posterior joint mean = activity probability times active-channel conditional mean; joint covariance includes uncertainty in both activity and channel |
| Additional measurements | Chapter III `eq:linear-variance`: MFLE posterior covariance depends on the pilot observation operator and noise variance. Q is the number of observation rows; fixed per-frame pilot energy means increasing Q also increases total pilot energy. Do not claim a fixed-total-energy comparison. |

No claim isolates covariance training, the derivative variance estimate, DRE, or damping as the cause of receiver superiority. The local STMP comparison also uses a learned activity classifier. No new results were generated.
