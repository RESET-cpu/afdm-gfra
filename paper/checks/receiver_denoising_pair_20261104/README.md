# 图 3：补全去噪前后对照

> 本轮历史图和绘图脚本已移入归档；当前生图入口见 [统一说明](../../../src/evaluation/plots/manuscript/README.md)。以下记录描述当时版本。

2026-11-04。作者认为上一版神经网络和信道矩阵配色仍需调整，并指出未体现 Cai 图中的去噪过程。

## 原图核对与修正

重新逐项检查 Cai 期刊版 Fig. 3，PDF p.10／印刷 p.3584（本轮参考页保存在 `references/cai2026_10.png`）。原图将含噪输入、网络、后验信道和外信息信道依次排列；含噪与去噪后矩阵的纹理对照承担了直观说明作用。此前版本采用了网络矢量形状，却用空网格表示输出且省略输入矩阵，没有完整保留这条视觉逻辑。

本轮在右侧展开图加入同一份输入 R_k 与实际去噪输出 F_k 的三张天线切片，并在网络下保留既有名称 Denoiser。网络改为蓝／浅绿／橙节点，信道幅度使用统一的 viridis 色标。两矩阵间保留本文 F_theta 的直接去噪关系；其后的条件矩、活动概率、联合矩和外信息更新继续按本文公式表示。下方 z_phi 仍为本文分类器，不把 Cai 的二阶 score 网络移植到本图。

左侧平行反向直箭头、浅绿/浅红模块、黑色加粗展开框、黑色内部文本框和连接箭头保持；展开框不重复写 GPJD。图 2 不变。

## 输入输出数据

图中不是空网格或人为平滑生成的纹理，使用已保存的独立 AWGN 去噪实验样本：

- 文件：`result/channel_denoising/data/colored_first_500_20261025_v2/scene000_predictions.npz`。
- 固定选取第一个场景、第一份设备样本（原用户索引 7），v=1，前三根天线。
- 输入为 `query[3,0,:3]`，输出为 `estimate[3,0,:3]`，均显示复数幅度。
- 六张切片统一线性范围 0 至共同最大值，无单独拉伸、滤波或平滑。
- 该文件属于有色噪声训练的第一网络在 C=vI 下的已有测试。仅用于说明去噪模块，不作为新增闭环接收机实验。

来源、选择规则、文件哈希与具体色标上限见 [DENOISING_SOURCE.json](DENOISING_SOURCE.json)。已验证保存输入与真值/噪声对应，保存预测与原实验误差记录一致；没有重新运行推断或训练。绘图读取原结果，未改任何实验文件。

## 交付与核验

[图 3 PDF](../../figures/learned_receiver.pdf) · [预览](../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/receiver_denoising_pair_20261104/preview/learned_receiver.png) · [绘图入口](../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/receiver_denoising_pair_20261104/draw_receiver.py) · [核验记录](VALIDATION.json)

尺寸仍为 468×158 pt，PDF/SVG/600 dpi PNG 同步。矩阵以矢量色块绘制，PDF 无嵌入位图。修改前副本在 `before/`。

仅图 3、相应图注及两版 PDF 改变；其他 TeX、图像及书目与修改前逐文件一致。主稿 13 页、完整稿 14 页，46 个编号公式、42 篇参考文献保持。逐页比较只第 7 页发生变化，两版第 7 页相同。独立图与论文第 7 页已目视检查，无观察到的重叠或裁切。
