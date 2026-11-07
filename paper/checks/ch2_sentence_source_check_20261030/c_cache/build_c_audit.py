import json, re, hashlib
from pathlib import Path
from collections import Counter

root = Path(r'D:/afdm-gfra/paper/C-STMP/checks/ch2_sentence_source_check_20261030')

def ref(key, page, section, quote=None, locator=None, eq=None, role='content_support'):
    d=dict(key=key,page=page,section=section,role=role)
    if quote is not None: d['quote']=quote
    if locator is not None: d['locator']=locator
    if eq is not None: d['eq']=eq
    return d

c4='PDF p.4 / journal p.3578'
c5='PDF p.5 / journal p.3579'
c2='PDF p.2 / journal p.3576'
c7='PDF p.7 / journal p.3581'
h3='PDF p.3 / journal p.2951'
activity = ref('cai2026',c4,'II-A',
    'We use an indicator function αk to model the device activity as',eq='(1)',
    locator='Left column, below Table I; cases: 1, if the k-th device is active; 0, otherwise.')
prob = ref('cai2026',c4,'II-A',
    'Let λ represent the probability of a device being active, i.e., p(αk = 1) = λ, where λ ≪ 1.',eq='after (1)')
rx = ref('cai2026',c4,'II-A',
    'After removing the CP and applying the DFT, the received signal Yt ∈ C^{N×M} during the t-th OFDM symbol is given by',
    eq='(3)',locator='Right column; Y_t = sum_k α_k Q_kt H_k + N_t, with Q_kt diagonal.')
noise = ref('cai2026',c4,'II-A',
    'where Nt ∈ C^{N×M} is an AWGN matrix with the elements i.i.d. drawn from CN(0, δ_0^2).',eq='where after (3)')
mmv = ref('cai2026',c4,'II-A',
    'We express the received signal Y over the T OFDM symbols in a more compact form as',
    eq='(4)',locator='Y: NT×M; Q: NT×NK; X: NK×M. Stacks received subcarriers and time vertically.')
shen_collect=ref('shen2025','PDF p.5','II-C',
    'Next, we collect the Q received frames into a single matrix as',eq='(15)',
    locator='Collects OTFS observations Y_q^l over frames; this is not the present AFDM indexing.')
full=ref('huang2026',h3,'III-A',
    'Since we directly estimate the full AFDM effective channel matrix Heff without imposing sparsity assumptions, using only one pilot sequence makes (6) underdetermined, so that multiple pilot sequences are required.',eq='after (6)')
block=ref('cai2026',c4,'II-A',
    'Due to the sporadic access of the devices, matrix X exhibits a block-sparsity structure. Specifically, if the k-th device is inactive, we have Xk = αkHk = 0.',eq='after (4)')
objective=ref('cai2026',c4,'II-B',
    'In this paper, we aim to simultaneously detect the active devices and estimate the corresponding channels based on the observation Y under a Bayesian inference framework.')
factor=ref('cai2026',c4,'II-B',
    'In message passing, we factorize the joint posterior distribution according to Baye’s theorem and the conditional independence relationships among the variables, expressed as',
    eq='(5)',locator='p(X,{H_k},{α_k}|Y) ∝ product_m p(y_m|x_m) product_k p(X_k|H_k,α_k)p(H_k)p(α_k).')
where=ref('cai2026',c5,'II-B',
    'where xm ∈ C^{NK} and ym ∈ C^{NT} denote the m-th column of X = [x1, ..., xM] and Y = [y1, ..., yM], respectively.',eq='where after (5)')
table=ref('cai2026',c5,'II-B, Table II',locator='Table II rows: p(y_m|x_m)=CN(Qx_m,δ_0²I_NT); p(X_k|H_k,α_k)=δ(X_k−α_kH_k); p(H_k) unspecified; p(α_k)=(1−λ)δ(α_k)+λδ(1−α_k).')
nonsep=ref('cai2026',c2,'I-A',
    'Moreover, unlike the separable denoisers in [5], [6], [11], and [27] that operate element-wise for channel denoising, our TMP framework models the spatial-frequency channel matrix as a super node in the factor graph, enabling the incorporation of score-based generative models as non-separable denoisers for more effective exploitation of channel correlations.')
learn=ref('cai2026',c2,'I, paragraph 2',
    'In light of the limitations of model-based approaches in accurately capturing the real wireless propagation environments, deep learning offers a powerful alternative by learning the channel distribution directly from data.')
