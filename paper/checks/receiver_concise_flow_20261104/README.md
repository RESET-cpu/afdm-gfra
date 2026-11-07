# 图 3：精简实现细节

> 本轮历史图和绘图脚本已移入归档；当前生图入口见 [统一说明](../../../src/evaluation/plots/manuscript/README.md)。以下记录描述当时版本。

2026-11-04。作者指出有限差分标签、阻尼框及解释性文字使图面再次变复杂。本轮简化图 3，保留上一轮已修正的数据依赖。

- 删除 Finite differences、扰动调用表达式及 Average over k；以一个紧凑框展示各设备 tauhat_k 到共同 taupost 的关系，并引用式 (29)。支路仍从输入分出，不把单次去噪输出误作方差估计的充分输入。
- 删除单独的 Damping (39) 框。展开图止于式 (22) 的原始外信息 X_k,out、gamma_out；左侧总览仍表示完整迭代的反馈状态 X^pri、gamma。数值阻尼由已有正文与 Algorithm 1 交代。
- 删除重复的 Denoiser 标签，将分类器名称缩短为 z_phi；R_k,v 与 F_k 在网络外汇合，ell_k 输出及活动概率路径保持。
- 保留 Gaussian site、联合均值和共同标量方差、Extrinsic 等必要角色与输出，不增加说明句或新模块。

Finite differences 指有限差分，是通过微小扰动近似导数的数值操作。已核对 Metzler 2016 作者稿 [PDF p.15、§V-B](../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/formula_prototypes_20261104/metzler2016_damp.pdf)，原小节名称是 Monte Carlo method；该处给出随机扰动的导数/散度估计，并未将 Finite differences 用作模块名称。本文中央差分、随机符号及协方差加权属于当前式 (29) 的具体适配，不能声称逐式照搬原文。删除图内标签不改变现有公式或正文说明。

左侧平行反向箭头、浅绿/浅红模块、黑色展开框和内部框线、网络蓝/浅绿/橙配色及 viridis 信道配色保持。沿用同一保存样本、三张天线切片和共同幅度色标，来源见 [DENOISING_SOURCE.json](DENOISING_SOURCE.json)；未运行推断、训练或实验。

## 输出与核验

[图 3 PDF](../../figures/learned_receiver.pdf) · [预览](../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/receiver_concise_flow_20261104/preview/learned_receiver.png) · [绘图入口](../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/receiver_concise_flow_20261104/draw_receiver.py) · [核验记录](VALIDATION.json)

三格式同步，尺寸仍为 468×158 pt，PDF 无嵌入位图。核对全部 1536 个热图单元、箭头端点及变量/公式对应；独立图与论文第 7 页已目视检查，无观察到的裁切或重叠。主稿 13 页、完整稿 14 页，46 式及 42 篇参考文献保持；仅第 7 页渲染变化，两版该页一致。全部 TeX、其他图、书目及原数据未改。修改前副本位于 before/。
