# 独立相位前端：主 SNR 1000 场景实验

状态：**COMPLETE**，已核验并重新评分 6000/6000 份前端输出。

相位先由冻结的边缘似然前端估计一次，再固定相位运行原条件接收机；后端相位更新次数为零。
主比较使用同一批 1000 个物理场景、六档 SNR；历史迭代相位版本仅在场景 0–499 上进行三方法同覆盖比较。
已知相位使用真实相位构建算子，是 oracle 参照；信道和活动真值只用于评价。

## 1000 场景主比较

当前覆盖 6000/6000 份配对输入。

| SNR/dB | 方法 | 输入数 | NMSE/dB | AER | 漏检 | 误检 | 平均迭代 | 未收敛 |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| -4 | Marginal phase frontend (fixed) | 1000 | -9.550972 | 0.004925 | 184 | 13 | 62.77 | 1 |
| -4 | Known phase (oracle) | 1000 | -9.855029 | 0.00455 | 177 | 5 | 63.32 | 3 |
| -2 | Marginal phase frontend (fixed) | 1000 | -11.226097 | 0.002225 | 86 | 3 | 61.23 | 1 |
| -2 | Known phase (oracle) | 1000 | -11.548157 | 0.0021 | 83 | 1 | 60.85 | 0 |
| 0 | Marginal phase frontend (fixed) | 1000 | -12.669665 | 0.00115 | 43 | 3 | 60.40 | 0 |
| 0 | Known phase (oracle) | 1000 | -13.012668 | 0.001075 | 42 | 1 | 60.47 | 0 |
| 2 | Marginal phase frontend (fixed) | 1000 | -13.876184 | 0.0006 | 24 | 0 | 61.00 | 0 |
| 2 | Known phase (oracle) | 1000 | -14.281260 | 0.000575 | 22 | 1 | 61.49 | 0 |
| 4 | Marginal phase frontend (fixed) | 1000 | -14.921644 | 0.0003 | 12 | 0 | 65.15 | 0 |
| 4 | Known phase (oracle) | 1000 | -15.419115 | 0.0003 | 12 | 0 | 64.92 | 0 |
| 6 | Marginal phase frontend (fixed) | 1000 | -15.870200 | 0.00025 | 10 | 0 | 72.32 | 0 |
| 6 | Known phase (oracle) | 1000 | -16.477028 | 0.000225 | 9 | 0 | 72.17 | 0 |

## 前 500 场景三方法配对比较

当前覆盖 3000/3000 份配对输入。

| SNR/dB | 方法 | 输入数 | NMSE/dB | AER | 漏检 | 误检 | 平均迭代 | 未收敛 |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| -4 | Marginal phase frontend (fixed) | 500 | -9.614292 | 0.0042 | 84 | 0 | 61.45 | 0 |
| -4 | Known phase (oracle) | 500 | -9.877553 | 0.00415 | 81 | 2 | 61.80 | 0 |
| -4 | Selected iterative phase | 500 | -9.571602 | 0.0047 | 89 | 5 | 95.36 | 1 |
| -2 | Marginal phase frontend (fixed) | 500 | -11.231593 | 0.00215 | 43 | 0 | 60.66 | 0 |
| -2 | Known phase (oracle) | 500 | -11.527537 | 0.00215 | 42 | 1 | 60.84 | 0 |
| -2 | Selected iterative phase | 500 | -11.262999 | 0.00245 | 48 | 1 | 101.80 | 0 |
| 0 | Marginal phase frontend (fixed) | 500 | -12.653412 | 0.0011 | 21 | 1 | 60.30 | 0 |
| 0 | Known phase (oracle) | 500 | -12.984285 | 0.00105 | 20 | 1 | 60.33 | 0 |
| 0 | Selected iterative phase | 500 | -12.726615 | 0.00125 | 25 | 0 | 105.48 | 0 |
| 2 | Marginal phase frontend (fixed) | 500 | -13.864487 | 0.00055 | 11 | 0 | 61.02 | 0 |
| 2 | Known phase (oracle) | 500 | -14.261245 | 0.0006 | 11 | 1 | 61.20 | 0 |
| 2 | Selected iterative phase | 500 | -13.993776 | 0.00085 | 16 | 1 | 111.44 | 0 |
| 4 | Marginal phase frontend (fixed) | 500 | -14.914041 | 0.0002 | 4 | 0 | 65.32 | 0 |
| 4 | Known phase (oracle) | 500 | -15.408293 | 0.00025 | 5 | 0 | 65.17 | 0 |
| 4 | Selected iterative phase | 500 | -15.107978 | 0.0008 | 11 | 5 | 120.04 | 0 |
| 6 | Marginal phase frontend (fixed) | 500 | -15.859601 | 0.00015 | 3 | 0 | 72.22 | 0 |
| 6 | Known phase (oracle) | 500 | -16.476092 | 0.00015 | 3 | 0 | 72.18 | 0 |
| 6 | Selected iterative phase | 500 | -16.220094 | 0.00045 | 7 | 2 | 123.76 | 0 |

