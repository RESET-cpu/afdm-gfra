from pathlib import Path
import json, re, hashlib
from collections import Counter

BASE = Path(__file__).resolve().parent

def ref(key, page, section, quote=None, locator=None, eq=None):
    d = dict(key=key, page=page, section=section)
    if quote is not None: d['quote'] = quote
    if locator is not None: d['locator'] = locator
    if eq is not None: d['eq'] = eq
    return d

def sentence(category, refs, changes, reason, technical, formula, action):
    return dict(category=category, source_refs=refs, changes=changes, reason=reason,
                technical_status=technical, formula_adaptation=formula, action=action)

CAI_ALLOC = 'Assume that a total of T OFDM symbols are allocated for pilot transmission.'
CAI_PILOT = 'Let q_ktn ∈ C be the pilot symbol transmitted by the k-th device during the t-th OFDM symbol on the n-th subcarrier.'
CAI_ORTH = 'For simplicity, we impose the condition that Q is partial orthogonal, specifically requiring that QQᴴ = KP I_NT, where each device has the same transmit power budget P.'
DING_IDAFT = 'The time-domain transmitted signal is generated through the inverse discrete affine Fourier transform (IDAFT) applied to x_k, mathematically formulated as'
HUANG_LEAK = 'In practical propagation environments, fractional Doppler shifts and fractional time delays can introduce significant power leakage in the effective channel matrix of (5), thereby weakening the sparsity of H_eff.'

data = []
def paragraph(pid, starts, rows, structure):
    text = (BASE / f'{pid}.input.txt').read_text(encoding='utf-8')
    positions = [text.index(s) for s in starts] + [len(text)]
    assert positions[0] == 0 and positions == sorted(positions)
    assert len(starts) == len(rows)
    for i, row in enumerate(rows):
        row['id'] = f'{pid}.S{i+1:02d}'
        row['draft_tex'] = text[positions[i]:positions[i+1]]
    joined = ''.join(r['draft_tex'] for r in rows)
    assert joined == text
    data.append(dict(id=pid, sentences=rows, paragraph_structure=structure,
                     coverage=dict(exact_concatenation=True, whitespace_ignored_match=True,
                                   input_sha256=hashlib.sha256((BASE / f'{pid}.input.txt').read_bytes()).hexdigest())))

