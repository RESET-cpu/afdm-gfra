"""Frozen first-layer activity statistics; no optimizer or receiver replacement.

The validation pool is independent of training scenes, but was already used for
checkpoint selection. The second half is held out from threshold calibration,
not an untouched final test set. Known phase and noise are used by this pool.
"""
import json
import math
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = Path(r'D:\afdm-gfra-cpu\runs\lstmp_refinenet_50000_fixed_budget_20261019')
OUT = ROOT / 'results/activity_energy_comparison_20261019'
os.environ['AFDM_LSTMP_ROOT'] = str(ROOT)
os.environ['AFDM_LSTMP_CONFIG'] = str(RUN / 'source_code/experiments/lstmp_candidate_20261019/reuse_50000_fixed_budget.json')
sys.path.insert(0, str(RUN / 'source_code'))
import numpy as np
import torch
from scipy.stats import rankdata
from threadpoolctl import threadpool_limits
from experiments.lstmp_candidate_20261019 import common, data, receiver
from afdm_jadcedd.algorithm.proposed.activity import FrozenEvidence


def auc(y, s):
    positives, negatives = int(y.sum()), int((~y).sum())
    if not positives or not negatives:
        return None
    ranks = rankdata(s, method='average')
    return float((ranks[y].sum() - positives * (positives + 1) / 2) / (positives * negatives))


def rates(y, predicted):
    return dict(active=int(y.sum()), inactive=int((~y).sum()),
                misses=int((y & ~predicted).sum()), false_alarms=int((~y & predicted).sum()),
                missed_detection_rate=float((~predicted[y]).mean()),
                false_alarm_rate=float(predicted[~y].mean()))


