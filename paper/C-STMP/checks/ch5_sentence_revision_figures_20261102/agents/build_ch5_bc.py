import json
import pathlib
import re
import textwrap
import difflib
import hashlib

HERE = pathlib.Path(__file__).resolve().parent
inputs = json.loads((HERE / 'ch5_bc_input_paragraphs.json').read_text(encoding='utf-8'))
original = (HERE / 'ch5_bc_input.tex').read_text(encoding='utf-8')

def source(paper, location, anchor, level, adaptation):
    return dict(paper=paper, location=location, short_anchor=anchor,
                support_level=level, adaptation=adaptation)

S = {
 'fixed': source('Shen et al. (2025)；本文既有前端', 'Shen PDF p.7，§III-B首段；本文 eq:effective-pilot 与 app:frontend', 'the noise variance, and the parameters', '原段关系：先交代给定参数，再进行后验消息计算；本文条件', 'Shen随后用EM更新参数，本稿前端输出在消息传递期间固定。只取交代已知量的叙述关系，不移入Shen的迭代EM更新。'),
 'phase': source("O’Leary–Rust (2013)", 'PDF pp.2、4，§1式(2)–(3)、§2式(5)–(6)', 'separable least squares problem', '技术来源与既有术语', '给定非线性参数后以最小二乘消去线性增益；本稿逐设备相位估计与前端调用安排属本文适配，引用保持。'),
 'mdl': source('Nadakuditi–Edelman (2008)', 'PDF pp.2–3／印刷pp.2626–2627，§II-A，式(5)–(7)及随后算术均值定义', 'sample covariance matrix (SCM)', '技术陈述及标准术语', '沿用文中回顾的Wax–Kailath MDL，以空间秩和尾部特征值拟合白噪声；不将信号秩写成设备数，不改成该文后续新估计器。低秩信号加白噪声条件保留。'),
 'internal_front': source('本文既有参数估计流程', 'V-B与Appendix app:frontend', '', '本文定义和交叉引用', '观测矩阵、物理噪声估计的构成与固定使用方式保持；不是另引文献的同一接收机。'),
 'vila': source('Vila–Schniter (2013)', 'PDF p.4／印刷p.4661，§III-A，式(22)–(27)', 'EM Update of the Gaussian Noise Variance', '技术关系：固定当前后验的期望似然→方差更新', '本稿在局部模型中更新输入方差v，不把它改称物理噪声估计或全局EM；本文复杂数据、活动混合后验、KD维度及后验方差均保留。缓存公式抽取缺符号，具体数学逐项保持本文原式，并依既有术语账本记录定位。'),
 'shen_update': source('Shen et al. (2025)', 'PDF p.9，§III-C，式(47)–(59)，特别式(56)', 'Based on the previous approximated posterior distributions', '原段推进关系：近似后验→参数目标→更新；残差和后验方差的相关构成', 'Shen式(56)更新物理观测噪声，本稿更新局部去噪输入方差；仅参考推导顺序与残差加不确定性的解释，不移植参数或算法。'),
 'internal_scale': source('本文既有方差目标和尺度更新', 'eq:query-variance-target；eq:query-variance-update；eq:mixture', '', '本文推导和迭代调度', '固定近似后验、KD归一化、通道与活动不确定性、kappa乘damped MFLE variance、下一轮才应用更新均保留。'),
 'cai_norm': source('Cai et al. (2026), arXiv v2', 'PDF p.10，§V-B2，式(59)–(65)', 'Channel Power Normalization', '论述任务：说明训练和推断的尺度关系；本文具体归一化', 'Cai按样本功率归一化并在线估计输入尺度；本稿使用训练集系数的固定RMS。不移植Cai的样本依赖公式，不声称本稿与其归一化一致。'),
 'cai_damping': source('Cai et al. (2026), arXiv v2', 'PDF pp.9–10，§V-B1，式(57)–(58)及其后对另一模块的说明', 'a linear combination of the current and previous updates', '技术关系及短表达：均值与方差的迭代阻尼', '本文保留已有eta、i>=2、当前已阻尼消息与新外信息的组合及两方向阻尼；不更改Cai/本文之间的具体历史索引差别。'),
 'internal_num': source('本文既有数值实现与Algorithm 1', 'eq:nonlinear-extrinsic；eq:input-damping；eq:output-damping；eq:gaussian-evidence；sec:simulation-settings', '', '本文实现条件和交叉引用', '训练方差范围之外保留Gaussian sites；裁剪区间和首轮不阻尼保持。仅陈述操作，不补回正值性或合法性解释。'),
 'stopping': source('Cai et al. (2026), arXiv v2；Huang et al. (2026)', 'Cai PDF p.10 Algorithm 2终止行；Huang PDF p.4 Algorithm 1 while条件', 'the stopping criterion is met', '原段/伪代码任务：终止规则及迭代上限；非相同判据', '本文保持估计与accepted site updates稳定或达到最大次数的既有判据；不移入Huang的Langevin相对变化阈值，不声称收敛保证。'),
 'internal_svd': source('本文既有矩阵模型与SVD展开', 'eq:linear-variance至eq:linear-extrinsic；eq:linear-fraction', '', '本文代数变换及复杂度计算', '块内固定观测矩阵、thin SVD、完整Gram矩阵及本文尺寸保留；不套用Cai部分正交/FFT或Wei行正交简化。'),
 'cai_complexity': source('Cai et al. (2026), arXiv v2', 'PDF p.11，§V-C复杂度完整段', 'the computational costs of a forward pass', '完整搭配与原段关系：矩阵运算、网络前向次数→单次迭代复杂度', '本文网络为denoiser和classifier，含1+2L_z次denoiser调用；C_theta/C_phi定义、逐设备K倍及矩阵量级来自本文，不能登记为Cai原公式。'),
 'shen_complexity': source('Shen et al. (2025)', 'PDF p.10，§III-C末复杂度段', 'For each iteration', '原段关系：逐项操作成本→合计；常规成本陈述', '只参考按矩阵乘法、模块操作、参数估计分解成本的顺序；本文SVD/空间协方差/前端成本均独立保留，不移植其复杂度或稀疏可忽略结论。'),
 'ding_complexity': source('Ding et al. (2026)', 'PDF p.5，§III-D，式(29)前后', 'the real-valued floating-point operations', '参考比较：运算分解及网络成本；未直接采用FLOP计数', 'Ding给具体层级FLOPs，本文只保留原有大O计算量及网络成本符号，不混淆计量单位、不移植其GNN结构独立性结论。'),
 'huang_complexity': source('Huang et al. (2026)', 'PDF p.4，§IV Table II及其后网络评估成本说明', 'with K network evaluations', '原段关系：网络单次成本×评估次数', 'Huang的K为采样网络调用数，本文K为设备数；仅参考计次叙述，本文明确1+2L_z次与每设备成本，不移植其符号或采样算法。'),
 'internal_storage': source('本文既有尺寸与参数共享实现', 'V-C；eq:linear-fraction；本文KN×MN消息、M×M空间协方差', '', '本文计算量/工作存储计数', '给定phases时C_phase=0；共享训练权重；工作存储不包含权重和网络激活。各项量级逐字保留，不作外部原句来源认定。'),
}

