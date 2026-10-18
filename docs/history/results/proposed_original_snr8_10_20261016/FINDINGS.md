# 原导频八点比较：十个配对物理场景

400 次推断全部完成并通过保存输出复核。Proposed、SOMP、GAMP-SBL、GNN-ASPL、Off-grid SBL 均使用相同观测和相位估计，统一获得准确物理热噪声方差。

| SNR / dB | Proposed NMSE / dB | Off-grid SBL NMSE / dB | Proposed 漏检 / 虚警 | GNN-ASPL 漏检 / 虚警 |
|---:|---:|---:|---:|---:|
| -4 | -9.132 | -6.120 | 1 / 0 | 2 / 0 |
| -2 | -10.588 | -7.536 | 1 / 0 | 1 / 0 |
| 0 | -11.951 | -8.721 | 1 / 0 | 0 / 0 |
| 2 | -13.334 | -9.553 | 0 / 0 | 0 / 0 |
| 4 | -14.573 | -10.140 | 0 / 0 | 0 / 0 |
| 6 | -15.698 | -10.500 | 0 / 0 | 0 / 0 |
| 8 | -16.432 | -10.872 | 0 / 0 | 0 / 0 |
| 10 | -16.092 | -11.145 | 1 / 0 | 0 / 0 |

Proposed 的完整信道 NMSE 在 8/8 档低于全部四个 baseline；每档的具体配对差异和描述性区间见 [PAIRED.json](PAIRED.json)。上述表格单列 Off-grid SBL 与 GNN-ASPL；全部五方法的 NMSE、漏检和虚警计数见 [完整报告](REPORT.md)。

每档为 39 个活跃用户和 361 个非活跃用户，来自同一批十个场景。八档重复使用这些场景；本批已有部分历史结果，不是新的独立确认集。零观测错误不能解释为总体错误概率为零。

Proposed 的停止状态为 {'CONVERGED': 80}；训练噪声范围外查询数为 0。所有 baseline 的原预算停止结果照常计入，详见 SUMMARY.json；完整 NMSE 使用全部用户的完整估计。

已知噪声指统一供给准确物理方差。GAMP-SBL 仍保留其原有噪声精度更新，准确方差进入 Gamma 先验参数；80 个输入的该参数关系均已核验，见 [噪声信息核对](NOISE_INFORMATION.json)。

10 dB 的 1 次漏检已通过完整公开接收入口独立重放：重新估计相位后的全部五个相位数组及五个接收输出数组均与批次保存值逐元素一致，见 [重放核验](high_snr_verification/REPLAY.json)。该重放不计入本批 400 次样本。此前固定热噪声的导频核查中，同场景标作 10 dB 的原导频实际 SNR 为 10.30855 dB；本批精确设为 10 dB 后，物理噪声方差增加约 7.36%，相位估计随观测重新计算。两批输入不同，不能沿用此前零漏检结论；这一比较尚不能分离噪声、相位误差及迭代过程各自的影响，见 [输入比较](high_snr_verification/INPUT_COMPARISON.json)。

此前 [四 baseline 的 1000 场景实验](../baselines_1000_20261015/REPORT.md)已经完成 24000 次推断，覆盖 −4、−2、0、2、4、6 dB，采用估计相位和估计噪声。其场景种子和噪声信息条件与本次不同，应分别报告。

![五方法完整比较](/Users/wangbo/Desktop/科研/JADCEDD/results/proposed_original_snr8_10_20261016/comparison.png)

输入与源码核验见 [VERIFICATION.json](VERIFICATION.json)，400 份输出的逐例评分与哈希核验见 [OUTPUT_AUDIT.json](OUTPUT_AUDIT.json)。全部八档结果保留。
