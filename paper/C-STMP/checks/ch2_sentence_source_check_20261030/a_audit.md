# P01–P03 逐句来源核查

12 句已完整覆盖：2 句可认定合理原句组合，6 句为有来源的改写，4 句为本稿定义/推导或显式假设。未发现需归 SOURCE_GAP 的无条件实质主张；这不代表 12 句均满足原句适配要求。

核查口径：每句包含其显示公式和从属 where；独立 Here 句单列。引文是从本轮原始 PDF 页面与 clean.pages 文本核对的原句，已合并 PDF 断词和排版空白。Li 不直引英文，仅提供定位和中文释义。未改正文、PDF、参考文献或模型。

| 类别 | 句数 |
|---|---:|
| REASONABLE_COMBINATION | 2 |
| SUPPORTED_PARAPHRASE | 6 |
| AUTHOR_DEFINED_OR_DERIVED | 4 |

全部 12 个连续片段按段拼接，与相应 Pxx.input.txt 规范化换行后逐字一致；覆盖通过不等于来源适配通过。

## P01

**段落顺序：** Ding §II 起首句 + Shen §II 阵列尺寸 → Shen §II 同段共享资源句 → Shen §II 同段无 GNSS 句

**结构判断：** 从 Ding 的系统配置进入 Shen 的共享资源与无预补偿设定，顺序连贯；把信号限制为导频和把时间间隔叫作 block 是本稿范围设定。阵列维数来自另一个来源，单引 Ding 不能覆盖此细节。

**段落结论：** 1 句合理组合，2 句支持性改写；不能称整段仅替换术语。

### P01-S01 — REASONABLE_COMBINATION

**当前稿完整句：**

```tex
We consider an AFDM-GFRA system in which a LEO satellite equipped
with $M=M_yM_z$ antennas serves $K$ single-antenna devices
\cite{ding2026}.
```

**原文定位：**

- ding2026，PDF 第 2 页，II. AFDM-GF-RA System。

> We consider an AFDM-GF-RA system, where a LEO satellite equipped with M antennas serves K single-antenna devices.

  定位/释义：左栏 §II 第一完整句。
- shen2025，PDF 第 3 页，II. System Model。

> The system comprises U single-antenna terrestrial devices that communicate with a LEO satellite equipped with a uniform planar array (UPA) consisting of N_a = N_z × N_y antennas and a regenerative payload for on-board baseband signal processing.

  定位/释义：右栏 Fig.1 后第一段第二句。
  对照限制：英文逐字核对；N_a=N_z×N_y 是原 PDF 数学记号的文本转写。

**具体改动：** 保留 Ding 起首句主干；AFDM-GF-RA→AFDM-GFRA 是缩写拼写调整。；把 M 展开为 M_y M_z，阵列尺寸依据是 Shen 的 N_a=N_z×N_y。；where 改为 in which 属连接语法调整，其余主体关系不变。

**分类理由：** 能定位 Ding 的完整主句及 Shen 的阵列维数子句；没有新增服务关系或收发天线配置。按协议接受为有定位的原句组合，而非仅凭系统主题相似。

**技术状态：** SUPPORTED：系统配置和二维阵列维数均有直接依据；当前句只引 Ding，阵列维数最好同时指向 Shen。

**公式适配：** M=N_yN_z 的变量改名与乘法因子顺序交换；无数学内容变化。

**处理建议：** 可保留；若目标是每个新增细节都可追溯，应在此处补 Shen 对阵列维数的来源。

### P01-S02 — SUPPORTED_PARAPHRASE

**当前稿完整句：**

```tex
In each transmission block, active devices
transmit their pilots over the same time-frequency resources.
```

**原文定位：**

- shen2025，PDF 第 3 页，II. System Model。

> During each time interval, active devices share the same time-frequency resources to transmit their signals to the satellite.

  定位/释义：右栏 Fig.1 后第一段第三句。

**具体改动：** During each time interval→In each transmission block。；share resources to transmit signals 改写为 transmit pilots over resources，变更句子谓语组织。；signals→pilots 是本稿导频对象限定；删除 to the satellite。