htrain=ref('huang2026',h3,'III-B, where after (9)',
    'which encourages the estimate to conform to the channel distribution learned during training and can be approximated by the trained network sθ.',
    locator='Quoted clause modifies the prior score ∇log p(H_eff^(i)); no q_tr notation or plug-in likelihood.')
integrals=ref('cai2026',c4,'II-B',
    'Exact Bayesian estimators, e.g., the MMSE estimator, are generally intractable due to the high-dimensional integrals in the marginalization of the joint posterior distribution p(X,{Hk}_{k=1}^K,{αk}_{k=1}^K|Y).')
mp=ref('cai2026',c4,'II-B',
    'Alternatively, message-passing algorithms [5], [6], [27], [47] provide a low-complexity iterative approach for approximately calculating the MMSE estimator.')
gen=ref('cai2026',c5,'II-B, concluding paragraph',
    'This paper seeks to address the aforementioned challenges by plugging in deep generative priors for efficient message calculation.')
avoid=ref('cai2026',c5,'II-B, continuation above III',
    'This insight enables the integration of score-based generative networks for provable MMSE denoising, eliminating the need to compute high-dimensional integrals.')

data={}
def add(p, start, category, refs, changes, reason, technical, formula, action, alignment=None):
    d=dict(category=category,source_refs=refs,changes=changes,reason=reason,
           technical_status=technical,formula_adaptation=formula,action=action)
    if alignment: d['language_alignment']=alignment
    data.setdefault(p,[]).append((start,d))

add('P09','Let $\\alpha_k$', 'SUPPORTED_PARAPHRASE',[activity,ref('cai2026_stmp_v2','PDF p.4','II-A',locator='Same indicator sentence and cases (1) as the formal version.',eq='(1)')],
    ['“We use an indicator function ... to model the device activity as”改为“Let ... denote the activity indicator of device k”.','二值分段公式保留，标点/排版作适配。'],
    '活动定义及 cases 可逐项定位，但引导句换了主谓结构；不是只替换术语。',
    'SUPPORTED: α_k∈{0,1}的定义与Cai一致。',
    '分段公式与Cai (1)同义；本稿只延续同一活动变量，未加入新的随机假设。',
    '若严格执行原句要求，可回到Cai的完整引导句并仅替换对象称呼；现稿应标支持性改写。')
add('P09','The activity probability', 'SUPPORTED_PARAPHRASE',[prob],
    ['λ→ρ、p→Pr是符号替换。','“Let λ represent the probability of a device being active”改成被动语态“The activity probability is denoted by ρ”；where→with。'],
    '源内容完全对应，但非必要的句法与措辞重写超过术语替换。',
    'SUPPORTED: 共同活动概率与稀疏活动假设有明确来源。',
    'Pr(α_k=1)=ρ及ρ≪1与Cai的λ定义一致。',
    '可按Cai原句保留句法、只把λ替换为ρ。')
add('P09','Each device maintains', 'AUTHOR_DEFINED_OR_DERIVED',[
    ref('cai2026',c4,'II-A','As a result, only a (small) subset of the devices is active in any given transmission block.',
        locator='Context plus one α_k with no t index in (1)–(4) supports block-constant activity implicitly, not this exact sentence.')],
    ['将原文的块级活动建模显式表述为整块状态保持。'],
    '在核对的Cai正式版/v2、Shen和Huang全文中未定位到这一完整原句；它是本稿对α_k不带帧索引的显式建模假设。',
    'CONSISTENT_MODEL_ASSUMPTION: 块内活动不变与后续Q帧共用α_k自洽；不是由物理信道公式自动推出。',
    '无显示公式；其作用是允许所有q使用同一α_k。',
    '作为本文假设保留并明确身份；不能称为找到参考原句。')
add('P09','We define', 'AUTHOR_DEFINED_OR_DERIVED',[
    ref('cai2026',c4,'II-A','Let Xk ≜ αkHk.',eq='between (3) and (4)'),
    ref('shen2025','PDF p.5','II-C',locator='(14)–(15) place OTFS phase factors Φ_q in C^{φ,l}; this is conceptual precedent, not A_qkn=P_qkn exp(jqβ_k).',eq='(14)–(15)')],
    ['X_k=α_kH_k沿用Cai定义。','“incorporate the inter-frame phase rotation into the pilot symbols”及A_qkn的具体定义为本稿增加。'],
    '前半句有明确公式来源，后半句将本稿P08的标量跨帧相位吸收入导频；已查资料没有该AFDM完整句与等式。',
    'VALID_UNDER_STATED_MODEL: 用H_k^(q)=exp(jqβ_k)H_k代入线性接收关系可得此定义。',
    '本稿附录app:afdm-model eq: path-operator、末段及本章eq:twc-frame-channel给出所需共同相位；共同ν_k、块内路径参数不变是条件。Cai无跨帧相位项。',
    '标为本文定义，并把跨帧相位的依据指向本稿已给推导；不可把Cai引用延伸成整个等式来自Cai。')
