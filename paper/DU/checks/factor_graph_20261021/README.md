# 后验因子图与消息推导补充

作者要求核对 Cai、Shen 是否从后验因子图出发组织推导，并补齐当前 TWC 稿件中这一步。
本轮修改第三章，新增 `figures/posterior_factor_graph.tex`；修改前版本保存在
`../../history/before_factor_graph_20261021/`。

## 原文核对

- Cai：正式版本 §II 式(5)，印刷第3578页；第3579页 Fig. 2、Table II；
  §III 首段及 §III-A 式(6)–(11)。先分解后验并给出因子图与因子定义，再按
  线性估计和用户级去噪两个模块推导 Gaussian belief 与 extrinsic message。
  本地原文为 `reference/literature/cai2026.pdf`，PDF 第4–5页。
- Shen：§III-A “Factor Graph Representation”，式(19)–(20)、Fig. 2，
  本地作者稿 `reference/literature/shen2025.pdf` 第6页。先引入变量与约束、
  分解联合后验，再将因子对应到不同模块，并用后续 Fig. 3 说明消息流动。

## 当前稿件的连接关系

1. III-A 定义观测似然、活动先验和约束因子，图中以用户的完整信道为变量节点。
   为便于展示，将所有观测似然归入同一 `f_y`；它仍可按观测列计算。
2. III-B 写出返回线性模块的 Gaussian 消息与该模块的 belief，由此接到原有
   均值、平均方差和消息相除公式。
3. III-C 将前向 Gaussian 消息按用户重排，经 `X_k=alpha_k H_k` 约束和
   先验积分得到原有活动/信道局部 belief，接到条件均值与活动概率。
4. III-D 明确 Gaussian 输出与前向消息的商，接回下一层的输入消息。
   输出方差仍由原残差与可学习映射构造；原有缩放、阻尼和训练方式保留。

正文不增加逐篇比较。图和新记号用于展示当前模型与算法的对应关系。
原51个正文编号公式保持原式，新增4个因子/消息定义式；含附录共62个编号公式。

`check_factor_graph.py` 核验旧公式、交叉引用及新增连接关系的确定性复数代数。
结果见 `validation.json`。编译与图表版面检查另见 `compile_result.json`。
本轮未运行训练或性能实验。
