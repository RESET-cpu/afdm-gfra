# 局部积分均值的Monte Carlo误差与条件后验方差

本诊断预先覆盖合并proposal的全部8查询、两次新抽样。保持原稳定性门槛；
下列误差估计不用于把失败改判为通过，也不作为遗漏区域的误差上界。

令f(g)=p(g)exp L_g，W_i=f(g_i)/q(g_i)，g_i独立抽自固定q。
μ_i是解析积分路径增益后的条件均值，C_i是同一条件分布的协方差。
归一化权重a_i=W_i/ΣW，估计μ̂=Σa_i μ_i、
T̂=Σa_i[tr(C_i)+||μ_i−μ̂||²]。T̂是信道后验协方差的迹，
不等于用有限几何样本计算μ̂的Monte Carlo均方误差。

对比值(A,B)=(N^-1ΣW_i μ_i,N^-1ΣW_i)作一阶delta method，
d(A/B)=(dA−μ dB)/Z。使用样本协方差分母N−1，得到实/虚部逐坐标相加：

    estimated tr Var_MC(μ̂) = N/(N−1) Σ a_i² ||μ_i−μ̂||².

对log Ẑ应用同样展开：

    estimated Var_MC(log Ẑ) = (N Σa_i²−1)/(N−1).

对T=E[tr C_g+||μ_g||²]−||μ||²，中心化影响量为
W/Z [tr C_g+||μ_g−μ||²−T]，故

    estimated Var_MC(T̂) = N/(N−1) Σ a_i² [tr C_i+||μ_i−μ̂||²−T̂]².

两次独立新抽样的均值差平方期望在忽略有限样本偏差时近似为两组方差迹之和。
只报告实际差/估计RMS差，不将其称作正态z检验或置信度；4096维方向不必独立或各向同性。
以上是向量比值估计的直接推导；delta method来源为Elvira–Martino–Robert，
Rethinking the Effective Sample Size v2，§3.1式(10)、Appendix A式(46)，PDF pp.5、23–24：
https://arxiv.org/pdf/1809.04129v2。
该文对ESS忽略被积函数、有限偏差和覆盖的限制仍适用。这里不假设实际接收机查询是AWGN，
也不把上述Monte Carlo误差与其他用户的反馈误差混为一谈。