**分类理由：** 内容与 Shen 原句一致且导频是信号的具体用途，但完整英文句经过重组，不只是必要术语替换，也不是拼接保留的原句分句。

**技术状态：** SUPPORTED：同时复用时频资源有原文直接支持；导频用途由本稿建模明确。

**公式适配：** 无公式。transmission block 是本稿时间分组，不能单凭此句获得多帧准静态条件。

**处理建议：** 若严格执行原句适配标准，应采用 Shen 的原句结构，只替换 time interval 为本稿 block、signals 为 pilots。

### P01-S03 — SUPPORTED_PARAPHRASE

**当前稿完整句：**

```tex
To reduce energy consumption, we assume that the devices operate
without GNSS capabilities and do not pre-compensate for delay and Doppler shifts
\cite{shen2025}.
```

**原文定位：**

- shen2025，PDF 第 3 页，II. System Model。

> Additionally, to minimize energy consumption, we assume that these terrestrial devices operate without GNSS capabilities and do not pre-compensate for delay and Doppler shifts.

  定位/释义：右栏 Fig.1 后第一段第四句。

**具体改动：** 删去 Additionally。；to minimize→To reduce、these terrestrial devices→the devices，属于普通措辞精简而不是技术术语替换。；without GNSS capabilities and do not pre-compensate for delay and Doppler shifts 保留了完整实质分句。

**分类理由：** 无 GNSS、无终端延迟与 Doppler 预补偿及节能动机均有明确原句；但普通词语已自行改写，按严格类别不能标 TERM_ONLY。

**技术状态：** SUPPORTED：假设与 Shen 相同，含义没有变强。

**公式适配：** 无公式。

**处理建议：** 若必须满足仅术语替换，可恢复 Shen 原句的动机和指代用语；现句可作为有来源的改写保留，但不能宣称逐字适配。

## P02

**段落顺序：** Shen §II-A 双扩展因果 → Huang §II 静止参考 + 共同 Doppler → 本稿向量/时间定义，Li/Shen 阵列背景 → Li 时变 CIR + Shen 差分延迟/阵列 + Huang 共同 Doppler的适配 → Shen §II-A 差分延迟定义 → Shen §II-A 共同延迟定义

**结构判断：** 该段把不同论文的模型条件组装成新系统模型。共同 Doppler 与共同阵列均有明确来源；从逐路径 Doppler 到共同 Doppler、从绝对时延到差分时延、以及本稿时间参考是实质模型适配，不是简单术语替换。所有条件应在公式附近透明说明。

**段落结论：** 1 句合理组合，3 句支持性改写，2 句本稿定义/推导；来源支持概念不等于整段原句改名。

### P02-S01 — SUPPORTED_PARAPHRASE

**当前稿完整句：**

```tex
The high mobility of the LEO satellite and multipath propagation
give rise to doubly dispersive terrestrial-satellite links (TSLs)
\cite{shen2025}.
```

**原文定位：**

- shen2025，PDF 第 3 页，II-A. Terrestrial-satellite Link Model。

> The TSLs will experience fast variations due to the high mobility of the LEO satellite. Hence, this time variation and multipath propagation require a doubly dispersive channel model for accurate TSLs characterization.

  定位/释义：§II-A 起首两句。

**具体改动：** 把“高速→时变”和“时变+多径→需要双扩展模型”两个句子的因果链压缩为单句。；will experience / require a ... channel model→give rise to ... links；删除 accurate ... characterization。

**分类理由：** 可定位完整的两句因果依据，但原句分句没有按原有语法保留，属于支持性概述，而非必要连接后直接组合。

**技术状态：** SUPPORTED：卫星高速及多径导致时变和频率选择性的描述与来源一致；不存在把单一 Doppler 误称为无时变的问题。

**公式适配：** 无公式。

**处理建议：** 若严格要求原句，保留 Shen 的两句及其因果连接，仅调整 TSLs 首次展开。

### P02-S02 — REASONABLE_COMBINATION

**当前稿完整句：**

```tex
We take the ground device as the stationary reference
point and assume that all propagation paths of device $k$ share the
same Doppler shift $\nu_k$ \cite{huang2026}.
```

**原文定位：**

