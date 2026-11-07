"""Independent, fixed 500-scene activity-evidence comparison."""
from pathlib import Path
import numpy as np
from project import ROOT
from utils import read_json, write_json, sha256
from evaluation.storage import arrays
from evaluation.metrics import score_arrays
from evaluation.white_matched_fp32_20261105.report import aggregate, check_metrics

OUT = ROOT/'result/snr_comparison/data/activity_evidence_500_20261105'
WHITE = ROOT/'result/snr_comparison/data/white_preconditioned_matched_fp32_1000_snr_20261105'
MAIN = ROOT/'result/main2000_known_phase_20261023/snr_comparison/PLAN.json'
METHODS = ('STMP-Gaussian', 'GP-MP-Gaussian')
SNRS = [-4, -2, 0, 2, 4, 6]

def checked(path, digest):
    if sha256(path) != digest:
        raise ValueError('Changed asset: '+str(path))

def tag(position):
    return f'scene{position//6:04d}_condition{position%6:02d}'

def verify():
    checked(OUT/'PLAN.json', read_json(OUT/'PLAN_HASH.json')['sha256'])
    plan = read_json(OUT/'PLAN.json')
    for p, h in plan['assets'].items():
        checked(p, h)
    assert plan['scenes'] == list(range(500)) and plan['snrs'] == SNRS
    assert plan['planned_new'] == 6000
    return plan

def prediction_check(prediction, truth, metrics):
    assert all(np.isfinite(v).all() for v in prediction.values())
    assert prediction['estimate'].shape == (40,16,16,16)
    assert prediction['probabilities'].shape == (40,)
    assert np.all((prediction['probabilities'] >= 0) & (prediction['probabilities'] <= 1))
    np.testing.assert_array_equal(prediction['activity_decision'], prediction['probabilities'] >= .5)
    measured = score_arrays(prediction, truth)
    check_metrics(metrics, measured)
    return measured

def reused_prediction(ref):
    prediction=arrays(ref['prediction']) if ref.get('prediction') else {}
    if 'compact' in ref:
        compact=arrays(ref['compact'])
        if prediction:
            np.testing.assert_array_equal(prediction['activity_decision'],compact['activity_decision'])
        prediction.update({k:compact[k] for k in ('probabilities','activity_decision','per_user_error','truth_activity')})
    return prediction

def reuse_metrics(ref,truth,metrics):
    prediction=reused_prediction(ref)
    if 'estimate' in prediction: return prediction_check(prediction,truth,metrics)
    # Historical policy: full channel arrays were serialized/rescored then deleted.
    # Activity predictions remain available; channel error is a retained statistic.
    assert all(np.isfinite(v).all() for v in prediction.values())
    active=np.asarray(truth['activity'],bool);decision=prediction['activity_decision']
    assert prediction['probabilities'].shape==(40,)
    assert np.all((prediction['probabilities']>=0)&(prediction['probabilities']<=1))
    np.testing.assert_array_equal(decision,prediction['probabilities']>=.5)
    np.testing.assert_array_equal(prediction['truth_activity'],truth['activity'])
    error=prediction['per_user_error'];assert error.shape==(40,) and np.all(error>=0)
    energy=np.sum(abs(truth['channel'])**2,axis=(1,2,3))
    measured=dict(active=int(active.sum()),inactive=int((~active).sum()),misses=int(np.sum(active&~decision)),
        false_alarms=int(np.sum(~active&decision)),decisions=decision.tolist(),
        full_error=float(error.sum()),active_error=float(error[active].sum()),inactive_error=float(error[~active].sum()),
        signal_energy=float(energy[active].sum()),per_user_error=error.tolist())
    check_metrics(metrics,measured)
    return dict(metrics,**measured)

def check_new(method, position, plan, *, preflight=False):
    folder = (OUT/'preflight' if preflight else Path(plan['native_directory']))/method/tag(position)
    row = read_json(folder/'RESULT.json')
    case = read_json(OUT/'INPUTS.json')[position]
    assert row['status'] == 'COMPLETE' and row['preflight'] == preflight
    assert row['method'] == method and row['input_files'] == case['files']
    assert (row['scene'],row['index'],row['snr_db']) == (position//6,position%6,SNRS[position%6])
    assert row['plan_sha256'] == sha256(OUT/'PLAN.json')
    for p,h in row['files'].items(): checked(p,h)
    assert set(row['files']) == {str(folder/n) for n in ('prediction.npz','record.json','INPUT_MANIFEST.json')}
    assert read_json(folder/'INPUT_MANIFEST.json')['case'] == case
    record = read_json(folder/'record.json')
    assert not record['classifier_loaded'] and record['classifier_calls'] == 0
    assert not record['receiver_truth_used'] and not record['noise_truth_used'] and record['oracle_phase_supplied']
    c = dict(record['configuration'])
    if method == 'STMP-Gaussian':
        assert c.pop('device') == 'cuda'
        assert c.pop('activity_prior') == float(arrays(Path(case['ready']).parent/'public.npz')['rho'])
        assert c.pop('activity_evidence') == 'gaussian_site'
        expected = dict(plan['configurations'][method]); expected.pop('activity_evidence')
    else:
        expected = plan['configurations'][method]
    assert c == expected
    assert row['iterations'] == record['iterations'] and 1 <= row['iterations'] <= 600
    assert row['stopping_reason'] == record['stopping_reason']
    assert row['converged'] == record['converged'] == (record['stopping_reason'] == 'CONVERGED')
    assert row['environment']['network_dtype'] == 'float32'
    assert all(row['environment'][k] is False for k in ('tf32','cudnn_tf32','cudnn_benchmark'))
    prediction = arrays(folder/'prediction.npz')
    row['metrics'] = prediction_check(prediction, arrays(Path(case['ready']).parent/'truth.npz'), row['metrics'])
    return row
