# 直接观测更新和 oracle 消息传递

所有信道和观测除以训练归一化尺度 s，噪声复方差除以 s²。给定真实活动集合 S，只保留
A=A_S，Y 的排列及 A 的展开完全沿用主线 MMVLinear；X 的每个用户块为 16×16×16。

## score 的尺度

网络输出为实坐标梯度拼成的复数 S=s_re+i s_im。若模型尺度比 c=s/s_checkpoint，
在网络中查询 cX 和 c²v，返回的 **Wirtinger 导数** 为 g_prior=(c/2)S。
这里 v=E|epsilon|²，每个实坐标方差是 v/2，与当前 Tweedie 均值 X+(cv/2)S 一致。

对于 Sigma 为 Hermitian 正定的复 Gaussian 似然，

    log l(X) = -tr[(Y-AX)ᴴ Sigma⁻¹ (Y-AX)] + constant,
    partial log l / partial X* = Aᴴ Sigma⁻¹(Y-AX).

因此方向导数为 2 Re <g_like, dX>。Huang 印刷式(10)和 Algorithm 1 的正向残差符号与
梯度上升不一致；本实现用上式并以有限差分验证，不推断其实际实验代码存在同样错误。

## 退火与随机更新

本试验固定两种近似似然：

    scalar:   Sigma_v = (sigma²+v) I,
    operator: Sigma_v = sigma² I + v A Aᴴ.

后者来自辅助模型 X0|X_v ~ CN(X_v,vI)，再对 Y=A X0+W 作 Gaussian 积分。
**这不是物理先验下真实 p(Y|X_v)**：在真实先验下 X0-X_v 与 X_v 一般相关且条件均值不为零。
它只是在有限 v 时考虑了 A 对假设输入误差的变换；v→0 时两种式子都回到真实观测似然。
本实验最小 v=0.001，不能据此称为精确后验采样。

每一步为

    X_next = X + eta [g_prior(X,v)+g_like(X,v)] + sqrt(2 beta eta) Z,
    Z ~ CN(0,I),
    eta = 0.05 / (1/v + max_j lambda_j / d_j),

其中 lambda_j 是 A Aᴴ 的特征值，scalar 的 d_j=sigma²+v，operator 的
d_j=sigma²+v lambda_j。所有随机种子和调度见 PLAN.md。
每个实坐标的随机增量方差为 beta*eta。由于漂移是实梯度的一半，理想可积 score、
固定 v、无离散误差且充分混合时，该尺度对应温度 beta；beta=1 对应该近似密度，
beta=0.01 是降低随机扰动的估计设置。有限网络不保证保守向量场，有限步也不保证混合。
不使用真值停止、不做梯度裁剪、不投影物理参数、不强制秩一。

## oracle 消息传递

直接在活动用户子空间运行原线性模块。oracle 去噪器计算原一、二阶网络的 F 和 tau_k；
使用同一 tau=max(mean(tau_k),floor)，在 tau/v<1 时接受与原代码相同的 Gaussian site。
之后 mu=(c_site R+v e_site)/(c_site+v)，条件协方差 tau_used I。
由于活动已知，联合均值就是 mu，协方差就是条件协方差。超出网络支持时保留 Gaussian site。
停止仍检查原来的均值、协方差和 site 残差；活动概率和相应残差恒为 1、0。
原接口中的公开 activity_prior 不参与 oracle 推断，保留它仅为复用四字段数据结构；真实集合
是本实验额外给出的信息。原 classifier 不加载，也不计为网络调用。

## 合成验证的含义

用解析 Gaussian 先验检查固定 v 下的梯度平衡点等于 Gaussian 后验均值，检查离散复 Langevin
的稳态方差为 beta/(precision*(1-eta*precision/2))。这只验证实现的符号、尺度和线性代数，
不保证学习 score 的质量或 AFDM 上的表现。
