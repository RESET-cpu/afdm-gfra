"""Archive public primary sources for the GFRA baseline audit; no experiments."""
import sys, json, hashlib, urllib.request
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from pypdf import PdfReader

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parent
SOURCES = [
 ('tropp2005_somp','https://tropp.caltech.edu/papers/TGS05-Algorithms-Simultaneous-I-preprint.pdf'),
 ('zhou2023_somp_gfra','https://arxiv.org/pdf/2201.02084v2'),
 ('ke2020_gmmv_amp','https://arxiv.org/pdf/1906.09867v4'),
 ('zhang2019_mp_bsbl','https://arxiv.org/pdf/1910.02953v1'),
 ('wei2022_offgrid_sbl','https://arxiv.org/pdf/2101.05629v1'),
 ('shen2022_dl_gamp','https://arxiv.org/pdf/2208.01828v1'),
 ('shen2025_mrf_mp_gamp','https://arxiv.org/pdf/2412.20806v1'),
 ('ge2026_ss_ep','https://arxiv.org/pdf/2608.03896v1'),
 ('alshoukairi2018_gamp_sbl','https://phil-schniter.web.app/pdf/tsp18_sbl.pdf'),
 ('marata2025_clmp','https://aaltodoc.aalto.fi/bitstreams/53a36764-729e-41cc-ba08-0c5dbef21bc9/download'),
]

def fetch(item):
    key,url = item
    p=ROOT/(key+'.pdf')
    try:
        if not p.exists():
            request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (academic literature audit)'})
            with urllib.request.urlopen(request,timeout=40) as r: data=r.read()
            if not data.startswith(b'%PDF'): raise ValueError('Response is not PDF')
            p.write_bytes(data)
        reader=PdfReader(p)
        text='\n\n'.join(f'=== PDF PAGE {i+1} ===\n'+(page.extract_text() or '') for i,page in enumerate(reader.pages))
        p.with_suffix('.txt').write_text(text,encoding='utf-8')
        result=dict(id=key,url=url,path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),pages=len(reader.pages),status='FETCHED_NOT_AUTOMATICALLY_VERIFIED')
    except Exception as error:
        result=dict(id=key,url=url,status='UNAVAILABLE',error=str(error))
    print(json.dumps(result,ensure_ascii=False),flush=True)
    return result

with ThreadPoolExecutor(max_workers=3) as pool: rows=list(pool.map(fetch,SOURCES))
for name in ['ding2026','shen2025']:
    p=ROOT.parent/'literature'/f'{name}.pdf'
    if p.exists():
        reader=PdfReader(p)
        (ROOT/(name+'_local.txt')).write_text('\n\n'.join(f'=== PDF PAGE {i+1} ===\n'+(page.extract_text() or '') for i,page in enumerate(reader.pages)),encoding='utf-8')
        rows.append(dict(id=name+'_local',path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),pages=len(reader.pages),status='EXISTING_PRIMARY_PDF'))
(ROOT/'FETCH_MANIFEST.json').write_text(json.dumps(dict(created_utc=datetime.now(timezone.utc).isoformat(),sources=rows),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
