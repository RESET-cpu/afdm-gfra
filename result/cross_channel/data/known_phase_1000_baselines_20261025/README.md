# 跨信道四 baseline：已完成并核验

2026-10-27：原始推断于北京时间 2026-10-26 23:52 完成；固定历史门限后处理于 2026-10-27 00:41 完成。正式 COMPLETE、全部绑定文件、96000 条结果及 384 万个活动判决均已核验，D 复用部分与原 SNR 的 96 万个判决逐项一致。每条件 1000 MC，D/A/B/C × 六档 SNR × 四方法共 96 组：24000 条复用、72000 条新算。四类信道的 NMSE/AER 图使用全部场景，已核对来源与版式。

采用既有接收机估计 SNR 判决规则，不重新拟合门限，原始 NMSE 不变。场景与门限开发重叠，属回顾性迁移评估；固定几何的表列信道剖面不代表完整时变多普勒谱，并发耗时仅诊断。后续独立运行时间实验仍须单独通过安静资源窗口，不能用本批次并发计时替代。

[正式报告](selected_readout_20261025/REPORT.md) · [四类信道图片](../../figures/baselines_selected_readout_20261027/README.md)

## 历史状态（原文保留）

# 跨信道四 baseline：正在运行

2026-10-26 01:58（北京时间）首次启动。活动概率已完成原始审计、采纳门限汇总与三幅图，进程和共享锁均正常结束后，本批次24条件输入预检PASS。driver **91668**（创建1792951140.0647013）、CPU worker **92792**（创建1792951144.4054163）及启动器91408均已核对；首个新条件四方法结果已完成输入/raw/compact哈希核验。

D/A/B/C × SNR −4/−2/0/2/4/6 dB，每条件1000MC、场景0–999，四baseline共96000条：D复用24000，A/B/C新算72000。40用户、16帧、p=0.1、已知相位、估计噪声；CPU单worker4线程、GPU0。不运行STMP/C-STMP或训练。已启动，**禁止重复启动、重新冻结或自动重试**；实际进度按结果指针计数，不能把STATUS.completed直接加24000。

沿用用户采纳的历史判决规则，门限开发与评估场景重叠，属回顾性迁移评估；并发耗时仅作诊断。保留既有固定几何和表列功率/时延/衰落剖面，不宣称完整时变多普勒谱。完整结果、图、索引核验后才接续运行时间实验。

[运行状态](STATUS.json) · [启动核验](LAUNCH_VERIFICATION.json) · [完整预检](PREFLIGHT.json) · [跟进协议](MONITOR_PROTOCOL.md)

## 准备阶段历史（保留原文）

# 跨信道四 baseline：冻结及只读预检完成，待活动概率收尾

当前状态：**READONLY_PREFLIGHT_PASS_WAITING_ACTIVITY_COMPLETION**。PLAN 与后处理应用已首次冻结，D 信道六档共 24000 条复用输出的完整只读核验通过；尚未启动新推断。活动概率正式结果、图片核验完成且原进程退出后，再执行一次 `validate.py --prepare-inputs`，通过完整 PREFLIGHT 后首次启动。

- D/A/B/C × SNR −4/−2/0/2/4/6 dB，每条件 1000 MC，四 baseline，共 96000 条；24000 复用、72000 新算。
- PLAN SHA256：`99cbe433cfe735878e520b4f648f294d43722e2bab57168c23fe7a7efb8e694c`。
- READOUT_APPLICATION_PLAN SHA256：`235ff4164e6216dc09a5db0b776187205935754021c75172233ed2a5299b9254`。
- 门限按已采纳规则，评估场景与开发重叠，属回顾性迁移评估；并发耗时只作诊断。
- 执行与首次启动门槛见 [MONITOR_PROTOCOL.md](MONITOR_PROTOCOL.md)。禁止重新冻结或自动重试。

## 准备阶段历史原文

# 跨信道四 baseline：待冻结脚本草稿

## Material Passport

- Mode: code experiment preparation
- Verification status: DRAFT；仅脚本和纯逻辑检查，尚未冻结、导入或启动。
- Authorization: 2026-10-25 用户要求按顺序完成所有实验的 baseline 部分。
- Data access: existing raw results read-only; no inference or training in preparation tests.
- Scope: cross_channel / known_phase_1000_baselines_20261025