tasks = {
1: ('明确后验计算所用观测矩阵和物理噪声从何得到，最后落实迭代期间固定。', '由前端参数转向下一段迭代内局部输入方差，二者不混同。'),
2: ('固定当前近似后验，从期望Gaussian负对数似然得到输入方差目标。', '目标函数→最小化→残差加后验不确定性；下一段解释并平滑更新。'),
3: ('解释目标中的两类误差，并定义当前方差尺度及其下一轮更新。', '将推导量v_tar接到已阻尼MFLE variance与kappa调度。'),
4: ('交代当前方差同时用于联合去噪和外信息，更新后的尺度从下一轮使用。', '保持反馈与去噪使用同一当前v，随后转向固定尺度和阻尼。'),
5: ('说明训练与在线的共同固定尺度，再给MFLE输出阻尼。', 'RMS归一化→消息线性组合；不引入Cai逐样本功率归一化。'),
6: ('给反馈比值的既有裁剪及反馈阻尼。', '从MFLE侧阻尼接到反馈侧，不补防御性合法性分析。'),
7: ('收束首轮、范围外处理和停止条件，并指向详细设置。', '将实现条件交代完整后进入计算量。'),
8: ('利用块内矩阵固定说明SVD复用，并给标量更新的等价计算。', '由算法运算形式进入一次性分解成本和每轮成本。'),
9: ('逐项统计块内一次性成本、每轮矩阵成本和网络评估成本。', 'C_theta/C_phi先定义，调用次数随后明确，最后合成C_iter。'),
10: ('将初始化和每轮成本合并为I次迭代的总量上界。', '接到给定相位特例和工作存储。'),
11: ('说明提供相位时的简化、参数共享和工作存储。', '完成复杂度分析，范围仍仅是在线工作空间。'),
}

