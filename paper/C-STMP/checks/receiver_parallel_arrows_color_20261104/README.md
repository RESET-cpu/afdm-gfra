# 图 3：平行双向箭头与局部配色修正

> 本轮历史图和绘图脚本已移入归档；当前生图入口见 [统一说明](../../../../src/evaluation/plots/manuscript/README.md)。以下记录描述当时版本。

2026-11-04，按作者对上一版的纠正完成以下调整：

- MFLE 向下、GPJD 向上的消息使用两条平行直箭头，取消左侧绕行反馈线。
- 左侧 MFLE 为加粗深绿边框与浅绿填充，GPJD 为加粗红色边框与浅红填充；名称仍为黑色加粗。
- 右侧展开图使用 1.4 pt 黑色外框，删除其中重复的 GPJD 标题。
- 内部运算文本框和模块间连接线保持黑色。神经网络恢复前一彩色版本的绿／灰／红节点及灰色网络连线，信道数组恢复红色边框与浅红底色。

此次明确纠正上一轮将“文本框换成黑色”扩大为网络、数组全部灰度化的理解。后续按本记录执行；不将内部图示全黑化，也不再给展开框着红色。

图宽高保持 468×158 pt，文字与内部布局保持。没有改动 TeX、图注、公式、伪代码、图 2 或实验图。PDF/SVG/600 dpi PNG 已同步导出，两版稿件重新编译。

[图 3 PDF](../../figures/learned_receiver.pdf) · [预览](../../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/receiver_parallel_arrows_color_20261104/preview/learned_receiver.png) · [重绘入口](../../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/receiver_parallel_arrows_color_20261104/draw_receiver.py) · [核验](VALIDATION.json)

主稿 13 页、完整稿 14 页，46 个编号公式和 42 篇参考文献保持；逐页渲染比较仅第 7 页变化，两版第 7 页图像相同。独立图和论文第 7 页已目视检查，没有发现裁切或重叠。PDF 保留矢量路径，无嵌入位图。修改前副本保存在 `before/`，资产哈希见 `BEFORE_HASHES.json`。
