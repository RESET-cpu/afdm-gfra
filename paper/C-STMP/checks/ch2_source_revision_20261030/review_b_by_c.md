# P04–P08 交叉复核

结论：6项来源措辞适配均已正确应用；本次未发现需要返工的来源、术语或模型改动。CPP的非严格不等式保留，Ding矩阵式的共轭/命名不一致没有抄入当前稿。

复核绑定正文SHA256：`0afc16e78752ee18b28745542dc4f1a581eadab45ab8fb3658a28c27549bbbc2`。

本次只检查`b_patch.json`的6项变更及其在当前英文第二章中的实际落点。另直接重新提取Ding原PDF第2页、Bemani原PDF第8页，实际查看Ding第2页、Bemani第8页及Huang第2页原页图像；Cai正式版第4页的导频与CP句沿用本人本轮已直接查看过的原PDF页面。未扩大为全模型或实验审计。

| 原句ID | 来源与实际适配 | 交叉判断 |
|---|---|---|
| P04.S02 | Cai正式版PDF p.4 / 期刊p.3578，II-A，式(3)前导频标量定义：`Let ... be the pilot symbol transmitted by ... during ... on ...`。当前保留此完整结构，仅将导频符号、时间索引、OFDM symbol与subcarrier适配为本稿AFDM帧与chirp subcarrier。 | 来源结构恢复成立。没有新增导频独立性、随机性或正交性假设。 |
| P05.S01 | Ding PDF p.2，II，式(1)前关于设备用AFDM发送符号的并列分句，与式(3)后`where T_s = 1/(NΔf) gives the sampling interval`从句组合。 | 仅去并列连接词、改句首大小写、将原符号向量换为既有导频向量。N、Δf、T_s关系与旧稿相同，未增加新的物理条件。 |
| P05.S02 | Ding PDF p.2，II，式(1)引导句及后续c1、c2参数说明。 | 已恢复`The time-domain transmitted signal is generated through ... applied to ... mathematically formulated as`。原有样本索引前缀属于本稿声明且保持原样；参数句用where连接属于必要语法调整。显示求和式逐字未改。 |
| P05.S03 | Ding PDF p.2，II，式(2)前`The signal in (1) can be represented in matrix form as`；Huang PDF p.2 / 期刊p.2950首段对DAFT矩阵的命名从句。 | 主句与矩阵名称可分别定位；F_A的元素式和s=F_A^H p沿用本稿既有定义，不是把Ding式(2)原封照抄。DAFT全称沿用当前稿首次定义，没有新名称。 |
| P06.S01 | Cai正式版PDF p.4，II-A，式(3)前CP长度句骨架；非严格比较关系可定位到Bemani PDF p.8，III-A，式(19)前的CPP长度条件。 | 当前英文为非严格比较，数学仍是N_CPP T_s ≥ max τ_kℓ，未被Cai的严格比较收紧为>。i.e.后原式明确本稿所用的最大差分时延条件，未改变既有边界。 |
| P07.S06 | Huang PDF p.2 / 期刊p.2950，II，式(5)后的完整功率泄漏句。 | 除既有方程引用和H_k符号替换外，限定语、词序、can introduce及thereby weakening结构均恢复原文。未增添额外稀疏性假设，也未改G算子。 |

## 重点核验

1. **CPP条件**：当前正文恰有一处原式`N_{\rm CPP}T_s\geq\max_{k,\ell}\tau_{k\ell}`，与替换前逐字相同。Bemani仅作为非严格长度比较的来源；本复核不将其短时延模型推广为对本稿全部时延范围的独立证明。
2. **Ding笔误没有移入**：原页式(2)在逆变换分解中写F，并在随后文字把A^H称为DAFT矩阵。当前稿没有复制该分解或名称关系；仍以负号指数定义F_A，以F_A^H作用于导频得到正号指数发射式。Huang第2页和Bemani第8页对A与A^H的约定支持当前矩阵方向。本轮修改仅改变相关英语引导语和命名动词。
3. **没有新增无出处技术名**：本次引入或恢复的AFDM modulation、sub-carrier spacing、IDAFT、DAFT matrix、CPP、power leakage等均在上述原PDF相关页出现；其余新增文字为句法连接、符号指代或原句限定语。未新增方法名、缩写或自拟模型名称。
4. **没有新增物理假设**：当前P04–P08忽略空白后恰好等于基准段落应用6个b操作所得文本。P08原文完整保留；P04导频能量/矩阵条件、P07路径矩阵与张量定义不变。跨帧相位关系未重新推导或改写。

## 实际应用与不变量

- 6个`new`文本块在当前canonical中各匹配一次。
- 6个操作涉及的全部显示公式与替换前逐字相同。
- P04–P08的标签序列与基准相同，既有维度没有变化。
- 没有写入canonical；本次唯一新增文件为本复核报告。

本结论限定为来源措辞适配和本次修改不变量检查。原有作者定义、符号重排和算子推导仍保持其作者定义身份，不因英语恢复而改称参考论文的原模型。
