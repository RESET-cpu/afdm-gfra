# C-STMP：条件均值、方差与活动检测接口

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: run + validate
- Origin Date: 2026-10-24
- Verification Status: 推导与解析测试完成；实际运行结果以所链接报告为准
- Version Label: c_stmp_integration_20261024

## 1. 三种算法的身份与本次范围

| 展示名称 | 程序标识 | 含义与模型 |
|---|---|---|
| STMP | `STMP` | 原三网络方法：一阶 score、二阶 score、活动分类器；实现、权重和冻结配置保持不变 |
| C-STMP | `C_STMP` | 本项目的 colored 候选名称；有色噪声训练的条件均值网络、由其导数估计的方差、显式沿用的旧活动分类器 |
| DU | `DU` | 原十层 deep unfolded 接收机；保留其权重与算法，`proposed` 作为历史兼容标识保留 |

C-STMP 是用户指定的项目名称，不宣称是既有论文已定义的算法。DU 对应文献的 deep unfolding 概念，十层结构及具体训练仍是本项目实现。

本次采用前次讨论确定的最小接入方案：**网络用有色 Gaussian 训练，实际查询暂取 C=vI，反馈仍为标量协方差。** 不是完整 D-GEC，也没有宣称接收机实际误差满足白 Gaussian。完整有色 C 的既有开发结果尚未显示稳定附加收益，因此不在本轮混入。

新网络固定为完成 200 轮后由原验证 DSM 选中的 EMA `first_best.pt`（选中 epoch=200）。分类器未微调。DU 使用当前保留的最新已接受权重，epoch=1、depth=10，并非与一阶网络同为200轮。

## 2. 坐标、噪声与条件均值

每用户复信道 H∈C^(16×16×16)，N=4096。所有接收机均使用原归一化尺度 s=0.2647966452702405。以下变量是除以 s 后的坐标，真实物理噪声方差同步除以 s²。

把实部、虚部依次打包，h_R,r_R∈R^(2N)。若复噪声为 proper complex Gaussian，复协方差为 C，则

\[
 r_R=h_R+n_R,\qquad
 \Sigma=\tfrac12\mathcal R(C),\qquad
 \mathcal R(C)=\begin{bmatrix}\Re C&-\Im C\\\Im C&\Re C\end{bmatrix}. \tag{1}
\]

这里不是逐元素取 Re(C)。本轮 C=vI_N，所以 Σ=(v/2)I_(2N)。一阶网络给出**活跃条件**均值 Dθ(r,C)≈E[h_R|r_R,C,a=1]，不是已经乘上活动概率的联合信道估计。

网络保持此前训练的参数化，参考实方差 q=1/2：

\[
B=(qI+\Sigma)^{-1/2},\quad K=q(qI+\Sigma)^{-1},\quad
O=q^{1/2}\Sigma^{1/2}(qI+\Sigma)^{-1/2},\quad
D_\theta=Kr_R+OF_\theta(Br_R,C). \tag{2}
\]

原加权 DSM 对应 ||Σ^(-1/2)(Dθ−h_R)||² 的期望，有限网络只是近似该条件均值。参数化、训练目标和原始文献定位见[既有推导](COLORED_PRECONDITIONED_TRAINING_20261024.md)。新 `forward` 已返回 Dθ，不得再次套旧读出 r+(v/2)score。

## 3. 从完整均值的导数得到标量方差

先对精确均值 D*=E[h_R|r_R,C,a=1] 推导。固定 C，对后验密度微分：

\[
\nabla_{r_R}\log p(h_R\mid r_R,C,a=1)=\Sigma^{-1}(h_R-D_*).
\]

以输出坐标为行、输入坐标为列定义 J_D，则

\[
J_{D_*}=P_R\Sigma^{-1},\quad
P_R=\operatorname{Cov}(h_R\mid r_R,C,a=1),\quad
P_R=J_{D_*}\Sigma. \tag{3}
\]

这是 Dytso–Poor–Shamai §IV Proposition 1 式(22)的同一恒等式；其原文 Jacobian 排列相反，需要转置后对应本式，不能交换非对易矩阵。复信道每元素方差是

\[
\tau_k=\frac{\operatorname{tr}P_R}{N}
=\frac{\operatorname{tr}(J_{D_*}\Sigma)}{N}
=\frac{v}{2N}\operatorname{tr}J_{D_*}\quad(C=vI). \tag{4}
\]

分母是4096，不是8192：每个复元素的误差能量等于其实部和虚部误差能量之和。

取实随机符号 z，各分量独立等概率±1，因此 E[zzᵀ]=I；令 w=Σ^(1/2)z。由 E[wᵀJ_Dw]=tr(J_DΣ)直接得到实现：

\[
\widehat\tau_k=\frac1{PN}\sum_{j=1}^P
w_j^T\frac{D_\theta(r_R+\epsilon w_j,C)-D_\theta(r_R-\epsilon w_j,C)}{2\epsilon}.
\tag{5}
\]

本轮 P=1、ε=0.01，同一输入的所有接收机迭代固定随机方向；新一次推断重置到同一确定性种子。上述期望恒等式针对与随机方向独立的固定查询；闭环中后续查询依赖此前反馈、可能间接依赖该方向，因此不宣称整条自适应轨迹上的迹估计无偏。它不是新增训练，也不是条件 MSE 的无偏估计。有限差分误差、随机迹误差和 Dθ 的近似误差必须分开看。

必须对**完整 Dθ**求导，固定 C、谱分解和所有噪声条件：

\[
J_{D_\theta}=K+O J_F B. \tag{6}
\]

线性分支 K 及输入 B 都不能遗漏，也不对从线性接收模块产生 C 的计算链求导。一次完整查询需要1+2P次均值网络前向；本轮是3次，不能把它记作一次 CNN 或虚构二阶网络调用。

## 4. 保持原 STMP 的 Gaussian site 和活动混合

现有标量反馈对全部 K_users 个用户平均方差，随后施加旧下限：

\[
\bar\tau=\frac1{K_{\rm users}}\sum_k\widehat\tau_k,\qquad
\tau=\max(\bar\tau,10^{-4}). \tag{7}
\]

若0<τ<v，Gaussian 相除给出

\[
\lambda_{\rm site}=1/\tau-1/v,\quad
\eta_{{\rm site},k}=D_{\theta,k}/\tau-r_k/v. \tag{8}
\]

令 t=1/λ_site、u_k=tη_site,k，与当前 query 重组：

\[
\widetilde D_k=\frac{tr_k+vu_k}{t+v},\qquad
\widetilde\tau=\frac{tv}{t+v}. \tag{9}
\]

接受更新时，在数值精度内恢复 Dθ 和 τ。若τ≥v，沿用旧 site；这时(9)不等于当前原始 Dθ。越出训练支持也遵循旧 fallback。**τ≥v 并不一定违反精确后验；拒绝它是为了满足正精度 Gaussian 外信息的算法约束。** 相比之下，vI 下精确均值的 Jacobian 为半正定；稳定负方向响应不能解释为合法的精确条件方差。

旧分类器读取同一查询的(r_k,v,Dθ,k)，包括原始均值及能量、相关性、残差特征。训练类别先验π_train=1/2，故

\[
\ell_k=f_\phi(r_k,v,D_{\theta,k})-\operatorname{logit}\pi_{\rm train},\quad
p_k=\operatorname{sigmoid}(\operatorname{logit}\rho+\ell_k). \tag{10}
\]

ρ只加入一次。分类器仍由旧一阶特征训练，本轮明确记录这一分布失配；不修改 checkpoint 内的原 teacher 哈希，不把它标为新配套分类器。即使site拒绝，分类器也沿用原STMP约定读取当前原始 Dθ，而Gaussian条件矩使用(9)。

