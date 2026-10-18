# 保留 score 网络的 Gaussian 因子分解：待验证接口

## Material Passport

2026-10-16；academic-research-suite / experiment-agent，inline validate。
本文件是局部数学接口及其数值控制，不是已采用的接收机修改。
目标仍为实际查询及其他用户反馈误差的验证与修正；原 Proposed 和三份权重保持不变。

## 1. 保留的概率对象

固定一个用户的外部 Gaussian 工作因子，写成

    L(H)=exp(c+2 Re tr(BᴴH)−tr(HᴴJH)), J⪰0, H∈C^(P×C).       (S1)

目标是 q(H)∝pρ(H)L(H)，pρ=(1−ρ)δ0+ρp1。
J、B 来自原线性模块的矩阵因子；给定后视为常量。
这不证明其他用户真实误差独立或 Gaussian，也不把真实轨迹风险替换为局部后验方差。

选 0<v<1/λmax(J)，令 M=I−vJ≻0，以及

    Jv=M⁻¹J, Bv=M⁻¹B,
    cv=c−C log det M−v Re tr(BᴴM⁻¹B).                         (S2)

零 J 时上界视为无穷。以上只求解 M，不要求 J 可逆。

## 2. 卷积恒等式

引入与 H 同形状的变量 Z，定义

    Lv(Z)=exp(cv+2 Re tr(BvᴴZ)−tr(ZᴴJvZ)).
    ∫ CN(Z;H,vI) Lv(Z) dZ = L(H).                            (S3)

证明：Gaussian 积分的精度为 K=I/v+Jv=M⁻¹/v，
自然参数为 H/v+Bv。积分的对数为

    cv−C log det(I+vJv)−||H||²/v
      +tr[(H/v+Bv)ᴴ K⁻¹(H/v+Bv)].                           (S4)

用 K⁻¹=vM、MBv=B、MJv=J 展开，得到 S1。
S2 的常数对于后验归一化、不同分量的证据比较必须保留。

因此联合分布 q(H,Z)∝pρ(H) CN(Z;H,vI) Lv(Z) 的 H 边缘严格为 S1，
而 H|Z 的条件分布恰为原标量 Gaussian 去噪问题。
这里的 Z 是新定义的辅助变量；不能把原实际查询 R 直接改名为 Z。

## 3. 三个原网络在接口中的位置

令 pρ,v 为 pρ 与 CN(0,vI) 的卷积，Fv(Z)=E[H|Z,a=1]，
τv(Z)=tr Cov(H|Z,a=1)/(PC)，πv(Z)=P(a=1|Z)。
一阶 score 给 Fv，二阶 score 的理想读出给 τv，原活动分类器近似 πv。
均衡训练分类器的 log density ratio 加 logit(ρ) 后得到 πv；ρ 不由采样结果重新估计。

采用 Wirtinger 导数，

    ∂ log q(Z)/∂Z* = [πv(Z)Fv(Z)−Z]/v + Bv−JvZ.             (S5)

原网络输出是实坐标 score 的实虚拼接，因此活跃均值仍为 Fv=Z+(v/2)s1。
S5 对应的实坐标梯度是其两倍，不能丢失此因子。
仅有有限样本 Z 时，需要积分/采样误差检查；不能把一个驻点当成后验均值。

若 Z 已按 q(Z) 正确取期望，则

    P(a=1|L)=E_q[πv],  E[H|L]=E_q[πv Fv],                   (S6)
    tr Cov(H|L)=E_q[πv(PC τv+||Fv||²)]−||E_q[πvFv]||².      (S7)

需要条件活跃矩时，令 p=E_q[πv]，
μ1=E_q[πvFv]/p，tr V1=E_q[πv(PCτv+||Fv||²)]/p−||μ1||²。
S7 同时包含每次条件不确定性与不同 Z 之间的均值变化，不能只平均 τv。
输出如接入 Gaussian 消息，仍须按同一原 J、B 做矩匹配；不能除去 Jv、Bv。

## 4. 与整个观测模型的关系及边界

对 Y=AH+N、N~CN(0,Σ)，若 D=Σ−vAAᴴ≻0，则可以定义

    Z|H~CN(H,vI),  Y|Z~CN(AZ,D).                            (S8)

积分 Z 后 Y|H 的协方差仍是 Σ，且 H|Z,Y=H|Z。
S8 给出完整观测因子的同类恒等式；它没有把其他用户误差独立 Gaussian 化。
但直接在整个 Z 上做联合推断会改变外部推断结构，本阶段只验证数学关系，
没有将它作为原 TMP 的已批准替代。局部 S1 保留原外部工作因子，其用户依赖近似仍需解决。
估计相位 A 与真实相位不同的误差，也没有被上述 Gaussian 恒等式消除。

## 5. 有限网络与可行性限制

1. S3、S6、S7 在精确条件分布下成立；现有网络不自动精确。
2. 已发现 first 的 Jacobian 不完全对称，以及 activity 与 first 不完全一致。
   把它们放入 S5 不保证得到任何归一化密度的精确 score。
3. 原 second 对有限 first 的训练最优目标含均值偏差平方，不能将其误差读出直接宣布为中心协方差。
4. q(Z) 仍可能多峰；离散 Langevin 的步长误差、混合、初始化和开销都未验证。
5. 当前只允许数学控制和公开输入的谱/网络支持核对，不启动新训练、采样扫描或完整接收机。
   本接口是否值得实现，需要先评估上述有限网络缺口，不能因恒等式成立就推进闭环。

## 来源

[Cai v2 §IV 式(43)–(54)](https://arxiv.org/html/2506.00581v2#S4)：一、二阶 score 的 Gaussian 去噪读出。
[Kawar–Vaksman–Elad, SNIPS, NeurIPS 2021](https://papers.nips.cc/paper/2021/file/b5c01503041b70d41d80e3dbe31bbd8c-Paper.pdf)，
§3.1 式(6)、§3.2 式(7)–(10)，PDF pp.5–6：合成噪声与观测噪声耦合及小噪声区间的条件 score。
本处只借鉴所有观测奇异方向均满足小噪声条件的表达；S1–S8 的复数矩阵、常数、
活动混合及矩恢复均在本文直接推导，不声称已复现完整 SNIPS 或其性能。

