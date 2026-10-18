# 原 score 提议的 Metropolis–Hastings 接受校正：固定单步核对

## Material Passport

2026-10-16；保留原 AWGN 训练的 first、second、activity；候选数学接口。
四倍时长诊断已完成，不能通过继续延长原实验来宣布收敛。
本核对回答：原 first 驱动的 Gaussian 提议，能否用原 activity 的密度比作接受校正。
不启动接收机，不重训，不使用真值，不将有限分类器视为真实物理密度。

## 明确定义目标

令 ell_phi(Z,v) 为均衡训练活动分类器的 logit，q0(Z)=CN(Z;0,vI)。
若 ell 是精确 log(q1/q0)，则原辅助变量目标可写为

    q(Z) ∝ q0(Z) Lv(Z) [(1-rho)+rho exp(ell(Z,v))].       (A1)

对实际有限分类器，用同一右端定义待检验的近似密度 q_phi，而不是宣称 q_phi=q。
令 P=(I/v+Jv)^-1、m0=P Bv，其非归一化 log 密度可计算为

    U_phi(Z)=-tr[(Z-m0)^H P^-1(Z-m0)]
             +logaddexp(log(1-rho),log(rho)+ell_phi).     (A2)

有限分类器的 q0 exp(ell_phi) 未验证单位积分，因此活动先验的校准仍有误差；
其梯度也未验证与 first 一致。保留这些限制，不通过接受校正将它们抹去。

仍用原 first 和 activity 形成 E2 的提议均值

    mu(Z)=Z+(1-exp(-h)) P[(pi_phi F_theta-Z)/v+Bv-Jv Z],
    Q(Z'|Z)=CN(Z';mu(Z),(1-exp(-2h))P).                 (A3)

接受概率为 min(1,exp(U_phi(Z')-U_phi(Z)+log Q(Z|Z')-log Q(Z'|Z)))。
该公式不要求提议方向是保守场；first 仍控制提议，且信道矩仍用 first/second 读出。
但对有限网络，读出不是 q_phi 对应精确条件矩的证明。
接受校正只处理对明确近似密度的转移偏差，不解决物理密度误差或混合问题。
来源：[Hastings 1970](https://probability.ca/hastings/hastings.pdf)，§2.2 pp.99–101，
式(4)–(8)与连续密度段。复矩阵目标和 Gaussian 提议为项目显式推导。

## 固定核对

取已保存长时诊断的全部64个末态（8因子×8链），每个状态4个独立噪声方向，
固定h=0.05、0.005、0.0005；相同步长比较复用相同基础噪声。
总计768个单步提议；不续接链、不按结果增加步数或更换输入。
固定种子202610164301。输出接受概率、log比值、预期接受后平方移动量；
仅是这些已访问状态的一步行为，不视为稳态接受率。

先核对d=1/3/7的复Gaussian代数、正反向详细平衡和零活动OU转移，门槛1e-9。
网络MPS单精度，Gaussian运算双精度。随后对每因子、每重复的chain0、噪声方向0，
三个步长共48对固定输入，完整CPU双精度复算，log接受比最大绝对差门槛0.02
（接受概率比变化至多exp(0.02)，约2%）。不把归一化数组误差用于掩盖log比值误差。
最高600秒，所有输入、权重和实现记录哈希；失败保留且不自动重复。
