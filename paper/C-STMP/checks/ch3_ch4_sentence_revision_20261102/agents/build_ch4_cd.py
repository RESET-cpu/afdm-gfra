import json
import pathlib
import re
import textwrap

ROOT = pathlib.Path(__file__).resolve().parents[1]
AGENTS = ROOT / 'agents'
paragraphs = [p for p in json.loads((ROOT / 'INPUT_PARAGRAPHS.json').read_text(encoding='utf-8')) if p['group'] == 'ch4_cd']

def split_sentences(text):
    text = ' '.join(text.split())
    out, start, depth, math = [], 0, 0, False
    for i, char in enumerate(text):
        escaped = i > 0 and text[i - 1] == '\\'
        if char == '$' and not escaped:
            math = not math
        if math:
            continue
        if char == '{' and not escaped:
            depth += 1
        if char == '}' and not escaped:
            depth -= 1
        if char == '.' and depth == 0 and (i + 1 == len(text) or text[i + 1] == ' '):
            out.append(text[start:i + 1].strip())
            start = i + 1
    if text[start:].strip():
        out.append(text[start:].strip())
    return out

def source(paper, location, excerpt, level, boundary):
    return dict(paper=paper, location=location, short_excerpt=excerpt,
                support_level=level, adaptation_boundary=boundary)