- huang2026，PDF 第 2 页，II. System Model; Doppler shift。

> Take the ground user as the stationary reference point.

  定位/释义：印刷页 2950，左栏 Doppler shift 小段首句。
- huang2026，PDF 第 2 页，II. System Model; Doppler shift，式 (2)。

> The resulting Doppler term D(ψ) is assumed to be common to all propagation paths within the same satellite-to-ground (S2G) link [15].

  定位/释义：印刷页 2950，Eq.(2) 后第二个完整句；下一句以很小的多径角度扩展解释该近似。

**具体改动：** Take→We take，user→device，给同一链路加入 k 下标。；把原文被动假设分句改为与 We take 并列的 and assume that ... share the same ...；D(ψ)→ν_k。；原文同一 S2G 链路各传播路径的范围改写为同一 device k 的全部路径，未扩展为不同设备共用 Doppler。

**分类理由：** 两分句均对应 Huang §II 同一 Doppler 小段的可定位原句；主动/被动调整用于合成同一主语的并列句，未添加额外物理前提。按协议接受合理组合。该结论并非由“Doppler”词汇重合或仅由仿真设定推断。

**技术状态：** SUPPORTED：Huang p.2 正文明言同链路各径共用 Doppler，并以很小的多径角扩展作近似依据；这里仍须理解为建模近似，非所有移动散射环境的恒等式。

**公式适配：** D(ψ)→ν_k；source 的单用户链路扩展为按 k 独立定义的一组链路，没有假定 ν_k=ν_{k′}。

**处理建议：** 可保留；正文可补一句小角扩展的物理理由，若用户要求最小变更则无需扩写。

### P02-S03 — AUTHOR_DEFINED_OR_DERIVED

**当前稿完整句：**

```tex
Let $\mathbf a_k$ denote the uniform planar array (UPA) response vector
of device $k$, and let $t_{\rm c}$ denote the time measured from the
start of the transmission block.
```

**原文定位：**

- li2023，PDF 第 4 页，II-B. Signal Models。
  定位/释义：左栏 Eq.(3) 之前的阵列段：先给出按路径的二维到达角和 Kronecker 阵列向量，再基于星地距离长令同一终端各路径到达角近似相同，并去掉阵列向量的路径下标。这里为中文释义，无英文直引。
  对照限制：阵列响应按方向采用负指数及单位范数；本稿采用正指数、单位模各元素，不能直接按同一数值向量替换。
- shen2025，PDF 第 3 页，II-A. Terrestrial-satellite Link Model，式 (1)。
  定位/释义：Eq.(1)：逐路径 h_{i,u} δ(τ−τ_{i,u}) δ(ν−ν_{i,u}) 乘 e^{jπ n_z Θ^z_u} e^{jπ n_y Θ^y_u}；阵列角没有路径下标，而 ν_{i,u} 有路径下标。Eq.(1) 后 where 句定义天线索引与 physical paths。

**具体改动：** a_k 是本稿给共同 UPA 阵列响应所取符号；Shen 用逐天线指数，Li 用 g_k。；t_c 从本稿 transmission block 起点计时，是本稿新增的时间参考定义。

**分类理由：** 查阅的来源支持共同阵列响应概念，但未找到含此时间起点和这两个定义的对应完整原句。本句是作者符号/坐标定义，不能因 Let ... denote 模板常见而算原句。

**技术状态：** SUPPORTED AS DEFINITION：共同 a_k 需采用同设备各径 AoA 近同的近似；Li p.4 有明确说明，Shen Eq.(1)采用该结构。t_c 可自行定义。

**公式适配：** 把逐天线阵列因子收成向量；确定接收端块参考时间。该定义不等于各时刻 h_k 不变。

**处理建议：** 作为本稿定义明确保留，并在引入共同 a_k 处引用/说明相同 AoA 近似；若要求每句均为参考原句，则此句不满足，不能作已通过处理。

### P02-S04 — AUTHOR_DEFINED_OR_DERIVED

**当前稿完整句：**

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

**原文定位：**

- li2023，PDF 第 3 页，II-B. Signal Models，式 (2)。
  定位/释义：右栏 Eq.(2) 及紧跟的 where 句：给出逐路径复增益、Doppler、绝对传播延迟、阵列向量相乘求和的时变冲激响应，逐项解释这些量。中文释义，无英文直引。
