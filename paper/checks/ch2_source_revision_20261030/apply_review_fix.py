from pathlib import Path
import hashlib
import json
import difflib

out = Path(__file__).resolve().parent
paper = out.parent.parent
source = paper / 'sections/02_system_model.tex'
report_path = out / 'APPLY_REPORT.json'
report = json.loads(report_path.read_text(encoding='utf-8'))
sha = lambda data: hashlib.sha256(data).hexdigest()
assert sha(source.read_bytes()) == report['source_after_sha256']
current = source.read_text(encoding='utf-8')
old = 'generative priors for efficient message calculation, eliminating\nthe need to compute high-dimensional integrals \\cite{cai2026}.\n'
new = 'generative priors for efficient message calculation \\cite{cai2026}.\n'
assert current.count(old) == 1
current = current.replace(old, new, 1)
(out / 'INITIAL_APPLY_REPORT.json').write_bytes(report_path.read_bytes())
source.write_bytes(current.encode('utf-8'))
(out / 'after.tex').write_bytes(current.encode('utf-8'))
report['post_review_base_sha256'] = report['source_after_sha256']
report['source_after_sha256'] = sha(source.read_bytes())
report['operations'].append({
    'part': 'review', 'operation': 0, 'old': old, 'new': new,
    'old_ids': ['P13.S01'],
    'source_refs': [{'key': 'cai2026', 'page': 5, 'section': 'II-B',
                    'locator': '末段中的生成先验用于message calculation；消除高维积分的后句另有score-based networks/MMSE关系作为前提。'}],
    'change_reason': '采纳交叉复核：删除脱离具体得分网络/MMSE关系的高维积分尾从句，保留近似求解与生成先验的源分句组合；不增加正文解释。'
})
report['operation_count'] = len(report['operations'])
report['review_fix'] = 'review_c_by_a.md P13.S01 recommendation adopted'
report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
before = (out / 'before.tex').read_text(encoding='utf-8')
(out / 'changes.diff').write_text(''.join(difflib.unified_diff(before.splitlines(True), current.splitlines(True), fromfile='before.tex', tofile='02_system_model.tex')), encoding='utf-8')
print(report['source_after_sha256'])
