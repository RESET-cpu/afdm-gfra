# 白噪声主线与逐项替换

作者于 2026-11-07 明确授权整理代码、让有色版本退出主线、保留数据，随后补跑后续实验，每项完成后替换对应图稿。

当前代码主线为 `algorithm.GP_MP`，默认登记 GP_MP / GP_MP_EP / pretrained_white_first。旧 C_STMP 标识兼容指向白噪声；历史有色登记保存在 `src/configs/historical/algorithms_colored_20261107.json`，旧源码、权重、数据和冻结计划保持原位。15 项 CPU 检查、16 项 AST 对照、六次 GPU 回放通过，所有回放预测数组逐元素一致。

| 顺序 | 结果目录 | 状态与预算 |
|---|---|---|
| 去噪 | result/channel_denoising/data/white_mainline_500_20261107 | 已完成核验和采用：500 场景、3000 条件、12000 信道查询 |
| 导频数 | result/pilot_frames/data/white_mainline_500_20261107 | 下一项；12000 结果，其中10000新增、2000复用 |
| 用户数 | result/user_count/data/white_mainline_500_20261107 | 等待导频采用；10000 结果，其中8000新增、2000复用 |
| 活动概率 | result/activity_probability/data/white_mainline_500_20261107 | 等待用户数采用；10000 结果，其中8000新增、2000复用 |
| 跨信道 | result/cross_channel/data/white_mainline_500_20261107 | 等待活动概率采用；12000 结果，其中9000新增、3000复用 |

每点500个原场景，三类扫描包括白噪声已知/估计相位及冻结 SBL 13/25；跨信道补白噪声已知相位。原始输入固定，不再生成新的接收机场景。所有新白噪声接收机使用统一阻尼0.4及其原有60–600轮等控制；历史用户数个别替换不带入本次。中心条件须逐份校验全部输入哈希与科学绑定后才能复用。接收机共有35000份新增推断，9000份复用，不按结果挑选。

每项完整保存预测、重评分、检查覆盖、来源和输出哈希。COMPLETION PASS / SUMMARY VERIFIED 后确认协调器与worker退出，再通过 `render_paper.py` 替换当前图源，保留旧图源、其他曲线和样式，并同步必要说明、编译与目视检查。写入 ADOPTION PASS 后才能运行下一项。不要同时启动所有阶段。

当前主 SNR、30 场景收敛和100场景消融均已完成，不恢复原预算。消融由另一聊天负责，不接管或发消息。论文维持工作稿状态，保留已经采纳的摘要、引言、结论及章节修改。

只读入口：`run_experiments.py white_followup inspect`。实际接收机入口：`evaluation.white_followup_20261107.receivers`，每次显式给出stage。新数组写入 `E:/afdm-gfra-results/white_followup_20261107/<stage>`；元数据在上述D盘目录。隐藏启动脚本 `archive/white_mainline_20261107/launch_receiver_stage.ps1` 只接受四个授权阶段，并检查上一项采用与已有启动记录。

最多3个常驻worker，按RAM/VRAM启用；每worker2个CPU线程，模型与输入索引复用。SBL按原协议CPU运行。新失败、暂停、完整部分输出都须保留并诊断，不自动重试；STOP.json用于排空。进程身份必须结合PID、创建时间和完整命令；START/锁/STATE/LAUNCH共同判断。

去噪采用证据在 [paper/C-STMP/checks/white_denoising_adopted_20261107/](https://github.com/RESET-cpu/afdm-gfra/tree/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/white_denoising_adopted_20261107)；主线代码核验在 `archive/white_mainline_20261107/`。实时进度以各阶段STATUS为准，此文件不是完成凭据。