add('P09','After removing', 'SUPPORTED_PARAPHRASE',[rx,noise,ref('huang2026','PDF p.2 / journal p.2950','II, System Model',locator='AFDM effective input-output relation (4)–(5): an N×N effective channel matrix acts on an N-vector; supports non-diagonal symbol coupling.',eq='(4)–(5)')],
    ['主句CP→CPP、DFT→DAFT、t-th OFDM symbol→q-th AFDM frame及Y维度替换。','where新增W_q=[W_qmr]索引，并把“with the elements i.i.d. drawn from”改写为“with independent entries distributed as”。'],
    '接收句主干逐词对应Cai，只需对象/符号替换；但按协议将where连入完整句后出现额外措辞改写，故整句为SUPPORTED_PARAPHRASE。此分类不以公式不同为理由。',
    'VALID_UNDER_STATED_MODEL: 全矩阵信道乘导频并对设备求和成立；独立等方差AWGN通过酉DAFT保持CN(0,σ²)。',
    'Cai (3)使用对角Q_kt及H_k∈C^{N×M}，逐接收子载波只有同一n的乘积；本稿为Σ_kΣ_n A_qkn X_kmrn，保留n→r的N×N耦合并引入M维阵列。该双求和是本稿根据P07/P08/本稿附录app:afdm-model所作AFDM适配，不能直接声称Cai原式已含r,n两维。',
    '语言上可逐词保留Cai的AWGN where句，仅必要替换对象符号；数学上明确eq:observation-tensor由本稿AFDM算子推出。',
    alignment={'main_clause':'TERM_ONLY','where_clause':'SUPPORTED_PARAPHRASE','formula_source':'AUTHOR_DEFINED_OR_DERIVED adaptation, not a direct Cai equation'})
add('P09','Collecting the', 'SUPPORTED_PARAPHRASE',[mmv,shen_collect],
    ['“We express ... in a more compact form as”或“Next, we collect ... into a single matrix as”重新写为“Collecting ... yields the matrix model”。','where的矩阵组织和全部维度改为本稿索引。'],
    '收集多帧得到矩阵式有Cai/Shen依据，但整句未直接采用任一原句，且显示式的具体堆叠为本稿定义。',
    'VALID_ALGEBRA: 按下一句四项索引逐元素检查，AX的(q,mN+r)元恰为双求和。',
    'Cai为NT×M观测、NT×NK测量矩阵、NK×M未知量；本稿为Q×MN、Q×KN、KN×MN。接收符号r移入列索引，发射符号n进入行块；这不是把T改名Q即可完成。Shen (15)也不是该排列。',
    '可借用Cai或Shen的完整收集句作为语言适配，同时将维度重排明确列为本稿数学定义。')
add('P09','The corresponding entries', 'AUTHOR_DEFINED_OR_DERIVED',[],
    ['新增四个张量至矩阵的元素索引定义。'],
    '在本轮Cai正式版/v2、Shen及Huang中没有这些索引式或对应原句；它们专属于本文n→r信道张量。',
    'VALID_ALGEBRA: m=0..M−1、r,n=0..N−1、k=1..K时索引范围分别为MN列与KN行，覆盖无冲突。',
    '四项映射保持eq:observation-tensor与eq:mmv逐元素等价；这里的X_k是张量块，矩阵中的设备行块有N行、MN列。',
    '按本文定义保留；不能伪装成参考论文原句。')
add('P09','We estimate the', 'SUPPORTED_PARAPHRASE',[full],
    ['从Huang的“Since we directly estimate ... without imposing sparsity assumptions”子句抽出主句。','matrix H_eff→tensor H_k是必要对象替换；删除directly并增写on its coefficients；未保留原句后半部单导频欠定的因果链。'],
    '目标与Huang直接对应，但当前写法是删减和扩写后的独立句，不是纯术语替换；新增“on its coefficients”不是原句片段。',
    'SUPPORTED: 不对每个H_k系数施加稀疏先验与后文活动诱导块稀疏不矛盾。',
    'Huang为单链路N×N有效矩阵；本稿扩展为M×N×N张量，未由该句得到设备活动模型。',
    '如要求原句组合，可保留Huang被抽取子句的措辞，只作独立成句所需语法调整，并另外声明张量扩展。')
