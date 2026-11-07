"""Apply predeclared development/acceptance gates without changing them."""
import argparse
import numpy as np
import repair_stability_development as d

TARGET='damping0.1_budget1200_fp32'


def evaluate(split,candidate=TARGET):
    protocol=d.paired.read(d.OUT/'PROTOCOL.json')
    count=protocol[f'{split}_scenes']; gates=protocol['acceptance_gates']
    records={m:[] for m in (candidate,'offgrid_sbl')}
    missing=[]
    for method in records:
        for scene in range(count):
            for users in protocol['users']:
                path=d.OUT/'evaluations'/split/method/f'scene{scene:03d}_users{users}'/'SUMMARY.json'
                if not path.exists():
                    missing.append(str(path));continue
                row=d.paired.read(path)
                assert d.paired.sha(path.parent/'prediction.npz')==row['prediction_sha256']
                records[method].append(row)
    if missing:
        return dict(status='INCOMPLETE',passed=False,missing=missing)
    candidate_rows=records[candidate]
    checks=dict(all_outputs_finite=all(r['finite'] for r in candidate_rows),
        all_cases_original_convergence_criteria=all(r['stopping_reason']=='CONVERGED' for r in candidate_rows),
        all_final_queries_inside_training_support=all(r['last']['supported'] for r in candidate_rows),
        worst_case_nmse_db_at_most=max(r['metrics']['nmse_db'] for r in candidate_rows)<=gates['worst_case_nmse_db_at_most'])
    comparisons=[]
    for users in protocol['users']:
        by_method={}
        for method in records:
            group=[r for r in records[method] if r['users']==users]
            sums={k:sum(r['metrics'][k] for r in group) for k in
                ('full_error','signal_energy','active','inactive','misses','false_alarms')}
            by_method[method]=dict(**sums,nmse_db=float(10*np.log10(sums['full_error']/sums['signal_energy'])),
                aer=(sums['misses']+sums['false_alarms'])/(sums['active']+sums['inactive']))
        a,b=by_method[candidate],by_method['offgrid_sbl']
        condition=dict(nmse_negative=a['nmse_db']<gates['each_condition_pooled_nmse_db_below'],
            nmse_nonregression=a['nmse_db']-b['nmse_db']<=gates['per_condition_nmse_db_vs_sbl_at_most'],
            aer_nonregression=a['aer']-b['aer']<=gates['per_condition_aer_vs_sbl_at_most'])
        comparisons.append(dict(users=users,methods=by_method,checks=condition))
        for key,value in condition.items():checks[f'K{users}_{key}']=value
    return dict(status='PASS' if all(checks.values()) else 'FAIL',passed=all(checks.values()),
        split=split,candidate=candidate,cases=len(candidate_rows),checks=checks,comparisons=comparisons,
        unconverged=[dict(scene=r['scene'],users=r['users'],iterations=r['iterations'],last=r['last'])
            for r in candidate_rows if r['stopping_reason']!='CONVERGED'],
        median_iterations=float(np.median([r['iterations'] for r in candidate_rows])),
        maximum_iterations=max(r['iterations'] for r in candidate_rows),
        protocol_sha256=d.paired.sha(d.OUT/'PROTOCOL.json'),
        interpretation='Independent scenes are the sampling units; pooled point estimates only, no significance or universal stability guarantee.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--split',choices=list(d.SEEDS),default='development')
    args=parser.parse_args();result=evaluate(args.split)
    d.paired.save(d.OUT/f'{args.split.upper()}_GATE.json',result)
    print({k:v for k,v in result.items() if k not in ('missing','comparisons')},flush=True)
