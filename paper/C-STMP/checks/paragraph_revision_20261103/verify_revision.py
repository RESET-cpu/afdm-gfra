"""Check source changes only; do not compile, open, or render either PDF."""
from pathlib import Path
from collections import Counter
import difflib
import hashlib
import json
import re

RUN = Path(__file__).resolve().parent
PAPER = RUN.parents[1]
BEFORE = json.loads((RUN / 'BEFORE.json').read_text(encoding='utf-8'))
FILES = [p for p in BEFORE['files'] if p.endswith('.tex')]
MATH = re.compile(r'\\begin\{(equation\*?|align\*?|gather\*?)\}[\s\S]*?\\end\{\1\}')
FIGURE = re.compile(r'\\begin\{(figure\*?)\}[\s\S]*?\\end\{\1\}')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def paragraphs(text):
    masked = FIGURE.sub(lambda m: re.sub(r'[^\n]', ' ', m.group()), text)
    masked = re.sub(r'^\\(?:section|subsection|subsubsection|label)\{[^\n]*\}.*$', '', masked, flags=re.M)
    result = []
    for m in re.finditer(r'\S[\s\S]*?(?=\n[ \t]*\n|\Z)', masked):
        body = m.group().strip()
        if not body or body.startswith('%'):
            continue
        result.append({'line': masked[:m.start()].count('\n') + 1, 'text': body})
    return result

