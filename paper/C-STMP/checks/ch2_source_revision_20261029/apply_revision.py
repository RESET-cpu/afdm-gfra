from pathlib import Path
import hashlib, json, re, difflib

root=Path(r'D:\afdm-gfra\paper\C-STMP')
run=root/'checks/ch2_source_revision_20261029'
target=root/'sections/02_system_model.tex'
oldbytes=target.read_bytes()
old=oldbytes.decode('utf-8-sig')
expected='bb94e3a63b6a85779285b7ffffe7bae89bcba05d919df132983b1ae0ee0a24a7'
assert hashlib.sha256(oldbytes).hexdigest()==expected, 'Source changed since audit'
manifest=json.loads((root/'checks/strict_sentence_audit_20261029/manifest.json').read_text(encoding='utf-8'))
paragraph={p['id']:p['text'] for p in manifest['paragraphs']}
read=lambda name:(run/name).read_text(encoding='utf-8-sig').strip()
bayes=read('bayes.tex')
posterior_start=bayes.index('Alternatively, message-passing algorithms')
posterior_end=bayes.index('\n\nThe main difficulty',posterior_start)
posterior=bayes[posterior_start:posterior_end]
# Keep the two whole closing sentences, without importing Cai's unrelated
# channel-model examples or adding a defensive sentence about the training prior.
closing=bayes[bayes.index('To summarize, the message-passing framework'):]
task=paragraph['P09'].replace('\nWe consider $Q<KN$ in \\eqref{eq:mmv}.','')
known=paragraph['P10']
exact=r'''Exact Bayesian estimators, e.g., the MMSE estimator, are generally
intractable due to the high-dimensional integrals in the
marginalization of the joint posterior distribution
$q(\mathbf X,\{H_k\}_{k=1}^{K},\{\alpha_k\}_{k=1}^{K}\mid\mathbf Y)$.'''
parts=[
    '\\section{System Model}\n\\label{sec:system}',
    read('opening.tex'),
    '\\subsection{Terrestrial-Satellite Link Model}',
    read('physical.tex'),
    '\\subsection{Multi-Frame AFDM Transmission}',
    read('transmission.tex'),
    read('channel.tex'),
    read('observation.tex'),
    '\\subsection{Problem Formulation}',
    task+'\nWe consider $Q<KN$ in \\eqref{eq:mmv}.',
    known,
    exact,
    posterior,
    closing,
]
new='\n\n'.join(parts)+'\n'
# Author-supplied scope: revise Chapter II against the strict sentence audit.
# Source snapshots and a scoped diff are evidence; other manuscript files stay intact.
other={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
       for p in list(root.rglob('*.tex'))+[root/'references.bib']
       if 'checks' not in p.parts and p!=target}
source_record={
    'authorization':'用户：不行，请你必须对照修改。范围为上一轮已审查的第二章。',
    'target':str(target), 'source_sha256':expected,
    'source_before':old, 'other_manuscript_sha256':other,
    'revision_basis':str(root/'checks/strict_sentence_audit_20261029/FULL_AUDIT.md'),
    'change_boundary':'第二章句式/术语与解释结构；不修改实验、算法实现、摘要、引言或其他章节。',
}
(run/'source_and_authority.json').write_text(json.dumps(source_record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(run/'chapter2.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='sections/02_system_model.tex.before',tofile='sections/02_system_model.tex')),encoding='utf-8')
assert set(re.findall(r'\\label\{([^}]+)\}',old))<=set(re.findall(r'\\label\{([^}]+)\}',new))
assert not re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f]',new), 'Unexpected control character'
target.write_text(new,encoding='utf-8',newline='\n')
for name,digest in other.items():
    assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest, name
print(json.dumps({'written':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'other_manuscript_files_unchanged':len(other),'old_lines':len(old.splitlines()),'new_lines':len(new.splitlines())},ensure_ascii=False))
