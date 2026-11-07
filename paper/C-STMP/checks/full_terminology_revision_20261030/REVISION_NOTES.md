# 全篇术语统一修订

日期：2026-10-30。对象：当前 C-STMP / GP-CCD-MP-DRE 稿件。

作者已同意落实[全篇清查清单](../full_terminology_audit_20261030/REPORT.md)，并明确要求 MIMO、GNN-ASPL、NTN-TDL-D 等缩写不必补展开。本轮落实 F01–F07、U01–U04、U06；U05 按作者要求不实施，MSE 也未另补展开。

## 已落实修改

| 清单项 | 最终处理 |
|---|---|
| F01 | 第二章 CPP 条件改为 maximum differential delay；表 I 的 [0,699] μs 改称 Differential-delay range。多径 Delay spread [30,50] ns 保留为另一物理量。 |
| F02 | 本文均值网络的 first-order network、mean network、channel network 统一为 channel denoiser；引言介绍 Cai 方法的 first-/second-order score networks 保留原意。 |
| F03 | 第六章直接说明分类器训练输入的噪声协方差 C=vI，以及冻结去噪器提供的特征；接收机沿用同一协方差形式。删除 training queries / scalar query covariance。 |
| F04 | covariance-weighted loss 改为明确引用第四章既有损失公式。原信道误差的 Σ⁻¹ 权重及等价得分误差的 Σ 权重不变。 |
| F05 | 使用 binary cross-entropy，并另说明训练时活动与非活动标签等概率；训练超参数均保留。 |
| F06 | 附录 B 删除 frequency wrapping 的名称及其不够明确的归属；直接以已有 wξ、ζn 和波形公式说明本稿采用的波形。Huang 引文支撑分数时延 AFDM 的背景，Bemani 引文支撑 CPP 关系，不将本文波形扩展冒称原文原式。 |
| F07 | 表 I 的 AFDM block length N 改为 Number of chirp subcarriers N，与 Q 帧组成 transmission block 的定义区分。 |
| U01 | 保留 proper complex Gaussian，在符号说明处新增 Neeser–Massey 1993 的直接引用。没有把非零均值复高斯变量误改为零均值变量。 |
| U02 | 图 6 横轴改为 Number of candidate devices；图 7 改为 Nominal activity probability。 |
| U03 | 当前正文、算法、表格、图注和附录统一称 device，K 对应候选设备数。内部文件名及 LaTeX 标签不变，引用论文的正式题名不改。 |
| U04 | 第六章标题、图注和比较说明统一为 channel profiles；图 8 的四个面板为 NTN-TDL-D/A/B/C。 |
| U06 | subcarrier(s)、precompensation/precompensate 统一拼写。正常的语法连字符不机械删除。 |

附录 D 的 variance-update residual 和 activity-history residual 紧接各自公式定义，保留为停止条件的直接描述。作者批准的 GP-CCD-MP-DRE、MFLE、GPJD、CCD 名称不变。

## 新增文献及定位

F. D. Neeser and J. L. Massey, “Proper Complex Random Processes with Applications to Information Theory,” *IEEE Transactions on Information Theory*, vol. 39, no. 4, pp. 1293–1302, July 1993. DOI: [10.1109/18.243446](https://doi.org/10.1109/18.243446)。[作者机构保存的原文](https://www.isiweb.ee.ethz.ch/archive/massey_pub/pdf/BI437.pdf)已取得，PDF 完整性检查通过，共 10 页。

- §III-A、Definition 1，印刷 p.1294 / PDF p.2：proper 的定义。
- Theorem 1、式 (10)，印刷 p.1295 / PDF p.3：含一般均值和非奇异协方差的 proper complex Gaussian 密度，直接支持符号说明的用法。
- 原文、哈希和读取检查存于 `sources/` 及 `VERIFICATION.json`；其余术语的来源定位延用上一轮清查报告，并将本轮落实情况追加至 `docs/TERMINOLOGY.md`。

## 内容与图件核验

- 11 份当前编入的 TeX 文件中，共 681 个行内/行间数学表达片段与修订前一致；数字及所有标签不变。仅增加一处既有损失公式的交叉引用。
- 32 个原引用键及全部原引用次数保留；新增 `neeser1993`，当前引用 33 个书目条目。Huang、Bemani 的附录引用位置调整，但引用次数不变。
- 中英文摘要保持原文，未重新生成；算法定义、训练设置、迭代参数和实验结论不改。
- 三幅图合计 204 个绘图点与原始统计严格一致，曲线样式、方法顺序、图例和尺寸完全一致。其余四幅独立图文件哈希不变。
- 17 个受保护文件的哈希不变，包括模型绑定、冻结绘图实现及配置、此次重绘使用的原始统计与原配置。未执行推断、批量实验或训练。

绘图只读取既有统计，新的标签保存在本目录的 `render_terminology_figures.py`；沿用前次已审查的绘图辅助函数和冻结样式，不修改冻结文件。源数据路径自动按当前 D: 工作目录解析。

## 编译和版面

唯一完整阅读稿仍为 `paper/C-STMP/main.pdf`，15 页。Tectonic 编译成功，无未解析引文/交叉引用、缺字、重复标签或 overfull 告警。3 处 underfull hbox 告警对应段落已目视检查，未见裁切或重叠。

最终 PDF 的第 1–15 页均经 Poppler 渲染并逐页查看，重点核对表 I、训练说明、图 6–8 标签、附录 B 和新增参考文献。页数、图表顺序及阅读效果正常。最终全文及三幅改图均通过 PDF 完整性检查。

`MANUSCRIPT.diff` 保存当前稿与本轮快照的差异，`VERIFICATION.json` 保存内容核验，`RENDER_VALIDATION.json` 保存数据与样式核验。旧清查报告保留为历史待办状态，本记录表明上述项目已落实；它不扩展此前文献全文检索的覆盖范围，也不声称所有专业表述已在所有文献中穷尽检索。
