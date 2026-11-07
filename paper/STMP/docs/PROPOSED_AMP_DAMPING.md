# 冻结联合去噪器的 AMP 阻尼递推

2026-10-15。软件入口`score_amp_damped`只标识独立实现，不作为新增学术名称。
原Proposed、原无阻尼AMP的定义和文件均保留。本文件接续[原推导](PROPOSED_AMP.md)的归一化、复数矩阵重排与联合去噪定义。

## 1. 本次改变与保持的对象

沿用 \(Y=AX+W\)，\(A\in\mathbb C^{Q\times L}\)，\(X\in\mathbb C^{L\times C}\)，当前 \((Q,L,C)=(16,640,256)\)。
固定一阶score与活动分类器组成的完整映射

\[
D_t(R)=p_\phi(R,v_t,F_\theta(R,v_t))F_\theta(R,v_t).
\tag{D1}
\]

活动先验修正、总体尺度和网络权重不变。本轮不引入新初始化、不训练网络。
对当前查询求导时固定 \(v_t\)，并保留分类器经 \(F_\theta\) 的完整依赖。
按原坐标约定定义

\[
B^t_{ab}=\frac1Q\sum_{i=1}^{L}
\frac{\partial D_t(R^t)_{ib}}{\partial R^t_{ia}}.
\tag{D2}
\]

\(B^t\)是一般复矩阵，其第一下标对应输入特征，第二下标对应输出特征。原实现中的四次中心差分与8个探针保持不变。

## 2. 从均值阻尼展开历史

固定新值权重 \(\beta\in(0,1]\)，令

\[
R^t=X^t+A^HZ^t,\qquad d^t=D_t(R^t),
\quad X^{t+1}=(1-\beta)X^t+\beta d^t.
\tag{D3}
\]

在 \(X^0=0\) 下，直接展开得

\[
X^{t+1}=\sum_{s=0}^{t}w_{t,s}D_s(R^s),\qquad
w_{t,s}=\beta(1-\beta)^{t-s}.
\tag{D4}
\]

历史输出权重之和为 \(1-(1-\beta)^{t+1}\)，剩余权重对应零初值；不额外归一化，否则会改变D3。
把各历史查询视为独立输入坐标，固定历史噪声标签，则

\[
\frac{\partial X^{t+1}_{ib}}{\partial R^s_{ja}}
=w_{t,s}\frac{\partial D_s(R^s)_{ib}}{\partial R^s_{ja}}.
\tag{D5}
\]

这是历史输入的偏导，不是沿实际迭代路径对某一历史状态求总导数。
依照全历史AMP的Onsager结构，各历史残差对应其历史偏导部分迹，因此使用

\[
Z^{t+1}=Y-AX^{t+1}+C^{t+1},\qquad
C^{t+1}=\sum_{s=0}^{t}w_{t,s}Z^sB^s.
\tag{D6}
\]

