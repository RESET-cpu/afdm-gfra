"""Evidence-backed inventory of names actually used in Chapter II; never edits TeX."""
from pathlib import Path
import collections
import hashlib
import json
import re
import sys
import unicodedata
from pypdf import PdfReader

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
PAPER = ROOT / 'paper/C-STMP'
TEXTS = PAPER / 'checks/full_terminology_audit_20261030/source_text'

# group | name in chapter | anchor in TeX | status | source | PDF page | source phrase | qualification
# 原词允许单复数、大小写和排版连字符变化，不允许词序重排或近义替换冒充原词。
DATA = r'''场景与物理信道|System Model|System Model|原词|cai2026|3|system model|章标题已有用例。
场景与物理信道|LEO satellite-enabled grant-free random access system|LEO satellite-enabled grant-free random access system|原词|shen2025|3|LEO satellite-enabled grant-free random access system|§II，系统场景原词；不表示本文采用其 OTFS 系统。
场景与物理信道|LEO satellite|LEO satellite|原词|shen2025|3|LEO satellite|沿用已有卫星名称。
场景与物理信道|AFDM|where AFDM|原词|bemani2022|1|affine frequency division multiplexing|该文题名及摘要给出 AFDM 全称。
场景与物理信道|doubly dispersive effect|doubly dispersive effect|原词|shen2025|3|doubly dispersive effect|§II。
场景与物理信道|terrestrial-satellite links (TSLs)|terrestrial-satellite links (TSLs)|原词|shen2025|2|terrestrial-satellite links|§I，含 TSLs 缩写。
场景与物理信道|single-antenna terrestrial devices|single-antenna terrestrial devices|原词|shen2025|3|single-antenna terrestrial devices|§II。
场景与物理信道|uniform planar array (UPA)|uniform planar array (UPA)|原词|shen2025|3|uniform planar array|§II，含 UPA 缩写。
场景与物理信道|antennas|antennas|原词|shen2025|3|antennas|§II，天线数量的名称。
场景与物理信道|transmission block|transmission block|原词|cai2026|4|transmission block|§II-A。
场景与物理信道|active devices|active devices|原词|cai2026|4|active devices|§II-B；active/inactive 条件也见同页式(1)及式(4)后的说明。
场景与物理信道|pilot resources|pilot resources|待核||||未在本轮检索的现有参考语料中核得完整名称；Cai p.1 的原词为 resources for pilot transmission，可直接采用。
场景与物理信道|GNSS capabilities|GNSS capabilities|原词|shen2025|3|GNSS capabilities|§II，整组表达和缩写均来自原文。
场景与物理信道|Terrestrial-Satellite Link Model|Terrestrial-Satellite Link Model|原词|shen2025|3|Terrestrial-Satellite Link Model|§II-A 原小节标题。
场景与物理信道|high mobility|high mobility|原词|shen2025|3|high mobility|§II-A，描述卫星运动。
场景与物理信道|time variation|time variation|原词|shen2025|3|time variation|§II-A，描述信道随时间变化。
场景与物理信道|multipath propagation|multipath propagation|原词|shen2025|3|multipath propagation|§II-A。
场景与物理信道|doubly dispersive channel model|doubly dispersive channel model|原词|shen2025|3|doubly dispersive channel model|§II-A。
场景与物理信道|common Doppler shift|common Doppler shift|原词|huang2026|4|common Doppler shift|§IV，描述各路径共享 Doppler；不是只匹配独立单词。
场景与物理信道|receiver compensation for the common delay|receiver compensation for the common delay|适配||||common delay 见 Shen p.3；接收端补偿的完整表述尚未核得同文用例，是本文操作说明，不能当成已有命名。
场景与物理信道|channel impulse response|channel impulse response|原词|li2023|3|channel impulse response|§II-B，式(1)–(2)附近。
场景与物理信道|time instant|time instant|原词|li2023|3|time instant|§II-B；本文另行规定时间原点。
场景与物理信道|number of physical paths|number of physical paths|原词|shen2025|3|number of physical paths|§II-A，式(1)后。
场景与物理信道|path gain / path gains|path gain|原词|shen2025|3|path gain|§II-A，式(1)后；增益为 1 的路径没有另取 unit-gain path 等名称。
场景与物理信道|Dirac delta function|Dirac delta function|原词|shen2025|3|Dirac delta function|Notations；不采用其他稿件误写的 Dirichlet function。
场景与物理信道|differential delay|differential delay|原词|shen2025|3|differential delay|§II-A，式(1)后。
场景与物理信道|propagation delay|propagation delay|原词|shen2025|3|propagation delay|§II-A，式(1)后。
场景与物理信道|common delay|common delay|原词|shen2025|3|common delay|§II-A，图1及式(1)后的定义。
场景与物理信道|propagation time|propagation time|原词|shen2025|3|propagation time|§II-A，公共时延的说明。
场景与物理信道|beam coverage|beam coverage|原词|shen2025|3|beam coverage|§II-A。
场景与物理信道|array response vector|array response vector|原词|li2023|3|array response vector|§II-B；p.4 给出阵列式。当前稿已不使用 UPA response。
场景与物理信道|wavelength|wavelength|原词|li2023|4|wavelength|§II-B，阵列响应定义后。
场景与物理信道|spacing between adjacent antennas along the v-axis|spacing between adjacent antennas|原词|li2023|4|spacing between adjacent antennas|§II-B，原文随后为 along the v-axis；本文只将坐标集合 x/y 换为 y/z。
场景与物理信道|directional cosines|directional cosines|原词|shen2025|3|directional cosines|§II-A。
场景与物理信道|z-axis / y-axis|z-axis and y-axis|原词|shen2025|3|z-axis and y-axis|§II-A，方向余弦说明。
场景与物理信道|arrival angles|arrival angles|待核||||未核得原词；Li §II-B/p.4 用 paired angles-of-arrival，Cai §VI-A/p.11 用 angle of arrival。可改为 angles of arrival，不能将词序不同登记为原词。
AFDM与导频|Multi-Frame AFDM Transmission|Multi-Frame AFDM Transmission|适配||||Shen p.4 有 multi-frame OTFS transmission；Huang p.2 有 AFDM frame。当前标题是技术对象替换后的标题，不能宣称为同一论文已有的完整名称。
AFDM与导频|chirp subcarriers / chirp subcarrier|chirp subcarriers|原词|huang2026|2|chirp subcarriers|§II 的 AFDM chirp subcarriers。
AFDM与导频|pilot transmission|pilot transmission|原词|cai2026|4|pilot transmission|§II-A；分配 Q 个 AFDM 帧是本文设定。
AFDM与导频|AFDM frame / AFDM frames|AFDM frames|原词|huang2026|2|AFDM frame|§II；允许单复数变化。
AFDM与导频|pilot symbol / pilot symbols|pilot symbol|原词|cai2026|4|pilot symbol|§II-A，式(2)后。
AFDM与导频|pilot vector|pilot vector|原词|arvinte2023|3|pilot vectors|§II-A，式(1)后；原文向量是空间导频，本文为子载波导频；名称适用，但不照搬其维度或构造。此来源已列入当前 PDF，无需依赖 Quayum。
AFDM与导频|known pilot matrix|known pilot matrix|适配||||pilot matrix 见 Cai p.4；Arvinte p.3 有 having knowledge of the transmitted pilot matrix。known pilot matrix 这个完整搭配未核得，已知性条件不等于新方法名。
AFDM与导频|satellite receiver|satellite receiver|原词|shen2025|1|satellite receiver|摘要，名称原词。
AFDM与导频|entries|entries|原词|cai2026|14|pilot matrix whose entries|Fig.12 附近；为矩阵元素的通用名称。
AFDM与导频|pilot energy|pilot energy|外部用例||||上轮仅核得 Tang 等 arXiv:2610.23420 §III-A/p.3 的 total useful-sample pilot energy per frame；Tang 未在本稿书目库或 PDF 参考文献中。Cai p.4 用 transmit power budget，不能作该名称的直接出处，也不能不核对量纲就替换 energy 为 power。
AFDM与导频|time-domain transmitted signal|time-domain transmitted signal|原词|ding2026|2|time-domain transmitted signal|§II，式(1)前。
AFDM与导频|inverse discrete affine Fourier transform (IDAFT)|inverse discrete affine Fourier transform (IDAFT)|原词|ding2026|2|inverse discrete affine Fourier transform|§II，式(1)前，原文同时给出 IDAFT。
AFDM与导频|AFDM modulation parameters|AFDM modulation parameters|原词|ding2026|2|AFDM modulation parameters|§II，式(1)后。
AFDM与导频|sampling interval|sampling interval|原词|ding2026|2|sampling interval|§II，式(3)后。
AFDM与导频|subcarrier spacing|subcarrier spacing|原词|huang2026|2|subcarrier spacing|§II；Ding p.2 另有 sub-carrier spacing 的拼写。
AFDM与导频|discrete affine Fourier transform (DAFT) matrix|discrete affine Fourier transform (DAFT) matrix|原词|ding2026|2|DAFT matrix|名称 DAFT matrix 见 Ding；本轮另外重读 Xu §II-B/印刷p.3（带封面 PDF p.4）式(6)后，核得完整展开名称。在线证据见 REMOTE_EVIDENCE.json，不依靠不同单词拼接通过。
AFDM与导频|chirp-periodic prefix (CPP)|chirp-periodic prefix (CPP)|原词|bemani2022|8|chirp-periodic prefix|§III-A，式(19)前；含 CPP 缩写。
AFDM与导频|CPP length|chirp-periodic prefix (CPP) length|原词|bemani2022|9|CPP length|§III-B，式(22)前；正文以括号展开 CPP。
AFDM与导频|maximum differential delay|maximum differential delay|原词|shen2025|12|maximum differential delay|小段 3) Feasibility of integration with existing satellite infrastructure；名称直接出现，本文 CPP 条件仍是本文适配。
AFDM与导频|time duration of an AFDM frame with CPP|time duration of an AFDM frame with CPP|适配||||Shen §II-B/p.4 的原文为 time duration of a OFDM symbol with CP；本文换成 AFDM frame/CPP，不能说完整释义原样出现过。
AFDM与导频|transmit waveform|transmit waveform|原词|shen2025|4|transmit waveform|§II-B，式(3)前。名称源于 Shen；本文连续波形公式另有 Bemani 的技术依据，二者不要混同。
AFDM与导频|CPP relation|CPP relation|适配||||CPP 有 Bemani 原词，relation 是本文对式(5)的回指；未核得 CPP relation 完整名称，不作为既有专门关系名称通过。
AFDM与导频|effective channel|effective channel|原词|huang2026|2|effective channel|§II，式(4)–(5)后；本文三阶维度不是来源相同公式的保证。
AFDM与导频|transmitted symbol position|transmitted and received symbol positions|待核||||正文合写 transmitted and received symbol positions。Shen p.4 的 received symbol position 不能反向证明 transmitted symbol position；未核得当前发送符号索引含义的原词。
AFDM与导频|received symbol position|transmitted and received symbol positions|原词|shen2025|4|received symbol position|§II-B，式(9)后的解释；Shen 为 delay 维，本文为 DAFT 输出位置，保留其通用索引含义，不声称域相同。
AFDM与导频|antenna index|antenna index|书目库原词|ke2020|13|antenna index|Appendix A；Ke 已在 references.bib，当前 main.bbl 没有该条。词源成立，不能宣称读者已能从当前 PDF 参考文献找到它。
AFDM与导频|channel response|channel response|原词|ding2026|2|channel response|§III-A，式(6)前；使用名称，不照搬导频提取模型。
AFDM与导频|power leakage|Power leakage|原词|huang2026|2|power leakage|§II，式(5)后。
AFDM与导频|fractional delays|fractional delays|原词|huang2026|2|fractional delay|§II，式(5)前；单复数变化，不要求全文恰好有复数拼写。
AFDM与导频|delay / delays|delays|原词|shen2025|3|delay|物理路径时延名称；本文不另外命名 d、g 等辅助变量。
AFDM与导频|Doppler shift / Doppler shifts|Doppler shifts|原词|shen2025|3|Doppler shift|§II-A；单复数变化。
AFDM与导频|sparsity|sparsity|原词|huang2026|2|sparsity|§II，式(5)后，信道稀疏性语境。
AFDM与导频|wrap|operatorname{wrap}|待核||||未在已核参考论文中找到将角度映射到 [-pi,pi) 的同名函数。3GPP 的计数器 wrap around 与 O'Leary 的 wrapper 不同义，不能用来通过。
AFDM与导频|angle|maps an angle|原词|shen2025|3|angle|§II-A，角的基本名称；不能用该词的出处替代 wrap 算子的出处。
AFDM与导频|phase evolution across frames|phase evolution across frames|适配||||当前引言贡献段有此表述，但本轮要求参考论文出处，不能以自己的引言证明已有论文用过。Shen p.5 的原词为 phase rotation，并说明 accumulates across multiple frames。
问题与概率模型|Problem Formulation|Problem Formulation|原词|shen2025|5|Problem Formulation|§II-C 原标题；Wei §II-B/p.2 也使用。
问题与概率模型|independent and identically distributed (i.i.d.)|independent and identically distributed (i.i.d.)|原词|cai2026|4|independent and identically distributed|§II-A，同时给出 i.i.d. 缩写。
问题与概率模型|indicator function|indicator function|原词|cai2026|4|indicator function|§II-A，式(1)前，与 0/1 活动指示用途一致。
问题与概率模型|device activity|device activity|原词|cai2026|4|device activity|§II-A，式(1)前。
问题与概率模型|probability of a device being active|probability of a device being active|原词|cai2026|4|probability of a device being active|§II-A，式(1)后；本文改概率变量字母不影响名称。
问题与概率模型|activity states|activity states|原词|ding2026|2|activity state|§II，式(4)后。单数原词已核得，因此复数可以通过；但不能据此证明本文整块不变假设。
问题与概率模型|block transmission|block transmission|原词|shen2025|1|block transmission|§I；原文恒定的是 fading channels，本文活动不变仍是自己的假设。
问题与概率模型|inter-frame phase rotation|inter-frame phase rotation|适配||||phase rotation 及其跨帧累积见 Shen p.5，但 inter-frame phase rotation 完整命名未核得。inter-frame interference 不能证明这个不同的名称。
问题与概率模型|received signal|received signal|原词|cai2026|4|received signal|§II-A，式(3)前。
问题与概率模型|AWGN matrix|AWGN matrix|原词|cai2026|4|AWGN matrix|§II-A，式(3)后；同为 i.i.d. 复高斯噪声矩阵。
问题与概率模型|block-sparsity structure|block-sparsity structure|原词|cai2026|4|block-sparsity structure|§II-A，式(4)后；对应设备不活动时整个块为零。
问题与概率模型|sporadic access|sporadic access|原词|cai2026|4|sporadic access|§II-A，式(4)后。
问题与概率模型|inverse problem|inverse problem|原词|wei2026|2|inverse problem|§II-B；当前观测的行列数条件仍按本文公式判断。
问题与概率模型|underdetermined|underdetermined|原词|wei2026|2|underdetermined|§II-B；原词为 severely underdetermined，本文未沿用程度词。
问题与概率模型|observation|observation|原词|cai2026|4|observation|§II-B，目标段中的 observation Y。
问题与概率模型|Bayesian inference framework|Bayesian inference framework|原词|cai2026|4|Bayesian inference framework|§II-B，目标段。
问题与概率模型|channel sparsity|channel sparsity|原词|cai2026|1|channel sparsity|§I；名称出处不意味着 Cai 使用本文相同的非稀疏信道模型。
问题与概率模型|channel prior|channel prior|原词|cai2026|5|channel prior|§II-B；本文 for training 只是 q_tr 的用途说明，不登记为独立名称 training prior 或 channel prior for training。
问题与概率模型|joint posterior distribution|joint posterior distribution|原词|cai2026|4|joint posterior distribution|§II-B，式(5)前；不自动证明本文固定前端后的后验等同于全联合后验。
问题与概率模型|Bayes' theorem|Bayes' theorem|原词|cai2026|2|Bayes' theorem|§I 的正确拼写；Cai p.4 的 Baye’s theorem 是误拼，不照抄。
问题与概率模型|conditional independence relationships|conditional independence relationships|原词|cai2026|4|conditional independence relationships|§II-B，式(5)前；具体独立对象是本文建模假设。
问题与概率模型|column|column|原词|cai2026|5|column|式(5)后；第 j 列是本文索引。
问题与概率模型|MMSE estimate|MMSE estimate|原词|li2023|8|MMSE estimate|§IV-A，原文使用 estimate；Cai p.4 使用 MMSE estimator，不能混报词形。
问题与概率模型|posterior probability of activity|posterior probability of activity|原词|cai2026|7|posterior probability of activity|§III-B2，式(30)后。
具名算子|diag|diag|原词|shen2025|3|diag|Notations 给出从元素组成对角矩阵的同义算子。wrap 已单独列出。'''


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize(text):
    text = unicodedata.normalize('NFKC', text).replace('’', "'")
    return re.sub(r'\s+', ' ', text)


