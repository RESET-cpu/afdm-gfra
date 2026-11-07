# 第二章严格原句核对结果

**结论：当前第二章不符合“每一句均来自参考文献原句，除必要术语替换外其余不变”的要求。**

十二个段落分别由十二个子代理逐句审查，主代理复核证据、句子边界、覆盖和计数。共70个完整说明句：9句原句一致，7句仅必要术语或符号替换，29句存在非术语增删改，25句本次未定位可对齐整句，0句因证据不可读而未核实。严格单句通过16/70；没有整段全部通过。

此前将“根据原文改写”表述为“只做必要术语替换”不准确，应以本次逐句证据为准。

## 范围与判定

对象：[当前第二章源文件](<D:/afdm-gfra/paper/C-STMP/sections/02_system_model.tex>)，第4—280行的12个TeX正文段落。章节标题不计段；公式及其where/Here定义归入完整语法句，不把匹配的前半句拆出计为通过。

只豁免空格、PDF断行与连字、TeX排版、引用及章节/公式号显示差异，以及可逐项列明的必要技术名称和数学符号替换。非术语删词、加解释、改谓语、改连接词、重排、跨句拼接均不通过。显示公式本身属于本文模型，未要求照抄，但公式周围的英文定义照常审查。

“本次未定位”只表示在所核查语料中找不到可逐词对齐的完整句子，不等于该内容技术错误，也不等于所有论文均无相关依据。本报告不是数学正确性或术语适用性认证。

## 分段结果

| 段落 | 内容 | 原句一致 | 仅术语替换 | 非术语增删改 | 未定位整句 | 严格通过/总句数 |
|---|---|---:|---:|---:|---:|---:|
| [P01](<D:/afdm-gfra/paper/C-STMP/checks/strict_sentence_audit_20261029/P01.md>) | 系统总述 | 1 | 1 | 3 | 0 | 2/5 |
| [P02](<D:/afdm-gfra/paper/C-STMP/checks/strict_sentence_audit_20261029/P02.md>) | 物理信道与参数 | 3 | 2 | 3 | 5 | 5/13 |
| [P03](<D:/afdm-gfra/paper/C-STMP/checks/strict_sentence_audit_20261029/P03.md>) | 多帧传输与IDAFT | 0 | 1 | 4 | 2 | 1/7 |
| [P04](<D:/afdm-gfra/paper/C-STMP/checks/strict_sentence_audit_20261029/P04.md>) | CPP与帧时长 | 0 | 0 | 3 | 1 | 0/4 |
| [P05](<D:/afdm-gfra/paper/C-STMP/checks/strict_sentence_audit_20261029/P05.md>) | 信道矩阵及其定义 | 0 | 0 | 3 | 7 | 0/10 |
| [P06](<D:/afdm-gfra/paper/C-STMP/checks/strict_sentence_audit_20261029/P06.md>) | 跨帧相位关系 | 0 | 0 | 3 | 1 | 0/4 |
| [P07](<D:/afdm-gfra/paper/C-STMP/checks/strict_sentence_audit_20261029/P07.md>) | 活动与接收观测模型 | 0 | 2 | 5 | 3 | 2/10 |
| [P08](<D:/afdm-gfra/paper/C-STMP/checks/strict_sentence_audit_20261029/P08.md>) | 块稀疏性与块内相关性 | 1 | 1 | 0 | 1 | 2/3 |
| [P09](<D:/afdm-gfra/paper/C-STMP/checks/strict_sentence_audit_20261029/P09.md>) | JADCE任务总述 | 1 | 0 | 0 | 1 | 1/2 |
| [P10](<D:/afdm-gfra/paper/C-STMP/checks/strict_sentence_audit_20261029/P10.md>) | 已知量与先验假设 | 0 | 0 | 1 | 3 | 0/4 |
| [P11](<D:/afdm-gfra/paper/C-STMP/checks/strict_sentence_audit_20261029/P11.md>) | 后验分解与估计目标 | 1 | 0 | 2 | 1 | 1/4 |
| [P12](<D:/afdm-gfra/paper/C-STMP/checks/strict_sentence_audit_20261029/P12.md>) | 消息传递困难与后续引出 | 2 | 0 | 2 | 0 | 2/4 |
| **合计** | | **9** | **7** | **29** | **25** | **16/70** |

## 各段关键差异

- **P01：**删去固定波束和星载处理设置；把广播公共时延改为补偿公共时延。
- **P02：**跨来源组合；时间原点、阵列完整定义和参数恒定说明等未定位整句。
- **P03：**删去spreading-based；改写公式后的定义并加入导频能量说明。
- **P04：**改变前缀条件及谓语，新增取模和长时延说明。
- **P05：**矩阵、逐项算子及索引说明多数未定位整句；泄漏句也有删改。
- **P06：**相位关系说明新增；删改原句原因、目标并改变原文叙述顺序。
- **P07：**删去活动概率和功率预算限定；重写观测及堆叠公式后的where定义。
- **P08：**前两句有连续来源；新增块内统计依赖解释未定位整句。
- **P09：**任务总述与Cai一致；Q<KN说明未定位整句。
- **P10：**将稍后更新改为由观测获得；训练先验及独立性说明未定位整句。
- **P11：**删去后验表达式；改写整个where定义；联合估计目标句未定位。
- **P12：**末两句一致；前两句各有删除，且跨原段与条目拼接。

## 审查材料与交付

- [完整逐句对照](<D:/afdm-gfra/paper/C-STMP/checks/strict_sentence_audit_20261029/FULL_AUDIT.md>): 每句当前文字、候选原句或定位、页码、变更清单、结论；每段另附原段组织检查。
- 各Pxx.json保留代理完整原始证据，包括补充来源与检索范围；[覆盖与文件校验记录](<D:/afdm-gfra/paper/C-STMP/checks/strict_sentence_audit_20261029/VALIDATION.json>)保留主代理复核结果。
- [原稿快照与段落边界](<D:/afdm-gfra/paper/C-STMP/checks/strict_sentence_audit_20261029/manifest.json>)；[来源文件及哈希](<D:/afdm-gfra/paper/C-STMP/checks/strict_sentence_audit_20261029/SOURCES.json>)；[统一核对标准](<D:/afdm-gfra/paper/C-STMP/checks/strict_sentence_audit_20261029/PROTOCOL.md>)。

直接核对用户提供的Shen、Cai期刊版、Cai v2、Ding、Huang原PDF；另补查Li和Bemani。两份补查来源分别为[Li arXiv:2207.11958](https://arxiv.org/abs/2207.11958)和[Bemani arXiv:2204.12798v2](https://arxiv.org/abs/2204.12798v2)。它们只在相关定义和CPP来源核对中使用。

十二个子代理各负责一个段落，并非跨模型独立盲审。主代理复核了完整说明文字的顺序覆盖，回查来源及分类，未以公式合理性代替语言来源。

本轮未修改论文正文或PDF。正文与审查起始快照SHA256一致：

`bb94e3a63b6a85779285b7ffffe7bae89bcba05d919df132983b1ae0ee0a24a7`

后续修改必须区分“可保留的原句”和“本文特有的模型说明”；不能仅为逐字一致而恢复不适用于本文的系统假设。此轮没有自动执行这些修改。
