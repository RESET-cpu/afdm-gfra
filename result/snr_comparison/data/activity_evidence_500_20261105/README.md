> 2026-11-06 作者已将采用预算改为每档 100 场景。1200 次目标内新推断与 1200 份复用结果已通过[独立核验](adopted100_20261106/README.md)，另 1 份竞态多余结果保留。原 500 场景计划停止，不再续跑；下文为原计划说明。当前汇总入口与结果见 `adopted100_20261106`。

# 500 场景活动证据对照

用户已授权在前置实验结束后运行。本批次不训练、不修改冻结主线。

- 固定场景 0–499，SNR −4、−2、0、2、4、6 dB；四组使用逐份哈希绑定的相同输入，已知相位，观测估计噪声。
- 新增 STMP Gaussian 与白噪声 GP-MP Gaussian，各 3000 份推断；复用 STMP 学习密度比与完整白噪声 GP-MP 各 3000 份。
- 每个接收机仅替换活动证据；网络、阻尼、阈值和原 60–600 轮停止设置保持。网络 FP32，matmul/cuDNN TF32 关闭；既有 NumPy 双精度消息代数保持。
- “原始 STMP”指一阶/二阶网络及 Gaussian 活动更新在同一 AFDM 模型上的适配，不是原文物理系统的完整复现。
- Gaussian 活动概率由归一化复高斯密度比和 Bernoulli 先验概率计算；沿用已验证的 `STMP.posterior.full_posterior`。公式与术语范围参见 `paper/C-STMP/docs/TERMINOLOGY.md` 中 Cai §III-B, 式 (28)–(31) 及 `paper/C-STMP/docs/C_STMP_SNR_ABLATION_20261028.md`。

## 证据与限制

前置收敛实验按用户决定采用 30 场景、三方法共 90 份实际 300 轮轨迹，图只展示前 150 轮。原 250 次计划在 215 次停止，不声称全部完成，也不恢复退役部分。白噪声批次完成 6000/6000；最终收据、哈希与进程退出由 `PREREQUISITES.json` 记录。

历史 STMP 完整信道预测仅场景 0 保留，其余场景按旧执行入口在保存、重新评分后删除完整矩阵，保留活动概率、判决及逐用户误差。本次全部活动预测重新评分；历史 STMP 的其余 NMSE 从已核对哈希的逐用户误差与真值能量重新汇总，不能称为再次从完整信道预测评分。数量和逐份来源见 `REUSE_AUDIT.json`、`REUSE.json`。新推断及白噪声 GP-MP 复用项保存完整预测，均从预测重新评分。

这些是既有研究场景，不是未经观察的测试集。所有有限的迭代上限结果保留并计数。并发运行时间不作为孤立算法延时比较。

## 执行与续跑

入口为 `src/evaluation/activity_evidence_500_20261105`，设置项目 `src` 为 PYTHONPATH 后使用项目 Python：

1. `-m evaluation.activity_evidence_500_20261105.prepare`：完整复用核验与独立计划。已有计划禁止覆盖。
2. `-m evaluation.activity_evidence_500_20261105.run coordinate --preflight-only`：两方法各一个完整输入预检，核对配置、禁止实例化/调用分类器、重新评分与峰值内存。
3. `-m evaluation.activity_evidence_500_20261105.run coordinate`：最多两个隐藏工作进程，每个输入独立进程，内存门控；预检已完成则核验复用。完成后自动汇总。
4. `-m evaluation.activity_evidence_500_20261105.report`：重新核验所有四组配对证据并生成表格。

计划及实现哈希冻结于 `PLAN.json` / `PLAN_HASH.json`。原生结果在 `E:\afdm-gfra-results\activity_evidence_500_20261105`。`STATUS.json` 是即时状态，不代替最终 `COMPLETION.json`。每次启动记录 PID、创建时间、命令及计划哈希；锁和进程身份防止重复启动。若续跑，只接纳经过完整核验的已有结果，任何未完成目录保留为待检查现场，不自动覆盖或重试。`STOP.json` 要求停止派发并等待在途工作完成。

结果全部通过后才同步稿件的 500 场景 AER 表，保留旧 354 场景表和来源。论文同步与编译尚待本批次完成。
