"""Verify information conditions and native-receiver parity on saved public input."""
import json
from pathlib import Path
import subprocess
import sys
import warnings
import argparse

import numpy as np
import torch
from threadpoolctl import threadpool_limits

sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'src'))

from afdm_jadcedd.algorithm.registry import ALGORITHMS
from afdm_jadcedd.algorithm.unknown_phase_baselines import build_estimated_phase_receiver
from afdm_jadcedd.algorithm.unknown_phase_model import load_input
from afdm_jadcedd.system.phase import phase_operator
from afdm_jadcedd.project import ROOT
from afdm_jadcedd.utils import sha256, write_json


parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parent)
OUT = parser.parse_args().output.resolve()
OUT.mkdir(parents=True, exist_ok=True)
SOURCE = ROOT/'results/unknown_phase_baselines_20261015/evaluation/scene000/snr+00/input.npz'


def cli(arguments, log):
    result = subprocess.run([sys.executable, '-B', str(ROOT/'run.py'), *map(str, arguments)],
                            cwd=ROOT, capture_output=True, text=True)
    (OUT/log).write_text(result.stdout+result.stderr)
    if result.returncode:
        raise RuntimeError(f'CLI failed; see {log}')
    return result.stdout


def main():
    checks = dict(scope='Integration smoke check; no population performance claim',
                  source=str(SOURCE.relative_to(ROOT)), source_sha256=sha256(SOURCE),
                  methods={}, paired_generation={}, cli={})
    for mode in ('estimated', 'known'):
        target = OUT/('paired_'+mode)
        args = ['simulate', '--seed', '202610159101', '--snr', '0', '--users', '3', '--output', target]
        if mode == 'known':
            args += ['--phase-mode', mode]
        cli(args, 'simulate_'+mode+'.log')
        args = ['run', '--method', 'gamp', '--input', target/'input.npz', '--output', target/'gamp.npz', '--device', 'cpu']
        if mode == 'known':
            args += ['--phase-mode', mode]
        cli(args, 'run_'+mode+'.log')
        record = json.loads((target/'gamp.json').read_text())
        checks['cli'][mode] = dict(status=record['status'], method=record['method'], input_sha256=sha256(target/'input.npz'))
    with np.load(OUT/'paired_estimated/input.npz') as unknown, np.load(OUT/'paired_known/input.npz') as known, \
         np.load(OUT/'paired_estimated/truth.npz') as truth, np.load(OUT/'paired_known/truth.npz') as truth_known:
        for key in ('observation', 'noise_variance', 'activity_prior'):
            assert np.array_equal(unknown[key], known[key]), key
        assert set(unknown.files) == {'observation', 'pilot', 'noise_variance', 'activity_prior'}
        assert set(known.files) == {'observation', 'operator', 'noise_variance', 'activity_prior'}
        assert truth.files == truth_known.files
        assert all(np.array_equal(truth[k], truth_known[k]) for k in truth.files)
        operator = phase_operator(unknown['pilot'], truth['phase_slopes'])
        np.testing.assert_allclose(operator, known['operator'], rtol=1e-13, atol=1e-13)
        checks['paired_generation'] = dict(status='PASS', observation_noise_prior_truth_identical=True,
            known_operator_max_error=float(np.max(abs(operator-known['operator']))),
            estimated_input_fields=unknown.files, known_input_fields=known.files)
    inputs = load_input(SOURCE)
    phase_reference = None
    torch.set_num_threads(1)
    with threadpool_limits(1):
        for method in ALGORITHMS:
            receiver = build_estimated_phase_receiver(method, device='auto')
            output = OUT/(method+'.npz')
            record = receiver.run(SOURCE, output)
            with np.load(output) as saved:
                arrays = {key:saved[key] for key in saved.files}
            assert record['status'] == 'COMPLETE'
            assert record['truth_used_in_inference'] is False
            assert all(np.isfinite(v).all() for v in arrays.values())
            if phase_reference is None:
                phase_reference = arrays['phase_slopes']
            assert np.array_equal(phase_reference, arrays['phase_slopes'])
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always', RuntimeWarning)
                native, native_record = receiver.base.infer(inputs.at_estimated_phase(arrays['phase_slopes']))
            write_json(OUT/(method+'_native.warnings.json'), [dict(category=w.category.__name__,
                message=str(w.message), filename=w.filename, lineno=w.lineno) for w in caught])
            parity = {key:bool(np.array_equal(value, arrays[key])) for key,value in native.items()}
            assert all(parity.values()), (method, parity)
            checks['methods'][method] = dict(status='PASS', native_array_exact_parity=parity,
                finite=True, truth_used_in_inference=False, phase_identical_across_methods=True,
                output_sha256=sha256(output), iterations=record['iterations'],
                inference_sha256=record['inference_sha256'])
            write_json(OUT/'CHECKS.json', checks)
            print(method+' PASS', flush=True)
    verification = json.loads(cli(['verify'], 'verify.log'))
    assert all(v['status']=='PASS' for v in verification.values())
    checks['asset_verification'] = verification
    previous = json.loads((Path(__file__).resolve().parent/'before/configs/mainline_assets.json').read_text())['sha256']
    changed = [path for path,digest in previous.items() if sha256(ROOT/path) != digest]
    assert changed == ['src/afdm_jadcedd/experiment/run.py'], changed
    checks['original_frozen_assets_changed'] = changed
    checks['status'] = 'PASS'
    write_json(OUT/'CHECKS.json', checks)
    print('All integration checks PASS', flush=True)


if __name__ == '__main__':
    main()
