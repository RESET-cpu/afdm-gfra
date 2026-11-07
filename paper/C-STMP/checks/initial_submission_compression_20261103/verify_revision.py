"""Check scoped manuscript compression and render the full retained-C PDF."""
from pathlib import Path
import difflib, hashlib, json, re, shutil, sys
sys.path.append(str(Path.home()/'.cache/codex-pymupdf'))
import pymupdf as fitz
from PIL import Image, ImageDraw

RUN=Path(__file__).resolve().parent
PAPER=RUN.parents[1]
def read(p): return p.read_text(encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(s): return re.sub(r'\s+', '', s)
def select_version(s, full):
    def branch(m):
        parts=m.group(1).split('\\else',1)
        return parts[0] if full else (parts[1] if len(parts)>1 else '')
    return re.sub(r'\\ifdefined\\FullManuscript(.*?)\\fi',branch,s,flags=re.S)
def blocks(s):
    pat=r'\\begin\{(equation\*?|align\*?|gather\*?|multline\*?)\}.*?\\end\{\1\}|\\\[.*?\\\]'
    return [m.group() for m in re.finditer(pat,s,re.S)]
def words(s):
    s=re.sub(r'(?<!\\)%[^\n]*',' ',s)
    for b in blocks(s): s=s.replace(b,' ')
    s=re.sub(r'\$[^$]*\$',' ',s,flags=re.S)
    s=re.sub(r'\\[A-Za-z]+(?:\[[^\]]*\])?\{[^}]*\}',' ',s)
    return len(re.findall(r'\b[A-Za-z]+(?:[-\u2013][A-Za-z]+)*\b',s))

changed=[f'sections/{x}.tex' for x in [
    '02_system_model','03_bayesian_receiver_design','04_generative_priors',
    '05_overall_algorithm','06_simulation_results',
    'appendix_parameter_estimation','appendix_afdm_channel_model']]
manifest=json.loads(read(RUN/'BEFORE.json'))
protected={r:sha(PAPER/r)==h for r,h in manifest.items() if r not in changed+['main.pdf','main.tex']}
assert all(protected.values()), protected
oldmaintex=read(RUN/'before/main.tex')
expected=oldmaintex.replace('\\input{sections/appendix_evaluation_protocol}',
    '\\ifdefined\\FullManuscript\n\\input{sections/appendix_evaluation_protocol}\n\\fi')
assert read(PAPER/'main.tex')==expected,'main changes exceed version selection'
assert '\\def\\FullManuscript{1}\n\\input{main.tex}' in read(PAPER/'main_full.tex')
counts={}; differences=[]; removed=[]; added=[]; retained=0
for rel in changed:
    old,new=read(RUN/'before'/rel),select_version(read(PAPER/rel),True)
    counts[rel]={'before':words(old),'after':words(new)}
    differences.extend(difflib.unified_diff(old.splitlines(True),read(PAPER/rel).splitlines(True),fromfile=rel+' (before)',tofile=rel))
    old_blocks={norm(b):b for b in blocks(old)}
    new_blocks={norm(b):b for b in blocks(new)}
    retained+=len(old_blocks.keys() & new_blocks.keys())
    removed += [{'file':rel,'labels':re.findall(r'\\label\{([^}]+)\}',b),'tex':b}
                for key,b in old_blocks.items() if key not in new_blocks]
    added += [{'file':rel,'labels':re.findall(r'\\label\{([^}]+)\}',b),'tex':b}
              for key,b in new_blocks.items() if key not in old_blocks]
allowed_removed={
    'eq:exact-local-moments','eq:score-matching-objective','eq:total-complexity',
    'eq:variance-stopping','frontend:eq:phase-aliases',
    'frontend:eq:spatial-noise-covariance','frontend:eq:noise-tail-statistics',
    'frontend:eq:noise-mdl','eq:matched-otfs-resources','eq:otfs-common-doppler',
    'eq:afdm-modulation-cost','eq:otfs-transform-cancellation'}
assert {l for b in removed for l in b['labels']}==allowed_removed
assert len(added)==1 and added[0]['labels']==['eq:noise-estimation']

active=['main.tex']+[f'sections/{x}.tex' for x in [
    '01_introduction','02_system_model','03_bayesian_receiver_design',
    '04_generative_priors','05_overall_algorithm','06_simulation_results',
    'appendix_parameter_estimation','appendix_afdm_channel_model','appendix_evaluation_protocol']]
source='\n'.join(re.sub(r'(?<!\\)%[^\n]*','',select_version(read(PAPER/r),True)) for r in active)
for full in [False,True]:
    files=[r for r in active if full or not r.endswith('appendix_evaluation_protocol.tex')]
    version_source='\n'.join(re.sub(r'(?<!\\)%[^\n]*','',select_version(read(PAPER/r),full)) for r in files)
    labels=re.findall(r'\\label\{([^}]+)\}',version_source)
    refs=re.findall(r'\\(?:ref|eqref|autoref|pageref)\{([^}]+)\}',version_source)
    assert len(set(labels))==len(labels),'duplicate label'
    assert not (set(refs)-set(labels)),(full,set(refs)-set(labels))
keys=set(re.findall(r'@\w+\s*\{\s*([^,]+),',read(PAPER/'references.bib')))
citations={key.strip() for group in re.findall(r'\\cite(?:\[[^]]*\])?\{([^}]+)\}',source) for key in group.split(',')}
assert not citations-keys,citations-keys

old6=read(RUN/'before/sections/06_simulation_results.tex')
new6=read(PAPER/'sections/06_simulation_results.tex')
tables=lambda s:re.findall(r'\\begin\{table\}.*?\\end\{table\}',s,re.S)
assert tables(old6)==tables(new6),'experiment tables changed'
includes=lambda s:re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}',s)
assert includes(old6)==includes(new6),'experiment figures changed'
oldmain='\n'.join(read(RUN/'before'/r) for r in active)
assert includes(oldmain)==includes(source),'figure order/paths changed'
markers=['fig:cstmp-denoising','tab:activity-evidence','fig:cstmp-convergence',
         'fig:cstmp-snr','fig:cstmp-users','fig:cstmp-activity','fig:cstmp-pilots','fig:cstmp-cross']
