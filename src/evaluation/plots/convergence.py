"""Plot saved, paired native iteration traces; never invoke a receiver or extend a curve."""
import argparse
from dataclasses import asdict
import json
from pathlib import Path

import numpy as np

from configurable import resolve_config, render
from data import PlotData, digest, read


def load_traces(source, methods):
    plan_path = source/'PLAN.json'
    plan = read(plan_path)
    methods = methods or ['C_STMP', 'STMP']
    if not methods or len(set(methods)) != len(methods):
        raise ValueError('Select distinct saved methods')
    rows, checks, configurations = [], {}, {}
    sources = {str(plan_path): digest(plan_path)}
    paired = None
    for method in methods:
        if method not in ('STMP', 'C_STMP'):
            raise ValueError('Supported saved trace IDs: STMP, C_STMP')
        label = method.replace('_', '-')
        record_path, array_path = source/f'{method}.json', source/f'{method}.npz'
        record = read(record_path)
        if record['method'] != label or record['plan_sha256'] != sources[str(plan_path)]:
            raise ValueError('Trace method or paired plan does not match')
        if digest(array_path) != record['output_sha256']:
            raise ValueError('Saved trace array hash mismatch')
        if record['configuration'] != plan['configurations'][label]:
            raise ValueError('Saved receiver configuration differs from plan')
        with np.load(array_path, allow_pickle=False) as z:
            error, probabilities, activity = z['per_user_error'], z['probabilities'], z['truth_activity']
            energy = float(z['signal_energy'])
        count = record['iterations']
        if error.shape != probabilities.shape or error.shape != (count, len(activity)):
            raise ValueError('Incomplete per-iteration arrays')
        if not np.isfinite(energy) or energy<=0 or not np.all(np.isfinite(error)) or np.any(error<0):
            raise ValueError('Invalid signal/error energy')
        if not np.all(np.isfinite(probabilities)) or np.any((probabilities<0)|(probabilities>1)):
            raise ValueError('Invalid activity probabilities')
        key = (record['scene'], record['snr_db'], energy, tuple(activity))
        if paired is not None and paired != key:
            raise ValueError('Methods must use the same saved scene and truth')
        paired = key
        nmse = 10*np.log10(error.sum(axis=1)/energy)
        threshold = record['configuration']['decision_threshold']
        aer = np.mean((probabilities>=threshold)!=activity, axis=1)
        trace = record['trace']
        if len(trace)!=count or [t['iteration'] for t in trace]!=list(range(1,count+1)):
            raise ValueError('Trace iteration sequence does not match native stopping')
        if not np.allclose(nmse,[t['nmse_db'] for t in trace],rtol=0,atol=1e-11):
            raise ValueError('Trace NMSE differs from saved per-user errors')
        if not np.array_equal(aer,[t['aer'] for t in trace]):
            raise ValueError('Trace AER differs from saved decisions')
        for t in trace:
            rows.append(dict(method=method,parameters={'iteration':t['iteration']},
                             nmse_db=t['nmse_db'],aer=t['aer']))
        checks[method] = dict(iterations=count, stopping_reason=record['stopping_reason'],
                             final_nmse_db=float(nmse[-1]), final_aer=float(aer[-1]))
        configurations[method] = record['configuration']
        sources.update({str(record_path):digest(record_path),str(array_path):digest(array_path)})
    metadata = dict(scene=plan['scene'],snr_db=plan['snr_db'],phase_mode=plan['phase_mode'],
                    noise_mode=plan['noise_mode'],users=len(paired[3]),active_users=int(sum(paired[3])),
                    sources=sources,configurations=configurations,checks=checks,
                    pointwise_metrics_verified=True,curves_end_at_native_stopping=True,
                    registered_cstmp=plan.get('registered_cstmp'),
                    matches_completed_snr_configuration=plan.get('matches_completed_snr_configuration',False),
                    stmp_provenance=plan.get('stmp_provenance'))
    return PlotData('convergence',rows,methods,1,metadata)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=Path(__file__).resolve().parents[2]/'configs/plots/convergence.json')
    parser.add_argument('--input',type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args(argv)
    cfg=resolve_config(args.config,'convergence',args.input,args.output)
    selection=cfg['selection']
    if any(selection.get(k) for k in ('conditions','scenes','per_scene')):
        raise ValueError('A native trace input is one paired scene; select another --input instead')
    data=load_traces(Path(cfg['input']),selection['methods'])
    out=Path(cfg['output'])
    if out.exists(): raise ValueError('Output already exists; choose a new --output')
    out.mkdir(parents=True)
    files=render(data,out,cfg)
    meta=data.metadata
    legacy=any(c.get('classifier_policy')=='frozen_legacy_teacher' for c in meta['configurations'].values())
    caption=(f"Single-scene STMP/C-STMP convergence, scene {meta['scene']}, SNR {meta['snr_db']} dB, "
             f"{meta['users']} users ({meta['active_users']} active); {meta['phase_mode']} phase and {meta['noise_mode']} noise. "
             "Left: NMSE. Right: empirical AER on a linear axis, including exact zeros. "
             "The legend applies to both panels. Each curve ends at its native stopping iteration. "
             "Native damping and stopping rules are unchanged. Iteration counts do not imply a runtime advantage. ")
    if legacy:
        caption += ("Historical C-STMP uses the derivative variance estimator and legacy activity classifier; "
                    "it is not the current query-variance-update C-STMP used in the final SNR comparison. ")
    elif meta['matches_completed_snr_configuration']:
        caption += ("C-STMP uses the current registered query-variance-update receiver and the same configuration "
                    "as the completed SNR experiment. The original paired STMP trace is reused with its original stopping controls. ")
    caption += "Single-scene illustration, not a Monte Carlo average."
    for name,value in [('CONFIG.json',cfg),('PLOT_DATA.json',asdict(data)),('CHECKS.json',meta)]:
        (out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    (out/'caption.txt').write_text(caption+'\n',encoding='utf-8')
    (out/'figure_include.tex').write_text('\\includegraphics[width=\\linewidth]{convergence.pdf}\n',encoding='utf-8')
    # Confirm plotting did not modify any saved experiment inputs.
    if any(digest(Path(p))!=h for p,h in meta['sources'].items()):
        raise ValueError('Saved experiment input changed during plotting')
    manifest=dict(status='PLOTTED',inference_started=False,training_started=False,
                  historical_cstmp=legacy,source=meta['sources'],config_source=str(args.config.resolve()),
                  config_source_sha256=digest(args.config),
                  scripts={p.name:digest(p) for p in Path(__file__).parent.glob('*.py')},
                  files={p.name:digest(p) for p in out.iterdir() if p.is_file()})
    (out/'FIGURES.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(output=str(out),checks=meta['checks'],files=len(files))))


if __name__=='__main__':
    main()
