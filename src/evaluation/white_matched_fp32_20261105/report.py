"""Verify all saved pairs and aggregate energy NMSE and all-device AER."""
import csv
import math
from pathlib import Path
import time

import numpy as np

from utils import read_json,write_json,sha256
from evaluation.metrics import score_arrays
from evaluation.storage import arrays as load_arrays
from .run import OUT,verify,checked,tag


def aggregate(rows):
    totals = {k:sum(r['metrics'][k] for r in rows) for k in
              ('full_error','signal_energy','active_error','inactive_error','active','inactive','misses','false_alarms')}
    decisions = totals['active']+totals['inactive']
    return dict(inputs=len(rows),**totals,decisions=decisions,
                nmse_db=10*math.log10(totals['full_error']/totals['signal_energy']),
                aer=(totals['misses']+totals['false_alarms'])/decisions,
                mean_iterations=float(np.mean([r['iterations'] for r in rows])),
                nonconverged=sum(not r['converged'] for r in rows),
                iteration_limit_count=sum(r['iterations']==600 for r in rows))


def check_metrics(saved, measured):
    for k in ('active','inactive','misses','false_alarms','decisions'):
        assert saved[k] == measured[k], ('Metric mismatch',k)
    for k in ('full_error','signal_energy','active_error','inactive_error','per_user_error'):
        np.testing.assert_allclose(saved[k],measured[k],rtol=1e-11,atol=1e-12)


