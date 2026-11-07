# 已知相位下的方向与公共矩阵消息：来源核对

核对日期：2026-09-28。综合：[研究报告](../../../paper/docs/KNOWN_PHASE_ITERATION_LITERATURE_REVIEW_20260928.md)。沿用项目 2026-09-24/26/27 的文献目录并重新核对本次关键论据，新增重点是 BAd-VAMP 观测参数更新、MVALSE-EP 接口、Cai 作者代码与论文的差异。

这是定向叙述性调研，不是数据库穷尽检索。F：作者/出版社全文 HTML 中已核对所列方法段；P：出版社可检索正文片段，未获得完整直接页面。F/P 表示访问范围，不是研究质量或人工阅读认证。未按网页行号引用 PDF 页码，未将预印本年份混称为正式发表年份。

## 纳入来源与定位

| ID | 作者、题名、核对版本 | 核对范围和用途 |
|---|---|---|
| R1 | Chang Cai, Wenjun Jiang, Xiaojun Yuan, Ying-Jun Angela Zhang. *Joint Activity Detection and Channel Estimation for Massive Connectivity: Where Message Passing Meets Score-Based Generative Priors*. [arXiv:2506.00581v2](https://arxiv.org/html/2506.00581v2), 2026-02-07。 | F。§III-B，式（15）–（16）、（24）–（30）、（35）–（38）；§IV-A 式（44）–（45）；§V 算法2、阻尼与功率归一化。核对学习矩、活动和外信息各自角色。正式发表信息另见[作者发表目录](https://chang-cai.github.io/publications.html)，本报告公式定位始终用 v2。 |
| R2 | Jisheng Dai, An Liu, Vincent K. N. Lau. *FDD Massive MIMO Channel Estimation with Arbitrary 2D-Array Geometry*. [arXiv:1711.06548v2](https://arxiv.org/html/1711.06548v2), 2018。 | F。§III-C–E、§IV；式（26）–（41）、附录E。固定后验的 EM 下界与角度小步更新。其 Gaussian 后验和驻点证明不直接覆盖本项目 score 循环。 |
| R3 | Subrata Sarkar, Alyson K. Fletcher, Sundeep Rangan, Philip Schniter. *Bilinear Recovery using Adaptive Vector-AMP*. [arXiv:1809.00024](https://arxiv.org/html/1809.00024), 所访问 v2, 2019；[DOI](https://doi.org/10.1109/TSP.2019.2916100)。 | F。§IV，算法3–4；式（61）–（71）的 q₂、均值和完整线性协方差；式（72）–（79）的仿射参数更新；§IV-D 的阻尼、负精度与局部解。非线性 UPA 只能借鉴组织方式后重新推导。 |
| R4 | Jiang Zhu, Lin Han, Rick S. Blum, Zhiwei Xu. *Multi-snapshot Newtonized Orthogonal Matching Pursuit for Line Spectrum Estimation with Multiple Measurement Vectors*. [arXiv:1802.01266v3](https://arxiv.org/html/1802.01266), 2019-05-08。 | F。§III-A/B，式（3）–（10）、算法1；§IV 式（11）–（16）。解析消去幅度、残差候选、循环精修及检测条件。原模型不是带固定用户导频标识的 JADCE。 |
| R5 | Jiang Zhu, Qi Zhang, Peter Gerstoft, Mihai-Alin Badiu, Zhiwei Xu. *Variational Bayesian Line Spectral Estimation with Multiple Measurement Vectors*. [arXiv:1803.06497v2](https://arxiv.org/html/1803.06497)。 | F。§III，式（13）–（20）、（21）–（26）；附录VIII-B；§VI-A/B。方向分布、幅度交叉协方差及支持点估计。性能段也有低快照数下多估分量的例子，不能推断方向分布必然改善检测。 |
| R6 | Qi Zhang, Jiang Zhu, Ning Zhang, Zhiwei Xu. *Multidimensional Variational Line Spectra Estimation*. [arXiv:1912.11759v1](https://arxiv.org/html/1912.11759), 2019-12-26；IEEE SPL 2020，[DOI](https://doi.org/10.1109/LSP.2020.2995107)。 | F。§III，式（9）–（13）、频率更新与算法概述；多维频率及独立 von Mises 投影。未把其支持点估计说成完整支持后验。 |
| R7 | **Ning Zhang, Jiang Zhu, Zhiwei Xu**. *Gridless Multisnapshot Variational Line Spectral Estimation from Coarsely Quantized Samples*. [arXiv:1906.08418v2](https://arxiv.org/html/1906.08418), 2022-06-07。 | F。§IV-B，式（90）–（108）、算法1。量化观测和结构模块之间 Gaussian 投影/消息相除；重构均值及方差。特别核对作者和 v2，避免与 Zhu、Zhang、Meng 的单快照 VALSE-EP 文章混淆。HTML 式（102）有渲染杂符号，未照录为本项目公式。 |
| R8 | Keke Ying et al. *Quasi-Synchronous Random Access for Massive MIMO-Based LEO Satellite Constellations*. [arXiv:2304.04484v1](https://arxiv.org/html/2304.04484), 2023-04-10。 | F。§II-B 同用户公共 AoA；§III-B–C，算法1–2。核对 OAMP-MMV 初估与已检出用户的 2D-ESPRIT 后处理顺序。本次不讨论其同步方案迁移。 |
| R9 | Ke-Xin Li, Xiqi Gao, Xiang-Gen Xia. *Channel Estimation for LEO Satellite Massive MIMO OFDM Communications*. [arXiv:2207.11958](https://arxiv.org/html/2207.11958)。 | F。§II-B–C 已知慢角度及统计信息假设；§IV 两阶段处理、式（29）–（31）。用作分解模型与处理顺序的参照，不能用作未知角度估计的验证。 |
| R10 | Yiming Zhu, Jiawei Zhuang, Gangle Sun, Hongwei Hou, Li You, Wenjin Wang. *Joint Channel Estimation and Prediction for Massive MIMO with Frequency Hopping Sounding*. [arXiv:2406.09053v1](https://arxiv.org/html/2406.09053), 2024-06-13。 | F。§IV-A/B 的受约束自由能与算法1；§IV-C 式（38）–（43）及低复杂度近似。只按已读预印本引用，未补造正式刊卷页码；HTML 式（42）符号不作为本项目推导的直接模板。 |
| R11 | Haichen Shen, Chongbin Xu, Xiaojun Yuan, Xin Wang. *Diffusion-Enhanced Multidimensional Variational Line Spectral Estimation*. Electronics **15**(9), 1927, 2026-05-02。[出版社](https://www.mdpi.com/2079-9292/15/9/1927)；[DOI](https://doi.org/10.3390/electronics15091927)。 | P。出版社索引显示摘要、§3.1–3.3、算法1–2和复杂度段。直接 open 失败；不声称读完全部附录。确认先扩散去噪、再有色噪声 MDVALSE，不能直接替代单次 score TMP。 |
| C1 | Chang Cai 作者仓库：[score-massive-connectivity](https://github.com/chang-cai/score-massive-connectivity)，提交 `0c75680c966dcb8e46250de146f4c27e9294c283`。 | 仓库由作者发表页 Code 链接核验。读取 `main_stmp_jadce.py`、README 和 LICENSE；文件第192、212–231行活动检测采用固定 Gaussian，而论文式（30）用学习外信息。第141–144行是专用导频结构的线性更新。仅源码审查，未执行，不推断隐藏版本。 |

## 不纳入核心方法结论的检索线索

- *Parametric Bilinear Generalized Approximate Message Passing*，arXiv:1508.07575：只作为更一般双线性推断线索，本轮未逐步核对其完整更新，不据此建议直接采用。
- *Bilinear Vector Approximate Message Passing-Based Off-Grid Channel Estimation for OTFS Systems*，VTC2024-Fall，[IEEE 摘要](https://ieeexplore.ieee.org/document/10757914/)，DOI 10.1109/VTC2024-Fall63153.2024.10757914：只取得出版页摘要；可确认存在 OTFS 离网格应用，不能据此称其解决我们的未知 UPA/score/JADCE 接口。
- 一般 RIS、波束赋形、AFDM ISAC、同步/预测文章如未提供上述消息接口，不用于支撑本项目的具体迭代顺序。二次聚合页只用于发现线索。

## 本地审查与复现范围

本项目交叉核对：`docs/POINT_DIRECTION_REPAIR_20260928.md`、`docs/KNOWN_REFERENCE_COMPARISON_20260924.md`、`docs/CAI_ADAPTATION_SCOPE_20260928.md`、当前 `score_mp/point_direction.py`、`score_mp/moment_iterations.py` 以及 `algorithm/legacy/known_direction.py`。此前文献报告与新一轮实验结果按各自日期保留。

作者代码原样保存在 `cai_official_main_stmp_jadce.py.txt`，附原 `CAI_CODE_LICENSE.txt`；SHA-256 为 `7e364f6c33962639b8fa1a5090b93b0d68db93de26e99192a3ff4f5ca3e8dbcd`。GitHub API 遇到速率限制后，使用公开 `git ls-remote` 核定 main 提交，再按提交地址保存源码。

本次仅新增小规模确定性代数验证：观测重排、有色协方差配方、用户块对角与完整协方差的方向依赖、单用户方向目标展开、方向不确定性下的重构协方差。可执行 `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 .venv/bin/python references/known_phase_iteration_review_20260928/check_algebra.py` 复现；不是接收机 Monte Carlo 实验。

跨论文候选对只覆盖与当前设计决策有关的比较，见 `cross_paper_tensions.json`，不声称全体论文两两穷尽核验。`scholar_confirmation` 保持 pending，未代替用户登记人工确认。
