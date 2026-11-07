from pathlib import Path
from collections import Counter
import difflib, hashlib, json, re, sys
from pypdf import PdfReader

RUN=Path(__file__).resolve().parent
PAPER=RUN.parents[1]
ROOT=PAPER.parents[1]
base=json.loads((RUN/'BASELINE.json').read_text(encoding='utf-8'))
read=lambda p:p.read_text(encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
norm=lambda s:re.sub(r'\s+','',s)
old={rel+'.tex':read(RUN/'before'/(rel+'.tex')) for rel in base['active_inputs']}
main=read(PAPER/'main.tex')
new_inputs=re.findall(r'^\\input\{([^}]+)\}',main,re.M)
new={rel+'.tex':read(PAPER/(rel+'.tex')) for rel in new_inputs}
assert new_inputs==[x for x in base['active_inputs'] if x!='sections/appendix_implementation']
assert main==read(RUN/'before/main.tex').replace('\\input{sections/appendix_implementation}\n','')

for rel in ['sections/01_introduction.tex','sections/00_abstract_zh.md','sections/appendix_evaluation_protocol.tex','references.bib']:
    assert sha(PAPER/rel)==base['files'][rel],rel
for name,h in base['figures'].items():assert sha(PAPER/'figures'/name)==h,name
for rel,h in base['protected'].items():assert sha(ROOT/rel)==h,rel

def equation_map(files):
    result={}
    for rel,t in files.items():
        for m in re.finditer(r'\\begin\{(equation\*?|align\*?|gather\*?|multline\*?)\}.*?\\end\{\1\}',t,re.S):
            for label in re.findall(r'\\label\{([^}]+)\}',m[0]):
                assert label not in result,label
                result[label]={'file':rel,'body':norm(m[0])}
    return result
oe,ne=equation_map(old),equation_map(new)
assert set(oe)-set(ne)=={'eq:path-operator'}
assert not set(ne)-set(oe)
for key in ne:assert oe[key]['body']==ne[key]['body'],('equation changed',key)
# The removed appendix expression duplicated the unchanged body path operator.
assert all(norm(s) in oe['eq:path-operator']['body'] and norm(s) in ne['eq:path-operator-system']['body'] for s in [
    r'\mathbf F_{\rm A}\mathbf D_{\nu,g}\mathbf B_d',
    r'\diag\{e^{j2\pi\nu T_s(g+t)}\}_{t=0}^{N-1}'
])

old_all=read(RUN/'before/main.tex')+'\n'+'\n'.join(old.values())
new_all=main+'\n'+'\n'.join(new.values())
labels=lambda t:re.findall(r'\\label\{([^}]+)\}',t)
assert set(labels(old_all))-set(labels(new_all))=={'eq:path-operator','app:implementation'}
assert all(v==1 for v in Counter(labels(new_all)).values())
refs=set(re.findall(r'\\(?:ref|eqref)\{([^}]+)\}',new_all))
assert refs<=set(labels(new_all)),refs-set(labels(new_all))
cites=lambda t:{k.strip() for m in re.findall(r'\\cite(?:\[[^\]]*\])*\{([^}]+)\}',t) for k in m.split(',')}
assert cites(old_all)==cites(new_all)
keys=set(re.findall(r'@\w+\s*\{\s*([^,\s]+)',read(PAPER/'references.bib')))
assert cites(new_all)<=keys

blocks=lambda t,kind:[m[0] for m in re.finditer(r'\\begin\{('+kind+r')\}.*?\\end\{\1\}',t,re.S)]
for rel,t in new.items():
    assert blocks(old[rel],r'table\*?')==blocks(t,r'table\*?'),rel
    expected=old[rel].replace('SVD implementation in Appendix~\\ref{app:implementation}. For','SVD expression in \\eqref{eq:linear-fraction}. For').replace('Appendix~\\ref{app:implementation} and update the stopping history;','Section~\\ref{sec:stopping-criteria} and update the stopping history;')
    assert blocks(expected,r'figure\*?')==blocks(t,r'figure\*?'),rel

results_marker=r'\subsection{Channel Denoising Performance}'
assert old['sections/06_simulation_results.tex'].split(results_marker)[1]==new['sections/06_simulation_results.tex'].split(results_marker)[1]
noise=old['sections/appendix_parameter_estimation.tex'].split(r'\subsection{Noise variance estimation}')[1].strip()
assert noise in new['sections/05_overall_algorithm.tex']
d=old['sections/appendix_implementation.tex']
stop=d.split(r'\subsection{Stopping Criteria}')[1].strip()
rule,values=stop.rsplit('\n\n',1)
assert rule in new['sections/05_overall_algorithm.tex']
assert values in new['sections/06_simulation_results.tex']
net=d.split(r'\subsection{Network Inputs and Training Settings}')[1].split(r'\subsection{Stopping Criteria}')[0].strip()
_,features,derivative=net.split('\n\n')
assert features in new['sections/04_generative_priors.tex']
assert norm(derivative[4:]) in norm(new['sections/06_simulation_results.tex'])
nums=lambda t:set(re.findall(r'\d+(?:\.\d+)?',re.sub(r'\\(?:cite|ref|eqref|label)\{[^}]+\}','',t)))
assert nums(old_all)==nums(new_all),(nums(old_all)-nums(new_all),nums(new_all)-nums(old_all))

log=read(PAPER/'main.log') if (PAPER/'main.log').exists() else read(RUN/'main.log')
for token in ['Overfull','LaTeX Error','Missing character','multiply defined','undefined references']:
    assert token not in log,token
assert not re.search(r'(Citation|Reference).*undefined',log)
sys.path.insert(0,r'C:\Users\25911\.codex\skills\academic-research-suite\ars\scripts')
from pdf_read_preflight import run_preflight
preflight=run_preflight(PAPER/'main.pdf');assert preflight['verdict']=='PASS'
pages=[p.extract_text() for p in PdfReader(PAPER/'main.pdf').pages]
visible='\n'.join(pages)
assert all(f'[{i}]' in visible for i in range(1,34))
assert 'APPENDIXC' in norm(visible) and 'APPENDIXD' not in norm(visible)
record={'status':'PASS','pages_before':base['pages_before'],'pages_after':len(pages),
    'numbered_equation_labels_before':len(oe),'numbered_equation_labels_after':len(ne),
    'remaining_equations_unchanged':True,'merged_duplicate_equation':'eq:path-operator -> eq:path-operator-system',
    'moved_equations':{k:{'from':oe[k]['file'],'to':ne[k]['file']} for k in ne if oe[k]['file']!=ne[k]['file']},
    'appendix_c_byte_identical':True,'appendix_c_letter_preserved':True,'introduction_byte_identical':True,
    'abstracts_unchanged':True,'main_preamble_unchanged':True,'figures_unchanged':True,'algorithm_only_references_updated':True,
    'experimental_results_text_unchanged':True,'stopping_rules_and_values_preserved':True,'noise_estimator_preserved':True,
    'network_inputs_preserved':True,'numerical_value_sets_unchanged':True,'citation_keys':len(cites(new_all)),
    'pdf_preflight':preflight,'pdf_sha256':sha(PAPER/'main.pdf'),
    'underfull_hbox_count':len(re.findall(r'Underfull \\hbox',log)),
    'underfull_vbox_count':len(re.findall(r'Underfull \\vbox',log)),
    'visual_review':'Pending','training_or_inference_run':False}
(RUN/'VERIFICATION.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(RUN/'PDF_TEXT.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
diff=[]
for rel in ['main.tex',*old]:
    a=read(RUN/'before'/rel);b=read(PAPER/rel) if (PAPER/rel).exists() else ''
    if a!=b:diff.extend(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='before/'+rel,tofile=rel))
(RUN/'MANUSCRIPT.diff').write_text(''.join(diff),encoding='utf-8')
print(json.dumps({k:record[k] for k in ['status','pages_after','numbered_equation_labels_before','numbered_equation_labels_after','appendix_c_byte_identical','introduction_byte_identical','citation_keys']},ensure_ascii=False))
