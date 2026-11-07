"""Stop on stable physical estimates across full phase-update intervals.

This is a project numerical rule, not a convergence theorem. Internal message
covariances and soft activity probabilities remain recorded diagnostics; the
returned channel, received-signal prediction, and decisions determine stopping.
"""
from algorithm.STMP.phase_stopping import CycleStopping


class OutputCycleStopping(CycleStopping):
    def check(self, iteration, mean, activity, prediction, input_covariance,
              feedback_covariance, *, noise_energy, phase_updates_completed):
        previous_stable = self.stable_cycles
        row = super().check(iteration, mean, activity, prediction, input_covariance,
                            feedback_covariance, noise_energy=noise_energy)
        changes = row["changes"]
        c = self.configuration
        # Unchanged phase is legitimate; do not force an update to permit stopping.
        passed = bool(changes
            and changes["channel_change"] < c["relative_tolerance"]
            and changes["prediction_change"] < c["relative_tolerance"]
            and self.decision_stable >= c["require_stable_decisions"]
            and self.current_moment_iterations >= c["require_stable_decisions"])
        self.stable_cycles = previous_stable + 1 if passed else 0
        stopped = (iteration >= self.minimum_iterations
                   and self.stable_cycles >= c["consecutive_cycles"])
        row.update(passed=passed, stable_cycles=self.stable_cycles, stop=stopped,
                   control_fields=["channel_change", "prediction_change",
                                   "decision_stable_iterations", "current_moment_iterations"],
                   phase_updates_completed=phase_updates_completed)
        return row
