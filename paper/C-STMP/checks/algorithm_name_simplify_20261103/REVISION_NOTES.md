# 算法名称及曲线样式统一

2026-11-03，按作者本轮连续指示采用以下最终名称与样式：

| 实验标识 | 正文与图例 | 颜色 | 线型 | 标记 |
|---|---|---|---|---|
| `STMP` | GP-MP | 红色 `#b83253` | 虚线 | 圆点 `o` |
| `C_STMP` | GP-MP-CCD | 红色 `#b83253` | 实线 | 方块 `s` |
| `C_STMP_phase_selected` | GP-MP-CCD-EP | 红色 `#b83253` | 虚线 | 三角 `^` |

GP 为 generative prior，MP 为 message passing，CCD 为 covariance-conditioned denoising，EP 表示 estimated phases。以上组合为作者批准的本文描述性名称，不归为已有文献的原名。主算法原名 GP-CCD-MP-DRE；本轮删除 DRE 后缀并调整 CCD 的位置。密度比估计、活动概率学习、公式和消融表均继续保留。EP 仅用于估计相位版本的名称；正文 expectation propagation 的含义不变。

## 基线归属与出处

原实验标识 STMP 对应本文三网络实现，已包含学习式活动证据。正文现在称其为 GP-MP，明确其沿用 Cai 的 STMP 框架并适配 AFDM，同时以学习活动证据替换解析更新。引用 Cai 原方法时仍使用 STMP。

- Cai v2 §III-B、§V-A（项目提取原文 `reference/reviews/stmp_message_awgn_review_20261024/text/23_cai2026_stmp.txt` 第 1734–1741 行）明确原 STMP-JADCE 的信道去噪使用两套得分网络，活动去噪和线性估计由解析推导得到。保存的作者代码 `reference/reviews/known_phase_iteration_review_20260928/cai_official_main_stmp_jadce.py.txt` 第 193–229 行调用 Gaussian 活动规则。
- 本项目 `src/algorithm/STMP/denoiser.py` 第 151、171–172 行使用分类器 logit 和先验比得到活动概率；`moments.py` 第 31 行起加载一阶与二阶网络。
- 当前主算法的均值与导数方差读出位于 `src/algorithm/C_STMP/moments.py`；查询方差自适应位于 `src/algorithm/C_STMP_variance_em_20261025/iterations.py` 第 14–20、47–57 行。第 VI-A 节保留这些实际配置差异，因此名称中的 CCD 不被解释为全部性能差异的唯一来源。
- generative prior、message passing、covariance-conditioned denoising、density ratio estimation 的技术含义和已有出处沿用术语账本：Cai §III–V；Shastri §III-B；Karras §5；Menon–Ong §4.2。没有新增技术模块或公式。

## 修改与复现范围

第五章标题、首次定义、Algorithm 1、第六章、附录 C、当前导航文档和六幅比较图同步新名称。白噪声基线的定义及估计相位版本的名称在 VI-A 集中交代；SNR 图注说明相位条件。第三、四章、摘要、所有模型参数、实验数据及存储标识保持。

五幅图使用 `render_five_figures.py` 从已核验的历史绘图入口派生；SNR 使用 `render_snr.py` 读取当前七曲线、每档 500 场景的 `PLOT_DATA.json`。数值逐点与源数据核对，合计 505 点。其余四种基线的曲线样式保持；本轮未编辑独立去噪图及三张方法图。工作区同时进行了因子图彩色分区修订，编译保留了该版本，详见 `../factor_graph_region_frames_20261103/README.md`。

未运行接收机推断、批量实验或训练。历史命名记录、冻结绘图引擎、结果目录和原始统计保持；修改前快照及哈希见 `before/` 与 `BEFORE_HASHES.json`。`RENDER_VALIDATION.json` 和 `SNR_VALIDATION.json` 保存重绘核验，完整文稿检查见 `VALIDATION.json`。

## 编译与检查

当前完整稿为 16 页。Tectonic 编译成功，无未定义引用、缺字或越界警告；原有 underfull 和图形 PDF 版本提示不影响本次显示。检查了六幅新图与完整稿 16 页，未见文字裁切或图例遮挡。数学表达、公式标签、Algorithm 1 的算法步骤及 505 个绘图点保持，SNR 图的三个新标签与三种指定样式均核对通过。
