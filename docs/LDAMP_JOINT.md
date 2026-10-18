# 联合去噪 L-DAMP 候选：模型、数值核验与复现

本候选配置为 `configs/ldamp_joint.json`，通过公共注册器显式传入配置使用。
活动阈值标定及 420 项新场景配对验证已完成，**联合版保留为可选实现，不替换默认配置**。
默认 `configs/ldamp.json` 仍指向原逐波束版本。
训练中的不利结果、统计失配及数值对照见
[开发报告](../docs/history/results/ldamp_complete_20261015/REVIEW.md)。

本轮沿用 `known_phase_geometry_v4`：40 个候选用户、16 次观测、4×4 UPA、
16×16 信道块，名义活动概率 0.1 并条件于非空场景，同一用户的路径方向扩展为 0°。
各方法均得到精确的已知有效测量算子；结论限定于这一条件实验。
物理约定见 [SYSTEM_MODEL.md](SYSTEM_MODEL.md)，每个新场景的几何和噪声记录保存在其
`generation.json` 中。

## 方法范围

文献依据及定位统一见 [TERMINOLOGY.md](TERMINOLOGY.md)。沿用 He §III-A
式(4)–(8)、Metzler §3 的 learned denoising / AMP 思路。本项目处理复数多用户 AFDM，
使用矩阵校正、联合波束去噪和噪声条件输入，因此是明确说明的适配，不能称为 He 原网络的逐项复现。
单独训练去噪器符合引用方法的训练方式；未做端到端训练本身不是缺陷。

公开输入仅有 `ReceiverInput` 的观测、感知算子、噪声方差和活动先验。
网络使用残差估计的有效误差方差；当前去噪器不直接使用输入的活动先验或测量噪声方差。
训练的名义活动概率为 0.1；在至少一名用户活跃的仿真条件下，公开边缘先验为
`0.1/(1-0.9**40)`，这一点不应被严格等于 0.1 的接口检查错误拒绝。

保留原有固定总体尺度 `0.2647966452702405`、阵列酉 DFT、双边逆 DAFT、
循环滞后重排和时间轴酉 DFT。变换保留所有系数，逆变换输出完整物理信道。
物理真值只用于离线数据生成和独立评分，不参与去噪、网络选择、归一化、停止或阈值应用。

## 冻结去噪函数

低噪声分支先使用原五段逐波束 DnCNN，再学习全用户信道的联合残差。
新网络为 20 层、宽度 64 的 Conv/BN/ReLU，输入包含查询的 32 个实通道、
基础去噪输出的 32 个实通道及 16 个公开对数方差通道。
输出残差按每个实坐标噪声标准差 `sqrt(v_b/2)` 缩放。
原五段网络的参数和 BN 统计在联合残差训练期间冻结。

高噪声分支为独立的 20 层、宽度 64、32 个实信号输入加 16 个噪声通道的网络。
训练总体复二阶矩为 `s_b`，公开复方差为 `v_b`，其三个尺度为

\[
c_{\mathrm{in},b}=\sqrt{2/(s_b+v_b)},\quad
c_{\mathrm{skip},b}=s_b/(s_b+v_b),\quad
c_{\mathrm{out},b}=\sqrt{s_bv_b/[2(s_b+v_b)]}.
\]

两支路均看到完整用户查询。若平均波束方差大于 100，全体输出使用高噪声分支；
否则仅方差大于 100 的输出波束使用该分支，其余使用低噪声分支。
这是开发阶段选定的明确规则，既不用真实误差选择，也不在测试集上调整。
单独按波束选择而不检查平均方差的早期规则，在最高噪声段劣于零估计，其结果完整保留。

低分支训练 5,000 步；高分支先训练 3,000 步，再从最佳检查点以学习率 0.001
继续 10,000 步。所有模型用同一 512 用户验证集的六段全信道误差比选择。
最终组合在六段上的误差/零估计误差为
`[0.003018, 0.010246, 0.045511, 0.192293, 0.681953, 0.942942]`。
这些是合成 Gaussian 去噪结果，不能当作接收机结果。

两个所选分支的最佳验证均值都出现在最后一次保存，因此本研究只能报告固定预算训练，
不能宣称已经充分收敛。低分支最后 500 步在前四个方差区间的误差变化为
−0.57%/−0.20%/−0.14%/+0.10%；其六区间均值的较大下降主要来自仍然失效的高方差区间。
高分支最后 500 步的六区间均值改善约 0.11%，但最高方差区间误差反而增加约 1.41%。
完整历史及分区间变化见
[训练轨迹核对](history/results/ldamp_complete_20261015/TRAINING_TRAJECTORY_AUDIT.json)和
[训练曲线](../docs/history/results/ldamp_complete_20261015/training_trajectories.png)。
曲线展示各分支单独的输出；最终按公开方差组合后的验证结果另行报告，不能混同。