S = {
    'internal_variance': source('本稿既有公式与条件', 'III-B eq:exact-local-moments；IV-A eq:tweedie-mean/eq:tweedie-covariance', '', '本文推导与段落承接', '只说明本文已定义的条件矩；不是 Shen、Xu、Huang、Ding 或 Wei 的原句最小替换。'),
    'dytso': source('Dytso, Poor, and Shamai (2021)', 'PDF p.2章节概述中的短摘录；p.5，§IV，Prop.1，式(22)；p.6式(25)', 'the Jacobian of the conditional expectation to the conditional variance', '技术陈述：Gaussian 扰动下均值导数与协方差关系', '原文 Jacobian 约定与本文转置；本文采用 output-by-input，故 P=J_m Sigma，Sigma 在右。固定 C、复数实表示和除以复维度 D 是本文适配。'),
    'real': source('Huang et al. (2026)', 'PDF p.3，§III-A，式(7)后的实虚表示段', 'a two-channel real–imaginary representation', '完整搭配及相关表示方式；非方差公式来源', 'Huang 支持把复信道实部和虚部分开表示；trace/D 与 v/(2D) 的因子是本稿由 Sigma=v I_(2D)/2 推导，不能归于 Huang。'),
    'metzler': source('Metzler, Maleki, and Baraniuk (2014)', 'PDF p.18，§V-B，式(21)及随后平均估计段', 'a good approximation of the divergence can be obtained', '技术思路与原段关系：导数难直接计算→随机扰动→平均', '原文使用标准 Gaussian 探针及单侧差分；本文用独立随机符号、Sigma^(1/2) 加权及双侧差分。这些是本文已存适配，不能声称为原文公式。'),
    'probe': source('本稿既有 eq:derivative-trace', 'IV-C，随机探针定义及双侧有限差分式', '', '本文定义、代数适配', 'E[zz^T]=I_(2D)、w=Sigma^(1/2)z、L_z 个独立探针、双侧差分和按 D 归一化全部保留。'),
    'mean_map': source('本稿既有 eq:derivative-trace 与 eq:mean-preconditioning', 'IV-C 与 VI-A2', '', '本文实现条件和公式引用', '导数作用于完整均值映射，固定噪声条件 C；不是只对网络残差或预条件前的输出求导。'),
    'receiver': source('本稿既有接收机和实验设置', 'V sec:overall；VI sec:receiver-settings', '', '本文交叉引用', '保留在线白噪声条件 C=v I_D 及有限差分设置位置，不移植其他文献的接收机。'),
    'ding_ratio': source('Ding et al. (2026)', 'PDF pp.3–4，§III-B，式(14)–(16)及式(16)后的跨页句', 'the likelihood ratio between the nonzero and zero components', '同任务的技术关系与完整搭配：两假设似然比→后验概率', 'Ding 使用解析 Bernoulli–Gaussian 稀疏先验；本稿为完整信道先验边缘化后学习密度比。只借鉴概率与两假设关系，不把其稀疏支持概率等同于本稿分类学习。'),
    'internal_activity': source('本稿既有活动后验和似然', 'III-B eq:query-densities/eq:local-activity；IV-D eq:activity-log-odds', '', '本文公式的等价改写与段落承接', '完整先验积分、active/inactive 两假设、rho 的 Bayes 校正均维持原义；此处 log-odds 形式不是 Shen、Ding 的原式。'),
    'menon': source('Menon and Ong (2016)', 'PDF p.3，§4.2，式(16)–(17)及 logistic-loss 例', 'Bayes-optimal scorer', '技术陈述：分类概率、训练类先验与密度比', '本稿采用 0/1 标签及 logit，并以 (R,v) 为输入。任意有限网络只给出估计；精确关系限于总体风险、无限制 logits 的最优解。'),
    'shen_training': source('Shen et al. (2025)', 'PDF p.11，§IV-A2，数据集构造段及式(60)–(61)', 'the cross entropy is utilized as the loss function', '同任务的段落顺序及短搭配：样本构造→网络输出→交叉熵', 'Shen 为有限星座数据检测，本稿为二元活动分类；不得移植其符号先验、CNN 标签、真后验表述或数据筛选规则。'),
    'training_model': source('本稿既有分类训练分布', 'IV-D eq:classifier-loss 之前；III-B eq:query-densities', '', '本文定义与相同条件分布的核对', 'pi_tr=1/2；active 为 H+W、inactive 为 W；W 为白 Gaussian 噪声并独立于 H；两类 v 采用同一采样律。不得改成有色分类训练。'),
    'shen_features': source('Shen et al. (2025)', 'PDF p.10，§IV-A1；p.11，§IV-B', 'exploit this statistical information', '原段关系：由估计结果组成检测网络输入', 'Shen 将后验均值/不确定性组成符号检测特征；本稿输入为观测及冻结均值映射输出。仅采用关系与表达，不移植模型、性能判断。'),
    'ding_train': source('Ding et al. (2026)', 'PDF p.4，§III-C，分阶段训练首段', 'with parameters of other layers kept fixed', '完整搭配和局部训练叙述顺序', 'Ding 随后还会联合优化既有层；本稿先训 denoiser、再冻结它训 classifier，并在线全部固定。不能把两种训练方案说成相同。'),
    'deterministic': source('本稿分类器输入与 Menon and Ong (2016) 的总体风险关系', 'IV-D eq:classifier-loss/eq:ideal-logit；Menon PDF p.3，§4.2式(16)', '', '本文推论', '完整保留 R,v 为分类器输入时，附加它们的确定性函数不会改变条件后验。该确定性特征结论不是 Menon 的原句，且不扩展为有限网络训练必达最优。'),
    'definitions': source('本稿既有 logit/sigmoid 定义；Menon and Ong (2016)', 'IV-D eq:activity-probability 后；Menon PDF p.3，§4.2 logistic-loss 例', 'with the logistic loss', '标准函数与技术对应；现有定义保留', '只保留标准 logit 和 sigmoid 定义及本文活动先验校正，不新增学习目标或先验。'),
    'synthesis': source('本稿已建立的均值、方差和活动估计', 'IV-B–D；III-B sec:joint-denoising', '', '本文总结与交叉引用', '始终写为 approximations；两个训练网络与一个均值导数估计不变；不命名 MFLE/GPJD。'),
}

