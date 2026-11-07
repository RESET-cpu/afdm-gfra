# 第二章原段原句对照：Shen、Cai、Xu、Ding、Wei

> 历史版本记录：本表对应本轮后续修改之前的正文。2026-11-01 的[定义句与衔接修正](../ch2_natural_expression_20261101/REVISION_NOTES.md)已替代受影响条目；尤其原第 12、13、15 项对拼接定义句与 UPA response 的出处归类不能继续作为通过依据。原文保留以便追溯。

本记录对应当前 `sections/02_system_model.tex`。按正文顺序，把每个句子或与陈列公式连用的定义单元列出。改后文字直接从实际源稿截取，没有另写一份展示稿。原句中的数学符号作可读转写，PDF 连字、断行已还原；来源中个别公式用方括号明确占位。

段落母本：01–03 以 Shen §II/II-A 为主；04 沿 Shen 阵列说明与 Cai 定义句；05–06 沿 Cai §II-A 导频段；07 沿 Ding §II 与 Xu §II-B 的 AFDM 调制段；08–11 采用相关前缀、公式定义和跨帧段落；12–15 沿 Cai §II-A 的活动、观测和稀疏性段，并使用 Wei 的已知矩阵／欠定问题句；16–17 沿 Cai §II-B 的贝叶斯问题段。

只有条件、符号、技术对象相符的句子才作局部替换。连续波形、跨帧 gq、wrap 和前端固定估计等本文特有内容，保留原数学定义，明确登记为“原定义句的对象替换／必要数学适配”，不虚称这些公式已经出现在母本。Table II 转正文的因子说明明确标作表格来源。

