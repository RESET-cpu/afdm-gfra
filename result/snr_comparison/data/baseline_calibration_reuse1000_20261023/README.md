# 复用现有主实验输出的门限校准

用户于 2026-10-23 确认采用以下固定划分：

| 场景编号 | 数量 | 用途 |
|---|---:|---|
| 0–499 | 500 | 拟合每种 baseline 的固定门限与估计 SNR 分档门限 |
| 500–999 | 500 | 比较两种策略并冻结最终选择 |
| 1000–1999 | 1000 | 后续对 STMP 和四个 baseline 使用相同场景作最终比较 |

全部使用原始主实验保存的输出，六档 SNR 为 −4、−2、0、2、4、6 dB；已知相位、估计噪声。
没有新增推断、训练或修改运行中的主实验。新种子的独立校准批次已暂停，其数据不混入本次拟合。

## 选择规则

同一校准集分别拟合每种方法的一个跨 SNR 固定门限、六个估计 SNR 分档门限。
两种策略以六档 SNR 等权的用户错误总数为目标；同错误数依次选虚警更少、门限更小的解。
分档拟合与执行都用接收机实际估计 SNR，最近邻取档，等距离取低档，超出范围取端点，空档用固定门限。
分数转为 float64 后进行 `>=` 判决，防止 float32 标量比较吞掉精确断点。

先写入 POLICIES.json 并冻结哈希，再审核和评估验证集。
默认固定门限；仅在分档减固定总体 AER 差值之 98.75% 配对 bootstrap 区间上界小于零时选分档。
沿用已确定的 10,000 次物理场景重采样，六档 SNR 同时重采样；四个总体比较作 Bonferroni 调整。
逐 SNR AER、漏检、虚警完整保留，不以曲线平滑程度选策略。

## 历史查看情况

前 800 场景已用于既往诊断，因此本次是回顾性的开发集划分，不声称验证完全盲态。
后 1000 场景不参与本次门限拟合或选择，但其中 1040–1057 共 18 场景曾用于早期算法诊断。
所有固定场景仍保留；最终报告需披露这一点，不能称为全新未查看的 1000 场景。
既往暴露清单只是已有记录的下界，见 PLAN.json 的 prior_exposure。

## 运行与产物

```powershell
.\.venv\Scripts\python.exe -B result\snr_comparison\data\baseline_calibration_reuse1000_20261023\test_reuse.py
.\.venv\Scripts\python.exe -B result\snr_comparison\data\baseline_calibration_reuse1000_20261023\run.py check
.\.venv\Scripts\python.exe -B -u result\snr_comparison\data\baseline_calibration_reuse1000_20261023\run.py run
```

首次计划已经冻结，勿重复执行 `plan`。`run` 只读取推断输出；已有完成产物会检查哈希并复用。
逐份核对原输入文件、结果和压缩数组哈希，复现旧活动判决，重算估计 SNR 和 AER。
两阶段共审核 24,000 份 baseline 结果；后 1000 场景的性能不在此脚本中读取。

- PLAN.json、SCENES.csv：场景划分、目标、决策规则与代码哈希。
- calibration/、validation/：可复用的 READOUT_INPUTS.npz、AUDIT.json、REFERENCES.json。
- POLICIES.json：校准得到的两类门限；POLICIES_FROZEN.json 记录验证开始前的冻结时间及哈希。
- RESULT.json、REPORT.md、VALIDATION.csv：验证结果及所有 SNR 的明细。
- FROZEN_READOUT.json：最终选用的精确门限，只供后 1000 场景的后处理使用。
- COMPLETE.json：校准完成标志与文件哈希；不表示主实验或后 1000 场景评估已经完成。

原始求解器配置不切换，避免影响冻结主实验续跑。最终图按 FROZEN_READOUT.json 重算活动判决；
STMP 判决保持不变。原始信道估计及其单场景 NMSE 不变；正式曲线的所有方法均汇总相同的后 1000 场景。
