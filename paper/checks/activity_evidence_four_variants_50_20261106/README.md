# 四组活动证据表

按作者确认，将正文原有两组、354 场景的表替换为四组的首 50 个配对场景快照。各档展示 AER (%) 和达到 600 轮的比例 (%)，其余计数留在 SUMMARY.json 与 PAIRED_ROWS.json。正文实验设置仅用一句交代样本量；表注不重复。两版共用相同章节来源。

数据来源：`result/snr_comparison/data/white_phase_frontend_marginal_1000_20261106/analysis/activity_first50_20261106/`。本目录保存对应 SUMMARY、逐场景结果、来源哈希和只读重评分脚本。四组全部活动预测已重新评分；历史 STMP 密度比的部分信道 NMSE 仅能由保留的逐用户误差重汇总，本表不展示 NMSE。所有有限的达到上限输出均纳入指标。

变更范围：`sections/06_simulation_results.tex` 的活动证据表、样本数和对应结果段；`sections/appendix_evaluation_protocol.tex` 的实际模型来源与该项协议；阶段决定记录。现有 Gaussian 公式、主 SNR 曲线、其他图与训练资产不变。继续使用已采用的 Gaussian approximation、density ratio、AER 等术语；新增结果句是本实验观察，不冒称参考论文原句或普遍结论。

作者本轮又将运行预算改为每档 100 场景。该停止请求与当前 50 场景表快照分别记录；停止监控不代表核验通过。完整 100 场景核验完成后再更新表值。原 500 场景 PLAN 与源码不变，不把原计划标为完成。

`before/` 保存修改前 TeX、两版 PDF、决定文档；`BEFORE_HASHES.json` 记录哈希。编译、48 个数据单元核对、版面检查及最终文件哈希见 `VALIDATION.json`。
