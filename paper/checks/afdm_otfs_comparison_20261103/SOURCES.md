# 本轮公式与术语依据

本轮采用现有 LaTeX 项目的定点补丁、修订前源码备份和文件哈希核验。用户已确认四项修订安排；未把稿件转写为 Markdown，也不声称完成 ARS 的路线图或机器授权认证。只改变当前 C-STMP 稿件的论证与说明，不改变共用物理模型、算法或实验配置。

## 1. AFDM 矩阵分解

- Bemani, Ksairi, and Kountouris, *Affine Frequency Division Multiplexing for Next Generation Wireless Communications*, TWC 2023。
- [原文](https://arxiv.org/html/2204.12798v2)，II-B 式 (16) 及其后逆矩阵表达式，III-A 式 (18)。
- 原术语：discrete affine Fourier transform、inverse DAFT、chirp-periodic prefix。
- 本稿：附录 B 的 IDAFT 分解；每帧一次 N 点逆 FFT 与最多 2N 次复数啁啾乘法。L 帧的计数是从分解直接相加得到的本文推导，不作为该文原结论。

## 2. 多帧 OTFS 信道和资源

- Shen et al., *LEO Satellite-Enabled Random Access with Large Differential Delay and Doppler Shift*。
- [原文](https://arxiv.org/html/2412.20806v1)，II-B 式 (2)–(3)、(7)–(10)，Proposition 1。
- 原术语：effective channel、multi-frame transmission、delay-Doppler-space domain、phase rotation。
- 原文 M 个子载波、N 个时隙重命名为本稿 N 和 L；本稿 M 继续表示天线数。每个 OFDM 时隙加 CP，而非整个 OTFS 帧仅加一次 CP。
- 本稿表 I：显式稠密数组 MN² 与 MLN² 是索引计数；共同带宽和相同保护长度下，L 个 AFDM 帧与一个 OTFS 帧匹配时长和有用观测数。保护样本比例 N/(N+G) 相同。
- 本稿附录 B：给原文式 (9) 加上本文的每设备共同多普勒假设后，提取同一个 Doppler 核及接收位置相位；保留原文整数时延网格，用离散指示函数表示路径所在抽头。路径系数采用原文相位约定，以带波浪号的 g 区别本稿连续时间约定。这是本文的受限模型代数推导，不能称为 Shen 原论文的结论。
- 范围：原文允许逐路径不同多普勒且采用整数时延近似，本稿共同多普勒并显式保留分数时延。条目数差异不能推出自由度、可辨识性、导频或性能普遍优势。用于接收机的 AFDM 紧凑数组和标量帧演化在这些条件下成立。

## 3. 矩形脉冲 OTFS 的变换消去

- Wenjun Xu, Tingting Zou, Hui Gao, Zhisong Bie, Zhiyong Feng, and Zhiguo Ding, *Low-Complexity Linear Equalization for OTFS Systems with Rectangular Waveforms*, 2019, arXiv:1911.08133。
- [元数据](https://arxiv.org/abs/1911.08133)，[原文](https://arxiv.org/html/1911.08133v1)，II-A 式 (1)、II-B 式 (4)–(5)。新增引用键 `xu2019otfs`，与已有 `xu2026` 区分。
- 原术语：inverse symplectic finite Fourier transform、OFDM modulation、rectangular waveforms、transmit windows。
- 本稿：单位发射窗口和矩形脉冲下，F_N^H(F_N X_DD F_L^H)=X_DD F_L^H。因此一个 OTFS 帧的有用样本调制需要 N 次 L 点逆 FFT。正文不再将二维变换直接等同于更高调制复杂度。
- 范围：比较包含有用样本的变换，排除前缀生成与接收机推断；总发射能量需要另计前缀能量。

## 4. 原始实验依据

- `result/snr_comparison/data/c_stmp_ablation_1000_20261028/phase_only_20261029/GAUSSIAN_RETAINED_SUMMARY.json`。
- 使用全部 354 个已完成配对场景 × 6 SNR = 2,124 条件，每条件 40 台设备，共 84,960 次判决。学习证据错误 111+3=114；Gaussian evidence 错误 187+31,207=31,394。AER 分别为 0.1341808% 与 36.9515066%，按原表精度显示。
- Gaussian evidence 中 724 条件未收敛，仍进入指标。完整保存输出 2,128；另外 4 条未形成完整场景的输出保留。未重启实验、剔除异常样本、平滑曲线或生成新实验图。
- GP-MP 的 STMP 适配、二阶网络及分类器与 GP-MP-CCD 的导数方差、协方差条件化和查询方差更新，均保留在附录 C。正文以训练噪声名称区分方案，不声称其他实现完全一致。

## 5. 摘要

本轮未重写中英文摘要。英文摘要没有普遍 AFDM–OTFS 复杂度优势的表述，修订不引入与其数值或适用范围相矛盾的结论。当前性能结果和主张沿用已验证数据。
