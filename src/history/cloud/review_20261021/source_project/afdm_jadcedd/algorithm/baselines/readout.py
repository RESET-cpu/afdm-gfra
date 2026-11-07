"""Frozen Ding Eq. (27) thresholds selected using public observation power."""
import json
import numpy as np

from afdm_jadcedd.project import ROOT
from afdm_jadcedd.utils import sha256
from .ding import activity_decisions


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
