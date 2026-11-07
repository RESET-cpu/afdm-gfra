# P01–P03 原句恢复候选

仅提供六处 old/new 替换，不写 canonical。6 句支持性改写全部处理；原有 2 句合理组合和 4 句本稿定义/推导保留。P02-S01 恢复为 Shen 连续两句，因此本部分由 12 个完整语法句变为 13 个。

恢复完整源句必要地增加少量文字；未新增模型论证、物理假设、防御性解释或研究范围。P03-S02 只组合方向余弦、轴、相邻阵元间距和波长定义，不引入新角度或三角函数。

| 旧句 | 操作 | 修改后类别 | 处理 |
|---|---|---|---|
| P01-S01 | KEEP | REASONABLE_COMBINATION | 保留已获核查认可的原句组合。 |
| P01-S02 | MODIFY | TERM_ONLY | 恢复 Shen 的 During ... share ... to transmit ... to the satellite 原句结构；time interval→transmission block、signals→pilots 是本稿对象限定。 |
| P01-S03 | MODIFY | EXACT | 恢复完整原句的 Additionally, to minimize ... these terrestrial devices；不再用 reduce 或压缩指代替代源措辞。 |
| P02-S01 | MODIFY | TERM_ONLY | 恢复 Shen 连续两句的高速引起时变、时变和多径要求双扩展模型的因果关系；仅首次将 TSLs 展开。不新增物理假设。 |
| P02-S02 | KEEP | REASONABLE_COMBINATION | 保留已获核查认可的原句组合。 |
| P02-S03 | KEEP | AUTHOR_DEFINED_OR_DERIVED | 保留本稿定义/公式/假设；不计作参考原句。 |
| P02-S04 | KEEP | AUTHOR_DEFINED_OR_DERIVED | 保留本稿定义/公式/假设；不计作参考原句。 |
| P02-S05 | MODIFY | TERM_ONLY | 恢复 Shen 的差值 represents differential delay ... where ... are denoted as ... respectively 结构；仅去掉本稿不存在的 Fig.1 指引，改路径/设备索引和共同延迟上下标。公式表达式保持不变。 |
| P02-S06 | MODIFY | TERM_ONLY | 将普通改写 is 恢复为源句 corresponds to；保留本稿已经定义的 τ_c 符号与 Earth 大写。 |
| P03-S01 | KEEP | AUTHOR_DEFINED_OR_DERIVED | 保留本稿定义/公式/假设；不计作参考原句。 |
| P03-S02 | MODIFY | REASONABLE_COMBINATION | 按主审确认，以 Shen 的 directional cosines/轴分句和 Li 的波长/相邻阵元间距分句作必要语法组合；不引入原文的角度变量、三角函数、阵列归一化或符号约定。将一般的阵元间距表述恢复为原文的“相邻阵元间距”定义，并作对应复数调整。 |
| P03-S03 | KEEP | AUTHOR_DEFINED_OR_DERIVED | 保留本稿定义/公式/假设；不计作参考原句。 |

## P01-S02

候选：

```tex
During each transmission block, active devices share the same
time-frequency resources to transmit their pilots to the satellite.
```

来源与替换：

- shen2025，PDF 第 3 页，II. System Model。

> During each time interval, active devices share the same time-frequency resources to transmit their signals to the satellite.

右栏 Fig.1 后第一段第三句。

必要替换：time interval→transmission block；signals→pilots

说明：恢复 Shen 的 During ... share ... to transmit ... to the satellite 原句结构；time interval→transmission block、signals→pilots 是本稿对象限定。

## P01-S03

候选：

```tex
Additionally, to minimize energy consumption, we assume that these
terrestrial devices operate without GNSS capabilities and do not
pre-compensate for delay and Doppler shifts \cite{shen2025}.
```

来源与替换：

- shen2025，PDF 第 3 页，II. System Model。

> Additionally, to minimize energy consumption, we assume that these terrestrial devices operate without GNSS capabilities and do not pre-compensate for delay and Doppler shifts.

右栏 Fig.1 后第一段第四句。

必要替换：仅保留本稿引用键；英文原句恢复。

说明：恢复完整原句的 Additionally, to minimize ... these terrestrial devices；不再用 reduce 或压缩指代替代源措辞。

## P02-S01

候选：

```tex
The terrestrial-satellite links (TSLs) will experience fast variations
due to the high mobility of the LEO satellite. Hence, this time variation
and multipath propagation require a doubly dispersive channel model
for accurate TSLs characterization \cite{shen2025}.
```

来源与替换：

