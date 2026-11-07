# 选定相位版本：SNR每档500场景

## 2026-11-01 恢复

用户明确要求续跑后，于北京时间13:18从654份已保存结果继续，剩余2346份。
恢复入口为 `resume_20261101.py run`，具体计划、原失败状态副本及日志见
[恢复记录](resume_20261101/README.md)。本次只调整执行并发和进程生命周期：
单个GPU推断进程、每份输入结束后退出，下一份重新启动；数值配置、算法及权重不变。
原 `PLAN.json`、`run.py`、`report.py` 和失败目录保持原字节。以下为原始批次说明。

用户请求：`那我们是不是可以按照新的相位估计进行SNR实验的500场景`。
沿用主SNR实验六档 −4、−2、0、2、4、6 dB，各取场景0–499，共3000份输出。
2026-10-30 12:23（北京时间）已启动；实时进度以 `STATUS.json` 为准，完成须同时有 `COMPLETION.json` 的 PASS。

沿用已验证的 `physical_no_hypotheses_legacy_stop`，完整绑定见 `PLAN.json`：

- 物理初始化，第20轮起每20轮检查；条件推断稳定后才更新相位。
- 条件相对变化阈值0.0005，活动变化阈值0.001，连续5轮满足。
- 完整周期的物理信道与接收预测相对变化均小于0.05；决策和有效矩稳定10轮，且至少发生一次实际相位更新。
- 最少80轮、最多600轮，相位更新后至少继续10轮；阻尼0.4。
- 保留固定消息下的相位细化，取消分类器局部相位候选替换；活动分类器仍保留。

复用25份配置及输入完全匹配的已完成结果，已逐份重评分。新增2975次推断使用版本选择时的同一冻结入口，首份保存并核验成功后扩展到4个GPU进程，每进程2个CPU线程。输出独立保存在 `E:/afdm-gfra-results/c_stmp_phase_selected_500_20261030/`，本目录只保存计划、指针、日志与汇总。每份输入最长2小时；失败停止派发并保存其余在途结果，不自动重试。`STOP.json` 请求排空后停止。

配对参照为相同输入的旧估计相位C-STMP及已知相位C-STMP，各3000份，直接读取既有输出。已知相位参照利用真实相位构建观测算子，图中明确标注。所有版本都报告达到上限的有限输出，不按是否收敛或性能筛选样本。结束后自动核验完整覆盖、哈希、实际配置及无真值推断标志，重新评分9000份预测，生成 `SUMMARY.json`、`SNR.csv`、`REPORT.md`、`ITERATION_CAPS.json`、独立SNR比较图和 `COMPLETION.json`。

本批包含13个参与相位版本选择的场景：0–5、12、101、151、157、166、175、198。主结果保留全部500场景，另报告排除这些完整场景后的487场景结果；后者不宣称从未用于此前研究。版本选择的预留验证场景700–719不纳入本批。每档500个输入对应同一组500个物理场景，六档合计不是3000个独立场景。

无训练，不进一步搜索参数，不恢复旧6000份暂停队列，不替换FINAL/MAINLINE，不修改论文图。旧配置内历史“待选择”文字保留原字节，权威选择状态以 `result/candidates/c_stmp_phase_selection_20261030/RECOMMENDED.json` 为准。并发时间不用于声称算法加速比。

## Material Passport

- Workflow: academic-research-suite / experiment-agent / run (inline execution)
- Material: existing simulated observations; raw observation/pilot/activity prior enter inference; truth enters scoring only
- State: running; not a completed 500-scene result
- Verification: 25 reused predictions re-scored; 6000 reference identities checked; 312 frozen assets bound
- Execution: `run.py run`; automatic full audit and report in `report.py`

