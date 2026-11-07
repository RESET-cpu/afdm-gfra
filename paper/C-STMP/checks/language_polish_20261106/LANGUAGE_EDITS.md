# 语言润色与来源对照（2026-11-06）

本轮以已确认的学术主线为基线，对照 Cai、Shen 的完整相关段落，辅助阅读 Huang 和 Xu 的领域表达。通读英文摘要、引言、正文 II–VII 及当前编入的评估协议附录；采用 14 处语言调整，不增加贡献、假设或实验结论。

## 读取范围与适用层次

- Cai，IEEE JSAC 期刊版，`reference/literature/cai2026.pdf`：§II-A/B（PDF pp.3–5／印刷 pp.3577–3579），§III 开头与 §III-A（PDF p.5），§IV-A/B（PDF pp.8–9），§VI-B/C 的去噪与性能比较（PDF pp.12–13）。重点核对模型目标、两模块交换、未知 score 到 DSM 的衔接、以 NMSE 为主语的性能比较。
- Shen，`reference/literature/shen2025.pdf` 本地版本：§II 与 §II-A（PDF p.3），读取完整系统段及相邻链路模型段。维持本文无预补偿场景和 AFDM 模型，修正搭配而不移入 OTFS 或同步条件。
- Huang，IEEE WCL 期刊版，`reference/literature/huang2026.pdf`：摘要和 §I 开头（PDF p.1／印刷 p.2949）。核对双选择性环境与 AFDM 的技术语境；不是用其性能程度词修饰本文。
- Xu，IEEE TCOM 接受稿，`reference/literature/xu2026_afdm_gfra_author.pdf`：仓库封面与正文首页（PDF pp.1–2），辅助核对 AFDM-GFRA 的场景与论文表达。其摘要研究检测及性能界，未将技术主张移植到本稿，也未将其列为某个改句的直接母本。

Cai 与 Shen 已分别提供 JSAC、TWC 的相关文风样本，不另外为期刊名堆积无关论文。普通语法修正与本文实现说明如实标注为本稿编辑，不冒称文献原句。摘要、引言三项贡献、结论的措辞已在前轮确认，检查后保留；正文里有明确概率含义的 conditional／posterior 不机械删除。

## L01 · sections/02_system_model.tex（当前第 5 行）

压缩 effect inherent in 的名词搭配，保留模型对象和作用。

原文：

```tex
as shown in Fig.~\ref{fig:system-multiframe}, where AFDM is adopted
to mitigate the doubly dispersive effect inherent
in terrestrial-satellite links (TSLs) \cite{shen2025,huang2026}.
```

改后：

```tex
as shown in Fig.~\ref{fig:system-multiframe}, where AFDM is adopted
to mitigate the effects of doubly dispersive terrestrial-satellite
links (TSLs) \cite{shen2025,huang2026}.
```

依据及适配范围：Shen §II 开头，PDF p.3；Huang §I，PDF p.1／印刷 p.2949。原搭配来自 Shen，本次是自然语法调整，不声称逐字复制。

## L02 · sections/02_system_model.tex（当前第 236 行）

精简重复的研究目的引式及 corresponding／based on。

原文：

```tex
In this paper, we aim to simultaneously detect the active devices and
estimate the corresponding channels based on the observation $\mathbf Y$
under a Bayesian inference framework \cite{cai2026}.
```

改后：

```tex
Our goal is to jointly detect active devices and estimate their channels
from the observation $\mathbf Y$ within a Bayesian inference framework
\cite{cai2026}.
```

依据及适配范围：Cai §II-B 首段，PDF p.4／印刷 p.3578；保留其目标—观测—Bayesian framework 关系，仅作语言压缩。

## L03 · sections/03_bayesian_receiver_design.tex（当前第 10 行）

用估计器作为主语，直接说明外信息交换。

原文：

```tex
Information is exchanged between the two estimators through Gaussian
extrinsic messages based on expectation propagation \cite{minka2001}.
```

改后：

```tex
The two estimators exchange Gaussian extrinsic messages based on
expectation propagation \cite{minka2001}.
```

依据及适配范围：Cai §III 开头与 §III-A，PDF p.5／印刷 p.3579；Minka 既有出处保持。原句被动改主动，无新技术结论。

## L04 · sections/04_generative_priors.tex（当前第 16 行）

明确堆叠结果与向量定义的关系。

原文：

```tex
real and imaginary parts of $\vect(\mathbf H)$ in $\mathbf h_{\mathbb
R}\in\mathbb R^{2D}$.
```

改后：

```tex
real and imaginary parts of $\vect(\mathbf H)$ to form $\mathbf h_{\mathbb
R}\in\mathbb R^{2D}$.
```

依据及适配范围：本文已有实坐标表示，仅调整介词搭配；不将其说成采用复坐标的 Cai 原句。

## L05 · sections/04_generative_priors.tex（当前第 57 行）

连接未知边缘 score 与可计算条件 score，避免连续短句割裂 DSM 动机。

原文：

```tex
The score of $q_v^{\mathbb R}$ is unknown.
For the conditional Gaussian density in \eqref{eq:training-query}, the score
is $-2(\mathbf u-\mathbf h_{\mathbb R})/v$.
```

改后：

```tex
Although the score of $q_v^{\mathbb R}$ is unknown, the conditional
Gaussian density in \eqref{eq:training-query} has score
$-2(\mathbf u-\mathbf h_{\mathbb R})/v$.
```

