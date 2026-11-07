"""Shared matrix checks and unchanged activity decision rules."""
import json
import numpy as np
from workspace import ROOT
from fileio import sha256

def validate(design, received, noise):
    a, y = np.asarray(design, complex), np.asarray(received, complex)
    if (a.ndim != 2 or y.ndim != 2 or a.shape[0] != y.shape[0] or not a.size or not y.size
            or not np.isfinite(a).all() or not np.isfinite(y).all() or not np.isfinite(noise) or noise <= 0):
        raise ValueError('finite complex MMV observation and positive noise variance required')
    return a, y


def coefficient_activity(coefficients, users):
    """Eq. (27): physical coefficient block energy divided by its maximum."""
    z = np.asarray(coefficients)
    if (z.ndim != 2 or not z.size or users < 1 or z.shape[0] % users
            or not np.isfinite(z).all()):
        raise ValueError('finite coefficient blocks and positive user count required')
    energy = np.mean(abs(z.reshape(users, -1, z.shape[1]))**2, axis=(1, 2))
    maximum = float(energy.max())
    score = energy/maximum if maximum > 0 else np.zeros(users)
    return score, energy


def activity_decisions(scores, energies, threshold):
    """Ding uses >=. An all-zero estimate has no defined relative energy."""
    if not np.isfinite(threshold) or threshold < 0:
        raise ValueError('finite nonnegative activity threshold required')
    return (np.asarray(scores) >= threshold) & (np.max(energies) > 0)


def public_snr_db(inputs):
    power = float(np.mean(abs(inputs.observation)**2))
    return float(10*np.log10(max(power/inputs.noise_variance-1., 1e-12)))


def nearest_node(value, nodes):
    return int(np.argmin(abs(np.asarray(nodes, float)-value)))


class FrozenReadout:
    def __init__(self, reference):
        path = ROOT/reference['path']
        if sha256(path) != reference['sha256']:
            raise ValueError('Frozen activity rule changed')
        self.policy = json.loads(path.read_text())
        self.sha256 = reference['sha256']
        self.nodes = np.asarray(self.policy['nodes_db'], float)
        if (self.policy['status'] != 'FROZEN_RULE_REUSED_ACROSS_USER_COUNTS'
                or self.policy['user_count_used_for_dispatch']
                or self.policy['thresholds_refitted']
                or self.policy['evaluation_labels_used_for_selection']
                or self.policy['comparator'] != '>='
                or self.nodes.ndim != 1 or not len(self.nodes)
                or not np.isfinite(self.nodes).all() or np.any(np.diff(self.nodes) <= 0)):
            raise ValueError('A fixed rule with ordered SNR nodes is required')
        for method in ('somp', 'gamp', 'gnn'):
            rows = self.policy['methods'][method]
            if ([row['node_db'] for row in rows] != self.nodes.tolist()
                    or any(row['comparator'] != '>=' or not np.isfinite(row['threshold'])
                           or row['threshold'] < 0 for row in rows)):
                raise ValueError('Complete matched activity threshold schedule required')

    def decide(self, inputs, method, score, energy):
        value = public_snr_db(inputs)
        selected = self.policy['methods'][method][nearest_node(value, self.nodes)]
        return activity_decisions(score, energy, selected['threshold']), dict(
            public_estimated_snr_db=value, node_db=selected['node_db'],
            threshold=selected['threshold'], comparator='>=',
            policy_sha256=self.sha256, user_count_used_for_dispatch=False)


