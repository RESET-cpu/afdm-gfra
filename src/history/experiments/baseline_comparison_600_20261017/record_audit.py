"""Check stored input pairing and native records without changing frozen runs.

Partial mode reports only completed records. Final mode requires the separate
21,000-output metric audit and all planned records; it never certifies a prefix.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'experiments/baseline_comparison_600_20261017'))
from run import OUT, arrays, digest, public_input, read, save, sha, verify_sources
import numpy as np


def audit(partial=False):
    spec = verify_sources()
    counts, reasons, warning_cases = Counter(), defaultdict(Counter), Counter()
    noise_ratios, iterations = defaultdict(list), defaultdict(list)
    conditions, seen = set(), set()
    for path in sorted((OUT / 'scenes').glob('*/*/*.metrics.json')):
        row = read(path)
        assert row['status'] == 'COMPLETE', path
        scene, snr, method = row['scene'], row['snr'], row['method']
        assert 0 <= scene < spec['scenes'] and snr in spec['snr_db'] and method in spec['methods']
        key = (scene, snr, method)
        assert key not in seen
        seen.add(key)
        folder = path.parent
        parent = folder.parent
        ready = read(folder / 'READY.json')
        if (scene, snr) not in conditions:
            inp = public_input(parent, snr)
            assert digest(inp.arguments()) == ready['public_array_sha256']
            assert sha(folder / 'phase.npz') == ready['phase_sha256']
            assert all(np.isfinite(v).all() for v in arrays(folder / 'phase.npz').values())
            conditions.add((scene, snr))
        record = read(folder / (method + '.record.json.gz'))
        assert record['noise_mode'] == spec['noise_mode']
        assert record['benchmark_truth_used_in_inference'] is False
        assert record['phase_sha256'] == ready['phase_sha256'] == row['shared_phase_sha256']
        if spec['noise_mode'] == 'estimated':
            assert record['supplied_noise_variance_used'] is False
            variance = float(record['noise_variance_estimate'])
            assert np.isfinite(variance) and variance > 0
            sigma = read(parent / 'READY.json')['power'] * 10 ** (-snr / 10)
            noise_ratios[method].append(variance / sigma)
        compact_path = folder / (method + '.compact.npz')
        assert sha(compact_path) == row['compact_sha256']
        compact = arrays(compact_path)
        native_vectors = {k: v for k, v in compact.items() if k not in ['per_user_error', 'truth_activity']}
        for name, identity in digest(native_vectors).items():
            assert record['output_array_sha256'][name] == identity
        counts[method] += 1
        reasons[method][record.get('stopping_reason', 'UNREPORTED')] += 1
        iterations[method].append(int(record['iterations']))
        if read(folder / (method + '.warnings.json')):
            warning_cases[method] += 1
    if not partial:
        assert read(OUT / 'VERIFICATION.json')['status'] == 'PASS'
        assert len(conditions) == spec['expected_conditions'] == 4200
        assert len(seen) == spec['expected_receiver_runs'] == 21000
        assert all(counts[m] == 4200 for m in spec['methods'])
    result = dict(status='PARTIAL_CHECK' if partial else 'PASS', checked_unix=time.time(),
                  receiver_records=len(seen), reconstructed_inputs=len(conditions), counts=dict(counts),
                  stopping_reasons={m: dict(c) for m, c in reasons.items()},
                  warning_cases=dict(warning_cases),
                  noise_ratio_summary={m: dict(mean=float(np.mean(v)), minimum=float(min(v)), maximum=float(max(v)))
                                       for m, v in noise_ratios.items()},
                  iterations={m: dict(mean=float(np.mean(v)), minimum=min(v), maximum=max(v))
                              for m, v in iterations.items()},
                  scope='Stored public inputs, phase identities, native scalar/vector identities and information conditions. Full-channel metrics are checked by report.py.')
    save(OUT / ('PARTIAL_RECORD_AUDIT.json' if partial else 'RECORD_AUDIT.json'), result)
    print(json.dumps({k: result[k] for k in ['status', 'receiver_records', 'reconstructed_inputs', 'counts']}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--partial', action='store_true')
    audit(parser.parse_args().partial)
