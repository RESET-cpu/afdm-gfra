from pathlib import Path
import hashlib
import json
import shutil

RUN = Path(__file__).resolve().parent
PAPER = RUN.parents[1]
PROJECT = PAPER.parents[1]
FILES = [
    'sections/03_bayesian_receiver_design.tex',
    'sections/04_generative_priors.tex',
    'sections/05_overall_algorithm.tex',
    'docs/TERMINOLOGY.md', 'docs/WRITING_GUIDE.md', 'README.md',
]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

if __name__ == '__main__':
    assert not (RUN / 'BEFORE.json').exists(), 'Snapshot already exists'
    for name in FILES:
        dest = RUN / 'before' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(PAPER / name, dest)
    protected = [p for p in PAPER.glob('sections/*.tex') if p.relative_to(PAPER).as_posix() not in FILES]
    protected += [PAPER / name for name in ['main.tex', 'main_full.tex', 'main.pdf', 'main_full.pdf', 'references.bib']]
    protected += list((PAPER / 'figures').glob('*'))
    payload = {
        'scope': 'Approved paragraph regrouping and source-grounded prose revision in Chapters III–V',
        'compile_requested': False,
        'files': {name: digest(PAPER / name) for name in FILES},
        'protected': {p.relative_to(PAPER).as_posix(): digest(p) for p in protected if p.is_file()},
    }
    (RUN / 'BEFORE.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    corpus = json.loads((PAPER / 'checks/prose_terminology_20261103/CORPUS.json').read_text(encoding='utf-8'))
    selected = {'cai2026.pdf': [5, 6, 7, 8, 9, 10, 11],
                'shen2025.pdf': [9, 11],
                'dytso2023_conditional_mean_published.pdf': [1, 3],
                'shastri2022_dgec_published.pdf': [8],
                'vila_schniter_2013.pdf': [4, 5]}
    evidence = {}
    for name, pages in selected.items():
        item = corpus[name]
        evidence[name] = {'sha256': item['sha256'], 'pages': {str(n): item['pages'][n-1] for n in pages}}
    (RUN / 'LOCAL_SOURCE_PAGES.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'snapshot_files': len(FILES), 'protected_files': len(payload['protected']), 'source_pages': sum(map(len, [v['pages'] for v in evidence.values()]))}))
