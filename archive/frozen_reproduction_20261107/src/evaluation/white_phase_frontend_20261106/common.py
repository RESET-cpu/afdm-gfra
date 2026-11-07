"""Paths, completion gates, and validation; importing this module never uses CUDA."""
from pathlib import Path
import time
import psutil
from project import ROOT
from utils import read_json, write_json, sha256

OUT = ROOT / 'result/snr_comparison/data/white_phase_frontend_marginal_1000_20261106'
WHITE = ROOT / 'result/snr_comparison/data/white_preconditioned_matched_fp32_1000_snr_20261105'
COLORED = ROOT / 'result/snr_comparison/data/c_stmp_phase_frontend_marginal_1000_20261104'
ABLATION = ROOT / 'result/snr_comparison/data/activity_evidence_500_20261105'
PACKAGE = Path(__file__).resolve().parent
BINDING = ROOT / 'src/configs/candidates/GP_MP_white_phase_frontend_marginal_20261106.json'
SNRS = [-4, -2, 0, 2, 4, 6]
METHODS = ('white_estimated_phase', 'colored_estimated_phase', 'white_known_phase')


def checked(path, digest):
    if sha256(path) != digest:
        raise ValueError('Changed asset: ' + str(path))


def tag(position):
    if not 0 <= position < 6000:
        raise ValueError('Position outside the authorized 6000 inputs')
    return f'scene{position//6:04d}_condition{position%6:02d}'


def live_processes(tokens):
    found = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
        try:
            info = proc.info
            command = ' '.join(info['cmdline'] or [])
            if (info['name'] or '').lower() in ('python.exe', 'pythonw.exe') and any(t in command for t in tokens):
                found.append(dict(pid=info['pid'], created_unix=info['create_time'], command=command))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return found


def dependencies():
    """Read actual completion receipts and exact coverage; absence means waiting."""
    reasons, receipts = [], {}
    for label, folder, groups, count in (
        ('white_known_phase', WHITE, ('GP-MP', 'CGP-MP'), 1000),
        ('ablation', ABLATION, ('STMP-Gaussian', 'STMP-LR', 'GP-MP-Gaussian', 'GP-MP-LR'), 500),
    ):
        if not all((folder/n).exists() for n in ('COMPLETION.json', 'SUMMARY.json', 'STATUS.json')):
            reasons.append(label + ' has no complete verified receipt')
            continue
        complete, summary, status = [read_json(folder/n) for n in ('COMPLETION.json', 'SUMMARY.json', 'STATUS.json')]
        assert complete['status'] == 'PASS' and summary['status'] == 'VERIFIED'
        checked(folder/'SUMMARY.json', complete['summary_sha256'])
        checked(folder/'PAIRED_CASES.csv', complete['paired_sha256'])
        assert set(summary['methods']) == set(groups)
        for group in groups:
            assert set(summary['methods'][group]) == {str(s) for s in SNRS}
            assert all(summary['methods'][group][str(s)]['inputs'] == count and
                       summary['methods'][group][str(s)]['decisions'] == count*40 for s in SNRS)
        if label == 'white_known_phase':
            assert complete['inputs'] == 6000 and complete['saved_arrays_rescored']
            assert complete['input_and_output_hashes_verified']
        else:
            assert complete['new_inferences'] == complete['reused_inferences'] == 6000
            assert complete['all_activity_predictions_rescored'] and complete['new_channel_predictions_rescored']
            assert complete['paired_coverage_verified']
            checked(folder/'PLAN.json', summary['plan_sha256'])
        if status['stage'] != 'COMPLETE' or status['active_workers'] != 0:
            reasons.append(label + ' coordinator has not published COMPLETE')
        receipts[label] = dict(completion_sha256=sha256(folder/'COMPLETION.json'),
                               summary_sha256=complete['summary_sha256'], paired_sha256=complete['paired_sha256'])
    live = live_processes(('evaluation.white_matched_fp32_20261105', 'evaluation.throughput_20261105.resume_white',
                           'evaluation.activity_evidence_500_20261105'))
    if live:
        reasons.append('Predecessor processes are still running')
    return dict(status='WAITING' if reasons else 'PASS', checked_unix=time.time(),
                reasons=reasons, receipts=receipts, live_processes=live)


