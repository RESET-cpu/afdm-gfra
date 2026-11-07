# 第二章七项表达与出处问题的后续修正

作者要求修正上一轮规范中登记的问题，并完整展示第二章、加粗本轮修改。基线为当前源稿（SHA-256：`64bdafcafa31bf07081d8a6f521d77291bfe2a9a0260f044f4af4e1e09ceb52b`）。备份见 `before/`，逐行差异见 `CHANGES.diff`，核验见 `VALIDATION.json`。

只调整六处文字与三处公式末尾标点，合计对应规范中的七项问题。干净源稿不加入审阅用粗体；审阅展示按本轮差异标粗。摘要、引言、其他章节及数学定义不作调整。

## 实际替换及依据

1. **相邻重复。** `Assume that a total of Q AFDM frames are allocated for pilot transmission.` → `Assume that Q AFDM frames are allocated for pilot transmission.` Cai §II-A、PDF p.4 的原句为 `Assume that a total of T OFDM symbols are allocated for pilot transmission.` 保留原分配句，删去重复的 a total of，维持本文 Q/AFDM 设置。不是模型改动。

2. **时间原点。** `The time instant t_c=0 corresponds to the beginning of the transmission block.` → `We set t_c=0 at the beginning of the transmission block.` `We set` 可直接核于 Cai §III-B2、PDF p.7、式(31)前的阈值设置句；`at the beginning of` 见 Li §II-A、PDF p.3 的 OFDM/CP 说明。这里只采用普通约定句式与时间表达，不声称完整新句来自同一原句，也不把阈值或 OFDM 条件移植到本文。时间原点是本文既有约定；后面的 Shen 公共时延定义保持。

3. **方向余弦。** `The directional cosines μ_z,k and μ_y,k are along the z-axis and y-axis, respectively.` → `Here μ_z,k and μ_y,k are the directional cosines along the z-axis and y-axis, respectively.` Shen §II-A、PDF p.3、式(1)后的原句用 `The directional cosines …, along the z-axis and y-axis, depend on …` 说明方向与角度。本文保持方向余弦术语、两个方向及其顺序，以变量为主语解释物理含义，不引入原文的角度参数化。此前压缩后的弱谓语被修正，不登记为逐字原句。

4. **路径对象。** `For path gain 1, delay dT_s, and Doppler shift ν, …` → `For a path with gain 1, delay dT_s, and Doppler shift ν, …` Shen §II-A、PDF p.3 使用 path gain、Doppler shift 并明确对应某一路径；Cai §II-A、PDF p.4、式(2)前提供 `the channel … response … can be expressed in a matrix form as`。本轮只补出当前路径对象，不将 `For a path with …` 登记为已核实的完整原句，不恢复未经核实的 unit-gain path 名称。增益为 1、时延及 Doppler 条件和式(8)均为原稿已有内容。

5. **先验指代。** `We model the entire H_k using q_tr(H_k), the channel prior for training, rather than factorizing it element-wise.` → `We model the entire H_k using the channel prior q_tr(H_k) for training, rather than factorizing this prior element-wise.` Cai 摘要、PDF p.1 的原句为 `… models the entire channel matrix as a super node, rather than factorizing it element-wise.` 同文 §II-B、PDF pp.4–5、式(5)及 Table II 给出完整信道先验因子 p(H_k)。本文保留原句框架，用 this prior 明确分解对象，并使 channel prior 紧邻 q_tr。q_tr 的训练用途沿用本文第三、四章；for training 是本文用途说明，不是蔡文的完整术语或同一训练设定。

6. **独立性归属。** `The variables H_k and α_k are independent for different values of k, and H_k is independent of α_k.` → `We assume that H_k and α_k are independent for different values of k, and that H_k is independent of α_k.` Li §II-C、PDF p.5 原句 `Moreover, we assume that α_{k,ℓ}'s are independent for different k and ℓ, …` 仅提供假设句式；该文 α_{k,ℓ} 是信道系数，并非本文活动指示变量。本文跨设备及信道与活动的独立性均为既有假设，不是由该句证明的结论。此前 Cai 关于不同列消息独立的来源不再作为相同技术陈述的依据。本轮不改变式(14)的因子分解。

7. **公式标点。** 式(2) `eq:upa`、式(6) `eq:continuous-waveform`、式(8) `eq:path-operator-system` 末尾句号均改为逗号，与紧接的小写 where 相连。仅改标点，不改表达式、变量、索引或条件。验证脚本只对这三处允许 period→comma，其余 14 个陈列式要求完全一致。

## 出处范围与复用

本轮直接复读了既有本地逐页摘录中的 Cai p.1/p.4/p.7、Shen p.3、Li p.3/p.5；原文页文本与 PDF 路径沿用前轮证据库。上述句子按适用层次登记：原句的最小删改、已有句式或术语的必要语法适配、本文原有定义／假设。不能把这些不同层次合并宣称为“每句完整文字和技术内容都出自母本”。

写作规范中的七项已同步标为按本轮范围解决；术语账本追加本轮记录。旧版逐句对照和前轮差异保留为历史，不覆盖其原始文件。没有新增专业术语、缩写、假设或参考文献，没有启动实验或训练。

## 核验结果

- `verify.py` 通过：恰为六处文字替换及三处标点替换；15 个编号公式的数学内容和 2 个无编号陈列式保持，全部标签保持。
- 20 个保护文件的 SHA-256 均未变化，包括承载英文摘要的 main.tex、引言、其他章节、书目及七幅图；术语账本旧内容完整保留。
- 新增正文词形仅 set，已有文献用例；这项词形检查不替代上文的句式及含义核对。
- Tectonic 缓存编译成功，main.pdf 为 13 页；无未定义引用或 Overfull，第二章无 Underfull。其他章节和书目的原有 Underfull 提示保留。
- 已渲染并目视检查第二章所在第 2–4 页：公式、文字、列间边界及页末内容完整，无裁切或重叠。渲染留存为 page-02.png 至 page-04.png。
