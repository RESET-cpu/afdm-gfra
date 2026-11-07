"""Truth-based metrics, separate from receiver inference."""
import numpy as np


def evaluate(estimate_path,truth_path):
    with np.load(estimate_path,allow_pickle=False) as z:
        arrays={key:z[key] for key in z.files}
    with np.load(truth_path,allow_pickle=False) as z:
        truth={key:z[key] for key in z.files}
    if 'activity_decision' not in arrays:
        if 'probabilities' not in arrays:
            raise ValueError('Prediction contains scores only; a matching frozen activity rule is required')
        arrays['activity_decision']=arrays['probabilities']>=.5
    return score_arrays(arrays,truth)


def score_arrays(arrays, truth):
    active = np.asarray(truth['activity'], bool); h = truth['channel']
    estimate = arrays['estimate']; decision = np.asarray(arrays['activity_decision'], bool)
    if estimate.shape != h.shape or decision.shape != active.shape:
        raise ValueError('estimate/truth dimensions differ')
    error = np.sum(abs(estimate-h)**2, axis=(1, 2, 3))
    energy = np.sum(abs(h)**2, axis=(1, 2, 3))
    signal_energy = float(energy[active].sum())
    full_error, active_error = float(error.sum()), float(error[active].sum())
    return dict(active=int(active.sum()), inactive=int((~active).sum()), misses=int(np.sum(active & ~decision)),
                false_alarms=int(np.sum(~active & decision)), active_error=active_error,
                signal_energy=signal_energy, full_error=full_error, inactive_error=float(error[~active].sum()),
                nmse_db=float(10*np.log10(max(full_error/signal_energy, np.finfo(float).tiny))) if signal_energy > 0 else None,
                active_nmse_db=float(10*np.log10(max(active_error/signal_energy, np.finfo(float).tiny))) if signal_energy > 0 else None,
                per_user_error=error.tolist(), decisions=decision.tolist())
