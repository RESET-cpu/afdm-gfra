# 名称简化为 GP-MP-C

> 本轮历史图和绘图脚本已移入归档；当前生图入口见 [统一说明](../../../../src/evaluation/plots/manuscript/README.md)。以下记录描述当时版本。

2026-11-04，作者在质疑 covariance-conditioned 后明确选择“就用 C”。

| 对象 | 旧展示名 | 当前展示名 |
|---|---|---|
| 本文主算法 | GP-MP-CCD | GP-MP-C |
| 估计相位版本 | GP-MP-CCD-EP | GP-MP-C-EP |
| 白噪声训练基线 | GP-MP | GP-MP |

C 是本文有色高斯噪声训练版本的标记。引言首次出现 GP-MP 时补 generative-prior message-passing；第五章首段说明 C 的含义。第四章将 condition the network on C 改为 provide C as an additional network input，评估协议直接写 denoiser trained with colored Gaussian noise。没有新增方法或改变协方差输入。

当前正文、Algorithm 1 标题、六幅接收机比较图例及两版 PDF 已同步。目录名、内部标签、C_STMP 实现标识、配置及冻结结果仍使用原标识；历史记录保留当时名称。连续通读 R01 已解决；R02 图注精简未获选择，保持现状。

## 检查结果

- 两版编译成功，主稿 13 页、完整稿 14 页，42 篇参考文献。数学表达式和算法运算与修改前逐项一致，原公式标签及编号保持；没有未定义引用或 overfull 警告。
- 六幅图沿用已批准的布局、线型、配色、画布尺寸及字号（图例 8 pt，坐标轴 8.5 pt），505 个数据点与保存结果一致。图 9 NMSE 为 −20～0 dB，AER 为 10⁻⁴～10⁻¹；超出范围按原值连线后裁切。
- 图 1–3 全部格式、图 4 去噪 PDF 及参考文献文件逐字节保持。没有运行训练或推断。
- 已检查六幅图和变动稿页，图例完整，未发现重叠、缺字或裁切。主稿变动页为 2、6、7、9–12；完整稿变动页为 2、6、7、9–13。

[重绘入口](../../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/algorithm_name_c_20261104/render_figures.py) · [曲线核验](RENDER_VALIDATION.json) · [源码差异](SOURCE_DIFF.txt) · [核验入口](../../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/algorithm_name_c_20261104/verify_revision.py) · [核验结果](VALIDATION.json) · [修改前备份](before/) · [预览](previews/)

[主稿 PDF](../../main.pdf) · [完整稿 PDF](../../main_full.pdf)

六幅独立图：[收敛](../../figures/convergence.pdf)、[SNR](../../figures/snr_comparison.pdf)、[用户数](../../figures/user_count.pdf)、[活动概率](../../figures/activity_probability.pdf)、[导频帧数](../../figures/pilot_frames.pdf)、[跨信道](../../figures/cross_channel.pdf)。