数学来源：Fan的[作者稿v5](https://arxiv.org/html/2008.11892v5#S5)，§5式(5.3)–(5.8)、(5.12)及Remark 5.1给出全历史非线性及iid Gaussian特例的各历史偏导校正。
复矩阵部分迹采用Kunde等[预印本v1](https://arxiv.org/html/2604.21115v1#S3.SS3)，§III-C式(18)–(21)、Remark 14与Appendix B。
在固定有限轮数下可把历史查询放进额外特征列：当前输出对历史块s的Jacobian就是D5。
该列扩展只用于推导，不在接收机中构造庞大历史矩阵。

Fan原文的实标量坐标、矩阵标度与本项目不同；本文件的 \(1/Q\) 和复矩阵下标从D2沿用，不能逐字符替换该文符号。
这些文献为历史校正与复数部分迹的形式提供依据；有限AFDM算子、经验标签以及有限网络与探针仍为待检验适配。

## 3. 无需保存全部历史的实现

由几何权重，有精确递推

\[
\boxed{C^{t+1}=(1-\beta)C^t+\beta Z^tB^t},\qquad C^0=0.
\tag{D7}
\]

结合 \(Z^t=Y-AX^t+C^t\)，得到

\[
\begin{aligned}
Z^{t+1}
&=Y-A\big[(1-\beta)X^t+\beta d^t\big]
 +(1-\beta)C^t+\beta Z^tB^t\\
&=(1-\beta)Z^t+\beta\big[Y-Ad^t+Z^tB^t\big].
\end{aligned}
\tag{D8}
\]

代码采用D3和D8，并维护D7用于逐轮代数核对。这里括号内必须使用**未阻尼**的 \(d^t\)，不是 \(X^{t+1}\)。
\(B^t\)仍是D1的部分迹：\(\beta\)已经出现在D7/D8中，不再乘进B后重复缩放。
只有保留 \((1-\beta)C^t\)，才与D4的历史依赖一致。

三项退化检查：

1. \(\beta=1\)：D3/D8逐步退化为原无阻尼AMP；不仅固定点相同，有限轮数轨迹也相同。
2. 关闭Onsager：\(C^t=0\)，始终 \(Z^t=Y-AX^t\)，是对应的阻尼去噪迭代。
3. 第一轮：\(R^0=A^HY\)、\(v_0\)、原始 \(d^0,p^0,B^0\) 与无阻尼完全相同；改变的是
   \(X^1=\beta d^0\)、\(C^1=\beta YB^0\)、\(Z^1\)。因此阻尼不会预先修复首轮分类饱和。

## 4. 方差必须包含交叉项

标签仍按实际残差计算

\[
v_t=\|Z^t\|_F^2/(QC).
\tag{D9}
\]

写 \(\widetilde Z^{t+1}=Y-Ad^t+Z^tB^t\)。D8给出的下一轮标签精确满足

\[
v_{t+1}=(1-\beta)^2v_t+\beta^2\widetilde v_{t+1}
+\frac{2\beta(1-\beta)}{QC}
\Re\operatorname{tr}\big[(Z^t)^H\widetilde Z^{t+1}\big].
\tag{D10}
\]

不能把两轮残差视为独立而丢弃交叉项，也不能把两个方差直接作线性插值并称为实际方差。
代码先更新残差数组，再由D9求标签，逐轮额外核对D10；没有标签裁剪。
D9能描述实际残差的能量，不自动保证它等于查询真实MSE，也不保证天线白性。
经验标签对输入的依赖仍未纳入D2，沿用原条件去噪器偏导约定；适应性标签的统计有效性不是本次代数恒等式的结论。

## 5. 固定点与收敛的严格边界

当映射是确定性的——例如采用精确导数，或者事先固定探针及全部规则——令原完整状态更新为 \(T(X,Z)\)，阻尼是

\[
T_\beta=(1-\beta)I+\beta T.
\tag{D11}
\]

对 \(\beta>0\)，固定点方程 \(T_\beta(s)=s\) 与 \(T(s)=s\) 等价。
若确定性映射在固定点处可微，其局部特征值从 \(\lambda\) 变为 \(1-\beta+\beta\lambda\)。
这可以抑制部分振荡方向，但对 \(\Re\lambda\ge1\) 的方向，不存在仅靠任意正小步长即可保证严格收缩的结论。

实际实现每轮重新抽取探针，并用有限差分与float32网络；因此不能直接用D11宣称随机样本路径收敛。
运行记录同时保存 \(\|d^t-X^t\|\) 和 \(\|\widetilde Z^{t+1}-Z^t\|\) 的相对变化，避免仅因步长小而误报收敛。
100轮完成只标记固定预算完成；失败、最后有效状态、完成预算三者分别记录。

DD-VAMP的[原文](https://arxiv.org/pdf/2010.11321v1)§3.1 Algorithm 1和§3.2支持研究阻尼及初始化的必要性，但其标量精度/灵敏度阻尼不是D3–D8。
本次实现保持原AMP框架，通过历史展开导出更新，不把它称为DD-VAMP。

## 6. 输出、代价与验证

主要信道输出为物理尺度下的阻尼状态 \(sX^T\)。另保存原始 \(s d^{T-1}\) 供诊断。
活动输出仍为最后一次基准查询的原始 \(p^{T-1}\)，阈值固定0.5；没有活动概率平滑。
该概率不被解释为阻尼状态对应的精确后验概率。不能依据真值在两个信道输出中择优。

每个成功完成的Onsager轮仍调用33次完整联合映射：一次基准和32次差分扰动；每次包含一阶score与分类器。
关闭Onsager每轮只需一次联合映射。阻尼本身不增加网络调用，历史校正只需维护一个 \(Q\times C\) 数组。
比较同时报告轮数、各网络调用与时间，不把不同方法的一轮视为相同成本。

验证包括：

- 原有9项与新增13项单元测试通过；权重1逐轮还原、完整历史参考、复数交叉项和失败状态均覆盖。
- 四个真实输入的权重1重放，在所有保存数组上与旧无阻尼轨迹完全相同，实际相对误差为0。
- 独立数学复核以复数跨行、跨特征映射和历史列扩展验证校正位置，见[审核](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_amp_damping_20261015/MATH_AUDIT.md)。
- 真实实验已依[冻结协议](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_amp_damping_20261015/PROTOCOL.md)完成16条新运行。beta=0.5/0.2/0.1分别完成2–3/5–7/9–14个有效更新后标签越界；beta=0.2无Onsager完成1–2个。全部未完成100轮预算，每个设置的142个非活跃用户均被误判为活跃，详见[结果报告](../../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_amp_damping_20261015/REPORT.md)。
- [独立数组核验](../../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_amp_damping_20261015/VERIFICATION.json)通过16条预测和55个快照；[公开入口重放](../../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_amp_damping_20261015/CLI_CHECK.json)与实验输出逐数组相同。35个保护文件哈希不变；共享注册表仅有本任务之外的L-DAMP分支改动，范围与影响单独[记录](../../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_amp_damping_20261015/BASELINE_CHANGE_REVIEW.json)。

## 7. 运行入口

```sh
.venv/bin/python scripts/run_proposed_amp_damped.py --input CASE/input.npz --output NEW/damped.npz
.venv/bin/python scripts/run_proposed_amp_damped.py --input CASE/input.npz --output NEW/beta01.npz --damping 0.1
.venv/bin/python scripts/run_proposed_amp_damped.py --input CASE/input.npz --output NEW/no_onsager.npz --without-onsager
```

默认100轮、beta=0.2。结果目录必须为新位置；推断失败仍保存记录并返回退出码2。
原入口 `scripts/run_proposed_amp.py` 和原Proposed主入口保持独立。