# Each item corresponds to one original sentence unit, including formula-introducing clauses.
edits = {
1: [
 (r'Before message passing, we determine the observation matrix $\widehat{\mathbf A}$ and physical noise variance $\widehat\sigma^2$ used in the posterior calculations.', '用先确定参数的叙述引出估计方法，固定使用条件仍由本段末句明确，消除首尾重复。', ['fixed','internal_front']),
 (None, '相位可用/未知两种情况、variable projection出处和矩阵构造关系已经清楚，保留。', ['phase','internal_front']),
 (r'For a lower-rank spatial signal plus white noise, the noise variance is estimated from the trailing eigenvalues of the spatial sample covariance.', '把低秩加白噪声条件放在句首，直接说明尾部特征值的用途，下一句再说明如何选择其范围；不增加理想分离保证。', ['mdl']),
 (r'After the minimum description length (MDL) criterion selects the signal rank, the mean of the remaining eigenvalues gives $\widehat\sigma^2$ \cite{nadakuditi2008}.', '将秩选择与尾部平均的先后依赖写清，公式对象、MDL全称和原引用保持。', ['mdl']),
 (None, '已有附录引用准确指向两项估计器，无需为了换词而修改。', ['internal_front']),
 (None, '这是固定前端与迭代内输入方差更新的必要区别，保留。', ['internal_front','fixed']),
],
2: [
 (None, '局部方差的物理对象和线性估计后的用途已经明确，保留。', ['internal_scale']),
 (None, '固定当前近似后验是所述最小化的关键条件；句意与Vila技术关系一致，保留。', ['vila','shen_update']),
 (None, '候选方差与目标的对应项完整且无多余修饰，保留原行内公式。', ['vila','internal_scale']),
 (None, '已经按最小化→展开平方误差引出下式，直接推进推导，不作同义替换。', ['vila','shen_update','internal_scale']),
],
3: [
 (r'The first term is the average squared residual of the posterior mean, while $\overline t_X$ accounts for the remaining channel and activity uncertainty.', '将误称为“error of the posterior mean”的含糊表述具体化为平均平方残差，避免读成真实估计误差；另一项不确定性含义保持。', ['shen_update','internal_scale']),
 (r'At iteration $i$, we use $v^{(i)}=\kappa^{(i)}\bar v^{(i)}$, where $\bar v^{(i)}$ denotes the damped MFLE variance.', '将当前迭代使用的量放在主句、辅助定义放在where从句，保持原有尺度关系。', ['internal_scale']),
 (None, '新消息权重的取值范围及“next scale”准确引出更新式，保留。', ['internal_scale','cai_damping']),
],
4: [
 (None, '这句明确同轮使用当前v、下一轮应用更新尺度，属于必要调度，不是防御性说明。', ['internal_scale']),
],
5: [
 (None, '固定归一化是本稿必要训练/推断条件，保留。', ['cai_norm','internal_front']),
 (r'Let $s$ denote the root mean square of the training-channel coefficients. We divide $(H_k,X_k,\mathbf Y,\mathbf W)$ by $s$ and the physical noise variance by $s^2$, retaining the same symbols for normalized quantities.', '将条件式If改为实际使用的尺度定义，再说明信号和方差的缩放，原定义和归一化量均不变。', ['cai_norm','internal_front']),
 (None, '保留归一化不作用于导频矩阵这一模型条件。', ['internal_front']),
 (r'The MFLE output is damped by combining the current and previous messages \cite[Sec.~V-B1]{cai2026} for $i\geq2$:', '采用Cai已核实的当前/前一消息线性组合关系，直接引出本文阻尼式，不加入稳定性保证。', ['cai_damping']),
],
6: [
 (None, '只陈述已有比值裁剪和epsilon范围，无额外正值性辩解，保留原定义。', ['internal_num']),
 (None, '简明承接输入侧阻尼并明确反馈使用同一权重，保留。', ['cai_damping','internal_num']),
],
7: [
 (None, '首轮不阻尼是实际算法条件，保留。', ['internal_num']),
 (None, '训练方差范围外的Gaussian sites和活动比值来源是算法所需分支，保留。', ['internal_num']),
 (r'Iterations continue until the estimates and accepted site updates have stabilized or the maximum iteration count is reached.', '用until统一两个终止分支，保留accepted site updates及迭代上限，不主张必然收敛。', ['stopping','internal_num']),
 (None, '详细判据和数值设置已有唯一位置，保留。', ['internal_num']),
],
8: [
 (None, '固定矩阵→thin SVD复用已形成准确因果链，保留全部尺寸和分解式。', ['internal_svd']),
 (r'With this decomposition, the scalar updates in \eqref{eq:linear-variance}--\eqref{eq:linear-extrinsic} can be written as', '明确下式是SVD下的标量更新写法，避免笼统become将整套矩阵公式都等同于三个标量式。', ['internal_svd']),
],
9: [
 (None, '外信息均值由f_L表示的等价式正确，保持。', ['internal_svd']),
 (r'For $Q\leq KN$, computing the SVD requires $O(KNQ^2)$ operations once per transmission block.', '使用计算对象→成本→频率的完整句式，保留Q条件和一次性成本。', ['shen_complexity','internal_svd']),
 (r'Noise estimation requires $O(QNM^2+M^3)$ operations. The phase-search, refinement, and gain-refitting cost in Appendix~\ref{app:frontend} is denoted by $C_{\rm phase}$.', '将噪声成本和相位成本定义拆成两句，使两个前端代价的对象分别清楚，数值量级不变。', ['shen_complexity','internal_front']),
 (None, '三个并列运算与量级一一对应、已较简洁，保留，不套用别篇模块计数。', ['shen_complexity','ding_complexity','internal_svd']),
 (r'Let $C_\theta,C_\phi$ denote the per-device denoiser and classifier costs. Within the training interval, GPJD requires $1+2L_z$ denoiser evaluations and one classifier evaluation.', '先定义每设备成本，再给GPJD网络评估次数，去掉不必要的假设式If；保留训练区间限制和所有调用数。', ['cai_complexity','huang_complexity','internal_scale']),
 (r'The resulting per-iteration complexity is', '直接引出合计成本，与前文分项同一对象，未新增结论。', ['cai_complexity','shen_complexity']),
],
10: [
 (None, '总复杂度是I次迭代的上界，条件及结论强度均准确，保留。', ['cai_complexity','internal_svd','internal_front']),
],
11: [
 (None, '已提供相位时的成本简化是实际特例，保留。', ['internal_storage']),
 (None, '共享参数这一实现条件简洁明确，保留。', ['internal_storage']),
 (r'The working storage for the pilot/SVD factors, channel messages, and spatial covariance matrices is $O(QKN+KMN^2+KM^2)$, excluding trained parameters and network activations.', '将所统计的工作存储对象置于句首，排除范围放在句末，所有量级和边界保持。', ['internal_storage']),
],
}

