from pathlib import Path
from collections import Counter
from datetime import datetime
import difflib
import hashlib
import json
import re
import unicodedata

ROOT = Path(__file__).resolve().parent
CATEGORIES = ('EXACT', 'TERM_ONLY', 'OTHER_CHANGE', 'NO_SOURCE', 'UNVERIFIED')
LABELS = {
    'EXACT': '原句一致', 'TERM_ONLY': '仅必要术语或符号替换',
    'OTHER_CHANGE': '存在非术语增删改', 'NO_SOURCE': '本次未定位可对齐整句',
    'UNVERIFIED': '未能核实',
}
TOPICS = ['系统总述', '物理信道与参数', '多帧传输与IDAFT', 'CPP与帧时长',
          '信道矩阵及其定义', '跨帧相位关系', '活动与接收观测模型',
          '块稀疏性与块内相关性', 'JADCE任务总述', '已知量与先验假设',
          '后验分解与估计目标', '消息传递困难与后续引出']
FINDINGS = [
    '删去固定波束和星载处理设置；把广播公共时延改为补偿公共时延。',
    '跨来源组合；时间原点、阵列完整定义和参数恒定说明等未定位整句。',
    '删去spreading-based；改写公式后的定义并加入导频能量说明。',
    '改变前缀条件及谓语，新增取模和长时延说明。',
    '矩阵、逐项算子及索引说明多数未定位整句；泄漏句也有删改。',
    '相位关系说明新增；删改原句原因、目标并改变原文叙述顺序。',
    '删去活动概率和功率预算限定；重写观测及堆叠公式后的where定义。',
    '前两句有连续来源；新增块内统计依赖解释未定位整句。',
    '任务总述与Cai一致；Q<KN说明未定位整句。',
    '将稍后更新改为由观测获得；训练先验及独立性说明未定位整句。',
    '删去后验表达式；改写整个where定义；联合估计目标句未定位。',
    '末两句一致；前两句各有删除，且跨原段与条目拼接。',
]

def read_json(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def words(s):
    s = re.sub(r'\\begin\{equation\}[\s\S]*?\\end\{equation\}', '', s)
    s = re.sub(r'\$[^$]*\$', '', s)
    s = re.sub(r'\\\([\s\S]*?\\\)', '', s)
    s = re.sub(r'\\(?:cite|label|eqref|ref)\{[^}]*\}', '', s)
    s = unicodedata.normalize('NFKC', s).replace('’', "'")
    return re.findall(r"[A-Za-z]+(?:['-][A-Za-z]+)*", s.lower())

def link(p, label=None):
    p = Path(p)
    return f'[{label or p.name}](<{p.as_posix()}>)'

def as_text(value):
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, indent=2)

manifest = read_json(ROOT/'manifest.json')
sources = read_json(ROOT/'SOURCES.json')
assert len(manifest['paragraphs']) == 12
assert sha(manifest['source_file']) == manifest['sha256'].lower(), '稿件与审查快照不同'
reports, validation_rows = [], []
totals = Counter()
for n, p in enumerate(manifest['paragraphs'], 1):
    pid = f'P{n:02d}'
    assert p['id'] == pid
    assert (ROOT/f'{pid}.md').is_file()
    d = read_json(ROOT/f'{pid}.json')
    assert d['paragraph_id'] == pid
    ss = d['sentences']
    assert [s['id'] for s in ss] == [f'{pid}-S{i:02d}' for i in range(1, len(ss)+1)]
    assert all(s['category'] in CATEGORIES for s in ss)
    a, b = words(p['text']), words(' '.join(s['draft'] for s in ss))
    diffs = [{'operation':tag, 'manuscript':a[i:j], 'audit':b[k:l]}
             for tag, i, j, k, l in difflib.SequenceMatcher(None, a, b).get_opcodes()
             if tag != 'equal']
    assert not diffs, (pid, diffs)
    counts = Counter(s['category'] for s in ss)
    for category in CATEGORIES:
        if category in d.get('counts', {}):
            assert d['counts'][category] == counts[category], (pid, category)
    for s in ss:
        assert s['draft'].strip() and s.get('reason')
        if s['category'] in ('EXACT', 'TERM_ONLY', 'OTHER_CHANGE'):
            assert s.get('source_file') and s.get('source_page'), s['id']
            assert s.get('source_quote') or s.get('source_locator'), s['id']
    totals.update(counts)
    validation_rows.append({
        'paragraph_id':pid, 'agent':f'/root/audit_ch2_p{n:02d}',
        'source_lines':[p['start_line'], p['end_line']], 'sentence_count':len(ss),
        'counts':dict(counts), 'complete_prose_token_coverage':True,
        'prose_token_count':len(a), 'sentence_ids_unique_and_consecutive':True,
        'report_sha256':sha(ROOT/f'{pid}.json'),
        'all_sentences_meet_strict_criterion':all(s['category'] in ('EXACT','TERM_ONLY') for s in ss),
    })
    reports.append(d)

