"""Check a prose-only revision and reuse the preceding 54 data checks."""
from pathlib import Path
import difflib
import hashlib
import json
import re
import sys

run=Path(__file__).resolve().parent
paper=run.parents[1]
prior=run.parent/'ch6_revision_20261103/validate_revision.py'
# This prefix contains all data assertions but no file-writing statements.
numeric_source=prior.read_text(encoding='utf-8').split('before=json.loads',1)[0]
scope={'__file__':str(prior)}
exec(compile(numeric_source,str(prior),'exec'),scope)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
hashes=json.loads((run/'BEFORE_HASHES.json').read_text())
changed={'sections/06_simulation_results.tex','sections/appendix_evaluation_protocol.tex',
         'docs/TERMINOLOGY.md','README.md','main.pdf'}
protected=[];diff=[];preserved=[]
for relative,h in hashes.items():
    name=relative.replace('\\','/')
    if name not in changed:
        assert sha(paper/relative)==h,relative
        protected.append(name)
for relative in sorted(changed-{'main.pdf'}):
    old=(run/'before'/relative).read_text(encoding='utf-8')
    new=(paper/relative).read_text(encoding='utf-8')
    diff.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='before/'+relative,tofile=relative))
    if relative.endswith('.tex'):
        for pattern in [r'(?<!\\)\$[^$]*\$',
                        r'\\begin\{(equation\*?|table|figure\*?)\}[\s\S]*?\\end\{\1\}']:
            assert [m.group() for m in re.finditer(pattern,old)]==[m.group() for m in re.finditer(pattern,new)],relative
        preserved.append(relative)
log=(paper/'main.log').read_text(encoding='utf-8')
assert not re.search(r'undefined references|Citation .+ undefined|Reference .+ undefined|multiply defined|Overfull',log,re.I)
sys.path.append(str(Path.home()/'.cache/codex-pymupdf'))
import pymupdf as fitz
doc=fitz.open(paper/'main.pdf')
aux=(paper/'main.aux').read_text()
labels={}
for label in ['sec:simulations','tab:activity-evidence','fig:cstmp-snr','fig:cstmp-cross']:
    m=re.search(r'\\newlabel\{'+re.escape(label)+r'\}\{\{([^}]+)\}\{([^}]+)\}',aux)
    assert m,label
    labels[label]={'number':m[1],'page':int(m[2])}
out={'status':'PASS','numeric_checks':scope['checks'],'source_hashes':scope['sources'],
     'protected_files_unchanged':protected,'math_figures_tables_unchanged':preserved,
     'pages':len(doc),'labels':labels,'undefined_references':False,'overfull_boxes':False,
     'pdf_sha256':sha(paper/'main.pdf'),'new_inferences':0,'training_runs':0}
(run/'VALIDATION.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
(run/'CHANGES.diff').write_text(''.join(diff),encoding='utf-8')
print(json.dumps({k:out[k] for k in ('status','pages','labels')},indent=2))
print('Data assertions passed:',len(scope['checks']))
