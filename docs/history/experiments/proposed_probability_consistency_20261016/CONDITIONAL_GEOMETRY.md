# 固定几何下保留原路径增益分布的积分

2026-10-16；本项目直接推导的局部诊断。尚未实现未知几何的积分，也未替换接收机。
Material Passport：academic-research-suite / experiment-agent，沿用用户授权的公式验证范围。

冻结生成器 `system/scenario/continuous.py` 的 standard 分支使用一个固定幅度、均匀随机相位的直达径，
以及三个独立复 Gaussian 散射径。固定几何 g（包含位置、方向、时延、多普勒和时延扩展），
将路径期望功率吸收入列向量，可写成

    H = u_g t + B_g z,   t=exp(iφ), φ~Uniform[0,2π), z~CN(0,I_3).                 (G1)

此处 H 已除以主线的固定全局尺度；没有逐样本功率归一化。
第一和第二径具有相同延迟，但 B 的列不必正交或线性无关。
由生成器的定义，G1 在给定 g 下成立；若直接令四个增益都服从 Gaussian，则会更改该条件先验。

令局部因子为 CN(x;H,vI)，定义 C=vI+BB^H、K=BB^H C^(-1)、d=(I-K)u、a=u^H C^(-1)x。
先积分 z，得到 CN(x;ut,C)；展开平方，再对 φ 积分：

    q_g(x;v)= exp(-x^H C^-1 x-u^H C^-1 u) I_0(2|a|) / (π^D det C).             (G2)
    I_n(κ)=(1/(2π))∫_0^(2π) exp(κ cos φ) cos(nφ) dφ.                          (G3)

G3 见 NIST DLMF §10.32 式(10.32.1)、(10.32.3)。
与 q_0=CN(x;0,vI) 相比，

    L_g = x^H(v^-1 I-C^-1)x - log det(I+BB^H/v)
          - u^H C^-1 u + log I_0(2|a|).                                    (G4)

归一化相位积分给出 m_n=E[t^n|x,g]=I_n(2|a|)/I_0(2|a|) · exp(in arg a)，n=1,2。
a=0 时 m_1=m_2=0。对 z 使用 Gaussian 条件分布，再对相位取全期望和全协方差：

    μ_g = Kx+d m_1,                                                        (G5)
    V_g = B(I+B^H B/v)^-1 B^H + dd^H(1-|m_1|²),                            (G6)
    P_g = dd^T(m_2-m_1²).                                                 (G7)

V_g=E[(H-μ)(H-μ)^H|x,g]；P_g=E[(H-μ)(H-μ)^T|x,g]，这里明确写出定义，
避免误把复协方差 V_g 独自当作全部实坐标二阶矩。即使原噪声圆对称，给定 x 后相位项也未必如此。
对复方向 e，真实二阶方向矩为

    Var(Re(e^H H)|x,g)=1/2·e^H V_g e + 1/2·Re(e^H P_g conj(e)).              (G8)

实方向对应 (Re e,Im e)。于是 ∂_e L_g=2Re(e^H μ_g)/v，
∂²_e L_g=4 Var(Re(e^H H)|x,g)/v²，与同一 Gaussian 局部因子的概率恒等式一致。
实现只逆 3×3 的 I+B^H B/v，不生成 4096×4096 协方差；Bessel 使用缩放值防止指数溢出。

未知几何仍需 q_1(x;v)=∫q_g(x;v)P(dg)，再以 q_g P(dg)/q_1 加权 G5–G7。
用有限几何样本替代该积分是新的数值近似，必须检查覆盖和积分误差，不能因 G2–G8 精确就声称解决。
把真实测试几何代入仅能作 oracle 数学控制，不能作为可部署接收输入。
此推导也没有解决原多用户实际查询的相关误差、共享场景几何依赖或相位估计误差。

验证预先固定：种子202610161600；小维随机、重复列、零直达径及零查询，v∈{.03,1,20}；
独立密集矩阵和相位求积对照（相对/缩放误差1e-10）；均值中心差分（1e-6），
曲率用均值的中心差分（1e-5）；正负方向均保留，未通过时不放宽标准。
再从两个固定新物理场景各取用户0验证生成器重构（1e-12）及完整4096维方向导数（同上述差分门槛）。
只用于公式与实现核查，不使用独立模型确认集，不开展性能选择。

来源：
- NIST DLMF https://dlmf.nist.gov/10.32.E1 和 https://dlmf.nist.gov/10.32.E3。
- Zhang 等，Multidimensional Variational Line Spectra Estimation，§III-A 式(16b)后的 I_1/I_0 定义及式(17b)的相位期望，
  https://arxiv.org/html/1912.11759 。本推导未采用该文的变分迭代或独立频率近似。
- 同一局部 Gaussian 因子的条件矩关系沿用 DERIVATION.md P1–P4 及其论文出处。