def summarize():
    plan=verify()
    cases,refs=read_json(OUT/'INPUTS.json'),read_json(OUT/'REFERENCES.json')
    expected={tag(i)+'.json' for i in range(6000)}
    assert {p.name for p in (OUT/'results').glob('*.json')} == expected
    rows={'GP-MP':[], 'CGP-MP':[]}; pairs=[]; hashes={}
    def audit(path,digest):
        checked(path,digest); hashes[str(path)]=digest
    for i,(case,ref) in enumerate(zip(cases,refs)):
        assert (case['scene'],case['index']) == (i//6,i%6)
        folder=Path(case['ready']).parent
        audit(case['ready'],case['ready_sha256'])
        for name,digest in case['files'].items(): audit(folder/name,digest)
        truth=load_arrays(folder/'truth.npz')
        pointerpath=OUT/'results'/(tag(i)+'.json')
        link=read_json(pointerpath); audit(pointerpath,sha256(pointerpath)); audit(link['result'],link['sha256'])
        resultpath=Path(link['result'])
        assert resultpath.parent.parent.resolve() == Path(plan['native_directory']).resolve()
        row=read_json(resultpath)
        assert row['environment']['tf32'] is False and row['environment']['cudnn_tf32'] is False
        assert row['environment']['cudnn_benchmark'] is False
        assert row['status']=='COMPLETE' and not row['preflight'] and row['input_files']==case['files']
        assert (row['scene'],row['index'],row['snr_db']) == (case['scene'],case['index'],case['snr_db'])
        assert row['plan_sha256']==sha256(OUT/'PLAN.json') and not row['channel_activity_truth_used_in_inference']
        for path,digest in row['files'].items(): audit(path,digest)
        assert all(str(resultpath.parent/n) in row['files'] for n in ('prediction.npz','record.json','INPUT_MANIFEST.json'))
        assert read_json(resultpath.parent/'INPUT_MANIFEST.json')['case']==case
        record=read_json(resultpath.parent/'record.json')
        assert record['configuration']==plan['receiver_configuration'] and not record['receiver_truth_used']
        assert not record['noise_truth_used'] and record['oracle_phase_supplied']
        assert record['iterations']==row['iterations'] and record['stopping_reason']==row['stopping_reason']
        prediction=load_arrays(resultpath.parent/'prediction.npz')
        assert all(np.isfinite(a).all() for a in prediction.values())
        np.testing.assert_array_equal(prediction['activity_decision'],prediction['probabilities']>=.5)
        metrics=score_arrays(prediction,truth); check_metrics(row['metrics'],metrics)
        row['metrics']=metrics; rows['GP-MP'].append(row)
        old=ref['known_phase']; audit(old['pointer'],old['pointer_sha256'])
        oldpointer=read_json(old['pointer'])
        assert Path(oldpointer['stem']).resolve()==Path(old['stem']).resolve()
        for mapping in (old['files'],oldpointer['files']):
            for path,digest in mapping.items(): audit(path,digest)
        stem=Path(old['stem'])
        for suffix in ('.json','.record.json','.npz'):
            assert str(stem.with_suffix(suffix)) in old['files']
        reference=read_json(stem.with_suffix('.json'))
        oldrecord=read_json(stem.with_suffix('.record.json'))
        assert reference['input_files']==case['files']
        assert (reference['scene'],reference['index'],reference['snr_db']) == (case['scene'],case['index'],case['snr_db'])
        base=read_json(plan['receiver_configuration']['base_receiver_configuration'])
        assert oldrecord['configuration']==base
        oldarrays=load_arrays(stem.with_suffix('.npz'))
        assert all(np.isfinite(a).all() for a in oldarrays.values())
        oldmetrics=score_arrays(oldarrays,truth); check_metrics(reference['metrics'],oldmetrics)
        reference.update(metrics=oldmetrics,converged=oldrecord['converged'])
        rows['CGP-MP'].append(reference)
        pairs.append(dict(scene=case['scene'],index=case['index'],snr_db=case['snr_db'],
                          white_nmse_db=metrics['nmse_db'],colored_nmse_db=oldmetrics['nmse_db'],
                          delta_full_error=metrics['full_error']-oldmetrics['full_error'],
                          delta_misses=metrics['misses']-oldmetrics['misses'],
                          delta_false_alarms=metrics['false_alarms']-oldmetrics['false_alarms'],
                          white_iterations=row['iterations'],colored_iterations=reference['iterations']))
        if (i+1)%100==0:
            write_json(OUT/'VERIFY_PROGRESS.json',dict(checked=i+1,planned=6000,updated_unix=time.time()))
    summary={method:{str(snr):aggregate([r for r in values if r['snr_db']==snr]) for snr in plan['snrs']}
             for method,values in rows.items()}
    assert all(s['inputs']==1000 and s['decisions']==40000 for v in summary.values() for s in v.values())
    with (OUT/'PAIRED_CASES.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(pairs[0]));writer.writeheader();writer.writerows(pairs)
    write_json(OUT/'SUMMARY.json',dict(status='VERIFIED',methods=summary,
               comparison='Same 6000 saved inputs; white matched networks versus colored matched networks.',
               limitations=['Historical research scenes, not untouched test data.','Concurrent times are not algorithm latency benchmarks.']))
    write_json(OUT/'OUTPUT_HASHES.json',hashes)
    # Independent comparison; never replaces a manuscript figure.
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(8,3.2),layout='constrained')
    for method,style in (('GP-MP','o-'),('CGP-MP','s-')):
        for ax,key,label in zip(axes,('nmse_db','aer'),('NMSE (dB)','AER')):
            ax.plot(plan['snrs'],[summary[method][str(s)][key] for s in plan['snrs']],style,label=method)
            ax.set(xlabel='SNR (dB)',ylabel=label);ax.grid(True,alpha=.3);ax.legend()
    fig.savefig(OUT/'white_colored_comparison.pdf');fig.savefig(OUT/'white_colored_comparison.png',dpi=180);plt.close(fig)
    verify()
    write_json(OUT/'COMPLETION.json',dict(status='PASS',completed_unix=time.time(),inputs=6000,scenes=1000,
               per_snr=1000,saved_arrays_rescored=True,input_and_output_hashes_verified=True,
               all_finite_iteration_limit_outputs_retained=True,
               inference_workers_exited=True,coordinator_exit_requires_live_followup=True,
               summary_sha256=sha256(OUT/'SUMMARY.json'),paired_sha256=sha256(OUT/'PAIRED_CASES.csv')))


if __name__=='__main__':
    summarize()