paragraph('P04', ['We allocate', 'Let $P_', 'The corresponding', 'Let $\\mathbf P', 'For simplicity', 'The pilot construction'], [
sentence('SUPPORTED_PARAPHRASE', [ref('cai2026',4,'II-A',CAI_ALLOC), ref('cai2026_stmp_v2',4,'II-A',locator='与正式版相同的导频分配句，式(3)之前'), ref('huang2026',2,'II', 'Let N denote the number of AFDM chirp subcarriers.')],
    'Assume that a total of ... are allocated 改成 We allocate；第二来源的 Let N denote ... 改成 with N ... per frame；OFDM symbols 改为 AFDM frames，T 改 Q。',
    '两个内容依据均可定位，但整句主动语态及 with 从句为自行重组；这些改动不只是必要名词替换，不能判为原句级合理组合。',
    '多帧导频资源安排是可行的本稿设定。Cai讨论OFDM符号，Huang的frame描述不自动包含本文CPP；这里的frame含义须以后文定义为准。',
    '无独立公式；Q帧及每帧N个AFDM chirp subcarriers是本文对两个来源的系统适配。',
    '若必须满足作者的原句要求，应保留两个可定位原句的句法，分别做必要对象替换；本记录仅审计、不改稿。'),
sentence('SUPPORTED_PARAPHRASE', [ref('cai2026',4,'II-A',CAI_PILOT)],
    'Let ... be 改为 Let ... denote；during ... on ... 的顺序改成 on ... in ...；删去 the k-th 形式，并改符号、AFDM子载波和帧名。',
    '传输者、导频、时频位置均有原句，但本句还改了谓词和介词结构；不能只凭同一模板称TERM_ONLY。',
    '定义一致，k为设备、q为帧、n为发射chirp子载波。',
    'q_ktn → P_qkn；OFDM子载波符号改成AFDM chirp子载波符号是系统定义，不声称两种调制信道相同。',
    '按严格原句目标需恢复来源句法，再列明对象和索引替换。'),
sentence('AUTHOR_DEFINED_OR_DERIVED', [ref('cai2026',4,'II-A',locator='导频定义后构造Q_kt=diag{q_kt1,...,q_ktN}；并非本文列向量p_qk',eq='(3)之前')],
    '自行将N个标量排成列向量，增加全部k、q的索引范围。',
    '在已检查语料中未定位该完整英文句；Cai相邻句定义的是对角矩阵，不能拿它替代本句列向量原句。',
    '维度和索引与P_qkn一致。',
    '向量化定义本身无需外部定理；属于本稿记号。',
    '保留为明确的本稿定义；若作者坚持每一句均参考原句，本句不满足该限定。'),
sentence('AUTHOR_DEFINED_OR_DERIVED', [ref('cai2026',4,'II-A',locator='式(4)及其where：Q=[Q_1,...,Q_K]，Q_k由各时刻对角导频矩阵纵向叠加，维度NT×NK',eq='(4)')],
    '新建Q×KN矩阵、规定列索引(k−1)N+n，并明确接收端已知。',
    '本稿把帧作为行、设备及发射chirp索引作为列；不是Cai的NT×NK块对角叠加矩阵。没有本句的参考原句。',
    '所给索引能唯一重排导频；接收端已知是本稿建模假设。',
    'Cai矩阵的行含时间和接收子载波，本文行只含帧；两者不能只换尺寸而宣称同一构造。',
    '标为本稿符号重排/定义。'),
sentence('AUTHOR_DEFINED_OR_DERIVED', [ref('cai2026',4,'II-A',CAI_ORTH,eq='(4)后'), ref('cai2026', '10–11','V-C',locator='式(66)采用K×K酉矩阵的行；同一子载波内T个行索引不同，NT个选择可跨子载波复用',eq='(66)')],
    'impose the condition...specifically requiring 压缩成 is chosen to satisfy；增加每设备每帧列向量能量E_p=||p_qk||²；Q矩阵结构与行维不同。',
    'Cai支持采用行正交导频简化估计的思想，但本文完整条件是对新矩阵及新能量定义的构造，不能冒作Cai原句仅术语替换。',
    '技术成立，已仅用当前VI-A eq:pilot做解析核对：不同DFT行、全列置换和固定列相位给PPᴴ=K E_p I_Q；每设备N个等模符号给能量E_p。无需实验。',
    '本文构造给[P Pᴴ]_{qq′}=(E_p/N)Σ_{c=0}^{KN−1}exp(−j2π(r_q−r_q′)c/(KN))=K E_p δ_{qq′}，Q≤KN；每组Σ_n|P_qkn|²=N(E_p/N)=E_p。Cai则在各子载波上从K×K矩阵取T个行，条件与能量口径不同。',
    '可保留该有效构造，但应把Cai归为设计动机，并明确这是本文构造；不得计为原句适配通过。'),
sentence('AUTHOR_DEFINED_OR_DERIVED', [ref('cai2026',4,'II-A', 'The design of partial orthogonal Q is deferred to Section V-C.')],
    'The design of partial orthogonal Q / is deferred 改成 The pilot construction / is given，并替换章节目标。',
    '来源有相似章节指引，但本文句子指向本稿VI-A，属于内部指引；不是只换章节号的完整原句。',
    '已核对06_simulation_results.tex的sec:simulation-settings确有eq:pilot。',
    '不适用；章节指引。',
    '保留为内部指引；严格逐句原句统计中单列。')],
dict(source_order=['cai2026 II-A','huang2026 II','本稿向量/矩阵定义','cai2026 II-A及V-C的设计动机 + 本稿VI-A构造','本稿内部指引'], cross_source_combination=True,
     structure_changes_conditions='是：OFDM符号及对角矩阵被改为AFDM帧及Q×KN矩阵，正交维度、可取行数和能量定义随之改变。当前DFT构造能满足新条件，但不能据此倒推文本原句来自Cai。',
     verdict='6句中2句为有支持的改写，4句为本文定义/构造/内部指引；无整句达到仅必要术语替换。'))