- shen2025，PDF 第 3 页，II-A. Terrestrial-satellite Link Model。

> The TSLs will experience fast variations due to the high mobility of the LEO satellite. Hence, this time variation and multipath propagation require a doubly dispersive channel model for accurate TSLs characterization.

§II-A 起首两句。

必要替换：TSLs 首次出现展开为 terrestrial-satellite links (TSLs)。

说明：恢复 Shen 连续两句的高速引起时变、时变和多径要求双扩展模型的因果关系；仅首次将 TSLs 展开。不新增物理假设。

## P02-S05

候选：

```tex
$\tau_{k\ell}=\widetilde\tau_{k\ell}-\tau_c$ represents the differential
delay for the $\ell$th path from device $k$ to the satellite, where
$\widetilde\tau_{k\ell}$ and $\tau_c$ are denoted as propagation delay
and common delay, respectively.
```

来源与替换：

- shen2025，PDF 第 3 页，II-A. Terrestrial-satellite Link Model。

> As shown in Fig. 1, τ_{i,u} = τ̃_{i,u} − τ^c represents the differential delay for the i-th path from the u-th device to the satellite, where τ̃_{i,u} and τ^c are denoted as propagation delay and common delay, respectively.

Eq.(1) 后第二句。

英文逐字核对；引语中的数学符号是原 PDF 的文本转写，原文共同延迟 c 为上标，本稿 τ_c 将其改为下标。

必要替换：i→ℓ、u→k、τ^c→τ_c。；删除 As shown in Fig.1，因为该图不属于本稿；the u-th device→device k。

说明：恢复 Shen 的差值 represents differential delay ... where ... are denoted as ... respectively 结构；仅去掉本稿不存在的 Fig.1 指引，改路径/设备索引和共同延迟上下标。公式表达式保持不变。

## P02-S06

候选：

```tex
The common delay $\tau_c$ corresponds to the propagation time between
the satellite and the closest point on Earth within the beam coverage
\cite{shen2025}.
```

来源与替换：

- shen2025，PDF 第 3 页，II-A. Terrestrial-satellite Link Model。

> The common delay corresponds to the propagation time between the satellite and the closest point on earth within the beam coverage [21].

Eq.(1) 后 τ 差定义之后。

必要替换：加入已经定义的 τ_c；earth→Earth；来源内部 [21]→shen2025。

说明：将普通改写 is 恢复为源句 corresponds to；保留本稿已经定义的 τ_c 符号与 Earth 大写。

## P03-S02

候选见 a_patch.json 第六项；为避免重复 Li 必要短分句，此处不再次列英文。

来源与替换：

- shen2025，PDF 第 3 页，II-A. Terrestrial-satellite Link Model。

> The directional cosines Θ^z_u = cos ϑ^z_u and Θ^y_u = sin ϑ^z_u sin ϑ^a_u, along the z-axis and y-axis, depend on the zenith angle ϑ^z_u and azimuth angle ϑ^a_u, respectively.

§II-A 在本页末尾的最后一句。

英文逐字核对；引语中的上下标及三角函数公式按原 PDF 转写。

- li2023，PDF 第 4 页，II-B. Signal Models。

左栏第一完整段无编号 UPA 公式后的 where 分句：定义波长及沿相应轴的相邻阵元间距。本轮 notes 不复引英文。

必要替换：Li 的单轴 d_v→已有 (d_y,d_z)，spacing→spacings；删去 c、f_c、v 等本稿本句不需要的变量定义。；源 x/y 轴→本稿 y/z 轴；Shen 的 Θ_y,Θ_z→已有 μ_y,k,μ_z,k。；将 Shen 名词分句连为定义谓语，避免引入新角度变量；不宣称是单一完整原句。

说明：按主审确认，以 Shen 的 directional cosines/轴分句和 Li 的波长/相邻阵元间距分句作必要语法组合；不引入原文的角度变量、三角函数、阵列归一化或符号约定。将一般的阵元间距表述恢复为原文的“相邻阵元间距”定义，并作对应复数调整。

## 核验

六个 old 片段均在 before.tex 中唯一出现；顺序应用候选后，全部显示公式和标签与原稿逐字一致。所有既有符号、物理假设不变；新增的 shen2025、li2023 引用使用现有 bib 键。Li 在 notes 不直引英文；候选正文相关必要短分句保守计 22 词，不超过 25 词。

原 PDF 依据沿用本轮已直接目视核对的 Shen PDF p.3 和 Li PDF p.4；核对图在上一轮 a_pdf_views。所有数学上下标引文均为原 PDF 记号转写，不冒充字符层逐字复制。