- li2023，PDF 第 4 页，II-B. Signal Models。
  定位/释义：左栏 Eq.(3) 之前的阵列段：先给出按路径的二维到达角和 Kronecker 阵列向量，再基于星地距离长令同一终端各路径到达角近似相同，并去掉阵列向量的路径下标。这里为中文释义，无英文直引。
  对照限制：阵列响应按方向采用负指数及单位范数；本稿采用正指数、单位模各元素，不能直接按同一数值向量替换。
- shen2025，PDF 第 3 页，II-A. Terrestrial-satellite Link Model，式 (1)。
  定位/释义：Eq.(1)：逐路径 h_{i,u} δ(τ−τ_{i,u}) δ(ν−ν_{i,u}) 乘 e^{jπ n_z Θ^z_u} e^{jπ n_y Θ^y_u}；阵列角没有路径下标，而 ν_{i,u} 有路径下标。Eq.(1) 后 where 句定义天线索引与 physical paths。
- shen2025，PDF 第 3 页，II-A. Terrestrial-satellite Link Model，式 (1)。

> As shown in Fig. 1, τ_{i,u} = τ̃_{i,u} − τ^c represents the differential delay for the i-th path from the u-th device to the satellite, where τ̃_{i,u} and τ^c are denoted as propagation delay and common delay, respectively.

  定位/释义：Eq.(1) 后第二句。
  对照限制：英文逐字核对；引语中的数学符号是原 PDF 的文本转写，原文共同延迟 c 为上标，本稿 τ_c 将其改为下标。
- huang2026，PDF 第 2 页，II. System Model; Doppler shift，式 (2)。

> The resulting Doppler term D(ψ) is assumed to be common to all propagation paths within the same satellite-to-ground (S2G) link [15].

  定位/释义：印刷页 2950，Eq.(2) 后第二个完整句；下一句以很小的多径角度扩展解释该近似。

**具体改动：** Li Eq.(2) 的逐路径 â、ν_{k,q}、τ_{k,q}、g_{k,q} 经符号改名与参数约束，得到共同 a_k 和 ν_k。；Shen 的差分时延替代绝对时延；本稿指定接收端补偿共同传播时延。；where 合并路径数、复增益和 Dirac 函数定义，但“补偿后时变向量 CIR”完整句及本稿公式不是任一参考原句。

**分类理由：** 这是可说明来源的模型适配/公式推导：至少施加共同阵列、共同 Doppler，并变更延迟和时间参考。不能称只做术语替换，也不能以多篇分别支持各个词语即认定原句组合。

**技术状态：** CONDITIONALLY CONSISTENT：在同设备各径共同 Doppler、共同 AoA、差分延迟及固定块参考下数学形式成立。Shen 只直接给差分时延模型和共同延迟定义，其正文没有逐字给出本稿“在卫星接收机补偿后”的操作句。

**公式适配：** 从 Li 的逐路径时变 CIR 出发，令 ν_{kℓ}=ν_k、a_{kℓ}=a_k；以 τ̃_{kℓ}−τ_c 重定延迟零点。若接收端 t_c 的零点随共同补偿平移，所产生的固定 Doppler 相位须吸收入 g_{kℓ}，因 g 为复增益可做到。Shen Eq.(4) 使用 e^{j2πν(t−τ)} 的约定，与本稿 e^{j2πνt_c} 比较时也须相应吸收逐路径固定相位；二者不能在保留同一增益数值时直接等同。

**处理建议：** 保留为明确的本稿适配，并在公式附近补来源和前提，尤其说明共同 a_k 与时间/复增益约定。不能将该整句报告为参考原句直接改名。

### P02-S05 — SUPPORTED_PARAPHRASE

**当前稿完整句：**

```tex
The differential delay
of this path is $\tau_{k\ell}=\widetilde\tau_{k\ell}-\tau_c$, where
$\widetilde\tau_{k\ell}$ denotes its propagation delay.
```

**原文定位：**

- shen2025，PDF 第 3 页，II-A. Terrestrial-satellite Link Model，式 (1)。

