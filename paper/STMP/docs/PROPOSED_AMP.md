# 使用冻结 score 与活动分类器的复数矩阵 AMP

2026-10-15。独立研究候选；软件入口名为 `score_amp`。该名字只标识实现，
不声称提出了一个已有文献命名之外的新算法。原 Proposed 保持为默认接收机。

本次实现与代数核验已完成；四个既有开发条件下，新循环均出现方差升出网络训练范围。
完整基校正的补充核验也未解决首场景的不稳定，详见
[实际结果](../../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_amp_20261015/REPORT.md)。以下推导明确区分恒等式与条件近似。

## 1. 推导的对象与成立范围

目标是把当前一阶 score 与活动分类器组成的联合去噪器放入 AMP 外循环，
明确区分四层事实：物理观测及重排恒等式、AWGN 工作模型下的 Bayes 恒等式、
适用随机矩阵条件下的 AMP 近似、有限结构化 AFDM 上的实际表现。
前两层不能证明后两层。完整推导、实现和配对结果分别可核查。

主要来源：

1. He 等，2018，*Deep Learning-based Channel Estimation for Beamspace mmWave
   Massive MIMO Systems*，§III-A 式(4)–(8)：D-AMP 残差、去噪与 Monte Carlo
   散度；[作者稿 v2](https://arxiv.org/html/1802.01290v2#S3.SS1)。
2. Liu–Yu，*Massive Connectivity with Massive MIMO—Part I*，§III-B 式(14)–(17)：
   多测量向量 AMP 及矩阵状态；[作者稿 v2](https://arxiv.org/html/1706.06438v2#S3.SS2)。
3. Kunde 等，2026 预印本，*Complex Approximate Message Passing with Non-separable
   Denoising*，§III-C 式(18)–(21)、Appendix B：复数非可分矩阵去噪、Wirtinger
   Jacobian；[作者稿 v1](https://arxiv.org/html/2604.21115v1#S3.SS3)。
4. Cai 等，§IV 的 Gaussian score 条件矩学习，以及本项目
   [THEORY.md T6a–T11、T15](THEORY.md)：既有网络的实际目标与坐标定义。
   [作者稿 v2](https://arxiv.org/html/2506.00581v2#S4)。

Kunde 文献的随机矩阵与正则条件没有在当前有限 AFDM 系统中得到验证。
以下 cavity 展开说明公式来源，不把对依赖变量的形式展开冒充状态演化证明。

## 2. 从实际观测到矩阵模型：精确重排

公开观测为

\[
Y^{\rm pub}_{qmr}=\sum_{k=1}^K\sum_{n=1}^{P}
A^{\rm pub}_{qkn}X^{\rm phys}_{kmrn}+W^{\rm pub}_{qmr},
\quad X^{\rm phys}_k=a_kH_k. \tag{A1}
\]

用 \(i=(k,n)\) 表示被感知坐标，\(b=(m,r)\) 表示特征坐标。
记 \(L=KP\)、\(C=MN_{\rm out}\)，则 \(A_0\in\mathbb C^{Q\times L}\)、
\(X_0\in\mathbb C^{L\times C}\)、\(Y_0\in\mathbb C^{Q\times C}\)，
且 \(Y_0=A_0X_0+W_0\)。当前为 \(Q=16,L=640,C=256\)。
完整向量化算子为 \(I_C\otimes A_0\)，故不能把各特征误认为使用独立测量矩阵。

令固定训练总体尺度 \(s=0.2647966452702405\)，并定义

\[
g^2=\|A_0\|_F^2/L,\quad A=A_0/g,\quad
X=X_0/s,\quad Y=Y_0/(sg),\quad W=W_0/(sg).
\tag{A2}
\]

于是 \(Y=AX+W\)，平均列能量为1，\(\sigma_w^2=\sigma_{\rm pub}^2/(s^2g^2)\)。
这是共同尺度变换，不改变各列相对功率，也不做逐用户信道真值归一化。
当前恒模导频各列能量相同；通用输入仅保证平均列能量为1，实际范围写入运行记录。

## 3. 联合先验与理想去噪器

沿用原 Proposed 的工作先验：用户活动边缘概率为公开 \(\rho\)，活跃完整信道
服从训练边缘分布 \(P_H\)。它与实际给定算子、噪声功率后的物理条件先验并非已证明相同。
各用户独立以及标量 AWGN 查询均为明示工作近似。

对一个用户的 \(D=M N_{\rm out}P=4096\) 个复坐标，假设

\[
R=X+E,\quad E\sim\mathcal{CN}(0,vI_D),\quad E\perp X.
\tag{A3}
\]

定义 \(q_0(R;v)=\mathcal{CN}(R;0,vI_D)\)、
\(q_1(R;v)=\int\mathcal{CN}(R;H,vI_D)\,dP_H(H)\)。Bayes 公式给出

\[
p^*(R,v)=\frac{\rho q_1}{(1-\rho)q_0+\rho q_1},\quad
F^*(R,v)=E[H\mid R,a=1],\quad D^*(R,v)=p^*F^*.
\tag{A4}
\]

该等式包括不活跃用户的零信道，不先作硬活动截断。
实坐标噪声方差是 \(v/2\)。由 Gaussian 核求导，
\(\nabla_u\log q_1=(E[H_{\mathbb R}\mid u]-u)/(v/2)\)，故

\[
F_\theta(R,v)=R+\frac v2\{S_{1,\Re}(R,v)+iS_{1,\Im}(R,v)\}.
\tag{A5}
\]

分类器以平衡活动比例训练，最优 logit 是 \(\log(q_1/q_0)\)。实际采用

\[
p_\phi=\operatorname{sigmoid}\{z_\phi(R,v,F_\theta)+\operatorname{logit}\rho\},
\qquad D_{\theta,\phi}=p_\phi F_\theta. \tag{A6}
\]

\(\rho\) 只加入一次。有限网络近似与实际输入失配保留，不能把 A6 称为精确物理后验均值。
原二阶网络估计的有限均值条件 MSE 不等于实际 Jacobian，因此新循环不调用它。
两个使用中的 checkpoint 与原 prior、教师身份绑定，旧二阶权重保留。

## 4. 查询与 residual 初始化

\[
X^0=0,\quad Z^0=Y,\qquad R^t=X^t+A^H Z^t,
\quad X^{t+1}=D_t(R^t;v_t). \tag{A7}
\]

在 \(E|A_{qi}|^2=1/Q\) 的随机矩阵标度下，匹配滤波的平均自身响应为1。
它不同于原 Proposed 的 LMMSE 与外信息查询；本实现没有保留旧 site 或外信息相除。
第一轮 Onsager 尚未发生，开启与关闭校正的第一轮查询及输出必须相同。

## 5. 从 cavity 展开到矩阵 Onsager

以下先在理想 iid proper-complex 随机测量模型解释近似。移去观测行 \(q\) 后，
查询的一阶变化为 \(\Delta R_{ja}\simeq\overline{A_{qj}}Z^t_{qa}\)。
对于完整非可分去噪映射，定义

\[
J_{ib,ja}=\frac{\partial D_{ib}}{\partial R_{ja}},\qquad
K_{ib,ja}=\frac{\partial D_{ib}}{\partial\overline R_{ja}},\qquad
\frac{\partial}{\partial z}=\frac12(\partial_{\Re z}-i\partial_{\Im z}).
\tag{A8}
\]

实方向 Taylor 展开为 \(\Delta D=J\Delta R+K\overline{\Delta R}\)。
因此反馈到观测行的自身响应完整包含

\[
\sum_{i,j,a}A_{qi}\overline{A_{qj}}J_{ib,ja}Z^t_{qa}
+\sum_{i,j,a}A_{qi}A_{qj}K_{ib,ja}\overline{Z^t_{qa}}.
\tag{A9}
\]

用户内不同输入坐标可以耦合，故不能预先删除 \(i\ne j\) 项。
在合适的 cavity 独立性、正则性及大系统集中条件下，利用
\(E[A_{qi}\overline{A_{qj}}]=\delta_{ij}/Q\)、\(E[A_{qi}A_{qj}]=0\)，
得到部分迹校正

\[
B^t_{ab}=\frac1Q\sum_{i=1}^{L}J^t_{ib,ia},\qquad
Z^{t+1}=Y-AX^{t+1}+Z^tB^t. \tag{A10}
\]

正号来自在普通残差中补回去噪器包含的该观测自身贡献。
\(B\) 的第一下标是输入特征，第二下标是输出特征；它一般不是 Hermitian 矩阵。
例如 \(D(R)=RT+\overline R U\)，应有 \(B=(L/Q)T\)，共轭项 \(U\) 不进入 A10。
在实际 AFDM 固定矩阵下 A9 不等于 A10，尤其不能因为导频元素模相等就删去其余项。
本研究实现标准复矩阵 AMP 形式，有限 AFDM 中使用 A10 是待检验的适配。

若 \(C=1\)，A10 化为复标量 AMP；若所有特征使用相同独立映射且平均导数相同，
\(B=bI\) 才进一步退化成一个标量系数。当前完整信道网络与活动概率跨特征耦合，
没有该条件，故保留完整 \(256\times256\) 矩阵。

对每用户 A6，实方向导数为

\[
dD_k=p_k\,dF_k+F_k\,dp_k,
\quad dp_k=p_k(1-p_k)\{\partial_Rz_k[dR]+\partial_Fz_k[dF_k]\}.
\tag{A11}
\]

只计算一阶 score 的导数或将活动概率固定，会遗漏项。
原分类器训练中的 `mean.detach()` 仅用于冻结教师的训练梯度；有限差分重新计算整个
数值函数，仍正确包含其输入特征随 \(R\) 的变化。

## 6. 有效噪声统计与旧网络接口

使用未中心化 residual 二阶矩

\[
\widehat\Sigma^t_{ab}=Q^{-1}\sum_qZ^t_{qa}\overline{Z^t_{qb}},\qquad
v_t=\operatorname{tr}\widehat\Sigma^t/C=\|Z^t\|_F^2/(QC).
\tag{A12}
\]

这里含热噪声与剩余估计误差，不减去热噪声再当成总噪声，也不额外重复加热噪声。
MMV 状态演化在适用条件下传播整个特征协方差；形式上有
\(\Sigma_{t+1}=\sigma_w^2I_C+\lim Q^{-1}E[(E_t)^{\mathsf T}\overline{E_t}]\)，
其中 \(E_t=D_t(X+G_t)-X\)、\(G_t\) 是对应 Gaussian 输入，且满足文献的极限与正则条件。
这不要求矩阵状态一定是 \(vI\)，也不是当前数据上可直接使用真值的更新。

旧网络只接收标量 \(v_t\)，将 A12 压为平均方差是本候选的主要失配来源之一。
没有补噪、白化或新训练。逐轮记录 residual 协方差及伪协方差指标，
但 \(Q=16,C=256\) 时样本矩阵秩至多16，即使纯 AWGN 也有很大的样本非对角能量；
必须与同尺寸有限样本 AWGN 对照比较，不能直接解释为总体有色。

每轮求 \(J\) 时固定该轮 \(v_t\)，得到条件映射 \(D_t(\cdot;v_t)\) 的偏导，
不对历史、残差方差估计继续求总导数。将经验自适应噪声标签用于 AMP 的统计有效性
需要额外条件，本次并未证明。该实现约定与 He 的条件去噪器散度计算一致。

## 7. 可计算的矩阵部分迹

取复探针 \(U\in\mathbb C^{L\times C}\)，满足
\(E[\overline U_{ia}U_{jb}]=\delta_{ij}\delta_{ab}\)，在固定 \(v\) 下计算

\[
V_\epsilon(U)=\frac{D(R+\epsilon U)-D(R-\epsilon U)
-i[D(R+i\epsilon U)-D(R-i\epsilon U)]}{4\epsilon}.
\tag{A13}
\]

若 \(L_R(U)=JU+K\overline U\) 是实方向导数，则
\(\{L_R(U)-iL_R(iU)\}/2=JU\)。这是精确方向导数的恒等式；A13 在有限步长下
仅近似实现它，在足够光滑条件下仍有 \(O(\epsilon^2)\) 截断误差。于是

\[
\widehat B=\frac1{QP_{\rm MC}}\sum_{p=1}^{P_{\rm MC}}U_p^H V_\epsilon(U_p),
\qquad E\widehat B\longrightarrow B\quad(\epsilon\to0).
\tag{A14}
\]

证明只需展开 \((U^HJU)_{ab}=\sum_{i,j,c}\overline U_{ia}J_{ib,jc}U_{jc}\)，
取期望后保留 \(j=i,c=a\)。一般非可分映射仍然适用，有限探针有抽样误差。
程序对 \(C\le L\) 使用独立随机行相位、列相位、排列和 DFT 列构造探针，
同时满足上述二阶矩及 \(U^HU=LI\)。这让常系数特征线性映射的部分迹可精确核验，
不意味着神经网络的有限探针估计精确。\(C>L\) 时采用独立单位圆相位。

默认 \(P_{\rm MC}=8\)、\(\epsilon=0.01\sqrt v\)。每轮一次基准加32次扰动，
共33次完整一阶 score 与分类器映射；二阶网络调用为零。
有限差分步长误差、float32误差、有限探针误差均保留；不将 \(B\) 对称化、
取实部、截为正数或只保留对角线。记录 \(Z\widehat B\) 的探针间波动与标准误描述；
该标准误不包含有限差分偏差。

## 8. 完整迭代和输出

1. 检查四字段输入、权重身份，作 A2，置 \(X^0=0,Z^0=Y\)。
2. 按 A7 得查询，按 A12 得总误差方差标签。
3. 若标签在冻结网络支持 \([10^{-3},100]\) 外，记录失败及最后有效输出；不裁剪标签。
4. 按 A5–A6 计算联合均值与活动概率。
5. 固定本轮标签，按 A13–A14 求完整矩阵校正，并执行 A10。
6. 重复至预设10轮；返回物理单位 \(sX^{10}\) 与最后基准查询的 \(p_k\)。
   活动判决固定为 \(p_k\ge0.5\)，不将判为不活跃的估计再次置零。

十轮完成标为 `FIXED_ITERATION_BUDGET`，不称收敛。发生超支持或非有限数时标为
`FAILED`；最后有效估计保存供诊断，不能当作完成十轮的结果。
关闭 Onsager 的对照只把 A10 的 \(ZB\) 置零，其余初始化、网络、标签和轮数保持相同。
两者每轮成本不同，比较时同时报告轮数、网络调用与实际时间。

## 9. 与原 Proposed 的关系

原 Proposed 的 LMMSE、二阶网络、Gaussian site、两端外信息和0.2阻尼仍在原位置运行。
本候选只共享冻结一阶/分类器权重及其只读定义，没有改写原注册表、默认配置和历史结果。
`docs/history/results/proposed_amp_20261015/PRESERVED_MAINLINE.json` 绑定28个原文件；
源码/配置备份在该目录 `original/`，模型权重继续保留在 `models/proposed/`。

本候选的实现身份、所有已完成/失败条件及数值核验见
[实验协议](../../../archive/paper_layout_20261026/original_paper/docs/history/experiments/proposed_amp_20261015/PROTOCOL.md)和
[结果报告](../../../archive/paper_layout_20261026/original_paper/docs/history/results/proposed_amp_20261015/REPORT.md)。

## 10. 运行

```sh
.venv/bin/python scripts/run_proposed_amp.py --input CASE/input.npz --output NEW/amp.npz
.venv/bin/python scripts/run_proposed_amp.py --input CASE/input.npz --output NEW/no_onsager.npz --without-onsager
.venv/bin/python run.py run --method proposed --input CASE/input.npz --output NEW/original.npz --device mps
.venv/bin/python run.py evaluate --estimate NEW/amp.npz --truth CASE/truth.npz
```

前两条独立入口不修改主线选择。失败运行仍写出记录，但退出码为2；评分必须结合记录状态。
未使用仿真真值选择噪声、探针、活动阈值或最终轮数。
