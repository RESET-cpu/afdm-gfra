# 图 3：按流程核对结果修正五处表达

> 本轮历史图和绘图脚本已移入归档；当前生图入口见 [统一说明](../../../src/evaluation/plots/manuscript/README.md)。以下记录描述当时版本。

2026-11-04。作者授权执行 [F01–F05 流程核对建议](../../docs/FIGURE3_FLOW_AUDIT_20261104.md)。本轮修改图 3，不改变算法、公式或实验。

| 项目 | 已实施 | 依据与复核 |
|---|---|---|
| F01 分类器输入 | R_k,v 与 F_k 两条依赖在网络外汇合，经一个输入端进入分类器；标出 z_phi(R_k,v,F_k) 与输出 ell_k | IV-D 式 (31)、(33)；实现先构造输入特征。没有任何来自 F_k 的箭头进入隐藏层 |
| F02 方差估计 | 从输入处分出独立支路；有限差分框显示 f_theta 在 u±delta_FD w_l 处的调用及式 (29)，再经 Average over k 得到 taupost | IV-C 式 (29)、Algorithm 1 的跨设备平均。复用同一 theta，不绘制第二网络或单次前向的方差输出头；固定下限仍由算法说明 |
| F03 site/条件矩 | 原运算框增加 Gaussian site 名称，保留 H_k^post,t_k 与式 (34)、(35) | V-A 及 Algorithm 1：框表示 site 更新和条件矩计算；不将 H_k^post 无条件等同于 F_k。site 保留条件由现有伪代码表达，未再铺开判断分支 |
| F04 共同方差 | 联合矩框输出改为 Xhat_k、tbar_X，保留式 (19)–(21) | III-B3：C_X,k 是中间量，外信息计算直接使用共同标量方差 tbar_X |
| F05 外信息与反馈 | 分成 Extrinsic (22) 与 Damping (39)，中间标 X_k,out、gamma_out，末端才标 X^pri、gamma | III-B3、V-B、Algorithm 1 的既定次序。第一轮及历史状态规则继续按伪代码，不额外添加贯穿图面的反馈线 |

保留左侧平行反向箭头、浅绿/浅红模块、加粗黑色展开框、黑色操作框与连接箭头。网络蓝／浅绿／橙配色、含噪/去噪后切片及共同色标与上一版完全一致；没有换样本、重新推断或重新训练。原数据来源复制记录于 [DENOISING_SOURCE.json](DENOISING_SOURCE.json)。

## 输出与核验

[图 3 PDF](../../figures/learned_receiver.pdf) · [预览](../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/receiver_flow_corrected_20261104/preview/learned_receiver.png) · [绘图入口](../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/receiver_flow_corrected_20261104/draw_receiver.py) · [核验记录](VALIDATION.json)

原生尺寸仍为 468×158 pt，主文字 8–9.5 pt。PDF/SVG/600 dpi PNG 同步，PDF 无嵌入位图。已检查输入箭头的真实端点、标签、边框内文字范围和前后切片的相同色标，并对独立图及论文第 7 页目视检查，无观察到的重叠或裁切。

全部 TeX、其他图像及书目与修改前哈希一致；只更新图 3 的三格式和两版 PDF。主稿 13 页、完整稿 14 页，46 个编号公式及 42 篇参考文献保持；逐页渲染比较只有第 7 页变化，两版第 7 页一致。修改前副本保存在 `before/`。
