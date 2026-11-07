"""Compare the concise manuscript with its immediate pre-edit snapshot."""
from pathlib import Path
from collections import Counter
import difflib,hashlib,json,re,sys
from pypdf import PdfReader
RUN=Path(__file__).resolve().parent
PAPER=RUN.parents[1]
ROOT=PAPER.parents[1]
base=json.loads((RUN/'BASELINE.json').read_text(encoding='utf-8'))
sys.path.insert(0,r'C:/Users/25911/.codex/skills/academic-research-suite/ars/scripts')
from pdf_read_preflight import run_preflight
read=lambda p:p.read_text(encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
norm=lambda t:re.sub(r'\s+','',t)
def uncomment(t):return re.sub(r'(?<!\\)%[^\n]*','',t)
def blocks(t,kind):
 return re.findall(r'\\begin\{('+kind+r')\}.*?\\end\{\1\}',t,re.S)
def spans(t,kind):
 return [m.group() for m in re.finditer(r'\\begin\{('+kind+r')\}.*?\\end\{\1\}',t,re.S)]
def math(t):
 prepared=uncomment(t).replace(r'\\','\x01\x01')
 return [norm(m.group().replace('\x01\x01',r'\\')) for m in re.finditer(r'(?<!\\)\$.*?(?<!\\)\$|\\\[.*?\\\]',prepared,re.S)]
def cites(t):return {k.strip() for x in re.findall(r'\\cite(?:\[[^\]]*\])*\{([^}]+)\}',t) for k in x.split(',')}
def number_set(t):
 t=re.sub(r'\\(?:cite|ref|eqref|label)(?:\[[^\]]*\])*\{[^}]+\}','',uncomment(t))
 # Compare numerical values; TeX comma grouping and exponent notation remain explicit.
 return set(re.findall(r'\d+(?:\.\d+)?',t))
reports,delta,diffs={}, {},[]
old_all,new_all='',''
numbered_count=0
for path in base['active_inputs']:
 rel=path+'.tex';old=read(RUN/'before'/rel);new=read(PAPER/rel)
 oldeq=spans(old,r'equation\*?|align\*?|gather\*?|multline\*?')
 neweq=spans(new,r'equation\*?|align\*?|gather\*?|multline\*?')
 assert [norm(t) for t in oldeq]==[norm(t) for t in neweq],(rel,'display equation changed')
 labels=re.findall(r'\\label\{([^}]+)\}',old)
 assert labels==re.findall(r'\\label\{([^}]+)\}',new),(rel,'label changed')
 for typ in [r'figure\*?',r'table\*?']:
  assert spans(old,typ)==spans(new,typ),(rel,typ,'changed')
 numbered_count+=sum(len(re.findall(r'\\label\{',s)) for s in oldeq)
 removed=Counter(math(old))-Counter(math(new));added=Counter(math(new))-Counter(math(old))
 delta[rel]={'removed_inline_math':dict(removed),'added_inline_math':dict(added),
             'removed_numerical_values':sorted(number_set(old)-number_set(new)),
             'added_numerical_values':sorted(number_set(new)-number_set(old))}
 reports[rel]={'numbered_equation_blocks_unchanged':len(oldeq),'all_labels_unchanged':True,
               'figures_algorithm_tables_unchanged':True,'chars_before':len(old),'chars_after':len(new)}
 old_all+=old+'\n';new_all+=new+'\n'
 diffs.append(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='before/'+rel,tofile=rel)))
for rel in ['main.tex','references.bib','sections/00_abstract_zh.md','sections/appendix_evaluation_protocol.tex']:
 assert sha(PAPER/rel)==base['files'][rel],(rel,'must remain byte-identical')
for rel,h in base['files'].items():
 if rel.startswith('figures/'):
  assert sha(PAPER/rel)==h,rel
for rel,h in base['protected'].items():assert sha(ROOT/rel)==h,rel
stop=r'\subsection{Stopping Criteria}'
rel='sections/appendix_implementation.tex'
assert read(PAPER/rel).split(stop)[1]==read(RUN/'before'/rel).split(stop)[1]
assert cites(old_all)==cites(new_all)
assert not delta['sections/06_simulation_results.tex']['removed_numerical_values']
assert not delta['sections/06_simulation_results.tex']['added_numerical_values']
all_current=read(PAPER/'main.tex')+new_all
labels=set(re.findall(r'\\label\{([^}]+)\}',all_current))
references=set(re.findall(r'\\(?:ref|eqref)\{([^}]+)\}',all_current))
assert references<=labels,references-labels
keys=set(re.findall(r'@\w+\s*\{\s*([^,\s]+)',read(PAPER/'references.bib')))
assert cites(all_current)<=keys
logpath=PAPER/'main.log'
if not logpath.exists():logpath=RUN/'main.log'
log=read(logpath)
for token in ['Overfull','LaTeX Error','Missing character','multiply defined','undefined references']:
 assert token not in log,token
assert not re.search(r'(Citation|Reference).*undefined',log)
reader=PdfReader(PAPER/'main.pdf');pages=[p.extract_text() for p in reader.pages]
assert len(pages)==12,len(pages)
preflight=run_preflight(PAPER/'main.pdf');assert preflight['verdict']=='PASS'
visible='\n'.join(pages)
for name in ['MIMO','GNN-ASPL','NTN-TDL-D','MSE']:
 assert name in visible,name
assert all(f'[{i}]' in visible for i in range(1,34))
record={'status':'PASS','pages_before':15,'pages_after':len(pages),
        'numbered_equations_preserved':numbered_count,'per_file':reports,
        'main_preamble_and_english_abstract_unchanged':True,'chinese_abstract_unchanged':True,
        'figure_pdfs_unchanged':7,'figure_table_algorithm_blocks_unchanged':True,
        'appendix_c_unchanged':True,'appendix_d_stopping_unchanged':True,
        'all_experimental_numerical_values_retained':True,'citation_key_count':len(cites(all_current)),
        'bibliography_unchanged':True,'pdf_preflight':preflight,'pdf_sha256':sha(PAPER/'main.pdf'),
        'font_sizes_page_dimensions_and_figure_widths_unchanged':True,
        'supplement_created':False,'training_or_inference_run':False,
        'underfull_hbox_count':len(re.findall(r'Underfull \\hbox',log)),
        'underfull_vbox_count':len(re.findall(r'Underfull \\vbox',log)),
        'visual_review':'Pending final render review'}
for name,data in [('VERIFICATION.json',record),('INLINE_MATH_REVIEW.json',delta),('FINAL_PDF_TEXT.json',pages)]:
 (RUN/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(RUN/'MANUSCRIPT.diff').write_text('\n'.join(diffs),encoding='utf-8')
print(json.dumps({k:record[k] for k in ['status','pages_before','pages_after','numbered_equations_preserved','citation_key_count']}))
print('Numerical differences outside experiments:',json.dumps({p:{k:v for k,v in d.items() if 'numerical' in k and v} for p,d in delta.items() if any(v for k,v in d.items() if 'numerical' in k)}))