def interpretation(s,mark):
    tail=s.split('\\label{'+mark+'}',1)[1]
    tail=re.split(r'\\end\{(?:figure\*?|table)\}',tail,maxsplit=1)[1]
    return re.split(r'\\sub(?:sub)?section\{',tail,maxsplit=1)[0].strip()
assert all(interpretation(old6,m)==interpretation(new6,m) for m in markers)
for name in ['main','main_full']:
    log=read(PAPER/f'{name}.log')
    assert 'Overfull' not in log
    assert not re.search(r'(?:Reference|Citation).*undefined|There were undefined',log)
    shutil.copy2(PAPER/f'{name}.log',RUN/f'{name}_compile.log')
differences.extend(difflib.unified_diff(oldmaintex.splitlines(True),read(PAPER/'main.tex').splitlines(True),fromfile='main.tex (before)',tofile='main.tex'))
differences.extend(difflib.unified_diff([],read(PAPER/'main_full.tex').splitlines(True),fromfile='/dev/null',tofile='main_full.tex'))
(RUN/'CHANGES.diff').write_text(''.join(differences),encoding='utf-8')
(RUN/'EQUATION_CHANGES.json').write_text(json.dumps({'removed_displays':removed,'added_displays':added},ensure_ascii=False,indent=2),encoding='utf-8')

pdfs={}
for name in ['main','main_full']:
    doc=fitz.open(PAPER/f'{name}.pdf');preview=RUN/'preview'/name;preview.mkdir(parents=True,exist_ok=True)
    locations={}
    for i,page in enumerate(doc,1):
        page.get_pixmap(dpi=110,alpha=False).save(preview/f'page-{i:02d}.png')
        text=page.get_text()
        for term in ['Fig. 1.', 'Fig. 2.', 'Fig. 3.','III. TURBO','IV. LEARNING','V. GP-MP','VI. SIMULATION','APPENDIX A','APPENDIX B','APPENDIX C','REFERENCES']:
            if term in text: locations.setdefault(term,[]).append(i)
    assert ('APPENDIX C' in locations)==(name=='main_full')
    for start in range(1,len(doc)+1,6):
        sheet=Image.new('RGB',(1440,1300),'white');draw=ImageDraw.Draw(sheet)
        for j,n in enumerate(range(start,min(start+6,len(doc)+1))):
            im=Image.open(preview/f'page-{n:02d}.png');im.thumbnail((470,620))
            x,y=j%3*480,j//3*650;sheet.paste(im,(x,y+24));draw.text((x+8,y+5),f'Page {n}',fill='black')
        sheet.save(preview/f'contact-{start:02d}.png')
    pdfs[name]={'pages':len(doc),'page_locations':locations,'sha256':sha(PAPER/f'{name}.pdf'),'visual_review':'pending'}
record={
 'protected_files_unchanged':protected,'math_blocks_retained_unchanged':retained,
 'removed_display_blocks':len(removed),'new_noise_estimator_display':True,
 'all_active_refs_and_citations_resolve':True,'no_duplicate_labels':True,
 'experimental_tables_and_figure_assets_unchanged':True,
 'eight_results_interpretation_paragraphs_unchanged':True,
 'word_counts_excluding_math_and_tex_commands':counts,
 'before_pdf_pages':len(fitz.open(RUN/'before/main.pdf')),'pdfs':pdfs,
 'main_tex_only_changed_for_version_selection':True,
 'no_overfull_or_undefined_references':True,
 'source_sha256':{r:sha(PAPER/r) for r in changed}}
(RUN/'VALIDATION.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in record.items() if k not in ['protected_files_unchanged','source_sha256']},ensure_ascii=False,indent=2))
print(f'{len(protected)} protected files unchanged.')
