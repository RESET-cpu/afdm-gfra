# 在固定 L-DAMP 递推中替换冻结 score 去噪器

本实现按“基线核验 → 相同查询去噪 → 完整闭环替换”执行。默认 L-DAMP、原 Proposed
和此前 AMP 实现分别保留。`ldamp_score` 仅为代码入口，不作为新的学术算法名称。
本次只检验冻结网络的直接迁移；完整记录见
[实验协议](history/experiments/ldamp_score_swap_20261015/PROTOCOL.md) 和
[结果](../docs/history/results/ldamp_score_swap_20261015/REPORT.md)。

## 1. 固定观测模型与归一化

公开输入为 \(Y_{qmr}=\sum_{kn}P_{qkn}H_{kmrn}+W_{qmr}\)。设
\(L=KN=640\)、\(C=MR=256\)、\(Q=16\)，重排矩阵的行指标为 \((k,n)\)，列指标为 \((m,r)\)。
固定训练总体尺度 \(s=0.2647966452702405\)，并令

\[
g=\sqrt{\|P\|_F^2/L},\qquad A=P/g,\qquad y=Y/(sg),\qquad X=H/s.
\]

于是 \(y=AX+W/(sg)\)。这里 \(P,Y\) 均指重排后的矩阵；输出只乘回 \(s\)，不再乘 \(g\)。
外层再对天线施加原基线固定的酉波束变换，仍与左侧 \(A\) 相容。

## 2. 维持原矩阵 AMP 更新

初始化 \(X^0=0,Z^0=y\)，固定十轮、八探针、原种子 202610146201：

\[
R^t=X^t+A^H Z^t,\quad
\Sigma^t_{ab}=Q^{-1}\sum_q Z^t_{qa}\overline{Z^t_{qb}},
\]
\[
X^{t+1}=D_t(R^t;\Sigma^t),\quad
Z^{t+1}=y-AX^{t+1}+Z^tB^t,
\qquad B^t_{ab}=Q^{-1}\sum_{i=1}^{L}
\frac{\partial D_{t,ib}}{\partial R^t_{ia}}.
\]

\(B\) 的第一指标为输入特征、第二指标为输出特征，所以残差右乘 \(B\)。
这沿用现有适配的递推；一般复数非可分映射的参考为
[Kunde 等 §III-C 式(18)–(21)、Remark 14](https://arxiv.org/html/2604.21115v1#S3.SS3)。
其独立圆对称 Gaussian 测量假设不覆盖本项目确定结构的 AFDM 导频，不能据此保证 AWGN 或收敛。

## 3. 两种去噪接口及受控比较

原 DnCNN 对第 \(m\) 束使用
\(v_m=R^{-1}\sum_{r}\Sigma_{(m,r),(m,r)}\)，按区间选取冻结网络，在原表示变换中去噪。
波束间严格独立，因此原 \(B\) 的跨波束块为零。

当前 score 网络同时处理一个用户的全部天线，训练坐标为原天线 AFDM 信道，且只接受一个复方差：

\[
v=C^{-1}\operatorname{tr}\Sigma.
\]

设 \(R_b=R_aT\) 是波束坐标，\(T\) 为固定酉矩阵。完整替换映射为

\[
D_b(R_b;v,\rho)=D_a(R_bT^H;v,\rho)T.
\]

不能直接把波束或 DnCNN 的时域表示系数输入已有 score 网络。将多个方差压缩成标量也是
明确的接口适配，并非只换权重。为分开影响，同一批保存查询比较：原逐波束 DnCNN、
同一 DnCNN 用共同方差选段、score 条件均值及完整联合均值。全部预测保存后再单独读取真值。

## 4. 完整 score 联合均值和导数

令 \(r=[\Re R_a,\Im R_a]\) 为实数打包。复 AWGN 的每个实分量方差为 \(v/2\)，因此冻结一阶 score 给出

\[
f(r;v)=r+\frac v2 s_\theta(r;v),\qquad
p(r;v,\rho)=\operatorname{sigmoid}\left(\ell_\phi(r,v,f)+\log\frac{\rho}{1-\rho}\right),
\qquad d_a(r)=p(r)f(r).
\]

\(s_\theta\) 以活动为条件；\(\ell_\phi\) 的训练类别先验为 1/2，\(\rho\) 来自公开输入。
score 去噪均值的依据见 [Cai §IV-A–C 式(43)–(54)](https://arxiv.org/html/2506.00581v2#S4)；
此处因采用复方差，实数打包的系数为 \(v/2\)。
各用户使用一个活动概率，乘该用户全部信道元素。二阶 score 不参与此去噪映射。
在固定 \(v,\rho\) 下，实方向 \(u\) 满足

\[
\dot f=u+\frac v2 J_{s_\theta}u,\quad
\dot\ell=(\partial_r\ell)u+(\partial_f\ell)\dot f,\quad
\dot p=p(1-p)\dot\ell,\quad
\dot d_a=p\dot f+f\dot p.
\]

原活动网络训练时对 \(f\) 的 `detach` 防止更新冻结 score；它不意味着推断函数不依赖 \(f(r)\)。
新实现保持同一特征数值，求导时保留上式的全部链路，不修改原训练代码。
`torch.func.jvp` 对完整实映射计算方向导数；前向/反向自动微分内积与独立中心差分分别核验。
术语依据为 [Baydin 等 §3.1–3.2，式(4)](https://www.jmlr.org/papers/volume18/17-468/17-468.pdf)。
网络数值运算为 float32；“精确方向”指按链式法则求导，不声称没有浮点误差。

## 5. 复数校正及有限探针误差

对实方向映射 \(\mathcal L_R(U)\)，Wirtinger 方向为

\[
J_z[U]=\frac{\mathcal L_R(U)-i\mathcal L_R(iU)}2,
\qquad
\widehat B=\frac1{8Q}\sum_{j=1}^{8}U_j^H J_z[U_j].
\]

沿用原逐波束构造的随机相位 DFT 探针及随机数流。组内列正交；组间只有所需的二阶矩条件，
没有声称全部 256 列每次都正交。新 score 跨波束耦合，必须保留完整 \(256\times256\) 矩阵；
原 DnCNN 继续使用已知结构零，不能人为向原基线的零块加入采样噪声。
自动微分消除方向差分步长问题，八探针部分迹仍有 Monte Carlo 误差；逐轮记录 \(ZB\) 的采样标准误差。
记录中的跨波束校正能量也含有限探针噪声，不能直接当作真实 Jacobian 跨波束能量。

固定噪声标签求去噪映射偏导，与
[He 等 §III-A 式(4)–(8)](https://arxiv.org/html/1802.01290v2#S3.SS1) 的接口一致。
当前复数矩阵公式、坐标和活动处理是公开的 AFDM 适配，不能称为该论文原实验原样复现。

## 6. 可复现入口和失败处理

```sh
.venv/bin/python scripts/run_ldamp_score.py --input INPUT.npz --output NEW_RESULT.npz --device mps
```

输入仍只有观测、算子、公开噪声方差和活动先验。网络方差支持区间为 [0.001,100]；越界保留
失败查询与原因，不截断标签。失败结果存为 `last_valid_estimate`，不能当作完成的十轮输出评分。
原能量门限迁移和 p≥0.5 仅作未重新校准的活动诊断。

原基线保留在 `algorithm/ldamp/receiver.py`，原 Proposed 保留在 `algorithm/proposed/receiver.py`。
两次实际网络回归分别核对了查询记录包装和新核心的独立波束模式，均与原基线逐位一致。