add('P09','Since $Q<KN$', 'AUTHOR_DEFINED_OR_DERIVED',[
    full,ref('cai2026',c4,'II-A',locator='(4) is an underdetermined JADCE linear recovery setting when the chosen pilot dimension is smaller than the unknown dimension; does not contain Q<KN.',eq='(4)')],
    ['把本稿Q×KN矩阵的尺寸不等式直接写成欠定结论。'],
    'Huang只讨论单导频使其(6)欠定；Cai采用不同矩阵行数。Q<KN及本稿eq:mmv的具体结论是本文维度判断，不是可替换符号获得的原句。',
    'VALID_LINEAR_ALGEBRA: 若Q<KN，A的列秩不可能达到KN，每列观测的无约束线性逆问题欠定。',
    '此句仅断言原始线性系统欠定；不声称有先验约束后的统计识别必然失败。',
    '按本稿条件和直接推论保留；不要用Huang的单导频原句冒充这个具体不等式。')
add('P09','Sporadic device activity', 'SUPPORTED_PARAPHRASE',[block],
    ['将“Due to ... matrix X exhibits ...”改写成“Sporadic device activity gives X ...”。','原文两句合为冒号句，Specifically与we have改为if/then结构。'],
    '两项命题均精确可定位；但首句主谓重写不是仅连接原句所需语法调整，因此整句为支持性改写。',
    'SUPPORTED: α_k=0推出整个设备块为零，不依赖H_k本身的系数稀疏性。',
    '零块关系直接沿用Cai；本文设备块从N×M扩展到M×N×N（矩阵重排为N×MN），块稀疏含义保持。',
    '可直接保留Cai两句措辞并只换必要符号；当前不要标原句组合。')

add('P10','Our objective', 'SUPPORTED_PARAPHRASE',[objective],
    ['In this paper, we aim to→Our objective is to；simultaneously→jointly；corresponding channels→their channels；based on the observation→from；under→within。'],
    '任务与Bayesian框架完全对应，但多处英文同义改写不属于必要术语替换。',
    'SUPPORTED: JADCE目标与Cai一致，本文的Y是另行定义的观测。',
    '无显示公式；Y的AFDM含义需依照本文而非沿用Cai的OFDM矩阵尺寸。',
    '若要求原句，可直接沿用Cai II-B首句，仅替换必要技术对象。')

add('P11','To formulate', 'AUTHOR_DEFINED_OR_DERIVED',[
    table],
    ['新增将估计A与σ²视为给定量的条件化/代入约定。'],
    'Cai Table II使用已知Q及δ_0²，没有本文的A_hat(Y)、σ_hat²(Y)前端估计约定；该句是本稿定义工作推断问题。',
    'VALID_AS_WORKING_MODEL: 给定估计后可构造Gaussian工作似然；不等于边缘化前端参数不确定性的完整物理后验。',
    '后验的“given”参数应理解为固定plug-in值，即使它们由同一Y计算；不能据此宣称估计误差已计入。',
    '保留为本文建模约定，不归入Cai原句适配。')
add('P11','These estimates', 'AUTHOR_DEFINED_OR_DERIVED',[],
    ['本文前端章节内部指引。'],
    'sec:frontend是当前稿件内标签，参考论文没有该章节关系。已只读定位到05_overall_algorithm.tex的sec:frontend以及appendix_parameter_estimation.tex末段。',
    'INTERNAL_REFERENCE_CONFIRMED: 当前稿sec:frontend确有A_hat及噪声估计说明，附录参数估计给出对应公式。',
    '无公式；这里只核内部存在性，不在本次扩大为算法精度或实验有效性评价。',
    '按内部章节指引保留，不要求为其捏造外部原句。')
add('P11','Let $q_{\\rm tr}$', 'AUTHOR_DEFINED_OR_DERIVED',[learn,htrain],
    ['引入q_tr作为训练样本代表的H_k先验分布。'],
    'Cai与Huang说明从训练数据学习信道分布，但未给出这个q_tr定义或这句英文；本稿用它明确训练分布与真实分布的区别。',
    'VALID_AS_DEFINED: 可把q_tr视作训练样本所代表的分布；有限样本或分数网络本身不能自动证明它等于真实信道先验。',
    '这是新的概率分布符号及解释，不是把Cai p(H_k)机械改名；工作后验明确使用其作为先验。',
    '明确保留为本文定义，可给学习先验的文献依据，但不能判TERM_ONLY。')
