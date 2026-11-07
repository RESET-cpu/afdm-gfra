# L-DAMP 实现与验证

当前安装的是经有限规模验证的逐波束五段版本。2026-10-15 的联合去噪实现及 420 项独立配对验证已完成；新版仅改善 0.052–0.190 dB，平均耗时约为原版 6.91 倍，故保留原版默认配置。具体不足、完整结果和采用决定见[当前开发记录](../../../archive/paper_layout_20261026/original_paper/docs/history/results/ldamp_complete_20261015/REVIEW.md)。上一轮联合波束候选失败及原因、公共 NMSE 评分修正见 `results/ldamp_implementation_20261014/REVIEW_20261014.md`。

联合候选的公共接口、模型包、完整导数核验和复现命令见 [LDAMP_JOINT.md](LDAMP_JOINT.md)。联合版通过显式配置调用，活动标定及独立配对验证均已完成；它是可选实现。

本文件描述复数多用户 AFDM 适配。安装状态以 `configs/ldamp.json` 和完整的[验证报告](../../../result/ldamp_implementation_20261014/REFERENCE_REPORT.md)为准；去噪有效、数值有限或仅优于零估计都不单独构成性能结论。

## 原文与项目适配

原始依据是 He 等 2018 WCL [作者稿](https://arxiv.org/pdf/1802.01290v2) §III-A 式(4)–(8)、§IV-A，以及 Metzler 等 [Learned D-AMP](https://arxiv.org/abs/1704.06625) §3。分别训练各噪声区间的去噪器是原文允许的训练方式；未做端到端训练本身不是实现错误。He 原场景是单用户实数波束域图像，不能原样套用到本项目的复数、重复观测算子及活动混合先验。具体来源与术语见 [TERMINOLOGY](TERMINOLOGY.md)，所有下载全文、作者代码与权重均保留。

保留十轮 AMP、跨轮共享的噪声分段 DnCNN、残差学习及 Onsager 校正。每个网络有二十个 3×3 卷积层，隐藏宽度 64，输入为实、虚两个通道；同一个网络用于所有用户和波束。每个中间层包含 BatchNorm 和 ReLU，推断冻结其统计。网络输出为输入减去预测噪声；其清洁输出 MSE 与噪声残差 MSE 代数等价。

公开 4×4 UPA 上作固定单位化 DFT；对完整 AFDM 信道作双边逆 DAFT、循环滞后重排及时间轴单位化 DFT。所有系数保留，输出完整逆变换。它们是可逆坐标操作，不需要真实方向、时延或 Doppler，也不把变换系数直接命名为连续物理路径参数。阵列变换同时用于观测，公开感知算子保持不变。

固定训练总体尺度为 0.2647966452702405，不按测试真值逐样本归一化。五个复方差区间的边界是 [0.001,0.01,0.1,1,10,100]，区间内对数均匀采样，实虚噪声各占一半方差。每区间采用固定输入尺度 sqrt(1+方差几何中点)，输出乘回同一尺度。越界使用端点网络并记录次数；没有方差 100 以上的独立 AWGN 去噪资格结论。

## 复数矩阵校正

将 H[k,m,r,n] 重排为 X[(k,n),(m,r)]，取 g=sqrt(‖P‖²_F/(KN))、A=P/g、y=Y/(scale·g)。更新为

\[
R^t=X^t+A^H Z^t,\qquad X^{t+1}=D(R^t;\Sigma^t),
\qquad Z^{t+1}=y-AX^{t+1}+Z^t B^t,
\]

\[
\Sigma^t_{ab}=Q^{-1}\sum_\mu Z^t_{\mu a}\overline{Z^t_{\mu b}},
\qquad B^t_{ab}=Q^{-1}\sum_i\frac{\partial D_{i,b}}{\partial R_{i,a}}.
\]

B 的第一个下标是输入特征，第二个是输出特征，导数采用 Wirtinger 定义。完整推导及高斯矩阵近似的位置见 [MATRIX_DERIVATION](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/ldamp_repair_20261014/MATRIX_DERIVATION.md)。固定波束网络彼此独立，因此跨波束 Jacobian 块解析为零，各 16×16 块均保留。

固定当前协方差、网络选择、BN 统计及 ReLU 状态，按链式法则计算实方向导数 L(U)、L(iU)，以 [L(U)−iL(iU)]/2 抵消共轭导数。每轮使用八个随机探针，种子 202610146201；方向导数由网络精确计算，部分迹仍是 Monte Carlo 估计。批量为 128，无按真值停止或失败回退。

去噪器仅使用每波束协方差的平均对角值选择网络，没有对白化后的相关误差作保证。AFDM 结构矩阵不满足所引用独立高斯矩阵分析的全部条件，因此理论公式核验与经验性能验证分别报告。

## 活动判决与证据

活动分数为 E_k=‖Ĥ_k‖²_F，使用已冻结的全局门限，并要求 E_k>0。分数是能量，不是概率。门限绑定推断代码、网络和设置的身份；没有对应门限时只输出分数，不给出活动判决。

第一次相对能量规则在独立 −4 dB 场景出现大量虚警，完整失败结果保留在 [首次验证](../../../archive/paper_layout_20261026/original_paper/docs/history/results/ldamp_implementation_20261014/independent_validation)。这 24 个原校准/评价场景随后全部转为开发数据，选择直接信道能量并校准门限 9.8172401072021。网络及信道估计没有因此改变。新场景结果与统一 10 场景比较分别报告；不得把这 24 个场景重称为最终独立验证。

比较以同一公开输入为准，完整信道 NMSE 使用总平方误差除以总真值能量，包含非活跃用户的估计误差。活动错误率分母为全部用户。各 SNR 复用物理场景，置信区间按物理场景成组重采样。旧 Proposed 比较曲线对应其原冻结版本，不等于后来调整阻尼后的当前默认版本。不同历史时间与并发 CPU/MPS 时间不用于声称运行速度排名。

## 接收噪声与去噪输入误差

当前物理观测保持 Y=AX+W，W 的元素独立且具有同一复方差 σ²。固定单位化阵列 DFT 保持 σ²I，不产生不同波束具有不同物理噪声方差的模型。L-DAMP 去噪输入却是 Rᵗ=Xᵗ+AᴴZᵗ；初始 X⁰=0、Z⁰=Y 时，R⁰−X=(AᴴA−I)X+AᴴW。第一项包含未消除的信道混叠，各波束信道能量不同可以使整个误差功率不同。这是观测方程的代数分解，不依赖 AMP 状态演化假设。

He §III-A 式(6)的 equivalent noise 和 Metzler §2.1 的 effective noise 指去噪输入与目标之差，与观测中的 W 不能混为一谈。用残差估计各波束有效误差方差、在去噪训练中覆盖其差异，可以作为本场景的算法适配；不得改动物理噪声生成规则或向推断提供真值误差。将这种误差近似成各波束不同方差、彼此独立的 Gaussian 扰动，仍忽略相关性和非 Gaussian 成分，须单独检验，不能称为系统模型本身。

## 训练与使用

训练使用原 50000 个完整物理用户信道及独立的 5000 个验证信道库，并校验文件 SHA 和物理场景不交叠。本轮选择固定 512 个验证用户：初始 1–10 段训练过程内部先用每用户一个空间坐标选权重，最终资格检查与其余区间均评价全部 16 个空间坐标。非活跃样本按 p=0.1 置零。先训练 1–10 段 5000 步，并仅用训练数据重估 BN；其余四段从该网络分别训练 5000 步，按固定验证 MSE 选择权重并比较训练数据 BN 重估版本。训练配置、源文件、随机种子、学习率和全部历史均写入输出目录。

所报性能绑定保存权重和对应源代码快照。当前入口采用已核对等价的 FFT 变换实现，提供同一训练方法的可重复配方；不将不同硬件、软件或浮点计算路径下的重训描述为逐位相同的权重轨迹。

```sh
.venv/bin/python scripts/train_ldamp.py --output results/ldamp_new_training --device mps
.venv/bin/python scripts/validate_ldamp.py --config results/ldamp_new_training/receiver.json --output results/ldamp_new_validation --device mps
.venv/bin/python run.py run --method ldamp --input INPUT.npz --output NEW_LDAMP.npz --device mps
.venv/bin/python run.py evaluate --estimate NEW_LDAMP.npz --truth TRUTH.npz
```

`--smoke` 仅检验流程，输出标为 SMOKE_ONLY，不能进入正式验证。`--resume-from` 要求相同配方和源文件，将已完成阶段复制到新输出目录，未完成阶段重新执行；不是逐更新精确续训。训练不会自动安装权重；独立校准与接收机验证仍须随后完成。

旧失败实现、权重和结果保留供复查，新入口仍统一为 `ldamp`。资产哈希通过只代表身份一致，不能替代接收机性能通过。

## 当前验证结果

已通过另外 16 个全新物理场景 × 六 SNR 的独立接收机检查。按用户指定的固定前 10 场景 × 六 SNR 配对比较，L-DAMP 全信道 NMSE 为 −2.908、−3.544、−4.216、−5.270、−6.112、−6.538 dB，活动错误率为 1.00%、0.75%、0.50%、0.25%、0.25%、0.25%。60 次推断无数值失败；600 次去噪调用中 13 次使用范围外端点规则。0–6 dB 优于 SOMP，高 SNR 与 GNN-ASPL 接近，仍弱于 off-grid SBL 和原冻结 Proposed。10 场景结果用于有限规模比较，区间按物理场景成组重采样；不作稀有错误率或跨训练种子稳定性的充分统计声明。

见[六方法比较](../../../result/ldamp_implementation_20261014/paired_comparison_10/SUMMARY.json)和[比较图](../../../result/ldamp_implementation_20261014/paired_comparison_10/comparison.png)。扩大运行已按用户要求停止，全部 191 个完成结果仍保留。

复审保留逐波束版本：完整变换、网络与方向导数经过独立稠密计算和自动微分核对；联合波束候选虽然通过 AWGN 去噪检查，却在实际接收机中失败。两个开发场景的第一轮 oracle 对照表明，各波束噪声方差差异已能复现联合候选的大部分误差，此时尚未发生 Onsager 校正。逐波束选段与此处的不同噪声方差相适应；未使用波束编号或跨波束关联仍是明示的建模简化。详细证据及适用范围见[复审](../../../result/ldamp_implementation_20261014/REVIEW_20261014.md)。

公共评分中的 `nmse_db` 现与比较图统一，包含非活跃用户误差；`active_nmse_db` 仅为另列的活跃用户诊断指标。既有图表使用完整误差，无需改写。最终来源与接口核验见 [FINAL_AUDIT.json](../../../result/ldamp_implementation_20261014/FINAL_AUDIT.json)。

## 输出 TSVD 改进（2026-10-15，独立比较完成）

后续结构对照保存在 `docs/history/experiments/ldamp_structure_20261015/` 与
`docs/history/results/ldamp_structure_20261015/`。以当前冻结逐波束 L-DAMP 为基础，对每个用户的
完整估计信道按空间维展开为 \(H\in\mathbb C^{16\times256}\)，保留一个奇异分量。
Truncated SVD 的术语与原文位置见 [TERMINOLOGY.md](TERMINOLOGY.md)。
该操作只读取估计信道，不读取真实活动、角度或信道。零用户内路径方向扩展是当前
物理模型的条件；物理信道秩一不能推出后验均值必须秩一。

本轮区分最终输出处理和每轮复合去噪。最终输出处理不进入 AMP 递推，原校正不变；
每轮复合去噪会引入跨波束依赖，必须连同投影一起求导并保留完整跨波束校正。
令 \(C=HH^H\)，最大特征值及其单位特征向量为 \(\lambda_1,u\)，则
\(F(H)=uu^H H\)。当最大特征值为单根时，对实方向 \(\Delta H\)，直接求导为

\[
\Delta C=\Delta H H^H+H\Delta H^H,\qquad
v=\sum_{j\ne1}u_j\frac{u_j^H\Delta C u}{\lambda_1-\lambda_j},
\]
\[
DF(H)[\Delta H]=uu^H\Delta H+(vu^H+uv^H)H.
\]

公式实现通过独立完整 SVD 自动微分、实/虚方向有限差分及包含共轭路径的复合函数核验。
零矩阵处的一阶方向响应并非方向的线性函数，开发实现明确采用零方向约定；非零重复首特征值
作为不可微情形报告，未通过任意加大特征值间隙隐藏。递推对照仅作开发证据。

两个旧场景、三个 SNR 的开发结果中，最终输出处理改善全信道 NMSE 约 1.71–2.03 dB，
每次附加处理约 4–5 ms。每轮加入投影并直接计算校正的版本再改善约 0.19–0.56 dB，
但总时间约为原版 4.7 倍。因此先选择最终输出处理进入后续验证，见 `SELECTION.json`。
新活动分数采用投影后的信道能量，在八个旧场景上拟合一个共同阈值；另外保留原活动判决
作为独立对照。十个新测试场景已预先固定，并与训练、标定及上一轮测试种子隔离。
这些开发结果不能当作独立验证，也没有解决基础网络的训练误差分布失配。

公共执行入口为 `scripts/run_ldamp_structure.py`，已提供配置
`configs/ldamp_output_tsvd.json`，默认采用 `--activity-rule original`。它读取同样的四字段 `ReceiverInput` 文件，完整保存
未按活动判决置零的估计、投影后能量、活动判决及推断身份。示例：

```bash
.venv/bin/python scripts/run_ldamp_structure.py \
  --config configs/ldamp_output_tsvd.json \
  --input path/to/input.npz \
  --output results/ldamp_output_tsvd_run/estimate.npz
```

模型、结构操作和阈值分别绑定，错误的阈值身份会被拒绝。
`scripts/run_ldamp_structure.py --help` 可查看设备及路径选项。
论文比较应明确标识为 “L-DAMP + output TSVD”，同时保留原版 L-DAMP 的来源和结果。

`--activity-rule calibrated` 使用投影后能量的冻结标定阈值；
`--activity-rule original` 原样保留基础 L-DAMP 的活动评分及判决，同时输出结构处理后的信道。
两种判决规则均作为本轮预先定义的配对对照，结果文件明确记录所用规则与对应阈值配置。

十个全新场景 × 六档 SNR 的独立比较已完成，60 个条件、180 组输出均通过重算。
全信道 NMSE 改善依次为 1.014/1.089/1.048/0.934/0.916/0.850 dB，
对应 −4/−2/0/2/4/6 dB，六个逐点配对 95% 区间均低于零。
60 个条件的全信道误差和活跃用户误差均下降；这些是十个独立场景上的相关条件，
不能当作 60 个独立样本。附加处理平均 4.28 ms，基础推断平均 11.97 s。

**重新标定的投影能量活动阈值未改善检测：** 新场景的漏检数为
11/10/6/5/4/3，原版为 7/5/4/4/2/2，虚警均为零。
这一失败已完整保留。预先设置的原判决对照具有同一份增强信道估计，活动判决逐项与原版一致；
公开命令默认采用该模式。该采用建议形成于本轮比较之后，没有重调新阈值，也不是又做了一次
采用后盲测。两种模式的公开命令重放结果均与保存的比较输出逐位一致。

完整表格、配对区间及曲线见[输出 TSVD 比较报告](../../../result/ldamp_structure_20261015/independent_validation/REPORT.md)，
来源与执行验证见[最终审计](../../../archive/paper_layout_20261026/original_paper/docs/history/results/ldamp_structure_20261015/FINAL_AUDIT.json)。
当前原版主线配置继续保留以复现原有六方法比较；增强版作为明确标注的可用对照提供。
