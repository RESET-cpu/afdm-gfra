"""CPU-only audit of frozen paired results; does not rerun or tune receivers."""
import csv
import hashlib
import json
import math
from pathlib import Path
import time

import numpy as np

ROOT=Path(r'C:\Users\25911\Desktop\afdm-gfra')
OUT=ROOT/'results/lstmp_vs_legacy20_repaired_20261019'
METHODS=['new_five_layer','legacy_50000_damping01']


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(2**20),b''):
            h.update(block)
    return h.hexdigest()


def close(a,b):
    assert np.isclose(a,b,rtol=1e-10,atol=1e-12),(a,b)


def main():
    complete=read(OUT/'COMPLETE.json');plan=read(OUT/'PLAN.json');report=read(OUT/'SUMMARY.json')
    binding=read(OUT/'BINDING.json');run=Path(plan['training_run'])
    assert not (OUT/'RUNNING.lock').exists() and not (OUT/'FAILURE.json').exists()
    assert complete['scene_counts']==dict.fromkeys(METHODS,20)
    assert sha(OUT/'PLAN.json')==complete['plan_sha256']==binding['plan_sha256']
    assert sha(OUT/'SUMMARY.json')==complete['summary_sha256']
    assert sha(run/'COMPLETE.json')==binding['training_complete_sha256']
    assert sha(run/plan['new_checkpoint'])==binding['selected_checkpoint_sha256']
    assert sha(run/'MANIFEST.json')==plan['training_manifest_sha256']
    assert sha(OUT/'source/evaluate_lstmp_vs_legacy20.py')==plan['evaluator_sha256']
    manifest=read(run/'MANIFEST.json')
    for p,digest in manifest['snapshot_hashes'].items():assert sha(p)==digest
    for p,digest in manifest['protected_assets'].items():assert sha(ROOT/p)==digest
    for depth,epochs in enumerate([2,2,2,2,4],1):
        q=run/f'checkpoints/depth_{depth}';c=read(q/'COMPLETE.json')
        assert c['status']=='COMPLETE' and c['steps']==4800*epochs
        assert c['checkpoint_sha256']==sha(q/'best.pt')
    for folder,case in [(OUT/'cases'/f'{c["index"]:03d}',c) for c in plan['cases']]+[(OUT/'warmup',plan['warmup'])]:
        for name in ['input','truth']:assert sha(folder/f'{name}.npz')==case[f'{name}_sha256']
        assert sha(folder/'generation.json')==case['generation_sha256']
    with (OUT/'per_scene.csv').open(encoding='utf-8-sig',newline='') as f:csv_rows=list(csv.DictReader(f))
    with (OUT/'summary.csv').open(encoding='utf-8-sig',newline='') as f:csv_summary=list(csv.DictReader(f))
    assert len(csv_rows)==40 and len(csv_summary)==2
    paired={}
    for method in METHODS:
        rows=[read(OUT/method/f'{i:03d}.json') for i in range(20)]
        assert len(list((OUT/method).glob('[0-9][0-9][0-9].json')))==20
        for row,case in zip(rows,plan['cases']):
            i=case['index'];folder=OUT/method
            assert row['status']=='COMPLETE' and row['case_index']==i and row['seed']==case['seed']
            assert row['input_sha256']==case['input_sha256']
            assert row['prediction_sha256']==sha(folder/f'{i:03d}.npz')
            trace=read(folder/f'{i:03d}_trace.json')
            if method=='new_five_layer':
                assert row['iterations']==5 and row['converged'] is None
                assert len(trace['diagnostics'])==5
            else:
                assert trace['checkpoint_sha256']==plan['old_binding']['checkpoint_sha256']
                # The receiver records the device and public per-scene prior at runtime.
                # Check these too rather than comparing a runtime record to a template.
                with np.load(OUT/'cases'/f'{i:03d}'/'input.npz') as public:
                    expected_config=dict(plan['old_binding']['applied_configuration'],
                        device=plan['device'],activity_prior=float(public['activity_prior']))
                assert trace['configuration']==expected_config
                assert row['iterations']<=600 and len(trace['trace'])==row['iterations']
            with np.load(folder/f'{i:03d}.npz') as z:estimate=z['estimate'];probability=z['probabilities']
            with np.load(OUT/'cases'/f'{i:03d}'/'truth.npz') as z:truth=z['channel'];active=z['activity'].astype(bool)
            assert np.isfinite(estimate).all() and np.isfinite(probability).all()
            assert np.all((probability>=0)&(probability<=1))
            err=float(np.sum(np.abs(estimate.astype(np.complex128)-truth)**2))
            energy=float(np.sum(np.abs(truth)**2))
            close(err,row['error_energy']);close(energy,row['truth_energy']);close(err/energy,row['nmse'])
            assert row['misses']==int(np.sum(active&(probability<.5)))
            assert row['false_alarms']==int(np.sum(~active&(probability>=.5)))
            close(row['preparation_seconds']+row['inference_seconds'],row['total_seconds'])
            cr=next(x for x in csv_rows if x['method']==method and int(x['case_index'])==i)
            for key,value in row.items():
                if isinstance(value,(int,float)) and not isinstance(value,bool):close(float(cr[key]),value)
                elif value is not None:assert cr[key]==str(value),(key,cr[key],value)
        s=report['methods'][method];cs=next(x for x in csv_summary if x['method']==method)
        for key,value in s.items():
            if isinstance(value,(int,float)):close(float(cs[key]),value)
        close(s['pooled_nmse_db'],10*math.log10(sum(x['error_energy'] for x in rows)/sum(x['truth_energy'] for x in rows)))
        close(s['mean_scene_nmse_db'],10*math.log10(np.mean([x['nmse'] for x in rows])))
        close(s['aer'],sum(x['misses']+x['false_alarms'] for x in rows)/800)
        close(s['mean_seconds'],np.mean([x['total_seconds'] for x in rows]))
        close(s['median_seconds'],np.median([x['total_seconds'] for x in rows]))
        assert s['iteration_limit_scenes']==sum(x['stopping_reason']=='MAX_ITERATIONS' for x in rows)
        paired[method]=rows
    close(report['speedup_legacy_over_new'],report['methods'][METHODS[1]]['mean_seconds']/report['methods'][METHODS[0]]['mean_seconds'])
    # Paired resampling at the independent-scene level, for descriptive uncertainty.
    indices=np.random.default_rng(20261020).integers(0,20,size=(10000,20))
    boot={}
    for method,rows in paired.items():
        e=np.array([r['error_energy'] for r in rows]);t=np.array([r['truth_energy'] for r in rows])
        errors=np.array([r['misses']+r['false_alarms'] for r in rows])
        boot[method]=dict(nmse_db=10*np.log10(e[indices].sum(1)/t[indices].sum(1)),aer=errors[indices].sum(1)/800)
    delta={metric:np.quantile(boot[METHODS[0]][metric]-boot[METHODS[1]][metric],[.025,.975]).tolist() for metric in ['nmse_db','aer']}
    result=dict(status='PASSED',checked_unix=time.time(),checks=['both methods 20/20; all cases retained',
        'frozen inputs, truth, generation, source and weights match their hashes',
        'five training-stage budgets complete','saved predictions reproduce per-scene errors and decisions',
        'CSV and SUMMARY agree; timing and iteration caps checked'],
        paired_bootstrap_new_minus_legacy_95_percentile=delta,bootstrap_resamples=10000,bootstrap_seed=20261020,
        uncertainty_note='Resample the 20 paired scenes, not individual users. Descriptive interval for this single condition; cannot establish a zero population error rate.',
        plan_sha256=sha(OUT/'PLAN.json'),summary_sha256=sha(OUT/'SUMMARY.json'),
        per_scene_csv_sha256=sha(OUT/'per_scene.csv'))
    (OUT/'RESULT_AUDIT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()
