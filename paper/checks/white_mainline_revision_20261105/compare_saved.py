"""Read-only paired audit of a fixed completed prefix; no inference or training."""
from pathlib import Path
import csv
import datetime
import hashlib
import json
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'src'))
from evaluation.metrics import score_arrays
from evaluation.storage import arrays

OUT = Path(__file__).resolve().parent
BATCH = ROOT / 'result/snr_comparison/data/white_preconditioned_matched_fp32_1000_snr_20261105'
N = 198
SEED = 202611051541

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

hashes = {}
def audit(path, expected=None):
    path = Path(path)
    key = str(path.resolve())
    if key not in hashes:
        hashes[key] = hashlib.sha256(path.read_bytes()).hexdigest()
    if expected is not None:
        assert hashes[key] == expected, str(path)
    return hashes[key]

def check_metrics(saved, measured):
    for k in ('active','inactive','misses','false_alarms','decisions'):
        assert saved[k] == measured[k], k
    for k in ('full_error','signal_energy','active_error','inactive_error','per_user_error'):
        np.testing.assert_allclose(saved[k], measured[k], rtol=1e-11, atol=1e-12)

def agg(rows):
    total = {k:sum(r['metrics'][k] for r in rows) for k in
             ('full_error','signal_energy','active','inactive','misses','false_alarms')}
    return dict(**total, inputs=len(rows), nmse_db=float(10*np.log10(total['full_error']/total['signal_energy'])),
                aer_percent=100*(total['misses']+total['false_alarms'])/(total['active']+total['inactive']),
                converged=sum(r['converged'] for r in rows),
                mean_iterations=float(np.mean([r['iterations'] for r in rows])),
                iteration_limit=sum(r['iterations']==600 for r in rows))

def main():
    plan=read(BATCH/'PLAN.json'); plan_hash=audit(BATCH/'PLAN.json')
    cases=read(BATCH/'INPUTS.json'); refs=read(BATCH/'REFERENCES.json')
    audit(BATCH/'INPUTS.json'); audit(BATCH/'REFERENCES.json')
    base=read(ROOT/plan['receiver_configuration']['base_receiver_configuration'])
    white=[]; colored=[]; paired=[]
    for i in range(N*6):
        case,ref=cases[i],refs[i]
        assert (case['scene'],case['index']) == (i//6,i%6)
        folder=Path(case['ready']).parent
        audit(case['ready'],case['ready_sha256'])
        for name,digest in case['files'].items(): audit(folder/name,digest)
        truth=arrays(folder/'truth.npz')
        pointer=BATCH/'results'/f'scene{i//6:04d}_condition{i%6:02d}.json'
        link=read(pointer); audit(pointer); audit(link['result'],link['sha256'])
        rp=Path(link['result']); w=read(rp)
        assert w['input_files']==case['files'] and w['plan_sha256']==plan_hash
        assert w['status']=='COMPLETE' and not w['preflight']
        assert not w['channel_activity_truth_used_in_inference']
        assert all(w['environment'][k] is False for k in ('tf32','cudnn_tf32','cudnn_benchmark'))
        for path,digest in w['files'].items(): audit(path,digest)
        record=read(rp.parent/'record.json')
        assert record['configuration']==plan['receiver_configuration']
        assert not record['receiver_truth_used'] and not record['noise_truth_used']
        assert read(rp.parent/'INPUT_MANIFEST.json')['case']==case
        pred=arrays(rp.parent/'prediction.npz')
        assert all(np.isfinite(a).all() for a in pred.values())
        np.testing.assert_array_equal(pred['activity_decision'],pred['probabilities']>=.5)
        wm=score_arrays(pred,truth); check_metrics(w['metrics'],wm)
        w['metrics']=wm
        old=ref['known_phase']; audit(old['pointer'],old['pointer_sha256'])
        op=read(old['pointer'])
        assert Path(op['stem']).resolve()==Path(old['stem']).resolve()
        for mapping in (old['files'],op['files']):
            for path,digest in mapping.items(): audit(path,digest)
        stem=Path(old['stem']); c=read(stem.with_suffix('.json'))
        cr=read(stem.with_suffix('.record.json'))
        assert cr['configuration']==base and c['input_files']==case['files']
        assert (c['scene'],c['index'],c['snr_db'])==(w['scene'],w['index'],w['snr_db'])
        cp=arrays(stem.with_suffix('.npz'))
        assert all(np.isfinite(a).all() for a in cp.values())
        cm=score_arrays(cp,truth); check_metrics(c['metrics'],cm)
        c.update(metrics=cm,converged=cr['converged'])
        white.append(w); colored.append(c)
        paired.append(dict(scene=i//6,snr_db=w['snr_db'],white_error=wm['full_error'],
          colored_error=cm['full_error'],signal_energy=wm['signal_energy'],
          white_errors=wm['misses']+wm['false_alarms'],colored_errors=cm['misses']+cm['false_alarms'],
          white_iterations=w['iterations'],colored_iterations=c['iterations']))
        if (i+1)%300==0: print('AUDITED',i+1,flush=True)
    rng=np.random.default_rng(SEED)
    selections=rng.integers(N,size=(20000,N))
    comparisons=[]
    for j,snr in enumerate(plan['snrs']):
        w=white[j::6]; c=colored[j::6]; wa=agg(w); ca=agg(c)
        we=np.array([r['metrics']['full_error'] for r in w]); ce=np.array([r['metrics']['full_error'] for r in c])
        wd=np.array([r['metrics']['misses']+r['metrics']['false_alarms'] for r in w])
        cd=np.array([r['metrics']['misses']+r['metrics']['false_alarms'] for r in c])
        assert all(r['metrics']['active']+r['metrics']['inactive']==40 for r in w+c)
        nm=10*np.log10(we[selections].sum(1)/ce[selections].sum(1))
        ad=(wd-cd)[selections].sum(1)/(N*40)*100
        comparisons.append(dict(snr_db=snr,white=wa,colored=ca,
          delta_nmse_db_white_minus_colored=wa['nmse_db']-ca['nmse_db'],
          delta_nmse_db_95pct_percentile_ci=np.quantile(nm,[.025,.975]).tolist(),
          delta_aer_percentage_points=wa['aer_percent']-ca['aer_percent'],
          delta_aer_pp_95pct_percentile_ci=np.quantile(ad,[.025,.975]).tolist()))
    summary=dict(status='VERIFIED_INTERIM',created_local=datetime.datetime.now().astimezone().isoformat(),
      physical_scenes=N,scene_indices=[0,N-1],paired_inputs=N*6,planned_scenes=1000,
      snrs=plan['snrs'],comparisons=comparisons,pooled=dict(white=agg(white),colored=agg(colored)),
      verification=dict(saved_arrays_rescored=True,input_output_hashes_verified=True,
        matched_receiver_configurations=True,white_tf32_disabled=True),
      bootstrap=dict(unit='physical scene',replicates=20000,seed=SEED,interval='pointwise percentile 95%',
        caution='Not a formal equivalence test; no equivalence margin was prespecified.'),
      limitations=['Incomplete batch; fixed completed prefix, not all 1000 scenes.',
        'One trained network pair per noise-training condition; does not estimate training-seed variability.',
        'Historical research scenes; not an untouched final test set.'])
    (OUT/'PAIRED_SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (OUT/'PAIRED_HASHES.json').write_text(json.dumps(hashes,indent=2)+'\n',encoding='utf-8')
    with (OUT/'PAIRED_CASES.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(paired[0]));writer.writeheader();writer.writerows(paired)
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
