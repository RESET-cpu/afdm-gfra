# 七项核心实验

每项实验一个入口文件，参数在文件顶部的 `EXPERIMENT`，共用调用与评分在 `_common.py`。
算法源码、冻结权重、原 500 场景正式结果保持不变。

| 实验 | 文件 | 默认条件 | 训练样本量对照 |
|---|---|---|---|
| SNR 对比 | [snr_comparison.py](snr_comparison.py) | −4～6 dB，间隔 2 dB；每点 500 场景 | **支持** |
| 导频帧数 | [pilot_frames.py](pilot_frames.py) | 8、16、24、32、40、48；每点 500 场景 | 不添加 |
| 用户数 | [user_count.py](user_count.py) | 20、40、60、80、100；每点 500 场景 | 不添加 |
| 活动概率 | [activity_probability.py](activity_probability.py) | 0.05～0.25，间隔 0.05；每点 500 场景 | 不添加 |
| 收敛对比 | [convergence.py](convergence.py) | −4、0、4 dB；每点 20 场景；附 Proposed 的 DFT/Hadamard 对照 | 不添加 |
| 独立信道去噪 | [channel_denoising.py](channel_denoising.py) | 复噪声方差 0.001、0.01、0.1、1、10、100；500 场景×4 信道 | **支持** |
| 跨信道模型 | [cross_channel.py](cross_channel.py) | NTN-TDL-D/A/B/C，各扫描 −4～6 dB；每点 500 场景 | 不添加 |

接收机实验比较 Proposed、Off-grid SBL、GNN-ASPL、GAMP-SBL、SOMP，固定权重及判决规则，估计相位与噪声。
除扫描变量外，默认 40 用户、16 导频帧、16 天线、0 dB、活动抽样概率 0.1。
独立去噪使用已知加性噪声方差，不运行接收机或活动检测。

## 运行入口

所有入口均提供 `plan / run / summarize`。先在新的空目录保存计划，再运行。
`run` 可继续未完成的条件；`summarize` 只汇总和绘图。运行、汇总只读取已保存计划，命令行参数只在 `plan` 生效。

```sh
.venv/bin/python -B experiment/snr_comparison.py plan --output results/snr_new
.venv/bin/python -B experiment/snr_comparison.py run --output results/snr_new
.venv/bin/python -B experiment/snr_comparison.py summarize --output results/snr_new

# 其他实验替换入口文件和输出目录，例如：
.venv/bin/python -B experiment/channel_denoising.py plan --output results/denoising_new
.venv/bin/python -B experiment/cross_channel.py plan --output results/cross_channel_new

# 查看已完成的原 500 场景结果，无推断或修改
.venv/bin/python -B experiment/snr_comparison.py saved
```

前四项扫描通过 `--values` 设置条件；收敛使用 `--snr`；去噪使用 `--values` 设置复噪声方差；
跨信道使用 `--profiles D A B C --snr -4 -2 0 2 4 6`。
各入口支持 `--scenes`、`--seed` 等参数，详见 `--help`。收敛沿用 CPU，其余默认 CPU，也可指定 `--device`。

每个计划记录源码及权重哈希。代码或权重变化后，应创建新计划，不能改旧计划的哈希冒充原实验。
历史入口已保存在 `archive/seven_experiments_20261018/experiment/`；原始 `experiments/` 复现依赖继续保留。

## 导频帧数扩展与 Off-grid SBL 预算

导频支持 1～48 帧，且不得超过 `K·N`。32 帧以内沿用原生成结果；40/48 帧使用同一部分 DFT 行排列的前缀。
前 32 帧标准噪声保持原值，第 33～48 帧来自独立固定随机流，40/48 帧继续共享前缀。
真实信道和相位斜率保持配对，按各帧数的实际无噪声接收功率设置 SNR；没有填零扩展观测。

新实验统一采用 `configs/experiments/offgrid_sbl_600.json`：Off-grid SBL 最多 600 轮，容差仍为 1e-4，
原超参数变化、偏移增量、噪声变化三项停止条件不变。达到预算必须如实报告，不能计作满足收敛条件。
原 `configs/offgrid_baselines.json` 的 120 轮配置和已有结果保留；原 500 场景 Off-grid 结果不能标成 600 轮结果。
新判决策略文件明确记录：复用原 120 轮策略的阈值，**尚未针对 600 轮重新标定**，也未使用正式测试标签调参。
原标定记录嵌入来源字段，不冒充新预算的标定结果；完整新配置与阈值文件均纳入计划哈希。

## 训练样本量只用于 SNR 和去噪

当前只有已冻结的完整 Proposed 三网络，训练库包含 50,000 个干净信道。
小样本三网络尚未训练，本次整理不会启动训练。建议下一阶段准备 5,000 信道版本。
未传入小样本配置时，入口可运行现有模型，但计划和汇总明确标记 `PENDING_SMALL_WEIGHTS`，不产生虚假的小样本曲线。

小样本版本就绪后，两个实验引用同一份**条件接收机** `receiver.json`：

