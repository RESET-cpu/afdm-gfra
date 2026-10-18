# 保留AWGN网络的联合观测因子

## Material Passport

2026-10-16；从已验证S8继续实现候选，不替换冻结主线。
目标是处理原目标中的用户反馈依赖。局部矩阵因子仍以独立Gaussian工作消息描述其他用户，
其内部采样改善不能消除这个外部近似。当前局部有限分类器目标的固定采样比较均已结束。

## 联合概率对象

归一化后的观测Y=AH+N，N的各列为CN(0,sigma²I_Q)。
H将40个用户的16×256矩阵按行堆叠，为640×256；A为16×640。
使用相同独立用户先验p_rho(H)=∏_k[(1-rho)delta_0(H_k)+rho p1(H_k)]。
取0<v<sigma²/lambda_max(AA^H)，令D=sigma²I-vAA^H≻0，定义

    Z|H ~ CN(H,vI),       Y|Z ~ CN(AZ,D).                (J1)

积分Z后，Y|H严格恢复CN(AH,sigma²I)。H|Z,Y=H|Z，
按用户分别调用原AWGN网络仍是正确的理想条件对象。
这里的Z是联合辅助变量，不是把原反馈查询直接认定为AWGN。

    q(Z|Y) ∝ [∏_k p_rho,v(Z_k)] CN(Y;AZ,D).            (J2)
    g(Z)=(m(Z)-Z)/v+A^H D^-1(Y-AZ),                    (J3)

其中m_k=pi_k F_k，F与pi来自相同标量AWGN条件，沿用S5的Wirtinger约定。
式J3中的所有用户共享同一个观测残差；没有独立Gaussian化其他用户的后验误差。
此处独立的是原模型的用户先验与物理热噪声，不是迭代反馈误差。

## 低维矩阵运算

设c=v/sigma²，M=I-cA^HA，P=vM。由Woodbury恒等式

    P=(I/v+A^H D^-1 A)^-1,
    P g(Z)=-Z+M m(Z)+v A^H Y/sigma².                   (J4)

令AA^H=U diag(lambda)U^H，W=U diag[1/(1+sqrt(1-c lambda))]U^H，则

    sqrt(P)E=sqrt(v)[E-c A^H W A E].                    (J5)

只需16×16矩阵分解及A/A^H作用，不构建640×640矩阵来做每步运算。
E的元素独立CN(0,1)。原线性Gaussian修正应用为

    Z'=exp(-h)Z+(1-exp(-h))[M m(Z)+v A^H Y/sigma²]
       +sqrt(1-exp(-2h)) sqrt(P)E.                     (J6)

J6对m=0或常量的Gaussian部分精确；有限网络及非线性目标仍近似。
当前不是声称已得到精确后验样本。有限classifier与first不一致的问题保留。
J2也可用有限classifier密度定义替代目标，但本阶段不因局部密度的数学可计算性，
就将其视作物理真实目标或自动采用已出现停滞的完整梯度路线。

## 矩恢复与相关性

每个用户仍用S6–S7：P(a_k=1|Y)=E[pi_k]，E[H_k|Y]=E[pi_k F_k]，
tr Cov(H_k|Y)/4096=E[pi_k(tau_k+||F_k||²/4096)]-||E[pi_kF_k]||²/4096。
不同用户的后验互协方差来自联合Z下m_k与m_j的共同变化；没有将它设为零。
不再构造或相除逐用户的独立外部反馈Gaussian因子。

## 当前边界

准备同两个开发场景scene003/007、-4 dB。只读取公开观测、导频、噪声尺度、活动先验，
以及冻结原Proposed输出的估计信道和估计相位作为初始化；不读取真值。
相位在本固定条件对照内保持原估计值，后续完整接收机须报告初始化计算成本并核对相位更新。
采用v=sigma²/(2 lambda_max(AA^H))，不是根据真值调优。

原三网络作为学习先验的作用继续保留。网络误差、有限步长、混合和计算成本需要实测，
不能以本数学分解替代完整配对接收机及独立确认验证。
来源沿用S1–S8与Cai §IV式(43)–(54)；J1–J6为项目直接矩阵推导。
