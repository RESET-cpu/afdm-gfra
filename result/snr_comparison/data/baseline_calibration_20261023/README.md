# 四种 baseline 的独立活动门限校准

用户于 2026-10-23 授权开始校准。此批次包含 SOMP、GAMP-SBL、GNN-ASPL、off-grid SBL；
使用现有冻结求解器和权重，只拟合活动判决门限。主实验的代码、配置、输入与结果保持原样。

## 数据与目标

- 校准集：500 个物理场景，种子 202610239300001–202610239300500。
- 验证集：另 500 个物理场景，种子 202610239400001–202610239400500。
- 功能检查：单独 1 个场景，种子 202610239900001，不参与拟合或验证统计。
- 每场景六档 SNR：−4、−2、0、2、4、6 dB，四种方法完全配对。
- 与主实验相同的 40 用户、16 帧、D 信道、DFT 导频、已知相位、估计噪声条件。
- 物理生成器保持主实验的非空活动条件；不依据性能或计算时间删除、替换场景。
- 同一物理场景在六档 SNR 下共享信道、活动、导频、相位和标准化噪声。

每种方法使用其原有归一化能量分数：前三种为系数能量，off-grid SBL 为重建信道能量。
不能将这些分数称为活动后验概率。目标为六档 SNR 等权的用户判决错误总数，
同错误数时依次选择虚警更少、数值更小的门限。用精确分数断点扫描，保留 `>=` 判决。
候选判决将原生保存分数转为 float64，再与门限比较，避免 float32 标量转换吞掉相邻断点。

比较两个策略：每种方法一个跨 SNR 固定门限；每种方法六个估计 SNR 分档门限。
分档拟合与使用均依据接收机实际使用的观测估计 SNR，不能用真实 SNR 选档。
节点为 −4 至 6 dB，最近邻、相等距离取低档、范围外取端点，空档回退到固定门限。
两者使用完全相同的校准样本，不为分档额外增加数据。

## 验证与选用规则

校准结束先保存并哈希冻结 POLICIES.json，再运行验证集。程序自动完成审核和比较。
配对 bootstrap 以物理场景重采样，保留六档 SNR 的相关性；共 10,000 次。
默认建议固定门限；仅当分档减固定的总体 AER 差值之 98.75% 区间上界小于零，才建议分档。
四种方法的总体比较作 Bonferroni 调整。各 SNR、漏检和虚警完整报告，单点区间仅供描述。
不以曲线平滑程度选用门限，不在验证集上重新拟合数值门限。
验证集也参与策略选择，所选策略的验证性能不能称为未使用过的最终测试。
这轮不会自动将候选门限写入主实验，完成后由研究结论决定采用方式。

## 执行及文件

```powershell
.\.venv\Scripts\python.exe -B result\snr_comparison\data\baseline_calibration_20261023\test_calibration.py
.\.venv\Scripts\python.exe -B result\snr_comparison\data\baseline_calibration_20261023\run.py plan
.\.venv\Scripts\python.exe -B -u result\snr_comparison\data\baseline_calibration_20261023\run.py smoke
.\.venv\Scripts\python.exe -B -u result\snr_comparison\data\baseline_calibration_20261023\run.py run
```

使用一路 CPU、4 线程、PASSIVE 等待，不创建 GPU 任务。并发耗时不是独占设备时延。
STATUS.json 每份方法结果更新；stdout.log 每完成物理场景记录一次。
支持中断后用相同 `run` 命令复用已校验结果；失败保留 traceback 和所有已产生数据。
STOP.json 只控制本批次在下一方法开始前退出，不能用于控制主实验。

PLAN.json、SCENES.csv 固定工况、场景和选择规则；shared/ 保存独立输入与预测；
calibration/、validation/ 保存结果引用、READOUT_INPUTS.npz 与完整 AUDIT.json。
最终 POLICIES.json、RESULT.json、REPORT.md、COMPLETE.json 给出门限、配对验证和文件哈希。
源码及全部冻结依赖以 PLAN.json 的 assets 字段绑定，run.py check 可核验。

文献及术语依据沿用 paper/docs/BASELINE_ACTIVITY_READOUT.md、paper/docs/TERMINOLOGY.md。