设 \widetilde D_k 展平成16×256矩阵，Bernoulli混合后

\[
m_k=p_k\widetilde D_k,\qquad
V_k=p_k\widetilde\tau I_{16}
 +p_k(1-p_k)\frac{\widetilde D_k\widetilde D_k^H}{256}. \tag{11}
\]

活动不确定性的第二项必须保留。不能先微分 pD 再重复加入 Bernoulli 混合。线性模块接收跨用户平均且投影为标量的 V，随后按原实现做 Gaussian 外信息和阻尼。

## 5. 线性模块、阻尼和停止

观测为Y=AX+W。以现有共同标量先验c、均值x_p计算LMMSE校正：A=USVᴴ，g_i=cs_i/(σ_w²+cs_i²)，α=Σ_i s_i g_i/(K_users·16)。

\[
r=x_p+V\operatorname{diag}(g_i)U^H(Y-Ax_p)/\alpha,\qquad
v=c(1-\alpha)/\alpha. \tag{12}
\]

对线性query的均值/协方差、对返回线性模块的外信息均值/协方差，分别沿用原算术阻尼。新值权重：原STMP为0.2，C-STMP为前次开发选定的0.4；该变化与网络和方差接口一起构成本次方法差异，不能把全部速度变化归因于噪声训练。

本轮原STMP与C-STMP均最少60轮、最多600轮、相对变化阈值0.0005，其余活动、site与决策稳定条件沿用保存配置。DU固定10层，层数与迭代成本并不相同。因此记录原生停止轮数、逐轮NMSE和实际热运行耗时三个量。阈值到达轮数仅作评分，不进入运行停止条件，不使用真值提前停止。

## 6. 实现与进一步训练的边界

- 独立实现：`src/algorithm/C_STMP/`。继承旧接收机包装，复用原 `STMP/denoiser.py`、`iterations.py` 的数值方程；旧文件哈希保持不变。
- 独立配置：`src/configs/candidates/C_STMP_20261024.json`。新模型schema单独验证，原STMP的teacher一致性检查不放宽。
- 标准接收机接口仍是四字段ReceiverInput→(arrays,record)。输入不含信道真值或活动标签。
- 本次验证已知相位形成的公共算子、由观测估计噪声。已知相位使用了相位真值，不能宣传为完全未知相位结果。C-STMP尚未接入STMP内部联合相位更新；通用实验入口可在外部先估相位，但该路径未在本轮验证。
- 保留两套学习网络即可运行：条件均值网络＋旧分类器；数值方差没有第三套学习参数。
- 若微调分类器，固定新一阶权重，复用干净信道，重新生成两类查询的均值特征；保证两类噪声法则一致、保留平衡训练先验，另用独立开发输入检查接收机查询。不能用本轮场景14训练后再把其结果叫独立验证。
- 若进一步使用完整有色C，需要相应协方差载体、标量反馈近似说明，以及分类器条件适配。这不是换一个C文件就等于完整D-GEC。

## 7. 验证与来源

解析测试覆盖实/复方差因子、相关Gaussian精确后验迹、site重组与活动混合、候选绑定和旧资产保护。实际200轮网络另用保存查询做有限差分与自动微分比较，结果不能由旧epoch92/154的诊断替代。

单场景配对协议、原始输出、逐轮指标、重复计时、导数核验及报告统一保存于[运行目录](../../../result/channel_denoising/data/c_stmp_integration_20261024)。不计算总体置信区间，不把用户数×迭代数当独立场景数。

来源定位：