训练使用 0.5 的活动采样概率和活动/非活动权重 0.2/1.8，使总体损失对应 0.1。
权重不改变 BN 看到的批次分布。对训练分布重估 BN 的控制未改善验证结果；
这项失配仍需如实报告。实际 AMP 查询误差具有空间相关，网络只输入逐波束平均对角方差，
也尚未解决这一统计失配。

## 完整导数与校正

递推保持
\[
R=X+A^H Z,\qquad X^+=D(R;\Sigma),\qquad
Z^+=y-AX^++ZB,\quad
B_{ab}=Q^{-1}\sum_i\partial D_{i,b}/\partial R_{i,a}.
\]

对当前公开协方差、分支选择和 BN 统计固定后，沿全部查询依赖计算导数。
特别是“基础去噪输出进入残差网络”这一条链不能省略。
以 `[L(U)-i L(iU)]/2` 提取 Wirtinger 部分，保留所有跨波束和用户内部跨位置的依赖。

当前候选直接计算所需的 `ZB`。每个用户的 N 行使用随机正交相位，
针对 Z 的每个观测行施加对应完整方向导数，再对行相位共轭加权求和。
完整 N=16 个方向时，在冻结、用户之间相互独立的去噪器条件下，此处部分迹抽样误差消失。
这是一项代数计算安排，不是新的文献算法名称。详见
[公式推导](../experiments/ldamp_complete_20261015/PROJECTED_TRACE_DERIVATION.md)。

开发候选暂设 10 轮、4 个行方向、观测方向批量 4、种子 202610150201。
一个行方向需要 Q 个复方向，不能与原来的一个矩阵探针视作相同计算预算。
同一已见场景 0 dB 的对照为：

| 设置 | 全信道 NMSE / dB | 相对完整基信道估计差异 | 时间 / s |
|---|---:|---:|---:|
| 2 个行方向 | −7.8377 | 8.24% | 43.1 |
| 4 个行方向 | −7.8712 | 6.04% | 85.0 |
| 完整 16 个行方向 | −7.8698 | 0 | 384.5 |

这些结果属于单例数值开发对照。NMSE 接近不代表活动判决或所有场景都不受抽样影响。
全部六个开发条件和第二个随机种子的结果保存在
`docs/history/results/ldamp_complete_20261015/public_development_v2/`，十二次运行全部完成，无运行警告。
两组种子在 −4/0/6 dB 的汇总 NMSE 分别为
`[−3.3246, −5.8613, −8.5859]` 和 `[−3.2902, −5.8755, −8.6570]` dB。
逐条件信道系数相对差异为 8.5%–23.0%，用户能量分数相对差异为 0.7%–2.1%。
因此只能说这些开发条件的 NMSE 变化较小，不能说系数估计不受抽样影响。
主要系数差异来自非活跃用户，但全信道评分继续包含这些误差。
第二个种子仅用于敏感性检查，后续仍使用检查之前固定的第一个种子，不按误差择优。
数值公式正确也不证明结构化 AFDM 算子满足引用文献的状态演化条件。

保留原逐波束网络、只更换校正计算的六条件对照也已完成，无运行警告。
四种组合的汇总 NMSE 如下，均为两个已见物理场景：

| SNR / dB | 原网络＋原校正 | 原网络＋直接校正 | 联合网络＋原校正 | 联合网络＋直接校正 |
|---|---:|---:|---:|---:|
| −4 | −3.202 | −3.206 | −3.296 | −3.325 |
| 0 | −5.660 | −5.804 | −5.664 | −5.861 |
| 6 | −8.426 | −8.429 | −8.505 | −8.586 |

两项改动的效果取决于 SNR，并有相互影响；不能用一个场景概括全部贡献。
在相同直接校正下，联合网络增益约 0.06–0.16 dB。
上述原校正的矩阵探针与直接校正的行方向计算预算不同，必须同时报告耗时。
本对照的原网络适配器与联合分支内的基础网络数学运算相同，浮点批处理布局不同，
不作逐位相同的断言。全部输出与来源见 `base_projected_control/`。

## 公共接口与绑定

```python
from afdm_jadcedd.algorithm.registry import build_receiver
from afdm_jadcedd.system.observation import load_input

receiver = build_receiver('ldamp', config='configs/ldamp_joint.json', device='mps')
arrays, record = receiver.infer(load_input('path/to/input.npz'))
```