> As shown in Fig. 1, τ_{i,u} = τ̃_{i,u} − τ^c represents the differential delay for the i-th path from the u-th device to the satellite, where τ̃_{i,u} and τ^c are denoted as propagation delay and common delay, respectively.

  定位/释义：Eq.(1) 后第二句。
  对照限制：英文逐字核对；引语中的数学符号是原 PDF 的文本转写，原文共同延迟 c 为上标，本稿 τ_c 将其改为下标。

**具体改动：** 把“τ差值 represents differential delay”改为“differential delay is τ差值”，重排定义方向。；删除 Fig.1 指引、重复的设备/卫星描述；把 propagation delay and common delay 的双定义拆出，只在本句保留传播延迟。

**分类理由：** 精确差分时延等式与物理含义有来源，但完整句的语序与从句组织已改写，不能归入仅术语替换。

**技术状态：** SUPPORTED：τ_{kℓ}=τ̃_{kℓ}−τ_c 与 Shen 相同。

**公式适配：** u→k、i→ℓ、共同延迟 τ^c→τ_c，差分时延等式无变化。

**处理建议：** 若必须逐句原句适配，恢复 Shen 该句的原有定义组织，并只改索引/删除失效图指引。

### P02-S06 — SUPPORTED_PARAPHRASE

**当前稿完整句：**

```tex
The common
delay $\tau_c$ is the propagation time between the satellite and
the closest point on Earth within the beam coverage
\cite{shen2025}.
```

**原文定位：**

- shen2025，PDF 第 3 页，II-A. Terrestrial-satellite Link Model，式 (1)。

> The common delay corresponds to the propagation time between the satellite and the closest point on earth within the beam coverage [21].

  定位/释义：Eq.(1) 后 τ 差定义之后。

**具体改动：** 增加 τ_c 符号。；corresponds to→is；earth→Earth；移除 Shen 的内部编号 [21]，替换为本稿引用。

**分类理由：** 核心连续原文高度一致，事实精确对应；但 corresponds to→is 是普通谓语改写，并非必要技术对象替换。严格类别应保留这个差别，不能把技术正确等同 TERM_ONLY。

**技术状态：** SUPPORTED：共同延迟取波束内最近地面点到卫星的传播时间，来源直接明确。

**公式适配：** 只补 τ_c 标签，无公式推导。

**处理建议：** 若严格要求仅术语替换，可把 is 恢复为 corresponds to；其余保留。

## P03

**段落顺序：** Shen Eq.(1) 阵列项 + Li §II-B 一般间距阵列，写成本稿向量索引 → Shen 方向余弦 + Li 间距/波长定义的改写 → 本稿四参数短块假设，背景为 Shen/Huang 的短时条件及 Li 的角度缓变

**结构判断：** 将阵列指数一般化后新增共同的块内参数冻结条件；该末句是本稿假设，不能由前两句阵列定义或 Li 的预补偿后 block fading 直接推出。短块条件应保留。

**段落结论：** 1 句支持性改写，2 句本稿定义/推导；当前三句都不能归为仅术语替换或直接原句组合。

### P03-S01 — AUTHOR_DEFINED_OR_DERIVED

**当前稿完整句：**

```tex
For antenna indices $n_z=0,\ldots,M_z-1$ and
$n_y=0,\ldots,M_y-1$, the entries of $\mathbf a_k$ are given by
\begin{equation}
 [\mathbf a_k]_{n_z+M_zn_y}
 =e^{j2\pi(d_yn_y\mu_{y,k}+d_zn_z\mu_{z,k})/\lambda}.
 \label{eq:upa}
\end{equation}
```

**原文定位：**

- shen2025，PDF 第 3 页，II-A. Terrestrial-satellite Link Model，式 (1)。
  定位/释义：Eq.(1)：逐路径 h_{i,u} δ(τ−τ_{i,u}) δ(ν−ν_{i,u}) 乘 e^{jπ n_z Θ^z_u} e^{jπ n_y Θ^y_u}；阵列角没有路径下标，而 ν_{i,u} 有路径下标。Eq.(1) 后 where 句定义天线索引与 physical paths。
