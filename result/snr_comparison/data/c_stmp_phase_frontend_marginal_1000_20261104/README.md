# 新相位前端：1000 场景主 SNR 实验

用户授权：2026-11-04「可以，那请你开始1000场景的主SNR实验把」。

冻结方案：`C_STMP_phase_frontend_marginal_20261104`，使用原观测和已知导频，
先以冻结的边缘似然初始化器估计一次相位，之后固定相位运行原 C-STMP 条件接收机。
前端拟合的功率、增益和活动判决不传入后端。每轮相位更新次数为零。
本批次不训练，不改变 FINAL/MAINLINE，不续跑已停止的旧前端批次。

## 输入和比较

- 物理场景 0–999；每场景 SNR 为 −4、−2、0、2、4、6 dB，共 6000 次全新推断。
- 主比较：相同输入、相同后端与权重的 6000 份已知相位结果（oracle 相位参照）。
- 前 500 场景另给三方法配对比较：新前端固定相位、历史迭代相位方案、已知相位。
- 复用历史输入与基准输出，不复用新候选的预测。历史场景不称为未触碰的独立验证集。
- 推断仅加载 raw.npz 中的 y、pilot、公共 rho；噪声从观测估计。
  文件字节哈希可在推断前读取；活动、信道、相位真值在预测保存后才解析评分。

## 运行

`run.py prepare` 冻结代码、配置、权重、输入与参照清单；`run.py run` 启动调度。
先单独重新推断 scene 0 / 4 dB，与已有小规模新前端结果核对。
启动复现阈值见 PLAN.json，阈值在推断前冻结，之后按场景和 SNR 索引升序运行剩余输入。

RTX 5080 CUDA，关闭 TF32 和 cuDNN benchmark，每进程 2 个 CPU 线程。
每份输入使用新进程，最多并行 4 个，按可用内存和预计进程增长预留内存。
状态文件按输入隔离，仅调度器写总状态。状态发布短暂冲突可重试，推断与科学输出不自动重试。
单输入限时 2 小时；调度期限从启动起 7 天。STOP.json 停止派发并等待已有任务保存。
执行失败停止新派发、保留已有输出及错误记录。有限但达到 600 次迭代上限的输出照常纳入统计。

结果数组保存至 `E:/afdm-gfra-results/c_stmp_phase_frontend_marginal_1000_20261104`；
本目录保留计划、日志、状态、结果指针及汇总。完成后自动运行 report.py 重新评分与核对覆盖。

## 预定汇总

AER 为全部漏检加误检除以用户决策数。NMSE 为总误差能量除以总信道能量后转 dB。
同时报告每档 SNR 的漏检、误检、迭代数、未收敛数和配对变化。
4/6 dB 全部新增错误用户单列，即使新增错误与纠正错误抵消，也不遗漏。
部分结果标为 PARTIAL；同场景六档 SNR 不视为六个独立物理场景。
COMPLETION 的 PASS 仅表示覆盖、哈希、保存数组评分通过，不预设性能通过。
并发运行耗时为运行记录，不作为严格控制硬件条件的速度比较。

## Material Passport

- Workflow: academic-research-suite / experiment-agent / run, then validate
- Material: simulated observations; frozen candidate; stored oracle and iterative references
- Verification Status: plan frozen by prepare; live execution status in STATUS.json
- Study scope: retrospective paired main SNR experiment; no training or mainline replacement
- Evidence: PLAN.json, INPUTS.json, REFERENCES.json, STARTUP_VALIDATION.json, STATUS.json
- Run ledger: README_run_ledger.yaml; launch receipts do not claim experiment completion
