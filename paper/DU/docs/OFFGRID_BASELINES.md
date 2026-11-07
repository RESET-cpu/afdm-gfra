# Off-grid SBL

当前接收机使用主图版配置 [offgrid_baselines.json](../../../src/configs/offgrid_baselines.json)，
估计噪声版本位于 `algorithm/offgrid_noise.py`，沿用 `algorithm/offgrid/sbl.py` 的后验及偏移计算。
活动判决使用 [offgrid_readout_policy.json](../../../src/configs/offgrid_readout_policy.json)，噪声设置见 [baseline_noise.json](../../../src/configs/baseline_noise.json)。

| 参数 | 数值 |
|---|---:|
| 最大迭代次数 | 120 |
| 行方差、噪声相对变化和偏移停止容差 | 0.0001 |
| rho | 0.001 |
| 每用户筛选原子 | 12 |
| 每轮偏移候选 | 48 |
| 坐标更新遍数 | 5 |
| 偏移预热轮数 | 5 |
| Doppler 网格步长参数 | 0.5 |

来源为 Wei 等 *Off-Grid Channel Estimation With Sparse Bayesian Learning for OTFS Systems*，
IEEE TWC 2022，[作者稿](https://arxiv.org/html/2101.05629v1) §III-B 式(17)–(24)、
§IV 式(35)–(57)、Algorithm 1。默认噪声学习按式(45)–(46)，详见 [噪声估计](BASELINE_NOISE.md)。AFDM 原子、共享行方差 MMV、候选筛选及
数值预算是本项目适配，不能称为原始 OTFS 实验的逐项复现。
当前还以观测空间协方差估计设置 Gamma 先验：c=1+QN·M、d=QN·M·σ̂²_spatial，
噪声初值保持 mean|Y|²/100。该先验与原文 §VI-A 的 c=d=1e−4 不同，属于明确的项目适配；
同一观测用于尺度和似然，不是独立额外数据。诊断及新场景验证见[核验报告](../../../archive/paper_layout_20261026/original_paper/docs/history/results/baseline_noise_audit_20261015/REPORT.md)。
术语与原文定位见 [TERMINOLOGY.md](TERMINOLOGY.md)。

主图评价为每 SNR 20 场景，120 个组合全部达到迭代预算，见[原始报告](../../../archive/paper_layout_20261026/original_paper/docs/history/results/offgrid_baselines_20261012/REPORT.md)。
MNOMP 见[独立归档](../../../archive/paper_layout_20261026/original_paper/docs/history/archive/mnomp_20261014/README.md)。
历史参数审查、配对结果及原文核对保留于各结果目录；本次入口整理记录见
[核验记录](../../../archive/paper_layout_20261026/original_paper/docs/history/results/offgrid_selection_20261014/VERIFICATION.json)。

## 公共观测与物理原子

默认接收机只读取 `observation`、原始 `pilot`、`activity_prior`，先估计相位，内部构造 `operator`。
求解器保留全部候选用户；活动先验字段维持接口一致，当前求解器未使用它更新稀疏性参数。
观测按帧和接收采样堆叠为 \(Y\in\mathbb C^{QN\times M}\)，每个原子为
\(a_k(d,f)=\operatorname{stack}_q\{\widetilde H(d,f)p_{qk}\}\)。
这里 \(d\) 用采样点表示，\(f=\nu/\Delta f\)。各天线共享参数位置，复系数逐天线估计。
原图实验提供已知跨帧相位与噪声。当前入口默认两者均未知；准确相位/噪声参考分别显式选择 `--phase-mode known` / `--noise-mode known`。
真实活动数、路径数、路径坐标和阵列方向均不传给接收机。

以下是从当前物理算子直接得到的项目推导。移除能由自由复系数吸收的标量相位：

\[
\widetilde H(d,f)=H(d,f\Delta f)
\exp\{-2\pi\mathrm i[c_1d^2+fN_{\rm CPP}/N]\}.
\]

本系统 \(2Nc_1=7\)，所以 \(\widetilde H(d+N,f)=\widetilde H(d,f)\)。
因此可在 \(0\le d<N\) 搜索折叠时延并估计自由复系数；只对完整物理信道评分，不把折叠坐标解释为绝对传播时延。
输出 `component_coefficients` 对应上述原子的系数，不是生成器的原始路径增益。

令 \(r,s=0,\ldots,N-1\)，\(w=(r-d)\bmod N\)，
\(\rho=\lfloor2c_1w+s/N\rfloor\)，原子变换前的相位为

\[
2\pi\mathrm i\{c_2s^2+c_1[(r-d)^2-d^2]+sw/N-\rho w+fr/N\}.
\]

在 \(w,\rho\) 分支固定的区间内，一阶导数由逐元素乘
\(t_d=2\pi\mathrm i(-2c_1r-s/N+\rho)\)、\(t_f=2\pi\mathrm i r/N\)
得到；二阶导数分别乘 \(t_d^2,t_dt_f,t_f^2\)，再作同一 DAFT。
当前含 floor 的算子在部分 \(d=j/7\) 处发生跳变。
例如 \(d=1/7\)、\(f=0.1\) 两侧距离 \(10^{-7}\) 时，矩阵相对差约 0.21694。
局部导数和更新限制在 \((j/7,(j+1)/7)\)，边界留 \(10^{-10}\) 数值余量。
这属于现有物理实现的性质；本次没有修改场景生成公式。

初始时延使用 112 个区间中心，多普勒使用 \([-41000,41000]\) Hz 内 7 个等距点。
每用户共 784 个初始原子，40 用户共 31360 列；已有整数网格基线为每用户 80 列。
新方法的搜索密度、连续模型和运算预算都有变化，不能把性能差异全部归于某一步参数更新。

## Off-grid SBL：MMV 更新

先用单位范数粗字典的 \(\|a_i^H Y\|_2^2\) 为每个用户保留 12 列，共 480 列。
这是降低复杂度的项目设置，弱路径可能在此步被漏掉。
在线性化中心计算导数，保持中心范数作列归一化，形成
\(A=A_0+D_d\operatorname{diag}(\delta_d)+D_f\operatorname{diag}(\delta_f)\)。
各行采用 \(x_{im}\sim\mathcal{CN}(0,\alpha_i)\)，这里 \(\alpha_i\) 为**方差**；
噪声 \(\sigma^2\) 每轮按后验期望残差学习。令 \(\Lambda=\operatorname{diag}(\alpha)\)：

\[
C=A\Lambda A^H+\sigma^2I,\quad
\mu=\Lambda A^HC^{-1}Y,\quad
\Sigma=\Lambda-\Lambda A^HC^{-1}A\Lambda.
\]

原文式(44)的指数方差超先验推广到 \(M\) 列后，
\(E_i=\sum_m|\mu_{im}|^2+M\Sigma_{ii}\)，更新为

\[
\alpha_i^{\rm new}=\frac{2E_i}{M+\sqrt{M^2+4\rho E_i}},\qquad \rho=10^{-3}.
\]

这是 \(\rho\alpha_i^2+M\alpha_i-E_i=0\) 的正根；避免两接近量相减。
Cholesky/Woodbury 计算在观测维度完成，无需构造完整的后验协方差。

每轮选择方差最大的 48 行更新偏移。对旧后验固定，设选中集合为 \(S\)，
\(T=\mu_S\mu_S^H+M\Sigma_{SS}\)，\(J=[D_{d,S},D_{f,S}]\)，并定义

\[
B=(Y-A\mu)\mu_S^H-M\sigma^2 C^{-1}A_S\Lambda_S,\quad
b=\Re\operatorname{diag}(J^H[B,B]),\quad
Q=\Re\{(J^HJ)\odot[\begin{smallmatrix}T&T\\T&T\end{smallmatrix}]^T\}.
\]

以坐标更新求盒约束下 \(\min_\Delta\Delta^TQ\Delta-2b^T\Delta\)，共 5 遍。
保留后验交叉协方差以及未选中行的作用。该 MMV 二次式是项目对原文式(46)–(57)的直接推广，测试中与完整期望残差独立核对。
前 5 轮更新行方差和噪声；最多 120 轮，行方差与噪声的相对变化、最大偏移增量均小于 \(10^{-4}\) 时提前停止。
中心及导数保持固定，偏移限制在本时延分支和 Doppler 半个采样间隔内。
达到预算记录 `MAX_ITERATIONS`，不当作已经收敛。

最终用估计坐标的精确物理原子重建 \(H\)。记录 `linearization_relative_error`
为精确预测与一阶预测的相对距离，用于识别线性近似影响。
`component_user_ids` 的 480 行对应筛选后的字典分量，不是估计出的 480 条物理路径。

## 活动判决、验证与运行

SBL 采用 \(e_k=\|\widehat H_k\|_F^2\)、\(s_k=e_k/\max_j e_j\)，全零输出令 \(s=0\)。
活动为 \(s_k\ge t\) 且 \(e_k>0\)。这是基于重建物理信道能量的项目判决，
不与已有基线的 Ding 系数能量统计混用。
每个公共估计 SNR 节点各自选择门限：仅在校准数据最小化总活动错误数，
并列时选最小的最优分数间隔中点。空节点使用本方法全部校准数据。

门限在读取测试标签前写入 [`offgrid_readout_policy.json`](../../../src/configs/offgrid_readout_policy.json)，
绑定求解器设置和源码散列。推断时由 \(10\log_{10}\max(\operatorname{mean}|Y|^2/\sigma^2-1,10^{-12})\)
选择最近节点，当前默认以最终噪声估计代入，不读取真实 SNR。门限沿用原校准，新推断身份另行记录；这不是新噪声条件下的重新校准。完整种子、输入散列、冻结配置及逐例结果在实验目录中。

```sh
.venv/bin/python -B run.py run --method offgrid_sbl --input INPUT.npz --output NEW_SBL.npz
.venv/bin/python -B run.py evaluate --estimate NEW_SBL.npz --truth TRUTH.npz
.venv/bin/python -B -m pytest tests/test_offgrid_baselines.py tests/test_consolidation.py -q
```

当前 `run.py evaluate` 的 `nmse_db` 对全部用户的物理信道误差能量汇总后转 dB，包含非活跃用户的估计能量；`active_nmse_db` 单列活跃用户误差。比较时须使用同一口径。

独立测试覆盖物理矩阵和解析导数、SBL 后验与偏移二次式、
偏移估计收益、文件输入/输出与门限身份绑定。
这批验证不足以替代完整 Monte Carlo、不同负载和模型失配实验。
