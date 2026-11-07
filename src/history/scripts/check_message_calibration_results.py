"""Read-only validation of completed calibration study and stratified summaries."""
import numpy as np
import torch
import validate_message_calibration as S


def main():
    protocol=S.verify(); rows=S.P.read(S.OUT/'physical/SUMMARY.json')['results']
    frozen=S.P.read(S.OUT/'FROZEN_MODELS.json'); pairs=[]; adapter_rows=[]; support=[]
    for case in sorted({r['case'] for r in rows}):
        group=[r for r in rows if r['case']==case]
        assert len(group)==4 and {r['variant'] for r in group}==set(protocol['variants'])
        completed=[r for r in group if r['status']=='COMPLETE']
        assert len({r['input_sha256'] for r in completed})<=1
        pairs.append(dict(case=case,same_input=True,completed=len(completed),failed=4-len(completed)))
        for r in completed:
            folder=S.OUT/'physical'/case/r['variant']
            prediction=S.P.arrays(folder/'prediction.npz');record=S.P.read(folder/'record.json')
            assert all(np.isfinite(x).all() for x in prediction.values())
            assert record['iterations']==300 and len(record['trace'])==300
            assert record['truth_used_in_inference'] is False
            unsupported=[t for t in record['trace'] if t['unsupported_users']]
            support.append(dict(case=case,variant=r['variant'],
                unsupported_iterations=len(unsupported),
                first_unsupported_iteration=unsupported[0]['iteration'] if unsupported else None,
                first_unsupported_variance=unsupported[0]['query_variance_min'] if unsupported else None,
                minimum_query_variance=min(t['query_variance_min'] for t in record['trace']),
                maximum_query_variance=max(t['query_variance_min'] for t in record['trace'])))
            if r['variant']!='baseline':
                diag=record['calibration_diagnostics']
                adapter_rows.append(dict(case=case,variant=r['variant'],supported_calls=len(diag),
                    raw_variance_clips=sum(d['raw_ratio_outside_bounds'] for d in diag),
                    alpha_min=min(d['alpha_quantiles'][0] for d in diag),
                    alpha_max=max(d['alpha_quantiles'][-1] for d in diag),
                    ratio_min=min(d['variance_ratio_quantiles'][0] for d in diag),
                    ratio_max=max(d['variance_ratio_quantiles'][-1] for d in diag)))
    batch=S.tensors('test'); synthetic={}
    for variant in protocol['variants']:
        model=S.Calibration('correlation' if variant=='baseline' else variant)
        if variant!='baseline':
            path=S.OUT/'models'/variant/'best.pt'
            assert S.P.sha(path)==frozen['models'][variant]
            blob=torch.load(path,weights_only=False)
            assert blob['protocol_sha256']==S.P.sha(S.OUT/'PROTOCOL.json')
            model.load_state_dict(blob['state_dict'])
        synthetic[variant]={}
        for label,mask in [('white',batch['white'].bool()),('correlated',~batch['white'].bool())]:
            synthetic[variant][label]=S.measurements(model,{k:v[mask] for k,v in batch.items()})
    S.P.save(S.RESULT/'CHECKS.json',dict(pairing=pairs,adapter=adapter_rows,support=support,
        synthetic_by_noise=synthetic,
        original_test_variance_clips=int(torch.sum((batch['raw_ratio'][:,0]<1e-5)|(batch['raw_ratio'][:,0]>1-1e-5))),
        zero_head_note='Synthetic baseline means/evidence unchanged apart from float32 cache; variance bounds applied, with count reported.',
        finite_outputs=True,raw_physical_runs=len(rows),unit_tests='tests/test_message_calibration_candidate.py: 4 passed',
        report_script_sha256=S.P.sha(__file__)))
    print('CHECKED',len(rows),'runs;',len(pairs),'paired inputs',flush=True)


if __name__=='__main__':main()
