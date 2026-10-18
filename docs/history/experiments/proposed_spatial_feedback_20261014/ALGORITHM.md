# 由观测初始化空间协方差与逐用户矩阵反馈试验

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent。
- Origin Mode: run + deterministic validation。
- Origin Date: 2026-10-14。
- Scope: 用户授权的接收机修改试验；三个旧网络冻结，主线源码与配置保持原样。
- Verification Status: 矩阵实现已通过独立稠密Gaussian参考核对；接收机结果以结果目录为准。

本文件说明实际实现，具体运行计划与源码哈希在每次运行前写入 `results/proposed_spatial_feedback_20261014/<stage>/PLAN.json`。以下操作是本项目候选组合，不命名为文献中已有算法，也不声称实现了独立AWGN等价模型。

## 1. 从公开观测构造初始空间矩阵

所有公式在原接收机的归一化复坐标中计算。令Q为导频帧数、M为天线数、R为AFDM输出维数，定义

\[
S_y=\frac1{QR}\sum_{q,r}y_{qr}y_{qr}^H,\qquad
g=\|A\|_F^2/Q,\qquad
S_0=\frac1g\operatorname{PSD}(S_y-\sigma^2I).
\]

PSD操作将负特征值置零。取 \(s=\max(\operatorname{tr}(S_0)/M,10^{-3}\gamma_0)\)，初始矩阵为

\[
C_0=0.9S_0+0.1sI.
\]

\(\gamma_0\) 是原算法的公开活动先验乘训练二阶矩。全部用户初始均值仍为零。10%标量混合与功率下限是预先固定的项目设置，未用这些场景的真值选择。混合形式参考 covariance shrinkage：Chen等《Shrinkage Algorithms for MMSE Covariance Estimation》§II式(3)–(4)、作者稿p.4，https://arxiv.org/pdf/0907.4698 。这里没有采用该文OAS/RBLW系数估计，也不满足其独立Gaussian快拍假设。

此矩阵是接收观测形成的初始化近似，不是精确条件信道协方差。有限导频交叉项、未知活跃集合以及样本相关都会影响它。噪声方差、A、Y和公开活动先验来自四字段ReceiverInput；本模块不读真值、方向、实际活跃人数或路径参数。

## 2. 两个候选的差别

- `spatial_start`：首轮用上述C0替代原标量初始化，采用原共同空间LMMSE，并执行第4节的加噪处理。之后完全回到原共同标量反馈与原三网络；加噪只执行一次，其影响随原查询阻尼历史逐步衰减。
- `spatial_feedback`：每轮保留各用户16×16协方差，按第3节进行线性更新，按第4节处理查询，再由每用户Gaussian外信息更新反馈矩阵。保留每用户二阶读数，不跨用户平均。使用已有PerUserDenoiser适配器批量查询同一组旧权重。

两个版本均保留原最少60轮、收敛阈值、判决门限和连续稳定窗口。首轮检查只运行1轮；完整开发筛选中三种方法统一用新值权重0.2、最多200轮。达到上限不算收敛，更不更改阈值宣称成功。

## 3. 逐用户空间Gaussian线性更新

对一个AFDM输出索引，令 \(B_k=A_k\otimes I_M\)，将用户k的变量按AFDM输入索引、天线排列。输入工作先验为

\[
x_k\sim\mathcal{CN}(\mu_k,I_P\otimes C_k),\qquad
S=\sigma^2I_{QM}+\sum_k(A_kA_k^H)\otimes C_k.
\]

在这个Gaussian模型内，均值更新精确为

\[
\mu_k^{\mathrm{post}}=\mu_k+(I_P\otimes C_k)B_k^HS^{-1}\left(y-\sum_jB_j\mu_j\right).
\]

这包含所有用户均值的软抵消，且通过各用户Cj在S中的贡献保留其空间不确定性；没有把某个已检出用户当作准确已知。

将精确后验协方差的每个输入索引对应M×M对角块取平均：

\[
T_k=\frac1P\sum_n(a_{kn}\otimes I)^HS^{-1}(a_{kn}\otimes I),\qquad
C_k^{\mathrm{post}}=C_k-C_kT_kC_k.
\]

对角块平均是保留矩阵消息形状的投影，丢弃输入索引间及用户间后验相关；“Gaussian更新精确”只适用于投影之前的工作模型。随后作Gaussian相除：

\[
V_k=\big[(C_k^{\mathrm{post}})^{-1}-C_k^{-1}\big]^{-1},\qquad
r_k=V_k\big[(C_k^{\mathrm{post}})^{-1}\mu_k^{\mathrm{post}}-C_k^{-1}\mu_k\big].
\]

Gaussian投影/外信息相除沿用项目THEORY T3–T5、T13–T17与Cai §III的定义；这里逐用户矩阵推广与块平均为项目直接推导。实现只分解256×256观测协方差，不形成10240×10240全变量矩阵。独立小维稠密模型核对均值最大绝对误差为1.27×10⁻¹⁵、协方差为4.75×10⁻¹⁶；另验证各向同性矩阵时退化到已有逐用户标量线性更新。

## 4. 保留原信道坐标的查询处理

对V的特征值 \(\lambda_i\)，若最大值处于旧网络支持范围，选 \(t=\lambda_{\max}\)，补加协方差

\[
\Delta=U\operatorname{diag}\{\max(t-\lambda_i,0)\}U^H,\qquad
r'=r+\Delta^{1/2}z,\quad z\sim\mathcal{CN}(0,I).
\]

旧网络仍估计原H坐标。给定V，额外扰动协方差的代数关系精确；V是否等于真实误差协方差依然是统计近似。

若完整补齐将超过网络上限，则选择t使 \(\operatorname{mean}_i\max(t,\lambda_i)\) 不超过支持上限的95%，仅抬升较小特征值。给网络的标签是补加之后矩阵的真实平均特征值，没有将超范围方差直接截断为可接受标签。若原平均值本已超限，则不再加噪，保留实际超限标签并使用原site回退规则。未完全补齐的用户数显式写入轨迹。

每次完整运行只生成一份固定z，矩阵版本每轮随Delta调整它，不累计叠加到上轮查询；这样避免新随机样本本身阻止数值停止。固定样本会与后续反馈有关，本方法不具有“每轮新增误差独立”的保证。噪声种子、功率增加及超范围次数均记录；如果通过四条件质量筛选，还须用另外两个固定种子核查。

## 5. 非线性输出与矩阵反馈

旧网络及活动分类器使用同一当前查询、同一标量方差标签。原条件均值、条件方差和活动混合产生用户联合均值与空间协方差。矩阵版本将这些协方差保留为M×M矩阵，在标量查询协方差 \(v_kI\) 下作Gaussian相除。后验与查询的特征值比例沿用原上下界 \([10^{-6},1-10^{-6}]\)，所有被裁剪方向计数保留。

原网络误差、Gaussian消息投影、忽略跨用户相关、观测驱动初始化及补加噪声都可能影响结果。增加空间矩阵不自动使方差正确；首轮改善不自动推出后续NMSE和检测改善。本轮用相同输入、相同阻尼的完整迭代对照判断，保留所有不利结果。
