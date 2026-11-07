# 参照 Cai、Shen 的符号统一

> 本轮历史图和绘图脚本已移入归档；当前生图入口见 [统一说明](../../../../src/evaluation/plots/manuscript/README.md)。以下记录描述当时版本。

后续状态：作者要求恢复原呈现方式，新增符号表和扩写的 Notation 段已撤回；重名修复及必要正文定义保留。当前状态见[回退记录](../notation_inline_only_20261103/REVISION_NOTES.md)。以下保留本轮完成时的记录。

日期：2026-11-03。对象：当前 C-STMP 稿件（展示名 GP-MP-CCD）的第 I–VI 章、附录 A–C、Algorithm 1 和方法图。由作者要求“你看下 cai 和 shen 都是怎么处理的，然后参照着处理一下”授权实施。

## 原文如何处理

| 原文位置 | 已核实的做法 | 本稿采用方式 |
|---|---|---|
| [Cai v2](../../../../reference/literature/cai2026_stmp_v2.pdf)，§I-C，PDF p.3 | 在引言后集中说明标量、向量、矩阵字体，以及转置、共轭转置、迹、对角算子和 Gaussian 记法。 | 补充 Notation 段，说明本文三阶张量继续采用普通字体，二维协方差采用粗体；定义单位虚数、转置及单位阵等。 |
| 同文 §II-A、Table I，PDF p.4 | 符号表汇总常用系统量与消息；以 pri/post/ext 上标和 A/B 模块下标区分均值、方差的用途。 | 增加 Table I，汇总 18 组常用符号。保留现有主要消息记号，只将容易与时延混淆的裸方差 tau 改为 tau^post。 |
| [Shen](../../../../reference/literature/shen2025.pdf)，Notations、§II-A，PDF p.3 | 用字体区分向量/矩阵，显式定义虚数单位、矩阵下标及运算符；系统量在模型中就地定义。 | 使用直立体 j 表示虚数单位；补齐张量展开顺序、列序号关系和各辅助量首次定义。 |
| 同文 §II-B，式 (2)–(10)，PDF pp.4–5 | 用 DD/TF 等领域上标和设备/帧/路径下标区分对象；求和索引按所在公式定义。 | 在前端导频响应、协方差生成和数值步骤中增加说明性上下标；保留作用域明确的局部哑元。 |

直接读取上述本地原文，并与已有逐式阅读记录交叉核对。这里借鉴的是组织和区分方式，不将本文所有字母、下标或 AFDM 张量定义登记为两文的原符号。Shen 的虚数单位采用加横线的 j；本文采用直立 j，是排版适配。Cai 的活动先验为 lambda、导频为 q_ktn，本文已有 rho、P_qkn 和 Q 保留。

## 已实施修改

| 位置/用途 | 修改前 | 当前记号或处理 |
|---|---|---|
| V-A 汇总后验方差 | tau | tau^post；正文、Algorithm 1、Fig. 3 同步，tau_raw、tau_min 和单设备估计保留。 |
| A-C 噪声样本数 | L=QN | N_s=QN；样本协方差分母与 MDL 的两处样本数同时修改。L 继续表示 OTFS 帧内时隙数。 |
| A-A 前端导频响应 | 粗体 h_k(d,nu) | 粗体 h_k^p(d,nu)，并注明维度 QN；II-A 的物理信道 h_k(t_c,tau) 保留。 |
| IV、VI 扰动协方差及因子 | 普通体 C、R_a、R_c | 粗体 C、R_a、R_c，与本文矩阵字体统一。 |
| VI-A 相关矩阵生成 | 普通体 R、G、xi | 粗体 R_corr、Z_tr 及 xi_corr；区分去噪输入、路径算子和波形时间变量。 |
| B-B 共同前缀长度 | G | N_pre；与 AFDM 的 N_CPP 对应，避免用同一字母表示矩阵和长度。 |
| IV-C 有限差分 | delta | delta_FD，并在首次使用处说明正步长及 L_z 为随机方向数。 |
| VI-A 活动历史平滑 | zeta | zeta_hist，与 II-B 的波形函数 zeta_n 区分。 |
| VI-A 评价索引 | i、未赋名的场景集合 | 定义当前条件下的场景索引集合 T，使用 e；迭代序号仍为 i。 |
| V-C 奇异值 | s_i、未明说的求和范围 | s_1,...,s_Q，求和使用 a=1,...,Q，明确条件 Q<=KN。 |
| V-A 与 VI-B 训练功率 | hat P_H 与 P_tr | 统一为 hat P_H，VI-B 回引 V-A 的训练均值定义。 |
| Algorithm 1 导频输入 | 未另行定义的普通体 P | 直接使用已定义的导频元素集合 {P_qkn}。 |

