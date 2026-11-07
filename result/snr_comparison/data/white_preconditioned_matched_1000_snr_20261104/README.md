# 白噪声配套网络：主 SNR 对照评估

2026-11-05，用户明确要求开始。独立后台协调器于 09:28 启动，实时状态以 `STATUS.json` 为准。

使用白噪声去噪器第 200 轮和配套分类器第 79 轮。两者分别完成 200/100 轮训练，训练预算、所选权重、教师绑定、来源与固定验证集选模均已核验，详见 `PREPARATION_CHECK.json`。独立配置为 `src/configs/candidates/GP_MP_white_preconditioned_matched_20261104.json`，适配器仅核验原生白噪声训练记录并绑定权重，直接继承原接收机的 `infer` 方法。数值控制与保存的 `EVALUATION_PLAN.json` 一致。

复用主 SNR 保存输入：场景 0–999，−4/−2/0/2/4/6 dB，共 6000 项；K=40、Q=16、p=0.1、NTN-TDL-D，已知相位、观测估计噪声。`INPUTS.json` 与 `REFERENCES.json` 冻结输入和同输入有色 CGP-MP 参照。信道、活动真值仅在推断与预测保存后读取评分。已知相位是双方明确共享的 oracle 条件。

协调器先执行场景 0、−4 dB 的完整推断预检，再自动派发全部正式任务；预检结果不计入 6000 项。使用 CUDA，最多两个工作进程、每份输入独立进程、每进程两个 CPU 数值线程；启动需满足 RAM 和 GPU 显存余量。当前并行 SBL 队列保持独立。内存等待属于正常状态，详细预算见 `PLAN.json`。失败或 `STOP.json` 停止进一步派发，保留正在运行的结果和失败记录；不自动重试。

结果数组位于 `E:/afdm-gfra-results/white_preconditioned_matched_1000_snr_20261104`；本目录 `results/` 保存指针。启动命令和进程身份见 `LAUNCH.json`，完整推断预检见 `PREFLIGHT.json`。执行源码在 `src/evaluation/white_matched_20261105/`，源码、配置、权重与输入清单哈希列于冻结计划中。

完成全部推断后协调器自动重读保存预测，核对覆盖、输入身份及文件哈希并重新评分，生成 `SUMMARY.json`、`PAIRED_CASES.csv`、`OUTPUT_HASHES.json`、`COMPLETION.json` 和独立比较图。NMSE 使用累计完整信道误差能量除以累计真值活动信道能量；AER 使用全部设备判决，另保留漏检、虚警、迭代数和未收敛数。所有有限迭代上限输出保留。完整结束还需核实协调器退出。

这些场景是历史研究场景，不能视作从未用于开发的测试集；并发墙钟时间不能作为独立算法时延。独立结果不自动替换论文图片或冻结主线。
