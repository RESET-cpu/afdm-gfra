# 白噪声导频数扫描

按 2026-11-07 作者授权，在独立白噪声代码主线下使用原保存的 500 个场景，导频数为 8、16、24、32、40、48。每点包含 GP-MP 已知相位、GP-MP-EP 估计相位，以及已冻结的 Off-grid SBL 13/25 两档。共 12000 份结果；输入与配置匹配的主 SNR 中心点复用 2000 份，新增 10000 份。

计划和全部科学绑定见 PLAN.json、PLAN_HASH.json；15 项 CPU 检查与四种方法的复用样本全量数组重评分见 CPU_PREPARATION_VALIDATION.json。正式入口为 evaluation.white_followup_20261107.receivers；当前进度见 STATUS.json。旧数据保持原位，新数组保存至 E:\afdm-gfra-results\white_followup_20261107\pilot_frames。

最多三个常驻工作进程，按实际 RAM/VRAM 门控，每个工作进程两个 CPU 线程。不同方法按顺序运行；GP-MP 两种相位使用 GPU，SBL 使用 CPU。保留全部有限迭代上限输出和失败；新失败不自动重试。STOP.json 停止派发并排空工作进程。续跑前必须核对锁、实际进程身份、失败/停止和完整部分结果。

该项完成后仍须保存数组全量重评分、覆盖及来源/输出哈希核验、进程退出核对，然后更新图 7 和必要稿件说明、编译及目视检查，并写入 ADOPTION PASS。此后才能进入用户数扫描。不能仅凭结果数把本项当作已采用。

沙箱内进程列表可能看不到沙箱外的实验进程；确认退出必须在同一宿主权限环境核对 PID、创建时间及完整命令行。archive/white_mainline_20261107/inspect_followup.py 提供只读核对并可在本目录保存监测收据。
