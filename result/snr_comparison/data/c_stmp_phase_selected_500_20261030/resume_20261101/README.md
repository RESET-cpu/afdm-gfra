# 2026-11-01 显式续跑

用户请求：`没事那你先续跑，我不在电脑旁边没法操作`。
北京时间2026-11-01 13:18启动，保留654份结果，只执行剩余2346份输入。
当前状态见本目录及上一级的 `STATUS.json`；启动不代表实验完成。

## 执行

- 入口：项目Python执行 `result/snr_comparison/data/c_stmp_phase_selected_500_20261030/resume_20261101.py run`。
- 单个GPU推断进程，每进程2个CPU线程；每份输入新建进程，完成后退出释放资源。
- 新输出：`E:/afdm-gfra-results/c_stmp_phase_selected_500_20261030/resume_20261101/`。
- 原scene108的condition01、02失败目录保留，本次重试写入上述独立目录。
- 新结果核验并重评分后，向原 `results/` 增加指针；不改写已有指针。
- 每份输入沿用原两小时硬超时，派发期限为七天。失败停止派发，不自动重试。
- 本目录或上一级的 `STOP.json` 会让当前输入完成保存后停止派发。
- 日志为 `host_stdout.log`、`host_stderr.log` 和 `worker.log`；状态每十秒更新进程和内存信息。

## 保留与验证

`PREVIOUS_STATUS.json`、`PREVIOUS_START.json` 保存原失败状态和启动记录。
原失败日志及输出目录保持原位。`PRESERVED_OUTPUTS.json` 记录654份已有结果及其文件哈希；
准备阶段核对312项原冻结依赖，以及已有结果指针、结果记录、预测、运行记录和输入清单的哈希。
准备阶段未重新评分已有654份预测，全部重评分留在原完成核验中执行。

本次计划单独保存在 `PLAN.json`，绑定恢复脚本及授权记录。原实验的 `PLAN.json`、
算法、配置、权重及报告脚本不变。达到迭代上限的有限结果继续保留。
完整覆盖3000份结果后，自动执行原 `report.py`，核验并重评分新相位、旧相位和已知相位
共9000份预测，生成原定汇总和独立比较图；同时核对既有结果未被改写。
只有上一级及本目录的 `COMPLETION.json` 为 `PASS` 才确认本次完成。

## Material Passport

- Workflow: academic-research-suite / experiment-agent / run, inline execution
- State: explicitly resumed; completion requires saved audit receipts
- Material: existing simulated observations and frozen receiver; truth used only for scoring
- Change: orchestration concurrency and process lifetime only
- Verification: original asset hashes and preserved output hashes checked before launch; new outputs re-scored before acceptance
