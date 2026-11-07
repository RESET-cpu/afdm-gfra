"""Passive truth-based trajectory scoring and complete paired aggregation."""
import numpy as np


class Collector:
    def __init__(self, truth, iterations):
        self.channel = np.array(truth['channel'], copy=True)
        self.active = np.asarray(truth['activity'], bool).copy()
        self.signal = float(np.sum(abs(self.channel[self.active])**2))
        self.limit = iterations
        self.errors, self.decisions, self.scores, self.rows = [], [], [], []

    def add(self, iteration, estimate, decisions, diagnostics, *, probability, native_would_stop):
        if iteration != len(self.rows) + 1 or iteration > self.limit:
            raise ValueError('Actual iterations must be consecutive, with no padding')
        if estimate.shape != self.channel.shape or decisions.shape != self.active.shape:
            raise ValueError('Prediction/truth dimensions differ')
        error = np.sum(abs(estimate - self.channel)**2, axis=(1, 2, 3))
        if not np.isfinite(error).all() or not np.isfinite(probability).all():
            raise FloatingPointError('Nonfinite trajectory; retain failed case without omission')
        decisions = np.asarray(decisions, bool).copy()
        self.errors.append(error)
        self.decisions.append(decisions)
        self.scores.append(np.array(probability, copy=True))
        self.rows.append(dict(iteration=iteration, diagnostics=diagnostics,
                              native_would_stop=native_would_stop,
                              error_energy=float(error.sum()), signal_energy=self.signal,
                              nmse_db=float(10*np.log10(max(error.sum()/self.signal, np.finfo(float).tiny))) if self.signal > 0 else None,
                              misses=int(np.sum(self.active & ~decisions)),
                              false_alarms=int(np.sum(~self.active & decisions)),
                              aer=float(np.mean(decisions != self.active))))

    def arrays(self):
        count = len(self.rows)
        shape = (count, len(self.active))
        return dict(iteration=np.arange(1, count + 1), per_user_error=np.asarray(self.errors).reshape(shape),
                    decisions=np.asarray(self.decisions, bool).reshape(shape),
                    activity_score=np.asarray(self.scores).reshape(shape),
                    truth_activity=self.active, signal_energy=np.asarray(self.signal),
                    native_would_stop=np.asarray([r['native_would_stop'] for r in self.rows], bool))

    def verify_final(self, arrays):
        if len(self.rows) != self.limit:
            raise ValueError('Incomplete actual iteration coverage')
        error = np.sum(abs(arrays['estimate'] - self.channel)**2, axis=(1, 2, 3))
        np.testing.assert_allclose(error, self.errors[-1], rtol=1e-10, atol=1e-12)
        np.testing.assert_array_equal(arrays['activity_decision'], self.decisions[-1])


def aggregate(traces, scene_ids, iterations):
    """Pool energy and user counts; never average scene dB or drop missing cases."""
    if set(traces) != set(scene_ids) or len(traces) != len(scene_ids):
        raise ValueError('All predeclared paired scenes are required')
    error = np.zeros(iterations)
    misses = np.zeros(iterations, dtype=np.int64)
    false_alarms = misses.copy()
    signal, users = 0., 0
    for scene in scene_ids:
        trace = traces[scene]
        if not np.array_equal(trace['iteration'], np.arange(1, iterations + 1)):
            raise ValueError('Incomplete actual iteration coverage')
        e, d, a = trace['per_user_error'], trace['decisions'], trace['truth_activity']
        if e.shape != (iterations, len(a)) or d.shape != e.shape or d.dtype != bool or a.dtype != bool:
            raise ValueError('Invalid trajectory dimensions/types')
        energy = float(trace['signal_energy'])
        if not np.isfinite(e).all() or np.any(e < 0) or not np.isfinite(energy) or energy < 0:
            raise ValueError('Invalid trajectory energy')
        error += e.sum(axis=1)
        signal += energy
        users += len(a)
        misses += np.sum(a[None] & ~d, axis=1)
        false_alarms += np.sum(~a[None] & d, axis=1)
    if signal <= 0 or users == 0:
        raise ValueError('Positive pooled signal energy and user count required')
    return dict(iteration=np.arange(1, iterations + 1),
                nmse_db=10*np.log10(np.maximum(error / signal, np.finfo(float).tiny)),
                aer=(misses + false_alarms) / users, error_energy=error,
                signal_energy=signal, users=users, misses=misses, false_alarms=false_alarms)
