from pathlib import Path
import collections
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent
def read_json(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8-sig'))

def compact(text):
    return re.sub(r'\s+', '', text)

def fmt(value):
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return '；'.join(fmt(x) for x in value)
    return json.dumps(value, ensure_ascii=False)

manifest = read_json('manifest.json')
sources = read_json('SOURCES.json')
reviews = [read_json(f'{part}_audit.json') for part in 'abc']
paragraphs = [p for review in reviews for p in review['paragraphs']]
paragraphs.sort(key=lambda p: p['id'])
adjudication = read_json('ADJUDICATION.json')
for override in adjudication['overrides']:
    row = next(s for p in paragraphs for s in p['sentences'] if s['id'] == override['id'])
    assert row['category'] == override['from']
    row['initial_category'] = row['category']
    row['initial_reason'] = row['reason']
    row['category'] = override['to']
    row['reason'] = override['reason']
    row['lead_adjudication'] = override
    row['action'] = '可按有定位的合理组合保留；技术范围仍限于本稿明确的帧结构。'
    parent = next(p for p in paragraphs if row in p['sentences'])
    parent['paragraph_structure']['verdict'] = '主审统一后：1句合理原句组合、1句支持性改写、4句本稿定义或内部指引。'
assert [p['id'] for p in paragraphs] == [p['id'] for p in manifest['paragraphs']]
source_keys = {s['key'] for s in sources}
required = {'id', 'draft_tex', 'source_refs', 'category', 'changes', 'reason',
            'technical_status', 'formula_adaptation', 'action'}
categories = ['EXACT', 'TERM_ONLY', 'REASONABLE_COMBINATION', 'SUPPORTED_PARAPHRASE',
              'AUTHOR_DEFINED_OR_DERIVED', 'SOURCE_GAP', 'UNVERIFIED']
labels = dict(zip(categories, ['原句一致', '仅术语/符号替换', '有定位的合理原句组合',
                              '有依据但经过自主改写', '本稿定义、假设或推导', '来源缺口', '未核实']))
checks = []
ids = []
for p, src in zip(paragraphs, manifest['paragraphs']):
    assert compact(''.join(s['draft_tex'] for s in p['sentences'])) == compact(src['text']), p['id']
    for s in p['sentences']:
        assert required <= s.keys(), (s.get('id'), required - s.keys())
        assert s['category'] in categories, s['id']
        ids.append(s['id'])
        for ref in s['source_refs']:
            assert ref['key'] in source_keys, (s['id'], ref)
            assert ref.get('quote') or ref.get('locator'), (s['id'], ref)
    checks.append({'paragraph': p['id'], 'sentence_count': len(p['sentences']),
                   'complete_sequential_coverage': True})
assert len(ids) == len(set(ids))
current_hash = hashlib.sha256(Path(manifest['source_file']).read_bytes()).hexdigest()
assert current_hash == manifest['source_sha256']
for s in sources:
    assert hashlib.sha256(Path(s['pdf']).read_bytes()).hexdigest() == s['sha256'], s['key']

sentences = [s for p in paragraphs for s in p['sentences']]
counts = {c: sum(s['category'] == c for s in sentences) for c in categories}
result = {'source_file': manifest['source_file'], 'source_sha256': current_hash,
          'paragraph_count': len(paragraphs), 'sentence_count': len(sentences),
          'counts': counts, 'coverage_checks': checks, 'all_source_hashes_match': True,
          'all_sentences_meet_original_adaptation_standard': all(s['category'] in categories[:3] for s in sentences),
          'lead_adjudication': adjudication,
          'paragraphs': paragraphs}
(ROOT / 'FINAL_AUDIT.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

out = ['# 第二章逐句来源核查：完整对照', '',
       '核查日期：2026-10-30。对象是当前英文第二章，非旧版本，也不是中文译文。', '',
       f"- 正文：[02_system_model.tex]({Path(manifest['source_file']).as_posix()})",
       f"- SHA-256：`{current_hash}`",
       f"- 覆盖：{len(paragraphs)} 个段落、{len(sentences)} 个完整句子，含所有显示公式及其从句。",
       '- 分组审查后由主审汇总复核；本次未修改正文、PDF或实验。', '',
       '分类反映措辞来源，不等同于技术正确性。未找到同一句话不自动构成模型错误；数学成立也不自动说明措辞属于原句替换。', '',
       '| 类别 | 句数 |', '|---|---:|']
out += [f'| {labels[c]} | {counts[c]} |' for c in categories]
out += ['', '## 段落索引', '', '| 段落 | 原文行号 | 句数 |', '|---|---|---:|']
for p, src in zip(paragraphs, manifest['paragraphs']):
    out.append(f"| [{p['id']}](#{p['id'].lower()}) | {src['start_line']}–{src['end_line']} | {len(p['sentences'])} |")
out += ['', '## 判读边界', '',
        '本次按完整语法句核查。原句支持已拆到具体页码/小节/公式；引语中的数学符号可能以可检索的线性写法转写，具体公式以原 PDF 为准。', '',
        '“有依据但经过自主改写”包括同义词替换、删减和语序重组，不能据此称原文凭空编造，也不能称只换了术语。“本稿定义、假设或推导”应由数学及显式条件支撑；无需为了满足逐字要求而伪造文献原句。', '',
        '逐句处理建议是来源整改选项，不表示必须向正文增加解释。作者自定义的符号、索引、公式推导和章节指引可保留为作者内容。', '']
out += ['主审对P04.S01统一了组合口径，最终分类以本表为准；其余53句保留分组判断。局部术语“working posterior”仍未闭合来源，详见P12.S02及[主审复核记录](ADJUDICATION.json)。', '']
out += ['## 标题核对', '', '| 标题 | 来源判断 |', '|---|---|',
        '| System Model | Shen §II及Huang §II等有相同标题，仅大小写排版差异。 |',
        '| Terrestrial-Satellite Link Model | Shen PDF p.3 §II-A同名标题，大小写差异。 |',
        '| Multi-Frame AFDM Transmission | 本稿按内容组合的标题；Shen §II-B为Transmission Scheme，不能称直接沿用其原题。标题不引入新算法术语。 |',
        '| Problem Formulation | Shen PDF p.5 §II-C同名标题。 |',
        '', '标题另列，不计入54个正文完整语法句。', '']
by_key = {s['key']: s for s in sources}
for p, src in zip(paragraphs, manifest['paragraphs']):
    out += [f"## {p['id']}", '', f"原文行号：{src['start_line']}–{src['end_line']}。", '']
    if p.get('paragraph_structure'):
        mapping = {'source_order': '来源顺序', 'cross_source': '跨来源组合',
                   'cross_source_combination': '跨来源组合', 'structure_effect': '结构变化',
                   'structure_changes_conditions': '条件变化', 'condition_change': '条件变化',
                   'verdict': '段落结论', 'assessment': '结构判断'}
        for key, value in p['paragraph_structure'].items():
            if isinstance(value, bool):
                value = '是' if value else '否'
            out += ['**' + mapping.get(key, key) + '：** ' + fmt(value), '']
    for s in p['sentences']:
        out += [f"### {s['id']} · {labels[s['category']]}", '', '**当前稿完整句（含公式）：**', '',
                '```tex', s['draft_tex'].strip(), '```', '', '**参考原文与定位：**', '']
        if not s['source_refs']:
            out += ['本句为本稿内部定义/指引，未认定为参考论文原句。', '']
        for ref in s['source_refs']:
            path = Path(by_key[ref['key']]['pdf']).as_posix()
            page = fmt(ref.get('page', '?'))
            place = f"[{ref['key']}]({path})，" + (page if 'PDF' in page else 'PDF 第 ' + page + ' 页')
            for key in ('section', 'eq'):
                if ref.get(key):
                    place += '，' + fmt(ref[key])
            out += [place + '。', '']
            if ref.get('quote') and ref['key'] not in ('li2023', 'bemani2022'):
                out += ['> ' + fmt(ref['quote']).replace('\n', '\n> '), '']
            if ref.get('locator'):
                out += ['定位/释义：' + fmt(ref['locator']), '']
            if ref.get('limitation'):
                out += ['来源限制：' + fmt(ref['limitation']), '']
        for field, heading in [('changes', '具体变化'), ('reason', '分类理由'),
                               ('technical_status', '技术判断'), ('formula_adaptation', '公式适配'),
                               ('action', '处理建议')]:
            out += [f'**{heading}：** ' + fmt(s[field]), '']
        for field in ('language_alignment', 'quote_note'):
            if s.get(field):
                out += ['补充：' + fmt(s[field]), '']
        if s.get('lead_adjudication'):
            out += ['主审调整：原分组类别为' + labels[s['initial_category']] + '；最终以本条分类及上述理由为准。', '']
out += ['## 完整性检查', '',
        '每段全部句子依序拼接并仅忽略空白，与原段落逐字一致；句号、公式和从句没有遗漏或重复。当前正文 SHA-256 与开始核查时一致，7 个原始 PDF 的 SHA-256 均与来源清单一致。覆盖通过不代表来源分类全部通过。', '',
        '分组原始报告：[P01–P03](a_audit.md)、[P04–P08](b_audit.md)、[P09–P13](c_audit.md)。', '']
(ROOT / 'FULL_AUDIT.md').write_text('\n'.join(out), encoding='utf-8')
print(json.dumps({'paragraphs': len(paragraphs), 'sentences': len(sentences), 'counts': counts,
                  'coverage': 'PASS', 'source_unchanged': True}, ensure_ascii=False))