proposed = original
reviews = []
for index, p in enumerate(inputs, 1):
    assert len(p['sentences']) == len(edits[index])
    task, transition = tasks[index]
    changed = []
    for j, (before, edit) in enumerate(zip(p['sentences'], edits[index]), 1):
        after, reason, keys = edit
        after = before if after is None else after
        changed.append(after)
        reviews.append(dict(paragraph_id=p['id'], sentence_id=f"{p['id']}-S{j:02d}",
                            before=before, after=after,
                            action='retain' if before == after else 'revise',
                            reason=reason, source=[S[k] for k in keys],
                            paragraph_task=task, transition=transition))
    replacement = '\n'.join(textwrap.fill(s, width=76, break_long_words=False,
                                          break_on_hyphens=False) for s in changed)
    assert proposed.count(p['text']) == 1, p['id']
    proposed = proposed.replace(p['text'], replacement)

block = lambda s: re.findall(r'\\begin\{equation\}.*?\\end\{equation\}', s, re.S)
assert block(proposed) == block(original)
assert len(block(proposed)) == 7
inline = lambda s: sorted(re.sub(r'\s+', '', x) for x in re.findall(r'(?<!\\)\$(.*?)(?<!\\)\$', s, re.S))
assert inline(proposed) == inline(original)
cite = lambda s: re.findall(r'\\cite(?:\[[^]]*\])?\{[^}]+\}', s)
assert cite(original) == cite(proposed)
assert len(reviews) == 36
for r in reviews:
    assert ' '.join(r['after'].split()) in ' '.join(proposed.split())
