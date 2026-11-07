from pathlib import Path
import shutil, json, hashlib, re, urllib.request, concurrent.futures

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BEFORE = HERE / 'before'
BEFORE.mkdir(exist_ok=True)
paths = [ROOT / x for x in ['main.tex', 'main_full.tex', 'main.pdf', 'main_full.pdf', 'references.bib', 'main.bbl', 'README.md', 'docs/TERMINOLOGY.md']]
paths += list((ROOT / 'sections').glob('*'))
manifest = {}
for p in paths:
    if not p.is_file(): continue
    rel = p.relative_to(ROOT)
    dest = BEFORE / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists(): shutil.copy2(p, dest)
    manifest[str(rel)] = hashlib.sha256(dest.read_bytes()).hexdigest()
(HERE/'BEFORE.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')

sources = dict(re.findall(r'@(\w+)\{([^,]+),', '')) if False else {}
for block in re.split(r'(?=^@)', (ROOT/'references.bib').read_text(encoding='utf-8'), flags=re.M):
    key=re.search(r'^@\w+\{([^,]+),',block)
    doi=re.search(r'doi\s*=\s*\{([^}]+)',block)
    if key and doi and not doi[1].startswith('10.48550'): sources[key[1]]=doi[1]
sources.update(kodheli2021='10.1109/COMST.2020.3028247', ma2017='10.1109/LSP.2017.2651918', rangan2019='10.1109/TIT.2019.2916359', wax1985='10.1109/TASSP.1985.1164557', lin2017='10.1109/CVPR.2017.549', zhu1997='10.1145/279232.279236', TroppGilbertStrauss2006SOMP='10.1016/j.sigpro.2005.05.030', vila2013='10.1109/TSP.2013.2272287')
def fetch(kv):
    key,doi=kv
    try:
        with urllib.request.urlopen('https://api.crossref.org/works/'+doi,timeout=25) as f:
            value=json.load(f)['message']
        (HERE/'metadata'/f'{key}.json').write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf-8')
        return key, {k:value.get(k) for k in ['title','volume','issue','page','published','DOI']}
    except Exception as e: return key, {'error':str(e)}
(HERE/'metadata').mkdir(exist_ok=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    result=dict(pool.map(fetch,sources.items()))
(HERE/'metadata_summary.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
