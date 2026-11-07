# 当前实验协议

主实验采用未知跨帧相位，接收机从观测估计相位并完成活动与信道推断。准确已知跨帧相位用于理想参考。当前已完成的未知相位面板为 40 用户、至少一人活跃、off-grid、六档 SNR（−4、−2、0、2、4、6 dB），六方法各 10 个配对物理场景，见[比较报告](../../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_unknown_phase_20261015/evaluation/REPORT.md)。历史已知相位结果及各自样本数见 [evaluation.json](../../../src/configs/evaluation.json) 和冻结结果目录。

2026-10-18：用户将最终比较范围修订为前500个完整场景、−4、−2、0、2、4、6、8 dB，五方法17500次推断已完成。Proposed和四个baseline均估计相位与噪声，不包含L-DAMP。原600计划保留，最终范围与结果见[500场景报告](../../../result/baseline_comparison_500_20261018/REPORT.md)。
上述十场景面板仍属于供给准确噪声的历史实验。新实现及原论文定位见 [BASELINE_NOISE.md](BASELINE_NOISE.md)，本轮有限核验见 [报告](../../../archive/paper_layout_20261026/original_paper/docs/history/results/baseline_noise_20261015/REPORT.md)。

## 场景与判决

活动向量由独立 Bernoulli(p=0.1) 抽样并拒绝全零向量；公开活动先验是条件边缘 p/[1−(1−p)^K]。Proposed 与 baseline 默认只需要 observation、原始 pilot、activity_prior，在内部估计跨帧相位及噪声。显式已知噪声参考还需要 noise_variance。真实相位、Doppler、活动及信道存入独立真值文件。真实信道使用连续时延与 Doppler；生成噪声的分布及真实方差不因接收机估计而改变。

`simulate/run/baseline` 默认 `--phase-mode estimated`。理想参考显式使用 `--phase-mode known`，输入中的 operator 包含准确相位。比较信息条件时使用同一种子、相同观测、噪声和条件接收机设置。报告估计相位下的绝对性能及其相对理想参考的差距；性能下降是信息条件变化的评价结果，采用未知相位模型以实际可获得的信息为依据。

接收机的默认噪声模式为 `estimated`；准确噪声参考需显式 `--noise-mode known`。`simulate --noise-mode estimated` 从公开输入删除噪声字段，并把生成方差写入独立真值文件。`simulate` 默认仍保留四字段以支持准确噪声参考；估计噪声模式的 Proposed 与基线忽略其中的噪声值，包括相位残差诊断。噪声估计前端不读取生成元数据、真实 SNR、真实活动数或真实信道。

相位估计内部的比较另列：例如先估计再固定相位、继续做后验更新，两者均属于未知相位条件。Shen §III-C 启发的更新实现、协方差与跨帧约束见 [BASELINE_PHASE.md](BASELINE_PHASE.md) 及 [Proposed 说明](../../STMP/docs/PROPOSED_UNKNOWN_PHASE.md)。

各方法共享对应场景、导频、标准化噪声和真值。三个 baseline 使用已有冻结的十节点公共 SNR 判决规则，见 [READOUT_POLICY.json](../../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_baselines_40_20261011/READOUT_POLICY.json)。改变用户数、SNR 或活动概率时沿用同一规则和权重，不能逐点重新取标签拟合阈值。规则允许按既定函数使用公开接收功率与噪声；当前证据不预先证明任意负载下均最优。Proposed 使用固定 0.5 概率门限。

估计噪声模式的所有 SNR 节点选择使用估计方差。门限复用单独标记，不修改原校准身份以冒充新校准；L-DAMP 维持固定活动能量门限。评价报告单列噪声估计误差、完整信道 NMSE、AER 和停止状态，不以超过理想信息条件作为采用估计模型的前提。

历史已知相位比较中，Proposed 的 100 场景与 baseline 前 100 场景配对，且此前已被查看；baseline 新增 900 场景另有汇总。已观察的结果不能作为后续调参的独立测试集。新的开发规则须单独记录开发数据、选取过程和预先固定的验证范围。

## 论文实验矩阵

| 实验组 | 改变的条件 | 输出 |
|---|---|---|
| SNR 性能 | SNR | AER、active/full NMSE |
| 导频资源 | 帧数 Q | AER、NMSE、达到目标精度所需资源 |
| 用户规模 | 候选用户数 K；固定 p 和导频资源 | AER、NMSE、实际平均活跃人数 |
| 活动负载 | 抽样概率 p；固定 K 和导频资源 | AER、NMSE、条件边缘活动率及平均活跃人数 |
| 信道分布泛化 | 固定权重，改变一项明确分布条件 | AER、NMSE、训练与测试条件 |
| 迭代与计算成本 | 同一代表条件 | 逐轮 NMSE、推断时间及离散程度 |

该矩阵保留为研究计划，不表示各组均已完成。未来重新训练时，GNN 训练和权重选择的验证集采用 on-grid；性能评价采用 off-grid。现有 GNN 权重来自 10001/256 样本、29 阶段、39 个 epoch 的混合 SNR/on-off-grid 训练，继续使用这套权重。

## 统计与运行记录

信道主指标基于完整物理信道 H 重构，记录信号/误差能量与活动错误计数后再聚合。有限迭代上限输出全部计入；数值失败和缺失须单列，不能删除失败后声称完整面板完成。每个算法记录输入身份、配置、权重/源码身份、停止原因及原生迭代次数。

区间按物理场景共同重抽样，不能把同一场景的用户或各 SNR 当作相互独立样本。不同样本数方法的区间分别计算。

计时固定设备、线程和批量，模型加载时间与原生推断时间区分。读取真值的逐轮评分观察器不参与推断或停止，其额外耗时不能并入正式速度对比。

当前 proposed 默认采用已完成 100 场景的停止配置。2026-10-11 的开发停止选项在 18/96 条件后按用户要求停止，见 [STOPPED.md](../../../archive/paper_layout_20261026/original_paper/docs/history/archive/workspace_organization_20261011/before/experiments/classifier_optimization_20261011/STOPPED.md)；它尚未成为默认。代码整理只进行迁移回归，不续跑研究队列。

完整历史协议、校准和开发阶段说明见[整理前协议](../../../archive/paper_layout_20261026/original_paper/docs/history/archive/code_consolidation_20261011/workspace/docs/EXPERIMENT_PROTOCOL.md)，冻结结果内的 PLAN、配置与原始证书保持原记录。
