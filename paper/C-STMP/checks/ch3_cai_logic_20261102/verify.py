from pathlib import Path
import difflib
import hashlib
import json
import re

RUN = Path(__file__).resolve().parent
ROOT = RUN.parent.parent
REL = Path('sections/03_bayesian_receiver_design.tex')
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


old, new = equations(before), equations(after)
assert old.keys() == new.keys()
changed = [key for key in old if old[key] != new[key]]
assert changed == ['eq:active-channel-posterior'], changed
fig = r'\\begin\{figure\}.*?\\end\{figure\}'
assert re.findall(fig, before, re.S) == re.findall(fig, after, re.S)
manifest = json.loads((RUN / 'BASELINE.json').read_text())
allowed = {
    str(REL), 'README.md', str(Path('docs/TERMINOLOGY.md')), 'main.pdf'
}
protected = [path for path in manifest if path not in allowed]
assert all(
    hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == manifest[path]
    for path in protected
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
missing = sorted(set(refs) - set(labels))
duplicates = sorted(key for key in set(labels) if labels.count(key) > 1)
assert not missing, missing
assert not duplicates, duplicates
assert not re.search(r'density.?ratio|classifi|training loss', after, re.I)

report = {
    'numbered_equation_labels': len(old),
    'preserved_equation_labels': sorted(old),
    'only_equivalent_formula_rewrite': changed,
    'figure_unchanged': True,
    'protected_files_unchanged': len(protected),
    'missing_refs_in_compiled_source': missing,
    'duplicate_labels_in_compiled_source': duplicates,
    'density_ratio_estimator_absent_from_chapter_III': True,
    'abstract_regenerated': False,
}
(RUN / 'VALIDATION.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
diffs = []
for file in [REL, Path('README.md'), Path('docs/TERMINOLOGY.md')]:
    a = (RUN / 'before' / file).read_text(encoding='utf-8')
    b = (ROOT / file).read_text(encoding='utf-8')
    diffs.extend(difflib.unified_diff(
        a.splitlines(True), b.splitlines(True),
        fromfile='before/' + file.as_posix(), tofile='after/' + file.as_posix()
    ))
(RUN / 'CHANGES.diff').write_text(''.join(diffs), encoding='utf-8')
(RUN / 'build').mkdir(exist_ok=True)

# Excerpt check: these abbreviations are defined earlier in the unchanged body.
prose = re.sub(r'\\begin\{figure\}.*?\\end\{figure\}', '', after, flags=re.S)
prose = re.sub(r'\\begin\{(equation|align)\}.*?\\end\{\1\}', '', prose, flags=re.S)
prose = re.sub(r'\$[^$]*\$', '', prose)
prose = re.sub(r'\\(?:label|ref|eqref|cite)(?:\[[^]]*\])?\{[^}]*\}', '', prose)
prose = re.sub(r'\\(?:section|subsection|subsubsection)\{([^}]*)\}', r'\1', prose)
(RUN / 'chapter3_prose.txt').write_text(prose, encoding='utf-8')
print(json.dumps(report, indent=2))
