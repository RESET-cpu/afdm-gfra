# 同一 Gaussian 局部因子的概率与条件矩

2026-10-16。这里是对既有局部模型的必要关系与候选训练目标推导。
不改变主线，不把真实查询误差假定为独立 Gaussian，也不宣称已经完成接收机修正。

## 1. 密度比决定的条件矩

令 x,h∈R^(2D)，复 Gaussian 噪声方差为v，因此每个实坐标方差为v/2。
固定活跃先验P，不活动信道为0。消去两个Gaussian密度的共同归一化因子后，

\[
L(x,v)=\log\frac{q_1(x,v)}{q_0(x,v)}
=\log\int\exp\{(2x^Th-\|h\|^2)/v\}\,P(dh). \tag{P1}
\]

对积分和归一化权重求导，记条件均值μ与实坐标中心协方差C：

\[
\nabla_xL=2\mu/v,\qquad
\nabla_x^2L=4C/v^2,\qquad
J_\mu=2C/v. \tag{P2}
\]

因此，精确μ的Jacobian必须对称且半正定，精确L在x上必须凸。
对任意确定方向e，eᵀHess(L)e≥0；不存在“随机迹估计有方差，所以负方向也可以是精确协方差”的解释。
随机探针估计的迹可以有抽样误差，但每个确定方向对应的精确协方差二次型都非负。
实际数值出现负值时仍须先排除浮点误差和不可微点；本轮用双精度及两步长中心差分独立核验。

每个复坐标平均的中心方差为

\[
\tau=\operatorname{tr}C/D
=\frac{v}{2D}\operatorname{tr}J_\mu
=\frac{v^2}{4D}\operatorname{tr}\nabla_x^2L. \tag{P3}
\]

这些是给定x,v的局部概率恒等式。算法真实生成x的机制不需要是AWGN，
但有限网络能否在那些x上近似这些函数，是需要另行验证的泛化问题。
来源与符号对应：Cai v2 §IV式(43)–(54)，本项目逐式审查M16–M26；
Jacobian半正定的一般结果可核对Gribonval–Nikolova v3 §2.5 Lemma 5及Appendix A.4。

进一步对v求导：

\[
\partial_vL=\frac{E[\|H\|^2\mid x]-2x^T\mu}{v^2},
\quad
\tau=\frac{v^2\partial_vL+2x^T\mu-\|\mu\|^2}{D}. \tag{P4}
\]

P4是对P1的直接求导，可作为跨噪声尺度的一致性检查。
任意神经网络L未必满足P3与P4相等；不能在两式中择优挑选方差或用裁剪掩盖不一致。
本轮批量诊断仍按事先确定的P3进行，P4尚未加入该面板，也未用于接收机。

## 2. 分类正确不保证导数正确

二元交叉熵对logit的导数为sigmoid(L)−a，绝对值不超过1。
给L添加ε sin(ωeᵀx)，每条交叉熵最多改变ε，但梯度扰动可达εω，二阶导数扰动可达εω²。
所以仅有低分类损失或高分类正确率，不能推出P2–P3。
这是一条函数层面的反例，不意味着原网络具有该特定振荡形式。

同理，有限均值网络的均方误差小，不自动保证其Jacobian近似后验协方差。
原second针对有限first的条件风险，还包含均值偏差平方：

\[
E[\|H-F(x,v)\|^2\mid x,a=1]
=\operatorname{tr}C+\|F(x,v)-\mu(x,v)\|^2. \tag{P5}
\]

因此三项差异须分别报告；不能把second、Jacobian迹或分类器曲率中的任一项先当作真值。

## 3. 候选的导数监督目标及其适用边界

保持同一活跃先验，生成H∼P及X=H+CN(0,vI)。令可微分类器的完整输出为Lθ(X,v)，
包括它对确定性特征F(X,v)的链式依赖，定义μθ=(v/2)∇_xLθ。
考虑活跃样本上的监督目标

\[
\mathcal J_{\rm mean}(\theta)
=E\big[\|\mu_\theta(X,v)-H\|^2/D\big]. \tag{P6}
\]

对H|X条件化并展开平方，交叉项为0：

\[
\mathcal J_{\rm mean}(\theta)
=E\big[\|\mu_\theta(X,v)-\mu(X,v)\|^2/D\big]
+E[\operatorname{tr}C/D]. \tag{P7}
\]

