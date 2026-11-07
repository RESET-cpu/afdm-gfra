from pathlib import Path
import hashlib,json,sys
sys.stdout.reconfigure(encoding='utf-8')
root=Path('D:/afdm-gfra')
b=root/'paper/C-STMP/checks/ch2_paragraph_review_20261102'
baseline=json.loads((b/'BASELINE.json').read_text(encoding='utf-8'))
changes=[p for p,h in baseline.items() if not (root/p).is_file() or hashlib.sha256((root/p).read_bytes()).hexdigest()!=h]
paragraphs=json.loads((b/'PARAGRAPHS.json').read_text(encoding='utf-8'))
reports=[];missing=[];errors=[]
for p in paragraphs:
    pid=p['id']; jp=b/'reports'/f'{pid}.json'; md=b/'reports'/f'{pid}.md'
    if not jp.exists() or not md.exists():missing.append(pid);continue
    try:
        r=json.loads(jp.read_text(encoding='utf-8-sig'))
        if r.get('paragraph_id')!=pid:errors.append(f'{pid}: mismatched id')
        if r.get('source_line_range')!=[p['start'],p['end']]:errors.append(f'{pid}: mismatched span')
        for key in ['overall_source_verdict','findings','strengths','recurrence','granularity','sources_read']:
            if key not in r:errors.append(f'{pid}: missing {key}')
        if not r.get('sources_read'):errors.append(f'{pid}: sources_read empty')
        reports.append({'id':pid,'title':p['title'],'lines':[p['start'],p['end']],
            'verdict':r.get('overall_source_verdict'),'findings':r.get('findings',[]),
            'md_sha256':hashlib.sha256(md.read_bytes()).hexdigest(),
            'json_sha256':hashlib.sha256(jp.read_bytes()).hexdigest()})
    except Exception as ex:errors.append(f'{pid}: {ex}')
result={'complete':not missing and not errors,'paragraph_count':len(paragraphs),'report_count':len(reports),'missing_reports':missing,'validation_errors':errors,'protected_files':len(baseline),'protected_files_changed':changes,'manuscript_unchanged':not changes,'reports':reports}
(b/'VALIDATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='reports'},ensure_ascii=False,indent=2))
