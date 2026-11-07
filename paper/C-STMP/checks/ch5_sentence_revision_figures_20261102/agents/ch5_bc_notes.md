# 第五章 B/C 逐句核对记录

覆盖现有 V-B Parameter Estimation and Numerical Implementation 与 V-C Computational Complexity Analysis：11 个公式前后文字单元、36 个原句单元；修改 14 个，保留 22 个。公式引出从句也作为一个可核对单元。三处长句拆为两句，原句覆盖以逐句 JSON 为准。

## 已读规范与原文

- 已读 WRITING_GUIDE.md；核对 TERMINOLOGY.md 中 variable projection、MDL、Vila variance update、SVD、damping、固定训练RMS及本日修订条目。
- Cai v2：PDF pp.9–11，V-A/B/C；实际重读p.10阻尼、功率归一化及Algorithm 2，p.11完整复杂度段。
- Shen：PDF p.7 III-B给定参数说明；p.9 III-C参数学习及式(47)–(59)；p.10算法、阻尼及完整复杂度段。
- Ding：PDF p.5 III-D，式(29)及其前后运算分解。未把FLOP计数或GNN结构结论移入本稿。
- Huang：PDF p.4 Algorithm 1、Table II及网络评估次数的复杂度段。只参考终止条件和网络计次的表述，不移入Langevin算法。
- Wei：PDF pp.2–3 III-A/B/C/D。该文固定压缩矩阵、层参数校准和残差方差与本稿前端及kappa更新不同；本组没有为了覆盖作者而强行套用。
- O’Leary–Rust：既有全文缓存PDF pp.2、4，线性参数消去及变量投影；Nadakuditi–Edelman：pp.2–3，MDL回顾及尾部样本特征值；Vila–Schniter：PDF p.4/印刷p.4661，III-A式(22)–(27)。Vila缓存数学符号抽取不全，本轮不根据缺损文本改动公式。

## 修改重点

1. 从前端参数的确定进入后验计算，明确两项输出在消息传递期间固定。低秩空间信号加白噪声的前提保留；MDL选秩之后才做尾部均值。
2. 保留固定后验下的Gaussian目标推导。将“posterior mean的error”具体化为平均平方残差，并让当前v、kappa及damped MFLE variance的定义更容易连续阅读。
3. 以实际RMS定义引出归一化，保持本文固定训练尺度；阻尼直接说明当前与先前消息的组合，不增加数值正值性或收敛保证。
4. 复杂度保持一次性前端/SVD、每轮矩阵与网络、I轮总量、工作存储的顺序。分别给出前端代价和每设备网络成本，所有量级不变。

## 检验

- 七个陈列公式逐字相等。
- 行内数学规范化后的多重集完全相等。
- 四个原引用命令及其顺序完全相等。
- 36个逐句after均在候选正文中匹配。
- 固定近似后验、低秩加白噪声、eta/epsilon范围、首轮不阻尼、训练方差范围外分支、accepted site updates及最大迭代次数全部保留。
- 正式稿、PDF、README和术语文件未写入；父代理负责集成和编译。

未发现需改变算法的语义问题。来源账本区分文献技术来源、原段顺序、短表达和本文推导；没有将本文前端、全协方差SVD或工作存储量级登记成Cai等人的原式，也没有声称通过措辞改写获得查重保证。

输入片段SHA-256：`d96538c4ed71cf16dd89a97a61bd6829be77312671c8e6ab7e7a0872225b2f71`。
