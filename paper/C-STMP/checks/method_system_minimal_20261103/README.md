# 系统图：删去解释性文字和推导公式

2026-11-03。按作者要求，重新查看 Cai v2 Fig.1／PDF p.4 与 Shen Fig.1／PDF p.3。Cai 的图主要标注设备状态、接收节点和资源维度；Shen 的公式用于说明图中距离与时延。本文系统图据此保留场景识别与局部结构标注，减少对第二章推导的重复。

删除跨帧信道等式、观测方程、共同延迟补偿文字及其流程箭头、阵列乘积式、共同活动状态长句和重复帧内标签。链路参数改为正文已有 TSL，保留 LEO satellite、UPA、M_y/M_z、Device k、Active/Inactive、K devices、帧编号和 CPP/AFDM 图例。共同活动、参考信道、相位与接收处理仍由第二章给出；图注只保留识图所需说明。

保持统一接入场景，将地面与阵列上移以收紧删除文字后的空间。尺寸从 396 × 214 pt 改为 396 × 194 pt。Shen Fig.1 的卫星、覆盖椭圆和 UPA 矢量图形及来源说明继续保留。没有新增术语或模型假设。

当前输出在 `../../figures/system_multiframe.pdf`、`.svg`、`.png`；PNG 为 600 dpi。`before/` 为改前系统图，`figure_inserts.tex` 为当前三图插入片段。已检查最终 PDF 的 Poppler 渲染及文字边界；PDF/SVG 无位图，PDF 字体内嵌。正文、阅读稿及另外两张方法图保持不变，核验见 `VALIDATION.json`。
