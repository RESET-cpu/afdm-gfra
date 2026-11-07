# 引言第三段：AFDM 低复杂度调制

日期：2026-11-06。作者确认采用聊天中展示的 AFDM 背景表述。

## 修改

仅修改 `sections/01_introduction.tex` 第三段的 AFDM 部分：一维啁啾信号的低复杂度调制结构；一次逆 FFT 与两组逐点啁啾乘法；适当参数下的满分集。实现结构沿用 Bemani 的具体章节引用。

删除该段末尾对本文 stationary-device 跨帧相位、共享有效信道与先验学习的提前说明。相关内容仍在第一项贡献和第二章。三项贡献以及引言其他段落逐字保持；未采用聊天中另提的活动检测段或过渡句候选。

## 文献依据

- Ding，§I，PDF p.1：一维 chirp modulation 与低复杂度动机；`reference/literature/ding2026.pdf`。
- Huang，§I，印刷 p.2949：一维 IDAFT 与实现复杂度；`reference/literature/huang2026.pdf`。
- Bemani、Ksairi、Kountouris，TWC 2023，§II-B 式 (16) 后的逆矩阵分解、§III-A 式 (18)：逆 FFT 与两组逐点啁啾乘法的依据；§III-E/§IV 支撑有条件满分集表述。[作者稿](https://arxiv.org/html/2204.12798v2)。

低复杂度表述为依据上述文献的改写，不是逐字转载，也不宣称 AFDM 相对所有 OTFS 实现具有普遍复杂度优势。此前矩形脉冲 OTFS 变换消去的比较边界继续有效。

## 核验

- Tectonic 0.17.0 编译 `main.tex`、`main_full.tex` 成功；输出 13/14 页、42 条参考文献。
- 在保存的正文、书目和图文件哈希范围内，仅引言源码发生变化；三项贡献保持。
- 无未定义引用、缺字或越栏。Ding 与 Bemani 的首次引用顺序改变，编号 10/11 对调，两版引用及书目同步。
- 受文字缩短影响的第 1–4 页已目视检查，两版对应页逐像素相同。第 8、9 页只有上述引用编号变化；参考文献页相应调整顺序。
- 一条 `Underfull vbox (badness 1412)` 为本次重排后的非阻塞提示，已检查相关页面，无遮挡或裁切。原有三幅图 PDF 版本提示保持。
- 未运行实验或训练，未修改其他论文稿件。

`before/` 保存原引言与两版 PDF/aux；[CHANGES.diff](CHANGES.diff) 为本轮局部差异；[VALIDATION.json](VALIDATION.json) 保存检查结果。出处及决定同步记录于本稿 `docs/TERMINOLOGY.md`、`docs/REVIEW_DECISIONS.md`。

## 后续：删除满分集句

作者反馈满分集对本文场景的动机作用有限，已删除第三段最后一句，保留低复杂度调制与 IFFT/逐点啁啾乘法两句，直接承接 JADCE。仅此一句正文删除；三项贡献及其他源码、图表保持。这里是叙事取舍，不否定已有文献在其条件下的结论。

两版重新编译成功，仍为 13/14 页、42 条参考文献、59 个公式标签；引用与公式编号保持，无 Overfull、Underfull、未定义引用或缺字提示。删句引起后续页面正常重排，已检查完整稿全篇布局预览；两版前四页逐像素相同。之前记录的 Underfull 提示在本轮消失。

本轮修改前副本、[差异](remove_diversity/CHANGES.diff)、[核验](remove_diversity/VALIDATION.json)及全篇布局预览保存在 `remove_diversity/`。本节描述当前版本，上文为前一步修订记录。