add('P11','We assume independence', 'AUTHOR_DEFINED_OR_DERIVED',[
    ref('cai2026','PDF pp.3–4 / journal pp.3577–3578','II-A','Moreover, we assume that the IoT devices are synchronized, and each device determines whether to access the channel in an independent and identically distributed (i.i.d.) manner.'),factor],
    ['将跨设备信道/活动独立及设备内活动—信道独立显式写成一条本稿假设。'],
    'Cai明确原句仅给出设备接入i.i.d.；Cai (5)的先验乘积支持更完整的独立结构，但没有定位到当前这句英文。不能把跨设备活动i.i.d.原句扩大成整个H_k与α_k独立原句。',
    'CONSISTENT_MODEL_ASSUMPTION: 独立先验允许后文按k相乘；独立性是建模选择，不由AFDM物理模型本身保证。',
    'product_k q_tr(H_k)p(α_k)需跨设备对(H_k,α_k)相互独立且每对内部独立；Cai (5)同型，未限定同一AFDM信道分布。',
    '按本文假设保留并可引用Cai因子分解；不能标外文原句只换术语。')
add('P11','The\nactivities follow', 'AUTHOR_DEFINED_OR_DERIVED',[table,nonsep],
    ['合并Bernoulli活动先验与保持设备内H_k联合依赖两项设定。','q_tr及其在本文张量系数上的作用为本稿限定。'],
    'Bernoulli形式可由Cai Table II逐项核对；非可分信道去噪及利用相关性的原句在Cai I-A。当前“q_tr retains dependence”并非其中任何原句，也不只是把两条原句连接；它是在声明本稿联合先验的结构。',
    'CONSISTENT_MODEL_ASSUMPTION: 不把q_tr(H_k)拆成系数乘积可保留其已有相关性；“retains”不应被解释为已证明有限网络精确恢复所有相关性。',
    'Bernoulli仅作用于α_k；q_tr作用于整个设备信道张量，不额外假设其系数独立。',
    '标为本稿结构假设，并分别指向Cai Table II与I-A作为方法依据。')

add('P12','Under these assumptions', 'AUTHOR_DEFINED_OR_DERIVED',[factor,where,ref('cai2026_stmp_v2','PDF pp.4–5','II-B',locator='Eq. (5) and its following where sentence agree with the formal version.',eq='(5)')],
    ['因子分解引导语由Cai的主动句及Bayes/条件独立说明压缩成Under these assumptions。','where句保持Cai句法，m→j、M→MN、NT→Q。','p(H_k)改为本文训练先验q_tr，后验p改为q，似然采用下一句给定估计值。'],
    '因子图骨架源于Cai (5)，where局部可按必要符号尺寸替换定位；但完整语句引入本文训练先验与工作后验，属于在本稿假设下建立的概率模型。不是仅因显示公式变动而否定原句对齐：引导语也有自主改写，q的概率含义由本文新定义。',
    'VALID_AS_WORKING_POSTERIOR: 独立AWGN、给定A_hat/σ_hat²、跨设备独立和X_k=α_kH_k足以得到此比例关系。观测列间似然因子化不要求H_k的列在先验中独立。',
    'Cai product_m至M →本稿product_j至MN来自不同的观测矩阵列数；X_k仍是同一变量集合的设备块重排。用训练先验和由Y得到的固定参数后，q是规范化后的工作分布；没有对β/σ²的估计不确定性积分，不能等同于真实生成模型的完整后验。',
    '把“参考因子分解模板”与“本文定义的q”分开标注；where可保留原句适配，其余应承认为本文建模。',
    alignment={'leading_clause':'SUPPORTED_PARAPHRASE of Cai II-B','where_clause':'TERM_ONLY','probability_model':'AUTHOR_DEFINED_OR_DERIVED'})
add('P12','Here, $q$', 'AUTHOR_DEFINED_OR_DERIVED',[table],
    ['定义working posterior名称与q；把Cai已知Q、δ_0²的Gaussian因子改为估计A_hat、σ_hat²并设Q维。'],
    '在所核Cai正式版/v2、Shen、Huang全文中没有当前“q denotes the working posterior”原句。Gaussian似然有Cai Table II作为数学模板，但本句用于本稿plug-in模型的定义。',
    'VALID_AS_WORKING_LIKELIHOOD: 假定σ_hat²>0，CN(y_j;A_hat x_j,σ_hat²I_Q)是正常的Gaussian工作因子。',
    '它忽略A_hat与σ_hat²估计误差，仅作为已固定参数的似然；此点与P11“as given”一致。名称working posterior在本轮语料未定位，不能归给Cai。',
    '按本文概率分布定义保留；working posterior在本轮语料未找到对应原词，按项目术语规则须补可定位出处，或用已定义的q及公式直接描述，不将其包装成Cai现成术语。')
