from pathlib import Path
from collections import Counter
import difflib
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]
CHECK = Path(__file__).resolve().parent

def read(path):
    return path.read_text(encoding='utf-8')

def strip_comments(text):
    return re.sub(r'(?<!\\)%[^\n]*', '', text)

main = strip_comments(read(ROOT/'main.tex'))
included = [ROOT/'main.tex'] + [ROOT/(p+'.tex') for p in re.findall(r'\\input\{([^}]+)\}', main)]
texts = [strip_comments(read(p)) for p in included]
text = '\n'.join(texts)
labels = Counter(re.findall(r'\\label\{([^}]+)\}', text))
refs = set(re.findall(r'\\(?:eqref|ref)\{([^}]+)\}', text))
keys = set(re.findall(r'@\w+\s*\{\s*([^,\s]+)', read(ROOT/'references.bib')))
cites = set()
for group in re.findall(r'\\cite(?:\[[^\]]*\])*\{([^}]+)\}', text):
    cites.update(s.strip() for s in group.split(','))

def equations(paths):
    result = {}
    for path in paths:
        for match in re.finditer(r'\\begin\{(equation|align)\}.*?\\end\{\1\}', read(path), re.S):
            for label in re.findall(r'\\label\{([^}]+)\}', match.group()):
                result[label] = re.sub(r'\s+', '', match.group())
    return result

old_eq = equations(CHECK/'before'/p.relative_to(ROOT) for p in included)
new_eq = equations(included)
baseline = json.loads(read(CHECK/'BASELINE.json'))
changed = [name.replace('\\','/') for name,digest in baseline.items()
           if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest]
allowed = {'README.md','docs/TERMINOLOGY.md',
           'sections/03_bayesian_receiver_design.tex',
           'sections/04_generative_priors.tex',
           'sections/05_overall_algorithm.tex',
           'sections/06_simulation_results.tex',
           'sections/appendix_parameter_estimation.tex'}
old_algorithm = re.search(r'\\begin\{figure\}.*?\\end\{figure\}', read(CHECK/'before/sections/05_overall_algorithm.tex'), re.S).group()
new_algorithm = re.search(r'\\begin\{figure\}.*?\\end\{figure\}', read(ROOT/'sections/05_overall_algorithm.tex'), re.S).group()
results_anchor = r'\subsection{Channel Denoising Performance}'
old_results = read(CHECK/'before/sections/06_simulation_results.tex').split(results_anchor,1)[1]
new_results = read(ROOT/'sections/06_simulation_results.tex').split(results_anchor,1)[1]
old_phase = read(CHECK/'before/sections/appendix_parameter_estimation.tex').split('\\label{app:frontend}',1)[1].strip()
phase_kept = old_phase in read(ROOT/'sections/appendix_parameter_estimation.tex')
log = read(CHECK/'build/main.log')
from pypdf import PdfReader
pdf = CHECK/'build/main.pdf'
reader = PdfReader(pdf)
pdf_texts = [p.extract_text() for p in reader.pages]
(CHECK/'build/main.txt').write_text('\n\f\n'.join(pdf_texts),encoding='utf-8')
report = {
    'scope':'Author-approved restructuring of chapters III--V; collateral relocation into VI-A and Appendix A.',
    'active_tex_files': [str(p.relative_to(ROOT)).replace('\\','/') for p in included],
    'changed_baseline_files':changed,
    'unexpected_changed_files':sorted(set(changed)-allowed),
    'duplicate_labels':sorted(k for k,v in labels.items() if v>1),
    'undefined_references':sorted(refs-set(labels)),
    'missing_bibliography_keys':sorted(cites-keys),
    'original_equation_label_count':len(old_eq),
    'removed_equation_labels':sorted(set(old_eq)-set(new_eq)),
    'changed_original_equations':sorted(k for k in old_eq.keys()&new_eq.keys() if old_eq[k]!=new_eq[k]),
    'added_equation_labels':sorted(set(new_eq)-set(old_eq)),
    'algorithm_table_unchanged':old_algorithm==new_algorithm,
    'experimental_results_text_unchanged':old_results==new_results,
    'original_phase_estimation_body_preserved':phase_kept,
    'abstract_regenerated':False,
    'code_experiments_or_training_changed':False,
    'compile_engine':'Tectonic 0.17.0',
    'pdf_pages':len(reader.pages),
    'latex_errors':re.findall(r'^!.*$',log,re.M),
    'overfull_boxes':re.findall(r'^Overfull.*$',log,re.M),
    'undefined_compile_references':re.findall(r'^.*(?:undefined|multiply defined).*$','\n'.join(log.splitlines()),re.M),
    'underfull_box_count':len(re.findall(r'^Underfull',log,re.M)),
    'other_warning':'Existing amsmath bracket-group notice from the unchanged matrix-indexing expression in chapter II.',
    'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),
    'visual_review':'Rendered pages 4--14 reviewed; formulas, algorithm table, relocated settings, figures and appendices remain readable without clipping or overlap.',
}
for key in ['unexpected_changed_files','duplicate_labels','undefined_references','missing_bibliography_keys',
            'removed_equation_labels','changed_original_equations','latex_errors','overfull_boxes','undefined_compile_references']:
    assert not report[key], (key,report[key])
for key in ['algorithm_table_unchanged','experimental_results_text_unchanged','original_phase_estimation_body_preserved']:
    assert report[key],key
assert report['added_equation_labels']==['eq:active-channel-posterior','eq:activity-log-odds','eq:conditional-channel-integrals']
diffs=[]
for name in changed:
    diffs.extend(difflib.unified_diff(read(CHECK/'before'/name).splitlines(keepends=True),read(ROOT/name).splitlines(keepends=True),fromfile='before/'+name,tofile='after/'+name))
(CHECK/'CHANGES.diff').write_text(''.join(diffs),encoding='utf-8',newline='\n')
(CHECK/'VALIDATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ['pdf_pages','original_equation_label_count','changed_original_equations','added_equation_labels','undefined_references','missing_bibliography_keys','algorithm_table_unchanged','experimental_results_text_unchanged']},ensure_ascii=False,indent=2))
