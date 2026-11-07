# 正文压缩与完整搭配修订

2026-11-03，按作者要求，对当前 main 及其共用正文进行删减，并核查完整术语搭配与具体操作的对应关系。范围包括摘要、I–VII、A–B、方法图；完整版附录 C 同步用词并收纳移出的实现说明。

## 完成内容

- 删除重复的索引顺序、张量维度、当前迭代方差、训练/推断提醒，以及泛泛的示意图免责声明。
- 将 moments 类概括写法改成具体的 mean and variance 或 mean and covariance；Fig. 3 两个节点标签同步，PDF/SVG/PNG 三格式重新导出。
- 改写 activity evidence、Gaussian-site probability、block-fixed、activity readout、first-order atom approximation、new-message weight、phase slopes、phase-policy、native convergence 等搭配。修改依据及保留项见[完整核查](TERMINOLOGY_AUDIT.md)。
- 完整停止检查、辅助容差与高精度归一化常数移至 main_full 的附录 C-G；正文保留停止逻辑与主要迭代设置。移出内容另存于 [IMPLEMENTATION_DETAILS.md](IMPLEMENTATION_DETAILS.md)。
- 修正术语账本把公式依据当成完整搭配证据的三处历史记录，保留修订历史并明确更正。

## 来源与边界

以 Cai 正式版及本地 v2、Shen 为主要语言参照；相关操作补核 Dytso、Shastri、Menon–Ong、Vehtari、Song、Karras、O'Leary–Rust 等原文。不是逐个单词找出处，也不因其他领域存在某搭配就保留它。

MFLE、GPJD、GP-MP、GP-MP-CCD、GP-MP-CCD-EP 是此前作者确认的本文名称。保留这些定义，并标明完整名称为本文组合；不误记为参考文献原名。未改变 STMP、DU 稿件的共用定义。

保留有关模型条件、已知/估计相位、genie 信息、评估重叠、选择性重跑、未收敛结果和回溯实验的具体事实。网络结构参照 Cai/Shen 的信息密度保留，未把复现所需设置统统视为多余细节。

## 检查

两版均用 Tectonic 成功编译：main 13 页，main_full 15 页。当前编入的 59 个编号数学环境与修改前逐字一致；引文与 42 篇书目保持；两张表中的数学数值保持。两版可见正文和图中均未检出 moment/moments。七幅实验图未修改，未运行训练或接收机实验。

无未定义引用、越界框或缺字警告。编译仍有行间松散提示及既有 PDF 版本提示。逐页渲染检查正文、图表和新增附录内容；重点核对第 6、8–10、12 页及完整版第 13–14 页，未见文字裁切或图表遮挡。

记录：[VALIDATION.json](VALIDATION.json)、[修改前快照](before)、[修改差异](CHANGES.diff)、[搭配证据](PHRASE_EVIDENCE.json)。数学检查只验证本轮未改变公式，不将其表述为重新证明全部理论。
