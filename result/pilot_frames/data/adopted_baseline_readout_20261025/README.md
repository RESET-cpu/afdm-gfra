# 已完成：导频四 baseline 采纳门限汇总

2026-10-26：首次后处理正常退出；24,000结果、6,000输入、24组各1,000场景、全部绑定文件核验通过。自己的READOUT锁已正常释放。

[正式报告](selected_readout_20261025/REPORT.md) · [完成证书](selected_readout_20261025/COMPLETE.json) · [图片](../../figures/baselines_selected_readout_20261025/pilot_frames_baselines.png)。本次新增推断0，沿用既有4000公共条件复用及20000导频推断；原始结果/NMSE不变。场景与门限开发重叠，属回顾性迁移评估。不得再次调用评分来重写正式结果。

以下为冻结、执行及准备历史。

# 当前状态：独立应用已首次冻结，正在生成采纳门限结果

应用 SHA256：`c9dd25190e86b387e8f45235185b48e463f211d9f7a202334046ffa9ee3cb060`。原始导频推断已完成，本次只做既有数据核验与活动判决后处理；新增推断0。执行记录见 `APPLY.log`。完成前不把派生汇总视为正式结果。

以下准备记录保留为历史。

# 导频 baseline 历史门限应用（待审阅，尚未冻结）

本目录独立准备用户采纳的历史混合判决规则，不覆盖旧导频 PLAN、代码、原始推断、完成证书或图。

- 原始来源：`../known_phase_1000_20261023/`。原批次包含五方法，本应用只读取四个 baseline：Off-grid SBL、GNN-ASPL、GAMP-SBL、SOMP。
- 导频帧数8/16/24/32/40/48，每条件固定场景0–999、1000 MC；40用户、活动概率0.1、SNR 0 dB、D信道、DFT导频、已知相位（模拟真值）、估计噪声。
- 本次24,000条全部取自既有输出。其中16帧的4,000条原本复用SNR公共条件，其他20,000条在已完成导频批次中推断；本次新增推断为0。
- 默认策略是 `result/BASELINE_READOUT.json` 指向的 POLICY，SHA256 `6962b3f99e72532b1962a69dc2a0fabb933da4b59fd280c2e0b900211f89b4bb`。
- Off-grid SBL/SOMP按接收机估计SNR最近节点−4/−2/0/2/4/6查表，中点取低档、范围外端点；GNN/GAMP历史固定门限。保存分数转float64，采用`>=`；全零能量判不活动。不使用仿真SNR查表、不重拟合、不训练。
- 门限0–499拟合、500–999选择，与本次0–999物理场景重叠，属于回顾性迁移评估，不是独立测试。并发耗时只作诊断。

## 审阅与运行边界

`APPLICATION_DRAFT.json` 是带当前候选实现/来源哈希的审阅草案，状态为 `DRAFT_NOT_FROZEN`，不是冻结执行授权；尚无正式 `READOUT_APPLICATION_PLAN.json` 或其HASH。

`finalize.py --check --draft` 只检查已有绑定；`--audit --draft` 核验完整24,000指针、原始JSON、compact、原活动判决与误差能量，以及6,000个输入收据所绑定的文件，不应用新门限。`validate.py` 仅做AST和合成边界检查。准备阶段不创建`selected_readout_20261025/`。

审阅通过后，由主代理将最终应用写为 `READOUT_APPLICATION_PLAN.json`（状态`FROZEN`），冻结最终实现和依赖哈希并保存 `READOUT_APPLICATION_PLAN_HASH.json`。不得通过重新冻结来绕过已有绑定失败。随后只调用一次本目录 `finalize.py --apply`。它会先核验所有原始资料，再仅生成本目录下的 `selected_readout_20261025/`：报告、SUMMARY、DECISIONS、逐场景实际门限、输入/结果引用、审计与COMPLETE。

相关真实driver/finalizer或READOUT锁存在时不执行；若派生目录已有有效COMPLETE则只核验并返回，若已存在但无有效COMPLETE则保留并停止，不自动重试。错误保留FAILURE和本进程锁；不会删除旧锁或恢复旧队列。原始目录不写入任何文件。

独立应用按已冻结原始证书、算法标识和实际保存字节验证数据，不执行原接收机，也不要求历史无关绘图代码仍与当时一致。完整预测矩阵无需重载：原始JSON与compact逐项哈希校验，原误差能量/活动判决复核，评分只修改`misses`、`false_alarms`和活动判决；NMSE及信道结果保持原样。

## 准备核验记录

`PREPARATION_AUDIT.json`：24,000条四baseline输出、6,000套输入的完整只读核验通过，24组各1,000场景；4,000条公共条件复用、20,000条既有导频推断，未进行新评分或推断。

`PREPARATION_TESTS_REVIEWED.json`：13项轻量检查通过；包含Windows相同参数祖先launcher允许、外部重复进程拒绝，旧worker命令行/父进程/创建时间匹配与PID复用区分，以及24组完整覆盖检查。此后只增强进程保护与派生完成核验，原始数据核验逻辑保持不变，没有重复全量读取。

完成核验会检查应用/源证书与文件哈希、24组精确条件、24,000个唯一场景结果、6,000个输入引用、决策阵列、汇总计数与原始NMSE不变。正式派生结果尚未产生，需主代理首次审阅冻结后执行。SNR当前入口由主代理独立处理，本目录不修改SNR资产。