- li2023，PDF 第 4 页，II-B. Signal Models。
  定位/释义：左栏第一完整段的无编号 UPA 公式 g(θ)=a_{M_x}(sin θ_y cos θ_x)⊗a_{M_y}(cos θ_y)，以及随后逐元素 a_{n_v}(x) 定义；其 where 句定义 λ=c/f_c 和沿轴相邻阵元间距 d_v。中文释义，无英文直引。
  对照限制：原式归一化因子为 1/√n_v，指数为负号。

**具体改动：** 由 Shen 的两个逐天线阵列指数抽取并相乘，写成本稿向量单个元素。；引入任意 d_y,d_z 和 λ；Shen Eq.(1) 的 π 指数对应 d_y=d_z=λ/2。；Li 一般间距向量具有负号和归一化，本稿改用正号和未归一化形式，另改轴命名与向量索引。

**分类理由：** 检索到的是源公式和相应定义，而不是“for antenna indices ... entries ... given by”连同此公式的原句。本稿完成向量化、索引展开与间距一般化，属于有来源的数学定义/适配。

**技术状态：** CONDITIONALLY CONSISTENT：当 μ 是相应 y/z 轴方向余弦并采用该接收阵列相位约定时公式成立；d=λ/2 时还原 Shen Eq.(1) 的阵列因子。归一化/相位符号与 Li 不同，不应声称其公式逐符号一致。

**公式适配：** n_z+M_z n_y 的索引与 Shen 的 n_z+n_y N_z 一致。将 e^{jπn_zΘ_z}e^{jπn_yΘ_y} 改写为 e^{j2π(d_y n_y μ_y+d_z n_z μ_z)/λ}，需要显式一般间距平面波阵列模型；不是只改变量名。

**处理建议：** 保留为本稿定义，附 Shen/Li 来源并写明阵列约定；若本稿实际固定半波长间距，可直接令 d_y=d_z=λ/2，但本次仅审计不修改。

### P03-S02 — SUPPORTED_PARAPHRASE

**当前稿完整句：**

```tex
Here, $\bigl(\mu_{y,k},\mu_{z,k}\bigr)$ are the directional cosines,
$\bigl(d_y,d_z\bigr)$ are the antenna spacings, and $\lambda$ is the
wavelength.
```

**原文定位：**

- shen2025，PDF 第 3 页，II-A. Terrestrial-satellite Link Model，式 (1)。

> The directional cosines Θ^z_u = cos ϑ^z_u and Θ^y_u = sin ϑ^z_u sin ϑ^a_u, along the z-axis and y-axis, depend on the zenith angle ϑ^z_u and azimuth angle ϑ^a_u, respectively.

  定位/释义：§II-A 在本页末尾的最后一句。
  对照限制：英文逐字核对；引语中的上下标及三角函数公式按原 PDF 转写。
- li2023，PDF 第 4 页，II-B. Signal Models。
  定位/释义：左栏第一完整段的无编号 UPA 公式 g(θ)=a_{M_x}(sin θ_y cos θ_x)⊗a_{M_y}(cos θ_y)，以及随后逐元素 a_{n_v}(x) 定义；其 where 句定义 λ=c/f_c 和沿轴相邻阵元间距 d_v。中文释义，无英文直引。
  对照限制：原式归一化因子为 1/√n_v，指数为负号。

**具体改动：** Shen 的两个方向余弦及角度关系改写为符号对 (μ_y,k, μ_z,k) 的统称。；Li 的 where 句给出波长及相邻阵元间距，本稿精简重组为 Here 后的三个并列定义。；未保留源句的完整原句或分句顺序。

**分类理由：** 三个物理名词都有可定位来源，含义可支持；本稿采用新符号并重写成并列定义句，不能将普通定义模板当作具体原句证据。

**技术状态：** SUPPORTED：方向余弦、间距和波长为上述阵列公式的相应物理量。方向余弦应明确关联 y/z 轴；该解释由公式和符号下标可推知，但当前句未展开角度定义。

**公式适配：** μ_y,k 对应 Shen Θ^y_u，μ_z,k 对应 Θ^z_u；d_y,d_z,λ 沿用一般阵列模型含义。