add('P12','The factor', 'SUPPORTED_PARAPHRASE',[table,prob],
    ['把Table II的δ约束解释成“enforces”；把二原子分布改写为α_k∈{0,1}上的Bernoulli质量函数。'],
    '两项数学含义都能直接从Cai Table II核对，但源文本是表格公式而非当前英文完整句；从公式转写解释句不能称原句组合。',
    'VALID_EQUIVALENT_REPRESENTATION: deterministic factor及Bernoulli PMF与Cai模型同义；α_k支持集已在P09声明。',
    'p(X_k|H_k,α_k)=δ(X_k−α_kH_k)支持“enforces”；ρ^{α_k}(1−ρ)^{1−α_k}与Cai双Dirac表示在二值支持集上等价，但公式表现形式为本稿改写。',
    '引用Cai Table II支持含义，承认这是对表格公式的解释性改写。')
add('P12','Under this posterior', 'AUTHOR_DEFINED_OR_DERIVED',[
    ref('cai2026',c7,'III-B.1',locator='Eq. (22) defines an MMSE denoising expectation E[H_k|H_k^pri], conditioned on a pseudo-observation, not the complete q posterior conditioned on Y.',eq='(22)'),
    ref('cai2026',c7,'III-B.2','is the posterior probability of activity for the k-th device.',eq='following (30)',locator='Refers to λ_k^post from a message belief; not an exact q(α_k=1|Y) equality.')],
    ['为当前q定义X_k的后验均值和α_k边缘概率，命名X_k^MMSE与p_k^Bayes。'],
    'MMSE=后验均值及活动后验概率有明确标准含义；Cai给出的是伪观测下的去噪均值与消息置信度更新。当前这组针对q、Y的目标符号及完整英文句是本文定义，不能把Cai (22)/(30)当成完全相同原式。',
    'VALID_TARGET_DEFINITION: 平方误差下E_q[X_k|Y]为该工作分布的MMSE估计；q(α_k=1|Y)为相应边缘概率。',
    '估计目标是X_k=α_kH_k，即活动加权有效信道，而非所有设备的H_k本身。消息传递后续近似这些目标，不因命名Bayes就获得真实物理模型的最优性保证。',
    '保留为本文目标定义；“channel estimate”应按X_k的活动加权含义理解，不夸称Cai完全相同公式。')
add('P13','We approximate', 'SUPPORTED_PARAPHRASE',[mp,gen,avoid,integrals],
    ['把Cai II-B中近似MMSE、deep generative priors、高维积分三个论述压成一条概括。','these quantities回指本文P12新定义的两个目标，原文没有此回指；“avoiding direct integration over the high-dimensional posterior”是自行概括。'],
    '内容有多条明确原句支持，但当前不是这些原句/分句只经必要连接后的组合，而是用新的主谓结构和回指做摘要式改写。',
    'SUPPORTED_APPROXIMATION_CLAIM: Cai说明以生成先验和消息传递近似求解、避免显式高维积分；本句没有声称完全精确。实际算法仍须由后文给出，本次不核实性能。',
    '无显示式；对“these quantities”的适配只能指本稿q下目标，而非自动继承Cai的所有近似性质。',
    '如果严格需要可定位原句组合，应分别沿用Cai近似MMSE句与生成先验消除积分句；当前标为支持性概括。')

