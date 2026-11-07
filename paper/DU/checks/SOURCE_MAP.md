# TWC第一版：章节、公式及代码对应

**后续修订：** 本表保留首次推导记录。当前正文按
[Cai/Shen行文修订](CAI_SHEN_PROSE_REVISION_20261021.md)组织：
风险分解、混合协方差及误差审计展开已不参与编译；相位与噪声估计现为附录A。
校准、正值映射、阻尼及训练目标本身保持原定义。

日期：2026-10-21。旧稿按DCN保留，新稿按TWC独立维护。
中心术语记录仍为 [TERMINOLOGY](../../../docs/TERMINOLOGY.md)。

| 内容 | 原文定位或项目依据 | 新稿定位 |
|---|---|---|
| Gaussian projection、moment matching、message division | Minka 2001，§2式(5)–(6)、§3式(8)–(10)；Cai §III-A | III-A；一般算子的完成平方和SVD计算直接推导 |
| 活动混合均值、协方差 | Cai v2，§III-B3，式(35)–(38) | III-B；完整协方差由全协方差公式展开 |
| score、Tweedie、DSM | Cai §IV-A–B，式(43)–(49)；Efron 2011；Vincent 2011 | IV-A；复方差v对应实坐标v/2 |
| L-STMP、逐层训练、独立score | Wei–Yuan v1，§III-D与§V-A，PDF第3–4页 | 引言、IV-C；继承训练思想，明确本文活动头和监督目标 |
| 一般算子校准查询 | 实际运行 receiver_base.py 的 linear_query | III-A；均值M+(1+gamma*f/d)*Delta与方差w*gamma*f/d同时修改 |
| 与Wei校准的区别 | Wei §III-B式(8)–(10)，PDF第3页 | III-A；不把本项目gamma位置写成原文等式 |
| 残差反馈 | Wei §III-C式(12)，PDF第3页；receiver_base.feedback_variance | III-C；正值映射及比例限制为项目设计，不称精确后验方差 |
| natural parameters、damping | Vehtari等2020，§5.2，印刷第17–18页；附录A，印刷第32页 | III-C；delta=min(1,w_ref/w_proposal)仅归因于项目实现 |
| 固定归一化、梯度、选模 | 第二版协议T4–T11；实际运行 objectives.py、receiver.py | IV、附录A；条件风险展开不命名新理论 |
| 执行次序及复杂度 | 实际接收机前向、整形和SVD预处理 | V；密集实现，不声称运行时间更短 |
| 相位与噪声估计 | DCN原III-A及其已有引用 | 附录B；物理模型仍在II |

实际运行代码相对于 [source_code](../../../cloud/review_20261021/source_code/)：

- experiments/lstmp_candidate_20261019/receiver_base.py：线性更新、查询校准、活动头、正值反馈。
- experiments/lstmp_candidate_20261019/message_damping.py：自然参数阻尼。
- experiments/lstmp_training_v2_20261020/receiver.py：组合前向、独立校准标量、有梯度的条件输出。
- experiments/lstmp_training_v2_20261020/objectives.py：T4/T5/T8损失、完整梯度、末层选模。
- [MANIFEST](../../../cloud/review_20261021/MANIFEST.json)：DirectCai主干、19条件、训练和验证规模。

## 版本选择与待补内容

引言保留旧稿背景与引文；本轮新核对Wei、Cai、Minka与Vehtari原文。
未开展新的穷尽性新颖性检索，贡献为方法描述，不使用“首次”“最优”“保证收敛”。
旧引言500场景结果属于DCN，不纳入TWC。第二版24条件/七层不作为第三版配置。

第三版为十层规划、19条件、4,750训练与1,900开发场景，每深度适配1轮、
联合2轮，前层监督0.2、末层1，活动门限0.5。一阶预训练复用50,000信道权重。
方法正文说明目标与执行，数值留在实验设置准备记录，不把预算写成完成记录。

风险证明采用固定查询与自由输出。真实模型容量、查询依赖及性能仍需实验。
附录B继承已有前端，尚未将其与新权重的完整评价写为已完成。
独立测试、统计区间、运行时间和内存仍待正式结果。

## 本轮验证

validate_manuscript.py核对非行正交、超定与秩亏矩阵的代数，
以有限离散分布直接枚举风险分解，并核对启用文件的标签、交叉引用、引文键。
DCN副本与原稿逐文件校验通过。未启动训练或批量接收机实验。
编译失败于远程资源包不可获取，源文件检查不等于编译通过。
