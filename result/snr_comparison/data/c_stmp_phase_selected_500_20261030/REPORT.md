# 新相位估计：SNR每档500场景

六档各500场景（0–499），3000份选定相位版本输出，逐份与旧相位和已知相位参照配对。
全部输入与输出已核验哈希并从预测数组重新评分；达到迭代上限的有限输出计入所有统计。

| SNR/dB | 新版 NMSE/dB | 旧版 NMSE/dB | 已知相位 NMSE/dB | 新版 AER | 旧版 AER | 新版平均轮数 | 新版未收敛 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| -4 | -9.571602 | -9.594962 | -9.877553 | 0.0047 | 0.0052 | 95.36 | 1 |
| -2 | -11.262999 | -11.278892 | -11.527537 | 0.00245 | 0.0026 | 101.80 | 0 |
| 0 | -12.726615 | -12.774846 | -12.984285 | 0.00125 | 0.0011 | 105.48 | 0 |
| 2 | -13.993776 | -14.047723 | -14.261245 | 0.00085 | 0.00075 | 111.44 | 0 |
| 4 | -15.107978 | -15.231110 | -15.408293 | 0.0008 | 0.0003 | 120.04 | 0 |
| 6 | -16.220094 | -16.288607 | -16.476092 | 0.00045 | 0.0002 | 123.76 | 0 |

本批包含13个参与相位版本选择的场景，属于扩展回顾性比较。SUMMARY.json另报告排除这些完整场景后的487场景结果；该子集也不宣称从未用于此前研究。
已知相位参照使用真实相位构建观测算子。并发运行时间不作为算法速度比较。无训练、无进一步调参，冻结主线与旧暂停批次保持不变。

## Material Passport

- Workflow: academic-research-suite / experiment-agent / run
- Material: simulated observations, saved predictions and evaluator-only truth
- Verification: complete paired coverage, saved-array re-scoring and content hashes
- Scope: descriptive SNR comparison; no global optimum or significance claim