1. Dytso, Poor, Shamai, *A General Derivative Identity for the Conditional Mean Estimator in Gaussian Noise and Some Applications*, [arXiv:2104.01883v1](https://arxiv.org/pdf/2104.01883)，§IV Proposition 1式(22)、Corollary 1式(23)，PDF pp.5–6。对应条件均值导数与协方差；(4)的复维归一化、(5)的随机符号中央差分为本项目明确推导。
2. Cai等，*Joint Activity Detection and Channel Estimation for Massive Connectivity: Where Message Passing Meets Score-Based Generative Priors*, [v2](https://arxiv.org/html/2506.00581v2)，§III-A–B Gaussian外信息及活动混合，§IV-A Tweedie关系，§V-B1式(57)–(58)阻尼。项目学习分类器、有限方差处理和具体停止规则另见代码，不归为论文原始实现。
3. Hershey, Le Roux, Weninger, *Deep Unfolding: Model-Based Inspiration of Novel Deep Architectures*, [arXiv:1409.2574](https://arxiv.org/abs/1409.2574)，摘要与§1的迭代算法展开说明。DU是项目展示名称；既有十层模型不因重命名改变。

## 8. 2026年10月25日：独立二阶 score 训练候选

### 8.1 任务与来源

用户明确授权开始训练二阶 score 网络。此次仅新增训练候选，不替换已冻结 STMP、DU 或现有 C-STMP 的导数方差版本。研究执行记录：ARS experiment-agent / run；状态以独立运行目录的 `status.json`、`complete.json` 为准，未完成训练与闭环比较时不报告已验证收益。

依据 [Cai v2 §IV-C式(50)–(54)](https://arxiv.org/html/2506.00581v2#S4.SS3) 的二阶得分匹配、只学习消息所需的迹，以及冻结一阶再训练二阶的流程。以下一般协方差加权迹是本项目公式推广，不是原论文已完成的有色 AFDM 实验。相关术语及 [Meng等，NeurIPS 2021](https://proceedings.neurips.cc/paper/2021/file/d582ac40970f9885836a61d7b2c662e4-Paper.pdf) §4–5 的依据已记入 TERMINOLOGY.md。

### 8.2 训练对象与方差读出

使用归一化信道的实打包坐标，维数为 \(d=2N\)，其中 \(N\) 为复坐标数。给定协方差条件 C，设 \(r=h+n\)、\(n\sim\mathcal N(0,\Sigma)\)，\(\Sigma=\mathcal R(C)/2\)。噪声与 h 条件独立。令

\[
s_1(r,C)=\nabla_r\log p(r\mid C),\quad S_2(r,C)=\nabla_r^2\log p(r\mid C),\quad
m=r+\Sigma s_1,\quad V=\Sigma+\Sigma S_2\Sigma. \tag{13}
\]

只需要每复坐标平均方差，因此训练的输出为一个归一化的二阶 score 加权迹：

\[
u_\phi(r,C)\approx\frac{\operatorname{tr}(\Sigma S_2\Sigma)}{\operatorname{tr}\Sigma},\quad
\nu=\frac{\operatorname{tr}\Sigma}{N},\quad
\widehat\tau=\nu(1+u_\phi). \tag{14}
\]

没有学习或构造完整 Hessian。卷积输出图经过全坐标平均得到 u，其各元素没有独立 Hessian 对角元的监督含义。对于训练中归一化轴因子的 C，\(\nu=v\)；代码从谱计算 \(\nu\)，避免忽略浮点迹偏差。接收机当前 \(C=vI\) 时，\(u=(v/2)\operatorname{tr}(S_2)/d\)，即原二阶 score 平均迹的无量纲参数化。必要时可以由 u 还原该平均迹为 \(2u/v\)。输入预条件仅改变神经网络参数化；式(13)的求导坐标始终是原 r。

冻结已训练的 \(D_\theta\)，定义 \(\widehat s_1=\Sigma^{-1}(D_\theta-r)\) 和 \(\widehat b=\widehat s_1+\Sigma^{-1}(r-h)\)，则 \(\Sigma\widehat b=D_\theta-h\)。对 Cai 二阶监督矩阵 \(\widehat b\widehat b^T-\Sigma^{-1}\) 两侧乘 \(\Sigma\)、取迹并归一化，得到

\[
\mathcal L_2=\mathbb E\left[\left(u_\phi-
\left\{\frac{\|D_\theta(r,C)-h\|^2}{\operatorname{tr}\Sigma}-1\right\}\right)^2\right]. \tag{15}
\]

平方放在全样本迹之后。在 \(C=vI\) 时，令旧网络 \(S_2\) 输出的平均值满足 \(u=(v/2)\operatorname{mean}(S_2)\)，式(15)严格退化为当前 `direct_second_loss`，没有改为逐坐标平方损失。

有限一阶网络误差必须保留：

\[
\mathbb E[\|D_\theta-h\|^2\mid r,C]
=\operatorname{tr}V+\|D_\theta-m\|^2. \tag{16}
\]

因此精确一阶下是二阶 score 加权迹监督；有限冻结一阶下，方差读出的条件最优值是该去噪器的条件误差风险，不自动等于真实后验方差或当前网络的 Jacobian 迹。此限制与原冻结有限一阶训练一致。验证直接报告原始负值比例，不用裁剪掩盖负预测。

### 8.3 独立实现和训练协议

- 代码：`src/training/colored_second_20261025/`；配置：`src/configs/training/colored_second_20261025.json`；输出：`result/channel_denoising/data/colored_second_50000_20261025/`。
- 一阶教师固定为有色预条件网络的 epoch 200 EMA，SHA-256 `7327d01785f10e3e18d76f7085604e1d1d53baa9d8cd80e12943768015452b91`；不共享可训练参数，也不反传二阶损失给一阶网络。
- 独立第二个 RefineNet 使用原始二阶随机初始化，扩展精确 C 条件；输入采用一阶候选已有的 \((0.5I+\Sigma)^{-1/2}r\) 缩放，输出为式(14)的 u。初始化参数沿用，但参数化改变，不声称初始函数与旧网络相同。
- 原 50000 个训练信道、5000 个内部验证信道和相同总体 RMS；沿用新一阶的单一连续有色 Gaussian 噪声族，SNR −20 至30 dB。每次在线重新采噪声，无白噪声/相关噪声四类混合。
- 沿用当前已部署旧二阶的 100 轮预算、batch 64、Adam学习率 \(10^{-4}\) 至 \(10^{-6}\)、EMA 0.999、梯度裁剪1及原二阶随机种子。两级噪声采样的分布一致，但有色查询和第一版白噪声二阶训练的逐样本噪声不声明逐位相同。
- 固定有色验证损失选择 EMA 权重；同一验证信道的固定白噪声查询单独监测当前接收机 \(C=vI\) 边界，不参与选模。按SNR分组报告方差/实测误差比、负方差比例和对单次误差实现的预测误差；这些均不称为 oracle 后验方差误差。没有使用正式接收机测试场景训练或选模。
- 支持完整 Adam、EMA、样本游标及随机数状态恢复；保存源码和保护资产哈希。CLI 的 `prepare`、`preflight` 不启动正式训练；只有显式 `train` 启动。训练与小检查的结果分别保存，初始化检查的更新不进入正式训练。

当前接收机代码、分类器和模型绑定不变。新二阶权重完成训练后，仍需与导数版本做相同输入的方差与单场景闭环比较，才能判断是否替换。

## 9. 2026年10月25日二阶网络完成与场景200配对比较

二阶网络已完成100轮、78200次优化更新，按原有色内部验证集选中epoch96 EMA；一阶固定epoch200 EMA。没有使用场景200选模。二阶权重SHA-256为`5892949324111a96d662d1e0ad3972c40e0c173253138be14f902741d87792a9`，训练完成记录见`result/channel_denoising/data/colored_second_50000_20261025/complete.json`。

独立接入文件为`src/algorithm/C_STMP/second_configuration.py`、`second_moments.py`和`second_receiver.py`，配置为`src/configs/candidates/C_STMP_second_20261025.json`。运行时继续使用C=vI，按式(14)从网络输出读出原始复方差；仍由原STMP去噪模块跨用户平均后设归一化下界10^-4，并保留原外信息精度检查。没有逐用户预先截断、取绝对值或改变二阶网络输出。

用户指定复用此前场景200。使用原0 dB观测，40用户中5个活跃，已知相位、估计噪声。两个C-STMP候选仅替换方差估计器；相同一阶、旧分类器、0.5判决门限、0.4阻尼及最少60轮的原停止规则。STMP参考仍用原0.2阻尼，所以STMP与C-STMP的差异不能全部归因于网络。信道和活动真值只供外部评分。

| 指标 | 原STMP | C-STMP导数方差 | C-STMP新二阶网络 |
|---|---:|---:|---:|
| 最终联合信道NMSE（dB） | -11.78767 | -13.85988 | -13.90984 |
| 最终AER | 0 | 0 | 0 |
| 原停止条件下迭代数 | 85 | 60 | 60 |
| AER此后持续为零的首轮 | 29 | 9 | 11 |
| 此后始终距自身最终NMSE不超过0.1 dB的首轮 | 67 | 25 | 25 |
| 此后NMSE始终不高于-12 dB的首轮 | 未达到 | 14 | 13 |
| 完整接收耗时中位数（秒） | 7.3303 | 7.9751 | 6.2230 |
| 三次耗时范围（秒） | 7.1283–7.5656 | 7.7571–7.9859 | 6.2140–6.2935 |
| 原始逐用户方差非正的次数 | 0 | 67/2400 | 0/2400 |
| 跨用户平均后触发方差下界的轮数 | 0 | 1 | 0 |

计时在RTX5080上进行，各方法先完成一次完整推断，再交错循环计时3次。包含噪声估计及完整接收迭代，在计时边界同步CUDA；不包括加载权重、真值评分观察器、绘图和写盘。所有重复的判决、停止轮数和概率均与对应首次推断一致。本输入中新二阶版本比导数版本耗时降低21.97%；原导数版每轮调用3次一阶网络，新版每轮1次一阶加1次二阶。这里报告的是实测时间，不由迭代次数推算加速。

新二阶版本NMSE仅改善0.04996 dB，达到自身平台的轮数不变，活动检测持续稳定反而晚2轮。可以据此认为本场景的精度基本持平、计算开销下降；不能宣称总体精度或收敛速度提升。没有负方差也不证明方差校准准确：最终原始平均方差为0.03379，导数版本为0.06779，两者估计对象及有限网络误差不同，尚未对真实后验方差作验证。此结果也不足以断言分类器普遍无需重训。

验证包含7项数学/适配器测试、同输入一阶输出精确一致、旧STMP和导数C-STMP与此前保存结果逐轮NMSE/概率/判决完全复现，以及77项受保护资产哈希不变。旧算法、权重、历史结果和FINAL绑定保留。

完整计划、代码哈希、逐轮输出、原始方差、计时与结果位于[独立结果目录](../../../result/snr_comparison/data/c_stmp_second_20261025_scene0200_snr0/RESULT.json)；[收敛与时间图](../../../result/snr_comparison/figures/c_stmp_second_20261025_scene0200_snr0/comparison.png)和[原始方差图](../../../result/snr_comparison/figures/c_stmp_second_20261025_scene0200_snr0/variance.png)已保存。`run.py`拒绝覆盖已有比较，应复制到同层新目录后执行复现；未启动其他场景或后续训练。

## 10. 2026年10月25日高SNR反馈排查

准备1000场景SNR实验时，场景200在8/10 dB、新二阶网络、0.4新消息权重下均达到600轮上限，NMSE分别为+14.14692/+14.47715 dB，AER均87.5%。因此没有启动完整8000次推断。用户随后授权排查；原0.4计划及失败输出保留，不以更改配置后的结果替换。

固定一阶、旧分类器、输入及停止规则，只比较方差估计器（导数/学习二阶）和新消息权重（0.4/0.2）。同一场景的结果为：

| 方差估计器、新消息权重 | 8 dB：NMSE / 轮数 | 10 dB：NMSE / 轮数 | 两档AER |
|---|---|---|---|
| 学习二阶、0.4 | +14.14692 / 600未收敛 | +14.47715 / 600未收敛 | 87.5% |
| 学习二阶、0.2 | −18.21061 / 103 | −19.12986 / 118 | 0 |
| 导数、0.4 | −18.30553 / 60 | −19.24330 / 60 | 0 |
| 导数、0.2 | −18.28420 / 94 | −19.21922 / 101 | 0 |

这里0.4→0.2表示更强阻尼，两个方向的消息更新均减少新值占比。0 dB学习二阶的0.2候选为−13.87569 dB、64轮、AER=0，对照原0.4为−13.90984 dB、60轮。没有调整门限、迭代上限或收敛容差。

失败两档未出现非正方差、方差下界触发、超出支持区间、拒绝site更新或外信息方差投影；但最后20轮连续更新方向的余弦均值分别为−0.98686、−0.98187。它们是有限值的大误差振荡，不能依据方差为正而判定反馈稳定。

8 dB失败末轮的标量输入方差v=3.12800，外部实测输入误差=10.13659；学习二阶0.2收敛末轮相应为0.80797和0.80817。这只是消息方差与一次误差实现的诊断，不是真实后验协方差校准的证明。保存失败输入上的同输入比较给出学习二阶原始平均方差0.05975、导数估计0.12148；两个适配器的一阶输出完全相同。换回旧一阶均值特征做离线分类，也未消除该失败输入上的全部虚警；稳定输入上两类特征均正确。该离线检查不等于完整闭环分类器消融，但实际不重训分类器即可恢复收敛，故本次优先修正阻尼。

方差对反馈的作用可以直接由Gaussian外信息公式说明。活动概率近似1，暂固定v及跨用户平均的τ，设D是实打包条件均值向量，J_D是对输入r的Jacobian，则

\[
e=\frac{D(r)-(\tau/v)r}{1-\tau/v},\qquad
J_e=\frac{J_D-(\tau/v)I}{1-\tau/v}. \tag{17}
\]

若d为实坐标总数，原导数方差在C=vI时估计τ_der/v≈tr(J_D)/d。因此，在这个固定方差近似下，选择相应导数迹影响输入导数中平均线性分量的抵消。学习二阶依据式(15)–(16)拟合有限D的条件误差风险，它不必等于当前D的导数迹。公式(17)未计入τ、v、活动概率及历史消息的全部变化，不能用作整个迭代收敛的证明；这里只解释为何换方差后不能直接继承导数版较大的新消息权重。专业名称继续采用第7–8节文献中的Gaussian外信息、条件均值、Jacobian及阻尼，不将本项目诊断另命名为已有方法。

独立检查预先固定四个新种子202610220020001–202610220020004，每种子八档SNR，并在8/10 dB保留导数0.4参考。0.2取自既有STMP设置，在这些输入生成前选定，不继续搜索权重。最终完成状态、全部错误和候选配置以[排查报告](../../../result/snr_comparison/data/c_stmp_stability_20261025/REPORT.md)及[机器可读汇总](../../../result/snr_comparison/data/c_stmp_stability_20261025/SUMMARY.json)为准；四个物理场景不替代1000场景总体比较。原算法与全局绑定不切换。

上述独立检查已完成：学习二阶0.2的32个条件全部按原规则收敛，60–194轮；−4 dB共3次漏检（该档AER=3/160=1.875%），其余七档无活动错误，全程无虚警。八个高SNR导数参考也全部收敛、AER=0；学习二阶0.2的NMSE比导数0.4高0.02866–0.16750 dB，平均轮数为131.75对65.5。本轮未测量排除诊断开销的独占设备时延，不能由此报告算法时间加速。已保存独立`C_STMP_second_damping02_20261025.json`，仅改ep.damping。49次完整推断的保存指标重算与文件身份核验通过，20份保存查询身份及77项旧资产哈希核验通过；正式8000次推断未启动。

## 11. 2026年10月25日补充完整接收时间核验

针对“导数版单轮成本可由较少迭代抵消”的判断，另对场景200的8/10 dB观测进行完整预热及交错重复计时，每方法每条件3次；原始数据与协议见[计时报告](../../../result/runtime_comparison/data/c_stmp_variance_scene0200_20261025/REPORT.md)。计时前后同步CUDA，包含噪声估计、线性模块建立及全部接收迭代，排除外部逐轮观察器、真值评分、加载权重和写盘。既有CPU用户数实验保持运行，故为同一后台负载下的交错比较，不声称独占整机。

| SNR | 旧STMP：轮数 / 秒 | 导数C-STMP：轮数 / 秒 | 学习二阶C-STMP：轮数 / 秒 |
|---:|---|---|---|
| 8 dB | 129 / 11.0290 | 60 / 7.3921 | 103 / 10.3238 |
| 10 dB | 144 / 12.1640 | 60 / 7.4457 | 118 / 12.1449 |

秒数为三次中位数，范围和全部重复保存在报告及TIMING.json。三套方法均AER=0；导数版NMSE分别为−18.30553/−19.24330 dB，旧STMP为−17.74302/−18.95950 dB，学习二阶为−18.21061/−19.12986 dB。导数版相对旧STMP总耗时减少32.98%/38.79%，相对学习二阶减少28.40%/38.69%。本例中较少迭代抵消了每轮额外的一阶网络计算，不能只依据网络调用次数否定导数方差。

新消息权重分别为0.2/0.4/0.2，故这是完整配置比较；并非固定阻尼、仅更换方差估计器的消融。18次计时均复现原停止轮数及活动判决，并通过概率/NMSE数值容差核验；77项保护资产保持不变。一个物理场景不能给出总体运行时间结论，原算法与全局绑定未切换，未启动正式1000场景实验。

## 12. 2026年10月25日：导数方差的论文推导与实现对应

本节展开第3节的证明，并说明它与二阶 score 读出的关系。条件均值导数恒等式及 Monte Carlo 散度估计已有文献依据，不作为本项目新提出的恒等式。项目采用的是有色噪声条件均值网络、协方差缩放的随机符号中央差分，以及现有 JADCE 消息更新的组合。当前接收机仍取 C=vI；一般 C 的推导不代表完整有色消息接口已经接入。

### 12.1 Gaussian 查询下的条件均值导数

省略用户和迭代下标。在活跃条件 a=1 下，将复信道 h 和查询 r 打包成实向量 x,y∈R^(2N)。采用工作模型

\[
y=x+\xi,\qquad \xi\mid C\sim\mathcal N(0,\Sigma),\qquad
\Sigma=\tfrac12\mathcal R(C)\succ0,\qquad
\xi\perp x\mid(C,a=1). \tag{18}
\]

所有导数均固定 C。Gaussian 查询是接收机的近似建模假设，不声称迭代产生的真实误差与信道独立且严格 Gaussian。复噪声的 proper 条件给出式(18)中的实协方差；以下实坐标推导不要求信道先验或后验也为 proper。

定义精确条件均值和实后验协方差

\[
m(y,C)=\mathbb E[x\mid y,C,a=1],\qquad
P(y,C)=\mathbb E[(x-m)(x-m)^T\mid y,C,a=1]. \tag{19}
\]

由 Bayes 公式与 Gaussian 似然，在可以交换积分与微分的条件下，有

\[
\begin{aligned}
\nabla_y\log p(y\mid C,a=1)&=\Sigma^{-1}(m-y),\\
\nabla_y\log p(x\mid y,C,a=1)
&=\Sigma^{-1}(x-y)-\Sigma^{-1}(m-y)
=\Sigma^{-1}(x-m).
\end{aligned} \tag{20}
\]

按输出坐标为行、输入坐标为列定义 [J_m]_{ij}=∂m_i/∂y_j。对条件均值的积分表达式求导：

\[
\begin{aligned}
J_m
&=\int x\,[\nabla_y p(x\mid y,C,a=1)]^T\,dx\\
&=\mathbb E[x(x-m)^T\mid y,C,a=1]\,\Sigma^{-1}
=P\Sigma^{-1},\\
\boxed{P=J_m\Sigma}. 
\end{aligned} \tag{21}
\]

这是 [Dytso–Poor–Shamai v1](https://arxiv.org/pdf/2104.01883v1) §IV Proposition 1式(22)，PDF p.5。该文 §II式(9)、PDF p.4 将 Jacobian 的输入坐标放在行上，故原文是相反排列；转换到本节约定后得到式(21)。一般有色 Σ 下，不能将本式误写成 ΣJ_m。

复信道每元素的条件方差为实协方差的迹除以复维数：

\[
\begin{aligned}
\tau_*(y,C)
&=\frac1N\mathbb E[\|h-\mathbb E[h\mid r,C,a=1]\|^2\mid r,C,a=1]\\
&=\frac1N\operatorname{tr}P
=\frac1N\operatorname{tr}(J_m\Sigma),\\
\boxed{\tau_* = \frac{v}{2N}\operatorname{div}_y m(y,vI)}
&\qquad\text{when }C=vI_N.
\end{aligned} \tag{22}
\]

这里 N=4096，实维数为2N=8192。分母 N 负责每复元素归一化，1/2 来自每个实分量的噪声方差为 v/2。若 h∼CN(0,aI)，精确条件均值为 m=a/(a+v)y，则式(22)给出 av/(a+v)，与解析后验一致；单位映射的导数读出为 v，可单独用于检查归一化因子。

### 12.2 与二阶 score 的等价关系及有限网络的区别

令 s_*=∇_y log p(y|C,a=1)。式(20)给出 m=y+Σs_*，因此

\[
J_m=I+\Sigma J_{s_*},\qquad
P=\Sigma+\Sigma\left[\nabla_y^2\log p(y\mid C,a=1)\right]\Sigma.
\tag{23}
\]

这与 [Cai等v2](https://arxiv.org/html/2506.00581v2) §IV-A式(44)–(45) 的一、二阶 Tweedie 读出对应；一般协方差的实坐标写法由上式给出。在精确条件均值下，导数版与二阶 score 版给出同一个后验协方差的迹。前者从均值映射计算所需导数，后者另用网络学习相关二阶统计量。

有限网络 Dθ 不保证等于 m。定义 eθ=Dθ−m，则未作有限差分和随机近似之前，导数读出的误差是

\[
\widetilde\tau_\theta=\frac1N\operatorname{tr}(J_{D_\theta}\Sigma),\qquad
\widetilde\tau_\theta-\tau_*
=\frac1N\operatorname{tr}(J_{e_\theta}\Sigma).
\tag{24}
\]

因此均值 NMSE 小并不自动保证导数方差准确。对比式(16)，冻结有限 Dθ 后直接拟合平方误差的条件最优读出为 τ_*+||eθ||²/N；它与式(24)的导数读出并非同一个量。论文中将前者的有限网络读出解释为条件误差风险，将后者称为由条件均值导数得到的方差近似；两者只在精确均值及相应理想条件下重合。

网络实际返回的是式(2)的完整 Dθ，而不是裸 score。固定 C 后，式(6)给出 J_D=K+OJ_FB。输入预条件、线性分支和输出缩放均进入求导；不只对 Fθ 求导，也不对上游估计 C 的计算链或整个接收迭代求导。

### 12.3 不构造完整 Jacobian 的随机方向计算

对与随机方向独立的固定查询，令 z_j 的实坐标独立等概率取±1，并令 w_j=Σ^(1/2)z_j。因此 E[w_jw_j^T]=Σ，有

\[
\mathbb E_z[w_j^T J_{D_\theta}w_j]
=\operatorname{tr}(J_{D_\theta}\Sigma),\qquad
J_{D_\theta}w_j\approx
\frac{D_\theta(y+\epsilon w_j,C)-D_\theta(y-\epsilon w_j,C)}{2\epsilon}.
\tag{25}
\]

得到实际读出

\[
\boxed{
\widehat\tau_k=
\frac1{PN}\sum_{j=1}^{P}
w_{k,j}^{T}
\frac{D_\theta(y_k+\epsilon w_{k,j},C)-D_\theta(y_k-\epsilon w_{k,j},C)}{2\epsilon}
}. \tag{26}
\]

当 C=vI 时，w=√(v/2)z；等价地令 δ=ε√(v/2)，则

\[
\widehat\tau_k=\frac{v}{2NP}\sum_{j=1}^P
z_{k,j}^T\frac{D_\theta(y_k+\delta z_{k,j},vI)-D_\theta(y_k-\delta z_{k,j},vI)}{2\delta}.
\tag{27}
\]

[Metzler–Maleki–Baraniuk v2](https://arxiv.org/html/1406.4175v2) §V-B式(21)给出 Monte Carlo 散度计算：Gaussian 随机方向和单侧差分。本项目式(25)–(27)使用随机符号、协方差缩放和中央差分，是根据二阶矩恒等式作的明确适配，不把这些细节说成原论文的实现。充分光滑时中央差分有 O(ε²) 截断误差；有限步长和有限精度下不声明严格无偏。

当前 P=1、ε=0.01。每批输入调用一次 Dθ(y,C) 得到均值，再调用两次得到中央差分，共3次一阶网络前向；没有第二个 score 网络，也不构造完整 Jacobian 或 Hessian。同一次接收推断的各轮迭代复用固定随机方向，新输入推断时从种子2026102407重新生成；后续查询可能经反馈依赖这些方向，因此固定查询的期望恒等式不能直接扩展为整条闭环轨迹无偏。代码对应 `src/algorithm/C_STMP/moments.py::trace_variance` 和 `ColoredMoments.infer`。

### 12.4 活动混合、数值处理与反馈解释

式(26)估计活跃条件下的信道方差。沿用现有实现，先对全部用户的原始读出平均，再设归一化下界10^-4，即式(7)；没有逐用户先截断。只有0<τ<v时才更新式(8)的正精度 Gaussian site，否则沿用旧 site。令当前 site 与查询重组后的复条件均值、每复元素平均方差为 μ̃_k、τ̃_k；接受更新时它们等于当前 Dθ 的复表示及共享 τ。

令 p_k 为当前分类器输出的活动概率，g_k=a_kh_k。由全期望与全协方差公式，工作后验的矩为

\[
\widehat g_k=p_k\widetilde\mu_k,\qquad
\nu_k=p_k\widetilde\tau_k+
\frac{p_k(1-p_k)}N\|\widetilde\mu_k\|^2.
\tag{28}
\]

式(28)是第4节空间协方差的归一化迹；后一项表示活动不确定性。对应 [Cai等v2](https://arxiv.org/html/2506.00581v2) §III-B3式(35)–(36)，但本项目 p_k 来自已有学习分类器。不能将 τ̂_k 直接视为联合活动–信道方差，也不能先求 p_kDθ 的导数后再次添加同一混合项。随后跨用户平均、Gaussian 外信息、投影和阻尼沿用第4–5节实现。

导数读出对外信息的作用可用第10节式(17)解释：活动概率近似1、暂固定 v 和 τ 时，外信息均值的 Jacobian 是 (J_D−(τ/v)I)/(1−τ/v)。在标量协方差下，导数读出由当前 D 的平均输入导数决定，因此直接参与平均线性响应的抵消；有限二阶网络的条件误差风险不必具有相同值。实际算法还包含跨用户平均、数值下界、活动概率、变化的 v/τ 和历史消息，故此关系不能推成整个闭环的收敛保证。

可用于论文的方法表述为：

> 在 Gaussian 查询近似下，利用条件均值的 Jacobian 与后验协方差之间的恒等式，将每复信道元素的平均后验方差写成协方差加权的 Jacobian 迹。通过对已训练条件均值网络施加协方差缩放的随机扰动，并计算中央差分，近似该迹，从而无需独立训练二阶 score 网络。该读出作为活跃条件下的方差近似，与活动概率结合后形成 JADCE 反馈消息。有限网络误差、随机方向与差分误差及查询模型失配通过实际接收实验评估。

本节复核运行了现有4项解析测试：复 Gaussian 的1/2因子、非对易相关 Gaussian 的精确协方差迹、单位去噪映射读出、Gaussian site重组与活动混合，均通过（`src/tests/test_c_stmp_20261024.py`）。这些测试验证数学映射与实现，不验证学习网络的后验精确性或一般闭环收敛。此次仅补充推导和文献定位，没有修改接收机、权重或绑定，也未启动新场景实验或训练。

### 12.5 与 Cai 路线相比的理论保证范围

基础恒等式没有降级：固定 Gaussian 查询模型时，式(21)与式(23)等价。有限网络的保证则需要区分。直接监督二阶统计量具有针对该统计量的训练目标；只训练一阶去噪器，再求其输入导数，并不能从较小的一阶损失自动推出较小的方差误差。这是本路线需要明确承认的薄弱环节，不能仅用“两个公式理想情况下等价”略去。

式(24)已给出两者的差别。对固定有限均值网络 Dθ，Cai §IV-C式(52)–(53)的平方监督在统一的实坐标和方差读出下，其无限容量、总体风险最优值对应式(16)的条件误差风险：τ_*+||Dθ−m||²/N。故一阶误差通过其平方进入该理想读出的偏差，实际第二网络另有拟合与泛化误差。导数读出的偏差则是 tr(J_eΣ)/N，需要关于输入导数的额外控制。一阶函数值误差小，不能一般性地约束此项。例如仅作为数学反例的实标量误差 e_η(y)=ηsin(y/η²) 一致趋于零，但 e'_η(y)=η^-1 cos(y/η²) 不趋于零。此反例不声称当前网络具有这种形状。

[Meng等，NeurIPS 2021](https://proceedings.neurips.cc/paper/2021/file/d582ac40970f9885836a61d7b2c662e4-Paper.pdf) §1、PDF pp.1–2明确指出，一阶训练损失较小不保证高阶导数估计误差较小；§4.4、PDF p.6给出其模型与数据上的直接学习/自动微分比较。这支持上述限制，但其完整矩阵/对角估计实验不能直接用于判定本项目单探针迹估计的准确率或速度。[Cai v2](https://arxiv.org/html/2506.00581v2) §IV-C式(52)后也讨论一阶误差对二阶学习的影响；不能把其理想目标与文中有界误差讨论写成有限训练网络必然准确。

实现另外引入有限步长和有限随机方向数。即使采用自动微分消除有限差分误差，式(24)中的学习导数误差仍然存在；增加方向数也只改进迹估计，不能自动纠正 Dθ 本身的导数。Cai §V-B1则明确说明 AWGN 查询依据依赖大系统及右旋转不变随机观测矩阵，有限维时可能失配并使用阻尼。其论述不能提供本项目 AFDM 接收机的无条件收敛保证；导数路线也没有这样的保证。

因此本项目能严格陈述的是：使用有明确 Gaussian 恒等式依据的导数方差近似，并验证其数值计算和实际闭环表现。已有较少迭代或较低耗时不证明后验方差更准确；已有解析测试及同方向自动微分核对也不能证明一阶网络导数接近真实条件均值导数。后续论证应分开报告导数数值误差、方向/步长敏感性、原始负读出与下界触发，以及独立场景中的 AER、NMSE、收敛和完整耗时。本节为理论边界核查，未新增实验或训练。

### 12.6 由预训练一阶网络计算方差的直接文献先例

2026-10-25针对“是否有已有论文实际采用”核查原文。除了Dytso的恒等式和D-AMP的随机散度计算，以下三项分别提供去噪不确定性、预训练score逆问题求解、消息传递精度更新的直接先例。阅读范围限于所列章节，不称为系统综述或整篇全文审查。

| 论文与版本 | 核验到的操作及原文位置 | 与本项目的对应及区别 |
|---|---|---|
| Hila Manor、Tomer Michaeli，*On the Posterior Distribution in Denoising: Application to Uncertainty Quantification*，ICLR 2024，[arXiv v2原文](https://arxiv.org/html/2309.13598v2)，[作者项目页及会议信息](https://hilamanor.github.io/GaussianDenoisingPosterior/) | §3.2 Theorem 2式(10)–(11)：后验协方差为σ²乘条件均值Jacobian；§4.1式(15)、Algorithm 1：对预训练去噪器作输入扰动，以单侧前向差分近似Jacobian–向量乘积，计算后验协方差的主要特征向量/特征值；Appendix H比较差分与自动微分。 | 实际使用预训练去噪器且无需独立二阶训练，与本项目从完整Dθ获取二阶统计量直接相关。论文主要计算后验主成分及方向分布；本项目计算协方差迹，使用随机符号中央差分。其DDPM去噪器实验将网络作为单个噪声等级的去噪器使用，不能描述成完整扩散采样接收机。 |
| Benjamin Boys等，*Tweedie Moment Projected Diffusions for Inverse Problems*，TMLR 2024，[arXiv v3原文](https://arxiv.org/html/2310.06721v3) | §3.1 Proposition 1式(5)–(6)：用一阶score得到m，再以C_(0|t)=(v_t/√α_t)J_m得到协方差；§3.2–3.3将其用于逆问题的条件采样；§3.4及Appendix E.1说明图像实验用Jacobian行和近似其对角，借助一次向量–Jacobian乘积降低成本。 | 提供“预训练score→均值及其导数→协方差→后续推断”的实际先例。本文估计的是去噪条件分布p(x0|xt)的矩，并用于近似观测似然；不是我们的JADCE反馈。行和近似不等于随机迹估计，其采样理论也不能直接用于本项目收敛。 |
| Saurav K. Shastri等，*Denoising Generalized Expectation-Consistent Approximation for MR Image Recovery*，[arXiv:2206.05049v2，2022](https://arxiv.org/pdf/2206.05049v2)；本地已存[PDF](../../../reference/literature/shastri2022_dgec.pdf) | §II-D Algorithm 1 line 10、PDF p.8：η2=γ2N/tr(J_f2)；§III-A式(31)、(33)、Algorithms 2–3，PDF pp.13–14：按组平均Jacobian对角，使用随机Gaussian方向及单侧差分计算迹，再形成后验/外信息精度；DNN用于去噪。 | 是与接收机消息更新最贴近的先例。其标量形式1/η2=(1/γ2)tr(J_f2)/N就是输入方差乘平均散度；精确MMSE均值下对应平均后验方差。DNN近似下不能自动称精确后验协方差；论文为MRI小波分组接口，本项目保留标量C=vI及自己的活动混合。 |

这里“由一阶score计算方差”具体指对输入求导：实坐标AWGN条件下Dθ(y)=y+σ²sθ(y)，故σ²J_D=σ²I+σ⁴J_s。仅复用同一套一阶网络的权重，仍需要输入导数或有限差分；并不是只用一个输入点处的score数值。上述网络输出一般是近似score/条件均值，因此实际协方差读出继续保留第12.5节的误差边界。

对论文的引用分工建议：Dytso支持一般协方差恒等式；Manor–Michaeli支持只用预训练去噪器及前向差分提取后验二阶信息；Boys等支持预训练score的导数协方差进入推断；D-GEC支持由Jacobian迹更新消息精度。不能把“对一阶网络求导得到方差”本身作为本项目新创方法，也不能把这四篇的不同实现混写成某一篇已提出本项目全部步骤。此次只更新文献记录，未更改算法或启动实验。

用户随后要求下载上述三篇全文，已统一保存于 `reference/reviews/derivative_variance_review_20261025/`：[Manor–Michaeli，31页](../../../reference/literature/manor_michaeli_2024_posterior.pdf)、[Boys等TMPD，45页](../../../reference/literature/boys_2024_tmpd.pdf)、[Shastri等D-GEC，40页](../../../reference/literature/shastri2022_dgec.pdf)。前两篇从固定版本arXiv地址新下载，D-GEC复用原文库并保持原文件不变。全部核对首页题名、作者及arXiv版本，逐页解析并提取分页文本；来源、字节数与SHA-256记录在[下载清单](../../../reference/reviews/derivative_variance_review_20261025/DOWNLOAD_MANIFEST.json)。文件可读性验证不等于已经审阅全文所有证明。

## 13. 当前标量查询方差修正的数学核查（2026-10-25）

核查对象为独立候选 `src/algorithm/C_STMP_variance_em_20261025/`，以及场景0–49、8档SNR的400份已保存结果。本文只验证其数学操作与实现，不更改接收机、权重、门限、阻尼或冻结结果，不新增推断和训练。原完整1000场景实验不因此恢复。

**结论：给定本轮查询和采用的近似后验矩，方差目标具有精确的期望残差恒等式及标量Gaussian目标最优性，比例参数阻尼保证同一轮固定条件下该目标不下降；没有证明完整神经网络接收机具有统一的全局EM/EC目标或全局收敛性。** 以下将项目直接推导与文献结论分别注明。

### 13.1 工作模型与固定条件

令有效信道为 \(g_k=a_k h_k\)，查询张量为 \(r\in\mathbb C^{K\times M\times N_{out}\times N_{in}}\)。设 \(L=N_{out}N_{in}\)、每用户复维度 \(n=ML\)、总复维度 \(D=Kn\)。本节的 \(D\) 表示维度，不是去噪网络。所有量使用接收机内部相同的幅度归一化。

考虑辅助查询模型

\[
p(r\mid g;v)=(\pi v)^{-D}\exp[-\|r-g\|_F^2/v],\qquad v>0.
\tag{29}
\]

它是标量 \(C=vI\) 的Gaussian工作模型，并非对物理观测 \(y\) 的精确似然声明。一个局部方差更新中固定 \(r_t\) 及近似分布 \(q_t(g)\)，记其矩为 \(m_t=\mathbb E_{q_t}g\)、\(P_t=\operatorname{Cov}_{q_t}(g)\)。求 \(v\) 的导数时，不再对网络均值、活动概率或协方差关于 \(v\) 求导；这正是固定分布后优化期望对数似然的含义。

### 13.2 复数期望残差与最优方差

对任意具有有限二阶矩的 \(q_t\)，展开 \(r-g=(r-m)+(m-g)\)，交叉项的期望为零，故

\[
S_t=\frac1D\mathbb E_{q_t}\|r_t-g\|_F^2
=\frac{\|r_t-m_t\|_F^2+\operatorname{tr}P_t}{D}.
\tag{30}
\]

式(30)不要求 \(q_t\) 本身为Gaussian或proper复分布。式(29)采用proper各向同性噪声；它对实、虚部各给出方差 \(v/2\)，实坐标似然与上述复坐标似然完全相同，不额外乘除2。

固定 \(r_t,q_t\) 时，

\[
Q_t(v)=\mathbb E_{q_t}\log p(r_t\mid g;v)
=\mathrm{const}-D\log v-\frac{D S_t}{v},\qquad
Q'_t(v)=\frac{D(S_t-v)}{v^2}.
\tag{31}
\]

当 \(S_t>0\) 时，\(Q_t\) 在 \((0,S_t)\) 严格增加、在 \((S_t,\infty)\) 严格减少，唯一全局最大值为 \(v=S_t\)。这里“全局”只指这个一维、固定条件的子问题。若 \(S_t=0\)，最大值退到方差零的边界，不能声明存在正的有限最优解；实现明确拒绝非正或非有限目标，本次保存轨迹全部为正。

[Vila–Schniter，IEEE TSP 2013](https://phil-schniter.web.app/pdf/tsp13_emgm.pdf) §III-A、式(22)–(27)、印刷p.4661给出物理Gaussian噪声方差的EM更新，式(27)同样由残差平方与后验方差组成。本文式(29)–(31)是把相同计算用于复数辅助查询模型的直接推导；不能把查询方差称为其原文的物理噪声方差，也不能把后续比例参数更新归为原文已有算法。

### 13.3 必须使用活动与信道的联合矩

对采用的活动概率 \(p_k\)，可定义合法的近似混合分布

\[
q_k(g_k)=(1-p_k)\delta_0(g_k)+p_k q_{k,active}(g_k),
\quad m_k=p_k\mu_k,
\quad P_k=p_k P_{k,active}+p_k(1-p_k)\mu_k\mu_k^H.
\tag{32}
\]

只要 \(0\le p_k\le1\)、条件协方差半正定，该分布及矩成立；例如取具有所用矩的Gaussian条件分布即可。这不证明网络均值、导数方差和分类器来自同一个固定先验的真实后验。

实现存储的空间协方差为 \(C_k=L^{-1}\sum_{\ell=1}^L\operatorname{Cov}_{q_t}(g_{k,:,\ell})\)，因此

\[
\operatorname{tr}P_t=L\sum_{k=1}^K\operatorname{tr}C_k,
\qquad S_t=\operatorname{mean}|r_t-m_t|^2+
\frac1{KM}\sum_{k=1}^K\operatorname{tr}C_k.
\tag{33}
\]

跨列或跨用户协方差不贡献总协方差的迹，所以无需存储完整 \(D\times D\) 矩阵即可计算所采用分布的此项。等价地，

\[
S_t=\frac1D\sum_k\left[(1-p_k)\|r_k\|^2+
p_k\left(\|r_k-\mu_k\|^2+\operatorname{tr}P_{k,active}\right)\right].
\tag{34}
\]

式(33)与式(34)代数相同。遗漏 \(p_k(1-p_k)\mu_k\mu_k^H\)，或将活跃条件方差直接当作联合方差，会破坏这个等价关系。代码 `expected_residual_power` 采用的是包含此项的 `state.spatial_covariance`。它估计工作模型下的残差二阶矩；若查询误差存在偏置，该量可吸收偏置能量，不能自动解释为去除偏置后的物理噪声协方差。

### 13.4 比例参数阻尼能保证什么

令 \(b_t>0\) 为保留原始线性阻尼历史所得的标量方差，\(a_t>0\) 为修正比例。实际条件为 \(v_t=a_tb_t\)。代码更新

\[
a_{t+1}=(1-\beta)a_t+\beta S_t/b_t,\qquad \beta=0.4.
\tag{35}
\]

在本轮相同 \(b_t\) 下，定义仅用于分析的方差

\[
\widetilde v_{t+1}=b_ta_{t+1}=(1-\beta)v_t+\beta S_t.
\tag{36}
\]

对 \(0<\beta\le1\)，它位于 \(v_t\) 与 \(S_t\) 之间，并保持正值。由式(31)两侧导数的符号，严格得到 \(Q_t(\widetilde v_{t+1})\ge Q_t(v_t)\)。本结论不需要把 \(Q_t\) 错称为关于 \(v\) 全局凹函数。

**下一轮实际使用的方差不是式(36)，而是**

\[
v_{t+1}=b_{t+1}a_{t+1}
=\frac{b_{t+1}}{b_t}\widetilde v_{t+1}.
\tag{37}
\]

此外 \(r_{t+1}\) 和 \(q_{t+1}\) 也改变，所以局部不下降不推出全程似然不下降。例如数学反例 \(Q(v)=-\log v-2/v\)、\(v_t=b_t=a_t=1\)、\(\beta=0.4\) 给出 \(\widetilde v=1.4\) 且 \(Q(1.4)>Q(1)\)；若下一轮 \(b_{t+1}=10\)，则实际 \(v_{t+1}=14\)，此时 \(Q(14)<Q(1)\)。这只是说明推理边界，不表示实测接收机发生了全局目标下降。

若各量达到共同稳定点，且 \(b_*>0\)、\(\beta>0\)，式(35)给出 \(v_*=a_*b_*=S_*\)，即局部方差目标的一阶驻点。停止检查 \(\delta=|S-v|/\max(S,v)<\epsilon\) 蕴含 \(|D^{-1}\partial Q/\partial\log v|=|S/v-1|<\epsilon/(1-\epsilon)\)，当前 \(\epsilon=0.0005\)。这是局部残差控制，不是全局收敛证明。

[Fletcher等，NIPS 2017](https://proceedings.neurips.cc/paper_files/paper/2017/file/4e8412ad48562e3c9934f45c3e144d48-Paper.pdf) §4、Definition 1、Theorem 2的variance auto-tuning有大系统、观测矩阵及可辨识性条件；本项目未验证这些条件。[Fletcher–Schniter，Learning and Free Energies for Vector Approximate Message Passing，v4](https://arxiv.org/html/1602.08207v4) §III给出其算法固定点的变分刻画，§IV开头仍明确不保证算法达到固定点。两者均不提供当前候选的整体收敛定理。

### 13.5 Gaussian外信息与神经网络近似的边界

对实际采用的Gaussian协方差 \(P_{used}\)，除去输入Gaussian消息的自然参数公式为

\[
V_e^{-1}=P_{used}^{-1}-(vI)^{-1},\qquad
V_e^{-1}r_e=P_{used}^{-1}m-(vI)^{-1}r.
\tag{38}
\]

当右侧精度正定时，这是两个Gaussian密度之商的精确公式。当前代码先将空间协方差跨用户平均并取各向同性近似，再把相对查询协方差的特征值限制在 \([10^{-6},1-10^{-6}]\)。因此式(38)对应**投影、裁剪后实际采用的协方差**，不等于对未经处理的真实联合后验作精确相除。随后的均值、协方差阻尼也不能直接称为某一全局自由能的坐标最优化。

每轮均值网络、固定条件导数、分类器及外信息减法共享 \(v_t\)，消除了这些模块使用不同有效方差造成的接口不一致。然而它不证明共同先验下的后验一致性，也不把真实查询误差变成Gaussian。导数方差继续有有限网络误差、单个随机方向和有限差分误差；固定方向经反馈复用，不保证闭环无偏。负或过小的条件方差读出存在既有下界处理，不应隐藏为精确协方差。既有不支持查询分支沿用Gaussian site，也不等于每轮都产生新的网络后验。

### 13.6 代码、保存轨迹与证据

本次新增独立数学测试 `src/tests/test_c_stmp_variance_math_audit_20261025.py`，与已有活动混合测试共同执行：

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q src/tests/test_c_stmp_variance_em_20261025.py src/tests/test_c_stmp_variance_math_audit_20261025.py
```

结果为 **8 passed in 2.10s**，包括复/实坐标一致性、独立数值优化、维数及尺度换算、精确Gaussian先验特例、活动混合恒等式、投影后的Gaussian自然参数相除，以及同轮阻尼上升与跨轮线性尺度变化反例。精确Gaussian特例的真实边缘似然不下降不能外推为神经接收机的保证。

对既有结果执行独立只读脚本 [verify.py](../../../result/snr_comparison/data/c_stmp_variance_math_audit_20261025/verify.py)，保存 [SUMMARY.json](../../../result/snr_comparison/data/c_stmp_variance_math_audit_20261025/SUMMARY.json) 及输入哈希清单：

| 检查 | 结果 |
|---|---|
| 全部输入、迭代及受保护资产 | 400份输入、27,605次迭代；816个受保护资产哈希不变 |
| 同轮共享方差、比例更新 | 保存量相对公式的最大相对差均为0 |
| 目标能量分解 | 最大相对差 \(1.11\times10^{-16}\) 以下 |
| 同轮固定 \(Q_t\) 的阻尼更新 | 超出舍入容差的不下降违例为0 |
| 最终活动混合均值、协方差 | 最大相对差分别 \(4.21\times10^{-17}\)、\(1.50\times10^{-16}\) |
| 最终方差固定点残差 | 最大 \(3.7661\times10^{-4}\)，小于原 \(5\times10^{-4}\) 容差 |

完整审计也保留近似行为：641次迭代触发外信息协方差投影，9,092次触发条件方差下界，8次走既有不支持查询分支；这些不是新修改或被删除的样本，400份最终输出均为支持查询。相邻27,205对迭代中，有2,178对将实际下一轮方差代入上一轮固定 \(Q_t\) 后低于旧值。这不是全局似然下降的度量，但直接说明不能把式(36)的局部结论扩展到式(37)的跨轮值。

文献阅读限于上述定位章节。Vila–Schniter原文已保存至 `reference/reviews/c_stmp_variance_math_audit_20261025/`，人工查看渲染的印刷p.4661并核对式(22)–(27)。PDF预检因对象偏移警告返回UNAVAILABLE；不把它记为结构完整性PASS。页码和公式由实际页面渲染与作者公开原文交叉确认，来源与哈希另存核查目录。

### 13.7 性能结论与论文表述

这50场景为回顾性配对验证，包含此前定位问题的开发场景，不是独立盲测集。400份输入均保留；误检由5降为0，漏检由7增为9，总错误12降为9；平均迭代数62.3125升为69.0125。2、4 dB的AER回升在本组结果中消失，但不能由式(30)推出AER随SNR必定单调，也不能仅由这组改善证明网络后验正确。

统计解释核查覆盖11项：分层异质性（保留−2、0 dB新增漏检）、群体到个体推断（不声称逐场景都改善）、选择偏差（开发场景重叠）、调整/碰撞变量偏差（本次无此调整，不适用）、基率（同时报告漏检和虚警）、外部有效性（不外推未知场景）、缺失与幸存偏差（400份全保留）、显著性/多重比较（无显著性声明，报告全部8档）、选择性分析（保留旧候选和冻结计划）、因果解释（配对程序变化不能证明总体理论性质）、观察性因果混淆（无此因果主张，不适用）。覆盖11/11，不据小样本消除全部不确定性。

建议论文使用如下限定准确的表述：

> 在标量Gaussian查询近似下，由活动与信道的联合后验矩计算期望残差能量，得到固定查询与近似后验时的有效方差最优值。接收机对其相对于线性模块方差的比例作阻尼更新，并让均值、导数方差、活动概率及外信息减法共享更新后的方差参数。该步骤具有固定条件下的局部目标不下降性质；完整接收机仍采用学习后验与Gaussian消息近似，其收敛与检测性能通过配对实验评估。

核查状态：**ANALYZED**（理论适用性与边界）；上述8项解析数值检查及保存轨迹中的代数关系为 **VERIFIED**。核查来源仅为实际候选代码、冻结配置、已保存原生结果及所列论文；未使用模拟接收结果替代实测，也未新增训练或推断。详细范围及产物哈希见本次核查目录的完成凭据。
