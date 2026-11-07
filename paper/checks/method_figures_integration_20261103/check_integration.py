from pathlib import Path
import re,json,hashlib,difflib,sys
import numpy as np
from PIL import Image, ImageOps, ImageDraw
sys.path.append(str(Path.home()/'.cache/codex-pymupdf'))
import pymupdf as fitz

RUN=Path(__file__).resolve().parent
PAPER=RUN.parents[1]
before=RUN/'before'
sections=['02_system_model.tex','03_bayesian_receiver_design.tex','05_overall_algorithm.tex']
math_pattern=r'\\begin\{(equation\*?|align\*?|gather\*?)\}[\s\S]*?\\end\{\1\}'
changes=[];math_checks=[]
for name in sections+['main.tex']:
    rel=Path('sections')/name if name!='main.tex' else Path(name)
    old=(before/rel).read_text(encoding='utf8')
    new=(PAPER/rel).read_text(encoding='utf8')
    a=[m.group(0) for m in re.finditer(math_pattern,old)]
    z=[m.group(0) for m in re.finditer(math_pattern,new)]
    assert a==z,rel
    math_checks.append({'file':str(rel),'numbered_math_blocks_unchanged':True,'count':len(a)})
    changes.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),
                                      fromfile='before/'+str(rel),tofile=str(rel)))
(RUN/'CHANGES.diff').write_text(''.join(changes),encoding='utf8')
old5=(before/'sections/05_overall_algorithm.tex').read_text()
new5=(PAPER/'sections/05_overall_algorithm.tex').read_text()
pattern=r'\\begin\{figure\}\[!t\][\s\S]*?\\end\{figure\}'
assert re.search(pattern,old5).group()==re.search(pattern,new5).group()
hashes=json.loads((RUN/'FIGURE_HASHES_BEFORE.json').read_text(encoding='utf-8-sig'))
for r in hashes:
    assert hashlib.sha256(Path(r['Path']).read_bytes()).hexdigest().upper()==r['Hash']
aux=(PAPER/'main.aux').read_text(encoding='utf8')
figs=[]
for label in ['fig:system-multiframe','fig:receiver-structure','fig:learned-receiver']:
    m=re.search(r'\\newlabel\{'+re.escape(label)+r'\}\{\{([^}]+)\}\{([^}]+)\}',aux)
    assert m,label
    figs.append({'label':label,'number':m[1],'page':int(m[2])})
log=(PAPER/'main.log').read_text(encoding='utf8')
assert not re.search(r'undefined references|Citation .+ undefined|Reference .+ undefined|multiply defined|Overfull',log,re.I)
doc=fitz.open(PAPER/'main.pdf')
for f in figs:assert 'Fig. '+f['number']+'.' in doc[f['page']-1].get_text(),f
for i,p in enumerate(doc):
    assert p.rect.width==612 and p.rect.height==792
    assert len(p.get_text().strip())>100,(i,'near-empty page')

# Page thumbnails make the locations of the new floats and page balance reviewable.
pages=sorted((RUN/'preview').glob('page-*.png'))
thumbs=[]
for i,path in enumerate(pages):
    im=Image.open(path).convert('RGB');im.thumbnail((300,390))
    tile=Image.new('RGB',(314,415),'#e8e8e8');tile.paste(im,((314-im.width)//2,18))
    ImageDraw.Draw(tile).text((10,400),str(i+1),fill='black');thumbs.append(tile)
for start in range(0,len(thumbs),8):
    chunk=thumbs[start:start+8];sheet=Image.new('RGB',(314*4,415*((len(chunk)+3)//4)),'white')
    for j,t in enumerate(chunk):sheet.paste(t,((j%4)*314,(j//4)*415))
    sheet.save(RUN/'preview'/f'contact-{start//8+1}.png')
result={'pages':len(doc),'figures':figs,'math_checks':math_checks,
        'algorithm_1_unchanged':True,'all_figure_files_unchanged':True,
        'undefined_references':False,'overfull_boxes':False,
        'sha256':hashlib.sha256((PAPER/'main.pdf').read_bytes()).hexdigest()}
(RUN/'VALIDATION.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps(result,indent=2))
