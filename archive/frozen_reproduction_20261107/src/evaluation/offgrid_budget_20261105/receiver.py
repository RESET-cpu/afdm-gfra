"""Reuse the frozen solver with explicit search-budget and readout provenance."""
from copy import deepcopy
from importlib.util import module_from_spec, spec_from_file_location

import numpy as np

from algorithm.baseline._base import EstimatedNoiseBaselineReceiver
from algorithm.baseline._validation import inference_signature
from algorithm.baseline.offgrid_sbl import Settings
from project import ROOT
from system.receiver.atoms import MAX_FREQUENCY, ORDER
from system import config as physical
from utils import json_digest, read_json, sha256


class Receiver:
    def __init__(self, configuration):
        self.path = ROOT / configuration
        self.budget = read_json(self.path)
        cfg = self.budget
        if cfg['schema'] != 'afdm-offgrid-search-budget-v1':
            raise ValueError('Independent search-budget configuration required')
        if set(cfg['solver_changes']) != {
                'doppler_step', 'candidates_per_user', 'offset_candidates'}:
            raise ValueError('Only the three declared search controls may change')
        self.original = EstimatedNoiseBaselineReceiver(
            'offgrid_sbl', config=ROOT / cfg['base_configuration'], device='cpu')
        self.native_configuration = deepcopy(self.original.configuration)
        original_solver = self.original.base.configuration['methods']['offgrid_sbl']['solver']
        solver = dict(original_solver, **cfg['solver_changes'])
        if solver['iterations'] != cfg['unchanged_iterations'] or solver['iterations'] != 120:
            raise ValueError('Original iteration budget must remain 120')
        count = int(np.ceil(2 * MAX_FREQUENCY / solver['doppler_step'])) + 1
        if count != cfg['doppler_points'] or physical.N * ORDER != cfg['delay_points']:
            raise ValueError('Grid cardinality differs from the declared budget')
        self.original.base.settings = Settings(**solver)
        # Original calibration is checked by the unchanged constructor above.
        # Replacing settings does not make its thresholds newly calibrated.
        self.original.base.configuration['methods']['offgrid_sbl']['solver'] = solver
        self.original.base.signature = inference_signature(
            self.original.base.configuration, 'offgrid_sbl')
        self.original.configuration['base_configuration'] = deepcopy(
            self.original.base.configuration)
        self.original.signature = json_digest(dict(
            configuration=self.original.configuration,
            base=self.original.base.signature, sources=self.original.sources))
        for key in ('activity_policy', 'activity_readout'):
            if sha256(ROOT / cfg[key]) != cfg[key + '_sha256']:
                raise ValueError('Adopted activity readout changed: ' + key)
        spec = spec_from_file_location('offgrid_adopted_readout', ROOT / cfg['activity_readout'])
        self.readout = module_from_spec(spec)
        spec.loader.exec_module(self.readout)
        self.policy = self.readout.load_policy()
        self.signature = json_digest(dict(
            budget=cfg, solver=self.original.signature,
            adapter_sha256=sha256(__file__), policy_sha256=cfg['activity_policy_sha256']))

    def infer(self, inputs):
        arrays, record = self.original.infer(inputs)
        arrays['native_activity_decision'] = arrays['activity_decision'].copy()
        snr = self.readout.estimated_snr(
            float(np.mean(abs(inputs.observation) ** 2)),
            float(arrays['noise_variance_estimate']))
        threshold, node = self.readout.threshold('offgrid_sbl', snr, policy=self.policy)
        arrays['activity_decision'] = self.readout.decide(
            arrays['activity_score'], arrays['channel_energy'], threshold)
        record.update(
            budget_configuration=self.budget,
            budget_configuration_sha256=sha256(self.path),
            search_budget_inference_sha256=self.signature,
            native_activity_threshold=record['activity_threshold'],
            activity_threshold=float(threshold),
            readout_snr_node_db=float(self.policy['methods']['offgrid_sbl']['snr_nodes_db'][int(node)]),
            public_estimated_snr_db=snr,
            threshold_status='CURRENT_MAIN_SNR_RULE_TRANSFERRED_WITHOUT_REFITTING',
            threshold_scope=self.budget['scope'],
            activity_policy_sha256=self.budget['activity_policy_sha256'],
            new_threshold_calibration=False, backend='cpu',
            doppler_points=self.budget['doppler_points'],
            delay_points=self.budget['delay_points'])
        expected_coarse = inputs.operator.shape[1] * self.budget['delay_points'] * self.budget['doppler_points']
        expected_screened = inputs.operator.shape[1] * self.budget['solver_changes']['candidates_per_user']
        if record['coarse_columns'] != expected_coarse or record['screened_columns'] != expected_screened:
            raise ValueError('Actual dictionary sizes differ from the frozen budget')
        return arrays, record
