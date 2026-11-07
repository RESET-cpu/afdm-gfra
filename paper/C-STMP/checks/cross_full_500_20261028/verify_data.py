"""Read-only verification of completed cross-channel assets and pooled metrics."""
from pathlib import Path
import json, csv, hashlib, math, time, collections, concurrent.futures
import psutil
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
B=ROOT/'result/cross_channel/data/stmp_c_stmp_500_20261026'
R=ROOT/'result/receiver_sweeps_500_20261026/resume_after_user_count_20261027'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()
def check(item):
    p,h=item
    try: return None if sha(p)==h else {'path':p,'reason':'hash mismatch'}
    except Exception as e: return {'path':p,'reason':str(e)}
if __name__=='__main__':
    complete=read(B/'COMPLETE.json'); audit=read(B/'AUDIT.json'); summary=read(B/'SUMMARY.json')
    assert complete['status']=='COMPLETE' and audit['status']=='PASS'
    identities=[]
    for p in [R/'START.json',*sorted((B/'worker_identity').glob('*.json'))]:
        d=read(p); pid=d['pid']; live=None
        try:
            proc=psutil.Process(pid)
            live={'pid':pid,'create_time':proc.create_time(),'cmdline':proc.cmdline(),'parent_pid':proc.ppid()}
        except psutil.NoSuchProcess: pass
        same=live is not None and abs(live['create_time']-d['create_time'])<.05
        assert not same, (p,live)
        identities.append({'source':str(p),'recorded':d,'same_process_alive':same,'current_pid_owner':live})
    assets=dict(audit['files']); assets.update(complete['files'])
    failures=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for n,result in enumerate(pool.map(check,assets.items()),1):
            if result: failures.append(result)
            if n%25000==0: print('asset hashes',n,'/',len(assets),flush=True)
    groups=collections.defaultdict(list)
    with (B/'per_scene.csv').open(newline='',encoding='utf-8-sig') as f:
        for row in csv.DictReader(f): groups[(row['method'],row['channel_model'],float(row['snr_db']))].append(row)
    assert len(groups)==144
    for row in summary['rows']:
        g=groups[(row['method'],row['channel_model'],float(row['snr_db']))]
        assert len(g)==500 and sorted(int(x['scene']) for x in g)==list(range(500))
        sums={k:math.fsum(float(x[k]) for x in g) for k in ['full_error','signal_energy','misses','false_alarms','active','inactive']}
        nmse=10*math.log10(sums['full_error']/sums['signal_energy'])
        aer=(sums['misses']+sums['false_alarms'])/(sums['active']+sums['inactive'])
        assert abs(nmse-row['nmse_db'])<1e-10 and abs(aer-row['aer'])<1e-12
        if row['method'] in ('STMP','C_STMP'): assert all(x['stopping_reason']=='CONVERGED' for x in g)
    receipt={'status':'PASS' if not failures else 'FAIL','created_unix':time.time(),'audit_asset_count':len(audit['files']),
        'unique_assets_checked':len(assets),'failures':failures,'groups':144,'scenes_per_group':500,'method_results':72000,
        'learning_outputs':24000,'learning_nonconverged':0,'pooled_metrics_recomputed':True,'process_exit':identities,
        'complete_sha256':sha(B/'COMPLETE.json'),'audit_sha256':sha(B/'AUDIT.json'),'summary_sha256':sha(B/'SUMMARY.json'),
        'disk_free_GiB':{drive:psutil.disk_usage(drive).free/2**30 for drive in ['D:/','E:/']}}
    (HERE/'DATA_VALIDATION.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in receipt.items() if k!='process_exit'},indent=2),flush=True)
    assert not failures
