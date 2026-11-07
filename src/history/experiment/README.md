> 2026-10-21 最终代码整理已完成。当前维护入口见[最终版本](../src/afdm_jadcedd/evaluation/README.md)；下文保留整理前的说明及历史路径。

# 当前实验入口（2026-10-21）

当前学习接收机保留最终 **十层 L-STMP** 与 **旧三网络**；按用户最新要求，旧三网络暂不执行。
常规对比默认运行十层、Off-grid SBL、GNN-ASPL、GAMP-SBL、SOMP。
十层固定使用完成训练后由原验证集选出的 depth 10 / epoch 1；不根据测试结果换权重或门限。
`MAINLINE.json` 的历史冻结记录没有被覆盖。

| 实验 | 入口 | 正式规模及条件 | 当前状态 |
|---|---|---|---|
| SNR | `snr_comparison.py` | 每点2000；−4、−2、0、2、4、6 dB | 接入十层与四个基线 |
| 导频数 | `pilot_frames.py` | 每点2000；8、16、24、32、40、48 | 接入十层与四个基线 |
| 用户数 | `user_count.py` | 每点2000；20、40、60、80、100 | 接入十层与四个基线 |
| 活动概率 | `activity_probability.py` | 每点2000；0.05、0.10、0.15、0.20、0.25 | 接入十层与四个基线 |
| 运行时间与精度 | `runtime_comparison.py` | 固定前20个共享场景；−4、0、4 dB；每场景测3次 | 替代收敛曲线 |
| 独立去噪 | `channel_denoising.py` | 2000场景×4候选信道；复噪声方差0.001至100 | 只测预训练一阶网络 |
| 跨信道 | `cross_channel.py` | D/A/B/C四种NTN-TDL；六档SNR；每点2000 | 接入十层与四个基线 |
| 密度比消融 | `density_ratio_ablation.py` | 每点2000；−4至8 dB | 依赖旧三网络，暂缓执行 |

共享的2000个物理场景种子是202610219100001—202610219102000。同一场景、同一工况在所有实验中使用同一份观测及相位估计；同一输入/方法的已完成结果只按身份校验复用。
场景数和共享规则来自已冻结的 `results/lstmp_v3_shared2000_20261021/PLAN.json`。该原计划保留原字节；当前运行计划另行记录用户后来确认的改动：预训练一阶网络去噪、运行时间替代收敛、暂缓旧三网络。

除扫描项外，40用户、16导频、0 dB、活动抽样概率0.1；正式接收机均估计相位和噪声。真实信道及活动仅用于观测生成和独立评分。
独立去噪使用已知AWGN方差，比较预训练一阶网络、噪声输入、Gaussian参考和显式使用真实几何/LOS信息的genie参考；不调用十层中的逐层网络、二阶网络或活动网络。
密度比消融的受控两臂属于旧三网络，十层完整接收机只是参考，不将结构不同的比较冒称单因素消融。

## 执行

在项目目录的PowerShell中：

```powershell
# 只冻结计划，不运行实验；默认新输出位于 results/lstmp_v3_formal2000_20261021/<实验名>
& .\.venv\Scripts\python.exe -B experiment/snr_comparison.py plan
& .\.venv\Scripts\python.exe -B experiment/snr_comparison.py inspect
& .\.venv\Scripts\python.exe -B experiment/snr_comparison.py run
& .\.venv\Scripts\python.exe -B experiment/snr_comparison.py summarize

# 独立检查场景，不接触2000个正式场景
& .\.venv\Scripts\python.exe -B experiment/pilot_frames.py plan --smoke --output results/pilot_smoke_new
& .\.venv\Scripts\python.exe -B experiment/pilot_frames.py run --output results/pilot_smoke_new
```

其他实验替换入口文件即可。`plan`需要空目录；`run`只读取保存的计划，可继续尚未完成的场景；已有COMPLETE不重复推断。`--values`修改扫描点，跨信道和运行时间用`--snr`；跨信道也支持`--profiles`。正式规模为2000，减少规模必须显式使用`--smoke`，后者使用独立种子202610219900001起。

旧三网络默认不跑。将来需要恢复它的实验时，可以在**新计划**中显式加入`--include-legacy`；本次不会使用该选项。密度比消融在未加入该选项时只生成暂缓计划，`run`返回DEFERRED_BY_USER。

## 计时及解释

十层使用CUDA FP32、关闭TF32；原有四个数值基线保留其原生CPU实现。报告逐方法标注实际后端，CPU/GPU跨后端时延比不能解释为纯算法加速。旧三网络接入保留CUDA选项。

运行时间实验按预定20个物理场景配对，独立场景预热，在每次测量前后同步CUDA，每输入重复3次取中位数，再报告跨场景均值、P50和P95。预测与其他性能实验使用相同冻结权重和判决规则；重复计时不增加独立统计样本数。普通性能扫描也保存一次同步时延，运行时间实验使用独立测量记录，不直接复用普通扫描的计时。

分别报告接收机推理时间、公共相位估计时间及两者之和。显存测量前其他学习接收机移到CPU；输入生成、磁盘读写和模型加载不计入推理时间。参数量、显存和时延分别列出，不能用固定十层直接推导“复杂度全面降低”。

所有结果保留逐场景错误个数、能量和输入/权重/源码哈希。完成时复核每个计划结果，计算汇总AER、漏检、虚警、信道NMSE，以及10000次以物理场景为单位的配对重抽样区间；同一组场景跨实验共用，不能视作独立重复确认。单场景检查不计算置信区间。

## 实现与历史

当前执行代码在 `experiments/lstmp_evaluation_2000_20261021/`，模型绑定为其中`models.json`。公开入口分派到这套流程；较早文件内的辅助函数用于复用已验证的物理模型与统计，不再决定新计划的模型与种子。

修改前的八项入口和辅助源码保存在 `results/experiment_integration_20261021/before/`。初次Windows路径身份检查失败及其记录保留；修复只统一哈希清单的路径分隔符，没有绕过权重、求解器或阈值校验。历史收敛图与比较报告保留，`convergence.py`的新执行已停用。

所有正式运行计划与当前小规模检查是不同产物；只有完成2000场景后才能报告全量实验结论。

当前七项启用入口已通过184条小规模检查记录；标准工况跨五个入口复用同一份输入与预测，旧权重删除后十层输出与原保存结果核对一致。检查规模、失败记录、清理清单和正式计划入口见[接入核验报告](../results/experiment_integration_20261021/REPORT.md)。正式计划已冻结，尚未启动全量推断；密度比消融随旧三网络暂缓。
