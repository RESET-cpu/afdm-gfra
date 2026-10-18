"""Read verified historical SNR results; never rerun a matching receiver.

Only the registered 500-scene panel is supported. Reuse requires identical
observations, phase, inference settings and frozen numerical sources.
"""
import numpy as np
from . import ROOT
from .storage import read, sha, arrays
from .settings import PHASE_CONFIG
from afdm_jadcedd.algorithm.unknown_phase_model import UnknownPhaseInput
from afdm_jadcedd.system.observation import array_sha256


class HistoricalSNR:
    def __init__(self, spec):
        self.spec = spec
        self.plan = None
        if not spec.get('reuse_plan'):
            return
        plan = read(ROOT / spec['reuse_plan'])
        controls = read(ROOT / spec.get('phase_config', PHASE_CONFIG))['phase_estimation']
        if plan['phase_controls'] != controls:
            return
        # Experimental entry points may change; frozen numerical code may not.
        for path, digest in plan['source_sha256'].items():
            if path.startswith('src/') and sha(ROOT / path) != digest:
                return
        self.plan = plan
        self.seeds = {seed: index for index, seed in enumerate(plan['seeds'])}

    def case(self, seed, parameters):
        if self.plan is None or seed not in self.seeds:
            return None
        if (parameters['users'] != 40 or parameters['frames'] != 16 or
                parameters['activity_probability'] != .1 or
                parameters.get('channel_model', 'D') != 'D' or
                parameters['snr_db'] not in self.plan['snr_db']):
            return None
        index = self.seeds[seed]
        parent = ROOT / self.plan['source_results'] / 'scenes' / f'scene{index:03d}'
        folder = parent / f'snr{int(parameters["snr_db"]):+03d}'
        base, ready = read(parent / 'READY.json'), read(folder / 'READY.json')
        for name, digest in [('pairing.npz', base['pairing_sha256']), ('truth.npz', base['truth_sha256'])]:
            if sha(parent / name) != digest:
                raise ValueError('Historical input/truth changed: ' + str(parent / name))
        if sha(folder / 'phase.npz') != ready['phase_sha256']:
            raise ValueError('Historical phase changed')
        pair = arrays(parent / 'pairing.npz')
        variance = base['power'] * 10**(-parameters['snr_db']/10)
        public = UnknownPhaseInput(pair['clean']+np.sqrt(variance)*pair['standard_noise'],
                                   pair['pilot'], variance, base['activity_prior'])
        hashes = {k: array_sha256(v) for k, v in public.arguments().items()}
        if hashes != ready['public_array_sha256']:
            raise ValueError('Historical observation identity changed')
        inputs = UnknownPhaseInput(public.observation, public.pilot, 1., public.activity_prior)
        truth = arrays(parent / 'truth.npz')
        record = read(folder / 'phase.json.gz')
        phase_values = arrays(folder / 'phase.npz')
        metadata = dict(read(parent / 'generation.json.gz'), snr_db=parameters['snr_db'],
                        generated_noise_variance=variance, noise_mode='estimated',
                        reused_input=str(folder.relative_to(ROOT)))
        return dict(index=index, snr=parameters['snr_db'], folder=folder, inputs=inputs, truth=truth,
                    metadata=metadata, phase=(phase_values, record, read(folder / 'phase.warnings.json')),
                    phase_sha256=ready['phase_sha256'])

    def result(self, case, method, receiver):
        if case is None or method == 'proposed_small':
            return None
        folder = case['folder']
        path = folder / f'{method}.metrics.json'
        if not path.exists():
            return None
        row, native = read(path), read(folder / f'{method}.record.json.gz')
        if (self.spec.get('reuse_require_same_device') and
                native['configuration'].get('device') != receiver.device):
            return None
        if not self.matches(method, receiver, native, case['inputs'].activity_prior):
            return None
        if row['status'] != 'COMPLETE' or row['shared_phase_sha256'] != case['phase_sha256']:
            raise ValueError('Historical result is incomplete or uses another phase')
        compact_path = folder / f'{method}.compact.npz'
        if sha(compact_path) != row['compact_sha256']:
            raise ValueError('Historical compact prediction changed')
        compact = arrays(compact_path)
        self.verify_metrics(compact, row['metrics'], case['truth'])
        return self.package(row, native, compact, [path, folder / f'{method}.record.json.gz', compact_path])

    @staticmethod
    def matches(method, receiver, record, activity_prior):
        if record.get('status') != 'COMPLETE' or record.get('noise_mode') != 'estimated':
            return False
        if record.get('supplied_noise_variance_used') is not False:
            return False
        configuration = record['configuration']
        if method == 'proposed':
            if configuration.get('activity_prior') != activity_prior:
                return False
            # Runtime metadata added by Receiver.infer, not algorithm controls.
            # Reused results retain their original CPU/MPS backend and timing.
            configuration = {k:v for k,v in configuration.items() if k not in ('device', 'activity_prior')}
        if configuration != receiver.configuration:
            return False
        if method != 'proposed' and record.get('inference_sha256') != receiver.signature:
            return False
        return True

    @staticmethod
    def verify_metrics(compact, metrics, truth):
        active = np.asarray(truth['activity'], bool)
        decision = np.asarray(compact['activity_decision'], bool)
        np.testing.assert_array_equal(compact['truth_activity'], truth['activity'])
        np.testing.assert_array_equal(decision, metrics['decisions'])
        np.testing.assert_allclose(compact['per_user_error'], metrics['per_user_error'], rtol=0, atol=0)
        np.testing.assert_allclose(np.sum(compact['per_user_error']), metrics['full_error'], rtol=8*np.finfo(float).eps, atol=0)
        np.testing.assert_allclose(np.sum(abs(truth['channel'])**2), metrics['signal_energy'], rtol=8*np.finfo(float).eps, atol=0)
        if (int(np.sum(active & ~decision)) != metrics['misses'] or
                int(np.sum(~active & decision)) != metrics['false_alarms']):
            raise ValueError('Historical activity counts differ from saved decisions')

    @staticmethod
    def package(row, native, compact, files):
        return dict(metrics=row['metrics'], compact=compact, receiver_seconds=row['receiver_seconds'],
                    iterations=native['iterations'], stopping_reason=native['stopping_reason'],
                    execution_device=native['configuration'].get('device', 'see native source'),
                    provenance={str(p.relative_to(ROOT)):sha(p) for p in files})
