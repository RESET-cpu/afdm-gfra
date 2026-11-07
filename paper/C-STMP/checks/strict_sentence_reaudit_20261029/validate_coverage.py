from pathlib import Path
import collections
import hashlib
import json
import re

run = Path(__file__).parent
manifest = json.loads((run/'manifest.json').read_text(encoding='utf-8'))
def norm(s):
    return re.sub(r'\s+', '', re.sub(r'\\label\{[^}]*\}', '', s))

rows=[]
for p in manifest['paragraphs']:
    path=run/(p['id']+'.json')
    if not path.exists():
        rows.append({'id':p['id'], 'status':'pending'})
        continue
    try:
        d=json.loads(path.read_text(encoding='utf-8-sig'))
        sentences=d['sentences']
        joined=''.join(x.get('draft_tex','') for x in sentences)
        coverage=norm(joined)==norm(p['text'])
        counts=dict(collections.Counter(s['category'] for s in sentences))
        issues=[]
        if not coverage:
            a,b=norm(joined),norm(p['text'])
            pos=next((i for i,(x,y) in enumerate(zip(a,b)) if x!=y),min(len(a),len(b)))
            issues.append({'coverage_mismatch_position':pos,'got':a[max(0,pos-50):pos+100],'expected':b[max(0,pos-50):pos+100]})
        if d.get('paragraph_id') != p['id']: issues.append('paragraph ID mismatch')
        for s in sentences:
            if s['category'] not in ['EXACT','TERM_ONLY','OTHER_CHANGE','NO_SOURCE','UNVERIFIED']: issues.append('unknown category '+s['id'])
            if s['category'] in ['EXACT','TERM_ONLY'] and not (s.get('source_quote') and s.get('source_file') and s.get('source_page')): issues.append('missing pass evidence '+s['id'])
        rows.append({'id':p['id'],'status':'complete','sentences':len(sentences),'coverage_exact':coverage,'counts':counts,'issues':issues,'sentence_level_pass':all(s['category'] in ['EXACT','TERM_ONLY'] for s in sentences),'paragraph_structure':d.get('paragraph_structure')})
    except Exception as e:
        rows.append({'id':p['id'],'status':'error','error':str(e)})
out={'manuscript_unchanged':hashlib.sha256(Path(manifest['source_file']).read_bytes()).hexdigest()==manifest['source_sha256'],'paragraphs':rows}
(run/'coverage_status.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=False,indent=2))