tasks = {
 1: ('从联合后验所需的条件方差出发，对已有均值恒等式求导得到协方差和标量方差。', '承接 IV-B 已学习的均值，下一段解释 trace 的复数归一化，不提替代二阶网络。'),
 2: ('解释 trace/D 和白噪声特例，明确同一均值函数给出所需方差。', '由精确关系自然进入学习均值及有限差分近似。'),
 3: ('用学习均值和随机双侧差分计算所需导数迹。', '先给近似对象，再给随机探针和估计式，下一段交代固定条件。'),
 4: ('说明有限差分的求导对象、固定协方差和在线使用条件。', '结束方差估计，为活动概率这一剩余后验量让出主线。'),
 5: ('由已获得的条件信道矩转到活动概率，并写为先验对数赔率加似然比。', '先指出所需概率，再给两个假设，随后引出比值的学习。'),
 6: ('指出主动似然积分未知，但活动更新只需要两似然的比值。', '从需估计的对象引出二元分类，下一段构造对应样本。'),
 7: ('定义与两假设一致的白噪声分类训练样本和交叉熵目标。', '按样本、分布、损失递进，下一段分析其总体最优解。'),
 8: ('给出无限制 logits 下总体交叉熵的最优输出。', '准确保留最优性条件，为去除训练先验做准备。'),
 9: ('从 classifier logit 中去除训练先验，代入接收机 Bayes 更新。', '密度比与接收机活动概率通过同一等价公式衔接。'),
 10: ('定义标准函数并说明 receiver prior 与 learned ratio 的关系。', '结束概率推导，下一段说明输入和训练方式。'),
 11: ('说明估计特征、分阶段训练、确定性特征的总体关系及最终输出用途。', '与第三章所需近似量对齐，同时交代在线网络固定，不扩展为算法操作清单。'),
}

