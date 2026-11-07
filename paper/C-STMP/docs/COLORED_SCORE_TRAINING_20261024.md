# 单一有色 Gaussian 噪声的 score 训练候选

**2026-10-24 后续状态更新：** 用户已授权并启动[50000样本、匹配原200轮设置的正式训练](../../../result/channel_denoising/data/colored_score_50000_matched_20261024/README.md)。下面的“未启动”和第4节小预算方案是此前准备阶段的历史记录，正式运行以该独立训练目录为准。随后完成了[网络结构文献核查与已有权重诊断](COLORED_SCORE_ARCHITECTURE_REVIEW_20261024.md)，尚未实现或启动新结构训练。

2026-10-24，修订2。按用户要求取消四类等比例混合，训练统一使用一个条件 Gaussian 噪声族。当前状态：实现与有界检查完成；正式训练、独立去噪比较及活动检测比较均未启动。此处只选择并实现训练噪声模型，不修改 GEC 分组或接收机消息更新。

后续已按“比标量白噪声更合理，不要求精确分布”完成[已有查询的相对近似检查](COLORED_COVARIANCE_RELATIVE_CHECK_20261024.md)：当前受限C族在未参与拟合的输出行上，整体Gaussian评分优于同样拟合功率的白噪声模型。虽然部分阶段的天线剩余相关增加，结果已支持保留当前rank=4、强度上限0.5作初步去噪试验候选，不再为精确白化扩张模型。该检查使用真值误差、属于旧查询内部的探索性分析，不是训练后性能结果或可部署C估计器。

## 1. 本次具体选择

复用原来的 50000 个干净训练信道和固定幅度归一化，在线重新加噪：

\[
r=h+e,\qquad e\mid C\sim\mathcal{CN}(0,C),\qquad
C=vR_a\otimes I_{16}\otimes R_c.
\]

张量轴为天线、输出行、输入列，输入列在 C-order 展平中最快。噪声给定 C 后与信道独立；输出行方向暂按独立处理。两个因子均正定且 trace 等于16，所以 v 是平均复噪声功率，不是每个元素都相等的方差。

每个训练样本都分别抽取 R_a 和 R_c，不抽噪声类别、不设置类别比例。两个因子独立使用同一个公式生成：

\[
R=(1-\alpha)I+\alpha\frac{16GG^H}{\operatorname{tr}(GG^H)},
\quad G\in\mathbb C^{16\times4},\ G_{ij}\sim\mathcal{CN}(0,1),
\quad\alpha\sim U[0,0.5].
\]

每个方向独立抽取自己的 G 和 alpha。alpha 是上式中的混合权重，不是任意一对位置的相关系数；它越接近0，因子越接近 I。连续采样不强制分配精确 AWGN 样本，也不等价于固定白噪声占比。max_strength=0 仍可生成精确 AWGN，用于公式退化检查；训练中的 AWGN 对照臂是单独的控制模型，不混进候选模型的训练样本。

总体噪声强度沿用原训练范围：q 在 [-20,30] dB 均匀采样，v=10^(-q/10)，即 [0.001,100]。q 相对于固定归一化后的单位参考功率，不是按每个信道真值功率重新定义的瞬时 SNR，也不等于接收机测量 SNR。

保留 rank=4 和 alpha 上限0.5，是为了本次只改变离散分类抽样这个设定，不同时改动多个采样参数。这些参数尚未通过去噪比较选优，更没有从正式 SNR 测试查询拟合。该族允许随机相关方向及非均匀对角方差；它不覆盖所有正定协方差。每个因子的最小特征值至少0.5，最大不超过8.5；因此 C 的条件数上界289。没有通过截断特征值修补异常样本。

“一个噪声族”指所有样本遵守同一条件生成公式，不是所有样本共享一个固定 C。把 C 忽略后得到的是协方差混合分布；本实现始终向网络提供该样本的 C 条件。

## 2. 网络和目标只作必要改动

保留现有一阶 score 主干和权重，只把原来的 log(v) 条件扩为 log(v)、R_a-I、R_c-I 的实部和虚部。共1025个实输入，第一层条件映射增加65536个权重；原有权重复制，新条件权重初始化为零。提供完整因子，避免假定一个未经验证的固定特征基。

当前实现不使用仅靠有限辅助噪声样本的条件。D-GEC 的 corr+corr 在 §III-B 式(38)–(41)训练的是去噪映射；不能直接把它改称精确 C 条件的 score，再照搬乘 C 的均值公式。有限辅助样本与精确协方差条件的差别，见[独立数学核查](../../../reference/reviews/stmp_message_awgn_review_20261024/notes/colored_score_training_algebra.md)。这并不否定原论文的直接去噪训练。

网络输出沿用现有的实梯度约定。令 x_R=[Re(x);Im(x)]，

\[
\Sigma=\tfrac12\begin{bmatrix}\Re C&-\Im C\\\Im C&\Re C\end{bmatrix},
\qquad s_\theta(r,C)\approx\nabla_{r_R}\log p(r_R\mid C).
\]

训练损失与去噪均值配套改为