依据及适配范围：Cai §IV-B，PDF pp.8–9／印刷 pp.3582–3583，式 (46)–(49) 前后完整段；本稿实坐标系数和加权目标保持。

## L06 · sections/05_overall_algorithm.tex（当前第 50 行）

修正章节充当估计执行者的主语问题。

原文：

```tex
When phases are unavailable, Section~\ref{sec:phase-estimation} estimates
them once before MP and keeps them fixed throughout the iterations.
```

改后：

```tex
When phases are unavailable, we estimate them once before MP using the
method in Section~\ref{sec:phase-estimation} and keep them fixed throughout
the iterations.
```

依据及适配范围：本文既有相位估计流程的语法修正；一次估计并固定的时序保持，不声称来自 Cai／Shen。

## L07 · sections/05_overall_algorithm.tex（当前第 170 行）

避免同句重复 minimize，保留各坐标的求解方式。

原文：

```tex
We minimize $\mathcal L$ by coordinate updates, analytically minimizing
over each $\gamma_k$ and refining $(d_k,\nu_k)$ using L-BFGS-B
```

改后：

```tex
We minimize $\mathcal L$ by coordinate updates, solving analytically
for each $\gamma_k$ and refining $(d_k,\nu_k)$ using L-BFGS-B
```

依据及适配范围：本稿已有 coordinate updates、Tipping–Faul §2.1 及 Zhu Algorithm 778 引用保持；语言改写，不重命名算法。

## L08 · sections/06_simulation_results.tex（当前第 351 行）

以 use the same 明确配对输入，避免 estimators share samples 的含混搭配。

原文：

```tex
$-10\log_{10}v$. At each of six SNRs from $-20$ to $30$~dB, both
neural estimators share $2{,}000$ samples from $500$ scenes and the
same white-noise realizations.
```

改后：

```tex
$-10\log_{10}v$. At each of six SNRs from $-20$ to $30$~dB, both
neural estimators use the same $2{,}000$ samples from $500$ scenes and
the same white-noise realizations.
```

依据及适配范围：Cai §VI-B，PDF pp.11–12／印刷 pp.3585–3586，为去噪器单独比较的叙述母本；样本数和配对条件为本文数据，不来自 Cai。

## L09 · sections/06_simulation_results.tex（当前第 375 行）

直接描述方法的误差，不用曲线高低代替指标。

原文：

```tex
Both learned curves remain above the genie-aided reference, which uses
true path information.
```

改后：

```tex
Both learned denoisers have higher NMSE than the genie-aided reference,
which uses true path information.
```

依据及适配范围：Cai §VI-B，PDF p.12／印刷 p.3586，含 genie-aided baseline 及比较段；本文相对差距方向沿用原稿结果，不移植 Cai 的性能幅度。

## L10 · sections/06_simulation_results.tex（当前第 381 行）

修正比较引式的惯用搭配。

原文：

```tex
probability update. As a comparison, the Gaussian approximation gives
```

改后：

```tex
probability update. For comparison, the Gaussian approximation gives
```

依据及适配范围：本稿活动证据消融段的普通语法调整；公式和对比设定保持。

## L11 · sections/06_simulation_results.tex（当前第 395 行）

去掉插入式说明，明确分类器仅用于密度比变体。

原文：

```tex
receiver unchanged. The GP-MP variants in this comparison use the
white-noise-trained denoiser and, for density ratio estimation, its
matched classifier.
```

改后：

```tex
receiver unchanged. Both GP-MP variants use the white-noise-trained
denoiser; the variant with density-ratio estimation also uses its
matched classifier.
```

依据及适配范围：本文已有四组消融配置说明；不新增实验或改变 Gaussian／密度比两变体的范围。

## L12 · sections/06_simulation_results.tex（当前第 424 行）

明确变化的是 NMSE，避免 baselines improve 的笼统表述。

原文：

```tex
sparse-recovery baselines. These baselines improve more slowly with SNR
than the learned receivers, so the NMSE gap between the two groups grows.
```

改后：

```tex
sparse-recovery baselines. The NMSE of these baselines decreases more
slowly with SNR than that of the learned receivers, so the gap between
the two groups grows.
```

依据及适配范围：Cai §VI-C，PDF pp.12–13／印刷 pp.3586–3587，为按指标、SNR 和方法差异组织结果的参考；实际趋势来自本稿。

## L13 · sections/appendix_evaluation_protocol.tex（当前第 18 行）

将生硬的 training-version assignment 改为明确的 network versions used。

原文：

```tex
The training-version assignment of the retained results is specified
at the start of Section~\ref{sec:simulations}.
```

改后：

```tex
The network versions used for the reported results are specified
at the start of Section~\ref{sec:simulations}.
```

依据及适配范围：本文工作稿状态的措辞调整，不是文献方法名称；版本对应关系保持。

## L14 · sections/appendix_evaluation_protocol.tex（当前第 47 行）

合并相邻重复的 All four，保留全部配对与数值设置。

原文：

```tex
All four variants use the same saved observations, known phases, and
noise variances estimated from the observations.
All four use single-precision inference with TF32 disabled.
```

改后：

```tex
All four variants use the same saved observations, known phases, and
noise variances estimated from the observations, with single-precision
inference and TF32 disabled.
```

依据及适配范围：本文实验协议的语法合并，无外部性能主张。