# One entry per original sentence.  None means retain the original wording.
edits = {
1: [
 (r'The joint posterior moments in \eqref{eq:exact-local-moments} require both the conditional channel mean and variance.', '用 both ... and ... 将本节目标与上一节均值并列，补明 conditional，未改变估计对象。', ['internal_variance']),
 (None, '固定 C、output-by-input Jacobian 及逐项求导方向均必要，现句已直接清楚，不为换词改动。', ['internal_variance','dytso']),
 (r'Right-multiplying by $\bm\Sigma$ and using \eqref{eq:tweedie-covariance}, we obtain \cite[Prop.~1]{dytso2021}', '把矩阵右乘操作紧邻已有公式，保持协方差左右乘顺序及出处。', ['dytso','internal_variance']),
],
2: [
 (r'The trace includes the variances of the real and imaginary components; division by $D$ therefore gives the variance per complex coordinate.', '明确迹中求和的对象是实虚分量方差，保留复维度 D，避免读成除以 2D。', ['real','internal_variance']),
 (None, '白噪声特例和 1/(2D) 因子准确且简洁，保留。', ['dytso','internal_variance']),
 (r'Thus, the required conditional variance can be computed from derivatives of the conditional mean.', '压缩 can be obtained from derivatives of the same ...，明确量为 conditional variance，自然承接而不作网络对比。', ['dytso','internal_variance']),
],
3: [
 (r'We estimate this trace using Monte Carlo finite differences \cite[Sec.~V-B]{metzler2014}, with $f_\theta$ in place of the conditional mean.', '引文紧跟 Monte Carlo finite differences，使 Metzler 只支撑导数迹估计方法；随后单独说明本文以 f_theta 近似条件均值，避免技术归属混淆。', ['metzler','probe']),
 (r'Let $\mathbf z_\ell$ be independent random sign vectors with $\E[\mathbf z_\ell\mathbf z_\ell^{\mathsf T}]=\I_{2D}$, and define $\mathbf w_\ell=\bm\Sigma^{1/2}\mathbf z_\ell$.', '将操作式 set 改为连贯数学定义句，随机符号、独立性及加权关系逐项不变。', ['probe']),
 (r'The resulting estimate is', '补 resulting 明确下式由刚定义的探针与差分构成；仅是本稿公式引出语，不冒称文献母句。', ['probe']),
],
4: [
 (r'The finite differences in \eqref{eq:derivative-trace} hold $C$ fixed and act on the complete mean map, including the preconditioning in \eqref{eq:mean-preconditioning}.', '将不够准确的“two evaluations differentiate”改为“finite differences act on”；所求完整均值及固定 C 条件不变。', ['mean_map']),
 (r'The conditional variance estimates used in message passing are then obtained by setting $C=v\I_D$.', '承接前句差分式，自然给出在线白噪声取值；不把训练有色条件写成在线全协方差推断。', ['receiver']),
 (None, '两项交叉引用有明确对象，保留已有实现与有限差分设置位置。', ['receiver']),
],
5: [
 (r'Having obtained the conditional channel mean and variance, we next consider the activity probability.', '将已完成的信道矩计算直接作为转向活动概率的前提，减少先总结再重新起句的停顿。', ['internal_activity']),
 (r'This probability depends on the likelihoods under the active and inactive hypotheses.', '前句已提出下一目标，此句只保留两假设似然关系，避免再次复述 remaining quantity。', ['ding_ratio','internal_activity']),
 (r'Taking the log odds of \eqref{eq:local-activity} gives', '明确 rewriting 的具体数学操作，与下式 log posterior odds 的对象一致。', ['internal_activity','menon']),
],
6: [
 (None, '已准确区分已知 inactive likelihood 和需积分 active likelihood，保留。', ['internal_activity']),
 (None, '简洁说明当前公式只需比值，是引出分类学习的关键，不添加额外防御。', ['internal_activity','menon']),
 (r'We learn this density ratio through binary classification using samples from the full channel prior \cite{menon2016}.', '将密度比、分类方式和完整信道样本连成一个目标句，Menon 仍为技术出处。', ['menon','training_model']),
],
7: [
 (r'The training data contain two classes with equal prior probability, $\Pr(a=1)=\pi_{\rm tr}=1/2$, where $a\in\{0,1\}$.', '把 draw 命令改为训练分布的叙述；类先验、a 的取值完整保留。借鉴 Shen 先构造训练数据再讲损失的段落任务。', ['shen_training','training_model']),
 (r'For $a=1$, the observation is $R=H+W$ with $H\sim q_{\rm tr}$; for $a=0$, it is $R=W$.', '从操作清单式 generate 改为两类观测的平行定义，条件模型不变。', ['training_model']),
 (r'The noise satisfies $\vect(W)\sim\CN(\mathbf0,v\I_D)$ independently of $H$, and both classes use the same sampling law for $v$.', '将两类同一 v 采样律表述为共同训练条件，保留白噪声与信道独立性。', ['training_model']),
 (r'The resulting class-conditional densities are therefore those in \eqref{eq:query-densities}.', '用 therefore 连接刚定义的样本与第三章似然；移除多余程度词 precisely，不降低相同分布的结论。', ['training_model','internal_activity']),
 (r'The classifier logit is learned by minimizing the binary cross-entropy loss', '采用训练目标承接网络输出的常规论文表述；保留 logit 而不误写为直接监督真实密度比。', ['shen_training','menon']),
],
8: [
 (None, 'population optimum 与 unrestricted logits 是精确结论的关键条件，原句精确自然，保留。', ['menon']),
],
9: [
 (None, '训练先验 log odds 的相减操作、估计性质与 Menon 技术归属准确，保留。', ['menon','internal_activity']),
 (r'With $F_k=F_\theta(R_k,v\I_D)$, inserting this estimate into \eqref{eq:activity-log-odds} gives the receiver activity probability', '补出 substitution 的对象 this estimate，直接承接上一句得到的 log density ratio。', ['internal_activity','menon']),
],
10: [
 (None, '标准函数定义无需为改写而换写，也不增加新名称。', ['definitions']),
 (None, '准确概括 receiver prior 与 learned ratio 的分工，保留 Bayes 校正并不主张新的技术结论。', ['internal_activity','menon']),
],
11: [
 (r'The classifier takes the observation together with $F_k$ as input, incorporating the channel estimate obtained from the learned prior.', '采用 Shen 的估计统计量进入检测网络这一关系，保留本文观测和信道均值两类输入，未照搬其符号检测内容。', ['shen_features','training_model']),
 (r'The denoiser is trained first and then kept fixed during classifier training.', '采用 Ding 已核实 kept fixed 搭配叙述先后训练，清楚交代冻结对象；不移植其后续联合解冻。', ['ding_train','training_model']),
 (r'The denoiser output is a deterministic function of $R$ and $v$, so the population relation in \eqref{eq:ideal-logit} remains valid.', '用 so 说明确定性附加特征与总体关系之间的因果；不将该关系推广为有限网络性能保证。', ['deterministic']),
 (None, '概括三种计算提供第三章所需近似量，approximation 强度恰当，保留。', ['synthesis']),
 (None, '在线网络保持固定是模型条件，短句已清楚，不作无益替换。', ['training_model','receiver']),
],
}

