# 导频旧 2000 场景计划：已停用

> 2026-10-23 更新：用户改为前 1000 场景。本目录已删除超范围的 2193 份复制结果，现保留 scene0000–scene0999、每方法 1000 份，共 5000 份。详见 `TRIM_TO_1000.json` 和 `DISPOSITION.json`。`STOP.json` 阻止旧计划启动；冻结计划及源码未改动。现行执行入口为[新导频批次](../known_phase_1000_20261023/README.md)，并接续[用户数批次](../../../user_count/data/known_phase_1000_20261023/README.md)。下文为裁剪前的历史准备记录，7193、2000 场景及旧启动命令均不再代表当前安排。

用户于 2026-10-23 授权：当前 SNR 实验结束后运行导频实验，先复制可复用结果，再补跑缺失数据。
本批次尚未开始推断。准备期间用户在“分析STMP与十层展开算法优劣”中追加要求：
先暂停整个实验，用编号 1000–1499 的 500 个场景校准 baseline 门限，再重画前 1000 场景。
源 SNR 已于 23:15 正常暂停，本聊天自动跟进 `snr` 因此也已暂停。
当前已复制并校验 **7193 份**重合结果（STMP 1185，四个 baseline 各 1502）。
计划和副本全部保留；恢复接续前须与校准后的比较设置对齐，不能把旧门限结果直接冒充校准后的结果。
当前处置和暂停依据见 `DISPOSITION.json`。

## 实验配置

- 2000 个固定场景，编号 scene0000 至 scene1999，沿用原场景种子。
- 导频帧数：8、16、24、32、40、48；固定 0 dB、40 用户、活动概率 0.1、D 信道、DFT 导频。
- 已知相位（模拟真值）、估计噪声；方法为 STMP、Off-grid SBL、GNN-ASPL、GAMP-SBL、SOMP。
- STMP 与正在运行的 SNR 实验完全相同：最少 60 轮、最多 600 轮、相对变化阈值 0.0005；权重、阻尼、其余阈值及算法实现不变。
- 四个 GPU 工作进程、一个 CPU 工作进程，每个工作进程四线程，PASSIVE 等待，七天运行上限。

## 复制与复用

源计划是 `result/main2000_known_phase_20261023/snr_comparison_passive/PLAN.json`。
源 `condition02`（16 帧、0 dB）与本批次 `condition01` 完全相同。
完整重合为 2000 × 5 = **10000 份结果**，其余五档需新算 **50000 次推断**；全批次汇总仍为 60000 份。

准备阶段先复制当前已完成的重合结果；源 SNR 全部完成后再次导入，校验既有副本并补齐余下结果。
`imported_results/` 存放实际复制的结果 JSON、紧凑 NPZ、算法诊断及 scene0000 的完整预测，保持源文件字节、runtime 身份及原计时。
`scene*/condition01/` 中的结果指针指向这些本地副本，逐项来源和哈希见 `IMPORTED_RESULTS.json`。
输入仍从原 `shared/inputs/` 读取，逐项校验 READY 身份及原始观测、公共输入、真值和相位文件哈希；READY 凭据另外复制到 `input_receipts/`。
其他导频数使用对应条件的独立输入缓存键，不能当作同一份观测。

复用检查涵盖场景种子、物理工况、相位/噪声信息、算法完整配置、权重绑定、输入身份、运行后端及重复次数。
原 SNR 包含两个合法运行阶段；导入记录保留各自原身份，不改写成新运行。
跨实验共享场景不是独立重复样本。并发计时含资源竞争，不能作为独占算法时延。

## 自动接续

本聊天的自动跟进已配置但当前暂停。原定调用为：

```powershell
& .\.venv\Scripts\python.exe -B result/pilot_frames/data/known_phase_2000_20261023/start_when_ready.py --start
```

入口先等待源 SNR 的 STATUS 为 COMPLETE、60000 份结果完整、汇总文件哈希通过、原进程退出、共享缓存锁释放。
然后补齐并核验 10000 份复制，隐藏启动本批次独立 `parallel_run.py`，仅派发没有结果的任务。
`LAUNCH.json` 的排他创建防止重复启动；已有启动凭据但进程异常结束时不会自动重试。
源实验或本批次失败、被停止时保留记录并报告，不跳过条件、删样本、改参数或启动其他实验。

只检查、不启动：

```powershell
& .\.venv\Scripts\python.exe -B result/pilot_frames/data/known_phase_2000_20261023/start_when_ready.py
```

本地自动跟进需要 Codex 应用保持运行，电脑保持开机、唤醒。自动接续尚未发生时可暂停本聊天自动跟进；
已启动后如需正常停止，在本目录放置 `STOP.json`，调度器停止派发并等待已派发任务结束。

## 文件与核验

- `PLAN.json`、`PLAN_HASH.json`：独立冻结计划，不覆盖 SNR 或旧导频计划。
- `SOURCE_SNAPSHOT.json`、`source_snapshot.zip`：代码和配置快照；权重由计划的路径及哈希绑定。
- `PREPARATION_AUDIT.json`：无推断检查、复用进度及自动跟进凭据。
- `LAUNCH.json`、`STATUS.json`、`stdout.log`、`stderr.log`、`workers/`：启动后运行状态。
- `SUMMARY.json`、`RESULT_AUDIT.json`、`COMPLETE.json`：完成后的汇总与核验。

准备核验只检查源码、配置、真实已有结果以及错误输入/提前启动/重复启动分支，不在 SNR 运行时启动导频推断。
本批次运行完成前，不把准备通过声称为导频实验完成。

## Material Passport

Origin: academic-research-suite / experiment-agent；Mode: run；Version: pilot_known_phase_2000。
Verification: prepared and checked without inference；执行进度以运行文件为准。
