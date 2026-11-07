"""Validate exact-mixture reference independently and bind final diagnostic reports."""
from itertools import product
from pathlib import Path
import numpy as np
from scipy.special import logsumexp
import diagnose_cai_framework_sequence as d


def validate_mixture():
    P=d.P;rows=[];rng=np.random.default_rng(202610199100001)
    for folder in sorted((d.OUT/'exact_mixture_supplement').glob('scene*')):
        r=P.read(folder/'REPORT.json');arrays=P.arrays(folder/'arrays.npz');y=arrays['observation']
        source=d.SOURCE/'bank/development'/f'scene{r["scene"]:03d}_users20'/'input.npz'
        op=P.arrays(source)['operator'][:,:6,:]
        vector=np.exp(2j*np.pi*np.arange(16)/16)
        cov=np.eye(16) if r['prior']=='iid' else .05*np.eye(16)+.95*np.outer(vector,vector.conj())
        components=[]
        for mask in product((0,1),repeat=6):
            sy=r['noise_variance']*np.eye(16,dtype=complex)
            for k,on in enumerate(mask):
                if on:sy+=op[:,k,:]@cov@op[:,k,:].conj().T
            inv=np.linalg.inv(sy)
            constant=sum(mask)*np.log(.25)+(6-sum(mask))*np.log(.75)-y.shape[1]*np.linalg.slogdet(sy)[1]
            components.append((mask,inv,constant))
        def evidence(obs):
            return float(logsumexp([c-np.vdot(obs,inv@obs).real for _,inv,c in components]))
        logs=np.array([c-np.vdot(y,inv@y).real for _,inv,c in components]);weights=np.exp(logs-logsumexp(logs))
        mean=np.zeros((6,16,y.shape[1]),complex)
        for (mask,inv,_),weight in zip(components,weights):
            for k,on in enumerate(mask):
                if on:mean[k]+=weight*cov@op[:,k,:].conj().T@inv@y
        mean=mean.reshape(96,-1)
        relative=float(np.linalg.norm(mean-arrays['exact_mean'])/max(np.linalg.norm(mean),1e-15));assert relative<1e-11
        direction=rng.normal(size=y.shape)+1j*rng.normal(size=y.shape);direction/=np.linalg.norm(direction)
        epsilon=1e-5
        numeric=(evidence(y+epsilon*direction)-evidence(y-epsilon*direction))/(2*epsilon)
        analytic=2*np.vdot(op.reshape(16,96)@mean-y,direction).real/r['noise_variance']
        gradient_error=float(abs(numeric-analytic)/max(1,abs(numeric),abs(analytic)))
        assert gradient_error<1e-6,(folder,gradient_error)
        rows.append(dict(case=folder.name,independent_mean_relative_error=relative,log_evidence_gradient_relative_error=gradient_error))
    return rows


def main():
    p=d.verify();P=d.P
    checks=validate_mixture()
    extra=P.read(d.OUT/'stage4_equal_budget/SUMMARY.json');assert extra['status']=='COMPLETE'
    original=P.read(d.ROOT/'results/cai_framework_sequence_20261019/REPORT.json')
    mixture=P.read(d.OUT/'exact_mixture_supplement/SUMMARY.json');assert mixture['status']=='COMPLETE'
    historical=P.read(d.ROOT/'runs/stability_repair_20261019/PRESERVATION.json')
    for path,digest in historical.items():assert P.sha(d.ROOT/path)==digest,path
    pairs=[]
    for case in original['cases']:
        if not case['case'].endswith('users100'):continue
        variants={r['variant']:r for r in extra['results'] if r['case']==case['case']}
        assert len(variants)==4
        pairs.append(dict(case=case['case'],variants=variants,
            activity_oracle_improvement_db={phase:variants[f'{phase}_phase_learned_activity']['metrics']['nmse_db']-variants[f'{phase}_phase_oracle_activity']['metrics']['nmse_db'] for phase in ('estimated','oracle')},
            phase_oracle_improvement_db={activity:variants[f'estimated_phase_{activity}_activity']['metrics']['nmse_db']-variants[f'oracle_phase_{activity}_activity']['metrics']['nmse_db'] for activity in ('learned','oracle')}))
    summary=dict(status='COMPLETE',main_stage_report=original,matched_300_iteration_pairs=pairs,
        exact_mixture_results=mixture,exact_mixture_reference_checks=checks,
        exact_mixture_max_normalized_excess_posterior_error=max(r['normalized_excess_posterior_squared_error'] for r in mixture['results']),
        exact_mixture_max_probability_abs_error=max(r['activity_probability_max_abs_error'] for r in mixture['results']),
        historical_files_verified_unchanged=len(historical),source_weight_files_verified_unchanged=len(p['source_and_weight_sha256']),
        training_started=False,formal_experiments='PAUSED',
        interpretation=['Gaussian cases establish arithmetic and fixed-point mean agreement only in those models.',
            'Exact activity-mixture controls retain approximation error, but no divergence was observed in eight small synthetic cases.',
            'Oracle activity lowers early active-user errors; its final influence must use the same iteration budget.',
            'Correct phase improves tested physical cases but does not eliminate early query mismatch.',
            'Residual NMSE alone does not prove a faulty receiver; finite noise and posterior uncertainty remain.',
            'These diagnostics do not isolate every physical prior, conditional-score, second-moment and classifier error or establish superiority over baselines.',
            'Original main-stage records inherit generic truth_loaded=false from core receiver; oracle_activity, oracle_phase and truth_used_in_inference explicitly override their information policy. Oracle controls are never deployable results.'],
        script_sha256=P.sha(Path(__file__)))
    target=d.ROOT/'results/cai_framework_sequence_20261019/FINAL_REPORT.json';assert not target.exists()
    P.save(target,summary)
    P.save(d.OUT/'STATUS.json',dict(status='COMPLETE',main_stages=3,physical_runs=24,gaussian_controls=8,
        exact_mixture_controls=8,training_started=False,formal_experiments='PAUSED'))
    print('Mixture derivative check max:',max(x['log_evidence_gradient_relative_error'] for x in checks))
    for row in pairs:
        print(row['case'])
        for name,r in row['variants'].items():print(name,r['metrics']['nmse_db'],r['metrics']['misses'],r['metrics']['false_alarms'])
        print('activity effect',row['activity_oracle_improvement_db'],'phase effect',row['phase_oracle_improvement_db'])
    print('Verified historical files:',len(historical))


if __name__=='__main__':main()
