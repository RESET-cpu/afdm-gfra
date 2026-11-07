# 相位估计的完整推导与搜索流程

2026-11-05，按作者确认，将相位估计的核心方法并入论文 V-B，搜索预算并入 VI-A4。原相位附录逐字保存在 [phase_estimation.tex](phase_estimation.tex)，不再作为独立附录编译；其中旧标签仅用于历史推导溯源。本文算法不变：先估计一次相位，再固定相位运行 GP-MP。

## 来源与模型

高斯边缘似然沿用 Tipping–Faul (2003)，作者稿 §2.1、PDF p.3 式 (7)–(8)；本项目独立复高斯增益、多天线观测列及连续物理位置的适配，见原始推导（仅本地历史资料：`archive/result_legacy_20261023/candidates/c_stmp_phase_init_marginal_20261104/README.md`）。L-BFGS-B 沿用 Zhu et al. (1997), Algorithm 778。术语与适用范围见 [TERMINOLOGY.md](../TERMINOLOGY.md) 的 2026-11-04 相位前端记录。

令 $\mathbf h_k=\mathbf h_k^{\rm p}(d_k,\nu_k)$，模型为
$\mathbf Y_{\rm s}\approx\sum_k\mathbf h_k\mathbf b_k^{\mathsf T}+\mathbf W_{\rm s}$，
$\mathbf b_k\sim\mathcal{CN}(\mathbf0,\gamma_k\mathbf I_M)$，$\gamma_k\geq0$。
积分消去增益后，每个天线列的协方差为

$$\mathbf S=\widehat\sigma^2\mathbf I_{QN}+\sum_k\gamma_k\mathbf h_k\mathbf h_k^{\mathsf H},$$

忽略与参数无关的常数并按天线数归一化，负对数边缘似然为

$$\mathcal L=\log\det\mathbf S+\frac1M\operatorname{tr}(\mathbf Y_{\rm s}^{\mathsf H}\mathbf S^{-1}\mathbf Y_{\rm s}).$$

## 单设备功率与位置更新

固定其他设备，记

$$\mathbf W_k=\left(\widehat\sigma^2\mathbf I_{QN}+\sum_{j\ne k}\gamma_j\mathbf h_j\mathbf h_j^{\mathsf H}\right)^{-1},\quad
s_k=\mathbf h_k^{\mathsf H}\mathbf W_k\mathbf h_k,\quad
t_k=\|\mathbf h_k^{\mathsf H}\mathbf W_k\mathbf Y_{\rm s}\|^2.$$

由矩阵行列式引理和 Sherman–Morrison 公式，设备 $k$ 对目标的增量为

$$\ell_k(\gamma_k)=\log(1+\gamma_k s_k)-\frac{\gamma_k t_k}{M(1+\gamma_k s_k)}.$$

其导数为

$$\ell_k'(\gamma_k)=\frac{s_k}{1+\gamma_k s_k}-\frac{t_k}{M(1+\gamma_k s_k)^2},$$

因而

$$\gamma_k^\star=\max\left\{0,\frac{t_k/(Ms_k)-1}{s_k}\right\}.$$

消去 $\gamma_k$ 后，增大 $t_k/s_k$ 不增大坐标目标；当 $t_k\leq Ms_k$ 时最优功率为零，目标增量为零。实现以 $t_k/s_k$ 排序候选并进行连续位置细化，保留当前参数作为候选，不据目标下降声称 NMSE 或 AER 必然改善。

## 搜索范围与接收机接口

搜索 $d\in[0,N)$、$|\nu|\leq\nu_{\max}$。在当前 $2Nc_1\in\mathbb N_+$ 条件下，将时延加上整数倍 $N$ 所产生的公共标量相位由增益吸收。对每个粗相位 $\beta$，枚举搜索范围内
$\nu_j=(\beta+2\pi j)/(2\pi T_{\rm frame})$，$j\in\mathbb Z$。

当前冻结设置为 128 个相位格点、3 个粗候选、12 个细化起点、每个起点最多 25 次 L-BFGS-B 迭代、2 次坐标扫描；从零功率开始，按初始导频相关得分降序扫描，并保留当前候选。每个局部搜索限制在波形可微区间。配置为 [phase.json](../../../src/configs/final/phase.json)，本轮未修改。

最终只把 $\widehat\beta_k$ 传给后端以构造 $\widehat{\mathbf A}$，随后固定相位。前端的增益、功率及单路径近似不替代 GPJD 的学习信道先验。
