本次只核查数学、现有接口和小规模 CPU 矩阵恒等式；未运行网络、GPU 或训练，未修改 `spatial_score_pilot.py` 或主算法。

结论：拟议一阶公式及损失成立，但其统计模型必须是“给定 C 的 proper-complex Gaussian 加性噪声”。把 C 输入网络不足以保证真实 AFDM 查询满足该模型。有限一阶网络的条件 MSE 可以连接一个明确的 Gaussian 近似；这不把它变成真实 posterior covariance。

**1. 复数因子、协方差轴和 native 等价性。**

令单用户 `H,R` 展平为 M×J 矩阵，J=NP，D=MJ；假设各列噪声独立且服从 CN(0,C)，C=Cᴴ≻0，求导时固定 C。对实际 `[M,N,P]` 的 C 顺序向量化，复协方差为 K=C⊗I_J。定义

\[
\Gamma(K)=\begin{bmatrix}\Re K&-\Im K\\ \Im K&\Re K\end{bmatrix},
\qquad \Sigma=\tfrac12\Gamma(K),\qquad
u=(\Re\operatorname{vec}R,\Im\operatorname{vec}R).
\]

若网络两通道输出为实梯度 \(s=\nabla_u\log q_C(u)\)，将其重组为 \(s_c=s_{\Re}+i s_{\Im}\)，则

\[
m=R+\tfrac12 C s_c. \tag{1}
\]

