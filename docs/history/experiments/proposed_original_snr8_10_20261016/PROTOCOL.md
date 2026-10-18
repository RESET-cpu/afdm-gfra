# 原导频、十场景、八档 SNR 配对实验

沿用已冻结的原 Proposed 主线：原 PartialDFTPilot、三网络、消息迭代、阻尼 0.2、门限 0.5。
本次是用户指定的评估范围扩展；算法探索已结束。

- 固定复用 seeds 202610168100001–202610168100010 的全部十个物理场景。
- SNR = −4、−2、0、2、4、6、8、10 dB，共 80 个输入条件。
- 方法：Proposed、SOMP、GAMP-SBL MMV、GNN-ASPL、Off-grid SBL；本轮按用户要求不运行 L-DAMP。
- 各方法使用完全相同的观测、原导频和从观测估计的相位；统一供给准确物理热噪声方差。
- 对每个场景，P = mean(|Y_clean,original|²)，sigma² = P 10^(−SNR/10)，Y = Y_clean,original + sqrt(sigma²) epsilon。
  八点共用同一标准噪声 epsilon；重新估计每档相位。旧固定噪声导频核查中的预测不直接复用。
- 保留原 Bernoulli(0.1) 后条件于非空的生成分布，公开边际活动先验为 0.1/(1−0.9^40)。不筛除弱用户。
- 不重训、不重新校准、不按测试输出修改门限。此前已看过这批场景的部分结果，因此不是新的独立确认集。
- 共 400 次推断，每条件 1200 秒硬预算；原算法停止条件保留。完整输出、失败、未收敛和警告均保存。
- 完整信道 NMSE 用全部用户误差能量除以真信道能量，不按活动判决屏蔽。MD、FA、AER、MDR、FAR 单独报告。
- 事前冻结评分脚本。20000 次物理场景配对 bootstrap，seed 202610168199999，全部 SNR 共用抽样索引；区间仅作描述。
- 所有八点均保留；后续展示区间的选择不删除完整结果。

## 噪声条件的文献核对

Cai 等，*Joint Activity Detection and Channel Estimation for Massive Connectivity: Where Message Passing Meets Score-Based Generative Priors*，
[v2 原文](https://arxiv.org/html/2506.00581v2)，Algorithm 1、Algorithm 2 的输入包含物理噪声方差 delta_0²。
§III-A 式(7)–(8)在线性估计中使用该量；迭代更新的消息方差 v、tau 不等同于重新估计物理热噪声方差。
[作者代码固定提交](https://github.com/chang-cai/score-massive-connectivity/blob/0c75680c966dcb8e46250de146f4c27e9294c283/main_stmp_jadce.py)：
L71–79 用 delta 生成噪声，L90 将同一参数存入接收机，L141–149 用 delta² 作线性估计；不更新该参数。
该证据支持本次已知方差条件，不表示知道噪声样本，也不表示本项目的相位模型或 SNR 定义与 Cai 完全相同。

本面板显式选择所有方法的已知噪声入口；项目 baseline 的默认估计噪声入口继续保留，其结果属于另一信息条件。