```sh
.venv/bin/python -B experiment/snr_comparison.py plan --output results/snr_two_sizes --small-config runs/proposed_5000/receiver.json
.venv/bin/python -B experiment/channel_denoising.py plan --output results/denoising_two_sizes --small-config runs/proposed_5000/receiver.json
```

上述路径是未来输出位置示例，当前不存在。配置必须绑定该版本自己的一阶、二阶和活动分类器，
以及记录真实 `train_samples` 的先验文件。入口检查网络哈希、教师/先验关系、推断控制、坐标尺度及较小的训练库，
禁止把同一套权重改名后充当小样本版本。配置、先验和三份权重全部加入计划哈希。
其余五个入口不接受 `--small-config`。

`N_train` 指当前干净信道训练库大小，不是测试场景数，也不包含在线噪声增强次数。
现有权重使用历史初始化检查点，入口不会把训练库大小包装成“此前仅见过这些样本”。
正式解释样本效率前，需要核实初始化数据来源；若不一致，应重新训练配对的完整/小样本模型。
训练集应按物理场景分组取嵌套子集，固定独立验证与测试场景。小样本二阶与分类器使用自己的教师。

## 独立信道去噪

每场景在活动掩码之前均匀选取 4 个候选用户，得到完整物理信道，统一除以冻结尺度。
用 `R = H/scale + sqrt(v) Z` 生成查询，`Z` 为单位方差复高斯噪声；不同方差复用同一标准噪声。
所有模型共享完全相同的信道与查询，不按单条信道重新归一化，不选择已被接收机正确检测的用户。
默认新测试种子与训练、验证独立；计划会拒绝与先验记录中的训练/验证场景种子范围重叠。

比较噪声输入、使用训练二阶矩的各向同性 Gaussian 先验线性估计、Proposed 一阶去噪结果及 Genie-aided MMSE 下界。
线性参考为 `P/(P+v) R`，`P` 来自原训练统计，不使用测试真值拟合。
二阶网络单独报告原始预测误差与实测平方误差的比值，理想平均匹配线为 1；
不裁剪负方差、不隐去失败样本，另计负方差预测数。该比值只检验整体平均误差，不能证明逐查询条件校准或精确后验协方差。