paragraph('P05', ['Let $\\Delta f', 'For sample index', 'Equivalently,'], [
sentence('SUPPORTED_PARAPHRASE', [ref('ding2026',2,'II',locator='式(1)前系统描述定义sub-carrier spacing Δf；式(3)后where明确Ts=1/(NΔf)',eq='(1),(3)'), ref('huang2026',2,'II', 'Each AFDM frame spans a duration of T = NΔt. The sampling rate is given by 1/Δt, and the subcarrier spacing to Δf = 1/T.')],
    '把Ding分散在两处的名词与采样间隔公式改写为统一Let ... denote句；Huang对应关系也不是该英文句法。',
    '定义和关系明确有源，但不存在当前完整原句；普通Let模板不算原句证据。',
    'Ts=1/(NΔf)与两个来源一致。',
    'Ts与Huang的Δt同义；此处N Ts是有效符号时长，不能把它当含CPP的整帧时长。',
    '严格原句要求下需采用可定位原句并必要换符号；当前归支持性改写。'),
sentence('SUPPORTED_PARAPHRASE', [ref('ding2026',2,'II',DING_IDAFT,eq='(1)'), ref('ding2026',2,'II', 'c1 and c2 are AFDM modulation parameters.',eq='(1)后')],
    'The ... is generated through ... applied to ... 改成 applying ... yields ...；增加For sample index从句；将独立参数句接为where从句。',
    '标量IDAFT及参数释义有准确来源，但英文主从结构主动改写，超过仅符号替换及必要拼接。',
    '标量公式与Ding式(1)一致，经索引重命名和增加帧索引即可得到。',
    'Ding n(时间)→t、m(频域)→n、x_k[m]→P_qkn、s_k[n]→s_qk[t]；正号、1/√N和三个相位项均保持。样本范围0,...,N−1与求和一致。',
    '若按原句标准，可直接使用Ding该主句并必要符号替换，参数句也有独立原句；当前不记TERM_ONLY。'),
sentence('SUPPORTED_PARAPHRASE', [ref('ding2026',2,'II', 'The signal in (1) can be represented in matrix form as',eq='(2)'), ref('huang2026',2,'II',locator='首段给s=Aᴴx=Λ_c1ᴴFᴴΛ_c2ᴴx，并定义A为DAFT矩阵'), ref('bemani2022','7–8','II及III-A',locator='p7式(11),(16)给DAFT矩阵；p8开头给其Hermitian inverse，式(18)后给s=Aᴴx',eq='(11),(16),(18)')],
    '加入Equivalently；The signal in (1)改为方程引用主语；represented改written；将分解矩阵展开为逐元素定义，并用is替代represents。',
    '矩阵关系有源，但完整英文句及显式元素展开为本稿重写；不是Ding式(2)文字的原样改名。',
    '本文F_A元素与标量式一致，F_Aᴴ确为IDAFT。实际查看Ding PDF p2，式(2)在分解中印F而不是Fᴴ，紧接文字把Aᴴ称DAFT；不能照抄这一处符号不一致。Bemani与Huang支持本文正确约定。',
    '从A=Λ_c2 F Λ_c1展开得到[F_A]_{rt}=N^(−1/2)exp[−j2π(c2 r²+rt/N+c1 t²)]；这一步是等价展开，不改变模型。',
    '保留正确数学；若追求原句文字，选用符号一致的Huang/Bemani对应文字并记录适配，不照搬Ding的印刷不一致。')],
dict(source_order=['Ding II采样关系 / Huang II','Ding II式(1)及参数说明','Ding矩阵说明 + Huang/Bemani核对正确DAFT约定'], cross_source_combination=True,
     structure_changes_conditions='主要是定义顺序和矩阵表示重写，没有改变标量IDAFT。需区分有效符号时长与含CPP帧时长。', verdict='3句均有数学/概念支持，但英文均经过自行改写；不满足完整原句仅必要替换。'))

