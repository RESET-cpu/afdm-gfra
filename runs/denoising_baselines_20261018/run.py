"""Run four existing baseline solvers on the saved 500-scene AWGN panel."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import multiprocessing
import time
import traceback
import warnings
from concurrent.futures import ProcessPoolExecutor, as_completed
from collections import Counter

from adapter import Denoisers, RUNTIME, np, torch
from afdm_jadcedd.system.observation import array_sha256

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[1]
OUT = ROOT / 'results/denoising_four_baselines_20261018'
INPUT = ROOT / 'results/local_baselines_20261018/formal/channel_denoising'
MERGED = ROOT / 'results/denoising_merged_20261018'
METHODS = ['somp', 'gamp', 'gnn', 'offgrid_sbl']
VALUES = [.001, .01, .1, 1., 10., 100.]
ENGINE = None


def read(path):
    return json.loads(path.read_text())


def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    temporary.replace(path)


def write_csv(path, rows):
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for row in rows for k in row)))
        writer.writeheader()
        writer.writerows(rows)


def warning_rows(caught):
    counts = Counter((str(w.message), w.filename, w.lineno) for w in caught)
    return [dict(message=k[0], file=k[1], line=k[2], count=n) for k, n in counts.items()]


def initialize():
    global ENGINE
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        ENGINE = Denoisers(read(INPUT / 'PLAN.json')['experiment']['scale'])
    ENGINE.initialization_warnings = warning_rows(caught)


def verify_snapshot():
    files = read(RUN / 'SNAPSHOT.json')
    for name, digest in files.items():
        assert sha(RUNTIME / name) == digest, name
    return len(files)


def prepare():
    verify_snapshot()
    plan = dict(schema='direct-awgn-existing-baselines-v1', scenes=500, candidates=4, methods=METHODS,
        variances=VALUES, snr_db=[-10*np.log10(v) for v in VALUES],
        input_root=str(INPUT.relative_to(ROOT)), input_plan_sha256=sha(INPUT / 'PLAN.json'),
        cloud_comparison=str(MERGED.relative_to(ROOT)), cloud_summary_sha256=sha(MERGED / 'SUMMARY.json'),
        runtime_snapshot_sha256=sha(RUN / 'SNAPSHOT.json'),
        source_sha256={n: sha(RUN / n) for n in ['adapter.py', 'run.py']},
        frozen_mainline_sha256=sha(ROOT / 'MAINLINE.json'),
        scale=read(INPUT / 'PLAN.json')['experiment']['scale'],
        observation='One candidate channel per call; identity input operator; all 16 antenna outputs retained.',
        normalization='Multiply saved normalized query by scale and variance by scale**2; divide estimate by scale for scoring.',
        noise='Known direct-AWGN variance supplied. GAMP retains its native Gamma-MAP internal noise update.',
        algorithms='Original known-noise conditional kernels, original configuration, budgets and GNN weights; activity and phase frontends not used.',
        inputs_to_inference=['query', 'noise_variance', 'identity_operator'],
        statistics='Pooled error/energy; 500 independent scenes, 4 dependent candidate channels per scene.',
        cloud_pairing=read(MERGED / 'SUMMARY.json')['pairing'])
    if (OUT / 'PLAN.json').exists():
        assert read(OUT / 'PLAN.json') == plan, 'Existing plan differs'
    else:
        save(OUT / 'PLAN.json', plan)
    return plan


def scene_job(scene):
    path = OUT / 'scenes' / f'scene{scene:03}.json'
    if path.exists():
        previous = read(path)
        assert previous['plan_sha256'] == sha(OUT / 'PLAN.json')
        assert sha(path.with_suffix('.npz')) == previous['compact_sha256']
        return dict(scene=scene, status=previous['status'], reused=True, seconds=previous['seconds'])
    start = time.perf_counter()
    errors = np.full((6, 4, 4), np.nan)
    energies = np.full((6, 4), np.nan)
    predictions = {}
    records, identities = [], []
    for condition, variance in enumerate(VALUES):
        folder = INPUT / f'scene{scene:03}/condition{condition:02}'
        identity = read(folder / 'INPUT.json')
        assert identity['variance'] == variance and identity['scale'] == ENGINE.scale
        assert identity['seed'] == 202610180500001 + scene
        assert sha(folder / 'query.npz') == identity['query_file_sha256']
        with np.load(folder / 'query.npz', allow_pickle=False) as data:
            truth, query = data['truth'], data['query']
            for key in ('truth', 'query', 'standard_noise'):
                assert array_sha256(data[key]) == identity[key + '_sha256'], (scene, condition, key)
            assert data['users'].tolist() == identity['users']
        identities.append(dict(condition=condition, **identity))
        energies[condition] = np.sum(abs(truth)**2, axis=(1, 2, 3))
        for mi, method in enumerate(METHODS):
            for candidate in range(4):
                record = dict(scene=scene, condition=condition, variance=variance,
                    snr_db=float(-10*np.log10(variance)), method=method, candidate=candidate,
                    user=identity['users'][candidate], status='RUNNING')
                began = time.perf_counter()
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter('always')
                    try:
                        estimate, details = ENGINE.infer(method, query[candidate], variance)
                        error = float(np.sum(abs(estimate-truth[candidate])**2))
                        assert np.isfinite(error)
                        errors[condition, mi, candidate] = error
                        record.update(status='COMPLETE', error=error, energy=float(energies[condition, candidate]), **details)
                        if scene == 0:
                            predictions[f'condition{condition:02}_{method}_candidate{candidate}'] = estimate
                    except Exception:
                        record.update(status='FAILED', exception=traceback.format_exc())
                record.update(seconds=time.perf_counter()-began, warnings=warning_rows(caught))
                records.append(record)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path.with_suffix('.npz'), error=errors, energy=energies)
    if predictions:
        np.savez_compressed(OUT / 'scene000_predictions.npz', **predictions)
    result = dict(scene=scene, status='COMPLETE' if all(r['status'] == 'COMPLETE' for r in records) else 'FAILED',
        seconds=time.perf_counter()-start, plan_sha256=sha(OUT / 'PLAN.json'),
        compact_sha256=sha(path.with_suffix('.npz')), inputs=identities, records=records,
        initialization_warnings=ENGINE.initialization_warnings)
    save(path, result)
    return {k: result[k] for k in ('scene', 'status', 'seconds')}


def preflight():
    initialize()
    # Identity operator consumes all channel entries exactly, without a pilot mixture.
    rng = np.random.default_rng(202610180901)
    h = rng.normal(size=(16, 16, 16)) + 1j*rng.normal(size=(16, 16, 16))
    actual = np.einsum('qkn,kmrn->qmr', ENGINE.operator, h[None], optimize=False)
    assert np.array_equal(actual, h.transpose(2, 0, 1))
    p = INPUT / 'scene000/condition03'
    with np.load(p / 'query.npz') as z:
        query = z['query'][0]
    # Compare the GNN cached-grid call against its unchanged public native wrapper.
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        adapted, details = ENGINE.infer('gnn', query, 1.)
        native, metadata = ENGINE.gnn.infer(ENGINE.inputs(query, 1.))
    expected = native['estimate'][0] / ENGINE.scale
    np.testing.assert_allclose(adapted, expected, rtol=1e-12, atol=1e-12)
    result = scene_job(0)
    assert result['status'] == 'COMPLETE', result
    record = read(OUT / 'scenes/scene000.json')
    save(OUT / 'PREFLIGHT.json', dict(status='PASS', identity_operator_exact=True,
        gnn_native_max_abs_difference=float(np.max(abs(adapted-expected))),
        gnn_reference_warnings=warning_rows(caught), completed_inferences=len(record['records']),
        conditions=6, candidates=4, methods=4, seconds=result['seconds'],
        timing_by_method={m:sum(r['seconds'] for r in record['records'] if r['method'] == m) for m in METHODS},
        stopping_reasons=dict(Counter(r['method'] + ':' + r['stopping_reason'] for r in record['records'])),
        qualification='Input adaptation, output finiteness and complete record verification only; no performance-based selection.'))
    print(json.dumps(read(OUT / 'PREFLIGHT.json'), ensure_ascii=False), flush=True)


def aggregate():
    scene_results = [read(OUT / 'scenes' / f'scene{s:03}.json') for s in range(500)]
    assert all(r['status'] == 'COMPLETE' for r in scene_results)
    errors, energies, details = [], [], []
    plan_hash = sha(OUT / 'PLAN.json')
    for result in scene_results:
        path = OUT / 'scenes' / f'scene{result["scene"]:03}.npz'
        assert result['plan_sha256'] == plan_hash and sha(path) == result['compact_sha256']
        with np.load(path, allow_pickle=False) as a:
            assert np.isfinite(a['error']).all() and np.isfinite(a['energy']).all()
            errors.append(a['error']); energies.append(a['energy'])
        assert len(result['records']) == 96
        for row in result['records']:
            assert row['status'] == 'COMPLETE'
            c, m, k = row['condition'], METHODS.index(row['method']), row['candidate']
            assert row['error'] == errors[-1][c, m, k] and row['energy'] == energies[-1][c, k]
            details.append(row)
    error, energy = np.stack(errors), np.stack(energies)
    np.savez_compressed(OUT / 'ALL_SCENES.npz', error=error, energy=energy)
    summaries = []
    for c, variance in enumerate(VALUES):
        for mi, method in enumerate(METHODS):
            e, power = float(error[:, c, mi].sum()), float(energy[:, c].sum())
            summaries.append(dict(method=method, variance=variance, snr_db=float(-10*np.log10(variance)),
                scenes=500, samples=2000, status='COMPLETE', error=e, energy=power,
                nmse_db=float(10*np.log10(e/power)), origin='local_existing_baselines', error_kind='realized_squared_error'))
    references = read(MERGED / 'SUMMARY.json')['rows']
    for row in summaries:
        ref = next(r for r in references if r['method'] == 'noisy' and r['variance'] == row['variance'])
        assert np.isclose(row['energy'], ref['energy'], rtol=1e-12)
    rows = summaries + references
    rows.sort(key=lambda r: (r['snr_db'], r['method']))
    summary = dict(status='COMPLETE', rows=rows, baseline_inferences=48000,
        baseline_scene_method_records=12000, paired_scenes=500, candidates_per_scene=4,
        baseline_configuration=read(OUT / 'PLAN.json'), inherited_comparison=read(MERGED / 'SUMMARY.json'),
        stopping_reasons=dict(Counter(r['method']+':'+r['stopping_reason'] for r in details)),
        warning_inferences=sum(bool(r['warnings']) for r in details),
        statement='Completion is not convergence; iteration-limit outcomes and all warnings are retained.',
        gnn_scope='Existing receiver-trained checkpoint reused without retraining on identity-observation denoising; this experiment measures its transfer performance.')
    save(OUT / 'SUMMARY.json', summary)
    write_csv(OUT / 'STATISTICS.csv', rows)
    write_csv(OUT / 'BASELINE_RECORDS.csv', [{k:v for k,v in r.items() if k != 'warnings'} for r in details])
    verify_snapshot()
    assert sha(ROOT / 'MAINLINE.json') == read(OUT / 'PLAN.json')['frozen_mainline_sha256']
    save(OUT / 'VERIFICATION.json', dict(status='PASS', scene_files=500, compact_arrays_verified=True,
        source_snapshot_verified=True, unchanged_mainline=True, input_files_verified_during_inference=3000,
        baseline_inferences=48000, failures=0, pooled_energy_matches_existing_references=True,
        cloud_pairing_verification=str((MERGED / 'VERIFICATION.json').relative_to(ROOT)),
        gnn_checkpoint_sha256=sha(RUNTIME / 'models/gnn/checkpoint.pt')))
    plot(rows)
    return summary


def plot(rows):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    styles = {
        'noisy': ('LS (noisy input)', '#999999', ':'),
        'gaussian': ('Gaussian prior', '#b08b35', '--'),
        'somp': ('SOMP', '#8b5da5', '-'),
        'gamp': ('GAMP-SBL', '#57a0a0', '-'),
        'gnn': ('GNN-ASPL (existing weights)', '#de8b40', '-'),
        'offgrid_sbl': ('Off-grid SBL', '#515d90', '-'),
        'proposed_small': ('Proposed (5,000 training channels)', '#2775b6', '-'),
        'proposed': ('Proposed (50,000 training channels)', '#d2493d', '-'),
        'genie_bound': ('Genie conditional MMSE (oracle)', '#299568', '--')}
    fig, ax = plt.subplots(figsize=(9, 6), layout='constrained')
    for method, (label, color, line) in styles.items():
        group = sorted([r for r in rows if r['method'] == method], key=lambda r:r['snr_db'])
        ax.plot([r['snr_db'] for r in group], [r['nmse_db'] for r in group],
            label=label, color=color, linestyle=line, marker='s' if method=='genie_bound' else 'o',
            linewidth=2.1 if method.startswith('proposed') else 1.5, markersize=5)
    ax.set(xlabel='SNR (dB)', ylabel='Channel NMSE (dB)',
        title='Direct channel denoising\n500 physical scenes × 4 channels; known input noise')
    ax.set_xticks([-20, -10, 0, 10, 20, 30]); ax.grid(alpha=.22)
    ax.legend(fontsize=8, loc='upper right', ncol=2)
    for ext in ['png', 'pdf']:
        fig.savefig(OUT / ('denoising.' + ext), dpi=200)
    plt.close(fig)


def run(workers):
    assert read(OUT / 'PREFLIGHT.json')['status'] == 'PASS'
    started = time.time()
    complete, failed = [], []
    with ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context('spawn'), initializer=initialize) as pool:
        futures = {pool.submit(scene_job, s): s for s in range(500)}
        for future in as_completed(futures):
            scene = futures[future]
            try:
                result = future.result()
                (complete if result['status'] == 'COMPLETE' else failed).append(scene)
            except Exception:
                failed.append(scene)
                save(OUT / 'failures' / f'scene{scene:03}.json', dict(scene=scene, exception=traceback.format_exc()))
            save(OUT / 'STATUS.json', dict(status='RUNNING', completed_scenes=len(complete), failed_scenes=failed,
                total_scenes=500, workers=workers, elapsed_seconds=time.time()-started))
            if (len(complete)+len(failed)) % 10 == 0:
                print(f'{len(complete)}/500 scenes complete; {len(failed)} failures; {time.time()-started:.1f} seconds', flush=True)
    if failed:
        save(OUT / 'STATUS.json', dict(status='INCOMPLETE', completed_scenes=len(complete), failed_scenes=failed))
        raise RuntimeError(f'Failed scenes retained: {failed}')
    save(OUT / 'STATUS.json', dict(status='VERIFYING', completed_scenes=500))
    summary = aggregate()
    save(OUT / 'STATUS.json', dict(status='COMPLETE', completed_scenes=500, failures=0,
        elapsed_seconds=time.time()-started, baseline_inferences=summary['baseline_inferences']))
    print('COMPLETE: 48,000 baseline inferences; merged plots and statistics verified.', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['preflight', 'run', 'aggregate'])
    parser.add_argument('--workers', type=int, default=6)
    args = parser.parse_args()
    prepare()
    if args.command == 'preflight': preflight()
    elif args.command == 'run': run(args.workers)
    else: aggregate()