下界参照 [Cai §VI-B Fig.4 的 Genie-aided lower bound](https://arxiv.org/html/2506.00581v2#S6.SS2)，
但本项目首个 LOS 分量为定模随机相位，不能把只知道几何的 LMMSE 直接当成 MMSE 下界。
这里额外向 Genie 提供真实 LOS 复增益，以及各路径的时延、多普勒、方向和期望功率；未知散射增益仍需估计。
这些真值信息只进入下界，不进入 Proposed 或 Gaussian 参考。

在冻结训练坐标中写作 `h = m + B g`，`m` 为已知 LOS 信道，`B` 为含功率平方根的散射路径矩阵，
`g ~ CN(0,I)`，`r = h + sqrt(v) z`。条件均值为
`m + B(BᴴB + vI)⁻¹Bᴴ(r-m)`，条件总 MSE 为 `Σᵢ v λᵢ/(λᵢ+v)`，`λᵢ` 为 `BᴴB` 的特征值。
实现使用薄 SVD，不把有限样本中重合或近重合的路径当成独立正交方向。
额外信息不会增加最优总体 MSE，因此它给出总体平均意义的下界；本项目这项额外 LOS 信息与 Cai 的侧信息设定不同。
图中汇总解析条件 MSE，并除以与其他曲线相同的测试信道总能量；有限场景估计不保证逐样本大小关系。
同时保存 Genie 后验均值的实际平方误差，`error_kind=analytic_conditional_mmse` 明确区分解析风险与实际误差。

输出 `denoising.png/pdf`（NMSE 与误差预测两面板）、`STATISTICS.csv`、`SUMMARY.json`，以及每场景每条件的逐信道误差。
首场景保存完整查询、真值和预测；其余可凭固定种子和输入哈希重新生成。
该实验不验证活动分类器，也不替代接收机模块消融。

## 跨信道模型

功率时延表采用 [3GPP TR 38.811 V15.3.0 §6.9.2，表 6.9.2-1～4，印刷页 89–90](https://atisorg.s3.amazonaws.com/archive/3gpp-documents/Rel15/ATIS.3GPP.38.811.V1530.pdf)。
A/B 为 Rayleigh 分量，C/D 的首抽头由同延迟的 LOS 与 Rayleigh 分量叠加。
保留表中相对功率、标准化时延与现有 30–50 ns 时延缩放范围。
各模型总期望抽头功率与现有 D 一致；只作分布级缩放，不对单次信道能量归一化。

D 直接调用原生成器，保持原数值；A/B/C 共享场景几何、活动、导频、标准化噪声并生成相应衰落。
接收机不读取信道模型标签，所有条件使用同一套原权重和估计相位/噪声流程，不重新训练或调整判决阈值。
结果按模型分列，分别画 AER 与 NMSE 随 SNR 的变化，保存每条件的来源、功率缩放和生成参数。

这里验证的是**本项目固定几何模型下的 NTN-TDL 功率时延及衰落分布变化**：
保留每用户共同方向和共同卫星多普勒，没有额外实现地面散射引起的完整时变多普勒谱，不能宣称全面复现全部标准信道特性。

## 收敛实验内的导频类型对照

参考 [Cai §VI-C Fig.12](https://arxiv.org/html/2506.00581v2#S6.SS3)，在同一个 `convergence.py` 入口增加 Proposed 的部分 DFT / 部分 Hadamard 对照。
保留原五方法 DFT 收敛图，另输出 `convergence_pilots.png/pdf`；DFT 的 Proposed 轨迹直接复用，不另算成第八项实验。
不添加训练样本量变化，不重训网络，不修改算法参数或原生停止规则。

默认命令自动包括该对照；只需要原五方法图时可在创建计划时指定 `--pilots dft`：

```sh
.venv/bin/python -B experiment/convergence.py plan --output results/convergence_pilots_new
.venv/bin/python -B experiment/convergence.py run --output results/convergence_pilots_new
.venv/bin/python -B experiment/convergence.py summarize --output results/convergence_pilots_new
```

默认共 20×3×(5+1)=360 条迭代轨迹；每个 SNR 的首场景还要执行未加观察器的配对核验。
显式选择不含 Proposed 的 `--methods` 时默认只跑 DFT；Hadamard 对照需要选择 Proposed。

两种原始导频均为 `Q × (K·N)`，每用户每帧能量为 1，行 Gram 矩阵为 `K I`。
当前 `K=40、N=16` 的 640 列 Hadamard 使用 20 阶 Paley 构造连续倍增得到，不补列或增加用户数。
采用随机行/列排列及列符号，元素为 `±1/sqrt(N)`。本入口实现支持 `2^m` 或 `20·2^m` 阶；其他尺寸应使用 DFT-only，不能截断更大矩阵后冒称同样行正交。
构造依据：[Hadamard constructions §4.1 Theorem 1、§4.2 Theorem 3](https://arxiv.org/html/2411.18897v1#S4)。

同一物理场景下保持真实信道、活动、相位、用户数、导频帧数和发送能量一致；更换导频后重新生成接收观测。
沿用原实验的接收 SNR 定义和配对标准噪声：两种导频的实际接收能量可能不同，因此物理噪声方差也可能不同，不能称为固定绝对噪声的比较。
相位估计分别使用各自导频与观测，不读取真值；Proposed 的三个网络、噪声估计和迭代完全保持原样。

原始导频行正交不代表叠加用户各自跨帧相位后的有效算子仍行正交；当前线性模块直接对有效矩阵作 SVD，因此不依赖这个假设。
这里只验证导频类型替换的适配性与数值收敛行为，不把 CPU 中的通用矩阵计算称为 Hadamard 专用快速实现。

## 收敛曲线口径

- 每个物理场景先估计一次共享相位，再运行五种条件接收机；曲线横轴不包括相位搜索轮数。
- 第 0 点为零信道估计。Proposed、GAMP-SBL、Off-grid SBL 按各自原生更新次数记录，GNN-ASPL 按 AMP 展开层数，SOMP 按选取原子数。它们的每轮计算量不同，不能将横轴当作统一计算预算。
- Proposed 和 SOMP 使用已有观察器；其余方法只读完成迭代时的局部状态，不修改冻结求解器文件。Off-grid SBL 在每次超参数更新后，使用该轮参数执行原生的最终后验与信道重构，结果仅供评分，不反馈给算法。
- 真实信道只进入观察评分。每个 SNR 的首个场景自动对照无观察器运行，要求全部最终输出数组逐元素一致、停止轮数和停止原因一致；每条轨迹末点也必须匹配原生最终信道。
- 多场景先汇总完整信道误差与真值能量，再转 dB。已停止的场景沿用最后估计，保持固定场景集合；原始轨迹不伪造后续迭代。各方法绘制到自身最晚停止轮数。
- 逐轮评分、SBL 附加后验重构及 Python 状态观察会增加耗时，因此本实验不作速度排名。有限轨迹反映本次实验的迭代行为，不构成理论收敛证明。

## 记录与统计

所有实验保留失败记录，失败或缺失条件不能从剩余样本汇总成完整结果。
接收机按 `sceneNNN/conditionNN/` 保存输入身份、真值、每方法指标与紧凑预测；首场景保留完整预测。
接收机实验输出 `comparison.png/pdf`、`STATISTICS.csv`、`SUMMARY.json`；收敛额外保留完整范围和前 100 轮曲线。

AER 汇总漏检与虚警，NMSE 先汇总误差和信号能量再转 dB。
同一条件下所有方法共享观测与估计相位；SNR 扫描复用物理场景和标准噪声。
用户数/活动概率扫描可能改变活动集合；去噪每场景的 4 个用户也不是 4 个独立场景。
正式统计区间应按物理场景分组计算。入口提供点估计，不据此宣称统计显著性。

已有正式性能证据仍是 [500 场景 SNR 比较](../results/baseline_comparison_500_20261018/REPORT.md)。
本次小规模检查用于验证代码与记录，不等同于七项正式实验已经完成。