另补充 theta、phi 为可训练参数，delta_0 为零张量处的概率测度，epsilon_mach 为机器精度，nu_max 为最大绝对 Doppler，clip(x,a,b)=min{b,max{a,x}}。

矩阵元素的零基索引与列序号通过 j=mN+r+1 接通。张量展开明确为 [vec(H_k)]_(mN²+rN+n)=H_kmrn，即 n 最快、r 次之、m 最慢，与 antenna–output–input 协方差因子排列一致。

## 与实现的对应

- `src/training/colored_score_20261024/noise.py` 的模块说明与 `Covariance.apply_complex` 采用 [antenna, output, input] 的 C-order 排列；`pack/unpack` 对每个样本将实部、虚部分开堆叠。新增展开定义据此核对。
- `src/evaluation/denoising.py:107` 的 GaussianMean 与 `src/algorithm/STMP/receiver.py:92` 的初始方差均读取 `initialization.normalized_training_second_moment`；C_STMP 继承该初始化。当前配置值为 1.0004404181394917。统一 hat P_H 有运行配置依据，未仅凭名称相似就合并。
- 上述代码、配置、权重与实验结果没有由本轮修改，也没有启动推断、批量实验或训练。

## 保留的局部复用

lambda 与 lambda_i、U 与 U_k、b 的局部用途、g_j 的谱统计及 g_q 的帧起点等，完整记号、对象和作用域已经区分，保留。不同求和符号无需在全文各占一个字母。p、rho、pi_tr、p_k 具有不同概率含义，不能合并；物理噪声方差、消息方差、条件与联合后验方差同样保持区别。EP 的曲线后缀沿用作者已确定名称，并保留 estimated phases 的正文解释。

上一轮[符号核查](../../docs/NOTATION_AUDIT_20261103.md)中的建议是修改前记录；其中 b_D、g_j^eig 等可选改名未采纳，不再当作必须消除的错误。pilot energy 的已有用例与书目边界仍按该报告记录，未新增引用或冒称来自 Cai。

## 核验和交付

- [修改前快照](BEFORE.json)与[最终逐行差异](CHANGES.diff)完整保留。
- 71 个独立公式块在逆向映射本轮记号、去除排版空白后全部一致。SVD 的求和明确为 Q 个奇异值，原条件 Q<=KN 保持；没有删除或重复任何公式标签，仅新增符号表标签。
- 第六章全部数字串保持一致；VI-C 及其后结果分析原文保持。七幅实验图、两幅其他方法图的三个格式、引言、附录 C、参考文献库共 16 份受保护文件均保持原字节。
- 小尺寸确定性索引、Kronecker 作用和复实展开核对通过，最大误差均为 0；这只是排列恒等式检查，不是新的性能实验。
- Tectonic 编译成功，最终 PDF 为 18 页，无 Overfull 和未定义引用。仍有少量 Underfull 间距提示及旧图 PDF 版本提示；逐页缩略检查和第 3、7、8、10、15、16 页放大检查未发现溢出、重叠或缺字。Fig. 3 新方差标签也已单独查看。
- [完整核验数据](VALIDATION.json)和[页面预览](preview/)保留。接收机图由[当前导出入口](../../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/notation_cai_shen_20261103/draw_receiver.py)仅更新两处方差标签，其他布局、颜色与线条沿用原稿。

当前阅读稿：[main.pdf](../../main.pdf)。本轮新增符号表使完整稿从 17 页增至 18 页，模型、算法计算和实验数值不变。
