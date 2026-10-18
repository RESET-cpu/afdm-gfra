# AMP 中的查询阻尼与完整历史校正

2026-10-15。`score_amp_query_damped` 是独立软件入口。原 Proposed、原 AMP、
仅输出阻尼的 AMP 均保留。继承 [归一化及复矩阵约定](PROPOSED_AMP.md) 和
[输出阻尼推导](PROPOSED_AMP_DAMPING.md)。本次只借鉴原 Proposed 的查询阻尼，
没有把 Gaussian 外信息和 AMP 校正重复叠加，也没有将二阶网络读数当成联合映射的导数。

## 1. 定义与初值

沿用 Y=AX+W，A∈C^{Q×L}、X∈C^{L×C}；当前 Q=16、L=640、C=256。
令 α、β∈(0,1] 分别为查询、输出的新值权重。X⁰=0，Z⁰=Y，H⁰=0。
基础查询与混合查询分别为

\[
U^t=X^t+A^HZ^t,\qquad
R^0=U^0,\quad R^t=(1-\alpha)R^{t-1}+\alpha U^t\quad(t\ge1).
\tag{Q1}
\]

首轮直接采用 U⁰，不能从零开始对首轮乘 α。记

\[
c_{t,0}=(1-\alpha)^t,\quad
c_{t,s}=\alpha(1-\alpha)^{t-s}\ (1\le s\le t),
\quad R^t=\sum_{s=0}^tc_{t,s}U^s,\quad\sum_sc_{t,s}=1.
\tag{Q2}
\]

完整联合去噪器仍是 dᵗ=D(Rᵗ;vₜ)=pφ(Rᵗ,vₜ,Fθ)Fθ(Rᵗ,vₜ)，
活动先验修正及三个冻结文件的绑定不变；本候选只执行一阶网络和分类器。

## 2. 同步混合残差及方差接口

定义与查询具有相同权重的残差

\[
\bar Z^0=Z^0,\qquad
\bar Z^t=(1-\alpha)\bar Z^{t-1}+\alpha Z^t
=\sum_{s=0}^tc_{t,s}Z^s,\qquad
v_t=\frac{\|\bar Z^t\|_F^2}{QC}.
\tag{Q3}
\]

这是混合残差的**精确能量**。其作为查询噪声标签的解释需要额外的联合状态演化条件：
若各基础查询误差 Uˢ−X 的跨轮协方差由对应残差交叉乘积估计，Q2 的权重和为1，
则混合查询误差的协方差使用同一权重二次型。有限 AFDM 下没有证明这些条件成立，
因此不能将 Q3 直接称为真实查询 MSE 或 AWGN 证明；实验必须另行评分校准与相关性。

Q3 明确保留交叉项：

\[
v_t=(1-\alpha)^2v_{t-1}+\alpha^2\frac{\|Z^t\|_F^2}{QC}
+\frac{2\alpha(1-\alpha)}{QC}\Re\langle\bar Z^{t-1},Z^t\rangle.
\tag{Q4}
\]

不能把两个标量方差直接算术平均。本实现先混合数组再算方差，保存未混合残差功率，
不裁剪标签。经验 vₜ 对观测的总导数不纳入下式；采用的是给定历史标签的条件偏导，
不是对整个自适应程序的总导数。

## 3. 从完整历史偏导推导校正项

输出阻尼为

\[
X^{t+1}=(1-\beta)X^t+\beta d^t
=\sum_{\ell=0}^t w_{t,\ell}D(R^\ell;v_\ell),\qquad
w_{t,\ell}=\beta(1-\beta)^{t-\ell}.
\tag{Q5}
\]

将 U⁰,…,Uᵗ 当作独立历史输入、冻结每轮标签，链式法则给出

\[
\frac{\partial X^{t+1}_{ib}}{\partial U^s_{ja}}
=\sum_{\ell=s}^t w_{t,\ell}c_{\ell,s}
\frac{\partial D(R^\ell;v_\ell)_{ib}}{\partial R^\ell_{ja}}.
\tag{Q6}
\]

这是包含查询记忆和输出记忆的偏导。令完整联合映射的 Wirtinger 部分迹为

