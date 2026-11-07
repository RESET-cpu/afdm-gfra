from pathlib import Path
import hashlib,json,re,shutil
RUN=Path(__file__).resolve().parent
PAPER=RUN.parents[1]
ROOT=PAPER.parents[1]
main=(PAPER/'main.tex').read_text(encoding='utf-8')
active=re.findall(r'^\\input\{([^}]+)\}',main,re.M)
files=['main.tex','references.bib','README.md','docs/TERMINOLOGY.md','sections/00_abstract_zh.md']+[p+'.tex' for p in active]
files += [p.relative_to(PAPER).as_posix() for p in (PAPER/'figures').glob('*.pdf')]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
record={'active_inputs':active,'files':{},'pdf_before_sha256':sha(PAPER/'main.pdf'),'pages_before':15,
        'authorization':'Compress repeated prose toward about 12 pages; retain core mathematics, figures, key numbers, and evaluation limitations. No font or figure shrinking.',
        'protected':{str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in [ROOT/'FINAL.json',ROOT/'MAINLINE.json']}}
for rel in files:
 p=PAPER/rel;out=RUN/'before'/rel
 assert not out.exists(),out
 out.parent.mkdir(exist_ok=True,parents=True)
 shutil.copy2(p,out)
 record['files'][rel]=sha(p)
(RUN/'BASELINE.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Snapshot:',len(files),'files; no full-PDF duplicate created.')
