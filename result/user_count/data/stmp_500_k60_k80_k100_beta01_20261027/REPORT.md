# 500 场景实验结果

## Material Passport

- Origin: academic-research-suite / experiment-agent
- Mode: run
- Status: COMPLETE
- Experiment: user_count

每条件固定场景 0–499；2500 个配对输入，15000 份算法结果。
已知相位由模拟真值形成算子；噪声方差由接收机估计。未训练，未切换主线。

NMSE 以总信道误差能量除以总真值信道能量计算；AER 以总漏检与虚警除以全部用户判决数计算。
收敛率严格统计原始 CONVERGED 标签；达到上限或其他停止标签的有限结果全部保留。
保存的并行运行耗时仅用于追溯，不作为独占算法时延。

完整预测数组重评分：4501 份；历史 compact 重算：499 份。
四种基线从保存的原始 JSON 与 compact 输出核验，沿用已采纳读出；分档门限使用各方法估计 SNR。

| 条件 | 算法 | NMSE (dB) | AER | 漏检 | 虚警 | 平均轮数 | 收敛率 |
|---|---|---:|---:|---:|---:|---:|---:|
| K=20 | C-STMP | -14.725378 | 0.0001 | 1 | 0 | 60.026 | 1.0000 |
| K=40 | C-STMP | -12.984285 | 0.00105 | 20 | 1 | 60.328 | 1.0000 |
| K=60 | C-STMP | -11.664522 | 0.0021666667 | 64 | 1 | 63.346 | 0.9980 |
| K=80 | C-STMP | -10.260630 | 0.004 | 154 | 6 | 71.604 | 1.0000 |
| K=100 | C-STMP | -8.840923 | 0.00826 | 356 | 57 | 128.634 | 0.9980 |
| K=20 | STMP | -13.581493 | 0.0003 | 3 | 0 | 84.580 | 1.0000 |
| K=40 | STMP | -11.418250 | 0.00185 | 37 | 0 | 91.682 | 1.0000 |
| K=60 | STMP | -9.811812 | 0.0037333333 | 111 | 1 | 180.862 | 1.0000 |
| K=80 | STMP | -8.144392 | 0.009025 | 338 | 23 | 209.640 | 0.9940 |
| K=100 | STMP | -5.614897 | 0.0187 | 742 | 193 | 253.288 | 0.9720 |
| K=20 | Off-grid SBL | -9.675092 | 0.0002 | 2 | 0 | 120.000 | 0.0000 |
| K=40 | Off-grid SBL | -8.512098 | 0.00125 | 20 | 5 | 120.000 | 0.0000 |
| K=60 | Off-grid SBL | -7.733599 | 0.0025 | 40 | 35 | 120.000 | 0.0000 |
| K=80 | Off-grid SBL | -6.996352 | 0.0054 | 102 | 114 | 120.000 | 0.0000 |
| K=100 | Off-grid SBL | -6.313996 | 0.01106 | 182 | 371 | 120.000 | 0.0000 |
| K=20 | GNN-ASPL | -6.199289 | 0.0004 | 3 | 1 | 10.000 | 0.0000 |
| K=40 | GNN-ASPL | -5.490580 | 0.00205 | 38 | 3 | 10.000 | 0.0000 |
| K=60 | GNN-ASPL | -4.714416 | 0.0054 | 122 | 40 | 10.000 | 0.0000 |
| K=80 | GNN-ASPL | -3.879010 | 0.01505 | 311 | 291 | 10.000 | 0.0000 |
| K=100 | GNN-ASPL | -3.029570 | 0.0323 | 599 | 1016 | 10.000 | 0.0000 |
| K=20 | GAMP-SBL | -5.405764 | 0.0004 | 4 | 0 | 136.738 | 0.0000 |
| K=40 | GAMP-SBL | -4.585216 | 0.00345 | 61 | 8 | 242.766 | 0.0000 |
| K=60 | GAMP-SBL | -3.886343 | 0.0061666667 | 144 | 41 | 346.714 | 0.0000 |
| K=80 | GAMP-SBL | -3.314883 | 0.01145 | 343 | 115 | 448.924 | 0.0000 |
| K=100 | GAMP-SBL | -2.832947 | 0.01874 | 602 | 335 | 554.292 | 0.0000 |
| K=20 | SOMP | -4.693386 | 0.0016 | 10 | 6 | 22.506 | 0.0000 |
| K=40 | SOMP | -3.905474 | 0.0043 | 65 | 21 | 24.708 | 0.0000 |
| K=60 | SOMP | -3.093754 | 0.010366667 | 137 | 174 | 27.302 | 0.0000 |
| K=80 | SOMP | -2.414449 | 0.01865 | 301 | 445 | 29.248 | 0.0000 |
| K=100 | SOMP | -1.785388 | 0.03218 | 513 | 1096 | 31.520 | 0.0000 |

## 核验与局限

- Fixed physical scenes 0-499; includes previously inspected/development scenes; retrospective paired comparison.
- Baseline threshold development overlaps evaluation scenes; use adopted policy without fitting.
- Known phase uses the simulation truth operator; noise is estimated. Nonempty activity is conditioned; read public rho unchanged.
- All finite nonconverged results retained. Concurrent throughput is not isolated method latency.
- Existing C-STMP comparison uses K100 beta=.2 and the user-requested retrospective K80 scene372 beta=.2 replacement; other K80 scenes beta=.4. Original results remain preserved.
- STMP K20/K40 retain beta=.2; all 500 scenes of K60/K80/K100 use beta=.1, selected retrospectively after original500 results and a12-input diagnostic.
- The12 diagnostic inputs are included and reused; this is parameter development rather than independent confirmation. Original beta=.2 outputs remain preserved.
- No failed, nonconverged, or unfavorable finite result is removed; no per-scene damping exceptions are permitted for STMP.
- 本批 STMP 在 20/40 用户档沿用 β=0.2，在 60/80/100 用户档对固定前 500 场景使用 β=0.1。该调整是在观察原 β=0.2 的 500 场景结果及 12 输入配对诊断后选择，属于回顾性参数开发；12 份同输入、同配置的诊断结果核验后复用，其余输入补齐推断。原 β=0.2 输出保留，不按成功与否筛选场景；本批全部有限输出（包括未收敛输出）均纳入汇总。
- 用户数 C-STMP 沿用已交付的回顾性结果：20/40/60 用户均为 β=0.4；80 用户仅场景 372 改用 β=0.2，其余 499 场景仍为 β=0.4；100 用户全部为 β=0.2。该单例在观察失败后选择，不代表整档 80 用户以 β=0.2 重跑。原始结果保留。
- 部分历史 STMP 全信道预测已按既有清理方案退役；这些结果核验原始 JSON 哈希、输入与种子绑定、逐用户误差、活动真值及概率 0.5 判决，并重新聚合。其信道误差依赖保存的逐用户误差，不能重新从已退役的信道预测计算。
- 保存输入采用至少一个活跃用户的条件 Bernoulli 抽样；横轴为名义活跃概率，接收机沿用保存输入中的条件活动先验。
- 图中数据已与汇总逐项核对；脚本未宣称完成图像的人工视觉审阅。
- 完整逐场景统计见 per_scene.csv；输入、原始输出与读出凭据见 AUDIT.json 和 BASELINE_AUDIT.json。
