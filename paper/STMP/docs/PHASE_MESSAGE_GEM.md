# 各向同性高斯消息下的一次广义EM参数更新

本文档对应用户已接受并接入主实验的 `message_gem` 实现。开发时使用原五个物理场景、Q16/Q8、估计噪声和冻结十层。层间使用网络实际传出的各向同性高斯消息；固定该消息后做一次E步和一次广义M步。训练信道相关二阶矩只用于初始化。

## 统一的固定消息概率模型

对每个天线列，`x~CN(mu,v I)`；这里 `mu,v` 来自原网络的高斯外信息。观测模型仍是

\[
Y=\sum_k D(\beta_k)e^{i\theta_k}B_k X_k+N,
\qquad N_{ij}\sim\mathcal{CN}(0,\sigma^2).
\tag{1}
\]

所有用户使用同一更新；`theta` 吸收入信道均值，首帧物理相位仍为1。固定消息下的边缘负对数似然是 [上一候选式(2)](../../../result/candidates/phase_conditional_likelihood_20261022/DERIVATION.md) 的 `R0=I,gamma=v` 情形。

在当前 `theta=0,beta=beta0` 下，令 `A=[D(beta_k)B_k]_k`，则

\[
V=\sigma^2I+vAA^H,\quad
\widehat X=\mu+vA^HV^{-1}(Y-A\mu),\quad
\Sigma=vI-v^2A^HV^{-1}A.
\tag{2}
\]

保留跨用户条件协方差。实现通过投影后的矩阵计算所需二阶矩，不构造完整 `(KRN)^2` 矩阵。式(2)是声明的高斯消息模型下的精确条件矩；消息与实际物理信道后验的一致性仍是近似。出处：[GPML §2.1.1式(2.6)–(2.8)，p.9](https://gaussianprocess.org/gpml/chapters/RW2.pdf)。

## 广义M步

固定式(2)，记各帧用户贡献为 `z_qk=B_qk X_k`，形成

\[
G_{q,kl}=\mathbb E[z_{qk}^Hz_{ql}\mid Y],\qquad
b_{q,k}=\mathbb E[z_{qk}\mid Y]^Hy_q,
\]
\[
Q(\beta,\theta)=\sum_q\phi_q^HG_q\phi_q-2\Re\sum_q b_q^H\phi_q,
\quad \phi_{qk}=e^{i(q\beta_k+\theta_k)}.
\tag{3}
\]

期望二次型对应 [Shen §III-C 式(48)–(53)](https://arxiv.org/html/2412.20806v1) 的做法；共同斜率约束和本稿高斯条件矩是项目扩展，不声称完整复现Shen。

固定其余用户，对第k个用户令 `u_q=b_qk−Σ_{l≠k}G_qkl phi_ql`，最小化式(3)等价于

\[
\max_{\beta_k,\theta_k}\Re\left[e^{-i\theta_k}\sum_qe^{-iq\beta_k}u_q\right]
=\max_{\beta_k}\left|\sum_qe^{-iq\beta_k}u_q\right|.
\tag{4}
\]

旋转角为相关和的辐角；模平方为三角多项式，求单位圆驻点并比较当前点，无相位网格、训练样本匹配和显式路径拟合。所有用户最多扫描10轮，至少2轮，其后按固定二次型相对下降1e−7停止。停止的是式(3)的坐标扫描，不是额外执行网络。

式(3)不增加，由 [Dempster等 §3、p.7、式(3.5)及Theorem 1式(3.7)–(3.10)](https://www.maths.usyd.edu.au/u/jchan/GLM/Dempster1977EM.pdf) 的广义EM性质，固定消息下的边缘负对数似然不增加。实现逐步检查这两项，审计另用直接矩阵构造重算目标。

## 初值、十层流程与边界

初值仍从原始观测以训练二阶矩的高斯协方差模型计算，采用[方向导数初始化及连续求解](../../../result/candidates/phase_likelihood_solver_20261022/DERIVATION.md)。第一层之后，以已有网络的高斯消息近似替代初始零均值分布进行条件更新。十层各调用一次，总共9次E/GEM参数更新，不运行外层完整网络。

本候选没有活动概率门限分流、残差协方差另一路提议或相位改变惩罚。但**初始化的先验近似与层间神经消息不同；上述固定消息单调性不能升级为整套神经接收机的统一全局收敛定理**。现有冻结网络本身并未被证明是某个固定目标的精确E步。代码及论文应保留这一界限。

与相关协方差直接求解候选相比，同时改变了消息协方差假设和层间求解方式，结果不能单独归因于其中一个因素。原场景已多次用于开发，任何优势只作为开发证据。

本轮CPU运行，以避免争用另一组正在执行的GPU实验。CPU耗时不与历史GPU耗时作速度结论。冻结权重、原始输入和噪声处理不变；没有把已知相位注入推断。
