from pathlib import Path
import difflib
import hashlib
import json
import re

RUN = Path(__file__).resolve().parent
ROOT = RUN.parent.parent
REL = 'sections/03_bayesian_receiver_design.tex'
before = (RUN / 'before' / REL).read_text(encoding='utf-8')
after = (ROOT / REL).read_text(encoding='utf-8')


def equations(source):
    result = {}
    for match in re.finditer(
        r'\\begin\{(equation|align)\}(.*?)\\end\{\1\}', source, re.S
    ):
        body = match.group(2)
        for label in re.findall(r'\\label\{([^}]+)\}', body):
            result[label] = re.sub(r'\s+', '', body)
    return result


assert equations(before) == equations(after)
annotated = (RUN / '01_annotated_logic.tex').read_text(encoding='utf-8')
assert equations(annotated) == equations(after)
assert (RUN / '02_polished_chapter.tex').read_bytes() == (ROOT / REL).read_bytes()
fig = r'\\begin\{figure\}.*?\\end\{figure\}'
assert re.findall(fig, before, re.S) == re.findall(fig, after, re.S)
manifest = json.loads((RUN / 'BASELINE.json').read_text())
allowed = {REL, 'README.md', 'docs/TERMINOLOGY.md', 'main.pdf'}
protected = [p for p in manifest if p not in allowed]
assert all(
    hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == manifest[p]
    for p in protected
)


def active_source(path):
    source = re.sub(r'(?<!\\)%[^\n]*', '', path.read_text(encoding='utf-8'))
    return re.sub(
        r'\\input\{([^}]+)\}',
        lambda match: active_source(ROOT / (match.group(1) + '.tex')),
        source,
    )


source = active_source(ROOT / 'main.tex')
labels = re.findall(r'\\label\{([^}]+)\}', source)
refs = re.findall(r'\\(?:eqref|ref)\{([^}]+)\}', source)
assert not set(refs) - set(labels)
assert len(labels) == len(set(labels))
assert not re.search(r'density.?ratio|classifi|training loss', after, re.I)
report = {
    'equations_identical_in_both_drafts_and_baseline': len(equations(after)),
    'figure_unchanged': True,
    'polished_snapshot_matches_current_chapter': True,
    'protected_files_unchanged': len(protected),
    'missing_refs': [],
    'duplicate_labels': [],
    'density_ratio_learning_stays_outside_chapter_III': True,
    'abstract_regenerated': False,
    'plagiarism_detector_evasion_performed': False,
    'similarity_or_originality_score_claimed': False,
}
(RUN / 'VALIDATION.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
diffs = []
for path in [REL, 'README.md', 'docs/TERMINOLOGY.md']:
    a = (RUN / 'before' / path).read_text(encoding='utf-8')
    b = (ROOT / path).read_text(encoding='utf-8')
    diffs.extend(difflib.unified_diff(
        a.splitlines(True), b.splitlines(True),
        fromfile='before/' + path, tofile='after/' + path
    ))
(RUN / 'CHANGES.diff').write_text(''.join(diffs), encoding='utf-8')

prose = re.sub(r'\\begin\{figure\}.*?\\end\{figure\}', '', after, flags=re.S)
prose = re.sub(r'\\begin\{(equation|align)\}.*?\\end\{\1\}', '', prose, flags=re.S)
prose = re.sub(r'\$[^$]*\$', '', prose)
prose = re.sub(r'\\(?:label|ref|eqref|cite)(?:\[[^]]*\])?\{[^}]*\}', '', prose)
prose = re.sub(r'\\(?:section|subsection|subsubsection)\{([^}]*)\}', r'\1', prose)
(RUN / 'chapter3_prose.txt').write_text(prose, encoding='utf-8')
print(json.dumps(report, indent=2))
