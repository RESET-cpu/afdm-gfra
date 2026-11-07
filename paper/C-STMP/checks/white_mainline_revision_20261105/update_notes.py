from pathlib import Path
import json

OUT = Path(__file__).resolve().parent
PAPER = OUT.parents[1]

p = PAPER / 'sections/00_abstract_zh.md'
t = p.read_text(encoding='utf-8')
old = '有限维、结构化的多帧AFDM观测模型可能导致去噪输入误差与用于训练的白高斯噪声之间的失配。因此，采用不同协方差矩阵的有色高斯噪声训练信道去噪器。'
new = '构建信道去噪器，分别通过其输出和输入导数估计后验均值与平均后验方差，从而在无需为方差估计进行额外训练的情况下提供信道估计及其不确定性信息。'
assert old in t
p.write_text(t.replace(old, new), encoding='utf-8')

p = PAPER / 'README.md'
t = p.read_text(encoding='utf-8')
t = t.replace('# CGP-MP：当前算法稿', '# GP-MP：当前算法稿（正文修订中）', 1)
start = t.index('当前稿件主算法展示名为')
end = t.index('\n\n', start)
t = t[:start] + '当前正文以 **GP-MP** 表示生成式先验辅助消息传递接收机，第四章采用白高斯噪声形式推导。**CGP-MP** 保留为实际采用有色训练权重的实现标签：第六章现有图表与第五章示例仍来自该实现，未改称白噪声结果。**STMP** 仍为含学习密度比活动更新的三网络适配基线。白噪声均值网络及配套分类器已经训练，统一关闭 TF32 的 1000 场景 SNR 对照正在继续；本轮仅用固定前 198 场景作配对核验，未切换 FINAL.json 或冻结资产。' + t[end:]
notice = '\n2026-11-05：同精度、同场景白/有色训练比较显示各档 NMSE 相差不超过 0.081 dB，支持先调整论文论述。已移除摘要、引言和方法章节中对有色训练收益的依赖，补充条件均值导数与不确定性估计的来源；预条件仅保留为实现设置。[配对结果与本轮修订](checks/white_mainline_revision_20261105/README.md)。以下带日期记录保留各自历史含义。\n'
t = t.replace('\n\n2026-11-04：', '\n' + notice + '\n2026-11-04：', 1)
p.write_text(t, encoding='utf-8')

p = PAPER / 'docs/WHITE_MAINLINE_REVISION_PLAN_20261105.md'
t = p.read_text(encoding='utf-8')
intro = '\n**最新状态（2026-11-05）：** 作者在阶段性配对比较后授权开始修改正文。本轮已修改摘要、引言相关动机和第二项贡献、第四至第五章及结论，并同步训练设置和实验归属；第二、三章及引言第一、第三项贡献保持。下文“仅讨论”“尚未修改”等均为此前阶段记录。白噪声 1000 场景实验仍在运行，既有有色图表未替换，冻结主线未切换。见[实施与核验](../checks/white_mainline_revision_20261105/README.md)。\n'
t = t.replace('\n\n日期：', '\n' + intro + '\n日期：', 1)
p.write_text(t, encoding='utf-8')

