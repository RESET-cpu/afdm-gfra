# Off-grid 600 轮与 Proposed：10 场景配对补测

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: run
- Origin Date: 2026-10-18
- Verification Status: ANALYZED
- Version Label: offgrid600_reuse10_v1

## 范围与复用

固定原 500 场景中的 scene000–scene009，在 0 dB、40 用户、16 导频帧、16 天线下补跑 Off-grid SBL 600 轮。复用 10 份观测/相位与 20 份 Proposed、Off-grid 120 轮结果，没有重新运行这两种比较方法。阈值不变，未重新标定。
所有新输入逐字段哈希与原记录一致；10 条 Off-grid 轨迹的前 120 轮与历史轨迹逐项完全一致；完整新预测均独立重新评分通过。

| 方法 | 完整信道 NMSE/dB | AER | 漏检/虚警 | 平均轮数 | 停止情况 |
|---|---:|---:|---:|---:|---|
| Off-grid 120（复用） | -8.1458 | 0.0075 | 3/0 | 120.0 | {'MAX_ITERATIONS': 10} |
| Off-grid 600（补测） | -8.2268 | 0.0075 | 3/0 | 409.2 | {'HYPERPARAMETER_CHANGE': 9, 'MAX_ITERATIONS': 1} |
| Proposed（复用） | -12.4109 | 0.0025 | 1/0 | 74.4 | {'CONVERGED': 10} |

Off-grid 提高上限后，汇总 NMSE 改善 0.0810 dB：9 场景改善、1 场景略差，活动判决完全不变。Proposed 的汇总 NMSE 仍低 4.1841 dB，并在全部 10 个场景的完整信道误差更低。

600 轮版本的 9 个场景在 256–557 轮满足原停止条件，1 个仍达到 600 轮上限。其平均轮数为 409.2；120 轮版本原先 10 个均触顶。增加预算改善了停止情况，当前子集的误差收益较小。

## 解释边界

NMSE 按完整信道误差与信号总能量汇总后转 dB；AER 分母是 400 次用户判决，实际包含 33 个活跃用户。这是已见数据的固定小子集，不是新的独立确认集；不据此宣称全部 SNR、500 场景上的差异或统计显著性。历史时间来自不同执行批次，不能直接用于速度排名。

## 执行与核验记录

执行入口：`run.py`，续接入口：`resume.py`。第 7 个场景在成功推断后遇到严格能量相等断言，原因是求和顺序造成 1.49e-16 相对尾差。故障与原计划保留于 `POSTPROCESS_FAILURE.json` 和 `PLAN.json`；修复记录为 `REPAIR.json`。以 8 倍双精度机器精度核验，并在后处理前保存预测。已完成的 6 个场景未重跑；第 7 个丢失的推断补跑一次。因此得到 10 个场景的有效新结果，共执行 11 次补测求解器调用。Proposed 与 Off-grid 120 的复用没有新增推断。

205 份冻结资产和 110 份复用文件哈希未改变。NumPy 数值警告按类型保留在每场景记录，所有保存的最终输出均有限。停止上限与满足收敛条件分别统计。

详细数据：`SUMMARY.json`；逐场景结果：`sceneNNN/result.json`；新完整预测：`sceneNNN/prediction.npz`；原生轨迹：`sceneNNN/native.json.gz`。