模型包位于 `models/ldamp_joint/v1/BUNDLE.json`，内部路径相对于模型包。
模型、基础五段权重和分支规则绑定 SHA-256。导出后的两个检查点只包含张量及普通 Python 值，
以 `weights_only=True` 加载。加载时逐项核验残差模型内嵌的基础网络与独立基础权重完全一致。
源训练检查点、噪声规则和导出来源也保存在清单中。

推断身份绑定代码、模型包、DAFT 数值矩阵和递推设置。
活动分数为物理信道能量。只有阈值身份与推断身份一致时才输出活动判决。
新候选的冻结阈值为 14.766221508020973，已绑定当前推断身份。
八个标定场景、三个 SNR 的 960 次用户/SNR 判决中有 2 次漏检、0 次虚警；
这 960 次判决并非独立样本，标定结果也不是泛化结果。三个 SNR 均通过最低效用检查。
240 次去噪中有 1 次调用了高噪声分支，未出现平均方差越界，全部推断无运行警告。
同一冻结阈值下，已见六条件的两种子离线诊断没有改变活动判决，
该诊断不构成第二种子的独立阈值资格。来源见 `CALIBRATION_BINDING_AUDIT.json`。
导出低/高/混合分支的输出及完整方向导数已与开发版本逐位一致；
公共接口完整十轮在首个对照场景的输出也逐位一致。

## 复现入口

已有数据和基础五段网络来自原冻结训练配方 `configs/training/ldamp.json`。
基础网络可通过 `scripts/train_ldamp.py` 复现，其来源、步骤及保存的训练状态见
原 [L-DAMP 文档](LDAMP.md)。联合训练用以下入口，所有输出目录应为新目录：

```bash
.venv/bin/python scripts/train_ldamp_joint.py --stage prepare --cache results/ldamp_reproduction/cache
.venv/bin/python scripts/train_ldamp_joint.py --stage high --cache results/ldamp_reproduction/cache --output results/ldamp_reproduction/high
.venv/bin/python scripts/train_ldamp_joint.py --stage refine --cache results/ldamp_reproduction/cache --checkpoint results/ldamp_reproduction/high/best.pt --output results/ldamp_reproduction/high_refined
.venv/bin/python scripts/train_ldamp_joint.py --stage low --cache results/ldamp_reproduction/cache --base-bank models/ldamp_joint/v1/base --output results/ldamp_reproduction/low
```

该入口调用原研究脚本，保留其随机种子、优化器、采样顺序、验证规则和恢复机制。
公开入口的 low 阶段默认基础网络目录是 `models/ldamp_joint/v1/base`，
与原训练所用基础权重逐项相同；也可通过 `--base-bank` 指定重训得到的基础网络。
prepare 阶段读取训练/验证信道及已记录的公开方差形状。
训练面向本次使用的 MPS 环境，不承诺跨设备逐位重现训练轨迹。
`--show-command` 可先检查实际命令，训练阶段支持 `--resume`。
原训练时的源文件快照保存在各结果目录的 `sources/` 下。
已有训练状态要求源文件与计划匹配；历史运行应使用其保存的源快照恢复，
不能将修改过的训练入口与旧状态混用后宣称轨迹完全连续。

`TRAINING_PROVENANCE_AUDIT.json` 的 41 项核验已通过：完整源数据与变换缓存哈希、
训练/验证物理场景隔离、抽样变换逐位一致、历史最佳检查点选择、训练源快照、
初始化绑定及导出张量一致性。复查命令为
`.venv/bin/python docs/history/experiments/ldamp_complete_20261015/audit_training_provenance.py`。
此审计不代替重新训练，也不承诺不同硬件或软件环境下重训得到逐位相同的权重。

已有选定模型可独立导出到一个新目录：

```bash
.venv/bin/python scripts/export_ldamp_joint.py --manifest docs/history/results/ldamp_complete_20261015/range_selection_mean_and_beam/residual_noise.json --output models/ldamp_joint/reexport
```

标定和新场景验证入口已提供；应在开发数值检查完成、模型和设置冻结后运行：

```bash
.venv/bin/python scripts/evaluate_ldamp_joint.py --stage calibrate --config configs/ldamp_joint.json --output docs/history/results/ldamp_complete_20261015/activity_calibration
.venv/bin/python scripts/evaluate_ldamp_joint.py --stage evaluate --config docs/history/results/ldamp_complete_20261015/activity_calibration/receiver.json --output docs/history/results/ldamp_complete_20261015/independent_validation --scenes 10
```

