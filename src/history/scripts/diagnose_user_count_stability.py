"""Post-hoc fixed-input stability diagnosis; oracle variants are NOT receiver results."""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
from dataclasses import replace
from pathlib import Path
import sys
import time
import numpy as np
import torch
from threadpoolctl import threadpool_limits
import evaluate_saved_baseline_inputs as paired
from benchmark_receiver_execution import GraphForward
from afdm_jadcedd.algorithm.proposed.receiver import Receiver
from afdm_jadcedd.algorithm.proposed.configuration import verify
from afdm_jadcedd.system.phase import phase_operator

ROOT = paired.ROOT
OUT = ROOT/'results/user_count_stability_20261019'


def run(variant, condition, scene):
    output = OUT/f'scene{scene:03d}_users{20*(condition+1)}_{variant}'
    if output.exists():
        raise ValueError('Fresh diagnostic output required')
    plan = paired.read(ROOT/'results/new_models_paired_20261019_v2/user_count/PLAN.json')
    paired.verify_sources(plan)
    index = paired.read(Path(plan['input_package'])/'inputs/INDEX.json')['experiments']['user_count']['cases']
    inputs, truth, hashes, proof, generation, phase = paired.load_case(plan, index, scene, condition)
    config = (paired.read(ROOT/'configs/proposed.json') if variant == 'old_networks'
              else plan['experiment']['proposed_bundles']['proposed']['configuration'])
    verified = verify(config)
    known_noise = variant in ('oracle_noise', 'oracle_both')
    known_phase = variant in ('oracle_phase', 'oracle_both')
    actual_noise = float(generation['generated_noise_variance'])
    if known_phase:
        folder = Path(plan['baseline_results'])/f'scene{scene:03d}/condition{condition:02d}'
        pilot = paired.arrays(folder/'public.npz')['pilot']
        inputs = replace(inputs, operator=phase_operator(pilot, truth['phase_slopes']))
    if known_noise:
        inputs = replace(inputs, noise_variance=actual_noise)
    torch.set_num_threads(1)
    model = Receiver(config, device='cuda') if known_noise else paired.EstimatedNoiseProposedReceiver(config, device='cuda')
    base = model if known_noise else model.base
    base.model.first = GraphForward(base.model.first)
    base.model.second = GraphForward(base.model.second)
    experiment = dict(variant=variant, condition=condition, scene=scene, config=config,
        input_sha256=hashes, conditional_operator_sha256=paired.array_sha256(inputs.operator),
        verified_weights=verified, original_inputs=proof, actual_noise_variance=actual_noise,
        oracle_noise=known_noise, oracle_phase=known_phase,
        truth_used_in_inference=known_noise or known_phase,
        truth_used_in_diagnostics=True, scoring_truth_does_not_modify_updates=True,
        purpose='Post-hoc diagnosis on already observed cases; no hyperparameter selection or formal performance claim',
        source_sha256=plan['source_and_weight_sha256'] | {str(Path(__file__)):paired.sha(Path(__file__)),
            str(ROOT/'scripts/benchmark_receiver_execution.py'):paired.sha(ROOT/'scripts/benchmark_receiver_execution.py')})
    paired.save(output/'PLAN.json', experiment)
    rows = []
    scale = config['scale']; target = truth['channel']/scale
    energy = float(np.sum(abs(target)**2)); active = truth['activity'].astype(bool)
    def observe(row, state, query, covariance, *unused):
        error = query-target; variance = float(np.trace(covariance).real/len(covariance))
        nmse = float(np.sum(abs(state.mean-target)**2)/energy)
        conditional_nmse = float(np.sum(abs(state.conditional_mean[active]-target[active])**2)/energy)
        values = dict(iteration=row['iteration'], nmse_db=float(10*np.log10(nmse)),
            active_conditional_nmse_db=float(10*np.log10(conditional_nmse)),
            misses=int(np.count_nonzero((state.activity<.5)&active)),
            false_alarms=int(np.count_nonzero((state.activity>=.5)&~active)),
            query_variance=variance, actual_query_mse=float(np.mean(abs(error)**2)),
            query_mse_to_label=float(np.mean(abs(error)**2)/variance),
            supported=row['moment_samples']>0, site_accepted=row['site_accepted'],
            raw_site_residual=row['raw_site_residual'], estimate_change=row['estimate_change'])
        if row['iteration'] in (1,2,5,10,20,50,100,200,400,600):
            packed = error.transpose(1,0,2,3).reshape(16,-1)
            cov = packed@packed.conj().T/packed.shape[1]
            eigen = np.linalg.eigvalsh(cov)
            values['error_largest_antenna_eigen_fraction'] = float(eigen[-1]/eigen.sum())
        if row['iteration'] in (1,20,100,600):
            paired.save_arrays(output/f'iteration{row["iteration"]:03d}.npz', dict(query=query,
                covariance=covariance, estimate=state.mean, probabilities=state.activity))
        rows.append(values)
    with threadpool_limits(1):
        prediction, record = model.infer(inputs, observer=observe)
    metrics = paired.score_arrays(prediction, truth)
    summary = dict(variant=variant, users=len(active), active_users=int(active.sum()),
        iterations=record['iterations'], stopping_reason=record['stopping_reason'], seconds=record['seconds'],
        metrics=metrics, actual_noise_variance=actual_noise,
        supplied_or_estimated_noise=actual_noise if known_noise else record['noise_variance_estimate'],
        supported_iterations=record['supported_query_iterations'],
        oracle=known_noise or known_phase,
        best_iteration_for_diagnosis_only=min(rows,key=lambda x:x['nmse_db']), last_iteration=rows[-1])
    if variant == 'new_networks' and scene == 0:
        reference = paired.arrays(ROOT/'results/new_models_paired_20261019_v2/user_count/scene000'/f'condition{condition:02d}'/'proposed.prediction.npz')
        summary['exact_replay'] = {k:bool(np.array_equal(v,reference[k])) for k,v in prediction.items()}
        assert all(summary['exact_replay'].values()), 'Diagnostic observer or execution altered inference'
    paired.save(output/'SUMMARY.json', summary)
    paired.save(output/'TRACE.json', rows)
    paired.save(output/'record.json', record)
    paired.save_arrays(output/'prediction.npz', prediction)
    print({k:summary[k] for k in ('variant','users','iterations','stopping_reason','seconds','supported_iterations')},
          'NMSE',metrics['nmse_db'], 'BEST_DIAGNOSTIC',summary['best_iteration_for_diagnosis_only']['nmse_db'], flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--variant', required=True, choices=('new_networks','old_networks','oracle_noise','oracle_phase','oracle_both'))
    parser.add_argument('--condition', type=int, required=True)
    parser.add_argument('--scene', type=int, default=0)
    args = parser.parse_args()
    run(args.variant, args.condition, args.scene)
