# 原图矢量改绘：三张方法图

2026-11-03。按作者反馈，撤换上一版大色块流程图。当前版本直接提取并改绘项目内参考论文的矢量图形，尽量保留原布局、形状、比例与连线。此次只修改方法图及图文件说明。

## 原图与具体改动

| 输出 | 直接采用的原图元素 | 本稿替换内容 |
|---|---|---|
| `system_multiframe` | Shen Fig.1 / PDF p.3：卫星、地面椭圆、活动与非活动设备、链路、UPA；Cai v2 Fig.1 / p.4：资源格子的单元、边线和坐标轴 | 灰蓝统一配色；差分时延、设备公共 Doppler、M_y/M_z；AFDM 帧与 chirp subcarrier 标签、IDAFT/CPP、共同活动状态及跨帧相位关系。删除原图解释框，保留紧凑公式。 |
| `factor_graph` | Cai v2 Fig.2 / p.5 的完整矩阵、节点位置、分支、圆节点、黑方形因子及行列底纹 | 最后一列与列似然的 M 改为 MN；p(H_k) 改为 q_tr(H_k)；Module A/B 改为 Linear estimation / Joint denoising；保留原来的列与设备块重组关系。因编辑相邻字体对象而丢失的矩阵括号按原位置恢复。 |
| `learned_receiver` | Cai v2 Fig.3 / p.10 的小因子图与局部放大构图；直接提取原网络的圆节点、层间连线和箭头，每个网络保留 71 个原矢量路径对象 | 小图采用上面已适配的因子图；上方为均值网络 F_theta，下方改为密度比分类器 z_phi；方差从同一个均值网络的有限差分获得；增加 Gaussian site、联合矩与反馈关系。信道图片替换成符号化张量切片，不表示数据取值。 |

源文件：`reference/literature/shen2025.pdf`、`reference/literature/cai2026_stmp_v2.pdf`。原图裁剪预览与解析记录在 `sources/`。Ding、Huang 曾用于前一轮方案比较；当前版本没有直接采用它们的图形，因此当前图注不列为改绘来源。

这版是**原图改绘**，不再标为独立原创绘图。图注使用 “Adapted from” 并标注文献与图号；来源登记与图形改动一同保留。

## 符号及技术核对

- 系统图对应 II 的 physical-channel、upa、effective-pilot、mmv；公共时延在卫星接收端补偿。资源格子的底纹仅突出显示两个帧列，全部 Q 帧用于导频观测。
- 因子图对应 working-posterior：列似然、设备关系因子、完整 q_tr(H_k)、活动先验 p(alpha_k)。其中 x_{kn,j} 表示 X 的第 (k,n) 行、第 j 列，j=1,...,MN。矩阵内部连接表示同一变量的重组，不是新增概率依赖。III 仍使用通用模块描述。
- 接收机图对应 IV 的 colored-query、derivative-trace、activity-probability 与 V 的 pooled-variance、site-update、conditional-moments。上方网络按有色协方差训练，在线在 vI_D 求值；分类器用白噪声两类样本训练，输入 R_k、v、F_k。方差支路共享 F_theta。tau 表示按 V-A 平均及加下限后的共用方差。
- Gaussian site 还使用当前 R_k、v，得到 mu_k、t_k；二者与 p_k 合成联合矩，结合当前 R_k、v 输出 Gaussian extrinsic message。图表示训练范围内采用学习器的主要关系；完整调度沿用 Algorithm 1。
- 网络图标沿用原文抽象画法，不把圆点数量解释为实际网络层数或宽度。张量切片是符号示意，不沿用原论文的信道热图或实验数据。

## 文件及验证

正式输出见 `../../figures/`，每张都有 PDF、SVG、600 dpi PNG。系统图与接收机图宽 177.8 mm，因子图保留接近原图的单栏比例，原生宽 94.9 mm；可按单栏宽度排版。SVG 将文字转为矢量路径，避免跨电脑字体替换；PDF 保留内嵌字体。

PDF 与 SVG 均不含嵌入位图。已用 Poppler 从实际 PDF 渲染，并检查符号、矩阵括号、节点、线条和边界。格式、尺寸和散列见 `EXPORTS.json` / `VALIDATION.json`。旧版九个图文件及说明保存在 `before/`。

`main.pdf` 与正文没有改动，七张实验图保持。当前插入片段为 `figure_inserts.tex`，尚未编入正文。

## 再次修改

绘图入口为 `adapt_figures.py`。在项目根目录运行：

```powershell
& .\.venv\Scripts\python.exe paper/C-STMP/checks/method_figures_source_adaptation_20261103/adapt_figures.py
```

依赖项目 Matplotlib，以及用户缓存 `C:/Users/25911/.cache/codex-pymupdf` 中的 PyMuPDF。脚本从原 PDF 提取矢量元素，按坐标替换文字和配色，再输出三个格式；不会启动训练或实验。
