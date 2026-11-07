from pathlib import Path
import hashlib,json,re,sys,difflib
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
PAPER=ROOT/'paper/C-STMP'
sys.path.insert(0,str(ROOT/'src/evaluation/plots'))
from manuscript.vector import fitz
from PIL import Image,ImageDraw

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(rel,old=False):return ((OUT/'before/paper/C-STMP') if old else PAPER).joinpath(rel).read_text(encoding='utf-8')
before=json.loads((OUT/'BEFORE_HASHES.json').read_text(encoding='utf-8'))
protected=[r for r in before if '/figures/' in r or r in ['FINAL.json','MAINLINE.json','src/configs/final/phase.json','src/configs/plots/manuscript.json']]
protected += ['paper/C-STMP/'+r for r in ['main_full.tex','references.bib','sections/00_abstract_zh.md',
    'sections/01_introduction.tex','sections/02_system_model.tex','sections/03_bayesian_receiver_design.tex',
    'sections/04_generative_priors.tex','sections/07_conclusion.tex']]
for rel in protected:assert sha(ROOT/rel)==before[rel],rel
assert not (PAPER/'sections/appendix_parameter_estimation.tex').exists()
assert sha(PAPER/'docs/derivations/phase_estimation.tex')==before['paper/C-STMP/sections/appendix_parameter_estimation.tex']

def equations(text):
    found={}
    for block in re.findall(r'\\begin\{equation\}(.*?)\\end\{equation\}',text,re.S):
        labels=re.findall(r'\\label\{([^}]+)\}',block)
        normalized=re.sub(r'\s+','',re.sub(r'\\label\{[^}]+\}','',block))
        for key in labels:found[key]=normalized
    return found
old_ch5=read('sections/05_overall_algorithm.tex',True)
new_ch5=read('sections/05_overall_algorithm.tex')
old_eq=equations(old_ch5);new_eq=equations(new_ch5)
for label,block in old_eq.items():assert new_eq[label]==block,label
phase_old=equations(read('sections/appendix_parameter_estimation.tex',True))
for src,dst in [('frontend:eq:phase-atom','eq:phase-atom'),('frontend:eq:marginal-objective','eq:phase-objective')]:
    assert phase_old[src]==new_eq[dst],(src,dst)
def algo(s):return s.split('\\begin{algorithmic}')[1].split('\\end{algorithmic}')[0]
assert algo(new_ch5)==algo(old_ch5).replace('Appendix~\\ref{app:phase-estimation}','Section~\\ref{sec:phase-estimation}')
old_ch6=read('sections/06_simulation_results.tex',True);new_ch6=read('sections/06_simulation_results.tex')
key='All receivers estimate the noise variance from the observations.'
float_pattern=r'\\begin\{(figure\*?|table\*?)\}.*?\\end\{\1\}'
def float_blocks(s):
    return {re.search(r'\\label\{([^}]+)\}',m.group(0)).group(1):m.group(0)
            for m in re.finditer(float_pattern,s,re.S)}
assert float_blocks(old_ch6)==float_blocks(new_ch6)
def prose(s):return re.sub(r'\s+','',re.sub(float_pattern,'',s,flags=re.S))
settings_start=new_ch6.index('For GP-MP-EP, we search')
settings_end=new_ch6.index(key)
assert prose(old_ch6)==prose(new_ch6[:settings_start]+new_ch6[settings_end:])
assert read('sections/appendix_evaluation_protocol.tex')==read('sections/appendix_evaluation_protocol.tex',True).replace('Appendix~\\ref{app:phase-estimation}','Section~\\ref{sec:phase-estimation}')
active='\n'.join(p.read_text(encoding='utf-8') for p in PAPER.joinpath('sections').glob('*.tex'))
assert not any(k in active for k in ['app:frontend','app:phase-estimation','frontend:eq:'])

# The receiver figure embeds these equation numbers as vector text.
figure_labels={'eq:derivative-trace':'29','eq:site-update':'34','eq:conditional-moments':'35',
 'eq:activity-probability':'33','eq:mixture':'19','eq:joint-spatial-covariance':'20',
 'eq:joint-average-variance':'21','eq:nonlinear-extrinsic':'22'}