paragraphs=[]
for pid, records in data.items():
    raw=(root/(pid+'.input.txt')).read_text(encoding='utf-8-sig')
    starts=[]
    for phrase,d in records:
        # Source inputs are read with universal newlines; all exact substrings preserve every non-whitespace character.
        pos=raw.index(phrase)
        starts.append(pos)
    assert starts==sorted(starts) and starts[0]==0, (pid,starts)
    sentences=[]
    for i,((phrase,d),start) in enumerate(zip(records,starts)):
        end=starts[i+1] if i+1<len(starts) else len(raw)
        d={'id':f'{pid}.S{i+1:02d}','draft_tex':raw[start:end],**d}
        for r in d['source_refs']:
            if 'quote' in r:
                r['quote_format']='英文措辞为原句/已注明的原句分句；数学排版用可读线性形式重建，非PDF逐字节转录。换行、连字、排版断词规范化。'
        sentences.append(d)
    reconstructed=''.join(x['draft_tex'] for x in sentences)
    assert re.sub(r'\s+','',reconstructed)==re.sub(r'\s+','',raw),pid
    structures={
    'P09':dict(source_order=['Cai II-A activity indicator/probability','本文块内假设与相位吸收定义','Cai received-signal sentence template + 本文AFDM双求和','Cai (4)/Shen (15)收集框架 + 本文MMV排列','Huang III-A full effective channel','本文Q<KN维度推论','Cai II-A activity-induced block sparsity'],cross_source_combination=True,condition_change='Cai的同步OFDM对角子载波模型变为本文具n→r耦合的AFDM算子；MMV维度重排及共同相位吸收不能由原句直接继承。Huang的不依赖系数稀疏与Cai的活动块稀疏兼容，须分清对象。',assessment='技术上可在本文P07/P08/本稿附录app:afdm-model条件下成立，语言上不满足全段仅必要术语替换。'),
    'P10':dict(source_order=['Cai II-B first sentence'],cross_source_combination=False,condition_change='目标同型，Y换为本稿AFDM观测。',assessment='语义对应但全句多处自主同义改写。'),
    'P11':dict(source_order=['本文前端估计条件化','本文内部章节指引','Cai/Huang learned distribution概念 + 本文q_tr定义','Cai Eq. (5)独立因子结构 + 本文显式假设','Cai Table II Bernoulli及I-A non-separable channel correlations + 本文联合先验'],cross_source_combination=True,condition_change='已知测量矩阵/噪声参数改为由同一Y得到的固定估计值；真实p(H_k)与训练q_tr明确区分。独立性是本文假设，不是物理模型必然结论。',assessment='整个段落主要是本文推断问题的补充定义，不能作为原文替换段落计入。'),
    'P12':dict(source_order=['Cai (5) factorization and where template','本文working q及plug-in Gaussian likelihood','Cai Table II delta/Bernoulli数学形式的解释性改写','本文q下目标定义，参考Cai MMSE/活动概率概念'],cross_source_combination=False,condition_change='公式骨架保持，但观测列数、训练先验、给定估计参数及目标条件集改变；Cai的消息置信度不等同精确全局后验。',assessment='where局部保持原句结构；整段为本文工作后验建模及标准目标定义，须与直接原句来源分栏。'),
    'P13':dict(source_order=['Cai II-B approximate MMSE','Cai II-B deep generative priors','Cai II-B eliminating high-dimensional integrals'],cross_source_combination=False,condition_change='新增对本文两个q目标的回指；不能从引用推得本文算法的精确性或性能。',assessment='支持性摘要，非仅必要语法连接的原句组合。')}
    paragraphs.append(dict(id=pid,sentences=sentences,paragraph_structure=structures[pid],coverage={'complete_ignoring_whitespace':True,'input_nonwhitespace_characters':len(re.sub(r'\s+','',raw)),'reconstructed_nonwhitespace_characters':len(re.sub(r'\s+','',reconstructed))}))