# Mapping follows the author's approved editorial assessment, not the earlier
# proposal to merge every split derived from the same Cai paragraph.
MAP = {
    'III': [
        ('III-01', 'Cai III, S3.p1, PDF p.5', '框架与两模块交换；沿用原段任务。'),
        ('III-02 + III-03首句', 'Cai III-A, S3.SS1.p1, PDF p.5, (6)–(8)', '标量协方差近似归回后验计算段；矩阵形式为本文模型。'),
        ('III-03余文 + III-04', 'Cai III-A, S3.SS1.p2, PDF pp.5–6, (9)–(11)', '外信息相除、重排、传送放在同段。'),
        ('III-05', 'Cai III-B, S3.SS2.p1–p2; III-B1, (20), PDF p.6', '保留已压缩的模块分工和输入模型；仍属多原段适配。'),
        ('III-06', 'Cai III-B1, S3.SS2.SSS1.p1–p3, PDF pp.6–7, (15)–(23)', '保留活跃条件、积分与估计量的紧凑推导，不声称单母段改写。'),
        ('III-07', 'Cai III-B2, S3.SS2.SSS2.p1, PDF p.7; Menon §2.1/§4.2', '活动后验原段的任务保留，完整先验积分和密度比为本文替换。'),
        ('III-08', 'Cai III-B3, S3.SS2.SSS3.p1, PDF p.7, (32)–(38); Liu §III-C/D', '混合分布与均值。'),
        ('III-09 + III-10', 'Cai III-B3, (36)–(38), PDF p.7; 本文空间协方差推导', '保留新增空间协方差段，将取迹平均接回；不是 Cai 同式。'),
        ('III-11 + III-12；删除 III-13', 'Cai III-B3, S3.SS2.SSS3.p2, PDF pp.7–8, (39)–(42)', '相除、正方差条件和下一轮输入同段；删除单独章节指引。'),
    ],
    'IV': [
        ('IV-01', 'Cai IV, S4.p1, PDF p.8; Menon §4.2', '章节引入；分别说明均值/方差与活动概率。'),
        ('IV-02', 'Cai IV-A, (43), PDF p.8; Shastri III-B, (38), PDF p.8; Dytso (1)–(3)', '一般协方差和复数实数转换为本文适配，保留独立模型段。'),
        ('IV-03 + IV-04', 'Cai IV-A, S4.SS1.p1, (44), PDF p.8; Dytso (3)', 'Tweedie 均值、score 定义及白噪声特例同段。'),
        ('IV-05', 'Cai IV-A, S4.SS1.p2, (45), PDF p.8; Dytso III, Proposition 1', '二阶 score 与协方差。'),
        ('IV-06', 'Cai IV-B, S4.SS2.p1, (46)–(48), PDF p.8; Vincent §4.2', 'DSM 目标；协方差权重为本稿适配，固定协方差条件保留。'),
        ('IV-07 + IV-08', 'Cai IV-A/B, (44), (48), PDF p.8; Dytso (3); 本文代入推导', '去噪器参数化、损失、期望对象及条件均值最优性同段。'),
        ('IV-09', 'Cai IV-B, S4.SS2.p2, (49), PDF pp.8–9; Shastri III-B, PDF pp.8–9', '多个噪声水平接有色训练；Kronecker 分布及网络条件输入为本文设置。'),
        ('IV-10', 'Cai Fig.3, PDF p.10; 本文网络输出与输入定义', '保留训练输出接回接收机的操作说明；不把完整句子归为 Cai 原句。'),
        ('IV-11 + IV-12', 'Dytso III, Proposition 1, (17), PDF p.3; Cai IV-C, (53), PDF p.9', 'Jacobian、条件协方差及白噪声迹公式同段；注意 Jacobian 转置约定。'),
        ('IV-13 + IV-14', 'Metzler 作者稿 V-B, PDF p.15', '有限差分、Monte Carlo 平均及参数指引同段；中心差分/随机符号/权重为本文设置。'),
        ('IV-15', 'Menon §2.1–2.2, PDF p.2; §4.2, (16)–(17), PDF p.3', 'Bayes log odds 接密度比估计任务。'),
        ('IV-16 + IV-17', 'Menon §2.1–2.2, PDF p.2; Shen IV-A2, (60)–(61), PDF p.11', '两类样本、交叉熵及理想函数最优解同段；不移植 Shen 的符号检测标签。'),
        ('IV-18', 'Menon §4.2, (16)–(17), PDF p.3; 本文 Bayes 公式', '减训练先验 log odds，再代入实际活动先验；删除式后重复强调。'),
    ],
    'V': [
        ('V-01', 'Cai V-A, S5.SS1.p2, PDF p.9', '保留算法总览先行的写法。'),
        ('V-02', 'Cai V-A, S5.SS1.p1, (55)–(56), PDF p.9; 本文估计器', '网络输出及共用方差；下限和分类器为本稿设置。'),
        ('V-03 + V-04', 'Cai III-B1/III-B3, (24)–(27)/(33)–(34), PDF p.7; Vehtari §2.1, pp.5–6', '合并 site 相除和条件统计量恢复；保留第五章实现位置，不称与 Cai 同章逐段一致。'),
        ('V-05 + V-11设置指引', 'Cai V-A/V-B2, S5.SS1.p2/S5.SS2.SSS2.p2, PDF pp.9–10; 本文初始化', '算法调用、初始化及设置指引集中。'),
        ('V-06', 'Wax–Kailath; Nadakuditi–Edelman II-A, (5)–(7), pp.2626–2627; 本文附录 A', '未知参数估计是新增任务；必要低秩/白噪声条件保留。'),
        ('V-07 + V-08', 'Vila–Schniter III-A, (24)–(27); Cai V-B1 阻尼名称', '固定后验的方差目标与实际缩放更新同段；更新对象为本稿输入方差。'),
        ('V-09归一化句', 'Cai V-B2, PDF p.10; 本文训练全局 RMS 设置', '归一化独立成段；不用 Cai 每样本归一化替换本文全局尺度。'),
        ('V-09阻尼 + V-10 + V-11首句', 'Cai V-B1, S5.SS2.SSS1.p1, (57)–(58), PDF pp.9–10; 本文截断设置', '双向阻尼及首次迭代集中，截断紧邻反馈公式。'),
        ('V-12', 'Bemani II-B, (16); Zou 作者稿 II-A/B, (1)/(4)/(5)', '波形调制复杂度独立；删除笼统成本说明。'),
        ('V-13 + V-14首句', '本文线性矩阵公式的 SVD 计算形式；Rangan VAMP III, (11), Algorithm 2, 作者稿 pp.3–4', '独立说明 SVD 复用，外信息表达式接回本段；不是 Cai 的正交导频设计。'),
        ('V-14余文 + V-15 + V-16', 'Cai V-C, S5.SS3.p2, PDF p.11; 本文算法运算次数', '单次/全部迭代成本、相位条件与存储连续说明；复杂度公式来自本文实现。'),
    ],
}