p = PAPER / 'docs/TERMINOLOGY.md'
t = p.read_text(encoding='utf-8')
entry = '''
### 2026-11-05：正文弱化训练噪声颜色，保留实验归属

本轮以已有作者标签 GP-MP 表示正文方法，采用白噪声形式展开公式；CGP-MP 继续标记第六章实际有色训练实现及其既有结果。两者不是引用文献中的原算法名称。STMP 仍指本项目三网络 AFDM 适配版本。此次是正文修订，不切换冻结权重或 FINAL.json。摘要和引言不再把预条件列为贡献。

| 表述 | 原文定位与采用范围 |
|---|---|
| channel prior / 信道先验；直接学习有效信道 | Huang，项目内 `reference/literature/huang2026.pdf`，摘要、贡献(i)，印刷 p.2949；§III-A 式(7)，p.2951。支持直接从 AFDM 有效信道学习而不施加稀疏、网格对齐假设；不称本文首次提出这一思路。 |
| conditional mean、conditional covariance / 条件均值、条件协方差 | Dytso–Poor–Shamai，正式出版 §III Proposition 1 式(17)，印刷 p.1885；[预印本](https://arxiv.org/pdf/2104.01883) §IV Proposition 1 式(22)。白噪声实表示满足 P=(v/2)J，复坐标平均方差为 v·div(m)/(2D)。 |
| denoiser / 去噪器；uncertainty quantification / 不确定性量化 | Manor–Michaeli，ICLR 2024，[原文](https://arxiv.org/html/2309.13598v2)，§3.2 Theorem 2 式(10)–(11)；§4.1 Algorithm 1 与式(15)。支持利用已训练去噪器及其输入导数估计后验不确定性，无需额外训练。本文使用随机方向中央差分估计平均方差；不将该具体估计器或原文运行时间结论照搬为本文原创/实证。 |
| without additional training for variance estimation | 本文对上述恒等式的实现描述：省去独立方差网络训练；仍需训练信道去噪器和活动分类器，有限差分仍有推理开销，不保证精度或收敛。Cai [v2](https://arxiv.org/html/2506.00581v2) §IV-C 式(52)–(54) 的二阶监督依赖一阶估计，既允许顺序训练也允许阻断目标梯度的同时训练。正文采用正面功能描述，不将 Cai 写成只允许一种训练流程。 |
| preconditioning / 预条件 | Karras 等，NeurIPS 2022，§5 式(7)–(8)、Table 1；归一化输入、输出与跳跃连接。保留为网络实现/训练设置，系数在推理中仍使用，并非训练结束后删除。白噪声实方差为 v/2。历史有色实现的矩阵推广据 Albuquerque–Pearson，NeurIPS 2024，Appendix B.1 式(67)–(68)、(73)、(77)–(78)。 |

公式及证据边界见[本轮核验](../checks/white_mainline_revision_20261105/README.md)。以下条目为历史记录。
'''
t = t.replace('# 当前术语与来源\n', '# 当前术语与来源\n' + entry, 1)
p.write_text(t, encoding='utf-8')

p = PAPER / 'docs/REVIEW_DECISIONS.md'
t = p.read_text(encoding='utf-8')
t += '''

## 2026-11-05：同精度阶段配对后开始正文修订

作者最新要求为“白高斯噪声实验进行了多少了，和同场景的有色噪声对比一下，如果基本没差距的话，我们就开始修改论文正文了”。固定前 198 个完成全部六档 SNR 的物理场景（0–197），重新读取保存数组评分，并核验输入/输出哈希、配置及关闭 TF32。各档 NMSE 差不超过 0.0808 dB，优劣方向并不一致；白/有色汇总 AER 为 0.11995%/0.12416%。当前不足以证明严格等价，但支持不再把有色训练作为主贡献，开始已授权正文修订。白噪声有一次达到 600 轮上限，未排除；完整 1000 场景仍继续。

本次执行摘要和引言相关动机、第二项贡献及第四至第五章的修订，第一、第三项贡献及第二、三章保持。信道先验学习沿 Huang 的对象与动机表述；去噪器输出与输入导数提供均值及平均方差，依据 Dytso 和 Manor–Michaeli。按作者后续意见，不再说“将先验参数化为条件均值去噪器”，不在摘要/引言列预条件，将独立二阶网络的省略柔化为无需为方差估计额外训练，不写成针对 Cai 的批评。预条件仍在实现设置中保留，且其系数用于训练及推理。

正文采用 GP-MP 与标量 v 记号。第六章和第五章示例继续明确 CGP-MP 的实际有色训练归属；保存的十幅图、实验数字、冻结实现与权重保持，不把其他工况、估计相位或跨信道实验直接改称白噪声结果。本次未开启训练或新增批量实验，未修改 FINAL.json。完整白噪声批次完成后再决定最终主图和模型绑定；已有实验的真实归属先保留。这是作者新授权的执行阶段，覆盖此前“本轮只讨论第二项、不改正式稿”的范围限制，不重开其他已撤回事项。

证据：[阶段配对、修改与核验](../checks/white_mainline_revision_20261105/README.md)、[原始汇总](../checks/white_mainline_revision_20261105/PAIRED_SUMMARY.json)、[逐场景指标](../checks/white_mainline_revision_20261105/PAIRED_CASES.csv)、[术语出处](TERMINOLOGY.md)。
'''
p.write_text(t, encoding='utf-8')

