from pathlib import Path
import shutil,json,hashlib,urllib.request,time
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BEFORE=HERE/'before'
BEFORE.mkdir(exist_ok=True)
paths=[ROOT/n for n in ['main.tex','main_full.tex','main.pdf','main_full.pdf','references.bib','main.bbl','README.md','docs/TERMINOLOGY.md']]+list((ROOT/'sections').glob('*'))
manifest={}
for p in paths:
    if not p.is_file():continue
    rel=p.relative_to(ROOT); dest=BEFORE/rel
    dest.parent.mkdir(exist_ok=True,parents=True)
    if not dest.exists():shutil.copy2(p,dest)
    manifest[str(rel)]=hashlib.sha256(dest.read_bytes()).hexdigest()
(HERE/'BEFORE.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
(HERE/'metadata').mkdir(exist_ok=True)
dois={'dytso2023':'10.1109/TIT.2022.3216012','metzler2016':'10.1109/TIT.2016.2556683','shastri2022':'10.1109/JSAIT.2022.3207109','zou2021otfs':'10.1109/ICCWorkshops50388.2021.9473771'}
for key,doi in dois.items():
    try:
        with urllib.request.urlopen(urllib.request.Request('https://api.crossref.org/works/'+doi,headers={'User-Agent':'ManuscriptMetadataCheck/1.0'}),timeout=25) as f:
            m=json.load(f)['message']
        (HERE/'metadata'/f'{key}.json').write_text(json.dumps(m,indent=2,ensure_ascii=False),encoding='utf-8')
        print(key,json.dumps({k:m.get(k) for k in ['title','author','volume','issue','page','published','DOI']},ensure_ascii=False))
    except Exception as e: print(key,str(e))
    time.sleep(1)

library=ROOT.parents[1]/'reference/literature'
pdfs={'dytso2023_conditional_mean_published.pdf':'https://par.nsf.gov/servlets/purl/10444847','shastri2022_dgec_published.pdf':'https://phil-schniter.web.app/pdf/jsait22_dgec.pdf'}
download={}
for name,url in pdfs.items():
    try:
        dest=library/name
        if not dest.exists():
            with urllib.request.urlopen(url,timeout=35) as f:data=f.read()
            assert data[:4]==b'%PDF',data[:80]
            dest.write_bytes(data)
        download[name]={'source':url,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()}
        print('PDF',name,dest.stat().st_size)
    except Exception as e:download[name]={'source':url,'error':str(e)};print('PDF ERROR',name,str(e))
(HERE/'SOURCES.json').write_text(json.dumps(download,indent=2),encoding='utf-8')