\[
B^\ell_{ab}=\frac1Q\sum_i
\frac{\partial D(R^\ell;v_\ell)_{ib}}{\partial R^\ell_{ia}}.
\tag{Q7}
\]

按历史 AMP 的残差—历史偏导配对形式，校正为

\[
H^{t+1}=\sum_{s=0}^t Z^s\sum_{\ell=s}^t w_{t,\ell}c_{\ell,s}B^\ell
=\sum_{\ell=0}^t w_{t,\ell}\bar Z^\ell B^\ell.
\tag{Q8}
\]

交换有限和后得到无需保存全部历史的递推：

\[
\boxed{H^{t+1}=(1-\beta)H^t+\beta\bar Z^tB^t},\qquad
Z^{t+1}=Y-AX^{t+1}+H^{t+1}.
\tag{Q9}
\]

等价实现为 Zᵗ⁺¹=(1−β)Zᵗ+β[Y−Adᵗ+Z̄ᵗBᵗ]。
不能继续用 ZᵗBᵗ 替代 Z̄ᵗBᵗ；也不能把 Bᵗ 再乘 α，查询权重已在 Z̄ᵗ 中。
四次中心差分对整个 pF 映射求导，包含分类器经 F 的依赖。默认8探针与原种子保持一致。

## 4. 依据、退化与理论边界

历史偏导形式参照 [Fan作者稿v5](https://arxiv.org/html/2008.11892v5#S5)，
§5式(5.3)–(5.8)、(5.12)、Remark 5.1；复数非可分矩阵部分迹参照
[Kunde等v1](https://arxiv.org/html/2604.21115v1#S3.SS3)，§III-C式(18)–(21)、
Remark 14、Appendix B。Q1–Q9 是本项目在明确缩放下的推导，不是原文已有算法名称。
完整历史可用固定有限轮数的额外特征列表示，参照
[OpAMP作者稿v2](https://arxiv.org/html/2405.08225v2#A1)，Appendix A Theorem 5与A.2.1。
这些随机矩阵定理没有为当前有限 AFDM、经验标签或有限探针给出保证。

查询与反馈两侧阻尼的经验动机来自原 Proposed，以及
[Cai等v2](https://arxiv.org/html/2506.00581v2#S5.SS2.SSS1)，§V-B1式(57)–(58)。
原算法的 LMMSE/外信息与二阶矩传播并未一并移植，Q3也不是原方差阻尼公式。
本次把“查询阻尼是否足够改善新 AMP”隔离为可识别的一项消融。

- α=1：所有有限轮数数组严格退化为已有输出阻尼 AMP；α=β=1退化为原 AMP。
- 首轮：所有 α 的查询、标签、去噪、概率、B、输出与残差均相同。
- 关闭校正：H始终为0，Z=Y−AX；仍保留查询和输出阻尼。
- 对确定性精确导数映射，正 α、β 下固定点有 R=U、Z̄=Z、X=D、H=ZB，
  与原 AMP 固定点一致；这不保证稳定。增广状态包含两个查询记忆，不能沿用
  单个输出阻尼的简单特征值变换。实际每轮新抽探针也不构成确定性映射。

## 5. 实验与使用

冻结设计见[协议](history/experiments/proposed_amp_revision_20261015/PROTOCOL.md)。
先补 β=.02、α=1，再与 α=.2 下 β=.2/.02 配对。100轮为计算预算，
不以阻尼后小变化声称收敛；保存未阻尼缺陷、实际混合查询和残差能量。
真值只在全部新预测完成后评分，失败照常保留。每个有效校正轮仍需33次一阶网络
及33次分类器；新增查询记忆不增加网络调用。

```sh
.venv/bin/python scripts/run_proposed_amp_query_damped.py --input CASE/input.npz --output NEW/estimate.npz
```

输出为物理尺度的阻尼状态，原始去噪输出另存；活动概率采用当前原始分类器。
支持 `--query-damping`、`--damping`、`--iterations` 和 `--without-onsager`。
所有输出须使用新路径；失败也保存记录，退出码2。
