from pathlib import Path
import hashlib
import json
import re
from datetime import datetime, timezone
from pypdf import PdfReader

audit = Path(__file__).resolve().parent
paper = audit.parent.parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
baseline = json.loads((audit / 'baseline.json').read_text(encoding='utf-8-sig'))
allowed = {'sections/06_simulation_results.tex', 'sections/appendix_evaluation_protocol.tex', 'main.pdf'}
protected = [row['path'] for row in baseline if row['path'] not in allowed]
assert all(sha(paper / row['path']) == row['sha256'] for row in baseline if row['path'] in protected)
migration = json.loads((audit / 'MIGRATION_VERIFICATION.json').read_text(encoding='utf-8-sig'))
assert migration['status'] == 'PASS' and migration['checks_count'] == 67
assert all(row['passed'] for row in migration['checks'])
log = (paper / 'main.log').read_text(encoding='utf-8', errors='replace')
issues = re.findall(r'^.*(?:undefined references|Reference .* undefined|Citation .* undefined|multiply[- ]defined|Overfull \\[hv]box|Missing character|^! ).*$', log, re.M | re.I)
assert not issues, issues
reader = PdfReader(paper / 'main.pdf')
assert len(reader.pages) == 15
body = '\n'.join(p.read_text(encoding='utf-8') for p in sorted((paper / 'sections').glob('0[1-6]*.tex')))
assert not re.search(r'app:evaluation-protocol|Appendix\s*(?:~|\\[a-z]+\s*)*C\b', body, re.I)
paths = [paper / row['path'] for row in baseline]
paths += [audit / name for name in ['REVIEW.md', 'MIGRATION_VERIFICATION.json', 'REVISION_NOTES.md', 'acronym_report.md', 'verify_protocol_migration.py']]
paths += sorted((audit / 'previews').glob('final-*.png'))
record = {
    'status': 'PASS',
    'generated_utc': datetime.now(timezone.utc).isoformat(),
    'scope': 'Placement-only edit; no new numerical experiment or claim of independent validation.',
    'migration_checks_passed': 67,
    'protected_files_unchanged': protected,
    'main_body_and_captions_have_no_appendix_c_pointer': True,
    'compiled_pdf_pages': len(reader.pages),
    'blocking_latex_diagnostics': issues,
    'visual_review': {'root': [8, 12, 13, 14, 15], 'chapter_reviewer': [9, 10, 11], 'result': 'No clipping, overlap, or visibly unresolved references observed.'},
    'acronym_review': 'Advisory partial-body report retained; existing findings remain, not a full-manuscript pass.',
    'sha256': {p.relative_to(paper).as_posix(): sha(p) for p in paths},
}
(audit / 'FINAL_VALIDATION.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'status': record['status'], 'migration_checks': 67, 'pdf_pages': len(reader.pages), 'protected_files': len(protected)}, ensure_ascii=False))