## 高 SNR 逐用户退化检查

4/6 dB 相对已知相位，前端有 3 份输入出现至少一个新增错误用户；历史迭代版在前 500 场景中有 10 份。
`HIGH_SNR_REGRESSIONS.csv` 列出全部这些输入，包括新增错误与纠正错误互相抵消、甚至总错误减少的情况；同时保留漏检、误检与对应用户编号。
用户编号沿用数组的 0 起始编号。`per_case.csv` 保存所有方法逐输入指标；`PAIRED_CASES.csv` 保存逐用户配对变化。

## 汇总与证据范围

NMSE 按总平方误差除以总真信道能量汇总，再转换为 dB；不平均单场景 dB。AER 按全部用户决策数归一化。
相位误差只对真实活动用户及 q=1..Q−1 帧评分，排除恒为零误差的参考帧。所有有限未收敛输出都计入性能统计，并在 `ITERATION_CAPS.json` 单列。
耗时仅为实际运行记录，不用于严格独占硬件速度结论。全部场景属于历史研究数据，不宣称未触碰的独立验证集；同场景六档 SNR 也不作为六个独立物理场景。
COMPLETION 的 PASS 仅表示覆盖、哈希与保存数组评分核验通过，不表示 AER、NMSE 或新方案性能通过。此次审计不等于重新运行全部推断进行独立复现。

## 统计解释检查（11/11）

| 检查 | 本报告处理 |
|---|---|
| Simpson 反转 | 总体及每档 SNR 均给出，主 1000 与前 500 分开 |
| 生态谬误 | 同时给出逐场景和逐用户错误，不由总体推断每个用户 |
| Berkson 选择偏差 | 高 SNR 困难输入仅作诊断，不替代完整样本统计 |
| 碰撞变量偏差 | 不按收敛或效果筛选纳入样本 |
| 忽略基率 | 报告活动/非活动数、漏检率及误警率 |
| 均值回归 | 配对相同输入；困难案例不作独立总体改善证据 |
| 幸存者偏差 | 有限 MAX_ITER 输出保留，部分覆盖明确标为 PARTIAL |
| 多重寻找 | 所有 SNR 与预定方法报告；不做显著性检验 |
| 分析选择自由度 | 保存冻结计划、输入与算法哈希；无事后性能门槛 |
| 相关误作因果 | 仅描述固定模拟条件下的配对性能 |
| 反向因果 | 无现实因果推断；不适用于本次数值比较 |

## Material Passport

- Workflow: academic-research-suite / experiment-agent / validate
- Material: simulated observations, stored receiver predictions, evaluator-only truth
- Verification Status: ANALYZED (saved-array re-scoring and content hashes; no inference replay)
- Coverage: COMPLETE, 6000/6000 frontend and known-phase pairs
- Scope: descriptive paired comparison; no significance or performance acceptance claim