第二项与θ无关。因此P6监督的是密度比的真实梯度，而不是把有限first的向量场当成精确老师。
两个类别同用v的抽样分布、训练类别各占1/2时，交叉熵的函数空间最优解为P1。
对任意λ>0，组合

\[
\mathcal J(\theta)=\mathcal J_{\rm BCE}(\theta)+\lambda\mathcal J_{\rm mean}(\theta) \tag{P8}
\]

在不限制函数类的理想情况下有共同最优解L；梯度项单独不能确定仅依赖v的加法常数，
交叉熵负责密度比的值。有限网络容量和有限训练会产生权衡，需要独立验证，不能由P7保证实际收益。

Chao等ICLR 2022 §4.1–4.2式(8)–(11)、Theorem 1讨论分类器的denoising likelihood score matching与交叉熵联合训练。
P6–P8是本项目二类问题利用已知零信道Gaussian密度得到的直接推导，
不是将该文的多类条件生成目标原样移植；尤其不使用原文的学习型无条件score代替已知q0。

P8至多提供一个待验证修正方向：它不强制有限Lθ处处凸，不保证P3与P4一致，
不保证与旧first/second完全一致，更不消除真实多用户反馈的相关性或保证完整迭代收敛。
完整诊断结束后才能固定候选训练协议，并以同输入闭环和独立确认判断是否采用。

## 4. 用固定参考密度改善数值尺度

设参考先验为32个零均值、各向同性的复Gaussian分量，方差为s_j>0、权重为w_j>0，
权重和为1。令q_G为该参考先验与同一Gaussian噪声的卷积；物理先验仍为P。
定义

\[
L_G(x,v)=\log\sum_j w_j\exp\left\{-D\log(1+s_j/v)
+\frac{s_j}{v(v+s_j)}\|x\|^2\right\},\qquad
L_\theta=L_G+u_\theta. \tag{P9}
\]

理想残差为u*=log(q_1/q_G)，因此L_G+u*=log(q_1/q_0)：这是恒等分解，
没有把目标物理先验替换为参考Gaussian混合。有限网络是否能学到这个残差仍是实验问题。
参考分量由全部50000个训练信道的归一化功率排序、等数量分成32组后取组均值；
权重取组内样本比例，保留总体二阶矩。此操作是本项目确定的参考构造，不称为最大似然拟合。

令π_j为P9的归一化分量权重，κ_j=s_j/(s_j+v)，则

\[
\mu_G=x\sum_j\pi_j\kappa_j,\qquad
\tau_G=v\sum_j\pi_j\kappa_j+
\frac{\|x\|^2}{D}\left(\sum_j\pi_j\kappa_j^2-
(\sum_j\pi_j\kappa_j)^2\right),\quad
\mu_\theta=\mu_G+(v/2)\nabla u_\theta. \tag{P10}
\]

这些矩由Gaussian条件分布及全方差公式直接得到。
P9–P10并不保证残差网络凸、归一化或满足跨v的一致性，也不修复用户间反馈相关。
参考本身在四个开发信道的v=0.1、10、100各漏检1例，不能直接用作接收机替代。

低v时，P9各分量的共同项||x||²/v可能达到数百万。
直接对数求和的float32自动微分在32个固定输入中的最大均值相对误差为21.36%。
实现先精确提出该共同项，余项为log w_j−D log(1+s_j/v)−||x||²/(v+s_j)，
再用固定平移量计算指数和；表达式不变，最大误差降至2.01×10⁻⁵，
CPU双精度降至2.40×10⁻¹⁴。原失败及同输入比较完整保留，门槛未放宽。
这里解决的是候选表达式的数值问题，尚无候选训练或完整接收机收益。

## 来源

- [Cai v2](https://arxiv.org/html/2506.00581v2#S4)，§IV式(43)–(54)。
- [Gribonval–Nikolova v3](https://arxiv.org/pdf/1807.04021v3)，§2.5 Lemma 5，PDF p.15；Appendix A.4，p.21。
- [Chao等ICLR 2022](https://arxiv.org/abs/2203.14206)，§4.1–4.2，PDF pp.6–7，式(8)–(11)、Theorem 1。
  下载文件与校验值见 `references/probability_consistency_20261016/SOURCES.json`。
