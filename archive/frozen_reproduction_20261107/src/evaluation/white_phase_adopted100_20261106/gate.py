"""Validate the adopted 100-scene ablation before the unchanged phase run."""
import csv
from evaluation.white_phase_frontend_20261106.common import *
from evaluation.white_phase_frontend_20261106 import common as original

ADOPTED = ABLATION / 'adopted100_20261106'
CONTROL = ABLATION / 'stop_after100_20261106'
AMENDMENT = OUT / 'gate_adopted100_20261106'
GROUPS = ('STMP-Gaussian', 'STMP-LR', 'GP-MP-Gaussian', 'GP-MP-LR')


def verify_amendment():
    receipt = read_json(AMENDMENT / 'AMENDMENT.json')
    checked(OUT/'PLAN.json', receipt['original_plan_sha256'])
    assert receipt['adopted_scenes_per_snr'] == 100
    assert receipt['estimated_phase_inputs'] == 6000
    for path, digest in receipt['assets'].items():
        checked(path, digest)
    return receipt


def verify(*, full=True):
    verify_amendment()
    return original.verify(full=full)


def validate_adopted(folder=ADOPTED, control=CONTROL, batch=ABLATION):
    complete = read_json(folder/'COMPLETION.json')
    summary = read_json(folder/'SUMMARY.json')
    request = read_json(control/'REQUEST.json')
    assert complete['status'] == 'PASS' and summary['status'] == 'VERIFIED'
    assert complete['adopted_scenes_per_snr'] == summary['paired_scenes_per_snr'] == 100
    assert request['scenes'] == summary['scene_ids'] == list(range(100))
    assert request['snrs'] == summary['snrs'] == SNRS
    assert complete['new_inferences'] == complete['reused_inferences'] == 1200
    assert summary['adopted_new_inferences'] == summary['reused_inferences'] == 1200
    assert summary['total_adopted_results'] == 2400
    assert complete['original_plan_completed'] is False
    for key in ('coordinator_and_workers_exited', 'paired_coverage_verified',
                'input_and_output_hashes_verified', 'all_activity_predictions_rescored',
                'all_finite_iteration_limit_outputs_retained'):
        assert complete[key] is True
    assert complete['full_channel_predictions_rescored'] == 1806
    assert summary['channel_rescoring_counts']['STMP-LR'] == {'full_prediction': 6, 'retained_per_user_error': 594}
    assert set(complete['artifacts']) >= {'SUMMARY.json','PAIRED_ROWS.json','PAIRED_CASES.csv','SOURCE_HASHES.json','PROCESS_EXIT.json'}
    for name, digest in complete['artifacts'].items():
        assert Path(name).name == name
        checked(folder/name, digest)
    checked(batch/'PLAN.json', complete['plan_sha256'])
    assert summary['plan_sha256'] == request['plan_sha256'] == complete['plan_sha256']
    checked(control/'REQUEST.json', summary['authorization_sha256'])
    checked(folder/'SOURCE_HASHES.json', summary['source_hashes_sha256'])
    assert set(summary['methods']) == set(GROUPS)
    for group in GROUPS:
        assert set(summary['methods'][group]) == {str(s) for s in SNRS}
        assert all(summary['methods'][group][str(s)]['inputs'] == 100 and
                   summary['methods'][group][str(s)]['decisions'] == 4000 for s in SNRS)
    with (folder/'PAIRED_CASES.csv').open(newline='', encoding='utf-8') as stream:
        rows = list(csv.DictReader(stream))
    keys = [(r['method'], int(r['scene']), int(r['index'])) for r in rows]
    expected = {(m,s,c) for m in GROUPS for s in range(100) for c in range(6)}
    assert len(keys) == 2400 and set(keys) == expected
    assert all(float(r['snr_db']) == SNRS[int(r['index'])] for r in rows)
    for group in GROUPS:
        for i,snr in enumerate(SNRS):
            selected = [r for r in rows if r['method']==group and int(r['index'])==i]
            aggregate = summary['methods'][group][str(snr)]
            assert sum(int(r['active'])+int(r['inactive']) for r in selected) == aggregate['decisions']
            assert sum(int(r['misses']) for r in selected) == aggregate['misses']
            assert sum(int(r['false_alarms']) for r in selected) == aggregate['false_alarms']
            assert sum(int(r['iterations'])==600 for r in selected) == aggregate['iteration_limit_count']
    assert read_json(folder/'PROCESS_EXIT.json')['status'] == 'PASS'
    status = read_json(batch/'STATUS.json')
    assert status['stage'] == 'PAUSED' and status['active_workers'] == status['failed'] == 0
    assert read_json(batch/'STOP.json')['effective_scenes'] == 100
    assert not (batch/'FAILURE.json').exists() and not (control/'FAILURE.json').exists()
    return dict(completion_sha256=sha256(folder/'COMPLETION.json'),
                summary_sha256=sha256(folder/'SUMMARY.json'),
                paired_sha256=sha256(folder/'PAIRED_CASES.csv'),
                source_hashes_sha256=sha256(folder/'SOURCE_HASHES.json'),
                adopted_scenes_per_snr=100, new_inferences=1200, reused_inferences=1200)


def dependencies():
    verify_amendment()
    reasons, receipts = [], {}
    if not all((WHITE/name).exists() for name in ('COMPLETION.json','SUMMARY.json','STATUS.json')):
        reasons.append('White known-phase completion receipt missing')
    else:
        complete, summary, status = [read_json(WHITE/name) for name in ('COMPLETION.json','SUMMARY.json','STATUS.json')]
        assert complete['status']=='PASS' and summary['status']=='VERIFIED'
        assert complete['inputs']==6000 and complete['saved_arrays_rescored'] and complete['input_and_output_hashes_verified']
        checked(WHITE/'SUMMARY.json', complete['summary_sha256'])
        checked(WHITE/'PAIRED_CASES.csv', complete['paired_sha256'])
        assert set(summary['methods'])=={'GP-MP','CGP-MP'}
        for values in summary['methods'].values():
            assert set(values)=={str(s) for s in SNRS}
            assert all(v['inputs']==1000 and v['decisions']==40000 for v in values.values())
        if status['stage']!='COMPLETE' or status['active_workers']!=0:
            reasons.append('White known-phase coordinator has not completed')
        receipts['white_known_phase']=dict(completion_sha256=sha256(WHITE/'COMPLETION.json'),
            summary_sha256=complete['summary_sha256'],paired_sha256=complete['paired_sha256'])
    if not (ADOPTED/'COMPLETION.json').exists():
        reasons.append('Adopted 100-scene ablation is not fully verified')
    else:
        receipts['ablation']=validate_adopted()
    live = live_processes(('evaluation.white_matched_fp32_20261105',
        'evaluation.throughput_20261105.resume_white', 'evaluation.activity_evidence_500_20261105',
        str(CONTROL/'guard.py'), str(ADOPTED/'summarize.py')))
    if live:
        reasons.append('Predecessor processes are still running')
    return dict(status='WAITING' if reasons else 'PASS', checked_unix=time.time(), reasons=reasons,
        receipts=receipts,live_processes=live,amendment_sha256=sha256(AMENDMENT/'AMENDMENT.json'))


def require_ready():
    result = dependencies()
    if result['status'] != 'PASS':
        raise RuntimeError('Predecessors incomplete: '+'; '.join(result['reasons']))
    return result