source_checks = []
for s in sources:
    check = {'key':s['key'], 'file':s['pdf'], 'expected_sha256':s['sha256'],
             'actual_sha256':sha(s['pdf'])}
    check['unchanged'] = check['expected_sha256'].lower() == check['actual_sha256']
    assert check['unchanged'], s['key']
    source_checks.append(check)

total = sum(totals.values())
passed = totals['EXACT'] + totals['TERM_ONLY']
summary = [
    '# 第二章严格原句核对结果', '',
    '**结论：当前第二章不符合“每一句均来自参考文献原句，除必要术语替换外其余不变”的要求。**', '',
    f'十二个段落分别由十二个子代理逐句审查，主代理复核证据、句子边界、覆盖和计数。共{total}个完整说明句：'
    f'{totals["EXACT"]}句原句一致，{totals["TERM_ONLY"]}句仅必要术语或符号替换，'
    f'{totals["OTHER_CHANGE"]}句存在非术语增删改，{totals["NO_SOURCE"]}句本次未定位可对齐整句，'
    f'{totals["UNVERIFIED"]}句因证据不可读而未核实。严格单句通过{passed}/{total}；没有整段全部通过。', '',
    '此前将“根据原文改写”表述为“只做必要术语替换”不准确，应以本次逐句证据为准。', '',
    '## 范围与判定', '',
    f'对象：{link(manifest["source_file"], "当前第二章源文件")}，第4—280行的12个TeX正文段落。'
    '章节标题不计段；公式及其where/Here定义归入完整语法句，不把匹配的前半句拆出计为通过。', '',
    '只豁免空格、PDF断行与连字、TeX排版、引用及章节/公式号显示差异，以及可逐项列明的必要技术名称和数学符号替换。'
    '非术语删词、加解释、改谓语、改连接词、重排、跨句拼接均不通过。显示公式本身属于本文模型，未要求照抄，但公式周围的英文定义照常审查。', '',
    '“本次未定位”只表示在所核查语料中找不到可逐词对齐的完整句子，不等于该内容技术错误，也不等于所有论文均无相关依据。'
    '本报告不是数学正确性或术语适用性认证。', '',
    '## 分段结果', '',
    '| 段落 | 内容 | 原句一致 | 仅术语替换 | 非术语增删改 | 未定位整句 | 严格通过/总句数 |',
    '|---|---|---:|---:|---:|---:|---:|',
]
for i, row in enumerate(validation_rows):
    c = Counter(row['counts'])
    pid = row['paragraph_id']
    summary.append(f'| {link(ROOT/(pid+".md"),pid)} | {TOPICS[i]} | {c["EXACT"]} | {c["TERM_ONLY"]} | {c["OTHER_CHANGE"]} | {c["NO_SOURCE"]} | {c["EXACT"]+c["TERM_ONLY"]}/{row["sentence_count"]} |')
summary += [f'| **合计** | | **{totals["EXACT"]}** | **{totals["TERM_ONLY"]}** | **{totals["OTHER_CHANGE"]}** | **{totals["NO_SOURCE"]}** | **{passed}/{total}** |', '', '## 各段关键差异', '']
for i, finding in enumerate(FINDINGS, 1):
    summary.append(f'- **P{i:02d}：**{finding}')
