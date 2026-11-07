"""Read-only prerequisite audit and complete rescore of the two reused arms."""
import time
from pathlib import Path
import psutil
import numpy as np
from .common import *

def prerequisites():
    completion = read_json(WHITE/'COMPLETION.json')
    assert completion['status']=='PASS' and completion['inputs']==6000
    assert read_json(WHITE/'STATUS.json')['stage']=='COMPLETE'
    assert read_json(WHITE/'SUMMARY.json')['status']=='VERIFIED'
    checked(WHITE/'SUMMARY.json',completion['summary_sha256'])
    checked(WHITE/'PAIRED_CASES.csv',completion['paired_sha256'])
    checked(WHITE/'PLAN.json',read_json(WHITE/'PLAN_HASH.json')['sha256'])
    for key in ('saved_arrays_rescored','input_and_output_hashes_verified','inference_workers_exited'):
        assert completion[key]
    source = ROOT/'result/snr_comparison/data/convergence_50x300_20261105'
    figure = ROOT/'result/snr_comparison/figures/convergence_first30_300_20261105'
    validation, plot = read_json(figure/'VALIDATION.json'),read_json(figure/'PLOT_DATA.json')
    assert validation['status']=='PASS' and validation['complete_cases']==90
    assert validation['actual_iterations_per_case']==300 and validation['displayed_iterations']==150
    checked(source/'PLAN.json',plot['plan_sha256'])
    assert plot['scene_ids']==list(range(30)) and len(plot['result_sha256'])==90
    from evaluation.convergence_20261105.run import load_case
    from evaluation.convergence_20261105.metrics import aggregate as trace_aggregate
    plan = read_json(source/'PLAN.json'); paired={}
    assert plan['snr_db']==0
    for path,h in plot['result_sha256'].items(): checked(source/path,h)
    for method in ('STMP','GP-MP','Off-grid SBL (7)'):
        traces={s:load_case(source,plan,method,s) for s in range(30)}
        for s,t in traces.items():
            if s in paired:
                np.testing.assert_array_equal(t['truth_activity'],paired[s]['truth_activity'])
                np.testing.assert_equal(t['signal_energy'],paired[s]['signal_energy'])
            paired[s]=t
        curves=trace_aggregate(traces,list(range(30)),300)
        for key in ('iteration','nmse_db','aer'):
            np.testing.assert_allclose(curves[key],plot['curves'][method][key],rtol=1e-12,atol=1e-12)
    live=[]
    for p in psutil.process_iter(['pid','name','cmdline','create_time']):
        cmd=' '.join(p.info['cmdline'] or [])
        if 'python' in (p.info['name'] or '').lower() and any(s in cmd for s in
                ('white_matched','convergence_20261105','convergence_50x300')):
            live.append(p.info)
    assert not live, live
    return dict(status='PASS',checked_unix=time.time(),white_completed=6000,
                adopted_convergence_results=90,adopted_scenes=30,actual_iterations=300,
                displayed_iterations=150,prior_computations_exited=True,
                hashes={str(p):sha256(p) for p in [WHITE/'COMPLETION.json',WHITE/'SUMMARY.json',
                        WHITE/'PLAN.json',figure/'VALIDATION.json',figure/'PLOT_DATA.json']})

