# 公式定位补充

2026-10-15，运行期间核对 [Cai v2 全文](https://arxiv.org/html/2506.00581v2)：

- §III 开头明确结合 sum-product rule 与 EP algorithm；不存在“在 TMP 中使用 EP 就必然另起框架”的依据。
- §III-A 式(7)–(11)：Gaussian 条件更新之后再用共同标量近似协方差。
- §III-B 式(23)、(38)：分别为条件信道和活动混合矩后的方差平均。
- §IV 式(43)–(54)：score 与矩的关系及训练目标。
- **式(56) 位于 §V-A，而非冻结 PLAN.md 所写的 §IV。** 仅修正引文节号，
  保留原冻结设计及其哈希；公式、候选、数据、运行或评价规则均无变化。
- §V-B1：实际等效噪声的 Gaussian 近似具有条件，阻尼用于改善数值稳定性。

逐用户风险读数先乘活动概率再平均的公式来自项目 THEORY T16 的直接展开。
这是现有消息投影的具体修改，不给它添加新的论文方法名。

第二项补充：Fletcher等[Generalized Expectation Consistency for Approximate Inference](https://arxiv.org/pdf/1602.07795v2)，
§II-A式(8)–(9)的block uniform diagonalization及§II-B Algorithm 1，PDF pp.2–3，
支持按变量块保留不同标量精度/方差。项目每用户作为一个块；复数MMV线性查询、
Bernoulli混合矩及受限Gaussian外信息的具体公式见STEP2_PLAN.md。
原文不保证当前有限网络的二阶风险是精确协方差，也不保证本AFDM实际查询满足AWGN。

第三项补充：2026-10-15核对[Minka修订作者稿](https://tminka.github.io/papers/ep/minka-ep-uai.pdf)，
§3式(8)–(10)和算法3(b)–3(d)，PDF p.3，明确先相除旧因子，再组合及更新。
Cai v2 §III-A式(7)–(11)的标量投影、§III-B式(24)–(30)的外信息和活动证据是本地对应点。
第三项保留的单用户矩阵似然、Gaussian分量权重校准和一次末端更新为项目适配，
不归为Minka或Cai的已有完整算法；也不称为物理先验下的精确联合后验。

第四项补充：2026-10-15核对[Kschischang–Frey–Loeliger，Factor Graphs and the Sum-Product Algorithm](https://www.mit.edu/~6.454/www_fall_2002/lizhong/factorgraph.pdf)，
IEEE TIT 47(2)，2001，§II-C式(5)–(6)，p.502，给出局部乘积与对其他变量求和；
§VI-A，p.513，讨论clustering与复杂度。第四项保留两用户活动的四种组合，使用该求和规则；
没有宣称在有环全局图上精确，也未照搬其junction tree结构。
因子相除仍对应Minka上述§3，Cai的Gaussian投影及活动混合矩仍对应§III-A/B。
伙伴分数p_j(1−p_j)||A_iᴴCy⁻¹A_jμ_j||²、复MMV四状态条件矩和末端一次执行，
均为STEP4_PLAN.md中的项目推导，不命名为新的已有算法。

第五项补充：2026-10-15重新核对[Friel–Pettitt作者稿](https://www2.stat.duke.edu/~scs/Courses/Stat376/Papers/NormConstants/FrielPettitPath05.pdf)，
§3式(4)–(5)、§3.1式(6)，PDF pp.4–6，以及[Friel–Hurn–Wyse v2](https://arxiv.org/html/1209.3198v2#S2)，
§2式(6)–(11)。使用power posterior、thermodynamic integration、log Bayes factor等已有术语。
g'(β)=Var_β(u)≥0对应后一文式(11)。固定复数标量噪声、条件矩形式、最大方差100的起点项和
神经矩替代为项目推导；这些论文没有保证有限score在本项目路径上准确。
已有20261012推导和合成检查仍保留；20261015第五项是实际冻结网络的首次该路径比较，结果失败。

先验积分诊断依据[Elvira–Martino–Robert v2，Rethinking the Effective Sample Size](https://arxiv.org/pdf/1809.04129v2)，
§1式(1)、§2.2式(7)，PDF pp.2、4，及§3.2–3.3的适用性限制。
本项目(Σw)²/Σw²只标记权重集中，不等同于真正独立样本数或积分误差。
delta method定位为该文Appendix A式(43)–(46)，PDF pp.23–24；本项目对log均值使用其一阶方差传播，
并将同场景4个信道权重先平均，计算s_group/(sqrt(G) mean_group)。这是本项目分组代入，
不是文中已证明的有限样本置信区间，稀有事件漏采和先验失配不由该标准误覆盖。

原迭代消息审计补充：2026-10-15重新核对Cai v2 §III-A式(7)–(11)的先标量压缩、
再相除输入消息，以及§III-B式(37)–(42)的混合矩压缩与外信息。原代码已有这两个相除环节。
§V-B1明确pseudo AWGN具有大系统和右旋转不变矩阵条件，不能从LMMSE代数正确推出实际AWGN。

[Vehtari等，Expectation Propagation as a Way of Life，JMLR 2020](https://www.jmlr.org/papers/volume21/18-817/18-817.pdf)，
§2.1 p.6、§5.3 p.18、Appendix A p.32核对natural parameters、precision matrix和precision mean。
矩阵消息用(J,B)而非显式(J⁻¹B,J⁻¹)表达，复MMV具体形式见MATRIX_MESSAGE_DESIGN (M1)。
该表示不改变似然信息量，也不能证明网络已经适配。
Minka §2式(4)–(6)、§3式(8)–(10)支持矩匹配及因子相除；
共同标量输出精度的求根(M3)是项目受限拟合推导。
由于活动分布包含原子，使用期望负对数Gaussian密度目标，不误称一般有限KL最小化。

矩阵消息闭环适配补充：定义 B=JH+ξ，ξ~CN(0,J)，并以可逆变换
R0=(1+v)(I+J)⁻¹B、v=16/tr(J) 作为网络输入。此式及其标量退化是项目代数，
不将一般J下的残差回归称为原标量Tweedie score。
条件均值回归对应 Cai §III-B 的条件均值定义；与 Cai §IV-C式(50)–(54)相同，
有限均值网络下 E[||F−H||²|B,J,a=1]/D 包含中心方差和均值偏差平方。
本次直接最小化 E[log τ+||F−H||²/(Dτ)]，对τ求导得到该条件误差，
将其用于Gaussian工作方差而非宣称精确后验方差；正参数化本身也不保证校准。

活动证据采用 [Menon–Ong ICML2016](https://proceedings.mlr.press/v48/menon16.pdf)
§2.2、§3、§4.2式(6)–(8)、(16)–(17)，pp.305–306 的分类概率/密度比关系；
训练类别先验0.5时最优logit为log密度比，部署时加一次logit(ρ)。
有限分类器及真实迭代分布失配仍限制其解释。
均值、协方差算术阻尼依据Cai §V-B1式(57)–(58)；
PROTOCOL.md给出的自然参数计算严格实现相同插值，不是Gaussian混合分布的协方差。
实施、固定预算及验证选择见 [闭环协议](matrix_receiver/PROTOCOL.md)。
