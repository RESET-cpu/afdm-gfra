# 五个 baseline 的噪声估计

2026-10-15 起，`run/baseline` 的五个 baseline 默认 `--noise-mode estimated`。
默认相位仍从原始导频估计。接收机公开文件只需 `observation`、`pilot`、`activity_prior`；
已知相位条件将 `pilot` 换成 `operator`。旧文件中的 `noise_variance` 字段允许保留，但不会读取其值。
噪声单位统一为复噪声方差 E|W|²，每个实分量方差为其一半。
2026-10-17 起 Proposed 也默认使用本页的空间协方差 MDL 噪声估计：先从观测估计一次物理噪声方差，再输入原条件接收机，三网络和迭代规则不变。
20 场景 × 八档 SNR 的配对验证中，全部活动判决不变、逐 SNR 汇总 NMSE 最大恶化 0.0623 dB，
符合预设性能容差；见[采用决定](../results/phase_optimization_20261017/NOISE_DECISION.json)。
当前五方法比较统一采用估计噪声。下方历史实验仍按其原有信息条件解释。

| 方法 | 原论文核对 | 当前实现 |
|---|---|---|
| SOMP | [Tropp–Gilbert–Strauss 作者稿](https://tropp.caltech.edu/papers/TGS05-Algorithms-Simultaneous-I-preprint.pdf)，§3.1 Algorithm 3.1 将停止准则作为输入；没有独立噪声估计器 | 用空间样本协方差估计噪声，代入原残差停止阈值和活动判决的 SNR 节点。该前端为项目适配。 |
| GAMP-SBL MMV | [Zhang 2023](../references/zhang2023_gamp_sbl_grant_free_noma.pdf)，式(17)–(19)，噪声精度的 Gamma-MAP 更新 | 保留输出后验的均值和方差项；沿用既有先验强度，使用空间协方差噪声估计设置其尺度。复 MMV 及数据依赖尺度是项目适配。 |
| GNN-ASPL | [Ding 2026](../paper/literature/ding2026.pdf)，式(12)–(13)使用 σ²；式(19)、(26)更新稀疏概率，没有更新 σ² | 用空间协方差估计值代入固定噪声位置；网络权重和十层推断保持。该前端为项目适配。 |
| off-grid SBL | [Wei 2022 作者稿](https://arxiv.org/html/2101.05629v1)，式(45)–(46)、Algorithm 1、§VI-A | 保留完整后验期望残差和原噪声初值，推广到共享噪声的 MMV；当前 Gamma 先验由空间噪声估计设置。原文 c=d=1e−4，当前先验属于项目适配。 |
| L-DAMP | [He 2018 作者稿](https://arxiv.org/pdf/1802.01290v2)，§III-A 式(4)–(6)及式(5)后的定义 | 沿用校正残差估计等效噪声；原复数矩阵适配及网络区间选择已使用残差协方差。额外输出的空间噪声估计仅作诊断，不参与去噪或活动判决。 |

实现为 `algorithm/baseline_noise.py`、`noise_estimation.py` 和 `offgrid_noise.py`，
数值设置为 `configs/baseline_noise.json`。原条件内核和权重不改写，供显式 `--noise-mode known` 参考使用。

## 空间协方差噪声估计

把 Q 帧、每帧 N 个接收采样视为 T=QN 个 M 维空间样本，形成未经均值消除的
R=Y_sᴴY_s/T。模型为低秩接收信号与空间白噪声之和。设样本特征值降序为 λ₁,…,λ_M，
候选空间秩为 k=0,…,M−1，尾部特征值的算术均值为 a_k，几何均值为 g_k：

\[
\widehat k=\arg\min_k\left[T(M-k)\log\frac{a_k}{g_k}
 +\frac{k(2M-k)}{2}\log T\right],\qquad
\widehat\sigma^2=a_{\widehat k}.
\]

秩选择使用 Wax–Kailath 的 minimum description length（MDL）准则；核对来源为
[Nadakuditi–Edelman，TSP 2008](https://math.mit.edu/~edelman/publications/sample_eigenvalue.pdf)
§II-A 式(5)–(7)及尾部均值定义，期刊 pp.2626–2627。该文重述 1985 年原准则；本项目没有实现该文随后提出的新估计器。
给定秩后，a_k 是“低秩信号协方差 + σ²I”模型的噪声极大似然估计。
算法不读取活动用户数，也不把空间秩当作用户活动判决。

当前场景为 16 天线、256 个样本，用户内路径方向扩展为零，使低秩空间模型具有依据。
弱信号可能并入噪声子空间；满秩信号、有色噪声、时间相关及模型失配会影响估计。
MDL 的经典一致性不自动成为当前 AFDM 样本的保证。实现要求至少两根天线且样本数大于天线数。

## 两个 Bayesian 基线的更新

设 Y 有 L×M 个复元素，噪声精度 γ=1/σ²，Gamma 先验采用 shape/rate 参数化。
GAMP 由输出端近似后验得到 û 和 vᵘ：

\[
\gamma^{\rm new}=\frac{LM+c-1}{\sum_{lm}(|Y_{lm}-\widehat u_{lm}|^2+v^u_{lm})+d},
\quad c=1+LM,\quad d=LM\widehat\sigma^2_{\rm spatial}.
\]

初始化 σ²₀=0.1 mean|Y|²，沿用原核函数的 1e−12 数值方差下限。
这里沿用既有条件基线的先验强度，空间噪声估计提供 Gamma 先验尺度，参数选择不使用测试真值。
该强度是项目既有设置，不归于原论文；同一观测参与尺度估计和似然，不能视作独立额外观测。
复 MMV 的计数来自复高斯似然，不能机械照搬原文实数写法中的因子 2。
令 E 为上述后验期望残差的和，则更新等价于

\[
(\sigma^2)^{\rm new}=\frac12\left[\frac{E}{LM}+\widehat\sigma^2_{\rm spatial}\right]
\geq\frac12\widehat\sigma^2_{\rm spatial}.
\]

这是 Gamma-MAP 更新直接给出的界，不额外截断迭代结果。它仍依赖空间估计的有效性，
不保证在有色噪声或空间信号接近满秩时准确。
原均值停止规则和 1000 轮预算保留，达到预算仍记录为 `MAX_ITERATIONS`。

Off-grid SBL 由当前同一轮的 A、α、σ² 计算 μ 和完整后验协方差 Σ，使用 Wei 式(46)的迹恒等式：

\[
E=\|Y-A\mu\|_F^2+M\operatorname{tr}(A\Sigma A^H)
 =\|Y-A\mu\|_F^2+M\sigma^2\sum_i(1-\Sigma_{ii}/\alpha_i),
\qquad (\sigma^2)^{\rm new}=\frac{E+d}{LM+c-1}.
\]

当前使用 c=1+LM、d=LMσ̂²_spatial，保留 σ²₀=mean|Y|²/100。
原文 §VI-A 的设置为 c=d=1e−4；该弱先验适配在原六条件中存在约 16%–28% 的向下偏差。
两条件控制实验中，改用空间估计初始化、或运行至 351/493 轮满足停止条件，仍未消除低估。
当前先验是依据该诊断增加的项目适配，单位权重与既有 GAMP 设置一致，未搜索权重或重拟合活动门限。
同一观测同时提供先验尺度和似然，不能视为独立额外观测。
其噪声更新同样为 (E/(LM)+σ̂²_spatial)/2，并具有上述非零下界；这不保证无偏。
原弱先验参数仍是 `offgrid_noise.solve` 的默认参数，历史实现和输出在结果目录中保留。
后验方差项含交叉协方差的作用，
不能用 Σ 的对角近似代替完整迹，也不能只用拟合残差。每轮噪声、行方差和偏移均从当前后验更新。
保留 120 轮预算，提前停止同时检查噪声相对变化、行方差相对变化和最大偏移增量，均小于 1e−4。
后验与字典失配可能被吸收到噪声估计；此时学到的值不一定等于纯热噪声。

## 判决与复现

SOMP、GNN-ASPL 使用空间噪声估计；GAMP、SBL 使用最终学习值，代入既有
10log₁₀ max(mean|Y|²/σ̂²−1, 1e−12) 节点选择。所有门限、网络权重均未重拟合。
新推断身份包含噪声设置和源码；保留原校准文件的身份及来源，明确标记为门限复用。
L-DAMP 使用原固定活动能量门限；等效噪声与物理噪声分开保存。
相位前端的噪声值只用于残差归一化诊断，估计相位本身不依赖它。

```sh
.venv/bin/python -B run.py simulate --noise-mode estimated --seed 202610090100001 --snr 0 --output NEW_CASE
.venv/bin/python -B run.py baseline --method offgrid_sbl --input NEW_CASE/input.npz --output NEW_SBL.npz
```

准确噪声参考需要含噪声方差的输入文件，并显式 `--noise-mode known`。
同时准确已知相位和噪声时还需 `--phase-mode known`。
输出包括 `noise_variance_estimate`、`noise_variance_history`、噪声来源与不使用真值的记录。
L-DAMP 的 `effective_noise_variance_history_normalized` 是归一化迭代等效误差，
不应拿它与物理噪声直接相除。

验证计划、全部输出及警告见 [本轮记录](../docs/history/results/baseline_noise_20261015/REPORT.md)。
原十场景面板继续属于供给准确噪声的历史实验，不作为新默认模式的性能结果。
GAMP 的首版弱先验适配曾在两个场景、三档 SNR 中出现严重低估与 20% AER。
该失败保留在上述原报告；当前默认已恢复既有先验强度并以空间估计设置尺度，
初始化控制、同场景回归及两个新场景的验证见 [GAMP 修正报告](../docs/history/results/gamp_noise_20261015/REPORT.md)。
其余四方法的检查、off-grid SBL 先验修正及固定新场景验证见
[后续核验报告](../docs/history/results/baseline_noise_audit_20261015/REPORT.md)。
SOMP/GNN-ASPL 的噪声估计传递、L-DAMP 的等效噪声单位另有回归检查；未发现同类迭代压低物理噪声的问题。
