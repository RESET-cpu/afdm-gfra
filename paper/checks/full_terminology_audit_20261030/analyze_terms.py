from pathlib import Path
import json,re,unicodedata,hashlib
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
PAPER=ROOT/'paper/C-STMP'
inventory=json.loads((OUT/'INVENTORY.json').read_text(encoding='utf-8'))
terms=[
 'grant-free random access','joint activity detection and channel estimation',
 'affine frequency division multiplexing','discrete affine Fourier transform',
 'inverse discrete affine Fourier transform','chirp-periodic prefix','differential delay',
 'common delay','delay spread','directional cosines','quasi-static','full diversity',
 'fractional Doppler','fractional delay','effective channel','multiple measurement vector',
 'block sparsity','score-based generative','Tweedie','conditional mean','conditional covariance',
 'expectation propagation','extrinsic message','site approximation','natural parameters',
 'linear MMSE','singular value decomposition','thin singular value decomposition',
 'device activity denoiser','first-order score network','colored Gaussian',
 'denoiser input','denoising score matching','preconditioning','Jacobian','Monte Carlo',
 'density ratio estimation','logistic loss','binary cross-entropy','RefineNet','Adam',
 'exponential moving average','variable projection','minimum description length','MDL',
 'simultaneous orthogonal matching pursuit','GNN-ASPL','off-grid','NTN-TDL-D',
 'normalized mean squared error','activity error rate','genie-aided','oracle',
 'frequency wrapping','proper complex Gaussian','covariance-weighted loss',
 'training queries','scalar query covariance','balanced binary cross-entropy',
 'variance-update residual','activity-history residual',
 'covariance-conditioned denoising','multi-frame linear estimation',
 'generative-prior-aided joint denoising','GP-CCD-MP-DRE'
]
def norm(s):
 s=unicodedata.normalize('NFKC',s).replace('\u00ad','')
 s=re.sub(r'([A-Za-z])-\s*\n\s*([a-z])',r'\1\2',s)
 s=re.sub(r'\s+',' ',s)
 return s
corpus={f.stem:[norm(t) for t in json.loads(f.read_text(encoding='utf-8'))] for f in (OUT/'source_text').glob('*.json')}
rows=[]
for term in terms:
 hits=[]
 # A lexical search is an aid, not a semantic source-verification verdict.
 pattern=r'(?<![A-Za-z])'+r'[-\s]*'.join(re.escape(w) for w in re.split(r'[\s-]+',term))+r'(?![A-Za-z])'
 for key,pages in corpus.items():
  for i,page in enumerate(pages):
   match=re.search(pattern,page,re.I)
   if match:
    hits.append({'key':key,'pdf_page':i+1,'excerpt':page[max(0,match.start()-65):match.end()+130]})
    break
 rows.append({'term':term,'lexical_hits':hits,'note':'First match per source; may be in references or extraction artifacts. See REPORT.md for manual disposition.'})
(OUT/'LEXICAL_SOURCE_MATCHES.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
# Prose export for acronym triage. Preserve abstract, headings and table text;
# supplement figures/algorithm/notation by manual checks recorded in REPORT.md.
inputs=[PAPER/'main.tex']+[PAPER/(x+'.tex') for x in inventory['active_inputs']]
parts=[]
for p in inputs:
 t=p.read_text(encoding='utf-8')
 t=re.sub(r'(?<!\\)%[^\n]*','',t)
 if p.name=='main.tex':
  t=re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}',t,re.S).group(1)
 for env in ['figure','figure*','equation','equation*','align','align*','gather','gather*','tikzpicture']:
  t=re.sub(r'\\begin\{'+re.escape(env)+r'\}.*?\\end\{'+re.escape(env)+r'\}',' ',t,flags=re.S)
 t=re.sub(r'(?<!\\)\$.*?(?<!\\)\$',' ',t,flags=re.S)
 t=re.sub(r'\\\[.*?\\\]',' ',t,flags=re.S)
 t=re.sub(r'\\(?:label|eqref|ref|input|bibliography)\{[^}]*\}',' ',t)
 t=re.sub(r'\\cite\w*(?:\[[^\]]*\])*\{[^}]*\}',' ',t)
 t=re.sub(r'\\[A-Za-z]+\*?(?:\[[^\]]*\])?',' ',t)
 t=t.replace('{',' ').replace('}',' ').replace('~',' ').replace('\\',' ')
 t=re.sub(r'[ \t]+',' ',t)
 t=re.sub(r'(?<!\n)\n(?!\n)',' ',t)
 heading='Abstract' if p.name=='main.tex' else p.stem
 parts.append('## '+heading+'\n\n'+t.strip())
parts.append('## Chinese Abstract\n\n'+(PAPER/'sections/00_abstract_zh.md').read_text(encoding='utf-8').replace('# 摘要',''))
(OUT/'acronym_input.md').write_text('\n\n'.join(parts),encoding='utf-8')
print('Source texts:',len(corpus),'Terms:',len(terms))
for row in rows:
 if row['term'] in ['frequency wrapping','proper complex Gaussian','covariance-weighted loss','training queries','scalar query covariance','balanced binary cross-entropy','device activity denoiser','RefineNet']:
  print(row['term'],[(h['key'],h['pdf_page']) for h in row['lexical_hits']])