aux=read('main.aux')
for label,number in figure_labels.items():
    assert f'\\newlabel{{{label}}}{{{{{number}}}' in aux,(label,number)
assert '\\newlabel{app:evaluation-protocol}{{A}' in read('main_full.aux')
assert 'app:evaluation-protocol' not in aux

render=OUT/'rendered';render.mkdir(exist_ok=True)
pdfs={}
for stem in ['main','main_full']:
    log=read(stem+'.log').lower()
    assert not any(x in log for x in ['undefined references','undefined citations','overfull \\hbox','overfull \\vbox','missing character'])
    with fitz.open(PAPER/(stem+'.pdf')) as doc:
        texts=[p.get_text() for p in doc]
        text='\n'.join(texts)
        assert 'PHASE ESTIMATION' not in text
        assert ('RECEIVER CONFIGURATIONS AND EVALUATION' in text)==(stem=='main_full')
        for phrase in ['Gaussian marginal-likelihood objective','128','L-BFGS-B']:
            assert phrase in text,phrase
        figure10_page=next(i+1 for i,t in enumerate(texts) if 'Fig. 10.' in t)
        references_page=next(i+1 for i,t in enumerate(texts) if '\nREFERENCES\n' in t)
        assert figure10_page<=references_page
        if figure10_page==references_page:
            page=doc[figure10_page-1]
            assert page.search_for('Fig. 10.')[0].y1<page.search_for('REFERENCES')[0].y0
        pages=[]
        for i,p in enumerate(doc):
            if i>=5:p.get_pixmap(dpi=85).save(render/f'{stem}-{i+1:02d}.png')
            if 'Gaussian marginal-likelihood objective' in texts[i]:pages.append(i+1)
        pdfs[stem]={'pages':len(doc),'phase_method_pages':pages,
                   'last_figure_page':figure10_page,'references_start_page':references_page,
                   'bibliography_entries':len(re.findall(r'\\bibitem\{',read(stem+'.bbl'))),
                   'sha256':sha(PAPER/(stem+'.pdf'))}
        (OUT/(stem+'_extracted.txt')).write_text('\n\f\n'.join(texts),encoding='utf-8')
files=sorted(render.glob('main-*.png'))
contact=Image.new('RGB',(1360,((len(files)+3)//4)*460),'#dddddd');draw=ImageDraw.Draw(contact)
for i,p in enumerate(files):
    im=Image.open(p).convert('RGB');im.thumbnail((328,430));x=(i%4)*340+6;y=(i//4)*460+22
    contact.paste(im,(x,y));draw.text((x,y-18),p.stem,fill='black')
contact.save(render/'main_contact.png')
files=sorted(render.glob('main_full-*.png'))
contact=Image.new('RGB',(1360,((len(files)+3)//4)*460),'#dddddd');draw=ImageDraw.Draw(contact)
for i,p in enumerate(files):
    im=Image.open(p).convert('RGB');im.thumbnail((328,430));x=(i%4)*340+6;y=(i//4)*460+22
    contact.paste(im,(x,y));draw.text((x,y-18),p.stem,fill='black')
contact.save(render/'full_contact.png')
diff=[]
for rel in before:
    p=ROOT/rel
    if p.exists() and p.suffix in ('.tex','.md') and sha(p)!=before[rel]:
        diff.extend(difflib.unified_diff((OUT/'before'/rel).read_text(encoding='utf-8').splitlines(True),
                      p.read_text(encoding='utf-8').splitlines(True),fromfile='before/'+rel,tofile='after/'+rel))
(OUT/'SOURCE_DIFF.txt').write_text(''.join(diff),encoding='utf-8')
result={'status':'PASS','protected_files_unchanged':protected,'original_appendix_preserved_verbatim':True,
 'existing_ch5_equations_unchanged':list(old_eq),'phase_equations_relocated_unchanged':2,
 'algorithm_operations_unchanged':True,'experiment_results_unchanged':True,
 'experiment_figures_tables_unchanged':True,'existing_ch6_prose_unchanged':True,
 'figure_equation_references_correct':figure_labels,'full_protocol_appendix':'A',
 'compiled_pdfs':pdfs}
(OUT/'VALIDATION.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({'status':'PASS','pdfs':pdfs},indent=2))
