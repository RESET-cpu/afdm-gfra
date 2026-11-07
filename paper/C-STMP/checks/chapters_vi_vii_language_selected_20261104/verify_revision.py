"""Check the nine approved VI/VII edits and the added verified reference."""
from pathlib import Path
import difflib,hashlib,json,re,sys,unicodedata
sys.path.insert(0,str(Path.home()/'.cache/codex-pymupdf'))
import fitz
from PIL import Image,ImageDraw
RUN=Path(__file__).resolve().parent; PAPER=RUN.parents[1]
read=lambda p:p.read_text(encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=json.loads(read(RUN/'BEFORE_HASHES.json'))
allowed={'sections/06_simulation_results.tex','sections/07_conclusion.tex','references.bib','main.pdf','main_full.pdf','main.aux','main_full.aux','main.log','main_full.log'}
changed=[k for k,v in before.items() if sha(PAPER/k)!=v]
assert set(changed)<=allowed,set(changed)-allowed
diffs=[]
for rel in ['sections/06_simulation_results.tex','sections/07_conclusion.tex','references.bib']:
 a,b=read(RUN/'before'/rel),read(PAPER/rel)
 diffs.extend(difflib.unified_diff(a.splitlines(True),b.splitlines(True),rel+' before',rel+' after'))
 if rel.endswith('.tex'):
  display=re.compile(r'\\begin\{(equation\*?|align\*?)\}.*?\\end\{\1\}',re.S)
  assert [m.group(0) for m in display.finditer(a)]==[m.group(0) for m in display.finditer(b)]
  assert sorted(re.findall(r'\$[^$]*\$',a))==sorted(re.findall(r'\$[^$]*\$',b))
  assert re.findall(r'\\label\{[^}]+\}',a)==re.findall(r'\\label\{[^}]+\}',b)
(RUN/'SOURCE_DIFF.txt').write_text(''.join(diffs),encoding='utf-8')
oldbib=read(RUN/'before/references.bib'); bib=read(PAPER/'references.bib')
newentry=re.search(r'@inproceedings\{albuquerque2024,.*?\n\}\n\n',bib,re.S)
assert newentry and bib.replace(newentry.group(0),'',1)==oldbib
s6=read(PAPER/'sections/06_simulation_results.tex'); s7=read(PAPER/'sections/07_conclusion.tex')
checks={
'VI01':'Each scene provides four channel samples before multiplication by $\\alpha_k$.' in s6,
'VI02':'initialization using the loss in \\eqref{eq:classifier-loss}, with batch size $32$' in s6,
'VI03':'default damping factors for GP-MP and GP-MP-C' in s6,
'VI04':'GP-MP-C achieves the lowest NMSE and a lower AER than GP-MP.' in s6,
'VI05':'compares channel-estimation performance on' in s6,
'VI06':'For $Q\\leq KN$, we select distinct DFT rows' in s6,
'VI07':'\\cite[Appendix~B.1]{albuquerque2024}' in s6,
'VII01':'lower NMSE than the four sparse-recovery\nbaselines across the tested NTN-TDL profiles without retraining.' in s7,
'VII02':'channel assumptions. We used colored\nGaussian noise to account for correlations' in s7}
assert all(checks.values()),checks
(RUN/'previews').mkdir(exist_ok=True)
results=[]; thumbs=[]
for name in ['main','main_full']:
 a,b=read(RUN/'before'/(name+'.aux')),read(PAPER/(name+'.aux'))
 labels=re.compile(r'\\newlabel\{((?:eq:|frontend:)[^}]+)\}\{\{([^}]+)\}')
 assert labels.findall(a)==labels.findall(b)
 oldkeys=set(re.findall(r'\\bibcite\{([^}]+)\}',a)); keys=set(re.findall(r'\\bibcite\{([^}]+)\}',b))
 assert keys==oldkeys|{'albuquerque2024'} and len(keys)==43
 log=read(PAPER/(name+'.log'))
 for needle in ['undefined references','undefined on input','Undefined control sequence','LaTeX Error','multiply defined','Overfull']:
  assert needle not in log,(name,needle)
 old=fitz.open(RUN/'before'/(name+'.pdf')); new=fitz.open(PAPER/(name+'.pdf'))
 text=unicodedata.normalize('NFKC','\n'.join(p.get_text() for p in new))
 assert 'Inflationary' in text and 'Pearson' in text
 assert 'GP-MP-C-EP' not in text
 changed_pages=[]
 for i,p in enumerate(new):
  if i>=len(old) or p.get_pixmap().samples!=old[i].get_pixmap().samples:
   changed_pages.append(i+1)
   p.get_pixmap(matrix=fitz.Matrix(1.3,1.3)).save(RUN/'previews'/f'{name}_{i+1}.png')
   thumbs.append((name,i+1,p.get_pixmap(matrix=fitz.Matrix(.55,.55))))
 (RUN/(name+'_text.txt')).write_text(text,encoding='utf-8')
 results.append({'name':name,'pages':len(new),'old_pages':len(old),'changed_pages':changed_pages,'references':len(keys),'sha256':sha(PAPER/(name+'.pdf'))})
cols=3; cw,ch=350,470
im=Image.new('RGB',(cols*cw,((len(thumbs)+cols-1)//cols)*ch),'#dddddd'); draw=ImageDraw.Draw(im)
for n,(name,i,pix) in enumerate(thumbs):
 x,y=(n%cols)*cw,(n//cols)*ch
 draw.text((x+4,y+3),f'{name} p.{i}',fill='black')
 im.paste(Image.frombytes('RGB',(pix.width,pix.height),pix.samples),(x,y+20))
im.save(RUN/'previews/changed_pages.png')
result={'status':'PASS','approved_items':checks,'changed_files':changed,'unchanged_protected_files':len(before)-len(changed),'all_math_expressions_preserved':True,'all_figures_unchanged':True,'only_one_new_bib_entry':True,'manuscripts':results,'training_started':False,'inference_started':False}
(RUN/'VALIDATION.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))

