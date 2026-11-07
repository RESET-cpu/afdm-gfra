# 独立相位前端：主 SNR 1000 场景配对实验

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: run / validate
- Origin Date: 2026-11-03
- Version Label: c_stmp_phase_frontend_1000_20261103
- Verification Status: PREPARING；实际运行状态见 STATUS.json，完整核验见 COMPLETION.json。
- Material: 已保存的模拟观测与冻结接收机；真实信道、活动和相位仅在推断后的评分中使用。

沿用 `C_STMP_phase_frontend_20261027`：从原始观测和导频估计一次相位，随后固定相位，运行原 C-STMP 条件接收机。原相位前端仍含物理时延、多普勒拟合；本次不优化或替换该前端，不修改网络、阻尼、60–600 轮停止条件或正式主线。

用户本轮要求使用主 SNR 的 1000 个场景，原话及范围保存在 AUTHORIZATION.json。原小样本绑定中的授权字段保留历史值；新批次单独保存授权和计划。

## 配对范围

- 场景 0–999，SNR 为 −4、−2、0、2、4、6 dB，每档 1000 个，共 6000 份新前端推断。
- 直接复用 `c_stmp_variance_em_1000_snr_m4_p6_20261025` 的原始观测、导频、噪声实现和 6000 份已知相位预测。
- 主比较为 1000 场景的前端固定相位与已知相位。后者明确使用真实相位构造算子，属于 oracle 参照。
- 前 500 场景另与已完成 `c_stmp_phase_selected_500_20261030` 的迭代相位版配对；不能把其 500 场景曲线当作 1000 场景对照。
- 不复用原九组 CPU 前端预测；首个新 CUDA 输入与原 scene0/−4 dB 固定容差复现比较，通过后继续。它计入正式 6000 份。
- 另一固定相位十例诊断采用不同停止规则，不并入本批。其已出现错误，故本次不预设取消相位更新能消除 AER 退化。

## 执行与结果

入口：项目 Python 执行本目录 `run.py prepare`，再执行 `run.py run`。独立输出数组保存在 `E:/afdm-gfra-results/c_stmp_phase_frontend_1000_20261103/`，本目录保存冻结计划、逐例指针、状态、日志、汇总和图。

单个 CUDA 推断进程，每份输入完成后退出释放内存；每进程两个 CPU 计算线程。每份输入硬超时两小时，总派发期限七天。运行错误保留完整记录并停止后续派发，不自动重试。在本目录创建 STOP.json 会使当前输入保存完成后停止派发。

STATUS.json 每十秒更新。WORKER_STATUS.json 给出当前相位前端或条件接收机进度。host_stdout.log、host_stderr.log、worker.log 保留执行日志。6000 份推断完成后自动执行 report.py，核验完整覆盖、输入和预测哈希，重新评分所有配对数组，生成：

- SUMMARY.json、SNR.csv、per_case.csv：分 SNR 的漏检、虚警、AER、能量合并 NMSE、迭代及未收敛计数。
- HIGH_SNR_REGRESSIONS.csv：4、6 dB 全部新增错误用户与纠正用户，包含总错误数相同但错误用户变化的输入。
- REPORT.md 及 figures/：主 1000 场景比较与前 500 三方法比较分别呈现。
- COMPLETION.json：PASS 仅表示覆盖和数值记录核验完成，不等于性能达到已知相位水平。

所有有限迭代上限输出保留，包括已知相位参照 −4 dB 的三份上限输出。相位评分使用真实活动用户的 q=1,…,Q−1，q=0 不计入均值。

这批场景已用于历史研究和部分针对性诊断，是回顾性配对评估，不是未接触的验证集。六档 SNR 共享 1000 个物理场景，不能当作 6000 个独立物理场景。记录的前端和后端耗时不作严格独占速度基准。

## 首例复现未通过

本次启动未派发第二个输入。新增批次入口遗漏统一GPU精度设置，首例未通过原复现容差；原计划、源码及输出完整保留。修正入口与当前批次位于同级 `c_stmp_phase_frontend_1000_20261103_v2/`，见其REVISION.json与STATUS.json。
