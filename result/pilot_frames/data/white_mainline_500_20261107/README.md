# 白噪声导频数扫描

按 2026-11-07 作者授权，在独立白噪声代码主线下使用原保存的 500 个场景，导频数为 8、16、24、32、40、48。每点包含 GP-MP 已知相位、GP-MP-EP 估计相位，以及已冻结的 Off-grid SBL 13/25 两档。共 12000 份结果；输入与配置匹配的主 SNR 中心点复用 2000 份，新增 10000 份。

计划和全部科学绑定见 PLAN.json、PLAN_HASH.json；15 项 CPU 检查与四种方法的复用样本全量数组重评分见 CPU_PREPARATION_VALIDATION.json。正式入口为 `python run_experiments.py white_followup coordinate --stage pilot_frames`；当前进度见 STATUS.json。旧数据保持原位，新数组保存至 E:\afdm-gfra-results\white_followup_20261107\pilot_frames。

最多三个常驻工作进程，按实际 RAM/VRAM 门控，每个工作进程两个 CPU 线程。不同方法按顺序运行；GP-MP 两种相位使用 GPU，SBL 使用 CPU。保留全部有限迭代上限输出和失败；新失败不自动重试。STOP.json 停止派发并排空工作进程。续跑前必须核对锁、实际进程身份、失败/停止和完整部分结果。

该项完成后仍须保存数组全量重评分、覆盖及来源/输出哈希核验、进程退出核对，然后更新图 7 和必要稿件说明、编译及目视检查，并写入 ADOPTION PASS。此后才能进入用户数扫描。不能仅凭结果数把本项当作已采用。

沙箱内进程列表可能看不到沙箱外的实验进程；确认退出必须在同一宿主权限环境核对 PID、创建时间及完整命令行。archive/white_mainline_20261107/inspect_followup.py 提供只读核对并可在本目录保存监测收据。

2026-11-07 22:03：作者要求复跑后，2906 份已有结果均通过重评分和输入/输出校验，任务文件读取增加最多两秒的 PermissionError 等待；27 项相关检查通过。已从原计划启动续跑，剩余 9094 份；原失败记录移入 `delete/pilot_resume_20261107/FAILURE.original.json`，原会话仍保留。接收机、模型、场景和数值控制不变。证据见 `archive/pilot_resume_20261107/`。