s = json.loads((OUT/'PAIRED_SUMMARY.json').read_text(encoding='utf-8'))
rows = '\n'.join(f"| {r['snr_db']} | {r['white']['nmse_db']:.4f} | {r['colored']['nmse_db']:.4f} | {r['delta_nmse_db_white_minus_colored']:+.4f} | {r['white']['aer_percent']:.4f} | {r['colored']['aer_percent']:.4f} |" for r in s['comparisons'])
report = '''# 白噪声阶段配对与正文修订

2026-11-05。作者条件授权：若同场景白/有色训练结果基本接近，即开始修改正文。结论是现有样本支持移除有色训练作为主贡献；不声称两者已经通过统计等价检验。

## 固定样本与结果

统一关闭 matmul/cuDNN TF32 的新白噪声批次 `white_preconditioned_matched_fp32_1000_snr_20261105`，固定物理场景 0–197，各六档 SNR，配对 1188 次/版本。保留相同观测、信道、活动、导频、已知相位、接收机设置与评分方法；白/有色各自使用配套均值网络和密度比分类器。接收机均为 vI 标量接口，不是把物理接收噪声改成有色。旧精度不一致的白噪声批次未混入。

| SNR (dB) | 白训练 NMSE (dB) | 有色训练 NMSE (dB) | 白−有色 (dB) | 白 AER (%) | 有色 AER (%) |
|---:|---:|---:|---:|---:|---:|
''' + rows + '''

NMSE 按总误差能量/总信号能量计算，不平均单场景 dB。每档 7920 个设备判决。汇总白/有色 NMSE −13.0169/−13.0207 dB；AER 0.11995%/0.12416%，分别 57 次漏检+0 次虚警、56 次漏检+3 次虚警。白/有色平均迭代数 61.28/63.42；白噪声有一次在 −2 dB 达到 600 轮上限，保留在全部指标中，有色为零次。

使用物理场景为重采样单位的 20000 次配对 bootstrap，随机种子 202611051541，逐点 95% percentile 区间见 PAIRED_SUMMARY.json。个别档位可能有很小但可辨别的差异，不能因多数区间跨零而声称严格等价。没有预设等价界值；当前仅一个训练种子配对，历史研究场景也不是从未查看的最终测试集。该阶段判断只支持开始编辑，完整 1000 场景仍待完成。

## 修改范围

- 摘要（中英文）与引言第二项保留直接学习信道先验，改为去噪器输出及其输入导数提供均值和平均方差，无需为方差估计额外训练。引言先客观描述 Cai，再说明 Dytso/Manor 的导数关系；不宣称恒等式为本文首创。
- 第二、三章及引言第一、第三项贡献保持。第四章将 C 专门化为 vI、实协方差为 (v/2)I；保留 1/v 损失权重、有限差分方向缩放、密度比估计。第五章使用已有 GP-MP 名称和标量 v 条件。
- 预条件不出现在摘要或引言，保留为实现设置，标量系数对应 Karras §5。第六章保留有色训练实现的实际协方差采样、矩阵推广和条件输入，明确目前图表均为 CGP-MP；第五章示例同样标明归属。
- 结论同步去掉有色收益解释。十幅图及第六章结果分析、实验数值不改。模型绑定、训练权重、接收机程序和正在运行的批次不改。

## 文献和术语

[TERMINOLOGY.md](../../docs/TERMINOLOGY.md) 登记原文定位：Huang（印刷 pp.2949、2951）；Dytso（正式版 §III Prop.1 式17）；Manor–Michaeli（ICLR 2024，§3.2 Theorem 2、§4.1 Algorithm 1/式15）；Cai v2 §IV-C 式52–54；Karras §5/Table 1；Albuquerque–Pearson Appendix B.1。新增 Manor–Michaeli 书目，其“无需额外训练”只用于方差估计，接收机的两个网络仍需训练。

## 复现与文件

- `compare_saved.py`：只读保存数据，验证输入输出哈希、匹配配置并重评分，无训练或推断。
- `PAIRED_SUMMARY.json`、`PAIRED_CASES.csv`、`PAIRED_HASHES.json`：阶段结果、逐例数据及来源哈希。
- `before/`、`BEFORE_HASHES.json`：本轮修改前的完整 TeX、书目、图与两版 PDF，保留原稿。
- `verify_revision.py`、`VALIDATION.json`：公式专门化、保留内容及编译检查；`SOURCE_DIFF.txt` 为本轮文本差异。
- `rendered/`：两版 PDF 版面预览，最终编译与目视验收追加在下方。
'''
(OUT/'README.md').write_text(report, encoding='utf-8')
print('Chinese abstract and revision records updated.')
