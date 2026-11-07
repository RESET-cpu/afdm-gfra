# P09–P13 交叉复核

复核对象：当前 `sections/02_system_model.tex`，SHA256 `0afc16e78752ee18b28745542dc4f1a581eadab45ab8fb3658a28c27549bbbc2`，及 `c_patch.json`。仅核对来源措辞、条件保留和数式不变；未修改正文。

结论：P09–P12 未发现本次修改引入的阻碍；P13 有一处来源分句的条件范围需要最小收紧。不是模型或数值错误，也不需要恢复 `working posterior`。

## 需处理的一处：P13 尾从句的来源条件

当前组合把“消除高维积分计算”直接接到泛称的 deep generative priors 和消息计算之后。Cai PDF p.5（印刷 p.3579，§II-B，Table II 下）的实际原句是：

> This insight enables the integration of score-based generative networks for provable MMSE denoising, eliminating the need to compute high-dimensional integrals.

其中 This insight 回指左栏末句：将信道先验因子处的置信度计算解释为 AWGN 观测下的 MMSE 去噪。因此，`eliminating ...` 有具体的得分网络/MMSE 去噪依托。当前 P13 组合保留了结论，却没有保留这一具体连接；不能仅因三个分句各自都能在同一节找到，就认定其组合条件完全不变。

最短修正是只删除尾部结果从句，保留已可定位的两个主干分句，既不增加篇幅，也不新增对本稿实现的技术主张：

```text
old: , eliminating
     the need to compute high-dimensional integrals \cite{cai2026}.
new:  \cite{cai2026}.
```

修正后末句仍陈述以消息传递迭代近似求取本稿目标、以生成先验进行消息计算。若后续要保留“消除积分”结论，应在已有算法说明中连接到具体的得分网络/MMSE 去噪关系；本轮不建议额外增加解释段。

## 已核对且无需修改

| 对象 | 核对结果 |
|---|---|
| P09 活动指示与活动概率 | 与 Cai PDF p.4 §II-A 原句对应；仅符号和引用排版适配，二值支持集不变。 |
| P09 接收信号与 AWGN 从句 | Cai p.4 Eqs.(3)–(4) 的句式和 i.i.d. 原词已恢复；AFDM、双求和及本稿矩阵维度继续是本稿数学适配，未伪称源公式直接复用。 |
| P09 有效信道稀疏性 | Huang PDF p.3 §III-A、Eq.(6) 后的原分句可定位；无稀疏性假设的宾语仍为完整有效信道 H_k，后续 X 的设备活动块稀疏性未删除。 |
| P09 块稀疏性两句 | 与 Cai p.4 Eq.(4) 后连续原句对应；不活跃设备导致零块的含义保持。 |
| P10 目标句 | 与 Cai p.4 §II-B 首句对应，没有增加精度或最优性承诺。 |
| P11 | 估计量由 Y 获取、推断中将其视为给定、训练先验 q_tr，以及跨设备/活动与信道的独立性条件均完整保留。 |
| P12 的 q | `Under these assumptions` 仍承接 P11；随后公式继续使用已固定的估计量与 q_tr。将术语改为源文已有的 `joint posterior distribution` 没有把它改成对估计误差积分后的另一分布，无需补回无出处的名称。该完整 q 定义依然是本稿模型定义，不应归为 Cai 整句直接替换。 |
| 新术语 | `indicator function`、`i.i.d.`、`block-sparsity structure`、`Bayesian inference framework`、`joint posterior distribution`、`deep generative priors` 均能在对应原页定位；未见本次新造的方法名称。 |

## 机械核验及原页核对

- `c_patch.json` 九个 new 片段均在当前正文中恰好出现一次。
- 从 Problem Formulation 到章末的 6 个 equation 环境、1 个独立 `\[...\]` 显示式及 6 个标签，与 `before.tex` 逐字一致。
- 正文 `working posterior` 已不存在；内部 `eq:working-posterior` 标签按保持标签的要求保留，属于引用标识而非论文技术名称。
- 直接读取 Cai 正式版 clean.pages 的 PDF pp.4–5，并实际查看原页渲染 `c_cache/cai2026-04.png`、`c_cache/cai2026-05.png`；Huang p.3 原分句与此前实际查看的完整原页再次对照。未用同伴审查结论替代原文。

## 问题关闭记录

已对唯一指出的 P13 尾从句复查。当前正文 SHA256 为 `e109f5b96caad0665dbbc54df3356287623460bb279940607c9b19306f33c156`，与主审提供值一致。该句现仅保留消息传递近似求取目标以及以生成先验进行消息计算的两个来源分句；所指出的“消除高维积分”尾从句已删除，末句与建议的最小修正结果逐字一致。

**P13 来源条件范围问题已关闭。** 本次只复查这一处，没有重做整区审查、修改正文或提出其他措辞建议。
