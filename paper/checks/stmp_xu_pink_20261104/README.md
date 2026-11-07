# 按 Xu 原图确定 STMP 粉色

2026-11-04，作者明确要求采用 Xu 论文中的粉色。已从 [Surrey 开放机构库](https://openresearch.surrey.ac.uk/esploro/outputs/journalArticle/AFDM-aided-Grant-Free-Random-Access-for-LEO/991050765702346)下载接受稿并保存为 [xu2026_afdm_gfra_author.pdf](../../../reference/literature/xu2026_afdm_gfra_author.pdf)。含机构库封面共 14 页。

直接查看印刷第 12 页／PDF 第 13 页的图 9–11，并从 PDF 矢量路径提取 EP with sparse prior 曲线颜色：RGB `(1, 0.4, 0.6)`，8 位 RGB `(255, 102, 153)`，十六进制 **`#ff6699`**。不是截图估色或再次自行选择近似色。来源、SHA-256、页码、图号及该页颜色统计保存于 [XU_SOURCE.json](XU_SOURCE.json)，原页预览位于 `reference/`。

## 修改与核验

- STMP 的七幅实验图和双面板嵌套配置共九处颜色，从 `#ff6666` 改为 `#ff6699`；原圆圈、虚线、宽度、图例及坐标保持。GP-MP-C 继续用纯红 `#ff0000`。
- 后续白噪声版 GP-MP 和估计相位版 GP-MP-C-EP 同用纯红，以不同线型、标记区分；没有提前添加待完成结果。
- [绘图报告](PLOT_VALIDATION.json)通过输入哈希、547 个曲线点、图例边界与遮挡核验。与上一轮逐项比较，全部曲线值相同，七图均无位图嵌入。
- [总体核验](VALIDATION.json)逐图确认生成 PDF 包含与 Xu 相同的矢量颜色。两版论文编译成功，13/15 页，逐页文本保持，只有第 10–12 页渲染改变；TeX、书目及三幅方法图哈希保持，没有未定义引用、缺字或 Overfull 报告。
- 已查看新主 SNR 图和三张变动正文页，并与 Xu 原页核对。粉色与红色区分清楚，现有图例和文字无新增遮挡、裁切。未运行训练、推断或修改实验安排。

改前文件及哈希位于 `before/`、[before_hashes.json](before_hashes.json)，两版编译日志位于 `build_main/`、`build_full/`，成图与正文预览位于 `render/`。当前配色已写入统一绘图说明、图目录和讨论决定记录，取代此前两个临时粉色值。