paragraph('P06', ['The chirp-periodic', 'By the chirp', 'Including the CPP'], [
sentence('SUPPORTED_PARAPHRASE', [ref('bemani2022',8,'III-A',locator='式(19)前一段：L_cp为整数，至少为最大delay spread所对应的样本数',eq='(19)之前'), ref('cai2026',4,'II-A', 'Assume that the cyclic prefix (CP) length exceeds the maximum channel delay spread.')],
    '将长度文字条件改成CPP duration is chosen to satisfy加不等式；由单链路delay spread改为已补偿公共传播时延后的所有设备残余路径时延最大值。',
    '前缀覆盖信道记忆有源；当前简明英文及多设备最大值不是原句仅术语替换。',
    '在本稿差分时延非负且所定义连续波形直接延迟的模型内，N_CPP Ts≥max τ_kℓ覆盖所需过去样本。',
    'N_CPP≥ceil(max τ_kℓ/Ts)是该不等式的整数实现。Bemani正文信道随后限定整数路径时延且l_max<N；当前不等式自身未重复该范围。',
    '可保留作为有源条件的本稿改写；不要称其全部内容是Bemani原句。'),
sentence('AUTHOR_DEFINED_OR_DERIVED', [ref('bemani2022',7,'II',locator='式(14)：任意整数周期偏移的chirp periodicity',eq='(14)'), ref('bemani2022',8,'III-A',locator='式(19)：s[n]以s[N+n]及一周期相位表示，n=−L_cp,...,−1',eq='(19)'), ref('bemani2022',9,'III-B',locator='信道段式(22)前明确l_max<N且路径时延为整数；p9首句仅在2Nc1为整数且N为偶数时说明CPP退化为CP',eq='(20)–(23)')],
    'With ... periodicity ... prefix is改成By ... samples satisfy；显式加入mod-N定义及2Nc1正整数条件；使用任意负索引的mod形式。',
    '这是从一般周期关系推得的表示和本文参数限制；已核原页，Bemani式(19)并未原样给出本文mod形式，也没有在该原句声称长CPP覆盖多周期。',
    'mod形式在整数采样点成立：令r=<t>_N、h=(t−r)/N∈Z，Bemani式(14)给相位c1(t²−r²)。N_CPP≤N时化为原式(19)；更长前缀需要本文多周期扩展定义。2Nc1∈N_+是额外选定条件，并非这个整数样本恒等式的必要条件；没有N为偶数不能据此宣称CPP=CP。',
    '对−N≤t<0，r=t+N，t²−r²=−(N²+2Nt)，与式(19)同式；对t<−N用一般整数h递推。Bemani后续有效信道推导采用l_max<N，不能直接把它当长时延有效信道已被原文证明。',
    '标为本文对Bemani周期关系的推导/推广，说明长CPP范围与额外参数选择；不得称原句照用。'),
sentence('AUTHOR_DEFINED_OR_DERIVED', [ref('huang2026',2,'II', 'Each AFDM frame spans a duration of T = NΔt.'), ref('shen2025',4,'II-B',locator='式(3)后where：OFDM含CP符号时长T_sym=T+T_cp',eq='(3)')],
    '新增Including the CPP，并将N Ts增加为(N+N_CPP)Ts；使用本稿帧计时。',
    '所查来源能分别支持有效符号长度与前缀相加思路，但没有当前AFDM含CPP帧长定义的完整原句；本文自行定义时间单位。',
    '连续相邻帧、每帧各有N_CPP前缀样本且无额外间隔时正确。',
    '这是样本数相加；Huang的T=NΔt不能直接作为本文T_frame。Shen定义的是OFDM符号时长，不是该AFDM帧。',
    '保留为明确的本稿定义。')],
dict(source_order=['Bemani III-A前缀长度','Bemani II式(14)/III-A式(19) + 本稿mod及多周期推广','本稿含CPP帧长'], cross_source_combination=True,
     structure_changes_conditions='是：来源信道段l_max<N、整数延迟；本文mod式及后续分数延迟/长CPP扩展超出该来源的直接信道结果。2Nc1正整数为本文选择，不能混同原文CPP=CP还需N偶数的条件。',
     verdict='1句为支持性改写，2句为本文定义/推导；前缀恒等式技术成立不意味着整段是参考原句。'))

