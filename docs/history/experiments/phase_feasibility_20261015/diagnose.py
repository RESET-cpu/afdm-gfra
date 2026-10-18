"""Check phase/channel ambiguity for the current unconstrained channel model.

This is a truth-based algebra diagnostic, not a receiver. The transformed
channel need not belong to the physical AFDM delay/Doppler model or its prior.
For invertible P_k, X'_k = solve(P_k, D(-delta) P_k X_k) exactly offsets a
delta change in the frame phase slope, including for spatial rank-one X_k.
"""
import argparse
import json
from pathlib import Path
import sys
import warnings

import numpy as np
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from afdm_jadcedd.experiment.generate import generate_case
from afdm_jadcedd.system import config as cfg
from afdm_jadcedd.system.pilot import PartialDFTPilot
from afdm_jadcedd.utils import sha256


def diagnose(seed):
    inputs, truth, _ = generate_case(seed, 0., .2647966452702405, fixed_active_users=1)
    k = int(np.flatnonzero(truth['activity'])[0])
    p = PartialDFTPilot(40, 16, seed + 10**12, input_size=16).dense().reshape(16, 40, 16)[:, k]
    x = truth['channel'][k].transpose(2, 0, 1).reshape(16, -1)
    beta = float(truth['phase_slopes'][k]); q = np.arange(16)
    px = np.einsum('qn,nc->qc', p, x, optimize=False)
    clean = np.exp(1j*q*beta)[:, None]*px
    rows = []
    for delta in (.001, .1, .37):
        alternative = np.linalg.solve(p, np.exp(-1j*q*delta)[:, None]*px)
        predicted = np.exp(1j*q*(beta+delta))[:, None]*np.einsum('qn,nc->qc', p, alternative, optimize=False)
        h = alternative.reshape(16, 16, 16).transpose(1, 2, 0)
        singular = np.linalg.svd(h.reshape(16, -1), compute_uv=False)
        relative = float(np.linalg.norm(predicted-clean)/np.linalg.norm(clean))
        spatial_ratio = float(singular[1]/singular[0])
        if not relative < 1e-11 or not spatial_ratio < 1e-11:
            raise AssertionError('Phase/channel equivalence failed numerical precision check')
        rows.append(dict(phase_slope_change_rad=delta, relative_observation_change=relative,
                         relative_channel_change=float(np.linalg.norm(alternative-x)/np.linalg.norm(x)),
                         spatial_second_first_singular_ratio=spatial_ratio))
    return dict(status='PASS', scope='Truth-based algebra diagnostic; not receiver performance',
                limitation='The alternative full channel is not asserted to satisfy the physical AFDM model or prior',
                seed=seed, active_user=k, pilot_rank=int(np.linalg.matrix_rank(p)),
                pilot_condition=float(np.linalg.cond(p)),
                frame_duration_s=(cfg.N+cfg.N_CPP)/cfg.BANDWIDTH_HZ,
                doppler_phase_alias_period_hz=cfg.BANDWIDTH_HZ/(cfg.N+cfg.N_CPP), checks=rows,
                source_sha256=sha256(Path(__file__)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, default=202610156701)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    with warnings.catch_warnings(record=True) as caught, threadpool_limits(1):
        warnings.simplefilter('always', RuntimeWarning)
        result = diagnose(args.seed)
    result['warnings'] = [dict(message=str(w.message), filename=w.filename, line=w.lineno) for w in caught]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(status=result['status'], output=str(args.output), checks=len(result['checks']))))
