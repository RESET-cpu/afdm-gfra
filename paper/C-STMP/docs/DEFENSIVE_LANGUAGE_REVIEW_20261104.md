# 正文的防御性、辩护性说明检查

日期：2026-11-04。状态：**作者已授权实施，六处建议均已完成；两版 PDF 已更新并核验。** 下表保留初次审查时的原文与判断，具体实施见文末。

作者在移除伪代码中的训练区间外 Gaussian evidence 分支后，询问正文是否还有类似说明。本轮通读当前 `main.tex` 中的摘要、第 I–VII 章正文和图表说明，并核对两份编入稿件的附录以区分正文与 full 版补充内容。未编译的历史附录不计入当前稿件。

判断依据为句子在当前上下文中的作用：模型条件、公式定义和实验口径应在适当位置交代；范围外兜底、重复限定、笼统自证和逐项实现检查不必占据主线。没有按 not、only、approximate 等单词机械判定，也没有重新给论文作 C/M 定级。

## 建议处理的六处

以下原文摘录来自初次审查时实际读取的源稿。行号对应 2026-11-04 伪代码修订后、此次精简前的版本；六处建议现均已实施。

| 编号与位置 | 原文摘录 | 判断 | 建议处理 |
|---|---|---|---|
| D1：VI-A3，[第 178 行](../sections/06_simulation_results.tex#L178) | “Outside the training interval …, the retained sites give”及式 (43) | 最直接的范围外兜底展开；目前又被放成了一段独立公式说明，与作者刚才指出的问题相同 | 从接收机设置段移出兜底叙述。式 (43) 同时用于 VI-C 的 Gaussian 活动概率消融对照，应移到该实验定义处、按对照计算引出，不能连同引用关系一起机械删除。范围外代码行为留在实现记录即可 |
| D2：V-C，[第 211 行](../sections/05_overall_algorithm.tex#L211) | “Within the training interval, each device requires …” | 把同一范围外例外带进复杂度叙述；网络调用次数本身有用 | 按执行网络更新的主迭代说明每设备调用数，或统一按每轮成本上界给出复杂度。去掉训练区间前缀时同步调整成本的表述口径，不改运算或数量 |
| D3：VI-A3，[第 156 行](../sections/06_simulation_results.tex#L156) | “With fixed adaptations to multiantenna AFDM, weights, and activity decision rules, …” | 笼统强调设置固定，具体对象不清，容易读成公平性的自我保证 | 删去这段笼统前置语，直接交代 SOMP 原子数、SBL 迭代数、GNN 层数；已有字典、相位和噪声信息继续在相应设置句说明。无需另加一句保证公平的文字 |
| D4：III-B1，[第 96 行](../sections/03_bayesian_receiver_design.tex#L96) | “The approximations are evaluated under the local model …” | 重复限定：前面的输入消息模型及 active hypothesis 已交代这层条件。属于轻微冗余，不是方法缺陷 | 可删这一重复前半句，保留后半句通向 V-A 的具体计算说明；首次定义的局部 AWGN 模型及公式中的近似记号保留 |
| D5：VI-A4，[第 200 行](../sections/06_simulation_results.tex#L200) | “stopping requires stable channel estimates, input variance, and activity probabilities, agreement … accepted, stable Gaussian site updates …” | 多个容差、窗口和检查项挤成一段，接近实现检查清单；主要是细节负担，不是辩护语气 | 正文保留停止原则及最小/最大轮数；细窗口与接受检查可集中在既有实现附录或实现说明。不能将简写理解成改变实际停止规则，也不改变表 II 的迭代上限统计 |
| D6：VI-C，[第 258 行](../sections/06_simulation_results.tex#L258) | “keeping all other receiver settings unchanged”; “identical observations”; “the same 354 paired scenes”; “All such runs are included in AER” | 前三处的配对与控制条件有重复；最后一句是统计口径，有实际信息 | 合成一处紧凑的消融设置说明，保留仅替换概率计算、每档 354 个配对场景和全部输出计入 AER 的事实。压缩重复措辞，不删除分 SNR 结果或实际纳入规则 |

D1 是最明确的兜底说明；D2 与它直接相关；D3 是笼统自证；D4–D6 是可压缩的重复限定或实现细节。不能把这六处全部说成严重的防御性辩护。

## 可选优化，不列为同类主要问题

II-C [第 235 行](../sections/02_system_model.tex#L235)的 “This block formulation follows …, with the device matrices defined by …” 是来源交代。若追求紧凑，可将 Cai 引文并入观测式引出句，省去单独的来源比较句。它不是错误或必须删除的辩护；作者此前关心来源可靠性，出处记录及必要引用仍应保留。

## 已检查、建议保留的内容

| 位置与内容 | 保留理由 |
|---|---|
| II-A 的共同 Doppler、块内参数近似不变；II-B 的 CPP 覆盖条件 | 支撑跨帧模型和观测关系的建模条件，不是替算法效果找理由 |
| II-C 的设备独立性与活动/信道先验关系 | 后验分解使用的假设 |
| III 的 Gaussian approximation、局部观测模型与正方差条件 | 说明实际近似和公式成立条件；只压缩重复表述 |
| IV 的 fixed C、均衡训练类别、理想密度比与网络近似的区分 | 说明训练目标及条件期望/密度比关系，属于方法论证 |
| V-B 的噪声估计假设、归一化、阻尼和裁剪参数 | 当前已有简短操作定义，有实际作用；本轮未发现大段为其辩护的文字 |
| VI 的已知/估计相位、估计噪声方差、genie-aided 参考条件 | 决定结果应如何解释的实验设置 |
| VI 的固定每帧能量、未重训、每点样本数、NMSE/AER 统计对象 | 定义比较范围及指标；可合并重复位置，不需要删除这些事实 |
| VI-D1 的单场景表述 “In this example” | 与单场景收敛曲线的证据范围相符 |
| 摘要、引言和结论中的非稀疏先验、有色噪声训练及密度比动机 | 主要是在说明方法选择；没有因为含 without 或 may 就将其标成辩护 |

## 正文与附录的范围

full 版附录 B 确有更显式的限制说明，例如“不单独分离训练协方差的影响”“不是独立验证”“不能据此确定未满足停止条件的原因”。这些没有出现在主稿第 I–VII 章，不能混进正文问题数量。

本轮未建议把附录 B 搬回正文，也未删除其中实际的评估选择、样本处理或参数选定信息；相关安排沿用 `REVIEW_DECISIONS.md`。若后续单独精简附录，可压缩重复评论，事实与必要解释仍以现有记录为准。

## 与已有建议的衔接

- 旧语言表 P10 为旧伪代码建议显式写训练区间分支，已由本轮之前的作者决定取代，不再执行。
- 旧语言表 P11 强调训练范围内的每设备复杂度；当前 D2 提供更符合作者最新呈现偏好的写法，不再照搬该长限定句。
- 旧语言表 P14 建议将 “fixed adaptations …” 拆成独立固定设置句。当前 D3 建议删除笼统前置语，避免把弱表述进一步扩写。具体最终设置继续保留。
- M5 的分 SNR 报告已完成；D6 仅是语言压缩建议，不重开该事项。

## 初次审查核验（修改前）

初次审查未改论文源码、公式、图表、书目、两版 PDF、代码或实验。32 个稿件资产的哈希保存在 [核验目录](../checks/defensive_language_review_20261104/)；当轮核对一致。

## 作者授权后的实施记录

作者随后要求：“可以，那就请你调整修改一下”。本轮按上述六项实施，不扩展到可选的 II-C 来源句或 full 版附录的评估评论。

| 项目 | 实施结果 |
|---|---|
| D1 | 从 VI-A3 删除范围外兜底引出段，把原式 (43) 完整移到 VI-C，作为 Gaussian 活动概率对照的定义；公式内容、标签和编号不变 |
| D2 | 改为说明 Algorithm 1 中 GPJD 更新的每设备网络调用次数，去掉训练范围前缀；调用次数和复杂度表达保持 |
| D3 | 删除笼统的 fixed adaptations 前置语，直接列出 SOMP 原子数、SBL 迭代数和 GNN 层数 |
| D4 | 删除已由前文说明的局部模型限定，保留指向 V-A 的计算说明 |
| D5 | 正文保留估计稳定性、方差一致性和最小/最大迭代轮数；窗口、接受条件及容差继续由已有 full 版附录 B-G 记录，实际停止规则未改 |
| D6 | 合并消融设置，保留仅替换概率计算、其余设置不变、已知相位、每档 354 个配对场景、AER 计入全部运行和 600 轮上限比例 |

范围外计算仍是代码中的既有实现：当输入方差不在训练范围内时，保留 Gaussian sites 并用其计算活动概率；该事实留在本内部记录与代码中，不在正文恢复兜底段。对应 `src/algorithm/STMP/denoiser.py` 的 supported 判断、site 保留和 full_posterior 路径。本次没有更改这些实现。

六处调整均沿用现有术语和运算，没有新增方法名称、引用、数学推导或实验结论。正文简写的停止规则以 `sections/appendix_evaluation_protocol.tex` 的 Additional Implementation Settings 和既有接收机实现为详细定义。

核验结果：

- `main.pdf` / `main_full.pdf` 编译成功，仍为 13/14 页，42 篇参考文献。
- 46 个编号公式的完整公式块及编号保持；所有图表块和图文件保持。
- 30 个输入文件中仅第三、第五、第六章三份源码发生变化，其余 27 个输入保持。两版 PDF 同步更新。
- 主稿第 5、8、9、10 页和 full 版对应修改页已渲染核对；无越界、未定义引用或重复标签。原有 underfull 和图 PDF 版本提示已检查，没有因此扩大排版修改。
- 未更改接收机代码、训练配置、权重或实验结果，未启动训练或实验。

证据：[修改前副本与页面预览](../checks/defensive_language_revision_20261104/)、[修改差异](../checks/defensive_language_revision_20261104/CHANGES.diff)、[核验结果](../checks/defensive_language_revision_20261104/VALIDATION.json)。