paragraph('P07', ['After CPP removal', 'Retaining fractional', 'The matrix $\\mathbf G', 'For a useful interval', 'Here, $\\varphi_n', 'Fractional delays'], [
sentence('AUTHOR_DEFINED_OR_DERIVED', [ref('huang2026',2,'II',locator='式(4)定义单天线单帧有效矩阵H_eff，未定义本文M×N×N、q索引和H_k=H_k^(0)',eq='(4)'), ref('ding2026',2,'II',locator='先去CPP、再DAFT的接收处理及路径矩阵；无本文张量定义',eq='(4),(5)')],
    '新定义设备、接收天线、输出/输入DAFT符号三个索引的张量，并选frame 0为参考。',
    '处理顺序有源，但本句核心是本文张量与参考帧定义；未找到对应完整英文原句。',
    'M个N×N有效矩阵堆叠为M×N×N张量，维度正确。',
    'Huang的H_eff和Ding逐天线路径算子可提供物理背景，但新增q及参考张量是本文记号。',
    '明确作为本稿定义保留，不计入参考原句适配。'),
sentence('AUTHOR_DEFINED_OR_DERIVED', [ref('huang2026',2,'II', 'To better capture the LEO channel dynamics, we incorporate fractional delay and fractional Doppler effects, and the resulting expression for the elements of the channel matrix H_i is given as follows',eq='(5)'), ref('huang2026',2,'II',locator='式(4)给各路径hi H_i叠加；式(5)给单路径分数delay/Doppler元素',eq='(4),(5)')],
    '来源的incorporate句压缩成Retaining...；单天线H_i元素被替换为含a_k、g_kℓ、参考起点N_CPP的多天线张量元素；新增系数的n→r物理定义。',
    'Huang支持保留分数效应与路径叠加，但并无该张量公式及where原句。整句不能由只替换术语得到；其核心为本稿模型合成。',
    '给定本文物理信道的公共a_k、ν_k和下一句定义的G，线性叠加式成立；这不等同于已证明G与Huang式(5)逐项相同。',
    'a_k乘路径增益、d=τ/Ts、取g=N_CPP均是本稿定义。Huang式(5)需另核归一化Doppler符号、频率折返区间及参考时间，不能仅因“fractional”相同声称同式。',
    '保留为本文构造；引文仅支持分数效应处理的背景。若要称Huang公式适配，需另给完整符号/区间/相位映射。'),
sentence('AUTHOR_DEFINED_OR_DERIVED', [ref('huang2026',2,'II',locator='式(4)中把hi置于H_i外，因此H_i为单位增益路径矩阵；无本文g或frame 0',eq='(4),(5)')],
    '定义G的三个参数及单位增益、归一化时延、frame 0含义。',
    '单位路径思想有源，当前完整句仍是本稿函数记号说明。',
    '与随后G(d,ν;g)及g0=N_CPP一致。',
    'G第三个参数是有用段起点g；G(d,ν;N_CPP)是参考帧的特例，不是“CPP长度独立地改变所有帧G”的一般表述。',
    '保留为本稿定义；如以后修订，可更早说明第三参数是起点，减少首次出现时的歧义。'),
sentence('AUTHOR_DEFINED_OR_DERIVED', [ref('huang2026',2,'II',locator='式(5)为元素级分段求和式，使用l_eq=k_ν+C l_τ及L_m,q；并不写F_A D_ν,g B_d',eq='(5)'), ref('bemani2022',10,'III-C/D',locator='整数delay的路径算子A Γ_CPP Δ_f Π^l Aᴴ及其输入输出式；此处仅精确定位，无原文引语',eq='(25)–(28)')],
    '新定义连续波形延迟矩阵B_d、绝对时间D_ν,g，以及三者乘积G。',
    '在已检查参考语料中无该完整英文句或带g的算子式；本稿附录app:afdm-model给出自己的波形与推导，不能用本稿证明充作参考原句。',
    '给定本稿附录app:afdm-model的φ_n，F_A D B_d按“延迟波形采样→Doppler→DAFT”组合成立；其连续波形插值/频率折返选择属于模型条件。未凭来源认定该式唯一代表所有分数delay AFDM实现。',
    '本稿附录app:afdm-model展开为常相位exp[j2π(c1d²+c2(n²−r²)−nd/N+νTs g)]乘Σ_t exp[j2π((n−r)/N−2c1d+νTs)t]exp[j2πζ_tn d]/N。对照Huang式(5)至少须映射k_ν=−νNTs、ζ对应折返区间，并处理exp(j2πνTs g)参考相位；原文未提供本文多周期CPP定义，不能仅凭形式相似声称完整等价。',
    '标为本文推导并保留附录支撑；若拟说直接采用Huang，需要补逐项映射，而不是只改引文。'),
sentence('AUTHOR_DEFINED_OR_DERIVED', [],
    '本文φ_n的含CPP延拓定义和附录指引；设定首有用样本g=N_CPP。',
    '这是内部定义说明，不存在应当据为外部原句的对象；已实际读appendix_afdm_channel_model.tex。',
    '与先发送N_CPP个前缀样本、随后从0起编号的N个有用样本相容；分数delay需要完整的样间波形定义。',
    'φ_n(ξ)含wξ=<ξ>_N和ζ_n(w)=floor(2c1w+n/N)；该具体组合及负时间延拓应归本稿，不宜说Huang/Bemani给了这个完整φ式。',
    '保留为本稿定义/内部指引。'),
sentence('SUPPORTED_PARAPHRASE', [ref('huang2026',2,'II',HUANG_LEAK,eq='(5)后')],
    '删In practical propagation environments；fractional Doppler shifts and fractional time delays改为Fractional delays and Doppler shifts；introduce改cause；of (5)改为in本文算子式；H_eff改H_k。',
    '原句定位很明确且含义基本相同，但有主动删改和同义改写，不是只换必要术语/符号。',
    '对分数delay/Doppler通常引起扩散的定性说法有来源支持；措辞can保留可能性，并非说所有参数必然显著泄漏。将它特指本文G需以本稿波形选择为条件。',
    'Huang说其式(5)，本文替换成路径算子；这种引用迁移不是自动的矩阵等价证明。',
    '若坚持原句要求，保留Huang整句句法，仅替换已解释的符号/方程；同时明确本稿G的适配性质。')],
dict(source_order=['Huang/Ding有效信道背景','本稿多天线张量及参考时刻','本稿G和连续波形定义/推导','Huang泄漏原句的改写'], cross_source_combination=True,
     structure_changes_conditions='是：单天线矩阵变为多天线张量、引入绝对时间g、频率折返连续波形和多周期CPP；这些是本文模型条件。Huang式(5)有分数效应，不足以自动推出本文所有G定义。',
     verdict='5句为本文定义/推导，1句为有明确原句依据的改写；不得把附录推导与外部原句证明混为一类。'))

