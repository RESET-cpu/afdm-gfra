"""Validate the mathematical specialization and preserve existing evidence."""
from pathlib import Path
import datetime
import difflib
import hashlib
import json
import re
import numpy as np
from pypdf import PdfReader

OUT = Path(__file__).resolve().parent
PAPER = OUT.parents[1]
before = json.loads((OUT/'BEFORE_HASHES.json').read_text(encoding='utf-8'))
checks = {}

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

for rel, digest in before.items():
    assert sha(OUT/'before'/rel) == digest, ('backup', rel)
checks['backups_verified'] = len(before)
protected = [p for p in before if p.startswith('figures')]
protected += ['main_full.tex', 'sections/02_system_model.tex',
              'sections/03_bayesian_receiver_design.tex',
              'sections/appendix_parameter_estimation.tex',
              'sections/appendix_second_order_training.tex']
for rel in protected:
    key = rel.replace('/', '\\') if rel.replace('/', '\\') in before else rel
    assert sha(PAPER/rel) == before[key], ('preserve', rel)
checks['protected_files_unchanged'] = protected

def read(rel, old=False):
    return ((OUT/'before') if old else PAPER).joinpath(rel).read_text(encoding='utf-8')

def contributions(s):
    s = s.split('Our main contributions are summarized as follows:')[1]
    s = s.split('\\end{enumerate}')[0]
    return s.split('\\item ')[1:]

a,b = [contributions(read('sections/01_introduction.tex', old)) for old in (True,False)]
assert a[0] == b[0] and a[2] == b[2]
checks['contributions_1_and_3_unchanged'] = True
for rel, marker in [('sections/06_simulation_results.tex', '\\subsubsection{Evaluation Settings and Metrics}'),
                    ('sections/appendix_evaluation_protocol.tex', '\\subsection{Paired Scenes and Parameter Selection}')]:
    assert read(rel).split(marker)[1] == read(rel, True).split(marker)[1]
checks['evaluation_numbers_results_and_protocol_unchanged'] = True
abstract = read('main.tex').split('\\begin{abstract}')[1].split('\\end{abstract}')[0]
assert 'precondition' not in abstract.lower()
assert 'precondition' not in read('sections/01_introduction.tex').lower()
checks['no_preconditioning_in_abstract_or_introduction'] = True

# Exact white-noise specialization of the former matrix loss,
# preconditioning and derivative trace; synthetic algebra only.
rng = np.random.default_rng(20261105)
D = 7
n = 2*D
h,u,g = rng.normal(size=(3,n))
errors=[]
for v in [1e-3, 0.1, 1.0, 100.0]:
    S=(v/2)*np.eye(n)
    sd2=.5
    B=np.linalg.inv(sd2*np.eye(n)+S)
    evals,Q=np.linalg.eigh(B)
    Bin=Q@np.diag(np.sqrt(evals))@Q.T
    K=sd2*B
    evals,Q=np.linalg.eigh(sd2*S@B)
    O=Q@np.diag(np.sqrt(evals))@Q.T
    ci=1/np.sqrt(sd2+v/2)
    cs=sd2/(sd2+v/2)
    co=np.sqrt(sd2*(v/2)/(sd2+v/2))
    np.testing.assert_allclose(Bin@u,ci*u,rtol=1e-12,atol=1e-12)
    np.testing.assert_allclose(K@u+O@g,cs*u+co*g,rtol=1e-12,atol=1e-12)
    f=cs*u+co*g
    loss_old=(f-h)@np.linalg.solve(S,f-h)/(2*D)
    loss_new=np.sum((f-h)**2)/(D*v)
    score=2*(f-u)/v
    dsm=v/(4*D)*np.sum((score+2*(u-h)/v)**2)
    np.testing.assert_allclose([loss_old,dsm],loss_new,rtol=1e-12,atol=1e-12)
    A=rng.normal(size=(n,n)); T=A@A.T+np.eye(n)
    J=T@np.linalg.inv(T+S)
    P=T-T@np.linalg.solve(T+S,T)
    np.testing.assert_allclose(P,(v/2)*J,rtol=1e-9,atol=1e-12)
    np.testing.assert_allclose(np.trace(P)/D,v*np.trace(J)/(2*D),rtol=1e-9)
    z=rng.choice([-1.,1.],size=n); w=np.sqrt(v/2)*z; delta=.01
    fd=w@(J@(u+delta*w)-J@(u-delta*w))/(2*delta*D)
    analytic=v*(z@J@z)/(2*D)
    np.testing.assert_allclose(fd,analytic,rtol=1e-10,atol=1e-12)
    errors.append({'v':v,'loss_abs_error':float(abs(loss_old-loss_new)),
                   'covariance_max_abs_error':float(np.max(np.abs(P-(v/2)*J))),
                   'finite_difference_abs_error':float(abs(fd-analytic))})
checks['algebra_white_specialization'] = errors

pdfs={}
for stem in ['main','main_full']:
    log=read(stem+'.log')
    bad=[line for line in log.splitlines() if any(s in line.lower() for s in
         ['undefined references', 'citation `', 'reference `', 'overfull \\hbox', 'overfull \\vbox'])]
    assert not bad, bad
    assert not any(line.startswith('!') for line in log.splitlines())
    reader=PdfReader(PAPER/(stem+'.pdf'))
    txts=[p.extract_text() for p in reader.pages]
    assert all(len(t.strip())>50 for t in txts)
    assert 'Manor' in '\n'.join(txts)
    pdfs[stem]={'pages':len(reader.pages),'sha256':sha(PAPER/(stem+'.pdf')),
                'bibliography_entries':len(re.findall(r'\\bibitem\{',read(stem+'.bbl'))),
                'no_undefined_references_or_overfull_boxes':True}
    (OUT/(stem+'_extracted.txt')).write_text('\n\f\n'.join(txts),encoding='utf-8')
    print(stem, len(txts), 'pages')
    for i,t in enumerate(txts):
        topics=[k for k in ['Abstract', 'First-Order Score Matching', 'Variance from',
                    'Network Architectures', 'GP-MP Algorithm','CONCLUSION','Receiver Configurations'] if k in t]
        print(i+1, ', '.join(topics), t[:80].replace('\n',' '))
checks['compiled_pdfs']=pdfs
diff=[]
for rel in before:
    p=PAPER/rel
    if p.suffix in ('.tex','.md','.bib') and sha(p)!=before[rel]:
        diff.extend(difflib.unified_diff((OUT/'before'/rel).read_text(encoding='utf-8').splitlines(True),
                                       p.read_text(encoding='utf-8').splitlines(True),
                                       fromfile='before/'+rel,tofile='after/'+rel))
(OUT/'SOURCE_DIFF.txt').write_text(''.join(diff),encoding='utf-8')
checks['status']='PASS_ALGEBRA_PRESERVATION_COMPILATION'
checks['created_local']=datetime.datetime.now().astimezone().isoformat()
(OUT/'VALIDATION.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
print(checks['status'])
