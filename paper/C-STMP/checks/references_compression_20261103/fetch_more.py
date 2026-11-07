from pathlib import Path
import urllib.request,json,time
here=Path(__file__).resolve().parent
dois={'ma2017':'10.1109/ACCESS.2017.2653119','rangan2019':'10.1109/TIT.2019.2916359','li2023':'10.1109/TWC.2023.3252895','ding2026':'10.1109/TVT.2026.3729877','ying2026':'10.1109/TWC.2025.3636585'}
for key,doi in dois.items():
    try:
        req=urllib.request.Request('https://api.crossref.org/works/'+doi,headers={'User-Agent':'ManuscriptMetadataCheck/1.0'})
        with urllib.request.urlopen(req,timeout=25) as f: m=json.load(f)['message']
        (here/'metadata'/f'{key}.json').write_text(json.dumps(m,indent=2,ensure_ascii=False),encoding='utf-8')
        print(key,json.dumps({k:m.get(k) for k in ['title','volume','issue','page','DOI']},ensure_ascii=False))
    except Exception as e: print(key,str(e))
    time.sleep(1)