paragraph('P08', ['For frame $q$', 'Since $\\nu_k$', 'The phase rotation'], [
sentence('AUTHOR_DEFINED_OR_DERIVED', [ref('shen2025',4,'II-B',locator='式(3)用n+qN表示OTFS帧中的OFDM符号起点；不是本文AFDM样本起点',eq='(3)')],
    '按本文帧结构新定义g_q。',
    '所查来源没有这个完整原句或AFDM含CPP的g_q式；这是从P06帧长计算出的索引。',
    '对q从0起、帧连续、每帧同一CPP长度的约定，首个有效样本为N_CPP+q(N+N_CPP)。',
    'g_q−g0=q(N+N_CPP)，乘Ts得到qT_frame。',
    '保留为本稿计时定义。'),
sentence('AUTHOR_DEFINED_OR_DERIVED', [ref('huang2026',2,'II', 'The resulting Doppler term D(ψ) is assumed to be common to all propagation paths within the same satellite-to-ground (S2G) link [15].'), ref('shen2025',4,'II-B',locator='式(8)–(10)：OTFS相位φ_u,q[l′]=exp(j2π k_tilde_i,u q)，依赖路径对应delay位置；不是本文单设备统一β',eq='(8)–(10)')],
    '以公共Doppler为条件从本文G提出标量；新设β_k的wrap定义。',
    '公共Doppler假设可定位Huang；Shen有跨帧相位先例，但本文整句、H_k^(q)=exp(jqβ_k)H_k及wrap不是来源原句。',
    '在公共ν_k、路径增益/延迟/阵列响应恒定及同一波形基的前提下成立。每个D_ν,gq=exp(j2πνqT_frame)D_ν,g0，标量可提出路径和。不同路径不同Doppler时一般不能提出一个公共标量。',
    '对整数q，wrap不改变exp(jqβ)；ν单位为Hz，2πνT_frame无量纲。该等式在冻结物理参数模型中精确，在真实参数仅近似恒定时为同阶近似。',
    '明确标为本文推导，引用Huang只支撑公共Doppler假设；不要声称Shen已经给出本AFDM公式。'),
sentence('AUTHOR_DEFINED_OR_DERIVED', [ref('shen2025','4–5','II-B',locator='式(9)后跨页段：有效OTFS张量约定下Q帧近似恒定而可汇集更多观测；p5讨论逐帧累积的分数Doppler相位',eq='(9),(10)后'), ref('huang2026',3,'III-A',locator='式(6)后讨论多个pilot sequences及相邻序列间effective channel变化近似可忽略',eq='(6)后')],
    '把本文公共标量模型解释为同一H_k的多帧观测；不是来源关于OTFS张量或近似信道不变的原句。',
    '“更多观测”思想有来源，但本句前半精确解释本文H_k^(q)及其标量相位，后半是由此得出的结论；未定位可只术语替换的原句。',
    '在前句假设内成立。Q帧提供同一参考张量的多组相位调制观测；并未由此保证相位已知、可辨识或足以唯一恢复全部系数。',
    '可由上句直接代入每帧线性观测得到。Huang相邻序列变化可忽略的近似不能当作本文累积相位已被处理的证据。',
    '保留为本稿推导解释，并在逐句来源统计中单列。')],
dict(source_order=['本稿帧计时','Huang公共Doppler假设 + 本稿G分解','本稿多观测结论；Shen/Huang仅提供相关先例'], cross_source_combination=True,
     structure_changes_conditions='是：Shen原模型允许逐路径相位且为OTFS；本文借助公共Doppler和冻结路径参数约化为每设备公共标量。Huang相邻pilot间近似不变也不等于该相位分解。',
     verdict='3句全是本文定义/推导，不是已有参考完整原句；技术成立的条件已显式列出。'))