当前活动概率实验完成并退出后，才可按顺序启动本批次。本目录尚无正式 PLAN、LAUNCH 或任何推断结果。其他批次和冻结资产保持不变。

条件为 D、A、B、C 四种已有信道剖面，各 −4/−2/0/2/4/6 dB，40 用户、16 帧、活动概率 0.1，已知相位、估计噪声。固定场景 0–999，各条件 1000 MC。仅运行 Off-grid SBL、GNN-ASPL、GAMP-SBL、SOMP；CPU 单 worker、4 线程、GPU worker 0，不运行 STMP/C-STMP，不训练。

共 24 条件 × 4 方法 × 1000 = 96000 条。D 的六档直接复用已完成 SNR 批次顶层 sceneNNNN/condition00–05 指针，共 24000 条；A/B/C 新算 72000 条。复用核对 SNR COMPLETE 绑定的 evaluation/REFERENCES.json、原始 JSON/compact、输入身份与输入文件哈希，不能假定旧导频本地副本覆盖六档。原始 SNR 计划固定 SHA256 为 38515a3266879104bf738c4443c35700824e972d17da47eb95bdf56abb38b576，COMPLETE 固定 SHA256 为 e1bb822bc63551ef1bf329f16e3283453e9704d501286a264fa23e1d81856d4e。

沿用已采纳历史判决规则，POLICY SHA256 为 6962b3f99e72532b1962a69dc2a0fabb933da4b59fd280c2e0b900211f89b4bb。Off-grid SBL/SOMP 使用接收机估计 SNR 的最近节点；中点取低档，范围外取端点。GNN-ASPL/GAMP-SBL 用历史固定门限；float64 >=，全零能量不活动。不用真实 SNR 查门限、不重新拟合。门限用 0–499 拟合、500–999 选择，本次 0–999 与开发场景重叠，属于回顾性迁移评估，不是独立测试。

保留既有至少一人活跃的条件抽样，接收机先验为 p/(1-(1-p)^40)，不是实际活跃人数。跨信道沿用 src/evaluation/profiles.py 的表列功率、时延和衰落剖面以及固定几何；共同方向、卫星多普勒和固定接收 SNR 约定不变，不宣称完整时变多普勒谱仿真。并发耗时仅作诊断，不代表独占算法时延。

## 后续执行步骤（本次均未执行）

1. `python -B -X utf8 prepare.py`：一次性验证冻结依赖，生成新 PLAN/应用计划和哈希，按 SNR 完成记录核验并导入 24000 条只读复用指针。不会生成共享输入或启动推断。已有 PLAN 或指针时拒绝覆盖；失败需保留证据，不自动重试。
2. `python -B -X utf8 validate.py --check`：只读核对全部 24000 条复用、输入哈希、原始统计、门限边界及方法排除。只在本目录记录 READONLY_PREFLIGHT，不抢共享锁、不生成共享输入。
3. 前序进程退出并释放共享锁后，`python -B -X utf8 validate.py --prepare-inputs`：持共享锁只准备/检查首场景的 24 个输入；生成 PREFLIGHT，不推断。
4. 主代理完成进程、锁、日志与启动记录核对后，只启动一次本地 `parallel_run.py --plan <本目录绝对PLAN路径>`。启动器须使用项目 .venv，隐藏窗口，并按冻结 parallel_execution.environment 传递 KMP_BLOCKTIME=0、OMP_WAIT_POLICY=PASSIVE、CUDA_VISIBLE_DEVICES 空字符串。保存 PID、创建时间、完整命令行和直接子进程；已有 LAUNCH/运行进程不重启。
5. 等真实 driver/worker 退出，核验 INFERENCE_COMPLETE、RAW_RESULT_AUDIT、全部 96000 唯一结果及输入/原始/compact 哈希后，执行本地 `finalize.py` 一次。`--check` 仅验证已有绑定。输出 selected_readout_20261025，仅重算活动判决，NMSE 不变。
6. 若已有 selected_readout COMPLETE，验证全部绑定并跳过；若输出目录存在但无有效 COMPLETE 或有相关 READOUT_RUNNING.lock，保留现场，不自动重试。最终更新索引及画图由主代理处理；用新 SUMMARY 并披露重叠。

失败不改冻结文件、不重写哈希、不删锁、不改参数、不自行重试。STATUS.completed 仅包含已访问复用指针，进度必须统计实际可用 scene/condition/方法.json，不能直接加 24000。
