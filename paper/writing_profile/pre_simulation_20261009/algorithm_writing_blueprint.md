# III–V 论证蓝图

## III. Bayesian Receiver Design

| 小节 | 必须完成的逻辑 | 依据 |
|---|---|---|
| A. Linear Estimation | 输入高斯 → 线性条件均值/协方差 → 平均迹 → 高斯外信息 | C01 III-A；C06 III-C；C11 IV-B |
| B. Channel and Activity Denoising | 高斯查询近似 → 两类密度/局部后验 → 精确条件混合矩 → 学习接口/高斯site → 近似联合矩 | C01 III-B；C09 III-C；C08 III-B |
| C. Extrinsic Message Update | 空间平均协方差 → 公共标量 → 正方差约束 → 反馈消息 | C01 III；C06 III-C |

III定义Fθ、误差读数与logit的用途，不展开其训练损失。近似查询是算法建模步骤，不声称已证明有限AFDM系统的状态演化。

## IV. Learning Channel and Activity Denoisers with Score-Based Generative Priors

| 小节 | 必须完成的逻辑 | 依据 |
|---|---|---|
| A. First-Order Score Matching | 高斯扰动密度 → 实部方差v/2 → Tweedie均值 → DSM损失 → 完整张量均值 | C01 IV-A/B；C03 II/III；C12 §4.1 |
| B. Conditional Error Estimation | 二阶Tweedie → 全坐标平均后平方 → 冻结均值条件MSE → 偏差分解 → 共享误差的条件风险拟合 | C01 IV-C；C13 §4.2；本项目数学推导 |
| C. Density Ratio Estimation | 同一v采样律 → BCE最优logit → 训练先验扣除 → 接入先验加入 | C14 §3/4.2；C01活动去噪问题接口 |
| D. Offline Training | 场景隔离；活跃候选信道；复高斯扰动；输入/输出；训练顺序与冻结关系 | C02 III-C；C03 III-A；C04 VI-A的内容边界 |

IV-B只识别标量条件误差，不把网络坐标输出表述为已识别的Hessian各项。IV-C的Fθ是由完整R确定的特征，保留完整R的意义用一句话说明。

## V. Overall Algorithm

| 小节 | 必须完成的逻辑 | 依据 |
|---|---|---|
| A. Message Scheduling | 初值；查询支持范围；site接受/保留；超范围高斯活动比；完整伪代码；SVD复用 | C05 III-B；C04 V-D；C08 Algorithm1 |
| B. Damping and Stopping Criteria | 输入/输出阻尼；分开的估计/活动容差；site与历史残差；独立计数；判决稳定窗口；迭代预算 | C01 V-B；C08 Algorithm1；项目实际实现 |
| C. Computational Complexity Analysis | 一次分解成本；每轮算子/协方差/网络成本；内存；训练与在线成本分离 | C01 V-C；C04 V-E；C06 IV-B |

数值停止检查说明判定什么即可；不重复“无全局收敛证明”。正文不报告试验运行速度或尚未完成的性能结论。停止逻辑核对于 mainline/iterations.py 与 full_score/denoiser.py，配置值仍留在VI。

