"""Compare returned estimates across complete periodic phase-update cycles.

This is a numerical stopping rule defined by the project, not a convergence
theorem. It deliberately does not use true activity, channel or phase.
"""
import numpy as np


def relative_change(current, previous, floor=1e-12):
    return float(np.linalg.norm(current-previous) /
                 max(np.linalg.norm(current), np.linalg.norm(previous), floor))


class CycleStopping:
    def __init__(self, configuration, *, minimum_iterations):
        c=configuration
        if c['comparison']!='completed_phase_update_cycles' or c['require_raw_site_residual'] is not False:
            raise ValueError('Expected complete-cycle output stopping')
        for name in ('relative_tolerance','activity_tolerance'):
            value=c[name]
            if isinstance(value,bool) or not np.isfinite(value) or value<=0:
                raise ValueError('Positive finite stopping tolerances required')
        for name in ('consecutive_cycles','require_stable_decisions'):
            if type(c[name]) is not int or c[name]<1:
                raise ValueError('Positive integer stopping windows required')
        self.configuration=dict(c)
        self.minimum_iterations=minimum_iterations
        self.previous=None
        self.previous_decision=None
        self.decision_stable=0
        self.current_moment_iterations=0
        self.stable_cycles=0

    def observe_decisions(self, activity, threshold, *, current_moments=True):
        decision=np.asarray(activity)>=threshold
        self.decision_stable=(self.decision_stable+1
            if self.previous_decision is not None and np.array_equal(decision,self.previous_decision)
            else 1)
        self.previous_decision=decision.copy()
        self.current_moment_iterations=(self.current_moment_iterations+1 if current_moments else 0)

    def check(self, iteration, mean, activity, prediction, input_covariance,
              feedback_covariance, *, noise_energy):
        values=dict(channel=np.asarray(mean),activity=np.asarray(activity),
            prediction=np.asarray(prediction),input_covariance=np.asarray(input_covariance),
            feedback_covariance=np.asarray(feedback_covariance))
        if (not all(np.isfinite(v).all() for v in values.values())
                or not np.isfinite(noise_energy) or noise_energy<=0):
            raise FloatingPointError('Finite estimates and positive observation noise required')
        changes={}
        passed=False
        c=self.configuration
        if self.previous is not None:
            for name in ('channel','prediction','input_covariance','feedback_covariance'):
                floor=max(np.sqrt(noise_energy),1e-12) if name=='prediction' else 1e-12
                changes[name+'_change']=relative_change(values[name],self.previous[name],floor)
            changes['activity_change']=float(np.max(abs(values['activity']-self.previous['activity'])))
            passed=(all(changes[name+'_change']<c['relative_tolerance']
                        for name in ('channel','prediction','input_covariance','feedback_covariance'))
                    and changes['activity_change']<c['activity_tolerance']
                    and self.decision_stable>=c['require_stable_decisions']
                    and self.current_moment_iterations>=c['require_stable_decisions'])
        self.stable_cycles=self.stable_cycles+1 if passed else 0
        # Endpoints remain in physical channel coordinates. A later phase update
        # must not rotate or otherwise modify this reference copy.
        self.previous={name:value.copy() for name,value in values.items()}
        stopped=(iteration>=self.minimum_iterations
                 and self.stable_cycles>=c['consecutive_cycles'])
        return dict(iteration=iteration,passed=bool(passed),changes=changes,
            stable_cycles=self.stable_cycles,decision_stable_iterations=self.decision_stable,
            current_moment_iterations=self.current_moment_iterations,
            stop=bool(stopped))
