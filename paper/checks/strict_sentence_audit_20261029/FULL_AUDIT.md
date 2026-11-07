# 第二章完整逐句对照

> 本轮历史图和绘图脚本已移入归档；当前生图入口见 [统一说明](../../../src/evaluation/plots/manuscript/README.md)。以下记录描述当时版本。

总览与统计见[审查总览](<D:/afdm-gfra/paper/checks/strict_sentence_audit_20261029/SUMMARY.md>)。本文件按P01—P12、每段S01起逐句列示。

当前文字保留TeX以避免二次改写；来源引文保留各审查员核实的数学转写。具体排版规范化及补充候选来源详见对应JSON。

## P01　系统总述

{'pass': False, 'summary': '不通过最严格标准：5句中2句满足句级EXACT/TERM_ONLY，3句有非术语删改；虽同源同序，完整限定和连接结构未保留。', 'most_important_failures': ['P01-S01删除固定波束限定。', 'P01-S02删除再生载荷和星上基带处理并列成分。', 'P01-S05把广播机制改为补偿条件，并改连接关系。']}

原始证据：[P01.json](<D:/afdm-gfra/paper/checks/strict_sentence_audit_20261029/P01.json>)；精简对照：[P01.md](<D:/afdm-gfra/paper/checks/strict_sentence_audit_20261029/P01.md>)。

### P01-S01　存在非术语增删改

**当前完整句：**

```latex
We consider a LEO satellite-enabled grant-free random access system, where AFDM is adopted to mitigate the doubly dispersive effect inherent in terrestrial-satellite links (TSLs) \cite{ding2026,bemani2022}.
```

**来源：** [shen2025.pdf](<D:/afdm-gfra/reference/literature/shen2025.pdf>)，PDF第3页；II. SYSTEM MODEL，Fig. 1下首段，第1句。

**核对原句：**

```text
We consider a LEO satellite-enabled grant-free random access system with the fixed beam as illustrated in Fig. 1, where OTFS is adopted to mitigate the doubly dispersive effect [18] inherent in TSLs.
```

**差异清单：**

```json
{
  "necessary_substitutions": [
    "OTFS → AFDM（调制对象名称替换）",
    "TSLs → terrestrial-satellite links (TSLs)（链路术语首次展开）"
  ],
  "other_changes": [
    "删除 system 之后的完整限定成分 with the fixed beam as illustrated in Fig. 1；其中 with the fixed beam 是系统假设限定，不能按图号/排版差异豁免。"
  ],
  "display_only": [
    "原文 [18] 位于 effect 后，当前改为句末 \\cite{ding2026,bemani2022}；引文显示差异不决定语言类别。"
  ]
}
```

**判定理由：** 虽然句型主体及where从句保留，但删除了固定波束限定及其图示从句，超出仅替换必要术语。

### P01-S02　存在非术语增删改

**当前完整句：**

```latex
The system comprises $K$ single-antenna terrestrial devices that communicate with a LEO satellite equipped with a uniform planar array (UPA) consisting of $M=M_yM_z$ antennas.
```

**来源：** [shen2025.pdf](<D:/afdm-gfra/reference/literature/shen2025.pdf>)，PDF第3页；II. SYSTEM MODEL，首段，第2句。

**核对原句：**

```text
The system comprises U single-antenna terrestrial devices that communicate with a LEO satellite equipped with a uniform planar array (UPA) consisting of N_a = N_z × N_y antennas and a regenerative payload for on-board baseband signal processing.
```

**差异清单：**

```json
{
  "necessary_substitutions": [
    "设备数 U → K。",
    "天线总数 N_a → M，阵列维度 N_z → M_z、N_y → M_y。"
  ],
  "other_changes": [
    "删除 antennas 后的 and a regenerative payload for on-board baseband signal processing，删去卫星配备再生载荷及其用途的完整并列成分。"
  ],
  "display_only": [
    "维度乘积 N_z × N_y → M_yM_z 同时交换两个标量因子顺序并省略乘号；该符号层调整不会使删除并列成分获得豁免。"
  ]
}
```

**判定理由：** 设备数和阵列维度可视为符号替换，但再生载荷及星上基带处理限定被整体删除。

### P01-S03　仅必要术语或符号替换

**当前完整句：**

```latex
During each transmission block, active devices share the same time-frequency resources to transmit their pilots to the satellite.
```

**来源：** [shen2025.pdf](<D:/afdm-gfra/reference/literature/shen2025.pdf>)，PDF第3页；II. SYSTEM MODEL，首段，第3句。

**核对原句：**

```text
During each time interval, active devices share the same time-frequency resources to transmit their signals to the satellite.
```

**差异清单：**

```json
{
  "necessary_substitutions": [
    "time interval → transmission block（本文用于描述一次传输所占时间单位的名称）。",
    "signals → pilots（本文传输对象改为导频）。"
  ],
  "other_changes": [],
  "display_only": []
}
```

**判定理由：** 完整原句可逐词对齐，仅两个技术对象名词短语替换；During each、share the same、to transmit their及其余词序全部保留，没有删从句或改操作谓语。

### P01-S04　原句一致

**当前完整句：**

```latex
Additionally, to minimize energy consumption, we assume that these terrestrial devices operate without GNSS capabilities and do not pre-compensate for delay and Doppler shifts.
```

**来源：** [shen2025.pdf](<D:/afdm-gfra/reference/literature/shen2025.pdf>)，PDF第3页；II. SYSTEM MODEL，首段，第4句。

**核对原句：**

```text
Additionally, to minimize energy consumption, we assume that these terrestrial devices operate without GNSS capabilities and do not pre-compensate for delay and Doppler shifts.
```

**差异清单：**

```json
{
  "necessary_substitutions": [],
  "other_changes": [],
  "display_only": [
    "仅归并原PDF断行、行末连字符和抽取层词内多余空格；文字已回看PDF确认。"
  ]
}
```

**判定理由：** 全部词语、词序、Additionally连接词及and并列关系一致。

### P01-S05　存在非术语增删改

**当前完整句：**

```latex
After compensating for the common propagation delay $\tau_c$, the satellite receiver handles the differential delay and Doppler shift observed in the uplink transmission \cite{shen2025}.
```

**来源：** [shen2025.pdf](<D:/afdm-gfra/reference/literature/shen2025.pdf>)，PDF第3页；II. SYSTEM MODEL，首段，第5句。

**核对原句：**

```text
Following 3GPP recommendations [19], [20], the satellite initially broadcasts a common delay for all devices, and subsequently handles the differential delay and Doppler shift observed in the uplink transmission.
```

**差异清单：**

```json
{
  "necessary_substitutions": [
    "the satellite → the satellite receiver（处理主体的技术名称细化；该局部替换本身不豁免其余机制改写）。"
  ],
  "other_changes": [
    "句首 Following 3GPP recommendations [19], [20] 改为 After compensating for the common propagation delay τ_c：依据某规范改成完成时延补偿之后的时间条件，连接关系和操作均变化。",
    "删除主语后 initially broadcasts a common delay for all devices, and subsequently：取消初始广播公共时延给全部设备的动作、for all devices范围和and随后处理的并列顺序。",
    "当前加入 common propagation delay τ_c 作为compensating for的宾语；原首段句子只说broadcasts a common delay，未在本句规定接收机完成公共传播时延补偿。"
  ],
  "display_only": [
    "增加句末 \\cite{shen2025}；删除/替换原规范引文编号不单独决定类别。"
  ]
}
```

**判定理由：** “卫星先广播公共时延、随后处理”被改成“补偿公共传播时延后由接收机处理”，并删除了原连接词和操作链，属于机制及句法改写。

### 段落组织

```json
{
  "same_original_paragraph": true,
  "source_paragraph": "Shen PDF第3页§II首段的第1—5句",
  "order_preserved": true,
  "cross_source_sentence_splicing": false,
  "connectives": "第1句where、第3句During each及to、第4句Additionally/to/that/and保留；第2句and a regenerative payload并列支被删；第5句Following…与and subsequently…被替换或删除。",
  "full_structure_preserved": false,
  "source_attribution_risk": "当前首句引Ding/Bemani，其文字框架实际对应Shen首段；这些技术引文不能证明该句符合原句仅术语替换。第5句的接收机补偿公共传播时延设定也不能由Shen原首段的广播句自动归属给Shen。",
  "scope_note": "整段可定位为对同一原段的按序改写；这不等于整段是仅替换必要术语。AFDM、导频传输、本文block命名及τ_c补偿表述应区分为本文适配内容。"
}
```

## P02　物理信道与参数

FAIL：13句中5句达到EXACT/TERM_ONLY，8句未达到；且整段组织不是同一原段。

原始证据：[P02.json](<D:/afdm-gfra/paper/checks/strict_sentence_audit_20261029/P02.json>)；精简对照：[P02.md](<D:/afdm-gfra/paper/checks/strict_sentence_audit_20261029/P02.md>)。

### P02-S01　原句一致

**当前完整句：**

```latex
The TSLs will experience fast variations due to the high mobility of
the LEO satellite.
```

**来源：** [shen2025.pdf](<D:/afdm-gfra/reference/literature/shen2025.pdf>)，PDF第3页；II-A Terrestrial-satellite Link Model。

**核对原句：**

```text
The TSLs will experience fast variations due to the high mobility of the LEO satellite.
```

**来源定位/检索边界：** 右栏II-A第一句；shen2025.pages.txt 368–369行。

**差异清单：**

```json
{
  "necessary_term_substitutions": [],
  "other_changes": []
}
```

**判定理由：** 完整句词语、词序、句法和限定条件一致；只规范化PDF断行。

### P02-S02　原句一致

**当前完整句：**

```latex
Hence, this time variation and multipath propagation
require a doubly dispersive channel model for accurate TSLs
characterization \cite{shen2025}.
```

**来源：** [shen2025.pdf](<D:/afdm-gfra/reference/literature/shen2025.pdf>)，PDF第3页；II-A Terrestrial-satellite Link Model。

**核对原句：**

```text
Hence, this time variation and multipath propagation require a doubly dispersive channel model for accurate TSLs characterization.
```

**来源定位/检索边界：** 右栏II-A第二句，紧接S01的原句；shen2025.pages.txt 369–371行。

**差异清单：**

```json
{
  "necessary_term_substitutions": [],
  "other_changes": [
    "当前句末增加来源引用；按协议属于引用显示层差异，不计实质修改。"
  ]
}
```

**判定理由：** 完整句及连接词Hence一致；抽取文本将and断成an d，已回看PDF确认。

### P02-S03　仅必要术语或符号替换

**当前完整句：**

```latex
Take the ground device as the
stationary reference point.
```

**来源：** [huang2026.pdf](<D:/afdm-gfra/reference/literature/huang2026.pdf>)，PDF第2页；II System Model，Doppler shift小段。

**核对原句：**

```text
Take the ground user as the stationary reference point.
```

**来源定位/检索边界：** 左栏Doppler shift斜体标签后的第一句、式(2)之前；huang2026.pages.txt 164–165行。

**差异清单：**

```json
{
  "necessary_term_substitutions": [
    "user → device（地面通信对象名称）"
  ],
  "other_changes": []
}
```

**判定理由：** 只有通信对象名称变化，冠词、介词、谓语及语序全部保留。

### P02-S04　仅必要术语或符号替换

**当前完整句：**

```latex
The resulting Doppler term $\nu_k$ is
assumed to be common to all propagation paths within the same TSL
\cite{huang2026}.
```

**来源：** [huang2026.pdf](<D:/afdm-gfra/reference/literature/huang2026.pdf>)，PDF第2页；II System Model，Doppler shift小段，式(2)之后。

**核对原句：**

```text
The resulting Doppler term $D(\psi)$ is assumed to be common to all propagation paths within the same satellite-to-ground (S2G) link [15].
```

**来源定位/检索边界：** 左栏式(2)及其where定义结束后的一整句；huang2026.pages.txt 171–173行。

**差异清单：**

```json
{
  "necessary_term_substitutions": [
    "$D(\\psi)$ → $\\nu_k$（Doppler量符号）",
    "satellite-to-ground (S2G) link → TSL（本文链路名称/缩写）"
  ],
  "other_changes": []
}
```

**判定理由：** 句型及其余词序一致。原文的resulting承接已给出的速度/角度Doppler公式；本文删去该前文属于段落组织问题，不额外计入本句。

### P02-S05　存在非术语增删改

**当前完整句：**

```latex
As a result of the long distance between the satellite
and device $k$, the angles-of-arrival for different paths tend to be
identical \cite{li2023}.
```

**来源：** [li2023.pdf](../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/strict_sentence_audit_20261029/sources/li2023.pdf)，PDF第4页；II-B Signal Models。

**来源定位/检索边界：** 左栏第一个完整段：阵列响应和波长/阵距定义之后、去除路径下标的结论之前，说明卫星与终端距离使各路径到达角趋同的完整句；li2023.pages.txt 370–373行。此处不用英文原文直引。

**差异清单：**

```json
{
  "necessary_term_substitutions": [
    "终端名称UT k → device k",
    "到达角缩写展开为angles-of-arrival"
  ],
  "other_changes": [
    "原句到达角的“成对”限定被删除。",
    "原句显式角度变量被删除。",
    "原句对不同路径属于同一终端信道的限定被删除。",
    "句末用于明确各路径角度相等及路径取值范围的解释成分整体被删除；不是只替换公式符号。"
  ]
}
```

**判定理由：** 可以明确定位完整原句，但多处句内删减超过必要术语替换；不能把剩余相似骨架判为TERM_ONLY。

### P02-S06　本次未定位可对齐整句

**当前完整句：**

```latex
Let $\mathbf a_k$ denote the array response
vector of device $k$.
```

**来源定位/检索边界：** 本次核查未定位可对齐整句。检索Shen、Huang、Li、Cai期刊版、Cai v2、Ding及Bemani的pages文本，并阅读相邻原文段。

**差异清单：**

```json
{
  "necessary_term_substitutions": [],
  "other_changes": [
    "没有可逐词对齐的整句，不能列出一组“必要替换”作为通过证据。当前句是在本文中为$\\mathbf a_k$设定名称。"
  ]
}
```

**判定理由：** Li有阵列响应定义及去除路径下标的说明，但它们的完整句法和信息结构不同；相同术语不足以建立原句对应。

### P02-S07　存在非术语增删改

**当前完整句：**

```latex
Then, the time-varying channel impulse response
from the $k$th device to the satellite can be represented as
\begin{equation}
 \mathbf h_k(t,\tau)
 =\mathbf a_k\sum_{\ell=1}^{L_k}g_{k\ell}
 e^{j2\pi\nu_k t}\delta(\tau-\tau_{k\ell}),
 \label{eq:physical-channel}
\end{equation}
where $L_k$ is the number of propagation paths, $g_{k\ell}$ denotes
the complex channel coefficient associated with the $\ell$th path,
and $\delta(\cdot)$ represents the Dirac delta function.
```

**来源：** [shen2025.pdf](<D:/afdm-gfra/reference/literature/shen2025.pdf>)，PDF第3页；II-A，式(1)引入及where；并拼接Huang II式(1)的部分说明。

**核对原句：**

