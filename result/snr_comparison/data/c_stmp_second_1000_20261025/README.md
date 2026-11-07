# C-STMP新二阶网络：1000场景SNR实验

**当前状态：尚未启动完整8000次推断；用户已选择先排查。** 八档预检已完成，接口和场景200、0dB回归通过，但8/10dB均600轮未收敛、AER87.5%；详见`READINESS.json`。`PREFLIGHT.json`中的PASS仅表示接口/复现检查通过，不表示接收机在八档SNR下稳定。独立排查记录位于`../c_stmp_stability_20261025/`，本目录仍保留原0.4配置及失败输出；后续不同参数必须使用新的冻结计划，不能混入这里。

**排查已完成：** 新消息权重0.2修复了已观察到的场景200振荡，并通过四个新随机场景×八档SNR的有限稳定性检查。新候选为`src/configs/candidates/C_STMP_second_damping02_20261025.json`，只修改阻尼；原权重和分类器未训练。见[完整报告](../c_stmp_stability_20261025/REPORT.md)。下方命令仍属于原0.4计划，不应用于运行新的0.2候选。

用户于2026-10-25授权接入完整JADCE并运行原1000场景SNR实验。每档固定使用场景0–999，SNR为−4、−2、0、2、4、6、8、10 dB，共8000次推断；相位已知、噪声估计、K=40、Q=16、活动先验0.1。

使用新一阶epoch200 EMA、配套二阶epoch96 EMA和原活动分类器，C=vI，门限0.5、阻尼0.4、最少60/最多600轮，其他停止条件不变。本次不训练或调参。STMP、DU和导数方差C-STMP的原实现、权重、结果以及全局绑定保留。

`catalog.json`仅在本实验中把展示名C-STMP绑定到`algorithm.C_STMP.second_receiver:Receiver`；全局算法登记不变。`inference/PLAN.json`由统一实验计划接口生成并冻结，`INPUTS.json`登记全部已保存输入及原STMP结果身份。`source_snapshot.zip`保留运行源码；`PROTECTED.json`记录77项保护资产。

入口：

```powershell
# 核验计划，不运行推断
.\.venv\Scripts\python.exe -B run_experiments.py snr_comparison inspect --output result/snr_comparison/data/c_stmp_second_1000_20261025/inference

# 八档SNR预检，包含场景200、0dB已保存结果的回归检查；首次执行
.\.venv\Scripts\python.exe -B -X utf8 -u result/snr_comparison/data/c_stmp_second_1000_20261025/parallel_run.py preflight

# 正式执行或经确认后继续未完成部分；只复用校验通过的已完成结果
.\.venv\Scripts\python.exe -B -X utf8 -u result/snr_comparison/data/c_stmp_second_1000_20261025/parallel_run.py run
```

并行驱动使用统一算法构造、完整接收机和`evaluation.suite.receiver_result`评分/序列化接口。4个GPU进程，每进程2个CPU线程，模型驻留；每进程使用场景200、0dB作一次不评分预热。预检完成的8条结果计入正式8000条，不重复计算、不挑选输出。不会生成或写入共享输入；每次读取均检查原文件哈希。预测写入本目录`cache/predictions`，不会争用其他正在执行实验的共享输出锁。

`STATUS.json`记录总体进度、每档SNR完成量和估计剩余时间；`workers/`记录进程和当前输入；`stdout.log`、`stderr.log`保存后台日志。创建本目录`STOP.json`会停止继续派发，等待当前最多4个输入写完。失败保留诊断，不自动重试。未收敛但达到600轮的输入仍保留并统计，不剔除。运行上限7天，超限进入失败记录。

完成后自动核验全部输入/输出，生成`SUMMARY.json`、`AUDIT.json`、`per_scene.csv`和新版本SNR图。主要比较为原STMP的逐场景配对NMSE、AER、漏检、虚警和迭代数，附10000次按物理场景重抽样的区间。历史四个baseline使用`old_first1000_all_fixed_snr10_20261024`已经固定的读出结果，不重新拟合门限；其回顾性校准范围沿用原说明。

此面板部分场景已在此前开发中查看，不称为从未见过的盲态测试。STMP阻尼0.2、C-STMP阻尼0.4，因此比较的是完整接收机。并发运行时间只表示吞吐，不能与历史结果作独占设备的算法时延比较；此前场景200独占重复计时单独保留。

Material Passport：academic-research-suite / experiment-agent，run；数据来自原固定模拟场景，核验状态及完成状态以PREPARATION、PREFLIGHT、STATUS和COMPLETE记录为准。
