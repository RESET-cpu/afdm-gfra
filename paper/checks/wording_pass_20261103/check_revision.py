"""Check only manuscript invariants and render the two compiled documents."""
from pathlib import Path
import sys,re,json,hashlib,difflib,shutil
sys.path.append(str(Path.home()/'.cache/codex-pymupdf'))
import pymupdf as fitz
from PIL import Image,ImageDraw
sys.stdout.reconfigure(encoding='utf-8')

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[1]
OUT=RUN/'render';OUT.mkdir(exist_ok=True)
source=(ROOT/'main.tex').read_text(encoding='utf-8')
active=[x+'.tex' for x in re.findall(r'\\input\{([^}]+)\}',source)]
result={}
math_pattern=r'\\begin\{(equation\*?|align\*?|gather\*?)\}[\s\S]*?\\end\{\1\}'
maths={};cites=[[],[]];diff=[]
for rel in ['main.tex','main_full.tex']+active:
    before=(RUN/'before'/rel).read_text(encoding='utf-8')
    after=(ROOT/rel).read_text(encoding='utf-8')
    a=[m.group(0) for m in re.finditer(math_pattern,before)]
    b=[m.group(0) for m in re.finditer(math_pattern,after)]
    maths[rel]={'count':len(a),'unchanged':a==b}
    for n,s in enumerate([before,after]):
        cites[n].extend(re.findall(r'\\cite(?:\[[^\]]*\])*\{[^}]*\}',s))
    diff.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='before/'+rel,tofile='after/'+rel))
result['active_numbered_math']=maths
result['active_numbered_math_count']=sum(x['count'] for x in maths.values())
result['all_active_numbered_math_unchanged']=all(x['unchanged'] for x in maths.values())
result['citations_unchanged']=sorted(cites[0])==sorted(cites[1])
result['bib_unchanged']=(RUN/'before/references.bib').read_bytes()==(ROOT/'references.bib').read_bytes()
result['reference_count']=len(re.findall(r'\\bibitem',(ROOT/'main.bbl').read_text(encoding='utf-8')))
sim='sections/06_simulation_results.tex'
cells=lambda s:re.findall(r'\$([^$]*)\$','\n'.join(re.findall(r'\\begin\{tabular\}[\s\S]*?\\end\{tabular\}',s)))
result['table_math_cells_unchanged']=cells((RUN/'before'/sim).read_text(encoding='utf-8'))==cells((ROOT/sim).read_text(encoding='utf-8'))
for name in ['main','main_full']:
    doc=fitz.open(ROOT/(name+'.pdf'));texts=[];tiles=[];pos={}
    for i,p in enumerate(doc,1):
        t=p.get_text();texts.append(t)
        for q in ['Fig. 1.','Fig. 2.','Fig. 3.','VII. CONCLUSION','Additional Implementation Settings']:
            if q in t:pos[q]=i
        dest=OUT/f'{name}-{i:02d}.png'
        p.get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).save(dest)
        im=Image.open(dest);im.thumbnail((260,350))
        tile=Image.new('RGB',(280,380),'#eeeeee');tile.paste(im,((280-im.width)//2,25))
        ImageDraw.Draw(tile).text((10,7),f'{name} page {i}',fill='black');tiles.append(tile)
    for n in range(0,len(tiles),8):
        canvas=Image.new('RGB',(1120,760),'white')
        for j,im in enumerate(tiles[n:n+8]):canvas.paste(im,((j%4)*280,(j//4)*380))
        canvas.save(OUT/f'{name}-overview-{n//8+1}.png')
    text='\n\f\n'.join(texts)
    (RUN/(name+'_text.txt')).write_text(text,encoding='utf-8')
    log=(ROOT/(name+'.log')).read_text(encoding='utf-8',errors='replace')
    shutil.copy2(ROOT/(name+'.log'),RUN/(name+'.log'))
    result[name]={'pages':len(doc),'positions':pos,'undefined_references':bool(re.search(r'undefined references|Citation .+ undefined|Reference .+ undefined',log,re.I)),'overfull_boxes':'Overfull' in log,'missing_characters':'Missing character' in log,'moment_visible':bool(re.search(r'\bmoments?\b',text,re.I)),'pdf_sha256':hashlib.sha256((ROOT/(name+'.pdf')).read_bytes()).hexdigest()}
    assert not any(result[name][x] for x in ['undefined_references','overfull_boxes','missing_characters','moment_visible'])
    print(name,':',len(doc),'pages; reference/layout/text checks passed')
result['experimental_figure_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'figures').glob('*.pdf') if p.stem not in ['learned_receiver','factor_graph','system_multiframe']}
for rel in ['README.md','figures/README.md','docs/TERMINOLOGY.md']:
    before=(RUN/'before'/rel).read_text(encoding='utf-8');after=(ROOT/rel).read_text(encoding='utf-8')
    diff.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='before/'+rel,tofile='after/'+rel))
(RUN/'CHANGES.diff').write_text(''.join(diff),encoding='utf-8')
assert result['all_active_numbered_math_unchanged'] and result['citations_unchanged'] and result['bib_unchanged'] and result['table_math_cells_unchanged']
(RUN/'VALIDATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('Active numbered math environments unchanged:',result['active_numbered_math_count'])
print('References:',result['reference_count'],'; table values unchanged')