\[
\mathcal L=\frac1{8192}\left\|\Sigma^{1/2}s_\theta+
\Sigma^{-1/2}(r_R-h_R)\right\|^2,
\qquad\hat h_R=r_R+\Sigma s_\theta.
\]

复合成后均值为 r+(1/2)C(s_Re+i s_Im)。AWGN 时精确退化为原有加权 DSM 和 r+(v/2)s。矩阵平方根采用 Hermitian 主平方根，按两个轴运算，不形成4096×4096矩阵。列轴右乘转置而非共轭转置；代码有包含虚部的密集矩阵对照。

一般协方差的均值公式依据 [Dytso–Poor–Shamai v1](https://arxiv.org/pdf/2104.01883v1)，PDF p.2式(3)；白噪声 DSM 依据 [Cai 等 v2](https://arxiv.org/html/2506.00581v2#S4.SS2)，§IV-B式(48)–(49)。以上矩阵加权、复实换算及项目张量实现是显式推导，不称为 D-GEC 原文已有的 score 实现。

## 3. 已完成的检查

- 修订后七项定向测试通过：轴顺序和实复协方差、AWGN loss/均值退化、解析 Gaussian 先验后验、采样协方差和伪协方差、连续强度采样及 trace/正定性、条件梯度和小网络更新、候选权重保存重载。
- 采样检查使用60000个独立小维向量，协方差与伪协方差的相对 Frobenius 误差均通过预设0.025容差。这是采样器检查，不是60000个物理实验场景。
- 用真实冻结一阶网络及一个原训练信道执行 CPU 检查：AWGN 输出最大绝对差为0；新增条件权重梯度范数0.0116578；一次优化前后 loss 为0.0939281、0.0849413。
- 单步 loss 变化仅说明这条训练路径可运行，不能当作收敛、泛化或活动检测改善的证据。该次更新没有保存权重。

本版原始记录：[SMOKE.json](../../../result/channel_denoising/data/colored_score_single_family_20261024/SMOKE.json)。前版数学核查为单独代理审阅，继承同一任务上下文，非盲审；本版沿用未变的条件 DSM/均值公式，重新执行代码检查。旧版源码、配置、测试和说明完整保存在[四类方案快照](../../../result/channel_denoising/data/colored_score_20261024/four_class_snapshot/MANIFEST.json)，旧 PLAN/CHECKS/SMOKE 未覆盖。

## 4. 下一阶段的最小配对对照已经准备

三种模型：冻结 AWGN 网络、继续用 AWGN 训练的一阶网络、单一有色 Gaussian 噪声族训练的一阶网络。后两者用相同初始化、相同行号顺序、相同噪声强度/基础白噪声、batch size 8、学习率1e-5、固定1000步；无验证集选 checkpoint，使用最后一步。这些预算是试运行配置，不是已训练结果。三个对照模型不代表三类混合训练噪声。

评价同一个有色噪声族，参考噪声 SNR -10/0/10/20 dB；每档均用1000个不同验证场景，编号0–999，各取一个预先随机抽取并存储的用户信道。所有模型处理同一输入；保存每场景误差及信号能量，以总误差除以总信号能量计算 NMSE。不再扫描四种噪声类别，AWGN 退化保留在单独的实现检查中。

训练和验证场景不重叠，路径与哈希已核查。由于冻结一阶模型曾使用这个验证库选权重，本轮必须称为开发验证，不是从未接触的最终测试集。它只能判断合成条件噪声下是否值得继续；实际消息匹配程度和活动检测效果仍需后续验证。

本对照同时改变训练噪声分布、协方差条件输入和矩阵均值恢复，比较的是这套配套修改的整体效果，不能把未来收益唯一归因于其中一项。只改采样器而仍使用原 AWGN 目标与读出并不构成相同条件 score 的正确实现。

代码位于 [独立候选目录](../../../src/training/colored_score_20261024)，配置为 [colored_score_20261024.json](../../../src/configs/training/colored_score_20261024.json)，结果入口为 [PLAN.json](../../../result/channel_denoising/data/colored_score_single_family_20261024/PLAN.json)。配置及候选 checkpoint schema 升为 v2，避免与旧采样方案混用。没有改动冻结网络、第二阶网络、活动分类器、STMP 接收机或 FINAL 绑定。

复现已执行的检查：

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -B -m pytest -q src/tests/test_colored_score_20261024.py
.\.venv\Scripts\python.exe -B -m training.colored_score_20261024.run plan
.\.venv\Scripts\python.exe -B -m training.colored_score_20261024.run smoke --device cpu
```

以下为后续显式启动命令，本轮未执行。应在现有 GPU 实验完成或另有空闲资源后执行；不会自动排队或占用 GPU。

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -B -m training.colored_score_20261024.run train --arm white --device cuda
.\.venv\Scripts\python.exe -B -m training.colored_score_20261024.run train --arm colored --device cuda
.\.venv\Scripts\python.exe -B -m training.colored_score_20261024.run evaluate --device cuda
```

训练输出各用独立目录，若已存在则不覆盖。此最小试运行脚本不实现断点恢复；失败日志保留，再试时使用新的 output 目录。
