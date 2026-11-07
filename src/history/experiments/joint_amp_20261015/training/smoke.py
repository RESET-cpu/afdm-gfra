"""Pretraining numerical checks and measured throughput; no receiver data."""
from copy import deepcopy
import json
import math
import os
from pathlib import Path
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'src'))
import numpy as np
import torch
from afdm_jadcedd.algorithm.joint_amp.network import JointScoreNetwork
from afdm_jadcedd.algorithm.joint_amp.training import transform_channels, make_batch, objective, cpu_state, utc
from afdm_jadcedd.algorithm.baselines.ldamp.representation import Representation
from afdm_jadcedd.utils import write_json


def main():
    output = ROOT / 'runs/joint_amp_20261015/smoke_v2'
    output.mkdir(parents=True, exist_ok=False)
    start = time.time()
    write_json(output / 'PROCESS.json', dict(pid=os.getpid(), started_utc=utc(),
        timeout_seconds=600, alive=True, cpu_steps=64, mps_steps=100))
    try:
        torch.set_num_threads(1)
        torch.manual_seed(202610159010)
        rng = np.random.default_rng(202610159011)
        prior = json.loads((ROOT / 'data/proposed/prior_definition.json').read_text())
        bank = np.load(ROOT / 'data/proposed/train_channel.npy', mmap_mode='r')
        coefficients = transform_channels(bank, np.arange(256), prior['global_complex_rms'], Representation())
        recipe = dict(active_batch_size=4, phase_augmentation=True)
        model = JointScoreNetwork(sigma_data=math.sqrt(prior['normalized_mean_element_power'] / 2))
        optimizer = torch.optim.Adam(model.parameters(), lr=3e-4)
        phases = []
        for device, steps, count in [('cpu', 64, 4), ('mps', 100, 64)]:
            model = model.to(device)
            optimizer = torch.optim.Adam(model.parameters(), lr=3e-4)
            recipe['active_batch_size'] = count
            losses = []
            phase_start = time.time()
            for step in range(steps):
                batch = [item.to(device) for item in make_batch(coefficients, rng, recipe)]
                optimizer.zero_grad(set_to_none=True)
                values = objective(model, *batch)
                if not bool(torch.isfinite(values[0])):
                    raise FloatingPointError('Nonfinite smoke loss')
                values[0].backward()
                norm = torch.nn.utils.clip_grad_norm_(model.parameters(), 10.)
                if not bool(torch.isfinite(norm)):
                    raise FloatingPointError('Nonfinite smoke gradient')
                optimizer.step()
                losses.append([float(item.detach().cpu()) for item in values])
                if time.time() - start > 600:
                    raise TimeoutError('Smoke hard timeout')
            elapsed = time.time() - phase_start
            phases.append(dict(device=device, steps=steps, active_batch=count, inactive_batch=count,
                elapsed_seconds=elapsed, steps_per_second=steps / elapsed,
                estimated_63342_step_training_seconds=63342 * elapsed / steps,
                first_losses=losses[0], last_losses=losses[-1]))
            print(json.dumps(phases[-1]), flush=True)
        model.eval()
        cpu = deepcopy(model).to('cpu').eval()
        noisy = torch.from_numpy(np.array(coefficients[:2], copy=True))
        # High noise tests the probability derivative away from a saturated
        # p=1. Strong active low-noise examples do not cover that chain term.
        variance = torch.full((2, 16), 100.)
        noisy = noisy + torch.from_numpy(rng.standard_normal(noisy.shape, dtype=np.float32)) * torch.sqrt(variance[:, None, :, None, None] / 2)
        direction = torch.from_numpy(rng.standard_normal(noisy.shape, dtype=np.float32))
        def rel(a, b):
            return float((a - b).norm() / b.norm().clamp_min(1e-20))
        cmean, cjvp = torch.func.jvp(lambda value: cpu(value, variance, .1), (noisy,), (direction,))
        gmean, gjvp = torch.func.jvp(lambda value: model(value, variance.to('mps'), .1),
            (noisy.to('mps'),), (direction.to('mps'),))
        checks = dict(cpu_mps_mean_relative_error=rel(gmean.cpu(), cmean),
            cpu_mps_jvp_relative_error=rel(gjvp.cpu(), cjvp),
            sample_independence_max_error=float((cpu(noisy[:1], variance[:1], .1) - cmean[:1]).abs().max()))
        double = deepcopy(cpu).double()
        x, d, v = noisy.double(), direction.double(), variance.double()
        result, derivative = torch.func.jvp(lambda value: double.components(value, v, .1), (x,), (d,))
        chain = (result['probability'][:, None, None, None, None] * derivative['conditional_mean']
                 + derivative['probability'][:, None, None, None, None] * result['conditional_mean'])
        frozen_p = result['probability'][:, None, None, None, None] * derivative['conditional_mean']
        epsilon = 1e-5
        finite_difference = (double(x + epsilon * d, v, .1) - double(x - epsilon * d, v, .1)) / (2 * epsilon)
        checks.update(product_rule_relative_error=rel(derivative['mean'], chain),
            detached_probability_omitted_term_relative_norm=rel(derivative['mean'], frozen_p),
            jvp_finite_difference_relative_error=rel(derivative['mean'], finite_difference),
            probability_direction_norm=float(derivative['probability'].norm()),
            score_identity_max_error=float((double.score(x, v, .1) * (v[:, None, :, None, None] / 2) + x - result['mean']).abs().max()))
        if checks['cpu_mps_mean_relative_error'] > 1e-4 or checks['cpu_mps_jvp_relative_error'] > 1e-4:
            raise AssertionError(checks)
        if checks['sample_independence_max_error'] > 2e-5 or checks['jvp_finite_difference_relative_error'] > 3e-5:
            raise AssertionError(checks)
        if checks['product_rule_relative_error'] > 1e-10 or checks['probability_direction_norm'] <= 1e-12:
            raise AssertionError(checks)
        result = dict(status='PASS', phases=phases, checks=checks,
            parameters=sum(p.numel() for p in model.parameters()),
            weights_scope='Disposable smoke initialization; formal training starts independently from random',
            elapsed_seconds=time.time() - start, completed_utc=utc(), pid=os.getpid(), alive=False)
        write_json(output / 'SMOKE.json', result)
        write_json(output / 'STATUS.json', result)
        print(json.dumps(result), flush=True)
    except BaseException as error:
        write_json(output / 'STATUS.json', dict(status='FAILED', error=repr(error), traceback=traceback.format_exc(),
            elapsed_seconds=time.time() - start, completed_utc=utc(), pid=os.getpid(), alive=False))
        raise


if __name__ == '__main__':
    main()
