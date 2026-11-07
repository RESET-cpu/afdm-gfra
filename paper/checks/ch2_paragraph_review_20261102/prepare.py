from pathlib import Path
import hashlib,json,sys
from pypdf import PdfReader
sys.stdout.reconfigure(encoding='utf-8')
root=Path('D:/afdm-gfra')
out=root/'paper/C-STMP/checks/ch2_paragraph_review_20261102'
for d in ['sources','paragraphs','reports','snapshot']:(out/d).mkdir(exist_ok=True,parents=True)
source=root/'paper/C-STMP/sections/02_system_model.tex'
raw=source.read_bytes(); lines=raw.decode('utf-8-sig').splitlines()
spans=[(4,14,'系统场景'),(18,44,'物理信道与差分时延'),(46,59,'阵列响应与块内恒定'),(63,74,'多帧导频与矩阵'),(76,81,'导频约束'),(83,110,'IDAFT与DAFT'),(112,126,'CPP与帧长'),(128,139,'连续波形'),(141,169,'有效信道与单路径矩阵'),(171,184,'跨帧相位关系'),(188,208,'设备活动与相位导频'),(210,219,'单帧接收模型'),(221,245,'MMV与块稀疏性'),(247,287,'贝叶斯问题与估计目标')]
items=[]
for i,(start,end,title) in enumerate(spans,1):
    pid=f'P{i:02d}'
    text='\n'.join(lines[start-1:end])+'\n'
    (out/'paragraphs'/f'{pid}.tex').write_text(text,encoding='utf-8')
    items.append(dict(id=pid,start=start,end=end,title=title,text=text))
(out/'PARAGRAPHS.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'snapshot'/'02_system_model.tex').write_bytes(raw)
protected={}
for p in [root/'paper/C-STMP/main.tex',root/'paper/C-STMP/main.pdf',*sorted((root/'paper/C-STMP/sections').glob('*')),root/'paper/C-STMP/docs/TERMINOLOGY.md',root/'paper/C-STMP/docs/WRITING_GUIDE.md']:
    if p.is_file():protected[str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest()
(out/'BASELINE.json').write_text(json.dumps(protected,indent=2),encoding='utf-8')
pdfs={k:root/f'reference/literature/{v}' for k,v in {'shen':'shen2025.pdf','cai':'cai2026.pdf','cai_v2':'cai2026_stmp_v2.pdf','ding':'ding2026.pdf','wei':'wei_yuan_2026_lstmp_v1.pdf','huang':'huang2026.pdf'}.items()}
pdfs.update({k:root/f'paper/C-STMP/checks/strict_sentence_audit_20261029/sources/{v}' for k,v in {'li':'li2023.pdf','bemani':'bemani2022.pdf'}.items()})
manifest=[]
for key,p in pdfs.items():
    doc=PdfReader(p)
    txt='\n\n'.join(f'=== PDF PAGE {i+1} ===\n'+page.extract_text(extraction_mode='layout') for i,page in enumerate(doc.pages))
    (out/'sources'/f'{key}.txt').write_text(txt,encoding='utf-8')
    manifest.append(dict(key=key,path=str(p.relative_to(root)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),pages=len(doc.pages)))
(out/'SOURCES.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'paragraphs':[(x['id'],x['start'],x['end'],x['title']) for x in items],'sources':manifest},ensure_ascii=False,indent=2))
