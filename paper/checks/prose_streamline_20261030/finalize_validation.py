"""Bind the completed source, numerical, compilation and visual checks."""
from pathlib import Path
import hashlib
import json
import re
from datetime import datetime, timezone
from pypdf import PdfReader

RUN = Path(__file__).resolve().parent
PAPER = RUN.parents[1]
ROOT = PAPER.parents[1]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

static = json.loads((RUN / 'STATIC_VALIDATION.json').read_text(encoding='utf-8'))
numerical = json.loads((RUN / 'NUMERICAL_VERIFICATION.json').read_text(encoding='utf-8'))
assert static['status'] == numerical['status'] == 'PASS'
for item in static['source_bindings']:
    assert digest(PAPER / item['path']) == item['sha256'], item['path']
for path, expected in numerical['inspected_prose_sha256'].items():
    assert digest(ROOT / path) == expected, path

log = (PAPER / 'main.log').read_text(encoding='utf-8', errors='replace')
bad_patterns = [r'Overfull', r'undefined', r'multiply defined', r'Missing character', r'^! ']
problems = [pattern for pattern in bad_patterns if re.search(pattern, log, re.I | re.M)]
assert not problems, problems
pdf = PAPER / 'main.pdf'
page_count = len(PdfReader(pdf).pages)
assert page_count == 15
previews = {str(page): digest(RUN / f'previews/final-{page:02d}.png')
            for page in range(2, 16)}
reports = ['CH23_REVIEW.md', 'IMPLEMENTATION_REVIEW.md', 'VI_PROSE_REVIEW.md',
           'STATIC_VALIDATION.json', 'NUMERICAL_VERIFICATION.json', 'acronym_report.md',
           'REVISION_NOTES.md']
report = {
    'status': 'PASS',
    'generated_utc': datetime.now(timezone.utc).isoformat(),
    'pdf': {'path': str(pdf), 'sha256': digest(pdf), 'pages': page_count},
    'source_bindings': static['source_bindings'],
    'checks': {
        'static': static['check_count'],
        'numerical': numerical['checks_count'],
        'display_math_environments_preserved': len(static['equation_preservation']),
        'source_hashes_still_match_reviews': True,
        'compile': 'Tectonic 0.17.0 exit code 0',
        'unresolved_references_duplicate_labels_missing_glyphs_overfull': [],
        'underfull_warnings': 'Retained; affected pages visually checked.',
        'visual_review': {
            '2-5': 'trim_review_ch23', '6-8': 'trim_review_ch45',
            '9-11': 'trim_review_ch6', '12-15': 'root',
            'result': 'Actual rendered images inspected; no clipping or overlap found.',
            'page_1': 'Unchanged opening material; not rerendered in this operation.',
        },
        'acronyms': 'Advisory partial prose check; existing findings retained.',
    },
    'preview_sha256': previews,
    'report_sha256': {name: digest(RUN / name) for name in reports},
    'training_or_inference_run': False,
}
(RUN / 'FINAL_VALIDATION.json').write_text(
    json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(json.dumps({'status': report['status'], 'pages': page_count,
                  'static_checks': static['check_count'],
                  'numerical_checks': numerical['checks_count'],
                  'math_environments': len(static['equation_preservation'])}))
