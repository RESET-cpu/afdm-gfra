# 主线入口：估计跨帧相位

2026-10-15。Proposed 与五个 baseline 的公开主入口统一采用未知跨帧相位，先从观测和原始导频估计相位，再运行各自的条件信道与活动推断。准确已知相位作为显式的理想参考。

## 入口与信息条件

- `simulate` 默认保存 `observation`、`pilot`、`noise_variance`、`activity_prior` 四项公开输入；真实相位、信道和活动保存在独立真值文件。
- `run`、`baseline` 默认从这四项输入估计相位。Proposed 使用 `configs/proposed_unknown_phase.json`；五基线共用 `algorithm/unknown_phase_baselines.py` 中的组合入口。
- 理想参考在生成和推断时指定 `--phase-mode known`，公开输入使用包含准确相位的 `operator`。
- 相位前端沿用既有物理拟合设置。主线核函数、网络权重、活动判决和条件接收机配置沿用原版本；固定资产清单加入新的公开入口及其相位依赖。

同一种子和生成参数产生相同观测、噪声与物理信道，两种模式改变接收机可获得的信息。主要报告估计相位下的完整信道 NMSE、AER 和计算量，并在配对物理场景中度量相对理想参考的差距。

## 已有实验的解释

GAMP-SBL 与 off-grid SBL 后验更新实验中的“固定相位”，指先从观测得到估计值，再固定用于条件推断。全步和半步设置继续更新这个估计。三组属于估计方法内部比较；真实相位仅用于该实验单列的 oracle 诊断。原始数值、失败与不利样本保留在[实验报告](../baseline_phase_learning_20261015/REPORT.md)及对应结果目录。

当前六方法未知相位图使用已有十场景面板；其中 L-DAMP 显式使用输出 TSVD 配置，默认条件配置仍为 `configs/ldamp.json`。历史已知相位图采用不同场景，跨条件损失需要同场景配对计算。各图对应配置在 `MAINLINE.json` 分别记录。

## 核验范围

核验通过：38 项相关测试；六种实际接收机的输出全部有限，与原条件求解器逐数组精确一致；六方法相位估计一致。同种子两种模式的观测、噪声、先验和全部真值完全相同，已知相位算子重构最大误差为 0。主线资产核验全部通过，索引修改后另复查了原测试中的 3 项。

相关测试日志见 [tests.log](tests.log)，主线索引更新后的复查见 [metadata_tests.log](metadata_tests.log)。实际入口核验使用一个已保存的 40 用户、0 dB 公开输入；逐方法重新估计相位，并与直接调用其原条件求解器进行逐数组比较。另以相同种子生成三用户的两种信息条件，运行实际命令行 GAMP 并检查观测和真值的一致性。这些运行用于验证接入正确性。

完整记录见 [CHECKS.json](CHECKS.json) 和 [default_device/CHECKS.json](default_device/CHECKS.json)。各次推断的浮点警告原样保存在配套文件；已知 NumPy Accelerate 警告的独立数值诊断见[已有诊断](../baseline_phase_learning_20261015/BLAS_DIAGNOSTIC.json)。本次核验不作为新的性能或速度基准。

核验脚本最初缺少项目导入路径，修正后继续执行。随后在 CPU 上运行 Proposed 的核验由代理中断，改用项目默认设备完成；中断记录保存在 [CPU_ATTEMPT.json](CPU_ATTEMPT.json)，与完成运行分别保存。