def prepare():
    audit=prerequisites()
    OUT.mkdir(parents=True,exist_ok=True)
    if (OUT/'PLAN.json').exists():
        raise RuntimeError('Existing plan retained; use verify/resume, never replace it')
    cases=read_json(WHITE/'INPUTS.json')[:3000]
    whiteplan=read_json(WHITE/'PLAN.json'); mainplan=read_json(MAIN)
    stmp=mainplan['algorithm_specs']['STMP']['kwargs']['configuration']
    configs={'STMP-Gaussian':stmp,'GP-MP-Gaussian':whiteplan['receiver_configuration']}
    # Historical precision evidence is bound to each cached prediction identity.
    assert mainplan['tf32'] is False
    essential=('src/algorithm/STMP/','src/networks/','src/system/receiver/noise_estimation.py','src/evaluation/receivers.py')
    historical={}
    for p,h in mainplan['assets'].items():
        rel=Path(p).relative_to(ROOT).as_posix()
        if rel.startswith(essential): checked(p,h);historical[p]=h
    assert historical
    reuse=[]; rows={'STMP-LR':[],'GP-MP-LR':[]}; input_hashes={}
    for i,case in enumerate(cases):
        assert (case['scene'],case['index'],case['snr_db'])==(i//6,i%6,SNRS[i%6])
        folder=Path(case['ready']).parent
        for path,h in [(Path(case['ready']),case['ready_sha256'])]+[(folder/n,h) for n,h in case['files'].items()]:
            if str(path) not in input_hashes: checked(path,h);input_hashes[str(path)]=h
        truth=arrays(folder/'truth.npz'); public=arrays(folder/'public.npz')
        stem=Path(case['STMP_result']); checked(stem,case['STMP_sha256'])
        old=read_json(stem); recordpath=stem.with_suffix('.record.json'); record=read_json(recordpath)
        assert old['status']=='COMPLETE' and old['rescoring']=='PASSED'
        identity=old['identity']; assert identity['input']==case['files'] and identity['method']=='STMP'
        assert identity['device']=='cuda' and identity['phase_mode']=='known' and identity['noise_mode']=='estimated'
        expected=dict(stmp,device='cuda',activity_prior=float(public['rho']))
        assert record['configuration']==expected
        assert record['classifier_loaded'] and record['activity_evidence']=='classifier'
        assert not record['truth_loaded'] and not record['noise_truth_used'] and record['oracle_phase_supplied']
        assert record['iterations']==old['iterations'] and record['stopping_reason']==old['stopping_reason']
        predpath=stem.with_suffix('.prediction.npz') if old['full_prediction_retained'] else None
        if predpath: checked(predpath,old['prediction_sha256'])
        compactpath=stem.with_suffix('.npz');checked(compactpath,old['compact_sha256'])
        ref=dict(result=str(stem),record=str(recordpath),prediction=str(predpath) if predpath else None,
                 compact=str(compactpath),files={str(p):sha256(p) for p in (stem,recordpath,predpath,compactpath) if p},
                 runtime_identity=identity['runtime'],channel_rescoring='full_prediction' if predpath else 'retained_per_user_error')
        old['metrics']=reuse_metrics(ref,truth,old['metrics'])
        old.update(scene=i//6,index=i%6,snr_db=SNRS[i%6],converged=record['converged'])
        rows['STMP-LR'].append(old)
        entry={'STMP-LR':ref}
        pointer=WHITE/'results'/(tag(i)+'.json'); link=read_json(pointer)
        checked(link['result'],link['sha256']); dest=Path(link['result']).parent
        row=read_json(link['result']); rec=read_json(dest/'record.json')
        assert row['status']=='COMPLETE' and row['preflight'] is False and row['input_files']==case['files']
        assert (row['scene'],row['index'],row['snr_db'])==(i//6,i%6,SNRS[i%6])
        assert row['plan_sha256']==sha256(WHITE/'PLAN.json')
        assert all(row['environment'][k] is False for k in ('tf32','cudnn_tf32','cudnn_benchmark'))
        assert rec['configuration']==configs['GP-MP-Gaussian']
        assert not rec['receiver_truth_used'] and not rec['noise_truth_used'] and rec['oracle_phase_supplied']
        assert row['iterations']==rec['iterations'] and row['converged']==rec['converged']
        for p,h in row['files'].items(): checked(p,h)
        row['metrics']=prediction_check(arrays(dest/'prediction.npz'),truth,row['metrics'])
        rows['GP-MP-LR'].append(row)
        entry['GP-MP-LR']=dict(result=link['result'],record=str(dest/'record.json'),prediction=str(dest/'prediction.npz'),
                              files={**row['files'],link['result']:link['sha256'],str(pointer):sha256(pointer)})
        reuse.append(entry)
        if (i+1)%100==0:
            write_json(OUT/'PREPARE_STATUS.json',dict(stage='AUDITING_REUSE',paired_inputs=i+1,planned=3000))
            print('Verified reuse pairs',i+1,flush=True)
    write_json(OUT/'PREREQUISITES.json',audit)
    write_json(OUT/'INPUTS.json',cases);write_json(OUT/'REUSE.json',reuse)
    write_json(OUT/'REUSE_AUDIT.json',dict(status='PASS',paired_inputs=3000,reused_inferences=6000,
        configurations_checked=True,all_activity_predictions_rescored=True,input_hashes=input_hashes,
        stmp_channel_full_predictions=sum(bool(r['STMP-LR']['prediction']) for r in reuse),
        stmp_channel_compact_error_statistics=sum(not bool(r['STMP-LR']['prediction']) for r in reuse),
        precision=dict(networks='FP32',tf32=False,cudnn_tf32=False,
            historical_source_hashes=historical,runtime_identities=sorted({r['STMP-LR']['runtime_identity'] for r in reuse})),
        methods={m:{str(s):aggregate([r for r in values if r['snr_db']==s]) for s in SNRS} for m,values in rows.items()}))
    assets={str(OUT/n):sha256(OUT/n) for n in ('INPUTS.json','REUSE.json','REUSE_AUDIT.json','PREREQUISITES.json')}
    for c in configs.values():
        for k,v in c.items():
            if k.endswith('_sha256') and isinstance(v,str) and k[:-7] in c:
                p=ROOT/c[k[:-7]];checked(p,v);assets[str(p)]=v
    for d in ('src/algorithm/STMP','src/algorithm/C_STMP','src/algorithm/C_STMP_variance_em_20261025',
              'src/algorithm/C_STMP_ablation_20261028','src/algorithm/C_STMP_retrained','src/networks',
              'src/system','src/utils','src/evaluation/activity_evidence_500_20261105',
              'src/evaluation/STMP_ablation','src/evaluation/white_matched_20261105',
              'src/evaluation/white_matched_fp32_20261105'):
        for p in (ROOT/d).rglob('*.py'): assets[str(p)]=sha256(p)
    for n in ('src/evaluation/storage.py','src/evaluation/metrics.py','src/project.py','src/utils.py'):
        p=ROOT/n;assets[str(p)]=sha256(p)
    plan=dict(schema='paired-activity-evidence-v1',created_unix=time.time(),scenes=list(range(500)),snrs=SNRS,
        configurations=configs,planned_new=6000,planned_reused=6000,
        native_directory='E:\\afdm-gfra-results\\activity_evidence_500_20261105',assets=assets,
        runtime=dict(max_workers=2,threads_per_worker=2,worker_peak_budget_gib=3.0,minimum_free_ram_gib=1.5,
            gpu_budget_gib_per_worker=6.,minimum_free_gpu_gib=1.,input_timeout_seconds=7200,total_timeout_seconds=1209600),
        only_changed_quantity='Activity evidence within each corresponding receiver',
        original_stmp_scope='Score-pair/Gaussian-site activity design adapted to the same AFDM model; not a full reproduction of the original physical system.',
        phase_mode='known',noise_mode='estimated',network_dtype='float32',matmul_tf32=False,cudnn_tf32=False,
        limitations=['Previously used research scenes, not an untouched test set.','Concurrent times are not isolated latency measurements.',
            'Historical STMP retains full channel predictions only for scene 0. Other NMSE values are reaggregated from hash-verified per-user errors, originally rescored before full-array deletion. All activity predictions are retained and rescored.'],
        finite_iteration_limit_outputs_retained=True,mainline_changed=False)
    native=Path(plan['native_directory'])
    assert not native.exists() or not any(native.iterdir()), 'Existing native data must be inspected'
    native.mkdir(parents=True,exist_ok=True)
    for n in ('results','launches','logs'): (OUT/n).mkdir(exist_ok=True)
    write_json(OUT/'PLAN.json',plan);write_json(OUT/'PLAN_HASH.json',dict(sha256=sha256(OUT/'PLAN.json')))
    write_json(OUT/'PREPARE_STATUS.json',dict(stage='VERIFIED',paired_inputs=3000,planned=3000))
    print('PREPARED',flush=True)

if __name__=='__main__': prepare()
