from pathlib import Path
import hashlib
import json
import re
import difflib

out = Path(__file__).resolve().parent
repo = out.parents[3]
paper = repo / 'paper/C-STMP'
source = paper / 'sections/02_system_model.tex'
sha = lambda data: hashlib.sha256(data).hexdigest()
manifest = json.loads((out / 'REVISION_MANIFEST.json').read_text(encoding='utf-8'))
assert sha(source.read_bytes()) == manifest['source_sha256'], 'Source changed since baseline; inspect before applying.'
before = (out / 'before.tex').read_text(encoding='utf-8')
after = before
applied = []
for part in ['a', 'b', 'c', 'lead']:
    patch = json.loads((out / f'{part}_patch.json').read_text(encoding='utf-8-sig'))
    for i, op in enumerate(patch['operations']):
        old, new = op['old'], op['new']
        assert after.count(old) == 1, (part, i, after.count(old), old[:100])
        after = after.replace(old, new, 1)
        applied.append({'part': part, 'operation': i, **op})

def equations(text):
    found = re.findall(r'\\begin\{equation\}(.*?)\\end\{equation\}', text, re.S)
    return [re.sub(r'\s+', '', body) for body in found]
assert len(equations(before)) == 14
assert equations(before) == equations(after), 'Numbered equations changed.'
assert re.findall(r'\\label\{([^}]+)\}', before) == re.findall(r'\\label\{([^}]+)\}', after)
assert re.findall(r'\\(?:sub)?section\{[^}]+\}', before) == re.findall(r'\\(?:sub)?section\{[^}]+\}', after)
assert 'working posterior' not in after.lower()
assert 'app:evaluation-protocol' not in after
for name, digest in manifest['protected_files'].items():
    assert sha((repo / name).read_bytes()) == digest, 'Protected file changed: ' + name
all_sources = [p.read_text(encoding='utf-8') for p in (paper / 'sections').glob('*.tex') if p != source]
all_sources += [after, (paper / 'main.tex').read_text(encoding='utf-8')]
all_labels = re.findall(r'\\label\{([^}]+)\}', '\n'.join(all_sources))
assert len(all_labels) == len(set(all_labels)), 'Duplicate labels.'
assert set(re.findall(r'\\(?:eqref|ref)\{([^}]+)\}', after)) <= set(all_labels)
bibkeys = set(re.findall(r'@\w+\{([^,]+),', (paper / 'references.bib').read_text(encoding='utf-8')))
newkeys = {k for group in re.findall(r'\\cite\{([^}]+)\}', after) for k in group.split(',')}
assert newkeys <= bibkeys, newkeys - bibkeys
stack = []
for command, env in re.findall(r'\\(begin|end)\{([^}]+)\}', after):
    if command == 'begin': stack.append(env)
    else: assert stack and stack.pop() == env, (command, env)
assert not stack

source.write_bytes(after.encode('utf-8'))
(out / 'after.tex').write_bytes(after.encode('utf-8'))
(out / 'changes.diff').write_text(''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile='before.tex', tofile='02_system_model.tex')), encoding='utf-8')
report = {'operation_count': len(applied), 'source_before_sha256': manifest['source_sha256'],
          'source_after_sha256': sha(source.read_bytes()), 'numbered_equations_identical': 14,
          'labels_unchanged': True, 'headings_unchanged': True,
          'all_citation_keys_resolve': True, 'all_cross_reference_labels_resolve': True,
          'protected_files_unchanged': list(manifest['protected_files']),
          'working_posterior_removed': True, 'operations': applied}
(out / 'APPLY_REPORT.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: v for k, v in report.items() if k not in ('operations', 'protected_files_unchanged')}, ensure_ascii=False))
