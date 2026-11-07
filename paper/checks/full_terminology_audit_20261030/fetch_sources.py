from pathlib import Path
import sys, json, hashlib, concurrent.futures, urllib.request
from pypdf import PdfReader
sys.path.insert(0, r'C:\Users\25911\.codex\skills\academic-research-suite\ars\scripts')
from pdf_read_preflight import run_preflight
OUT=Path(__file__).resolve().parent
TMP=OUT/'downloaded_sources'
TMP.mkdir(exist_ok=True)
SOURCES={
'vehtari2020':'https://jmlr.org/papers/volume21/18-817/18-817.pdf',
'menon2016':'https://proceedings.mlr.press/v48/menon16.pdf',
'song2019':'https://arxiv.org/pdf/1907.05600',
'minka2001':'https://tminka.github.io/papers/ep/minka-ep-uai.pdf',
'dytso2021':'https://arxiv.org/pdf/2104.01883',
'efron2011':'https://efron.ckirby.su.domains/papers/2011TweediesFormula.pdf',
'vincent2011':'https://gwern.net/doc/ai/nn/diffusion/2011-vincent.pdf',
'metzler2014':'https://arxiv.org/pdf/1406.4175v2',
'ma2015':'https://lsec.cc.ac.cn/~mjj/papers/Ma2015b.pdf',
'li2023':'https://arxiv.org/pdf/2207.11958',
'arvinte2023':'https://arxiv.org/pdf/2204.07122',
'bemani2022':'https://arxiv.org/pdf/2204.12798v2',
'ying2026':'https://arxiv.org/pdf/2505.12382v3',
'oleary2013':'https://www.cs.umd.edu/users/oleary/software/varpro.pdf',
'nadakuditi2008':'https://math.mit.edu/~edelman/publications/sample_eigenvalue.pdf',
'3gpp38300':'https://www.etsi.org/deliver/etsi_ts/138300_138399/138300/17.02.00_60/ts_138300v170200p.pdf',
}
def fetch(item):
    key,url=item
    dest=TMP/(key+'.pdf')
    record={'key':key,'url':url}
    try:
        if not dest.exists():
            req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 academic terminology source check'})
            with urllib.request.urlopen(req,timeout=25) as r: data=r.read()
            if not data.startswith(b'%PDF'): raise ValueError('Not a PDF response')
            dest.write_bytes(data)
        record['preflight']=run_preflight(dest)
        pages=[page.extract_text() or '' for page in PdfReader(dest).pages]
        (OUT/'source_text'/(key+'.json')).write_text(json.dumps(pages,ensure_ascii=False,indent=2),encoding='utf-8')
        record.update(status='downloaded',pages=len(pages),sha256=hashlib.sha256(dest.read_bytes()).hexdigest())
    except Exception as exc: record.update(status='unavailable',error=str(exc))
    return record
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
    records=list(ex.map(fetch,SOURCES.items()))
(OUT/'REMOTE_SOURCES.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
for r in records: print(r['key'],r['status'],r.get('pages',''),r.get('preflight',{}).get('verdict',''),r.get('error',''))