```text
Then, the delay-Doppler-space domain channel from the $u$-th device to the $(n_z+n_yN_z)$-th antenna at the satellite can be represented as [18] [原式(1)] where $u=0,\ldots,U-1$, $n_z=0,\ldots,N_z-1$, $n_y=0,\ldots,N_y-1$, and $P$ is the number of physical paths.
```

**来源定位/检索边界：** Shen右栏II-A第三句及式(1)后的索引/路径数说明；Huang PDF第2页左栏式(1)前后。以下原式占位只替代显示公式；文字说明按整语法单元记录。

**差异清单：**

```json
{
  "necessary_term_substitutions": [
    "$u$ → $k$，路径索引$i$ → $\\ell$等符号变化",
    "信道名称从delay-Doppler-space domain channel改成time-varying channel impulse response（领域/对象名称变化，但不是本句唯一改动）",
    "Huang的$h_i$ → $g_{k\\ell}$"
  ],
  "other_changes": [
    "Shen句中的逐天线接收对象改为整体卫星；原逐天线索引短语被删除，接收量组织改变。",
    "Shen公式后原有设备与两个阵列索引范围整体删除。",
    "路径数定义从physical paths改为propagation paths，并从$P$改为设备相关的$L_k$。",
    "加入Huang式(1)说明中关于复系数及Dirac函数的两段原词序，新增and连接；Huang原完整说明中的时延/Doppler范围、归一化表达和索引等剩余成分未保留。",
    "本句因此是引入语和变量说明跨文献组合；即使每个术语正确，也不是一个来源完整句的纯替换。"
  ]
}
```

**判定理由：** 含where的完整句不能通过：能定位Shen引入骨架和Huang定义语，但存在删除、增补及拼接。

### P02-S08　存在非术语增删改

**当前完整句：**

```latex
$\tau_{k\ell}=\widetilde\tau_{k\ell}-\tau_c$ represents the differential
delay for the $\ell$th path from the $k$th device to the satellite,
where $\widetilde\tau_{k\ell}$ and $\tau_c$ are denoted as propagation
delay and common delay, respectively.
```

**来源：** [shen2025.pdf](<D:/afdm-gfra/reference/literature/shen2025.pdf>)，PDF第3页；II-A，式(1)之后。

**核对原句：**

```text
As shown in Fig. 1, $\tau_{i,u}=\widetilde\tau_{i,u}-\tau^c$ represents the differential delay for the $i$-th path from the $u$-th device to the satellite, where $\widetilde\tau_{i,u}$ and $\tau^c$ are denoted as propagation delay and common delay, respectively.
```

**来源定位/检索边界：** 右栏式(1)后，路径数说明之后、公共时延定义之前；shen2025.pages.txt 381–386行。

**差异清单：**

```json
{
  "necessary_term_substitutions": [
    "$\\tau_{i,u}$ → $\\tau_{k\\ell}$",
    "$\\widetilde\\tau_{i,u}$ → $\\widetilde\\tau_{k\\ell}$",
    "$\\tau^c$ → $\\tau_c$",
    "$i$-th → $\\ell$th；$u$-th → $k$th（路径/设备索引）"
  ],
  "other_changes": [
    "删除完整句首“As shown in Fig. 1,”；删除的是图示引导语，不只是变更图号。"
  ]
}
```

**判定理由：** 其余正文可以逐词对齐，但严格协议下删除一个句内成分即不能判TERM_ONLY。

### P02-S09　原句一致

**当前完整句：**

```latex
The common delay corresponds
to the propagation time between the satellite and the closest point
on earth within the beam coverage \cite{shen2025}.
```

**来源：** [shen2025.pdf](<D:/afdm-gfra/reference/literature/shen2025.pdf>)，PDF第3页；II-A，式(1)之后的公共时延定义。

**核对原句：**

```text
The common delay corresponds to the propagation time between the satellite and the closest point on earth within the beam coverage [21].
```

**来源定位/检索边界：** 右栏S08原句之后紧接的一句；shen2025.pages.txt 386–389行。

**差异清单：**

```json
{
  "necessary_term_substitutions": [],
  "other_changes": [
    "引用号变为本文文献引用，属于协议允许的显示层差异。"
  ]
}
```

**判定理由：** 包括earth的小写形式在内，完整句词语和顺序一致；PDF抽取的closes t已按页面恢复。

### P02-S10　本次未定位可对齐整句

**当前完整句：**

```latex
Let $t$ denote the time measured from the start of the transmission
block.
```

**来源定位/检索边界：** 本次核查未定位可对齐整句；对所有本轮sources文本检索时间原点、从传输块开始计时的完整短语，并检查相关系统模型。

**差异清单：**

```json
{
  "necessary_term_substitutions": [],
  "other_changes": [
    "当前增加本文时间变量的参考原点定义；没有可对齐的完整来源句。"
  ]
}
```

**判定理由：** 时间变量出现在文献模型中，不等于“从本传输块开始测量”的整句有文献原句。

### P02-S11　本次未定位可对齐整句

**当前完整句：**

```latex
The array response vector $\mathbf a_k$ can be represented as
\begin{equation}
 [\mathbf a_k]_{n_z+M_zn_y}
 =e^{j2\pi(d_yn_y\mu_{y,k}+d_zn_z\mu_{z,k})/\lambda},
 \label{eq:upa}
\end{equation}
where $\mu_{y,k}$ and $\mu_{z,k}$ are the directional cosines, $d_y$
and $d_z$ are the antenna spacings, $\lambda$ is the wavelength,
$0\leq n_y<M_y$, and $0\leq n_z<M_z$.
```

**来源定位/检索边界：** 本次核查未定位可对齐的完整引入语＋式(2)＋where句。Li PDF第4页II-B阵列定义和Shen PDF第3页II-A最后一句仅是相关内容。

**差异清单：**

```json
{
  "necessary_term_substitutions": [],
  "other_changes": [
    "当前将方向余弦、两个轴间距、波长及两个索引范围组合为一个where列表；未定位保留这一完整词序及连接关系的来源句。",
    "不能把阵列响应、波长、方向余弦等分散术语视为同一个原句。"
  ]
}
```

**判定理由：** 阵列公式可与文献模型作数学对应，但其整句说明没有可逐词对齐的来源；据一般数学形式推得不属于原句一致性证据。

### P02-S12　本次未定位可对齐整句

**当前完整句：**

```latex
Assume that the path gains,
differential delays, Doppler shifts, and angles-of-arrival remain
approximately constant within a transmission block.
```

**来源定位/检索边界：** 本次核查未定位同时列出四类路径参数并在传输块内保持近似不变的可对齐整句。最接近的Cai两版块衰落句只可作对照，不能视为本句原文。

**差异清单：**

```json
{
  "necessary_term_substitutions": [],
  "other_changes": [
    "当前主语为路径增益、差分时延、Doppler、到达角四项；Cai的相关句主语是所有信道，且开头先声明块衰落模型。",
    "Shen的相关近似不变结论是DD域有效信道跨连续帧的性质，Huang相关说明是相邻导频序列的有效信道变化小；两者均不是该四项参数列表句。"
  ]
}
```

**判定理由：** 主题相关不足以建立完整原句。把整信道准静态句替换为四类参数恒定还会改变模型对象，不能将这种变化包装成必要术语替换。

### P02-S13　本次未定位可对齐整句

**当前完整句：**

```latex
The time variation in \eqref{eq:physical-channel} is therefore
determined by $e^{j2\pi\nu_k t}$.
```

**来源定位/检索边界：** 本次核查未定位可对齐整句。对sources文本检索时间变化与相位指数决定关系，并检查Shen/Huang/Li相关模型。

**差异清单：**

```json
{
  "necessary_term_substitutions": [],
  "other_changes": [
    "这是从本文式(1)与S12冻结参数假设导出的解释句，新增therefore因果承接。"
  ]
}
```

**判定理由：** 本文公式可以支持这个推论，不等于它是文献完整原句的纯术语替换。

### 段落组织

```json
{
  "same_original_paragraph": false,
  "organization_pass": false,
  "sequence": "Shen II-A开头两句 → Huang Doppler小段的首句及较后一句 → Li II-B到达角句的删改 → 本文符号句 → Shen/Huang拼接的式(1)说明 → Shen差分时延与公共时延相邻两句 → 本文计时、阵列定义、冻结参数及推论。",
  "preserved_local_order": [
    "S01→S02沿用Shen相邻两句和Hence。",
    "S08→S09沿用Shen相邻两句顺序。"
  ],
  "omitted_or_reordered_context": [
    "S03与S04之间原有Huang卫星速度、Doppler公式和变量解释被抽走；resulting仍保留但原承接不存在。",
    "S02之后原本紧跟Shen的信道式引入；当前在S07之前插入Huang、Li和自定义句，Then的前文已改变。",
    "Li原文先给每路径阵列响应及阵距/波长定义，再解释路径到达角趋同，继而去除路径下标；当前将趋同句提前到阵列定义之前。",
    "S13的therefore为本文自己追加的参数冻结→时变因子推论。"
  ],
  "attribution_risks": [
    "式(1)和式(2)属于本文组合的具体模型约定，不能因旁边引了Shen/Huang/Li就宣称整段来自其中一个原段。",
    "Cai整信道块衰落假设与本文路径参数冻结并非同一表述或同一对象。"
  ],
  "conclusion": "整段不是同一原段的必要术语替换：至少混合Shen、Huang、Li三个来源位置，并加入本文模型定义及推论；整段组织不通过。"
}
```

## P03　多帧传输与IDAFT

不通过最严格标准：7句中仅1句TERM_ONLY，其余4句OTHER_CHANGE、2句NO_SOURCE；且段落并非来自同一原段。仅审查，未修改正文。

原始证据：[P03.json](<D:/afdm-gfra/paper/checks/strict_sentence_audit_20261029/P03.json>)；精简对照：[P03.md](<D:/afdm-gfra/paper/checks/strict_sentence_audit_20261029/P03.md>)。

### P03-S01　存在非术语增删改

**当前完整句：**

```latex
The multi-frame AFDM transmission scheme is proposed to handle the large differential delay and Doppler shift.
```

**来源：** [shen2025.pdf](<D:/afdm-gfra/reference/literature/shen2025.pdf>)，PDF第4页；II-B Transmission Scheme，首句。

**核对原句：**

```text
The spreading-based multi-frame OTFS transmission scheme is proposed to handle the large differential delay and Doppler shift.
```

**差异清单：**

```json
{
  "necessary_terminology": [
    "OTFS → AFDM。"
  ],
  "other": [
    "删除 spreading-based。该词限定方案采用扩频机制；删除此限定不等于只替换调制名称。"
  ],
  "display_only": []
}
```

**判定理由：** 除 OTFS → AFDM 外还删去了方案机制限定语，故整句不能归入 TERM_ONLY。

### P03-S02　仅必要术语或符号替换

**当前完整句：**

```latex
Assume that a total of $Q$ AFDM frames are allocated for pilot transmission.
```

**来源：** [cai2026.pdf](<D:/afdm-gfra/reference/literature/cai2026.pdf>)，PDF第4页；II-A System Model，式(2)后、式(3)前的导频段首句。

**核对原句：**

```text
Assume that a total of $T$ OFDM symbols are allocated for pilot transmission.
```

**差异清单：**

```json
{
  "necessary_terminology": [
    "数量符号 T → Q。",
    "传输单位 OFDM symbols → AFDM frames（OFDM → AFDM；symbols → frames）。"
  ],
  "other": [],
  "display_only": [
    "恢复提取层连写的 ofT/TOFDM 等空格。"
  ]
}
```

**判定理由：** 保留 Assume that a total of … are allocated for pilot transmission 的完整词序和连接关系，只换数量符号及传输对象名称。

### P03-S03　存在非术语增删改

**当前完整句：**

```latex
Specifically, in the $q$th AFDM frame, $q=0,\ldots,Q-1$, the $k$th device is assigned a pilot vector $\mathbf p_{qk}\in\mathbb C^N$, with $[\mathbf p_{qk}]_n=P_{qkn}$, where $N$ is the number of AFDM chirp subcarriers and $\Delta f$ is the subcarrier spacing.
```

**来源：** [shen2025.pdf](<D:/afdm-gfra/reference/literature/shen2025.pdf>)，PDF第4页；II-B Transmission Scheme，首段 Specifically 句、式(2)前。

**核对原句：**

```text
Specifically, in the $q$-th OTFS frame, $q=0,\ldots,Q-1$, the $u$-th device is assigned a spreading code $C_{u,q}[k,l]$, $k=\lceil-N/2\rceil,\ldots,\lceil N/2\rceil-1$, $l=0,\ldots,M-1$, where $M$ and $N$ are the number of subcarriers and OFDM symbols within one OTFS frame, respectively.
```

**差异清单：**

```json
{
  "necessary_terminology": [
    "主干中的 OTFS → AFDM；设备指标 u → k。",
    "spreading code C_{u,q}[k,l] → pilot vector p_{qk}（对象名称及二维扩频码至一维向量的记号/维度调整）。",
    "子载波数量符号 M → N；subcarriers → AFDM chirp subcarriers 可视为技术对象限定，但仍须核查整段 where 语法。"
  ],
  "other": [
    "在向量对象后加入数学类型 p_{qk}∈C^N；原二维指标范围 k=…、l=… 被删去。数学维度调整单列记录，不以其自身作为语言不通过的唯一依据。",
    "新增完整短语 with [p_{qk}]_n=P_{qkn}，包括原句没有的连接词 with 和元素定义。",
    "where M and N are the number of … 改成 where N is the number of …：删去并列变量中的一个成员并把 are 改为 is；这使原双变量、双对象对应定义改为单变量定义。",
    "删除原定义尾部 and OFDM symbols within one OTFS frame, respectively；OFDM 符号数量及逐项对应关系不再保留。",
    "在 subcarriers 后增加 and Δf is the subcarrier spacing；这是新增的第二个独立定义从句，不是替换原 OFDM symbols 的一个术语。",
    "Huang 的 Let N denote the number of AFDM chirp subcarriers 仅以术语/定义片段进入当前 where 从句；其 Let、denote 句型未保留。Ding 子载波间隔表述也未作为完整原句保留。"
  ],
  "display_only": [
    "Specifically, in the … frame 及 q=0,…,Q−1 的次序保留。",
    "数学指标排印 q-th/u-th 与 $q$th/$k$th 的连字符和 TeX 写法不单独计为实质改动。"
  ]
}
```

**判定理由：** 主干可对齐 Shen，但增加 with 定义，并重写、删减和扩展 where 定义；完整句不是仅术语替换。

### P03-S04　本次未定位可对齐整句

**当前完整句：**

```latex
The $N$ pilot symbols have energy $\|\mathbf p_{qk}\|^2=E_p$.
```

**来源定位/检索边界：** 本次在 Shen、Cai期刊版、Cai v2、Ding、Huang 的逐页文本中检索并核对导频/能量段，未定位可逐词对齐的完整原句；相关但不等同内容为 Cai期刊版 PDF第4页 II-A 式(4)后、Cai v2 PDF第4页 II-A 式(4)后。

**差异清单：**