这是一般实协方差 Tweedie 公式 \(m_u=u+\Sigma\nabla\log q_C\) 的复坐标重写。[Dytso–Poor–Shamai，PDF p.2 式(3)](https://arxiv.org/pdf/2104.01883)。若 score 定义为 Wirtinger 导数 \(\partial\log q/\partial R^*=s_c/2\)，则应写 \(m=R+C\partial\log q/\partial R^*\)，不能再乘一次 1/2。一般复 Hermitian C 的虚部会耦合两实通道；不能分别只用 Re(C) 乘实、虚通道。

对于有限网络 \(F=R+C s_c/2\)，\(\epsilon=R-H\)，拟议损失满足精确恒等式

\[
\frac{\|C^{-1/2}(F-H)\|_F^2}{D}
=\frac{1}{4D}\|C^{1/2}(s_c+2C^{-1}\epsilon)\|_F^2. \tag{2}
\]

因此它是按给定 C 加权的 Gaussian DSM；条件函数空间最优值为 \(F=E[H\mid R,C]\)。这里使用 Hermitian 平方根；若用 Cholesky 因子 C=LLᴴ，则白化为 L⁻¹(F−H)，不是 L⁻ᴴ(F−H)。

取 C=cI、ν=c/2，式(2)恰为

\[
\frac1{2D}\|\sqrt\nu\,s+\epsilon_u/\sqrt\nu\|_2^2,
\]

与 [direct_first_loss 第5行](/Users/wangbo/Desktop/科研/JADCEDD/src/afdm_jadcedd/experiment/training/scores/direct_objectives.py:5) 完全一致，不需要再改维度或乘 2。该等价性指公式与参数化；更换网络结构、协方差编码或训练权重不保证 checkpoint 输出相同。若旧坐标为 R_old=aR，则必须传 C_old=a²C，读出 F=R+(a/2)C s_old，二阶协方差读出除以 a²。

**轴是当前方案的实质限制。** 上式 C 作用在 M 天线轴，对应 [spatial_apply 第18行](/Users/wangbo/Desktop/科研/JADCEDD/src/afdm_jadcedd/algorithm/proposed/gaussian.py:18)。已核实的 \(\sigma^2L_kL_k^H\) 作用在 P 输入列轴，并随用户 k 变化。共同天线 C 不覆盖这一结构。若 C_P 表示每个输入列向量的 covariance，则张量收缩应为 \(F_{mnp}=R_{mnp}+\tfrac12\sum_q(C_P)_{pq}s_{mnq}\)；用最后一轴行向量表示时右乘 C_Pᵀ，不能误写右乘 C_P。保持 `[B,2,M,N,P]` 不妨碍正确指定轴，但更换协方差轴不能沿用当前天线协方差接口而不作适配。

**2. 二阶条件矩：真实协方差与有限均值的条件风险。**

理想 score 的一般实坐标二阶式为

\[
V_u=\operatorname{Cov}(H_u\mid R,C)
=\Sigma+\Sigma\nabla_u^2\log q_C\,\Sigma. \tag{3}
\]

式(3)由式(1)求导并结合条件均值 Jacobian 恒等式得到；[Dytso–Poor–Shamai，PDF p.5 Proposition 1 式(22)](https://arxiv.org/pdf/2104.01883)。按 \(J_{ij}=\partial m_i/\partial u_j\) 的行列约定，\(J=V_u\Sigma^{-1}\)；文献的 Jacobian 排列约定为其转置。一般 C 下不能把非交换矩阵次序任意调换，也不能只用原来的 Hessian 全局平均重建矩阵协方差。

设 m 为精确条件均值，T 为真实条件协方差各列对角块的平均。冻结有限 F 后，矩阵回归目标应为

\[
B(R,C)=\frac1J E[(H-F)(H-F)^H\mid R,C,a=1]
=T(R,C)+\frac{(F-m)(F-m)^H}{J}. \tag{4}
\]

式(4)为条件平方误差分解。当前 [direct_second_loss 第11行](/Users/wangbo/Desktop/科研/JADCEDD/src/afdm_jadcedd/experiment/training/scores/direct_objectives.py:11) 仅回归其标量迹版本；有限 F 下不能声称已经学得精确 posterior covariance。与原文二阶目标的对应位置为 [Cai v2 §IV-C 式(50)–(54)](https://arxiv.org/html/2506.00581v2#S4.SS3)。

若只回归白化风险

\[
a(R,C)=\frac1D E\|C^{-1/2}(F-H)\|_F^2
=\frac1M\operatorname{tr}(C^{-1}B), \tag{5}
\]

一个标量 a 无法识别完整 B。最小且明确的选择有两种：

- 保持标量第二输出，明示限制 \(B_{\rm approx}=aC\)。这是中心固定 F、协方差限制为 aC 的 Gaussian 族的最优期望负对数密度拟合；C=cI 时恢复 native 标量风险含义。
- 要表达任意 M×M Hermitian B，就训练矩阵条件风险，例如冻结 F 后，以 \(C^{-1/2}(F-H)(F-H)^HC^{-1/2}/J\) 为矩阵回归目标，再按 C 的平方根变回原坐标。只给旧标量二阶网络增加 C 输入仍缺少所需信息。

上述矩阵仍平均了 NP 个位置，并忽略位置间交叉协方差。proper-complex 噪声也不保证非 Gaussian 先验的条件后验具有零伪协方差；使用 proper Gaussian 近似还明确舍弃该部分结构。

**3. 条件 MSE 可以怎样接入现有矩阵外信息。**

对中心固定 F 的近似 \(q_F(H)=\prod_{j=1}^J\mathcal{CN}(H_j;F_j,B)\)，期望负对数密度中与 B 有关的部分为

\[
J\log\det B+\operatorname{tr}\{B^{-1}E[(H-F)(H-F)^H]\}.
\]

其最优 B 正是式(4)。所以风险当作**该近似 Gaussian 的 covariance**有明确拟合含义；它不是均值仍为 m 的真实后验中心协方差。这一结论由上述目标直接求导得到，不额外依赖近似推断定理。

若 \(0\prec B\prec C\)，则

\[
S=(B^{-1}-C^{-1})^{-1},\qquad
E=S(B^{-1}F-C^{-1}R), \tag{6}
\]

给出正定、可归一化 Gaussian site；乘回 CN(H;R,C) 后精确恢复 F、B。非交换 C、B 同样成立。若 B 越过 C，精度差可能不正定；即使精确 posterior covariance，也没有普遍的逐查询 B≺C 保证，更不用说含均值偏差的风险。

[gaussian_extrinsic 第26–36行](/Users/wangbo/Desktop/科研/JADCEDD/src/afdm_jadcedd/algorithm/proposed/gaussian.py:26) 的矩阵次序正确，但会把 \(C^{-1/2}BC^{-1/2}\) 特征值裁至给定区间。裁剪后式(6)对应调整后的 B，不再对应原始风险矩阵。必须保留 raw/used 特征值、裁剪量以及正定性诊断；不能把裁剪称为保证贝叶斯正确的理论修复。若保留旧 site，后续 conditional mean 与 covariance 应由该旧 site 和当前 C 重新相乘获得，不能把针对当前 F 训练的风险直接贴给不同的沿用均值。

活动概率 p 给定后，工作混合分布 \((1-p)\delta_0+p q_F\) 的共同天线矩应为

\[
\mu=pF,\qquad V=pB+p(1-p)FF^H/J. \tag{7}
\]

这两式对所声明的近似混合分布精确。向线性模块反馈时可取用户平均 \(\bar V\)，再与共同 cavity C 做外信息相除；不要同时把它压回标量却声称保留了空间协方差。[iterations 第73行](/Users/wangbo/Desktop/科研/JADCEDD/src/afdm_jadcedd/algorithm/proposed/iterations.py:73) 已区分 spatial/isotropic。当前 [Denoiser 第84行](/Users/wangbo/Desktop/科研/JADCEDD/src/afdm_jadcedd/algorithm/proposed/denoiser.py:84) 明确拒绝非各向同性 cavity，且 site、二阶和证据接口均仍是标量，因而现阶段不能只换 first 然后宣称整条闭环已兼容 C。

**4. 活动证据必须使用同一个 C 模型。**

对训练工作模型，\(q_{1,C}(R)=\int\prod_j\mathcal{CN}(R_j;H_j,C)P_H(dH)\)，\(q_{0,C}(R)=\prod_j\mathcal{CN}(R_j;0,C)\)。平衡 BCE 分类器在两类使用相同 C 分布、相同当前 F、并显式条件于 C 时，理想 logit 才是 \(\log(q_{1,C}/q_{0,C})\)。部署概率仍为 \(\operatorname{sigmoid}(\operatorname{logit}\rho+\ell)\)。这是条件 BCE 最优解的直接推导。需要改变两类噪声生成和协方差特征；仅以 tr(C)/M 替代原 v 会丢失方向信息。旧 isotropic classifier 的输出无该校准保证。

若使用正常化的 Gaussian site CN(H_j;E_j,S) 作解析回退，则精确式为

\[
\ell=J[\log\det C-\log\det(C+S)]
+\operatorname{tr}(C^{-1}RR^H)
-\operatorname{tr}[(C+S)^{-1}(R-E)(R-E)^H], \tag{8}
\]

\[
T=(S^{-1}+C^{-1})^{-1},\qquad
\mu=T(S^{-1}E+C^{-1}R). \tag{9}
\]

式(8)–(9)由 proper-complex Gaussian 积分、完成平方直接得到；scalar 版本对应 [Cai v2 §III-B2 式(26)–(30)](https://arxiv.org/html/2506.00581v2#S3.SS2.SSS2)。不能忽略 J 倍 log determinant，也不能用逐元素的 `(cR+vE)/(c+v)` 推广到非交换矩阵。由 F、B 两个矩本身不能确定任意真实 prior 的边缘密度 q₁；解析 site 证据只属于所声明的 Gaussian 近似。

**最小实施范围与统计边界。** 先把一阶试验限定为明确轴、明确 C 生成律的条件 Gaussian 去噪，保留原实梯度约定；C=cI 的噪声采样、损失、读出和坐标尺度必须逐项等价。若后续接闭环，第二目标应选择式(5)的 aC 限制或式(4)的矩阵风险之一，并让证据、site、联合矩、共同投影和支持判定使用同一 C。不能仅以最大/平均特征值落在旧 scalar 支持区间就宣称覆盖了协方差方向和条件数。独立生成的有色 Gaussian 控制验证的是该条件去噪模型；实际自适应 C、信号相关误差、阻尼历史和输入列轴相关性仍须独立验证。

小规模 CPU 代数自检已通过（seed=202610122019，M=3，N=2，P=4；使用具有复非对角项且不交换的 prior covariance 与 C，未调用网络）：一般 C 的实/复读出误差 3.14e−16；实块乘法 1.14e−16；Hessian covariance 4.54e−16；DSM 损失恒等式 4.44e−16；native scalar 损失差 0；尺度换算 2.13e−16；现有 gaussian_extrinsic 恢复 Gaussian prior 的 covariance/mean 误差分别 8.93e−15/9.55e−15；有限均值风险 Gaussian 的 covariance/mean 往返误差 2.13e−15/4.57e−16；式(8)与完整 Kronecker Gaussian 密度比差 1.42e−14。全部低于 1e−11。测试认证矩阵代数，不认证网络近似质量或真实查询分布。

**补充：保留标量第二读出的完整 B≈aC 候选。**

可以先采用这一明确受限的 Gaussian 近似，不需要先增加全矩阵预测头；其收益仍待 first pilot 验证。为保持 native 参数量纲，定义 \(v=\operatorname{tr}(C)/M>0\)、\(\nu=v/2\)，第二网络仍输出 `[B,2,M,N,P]`，但只使用以下全局读出：

\[
a_\theta(R,C)=1+\frac v2\operatorname{mean}_{2D}s_{2,\theta}(R,C),\quad
\widehat\ell_C=\frac{\|C^{-1/2}(F-H)\|_F^2}{D},\quad
\mathcal L_2=E[(a_\theta-\widehat\ell_C)^2]. \tag{10}
\]

F 必须来自已经冻结的同一 first 和当前 (R,C)，不允许二阶损失回传改变它。必须先逐样本完成全部 2D 实坐标归约，再平方，再对 batch 平均。

当 C=vI 时，\(b=\sqrt\nu s_1+(R_u-H_u)/\sqrt\nu\)，有

\[
\widehat\ell_C=\operatorname{mean}_{2D}b^2,\qquad
a_\theta-\widehat\ell_C
=\operatorname{mean}_{2D}(\nu s_2-b^2+1). \tag{11}
\]

所以式(10)逐样本严格恢复 native `direct_second_loss`，包括“全局平均后平方”的顺序；不是仅有比例常数上的等价。这里 v 是参数化尺度，不能把 C 的实际色结构丢弃后只传 v。

对于任意固定 C，令 \(A=C/v\)，\(Z=A^{-1/2}R\)、\(H_Z=A^{-1/2}H\)，则变换后噪声为 CN(0,vI)。q_Z 是给定 C 的变换后查询密度，取 Z 的实坐标梯度。理想 first 时由式(3)得到

\[
a^*_{\rm MMSE}
=\frac{\operatorname{tr}(C^{-1}T)}{M}
=1+\frac{v}{4D}\operatorname{tr}\nabla_{Z_u}^2\log q_Z(Z\mid C,a=1). \tag{12}
\]

因此式(10)的平均读数在理想 first 下对应 **Z 坐标的 Hessian 对角线平均**。这是原 R 坐标 Hessian 的加权迹；一般不等于其普通迹。网络虽然可以接收原 (R,C)，输出量的坐标含义仍必须按式(12)声明。全局迹损失只识别平均值，不能逐坐标认证各个 s₂ 输出都是 Hessian 对角元。有限 first 时则为

\[
a^*=a^*_{\rm MMSE}
+\frac{\|C^{-1/2}(F-m)\|_F^2}{D}, \tag{13}
\]

应称为白化条件风险读出；不能将额外偏差项算作原始或 Z 坐标的真实二阶 score。式(11)是实现代数；式(12)来自固定协方差的变量变换及式(3)；式(13)来自条件风险分解。

与 native 共用活动条件方差的做法一致，可对用户取 \(\bar a_{\rm raw}=K^{-1}\sum_k a_{\theta,k}\)。若保留现有平均方差下限 \(\tau_{\min}\)，定义 \(\bar a=\max(\bar a_{\rm raw},\tau_{\min}/v)\)、\(B=\bar a C\)，此时 \(\operatorname{tr}B/M\ge\tau_{\min}\)。它是平均方差下限，不是对每个特征值施加同一下限；C=vI 时完全恢复 \(\tau=\max(v\bar a_{\rm raw},\tau_{\min})\)。原始读数和下限处理应分别保留。

当 \(0<\bar a<1\) 且查询在声明的 C 支持范围内时，式(6)化简为

\[
B=\bar a C,\qquad
S=\frac{\bar a}{1-\bar a}C,\qquad
E_k=\frac{F_k-\bar a R_k}{1-\bar a}. \tag{14}
\]

乘回当前 cavity 恢复 conditional mean F_k、conditional covariance B。随后用匹配 C 的分类器或式(8)得到 p_k，以式(7)组成联合矩，取 \(V_{\rm joint}=K^{-1}\sum_k[p_kB+p_k(1-p_k)F_kF_k^H/J]\)，最后用 \((p_kF_k,V_{\rm joint};R,C)\) 调用现有矩阵外信息运算。活动混合产生的共同反馈一般不再与 C 成比例；现有矩阵函数可以处理它，但广义特征值裁剪仍需明确标记。

若当前 site 不接受或超出支持范围，沿用旧 (E,S)，并按式(9)重新计算 conditional mean/covariance；再用这些沿用后的矩组成式(7)。即使新接受的 B 一直限制为 aC，只要 C 随轮变化，旧 S 通常也不会与当前 C 成比例，因此需要存储 M×M Gaussian site covariance，而非只存一个标量。这只要求矩阵消息状态，不要求全矩阵网络预测头。共同 C、共同池化 a 下，S 仍可在用户间共享。

这条路径的自洽范围是“白化风险拟合的受限 Gaussian + 明确选择的活动证据 + 精确 Gaussian 消息代数”；不是完整物理后验保证。保留 C 输入、native 标量退化和 B≈aC 约束，使它成为可审计的有限候选；先评估 first pilot，之后再判断是否值得连接二阶、分类器和闭环。它仍不能自行修复 P 输入列轴的用户相关 covariance、非 Gaussian 误差或自适应 C 带来的分布变化。

补充 CPU 自检（seed=202610122027）：式(12)与非交换 Gaussian prior 的解析 conditional covariance 相差 2.22e−16；式(11)的 native residual 相差 4.44e−16，对应第二损失相差 1.11e−15。未调用网络或 GPU。
