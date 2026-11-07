# 第二章定义句与段落衔接修正

## 本轮直接核实的结论

作者指出的整句 “The notations … denote the UPA response, the time from the block start, and the Dirac delta function, respectively.” 不是已核参考文献的原句。上一轮将 Shen 的转置运算符定义、Dirac 函数定义和本文的向量/时间说明拼接到同一句中，再以“原定义句适配”登记，不能满足作者要求的原段原句最小合理替换。该出处归类在本轮撤回。

本轮对 Shen、Cai、Ding、Li、Huang、Bemani 的缓存逐页正文及 Wei 本地全文作词面检查，未找到完整短语 **UPA response**。这只是已查语料的结果，不代表断言全部文献都没有此用法。Li §II-B、PDF p.3 式(2)后的用词是 **array response vector at the satellite side**；p.4 的阵列响应段随后以原句 “Then, the array response vector … can be written as …” 引出表达式。本稿采用这一原有名称与相应句式。

旧稿完整的 `The notations` 实际出现两次。问题不仅是次数：第一处将向量、时间、函数硬并为一组，第二处又套同一句式解释阵元间距；加上邻近连续的 Let、Define、Then 及重复定义，产生逐项列说明的感觉。此次不以删除某个词或控制次数作为质量标准，而按公式和物理对象组织解释。

## 实际修改与原文定位

| 修改位置 | 原文依据 | 当前处理 |
|---|---|---|
| 物理信道式前、式后 | Li §II-B，PDF p.3，式(1)前 time instant 和式(2)后 where 定义；Shen §II-A p.3 路径定义 | 把路径数、增益、Dirac 函数放在物理信道式后的 where 中；时间原点单独说明；不再把阵列向量混进该列表。时间原点是本稿原约定，不能称为 Li 的相同假设。 |
| 阵列响应式前 | Li §II-B，PDF pp.3–4 的上述原词与原句 | 改为 The array response vector … at the satellite side can be written as；仅代入本稿 a_k，阵列公式不变。 |
| 阵元间距 | Li §II-B，PDF p.4，阵列向量定义后关于 d_v 的原定义 | 采用 d_v 与 v∈{y,z} 的原式说明方式，轴集合由 x/y 改为 y/z；直接放在阵列式后的 where 从句中，删除第二个 The notations。 |
| IDAFT 与矩阵形式 | Ding §II，PDF p.2，式(1)后参数说明和式(2)前原句 | 删除 The parameters … are … parameters 的重复；采用 “The signal in (1) can be represented in matrix form as”，式号换成本稿相应式号，取代重复说 time-domain signal 的引出句。原来借用 Xu 的那一句由更贴合上下文的 Ding 原句替换，不为凑齐作者数量保留。 |
| 连续波形 | Bemani §III-A，PDF p.8，式(18)前后的 modulated signal → where 组织；原句开头为 “The modulated signal can be written as” | 先给出本文波形，再在式后解释 w、ζ；将信号对象换为本文波形与时间。该连续波形仍是本文已存在的表达，不能声称就是 Bemani 式(18)。 |
| 参考帧有效信道 | Cai §II-A，PDF p.4，式(2)前的有效对象—can be expressed 句式 | 把 Let H_k=H_k^(0) 与 Then… 合并成 For q=0 的一句，避免先命名再重复引出同一对象。 |
| 跨帧信道 | Shen §II-B，PDF p.4，Proposition 1 前 Based on…we can derive… 原句 | 把本文 g_q 的取值直接放入该推导句的条件中；不再先单列 After…let… 再重复启动推导。 |
| 信道先验与后验 | Cai 摘要 p.1 关于 entire channel matrix / element-wise 的原句，以及 §II-B p.4 的后验分解句 | 把 q_tr 的定义并入完整信道建模句；把固定 Ahat、sigmahat² 的条件移到后验分解句前。后者是本稿推断条件的必要适配，不登记为 Cai 原有前端。 |

逐项的真实文本差异见 [CHANGES.diff](CHANGES.diff)。本次使用原文句段组织相应内容，仍明确区分直接采用原句、对象/符号替换与本文条件适配；不会再用“句中词形都有来源”替代完整搭配核验。

## 核验

15 个编号公式和 2 个无编号陈列公式保持逐字一致；标号不变。新使用的 d_v 只是 d_y、d_z 的统一写法，t_c=0 只是原“从块起点计时”的等价说明。原有独立性、共同 Doppler、参数不变、训练先验及固定前端条件保持。

摘要未重新生成；摘要、引言、其他章节、书目与七幅图共 20 个保护文件保持。阅读稿仍为 main.pdf。编译与页面核验详见 [VALIDATION.json](VALIDATION.json)。

上一轮 [SENTENCE_ALIGNMENT.md](../ch2_shen_cai_rewrite_20261101/SENTENCE_ALIGNMENT.md) 保留为当时版本的历史记录。本记录与差异文件明确替代其中受本轮修改影响的条目，特别是 12、13、15 等条目，不能继续用旧对照证明当前正文逐字匹配。