counts=Counter(s['category'] for p in paragraphs for s in p['sentences'])
audit={
 'scope':'P09–P13, current English Chapter 2; standalone audit without prior verdicts',
 'review_date':'2026-10-30',
 'protocol':'PROTOCOL.md',
 'source_file_sha256':json.loads((root/'manifest.json').read_text(encoding='utf-8-sig'))['source_sha256'],
 'sentence_unit':'完整语法句；显示公式以及其后where纳入同一句；无标点的显示公式定义按其引导句计。',
 'classification_note':'整体类别按完整句；局部原句对齐单独列language_alignment。公式自身扩展不自动降低已对应的英文原句类别。0个完整句满足EXACT/TERM_ONLY/REASONABLE_COMBINATION，不代表全部内容无文献依据。',
 'read_evidence':{
  'original_pdfs':['reference/literature/cai2026.pdf','reference/literature/cai2026_stmp_v2.pdf','reference/literature/shen2025.pdf','reference/literature/huang2026.pdf'],
  'fresh_full_pdf_text_extractions':['c_cache/cai2026.fresh.txt','c_cache/cai2026_stmp_v2.fresh.txt','c_cache/shen2025.fresh.txt','c_cache/huang2026.fresh.txt'],
  'source_page_images_actually_viewed':['c_cache/cai2026-04.png','c_cache/cai2026-05.png','c_cache/huang2026-3.png'],
  'page_image_findings':'Cai (3) uses diagonal pilot Q_kt, (4) dimensions NT×M / NT×NK / NK×M; Table II Gaussian, delta and Bernoulli entries verified visually. Huang p.3 full-channel/no-sparsity sentence and (6)/(9) context verified visually.',
  'current_manuscript_cross_checks':['sections/appendix_afdm_channel_model.tex: path operator and final cross-frame phase derivation','sections/05_overall_algorithm.tex: sec:frontend exists','sections/appendix_parameter_estimation.tex: A_hat and sigma_hat² estimates/fixedness'],
  'prior_verdicts_read':False,
  'quote_normalization':'PDF linewraps, ligatures, split words and mathematical typography normalized; no substantive sentence content silently added. Formula-only source material is explicitly a locator, not fabricated prose.'
 },
 'category_counts':dict(counts),
 'paragraphs':paragraphs,
 'key_findings':[
  'Cai接收句主干可按必要术语替换对齐，但本稿整句where有自主改写；更一般AFDM双求和及MMV重排为本稿推导。',
  'q_tr、由Y得到并固定的A_hat/σ_hat²、working q及q下估计目标主要是本稿定义；Cai模板不能替代这些定义的来源身份。',
  'Cai明确有接入i.i.d.原句、Eq. (5)独立先验结构、I-A non-separable denoisers exploiting channel correlations；三者需分别对应，不能合称当前独立性句就是原句。',
  '按用户逐句原文要求，支持性改写与本文建模均不可算“全部原句仅替换术语”；但本次未发现这些建模关系本身的确定性代数矛盾。'
 ]}
(root/'c_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

lines=['# P09–P13 逐句来源核查','',
 '本次只读当前英文稿，重新提取四份原始PDF；没有读取历史审计结论或其他审查员报告。句内显示公式、where与过渡句均纳入覆盖。',
 '', '完整语法句共21句。分类统计：'+ '；'.join(f'{k}={v}' for k,v in counts.items())+'。',
 '完整句没有一条达到 EXACT / TERM_ONLY / REASONABLE_COMBINATION；接收句主干与后验where局部可以按必要术语/符号替换逐词定位。该结论针对严格语言来源标准，不等于全部内容没有文献依据或技术错误。',
 '', '已实际查看 Cai 正式版PDF第4、5页及Huang第3页图像；Cai v2、Shen另以原始PDF全文新提取核对。页码均区分PDF页与期刊页。',
 '', '关键区分：Cai原接收模型为OFDM对角导频及NT×M拼接；本文n→r耦合、Q×MN观测及KN×MN未知量需要本稿算子推导。训练q_tr、给定前端估计及working q是本文建模，不是Cai原句。', '']
for p in paragraphs:
    lines += [f"## {p['id']}",'', '段落顺序：'+' → '.join(p['paragraph_structure']['source_order']), '',
              '条件变化：'+p['paragraph_structure']['condition_change'], '',
              '结构判断：'+p['paragraph_structure']['assessment'],'']
    for s in p['sentences']:
        lines += [f"### {s['id']} — {s['category']}",'','当前完整句：','','```tex',s['draft_tex'].rstrip(),'```','', '直接来源：','']
        if not s['source_refs']: lines += ['- 在本轮所核全文中未定位对应原句；此项属于本文定义或内部指引。']
        for r in s['source_refs']:
            location=f"{r['key']}，{r['page']}，{r['section']}"+(f"，{r['eq']}" if 'eq' in r else '')
            lines += ['- '+location]
            if 'quote' in r: lines += ['','  > '+r['quote']]
            if 'locator' in r: lines += ['','  定位说明：'+r['locator']]
        lines += ['','改动：'+'；'.join(s['changes']),'','判定理由：'+s['reason'],'',
                  '技术判断：'+s['technical_status'],'','公式适配：'+s['formula_adaptation'],'',
                  '处理建议：'+s['action'],'']
    lines += ['覆盖检查：全部draft_tex按顺序拼接，忽略空白后与Pxx.input.txt完全一致；仅表示无漏句。','']
(root/'c_audit.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps({'paragraphs':len(paragraphs),'sentences':sum(len(p['sentences']) for p in paragraphs),'counts':dict(counts),'coverage':all(p['coverage']['complete_ignoring_whitespace'] for p in paragraphs)},ensure_ascii=False))
