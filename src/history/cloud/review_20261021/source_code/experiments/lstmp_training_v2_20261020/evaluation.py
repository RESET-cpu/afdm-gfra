"""Complete validation, including conditional means and user probabilities."""
import math
import time
import torch
from experiments.lstmp_candidate_20261019 import receiver as base
from experiments.lstmp_candidate_20261019.common import check_budget
from .objectives import layer_terms, loss_components


def metrics(output, labels, statistics):
    row = base.metrics([(output['estimate'], output['logits'])], labels)
    h, a = layer_terms(output, labels, statistics)
    active = labels['active'].bool()
    conditional_error = (output['conditional'].detach().double() -
                         labels['x'].double()).square().flatten(1).sum(1)
    scale2 = labels['physical_scale'] ** 2
    row.update(channel_loss=float(h), activity_loss=float(a), selection_loss=float(h + a),
               conditional_error_energy=float(conditional_error[active].sum()) * scale2,
               activity_bce_sum=row['activity_bce'] * len(active))
    return row


def summarize(rows):
    result = base.summarize_rows(rows)
    for key in ('channel_loss', 'activity_loss', 'selection_loss'):
        result[key] = sum(r[key] for r in rows) / len(rows)
    error = sum(r['conditional_error_energy'] for r in rows)
    energy = result['active_truth_energy']
    result.update(conditional_error_energy=error, conditional_nmse=error / energy,
                  conditional_nmse_db=10 * math.log10(error / energy) if error > 0 else None,
                  pooled_activity_bce=sum(r['activity_bce_sum'] for r in rows) /
                    (result['active'] + result['inactive']))
    return result


def by_condition(rows):
    groups = {}
    for row in rows:
        key = tuple(sorted(dict(row['condition'], snr_db=row['snr']).items()))
        groups.setdefault(key, []).append(row)
    return [dict(condition=dict(key), **summarize(group)) for key, group in groups.items()]


def evaluate(model, cases, statistics, *, started=None, on_progress=None):
    model.eval()
    rows = []
    with torch.no_grad():
        for index in range(len(cases)):
            if started is not None:
                check_budget(started)
            base.synchronize(cases.device)
            before = time.perf_counter()
            public, labels, info = cases[index]
            base.synchronize(cases.device)
            ready = time.perf_counter()
            calls_before = model.score_evaluations
            outputs, diagnostics, messages = model(public, return_messages=True)
            base.synchronize(cases.device)
            finished = time.perf_counter()
            components = loss_components(outputs, labels, statistics)
            layer_metrics = [metrics(output, labels, statistics) for output in outputs]
            active = labels['active'].bool()
            for diag, message in zip(diagnostics, messages):
                error = (message['query'] - labels['x']).square()
                diag.update(query_mse=float(2 * error.mean()),
                            query_active_mse=float(2 * error[active].mean()),
                            query_inactive_mse=float(2 * error[~active].mean()) if (~active).any() else None)
            last = outputs[-1]
            per_user = lambda x: x.detach().double().square().flatten(1).sum(1).cpu().tolist()
            row = dict(**info, case_index=index, loss=float(components['total']),
                       **layer_metrics[-1], diagnostics=diagnostics, layer_metrics=layer_metrics,
                       user_probabilities=torch.sigmoid(last['logits']).cpu().tolist(),
                       user_logits=last['logits'].cpu().tolist(),
                       user_activity=labels['active'].cpu().tolist(),
                       user_truth_energy=per_user(labels['x']),
                       user_effective_error=per_user(last['estimate'] - labels['x']),
                       user_conditional_error=per_user(last['conditional'] - labels['x']),
                       user_conditional_energy=per_user(last['conditional']),
                       user_energy_coordinates='fixed RMS normalized; conditional error is supervised only for a=1',
                       score_forward_calls=model.score_evaluations - calls_before,
                       preparation_seconds=ready - before, inference_seconds=finished - ready,
                       total_seconds=finished - before)
            if not all(math.isfinite(row[k]) for k in ('loss', 'selection_loss', 'nmse')):
                raise FloatingPointError(f'Nonfinite validation: position {index}, seed {info["seed"]}; retained')
            rows.append(row)
            if on_progress and ((index + 1) % 100 == 0 or index + 1 == len(cases)):
                on_progress(index + 1)
    return dict(summary=summarize(rows), by_condition=by_condition(rows),
                layer_summary=[dict(layer=i + 1, **summarize([r['layer_metrics'][i] for r in rows]))
                               for i in range(len(model.layers))], rows=rows)