counts = Counter(s['category'] for p in data for s in p['sentences'])
audit = dict(scope='P04–P08；只读当前稿件和参考原文，不读取旧评审结论或同伴审计',
    source_file='D:/afdm-gfra/paper/C-STMP/sections/02_system_model.tex',
    source_sha256=json.loads((BASE/'manifest.json').read_text(encoding='utf-8-sig'))['source_sha256'],
    category_policy='按完整英文语法句及真实文本增删改分类；公式的重排、推广和条件另在formula_adaptation/technical_status列明，技术成立不代表原句标准通过。',
    search_scope=['cai2026 PDF及clean.pages：II-A、V-C；cai2026_stmp_v2相同位置文本核对', 'ding2026 PDF及clean.pages：II', 'huang2026 PDF及clean.pages：II、III-A', 'bemani2022 PDF及clean.pages：II、III-A/B/C/D', 'shen2025 PDF及clean.pages：II-B及II-C相关段', '本文appendix_afdm_channel_model.tex及06_simulation_results.tex仅用于技术核验，不作参考原句证据'],
    inspected_pdf_pages=[dict(key='cai2026', pages=[4,10,11]),dict(key='ding2026',pages=[2]),dict(key='huang2026',pages=[2,3]),dict(key='bemani2022',pages=[7,8,9]),dict(key='shen2025',pages=[4,5])],
    pdf_inspection_notes='均用pdftoppm从原PDF渲染，并由view_image实际查看，图在b_render/。Poppler报告部分系统字体映射警告，但所核公式与文字可读。Bemani p10用clean.pages定位，未声称已视觉查看。Ding p2的F/Fᴴ及A/Aᴴ不一致、Huang p2式(5)的负Doppler约定、Bemani p7–9周期/前缀范围均已回看原页。',
    quotation_policy=dict(bemani2022_english_direct_quote_words=0,li2023_english_direct_quote_words=0, note='用户提供PDF的必要原句可引；公式采用Unicode符号转写，英文原词保持；Bemani只给页/式定位和中文说明。'),
    paragraphs=data,
    summary=dict(sentence_count=sum(len(p['sentences']) for p in data),categories=dict(counts),
        exact_term_only_or_reasonable_combination=0,
        conclusion='P04–P08共21个完整语法句全部覆盖；7句为支持性改写，14句为本稿定义/推导。没有一句达到当前严格的“完整原句仅必要术语替换或合理原句组合”要求。此结论不等于21句技术错误；导频构造、CPP整数样本关系与公共Doppler相位均有条件成立的解析说明。',
        limitations='未启动任何实验，也未核验实现代码或数值输出；未宣称Huang式(5)与本文分数delay、多周期CPP的G完整等价。来源缺失结论仅限上述语料，不声称全部文献无对应句。'))
