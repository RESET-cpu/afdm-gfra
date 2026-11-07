# 固定分组的首轮消息比较

范围：正式场景0–999，−4/0 dB；相位已知、噪声按冻结入口从观测估计。仅计算一次线性消息，不加载网络、不训练、不运行完整接收机。承接 [上一轮验证](../stmp_covariance_validation_20261024/README.md)。

## 预先固定的七个分支

1. global_scalar：全部640输入模式共用一个精度，复现旧首轮。
2. user_1：每用户16个模式共用一个精度。
3. user_2：每用户按公开Gram特征值升序分为2个连续等长组。
4. user_4：相同规则，4组。
5. user_8：相同规则，8组。
6. user_16：每模式独立精度，复现上一轮细分首轮。
7. user_4_folded：固定模式编号组为[0,7,8,15]、[1,6,9,14]、[2,5,10,13]、[3,4,11,12]。仅检查成员选择的影响，不作为新具名算法。

各模式还包含天线×输出行的256个坐标。所有分组不使用真值或查询来选择成员。连续分组构成嵌套分区，4组对折分支与连续4组不能按细化关系排序。

## 文件

- PLAN.json：在运行前固定输入、分支、公式、统计量、边界和受保护文件哈希。
- run_grouping.py：单次线性比较及数值代数检查。
- RESULTS.npz：七分支完整指标、原始h、初始化方差、分组标签、元数据和块条件数。
- GAUSSIAN_REFERENCE.npz：2048份CN(0,I)查询参考，公开方差白化后不再oracle拟合。
- ALGEBRA.json：640维协方差对角、组内平均和嵌套组平均方差的数值核对。
- RUN_COMPLETE.json：执行结束及原始输出哈希；不能替代科学结论。
- summarize_grouping.py / SUMMARY.json：全部分支、SNR、活动分层及既有暴露分层的描述统计。
- VALIDATION.json：复现、数据完整性、受保护文件与11类统计谬误检查。
- 研究结论见 [报告](../../../../paper/docs/STMP_COVARIANCE_GROUPING_20261024.md)。

## 复算

在仓库根目录使用：

    .venv\Scripts\python.exe result/snr_comparison/data/stmp_covariance_grouping_20261024/run_grouping.py
    .venv\Scripts\python.exe result/snr_comparison/data/stmp_covariance_grouping_20261024/summarize_grouping.py

已有RUN_COMPLETE时第一条保留结果并直接返回。新版本另建目录，不删除当前结果以覆盖实验。

RESULTS的metrics维度为[7,80000,14]，properties为[7,80000,8]；meta列为scene、condition、user、active、previously_examined。condition=0对应−4 dB，2对应0 dB。名称保存于npz，详细公式在run_grouping.py和上一轮metrics.py。

## 解释边界

各首轮query在保留公开缩放/噪声估计元数据时可互相恢复；原始MSE比较不能当作信息量或最终检测性能比较。粗分组后的自身模式增益通常不为1，组平均方差正确也不保证每模式方差正确。逐模式恢复单位自身增益会回到细分query，且不消除其他模式或用户的耦合。

所有近奇异样本保留，极端算术均值和最大值不当作可靠物理效应量。实际数据此前参与过项目实验，不称新独立确认集。2048份Gaussian参考只提供同尺寸描述分布，不提供逐query的精确显著性检验。
