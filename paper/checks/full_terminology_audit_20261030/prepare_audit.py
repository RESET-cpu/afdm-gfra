from pathlib import Path
import re, json, hashlib, sys, unicodedata
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
PAPER = ROOT / 'paper/C-STMP'
sys.path.insert(0, r'C:\Users\25911\.codex\skills\academic-research-suite\ars\scripts')
from pdf_read_preflight import run_preflight

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def strip_comments(t):
    return re.sub(r'(?<!\\)%[^\n]*', '', t)

main = strip_comments((PAPER/'main.tex').read_text(encoding='utf-8'))
inputs = re.findall(r'\\input\{([^}]+)\}', main)
paths = [PAPER/'main.tex'] + [PAPER/(x+'.tex') for x in inputs]
aux = [PAPER/'sections/00_abstract_zh.md', PAPER/'references.bib', PAPER/'main.pdf']
texts = {str(p.relative_to(ROOT)): strip_comments(p.read_text(encoding='utf-8')) for p in paths}
citations = sorted({k.strip() for t in texts.values() for group in re.findall(r'\\cite(?:\[[^\]]*\])?\{([^}]+)\}', t) for k in group.split(',')})
bibkeys = re.findall(r'@\w+\{([^,]+),', (PAPER/'references.bib').read_text(encoding='utf-8'))
pdfs = [PAPER/'main.pdf'] + sorted((PAPER/'figures').glob('*.pdf'))
(OUT/'extracted').mkdir(parents=True, exist_ok=True)
pdf_records = []
for p in pdfs:
    pre = run_preflight(p)
    pages = [page.extract_text() or '' for page in PdfReader(p).pages]
    (OUT/'extracted'/(p.stem+'.json')).write_text(json.dumps(pages, ensure_ascii=False, indent=2),encoding='utf-8')
    (OUT/'extracted'/(p.stem+'.txt')).write_text('\n\n'.join(f'[PDF page {i+1}]\n{t}' for i,t in enumerate(pages)), encoding='utf-8')
    pdf_records.append({'path':str(p.relative_to(ROOT)), 'sha256':digest(p),'preflight':pre,'pages':len(pages)})
local_sources = {
    'cai2026':'cai2026.pdf', 'ding2026':'ding2026.pdf', 'shen2025':'shen2025.pdf',
    'huang2026':'huang2026.pdf','wei2026':'wei_yuan_2026_lstmp_v1.pdf',
    'liu2018':'liu2018_massive_mimo.pdf','shastri2022':'shastri2022_dgec.pdf',
    'karras2022':'karras2022_edm.pdf','vila2013':'vila_schniter_2013.pdf',
    'TroppGilbertStrauss2006SOMP':'tropp2005_somp.pdf','WeiEtAl2022OffgridSBL':'wei2022_offgrid_sbl.pdf'
}
(OUT/'source_text').mkdir(exist_ok=True)
source_records = []
for key,name in local_sources.items():
    p = ROOT/'reference/literature'/name
    pre = run_preflight(p)
    pages = [page.extract_text() or '' for page in PdfReader(p).pages]
    (OUT/'source_text'/(key+'.json')).write_text(json.dumps(pages,ensure_ascii=False,indent=2),encoding='utf-8')
    source_records.append({'key':key,'path':str(p.relative_to(ROOT)),'sha256':digest(p),'pages':len(pages),'preflight':pre})
inventory = {'scope':'Current compiled C-STMP manuscript, Chinese abstract as auxiliary; no inactive conclusion or historical drafts',
 'files':[{ 'path':str(p.relative_to(ROOT)), 'sha256':digest(p)} for p in paths+aux],
 'active_inputs':inputs,'cited_keys':citations,'cited_count':len(citations),
 'missing_bibkeys':sorted(set(citations)-set(bibkeys)),
 'uncited_bibkeys':sorted(set(bibkeys)-set(citations)),
 'pdfs':pdf_records,'local_sources':source_records}
(OUT/'INVENTORY.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'manuscript_numbered.txt').write_text('\n\n'.join('FILE '+f+'\n'+'\n'.join(f'{i+1}: {line}' for i,line in enumerate((ROOT/f).read_text(encoding='utf-8').splitlines())) for f in texts),encoding='utf-8')
print(json.dumps({'cited_count':len(citations),'missing_bibkeys':inventory['missing_bibkeys'],'uncited_bibkeys':inventory['uncited_bibkeys'],'source_preflights':[(r['key'],r['preflight']['verdict']) for r in source_records],'pdf_pages':[(r['path'],r['pages']) for r in pdf_records]},ensure_ascii=False,indent=2))