Xu 使用[Surrey 作者稿](https://openresearch.surrey.ac.uk/esploro/outputs/journalArticle/AFDM-aided-Grant-Free-Random-Access-for-LEO/991050765702346)，§II-B、印刷 p.3、式(6)前。仅采用已读到的一句；当前读取到在线 PDF 文本，未取得该页截图。其余四篇为本地原文。Wei 指 Yiming Wei 与 Xiaojun Yuan 的 L-STMP 论文。


## 01 系统场景

### 01（正文第 4 行）

**原句 — Shen, PDF p.3, §II 首段第1句：**

> We consider a LEO satellite-enabled grant-free random access system with the fixed beam as illustrated in Fig. 1, where OTFS is adopted to mitigate the doubly dispersive effect [18] inherent in TSLs.

**改后：**

```tex
We consider a LEO satellite-enabled grant-free random access system, where AFDM is adopted to mitigate the doubly dispersive effect inherent in terrestrial-satellite links (TSLs) \cite{shen2025,huang2026}.
```

**必要替换：**删除 fixed beam、图号；OTFS→AFDM；TSLs 首次展开。

### 02（正文第 7 行）

**原句 — Shen, PDF p.3, §II 首段第2句：**

> The system comprises U single-antenna terrestrial devices that communicate with a LEO satellite equipped with a uniform planar array (UPA) consisting of Na = Nz × Ny antennas and a regenerative payload for on-board baseband signal processing.

**改后：**

```tex
The system comprises $K$ single-antenna terrestrial devices that communicate with a LEO satellite equipped with a uniform planar array (UPA) consisting of $M=M_yM_z$ antennas.
```

**必要替换：**U→K，Na=NzNy→M=MyMz；删除本文未建模的载荷描述。

### 03（正文第 10 行）

**原句 — Shen, PDF p.3, §II 首段第3句：**

> During each time interval, active devices share the same time-frequency resources to transmit their signals to the satellite.

**改后：**

```tex
During each transmission block, active devices share the same pilot resources to transmit their signals to the satellite.
```

**必要替换：**time interval→transmission block；time-frequency resources→pilot resources。

### 04（正文第 12 行）

**原句 — Shen, PDF p.3, §II 首段第4句：**

> Additionally, to minimize energy consumption, we assume that these terrestrial devices operate without GNSS capabilities and do not pre-compensate for delay and Doppler shifts.

**改后：**

```tex
Additionally, we assume that these terrestrial devices operate without GNSS capabilities and do not pre-compensate for delay and Doppler shifts \cite{shen2025}.
```

**必要替换：**仅删除动机状语 to minimize energy consumption。


## 02 物理信道引入

### 05（正文第 18 行）

**原句 — Shen, PDF p.3, §II-A 首段第1–2句：**

> The TSLs will experience fast variations due to the high mobility of the LEO satellite. Hence, this time variation and multipath propagation require a doubly dispersive channel model for accurate TSLs characterization.

**改后：**

```tex
The TSLs experience fast variations due to the high mobility of the LEO satellite. Hence, this time variation and multipath propagation require a doubly dispersive channel model \cite{shen2025}.
```

**必要替换：**删除 will 和结尾重复的 characterization；保留原两句因果顺序。

### 06（正文第 21 行）

**原句 — Cai, PDF pp.3–4, §II-A 首段：**

> Moreover, we assume that the IoT devices are synchronized, and each device determines whether to access the channel in an independent and identically distributed (i.i.d.) manner.

**改后：**

```tex
Moreover, we assume that the terrestrial devices are stationary and all paths from the $k$th device have a common Doppler shift $\nu_k$ \cite{huang2026}.
```

**必要替换：**保留假设句骨架，将同步／接入假设换成本文已有的静止设备与共同 Doppler 假设。

### 07（正文第 24 行）

**原句 — Shen, PDF p.3, §II-A 式(1)前：**

> Then, the delay-Doppler-space domain channel from the u-th device to the (nz + nyNz)-th antenna at the satellite can be represented as [18]

**改后：**

```tex
After receiver compensation for the common delay $\tau_c$, the channel impulse response from the $k$th device to the satellite can be represented as [本文原公式 eq:physical-channel]
```

**必要替换：**改为时间域冲激响应和阵列向量；补入原稿已有的接收端公共时延补偿。


## 03 路径参数定义

### 08（正文第 34 行）

**原句 — Shen, PDF p.3, §II-A 式(1)后：**

> where u = 0,...,U − 1, nz = 0,...,Nz − 1, ny = 0,...,Ny − 1, and P is the number of physical paths.

**改后：**

```tex
where $k=1,\ldots,K$ and $L_k$ is the number of physical paths.
```

**必要替换：**代入 k、Lk；阵列索引放在阵列响应式后。

### 09（正文第 35 行）

**原句 — Shen, PDF p.3, §II-A 式(1)后：**

> As shown in Fig. 1, τi,u = τ̃i,u − τc represents the differential delay for the i-th path from the u-th device to the satellite, where τ̃i,u and τc are denoted as propagation delay and common delay, respectively.

**改后：**

```tex
Here $\tau_{k\ell}=\widetilde\tau_{k\ell}-\tau_c$ represents the differential delay for the $\ell$th path from the $k$th device to the satellite, where $\widetilde\tau_{k\ell}$ and $\tau_c$ are denoted as propagation delay and common delay, respectively.
```

**必要替换：**删除图号，i/u→ℓ/k；保持差分时延原句顺序。

### 10（正文第 39 行）

**原句 — Shen, PDF p.3, §II-A 式(1)后：**

> The common delay corresponds to the propagation time between the satellite and the closest point on earth within the beam coverage [21].

**改后：**

```tex
The common delay corresponds to the propagation time between the satellite and the closest point on Earth within the beam coverage \cite{shen2025}.
```

**必要替换：**保留原句，仅 Earth 大写及本文引文键。

### 11（正文第 42 行）

**原句 — Shen, PDF p.3, §II-A 式(1)后：**

> Additionally, the notations hi,u and νi,u are the path gain and Doppler shift of the i-th path from u-th device to the satellite, respectively.

**改后：**

```tex
Additionally, $g_{k\ell}$ is the path gain of the $\ell$th path from the $k$th device to the satellite.
```

**必要替换：**只保留此处需要定义的 path gain；共同 Doppler 已在式前定义。

### 12（正文第 44 行）

**原句 — Shen, PDF p.3, Notations：**

> The superscripts (·)* and (·)H denote the conjugate and conjugated-transpose operations, respectively. δ(·) denotes the Dirac delta function.

**改后：**

```tex
The notations $\mathbf a_k$, $t_{\rm c}$, and $\delta(\cdot)$ denote the UPA response, the time from the block start, and the Dirac delta function, respectively.
```

**必要替换：**沿用原记号定义句，代入本文 a_k、t_c、δ 及已有含义；非 Shen 同一符号定义。


## 04 阵列与块内参数

### 13（正文第 48 行）

**原句 — Cai, PDF p.11, 信道模型段：**

> the temporal and spatial steering vectors are defined as [aN(τl) 与 bM(φl) 的向量公式]

**改后：**

```tex
The UPA response is defined as \cite{shen2025,li2023} [本文原公式 eq:upa]
```

**必要替换：**两种 steering vectors→UPA response；其公式仍由本文原式及 Shen/Li 支撑。

### 14（正文第 54 行）

**原句 — Shen, PDF p.3, §II-A 式(1)后：**

> where u = 0,...,U − 1, nz = 0,...,Nz − 1, ny = 0,...,Ny − 1, and P is the number of physical paths.

**改后：**

```tex
where $n_z=0,\ldots,M_z-1$, $n_y=0,\ldots,M_y-1$, and $\lambda$ is the wavelength.
```

**必要替换：**保留阵列索引枚举方式；代入本文范围和 λ 定义。

### 15（正文第 56 行）

**原句 — Shen, PDF p.3, Notations：**

> The superscripts (·)* and (·)H denote the conjugate and conjugated-transpose operations, respectively. δ(·) denotes the Dirac delta function.

**改后：**

```tex
The notations $d_y$ and $d_z$ denote the spacing between adjacent antennas along the y-axis and z-axis, respectively.
```

**必要替换：**原记号定义句代入 d_y/d_z；spacing between adjacent antennas 用词仍据 Li p.4。

### 16（正文第 58 行）

**原句 — Shen, PDF p.3, §II-A 末句：**

> The directional cosines Θz_u = cos θz_u and Θy_u = sin θz_u sin θa_u, along the z-axis and y-axis, depend on the zenith angle θz_u and azimuth angle θa_u, respectively.

**改后：**

```tex
The directional cosines $\mu_{z,k}$ and $\mu_{y,k}$ are along the z-axis and y-axis, respectively.
```

**必要替换：**Θ→μ；保留 z/y 顺序，删除本稿未引入的 θ 参数。

### 17（正文第 60 行）

**原句 — Cai, PDF p.3, §II-A 首段：**

> We adopt a block-fading model, i.e., all the channels remain quasi-static within a transmission block.

**改后：**

```tex
We assume that the path gains, delays, Doppler shifts, and arrival angles remain approximately constant within a transmission block.
```

**必要替换：**把原句准静态对象由整个信道改为本文原有的物理参数；不引入 block-fading 假设。


## 05 导频分配

### 18（正文第 65 行）

**原句 — Cai, PDF p.3, §II-A 首段：**

> A total of N adjacent OFDM subcarriers are shared among the devices for pilot transmission.

**改后：**

```tex
A total of $N$ chirp subcarriers are shared among the devices for pilot transmission \cite{cai2026,huang2026}.
```

**必要替换：**adjacent OFDM→chirp；保留共享导频资源句式。

### 19（正文第 67 行）

**原句 — Cai, PDF p.4, §II-A 导频段：**

> Assume that a total of T OFDM symbols are allocated for pilot transmission.

**改后：**

```tex
Assume that a total of $Q$ AFDM frames are allocated for pilot transmission.
```

**必要替换：**T OFDM symbols→Q AFDM frames。

### 20（正文第 69 行）

**原句 — Cai, PDF p.4, §II-A 导频段：**

> Let qktn ∈ C be the pilot symbol transmitted by the k-th device during the t-th OFDM symbol on the n-th subcarrier.

**改后：**

```tex
Let $P_{qkn}\in\mathbb C$ be the pilot symbol transmitted by the $k$-th device during the $q$-th AFDM frame on the $n$-th chirp subcarrier.
```

**必要替换：**qktn→Pqkn，OFDM symbol→AFDM frame，subcarrier→chirp subcarrier。

### 21（正文第 71 行）

**原句 — Cai, PDF p.4, §II-A 导频段：**

> We construct a diagonal pilot matrix as Qkt ≜ diag{qkt1,...,qktN} ∈ C^(N×N), ∀k,t.

**改后：**

```tex
We construct a pilot vector as $\mathbf p_{qk}=[P_{qk0},\ldots,P_{qk,N-1}]^{\mathsf T} \in\mathbb C^N$, $k=1,\ldots,K$, $q=0,\ldots,Q-1$.
```

**必要替换：**diagonal pilot matrix→pilot vector，保留本文原向量定义。

### 22（正文第 74 行）

**原句 — Wei–Yuan, PDF p.2, §II-A 式(2)前：**

> Let M denote the number of compressed spatial measurements per subcarrier, where M ≪ Nr, and let B ∈ C^(M×Nr) denote a known analog spatial compression matrix.

**改后：**

```tex
Let $\mathbf P\in\mathbb C^{Q\times KN}$ denote a known pilot matrix at the satellite receiver, with entries $[\mathbf P]_{q,(k-1)N+n}=P_{qkn}$.
```

**必要替换：**保留 let…denote a known…matrix；代入本文 P、维度、接收端和索引。


## 06 导频条件

### 23（正文第 78 行）

**原句 — Cai, PDF p.4, §II-A 式(4)后：**

> For simplicity, we impose the condition that Q is partial orthogonal, specifically requiring that QQH = KP INT, where each device has the same transmit power budget P.

**改后：**

```tex
For simplicity, we impose the condition that $\mathbf P\mathbf P^{\mathsf H}=KE_p\I_Q$, where each device has the same pilot energy $E_p=\|\mathbf p_{qk}\|^2$ in each frame \cite{cai2026}.
```

**必要替换：**Q→P，功率预算→原有每帧导频能量；保留原 PPH 条件。

### 24（正文第 82 行）

**原句 — Cai, PDF p.4, §II-A 式(4)后：**

> The design of partial orthogonal Q is deferred to Section V-C.

**改后：**

```tex
The design of $\mathbf P$ is deferred to Section~\ref{sec:simulation-settings}.
```

**必要替换：**只换矩阵名与章节号；删去重复修饰语。


## 07 AFDM 调制

### 25（正文第 85 行）

**原句 — Ding, PDF p.2, §II 式(1)前：**

> The time-domain transmitted signal is generated through the inverse discrete affine Fourier transform (IDAFT) applied to xk, mathematically formulated as

**改后：**

```tex
The time-domain transmitted signal is generated through the inverse discrete affine Fourier transform (IDAFT) applied to $\mathbf p_{qk}$, mathematically formulated as \cite{ding2026} [本文原公式 eq:afdm-time-signal]
```

**必要替换：**仅 x_k→p_qk；IDAFT 公式保持本稿原式。

### 26（正文第 94 行）

**原句 — Shen, PDF p.4, §II-B 式(7)后：**

> where li,u = 0,...,M − 1 and ki,u = ⌈−N/2⌉,...,⌈N/2⌉ − 1 represent the indexes of the delay and Doppler tap, respectively.

**改后：**

```tex
where $t=0,\ldots,N-1$.
```

**必要替换：**索引定义句，换为本稿时域样本范围；不移植 Shen 的延迟／Doppler 网格。

### 27（正文第 95 行）

**原句 — Ding, PDF p.2, §II 式(1)后及式(3)后：**

> c1 and c2 are AFDM modulation parameters. where Ts = 1/(NΔf) gives the sampling interval.

**改后：**

```tex
Here $T_s=1/(N\Delta f)$ gives the sampling interval, with $\Delta f$ denoting the subcarrier spacing.
```

**必要替换：**保留采样间隔原句，补回原稿 Δf 的既有定义。

### 28（正文第 97 行）

**原句 — Ding, PDF p.2, §II 式(1)后及式(3)后：**

> c1 and c2 are AFDM modulation parameters. where Ts = 1/(NΔf) gives the sampling interval.

**改后：**

```tex
The parameters $c_1$ and $c_2$ are AFDM modulation parameters.
```

**必要替换：**只增加 The parameters 作主语引导，参数名称不变。

### 29（正文第 98 行）

**原句 — Xu, 作者稿印刷 p.3（含封面 PDF p.4）, §II-B 式(6)前：**

> The time-domain signal can be obtained by

**改后：**

```tex
The time-domain signal can be obtained by \cite{xu2026} [本文原公式 无编号]
```

**必要替换：**保留原句，矩阵符号及公式用本文原稿。

### 30（正文第 102 行）

**原句 — Ding, PDF p.2, §II 式(2)后：**

> where AH = Λc1^H F Λc2^H represents the DAFT matrix.

**改后：**

```tex
where [本文原公式 eq:daft] denotes the discrete affine Fourier transform (DAFT) matrix.
```

**必要替换：**使用本文 F_A 的 DAFT 约定；不复制 Ding 原文中 A^H 的混用。


## 08 CPP

### 31（正文第 113 行）

**原句 — Cai, PDF p.4, §II-A 式(3)前：**

> Assume that the cyclic prefix (CP) length exceeds the maximum channel delay spread.

**改后：**

```tex
Assume that the chirp-periodic prefix (CPP) length is greater than or equal to the maximum differential delay, i.e., $N_{\rm CPP}T_s\geq\max_{k,\ell}\tau_{k\ell}$.
```

**必要替换：**CP→CPP，exceeds→greater than or equal to，最大时延→最大差分时延；均由本文原条件决定。

### 32（正文第 116 行）

**原句 — Shen, PDF p.4, §II-B 式(2)前：**

> Then, the transmitted signal in the delay-Doppler domain is given by XDD_u,q[k,l] = Cu,q[k,l]td_u[l], where td_u[l] represents the data symbol selected from a predefined alphabet A = {a1,...,a|A|} with cardinality |A|.

**改后：**

```tex
The CPP is given by \cite{bemani2022} [本文原公式 eq:cpp]
```

**必要替换：**原公式引导句的定义对象换为 CPP；具体公式仍为原稿/Bemani，不称 Shen 使用 CPP。

### 33（正文第 125 行）

**原句 — Cai, PDF p.4, §II-A 式(4)前：**

> Define Y ≜ [Y1^H,...,YT^H]^H ∈ C^(NT×M), Qk ≜ [Qk1^H,...,QkT^H]^H ∈ C^(NT×N), and N ≜ [N1^H,...,NT^H]^H ∈ C^(NT×M).

**改后：**

```tex
where $\langle x\rangle_N=x-N\lfloor x/N\rfloor$ and $2Nc_1\in\mathbb N_+$.
```

**必要替换：**用原多变量定义句承接本文已有模运算和 2Nc1 条件；公式内容不来自 Cai。

### 34（正文第 127 行）

**原句 — Shen, PDF p.4, §II-B 式(3)后：**

> where Tcp is the time duration of the cyclic prefix (CP), and Tsym = T + Tcp is the time duration of a OFDM symbol with CP.

**改后：**

```tex
Here $T_{\rm frame}=(N+N_{\rm CPP})T_s$ is the time duration of an AFDM frame with CPP.
```

**必要替换：**Tsym、OFDM symbol、CP→Tframe、AFDM frame、CPP；保留原句时长结构。


## 09 连续波形

### 35（正文第 130 行）

**原句 — Cai, PDF p.4, §II-A 式(4)前：**

> Define Y ≜ [Y1^H,...,YT^H]^H ∈ C^(NT×M), Qk ≜ [Qk1^H,...,QkT^H]^H ∈ C^(NT×N), and N ≜ [N1^H,...,NT^H]^H ∈ C^(NT×M).

**改后：**

```tex
Define $w_\xi=\langle\xi\rangle_N$ and $\zeta_n(w)=\lfloor2c_1w+n/N\rfloor$ for time $\xi T_s$.
```

**必要替换：**同一多变量定义句代入 wξ、ζn 与原时间变量；本文特有定义。

### 36（正文第 132 行）

**原句 — Shen, PDF p.4, §II-B 式(7)前：**

> We denote the delay and Doppler taps for the i-th path of the u-th device as follows

**改后：**

```tex
We denote the transmit waveform for the $n$th chirp subcarrier as follows \cite{bemani2022} [本文原公式 eq:continuous-waveform]
```

**必要替换：**保持 We denote…as follows；定义对象换为第 n 个 chirp subcarrier 的 transmit waveform。

### 37（正文第 139 行）

**原句 — Shen, PDF p.4, §II-B Proposition 1 后：**

> Note that the relationship (8) aligns with those in [30], [34] when adopting a single-frame OTFS transmission with replacing Cu,q[k,l]td_u[l] for XDD_u,q[k,l], provided Δf > 2νmax and T > τmax.

**改后：**

```tex
Note that $\varphi_n(t)=[\mathbf F_{\rm A}^{\mathsf H}]_{tn}$ for $t=0,\ldots,N-1$, while $\varphi_n(\xi)$ satisfies the CPP relation \eqref{eq:cpp} for $\xi<0$.
```

**必要替换：**保留“说明公式与另一表达一致并给出条件”的句子功能；代入原样本等式和 CPP 条件，属于必要数学适配。


## 10 有效信道

### 38（正文第 143 行）

**原句 — Cai, PDF p.4, §II-A 式(2)前：**

> Denote by hknm ∈ C the channel frequency response on the n-th subcarrier from the k-th device to the m-th BS antenna.

**原句 — Cai, PDF p.4, §II-A 式(3)前：**

> After removing the CP and applying the DFT, the received signal Yt ∈ C^(N×M) during the t-th OFDM symbol is given by

**改后：**

```tex
Denote by $H_k^{(q)}\in\mathbb C^{M\times N\times N}$ the effective channel from the $k$th device to the satellite during the $q$th AFDM frame, after removing the CPP and applying the DAFT.
```

**必要替换：**保留 Denote by…from the kth device…；把 OFDM 子载波响应换为经 CPP/DAFT 后的 AFDM 有效信道。

### 39（正文第 146 行）

**原句 — Cai, PDF p.4, §II-A 式(3)后：**

> Let Xk ≜ αkHk.

**改后：**

```tex
Let $H_k=H_k^{(0)}$.
```

**必要替换：**原 Let 等式定义句，代入本文参考帧定义。

### 40（正文第 147 行）

**原句 — Cai, PDF p.4, §II-A 式(2)前：**

> Then, the channel frequency response from the k-th device to the BS can be expressed in a matrix form as

**改后：**

```tex
Then, the effective channel $H_k$ can be expressed as [本文原公式 eq:channel]
```

**必要替换：**channel frequency response→effective channel Hk；删去不对应张量的 matrix form。

### 41（正文第 154 行）

**原句 — Shen, PDF p.4, §II-B 式(7)后：**

> where li,u = 0,...,M − 1 and ki,u = ⌈−N/2⌉,...,⌈N/2⌉ − 1 represent the indexes of the delay and Doppler tap, respectively.

**改后：**

```tex
where $n$ and $r$ represent the transmitted and received symbol positions, respectively, and $m$ is the antenna index.
```

**必要替换：**原成对索引说明改为发射／接收符号索引，并保留原天线索引定义。

### 42（正文第 156 行）

**原句 — Cai, PDF p.4, §II-A 式(2)前：**

> Then, the channel frequency response from the k-th device to the BS can be expressed in a matrix form as

**改后：**

```tex
For path gain $1$, delay $dT_s$, and Doppler shift $\nu$, the channel response can be expressed in a matrix form as [本文原公式 eq:path-operator-system]
```

**必要替换：**原 channel response→matrix form 句；前置本稿原路径增益、时延和 Doppler 条件。

### 43（正文第 167 行）

**原句 — Cai, PDF p.4, §II-A 式(4)前：**

> Define Y ≜ [Y1^H,...,YT^H]^H ∈ C^(NT×M), Qk ≜ [Qk1^H,...,QkT^H]^H ∈ C^(NT×N), and N ≜ [N1^H,...,NT^H]^H ∈ C^(NT×M).

**改后：**

```tex
where $t_{\rm c}=(g+t)T_s$ for $t=0,\ldots,N-1$ after removing the CPP, and $g=N_{\rm CPP}$ for frame $0$.
```

**必要替换：**原多变量定义句适配本稿已有时间对应与参考帧起点。

### 44（正文第 169 行）

**原句 — Cai, PDF p.9, §IV-B 式(51)后：**

> Please refer to [31, Appendix F] for the detailed derivation.

**改后：**

```tex
Please refer to Appendix~\ref{app:afdm-model} for the detailed derivation and the expression for integer $d$.
```

**必要替换：**只换为本稿附录，并保留原稿对整数 d 情形的指引。

### 45（正文第 171 行）

**原句 — Cai, PDF p.3, §I-B1：**

> However, an energy leakage problem arises from the inverse discrete Fourier transform (IDFT) to obtain the time-domain channel, which undermines its sparsity level.

**改后：**

```tex
Power leakage arises from fractional delays and Doppler shifts, which can weaken the sparsity of $H_k$ \cite{huang2026}.
```

**必要替换：**保留 leakage arises from…which…sparsity 的整句结构；原因换为本稿分数时延/Doppler，术语与结论据 Huang。


## 11 跨帧关系

### 46（正文第 174 行）

**原句 — Cai, PDF p.4, §II-A 式(3)前：**

> After removing the CP and applying the DFT, the received signal Yt ∈ C^(N×M) during the t-th OFDM symbol is given by

**原句 — Cai, PDF p.4, §II-A 式(3)后：**

> Let Xk ≜ αkHk.

**改后：**

```tex
After removing the CPP in frame $q$, let $g_q=N_{\rm CPP}+q(N+N_{\rm CPP})$.
```

**必要替换：**Cai 的 CPP 接收操作句承接原 Let 定义，代入本稿 gq；无对应原文跨帧 gq 定义。

### 47（正文第 176 行）

**原句 — Shen, PDF p.4, §II-B Proposition 1 前：**

> Based on (1)-(7), we can derive the input-output relationship of the system, as given in the following proposition.

**改后：**

```tex
Based on \eqref{eq:path-operator-system}, we can derive the effective channel in the $q$th AFDM frame as [本文原公式 eq:twc-frame-channel]
```

**必要替换：**保留 Based on…we can derive…as，代入原推导关系及 qth AFDM frame。

### 48（正文第 185 行）

**原句 — Shen, PDF p.4, §II-B 式(6)前：**

> Finally, the symplectic finite Fourier transform (SFFT) [31] maps the symbols into the delay-Doppler-space domain as

**改后：**

```tex
where $\operatorname{wrap}(\cdot)$ maps an angle to $[-\pi,\pi)$.
```

**必要替换：**保留 maps…to/into 的映射句，改为本文原 wrap 映射；不称 Shen 定义了该算子。

### 49（正文第 186 行）

**原句 — Shen, PDF p.4, §II-B 末段：**

> Fortunately, HDDS_nz,ny,u[k′,l′,l] remains approximately constant over Q consecutive frames, benefited by the quasi-static property of (1) in the delay-Doppler domain.

**改后：**

```tex
After separating the phase evolution across frames, $H_k$ remains approximately constant over $Q$ consecutive frames.
```

**必要替换：**保留 remains approximately constant over Q consecutive frames；成立条件换为本稿已定义的相位分离，沿用引言措辞。


## 12 活动与有效导频

### 50（正文第 191 行）

**原句 — Cai, PDF pp.3–4, §II-A 首段：**

> Moreover, we assume that the IoT devices are synchronized, and each device determines whether to access the channel in an independent and identically distributed (i.i.d.) manner.

**改后：**

```tex
Each device determines whether to access the channel in an independent and identically distributed (i.i.d.) manner.
```

**必要替换：**保留原接入独立同分布分句，删除不适用于本稿的同步假设。

### 51（正文第 193 行）

**原句 — Cai, PDF p.4, §II-A：**

> As a result, only a (small) subset of the devices is active in any given transmission block.

**改后：**

```tex
As a result, only a small subset of the devices is active in any given transmission block.
```

**必要替换：**仅去括号；保持原句。

### 52（正文第 195 行）

**原句 — Cai, PDF p.4, §II-A 式(1)前：**

> We use an indicator function αk to model the device activity as

**改后：**

```tex
We use an indicator function $\alpha_k$ to model the device activity as \cite{cai2026} [本文原公式 无编号]
```

**必要替换：**保留原句与本稿原活动定义。

### 53（正文第 203 行）

**原句 — Cai, PDF p.4, §II-A 式(1)后：**

> Let λ represent the probability of a device being active, i.e., p(αk = 1) = λ, where λ ≪ 1.

**改后：**

```tex
Let $\rho$ represent the probability of a device being active, i.e., $\Pr(\alpha_k=1)=\rho$, where $\rho\ll1$.
```

**必要替换：**λ→ρ，p→Pr，技术定义不变。

### 54（正文第 204 行）

**原句 — Shen, PDF p.1, §I：**

> It should be noted that the schemes in [9]–[17] are designed for block fading channels, which are assumed to remain constant during one block transmission.

**改后：**

```tex
The activity states are assumed to remain constant during one block transmission.
```

**必要替换：**原不变性从句作用于本稿已有活动状态假设。

### 55（正文第 206 行）

**原句 — Cai, PDF p.4, §II-A 式(3)后：**

> Let Xk ≜ αkHk.

**改后：**

```tex
Let $X_k=\alpha_kH_k$.
```

**必要替换：**原句，仅保留本稿等号写法。

### 56（正文第 207 行）

**原句 — Shen, PDF p.4, §II-B 式(2)前：**

> Then, the transmitted signal in the delay-Doppler domain is given by XDD_u,q[k,l] = Cu,q[k,l]td_u[l], where td_u[l] represents the data symbol selected from a predefined alphabet A = {a1,...,a|A|} with cardinality |A|.

**改后：**

```tex
The pilot symbols including the inter-frame phase rotation are given by [本文原公式 eq:effective-pilot]
```

**必要替换：**原 transmitted signal is given by 的对象换为含帧间相位的导频；式(10)仍是本文原式。


## 13 接收观测

### 57（正文第 213 行）

**原句 — Cai, PDF p.4, §II-A 式(3)前：**

> After removing the CP and applying the DFT, the received signal Yt ∈ C^(N×M) during the t-th OFDM symbol is given by

**改后：**

```tex
After removing the CPP and applying the DAFT, the received signal $\mathbf Y_q\in\mathbb C^{M\times N}$ during the $q$th AFDM frame is given by \cite{cai2026} [本文原公式 eq:observation-tensor]
```

**必要替换：**CP/DFT/OFDM→CPP/DAFT/AFDM；维度与索引保持本文原稿。

### 58（正文第 221 行）

**原句 — Cai, PDF p.4, §II-A 式(3)后：**

> where Nt ∈ C^(N×M) is an AWGN matrix with the elements i.i.d. drawn from CN(0,δ0²).

**改后：**

```tex
where $\mathbf W_q=[W_{qmr}]_{m,r}\in\mathbb C^{M\times N}$ is an AWGN matrix with the elements i.i.d. drawn from $\CN(0,\sigma^2)$.
```

**必要替换：**Nt→Wq，δ0²→σ²，并代入本稿噪声矩阵维度。


## 14 紧凑观测

### 59（正文第 224 行）

**原句 — Cai, PDF p.4, §II-A 式(4)前：**

> We express the received signal Y over the T OFDM symbols in a more compact form as

**改后：**

```tex
We express the received signal $\mathbf Y$ over the $Q$ AFDM frames in a more compact form as [本文原公式 eq:mmv]
```

**必要替换：**T OFDM symbols→Q AFDM frames，保持句式及原 MMV 式。

### 60（正文第 230 行）

**原句 — Cai, PDF p.4, §II-A 式(4)前：**

> Define Y ≜ [Y1^H,...,YT^H]^H ∈ C^(NT×M), Qk ≜ [Qk1^H,...,QkT^H]^H ∈ C^(NT×N), and N ≜ [N1^H,...,NT^H]^H ∈ C^(NT×M).

**改后：**

```tex
where $\mathbf Y,\mathbf W\in\mathbb C^{Q\times MN}$, $\mathbf A\in\mathbb C^{Q\times KN}$, and $\mathbf X\in\mathbb C^{KN\times MN}$.
```

**必要替换：**原矩阵定义方式，代入本文四个矩阵的维度。

### 61（正文第 233 行）

**原句 — Shen, PDF p.5, §II-C 式(14)后：**

> where Yl_q and Zl_q are with the (k,az + Nzay)-th element YDDA_az,ay,q[k,l] and ZDDA_az,ay,q[k,l], respectively.

**改后：**

```tex
The matrices $\mathbf Y$, $\mathbf W$, $\mathbf A$, and $\mathbf X$ have the following entries: [本文原公式 eq:mmv-indexing]
```

**必要替换：**原矩阵—元素对应句改列四个矩阵的条目；are with 改 have，保留本稿全部索引等式。


## 15 稀疏结构

### 62（正文第 244 行）

**原句 — Cai, PDF p.4, §II-A 式(4)后：**

> Due to the sporadic access of the devices, matrix X exhibits a block-sparsity structure. Specifically, if the k-th device is inactive, we have Xk = αkHk = 0.

**改后：**

```tex
Due to the sporadic access of the devices, $\mathbf X$ exhibits a block-sparsity structure. Specifically, if the $k$th device is inactive, we have $X_k=\alpha_kH_k=\mathbf0$ \cite{cai2026}.
```

**必要替换：**恢复原段两句顺序及 Specifically；仅删去 matrix 修饰语。

### 63（正文第 248 行）

**原句 — Wei–Yuan, PDF p.2, §II-B 式(4)后：**

> Since M ≪ Nr and ρ ≪ 1 in the extreme compression regime of interest, this inverse problem is severely underdetermined and requires both measurement consistency and effective channel priors.

**改后：**

```tex
Since $Q<KN$, the inverse problem in \eqref{eq:mmv} is underdetermined.
```

**必要替换：**保留 Since…this inverse problem is…underdetermined；条件换为本文维度，删除 severely 和无关后半句。


## 16 贝叶斯问题

### 64（正文第 250 行）

**原句 — Cai, PDF p.4, §II-B 首句：**

> In this paper, we aim to simultaneously detect the active devices and estimate the corresponding channels based on the observation Y under a Bayesian inference framework.

**改后：**

```tex
In this paper, we aim to simultaneously detect the active devices and estimate the corresponding channels based on the observation $\mathbf Y$ under a Bayesian inference framework \cite{cai2026}.
```

**必要替换：**保留原句，符号仍为 Y。

### 65（正文第 253 行）

**原句 — Cai, PDF p.4, §II-B 首句：**

> In this paper, we aim to simultaneously detect the active devices and estimate the corresponding channels based on the observation Y under a Bayesian inference framework.

**改后：**

```tex
We estimate the full $H_k$ without imposing channel sparsity \cite{huang2026}.
```

**必要替换：**原 aim…estimate…channels 句的对象与限定换成原稿 full Hk、without imposing channel sparsity；技术依据仍为 Huang。

### 66（正文第 255 行）

**原句 — Cai, PDF p.4, §II-A 导频段：**

> Let qktn ∈ C be the pilot symbol transmitted by the k-th device during the t-th OFDM symbol on the n-th subcarrier.

**改后：**

```tex
Let $\widehat{\mathbf A}$ and $\widehat\sigma^2$ be fixed as in Section~\ref{sec:frontend}.
```

**必要替换：**使用原 Let…be…定义句；本文特有的 Ahat、σhat² 条件固定方式保留，不称 Cai 有同一前端。

### 67（正文第 257 行）

**原句 — Cai, PDF p.4, §II-A 式(1)后：**

> Let λ represent the probability of a device being active, i.e., p(αk = 1) = λ, where λ ≪ 1.

**改后：**

```tex
Let $q_{\rm tr}(H_k)$ represent the channel prior for training.
```

**必要替换：**使用原 Let…represent…定义句，代入原 qtr 训练信道先验。

### 68（正文第 258 行）

**原句 — Cai, PDF p.1, 摘要：**

> Specifically, we develop a novel turbo message passing (TMP) framework that models the entire channel matrix as a super node, rather than factorizing it element-wise.

**改后：**

```tex
Specifically, we model the entire $H_k$ using $q_{\rm tr}(H_k)$, rather than factorizing it element-wise.
```

**必要替换：**保留 model the entire…rather than factorizing it element-wise；删除不在本章引入的 TMP/super node。

### 69（正文第 260 行）

**原句 — Cai, PDF p.6, §III-B 式(14)后：**

> where (13) arises from the fact that the messages Mfym→xkm(xkm) are independent for different values of m.

**改后：**

```tex
The variables $H_k$ and $\alpha_k$ are independent for different values of $k$, and $H_k$ is independent of $\alpha_k$.
```

**必要替换：**保留 independent for different values of…；对象与 k 内独立条件均是本文原假设。

### 70（正文第 262 行）

**原句 — Cai, PDF p.4, §II-B 式(5)前：**

> In message passing, we factorize the joint posterior distribution according to Baye’s theorem and the conditional independence relationships among the variables, expressed as

**改后：**

```tex
We factorize the joint posterior distribution according to Bayes' theorem and the conditional independence relationships among the variables, expressed as \cite{cai2026} [本文原公式 eq:working-posterior]
```

**必要替换：**保留原整句，删除 In message passing；修正 Baye’s 拼写为 Bayes'。


## 17 后验因子与目标

### 71（正文第 275 行）

**原句 — Cai, PDF p.5, §II-B 式(5)续文：**

> where xm ∈ C^(NK) and ym ∈ C^(NT) denote the m-th column of X = [x1,...,xM] and Y = [y1,...,yM], respectively.

**改后：**

```tex
where $\mathbf x_j\in\mathbb C^{KN}$ and $\mathbf y_j\in\mathbb C^Q$ denote the $j$th column of $\mathbf X$ and $\mathbf Y$, respectively.
```

**必要替换：**m→j，并换为本文维度；删除重复写出的列向量拼接。

### 72（正文第 277 行）

**原句 — Cai, PDF p.5, Table II（表格，非原句）：**

> p(ym|xm): CN(Qxm,δ0² INT); p(Xk|Hk,αk): δ(Xk−αkHk); p(αk): (1−λ)δ(αk)+λδ(1−αk).

**改后：**

```tex
Here $p(\mathbf y_j\mid\mathbf x_j)=\CN(\mathbf y_j; \widehat{\mathbf A}\mathbf x_j,\widehat\sigma^2\I_Q)$, $p(X_k\mid H_k,\alpha_k)$ enforces $X_k=\alpha_kH_k$, and $p(\alpha_k)=\rho^{\alpha_k}(1-\rho)^{1-\alpha_k}$.
```

**必要替换：**表中因子的公式写入正文；保留原稿 Ahat、σhat²、硬约束和 Bernoulli 质量函数，不标作原文完整句。

### 73（正文第 282 行）

**原句 — Cai, PDF p.7, §III-B2/3 式(30)、(35)附近：**

> is the posterior probability of activity for the k-th device. By taking the Gaussian projection, the mean of xkm with respect to the belief MfXk(Xk) is given by

**改后：**

```tex
The MMSE estimate and the posterior probability of activity for the $k$th device are given by [本文原公式 eq:targets]
```

**必要替换：**以原 posterior probability of activity 与 mean…is given by 两处说明合并引出本文两个既有目标；未使用高斯投影。