def phrase_regex(phrase):
    # 只修复 PDF 断词及排版连字符，命中仍经人工读上下文。
    return re.compile('[\\s\\-]*'.join(map(re.escape, re.sub(r'[\s-]', '', normalize(phrase)))), re.I)


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def run():
    protected = [PAPER / 'main.tex', PAPER / 'references.bib', PAPER / 'main.bbl', PAPER / 'main.pdf']
    protected += sorted((PAPER / 'sections').glob('*.tex'))
    before = {str(p.relative_to(ROOT)): digest(p) for p in protected}
    baseline = OUT / 'BASELINE.json'
    if not baseline.exists():
        write_json(baseline, before)
    else:
        assert json.loads(baseline.read_text(encoding='utf-8')) == before, 'Manuscript changed since audit baseline'

    tex = (PAPER / 'sections/02_system_model.tex').read_text(encoding='utf-8')
    flat = normalize(tex)
    # Map normalized matches back to source lines through whitespace-only matching.
    def line_of(anchor):
        match = re.search(r'\s+'.join(map(re.escape, anchor.split())), tex, re.I)
        assert match, ('Not in Chapter II', anchor)
        return tex[:match.start()].count('\n') + 1

    corpus = {p.stem: json.loads(p.read_text(encoding='utf-8-sig')) for p in TEXTS.glob('*.json')}
    corpus['ke2020'] = [p.extract_text() for p in PdfReader(ROOT / 'reference/literature/ke2020_gmmv_amp.pdf').pages]
    bib = set(re.findall(r'@\w+\s*\{\s*([^,\s]+)', (PAPER / 'references.bib').read_text(encoding='utf-8')))
    cited = set(re.findall(r'\\bibitem\{([^}]+)\}', (PAPER / 'main.bbl').read_text(encoding='utf-8')))

    rows = []
    for number, line in enumerate(DATA.splitlines(), 1):
        group, name, anchor, status, key, page, phrase, note = line.split('|')
        row = dict(id=number, group=group, name=name, tex_line=line_of(anchor), status=status, source=key, pdf_page=int(page) if page else None, source_phrase=phrase, note=note)
        if key:
            assert key in bib
            if status == '原词':
                assert key in cited
            source = normalize(corpus[key][int(page) - 1])
            match = phrase_regex(phrase).search(source)
            assert match, ('Source phrase not found', number, key, page, phrase)
            row['source_context'] = source[max(0, match.start() - 55):match.end() + 190]
            row['in_bib'] = key in bib
            row['in_current_pdf_references'] = key in cited
        rows.append(row)

    # Save bounded, literal-phrase checks for the unresolved/full-expression items.
    unresolved = []
    for row in rows:
        if row['status'] not in {'待核', '适配', '外部用例'}:
            continue
        hits = []
        for key, pages in corpus.items():
            for page, value in enumerate(pages, 1):
                text = normalize(value)
                match = phrase_regex(row['name']).search(text)
                if match:
                    hits.append(dict(source=key, pdf_page=page, context=text[max(0, match.start()-50):match.end()+140]))
        unresolved.append(dict(name=row['name'], hits=hits, meaning_review='Nonempty hits require manual same-meaning review; wrap-around counters/wrappers are not the angle operator.'))

    counts = dict(collections.Counter(r['status'] for r in rows))
    write_json(OUT / 'INVENTORY.json', rows)
    write_json(OUT / 'SEARCH_SCOPE.json', dict(local_page_text_keys=sorted(corpus), keys_in_bib=sorted(bib), keys_in_current_pdf_references=sorted(cited), bib_keys_without_full_local_page_text=sorted(bib-set(corpus)), caution='Not found means not verified in this bounded corpus, never absent from all literature. Xu is not included in automated full-text absence claims.'))
    write_json(OUT / 'FULL_EXPRESSION_SEARCH.json', unresolved)
    write_json(OUT / 'SOURCE_TEXT_HASHES.json', {str(p.relative_to(ROOT)): digest(p) for p in TEXTS.glob('*.json')})

    report = [
        '# 第二章全部具名对象与技术表达的出处核查', '',
        '日期：2026-11-01。核查对象：当前 `sections/02_system_model.tex` 的全部正文、小节标题与公式中的具名算子。第二章 SHA-256：`' + digest(PAPER / 'sections/02_system_model.tex') + '`。本轮只写核查文档，未修改正文、书目或阅读 PDF。', '',
        '## 结论与口径', '',
        '**不能确认所有名称都已经来自现有参考文献。** 完整清单合并重复用法及单复数，共 ' + str(len(rows)) + ' 项：' + '；'.join(str(v)+' 项'+k for k,v in counts.items()) + '。这些数量是下面逐项清单的分类统计，不是对全体英文单词的统计。', '',
        '- **原词**：当前 PDF 已列出的参考论文实际使用该名称，语义适用。允许单复数、大小写、排版连字符及已定义缩写的展开，不允许换词序或拼接近义词后当成原词。名称适用不等于其公式、域、维度和假设全部相同。',
        '- **书目库原词**：原词有参考论文依据，该论文已在 `references.bib`，但尚未列入当前 `main.bbl`／PDF 参考文献。',
        '- **适配**：核心术语有来源，完整标题、修饰语或操作描述是本文适配；按作者“完整名称也要已有出处”的标准，不能并入原词通过项。',
        '- **外部用例**：此前找到的外部论文有用例，但不属于本稿现有书目，不能拿来宣称现有参考文献已覆盖。',
        '- **待核**：本轮没有核到同义完整用例，不表示学界从未用过。', '',
        '本轮查询了本地已有的 27 份逐页参考文本及 Ke 原 PDF；出处判定还逐一阅读了命中处上下文。未持有全文的 Xu 等条目不纳入“全文没出现”的断言；具体检索边界见 `checks/ch2_all_names_20261101/SEARCH_SCOPE.json`。其中 3GPP 是标准而非论文，没有将其不同语义的词形匹配作为论文术语依据。', '',
        '变量字母、索引、取值集合和纯公式定义不因存在符号就自动获得一个英文名称。`q_tr` 的 for training 是用途说明；没有据此补造 training prior。CN、E、Pr、转置、范数等只有数学记号的项沿用 [变量审计](VARIABLE_NAMES_AUDIT.md) 的覆盖，不把核查者翻译出的名称混入本清单。正文未另取名字的 B_d、D、g_q 等也不重复制造名称。', '',
        '## 当前未能作为“现有参考文献原词”通过的项目', '',
        '| 编号 | 当前名称或完整表达 | 分类 | 原因／已经核实的替代依据 |',
        '|---|---|---|---|',
    ]
    for row in rows:
        if row['status'] != '原词':
            report.append(f"| {row['id']:02d} | {row['name']} | {row['status']} | {row['note']} |")
    report += ['', '## 全部逐项清单', '', '页码均为各来源 PDF 的文件页码；正文行号指本轮未修改的 TeX。相邻同源条目分开列出，便于逐项核对。', '']
    for group in dict.fromkeys(r['group'] for r in rows):
        report += ['### '+group, '', '| 编号 | 第二章实际名称 | 正文行 | 判定与出处 |', '|---|---|---|---|']
        for row in rows:
            if row['group'] != group:
                continue
            source = (f"`{row['source']}`，PDF p.{row['pdf_page']}，原词 `{row['source_phrase']}`。" if row['source'] else '')
            report.append(f"| {row['id']:02d} | {row['name']} | [L{row['tex_line']}](../sections/02_system_model.tex:{row['tex_line']}) | **{row['status']}**：{source}{row['note']} |")
        report.append('')
    report += [
        '## 对上轮记录的补充与纠正', '',
        '1. **pilot vector**：现已在当前参考文献 Arvinte §II-A/p.3 核到 pilot vectors，不再只依赖书目外的 Quayum。原文为向量导频；这里仅据此认定名称适用，不照搬空间维度和导频码本。',
        '2. **activity states**：Ding §II/p.2 的 activity state 是同一活动指示含义。允许单复数后可以通过。不能因为只搜索复数未命中就判定无出处。',
        '3. **antenna index**：Ke Appendix A/p.13 的词源成立，而且 Ke 本来就在 references.bib；但当前 PDF 没有引用到 Ke。应区分“书目库已有”和“阅读稿列出”。',
        '4. **pilot energy**：Tang 的用例不能算作本稿已有参考文献。此前“补查有出处”不能简写成“当前参考文献已有出处”。',
        '5. **arrival angles**：不能由 angle of arrival / angles-of-arrival 推出词序已被原文使用。此前变量核查未单列这处描述，本轮补上。',
        '6. 通过的是名称与语义，不是全部句子、全部模型条件和全部推导都来自同一参考论文。此前若作过“第二章所有内容都从已有论文来”的笼统保证，应以本清单为准撤回该保证。', '',
        '## 来源与复核入口', '',
        '| 书目键 | 本地原论文 | 本轮主要定位 |',
        '|---|---|---|',
        '| shen2025 | [Shen PDF](../../../reference/literature/shen2025.pdf) | pp.1–5、12 |',
        '| cai2026 | [Cai PDF](../../../reference/literature/cai2026.pdf) | pp.1–5、7、11、14 |',
        '| ding2026 | [Ding PDF](../../../reference/literature/ding2026.pdf) | p.2；不是 ding2026_iccdm |',
        '| huang2026 | [Huang PDF](../../../reference/literature/huang2026.pdf) | pp.2、4 |',
        '| li2023 | [Li PDF](../checks/strict_sentence_audit_20261029/sources/li2023.pdf) | pp.3–4、8 |',
        '| bemani2022 | [Bemani PDF](../checks/strict_sentence_audit_20261029/sources/bemani2022.pdf) | pp.1、8–9 |',
        '| wei2026 | [Wei PDF](../../../reference/literature/wei_yuan_2026_lstmp_v1.pdf) | p.2 |',
        '| arvinte2023 | [Arvinte PDF](../checks/full_terminology_audit_20261030/downloaded_sources/arvinte2023.pdf) | §II-A，p.3，式(1)后 |',
        '| ke2020 | [Ke PDF](../../../reference/literature/ke2020_gmmv_amp.pdf) | Appendix A，p.13；当前 PDF 未列该参考文献 |', '',
        'Xu 的 DAFT 矩阵完整名称另经 [Surrey 作者稿](https://openresearch.surrey.ac.uk/esploro/outputs/journalArticle/AFDM-aided-Grant-Free-Random-Access-for-LEO/991050765702346)在线 PDF 文本复核，定位为 §II-B、印刷 p.3／PDF p.4、式(6)后；见 [在线证据](../checks/ch2_all_names_20261101/REMOTE_EVIDENCE.json)。未将部分在线核验计入本地全篇检索覆盖。', '',
        '每项原文上下文见 [INVENTORY.json](../checks/ch2_all_names_20261101/INVENTORY.json)。检索命中只是取证辅助；wrap 的不同义命中明确未通过。第二章全部行均已人工通读，机器检查只验证登记名称确实出现在正文、登记的原词确实出现在指定来源页，以及正文未被更改，不能自动证明语言清单没有遗漏。', '',
        '本轮不改正文、不改公式、不新增引用。书目覆盖和完整表述未通过的项目保留待处理，不能为了通过审计而把本文适配伪称为引用原词。', '',
    ]
    (PAPER / 'docs/CHAPTER_II_NAMES_AUDIT.md').write_text('\n'.join(report), encoding='utf-8')
    after = {str(p.relative_to(ROOT)): digest(p) for p in protected}
    assert before == after
    write_json(OUT / 'VALIDATION.json', dict(rows=len(rows), counts=counts, named_source_matches_checked=sum(bool(r['source']) for r in rows), tex_anchors_checked=len(rows), protected_files=len(protected), manuscript_bib_bbl_pdf_unchanged=before==after, exhaustive_inventory='Manual read of all Chapter II lines; not an automated completeness proof.'))
    print(json.dumps(dict(rows=len(rows), counts=counts, protected_files_unchanged=len(protected)), ensure_ascii=False))


if __name__ == '__main__':
    run()
