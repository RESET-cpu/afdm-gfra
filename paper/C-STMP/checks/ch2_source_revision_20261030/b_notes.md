# P04–P08 第二章修订候选

仅输出候选操作，未改canonical。依据FINAL_AUDIT，修改剩余6个SUPPORTED_PARAPHRASE句；P04.S01沿用主审REASONABLE_COMBINATION，另14个本文定义/推导句保持。

## 修改说明

- **P04.S02**：恢复Cai的Let ... be ... transmitted by ... during ... on ...完整句法，只作P/q索引、OFDM symbol→AFDM frame及subcarrier→chirp subcarrier的必要对象替换。
- **P05.S01**：用Ding原句中完整发射分句与采样间隔where分句组合：去掉并列连接and并大写The，x_k替换为本稿导频向量p_qk。Δf和Ts关系不变，无新物理假设。
- **P05.S02**：撤销applying ... yields主动改写，恢复Ding原始主谓结构。现有t索引范围和显示公式原字节保留；参数原句用where连接，只有为完整公式句必要的语法连接。
- **P05.S03**：矩阵主句恢复Ding的The signal in ... can be represented；矩阵命名采用Huang的where A denotes the DAFT matrix。A换为本稿F_A并保留已定义的完整元素式，DAFT展开全称；所有显示数学原字节不动。
- **P06.S01**：采用Cai完整句骨架，CP→CPP；exceeds按Bemani既有非严格边界措辞适配，保持本稿≥而不收紧为>；i.e.后原不等式保持不变。
- **P07.S06**：恢复Huang完整原句词序、限定语、can introduce及of方程引用，只替换已存在的本文方程引用和H_k符号；不把本稿G改称Huang完整原式，也不改G定义。

## 每个旧句处理索引

| 旧句 | 处理 | 旧分类 |
|---|---|---|
| P04.S01 | KEEP | REASONABLE_COMBINATION |
| P04.S02 | MODIFY | SUPPORTED_PARAPHRASE |
| P04.S03 | KEEP | AUTHOR_DEFINED_OR_DERIVED |
| P04.S04 | KEEP | AUTHOR_DEFINED_OR_DERIVED |
| P04.S05 | KEEP | AUTHOR_DEFINED_OR_DERIVED |
| P04.S06 | KEEP | AUTHOR_DEFINED_OR_DERIVED |
| P05.S01 | MODIFY | SUPPORTED_PARAPHRASE |
| P05.S02 | MODIFY | SUPPORTED_PARAPHRASE |
| P05.S03 | MODIFY | SUPPORTED_PARAPHRASE |
| P06.S01 | MODIFY | SUPPORTED_PARAPHRASE |
| P06.S02 | KEEP | AUTHOR_DEFINED_OR_DERIVED |
| P06.S03 | KEEP | AUTHOR_DEFINED_OR_DERIVED |
| P07.S01 | KEEP | AUTHOR_DEFINED_OR_DERIVED |
| P07.S02 | KEEP | AUTHOR_DEFINED_OR_DERIVED |
| P07.S03 | KEEP | AUTHOR_DEFINED_OR_DERIVED |
| P07.S04 | KEEP | AUTHOR_DEFINED_OR_DERIVED |
| P07.S05 | KEEP | AUTHOR_DEFINED_OR_DERIVED |
| P07.S06 | MODIFY | SUPPORTED_PARAPHRASE |
| P08.S01 | KEEP | AUTHOR_DEFINED_OR_DERIVED |
| P08.S02 | KEEP | AUTHOR_DEFINED_OR_DERIVED |
| P08.S03 | KEEP | AUTHOR_DEFINED_OR_DERIVED |

## 核验与边界

- 6个old均在当前canonical中唯一匹配；在内存中顺序应用后，全部显示数学块、全部标签保持逐字一致。
- 原有14个equation环境保持。没有修改维度、先验、公共Doppler假设、CPP不等式边界、G算子、长CPP延拓或跨帧相位式。
- P05.S01采用Ding两个原有分句组合，首个并列分句独立成主句；只把其发射符号换成本稿已有导频向量。
- P05.S02保留作者原有样本索引范围；公式主体与where参数说明不动，只恢复Ding的原始IDAFT主句。索引声明不冒充外部原句。
- P05.S03的矩阵命名取Huang，正确数学仍用本文已有F_A，避开Ding式(2)的F/Fᴴ及A/Aᴴ不一致。
- P06.S01采用Cai句法，并按Bemani已有的非严格比较措辞保持本稿≥。Bemani未在说明或source_refs中引完整句；候选正文只借用短比较用语。根代理已明确接受这一必要数学边界适配。
- P07.S06只恢复Huang泄漏句语言；引用本文算子不表示已经核实其与Huang式(5)完整等价，本文G仍归本稿定义/推导。
- 未加防御性正文解释，未改正文文件、PDF、模型或实验。