def require_ready():
    result = dependencies()
    if result['status'] != 'PASS':
        raise RuntimeError('Predecessors incomplete: ' + '; '.join(result['reasons']))
    return result


def verify(*, full=True):
    checked(OUT/'PLAN.json', read_json(OUT/'PLAN_HASH.json')['sha256'])
    plan = read_json(OUT/'PLAN.json')
    for path, digest in plan['assets' if full else 'worker_assets'].items():
        checked(path, digest)
    assert plan['planned'] == 6000 and plan['scenes'] == list(range(1000)) and plan['snrs'] == SNRS
    assert plan['receiver_configuration'] == read_json(WHITE/'PLAN.json')['receiver_configuration']
    assert plan['frontend_binding'] == read_json(BINDING)
    return plan


def check_phase_record(record, prediction, *, configuration=None, binding=None):
    import numpy as np
    assert record['phase_mode'] == 'estimated' and record['phase_updates_inside_receiver'] == 0
    assert record['phase_method'] == 'Marginal physical phase estimate once, then hold fixed'
    assert all(not record[k] for k in ('oracle_phase_supplied', 'receiver_truth_used', 'noise_truth_used',
                                      'supplied_phase_operator_used', 'initializer_gain_or_power_forwarded'))
    assert not record['phase_initialization']['truth_used_in_inference']
    assert record['input_fields'] == ['observation', 'pilot', 'activity_prior']
    np.testing.assert_array_equal(prediction['phase'], prediction['initial_phase'])
    np.testing.assert_array_equal(prediction['phase_slopes'], prediction['initial_phase_slopes'])
    if configuration is not None:
        assert record['configuration'] == configuration
    if binding is not None:
        assert record['frontend_binding'] == binding


def validate_result(position, plan, *, preflight=False):
    import numpy as np
    from evaluation.storage import arrays
    from evaluation.metrics import score_arrays
    from evaluation.white_matched_fp32_20261105.report import check_metrics
    folder = (OUT/'preflight' if preflight else Path(plan['native_directory']))/tag(position)
    case = read_json(OUT/'INPUTS.json')[position]
    row = read_json(folder/'RESULT.json')
    assert row['status'] == 'COMPLETE' and row['preflight'] == preflight
    assert (row['scene'], row['index'], row['snr_db']) == (position//6, position%6, SNRS[position%6])
    assert row['input_files'] == case['files'] and row['plan_sha256'] == sha256(OUT/'PLAN.json')
    assert row['phase_mode'] == 'estimated' and not row['oracle_phase_supplied']
    assert not row['channel_activity_truth_used_in_inference']
    assert set(row['files']) == {str(folder/n) for n in ('prediction.npz', 'record.json', 'INPUT_MANIFEST.json')}
    for path, digest in row['files'].items():
        checked(path, digest)
    manifest = read_json(folder/'INPUT_MANIFEST.json')
    assert manifest['case'] == case and manifest['plan_sha256'] == row['plan_sha256']
    assert all(row['environment'][k] is False for k in ('tf32', 'cudnn_tf32', 'cudnn_benchmark'))
    assert row['environment']['network_dtype'] == 'float32'
    record, prediction = read_json(folder/'record.json'), arrays(folder/'prediction.npz')
    check_phase_record(record, prediction, configuration=plan['receiver_configuration'], binding=plan['frontend_binding'])
    assert record['denoiser_training_noise'] == 'white Gaussian'
    assert row['iterations'] == record['iterations'] and 1 <= row['iterations'] <= 600
    assert row['converged'] == record['converged'] == (record['stopping_reason'] == 'CONVERGED')
    assert row['stopping_reason'] == record['stopping_reason']
    assert all(np.isfinite(v).all() for v in prediction.values())
    assert prediction['estimate'].shape == (40, 16, 16, 16) and prediction['probabilities'].shape == (40,)
    assert np.all((prediction['probabilities'] >= 0) & (prediction['probabilities'] <= 1))
    np.testing.assert_array_equal(prediction['activity_decision'], prediction['probabilities'] >= .5)
    metrics = score_arrays(prediction, arrays(Path(case['ready']).parent/'truth.npz'))
    check_metrics(row['metrics'], metrics)
    return row, record, prediction
