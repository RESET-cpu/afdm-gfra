"""Rescore all 12000 saved predictions; retain every finite capped result."""
import csv
import time
from .common import *

def summarize():
    plan=verify();cases=read_json(OUT/'INPUTS.json');reuse=read_json(OUT/'REUSE.json')
    rows={m:[] for m in (*METHODS,'STMP-LR','GP-MP-LR')};pairs=[]
    expected={m+'_'+tag(i)+'.json' for m in METHODS for i in range(3000)}
    assert {p.name for p in (OUT/'results').glob('*.json')}==expected
    for i,case in enumerate(cases):
        folder=Path(case['ready']).parent
        checked(case['ready'],case['ready_sha256'])
        for n,h in case['files'].items(): checked(folder/n,h)
        truth=arrays(folder/'truth.npz')
        for m in rows:
            if m in METHODS:
                pointer=read_json(OUT/'results'/(m+'_'+tag(i)+'.json'))
                checked(pointer['result'],pointer['sha256'])
                assert Path(pointer['result'])==Path(plan['native_directory'])/m/tag(i)/'RESULT.json'
                row=check_new(m,i,plan)
            else:
                ref=reuse[i][m]
                for p,h in ref['files'].items(): checked(p,h)
                row=read_json(ref['result']);record=read_json(ref['record'])
                row['metrics']=reuse_metrics(ref,truth,row['metrics'])
                row.update(scene=case['scene'],index=case['index'],snr_db=case['snr_db'],converged=record['converged'])
            rows[m].append(row)
            pairs.append(dict(method=m,scene=case['scene'],snr_db=case['snr_db'],
                misses=row['metrics']['misses'],false_alarms=row['metrics']['false_alarms'],
                active=row['metrics']['active'],inactive=row['metrics']['inactive'],
                full_error=row['metrics']['full_error'],signal_energy=row['metrics']['signal_energy'],
                nmse_db=row['metrics']['nmse_db'],iterations=row['iterations'],converged=row['converged']))
        if (i+1)%100==0: write_json(OUT/'VERIFY_PROGRESS.json',dict(checked=i+1,planned=3000,updated_unix=time.time()))
    summaries={}
    for method,values in rows.items():
        summaries[method]={}
        for snr in SNRS:
            v=aggregate([r for r in values if r['snr_db']==snr])
            assert v['inputs']==500 and v['decisions']==20000
            v.update(miss_rate=v['misses']/v['active'],false_alarm_rate=v['false_alarms']/v['inactive'],
                     converged=v['inputs']-v['nonconverged'])
            summaries[method][str(snr)]=v
    with (OUT/'PAIRED_CASES.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(pairs[0]));w.writeheader();w.writerows(pairs)
    write_json(OUT/'SUMMARY.json',dict(status='VERIFIED',methods=summaries,plan_sha256=sha256(OUT/'PLAN.json'),
        new_inferences=6000,reused_inferences=6000,paired_scenes_per_snr=500,limitations=plan['limitations']))
    lines=['# 500-scene paired activity evidence comparison','',
           'Known phase; observation-estimated noise; white-trained networks. Original STMP is an AFDM adaptation.',
           '', '| SNR (dB) | STMP Gaussian | STMP density ratio | GP-MP Gaussian | GP-MP density ratio |',
           '|---:|---:|---:|---:|---:|']
    for s in SNRS:
        lines.append('| '+str(s)+' | '+' | '.join(f"{summaries[m][str(s)]['aer']:.6f}" for m in
            ('STMP-Gaussian','STMP-LR','GP-MP-Gaussian','GP-MP-LR'))+' |')
    lines+=['','Full miss/false-alarm counts, NMSE and iteration-limit counts are in SUMMARY.json.',
            'All finite iteration-limit outputs are retained. Manuscript synchronization is a separate final step.']
    (OUT/'AER_TABLE.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    verify()
    write_json(OUT/'COMPLETION.json',dict(status='PASS',completed_unix=time.time(),new_inferences=6000,reused_inferences=6000,
        all_activity_predictions_rescored=True,new_channel_predictions_rescored=True,
        historical_stmp_nmse_evidence='Full predictions for scene 0, retained per-user errors for other scenes; see REUSE_AUDIT.json',
        paired_coverage_verified=True,all_finite_iteration_limit_outputs_retained=True,
        summary_sha256=sha256(OUT/'SUMMARY.json'),paired_sha256=sha256(OUT/'PAIRED_CASES.csv'),
        manuscript_updated=False,coordinator_exit_requires_live_followup=True))

if __name__=='__main__': summarize()
