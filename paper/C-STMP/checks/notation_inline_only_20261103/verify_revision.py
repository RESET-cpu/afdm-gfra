"""Verify the scoped rollback and render the current manuscript."""
from pathlib import Path
import difflib, hashlib, json, re, shutil, sys
sys.path.append(str(Path.home()/'.cache/codex-pymupdf'))
import pymupdf as fitz
from PIL import Image, ImageDraw

RUN=Path(__file__).resolve().parent
PAPER=RUN.parents[1]
def read(p): return p.read_text(encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads(read(RUN/'BEFORE.json'))
active=[rel for rel in manifest if rel.endswith('.tex')]
diff=[]
display_count=0
labels_old=[]; labels_new=[]
for rel in active:
    old,new=read(RUN/'before'/rel),read(PAPER/rel)
    equations=lambda s: re.findall(r'\\begin\{equation\*?\}.*?\\end\{equation\*?\}|\\\[.*?\\\]',s,re.S)
    assert equations(old)==equations(new),rel
    display_count+=len(equations(new))
    labels_old+=re.findall(r'\\label\{([^}]+)\}',old)
    labels_new+=re.findall(r'\\label\{([^}]+)\}',new)
    diff.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=rel+' (before)',tofile=rel))
(RUN/'CHANGES.diff').write_text(''.join(diff),encoding='utf-8')
other=[rel for rel in manifest if (rel.startswith('figures/') and not rel.endswith('README.md')) or rel=='references.bib' or (rel.startswith('sections/') and rel!='sections/02_system_model.tex')]
unchanged={rel:sha(PAPER/rel)==manifest[rel] for rel in other}
assert all(unchanged.values())
assert read(PAPER/'main.tex')==read(PAPER/'checks/notation_cai_shen_20261103/before/main.tex')
assert set(labels_old)-set(labels_new)=={'tab:notation'}
assert set(labels_new)-set(labels_old)==set()
assert 'tab:notation' not in read(PAPER/'sections/02_system_model.tex')
log=read(PAPER/'main.log')
assert 'Overfull' not in log
assert not re.search(r'(?:Reference|Citation).*undefined|There were undefined',log)
shutil.copy2(PAPER/'main.log',RUN/'compile.log')
preview=RUN/'preview'; preview.mkdir(exist_ok=True)
doc=fitz.open(PAPER/'main.pdf')
locations={}
for i,page in enumerate(doc,1):
    page.get_pixmap(dpi=105,alpha=False).save(preview/f'page-{i:02d}.png')
    t=page.get_text()
    assert 'SUMMARY OF NOTATIONS' not in t
    for term in ['Fig. 1.', 'Fig. 2.', 'Fig. 3.', 'SIMULATION PARAMETERS', 'AER WITH DIFFERENT ACTIVITY EVIDENCE']:
        if term in t: locations.setdefault(term,[]).append(i)
for start in range(1,len(doc)+1,6):
    sheet=Image.new('RGB',(1440,1300),'white'); draw=ImageDraw.Draw(sheet)
    for j,n in enumerate(range(start,min(start+6,len(doc)+1))):
        im=Image.open(preview/f'page-{n:02d}.png'); im.thumbnail((470,620))
        x,y=(j%3)*480,(j//3)*650; sheet.paste(im,(x,y+24)); draw.text((x+8,y+5),f'Page {n}',fill='black')
    sheet.save(preview/f'contact-{start:02d}.png')
record={'display_blocks_identical':display_count,'main_tex_restored_to_pre_table_version':True,'removed_label':'tab:notation','protected_files_unchanged':unchanged,'no_overfull_or_undefined_references':True,'pdf_pages':len(doc),'pdf_sha256':sha(PAPER/'main.pdf'),'page_locations':locations,'visual_review':'pending','source_hashes':{r:sha(PAPER/r) for r in active}}
(RUN/'VALIDATION.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in record.items() if k not in ['protected_files_unchanged','source_hashes']},ensure_ascii=False,indent=2))
print(f'{len(other)} protected files unchanged.')