summary += ['', '## 审查材料与交付', '',
    f'- {link(ROOT/"FULL_AUDIT.md", "完整逐句对照")}: 每句当前文字、候选原句或定位、页码、变更清单、结论；每段另附原段组织检查。',
    f'- 各Pxx.json保留代理完整原始证据，包括补充来源与检索范围；{link(ROOT/"VALIDATION.json", "覆盖与文件校验记录")}保留主代理复核结果。',
    f'- {link(ROOT/"manifest.json", "原稿快照与段落边界")}；{link(ROOT/"SOURCES.json", "来源文件及哈希")}；{link(ROOT/"PROTOCOL.md", "统一核对标准")}。', '',
    '直接核对用户提供的Shen、Cai期刊版、Cai v2、Ding、Huang原PDF；另补查Li和Bemani。两份补查来源分别为'
    '[Li arXiv:2207.11958](https://arxiv.org/abs/2207.11958)和'
    '[Bemani arXiv:2204.12798v2](https://arxiv.org/abs/2204.12798v2)。它们只在相关定义和CPP来源核对中使用。', '',
    '十二个子代理各负责一个段落，并非跨模型独立盲审。主代理复核了完整说明文字的顺序覆盖，回查来源及分类，未以公式合理性代替语言来源。', '',
    '本轮未修改论文正文或PDF。正文与审查起始快照SHA256一致：', '',
    f'`{manifest["sha256"]}`', '',
    '后续修改必须区分“可保留的原句”和“本文特有的模型说明”；不能仅为逐字一致而恢复不适用于本文的系统假设。此轮没有自动执行这些修改。', '',
]
(ROOT/'SUMMARY.md').write_text('\n'.join(summary), encoding='utf-8')

full = ['# 第二章完整逐句对照', '',
        f'总览与统计见{link(ROOT/"SUMMARY.md", "审查总览")}。本文件按P01—P12、每段S01起逐句列示。', '',
        '当前文字保留TeX以避免二次改写；来源引文保留各审查员核实的数学转写。具体排版规范化及补充候选来源详见对应JSON。', '']
for i, d in enumerate(reports):
    pid = d['paragraph_id']
    full += [f'## {pid}　{TOPICS[i]}', '', str(d['verdict']), '',
             f'原始证据：{link(ROOT/(pid+".json"))}；精简对照：{link(ROOT/(pid+".md"))}。', '']
    for s in d['sentences']:
        full += [f'### {s["id"]}　{LABELS[s["category"]]}', '', '**当前完整句：**', '',
                 '```latex', s['draft'], '```', '']
        if s.get('source_file'):
            full += [f'**来源：** {link(s["source_file"])}，PDF第{s.get("source_page")}页；{as_text(s.get("source_section", ""))}。', '']
        if s.get('source_quote'):
            full += ['**核对原句：**', '', '```text', s['source_quote'], '```', '']
        if s.get('source_locator'):
            full += ['**来源定位/检索边界：** '+as_text(s['source_locator']), '']
        full += ['**差异清单：**', '', '```json',
                 json.dumps(s.get('changes', {}), ensure_ascii=False, indent=2), '```', '',
                 '**判定理由：** '+s['reason'], '']
    full += ['### 段落组织', '', '```json',
             json.dumps(d['paragraph_structure'], ensure_ascii=False, indent=2), '```', '']
(ROOT/'FULL_AUDIT.md').write_text('\n'.join(full), encoding='utf-8')

validation = {
    'generated_at':datetime.now().astimezone().isoformat(),
    'scope':'第二章逐句来源与必要术语替换边界',
    'manuscript_file':manifest['source_file'], 'manuscript_sha256':manifest['sha256'],
    'manuscript_unchanged_since_manifest':True,
    'paragraph_count':12, 'distinct_paragraph_agent_count':12,
    'sentence_count':total, 'counts':{c:totals[c] for c in CATEGORIES},
    'strict_sentence_pass_count':passed,
    'paragraphs_with_all_sentences_passing':sum(r['all_sentences_meet_strict_criterion'] for r in validation_rows),
    'coverage_method':'显示公式、行内数学和交叉引用宏去除后，按NFKC英文词序逐项核对；包括完整说明文字，公式另由审查员按协议检查边界。覆盖检查不等于科学正确性验证。',
    'paragraphs':validation_rows, 'source_integrity':source_checks,
    'output_files':{f:sha(ROOT/f) for f in ('SUMMARY.md','FULL_AUDIT.md')},
}
(ROOT/'VALIDATION.json').write_text(json.dumps(validation, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'paragraphs':12, 'sentences':total, 'counts':dict(totals),
                 'strict_pass':passed, 'complete_coverage':True, 'manuscript_unchanged':True,
                 'source_hashes_unchanged':True}, ensure_ascii=False))
