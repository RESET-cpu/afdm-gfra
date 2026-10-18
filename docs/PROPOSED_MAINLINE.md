# Proposed 主线与保存规则

2026-10-15：以已有结果对应的原版 Proposed 为后续研究基准。
固定版本位于 [proposed_mainline_20261015](../archive/proposed_mainline_20261015/README.md)，
机器可读绑定见 [MAINLINE.json](../MAINLINE.json) 的 `algorithms.proposed.preservation`。

2026-10-16：用户正式确定本页版本为算法主线，并结束本轮算法探索。
采用原导频、原三网络、原迭代和原门限；后续 SNR 点扩展为 −4、−2、0、2、4、6、8、10 dB，
正式实验按原导频下无噪接收功率与热噪声方差之比标定 SNR。
后续工作以该版本的复现、baseline 配对比较及结果和论文整理为范围；
进一步算法探索须由用户重新明确提出。已有候选和失败结果作为历史记录保留。
本决定对应[确认记录](../docs/history/results/proposed_mainline_confirmation_20261016/DECISION.json)。

2026-10-17：按用户要求完成相位前端优化与 Proposed 噪声估计的配对验证，默认入口已更新。
相位仍采用两轮完整搜索；缓存固定几何、批量计算相关量并省去未使用的二阶导数后，
30 个场景、240 个条件的五组相位输出均与原版逐元素一致。
8 个条件的独立交替计时由平均 6.035 秒降至 4.309 秒，减少 28.6%。
Proposed 增加观测驱动的空间协方差 MDL 噪声估计；20 个场景、160 个条件的活动判决不变，
逐 SNR 汇总 NMSE 最大恶化 0.0623 dB，全部通过预设 0.15 dB / 0.1 个百分点的验收容差。
这是有限样本的性能验收，不能解释为总体无误差或估计器无偏。
验证与旧入口快照见[采用核验](../results/phase_optimization_20261017/PUBLIC_INTEGRATION.json)、
[噪声结果](../results/phase_optimization_20261017/noise_fresh/SUMMARY.json)与
[计时](../results/phase_optimization_20261017/ISOLATED_TIMING.json)。
五方法比较按用户最新要求在500场景结束，−4～8 dB，共17500次推断核验通过。原导频、权重及推断未改变，五方法均估计相位与噪声。图例n=500，AER采用概率值对数轴。见[最终报告](../results/baseline_comparison_500_20261018/REPORT.md)和[范围计划](../results/baseline_comparison_500_20261018/PLAN.json)。

## 固定的算法

| 项目 | 当前主线 |
|---|---|
| 公开入口 | `run.py run --method proposed --phase-mode estimated --noise-mode estimated`（两项均为默认） |
| 接收机 | `src/afdm_jadcedd/algorithm/proposed_frontend_candidate.py`，调用原条件接收机 |
| 配置 | `configs/proposed_frontend.json` → `configs/proposed.json` |
| 物理导频 | 原 `PartialDFTPilot`，由 `src/afdm_jadcedd/experiment/unknown_phase.py` 的默认生成入口提供 |
| 相位 | 从原始导频和观测估计，原两轮完整搜索的优化实现 |
| 网络 | `models/proposed/first.pt`、`second.pt`、`activity.pt` |
| 推断 | 原完整信道三网络与消息传递，`covariance_mode=isotropic` |
| 阻尼 | 0.2，为新查询/反馈矩的权重 |
| 停止 | 最多 600 轮，最少 60 轮，保留全部原收敛条件 |
| 活动判决 | 原分类器，概率门限 0.5 |
| 噪声 | 空间协方差 MDL 估计一次，再输入原推断；显式 `--noise-mode known` 为准确噪声参考 |

以上是版本身份，不代表对近似正确性的新结论。
逐式推导与适用性问题分别见[公式核对](history/results/proposed_cai_equation_audit_20261015/REPORT.md)和
[近似评估](../docs/history/results/proposed_cai_equation_audit_20261015/APPROXIMATION_ASSESSMENT.md)。

2026-10-16：按用户选择，后续 Proposed 比较采用原导频，继续使用原三网络、原迭代及原门限；
本轮后续 SNR 点为 0、2、4、6、8、10 dB。默认生成入口本身一直保留原导频，冻结主线无需改动。
酉导频比较作为独立实验保留。最新十场景在 4、6 dB 的固定热噪声配对核查中，原导频均为
0 次漏检、0 次虚警，酉导频分别为 0/1、0/4；原导频完整 NMSE 分别为 −14.666、−15.480 dB。
这里 4、6 dB 是酉导频参考点；保持同一热噪声后，原导频实际 SNR 相差 −0.240 至 +0.309 dB。
旧面板两个样例及本轮两个虚警样例的重放均逐元素一致，网络、配置和核心实现身份相同。
结果见[配对核查](../docs/history/results/proposed_polar_snr6_10_20261016/version_audit/SUMMARY.json)、
重放（历史文件已清理，原路径：`results/proposed_polar_snr6_10_20261016/version_audit/REPLAYS.json`）与
[采用记录](../docs/history/results/proposed_polar_snr6_10_20261016/version_audit/PILOT_SELECTION.json)。
此核查只运行 Proposed，不替代原导频下六档 SNR 的完整六方法比较。

