"""Summarize completed ordered diagnostics; no inference or training."""
from pathlib import Path
import numpy as np
import diagnose_cai_framework_sequence as d


def main():
    p=d.verify();P=d.P
    out=d.ROOT/'results/cai_framework_sequence_20261019';assert not out.exists()
    stages=[P.read(d.OUT/f'{name}/SUMMARY.json') for name in ('stage1_gaussian','stage2_activity','stage3_phase')]
    assert all(s['status']=='COMPLETE' for s in stages)
    g=stages[0]['results'];runs=stages[1]['results']+stages[2]['results'];cases=[]
    for name in d.CASES:
        selected={r['variant']:r for r in runs if r['case']==name}
        assert len(selected)==4
        assert len({r['noise_variance_estimate'] for r in selected.values()})==1
        bank=d.SOURCE/'bank/development'/name
        truth=P.arrays(bank/'truth.npz');public=P.arrays(bank/'public.npz');est=P.arrays(bank/'phase.npz')
        data=P.arrays(bank/'input.npz');active=truth['activity'].astype(bool)
        make=lambda slopes:public['pilot']*np.exp(1j*np.arange(len(public['pilot']))[:,None,None]*slopes[None,:,None])
        assert np.array_equal(make(est['phase_slopes']),data['operator'])
        x=truth['channel'].transpose(0,3,1,2).reshape(len(active)*16,-1)
        residual={label:float(np.mean(abs(public['observation'].reshape(16,-1)-a.reshape(16,-1)@x)**2))
                  for label,a in [('estimated',data['operator']),('oracle',make(truth['phase_slopes']))]}
        phase_diff=np.angle(np.exp(1j*(est['phase_slopes']-truth['phase_slopes'])))
        compact={v:{k:r[k] for k in ('iterations','converged','seconds','metrics','checkpoints','original_prefix_checks')} for v,r in selected.items()}
        activity_improvement={phase:selected[f'{phase}_phase_learned_activity']['metrics']['nmse_db']-selected[f'{phase}_phase_oracle_activity']['metrics']['nmse_db'] for phase in ('estimated','oracle')}
        phase_improvement={activity:selected[f'estimated_phase_{activity}_activity']['metrics']['nmse_db']-selected[f'oracle_phase_{activity}_activity']['metrics']['nmse_db'] for activity in ('learned','oracle')}
        cases.append(dict(case=name,active=int(active.sum()),variants=compact,
            active_phase_rmse_radians=float(np.sqrt(np.mean(phase_diff[active]**2))),
            truth_assisted_measurement_residual_mean_square=residual,
            provided_noise_variance=float(data['noise_variance']),
            estimated_noise_variance=selected['estimated_phase_learned_activity']['noise_variance_estimate'],
            activity_oracle_nmse_improvement_db=activity_improvement,phase_oracle_nmse_improvement_db=phase_improvement))
    result=dict(status='COMPLETE',protocol=p,gaussian=dict(results=g,
        all_converged=all(r['converged'] for r in g),max_mean_reference_error=max(r['exact_posterior_mean_relative_error'] for r in g),
        max_variance_relative_error=max(abs(r['variance_ratio']-1) for r in g)),cases=cases,
        independent_physical_scenes=2,physical_conditions=4,physical_runs=16,
        training_started=False,formal_experiments='PAUSED',protected_files_unchanged=True,
        scope='Exploratory diagnosis. Exact Gaussian experiment and truth-assisted ablations do not certify an AFDM deployable solution.',
        comparison='Final native outputs use unequal stopping times. Common checkpoints are provided separately; oracle activity trivially removes detection errors and cannot alone prove channel accuracy improves.',
        source_sha256={str(path.resolve()):P.sha(path) for path in [Path(__file__),d.OUT/'PROTOCOL.json',
            d.OUT/'stage1_gaussian/SUMMARY.json',d.OUT/'stage2_activity/SUMMARY.json',d.OUT/'stage3_phase/SUMMARY.json']})
    P.save(out/'REPORT.json',result)
    for case in cases:
        print(case['case'],'active',case['active'],'phase_rmse',case['active_phase_rmse_radians'])
        for variant,row in case['variants'].items():
            m=row['metrics'];print(variant,row['iterations'],row['converged'],round(m['nmse_db'],3),m['misses'],m['false_alarms'])
        print('residual',case['truth_assisted_measurement_residual_mean_square'])
    P.save(d.OUT/'STATUS.json',dict(status='COMPLETE',stages=3,physical_runs=16,training_started=False,formal_experiments='PAUSED'))


if __name__=='__main__':main()
