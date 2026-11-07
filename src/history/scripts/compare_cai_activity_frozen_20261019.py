"""Frozen CPU-only developmental comparison; no optimizer or training writes.

Cai's released Gaussian-prior activity rule is substituted into the *current*
receiver. This is neither a reproduction of all of Cai's nonlinear module nor
a five-layer trained comparison. The same-message arm never feeds back.
"""
import argparse
import copy
import csv
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import sys
import time
import traceback

ROOT = Path(r'C:\Users\25911\Desktop\afdm-gfra')
RUN = Path(r'D:\afdm-gfra-cpu\runs\lstmp_refinenet_50000_message_damping_20261019')
OUT = ROOT / 'results/lstmp_cai_activity_frozen_20261019'
CONFIG = RUN / 'source_code/experiments/lstmp_candidate_20261019/reuse_50000_fast.json'
CHECKPOINT = RUN / 'checkpoints/depth_3/best.pt'
EXPECTED_CHECKPOINT = '5cbb0a8bf8f04d06f29a838bc864c0dd9107c67a86b957ec75ede7a8586ef833'
METHODS = ('classifier', 'cai_same_messages', 'cai_feedback')


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
    temp.replace(path)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(2**20), b''):
            h.update(block)
    return h.hexdigest()


def freeze():
    if OUT.exists():
        raise FileExistsError('Preserve the existing experiment; no plan or results overwritten')
    config = read(CONFIG)
    assert sha(CHECKPOINT) == EXPECTED_CHECKPOINT
    scenes = []
    profiles, snrs = config['receiver']['conditions']['validation'], config['receiver']['snr_db']
    assert len(profiles) * len(snrs) == 24
    for i in range(48):
        scenes.append(dict(group='balanced', seed=202610211300001+i,
                           **profiles[(i//len(snrs)) % len(profiles)], snr_db=snrs[i % len(snrs)]))
    for group, base, users, frames, snr in [('standard', 202610211400001, 40, 16, 5),
                                          ('stress', 202610211500001, 100, 8, 10)]:
        for i in range(24):
            scenes.append(dict(group=group, seed=base+i, users=users, frames=frames,
                               activity_probability=.1, snr_db=snr))
    seeds = {s['seed'] for s in scenes}
    assert len(seeds) == len(scenes)
    for split in ['train', 'validation', 'test']:
        c = config['receiver']
        assert seeds.isdisjoint(range(c[f'{split}_seed'], c[f'{split}_seed']+c[f'{split}_scenes']))
    assert seeds.isdisjoint(range(202610198700001, 202610198700021))
    assert 202610198799999 not in seeds
    source_paths = sorted((RUN/'source_code').rglob('*.py')) + sorted((RUN/'source_project').rglob('*.py'))
    protected = {str(p): sha(p) for p in source_paths + [CONFIG, CHECKPOINT, RUN/'MANIFEST.json']}
    evidence = ROOT/'experiments/lstmp_cai_activity_candidate_20261019/evidence.py'
    tests = ROOT/'tests/test_lstmp_cai_activity.py'
    author = ROOT/'references/known_phase_iteration_review_20260928/cai_official_main_stmp_jadce.py.txt'
    (OUT/'source').mkdir(parents=True)
    for p in [Path(__file__), evidence, tests, author]:
        shutil.copy2(p, OUT/'source'/p.name)
    plan = dict(schema='cai-activity-frozen-v1', created_unix=time.time(),
        checkpoint=str(CHECKPOINT), checkpoint_sha256=EXPECTED_CHECKPOINT, depth=3,
        checkpoint_epoch=2, device='cpu', torch_threads=2, optimizer_updates=0,
        methods=list(METHODS), phase='known', noise='known', activity_threshold=.5,
        active_prior_power=config['normalized_training_second_moment'],
        hypothesis='H0 CN(0,vI), H1 CN(0,(v+beta)I); beta from training only',
        intervention='Replace activity heads only; retain score, calibration, residual feedback and damping',
        same_messages='Recompute p and terminal p*mu on each native query; never feed this arm back',
        scope='Completed depth-3 development checkpoint, not final five-layer evaluation or complete Cai module B',
        no_threshold_or_power_fitting=True, retain_all_scenes=True, scenes=scenes,
        seed_audit='New ranges absent from existing scripts/experiments/results JSON and text before runner creation; disjoint training/validation and reserved 20+1 scenes',
        protected=protected, source_sha256={str(p.relative_to(OUT)):sha(p) for p in (OUT/'source').iterdir()},
        formula_source='https://arxiv.org/html/2506.00581v2, III-B2 Eq (30)',
        code_source='https://github.com/chang-cai/score-massive-connectivity/blob/0c75680c966dcb8e46250de146f4c27e9294c283/main_stmp_jadce.py, lambda_post_gaussian',
        validation='Four CPU tests: complex density, author code parity, Gaussian site inversion, invalid precision')
    save(OUT/'PLAN.json', plan)
    print(json.dumps(dict(stage='PLAN_FROZEN', scenes=len(scenes), output=str(OUT))), flush=True)


def run():
    os.environ['CUDA_VISIBLE_DEVICES'] = ''
    os.environ['AFDM_LSTMP_ROOT'] = str(ROOT)
    os.environ['AFDM_LSTMP_CONFIG'] = str(CONFIG)
    sys.path.insert(0, str(RUN/'source_code'))
    import numpy as np
    import torch
    from threadpoolctl import threadpool_limits
    from experiments.lstmp_candidate_20261019 import common, data, receiver
    from afdm_jadcedd.experiment.generate import generate_case
    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
    threadpool_limits(2, user_api='blas')
    plan = read(OUT/'PLAN.json')
    for name, digest in {**plan['protected'], **{str(OUT/k):v for k,v in plan['source_sha256'].items()}}.items():
        if sha(name) != digest:
            raise ValueError(f'Frozen asset changed: {name}')
    if (OUT/'COMPLETE.json').exists() or (OUT/'RUNNING.lock').exists():
        raise FileExistsError('Existing completed/active experiment; no duplicate launch')
    if (OUT/'scene_metrics.csv').exists():
        raise FileExistsError('Existing partial results retained; inspect before any restart')
    spec = importlib.util.spec_from_file_location('frozen_cai_evidence', OUT/'source/evidence.py')
    evidence = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(evidence)
    checkpoint = torch.load(CHECKPOINT, map_location='cpu', weights_only=False)
    assert checkpoint['depth'] == 3 and checkpoint['epoch'] == 2
    scale = float(checkpoint['scale'])
    torch.manual_seed(20261019)
    native = receiver.Receiver()
    for _ in range(plan['depth']):
        native.add_layer(None)
    native.load_state_dict(checkpoint['state'])
    del checkpoint
    native.eval().requires_grad_(False)
    native.use_checkpoint = False
    analytic = copy.deepcopy(native)
    for layer in analytic.layers:
        layer.activity = evidence.GaussianPriorActivity(plan['active_prior_power'])
    analytic.eval().requires_grad_(False)
    assert not torch.cuda.is_initialized()
    (OUT/'RUNNING.lock').write_text(str(os.getpid()), encoding='utf-8')
    started = time.time()
    rows, input_receipts, failures = [], [], []

    def status(stage, **fields):
        value = dict(stage=stage, pid=os.getpid(), updated_unix=time.time(),
                     elapsed_seconds=time.time()-started, **fields)
        save(OUT/'STATUS.json', value)
        print(json.dumps(value), flush=True)

    def score_output(scene, index, method, depth, output, diagnostic, message, labels, rho):
        x, logits = output
        if not (torch.isfinite(x).all() and torch.isfinite(logits).all()):
            raise FloatingPointError(f'Nonfinite {method} output, scene {index}, layer {depth}')
        m = receiver.metrics([output], labels)
        p = torch.sigmoid(logits.double())
        y = labels['active'].double()
        k = len(y)
        row = dict(scene=index, **scene, method=method, depth=depth, **m,
            brier_sum=float(((p-y)**2).sum()),
            bce_sum=float(torch.nn.functional.binary_cross_entropy_with_logits(logits.double(),y,reduction='sum')),
            saturated=int(((p<1e-6)|(p>1-1e-6)).sum()),
            confidently_wrong=int((((y>0)&(p<1e-6))|((y==0)&(p>1-1e-6))).sum()),
            max_abs_logit=float(logits.abs().max()), **diagnostic)
        r, v = message['query'], diagnostic['query_variance']
        d = r[0].numel()//2
        query_energy = r.double().square().flatten(1).sum(1)/(d*v)
        query_error = (r.double()-labels['x'].double()).square().flatten(1).sum(1)/(d*v)
        row['inactive_query_energy_over_v_sum'] = float(query_energy[y==0].sum())
        row['active_query_error_over_v_sum'] = float(query_error[y>0].sum())
        return row, dict(logit=logits.cpu().numpy(), probability=p.cpu().numpy(),
                        query_energy_over_v=query_energy.cpu().numpy(),
                        query_error_over_v=query_error.cpu().numpy())

    try:
        status('CPU_FROZEN_DIAGNOSTIC', scenes=0, total=len(plan['scenes']))
        with torch.inference_mode():
            for index, scene in enumerate(plan['scenes']):
                folder = OUT/'scenes'/f'{index:03d}'
                folder.mkdir(parents=True, exist_ok=True)
                args = {k:v for k,v in scene.items() if k not in ('group','seed','snr_db')}
                inp, truth, generation = generate_case(scene['seed'], scene['snr_db'], scale, **args)
                save(folder/'GENERATION.json', generation)
                np.savez_compressed(folder/'input.npz', **dict(inp))
                np.savez_compressed(folder/'truth.npz', channel=truth['channel'], activity=truth['activity'])
                public_arrays = dict(y=inp['observation'], a=inp['operator'], noise=inp['noise_variance'],rho=inp['activity_prior'])
                public, preparation = data.prepare_public(public_arrays,scale,'cpu',phase_mode='known',noise_mode='known')
                labels = dict(x=common.real_tensor(truth['channel']/scale,'cpu'),
                              active=torch.tensor(truth['activity'],dtype=torch.float32),physical_scale=scale)
                receipt = dict(scene=index, input_sha256=sha(folder/'input.npz'),truth_sha256=sha(folder/'truth.npz'),
                               preparation=preparation)
                input_receipts.append(receipt)
                save(folder/'IDENTITY.json', dict(**scene, **receipt))
                predictions = dict(active=truth['activity'])
                scene_rows = []
                for method, model in [('classifier',native), ('cai_feedback',analytic)]:
                    t = time.perf_counter()
                    try:
                        outputs, diagnostics, messages = model(public,return_messages=True)
                        duration = time.perf_counter()-t
                        for j, (output, diagnostic, message) in enumerate(zip(outputs,diagnostics,messages),1):
                            row, values = score_output(scene,index,method,j,output,diagnostic,message,labels,public['rho'])
                            row['forward_seconds'] = duration
                            scene_rows.append(row)
                            predictions.update({f'{method}_layer{j}_{k}':v for k,v in values.items()})
                        predictions[f'{method}_estimate'] = outputs[-1][0].cpu().numpy()
                        if method == 'classifier':
                            for j, (diagnostic,message) in enumerate(zip(diagnostics,messages),1):
                                logits = analytic.layers[j-1].activity(message['query'],diagnostic['query_variance'],message['conditional'],public['rho'])
                                x = torch.sigmoid(logits)[:,None,None,None,None]*message['conditional']
                                row, values = score_output(scene,index,'cai_same_messages',j,(x,logits),diagnostic,message,labels,public['rho'])
                                row['forward_seconds'] = None
                                scene_rows.append(row)
                                predictions.update({f'cai_same_messages_layer{j}_{k}':v for k,v in values.items()})
                    except Exception:
                        failure = dict(scene=index,method=method,traceback=traceback.format_exc())
                        failures.append(failure)
                        save(folder/f'FAILURE_{method}.json',failure)
                np.savez_compressed(folder/'predictions.npz', **predictions)
                save(folder/'metrics.json', scene_rows)
                rows.extend(scene_rows)
                save(OUT/'INPUTS.json',input_receipts)
                # Persist each completed scene before beginning the next.
                if rows:
                    fields = sorted(set().union(*(r.keys() for r in rows)))
                    with (OUT/'scene_metrics.csv').open('w',newline='',encoding='utf-8') as f:
                        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
                status('CPU_FROZEN_DIAGNOSTIC',scenes=index+1,total=len(plan['scenes']),failures=len(failures))
        summaries = {}
        for group in ['all','balanced','standard','stress']:
            summaries[group] = {}
            for method in METHODS:
                summaries[group][method] = []
                for depth in range(1,plan['depth']+1):
                    selected=[r for r in rows if r['method']==method and r['depth']==depth and (group=='all' or r['group']==group)]
                    if not selected:
                        continue
                    s=receiver.summarize_rows(selected)
                    n=s['active']+s['inactive']
                    s.update(depth=depth, max_scene_nmse_db=10*math.log10(max(r['nmse'] for r in selected)),
                        probability_brier=sum(r['brier_sum'] for r in selected)/n,
                        user_mean_bce=sum(r['bce_sum'] for r in selected)/n,
                        saturated_fraction=sum(r['saturated'] for r in selected)/n,
                        confidently_wrong_fraction=sum(r['confidently_wrong'] for r in selected)/n,
                        inactive_query_energy_over_v=sum(r['inactive_query_energy_over_v_sum'] for r in selected)/s['inactive'],
                        active_query_error_over_v=sum(r['active_query_error_over_v_sum'] for r in selected)/s['active'])
                    summaries[group][method].append(s)
        changed=[p for p,h in plan['protected'].items() if sha(p)!=h]
        assert not changed, changed
        assert not torch.cuda.is_initialized()
        report=dict(scope=plan['scope'],summaries=summaries,failures=failures,
            rows=len(rows),expected_rows=len(plan['scenes'])*plan['depth']*len(METHODS),
            protected_unchanged=True,cuda_initialized=False,optimizer_updates=0,
            elapsed_seconds=time.time()-started,plan_sha256=sha(OUT/'PLAN.json'),
            input_receipts_sha256=sha(OUT/'INPUTS.json'),metrics_sha256=sha(OUT/'scene_metrics.csv'))
        save(OUT/'REPORT.json',report)
        if failures or report['rows'] != report['expected_rows']:
            save(OUT/'FAILURE.json',dict(reason='Per-scene failure; all results retained',**report))
            status('COMPLETED_WITH_FAILURES',scenes=len(plan['scenes']),failures=len(failures))
        else:
            save(OUT/'COMPLETE.json',dict(completed_unix=time.time(),report_sha256=sha(OUT/'REPORT.json'),scenes=len(plan['scenes'])))
            status('COMPLETE',scenes=len(plan['scenes']),failures=0)
    except BaseException:
        save(OUT/'FAILURE.json',dict(traceback=traceback.format_exc(),completed_scenes=len(input_receipts),rows=len(rows)))
        raise
    finally:
        (OUT/'RUNNING.lock').unlink(missing_ok=True)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    action=parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--freeze',action='store_true')
    action.add_argument('--run',action='store_true')
    args=parser.parse_args()
    freeze() if args.freeze else run()
