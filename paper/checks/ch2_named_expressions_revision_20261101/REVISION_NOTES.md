# 第二章具名表达替换记录

日期：2026-11-01。作者指令：“能替换的全部替换”。本轮处理上一轮全部名称清单中特别列出的 13 项，落实为第二章 12 处局部替换；两项索引名称位于同一句，合并处理，跨帧公式与其说明也一并更新。附录 A 仅同步替换原来的 wrap 调用。

第二章修改前 SHA-256：`ee2a176d5eda597807fbb028171a82b62cbc24d1dc111f134539c59f70b49f16`。修改后：`d0ac91a7b4473d9974b67481d6a69959d85a6eb2a6bd9f507d093b6b8acb3c39`。源稿保留干净排版，不加入审阅粗体。

## 13 项逐项处理

| 原表达 | 当前处理 | 已读出处与支持范围 |
|---|---|---|
| pilot resources | **resources for pilot transmission** | Cai，PDF p.1，§I：原文同一完整短语。删去后面重复的 to transmit their signals，保留导频发往卫星。 |
| receiver compensation for the common delay | **delay compensation**，在句中说明 for τ_c at the satellite receiver | Li，PDF p.4，§II-B 的 delay compensation techniques。τ_c 与卫星接收端仍是本文原设定；不把 Li 的终端预补偿模型移植进来，也不将完整改后句冒称 Li 原句。 |
| arrival angles | **angles of arrival** | Li，PDF p.4，§II-B 的 paired angles-of-arrival；只作常见连字符调整，不换词序。 |
| Multi-Frame AFDM Transmission | **Transmission Scheme** | Shen，PDF p.4，§II-B 的原小节标题。多帧 AFDM 的事实仍由本小节正文与公式说明。 |
| known pilot matrix | **pilot matrix**；已知性单独表述为 The pilot symbols are known at the satellite receiver. | pilot matrix 见 Cai §II-A/p.4；已知性句见 Wei §II-A/p.2 原句 The pilot symbols are known at the receiver…，只增加本文已有的 satellite。P 的维度、元素与接收端已知条件保持。 |
| pilot energy | 不再另取英文名称，直接写 **‖p_qk‖²=E_p for all k and q** | 保留原有的向量平方范数定义和各设备各帧相同的约束。不把 energy 改成 Cai 的 transmit power budget；不引入 Tang 引用。这里是同一数学条件的直接表达，不是为新名称寻找拼接出处。 |
| time duration of an AFDM frame with CPP | **Each AFDM frame spans a duration of T_frame=(N+N_CPP)T_s.** | Huang，PDF p.2，§II：Each AFDM frame spans a duration of T=NΔt. 只代入本文原有的含 CPP 时长及符号；不采用 Huang 不含 CPP 的数值公式。 |
| CPP relation | **satisfies (5)**，直接引用原公式 | 仅删去未经核实的组合名称；仍指向原 CPP 等式，条件 ξ<0 保持。 |
| transmitted symbol position | **transmitted symbols**，由 n 对应 | Bemani，PDF p.10，§III-D：received symbols / transmitted symbols 同处输入输出说明。此处不再为索引 n 另造 position 名称。 |
| antenna index | 写出 **m=0,…,M−1** | m 已是式(7)中阵列分量 [a_k]_m 的下标；范围与式(2)的 n_z+M_z n_y 一致。删除该名称，不为一个通用下标额外加入 Ke 引用。原句中的 received symbol position 同步改为 received symbols，使收发对象并列一致。 |
| wrap | **用 floor 的显式等价式定义 β_k** | 直接展开原来映射到 [-π,π) 的数学操作；不引入新英文函数名，不冒称该展开式来自参考论文。附录 A 同步按式(9)计算估计相位。 |
| phase evolution across frames | **The phase rotation e^{jqβ_k} accumulates across multiple frames, while H_k remains approximately constant over Q consecutive frames.** | Shen，PDF p.5，§II-B：phase rotation…accumulates across multiple frames；同文 p.4：remains approximately constant over Q consecutive frames。分别保留两部分的真实来源，不把拼接后的完整句登记为原句。 |
| inter-frame phase rotation | **phase rotation** | Shen，PDF p.5，§II-B 原词；q 与 e^{jqβ_k} 已明确表达跨帧关系，不需要另造复合名称。 |

上述处理后，13 项旧表达在第二章均不再保留。没有用尚未核实的近义复合词替代它们。其余已核得的名称保持，包括 pilot vector、activity states、array response vector、channel prior 等。

## 相位公式为何等价

原定义是将 2πν_k T_frame 映射到 [-π,π)。现在写成

\[
\beta_k=2\pi\left(\nu_kT_{\rm frame}
-\left\lfloor\nu_kT_{\rm frame}+\frac12\right\rfloor\right).
\]

令 x=ν_k T_frame，整数 a=⌊x+1/2⌋ 满足 −1/2≤x−a<1/2，因此 β_k∈[−π,π)。且对整数帧索引 q，有 e^{jqβ_k}=e^{j2πqx}，所以原跨帧信道关系不变。半整数边界映射至 −π，与原来的半开区间约定一致。

只有式(9)的 β_k 定义作等价展开；同式 H_k^(q)=e^{jqβ_k}H_k 保持。其他 14 个编号公式、2 个无编号陈列式及附录 A 的全部编号公式逐字保持。原来的 E_p=‖p_qk‖² 换向书写为 ‖p_qk‖²=E_p；显式的 m 范围也不改变原索引集合。

## 范围与验证

- 第二章差异严格限于登记的 12 处替换；附录 A 仅一处依赖同步。完整差异见 [CHANGES.diff](CHANGES.diff)。
- 19 个保护文件的 SHA-256 保持，包括 main.tex／英文摘要、引言、其他正文与附录、中文摘要、references.bib 和七幅图。正文引用命令未新增、未删除。
- 相位等价式除上述代数说明外，还用精确分数检查了 21,627 个输入，包含正负半整数边界及边界两侧；区间和整数帧相位一致性均通过。该检查是公式一致性验证，不是实验或训练。
- 11 组本轮使用的原词／句式片段已对照指定来源页，摘录保存在 [SOURCE_EVIDENCE.json](SOURCE_EVIDENCE.json)。
- Tectonic 缓存编译成功，唯一阅读稿 main.pdf 仍为 13 页，无未定义引用或 Overfull；第二章无 Underfull。原有其他章节的 Underfull 提示不在本轮改动范围。
- 已目视检查第二章所在 pp.2–4 及附录 A 所在 p.11，公式、列宽和段落均无新增裁切、重叠。
- 编译时发现旧 main.bbl 没有收录 main.tex 第 80 行本来就已引用的 neeser1993。重新生成的 main.bbl 收录了该条；没有改动书目源文件或新增引用命令。核验如实记录该缓存差异，不声称生成的 .bbl 字节不变。

核验结果见 [VALIDATION.json](VALIDATION.json)，备份见 before/。旧的 96 项清单作为修改前审计保留，当前处理状态以本记录为准。名称／搭配来源、本文条件与本文数学展开仍分别记录，不将本文整个系统模型追认成参考论文原有模型。