**处理建议：** 若必须采用原句组合，可明确拼合 Shen 的 directional-cosines 句与 Li 的定义分句，并妥善处理 Li 引用长度；现句应如实标为支持性改写。

### P03-S03 — AUTHOR_DEFINED_OR_DERIVED

**当前稿完整句：**

```tex
The path gains, differential delays, Doppler shifts, and
angles of arrival are assumed to remain approximately constant
within a transmission block.
```

**原文定位：**

- shen2025，PDF 第 4 页，II-B. Transmission Scheme，式 (1), (9)。

> Fortunately, H^{DDS}_{n_z,n_y,u}[k′,l′,l] remains approximately constant over Q consecutive frames, benefited by the quasi-static property of (1) in the delay-Doppler domain.

  定位/释义：右栏最后一句，Eq.(9) 讨论之后。
  对照限制：英文逐字核对；引语中的 H 张量记号按原 PDF 转写。
- shen2025，PDF 第 5 页，II-B. Transmission Scheme。

> In practice, the quasi-static property may be disrupted when the number of transmitted frames becomes large.

  定位/释义：左栏上端第二句；随后给 Q=8 与 Q=25 的 Doppler/时延变化例子，说明近似有时间范围。
- huang2026，PDF 第 3 页，III-A. Score-Based Model Training for AFDM Channel，式 (6)。

> Meanwhile, although AFDM can only guarantee approximate channel invariance within a finite signaling duration, the effective channel variation across several adjacent pilot sequences remains negligible because the corresponding Doppler-angle variation over a short interval is relatively small within pilot frames.

  定位/释义：印刷页 2951，左栏 Eq.(6) 后第二段末句。
- li2023，PDF 第 4 页，II-B. Signal Models，式 (5)。
  定位/释义：左栏阵列段末两句指出星地距离长使空间角变化缓慢；右栏 Eq.(5) 后的 block-fading 讨论则依赖终端 Doppler/时延预补偿。该后者条件不适用于本稿无终端预补偿情形。中文释义，无英文直引。

**具体改动：** 把 Shen 对 Q 帧 DD 域信道的准静态讨论与 Huang 的短时相邻导频讨论，细化为四类物理参数在本稿 transmission block 内近似不变。；加入 angles of arrival 的联合冻结条件；Li 只直接说明角度缓变。；未给 block 时长相对于这些变化尺度的明确界限。

**分类理由：** 在本轮核查的 Shen、Ding、Huang、Li 及 Cai 两版本中，未找到列出这四类参数并以 transmission block 为范围的对应原句。相关文献提供短时近似的背景，但该完整假设是本稿明确建立的模型条件。其写法“are assumed”允许作为作者假设，不等于来源错误或必须删除。

**技术状态：** CONDITIONALLY REASONABLE：冻结 g、τ、ν、AoA 不会消除 e^{j2πνt_c} 的相位变化，因而与时变 CIR 并不矛盾。该近似只适用于足够短的块，Shen 明示 Q 大时失效。Li Eq.(5) 后的补偿后 block fading 不可搬用为本稿无终端预补偿的直接证明。

**公式适配：** 无新显示公式；这是后续跨帧只含共同相位变化所需的建模条件。文献不能自动保证本稿任意 Q 或任意 block 时长均满足近似。

**处理建议：** 明确标为本稿短块假设，并在邻近处引用 Shen/Huang/Li 的限定依据。若用户坚持每句都是参考原句，本句目前不满足；不能只加一条泛引就标成原句适配。

## 原页视觉核对

本轮用 Poppler 重新渲染并实际 view_image 核对上列 8 个整页。Poppler 对 Shen 字体映射输出警告，相关原句、符号和公式均可读；以页面核对去除 clean 文本中的跨行断词/伪空格。

已查看：Shen PDF 3/4/5；Ding PDF 2；Huang PDF 2/3（印刷 2950/2951）；Li PDF 3/4。PNG 留存在 a_pdf_views/。

本轮关于“未找到原句”的结论仅限 SOURCES.json 所列且本审查员检索的 Shen、Ding、Huang、Li 和 Cai 两版本，不代表所有文献均无此表述。
