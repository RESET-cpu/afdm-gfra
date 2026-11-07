# 第二章逐句来源核查：完整对照

> 本轮历史图和绘图脚本已移入归档；当前生图入口见 [统一说明](../../../../src/evaluation/plots/manuscript/README.md)。以下记录描述当时版本。

核查日期：2026-10-30。对象是当前英文第二章，非旧版本，也不是中文译文。

- 正文：[02_system_model.tex](D:/afdm-gfra/paper/C-STMP/sections/02_system_model.tex)
- SHA-256：`94a99c98c0460c689285ea211827fb07974f935d79a8602cf0edc5b846c8e37a`
- 覆盖：13 个段落、54 个完整句子，含所有显示公式及其从句。
- 分组审查后由主审汇总复核；本次未修改正文、PDF或实验。

分类反映措辞来源，不等同于技术正确性。未找到同一句话不自动构成模型错误；数学成立也不自动说明措辞属于原句替换。

| 类别 | 句数 |
|---|---:|
| 原句一致 | 0 |
| 仅术语/符号替换 | 0 |
| 有定位的合理原句组合 | 3 |
| 有依据但经过自主改写 | 21 |
| 本稿定义、假设或推导 | 30 |
| 来源缺口 | 0 |
| 未核实 | 0 |

## 段落索引