同日补齐同十场景的 8、10 dB 参考点，二十次原导频推断全部完成并收敛，
两档均为 0 次漏检、0 次虚警；酉导频对应为 0/3、0/1。
原导频完整 NMSE 分别为 −16.440、−16.865 dB，相对酉导频分别改善 0.214 dB、退化 0.063 dB。
配对仍保持相同热噪声，原导频实际接收 SNR 的偏移仍为 −0.240 至 +0.309 dB。
至此，这批十个物理场景在原导频的 4、6、8、10 dB 参考点全部为零漏检、零虚警，
不把四档重复测量计为四十个独立物理场景。详见[补充结果](../docs/history/results/proposed_polar_snr6_10_20261016/original_pilot_8_10/SUMMARY.json)
及[保存结果复核](../docs/history/results/proposed_polar_snr6_10_20261016/original_pilot_8_10/VERIFICATION.json)。

## 与已有结果对应

2026-10-16：当前主线已完成原导频十场景 × 八档 SNR 的五方法配对比较，共 400 次推断。
本批使用估计相位并供给准确物理噪声方差；每档 SNR 按原导频下的无噪接收功率精确设置。
Proposed 的完整信道 NMSE 在各档均低于四个 baseline；−4、−2、0、10 dB 各漏检 1 个，
2、4、6、8 dB 无漏检，全部八档无虚警。十个场景不构成对总体零错误的保证。
10 dB 漏检在完整公开入口重放中逐元素复现；先前固定热噪声导频核查的同样本实际为 10.30855 dB。
这两批输入和相位估计不同；此前零漏检仅适用于当时核查的输入。
见[八档比较](history/results/proposed_original_snr8_10_20261016/FINDINGS.md)及
[完整入口重放](../docs/history/results/proposed_original_snr8_10_20261016/high_snr_verification/REPLAY.json)。

当前版本的直接证据为
[未知相位实验](../docs/history/results/proposed_unknown_phase_20261015/evaluation/REPORT.md)：
10 个物理场景，−4、−2、0、2、4、6 dB，共 60 次 Proposed 推断。
冻结包独立复制全部 60 组公开输入、评价真值、输出、运行记录、警告、配置和结果汇总。
真值仅供独立评分；重放入口不读取真值。

该历史六方法面板均供给准确噪声；它不代表后来改为估计噪声的五基线版本。
2026-10-09 的 100 场景结果使用已知相位和阻尼 0.1，作为单独的历史参考保留。
冻结包保存其配置、来源记录、汇总和图；历史逐例大数组仍保留在原结果目录，
不将其成绩登记成当前阻尼 0.2、未知相位版本的成绩。

## 后续工作与保存规则

1. 当前默认 Proposed 固定为上述版本。本轮算法探索已按用户要求结束；不按历史待办自行续训网络、修改近似或扩展候选。
2. 用户日后明确重新开展算法探索时，候选使用独立的实现、配置、权重和结果路径；冻结包本身不作为开发目录。
3. 对比使用相同输入、噪声/相位条件和评价方式，保留全部失败样本与运行记录。性能更好或推导更完整均需分别提供证据。
4. 用户选择切换主线时，先保存新版本与配对验证记录，再更新默认绑定；保留本次固定版本供对照和恢复。
5. 文件清理默认排除该冻结包。冻结包不使用指向活动源码或模型的符号链接、硬链接；所有文件均有 SHA-256 清单。

## 检查与重放

在项目根目录运行：

```sh
.venv/bin/python -B archive/proposed_mainline_20261015/verify.py
.venv/bin/python -B run.py verify
.venv/bin/python -B archive/proposed_mainline_20261015/replay.py --device mps --output NEW_REPLAY_DIRECTORY
```

前两条分别检查历史冻结包完整性和当前源码／资产绑定。
当前公共模块的 baseline 导入路径已随目录整理更新，迁移前后数值核对见
[目录迁移记录](../results/baseline_package_20261016/REPORT.md)。
最后一条直接导入冻结副本，默认重放 `scene000/snr+00`，输出目录必须是新路径；
可以使用 `--case scene003/snr-04` 选择其他已保存条件。
依赖版本保存于冻结包的 `ENVIRONMENT.json`。已有环境使用 MPS；其他设备的数值一致性需另行核验。
此包保存推断和重放所需的三份训练权重与训练记录；大规模训练数组仍在原目录。

Git 自动快照保持停用。本次为用户要求的一次独立文件保存。
