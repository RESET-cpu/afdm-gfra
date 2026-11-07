"""Pretrained first-score AWGN denoising only."""
from scenario.catalog import DEFAULT

NAME = 'channel_denoising'
DESCRIPTION = 'Pretrained first-score AWGN denoising only'
KIND = 'denoiser'


def conditions(config, args):
    values = args.values if args.values is not None else config['values']
    return [dict(variance=v, users=40, candidates=4) for v in values]


def main(argv=None):
    from experiment.suite import main as execute
    return execute(NAME, argv)


def evaluate_case(plan, models, scene, condition):
    """Evaluate only configured denoisers on the same saved AWGN query."""
    import numpy as np
    from pathlib import Path
    from receiver.registry import build_algorithm
    from channel.observation import array_sha256
    from scenario.channel_samples import clean_channels
    from experiment.metrics import denoising_metrics
    from experiment.storage import save_arrays
    from experiment.suite import checked_result
    from fileio import json_digest
    from fileio import write_json
    from fileio import sha256

    variance = condition['variance']
    scale = plan['model_binding']['STMP']['scale']
    seed = plan['base_seed']+scene
    physical, selected, priors = clean_channels(seed, 40, 4, genie_scale=scale)
    truth = physical/scale
    rng = np.random.default_rng(np.random.SeedSequence([seed,8240]))
    epsilon = (rng.normal(size=truth.shape)+1j*rng.normal(size=truth.shape))/np.sqrt(2)
    query = truth+np.sqrt(variance)*epsilon
    identity = dict(runtime=plan['runtime_identity'], seed=seed, variance=variance,
                    query_sha256=array_sha256(query), truth_sha256=array_sha256(truth),
                    users=selected.tolist(), device=plan['device'])
    folder = Path(plan['cache']) / 'denoising' / json_digest(identity)
    save_arrays(folder / 'query.npz', dict(query=query, truth=truth, users=selected))
    results = []
    for method in plan['methods']:
        spec = plan['algorithm_specs'][method]
        method_identity = dict(identity, method=method, algorithm=json_digest(spec))
        # One digest includes both input and settings; avoid nested long hashes
        # in Windows paths while retaining distinct configured predictions.
        path = Path(plan['cache'])/'denoising'/'predictions'/(json_digest(method_identity)+'.json')
        saved = checked_result(path, method_identity)
        if saved is not None:
            results.append((saved,path))
            continue
        if method not in models:
            models[method] = build_algorithm(method, binding=plan['model_binding'],
                device=plan['device'], definitions=plan['algorithm_specs'])
        mean, metadata = models[method].infer(query, variance, priors=priors if spec.get('uses_truth') else None)
        values = denoising_metrics(mean, truth)
        analytic = 'analytic_error' in metadata
        if analytic:
            if not spec.get('uses_truth'):
                raise ValueError('Analytic conditional risk requires an explicitly truth-using method')
            values.update(realized_error=values['error'], error=metadata['analytic_error'])
        save_arrays(path.with_suffix('.npz'), values)
        row = dict(identity=method_identity, status='COMPLETE',
                   compact_sha256=sha256(path.with_suffix('.npz')), error=float(values['error'].sum()),
                   energy=float(values['energy'].sum()), samples=4, truth_used=bool(spec.get('uses_truth')),
                   error_kind='analytic_conditional_mmse' if analytic else 'realized_squared_error')
        write_json(path, row)
        if scene == 0:
            save_arrays(path.with_suffix('.prediction.npz'), dict(estimate=mean))
        results.append((row,path))
    return results


if __name__ == '__main__':
    raise SystemExit(main())