(BASE/'b_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

lines = ['# P04–P08 逐句来源核查', '', audit['summary']['conclusion'], '',
         '分类依据是完整英文句是否可由原句按限定改动得到。数学式成立、内容有来源、英文句来自原句是三件不同的事。未改正文、模型或实验。', '',
         '## 关键边界', '',
         '- Cai的行正交思想可作依据；本文Q×KN导频矩阵和每设备每帧E_p定义是新构造。VI-A给出的DFT构造解析上满足两项要求。',
         '- Bemani式(14)支持整数采样点的多周期chirp关系；式(19)是单周期写法，后续信道明示l_max<N及整数delay。本文mod形式、长CPP适用范围及参数限制须归本文推导/设定。',
         '- Huang确实给出分数delay/Doppler矩阵；但其式(5)不是本文F_A D_ν,g B_d，仍需核对Doppler符号、折返区间、起点相位与长CPP范围。本文附录不能冒充外部原句。',
         '- 每设备公共跨帧相位由公共Doppler和固定路径参数推出；Shen的OTFS逐路径/延迟位置相位只提供相关先例。',
         '- 原PDF确认Ding式(2)的F/Fᴴ及对Aᴴ的命名存在不一致；本文当前DAFT符号与其标量式及Bemani/Huang一致，不应为追逐原句而复现该不一致。', '',
         '## 完整逐句记录', '']
for p in data:
    lines += [f"### {p['id']}", '', f"段落结构：{' → '.join(p['paragraph_structure']['source_order'])}", '',
              f"条件变化：{p['paragraph_structure']['structure_changes_conditions']}", '', p['paragraph_structure']['verdict'], '']
    for s in p['sentences']:
        lines += [f"#### {s['id']} — {s['category']}", '', '当前完整句（含连续公式及where说明）：', '', '```tex', s['draft_tex'].strip(), '```', '', '原文定位：', '']
        if not s['source_refs']:
            lines.append('- 无外部原句；本文内部定义。')
        for r in s['source_refs']:
            line=f"- **{r['key']}，PDF p. {r['page']}，{r['section']}"
            if r.get('eq'): line += f"，式 {r['eq']}"
            lines.append(line+'**。')
            if r.get('quote'): lines += ['', '> '+r['quote'], '']
            if r.get('locator'): lines += ['  '+r['locator']]
        lines += ['', '**实际改动：** '+s['changes'], '', '**分类理由：** '+s['reason'], '',
                  '**技术核验：** '+s['technical_status'], '', '**公式适配：** '+s['formula_adaptation'], '',
                  '**处理建议：** '+s['action'], '']
lines += ['## 覆盖及原页检查', '',
          '- 五段均由Pxx.input.txt精确连续切分；按序拼接与输入完全一致（比忽略空白更严格）。21句，无漏句或重复。',
          '- 分类数：'+json.dumps(dict(counts),ensure_ascii=False)+'。覆盖通过不代表原句标准通过。',
          '- 实际视觉查看：Cai PDF 4、10、11；Ding 2；Huang 2、3；Bemani 7、8、9；Shen 4、5。',
          '- 渲染文件位于b_render/；原文与图像只作为本次审计证据。Bemani直接英文引语为0词，Li为0词。',
          '- '+audit['summary']['limitations'], '']
(BASE/'b_audit.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps(dict(sentences=audit['summary']['sentence_count'], categories=dict(counts), coverage='exact concatenation all five paragraphs'),ensure_ascii=False))