标定使用八个已见场景的 −4/0/6 dB，按全局活动错误最少、并列取最大阈值。
验证固定使用新场景的六个 SNR，并保留所有失败。
默认同时运行当前原版 L-DAMP；可显式选择当前 Proposed 和其它 baseline。
本轮冻结协议计划在十个新场景、六个 SNR 上同时比较 `joint original proposed somp gamp gnn offgrid_sbl`，
通过 `--methods` 明确传入这七项（六种当前方法加原 L-DAMP 版本对照）。
该试验已完成，420 项全部成功，输出位于 `docs/history/results/ldamp_complete_20261015/independent_validation/`；
各方法的配置、代码快照和活动规则均在生成第一个新场景之前冻结。
新场景种子还与共同信道库、GNN 训练/验证、共享活动规则、Off-grid SBL 标定及
两版 L-DAMP 开发/标定的 13 组来源作了交叉核对，均无重叠，见
`docs/history/results/ldamp_complete_20261015/COMPARISON_SEED_AUDIT.json`。
共享活动规则引用的两个历史配置文件已不在原路径；其种子来源由仍在的、哈希绑定的
标定计划与证书核验。本次冻结的实际配置完整保存，未把历史配置缺失记作已验证。
每项保存精确配置与推断身份，避免把历史 damping=0.1 的 Proposed 当成当前 damping=0.2。
不确定性按物理场景配对 bootstrap，用户和同场景多个 SNR 不作为独立样本。
此入口不会自动安装模型或更改主线资产清单。
原始全信道 NMSE 始终作为主指标；另对所有方法统一报告仅按各自活动判决置零后的 NMSE，
该统计不使用真实活动掩码，也不替换主指标。所有数值警告按来源、位置和次数记录。

从已经完成的独立配对结果重建报告：

```bash
.venv/bin/python scripts/report_ldamp_joint.py --results docs/history/results/ldamp_complete_20261015/independent_validation
```

该入口拒绝缺失或失败的配对面板，核验输入、输出和保存源码的哈希，
独立复算活动与非活动用户误差、漏检及虚警，再生成表格、图和配对差值区间。
零观测活动错误可能得到退化的 bootstrap 区间，不能解释为总体错误率为零。
其两个合成夹具测试已通过；正式结果尚未生成，正式图仍需在生成后目视核验。

```bash
.venv/bin/python -m pytest -q tests/test_ldamp_joint_trace.py tests/test_ldamp_joint_bundle.py
```

本次四项公共检查已通过，包括独立显式复 Jacobian 的完整校正及三轮递推、
导出一致性、旧主线身份保持和错误阈值绑定拒绝。
第一轮接口检查因错误要求活动先验严格等于 0.1 而失败，记录保留在
`docs/history/results/ldamp_complete_20261015/public_development/`；修正后另存新运行目录。

## 本轮独立结果与使用决定

十个新物理场景、六个 SNR 的完整比较见[独立报告](../docs/history/results/ldamp_complete_20261015/independent_validation/REPORT.md)。
联合版相对原版的全信道 NMSE 改善为 0.190/0.112/0.052/0.153/0.131/0.076 dB，
对应 −4/−2/0/2/4/6 dB；0 dB 的配对 95% 区间包含零。
平均推断时间为 103.00 s，原版为 14.91 s；探针定义和网络结构不同，不作相同计算预算比较。
−4 dB 联合版多一次漏检，其余 SNR 活动错误相同。
因此保留原版默认配置，联合版以 `INDEPENDENTLY_EVALUATED_NOT_DEFAULT` 标记，
通过本文公开接口显式选择。模型和阈值未按独立测试结果调整。

改善主要包含非活跃用户误差的减少；0 dB 活跃用户误差甚至略增，
不能将小幅总 NMSE 改善等同于活跃信道恢复已显著改善。
600 次去噪调用中仅 2 次对部分波束使用高噪声分支，最大平均方差 23.47，
因此本面板不验证平均方差大于 100 时的接收机效果。

420 项输出评分复算、60 组输入精确重建和模型来源核验均通过。
另在一个固定条件重放四种带警告的方法，57,648 次 NumPy 矩阵乘法满足操作数范数缩放误差界，
最终输出逐位复现；不将此范围扩大为对全部条件、所有底层库运算的保证。
训练未充分收敛、相关误差失配和有限场景统计的限制仍然成立。
完整判断见[最终复审](../docs/history/results/ldamp_complete_20261015/REVIEW.md)。