| 段落 | 原文行号 | 句数 |
|---|---|---:|
| [P01](#p01) | 4–10 | 3 |
| [P02](#p02) | 14–37 | 6 |
| [P03](#p03) | 39–50 | 3 |
| [P04](#p04) | 54–67 | 6 |
| [P05](#p05) | 69–93 | 3 |
| [P06](#p06) | 95–109 | 3 |
| [P07](#p07) | 111–142 | 6 |
| [P08](#p08) | 144–158 | 3 |
| [P09](#p09) | 162–212 | 10 |
| [P10](#p10) | 214–216 | 1 |
| [P11](#p11) | 218–225 | 5 |
| [P12](#p12) | 227–255 | 4 |
| [P13](#p13) | 257–260 | 1 |

## 判读边界

本次按完整语法句核查。原句支持已拆到具体页码/小节/公式；引语中的数学符号可能以可检索的线性写法转写，具体公式以原 PDF 为准。

“有依据但经过自主改写”包括同义词替换、删减和语序重组，不能据此称原文凭空编造，也不能称只换了术语。“本稿定义、假设或推导”应由数学及显式条件支撑；无需为了满足逐字要求而伪造文献原句。

逐句处理建议是来源整改选项，不表示必须向正文增加解释。作者自定义的符号、索引、公式推导和章节指引可保留为作者内容。

主审对P04.S01统一了组合口径，最终分类以本表为准；其余53句保留分组判断。局部术语“working posterior”仍未闭合来源，详见P12.S02及[主审复核记录](ADJUDICATION.json)。

## 标题核对

| 标题 | 来源判断 |
|---|---|
| System Model | Shen §II及Huang §II等有相同标题，仅大小写排版差异。 |
| Terrestrial-Satellite Link Model | Shen PDF p.3 §II-A同名标题，大小写差异。 |
| Multi-Frame AFDM Transmission | 本稿按内容组合的标题；Shen §II-B为Transmission Scheme，不能称直接沿用其原题。标题不引入新算法术语。 |
| Problem Formulation | Shen PDF p.5 §II-C同名标题。 |

标题另列，不计入54个正文完整语法句。

## P01

原文行号：4–10。

**来源顺序：** Ding §II 起首句 + Shen §II 阵列尺寸；Shen §II 同段共享资源句；Shen §II 同段无 GNSS 句

**跨来源组合：** 是

**结构变化：** 从 Ding 的系统配置进入 Shen 的共享资源与无预补偿设定，顺序连贯；把信号限制为导频和把时间间隔叫作 block 是本稿范围设定。阵列维数来自另一个来源，单引 Ding 不能覆盖此细节。

**段落结论：** 1 句合理组合，2 句支持性改写；不能称整段仅替换术语。

### P01-S01 · 有定位的合理原句组合

**当前稿完整句（含公式）：**

```tex
We consider an AFDM-GFRA system in which a LEO satellite equipped
with $M=M_yM_z$ antennas serves $K$ single-antenna devices
\cite{ding2026}.
```

**参考原文与定位：**

[ding2026](D:/afdm-gfra/reference/literature/ding2026.pdf)，PDF 第 2 页，II. AFDM-GF-RA System。

> We consider an AFDM-GF-RA system, where a LEO satellite equipped with M antennas serves K single-antenna devices.

定位/释义：左栏 §II 第一完整句。

[shen2025](D:/afdm-gfra/reference/literature/shen2025.pdf)，PDF 第 3 页，II. System Model。

> The system comprises U single-antenna terrestrial devices that communicate with a LEO satellite equipped with a uniform planar array (UPA) consisting of N_a = N_z × N_y antennas and a regenerative payload for on-board baseband signal processing.

定位/释义：右栏 Fig.1 后第一段第二句。

**具体变化：** 保留 Ding 起首句主干；AFDM-GF-RA→AFDM-GFRA 是缩写拼写调整。；把 M 展开为 M_y M_z，阵列尺寸依据是 Shen 的 N_a=N_z×N_y。；where 改为 in which 属连接语法调整，其余主体关系不变。

**分类理由：** 能定位 Ding 的完整主句及 Shen 的阵列维数子句；没有新增服务关系或收发天线配置。按协议接受为有定位的原句组合，而非仅凭系统主题相似。

**技术判断：** SUPPORTED：系统配置和二维阵列维数均有直接依据；当前句只引 Ding，阵列维数最好同时指向 Shen。

**公式适配：** M=N_yN_z 的变量改名与乘法因子顺序交换；无数学内容变化。

**处理建议：** 可保留；若目标是每个新增细节都可追溯，应在此处补 Shen 对阵列维数的来源。

### P01-S02 · 有依据但经过自主改写

**当前稿完整句（含公式）：**

```tex
In each transmission block, active devices
transmit their pilots over the same time-frequency resources.
```

**参考原文与定位：**

[shen2025](D:/afdm-gfra/reference/literature/shen2025.pdf)，PDF 第 3 页，II. System Model。

> During each time interval, active devices share the same time-frequency resources to transmit their signals to the satellite.

定位/释义：右栏 Fig.1 后第一段第三句。

**具体变化：** During each time interval→In each transmission block。；share resources to transmit signals 改写为 transmit pilots over resources，变更句子谓语组织。；signals→pilots 是本稿导频对象限定；删除 to the satellite。

**分类理由：** 内容与 Shen 原句一致且导频是信号的具体用途，但完整英文句经过重组，不只是必要术语替换，也不是拼接保留的原句分句。

**技术判断：** SUPPORTED：同时复用时频资源有原文直接支持；导频用途由本稿建模明确。

**公式适配：** 无公式。transmission block 是本稿时间分组，不能单凭此句获得多帧准静态条件。

**处理建议：** 若严格执行原句适配标准，应采用 Shen 的原句结构，只替换 time interval 为本稿 block、signals 为 pilots。

### P01-S03 · 有依据但经过自主改写

**当前稿完整句（含公式）：**

```tex
To reduce energy consumption, we assume that the devices operate
without GNSS capabilities and do not pre-compensate for delay and Doppler shifts
\cite{shen2025}.
```

**参考原文与定位：**

[shen2025](D:/afdm-gfra/reference/literature/shen2025.pdf)，PDF 第 3 页，II. System Model。

> Additionally, to minimize energy consumption, we assume that these terrestrial devices operate without GNSS capabilities and do not pre-compensate for delay and Doppler shifts.

定位/释义：右栏 Fig.1 后第一段第四句。

**具体变化：** 删去 Additionally。；to minimize→To reduce、these terrestrial devices→the devices，属于普通措辞精简而不是技术术语替换。；without GNSS capabilities and do not pre-compensate for delay and Doppler shifts 保留了完整实质分句。

**分类理由：** 无 GNSS、无终端延迟与 Doppler 预补偿及节能动机均有明确原句；但普通词语已自行改写，按严格类别不能标 TERM_ONLY。

**技术判断：** SUPPORTED：假设与 Shen 相同，含义没有变强。

**公式适配：** 无公式。

**处理建议：** 若必须满足仅术语替换，可恢复 Shen 原句的动机和指代用语；现句可作为有来源的改写保留，但不能宣称逐字适配。

## P02

原文行号：14–37。

**来源顺序：** Shen §II-A 双扩展因果；Huang §II 静止参考 + 共同 Doppler；本稿向量/时间定义，Li/Shen 阵列背景；Li 时变 CIR + Shen 差分延迟/阵列 + Huang 共同 Doppler的适配；Shen §II-A 差分延迟定义；Shen §II-A 共同延迟定义

**跨来源组合：** 是

**结构变化：** 该段把不同论文的模型条件组装成新系统模型。共同 Doppler 与共同阵列均有明确来源；从逐路径 Doppler 到共同 Doppler、从绝对时延到差分时延、以及本稿时间参考是实质模型适配，不是简单术语替换。所有条件应在公式附近透明说明。

**段落结论：** 1 句合理组合，3 句支持性改写，2 句本稿定义/推导；来源支持概念不等于整段原句改名。

### P02-S01 · 有依据但经过自主改写

**当前稿完整句（含公式）：**

```tex
The high mobility of the LEO satellite and multipath propagation
give rise to doubly dispersive terrestrial-satellite links (TSLs)
\cite{shen2025}.
```

**参考原文与定位：**

[shen2025](D:/afdm-gfra/reference/literature/shen2025.pdf)，PDF 第 3 页，II-A. Terrestrial-satellite Link Model。

> The TSLs will experience fast variations due to the high mobility of the LEO satellite. Hence, this time variation and multipath propagation require a doubly dispersive channel model for accurate TSLs characterization.

定位/释义：§II-A 起首两句。

**具体变化：** 把“高速→时变”和“时变+多径→需要双扩展模型”两个句子的因果链压缩为单句。；will experience / require a ... channel model→give rise to ... links；删除 accurate ... characterization。

**分类理由：** 可定位完整的两句因果依据，但原句分句没有按原有语法保留，属于支持性概述，而非必要连接后直接组合。

**技术判断：** SUPPORTED：卫星高速及多径导致时变和频率选择性的描述与来源一致；不存在把单一 Doppler 误称为无时变的问题。

**公式适配：** 无公式。

**处理建议：** 若严格要求原句，保留 Shen 的两句及其因果连接，仅调整 TSLs 首次展开。

### P02-S02 · 有定位的合理原句组合

**当前稿完整句（含公式）：**

```tex
We take the ground device as the stationary reference
point and assume that all propagation paths of device $k$ share the
same Doppler shift $\nu_k$ \cite{huang2026}.
```

**参考原文与定位：**

[huang2026](D:/afdm-gfra/reference/literature/huang2026.pdf)，PDF 第 2 页，II. System Model; Doppler shift。

> Take the ground user as the stationary reference point.

定位/释义：印刷页 2950，左栏 Doppler shift 小段首句。

[huang2026](D:/afdm-gfra/reference/literature/huang2026.pdf)，PDF 第 2 页，II. System Model; Doppler shift，(2)。

> The resulting Doppler term D(ψ) is assumed to be common to all propagation paths within the same satellite-to-ground (S2G) link [15].

定位/释义：印刷页 2950，Eq.(2) 后第二个完整句；下一句以很小的多径角度扩展解释该近似。

**具体变化：** Take→We take，user→device，给同一链路加入 k 下标。；把原文被动假设分句改为与 We take 并列的 and assume that ... share the same ...；D(ψ)→ν_k。；原文同一 S2G 链路各传播路径的范围改写为同一 device k 的全部路径，未扩展为不同设备共用 Doppler。

**分类理由：** 两分句均对应 Huang §II 同一 Doppler 小段的可定位原句；主动/被动调整用于合成同一主语的并列句，未添加额外物理前提。按协议接受合理组合。该结论并非由“Doppler”词汇重合或仅由仿真设定推断。

**技术判断：** SUPPORTED：Huang p.2 正文明言同链路各径共用 Doppler，并以很小的多径角扩展作近似依据；这里仍须理解为建模近似，非所有移动散射环境的恒等式。

**公式适配：** D(ψ)→ν_k；source 的单用户链路扩展为按 k 独立定义的一组链路，没有假定 ν_k=ν_{k′}。

**处理建议：** 可保留；正文可补一句小角扩展的物理理由，若用户要求最小变更则无需扩写。

### P02-S03 · 本稿定义、假设或推导

**当前稿完整句（含公式）：**

```tex
Let $\mathbf a_k$ denote the uniform planar array (UPA) response vector
of device $k$, and let $t_{\rm c}$ denote the time measured from the
start of the transmission block.
```

**参考原文与定位：**

[li2023](../../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/strict_sentence_audit_20261029/sources/li2023.pdf)，PDF 第 4 页，II-B. Signal Models。

定位/释义：左栏 Eq.(3) 之前的阵列段：先给出按路径的二维到达角和 Kronecker 阵列向量，再基于星地距离长令同一终端各路径到达角近似相同，并去掉阵列向量的路径下标。这里为中文释义，无英文直引。

[shen2025](D:/afdm-gfra/reference/literature/shen2025.pdf)，PDF 第 3 页，II-A. Terrestrial-satellite Link Model，(1)。

定位/释义：Eq.(1)：逐路径 h_{i,u} δ(τ−τ_{i,u}) δ(ν−ν_{i,u}) 乘 e^{jπ n_z Θ^z_u} e^{jπ n_y Θ^y_u}；阵列角没有路径下标，而 ν_{i,u} 有路径下标。Eq.(1) 后 where 句定义天线索引与 physical paths。

**具体变化：** a_k 是本稿给共同 UPA 阵列响应所取符号；Shen 用逐天线指数，Li 用 g_k。；t_c 从本稿 transmission block 起点计时，是本稿新增的时间参考定义。

**分类理由：** 查阅的来源支持共同阵列响应概念，但未找到含此时间起点和这两个定义的对应完整原句。本句是作者符号/坐标定义，不能因 Let ... denote 模板常见而算原句。

**技术判断：** SUPPORTED AS DEFINITION：共同 a_k 需采用同设备各径 AoA 近同的近似；Li p.4 有明确说明，Shen Eq.(1)采用该结构。t_c 可自行定义。

**公式适配：** 把逐天线阵列因子收成向量；确定接收端块参考时间。该定义不等于各时刻 h_k 不变。

**处理建议：** 作为本稿定义明确保留，并在引入共同 a_k 处引用/说明相同 AoA 近似；若要求每句均为参考原句，则此句不满足，不能作已通过处理。

### P02-S04 · 本稿定义、假设或推导

**当前稿完整句（含公式）：**

```tex
After compensation for the common
propagation delay $\tau_c$ at the satellite receiver, the time-varying
channel impulse response from device $k$ to the satellite is
\begin{equation}
 \mathbf h_k(t_{\rm c},\tau)
 =\mathbf a_k\sum_{\ell=1}^{L_k}g_{k\ell}
 e^{j2\pi\nu_k t_{\rm c}}\delta(\tau-\tau_{k\ell}),
 \label{eq:physical-channel}
\end{equation}
where $k=1,\ldots,K$, $L_k$ is the number of physical paths,
$g_{k\ell}$ is the complex gain of the $\ell$th path, and
$\delta(\cdot)$ is the Dirac delta function.
```

**参考原文与定位：**

[li2023](../../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/strict_sentence_audit_20261029/sources/li2023.pdf)，PDF 第 3 页，II-B. Signal Models，(2)。

定位/释义：右栏 Eq.(2) 及紧跟的 where 句：给出逐路径复增益、Doppler、绝对传播延迟、阵列向量相乘求和的时变冲激响应，逐项解释这些量。中文释义，无英文直引。

[li2023](../../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/strict_sentence_audit_20261029/sources/li2023.pdf)，PDF 第 4 页，II-B. Signal Models。

定位/释义：左栏 Eq.(3) 之前的阵列段：先给出按路径的二维到达角和 Kronecker 阵列向量，再基于星地距离长令同一终端各路径到达角近似相同，并去掉阵列向量的路径下标。这里为中文释义，无英文直引。

[shen2025](D:/afdm-gfra/reference/literature/shen2025.pdf)，PDF 第 3 页，II-A. Terrestrial-satellite Link Model，(1)。

定位/释义：Eq.(1)：逐路径 h_{i,u} δ(τ−τ_{i,u}) δ(ν−ν_{i,u}) 乘 e^{jπ n_z Θ^z_u} e^{jπ n_y Θ^y_u}；阵列角没有路径下标，而 ν_{i,u} 有路径下标。Eq.(1) 后 where 句定义天线索引与 physical paths。

[shen2025](D:/afdm-gfra/reference/literature/shen2025.pdf)，PDF 第 3 页，II-A. Terrestrial-satellite Link Model，(1)。

> As shown in Fig. 1, τ_{i,u} = τ̃_{i,u} − τ^c represents the differential delay for the i-th path from the u-th device to the satellite, where τ̃_{i,u} and τ^c are denoted as propagation delay and common delay, respectively.

定位/释义：Eq.(1) 后第二句。

[huang2026](D:/afdm-gfra/reference/literature/huang2026.pdf)，PDF 第 2 页，II. System Model; Doppler shift，(2)。

> The resulting Doppler term D(ψ) is assumed to be common to all propagation paths within the same satellite-to-ground (S2G) link [15].

定位/释义：印刷页 2950，Eq.(2) 后第二个完整句；下一句以很小的多径角度扩展解释该近似。

**具体变化：** Li Eq.(2) 的逐路径 â、ν_{k,q}、τ_{k,q}、g_{k,q} 经符号改名与参数约束，得到共同 a_k 和 ν_k。；Shen 的差分时延替代绝对时延；本稿指定接收端补偿共同传播时延。；where 合并路径数、复增益和 Dirac 函数定义，但“补偿后时变向量 CIR”完整句及本稿公式不是任一参考原句。

**分类理由：** 这是可说明来源的模型适配/公式推导：至少施加共同阵列、共同 Doppler，并变更延迟和时间参考。不能称只做术语替换，也不能以多篇分别支持各个词语即认定原句组合。

**技术判断：** CONDITIONALLY CONSISTENT：在同设备各径共同 Doppler、共同 AoA、差分延迟及固定块参考下数学形式成立。Shen 只直接给差分时延模型和共同延迟定义，其正文没有逐字给出本稿“在卫星接收机补偿后”的操作句。

**公式适配：** 从 Li 的逐路径时变 CIR 出发，令 ν_{kℓ}=ν_k、a_{kℓ}=a_k；以 τ̃_{kℓ}−τ_c 重定延迟零点。若接收端 t_c 的零点随共同补偿平移，所产生的固定 Doppler 相位须吸收入 g_{kℓ}，因 g 为复增益可做到。Shen Eq.(4) 使用 e^{j2πν(t−τ)} 的约定，与本稿 e^{j2πνt_c} 比较时也须相应吸收逐路径固定相位；二者不能在保留同一增益数值时直接等同。

**处理建议：** 保留为明确的本稿适配，并在公式附近补来源和前提，尤其说明共同 a_k 与时间/复增益约定。不能将该整句报告为参考原句直接改名。

### P02-S05 · 有依据但经过自主改写

**当前稿完整句（含公式）：**

```tex
The differential delay
of this path is $\tau_{k\ell}=\widetilde\tau_{k\ell}-\tau_c$, where
$\widetilde\tau_{k\ell}$ denotes its propagation delay.
```

**参考原文与定位：**

[shen2025](D:/afdm-gfra/reference/literature/shen2025.pdf)，PDF 第 3 页，II-A. Terrestrial-satellite Link Model，(1)。

> As shown in Fig. 1, τ_{i,u} = τ̃_{i,u} − τ^c represents the differential delay for the i-th path from the u-th device to the satellite, where τ̃_{i,u} and τ^c are denoted as propagation delay and common delay, respectively.

定位/释义：Eq.(1) 后第二句。

**具体变化：** 把“τ差值 represents differential delay”改为“differential delay is τ差值”，重排定义方向。；删除 Fig.1 指引、重复的设备/卫星描述；把 propagation delay and common delay 的双定义拆出，只在本句保留传播延迟。

**分类理由：** 精确差分时延等式与物理含义有来源，但完整句的语序与从句组织已改写，不能归入仅术语替换。

**技术判断：** SUPPORTED：τ_{kℓ}=τ̃_{kℓ}−τ_c 与 Shen 相同。

**公式适配：** u→k、i→ℓ、共同延迟 τ^c→τ_c，差分时延等式无变化。

**处理建议：** 若必须逐句原句适配，恢复 Shen 该句的原有定义组织，并只改索引/删除失效图指引。

### P02-S06 · 有依据但经过自主改写

**当前稿完整句（含公式）：**

```tex
The common
delay $\tau_c$ is the propagation time between the satellite and
the closest point on Earth within the beam coverage
\cite{shen2025}.
```

**参考原文与定位：**

[shen2025](D:/afdm-gfra/reference/literature/shen2025.pdf)，PDF 第 3 页，II-A. Terrestrial-satellite Link Model，(1)。

> The common delay corresponds to the propagation time between the satellite and the closest point on earth within the beam coverage [21].

定位/释义：Eq.(1) 后 τ 差定义之后。

**具体变化：** 增加 τ_c 符号。；corresponds to→is；earth→Earth；移除 Shen 的内部编号 [21]，替换为本稿引用。

**分类理由：** 核心连续原文高度一致，事实精确对应；但 corresponds to→is 是普通谓语改写，并非必要技术对象替换。严格类别应保留这个差别，不能把技术正确等同 TERM_ONLY。

**技术判断：** SUPPORTED：共同延迟取波束内最近地面点到卫星的传播时间，来源直接明确。

**公式适配：** 只补 τ_c 标签，无公式推导。

**处理建议：** 若严格要求仅术语替换，可把 is 恢复为 corresponds to；其余保留。

## P03

原文行号：39–50。

**来源顺序：** Shen Eq.(1) 阵列项 + Li §II-B 一般间距阵列，写成本稿向量索引；Shen 方向余弦 + Li 间距/波长定义的改写；本稿四参数短块假设，背景为 Shen/Huang 的短时条件及 Li 的角度缓变

**跨来源组合：** 是

**结构变化：** 将阵列指数一般化后新增共同的块内参数冻结条件；该末句是本稿假设，不能由前两句阵列定义或 Li 的预补偿后 block fading 直接推出。短块条件应保留。

**段落结论：** 1 句支持性改写，2 句本稿定义/推导；当前三句都不能归为仅术语替换或直接原句组合。

### P03-S01 · 本稿定义、假设或推导

**当前稿完整句（含公式）：**

```tex
For antenna indices $n_z=0,\ldots,M_z-1$ and
$n_y=0,\ldots,M_y-1$, the entries of $\mathbf a_k$ are given by
\begin{equation}
 [\mathbf a_k]_{n_z+M_zn_y}
 =e^{j2\pi(d_yn_y\mu_{y,k}+d_zn_z\mu_{z,k})/\lambda}.
 \label{eq:upa}
\end{equation}
```

**参考原文与定位：**

[shen2025](D:/afdm-gfra/reference/literature/shen2025.pdf)，PDF 第 3 页，II-A. Terrestrial-satellite Link Model，(1)。

定位/释义：Eq.(1)：逐路径 h_{i,u} δ(τ−τ_{i,u}) δ(ν−ν_{i,u}) 乘 e^{jπ n_z Θ^z_u} e^{jπ n_y Θ^y_u}；阵列角没有路径下标，而 ν_{i,u} 有路径下标。Eq.(1) 后 where 句定义天线索引与 physical paths。

[li2023](../../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/strict_sentence_audit_20261029/sources/li2023.pdf)，PDF 第 4 页，II-B. Signal Models。

定位/释义：左栏第一完整段的无编号 UPA 公式 g(θ)=a_{M_x}(sin θ_y cos θ_x)⊗a_{M_y}(cos θ_y)，以及随后逐元素 a_{n_v}(x) 定义；其 where 句定义 λ=c/f_c 和沿轴相邻阵元间距 d_v。中文释义，无英文直引。

**具体变化：** 由 Shen 的两个逐天线阵列指数抽取并相乘，写成本稿向量单个元素。；引入任意 d_y,d_z 和 λ；Shen Eq.(1) 的 π 指数对应 d_y=d_z=λ/2。；Li 一般间距向量具有负号和归一化，本稿改用正号和未归一化形式，另改轴命名与向量索引。

**分类理由：** 检索到的是源公式和相应定义，而不是“for antenna indices ... entries ... given by”连同此公式的原句。本稿完成向量化、索引展开与间距一般化，属于有来源的数学定义/适配。

**技术判断：** CONDITIONALLY CONSISTENT：当 μ 是相应 y/z 轴方向余弦并采用该接收阵列相位约定时公式成立；d=λ/2 时还原 Shen Eq.(1) 的阵列因子。归一化/相位符号与 Li 不同，不应声称其公式逐符号一致。

**公式适配：** n_z+M_z n_y 的索引与 Shen 的 n_z+n_y N_z 一致。将 e^{jπn_zΘ_z}e^{jπn_yΘ_y} 改写为 e^{j2π(d_y n_y μ_y+d_z n_z μ_z)/λ}，需要显式一般间距平面波阵列模型；不是只改变量名。

**处理建议：** 保留为本稿定义，附 Shen/Li 来源并写明阵列约定；若本稿实际固定半波长间距，可直接令 d_y=d_z=λ/2，但本次仅审计不修改。

### P03-S02 · 有依据但经过自主改写

**当前稿完整句（含公式）：**

```tex
Here, $\bigl(\mu_{y,k},\mu_{z,k}\bigr)$ are the directional cosines,
$\bigl(d_y,d_z\bigr)$ are the antenna spacings, and $\lambda$ is the
wavelength.
```

**参考原文与定位：**

[shen2025](D:/afdm-gfra/reference/literature/shen2025.pdf)，PDF 第 3 页，II-A. Terrestrial-satellite Link Model，(1)。

> The directional cosines Θ^z_u = cos ϑ^z_u and Θ^y_u = sin ϑ^z_u sin ϑ^a_u, along the z-axis and y-axis, depend on the zenith angle ϑ^z_u and azimuth angle ϑ^a_u, respectively.

定位/释义：§II-A 在本页末尾的最后一句。

[li2023](../../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/strict_sentence_audit_20261029/sources/li2023.pdf)，PDF 第 4 页，II-B. Signal Models。

定位/释义：左栏第一完整段的无编号 UPA 公式 g(θ)=a_{M_x}(sin θ_y cos θ_x)⊗a_{M_y}(cos θ_y)，以及随后逐元素 a_{n_v}(x) 定义；其 where 句定义 λ=c/f_c 和沿轴相邻阵元间距 d_v。中文释义，无英文直引。

**具体变化：** Shen 的两个方向余弦及角度关系改写为符号对 (μ_y,k, μ_z,k) 的统称。；Li 的 where 句给出波长及相邻阵元间距，本稿精简重组为 Here 后的三个并列定义。；未保留源句的完整原句或分句顺序。

**分类理由：** 三个物理名词都有可定位来源，含义可支持；本稿采用新符号并重写成并列定义句，不能将普通定义模板当作具体原句证据。

**技术判断：** SUPPORTED：方向余弦、间距和波长为上述阵列公式的相应物理量。方向余弦应明确关联 y/z 轴；该解释由公式和符号下标可推知，但当前句未展开角度定义。

**公式适配：** μ_y,k 对应 Shen Θ^y_u，μ_z,k 对应 Θ^z_u；d_y,d_z,λ 沿用一般阵列模型含义。

**处理建议：** 若必须采用原句组合，可明确拼合 Shen 的 directional-cosines 句与 Li 的定义分句，并妥善处理 Li 引用长度；现句应如实标为支持性改写。

### P03-S03 · 本稿定义、假设或推导

**当前稿完整句（含公式）：**

```tex
The path gains, differential delays, Doppler shifts, and
angles of arrival are assumed to remain approximately constant
within a transmission block.
```

**参考原文与定位：**

[shen2025](D:/afdm-gfra/reference/literature/shen2025.pdf)，PDF 第 4 页，II-B. Transmission Scheme，(1), (9)。

> Fortunately, H^{DDS}_{n_z,n_y,u}[k′,l′,l] remains approximately constant over Q consecutive frames, benefited by the quasi-static property of (1) in the delay-Doppler domain.

定位/释义：右栏最后一句，Eq.(9) 讨论之后。

[shen2025](D:/afdm-gfra/reference/literature/shen2025.pdf)，PDF 第 5 页，II-B. Transmission Scheme。

> In practice, the quasi-static property may be disrupted when the number of transmitted frames becomes large.

定位/释义：左栏上端第二句；随后给 Q=8 与 Q=25 的 Doppler/时延变化例子，说明近似有时间范围。

[huang2026](D:/afdm-gfra/reference/literature/huang2026.pdf)，PDF 第 3 页，III-A. Score-Based Model Training for AFDM Channel，(6)。

> Meanwhile, although AFDM can only guarantee approximate channel invariance within a finite signaling duration, the effective channel variation across several adjacent pilot sequences remains negligible because the corresponding Doppler-angle variation over a short interval is relatively small within pilot frames.

定位/释义：印刷页 2951，左栏 Eq.(6) 后第二段末句。

[li2023](../../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/strict_sentence_audit_20261029/sources/li2023.pdf)，PDF 第 4 页，II-B. Signal Models，(5)。

定位/释义：左栏阵列段末两句指出星地距离长使空间角变化缓慢；右栏 Eq.(5) 后的 block-fading 讨论则依赖终端 Doppler/时延预补偿。该后者条件不适用于本稿无终端预补偿情形。中文释义，无英文直引。

**具体变化：** 把 Shen 对 Q 帧 DD 域信道的准静态讨论与 Huang 的短时相邻导频讨论，细化为四类物理参数在本稿 transmission block 内近似不变。；加入 angles of arrival 的联合冻结条件；Li 只直接说明角度缓变。；未给 block 时长相对于这些变化尺度的明确界限。

**分类理由：** 在本轮核查的 Shen、Ding、Huang、Li 及 Cai 两版本中，未找到列出这四类参数并以 transmission block 为范围的对应原句。相关文献提供短时近似的背景，但该完整假设是本稿明确建立的模型条件。其写法“are assumed”允许作为作者假设，不等于来源错误或必须删除。

**技术判断：** CONDITIONALLY REASONABLE：冻结 g、τ、ν、AoA 不会消除 e^{j2πνt_c} 的相位变化，因而与时变 CIR 并不矛盾。该近似只适用于足够短的块，Shen 明示 Q 大时失效。Li Eq.(5) 后的补偿后 block fading 不可搬用为本稿无终端预补偿的直接证明。

**公式适配：** 无新显示公式；这是后续跨帧只含共同相位变化所需的建模条件。文献不能自动保证本稿任意 Q 或任意 block 时长均满足近似。

**处理建议：** 明确标为本稿短块假设，并在邻近处引用 Shen/Huang/Li 的限定依据。若用户坚持每句都是参考原句，本句目前不满足；不能只加一条泛引就标成原句适配。

## P04

原文行号：54–67。

**来源顺序：** cai2026 II-A；huang2026 II；本稿向量/矩阵定义；cai2026 II-A及V-C的设计动机 + 本稿VI-A构造；本稿内部指引

**跨来源组合：** 是

**条件变化：** 是：OFDM符号及对角矩阵被改为AFDM帧及Q×KN矩阵，正交维度、可取行数和能量定义随之改变。当前DFT构造能满足新条件，但不能据此倒推文本原句来自Cai。

**段落结论：** 主审统一后：1句合理原句组合、1句支持性改写、4句本稿定义或内部指引。

### P04.S01 · 有定位的合理原句组合

**当前稿完整句（含公式）：**

```tex
We allocate $Q$ AFDM frames to pilot transmission \cite{cai2026},
with $N$ chirp subcarriers per frame \cite{huang2026}.
```

**参考原文与定位：**

[cai2026](D:/afdm-gfra/reference/literature/cai2026.pdf)，PDF 第 4 页，II-A。

> Assume that a total of T OFDM symbols are allocated for pilot transmission.

[cai2026_stmp_v2](D:/afdm-gfra/reference/literature/cai2026_stmp_v2.pdf)，PDF 第 4 页，II-A。

定位/释义：与正式版相同的导频分配句，式(3)之前

[huang2026](D:/afdm-gfra/reference/literature/huang2026.pdf)，PDF 第 2 页，II。

> Let N denote the number of AFDM chirp subcarriers.

**具体变化：** Assume that a total of ... are allocated 改成 We allocate；第二来源的 Let N denote ... 改成 with N ... per frame；OFDM symbols 改为 AFDM frames，T 改 Q。

**分类理由：** 统一与P02-S02的组合口径：Cai的分配导频句改为主动语态，接Huang对每帧N个chirp subcarriers的定义；两条具体命题都可定位，主被动调整与with连接不增加新的技术结论。不能仅因组合句改变主被动而否定组合，同时却接受P02-S02的同类调整。

**技术判断：** 多帧导频资源安排是可行的本稿设定。Cai讨论OFDM符号，Huang的frame描述不自动包含本文CPP；这里的frame含义须以后文定义为准。

**公式适配：** 无独立公式；Q帧及每帧N个AFDM chirp subcarriers是本文对两个来源的系统适配。

**处理建议：** 可按有定位的合理组合保留；技术范围仍限于本稿明确的帧结构。

主审调整：原分组类别为有依据但经过自主改写；最终以本条分类及上述理由为准。

### P04.S02 · 有依据但经过自主改写

**当前稿完整句（含公式）：**

```tex
Let $P_{qkn}\in\mathbb C$ denote the pilot symbol transmitted by
device $k$ on chirp subcarrier $n$ in frame $q$.
```

**参考原文与定位：**

[cai2026](D:/afdm-gfra/reference/literature/cai2026.pdf)，PDF 第 4 页，II-A。

> Let q_ktn ∈ C be the pilot symbol transmitted by the k-th device during the t-th OFDM symbol on the n-th subcarrier.

**具体变化：** Let ... be 改为 Let ... denote；during ... on ... 的顺序改成 on ... in ...；删去 the k-th 形式，并改符号、AFDM子载波和帧名。

**分类理由：** 传输者、导频、时频位置均有原句，但本句还改了谓词和介词结构；不能只凭同一模板称TERM_ONLY。

**技术判断：** 定义一致，k为设备、q为帧、n为发射chirp子载波。

**公式适配：** q_ktn → P_qkn；OFDM子载波符号改成AFDM chirp子载波符号是系统定义，不声称两种调制信道相同。

**处理建议：** 按严格原句目标需恢复来源句法，再列明对象和索引替换。

### P04.S03 · 本稿定义、假设或推导

**当前稿完整句（含公式）：**

```tex
The corresponding
pilot vector is
$\mathbf p_{qk}=[P_{qk0},\ldots,P_{qk,N-1}]^{\mathsf T}
\in\mathbb C^N$, $k=1,\ldots,K$, $q=0,\ldots,Q-1$.
```

**参考原文与定位：**

[cai2026](D:/afdm-gfra/reference/literature/cai2026.pdf)，PDF 第 4 页，II-A，(3)之前。

定位/释义：导频定义后构造Q_kt=diag{q_kt1,...,q_ktN}；并非本文列向量p_qk

**具体变化：** 自行将N个标量排成列向量，增加全部k、q的索引范围。

**分类理由：** 在已检查语料中未定位该完整英文句；Cai相邻句定义的是对角矩阵，不能拿它替代本句列向量原句。

**技术判断：** 维度和索引与P_qkn一致。

**公式适配：** 向量化定义本身无需外部定理；属于本稿记号。

**处理建议：** 保留为明确的本稿定义；若作者坚持每一句均参考原句，本句不满足该限定。

### P04.S04 · 本稿定义、假设或推导

**当前稿完整句（含公式）：**

```tex
Let $\mathbf P\in\mathbb C^{Q\times KN}$ denote the pilot matrix
known at the satellite receiver, with entries
$[\mathbf P]_{q,(k-1)N+n}=P_{qkn}$.
```

**参考原文与定位：**

[cai2026](D:/afdm-gfra/reference/literature/cai2026.pdf)，PDF 第 4 页，II-A，(4)。

定位/释义：式(4)及其where：Q=[Q_1,...,Q_K]，Q_k由各时刻对角导频矩阵纵向叠加，维度NT×NK

**具体变化：** 新建Q×KN矩阵、规定列索引(k−1)N+n，并明确接收端已知。

**分类理由：** 本稿把帧作为行、设备及发射chirp索引作为列；不是Cai的NT×NK块对角叠加矩阵。没有本句的参考原句。

**技术判断：** 所给索引能唯一重排导频；接收端已知是本稿建模假设。

**公式适配：** Cai矩阵的行含时间和接收子载波，本文行只含帧；两者不能只换尺寸而宣称同一构造。

**处理建议：** 标为本稿符号重排/定义。

### P04.S05 · 本稿定义、假设或推导

**当前稿完整句（含公式）：**

```tex
For simplicity, $\mathbf P$ is chosen to satisfy
$\mathbf P\mathbf P^{\mathsf H}=KE_p\I_Q$, with equal pilot energy
$E_p=\|\mathbf p_{qk}\|^2$ for all devices and frames \cite{cai2026}.
```

**参考原文与定位：**

[cai2026](D:/afdm-gfra/reference/literature/cai2026.pdf)，PDF 第 4 页，II-A，(4)后。

> For simplicity, we impose the condition that Q is partial orthogonal, specifically requiring that QQᴴ = KP I_NT, where each device has the same transmit power budget P.

[cai2026](D:/afdm-gfra/reference/literature/cai2026.pdf)，PDF 第 10–11 页，V-C，(66)。

定位/释义：式(66)采用K×K酉矩阵的行；同一子载波内T个行索引不同，NT个选择可跨子载波复用

**具体变化：** impose the condition...specifically requiring 压缩成 is chosen to satisfy；增加每设备每帧列向量能量E_p=||p_qk||²；Q矩阵结构与行维不同。

**分类理由：** Cai支持采用行正交导频简化估计的思想，但本文完整条件是对新矩阵及新能量定义的构造，不能冒作Cai原句仅术语替换。

**技术判断：** 技术成立，已仅用当前VI-A eq:pilot做解析核对：不同DFT行、全列置换和固定列相位给PPᴴ=K E_p I_Q；每设备N个等模符号给能量E_p。无需实验。

**公式适配：** 本文构造给[P Pᴴ]_{qq′}=(E_p/N)Σ_{c=0}^{KN−1}exp(−j2π(r_q−r_q′)c/(KN))=K E_p δ_{qq′}，Q≤KN；每组Σ_n|P_qkn|²=N(E_p/N)=E_p。Cai则在各子载波上从K×K矩阵取T个行，条件与能量口径不同。

**处理建议：** 可保留该有效构造，但应把Cai归为设计动机，并明确这是本文构造；不得计为原句适配通过。

### P04.S06 · 本稿定义、假设或推导

**当前稿完整句（含公式）：**

```tex
The pilot construction is given in Section~\ref{sec:simulation-settings}.
```

**参考原文与定位：**

[cai2026](D:/afdm-gfra/reference/literature/cai2026.pdf)，PDF 第 4 页，II-A。

> The design of partial orthogonal Q is deferred to Section V-C.

**具体变化：** The design of partial orthogonal Q / is deferred 改成 The pilot construction / is given，并替换章节目标。

**分类理由：** 来源有相似章节指引，但本文句子指向本稿VI-A，属于内部指引；不是只换章节号的完整原句。

**技术判断：** 已核对06_simulation_results.tex的sec:simulation-settings确有eq:pilot。

**公式适配：** 不适用；章节指引。

**处理建议：** 保留为内部指引；严格逐句原句统计中单列。

## P05

原文行号：69–93。

**来源顺序：** Ding II采样关系 / Huang II；Ding II式(1)及参数说明；Ding矩阵说明 + Huang/Bemani核对正确DAFT约定

**跨来源组合：** 是

**条件变化：** 主要是定义顺序和矩阵表示重写，没有改变标量IDAFT。需区分有效符号时长与含CPP帧时长。

**段落结论：** 3句均有数学/概念支持，但英文均经过自行改写；不满足完整原句仅必要替换。

### P05.S01 · 有依据但经过自主改写

**当前稿完整句（含公式）：**

```tex
Let $\Delta f$ denote the subcarrier spacing and
$T_s=1/(N\Delta f)$ denote the sampling interval.
```

**参考原文与定位：**

[ding2026](D:/afdm-gfra/reference/literature/ding2026.pdf)，PDF 第 2 页，II，(1),(3)。

定位/释义：式(1)前系统描述定义sub-carrier spacing Δf；式(3)后where明确Ts=1/(NΔf)

[huang2026](D:/afdm-gfra/reference/literature/huang2026.pdf)，PDF 第 2 页，II。

> Each AFDM frame spans a duration of T = NΔt. The sampling rate is given by 1/Δt, and the subcarrier spacing to Δf = 1/T.

**具体变化：** 把Ding分散在两处的名词与采样间隔公式改写为统一Let ... denote句；Huang对应关系也不是该英文句法。

**分类理由：** 定义和关系明确有源，但不存在当前完整原句；普通Let模板不算原句证据。

**技术判断：** Ts=1/(NΔf)与两个来源一致。

**公式适配：** Ts与Huang的Δt同义；此处N Ts是有效符号时长，不能把它当含CPP的整帧时长。

**处理建议：** 严格原句要求下需采用可定位原句并必要换符号；当前归支持性改写。

### P05.S02 · 有依据但经过自主改写

**当前稿完整句（含公式）：**

```tex
For sample index $t=0,\ldots,N-1$, applying the inverse discrete
affine Fourier transform (IDAFT) to $\mathbf p_{qk}$ yields the
time-domain transmitted signal \cite{ding2026}
\begin{equation}
 s_{qk}[t]=\frac{1}{\sqrt N}\sum_{n=0}^{N-1}
 P_{qkn}e^{j2\pi(c_1t^2+c_2n^2+nt/N)},
 \label{eq:afdm-time-signal}
\end{equation}
where $c_1$ and $c_2$ are AFDM modulation parameters.
```

**参考原文与定位：**

[ding2026](D:/afdm-gfra/reference/literature/ding2026.pdf)，PDF 第 2 页，II，(1)。

> The time-domain transmitted signal is generated through the inverse discrete affine Fourier transform (IDAFT) applied to x_k, mathematically formulated as

[ding2026](D:/afdm-gfra/reference/literature/ding2026.pdf)，PDF 第 2 页，II，(1)后。

> c1 and c2 are AFDM modulation parameters.

**具体变化：** The ... is generated through ... applied to ... 改成 applying ... yields ...；增加For sample index从句；将独立参数句接为where从句。

**分类理由：** 标量IDAFT及参数释义有准确来源，但英文主从结构主动改写，超过仅符号替换及必要拼接。

**技术判断：** 标量公式与Ding式(1)一致，经索引重命名和增加帧索引即可得到。

**公式适配：** Ding n(时间)→t、m(频域)→n、x_k[m]→P_qkn、s_k[n]→s_qk[t]；正号、1/√N和三个相位项均保持。样本范围0,...,N−1与求和一致。

**处理建议：** 若按原句标准，可直接使用Ding该主句并必要符号替换，参数句也有独立原句；当前不记TERM_ONLY。

### P05.S03 · 有依据但经过自主改写

**当前稿完整句（含公式）：**

```tex
Equivalently,
\eqref{eq:afdm-time-signal} can be written in matrix form as
\[
 \mathbf s_{qk}=\mathbf F_{\rm A}^{\mathsf H}\mathbf p_{qk},
\]
where
\begin{equation}
 \begin{gathered}
 \mathbf F_{\rm A}
 =\left[\frac{1}{\sqrt N}e^{-j2\pi(c_2r^2+rt/N+c_1t^2)}
 \right]_{r,t=0}^{N-1}
 \end{gathered}
 \label{eq:daft}
\end{equation}
is the discrete affine Fourier transform (DAFT) matrix.
```

**参考原文与定位：**

[ding2026](D:/afdm-gfra/reference/literature/ding2026.pdf)，PDF 第 2 页，II，(2)。

> The signal in (1) can be represented in matrix form as

[huang2026](D:/afdm-gfra/reference/literature/huang2026.pdf)，PDF 第 2 页，II。

定位/释义：首段给s=Aᴴx=Λ_c1ᴴFᴴΛ_c2ᴴx，并定义A为DAFT矩阵

[bemani2022](../../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/strict_sentence_audit_20261029/sources/bemani2022.pdf)，PDF 第 7–8 页，II及III-A，(11),(16),(18)。

定位/释义：p7式(11),(16)给DAFT矩阵；p8开头给其Hermitian inverse，式(18)后给s=Aᴴx

**具体变化：** 加入Equivalently；The signal in (1)改为方程引用主语；represented改written；将分解矩阵展开为逐元素定义，并用is替代represents。

**分类理由：** 矩阵关系有源，但完整英文句及显式元素展开为本稿重写；不是Ding式(2)文字的原样改名。

**技术判断：** 本文F_A元素与标量式一致，F_Aᴴ确为IDAFT。实际查看Ding PDF p2，式(2)在分解中印F而不是Fᴴ，紧接文字把Aᴴ称DAFT；不能照抄这一处符号不一致。Bemani与Huang支持本文正确约定。

**公式适配：** 从A=Λ_c2 F Λ_c1展开得到[F_A]_{rt}=N^(−1/2)exp[−j2π(c2 r²+rt/N+c1 t²)]；这一步是等价展开，不改变模型。

**处理建议：** 保留正确数学；若追求原句文字，选用符号一致的Huang/Bemani对应文字并记录适配，不照搬Ding的印刷不一致。

## P06

原文行号：95–109。

**来源顺序：** Bemani III-A前缀长度；Bemani II式(14)/III-A式(19) + 本稿mod及多周期推广；本稿含CPP帧长

**跨来源组合：** 是

**条件变化：** 是：来源信道段l_max<N、整数延迟；本文mod式及后续分数延迟/长CPP扩展超出该来源的直接信道结果。2Nc1正整数为本文选择，不能混同原文CPP=CP还需N偶数的条件。

**段落结论：** 1句为支持性改写，2句为本文定义/推导；前缀恒等式技术成立不意味着整段是参考原句。

### P06.S01 · 有依据但经过自主改写

**当前稿完整句（含公式）：**

```tex
The chirp-periodic prefix (CPP) duration is chosen to satisfy
$N_{\rm CPP}T_s\geq\max_{k,\ell}\tau_{k\ell}$.
```

**参考原文与定位：**

[bemani2022](../../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/strict_sentence_audit_20261029/sources/bemani2022.pdf)，PDF 第 8 页，III-A，(19)之前。

定位/释义：式(19)前一段：L_cp为整数，至少为最大delay spread所对应的样本数

[cai2026](D:/afdm-gfra/reference/literature/cai2026.pdf)，PDF 第 4 页，II-A。

> Assume that the cyclic prefix (CP) length exceeds the maximum channel delay spread.

**具体变化：** 将长度文字条件改成CPP duration is chosen to satisfy加不等式；由单链路delay spread改为已补偿公共传播时延后的所有设备残余路径时延最大值。

**分类理由：** 前缀覆盖信道记忆有源；当前简明英文及多设备最大值不是原句仅术语替换。

**技术判断：** 在本稿差分时延非负且所定义连续波形直接延迟的模型内，N_CPP Ts≥max τ_kℓ覆盖所需过去样本。

**公式适配：** N_CPP≥ceil(max τ_kℓ/Ts)是该不等式的整数实现。Bemani正文信道随后限定整数路径时延且l_max<N；当前不等式自身未重复该范围。

**处理建议：** 可保留作为有源条件的本稿改写；不要称其全部内容是Bemani原句。

### P06.S02 · 本稿定义、假设或推导

**当前稿完整句（含公式）：**

```tex
By the chirp periodicity, the prefix samples satisfy \cite{bemani2022}
\begin{equation}
 \begin{gathered}
 s_{qk}[t]=e^{j2\pi c_1(t^2-\langle t\rangle_N^2)}
 s_{qk}[\langle t\rangle_N],\\
 -N_{\rm CPP}\leq t<0,
 \end{gathered}
 \label{eq:cpp}
\end{equation}
where $\langle x\rangle_N=x-N\lfloor x/N\rfloor$ and
$2Nc_1\in\mathbb N_+$.
```

**参考原文与定位：**

[bemani2022](../../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/strict_sentence_audit_20261029/sources/bemani2022.pdf)，PDF 第 7 页，II，(14)。

定位/释义：式(14)：任意整数周期偏移的chirp periodicity

[bemani2022](../../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/strict_sentence_audit_20261029/sources/bemani2022.pdf)，PDF 第 8 页，III-A，(19)。

定位/释义：式(19)：s[n]以s[N+n]及一周期相位表示，n=−L_cp,...,−1

[bemani2022](../../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/strict_sentence_audit_20261029/sources/bemani2022.pdf)，PDF 第 9 页，III-B，(20)–(23)。

定位/释义：信道段式(22)前明确l_max<N且路径时延为整数；p9首句仅在2Nc1为整数且N为偶数时说明CPP退化为CP

**具体变化：** With ... periodicity ... prefix is改成By ... samples satisfy；显式加入mod-N定义及2Nc1正整数条件；使用任意负索引的mod形式。

**分类理由：** 这是从一般周期关系推得的表示和本文参数限制；已核原页，Bemani式(19)并未原样给出本文mod形式，也没有在该原句声称长CPP覆盖多周期。

**技术判断：** mod形式在整数采样点成立：令r=<t>_N、h=(t−r)/N∈Z，Bemani式(14)给相位c1(t²−r²)。N_CPP≤N时化为原式(19)；更长前缀需要本文多周期扩展定义。2Nc1∈N_+是额外选定条件，并非这个整数样本恒等式的必要条件；没有N为偶数不能据此宣称CPP=CP。

**公式适配：** 对−N≤t<0，r=t+N，t²−r²=−(N²+2Nt)，与式(19)同式；对t<−N用一般整数h递推。Bemani后续有效信道推导采用l_max<N，不能直接把它当长时延有效信道已被原文证明。

**处理建议：** 标为本文对Bemani周期关系的推导/推广，说明长CPP范围与额外参数选择；不得称原句照用。

### P06.S03 · 本稿定义、假设或推导

**当前稿完整句（含公式）：**

```tex
Including the CPP, each AFDM frame has duration
$T_{\rm frame}=(N+N_{\rm CPP})T_s$.
```

**参考原文与定位：**

[huang2026](D:/afdm-gfra/reference/literature/huang2026.pdf)，PDF 第 2 页，II。

> Each AFDM frame spans a duration of T = NΔt.

[shen2025](D:/afdm-gfra/reference/literature/shen2025.pdf)，PDF 第 4 页，II-B，(3)。

定位/释义：式(3)后where：OFDM含CP符号时长T_sym=T+T_cp

**具体变化：** 新增Including the CPP，并将N Ts增加为(N+N_CPP)Ts；使用本稿帧计时。

**分类理由：** 所查来源能分别支持有效符号长度与前缀相加思路，但没有当前AFDM含CPP帧长定义的完整原句；本文自行定义时间单位。

**技术判断：** 连续相邻帧、每帧各有N_CPP前缀样本且无额外间隔时正确。

**公式适配：** 这是样本数相加；Huang的T=NΔt不能直接作为本文T_frame。Shen定义的是OFDM符号时长，不是该AFDM帧。

**处理建议：** 保留为明确的本稿定义。

## P07

原文行号：111–142。

**来源顺序：** Huang/Ding有效信道背景；本稿多天线张量及参考时刻；本稿G和连续波形定义/推导；Huang泄漏原句的改写

**跨来源组合：** 是

**条件变化：** 是：单天线矩阵变为多天线张量、引入绝对时间g、频率折返连续波形和多周期CPP；这些是本文模型条件。Huang式(5)有分数效应，不足以自动推出本文所有G定义。

**段落结论：** 5句为本文定义/推导，1句为有明确原句依据的改写；不得把附录推导与外部原句证明混为一类。

### P07.S01 · 本稿定义、假设或推导

**当前稿完整句（含公式）：**

```tex
After CPP removal and DAFT demodulation, the effective channel of
device $k$ in frame $q$ is represented by
$H_k^{(q)}\in\mathbb C^{M\times N\times N}$, with
$H_k=H_k^{(0)}$.
```

**参考原文与定位：**

[huang2026](D:/afdm-gfra/reference/literature/huang2026.pdf)，PDF 第 2 页，II，(4)。

定位/释义：式(4)定义单天线单帧有效矩阵H_eff，未定义本文M×N×N、q索引和H_k=H_k^(0)

[ding2026](D:/afdm-gfra/reference/literature/ding2026.pdf)，PDF 第 2 页，II，(4),(5)。

定位/释义：先去CPP、再DAFT的接收处理及路径矩阵；无本文张量定义

**具体变化：** 新定义设备、接收天线、输出/输入DAFT符号三个索引的张量，并选frame 0为参考。

**分类理由：** 处理顺序有源，但本句核心是本文张量与参考帧定义；未找到对应完整英文原句。

**技术判断：** M个N×N有效矩阵堆叠为M×N×N张量，维度正确。

**公式适配：** Huang的H_eff和Ding逐天线路径算子可提供物理背景，但新增q及参考张量是本文记号。

**处理建议：** 明确作为本稿定义保留，不计入参考原句适配。

### P07.S02 · 本稿定义、假设或推导

**当前稿完整句（含公式）：**

```tex
Retaining fractional
delay and Doppler effects \cite{huang2026}, the entries of $H_k$ are
\begin{equation}
 H_{kmrn}
 =[\mathbf a_k]_m\sum_{\ell=1}^{L_k}g_{k\ell}
 [\mathbf G(\tau_{k\ell}/T_s,\nu_k;N_{\rm CPP})]_{rn},
 \label{eq:channel}
\end{equation}
where $H_{kmrn}$ is the channel coefficient from transmitted
DAFT-domain symbol $n$ to received DAFT-domain symbol $r$ at
antenna $m$.
```

**参考原文与定位：**

[huang2026](D:/afdm-gfra/reference/literature/huang2026.pdf)，PDF 第 2 页，II，(5)。

> To better capture the LEO channel dynamics, we incorporate fractional delay and fractional Doppler effects, and the resulting expression for the elements of the channel matrix H_i is given as follows

[huang2026](D:/afdm-gfra/reference/literature/huang2026.pdf)，PDF 第 2 页，II，(4),(5)。

定位/释义：式(4)给各路径hi H_i叠加；式(5)给单路径分数delay/Doppler元素

**具体变化：** 来源的incorporate句压缩成Retaining...；单天线H_i元素被替换为含a_k、g_kℓ、参考起点N_CPP的多天线张量元素；新增系数的n→r物理定义。

**分类理由：** Huang支持保留分数效应与路径叠加，但并无该张量公式及where原句。整句不能由只替换术语得到；其核心为本稿模型合成。

**技术判断：** 给定本文物理信道的公共a_k、ν_k和下一句定义的G，线性叠加式成立；这不等同于已证明G与Huang式(5)逐项相同。

**公式适配：** a_k乘路径增益、d=τ/Ts、取g=N_CPP均是本稿定义。Huang式(5)需另核归一化Doppler符号、频率折返区间及参考时间，不能仅因“fractional”相同声称同式。

**处理建议：** 保留为本文构造；引文仅支持分数效应处理的背景。若要称Huang公式适配，需另给完整符号/区间/相位映射。

### P07.S03 · 本稿定义、假设或推导

**当前稿完整句（含公式）：**

```tex
The matrix $\mathbf G(d,\nu;N_{\rm CPP})$ is the effective channel
matrix of a path with gain $1$, normalized delay $d$, and Doppler
shift $\nu$ in frame $0$.
```

**参考原文与定位：**

[huang2026](D:/afdm-gfra/reference/literature/huang2026.pdf)，PDF 第 2 页，II，(4),(5)。

定位/释义：式(4)中把hi置于H_i外，因此H_i为单位增益路径矩阵；无本文g或frame 0

**具体变化：** 定义G的三个参数及单位增益、归一化时延、frame 0含义。

**分类理由：** 单位路径思想有源，当前完整句仍是本稿函数记号说明。

**技术判断：** 与随后G(d,ν;g)及g0=N_CPP一致。

**公式适配：** G第三个参数是有用段起点g；G(d,ν;N_CPP)是参考帧的特例，不是“CPP长度独立地改变所有帧G”的一般表述。

**处理建议：** 保留为本稿定义；如以后修订，可更早说明第三参数是起点，减少首次出现时的歧义。

### P07.S04 · 本稿定义、假设或推导

**当前稿完整句（含公式）：**

```tex
For a useful interval starting at sample
$g$ of the transmission block, the path matrix is
\begin{equation}
 \begin{gathered}
 \mathbf G(d,\nu;g)=\mathbf F_{\rm A}\mathbf D_{\nu,g}\mathbf B_d,\\
 \mathbf D_{\nu,g}=\diag\{e^{j2\pi\nu T_s(g+t)}\}_{t=0}^{N-1},\\
 [\mathbf B_d]_{tn}=\varphi_n(t-d).
 \end{gathered}
 \label{eq:path-operator-system}
\end{equation}
```

**参考原文与定位：**

[huang2026](D:/afdm-gfra/reference/literature/huang2026.pdf)，PDF 第 2 页，II，(5)。

定位/释义：式(5)为元素级分段求和式，使用l_eq=k_ν+C l_τ及L_m,q；并不写F_A D_ν,g B_d

[bemani2022](../../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/strict_sentence_audit_20261029/sources/bemani2022.pdf)，PDF 第 10 页，III-C/D，(25)–(28)。

定位/释义：整数delay的路径算子A Γ_CPP Δ_f Π^l Aᴴ及其输入输出式；此处仅精确定位，无原文引语

**具体变化：** 新定义连续波形延迟矩阵B_d、绝对时间D_ν,g，以及三者乘积G。

**分类理由：** 在已检查参考语料中无该完整英文句或带g的算子式；本稿附录app:afdm-model给出自己的波形与推导，不能用本稿证明充作参考原句。

**技术判断：** 给定本稿附录app:afdm-model的φ_n，F_A D B_d按“延迟波形采样→Doppler→DAFT”组合成立；其连续波形插值/频率折返选择属于模型条件。未凭来源认定该式唯一代表所有分数delay AFDM实现。

**公式适配：** 本稿附录app:afdm-model展开为常相位exp[j2π(c1d²+c2(n²−r²)−nd/N+νTs g)]乘Σ_t exp[j2π((n−r)/N−2c1d+νTs)t]exp[j2πζ_tn d]/N。对照Huang式(5)至少须映射k_ν=−νNTs、ζ对应折返区间，并处理exp(j2πνTs g)参考相位；原文未提供本文多周期CPP定义，不能仅凭形式相似声称完整等价。

**处理建议：** 标为本文推导并保留附录支撑；若拟说直接采用Huang，需要补逐项映射，而不是只改引文。

### P07.S05 · 本稿定义、假设或推导

**当前稿完整句（含公式）：**

```tex
Here, $\varphi_n$ is the $n$th AFDM basis waveform with its CPP
extension, defined in Appendix~\ref{app:afdm-model}, and frame $0$
corresponds to $g=N_{\rm CPP}$.
```

**参考原文与定位：**

本句为本稿内部定义/指引，未认定为参考论文原句。

**具体变化：** 本文φ_n的含CPP延拓定义和附录指引；设定首有用样本g=N_CPP。

**分类理由：** 这是内部定义说明，不存在应当据为外部原句的对象；已实际读appendix_afdm_channel_model.tex。

**技术判断：** 与先发送N_CPP个前缀样本、随后从0起编号的N个有用样本相容；分数delay需要完整的样间波形定义。

**公式适配：** φ_n(ξ)含wξ=<ξ>_N和ζ_n(w)=floor(2c1w+n/N)；该具体组合及负时间延拓应归本稿，不宜说Huang/Bemani给了这个完整φ式。

**处理建议：** 保留为本稿定义/内部指引。

### P07.S06 · 有依据但经过自主改写

**当前稿完整句（含公式）：**

```tex
Fractional delays and Doppler shifts can cause
significant power leakage in the effective channel matrix in
\eqref{eq:path-operator-system}, thereby weakening the sparsity of
$H_k$ \cite{huang2026}.
```

**参考原文与定位：**

[huang2026](D:/afdm-gfra/reference/literature/huang2026.pdf)，PDF 第 2 页，II，(5)后。

> In practical propagation environments, fractional Doppler shifts and fractional time delays can introduce significant power leakage in the effective channel matrix of (5), thereby weakening the sparsity of H_eff.

**具体变化：** 删In practical propagation environments；fractional Doppler shifts and fractional time delays改为Fractional delays and Doppler shifts；introduce改cause；of (5)改为in本文算子式；H_eff改H_k。

**分类理由：** 原句定位很明确且含义基本相同，但有主动删改和同义改写，不是只换必要术语/符号。

**技术判断：** 对分数delay/Doppler通常引起扩散的定性说法有来源支持；措辞can保留可能性，并非说所有参数必然显著泄漏。将它特指本文G需以本稿波形选择为条件。

**公式适配：** Huang说其式(5)，本文替换成路径算子；这种引用迁移不是自动的矩阵等价证明。

**处理建议：** 若坚持原句要求，保留Huang整句句法，仅替换已解释的符号/方程；同时明确本稿G的适配性质。

## P08

原文行号：144–158。

**来源顺序：** 本稿帧计时；Huang公共Doppler假设 + 本稿G分解；本稿多观测结论；Shen/Huang仅提供相关先例

**跨来源组合：** 是

**条件变化：** 是：Shen原模型允许逐路径相位且为OTFS；本文借助公共Doppler和冻结路径参数约化为每设备公共标量。Huang相邻pilot间近似不变也不等于该相位分解。

**段落结论：** 3句全是本文定义/推导，不是已有参考完整原句；技术成立的条件已显式列出。

### P08.S01 · 本稿定义、假设或推导

**当前稿完整句（含公式）：**

```tex
For frame $q$, the $N$ samples after CPP removal start at
$g_q=N_{\rm CPP}+q(N+N_{\rm CPP})$.
```

**参考原文与定位：**

[shen2025](D:/afdm-gfra/reference/literature/shen2025.pdf)，PDF 第 4 页，II-B，(3)。

定位/释义：式(3)用n+qN表示OTFS帧中的OFDM符号起点；不是本文AFDM样本起点

**具体变化：** 按本文帧结构新定义g_q。

**分类理由：** 所查来源没有这个完整原句或AFDM含CPP的g_q式；这是从P06帧长计算出的索引。

**技术判断：** 对q从0起、帧连续、每帧同一CPP长度的约定，首个有效样本为N_CPP+q(N+N_CPP)。

**公式适配：** g_q−g0=q(N+N_CPP)，乘Ts得到qT_frame。

**处理建议：** 保留为本稿计时定义。

### P08.S02 · 本稿定义、假设或推导

**当前稿完整句（含公式）：**

```tex
Since $\nu_k$ is common to all paths of device $k$,
\eqref{eq:path-operator-system} yields
\begin{equation}
 \begin{gathered}
 H_k^{(q)}=e^{jq\beta_k}H_k,\\
 \beta_k=\operatorname{wrap}(2\pi\nu_kT_{\rm frame}),
 \end{gathered}
 \label{eq:twc-frame-channel}
\end{equation}
where $\operatorname{wrap}(\cdot)$ maps an angle to $[-\pi,\pi)$.
```

**参考原文与定位：**

[huang2026](D:/afdm-gfra/reference/literature/huang2026.pdf)，PDF 第 2 页，II。

> The resulting Doppler term D(ψ) is assumed to be common to all propagation paths within the same satellite-to-ground (S2G) link [15].

[shen2025](D:/afdm-gfra/reference/literature/shen2025.pdf)，PDF 第 4 页，II-B，(8)–(10)。

定位/释义：式(8)–(10)：OTFS相位φ_u,q[l′]=exp(j2π k_tilde_i,u q)，依赖路径对应delay位置；不是本文单设备统一β

**具体变化：** 以公共Doppler为条件从本文G提出标量；新设β_k的wrap定义。

**分类理由：** 公共Doppler假设可定位Huang；Shen有跨帧相位先例，但本文整句、H_k^(q)=exp(jqβ_k)H_k及wrap不是来源原句。

**技术判断：** 在公共ν_k、路径增益/延迟/阵列响应恒定及同一波形基的前提下成立。每个D_ν,gq=exp(j2πνqT_frame)D_ν,g0，标量可提出路径和。不同路径不同Doppler时一般不能提出一个公共标量。

**公式适配：** 对整数q，wrap不改变exp(jqβ)；ν单位为Hz，2πνT_frame无量纲。该等式在冻结物理参数模型中精确，在真实参数仅近似恒定时为同阶近似。

**处理建议：** 明确标为本文推导，引用Huang只支撑公共Doppler假设；不要声称Shen已经给出本AFDM公式。

### P08.S03 · 本稿定义、假设或推导

**当前稿完整句（含公式）：**

```tex
The phase rotation $e^{jq\beta_k}$ accounts for the variation of
$H_k^{(q)}$ across frames, so the $Q$ frames provide multiple
observations of $H_k$.
```

**参考原文与定位：**

[shen2025](D:/afdm-gfra/reference/literature/shen2025.pdf)，PDF 第 4–5 页，II-B，(9),(10)后。

定位/释义：式(9)后跨页段：有效OTFS张量约定下Q帧近似恒定而可汇集更多观测；p5讨论逐帧累积的分数Doppler相位

[huang2026](D:/afdm-gfra/reference/literature/huang2026.pdf)，PDF 第 3 页，III-A，(6)后。

定位/释义：式(6)后讨论多个pilot sequences及相邻序列间effective channel变化近似可忽略

**具体变化：** 把本文公共标量模型解释为同一H_k的多帧观测；不是来源关于OTFS张量或近似信道不变的原句。

**分类理由：** “更多观测”思想有来源，但本句前半精确解释本文H_k^(q)及其标量相位，后半是由此得出的结论；未定位可只术语替换的原句。

**技术判断：** 在前句假设内成立。Q帧提供同一参考张量的多组相位调制观测；并未由此保证相位已知、可辨识或足以唯一恢复全部系数。

**公式适配：** 可由上句直接代入每帧线性观测得到。Huang相邻序列变化可忽略的近似不能当作本文累积相位已被处理的证据。

**处理建议：** 保留为本稿推导解释，并在逐句来源统计中单列。

## P09

原文行号：162–212。

**来源顺序：** Cai II-A activity indicator/probability；本文块内假设与相位吸收定义；Cai received-signal sentence template + 本文AFDM双求和；Cai (4)/Shen (15)收集框架 + 本文MMV排列；Huang III-A full effective channel；本文Q<KN维度推论；Cai II-A activity-induced block sparsity

**跨来源组合：** 是

**条件变化：** Cai的同步OFDM对角子载波模型变为本文具n→r耦合的AFDM算子；MMV维度重排及共同相位吸收不能由原句直接继承。Huang的不依赖系数稀疏与Cai的活动块稀疏兼容，须分清对象。

**结构判断：** 技术上可在本文P07/P08/本稿附录app:afdm-model条件下成立，语言上不满足全段仅必要术语替换。

### P09.S01 · 有依据但经过自主改写

**当前稿完整句（含公式）：**

```tex
Let $\alpha_k$ denote the activity indicator of device $k$
\cite{cai2026}:
\[
 \alpha_k=\begin{cases}
 1,&\text{if the $k$th device is active},\\
 0,&\text{otherwise}.
 \end{cases}
\]
```

**参考原文与定位：**

[cai2026](D:/afdm-gfra/reference/literature/cai2026.pdf)，PDF p.4 / journal p.3578，II-A，(1)。

> We use an indicator function αk to model the device activity as

定位/释义：Left column, below Table I; cases: 1, if the k-th device is active; 0, otherwise.

[cai2026_stmp_v2](D:/afdm-gfra/reference/literature/cai2026_stmp_v2.pdf)，PDF p.4，II-A，(1)。

定位/释义：Same indicator sentence and cases (1) as the formal version.

**具体变化：** “We use an indicator function ... to model the device activity as”改为“Let ... denote the activity indicator of device k”.；二值分段公式保留，标点/排版作适配。

**分类理由：** 活动定义及 cases 可逐项定位，但引导句换了主谓结构；不是只替换术语。

**技术判断：** SUPPORTED: α_k∈{0,1}的定义与Cai一致。

**公式适配：** 分段公式与Cai (1)同义；本稿只延续同一活动变量，未加入新的随机假设。

**处理建议：** 若严格执行原句要求，可回到Cai的完整引导句并仅替换对象称呼；现稿应标支持性改写。

### P09.S02 · 有依据但经过自主改写

**当前稿完整句（含公式）：**

```tex
The activity probability is denoted by $\rho$, i.e.,
$\Pr(\alpha_k=1)=\rho$, with $\rho\ll1$.
```

**参考原文与定位：**

[cai2026](D:/afdm-gfra/reference/literature/cai2026.pdf)，PDF p.4 / journal p.3578，II-A，after (1)。

> Let λ represent the probability of a device being active, i.e., p(αk = 1) = λ, where λ ≪ 1.

**具体变化：** λ→ρ、p→Pr是符号替换。；“Let λ represent the probability of a device being active”改成被动语态“The activity probability is denoted by ρ”；where→with。

**分类理由：** 源内容完全对应，但非必要的句法与措辞重写超过术语替换。

**技术判断：** SUPPORTED: 共同活动概率与稀疏活动假设有明确来源。

**公式适配：** Pr(α_k=1)=ρ及ρ≪1与Cai的λ定义一致。

**处理建议：** 可按Cai原句保留句法、只把λ替换为ρ。

### P09.S03 · 本稿定义、假设或推导

**当前稿完整句（含公式）：**

```tex
Each device maintains
its activity state throughout a transmission block.
```

**参考原文与定位：**

[cai2026](D:/afdm-gfra/reference/literature/cai2026.pdf)，PDF p.4 / journal p.3578，II-A。

> As a result, only a (small) subset of the devices is active in any given transmission block.

定位/释义：Context plus one α_k with no t index in (1)–(4) supports block-constant activity implicitly, not this exact sentence.

**具体变化：** 将原文的块级活动建模显式表述为整块状态保持。

**分类理由：** 在核对的Cai正式版/v2、Shen和Huang全文中未定位到这一完整原句；它是本稿对α_k不带帧索引的显式建模假设。

**技术判断：** CONSISTENT_MODEL_ASSUMPTION: 块内活动不变与后续Q帧共用α_k自洽；不是由物理信道公式自动推出。

**公式适配：** 无显示公式；其作用是允许所有q使用同一α_k。

**处理建议：** 作为本文假设保留并明确身份；不能称为找到参考原句。

### P09.S04 · 本稿定义、假设或推导

**当前稿完整句（含公式）：**

```tex
We define
$X_k=\alpha_kH_k$ and incorporate the inter-frame phase rotation
into the pilot symbols as
\begin{equation}
 A_{qkn}=P_{qkn}e^{jq\beta_k}.
 \label{eq:effective-pilot}
\end{equation}
```

**参考原文与定位：**

[cai2026](D:/afdm-gfra/reference/literature/cai2026.pdf)，PDF p.4 / journal p.3578，II-A，between (3) and (4)。

> Let Xk ≜ αkHk.

[shen2025](D:/afdm-gfra/reference/literature/shen2025.pdf)，PDF p.5，II-C，(14)–(15)。

定位/释义：(14)–(15) place OTFS phase factors Φ_q in C^{φ,l}; this is conceptual precedent, not A_qkn=P_qkn exp(jqβ_k).

**具体变化：** X_k=α_kH_k沿用Cai定义。；“incorporate the inter-frame phase rotation into the pilot symbols”及A_qkn的具体定义为本稿增加。

**分类理由：** 前半句有明确公式来源，后半句将本稿P08的标量跨帧相位吸收入导频；已查资料没有该AFDM完整句与等式。

**技术判断：** VALID_UNDER_STATED_MODEL: 用H_k^(q)=exp(jqβ_k)H_k代入线性接收关系可得此定义。

**公式适配：** 本稿附录app:afdm-model eq: path-operator、末段及本章eq:twc-frame-channel给出所需共同相位；共同ν_k、块内路径参数不变是条件。Cai无跨帧相位项。

**处理建议：** 标为本文定义，并把跨帧相位的依据指向本稿已给推导；不可把Cai引用延伸成整个等式来自Cai。

### P09.S05 · 有依据但经过自主改写

**当前稿完整句（含公式）：**

```tex
After removing the CPP and applying the DAFT, the received signal
$\mathbf Y_q\in\mathbb C^{M\times N}$ during the $q$th AFDM
frame is given by \cite{cai2026}
\begin{equation}
 Y_{qmr}=[\mathbf Y_q]_{mr}
 =\sum_{k=1}^K\sum_{n=0}^{N-1}A_{qkn}X_{kmrn}+W_{qmr},
 \label{eq:observation-tensor}
\end{equation}
where $\mathbf W_q=[W_{qmr}]_{m,r}\in\mathbb C^{M\times N}$ is an
AWGN matrix with independent entries distributed as $\CN(0,\sigma^2)$.
```

**参考原文与定位：**

[cai2026](D:/afdm-gfra/reference/literature/cai2026.pdf)，PDF p.4 / journal p.3578，II-A，(3)。

> After removing the CP and applying the DFT, the received signal Yt ∈ C^{N×M} during the t-th OFDM symbol is given by

定位/释义：Right column; Y_t = sum_k α_k Q_kt H_k + N_t, with Q_kt diagonal.

[cai2026](D:/afdm-gfra/reference/literature/cai2026.pdf)，PDF p.4 / journal p.3578，II-A，where after (3)。

> where Nt ∈ C^{N×M} is an AWGN matrix with the elements i.i.d. drawn from CN(0, δ_0^2).

[huang2026](D:/afdm-gfra/reference/literature/huang2026.pdf)，PDF p.2 / journal p.2950，II, System Model，(4)–(5)。

定位/释义：AFDM effective input-output relation (4)–(5): an N×N effective channel matrix acts on an N-vector; supports non-diagonal symbol coupling.

**具体变化：** 主句CP→CPP、DFT→DAFT、t-th OFDM symbol→q-th AFDM frame及Y维度替换。；where新增W_q=[W_qmr]索引，并把“with the elements i.i.d. drawn from”改写为“with independent entries distributed as”。

**分类理由：** 接收句主干逐词对应Cai，只需对象/符号替换；但按协议将where连入完整句后出现额外措辞改写，故整句为SUPPORTED_PARAPHRASE。此分类不以公式不同为理由。

**技术判断：** VALID_UNDER_STATED_MODEL: 全矩阵信道乘导频并对设备求和成立；独立等方差AWGN通过酉DAFT保持CN(0,σ²)。

**公式适配：** Cai (3)使用对角Q_kt及H_k∈C^{N×M}，逐接收子载波只有同一n的乘积；本稿为Σ_kΣ_n A_qkn X_kmrn，保留n→r的N×N耦合并引入M维阵列。该双求和是本稿根据P07/P08/本稿附录app:afdm-model所作AFDM适配，不能直接声称Cai原式已含r,n两维。

**处理建议：** 语言上可逐词保留Cai的AWGN where句，仅必要替换对象符号；数学上明确eq:observation-tensor由本稿AFDM算子推出。

补充：{"main_clause": "TERM_ONLY", "where_clause": "SUPPORTED_PARAPHRASE", "formula_source": "AUTHOR_DEFINED_OR_DERIVED adaptation, not a direct Cai equation"}

### P09.S06 · 有依据但经过自主改写

**当前稿完整句（含公式）：**

```tex
Collecting the $Q$ received frames yields the matrix model
\begin{equation}
 \mathbf Y=\mathbf A\mathbf X+\mathbf W,
 \label{eq:mmv}
\end{equation}
where $\mathbf Y,\mathbf W\in\mathbb C^{Q\times MN}$,
$\mathbf A\in\mathbb C^{Q\times KN}$, and
$\mathbf X\in\mathbb C^{KN\times MN}$.
```

**参考原文与定位：**

[cai2026](D:/afdm-gfra/reference/literature/cai2026.pdf)，PDF p.4 / journal p.3578，II-A，(4)。

> We express the received signal Y over the T OFDM symbols in a more compact form as

定位/释义：Y: NT×M; Q: NT×NK; X: NK×M. Stacks received subcarriers and time vertically.

[shen2025](D:/afdm-gfra/reference/literature/shen2025.pdf)，PDF p.5，II-C，(15)。

> Next, we collect the Q received frames into a single matrix as

定位/释义：Collects OTFS observations Y_q^l over frames; this is not the present AFDM indexing.

**具体变化：** “We express ... in a more compact form as”或“Next, we collect ... into a single matrix as”重新写为“Collecting ... yields the matrix model”。；where的矩阵组织和全部维度改为本稿索引。

**分类理由：** 收集多帧得到矩阵式有Cai/Shen依据，但整句未直接采用任一原句，且显示式的具体堆叠为本稿定义。

**技术判断：** VALID_ALGEBRA: 按下一句四项索引逐元素检查，AX的(q,mN+r)元恰为双求和。

**公式适配：** Cai为NT×M观测、NT×NK测量矩阵、NK×M未知量；本稿为Q×MN、Q×KN、KN×MN。接收符号r移入列索引，发射符号n进入行块；这不是把T改名Q即可完成。Shen (15)也不是该排列。

**处理建议：** 可借用Cai或Shen的完整收集句作为语言适配，同时将维度重排明确列为本稿数学定义。

### P09.S07 · 本稿定义、假设或推导

**当前稿完整句（含公式）：**

```tex
The corresponding entries are defined by
\begin{equation}
 \begin{aligned}
 [\mathbf Y]_{q,mN+r}&=Y_{qmr},\\
 [\mathbf W]_{q,mN+r}&=W_{qmr},\\
 [\mathbf A]_{q,(k-1)N+n}&=A_{qkn},\\
 [\mathbf X]_{(k-1)N+n,mN+r}&=X_{kmrn}.
 \end{aligned}
 \label{eq:mmv-indexing}
\end{equation}
```

**参考原文与定位：**

本句为本稿内部定义/指引，未认定为参考论文原句。

**具体变化：** 新增四个张量至矩阵的元素索引定义。

**分类理由：** 在本轮Cai正式版/v2、Shen及Huang中没有这些索引式或对应原句；它们专属于本文n→r信道张量。

**技术判断：** VALID_ALGEBRA: m=0..M−1、r,n=0..N−1、k=1..K时索引范围分别为MN列与KN行，覆盖无冲突。

**公式适配：** 四项映射保持eq:observation-tensor与eq:mmv逐元素等价；这里的X_k是张量块，矩阵中的设备行块有N行、MN列。

**处理建议：** 按本文定义保留；不能伪装成参考论文原句。

### P09.S08 · 有依据但经过自主改写

**当前稿完整句（含公式）：**

```tex
We estimate the full AFDM effective channel tensor $H_k$
without imposing sparsity assumptions on its coefficients
\cite{huang2026}.
```

**参考原文与定位：**

[huang2026](D:/afdm-gfra/reference/literature/huang2026.pdf)，PDF p.3 / journal p.2951，III-A，after (6)。

> Since we directly estimate the full AFDM effective channel matrix Heff without imposing sparsity assumptions, using only one pilot sequence makes (6) underdetermined, so that multiple pilot sequences are required.

**具体变化：** 从Huang的“Since we directly estimate ... without imposing sparsity assumptions”子句抽出主句。；matrix H_eff→tensor H_k是必要对象替换；删除directly并增写on its coefficients；未保留原句后半部单导频欠定的因果链。

**分类理由：** 目标与Huang直接对应，但当前写法是删减和扩写后的独立句，不是纯术语替换；新增“on its coefficients”不是原句片段。

**技术判断：** SUPPORTED: 不对每个H_k系数施加稀疏先验与后文活动诱导块稀疏不矛盾。

**公式适配：** Huang为单链路N×N有效矩阵；本稿扩展为M×N×N张量，未由该句得到设备活动模型。

**处理建议：** 如要求原句组合，可保留Huang被抽取子句的措辞，只作独立成句所需语法调整，并另外声明张量扩展。

### P09.S09 · 本稿定义、假设或推导

**当前稿完整句（含公式）：**

```tex
Since $Q<KN$, \eqref{eq:mmv} is underdetermined.
```

**参考原文与定位：**

[huang2026](D:/afdm-gfra/reference/literature/huang2026.pdf)，PDF p.3 / journal p.2951，III-A，after (6)。

> Since we directly estimate the full AFDM effective channel matrix Heff without imposing sparsity assumptions, using only one pilot sequence makes (6) underdetermined, so that multiple pilot sequences are required.

[cai2026](D:/afdm-gfra/reference/literature/cai2026.pdf)，PDF p.4 / journal p.3578，II-A，(4)。

定位/释义：(4) is an underdetermined JADCE linear recovery setting when the chosen pilot dimension is smaller than the unknown dimension; does not contain Q<KN.

**具体变化：** 把本稿Q×KN矩阵的尺寸不等式直接写成欠定结论。

**分类理由：** Huang只讨论单导频使其(6)欠定；Cai采用不同矩阵行数。Q<KN及本稿eq:mmv的具体结论是本文维度判断，不是可替换符号获得的原句。

**技术判断：** VALID_LINEAR_ALGEBRA: 若Q<KN，A的列秩不可能达到KN，每列观测的无约束线性逆问题欠定。

**公式适配：** 此句仅断言原始线性系统欠定；不声称有先验约束后的统计识别必然失败。

**处理建议：** 按本稿条件和直接推论保留；不要用Huang的单导频原句冒充这个具体不等式。

### P09.S10 · 有依据但经过自主改写

**当前稿完整句（含公式）：**

```tex
Sporadic device activity gives $\mathbf X$ a block-sparsity structure:
if device $k$ is inactive, then $X_k=\alpha_kH_k=\mathbf 0$
\cite{cai2026}.
```

**参考原文与定位：**

[cai2026](D:/afdm-gfra/reference/literature/cai2026.pdf)，PDF p.4 / journal p.3578，II-A，after (4)。

> Due to the sporadic access of the devices, matrix X exhibits a block-sparsity structure. Specifically, if the k-th device is inactive, we have Xk = αkHk = 0.

**具体变化：** 将“Due to ... matrix X exhibits ...”改写成“Sporadic device activity gives X ...”。；原文两句合为冒号句，Specifically与we have改为if/then结构。

**分类理由：** 两项命题均精确可定位；但首句主谓重写不是仅连接原句所需语法调整，因此整句为支持性改写。

**技术判断：** SUPPORTED: α_k=0推出整个设备块为零，不依赖H_k本身的系数稀疏性。

**公式适配：** 零块关系直接沿用Cai；本文设备块从N×M扩展到M×N×N（矩阵重排为N×MN），块稀疏含义保持。

**处理建议：** 可直接保留Cai两句措辞并只换必要符号；当前不要标原句组合。

## P10

原文行号：214–216。

**来源顺序：** Cai II-B first sentence

**跨来源组合：** 否

**条件变化：** 目标同型，Y换为本稿AFDM观测。

**结构判断：** 语义对应但全句多处自主同义改写。

### P10.S01 · 有依据但经过自主改写

**当前稿完整句（含公式）：**

```tex
Our objective is to jointly detect the active devices and estimate
their channels from $\mathbf Y$ within a Bayesian inference framework
\cite{cai2026}.
```

**参考原文与定位：**

[cai2026](D:/afdm-gfra/reference/literature/cai2026.pdf)，PDF p.4 / journal p.3578，II-B。

> In this paper, we aim to simultaneously detect the active devices and estimate the corresponding channels based on the observation Y under a Bayesian inference framework.

**具体变化：** In this paper, we aim to→Our objective is to；simultaneously→jointly；corresponding channels→their channels；based on the observation→from；under→within。

**分类理由：** 任务与Bayesian框架完全对应，但多处英文同义改写不属于必要术语替换。

**技术判断：** SUPPORTED: JADCE目标与Cai一致，本文的Y是另行定义的观测。

**公式适配：** 无显示公式；Y的AFDM含义需依照本文而非沿用Cai的OFDM矩阵尺寸。

**处理建议：** 若要求原句，可直接沿用Cai II-B首句，仅替换必要技术对象。

## P11

原文行号：218–225。

**来源顺序：** 本文前端估计条件化；本文内部章节指引；Cai/Huang learned distribution概念 + 本文q_tr定义；Cai Eq. (5)独立因子结构 + 本文显式假设；Cai Table II Bernoulli及I-A non-separable channel correlations + 本文联合先验

**跨来源组合：** 是

**条件变化：** 已知测量矩阵/噪声参数改为由同一Y得到的固定估计值；真实p(H_k)与训练q_tr明确区分。独立性是本文假设，不是物理模型必然结论。

**结构判断：** 整个段落主要是本文推断问题的补充定义，不能作为原文替换段落计入。

### P11.S01 · 本稿定义、假设或推导

**当前稿完整句（含公式）：**

```tex
To formulate the inference problem, we treat $\widehat{\mathbf A}$
and $\widehat\sigma^2$ as given.
```

**参考原文与定位：**

[cai2026](D:/afdm-gfra/reference/literature/cai2026.pdf)，PDF p.5 / journal p.3579，II-B, Table II。

定位/释义：Table II rows: p(y_m|x_m)=CN(Qx_m,δ_0²I_NT); p(X_k|H_k,α_k)=δ(X_k−α_kH_k); p(H_k) unspecified; p(α_k)=(1−λ)δ(α_k)+λδ(1−α_k).

**具体变化：** 新增将估计A与σ²视为给定量的条件化/代入约定。

**分类理由：** Cai Table II使用已知Q及δ_0²，没有本文的A_hat(Y)、σ_hat²(Y)前端估计约定；该句是本稿定义工作推断问题。

**技术判断：** VALID_AS_WORKING_MODEL: 给定估计后可构造Gaussian工作似然；不等于边缘化前端参数不确定性的完整物理后验。

**公式适配：** 后验的“given”参数应理解为固定plug-in值，即使它们由同一Y计算；不能据此宣称估计误差已计入。

**处理建议：** 保留为本文建模约定，不归入Cai原句适配。

### P11.S02 · 本稿定义、假设或推导

**当前稿完整句（含公式）：**

```tex
These estimates are obtained from
$\mathbf Y$ as described in Section~\ref{sec:frontend}.
```

**参考原文与定位：**

本句为本稿内部定义/指引，未认定为参考论文原句。

**具体变化：** 本文前端章节内部指引。

**分类理由：** sec:frontend是当前稿件内标签，参考论文没有该章节关系。已只读定位到05_overall_algorithm.tex的sec:frontend以及appendix_parameter_estimation.tex末段。

**技术判断：** INTERNAL_REFERENCE_CONFIRMED: 当前稿sec:frontend确有A_hat及噪声估计说明，附录参数估计给出对应公式。

**公式适配：** 无公式；这里只核内部存在性，不在本次扩大为算法精度或实验有效性评价。

**处理建议：** 按内部章节指引保留，不要求为其捏造外部原句。

### P11.S03 · 本稿定义、假设或推导

**当前稿完整句（含公式）：**

```tex
Let $q_{\rm tr}$ denote the prior distribution of $H_k$ represented
by the training channel samples.
```

**参考原文与定位：**

[cai2026](D:/afdm-gfra/reference/literature/cai2026.pdf)，PDF p.2 / journal p.3576，I, paragraph 2。

> In light of the limitations of model-based approaches in accurately capturing the real wireless propagation environments, deep learning offers a powerful alternative by learning the channel distribution directly from data.

[huang2026](D:/afdm-gfra/reference/literature/huang2026.pdf)，PDF p.3 / journal p.2951，III-B, where after (9)。

> which encourages the estimate to conform to the channel distribution learned during training and can be approximated by the trained network sθ.

定位/释义：Quoted clause modifies the prior score ∇log p(H_eff^(i)); no q_tr notation or plug-in likelihood.

**具体变化：** 引入q_tr作为训练样本代表的H_k先验分布。

**分类理由：** Cai与Huang说明从训练数据学习信道分布，但未给出这个q_tr定义或这句英文；本稿用它明确训练分布与真实分布的区别。

**技术判断：** VALID_AS_DEFINED: 可把q_tr视作训练样本所代表的分布；有限样本或分数网络本身不能自动证明它等于真实信道先验。

**公式适配：** 这是新的概率分布符号及解释，不是把Cai p(H_k)机械改名；工作后验明确使用其作为先验。

**处理建议：** 明确保留为本文定义，可给学习先验的文献依据，但不能判TERM_ONLY。

### P11.S04 · 本稿定义、假设或推导

**当前稿完整句（含公式）：**

```tex
We assume independence across
devices and between each device's activity and channel.
```

**参考原文与定位：**

[cai2026](D:/afdm-gfra/reference/literature/cai2026.pdf)，PDF pp.3–4 / journal pp.3577–3578，II-A。

> Moreover, we assume that the IoT devices are synchronized, and each device determines whether to access the channel in an independent and identically distributed (i.i.d.) manner.

[cai2026](D:/afdm-gfra/reference/literature/cai2026.pdf)，PDF p.4 / journal p.3578，II-B，(5)。

> In message passing, we factorize the joint posterior distribution according to Baye’s theorem and the conditional independence relationships among the variables, expressed as

定位/释义：p(X,{H_k},{α_k}|Y) ∝ product_m p(y_m|x_m) product_k p(X_k|H_k,α_k)p(H_k)p(α_k).

**具体变化：** 将跨设备信道/活动独立及设备内活动—信道独立显式写成一条本稿假设。

**分类理由：** Cai明确原句仅给出设备接入i.i.d.；Cai (5)的先验乘积支持更完整的独立结构，但没有定位到当前这句英文。不能把跨设备活动i.i.d.原句扩大成整个H_k与α_k独立原句。

**技术判断：** CONSISTENT_MODEL_ASSUMPTION: 独立先验允许后文按k相乘；独立性是建模选择，不由AFDM物理模型本身保证。

**公式适配：** product_k q_tr(H_k)p(α_k)需跨设备对(H_k,α_k)相互独立且每对内部独立；Cai (5)同型，未限定同一AFDM信道分布。

**处理建议：** 按本文假设保留并可引用Cai因子分解；不能标外文原句只换术语。

### P11.S05 · 本稿定义、假设或推导

**当前稿完整句（含公式）：**

```tex
The
activities follow Bernoulli priors, while $q_{\rm tr}(H_k)$ retains
the dependence among the coefficients within $H_k$.
```

**参考原文与定位：**

[cai2026](D:/afdm-gfra/reference/literature/cai2026.pdf)，PDF p.5 / journal p.3579，II-B, Table II。

定位/释义：Table II rows: p(y_m|x_m)=CN(Qx_m,δ_0²I_NT); p(X_k|H_k,α_k)=δ(X_k−α_kH_k); p(H_k) unspecified; p(α_k)=(1−λ)δ(α_k)+λδ(1−α_k).

[cai2026](D:/afdm-gfra/reference/literature/cai2026.pdf)，PDF p.2 / journal p.3576，I-A。

> Moreover, unlike the separable denoisers in [5], [6], [11], and [27] that operate element-wise for channel denoising, our TMP framework models the spatial-frequency channel matrix as a super node in the factor graph, enabling the incorporation of score-based generative models as non-separable denoisers for more effective exploitation of channel correlations.

**具体变化：** 合并Bernoulli活动先验与保持设备内H_k联合依赖两项设定。；q_tr及其在本文张量系数上的作用为本稿限定。

**分类理由：** Bernoulli形式可由Cai Table II逐项核对；非可分信道去噪及利用相关性的原句在Cai I-A。当前“q_tr retains dependence”并非其中任何原句，也不只是把两条原句连接；它是在声明本稿联合先验的结构。

**技术判断：** CONSISTENT_MODEL_ASSUMPTION: 不把q_tr(H_k)拆成系数乘积可保留其已有相关性；“retains”不应被解释为已证明有限网络精确恢复所有相关性。

**公式适配：** Bernoulli仅作用于α_k；q_tr作用于整个设备信道张量，不额外假设其系数独立。

**处理建议：** 标为本稿结构假设，并分别指向Cai Table II与I-A作为方法依据。

## P12

原文行号：227–255。

**来源顺序：** Cai (5) factorization and where template；本文working q及plug-in Gaussian likelihood；Cai Table II delta/Bernoulli数学形式的解释性改写；本文q下目标定义，参考Cai MMSE/活动概率概念

**跨来源组合：** 否

**条件变化：** 公式骨架保持，但观测列数、训练先验、给定估计参数及目标条件集改变；Cai的消息置信度不等同精确全局后验。

**结构判断：** where局部保持原句结构；整段为本文工作后验建模及标准目标定义，须与直接原句来源分栏。

### P12.S01 · 本稿定义、假设或推导

**当前稿完整句（含公式）：**

```tex
Under these assumptions, the joint posterior factorizes as
\begin{equation}
 \begin{aligned}
 &q(\mathbf X,\{H_k\}_{k=1}^{K},\{\alpha_k\}_{k=1}^{K}\mid\mathbf Y)\\
 &\quad\propto\prod_{j=1}^{MN}p(\mathbf y_j\mid\mathbf x_j)\\
 &\qquad\times\prod_{k=1}^{K}
 p(X_k\mid H_k,\alpha_k)q_{\rm tr}(H_k)p(\alpha_k),
 \end{aligned}
 \label{eq:working-posterior}
\end{equation}
where $\mathbf x_j\in\mathbb C^{KN}$ and
$\mathbf y_j\in\mathbb C^Q$ denote the $j$-th column of
$\mathbf X=[\mathbf x_1,\ldots,\mathbf x_{MN}]$ and
$\mathbf Y=[\mathbf y_1,\ldots,\mathbf y_{MN}]$, respectively.
```

**参考原文与定位：**

[cai2026](D:/afdm-gfra/reference/literature/cai2026.pdf)，PDF p.4 / journal p.3578，II-B，(5)。

> In message passing, we factorize the joint posterior distribution according to Baye’s theorem and the conditional independence relationships among the variables, expressed as

定位/释义：p(X,{H_k},{α_k}|Y) ∝ product_m p(y_m|x_m) product_k p(X_k|H_k,α_k)p(H_k)p(α_k).

[cai2026](D:/afdm-gfra/reference/literature/cai2026.pdf)，PDF p.5 / journal p.3579，II-B，where after (5)。

> where xm ∈ C^{NK} and ym ∈ C^{NT} denote the m-th column of X = [x1, ..., xM] and Y = [y1, ..., yM], respectively.

[cai2026_stmp_v2](D:/afdm-gfra/reference/literature/cai2026_stmp_v2.pdf)，PDF pp.4–5，II-B，(5)。

定位/释义：Eq. (5) and its following where sentence agree with the formal version.

**具体变化：** 因子分解引导语由Cai的主动句及Bayes/条件独立说明压缩成Under these assumptions。；where句保持Cai句法，m→j、M→MN、NT→Q。；p(H_k)改为本文训练先验q_tr，后验p改为q，似然采用下一句给定估计值。

**分类理由：** 因子图骨架源于Cai (5)，where局部可按必要符号尺寸替换定位；但完整语句引入本文训练先验与工作后验，属于在本稿假设下建立的概率模型。不是仅因显示公式变动而否定原句对齐：引导语也有自主改写，q的概率含义由本文新定义。

**技术判断：** VALID_AS_WORKING_POSTERIOR: 独立AWGN、给定A_hat/σ_hat²、跨设备独立和X_k=α_kH_k足以得到此比例关系。观测列间似然因子化不要求H_k的列在先验中独立。

**公式适配：** Cai product_m至M →本稿product_j至MN来自不同的观测矩阵列数；X_k仍是同一变量集合的设备块重排。用训练先验和由Y得到的固定参数后，q是规范化后的工作分布；没有对β/σ²的估计不确定性积分，不能等同于真实生成模型的完整后验。

**处理建议：** 把“参考因子分解模板”与“本文定义的q”分开标注；where可保留原句适配，其余应承认为本文建模。

补充：{"leading_clause": "SUPPORTED_PARAPHRASE of Cai II-B", "where_clause": "TERM_ONLY", "probability_model": "AUTHOR_DEFINED_OR_DERIVED"}

### P12.S02 · 本稿定义、假设或推导

**当前稿完整句（含公式）：**

```tex
Here, $q$ denotes the working posterior, and
$p(\mathbf y_j\mid\mathbf x_j)=\CN(\mathbf y_j;
\widehat{\mathbf A}\mathbf x_j,\widehat\sigma^2\I_Q)$ is the
Gaussian likelihood associated with \eqref{eq:mmv}.
```

**参考原文与定位：**

[cai2026](D:/afdm-gfra/reference/literature/cai2026.pdf)，PDF p.5 / journal p.3579，II-B, Table II。

定位/释义：Table II rows: p(y_m|x_m)=CN(Qx_m,δ_0²I_NT); p(X_k|H_k,α_k)=δ(X_k−α_kH_k); p(H_k) unspecified; p(α_k)=(1−λ)δ(α_k)+λδ(1−α_k).

**具体变化：** 定义working posterior名称与q；把Cai已知Q、δ_0²的Gaussian因子改为估计A_hat、σ_hat²并设Q维。

**分类理由：** 在所核Cai正式版/v2、Shen、Huang全文中没有当前“q denotes the working posterior”原句。Gaussian似然有Cai Table II作为数学模板，但本句用于本稿plug-in模型的定义。

**技术判断：** VALID_AS_WORKING_LIKELIHOOD: 假定σ_hat²>0，CN(y_j;A_hat x_j,σ_hat²I_Q)是正常的Gaussian工作因子。

**公式适配：** 它忽略A_hat与σ_hat²估计误差，仅作为已固定参数的似然；此点与P11“as given”一致。名称working posterior在本轮语料未定位，不能归给Cai。

**处理建议：** 按本文概率分布定义保留；working posterior在本轮语料未找到对应原词，按项目术语规则须补可定位出处，或用已定义的q及公式直接描述，不将其包装成Cai现成术语。

### P12.S03 · 有依据但经过自主改写

**当前稿完整句（含公式）：**

```tex
The factor
$p(X_k\mid H_k,\alpha_k)$ enforces $X_k=\alpha_kH_k$, and
$p(\alpha_k)=\rho^{\alpha_k}(1-\rho)^{1-\alpha_k}$.
```

**参考原文与定位：**

[cai2026](D:/afdm-gfra/reference/literature/cai2026.pdf)，PDF p.5 / journal p.3579，II-B, Table II。

定位/释义：Table II rows: p(y_m|x_m)=CN(Qx_m,δ_0²I_NT); p(X_k|H_k,α_k)=δ(X_k−α_kH_k); p(H_k) unspecified; p(α_k)=(1−λ)δ(α_k)+λδ(1−α_k).

[cai2026](D:/afdm-gfra/reference/literature/cai2026.pdf)，PDF p.4 / journal p.3578，II-A，after (1)。

> Let λ represent the probability of a device being active, i.e., p(αk = 1) = λ, where λ ≪ 1.

**具体变化：** 把Table II的δ约束解释成“enforces”；把二原子分布改写为α_k∈{0,1}上的Bernoulli质量函数。

**分类理由：** 两项数学含义都能直接从Cai Table II核对，但源文本是表格公式而非当前英文完整句；从公式转写解释句不能称原句组合。

**技术判断：** VALID_EQUIVALENT_REPRESENTATION: deterministic factor及Bernoulli PMF与Cai模型同义；α_k支持集已在P09声明。

**公式适配：** p(X_k|H_k,α_k)=δ(X_k−α_kH_k)支持“enforces”；ρ^{α_k}(1−ρ)^{1−α_k}与Cai双Dirac表示在二值支持集上等价，但公式表现形式为本稿改写。

**处理建议：** 引用Cai Table II支持含义，承认这是对表格公式的解释性改写。

### P12.S04 · 本稿定义、假设或推导

**当前稿完整句（含公式）：**

```tex
Under this posterior, the MMSE channel estimate and posterior
activity probability are
\begin{equation}
 \begin{aligned}
 X_k^{\rm MMSE}&=\E_q[X_k\mid\mathbf Y],\\
 p_k^{\rm Bayes}&=q(\alpha_k=1\mid\mathbf Y).
 \end{aligned}
 \label{eq:targets}
\end{equation}
```

**参考原文与定位：**

[cai2026](D:/afdm-gfra/reference/literature/cai2026.pdf)，PDF p.7 / journal p.3581，III-B.1，(22)。

定位/释义：Eq. (22) defines an MMSE denoising expectation E[H_k|H_k^pri], conditioned on a pseudo-observation, not the complete q posterior conditioned on Y.

[cai2026](D:/afdm-gfra/reference/literature/cai2026.pdf)，PDF p.7 / journal p.3581，III-B.2，following (30)。

> is the posterior probability of activity for the k-th device.

定位/释义：Refers to λ_k^post from a message belief; not an exact q(α_k=1|Y) equality.

**具体变化：** 为当前q定义X_k的后验均值和α_k边缘概率，命名X_k^MMSE与p_k^Bayes。

**分类理由：** MMSE=后验均值及活动后验概率有明确标准含义；Cai给出的是伪观测下的去噪均值与消息置信度更新。当前这组针对q、Y的目标符号及完整英文句是本文定义，不能把Cai (22)/(30)当成完全相同原式。

**技术判断：** VALID_TARGET_DEFINITION: 平方误差下E_q[X_k|Y]为该工作分布的MMSE估计；q(α_k=1|Y)为相应边缘概率。

**公式适配：** 估计目标是X_k=α_kH_k，即活动加权有效信道，而非所有设备的H_k本身。消息传递后续近似这些目标，不因命名Bayes就获得真实物理模型的最优性保证。

**处理建议：** 保留为本文目标定义；“channel estimate”应按X_k的活动加权含义理解，不夸称Cai完全相同公式。

## P13

原文行号：257–260。

**来源顺序：** Cai II-B approximate MMSE；Cai II-B deep generative priors；Cai II-B eliminating high-dimensional integrals

**跨来源组合：** 否

**条件变化：** 新增对本文两个q目标的回指；不能从引用推得本文算法的精确性或性能。

**结构判断：** 支持性摘要，非仅必要语法连接的原句组合。

### P13.S01 · 有依据但经过自主改写

**当前稿完整句（含公式）：**

```tex
We approximate these quantities by message passing with learned
generative priors, avoiding direct integration over the
high-dimensional posterior \cite{cai2026}.
```

**参考原文与定位：**

[cai2026](D:/afdm-gfra/reference/literature/cai2026.pdf)，PDF p.4 / journal p.3578，II-B。

> Alternatively, message-passing algorithms [5], [6], [27], [47] provide a low-complexity iterative approach for approximately calculating the MMSE estimator.

[cai2026](D:/afdm-gfra/reference/literature/cai2026.pdf)，PDF p.5 / journal p.3579，II-B, concluding paragraph。

> This paper seeks to address the aforementioned challenges by plugging in deep generative priors for efficient message calculation.

[cai2026](D:/afdm-gfra/reference/literature/cai2026.pdf)，PDF p.5 / journal p.3579，II-B, continuation above III。

> This insight enables the integration of score-based generative networks for provable MMSE denoising, eliminating the need to compute high-dimensional integrals.

[cai2026](D:/afdm-gfra/reference/literature/cai2026.pdf)，PDF p.4 / journal p.3578，II-B。

> Exact Bayesian estimators, e.g., the MMSE estimator, are generally intractable due to the high-dimensional integrals in the marginalization of the joint posterior distribution p(X,{Hk}_{k=1}^K,{αk}_{k=1}^K|Y).

**具体变化：** 把Cai II-B中近似MMSE、deep generative priors、高维积分三个论述压成一条概括。；these quantities回指本文P12新定义的两个目标，原文没有此回指；“avoiding direct integration over the high-dimensional posterior”是自行概括。

**分类理由：** 内容有多条明确原句支持，但当前不是这些原句/分句只经必要连接后的组合，而是用新的主谓结构和回指做摘要式改写。

**技术判断：** SUPPORTED_APPROXIMATION_CLAIM: Cai说明以生成先验和消息传递近似求解、避免显式高维积分；本句没有声称完全精确。实际算法仍须由后文给出，本次不核实性能。

**公式适配：** 无显示式；对“these quantities”的适配只能指本稿q下目标，而非自动继承Cai的所有近似性质。

**处理建议：** 如果严格需要可定位原句组合，应分别沿用Cai近似MMSE句与生成先验消除积分句；当前标为支持性概括。

## 完整性检查

每段全部句子依序拼接并仅忽略空白，与原段落逐字一致；句号、公式和从句没有遗漏或重复。当前正文 SHA-256 与开始核查时一致，7 个原始 PDF 的 SHA-256 均与来源清单一致。覆盖通过不代表来源分类全部通过。

分组原始报告：[P01–P03](a_audit.md)、[P04–P08](b_audit.md)、[P09–P13](c_audit.md)。