text = (AGENTS / 'ch4_cd_input.tex').read_text(encoding='utf-8')
reviews = []
paragraph_review = []
for p in paragraphs:
    number = int(p['id'].rsplit('P', 1)[1])
    original_sentences = split_sentences(p['text'])
    assert len(original_sentences) == len(edits[number]), (number, len(original_sentences))
    revised_sentences = []
    task, transition = tasks[number]
    for i, (original, edit) in enumerate(zip(original_sentences, edits[number]), 1):
        revised, reason, keys = edit
        revised = original if revised is None else revised
        revised_sentences.append(revised)
        reviews.append(dict(paragraph_id=p['id'], sentence_id=f"{p['id']}-S{i:02d}",
                            original=original, revised=revised,
                            decision='retain' if revised == original else 'revise',
                            reason_zh=reason, source=[S[k] for k in keys],
                            paragraph_task_zh=task, transition_zh=transition))
    revised_paragraph = '\n'.join(textwrap.fill(s, width=76, break_long_words=False,
                                               break_on_hyphens=False) for s in revised_sentences)
    assert text.count(p['text']) == 1, p['id']
    text = text.replace(p['text'], revised_paragraph)
    paragraph_review.append(dict(paragraph_id=p['id'], task_zh=task, transition_zh=transition,
                                 sentence_count=len(original_sentences)))

original = (AGENTS / 'ch4_cd_input.tex').read_text(encoding='utf-8')
blocks = lambda t: re.findall(r'\\begin\{equation\}.*?\\end\{equation\}', t, re.S)
assert blocks(original) == blocks(text), 'Display equations changed'
assert len(blocks(text)) == 6
assert len(paragraph_review) == 11
assert len(reviews) == 33
(AGENTS / 'ch4_cd_proposed.tex').write_text(text, encoding='utf-8')
(AGENTS / 'ch4_cd_review.json').write_text(json.dumps(reviews, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
(AGENTS / 'ch4_cd_paragraphs.json').write_text(json.dumps({
  'paragraphs': paragraph_review,
  'source_selection_zh': {
    'Shen': '已读 PDF pp.7、9–11。取估计统计量→检测输入、训练数据→交叉熵的段落任务与短搭配；其符号检测和离散先验不移植。',
    'Ding': '已读 PDF pp.3–5。取似然比与后验概率关系及 kept fixed 搭配。本文密度比学习和冻结训练不同，逐句登记。',
    'Huang': '已读 PDF p.3。实虚表示可作相关搭配依据；不为本文 trace/D 推导背书。',
    'Wei': '已读 PDF p.3 §III-C/D。该文方差为压缩残差经验估计，且含显式 STMP 对比；不适用于本文均值导数推导，因此不强行替换。',
    'Xu': '已读 sources/xu_reading.md 中网页抽取锚点，IV-A/B 印刷 pp.7–8、式(49)–(64)。其离散数据检测/EP 不能作为本稿均值导数或分类密度比技术来源，本组不强行使用。',
    'Dytso/Metzler/Menon': '实际读取 full_terminology_audit_20261030/source_text 中原文缓存；继续保持对应真实技术引用，本文特定适配单独登记。'
  },
  'checks': {'paragraphs': 11, 'sentences': 33, 'display_equations': 6,
             'display_equations_byte_equal': True,
             'formal_sections_modified': False},
  'semantic_notes_zh': [
    'P04-S01修正语言动作：函数求值并不“differentiate”，现在由 finite differences 作用于完整均值映射；不是算法修改。',
    'P08总体无限制 logits 的最优性、P11确定性附加特征及在线固定条件保留。',
    '6个陈列公式逐字相等。随机符号双侧差分、D/2D归一化、固定C、在线C=vI、白噪声分类、两类v同采样律全部保留。',
    '未把通用句型或部分搭配登记为整句母本，也未声称逐句由五篇文献替换；本文推导如实标记。'
  ]
}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'paragraphs': len(paragraph_review), 'sentences': len(reviews),
                  'retained': sum(r['decision'] == 'retain' for r in reviews),
                  'revised': sum(r['decision'] == 'revise' for r in reviews),
                  'display_equations_unchanged': len(blocks(text))}))