def calibrated_threshold(y, s, target=.01):
    # Decisions use s > threshold. This order statistic permits at most floor
    # (target * n_inactive) calibration false alarms; ties are conservative.
    negative = np.sort(s[~y])
    permitted = int(math.floor(target * len(negative)))
    return float(negative[len(negative) - permitted - 1])


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    if (RUN / 'RUNNING.lock').exists():
        raise RuntimeError('Training must remain paused')
    OUT.mkdir(parents=True)
    started = time.time()
    plan = dict(scope='Frozen first-layer diagnostic; no final five-layer performance claim',
        calibration_scene_indices=list(range(240)), confirmation_scene_indices=list(range(240, 480)),
        selection='First twenty complete 24-condition cycles, split into ten cycles each before reading scores',
        threshold_rule='Each statistic independently targets <=1% calibration false alarms; confirmation labels never select thresholds',
        caveat='Validation pool was used to select the depth-1 checkpoint; confirmation is not an untouched test set',
        phase_mode=common.CONFIG['receiver']['phase_mode'], noise_mode=common.CONFIG['receiver']['noise_mode'],
        optimizer_updates=0, inference_activity_labels_used=False, created_unix=started)
    common.save_json(OUT / 'PLAN.json', plan)
    torch.set_num_threads(4)
    threadpool_limits(4)
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    torch.backends.cudnn.benchmark = True
    score_path = ROOT / common.CONFIG['pretrained_score']['path']
    classifier_path = ROOT / 'runs/proposed_auxiliary_100_cuda_graph_20261019/n50000/activity/evidence_best.pt'
    selected_path = RUN / 'checkpoints/depth_1/best.pt'
    protected = {str(p): common.sha(p) for p in (score_path, classifier_path, selected_path, RUN / 'checkpoints/depth_2/last.pt')}
    first = torch.load(score_path, map_location='cpu', weights_only=False)
    old = FrozenEvidence(classifier_path, device='cuda')
    cases = data.Cases('validation', first['global_complex_rms'], 'cuda')
    torch.manual_seed(common.CONFIG['seed'] + 1)
    model = receiver.Receiver()
    model.add_layer(first['state_dict'])
    model.cuda().eval()
    model.use_checkpoint = False
    all_results = {}
    for stage in ('original_score', 'finetuned_depth1_score'):
        if stage == 'finetuned_depth1_score':
            model.load_state_dict(torch.load(selected_path, map_location='cpu', weights_only=False)['state'])
        records = []
        with torch.no_grad():
            for index in range(480):
                public, labels, info = cases[index]
                outputs, diagnostics, messages = model(public, return_messages=True)
                r, mu = messages[0]['query'], messages[0]['conditional']
                v = float(diagnostics[0]['query_variance'])
                nv = r.new_full((len(r),), v)
                dimension = r[0].numel() // 2
                er = r.double().square().flatten(1).sum(1) / dimension
                em = mu.double().square().flatten(1).sum(1) / dimension
                old_logits = old.network(r, nv, mu).double()
                old_logits += math.log(public['rho'] / (1-public['rho'])) - math.log(old.training_class_prior / (1-old.training_class_prior))
                # Normalized active prior power beta=1 is a declared approximation;
                # never insert per-user true channel power into the likelihood.
                gaussian = dimension * (er / (v * (v+1)) - math.log1p(1/v)) + math.log(public['rho'] / (1-public['rho']))
                values = dict(message_energy_over_v=er/v,
                    conditional_mean_energy=em, conditional_mean_energy_over_v=em/v,
                    gaussian_prior_log_odds=gaussian, pretrained_classifier_log_odds=old_logits,
                    candidate_classifier_log_odds=outputs[0][1].double())
                values = {k: t.cpu().numpy() for k, t in values.items()}
                if not all(np.isfinite(t).all() for t in values.values()):
                    raise FloatingPointError(f'Nonfinite statistic at {stage}/{index}; no sample removed')
                active = labels['active'].bool().cpu().numpy()
                for user in range(len(active)):
                    records.append(dict(scene=index, condition=index % 24, user=user,
                        active=bool(active[user]), variance=v, **{k: float(t[user]) for k, t in values.items()}))
                if (index+1) % 120 == 0:
                    print(json.dumps(dict(stage=stage, scenes=index+1, total=480,
                        elapsed_seconds=round(time.time()-started, 1))), flush=True)
        names = list(values)
        arrays = {name: np.asarray([row[name] for row in records])
                  for name in ('scene', 'condition', 'user', 'active', 'variance', *names)}
        np.savez_compressed(OUT / f'{stage}_statistics.npz', **arrays)
        calibration = arrays['scene'] < 240
        confirmation = ~calibration
        y = arrays['active']
        comparisons = {}
        for name in names:
            s = arrays[name]
            t = calibrated_threshold(y[calibration], s[calibration])
            predicted = s > t
            by_condition = []
            condition_thresholds = np.zeros(len(s))
            for condition in range(24):
                condition_mask = arrays['condition'] == condition
                cal = condition_mask & calibration
                confirm = condition_mask & confirmation
                tc = calibrated_threshold(y[cal], s[cal])
                condition_thresholds[condition_mask] = tc
                by_condition.append(dict(condition=data.condition_for('validation', condition),
                    condition_id=condition, auc=auc(y[confirm], s[confirm]),
                    global_threshold_rates=rates(y[confirm], predicted[confirm]),
                    condition_threshold=tc, condition_threshold_rates=rates(y[confirm], s[confirm] > tc)))
            comparisons[name] = dict(global_threshold=t, calibration=rates(y[calibration], predicted[calibration]),
                confirmation=rates(y[confirmation], predicted[confirmation]),
                confirmation_auc=auc(y[confirmation], s[confirmation]),
                mean_condition_auc=float(np.mean([row['auc'] for row in by_condition])),
                condition_calibrated_confirmation=rates(y[confirmation], s[confirmation] > condition_thresholds[confirmation]),
                by_condition=by_condition)
            if name.endswith('log_odds'):
                comparisons[name]['uncalibrated_threshold_zero_confirmation'] = rates(y[confirmation], s[confirmation] > 0)
        all_results[stage] = comparisons
    assert all(common.sha(Path(path)) == digest for path, digest in protected.items())
    report = dict(plan=plan, results=all_results, protected_sha256=protected,
        protected_assets_unchanged=True, elapsed_seconds=time.time()-started,
        statistics=dict(message_energy_over_v='||r||^2/(4096*v)',
            conditional_mean_energy='||mu||^2/4096, before multiplying by activity probability',
            conditional_mean_energy_over_v='||mu||^2/(4096*v)',
            gaussian_prior_log_odds='beta=1 zero-mean isotropic Gaussian approximation with public rho',
            pretrained_classifier_log_odds='Completed AWGN classifier with prior correction exactly once',
            candidate_classifier_log_odds='Frozen current head output; not retrained for this comparison'))
    common.save_json(OUT / 'REPORT.json', report)
    print(json.dumps({stage: {name: {k: v for k, v in value.items() if k != 'by_condition'}
        for name, value in methods.items()} for stage, methods in all_results.items()}), flush=True)


if __name__ == '__main__':
    main()
