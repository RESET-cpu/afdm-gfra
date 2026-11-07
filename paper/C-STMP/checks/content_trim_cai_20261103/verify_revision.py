"""Verify a prose-only manuscript trim and render the compiled PDF."""
from pathlib import Path
import difflib, hashlib, json, re, shutil, sys
sys.path.append(str(Path.home()/'.cache/codex-pymupdf'))
import pymupdf as fitz
from PIL import Image, ImageDraw

RUN=Path(__file__).resolve().parent
PAPER=RUN.parents[1]
def read(path): return path.read_text(encoding='utf-8')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def blocks(text):
    pattern=r'\\begin\{(equation\*?|align\*?|gather\*?|multline\*?)\}.*?\\end\{\1\}|\\\[.*?\\\]'
    return [m.group() for m in re.finditer(pattern,text,re.S)]
def word_count(text):
    text=re.sub(r'(?<!\\)%[^\n]*',' ',text)
    for block in blocks(text): text=text.replace(block,' ')
    text=re.sub(r'\$[^$]*\$',' ',text,flags=re.S)
    text=re.sub(r'\\[A-Za-z]+(?:\[[^\]]*\])?\{[^}]*\}',' ',text)
    return len(re.findall(r'\b[A-Za-z]+(?:[-\u2013][A-Za-z]+)*\b',text))

manifest=json.loads(read(RUN/'BEFORE.json'))
changed=['sections/'+s for s in ['03_bayesian_receiver_design.tex','04_generative_priors.tex','05_overall_algorithm.tex','06_simulation_results.tex']]
protected={rel:sha(PAPER/rel)==expected for rel,expected in manifest.items() if rel not in changed+['main.pdf']}
assert all(protected.values()),protected
diff=[]; counts={}; equations=0; deletion_only={}
for rel in changed:
    old,new=read(RUN/'before'/rel),read(PAPER/rel)
    assert blocks(old)==blocks(new),rel
    equations+=len(blocks(new))
    assert re.findall(r'\\label\{[^}]+\}',old)==re.findall(r'\\label\{[^}]+\}',new)
    counts[rel]={'before':word_count(old),'after':word_count(new)}
    diff.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=rel+' (before)',tofile=rel))
    if not rel.endswith('06_simulation_results.tex'):
        a,b=re.sub(r'\s+','',old),re.sub(r'\s+','',new)
        cursor=iter(a)
        deletion_only[rel]=all(char in cursor for char in b)
assert all(deletion_only.values())
rel='sections/06_simulation_results.tex'
old,new=read(RUN/'before'/rel),read(PAPER/rel)
key=r'\subsection{Channel Denoising Performance}'
assert old.split(key)[0]==new.split(key)[0]
counts['VI-B-E']={'before':word_count(old.split(key)[1]),'after':word_count(new.split(key)[1])}
float_pattern=r'\\begin\{(figure\*?|table\*?)\}.*?\\end\{\1\}'
assert [m.group() for m in re.finditer(float_pattern,old,re.S)]==[m.group() for m in re.finditer(float_pattern,new,re.S)]
inline=lambda s:set(re.findall(r'\$[^$]*\$',s,re.S))
assert inline(new)<=inline(old),inline(new)-inline(old)
(RUN/'CHANGES.diff').write_text(''.join(diff),encoding='utf-8')
log=read(PAPER/'main.log')
assert 'Overfull' not in log
assert not re.search(r'(?:Reference|Citation).*undefined|There were undefined',log)
shutil.copy2(PAPER/'main.log',RUN/'compile.log')
doc=fitz.open(PAPER/'main.pdf'); preview=RUN/'preview'; preview.mkdir(exist_ok=True)
locations={}
for i,page in enumerate(doc,1):
    page.get_pixmap(dpi=110,alpha=False).save(preview/f'page-{i:02d}.png')
    text=page.get_text()
    for term in ['Fig. 1.', 'Fig. 2.', 'Fig. 3.', 'VI. SIMULATION RESULTS','APPENDIX A','APPENDIX B','APPENDIX C','REFERENCES']:
        if term in text: locations.setdefault(term,[]).append(i)
for start in range(1,len(doc)+1,6):
    sheet=Image.new('RGB',(1440,1300),'white'); draw=ImageDraw.Draw(sheet)
    for j,n in enumerate(range(start,min(start+6,len(doc)+1))):
        im=Image.open(preview/f'page-{n:02d}.png'); im.thumbnail((470,620))
        x,y=(j%3)*480,(j//3)*650; sheet.paste(im,(x,y+24)); draw.text((x+8,y+5),f'Page {n}',fill='black')
    sheet.save(preview/f'contact-{start:02d}.png')
record={
    'scope':'deletions only in III-V; condensed results prose in VI-B-E',
    'protected_files_unchanged':protected,
    'changed_sections_display_blocks_unchanged':equations,
    'III_V_deletions_only':deletion_only,
    'VI_A_and_all_VI_figures_tables_unchanged':True,
    'all_retained_VI_inline_math_from_original':True,
    'word_counts_excluding_math_and_tex_commands':counts,
    'before_pdf_pages':len(fitz.open(RUN/'before/main.pdf')),
    'after_pdf_pages':len(doc),'pdf_sha256':sha(PAPER/'main.pdf'),
    'page_locations':locations,'no_overfull_or_undefined_references':True,
    'visual_review':'pending',
    'source_sha256':{rel:sha(PAPER/rel) for rel in changed}
}
(RUN/'VALIDATION.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in record.items() if k not in ['protected_files_unchanged','source_sha256']},ensure_ascii=False,indent=2))
print(f'All {len(protected)} protected files are byte-identical.')