(HERE / 'ch5_bc_proposed.tex').write_text(proposed, encoding='utf-8')
(HERE / 'ch5_bc_review.json').write_text(json.dumps(reviews, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
(HERE / 'ch5_bc_changes.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True), proposed.splitlines(True), fromfile='ch5_bc_input.tex', tofile='ch5_bc_proposed.tex')), encoding='utf-8')
revised = sum(r['action'] == 'revise' for r in reviews)
notes = f'''# 第五章 B/C 逐句核对记录

覆盖现有 V-B Parameter Estimation and Numerical Implementation 与 V-C Computational Complexity Analysis：11 个公式前后文字单元、36 个原句单元；修改 {revised} 个，保留 {36-revised} 个。公式引出从句也作为一个可核对单元。三处长句拆为两句，原句覆盖以逐句 JSON 为准。

## 已读规范与原文

- 已读 WRITING_GUIDE.md；核对 TERMINOLOGY.md 中 variable projection、MDL、Vila variance update、SVD、damping、固定训练RMS及本日修订条目。
- Cai v2：PDF pp.9–11，V-A/B/C；实际重读p.10阻尼、功率归一化及Algorithm 2，p.11完整复杂度段。
- Shen：PDF p.7 III-B给定参数说明；p.9 III-C参数学习及式(47)–(59)；p.10算法、阻尼及完整复杂度段。
- Ding：PDF p.5 III-D，式(29)及其前后运算分解。未把FLOP计数或GNN结构结论移入本稿。
- Huang：PDF p.4 Algorithm 1、Table II及网络评估次数的复杂度段。只参考终止条件和网络计次的表述，不移入Langevin算法。
- Wei：PDF pp.2–3 III-A/B/C/D。该文固定压缩矩阵、层参数校准和残差方差与本稿前端及kappa更新不同；本组没有为了覆盖作者而强行套用。
- O’Leary–Rust：既有全文缓存PDF pp.2、4，线性参数消去及变量投影；Nadakuditi–Edelman：pp.2–3，MDL回顾及尾部样本特征值；Vila–Schniter：PDF p.4/印刷p.4661，III-A式(22)–(27)。Vila缓存数学符号抽取不全，本轮不根据缺损文本改动公式。

## 修改重点

1. 从前端参数的确定进入后验计算，明确两项输出在消息传递期间固定。低秩空间信号加白噪声的前提保留；MDL选秩之后才做尾部均值。
2. 保留固定后验下的Gaussian目标推导。将“posterior mean的error”具体化为平均平方残差，并让当前v、kappa及damped MFLE variance的定义更容易连续阅读。
3. 以实际RMS定义引出归一化，保持本文固定训练尺度；阻尼直接说明当前与先前消息的组合，不增加数值正值性或收敛保证。
4. 复杂度保持一次性前端/SVD、每轮矩阵与网络、I轮总量、工作存储的顺序。分别给出前端代价和每设备网络成本，所有量级不变。

## 检验

- 七个陈列公式逐字相等。
- 行内数学规范化后的多重集完全相等。
- 四个原引用命令及其顺序完全相等。
- 36个逐句after均在候选正文中匹配。
- 固定近似后验、低秩加白噪声、eta/epsilon范围、首轮不阻尼、训练方差范围外分支、accepted site updates及最大迭代次数全部保留。
- 正式稿、PDF、README和术语文件未写入；父代理负责集成和编译。

未发现需改变算法的语义问题。来源账本区分文献技术来源、原段顺序、短表达和本文推导；没有将本文前端、全协方差SVD或工作存储量级登记成Cai等人的原式，也没有声称通过措辞改写获得查重保证。

输入片段SHA-256：`{hashlib.sha256(original.encode()).hexdigest()}`。
'''
(HERE / 'ch5_bc_notes.md').write_text(notes, encoding='utf-8')
print(json.dumps(dict(paragraphs=11, original_sentence_units=36, revised=revised,
                     retained=36-revised, equations_unchanged=7,
                     inline_math_equal=True, citation_commands_equal=True)))