```json
{
  "necessary_terminology": [],
  "other": [
    "没有可对齐原句，不能编造逐词替换表。当前完整命题（N 个导频符号的向量能量为 E_p）属于本次未定位来源的新增说明。",
    "Cai 的相同 transmit power budget 与本文每帧向量能量条件不能仅通过 P→E_p 取得当前完整句；主语、谓语及约束表达均不同。"
  ],
  "display_only": []
}
```

**判定理由：** 相关功率预算概念不足以提供整句词语与句型来源；本次核查未定位。

### P03-S05　本次未定位可对齐整句

**当前完整句：**

```latex
Different pilot vectors, known at the satellite receiver, are used across frames.
```

**来源定位/检索边界：** 本次在全部七份 sources/*.pages.txt 中检索 pilot vector(s)、known at the satellite、different pilot 及跨行规范化文本；核心来源中未定位完整可对齐句。相关位置是 Huang PDF第3页 III-A 式(6)后 multiple pilot sequences 的说明，及 Shen PDF第4页 II-B 的逐帧 spreading code 定义。

**差异清单：**

```json
{
  "necessary_terminology": [],
  "other": [
    "没有可对齐原句，无法认定存在仅术语替换。",
    "Different、known at the satellite receiver 插入语、are used across frames 这一整体组合为本次未定位来源的说明；多导频或逐帧索引不能替代整句证据。"
  ],
  "display_only": []
}
```

**判定理由：** 查到的是多导频/逐帧索引的相关概念，未查到当前完整句的措辞和连接关系。

### P03-S06　存在非术语增删改

**当前完整句：**

```latex
The time-domain transmitted signal is generated through the inverse discrete affine Fourier transform (IDAFT) applied to $\mathbf p_{qk}$, mathematically formulated as $\mathbf s_{qk}=\mathbf F_{\rm A}^{\mathsf H}\mathbf p_{qk}$ \cite{ding2026}, where $\mathbf F_{\rm A}$ denotes the discrete affine Fourier transform (DAFT) matrix, given by \begin{equation}\begin{gathered}[\mathbf F_{\rm A}]_{rt}=\frac{1}{\sqrt N}e^{-j2\pi(c_2r^2+rt/N+c_1t^2)},\\r,t=0,\ldots,N-1.\end{gathered}\label{eq:daft}\end{equation}
```

**来源：** [ding2026.pdf](<D:/afdm-gfra/reference/literature/ding2026.pdf>)，PDF第2页；II，式(1)主句及其 where；式(2)的矩阵形式句及其 where。

**核对原句：**

```text
The time-domain transmitted signal is generated through the inverse discrete affine Fourier transform (IDAFT) applied to $\mathbf x_k$, mathematically formulated as $s_k[n]=\frac{1}{\sqrt N}\sum_{m=0}^{N-1}x_k[m]e^{j2\pi(c_1n^2+c_2m^2+nm/N)}$, where $x_k[m]$ represents the $m$-th symbol of $\mathbf x_k$.
```

**差异清单：**

```json
{
  "necessary_terminology": [
    "IDAFT 主干中的输入 x_k → p_{qk}；输出及帧指标 s_k → s_{qk}；矩阵记号 A → F_A。"
  ],
  "other": [
    "Ding 式(1)所附 where x_k[m] represents the m-th symbol of x_k 被整体省去；当前在同一主句后接的是另一种矩阵定义。",
    "把 Ding 式(1)的主干与式(2)的矩阵形式/定义组织到同一句；省去式(2)独立引导句 The signal in (1) can be represented in matrix form as。两处原句之间还隔着 c1 and c2 的独立定义，故不是原有同一句的连续保留。",
    "若按 Ding 式(2) where 对齐：矩阵定义中的 represents → denotes，并把原 A^H=Λ^H F Λ^H 的定义对象改成 F_A；不把整个原定义从句视为一个术语。",
    "在 DAFT matrix 之前增加全称 discrete affine Fourier transform 并把 DAFT 放入括号；这是展开缩写的字词增加，按本轮仅术语替换标准仍须列出。",
    "新增连接短语 given by，并接本文式(3)的逐元素表达；Ding 对应说明句没有 given by。",
    "若选择 Huang 的 where A denotes the DAFT matrix 为局部来源，须同时记录删去后续 c1/c2、Λ_c、F 三组并列定义，并将此子句接到 Ding 主干之后；仍然是跨句/跨来源组合。此为文本对齐的替代证据路径，不断言作者实际写作顺序。"
  ],
  "display_only": [
    "行内/显示公式、式号与引用编号的改变本身不计语言违规。",
    "Ding 标量求和式换为矩阵式、DAFT逐元素定义属于公式组织/记号变化，单独记录但不以公式本身未逐字同式判失败。"
  ]
}
```

**判定理由：** 公式前主干虽可对齐，但附带 where/给出矩阵的说明不再是原句；不能只审主干就给整句通过。

### P03-S07　存在非术语增删改

**当前完整句：**

```latex
Here, $c_1$ and $c_2$ are AFDM modulation parameters, and $T_s=1/(N\Delta f)$ gives the sampling interval.
```

**来源：** [ding2026.pdf](<D:/afdm-gfra/reference/literature/ding2026.pdf>)，PDF第2页；II，式(1)后独立参数句；式(3)后的采样间隔 where。

**核对原句：**

```text
$c_1$ and $c_2$ are AFDM modulation parameters.
```

**差异清单：**

```json
{
  "necessary_terminology": [],
  "other": [
    "在首个参数句前新增 Here,。",
    "把首个参数句末的句号改成逗号，并新增并列连接词 and。",
    "从另一处式(3)说明取出采样间隔从句，删除其原有引导词 where。",
    "把相隔的两处说明合并为一个完整句；原位置分别是式(1)后和信道式(3)后，中间经过矩阵式(2)及其解释与 TSL 引导句。"
  ],
  "display_only": [
    "c_1、c_2、T_s=1/(NΔf) 及 gives the sampling interval 本身与来源一致。"
  ]
}
```

**判定理由：** 两个局部文字可定位，完整句却新增 Here/and、删除 where 并跨句合并，连接关系已变。

### 段落组织

```json
{
  "same_original_paragraph": false,
  "source_sequence": [
    "S01：Shen II-B首句（删除spreading-based）",
    "S02：插入Cai II-A导频分配句",
    "S03：回到Shen II-B的Specifically句并重写where；Huang/Ding可定位部分术语",
    "S04-S05：本次未定位完整原句的本文条件",
    "S06：Ding II式(1)/(2)主句、定义及可能的Huang局部定义组合",
    "S07：Ding II式(1)后与式(3)后的分离说明合并"
  ],
  "omitted_source_bridge": {
    "file": "D:/afdm-gfra/reference/literature/shen2025.pdf",
    "page": 4,
    "section": "II-B首段、S01与Specifically句之间",
    "quote": "In this scheme, each device is assigned an unique spreading code and its transmitted data symbols are spread into Q consecutive frames during once transmission, where these frames are experienced OTFS modulation and demodulation independently, and are collected for further joint processing at the receiver.",
    "finding": "该整句未保留，被Cai的导频分配句替代；故即使Specifically词形仍在，它承接的上文已不同。源文 an unique、during once transmission 等语法按PDF保留。"
  },
  "order_and_connectors": "段内跨Shen→Cai→Shen→未定位新增条件→Ding/Huang，未保留单一原段顺序。Specifically原词保留但前接Cai句；with、given by、Here、并列and新增；一个来源where被去掉。",
  "attribution_risk": "风险是把本文的多帧纯导频安排、向量元素定义、固定能量与跨帧不同导频，以及重组后的DAFT说明，描述为某篇原文仅术语替换。Ding引用在IDAFT等式附近只能定位其相关变换表达，不能据此证明整个P03来自Ding或Shen同一原段。",
  "structure_verdict": "不是同一原段的术语替换式迁移；即便S02句级通过，段落组织仍不通过。"
}
```

## P04　CPP与帧时长

FAIL：4句中0句满足EXACT/TERM_ONLY；3句OTHER_CHANGE，1句NO_SOURCE；整段组织也不是同一原段原顺序。

原始证据：[P04.json](<D:/afdm-gfra/paper/checks/strict_sentence_audit_20261029/P04.json>)；精简对照：[P04.md](<D:/afdm-gfra/paper/checks/strict_sentence_audit_20261029/P04.md>)。

### P04-S01　存在非术语增删改

**当前完整句：**

```latex
Assume that the chirp-periodic prefix (CPP) duration satisfies $N_{\rm CPP}T_s\geq\max_{k,\ell}\tau_{k\ell}$.
```

**来源：** [cai2026.pdf](<D:/afdm-gfra/reference/literature/cai2026.pdf>)，PDF第4页；II-A系统模型，式(2)后、式(3)前的导频/CP段，印刷页3578。

**核对原句：**

```text
Assume that the cyclic prefix (CP) length exceeds the maximum channel delay spread.
```

**差异清单：**

```json
{
  "necessary_substitutions": [
    "cyclic prefix (CP) → chirp-periodic prefix (CPP)",
    "CP长度量与本文前缀时长/差分时延符号存在技术映射候选，但不可豁免谓语和条件改变。"
  ],
  "other_changes": [
    "length → duration",
    "exceeds → satisfies，谓语改变",
    "最大信道时延扩展改为关于全设备及路径差分时延最大值的完整不等式",
    "严格超过改为≥，允许相等，限定条件改变"
  ]
}
```

**判定理由：** 可定位Cai原句，但不是逐词只换术语：谓语、句内结构和边界条件均已改变。

### P04-S02　存在非术语增删改

**当前完整句：**

```latex
With the chirp periodicity, the prefix is \cite{bemani2022}
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

**来源：** [bemani2022.pdf](../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/strict_sentence_audit_20261029/sources/bemani2022.pdf)，PDF第8页；III-A Modulation，式(19)前导句及式(19)。

**来源定位/检索边界：** 式(19)紧前一句；原文指向式(15)的周期性定义，稿件删去该文字定位并添加chirp限定。为遵守该补查文献直引配额，原文短引仅置于P04.md，不在JSON重复。

**差异清单：**

```json
{
  "necessary_substitutions": [
    "s、n → 带帧/设备下标的s_{qk}、t",
    "源CPP长度符号 → N_CPP；虚数单位显示调整",
    "周期性添加chirp作为技术限定候选"
  ],
  "other_changes": [
    "删除源前导句中指向周期定义所在公式的语法成分，超出仅换公式编号",
    "式(19)的一次N+n偏移表达改为模N和平方差相位表达；公式本身非逐字审查对象，但新增where说明必须审查",
    "where新增取模的向下取整定义",
    "where新增2Nc1属于正整数的条件；源文有关整数条件的句子还包含N为偶数及CPP退化为CP的结论，并非稿件现句",
    "一般周期关系、普通CPP及后页参数说明被组合；本文长前缀和超过NT_s时延的使用范围不应当作源文原句"
  ]
}
```

**判定理由：** 前导句删除非术语文字，并在where从句增补定义与条件；可由公式推导不等于解释句逐字来源成立。

### P04-S03　本次未定位可对齐整句

**当前完整句：**

```latex
The prefix prevents inter-frame interference even when the differential delay exceeds $NT_s$.
```

**来源定位/检索边界：** 本次核查未定位可逐词对齐的完整原句。相关概念位置：Shen PDF第15页Appendix A式(65)后、式(66)前；Shen第4页II-B开头及Proposition 1；Bemani第9页III-B式(21)后、式(22)前。

**差异清单：**

```json
{
  "necessary_substitutions": [],
  "other_changes": [
    "无完整对齐原句，不能建立逐项术语替换表",
    "相对于相关概念说明，稿件以prefix为主语，使用prevents谓语，新增even when让步关系和超过NT_s的范围；属于本文长CPP说明"
  ]
}
```

**判定理由：** 相近术语和相关结论不能提供整句语言来源；本次核查未定位，不断言所有论文都不存在。

### P04-S04　存在非术语增删改

**当前完整句：**

```latex
$T_{\rm frame}=(N+N_{\rm CPP})T_s$ is the time duration of an AFDM frame with CPP.
```

**来源：** [shen2025.pdf](<D:/afdm-gfra/reference/literature/shen2025.pdf>)，PDF第4页；II-B Transmission Scheme，式(3)后完整where说明。

**核对原句：**

```text
where $T_{\rm cp}$ is the time duration of the cyclic prefix (CP), and $T_{\rm sym}=T+T_{\rm cp}$ is the time duration of a OFDM symbol with CP.
```

**来源定位/检索边界：** 已回看PDF，源确实为a OFDM；不是抽取错误。Huang第2页另有AFDM帧时长定义，但句型不同。

**差异清单：**

```json
{
  "necessary_substitutions": [
    "T_sym=T+T_cp → T_frame=(N+N_CPP)T_s",
    "OFDM symbol → AFDM frame",
    "CP → CPP"
  ],
  "other_changes": [
    "删除完整where句的前半CP时长定义及连接词and，将后半并列分句独立成句",
    "a → an；属于非技术词修改，按本轮最严格标准不得自动豁免"
  ]
}
```

**判定理由：** 可定位后半分句，但完整原句被删除、拆分并修改冠词，不是整句仅术语替换。

### 段落组织

```json
{
  "same_original_paragraph": false,
  "sequence_preserved": false,
  "connectives_preserved": false,
  "source_sequence": [
    "Cai CP覆盖假设框架",
    "Bemani CPP前导句及其他位置的周期/参数内容",
    "本文长CPP干扰说明",
    "Shen完整时长where句的后半分句"
  ],
  "finding": "跨文献、跨段落的改写拼接；没有确认一篇文献有相同整段和顺序。",
  "attribution_risk": "式(4)旁Bemani引用不能使本文模N长CPP表达、where中的附加限制及超过NT_s时延范围成为Bemani原句。"
}
```

## P05　信道矩阵及其定义

不通过最严格标准：10句中没有一句可确认EXACT或TERM_ONLY；3句能定位原句但超出术语替换，7句本次未定位可对齐整句。也不能确认本段来自同一原段。

原始证据：[P05.json](<D:/afdm-gfra/paper/checks/strict_sentence_audit_20261029/P05.json>)；精简对照：[P05.md](<D:/afdm-gfra/paper/checks/strict_sentence_audit_20261029/P05.md>)。

### P05-S01　存在非术语增删改

**当前完整句：**

```latex
After removing the CPP and applying the DAFT, let $H_k^{(q)}\in\mathbb C^{M\times N\times N}$ denote the effective channel of device $k$ in frame $q$, with $H_k=H_k^{(0)}$.
```

**来源：** [cai2026.pdf](<D:/afdm-gfra/reference/literature/cai2026.pdf>)，PDF第4页；II-A System Model，式(3)引出句；期刊页3578右栏。

**核对原句：**

```text
After removing the CP and applying the DFT, the received signal $\mathbf Y_t\in\mathbb C^{N\times M}$ during the $t$-th OFDM symbol is given by
```

**来源定位/检索边界：** 该引出句续接式(3)及 where 噪声定义；Cai v2 PDF第4页II-A式(3)措辞相同。Ding PDF第2页II节在式(4)前说移除CPP、式(5)前说DAFT，不能拼为当前整句。

**差异清单：**

```json
{
  "necessary_terminology_substitutions": [
    "CP → CPP",
    "DFT → DAFT"
  ],
  "other_changes": [
    "原主句“the received signal … during the t-th OFDM symbol is given by”改成“let … denote the effective channel of device k in frame q”。",
    "增加“with H_k=H_k^(0)”的基准帧定义。",
    "将原接收信号表达式引出句改成有效信道张量定义句；不只是符号或维度替换。"
  ]
}
```

**判定理由：** Cai的前置状语可直接定位，但主谓结构和说明目的已改写，完整句不能逐词对齐。

### P05-S02　存在非术语增删改

**当前完整句：**

```latex
To better capture the LEO channel dynamics, we incorporate fractional delay and fractional Doppler effects, and the resulting expression for the elements of $H_k$ is given as follows \cite{huang2026}: $H_{kmrn}=[\mathbf a_k]_m\sum_{\ell=1}^{L_k}g_{k\ell}[\mathbf G(\tau_{k\ell}/T_s,\nu_k;N_{\rm CPP})]_{rn}$.
```

**来源：** [huang2026.pdf](<D:/afdm-gfra/reference/literature/huang2026.pdf>)，PDF第2页；II System Model，式(5)前；期刊页2950右栏。

**核对原句：**

```text
To better capture the LEO channel dynamics, we incorporate fractional delay and fractional Doppler effects, and the resulting expression for the elements of the channel matrix $\mathbf H_i$ is given as follows
```

**来源定位/检索边界：** 原句续接单径矩阵元素式(5)，其后同一语法单元还以where定义equivalent delay、C及L_{m,q}；本文式(5)后以句号结束，没有保留该where说明。

**差异清单：**

```json
{
  "necessary_terminology_substitutions": [
    "原符号 H_i → 当前 H_k（作为拟议对象映射列出，不抵销其余删改）。"
  ],
  "other_changes": [
    "删除“the channel matrix”四个英文词，而非仅把H_i换为H_k。",
    "原公式之后where定义的附属解释没有保留；当前模型另以S03—S08解释。",
    "当前公式描述多路径、天线响应的设备信道；原式(5)为单径H_i的闭式元素公式。公式本体不按逐字同式计，但内容不可称为原式仅换符号。"
  ]
}
```

**判定理由：** 长段引导文字确有直接原句，但删去普通词组并重组附属说明，最严格标准下不是TERM_ONLY。

### P05-S03　本次未定位可对齐整句

**当前完整句：**

```latex
Here, $H_{kmrn}$ is the channel coefficient from transmitted DAFT-domain symbol $n$ to received DAFT-domain symbol $r$ at antenna $m$.
```

**来源定位/检索边界：** 本次核查未定位可对齐整句。核查Huang II第2页、Ding II第2页、Cai两版II-A第4页，并搜索全部7份clean.pages文本。Cai第4页的h_knm频响定义仅为相关概念对照，不能据此确认当前句来源。

**差异清单：**

```json
{
  "necessary_terminology_substitutions": [],
  "other_changes": [
    "没有可对齐整句，不能可靠列出原句逐词替换；当前句加入发送索引n、接收索引r及天线索引m的系数释义。"
  ]
}
```

**判定理由：** “channel coefficient”等术语和一般定义句式不构成含双DAFT符号索引的完整原句证据。

### P05-S04　本次未定位可对齐整句

**当前完整句：**

```latex
$\mathbf G(d,\nu;N_{\rm CPP})$ denotes the effective channel matrix of a path with gain $1$, normalized delay $d$, and Doppler shift $\nu$ in frame $0$.
```

**来源定位/检索边界：** 本次核查未定位可对齐整句。Huang第2页式(4)只定义H_eff；Ding第2页式(5)用Phi表示联合时延多普勒作用，未给出当前G、单位增益及frame 0整句。

**差异清单：**

```json
{
  "necessary_terminology_substitutions": [],
  "other_changes": [
    "无完整原句可建立替换表。",
    "当前单位增益、归一化时延d及第0帧限定是该G算子的本文定义，不能把整个定义短语视作一个可替换术语。"
  ]
}
```

**判定理由：** 原文的有效信道术语和路径参数不能覆盖本句全部限定条件及连接结构。

### P05-S05　本次未定位可对齐整句

**当前完整句：**

```latex
For the $N$ samples after CPP removal, starting at sample $g$, this matrix is given by $\mathbf G(d,\nu;g)=\mathbf F_{\rm A}\mathbf D_{\nu,g}\mathbf B_d,\quad\mathbf D_{\nu,g}=\diag\{e^{j2\pi\nu T_s(g+t)}\}_{t=0}^{N-1},\quad[\mathbf B_d]_{tn}=\varphi_n(t-d)$.
```

**来源定位/检索边界：** 本次核查未定位可对齐整句。Ding第2页式(4)—(5)的CPP/Doppler/cyclic-shift算子是相关数学结构，未出现当前“starting at sample g”采样起点说明。Bemani PDF第9页IV-B式(22)—(23)、第10页IV-C式(25)仅作公式结构对照，不摘录原文。

**差异清单：**

```json
{
  "necessary_terminology_substitutions": [],
  "other_changes": [
    "无可逐词对齐原句。",
    "当前g起始采样及G/D/B分解是本文模型陈述，不能因式中矩阵结构相似而豁免其说明句。"
  ]
}
```

**判定理由：** 现有文献的CPP移除和矩阵形式不构成这一含g及三个算子定义的完整句来源。

### P05-S06　本次未定位可对齐整句

**当前完整句：**

```latex
Here, $\varphi_n$ is the transmitted waveform when the $n$th DAFT-domain symbol equals $1$ and all other input symbols are zero, with the CPP defined in \eqref{eq:cpp}.
```

**来源定位/检索边界：** 本次核查未定位可对齐整句。搜索waveform、equals 1、all other、input symbols及相关变体，复核Huang/Ding第2页调制定义；Bemani第8页IV-A式(18)定义基函数，但没有当前单位符号激励+其余全零+CPP从句的整句。

**差异清单：**

```json
{
  "necessary_terminology_substitutions": [],
  "other_changes": [
    "无完整原句可建立术语替换表。",
    "单位输入、其余输入为零和with CPP从句是完整操作性定义，不能整块按“技术术语”豁免。"
  ]
}
```

**判定理由：** 公式中出现基函数不等于文中存在这一完整波形解释句。

### P05-S07　本次未定位可对齐整句

**当前完整句：**

```latex
Its expression and the derivation of \eqref{eq:path-operator-system} for fractional delays, including delays exceeding $NT_s$, are given in Appendix~\ref{app:afdm-model}.
```

**来源定位/检索边界：** 本次核查未定位可对齐整句。检索including delays/exceeding/derivation及相关短语，未找到这一指向本文附录并覆盖超过NT_s的分数时延推导句。Huang第2页式(5)不能替代该句的语言证据。

**差异清单：**

```json
{
  "necessary_terminology_substitutions": [],
  "other_changes": [
    "无完整来源句可对齐。",
    "“including delays exceeding NT_s”是实质模型范围，不是章节编号替换；指向本文附录也不自动构成原句。"
  ]
}
```

**判定理由：** 这是本文推导与适用范围的内部说明；不能以附录号可替换为由将整句视为合格。

### P05-S08　本次未定位可对齐整句

**当前完整句：**

```latex
For frame $0$, $g=N_{\rm CPP}$.
```

**来源定位/检索边界：** 本次核查未定位可对齐整句。核心文献无当前g起点与frame 0配对的此句；只在本文G(d,nu;g)定义中出现。

**差异清单：**

```json
{
  "necessary_terminology_substitutions": [],
  "other_changes": [
    "无完整来源句可对齐；本句设定当前模型的基准采样起点。"
  ]
}
```

**判定理由：** 简短等式说明仍在核查范围内，能够由模型推出不等于存在来源原句。

### P05-S09　存在非术语增删改

**当前完整句：**

```latex
In practical propagation environments, fractional Doppler shifts and fractional time delays can introduce significant power leakage in the effective channel matrix, thereby weakening its sparsity \cite{huang2026}.
```

**来源：** [huang2026.pdf](<D:/afdm-gfra/reference/literature/huang2026.pdf>)，PDF第2页；II System Model末段，式(5)后；期刊页2950右栏。

**核对原句：**

```text
In practical propagation environments, fractional Doppler shifts and fractional time delays can introduce significant power leakage in the effective channel matrix of (5), thereby weakening the sparsity of $\mathbf H_{\rm eff}$.
```

**差异清单：**

```json
{
  "necessary_terminology_substitutions": [],
  "other_changes": [
    "删除“of (5)”；即便宽免公式定位这一显示层变化，下一项仍构成普通措辞改写。",
    "把“the sparsity of H_eff”改为“its sparsity”，删去the和of，改变词序，并将显式对象改成代词。"
  ]
}
```

**判定理由：** 来源整句已确认，但“its sparsity”不是仅替换H_eff数学符号，最严格词序/词语标准不通过。

### P05-S10　本次未定位可对齐整句

**当前完整句：**

```latex
To address this issue, we retain the full $N\times N$ channel matrix at each antenna.
```

**来源定位/检索边界：** 本次核查未定位可对齐整句。Huang第2页II末段有相同通用起句，但其主句为develop a diffusion framework等，而不是retain the full N×N channel matrix at each antenna；共享通用引导语不确认整句来源。

**差异清单：**

```json
{
  "necessary_terminology_substitutions": [],
  "other_changes": [
    "没有支持当前完整句子的可对齐原句。",
    "若强行以Huang相邻句作来源，将需要把develop a diffusion framework改成retain the full N×N channel matrix at each antenna，并删除关系从句和enabling结果分句；这不是术语替换。"
  ]
}
```

**判定理由：** 原文有相邻的讨论语境和通用连接语，但未找到当前“保留每根天线完整矩阵”的完整句证据。

### 段落组织

```json
{
  "same_original_paragraph": false,
  "source_sequence": [
    "S01可定位Cai CP/DFT前置状语，主体为本文有效信道定义。",
    "S02来自Huang II式(5)引导语，存在删改。",
    "S03—S08为本次未找到整句来源的本文H/G/D/B/phi和长时延说明。",
    "S09回到Huang II后续另一个段落的泄漏句，存在改写。",
    "S10仅在Huang末段有通用连接语相同的上下文对照。"
  ],
  "order_and_connectives": "Huang的局部先后顺序（分数参数表达式→泄漏现象）仍可见，但本文在中间加入六个定义/推导说明句；Huang原文在泄漏句与To address之间还有Consequently引导的CS估计器退化句，当前未保留。因此不存在同一原段、同样顺序和全部连接关系的证据。",
  "attribution_risk": "Huang引用紧接本文式(5)的引出句，后续G/D/B/phi、g起点及超过NT_s范围是本文模型叙述，不能把Huang近原句的存在扩展为这些定义也有相同原句；Ding/Bemani类似矩阵结构也不能提供语言豁免。",
  "independent_formula_content": [
    "式(5)：设备k、多天线索引m与阵列响应乘多路径G之和。",
    "式(6)：带绝对起始样点g的D_nu,g、延迟采样B_d及单位激励phi_n。",
    "超过NT_s的时延范围、frame 0时g=N_CPP。"
  ]
}
```

## P06　跨帧相位关系

{'strict_pass': False, 'summary': '4个完整说明句均未达到 EXACT/TERM_ONLY：3句 OTHER_CHANGE、1句 NO_SOURCE；段落组织亦未保留。本结论只涉及语言一致性，不等于判定式(7)技术错误。', 'manuscript_modified': False}

原始证据：[P06.json](<D:/afdm-gfra/paper/checks/strict_sentence_audit_20261029/P06.json>)；精简对照：[P06.md](<D:/afdm-gfra/paper/checks/strict_sentence_audit_20261029/P06.md>)。

### P06-S01　存在非术语增删改

**当前完整句：**

```latex
Furthermore, the phase rotation $e^{j2\pi\nu_kqT_{\rm frame}}$ caused by the Doppler shift $\nu_k$ accumulates across multiple frames \cite{shen2025}.
```

**来源：** [shen2025.pdf](<D:/afdm-gfra/reference/literature/shen2025.pdf>)，PDF第5页；II-B, Transmission Scheme；左栏 Note that 开头跨页段的最后一句，在 smaller Q values 句后、To exploit the sparsity 段前。。

**核对原句：**

```text
Furthermore, the phase rotation φ_{u,q}[l′] caused by fractional Doppler accumulates across multiple frames and will be addressed carefully in our algorithm design.
```

**来源定位/检索边界：** sources/shen2025.clean.pages.txt:611-614；相关相位定义在原 PDF 第4页式(10)。

**差异清单：**

```json
{
  "necessary_term_substitutions": [
    {
      "source": "φ_{u,q}[l′]",
      "draft": "$e^{j2\\pi\\nu_kqT_{\\rm frame}}$",
      "status": "相位量名称/表达式的候选模型替换；原相位有路径/时延索引，现稿是设备共同标量，不能只凭名称确认机制相同。"
    }
  ],
  "other_changes": [
    {
      "type": "changed_qualification",
      "source": "fractional Doppler",
      "draft": "the Doppler shift $\\nu_k$",
      "detail": "增加 the、shift 和符号 ν_k，并把 fractional 限定改成本文共同 Doppler shift；不是仅更换符号。"
    },
    {
      "type": "deleted_coordinated_predicate",
      "source": "and will be addressed carefully in our algorithm design",
      "draft": "",
      "detail": "删去完整并列谓语及算法处理承诺，足以判定超过必要术语替换。"
    },
    {
      "type": "reordered_in_paragraph",
      "detail": "该 Furthermore 句原在近似不变、更多观测和 Q 增大限制之后；现被移到这些材料之前。"
    }
  ],
  "display_only": [
    "引用编号和数学排版差异不计实质修改。"
  ]
}
```

**判定理由：** 可定位完整来源句，但删除并列谓语并改变 fractional Doppler 的限定，不能判为 TERM_ONLY。

### P06-S02　本次未定位可对齐整句

**当前完整句：**

```latex
Since $\nu_k$ is common to all paths of device $k$, \eqref{eq:physical-channel} yields \begin{equation}\begin{gathered}H_k^{(q)}=e^{jq\beta_k}H_k,\\ \beta_k=\operatorname{wrap}(2\pi\nu_kT_{\rm frame}),\end{gathered}\label{eq:twc-frame-channel}\end{equation} where $\operatorname{wrap}(\cdot)$ maps an angle to $[-\pi,\pi)$.
```

**来源定位/检索边界：** 本次在所列七份核心/相关来源中未定位可对齐整句。Huang 有共同 Doppler 假设，Shen 有另一模型的相位分解，但均无当前完整 Since…yields + where wrap 句。

**差异清单：**

```json
{
  "necessary_term_substitutions": [],
  "other_changes": [
    {
      "type": "new_causal_sentence",
      "draft": "Since $\\nu_k$ is common to all paths of device $k$, \\eqref{eq:physical-channel} yields",
      "detail": "Since 因果关系和 yields 本文物理信道推导均为新增；相关 Huang 句没有此句法或推导谓语。技术上可推出也不等于来源原句。"
    },
    {
      "type": "rewritten_related_assumption",
      "source": "The resulting Doppler term D(ψ) is assumed to be common to all propagation paths within the same satellite-to-ground (S2G) link [15].",
      "draft": "Since ν_k is common to all paths of device k,",
      "detail": "就相关片段而言，删去 The resulting Doppler term、assumed to be、propagation，改写 within the same … link 为 of device k，并把陈述句改为原因从句；不能全部按术语豁免。"
    },
    {
      "type": "new_definition",
      "draft": "where $\\operatorname{wrap}(\\cdot)$ maps an angle to $[-\\pi,\\pi)$.",
      "detail": "本次核查未定位该定义句来源；它是本文选择的角度主值区间定义。"
    }
  ],
  "display_only": []
}
```

**判定理由：** 本次核查未定位可对齐完整原句；相关假设或相位公式不能替代 Since 推导和 wrap 定义的语言来源。

### P06-S03　存在非术语增删改

**当前完整句：**

```latex
After separating the inter-frame phase rotation in \eqref{eq:twc-frame-channel}, $H_k$ remains approximately constant over $Q$ consecutive frames.
```

**来源：** [shen2025.pdf](<D:/afdm-gfra/reference/literature/shen2025.pdf>)，PDF第4页；II-B, Transmission Scheme；右栏页末，式(10)后 Note that 开头原段内。。

**核对原句：**

```text
Fortunately, H^{DDS}_{n_z,n_y,u}[k′,l′,l] remains approximately constant over Q consecutive frames, benefited by the quasi-static property of (1) in the delay-Doppler domain.
```

**来源定位/检索边界：** sources/shen2025.clean.pages.txt:586-589。

**差异清单：**

```json
{
  "necessary_term_substitutions": [
    {
      "source": "H^{DDS}_{n_z,n_y,u}[k′,l′,l]",
      "draft": "H_k",
      "status": "信道对象/数学符号的候选替换；不能覆盖新操作条件。"
    }
  ],
  "other_changes": [
    {
      "type": "new_condition_and_connector",
      "source": "Fortunately,",
      "draft": "After separating the inter-frame phase rotation in (7),",
      "detail": "把评价性连接词改成操作先后/条件从句，新增相位分离操作和本文式(7)指引。"
    },
    {
      "type": "deleted_explanation",
      "source": ", benefited by the quasi-static property of (1) in the delay-Doppler domain",
      "draft": "",
      "detail": "删除原文近似不变的原因与 delay-Doppler domain 限定；整个从句不能当作术语替换。"
    }
  ],
  "display_only": [
    "Q 的数学排版差异。"
  ]
}
```

**判定理由：** 保留主干 remains approximately constant over Q consecutive frames，但新增 After 操作条件、删去原原因限定，超过 TERM_ONLY。

### P06-S04　存在非术语增删改

**当前完整句：**

```latex
This characteristic allows the proposed scheme to gather more observations, thereby facilitating channel estimation without increasing the number of channel coefficients to be estimated.
```

**来源：** [shen2025.pdf](<D:/afdm-gfra/reference/literature/shen2025.pdf>)，PDF第[4, 5]页；II-B, Transmission Scheme；第4页右栏最后 This characteristic 与第5页左栏开头构成完整跨页句。。

**核对原句：**

```text
This characteristic allows the proposed scheme to gather more observations, thereby facilitating the joint design of channel estimation and symbol detection.
```

**来源定位/检索边界：** sources/shen2025.clean.pages.txt:589-594。

**差异清单：**

```json
{
  "necessary_term_substitutions": [],
  "other_changes": [
    {
      "type": "deleted_object_components",
      "source": "the joint design of channel estimation and symbol detection",
      "draft": "channel estimation",
      "detail": "删除 the joint design of 和 and symbol detection；将联合设计目标缩成信道估计，不是术语等位替换。"
    },
    {
      "type": "added_inference",
      "source": "",
      "draft": "without increasing the number of channel coefficients to be estimated",
      "detail": "新增待估信道系数数量不增的结论。既不在已定位原句中，本次检索也未定位可对齐来源；不能因为共享 H_k 可推得就放行。"
    }
  ],
  "display_only": []
}
```

**判定理由：** 前半句一致，但后半句同时删去原目标成分并加入 without 新结论，属于改写。

### 段落组织

```json
{
  "same_original_paragraph": false,
  "source_paragraph_finding": "S01、S03、S04 的相关完整原句均来自 Shen 同一个原段（第4页式(10)后 Note that 开始，至第5页左栏 algorithm design 结束），但当前 P06 并非保持该原段的术语替换版。",
  "source_order": [
    "单帧关系、三维信道与估计/检测困难。",
    "Fortunately 近似不变（现 S03 来源）。",
    "This characteristic 更多观测/联合估计检测（现 S04 来源）。",
    "In practice 大量帧会破坏准静态；Q=8、25 数值例及较小 Q 建议。",
    "Furthermore fractional Doppler 相位积累与算法处理承诺（现 S01 来源）。"
  ],
  "draft_order": [
    "Furthermore 相位积累。",
    "新增 Since 共同 Doppler → 本文式(7) → where wrap。",
    "After 相位分离 → 近似不变。",
    "This characteristic → 更多观测/估计且系数数目不增。"
  ],
  "reordered": true,
  "connectors_preserved": false,
  "spliced_material": [
    "把 Shen 原段末尾相位句前移到近似不变/更多观测两句之前。",
    "插入本文共同 Doppler 推导、式(7)、wrap；假设有 Huang 相关来源，但完整 Since 句不是 Huang 原句。",
    "删去 Shen 对过多帧破坏准静态的说明及数值例，未保留原段限制条件和 Furthermore 的局部承接。"
  ],
  "attribution_risk": "段首 cite{shen2025} 不能把共路径标量式(7)、wrap、After 相位分离条件或 without 系数数量结论变成 Shen 原句。",
  "decision": "段落组织不通过：同一原段的材料经过重排、删节和本文模型插入，不能称为原段仅换必要术语。"
}
```

## P07　活动与接收观测模型

不通过最严格标准。10个完整说明句仅2句TERM_ONLY；5句存在可定位原句的实质增删改，3句本次未定位可对齐整句；整段并非同一来源原段。未修改稿件。

原始证据：[P07.json](<D:/afdm-gfra/paper/checks/strict_sentence_audit_20261029/P07.json>)；精简对照：[P07.md](<D:/afdm-gfra/paper/checks/strict_sentence_audit_20261029/P07.md>)。

### P07-S01　存在非术语增删改

**当前完整句：**

```latex
We use an indicator function $\alpha_k\in\{0,1\}$ to model the device activity, where $\alpha_k=1$ if the $k$th device is active, and $\alpha_k=0$ otherwise.
```

**来源：** [cai2026.pdf](<D:/afdm-gfra/reference/literature/cai2026.pdf>)，PDF第4页；II-A，式(1)引导句及分段定义；期刊印刷页3578。

**核对原句：**

```text
We use an indicator function $\alpha_k$ to model the device activity as $\alpha_k=\begin{cases}1,&\text{if the }k\text{-th device is active},\\0,&\text{otherwise}.\end{cases}$
```

**差异清单：**

```json
{
  "necessary_substitutions": [],
  "other_changes": [
    "在indicator function后的符号上增加显式取值域α_k∈{0,1}。",
    "将原句的“activity as [分段定义]”改成“activity, where α_k=1 if …, and α_k=0 otherwise”。这里新增where、and并改写条件与等式的连接方式，超出单纯显示公式从块排改为行内的排版变化。"
  ],
  "display_only": [
    "k-th与TeX中的$k$th排版归一。",
    "原文分段函数用TeX重排以便核对。"
  ]
}
```

**判定理由：** 开头主干能定位到Cai，但完整句的连接词和定义表达经过改写，不能把公式内联及新增连接词统称为术语替换。

### P07-S02　存在非术语增删改

**当前完整句：**

```latex
Let $\rho$ represent the probability of a device being active, i.e., $\Pr(\alpha_k=1)=\rho$.
```

**来源：** [cai2026.pdf](<D:/afdm-gfra/reference/literature/cai2026.pdf>)，PDF第4页；II-A，式(1)后。

**核对原句：**

```text
Let $\lambda$ represent the probability of a device being active, i.e., $p(\alpha_k=1)=\lambda$, where $\lambda\ll1$.
```

**差异清单：**

```json
{
  "necessary_substitutions": [
    "λ→ρ（设备活动概率符号）。",
    "p(α_k=1)→Pr(α_k=1)（概率记号）。"
  ],
  "other_changes": [
    "删除原句末尾完整限定从句“where λ≪1”。"
  ],
  "display_only": []
}
```

**判定理由：** 保留了前半句，但删除稀疏活动概率的限定条件；完整原句不是仅术语/符号替换。

### P07-S03　本次未定位可对齐整句

**当前完整句：**

```latex
Each device maintains its activity state throughout a transmission block.
```

**来源定位/检索边界：** 本次核查未定位可逐词对齐的完整句。检索Cai期刊版/v2 II-A、Shen II-C及Ding、Huang核心文本，并以activity/state/maintains/throughout/transmission block等组合检索全部clean.pages.txt；Cai PDF p.4仅有“任一传输块中小部分设备活跃”的不同句，Shen/Ding的activity state为术语级关联。

**差异清单：**

```json
{
  "necessary_substitutions": [],
  "other_changes": [
    "新增明确要求整个传输块内活动状态不变的独立说明句；未定位其整句来源。"
  ],
  "display_only": []
}
```

**判定理由：** 块活动建模可以解释这项假设，但技术合理性或可从模型推断不能作为整句语言来源。

### P07-S04　仅必要术语或符号替换

**当前完整句：**

```latex
Let $X_k=\alpha_kH_k$.
```

**来源：** [cai2026.pdf](<D:/afdm-gfra/reference/literature/cai2026.pdf>)，PDF第4页；II-A，式(3)后的噪声定义句之后。

**核对原句：**

```text
Let $\mathbf X_k\triangleq\alpha_k\mathbf H_k$.
```

**差异清单：**

```json
{
  "necessary_substitutions": [
    "原文矩阵符号\\mathbf X_k、\\mathbf H_k→本文对应张量符号X_k、H_k。",
    "定义等号△=→=；Let结构仍明确这是定义，属于数学记号的替换。"
  ],
  "other_changes": [],
  "display_only": []
}
```

**判定理由：** 完整独立句只有Let及对应定义式，词语、词序和连接关系保留；变化均在对应对象的数学记号内。

### P07-S05　存在非术语增删改

**当前完整句：**

```latex
According to the superposition principle, the $q$th received frame in the DAFT domain is given by
\begin{equation}
 Y_{qmr}=\sum_{k=1}^K\sum_{n=0}^{N-1}A_{qkn}X_{kmrn}+W_{qmr},
 \label{eq:observation-tensor}
\end{equation}
where $W_{qmr}$ are i.i.d.\ drawn from $\CN(0,\sigma^2)$, and
\begin{equation}
 A_{qkn}=P_{qkn}e^{jq\beta_k}
 \label{eq:effective-pilot}
\end{equation}
is the pilot symbol multiplied by the phase rotation in \eqref{eq:twc-frame-channel}.
```

**来源：** [shen2025.pdf](<D:/afdm-gfra/reference/literature/shen2025.pdf>)，PDF第5页；II-C，式(13)及其where从句（左栏末至右栏首）。

**核对原句：**

```text
According to the superposition principle, the $q$-th received frame in the delay-Doppler-angle domain is given by
$Y^{\mathrm{DDA}}_{a_z,a_y,q}[k,l]=\sum_{u=0}^{U-1}\lambda_uY^{\mathrm{DDA},q}_{a_z,a_y,u}[k,l]+Z^{\mathrm{DDA}}_{a_z,a_y,q}[k,l]$,
where $\lambda_u\in\{0,1\}$ is the activity indicator of the $u$-th device and $Z^{\mathrm{DDA}}_{a_z,a_y,q}[k,l]\sim\mathcal{CN}(0,\sigma^2)$ is the noise.
```

**差异清单：**

```json
{
  "necessary_substitutions": [
    "delay-Doppler-angle domain→DAFT domain（仅引导主句内部的技术域替换）。",
    "接收量、噪声及设备符号依本文模型改名/改索引；显示公式本体不以逐字同式作为要求。"
  ],
  "other_changes": [
    "原where从句先定义λ_u活动指示，再定义Z为噪声；当前删除活动指示定义，将噪声改写成W are i.i.d. drawn from CN(...)。",
    "新增and引导的A_{qkn}独立对象定义及“is the pilot symbol multiplied by the phase rotation in ...”说明。",
    "当前噪声措辞与Cai式(3)后的i.i.d. drawn from相近，但原Cai完整从句还包含AWGN matrix with the elements；将其压缩后接入Shen句式属于拼接与改写。"
  ],
  "display_only": [
    "q-th与$q$th等TeX排版归一。"
  ]
}
```

**判定理由：** 只能认定Shen主句相似（域名称替换）；当前完整语法句还含两个公式及where/and/A解释，新增删除内容不能作长术语豁免。

### P07-S06　存在非术语增删改

**当前完整句：**

```latex
Next, we collect the $Q$ received frames into a single matrix as
\begin{equation}
 \mathbf Y=\mathbf A\mathbf X+\mathbf W,
 \label{eq:mmv}
\end{equation}
where $\mathbf Y,\mathbf W\in\mathbb C^{Q\times MN}$,
$\mathbf A\in\mathbb C^{Q\times KN}$ has entries
$[\mathbf A]_{q,(k-1)N+n}=A_{qkn}$, and
$\mathbf X\in\mathbb C^{KN\times MN}$ is defined together with $\mathbf Y$ by
\begin{equation}
 \begin{aligned}
 [\mathbf Y]_{q,mN+r}&=Y_{qmr},\\
 [\mathbf X]_{(k-1)N+n,mN+r}&=X_{kmrn}.
 \end{aligned}
 \label{eq:mmv-indexing}
\end{equation}
```

**来源：** [shen2025.pdf](<D:/afdm-gfra/reference/literature/shen2025.pdf>)，PDF第5页；II-C，式(15)及where从句。

**核对原句：**

```text
Next, we collect the $Q$ received frames into a single matrix as
$\mathbf Y^l=\mathbf C^{\phi,l}(\mathbf T^l\otimes\mathbf I_N)\mathbf H^l+\mathbf Z^l$,
where $\mathbf Y^l=[(\mathbf Y_0^l)^{\mathsf T},\ldots,(\mathbf Y_{Q-1}^l)^{\mathsf T}]^{\mathsf T}$,
$\mathbf H^l=(\mathbf\Lambda\otimes\mathbf I_{MN})\widetilde{\mathbf H}^l$,
$\mathbf C^{\phi,l}=[(\mathbf C_0^l(\mathbf\Phi_0\otimes\mathbf I_N))^{\mathsf T},\ldots,(\mathbf C_{Q-1}^l(\mathbf\Phi_{Q-1}\otimes\mathbf I_N))^{\mathsf T}]^{\mathsf T}$.
```

**差异清单：**

```json
{
  "necessary_substitutions": [
    "主句中Q帧/矩阵指代沿用；各数学对象依本文DAFT观测替换。"
  ],
  "other_changes": [
    "原where依次给Y^l纵向堆叠、H^l活动加权、C^{φ,l}纵向堆叠；当前改成Y/W维数、A维数及逐项索引、X与Y联合定义。",
    "新增完整谓语结构“has entries”与“is defined together with ... by”。",
    "新增and并更换定义顺序和逻辑关系；这不是只替换矩阵名称/维度。",
    "当前式(11)引入mN+r及(k−1)N+n索引规则，不能用原文堆叠公式自动证明说明句相同。"
  ],
  "display_only": []
}
```

**判定理由：** Next引导主句逐词一致，但完整句所带where从句重写；原句的三个直接数学定义不能对齐成当前新增的两个英文谓语。

### P07-S07　本次未定位可对齐整句

**当前完整句：**

```latex
The column index is $mN+r$, and each device occupies $N$ rows indexed by its transmitted symbol $n$.
```

**来源定位/检索边界：** 本次核查未定位可逐词对齐的完整句。重点比较Shen PDF p.5 II-C式(14)的(k,a_z+N_z a_y)及(uMN+l′N+k′,a_z+N_z a_y)逐元素定位、Cai PDF p.4 II-A式(4)的按设备堆叠；Ding PDF p.2 III-A式(7)后也有column index，但定义的是导频子矩阵选取区间，不是本句。

**差异清单：**

```json
{
  "necessary_substitutions": [],
  "other_changes": [
    "新增对本文mN+r列编号与每设备N行的说明；未定位整句来源。"
  ],
  "display_only": []
}
```

**判定理由：** 不同文献确有矩阵索引概念，但本文句型、and连接及设备/发射符号的行占用说明没有整句对应。

### P07-S08　本次未定位可对齐整句

**当前完整句：**

```latex
Let $\mathbf P\in\mathbb C^{Q\times KN}$ denote the pilot matrix, with entries $[\mathbf P]_{q,(k-1)N+n}=P_{qkn}$.
```

**来源定位/检索边界：** 本次核查未定位完整原句。比较Cai PDF p.4 II-A的“构造对角导频矩阵Q_kt”与Q=[Q_1,...,Q_K]定义，Shen PDF p.5 II-C的C_q^l/C^{φ,l}矩阵定义，以及Huang PDF p.3 III-A式(6)后pilot matrix定义；这些仅提供导频矩阵术语或不同数学定义，不覆盖当前完整句。

**差异清单：**

```json
{
  "necessary_substitutions": [],
  "other_changes": [
    "本文新增P∈C^{Q×KN}的统一命名和逐项索引说明；未定位相同Let ... denote ... with entries整句。"
  ],
  "display_only": []
}
```

**判定理由：** “Let ... denote”是通用定义模板；不能将大段对象定义当成一个术语替换，或将pilot matrix词组的来源当成整句出处。

### P07-S09　存在非术语增删改

**当前完整句：**

```latex
For simplicity, we impose the condition that $\mathbf P$ is partial orthogonal, specifically requiring that $\mathbf P\mathbf P^{\mathsf H}=KE_p\I_Q$.
```

**来源：** [cai2026.pdf](<D:/afdm-gfra/reference/literature/cai2026.pdf>)，PDF第4页；II-A，式(4)后的正交条件句。

**核对原句：**

```text
For simplicity, we impose the condition that $\mathbf Q$ is partial orthogonal, specifically requiring that $\mathbf Q\mathbf Q^{\mathsf H}=KP\mathbf I_{NT}$, where each device has the same transmit power budget $P$.
```

**差异清单：**

```json
{
  "necessary_substitutions": [
    "导频矩阵\\mathbf Q→\\mathbf P。",
    "归一化标量P→E_p、单位阵维数NT→Q，按本文符号/维度对应记录；本审查不以公式的物理等价性作语言通过依据。"
  ],
  "other_changes": [
    "删除句末整个“where each device has the same transmit power budget P”限定从句。"
  ],
  "display_only": []
}
```

**判定理由：** For simplicity到正交公式的主干确实复用，但删除了完整where从句，严格标准下不是仅术语替换。

### P07-S10　仅必要术语或符号替换

**当前完整句：**

```latex
The design of partial orthogonal $\mathbf P$ is deferred to Section~\ref{sec:simulation-settings}.
```

**来源：** [cai2026.pdf](<D:/afdm-gfra/reference/literature/cai2026.pdf>)，PDF第4页；II-A，正交条件句之后。

**核对原句：**

```text
The design of partial orthogonal $\mathbf Q$ is deferred to Section V-C.
```

**差异清单：**

```json
{
  "necessary_substitutions": [
    "导频矩阵符号\\mathbf Q→\\mathbf P。"
  ],
  "other_changes": [],
  "display_only": [
    "Section V-C→Section~\\ref{sec:simulation-settings}，按协议属于章节号/交叉引用差异。"
  ]
}
```

**判定理由：** 完整句保留原词语、词序及连接关系，仅对应矩阵符号与章节交叉引用改变。

### 段落组织

```json
{
  "same_original_paragraph": false,
  "source_sequence": "Cai II-A活动建模段（S01–S02）→本文活动持续说明（S03）→Cai式(3)后独立定义句提前（S04）→Shen II-C式(13)主句加改写/本文A定义（S05）→Shen式(15)主句加本文矩阵与索引说明（S06）→本文索引/P定义（S07–S08）→Cai式(4)后正交假设与设计指向（S09–S10）。",
  "reordering_and_connectors": [
    "Cai的Let X_k≜α_kH_k原在接收信号式(3)与噪声说明之后；当前移到观测式(8)之前。",
    "Shen的Next原先紧接式(14)逐帧矩阵形式与多个矩阵定义；当前Next紧接式(8)–(9)标量观测/有效导频定义，中间承接内容不同。",
    "S01的as被where/and重新组织；S02/S09各删去一个where从句；S05/S06仅保留引导主干而更换公式后解释。"
  ],
  "model_attribution_risk": "式(8)–(11)的DAFT多用户双和、A_{qkn}=P_{qkn}e^{jqβ_k}、Q×MN展平方式及(mN+r,(k−1)N+n)索引是本文具体模型内容。引用Shen叠加/多帧堆叠的引导句或Cai线性模型，不足以把这些完整解释句归为他文原句。",
  "organization_conclusion": "跨文献、跨原段选择并重排，夹入本文定义；即便两句单句TERM_ONLY，也不能认定整段为同一原段仅替换术语。"
}
```

## P08　块稀疏性与块内相关性

P08不通过最严格整段标准：1句EXACT、1句TERM_ONLY、1句NO_SOURCE。前两句有明确连续出处；最后关于common path parameters and array response的完整句子本次核查未定位。整段组织也不是Cai原段原样保留。

原始证据：[P08.json](<D:/afdm-gfra/paper/checks/strict_sentence_audit_20261029/P08.json>)；精简对照：[P08.md](<D:/afdm-gfra/paper/checks/strict_sentence_audit_20261029/P08.md>)。

### P08-S01　原句一致

**当前完整句：**

```latex
Due to the sporadic access of the devices, matrix $\mathbf X$ exhibits a block-sparsity structure.
```

**来源：** [cai2026.pdf](<D:/afdm-gfra/reference/literature/cai2026.pdf>)，PDF第4页；II-A System Model，式(4)后的where段，右栏末部。

**核对原句：**

```text
Due to the sporadic access of the devices, matrix X exhibits a block-sparsity structure.
```

**差异清单：**

```json
{
  "necessary_term_or_symbol_substitutions": [],
  "other_additions": [],
  "other_deletions": [],
  "other_rephrasings": [],
  "display_only": [
    "TeX数学字体、空格及断行"
  ]
}
```

**判定理由：** 整句逐词对齐，Due to、the、of、matrix、exhibits和block-sparsity structure均保持原词序。

### P08-S02　仅必要术语或符号替换

**当前完整句：**

```latex
Specifically, if the $k$th device is inactive, we have $X_k=\alpha_kH_k=\mathbf 0$ \cite{cai2026}.
```

**来源：** [cai2026.pdf](<D:/afdm-gfra/reference/literature/cai2026.pdf>)，PDF第4页；II-A System Model，式(4)后的where段，紧接P08-S01对应原句。

**核对原句：**

```text
Specifically, if the k-th device is inactive, we have X_k = α_k H_k = 0.
```

**差异清单：**

```json
{
  "necessary_term_or_symbol_substitutions": [
    {
      "from": "原文粗体矩阵\\mathbf X_k",
      "to": "本文张量/设备块X_k",
      "why": "对应本文X_k=α_kH_k及其展开后的设备块定义，保留同一零活动条件。"
    },
    {
      "from": "原文粗体N×M信道矩阵\\mathbf H_k",
      "to": "本文M×N×N有效信道H_k",
      "why": "将原OFDM矩阵对象映射到本文AFDM信道对象；这属于显式数学对象/符号替换，故保守归为TERM_ONLY。"
    }
  ],
  "other_additions": [],
  "other_deletions": [],
  "other_rephrasings": [],
  "display_only": [
    "k-th → $k$th：序数连字符的排版/拼写样式，不改变词义或句法；如要求字面连字符也完全保留，可恢复k-th。",
    "稿件增加\\cite{cai2026}引用标记，属于协议允许的引用显示差异。",
    "等式内空格和TeX数学表示变化；等号、α_k、零值关系保持。"
  ]
}
```

**判定理由：** 有可完整对齐的原句，Specifically, if…is inactive, we have…的词语、词序、条件关系均不变；仅把信道及活动信道数学对象映射到本文定义。

### P08-S03　本次未定位可对齐整句

**当前完整句：**

```latex
The channel coefficients within each active block are statistically dependent through the common path parameters and array response in \eqref{eq:channel}.
```

**来源定位/检索边界：** 本次核查未定位可对齐整句。已检索Shen、Cai期刊版、Cai v2、Ding、Huang、Li、Bemani全部clean.pages.txt；并回看Cai两版PDF第4页II-A对应原段。Cai该处在前两句后实际接Table I符号汇总句，未接本句。

**差异清单：**

```json
{
  "necessary_term_or_symbol_substitutions": [],
  "other_additions": [
    "相对于已确认的Cai块稀疏两句，整句新增：活动块内部系数的统计依赖，以及依赖来自共同路径参数和阵列响应的解释。",
    "加入对本文eq:channel的引用，把本文模型的结构解释接到Cai原句之后。"
  ],
  "other_deletions": [],
  "other_rephrasings": [],
  "alignment_limit": "没有找到对齐原句，不能声称已列出相对于某原句的精确编辑距离；以上新增描述仅指它相对于已核实的Cai段落所起的增补作用。"
}
```

**判定理由：** 必须检查整句；即使共同路径参数与阵列响应可为本文提供技术解释，也不构成可逐词对齐的来源，更不能把整个原因短语当作术语替换。

### 段落组织

```json
{
  "same_original_paragraph_in_full": false,
  "first_two_from_same_original_paragraph": true,
  "original_location": "Cai两版本PDF第4页II-A，式(4)后的where段末；原段从矩阵定义延续到部分正交条件、设计章节指引、块稀疏两句，最后是Table I汇总句。",
  "order_and_connectors": "P08-S01→S02与原文相邻顺序一致；Due to和Specifically, if保持。P08-S03没有可核实的原句顺序或连接关系可保留。",
  "boundary_change": "当前稿件在Due to前另起P08；该处在两版原PDF中没有另起段落，而是式(4)后的同一where段中部。",
  "omissions_and_additions": "原段末的Table I汇总句未采用；加入本文共同路径参数/阵列响应解释句。没有证据把第三句认定为拼接自另一篇论文，故只判已确认原句与本次未定位句的组合。",
  "attribution_risk": "引用cai2026放在S02末可支持前两句；若把整个P08报告为Cai原段仅换术语，会将S03关于本文eq:channel的依赖机制错误归于Cai。",
  "structure_verdict": "不是同一原段的整体逐句保留。"
}
```

## P09　JADCE任务总述

不通过最严格的整段标准：S01为EXACT，S02为NO_SOURCE；且P09整体不对应同一原文段落。该结果是语言来源判定，不是模型错误判定。

原始证据：[P09.json](<D:/afdm-gfra/paper/checks/strict_sentence_audit_20261029/P09.json>)；精简对照：[P09.md](<D:/afdm-gfra/paper/checks/strict_sentence_audit_20261029/P09.md>)。

### P09-S01　原句一致

**当前完整句：**

```latex
In this paper, we aim to simultaneously detect the active devices and estimate the corresponding channels based on the observation $\mathbf Y$ under a Bayesian inference framework \cite{cai2026}.
```

**来源：** [cai2026.pdf](<D:/afdm-gfra/reference/literature/cai2026.pdf>)，PDF第4页；II-B. Problem Statement，首段第一句；期刊印刷页3578。。

**核对原句：**

```text
In this paper, we aim to simultaneously detect the active devices and estimate the corresponding channels based on the observation Y under a Bayesian inference framework.
```

**差异清单：**

```json
{
  "necessary_term_substitutions": [],
  "other_changes": [],
  "display_only_changes": [
    "PDF中的粗体数学符号Y以TeX $\\mathbf Y$书写。",
    "换行和空格规范化。",
    "句末增加本文引用\\cite{cai2026}，属于协议明确允许的引用显示层差异。"
  ]
}
```

**判定理由：** 两个版本的完整句子均可逐词一一对齐；除协议允许的排版和引用显示差异外，没有术语、谓语、连接词或词序改动。

### P09-S02　本次未定位可对齐整句

**当前完整句：**

```latex
We consider $Q<KN$ in \eqref{eq:mmv}.
```

**来源定位/检索边界：** 本次核查未定位可与该整句逐词对齐的来源。已全文检索7份clean.pages.txt，并直接复核蔡文两个版本第4页II-A式(4)及II-B首段。

**差异清单：**

```json
{
  "necessary_term_substitutions": [],
  "other_changes": [
    "相对于已定位的蔡文II-B原段，本文在任务总述后新增整句“We consider Q<KN in (本文MMV公式).”；原文对应位置紧接精确贝叶斯估计器难以计算的说明。"
  ],
  "display_only_changes": [
    "\\eqref{eq:mmv}为本文公式引用，显示形式本身不构成来源证据。"
  ]
}
```

**判定理由：** 本次核查未定位完整原句；‘We consider’是通用句型，Q<KN可以是本文设定，但这些均不足以判为EXACT或TERM_ONLY。

### 段落组织

```json
{
  "same_original_paragraph": false,
  "original_structure": "蔡文两个版本II-B首段均为任务总述句，随后在同一原段解释Exact Bayesian estimators一般难以计算。下一原段才由Alternatively引出消息传递。",
  "draft_structure": "当前P09保留蔡文首段第一句，然后添加Q<KN条件句。",
  "sentence_order": "已借用的第一句自身词序完整保留；两句整体并非蔡文原段的连续顺序。",
  "connective_preservation": "S01内部and、based on、under等连接关系完整保留；S02无可对齐原句或原段连接关系。",
  "cross_source_splicing": "未确认S02来自另一文献，因此不能断言两篇原文拼接；可确认是一个完整来源句与一个本次未定位来源句的组合。",
  "attribution_risk": "不能用S01句末cai2026的引用把S02条件及本文AFDM观测模型一并归于蔡文。",
  "paragraph_pass": false
}
```

## P10　已知量与先验假设

不通过最严格“只有必要术语替换，其余词语/句式/连接词不变”标准。4句中0句可判EXACT/TERM_ONLY，1句OTHER_CHANGE，3句本次核查未定位可对齐整句。正文未改。

原始证据：[P10.json](<D:/afdm-gfra/paper/checks/strict_sentence_audit_20261029/P10.json>)；精简对照：[P10.md](<D:/afdm-gfra/paper/checks/strict_sentence_audit_20261029/P10.md>)。

### P10-S01　存在非术语增删改

**当前完整句：**

```latex
In this subsection, we assume that the estimates $\widehat{\mathbf A}$ and $\widehat\sigma^2$ are known, which are obtained from $\mathbf Y$ as described in Section~\ref{sec:frontend}.
```

**来源：** [shen2025.pdf](<D:/afdm-gfra/reference/literature/shen2025.pdf>)，PDF第7页；III-B. Message Scheduling，首句。

**核对原句：**

```text
In this subsection, we assume that the phase rotation caused by fractional Doppler, the noise variance, and the parameters of BGM are known, which will be updated later.
```

**差异清单：**

```json
{
  "necessary_term_substitutions": [
    {
      "from": "the noise variance",
      "to": "$\\widehat\\sigma^2$",
      "qualification": "可识别的噪声方差名称至估计符号对应；仅此局部对应不能使整句成为TERM_ONLY。"
    }
  ],
  "other_changes": [
    "把已知量的三项列举（phase rotation caused by fractional Doppler / noise variance / parameters of BGM）改成 the estimates Ahat and sigmahat^2 的两项估计量列举，加入 estimates 并删去 BGM 参数；不是逐项保留的对象名称替换。",
    "phase rotation caused by fractional Doppler 至 Ahat 的对应不是直接同一对象换符号：本稿将有效导频矩阵估计放入该位置，不能把整个名词列表视为一个术语。",
    "which will be updated later 改为 which are obtained from Y：will be updated 的将来更新机制改为 are obtained 的观测获取机制，并删除 later。",
    "新增 from Y 和 as described in Section~ref{sec:frontend}；这是一整段新增来源/流程说明，不是单纯章节号显示差异。"
  ],
  "retained_frame": "In this subsection, we assume that the ... are known, which ... 保留了框架，但关系从句的谓语、时间和操作含义均改变。"
}
```

**判定理由：** 可明确定位 Shen 原句，但存在列表删改、谓语与估计机制改写及新增解释，超过必要术语替换。

### P10-S02　本次未定位可对齐整句

**当前完整句：**

```latex
Let $q_{\rm tr}$ denote the prior distribution of $H_k$ represented by the channel samples used for training.
```

**来源定位/检索边界：** 本次核查未定位可逐词对齐整句。最相关概念见 Cai期刊版及v2 PDF第8页 IV-A末段（合并训练集）和 IV-B首句（p(H)为总K个设备信道的混合分布）；参见E2/E3。

**差异清单：**

```json
{
  "necessary_term_substitutions": [],
  "other_changes": [
    "未找到可作为完整原句的来源，故不能批准 p(H)→q_tr 为足以通过的单一符号替换。",
    "相对E3：With a slight abuse of notation, let ... be ... 改成 Let ... denote ...；删除 mixture、total K devices 和函数域/值域描述；新增 represented by the channel samples used for training。",
    "E2描述将不同设备的训练样本合成一个训练集；本句将训练样本与先验定义合为一句，原文E2没有该句型或 q_tr 定义。上述为相关段落比较，不能冒称已找到直接改写原句。"
  ]
}
```

**判定理由：** Cai的训练样本与混合分布概念有关，但本次未找到保留本句句式、词序与连接关系的完整原句。

### P10-S03　本次未定位可对齐整句

**当前完整句：**

```latex
For inference, we assume independence across devices and between each device's activity and channel.
```

**来源定位/检索边界：** 本次核查未定位可逐词对齐整句。相关模型证据为 Cai期刊版及v2 PDF第4页 II-B式(5)，其引导句仅概称 conditional independence relationships；设备活动的i.i.d.描述位于II-A跨第3–4页，均非本句。

**差异清单：**

```json
{
  "necessary_term_substitutions": [],
  "other_changes": [
    "本次未定位含 For inference, we assume independence across devices and between each device's activity and channel 的完整原句。",
    "Cai式(5)按设备相乘并分别使用p(H_k)、p(alpha_k)，属于相关先验分解；公式所表达的假设不能充当本句英文原句。",
    "Cai式(5)引导句使用 In message passing, we factorize ... according to ... and ... expressed as，主语后的谓语及组织均不同；跨设备/每设备活动与信道两个明确独立性范围是本句自行写出的说明，不能视作数学符号更换。"
  ]
}
```

**判定理由：** 能够找到相关因子分解，但概念或公式一致不等于找到本句可逐词对齐的文字来源。

### P10-S04　本次未定位可对齐整句

**当前完整句：**

```latex
The activities follow Bernoulli priors, while $q_{\rm tr}(H_k)$ retains the dependence among the coefficients within $H_k$.
```

**来源定位/检索边界：** 本次核查未定位由 while 连接这两个分句的完整原句。相关概念分散于 Cai期刊版PDF第5页Table II（活动先验）、第2页I-A（non-separable denoisers及channel correlations），训练分布另见第8页IV-A/B；参见E5/E6。

**差异清单：**

```json
{
  "necessary_term_substitutions": [],
  "other_changes": [
    "The activities follow Bernoulli priors 只有活动先验的概念依据，Table II为分布公式，不是该英文说明句。",
    "while引入的对照结构与q_tr(H_k) retains the dependence among the coefficients within H_k未找到完整对应原句。",
    "Cai第2页讨论将spatial-frequency channel matrix作为super node、引入non-separable denoisers以利用channel correlations；本句改成训练先验保留块内系数依赖的陈述，不能将原文整段架构解释当作一个必要术语替换。",
    "若以E5/E6支撑整句，属于汇总不同位置的相关内容，不能按原句语言一致性通过。"
  ]
}
```

**判定理由：** Bernoulli先验与信道相关性的概念可定位，但本次未定位包含本句两分句及while连接关系的整句。

### 段落组织

```json
{
  "same_original_paragraph": false,
  "assessment": "P10不是可确认来自同一原段并保持句序的段落：S01取Shen III-B的开头框架却改了关系从句；S02–S04在Cai有分散的概念关联，但本次未定位对应整句。",
  "order_and_connectors": "Shen原首句后接 In addition, 对消息符号作定义，再接 Now, we describe...；本稿改接 Let q_tr...、For inference...和while结构，原段后续顺序与连接关系未保留。Cai的训练集与分布描述位于IV-A/IV-B，活动先验与信道相关性位于II-B/Table II及I-A，无法确认当前顺序来自一个原段。",
  "source_mixing": "能确认Shen句架与Cai相关概念出自不同文献/不同原段；不能反推S02–S04一定由某些原句拼接，因其整句来源未定位。",
  "attribution_risk": "不能把本文Ahat/sigmahat由Y获取、q_tr训练先验定义、显式独立性说明及while对照句统称为他文原句的术语替换；技术相关性不豁免文字新增。",
  "formula_specificity": "P10无显示公式；q_tr的定义与推断假设属于本文建模说明，须单独识别。"
}
```

## P11　后验分解与估计目标

不通过：4句中1句EXACT、2句OTHER_CHANGE、1句NO_SOURCE；整段非同一原段保留组织。

原始证据：[P11.json](<D:/afdm-gfra/paper/checks/strict_sentence_audit_20261029/P11.json>)；精简对照：[P11.md](<D:/afdm-gfra/paper/checks/strict_sentence_audit_20261029/P11.md>)。

### P11-S01　存在非术语增删改

**当前完整句：**

```latex
Exact Bayesian estimators, e.g., the MMSE estimator, are generally
intractable due to the high-dimensional integrals in the
marginalization of the joint posterior distribution.
```

**来源：** [cai2026.pdf](<D:/afdm-gfra/reference/literature/cai2026.pdf>)，PDF第[4]页；II-B首段第二句。

**核对原句：**

```text
Exact Bayesian estimators, e.g., the MMSE estimator, are generally intractable due to the high-dimensional integrals in the marginalization of the joint posterior distribution \(p(\mathbf X,\{\mathbf H_k\}_{k=1}^{K},\{\alpha_k\}_{k=1}^{K}\mid\mathbf Y)\).
```

**差异清单：**

```json
{
  "necessary_term_substitutions": [],
  "other_changes": [
    {
      "type": "deletion",
      "original": "\\(p(\\mathbf X,\\{\\mathbf H_k\\}_{k=1}^{K},\\{\\alpha_k\\}_{k=1}^{K}\\mid\\mathbf Y)\\)",
      "draft": "删除",
      "explanation": "原句在joint posterior distribution之后、句号之前的完整后验表达式被删除。它是句内成分，不是公式编号。"
    }
  ],
  "display_only": [
    "除该删除外，英文词语与词序一致；PDF断行、数学排版规范化。"
  ]
}
```

**判定理由：** 删除了原句内明确的联合后验表达式，不能判EXACT或TERM_ONLY。

### P11-S02　原句一致

**当前完整句：**

```latex
Alternatively, message-passing algorithms provide a low-complexity
iterative approach for approximately calculating the MMSE estimator
\cite{cai2026}.
```

**来源：** [cai2026.pdf](<D:/afdm-gfra/reference/literature/cai2026.pdf>)，PDF第[4]页；II-B第二段首句。

**核对原句：**

```text
Alternatively, message-passing algorithms [5], [6], [27], [47] provide a low-complexity iterative approach for approximately calculating the MMSE estimator.
```

**差异清单：**

```json
{
  "necessary_term_substitutions": [],
  "other_changes": [],
  "display_only": [
    "原文algorithms后的[5], [6], [27], [47]改为现稿句末\\cite{cai2026}。引文项及位置变化单列；按本轮语言一致性口径去掉引文标注后，全部词语与词序一致。",
    "PDF approxi-/mately断行还原。"
  ],
  "citation_note": "EXACT只证明说明文字一致，不证明引用对象或引用方式正确。"
}
```

**判定理由：** 除引文标注及排版外，完整说明句逐字一致。

### P11-S03　存在非术语增删改

**当前完整句：**

```latex
In message passing, we factorize the joint posterior
distribution according to Bayes' theorem and the conditional
independence relationships among the variables, expressed as
\begin{equation}
 \begin{aligned}
 &q(\mathbf X,\{H_k\},\bm\alpha\mid\mathbf Y)\\
 &\quad\propto p(\mathbf Y\mid\mathbf X)\\
 &\qquad\times\prod_{k=1}^{K}
 p(X_k\mid H_k,\alpha_k)q_{\rm tr}(H_k)p(\alpha_k),
 \end{aligned}
 \label{eq:working-posterior}
\end{equation}
where $p(\mathbf Y\mid\mathbf X)$ is the Gaussian likelihood from
\eqref{eq:mmv}, $p(X_k\mid H_k,\alpha_k)$ imposes
$X_k=\alpha_kH_k$, and
$p(\alpha_k)=\rho^{\alpha_k}(1-\rho)^{1-\alpha_k}$.
```

**来源：** [cai2026.pdf](<D:/afdm-gfra/reference/literature/cai2026.pdf>)，PDF第[4, 5]页；II-B，式(5)及跨页where。

**核对原句：**

```text
In message passing, we factorize the joint posterior distribution according to Baye’s theorem and the conditional independence relationships among the variables, expressed as
\[
p(\mathbf X,\{\mathbf H_k\}_{k=1}^{K},\{\alpha_k\}_{k=1}^{K}\mid\mathbf Y)
\propto\prod_{m=1}^{M}p(\mathbf y_m\mid\mathbf x_m)
\prod_{k=1}^{K}p(\mathbf X_k\mid\mathbf H_k,\alpha_k)p(\mathbf H_k)p(\alpha_k), \tag{5}
\]
where \(\mathbf x_m\in\mathbb C^{NK}\) and \(\mathbf y_m\in\mathbb C^{NT}\) denote the \(m\)-th column of \(\mathbf X=[\mathbf x_1,\ldots,\mathbf x_M]\) and \(\mathbf Y=[\mathbf y_1,\ldots,\mathbf y_M]\), respectively.
```

**差异清单：**

```json
{
  "necessary_term_substitutions": [
    {
      "original": "粗体矩阵X_k、H_k",
      "draft": "本文设备块/张量X_k、H_k",
      "note": "这是可映射的对象表示；不能豁免后续说明替换。"
    },
    {
      "original": "λ",
      "draft": "ρ",
      "note": "仅在与Table II比较活动概率时可作符号对应；原where句没有λ，因此不是原where的逐词替换。"
    }
  ],
  "other_changes": [
    {
      "type": "spelling_or_possessive_correction",
      "original": "Baye’s",
      "draft": "Bayes'",
      "explanation": "两版PDF均印作Baye’s。弯/直撇号可属显示层，撇号相对s的位置变化是实际文字修正；即使是纠错也非术语替换。"
    },
    {
      "type": "whole_clause_deletion",
      "original": "where \\(\\mathbf x_m\\in\\mathbb C^{NK}\\) and \\(\\mathbf y_m\\in\\mathbb C^{NT}\\) denote the \\(m\\)-th column of \\(\\mathbf X=[\\mathbf x_1,\\ldots,\\mathbf x_M]\\) and \\(\\mathbf Y=[\\mathbf y_1,\\ldots,\\mathbf y_M]\\), respectively.",
      "draft": "无此列向量定义",
      "explanation": "删除x_m、y_m、两个维度、m-th column、X/Y列展开及respectively。"
    },
    {
      "type": "new_explanatory_clause",
      "original": "原where无此内容",
      "draft": "where \\(p(\\mathbf Y\\mid\\mathbf X)\\) is the Gaussian likelihood from \\eqref{eq:mmv}",
      "explanation": "新增整矩阵高斯似然说明与本文mmv回指。"
    },
    {
      "type": "new_explanatory_clause",
      "original": "原where无此内容",
      "draft": "\\(p(X_k\\mid H_k,\\alpha_k)\\) imposes \\(X_k=\\alpha_kH_k\\)",
      "explanation": "新增imposes谓语及约束解释。"
    },
    {
      "type": "new_explanatory_clause",
      "original": "原where无此内容",
      "draft": "and \\(p(\\alpha_k)=\\rho^{\\alpha_k}(1-\\rho)^{1-\\alpha_k}\\)",
      "explanation": "新增显式Bernoulli质量函数。and由原句连接两个列向量改为连接约束解释与活动先验；三项定义组织是新写的。"
    },
    {
      "type": "model_substitution",
      "original": "p(H_k)",
      "draft": "q_tr(H_k)",
      "explanation": "当前P10将q_tr定义为训练样本代表的先验；不能把整个先验含义变更当成任意可豁免术语。"
    }
  ],
  "display_equation_changes": [
    {
      "original": "\\(p(\\mathbf X,\\{\\mathbf H_k\\}_{k=1}^{K},\\{\\alpha_k\\}_{k=1}^{K}\\mid\\mathbf Y)\\)",
      "draft": "\\(q(\\mathbf X,\\{H_k\\},\\bm\\alpha\\mid\\mathbf Y)\\)",
      "explanation": "后验p→q；活动集合→α向量；H集合省略显式k范围。"
    },
    {
      "original": "\\(\\prod_{m=1}^{M}p(\\mathbf y_m\\mid\\mathbf x_m)\\)",
      "draft": "\\(p(\\mathbf Y\\mid\\mathbf X)\\)",
      "explanation": "逐列似然乘积压缩为整矩阵似然；相应m索引和列向量定义消失。"
    },
    {
      "original": "\\(\\prod_k p(\\mathbf X_k\\mid\\mathbf H_k,\\alpha_k)p(\\mathbf H_k)p(\\alpha_k)\\)",
      "draft": "\\(\\prod_k p(X_k\\mid H_k,\\alpha_k)q_{\\rm tr}(H_k)p(\\alpha_k)\\)",
      "explanation": "保留按设备的三类因子，但替换信道先验与对象表示。"
    },
    {
      "original": "Table II: \\((1-\\lambda)\\delta(\\alpha_k)+\\lambda\\delta(1-\\alpha_k)\\)",
      "draft": "\\(\\rho^{\\alpha_k}(1-\\rho)^{1-\\alpha_k}\\)",
      "explanation": "δ混合写法改成二值质量函数。λ→ρ可以对应，但整个数学表示不是表中逐字迁移。"
    }
  ],
  "display_only": [
    "式号/排版不计不通过；式体无需同式。上述说明文字删除/新增仍须判OTHER_CHANGE。"
  ]
}
```

**判定理由：** 可定位引导句，但完整句的where被整体替换，并存在Baye’s的非术语文字修正。

### P11-S04　本次未定位可对齐整句

**当前完整句：**

```latex
The MMSE channel estimate and posterior probability of activity
can be calculated as
\begin{equation}
 \begin{aligned}
 X_k^{\rm MMSE}&=\E_q[X_k\mid\mathbf Y],\\
 p_k^{\rm Bayes}&=q(\alpha_k=1\mid\mathbf Y).
 \end{aligned}
 \label{eq:targets}
\end{equation}
```

**来源定位/检索边界：** 本次七份语料未定位可对齐完整句。最近内容是Cai两版III-B(1) PDF p6式(18)–(19)及where、p7式(22)–(23)，及III-B(2) PDF p7式(28)–(30)及where。

**差异清单：**

```json
{
  "necessary_term_substitutions": [],
  "other_changes": [
    {
      "type": "no_whole_sentence_alignment",
      "explanation": "未定位以The MMSE channel estimate and posterior probability of activity为联合主语、用can be calculated as引出当前两个目标的原句；普通计算模板及单个术语相同不足以建立整句来源。"
    },
    {
      "type": "comparison_to_mean_template",
      "explanation": "若与III-B(1)强行对齐，主语由后验均值/方差变为信道估计/活动概率，删除原变量名，替换两式，删除整个Z_k归一化where，均非简单术语替换。"
    },
    {
      "type": "comparison_to_activity_definition",
      "explanation": "III-B(2)的posterior probability of activity是活动信念式后的定义；当前变成句首并列主语，去掉for the k-th device并改变谓语；只有词组重合，无法对齐整句。"
    }
  ],
  "display_equation_changes": [
    {
      "draft": "\\(X_k^{\\rm MMSE}=\\mathbb E_q[X_k\\mid\\mathbf Y]\\)",
      "explanation": "本文工作后验q下的设备块目标；Cai式(22)是H_k给定H_k^pri的均值，对象与条件不同。"
    },
    {
      "draft": "\\(p_k^{\\rm Bayes}=q(\\alpha_k=1\\mid\\mathbf Y)\\)",
      "explanation": "本文后验活动概率目标；Cai式(30)是λ_k^post的消息更新闭式。"
    }
  ]
}
```

**判定理由：** 本次核查未定位可对齐整句；相关词组分散在不同去噪子节，不能拼接为原句证据。

### 段落组织

```json
{
  "same_original_paragraph": false,
  "source_mapping": [
    "S01来自II-B第一原段第二句；原第一句位于当前P09。",
    "S02和S03引导语来自II-B第二原段，原where跨PDF p4–5。",
    "S03新增where在数学上接近p5 Table II，但非该原段英文；q_tr训练先验与mmv回指是本文模型内容。",
    "S04未定位整句；最近内容在III-B(1)/(2)而非II-B。"
  ],
  "order_and_connectors": "S01→Alternatively(S02)→In message passing(S03)保留跨两个原段的相邻顺序及过渡语；完整where重写后，再加入未定位的两目标句，已非同一原段整体迁移。",
  "omissions": "S03原列向量定义删除；原文接着的因子图和Table II说明未保留于P11。后两完整句仅记录段落衔接，不另算P11删句。",
  "attribution_risk": "不能让Cai原引导语使本文q_tr、整矩阵似然解释和两目标定义看似完整源于同一原段。",
  "cross_document_status": "未确认逐字拼接其他作者文献；Huang只在权重段使用Gaussian likelihood，不能对应当前where。",
  "paragraph_organization_pass": false
}
```

## P12　消息传递困难与后续引出

{'strict_pass': False, 'sentence_level_pass': False, 'paragraph_structure_pass': False, 'conclusion': '不通过：P12-S01、P12-S02除符号替换外还各删除一个完整提示成分；P12-S03、P12-S04逐词一致；整段跨原说明段、第二条目和总结段拼接。'}

原始证据：[P12.json](<D:/afdm-gfra/paper/checks/strict_sentence_audit_20261029/P12.json>)；精简对照：[P12.md](<D:/afdm-gfra/paper/checks/strict_sentence_audit_20261029/P12.md>)。

### P12-S01　存在非术语增删改

**当前完整句：**

```latex
The main difficulty in implementing message passing on the factor graph lies in the message calculation associated with the factor node $q_{\rm tr}(H_k)$ \cite{cai2026}.
```

**来源：** [cai2026.pdf](<D:/afdm-gfra/reference/literature/cai2026.pdf>)，PDF第5页；II-B Problem Statement；式(5)后的说明段末句，左栏中部、两个项目符号之前。。

**核对原句：**

```text
The main difficulty in implementing message passing on the factor graph lies in the message calculation associated with the factor node $p(\mathbf H_k)$, detailed as follows.
```

**差异清单：**

```json
{
  "term_substitutions": [
    {
      "source": "$p(\\mathbf H_k)$",
      "draft": "$q_{\\rm tr}(H_k)$",
      "type": "technical_symbol_or_object_replacement",
      "details": "先验分布函数 p 改为 q_tr；其信道参数记法由粗体 H_k 改为本文 H_k。此处仅记录符号／对象替换，不据此认定真实信道先验与训练样本先验等价。"
    }
  ],
  "other_changes": [
    {
      "operation": "delete",
      "source_text": ", detailed as follows",
      "draft_text": "",
      "scope": "sentence",
      "details": "删去逗号及三个英文词，句点前不再有引出后文条目的短语；其余非术语词无增加、替换或重排。"
    }
  ],
  "display_normalizations": [
    "仅合并空白和断行；原文数学粗体、下标按LaTeX记法转写。",
    "现句添加 \\cite{cai2026} 作为来源标记；按协议属于引文显示层差异，不计为非术语文本添加。",
    "期刊抽取文本 difﬁculty 的 fi 连字规范化为 difficulty；PDF已确认。"
  ],
  "nonterm_additions": [],
  "connector_changes": [],
  "word_order_changes": []
}
```

**判定理由：** 能完整对齐两版本原句；除先验符号替换外，删除句末“detailed as follows”，属于非术语删减。

### P12-S02　存在非术语增删改

**当前完整句：**

```latex
Generally speaking, even if the ground-truth channel distribution becomes analytically available, calculating the messages for the factor node $q_{\rm tr}(H_k)$ remains highly challenging due to the complicated and high-dimensional integrals.
```

**来源：** [cai2026.pdf](<D:/afdm-gfra/reference/literature/cai2026.pdf>)，PDF第5页；II-B Problem Statement；第二条目 Intractable high-dimensional integrals 的末句，左栏下部。。

**核对原句：**

```text
Generally speaking, even if the ground-truth channel distribution becomes analytically available, calculating the messages for the factor node $p(\mathbf H_k)$ remains highly challenging due to the complicated and high-dimensional integrals (as will be discussed in Section III-B).
```

**差异清单：**

```json
{
  "term_substitutions": [
    {
      "source": "$p(\\mathbf H_k)$",
      "draft": "$q_{\\rm tr}(H_k)$",
      "type": "technical_symbol_or_object_replacement",
      "details": "先验分布函数 p 改为 q_tr；其信道参数记法由粗体 H_k 改为本文 H_k。此处仅记录符号／对象替换，不据此认定真实信道先验与训练样本先验等价。"
    }
  ],
  "other_changes": [
    {
      "operation": "delete",
      "source_text": " (as will be discussed in Section III-B)",
      "draft_text": "",
      "scope": "sentence",
      "details": "删除完整括号及其中预告性从句，不只是更换 Section III-B 的编号；其余非术语词无增加、替换或重排。"
    }
  ],
  "display_normalizations": [
    "仅合并空白和断行；原文数学粗体、下标按LaTeX记法转写。"
  ],
  "nonterm_additions": [],
  "connector_changes": [],
  "word_order_changes": []
}
```

**判定理由：** 能完整对齐两版本原句；除先验符号替换外，删除整段章节预告括号，不能视作仅变更章节编号。

### P12-S03　原句一致

**当前完整句：**

```latex
To summarize, the message-passing framework faces a dilemma: the adopted channel prior is either too imprecise to ensure good performance, or too complex to facilitate efficient message calculation.
```

**来源：** [cai2026.pdf](<D:/afdm-gfra/reference/literature/cai2026.pdf>)，PDF第5页；II-B Problem Statement；两条目后的总结段第1句，左栏下部。。

**核对原句：**

```text
To summarize, the message-passing framework faces a dilemma: the adopted channel prior is either too imprecise to ensure good performance, or too complex to facilitate efficient message calculation.
```

**差异清单：**

```json
{
  "term_substitutions": [],
  "other_changes": [],
  "display_normalizations": [
    "仅合并空白和断行；原文数学粗体、下标按LaTeX记法转写。",
    "期刊抽取文本 efﬁcient 的 fi 连字规范化为 efficient；PDF已确认。"
  ],
  "nonterm_additions": [],
  "connector_changes": [],
  "word_order_changes": []
}
```

**判定理由：** 经两个PDF逐字核对，并以抽取文本验证，原句词语、词序、冒号、逗号和连接关系均一致。

### P12-S04　原句一致

**当前完整句：**

```latex
This paper seeks to address the aforementioned challenges by plugging in deep generative priors for efficient message calculation.
```

**来源：** [cai2026.pdf](<D:/afdm-gfra/reference/literature/cai2026.pdf>)，PDF第5页；II-B Problem Statement；两条目后的总结段第2句，左栏下部。。

**核对原句：**

```text
This paper seeks to address the aforementioned challenges by plugging in deep generative priors for efficient message calculation.
```

**差异清单：**

```json
{
  "term_substitutions": [],
  "other_changes": [],
  "display_normalizations": [
    "仅合并空白和断行；原文数学粗体、下标按LaTeX记法转写。",
    "期刊抽取文本 efﬁcient 的 fi 连字规范化为 efficient；PDF已确认。",
    "两版本原文行末 afore- 与下一行 mentioned 合并为 aforementioned；这是断行连字符消除，不是词语删改。"
  ],
  "nonterm_additions": [],
  "connector_changes": [],
  "word_order_changes": []
}
```

**判定理由：** 经两个PDF逐字核对，并以抽取文本验证，原句词语、词序及句法完全一致；原文断行的 afore-mentioned 只合并为 aforementioned。

### 段落组织

```json
{
  "same_document_source": true,
  "same_original_paragraph": false,
  "cross_document_splicing": false,
  "cross_paragraph_or_bullet_splicing": true,
  "mapping": [
    {
      "draft": "P12-S01",
      "origin": "式(5)后说明段末句；其前文是 where 定义、因子图及表II说明。"
    },
    {
      "draft": "P12-S02",
      "origin": "第二条目最后一句；第一条目全部、第二条目标题及前两句未保留。"
    },
    {
      "draft": "P12-S03–S04",
      "origin": "随后独立总结段的前两句；原总结段还有三句后续方法预告未保留。"
    }
  ],
  "source_order_preserved": true,
  "order_explanation": "在期刊版和v2中均按 S01→第二条目末句S02→总结段S03→S04 的先后出现；没有将来源句倒序。S03与S04在来源中连续。S01与S02之间省去两个标题和五个完整解释句。",
  "connectors_preserved": [
    "Generally speaking,",
    "even if",
    "due to",
    "To summarize,",
    "either ... or",
    "by plugging in"
  ],
  "connectors_or_structural_cues_removed": [
    ", detailed as follows",
    "(as will be discussed in Section III-B)",
    "两个项目符号、条目标题及原段落边界"
  ],
  "omissions_are_paragraph_level_not_extra_draft_sentences": true,
  "omitted_source_context": {
    "omitted_first_bullet_title": "Lack of exact characterization of channel distribution:",
    "omitted_first_bullet_sentences": [
      "It is extremely challenging, if not impossible, to obtain an accurate characterization of the channel distribution $p(\\mathbf H_k)$.",
      "Existing literature resorts to various assumptions, e.g., Rayleigh fading [5], [6], Rician fading [10], angular-frequency structured sparsity [11], or frequency-domain block-wise linearity [27], to model the wireless channel.",
      "These assumptions, however, may be mismatched with the ground-truth prior distribution, leading to significant performance degradation and potentially causing the algorithm to diverge."
    ],
    "second_bullet_title": "Intractable high-dimensional integrals:",
    "omitted_second_bullet_leading_sentences": [
      "The messages associated with the factor node $p(\\mathbf H_k)$ can only be derived under specific, simple, and easily computable priors.",
      "For example, the work in [11] adopted a simple i.i.d. Bernoulli-Gaussian distribution to account for the inherent sparsity in the angular domain."
    ],
    "omitted_summary_tail_sentences": [
      "We begin by developing a TMP framework for JADCE.",
      "Then, we present a unique interpretation of the belief calculation at the factor node $p(\\mathbf H_k)$ as an MMSE denoising problem under AWGN observations.",
      "This insight enables the integration of score-based generative networks for provable MMSE denoising, eliminating the need to compute high-dimensional integrals."
    ]
  },
  "context_effect": "To summarize 和 aforementioned challenges 逐词保留，但原文支撑“过于不精确／过于复杂”两方面困境的第一条目已省去，第二条目也只保留末句；这使总结对象的显式铺垫发生变化。",
  "own_model_attribution_risk": "原文 p(H_k) 为其信道先验；本文将因子改为训练样本先验 q_tr(H_k)。这不是原文已验证本文先验或模型的证据。末句虽逐词相同，This paper 在本文中指向本文，原文不自动证明本文完成该目标。本段没有显式展示公式。",
  "paragraph_structure_pass": false,
  "conclusion": "同一来源论证区间中的摘取拼合，不是同一原段仅替换术语。"
}
```