if __name__ == '__main__':
    checks = {}
    after_rows = []
    diff = []
    cites = [[], []]
    for chapter, name in zip(MAP, FILES):
        old = (RUN / 'before' / name).read_text(encoding='utf-8')
        new = (PAPER / name).read_text(encoding='utf-8')
        op, np = paragraphs(old), paragraphs(new)
        assert len(np) == len(MAP[chapter]), (chapter, len(np), len(MAP[chapter]))
        checks[name] = {
            'paragraphs_before': len(op), 'paragraphs_after': len(np),
            'numbered_math_count': len(list(MATH.finditer(new))),
            'numbered_math_identical': [m.group() for m in MATH.finditer(old)] == [m.group() for m in MATH.finditer(new)],
            'figures_and_algorithm_identical_except_svd_qualifier': [m.group().replace('Compute the thin SVD', 'Compute the SVD') for m in FIGURE.finditer(old)] == [m.group() for m in FIGURE.finditer(new)],
            'headings_identical': re.findall(r'\\(?:section|subsection|subsubsection)\{[^}]+\}', old) == re.findall(r'\\(?:section|subsection|subsubsection)\{[^}]+\}', new),
        }
        for i, text in enumerate([old, new]):
            cites[i].extend(re.findall(r'\\cite(?:\[[^\]]*\])*\{[^}]*\}', text))
        for i, (p, mapping) in enumerate(zip(np, MAP[chapter]), 1):
            after_rows.append(dict(id=f'{chapter}-{i:02}', file=name, **p,
                                   before=mapping[0], sources=mapping[1], note=mapping[2]))
    for name in BEFORE['files']:
        old = (RUN / 'before' / name).read_text(encoding='utf-8')
        new = (PAPER / name).read_text(encoding='utf-8')
        diff.extend(difflib.unified_diff(old.splitlines(True), new.splitlines(True), fromfile='before/' + name, tofile='after/' + name))
    active = re.findall(r'\\input\{([^}]+)\}', (PAPER / 'main.tex').read_text(encoding='utf-8'))
    active = [p + '.tex' for p in active]
    alltext = '\n'.join((PAPER / p).read_text(encoding='utf-8') for p in ['main.tex'] + active)
    labels = re.findall(r'\\label\{([^}]+)\}', alltext)
    refs = re.findall(r'\\(?:eqref|ref)\{([^}]+)\}', alltext)
    bib = set(re.findall(r'@\w+\{([^,]+)', (PAPER / 'references.bib').read_text(encoding='utf-8')))
    citelist = re.findall(r'\\cite(?:\[[^\]]*\])*\{([^}]+)\}', alltext)
    unresolved_cites = sorted({k.strip() for item in citelist for k in item.split(',')} - bib)
    env_errors = []
    for name in FILES:
        stack = []
        text = (PAPER / name).read_text(encoding='utf-8')
        for m in re.finditer(r'\\(begin|end)\{([^}]+)\}', text):
            if m[1] == 'begin':
                stack.append(m[2])
            elif not stack or stack.pop() != m[2]:
                env_errors.append([name, m.group()])
        if stack:
            env_errors.append([name, stack])
    suspicious = []
    patterns = [r'posterior moments?', r'activity evidence', r'new-message weight',
                r'mean function', r'complex mean map', r'it is worth noting',
                r'it should be noted', r'for the avoidance of doubt', r'not a claim']
    for name in FILES:
        text = (PAPER / name).read_text(encoding='utf-8')
        for pattern in patterns:
            if re.search(pattern, text, re.I):
                suspicious.append([name, pattern])
    result = {
        'compile_performed': False, 'pdfs_updated': False,
        'abstract_regenerated': False, 'scope': checks,
        'total_paragraphs_before': sum(v['paragraphs_before'] for v in checks.values()),
        'total_paragraphs_after': sum(v['paragraphs_after'] for v in checks.values()),
        'all_active_numbered_math_count': len(list(MATH.finditer(alltext))),
        'citation_instances_unchanged': sorted(cites[0]) == sorted(cites[1]),
        'protected_files_unchanged': all(sha(PAPER / p) == digest for p, digest in BEFORE['protected'].items()),
        'changed_protected_files': [p for p, digest in BEFORE['protected'].items() if sha(PAPER / p) != digest],
        'undefined_source_references': sorted(set(refs) - set(labels)),
        'duplicate_labels': [label for label, count in Counter(labels).items() if count > 1],
        'undefined_citations': unresolved_cites, 'environment_errors': env_errors,
        'flagged_phrases': suspicious,
        'source_hashes': {p: sha(PAPER / p) for p in FILES},
        'manual_review': 'Full prose read; source terminology/context checked; mathematical conditions retained. No typeset/layout check in this run.',
    }
    (RUN / 'AFTER_PARAGRAPHS.json').write_text(json.dumps(after_rows, ensure_ascii=False, indent=2), encoding='utf-8')
    (RUN / 'VALIDATION.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    (RUN / 'CHANGES.diff').write_text(''.join(diff), encoding='utf-8')
    lines = ['# 第3–5章修订后的段落与来源', '',
             '按作者确认的分段判断实施。新编号以修订后的段落为准；旧编号指上一轮47段核查。表格区分来源原段、本文推导与实现设置，不把多个来源的适配称为原句照搬或严格一一对应。', '',
             '| 当前段 | 原段处理 | 文献位置 | 处理与含义 |', '|---|---|---|---|']
    for p in after_rows:
        lines.append(f"| [{p['id']}](../../{p['file']}#L{p['line']}) | {p['before']} | {p['sources']} | {p['note']} |")
    (RUN / 'PARAGRAPH_MAP.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    assert all(v['numbered_math_identical'] and v['figures_and_algorithm_identical_except_svd_qualifier'] and v['headings_identical'] for v in checks.values())
    assert result['citation_instances_unchanged'] and result['protected_files_unchanged']
    assert not any(result[k] for k in ['undefined_source_references', 'duplicate_labels', 'undefined_citations', 'environment_errors', 'flagged_phrases'])
    print(json.dumps(result, ensure_ascii=False, indent=2))
