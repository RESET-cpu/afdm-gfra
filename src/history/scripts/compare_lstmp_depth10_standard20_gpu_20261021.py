"""Four frozen receivers on the same saved estimated-phase/noise standard panel.

All four receivers are newly executed, sequentially, on CUDA FP32 with TF32 off.
The common estimated frontend is byte-reused and excluded from receiver timing.
"""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '4'
import argparse
import csv
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
import traceback
sys.dont_write_bytecode = True
import numpy as np

ROOT = Path(r'C:\Users\25911\Desktop\afdm-gfra')
OUT = ROOT / 'results/lstmp_v3_depth10_standard20_gpu_20261021'
PREVIOUS = ROOT / 'results/lstmp_v3_depth6_standard20_cpu_20261021'
KNOWN = ROOT / 'results/lstmp_v3_depth10_previous20_20261020'
TRAIN = Path(r'D:\afdm-gfra-cpu\runs\lstmp_conditional_bce_v3_depth10_fast_20261020')
NEW = 'v3_ten_layer'
LEGACY = 'legacy_formal_damping02'
METHODS = (NEW, 'prior_seven_layer', 'prior_five_layer', LEGACY)
LABELS = ('新十层', '此前七层', '此前五层', '旧三网络（正式阻尼0.2）')


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    temporary.replace(path)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def status(stage, **fields):
    row = dict(stage=stage, pid=os.getpid(), updated_unix=time.time(), **fields)
    write(OUT / 'STATUS.json', row)
    print(json.dumps(row, ensure_ascii=False), flush=True)


def training_ready():
    frozen = module(KNOWN / 'source/evaluate_lstmp_v3_depth10_previous20_20261020.py', 'training_completion_gate')
    assert frozen.readiness(TRAIN) == (True, 'READY')
    c = read(TRAIN / 'COMPLETE.json')
    d = read(TRAIN / 'checkpoints/depth_10/COMPLETE.json')
    assert sha(TRAIN / 'checkpoints/depth_10/best.pt') == c['selected_sha256'] == d['best_sha256']
    assert d['selected_epoch'] == 1
    return d


def verify(plan):
    assert sha(OUT / 'PLAN.json') == read(OUT / 'PLAN_SHA256.json')['sha256']
    for path, digest in plan['protected_hashes'].items():
        if sha(path) != digest:
            raise ValueError('Protected source or model changed: ' + path)
    for relative, digest in plan['local_hashes'].items():
        if sha(OUT / relative) != digest:
            raise ValueError('Frozen local input/source changed: ' + relative)
    assert not (TRAIN / 'RUNNING.lock').exists()


def prepare():
    if OUT.exists():
        raise FileExistsError('Fresh comparison directory required: ' + str(OUT))
    receipt = training_ready()
    previous = read(PREVIOUS / 'PLAN.json')
    assert read(PREVIOUS / 'COMPLETE.json')['status'] == 'COMPLETE'
    assert previous['condition'] == dict(users=40, frames=16, activity_probability=.1, snr_db=0.)
    assert previous['phase_mode'] == previous['noise_mode'] == 'estimated'
    assert [c['seed'] for c in previous['cases']] == list(range(202610180400001, 202610180400021))
    # Existing public inputs and all original method assets are checked before reuse.
    for path, digest in previous['protected_hashes'].items():
        if sha(path) != digest:
            raise ValueError('Previous protected asset changed: ' + path)
    for relative, digest in previous['local_hashes'].items():
        if sha(PREVIOUS / relative) != digest:
            raise ValueError('Previous frozen input/source changed: ' + relative)
    OUT.mkdir()
    (OUT / 'source').mkdir()
    shutil.copy2(__file__, OUT / 'source' / Path(__file__).name)
    shutil.copy2(KNOWN / 'source/paired_core.py', OUT / 'source/paired_core.py')
    shutil.copy2(KNOWN / 'execution_repair_01/gpu_preflight.py', OUT / 'source/gpu_preflight.py')
    shutil.copytree(PREVIOUS / 'cases', OUT / 'cases')
    models = {k: previous['models'][k] for k in METHODS[1:3]}
    models[NEW] = dict(run=str(TRAIN), depth=10, checkpoint=str(TRAIN / 'checkpoints/depth_10/best.pt'),
        checkpoint_sha256=receipt['best_sha256'], selected_epoch=receipt['selected_epoch'],
        config=str(TRAIN / 'source_code/experiments/lstmp_execution_v3_20261020/config.json'),
        package='lstmp_execution_v3_20261020', manifest_sha256=sha(TRAIN / 'MANIFEST.json'))
    protected = dict(previous['protected_hashes'])
    for p in (PREVIOUS / 'PLAN.json', PREVIOUS / 'RESULT_AUDIT.json', PREVIOUS / 'COMPLETE.json',
              KNOWN / 'PLAN.json', TRAIN / 'COMPLETE.json', TRAIN / 'checkpoints/depth_10/COMPLETE.json',
              TRAIN / 'checkpoints/depth_10/best.pt', ROOT / 'MAINLINE.json'):
        protected[str(p)] = sha(p)
    for p in (ROOT / 'src/afdm_jadcedd').rglob('*.py'):
        protected[str(p)] = sha(p)
    for bound in models.values():
        manifest = read(Path(bound['run']) / 'MANIFEST.json')
        protected.update(manifest['snapshot_hashes'])
        assert sha(bound['checkpoint']) == bound['checkpoint_sha256']
    # Rebuild the conditional operator from the saved estimated phase, and
    # recompute the noise estimate from Y only. Simulation truth is never used.
    sys.path.insert(0, str(ROOT / 'src'))
    from afdm_jadcedd.system.phase import phase_operator
    from afdm_jadcedd.algorithm.baselines.noise_estimation import estimate_spatial_noise
    from afdm_jadcedd.system.observation import array_sha256
    for case in previous['cases']:
        folder = OUT / f"cases/{case['index']:03d}"
        frontend = read(folder / 'FRONTEND.json')
        assert frontend['phase_mode'] == frontend['noise_mode'] == 'estimated'
        assert frontend['truth_used_in_inference'] is False
        assert sha(folder / 'input.npz') == case['input_sha256']
        cache = read(folder / 'PHASE_CACHE.json')
        assert sha(folder / 'phase.npz') == cache['phase_sha256']
        with np.load(folder / 'public.npz', allow_pickle=False) as public, np.load(folder / 'phase.npz', allow_pickle=False) as phase, np.load(folder / 'input.npz', allow_pickle=False) as conditional:
            assert {k:array_sha256(public[k]) for k in public.files} == frontend['historical_input_hashes']
            np.testing.assert_array_equal(public['observation'], conditional['observation'])
            np.testing.assert_array_equal(phase_operator(public['pilot'], phase['phase_slopes']), conditional['operator'])
            estimated_noise, noise_record = estimate_spatial_noise(public['observation'])
            assert not noise_record['supplied_noise_variance_used']
            assert np.isclose(estimated_noise, float(conditional['noise_variance']), rtol=1e-12, atol=1e-12)
    local = {p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file()}
    plan = dict(schema='standard20-four-receivers-gpu-v1', created_unix=time.time(),
        authorization='User explicitly requested ten/seven/five-layer and legacy comparison on 20 paired K40/Q16/0dB scenes with estimated phase/noise.',
        condition=previous['condition'], scale=previous['scale'], phase_mode='estimated', noise_mode='estimated',
        threshold=.5, methods=list(METHODS), cases=previous['cases'], models=models,
        legacy_configuration=previous['legacy_configuration'], protected_hashes=protected, local_hashes=local,
        device='cuda', cpu_threads=4, allow_tf32=False,
        warmup='One untimed execution of the fixed first scene per method, in eval mode with no optimizer or tuning.',
        bootstrap=dict(samples=10000, seed=2026102199, unit='paired physical scene'),
        model_selection='Original validation-selected checkpoints fixed before this panel; ten-layer selected epoch 1.',
        inference_truth_boundary='Only estimated conditional input.npz is passed to each receiver. Separate truth.npz is loaded after inference for scoring.',
        timing='All four methods newly run sequentially on RTX5080, FP32 TF32 off, four CPU threads. Synchronized CPU conditional inputs to CPU predictions, including method preparation and transfer. Common estimated phase/noise frontend, disk I/O, model load, warmup, scoring and plotting excluded. Desktop background remains. This is conditional receiver timing, not full end-to-end latency or equal-accuracy speedup.',
        scope='Previously revealed formal panel of all 20 saved DFT scenes. Descriptive paired comparison, not independent confirmation. Depth, training objective and distribution differ simultaneously.',
        legacy_difference_from_5db='Formal damping 0.2; previous known-phase 5dB comparison used 0.1. Same three checkpoint files; original stopping criteria retained.',
        soft_timeout_seconds=7200)
    write(OUT / 'PLAN.json', plan)
    write(OUT / 'PLAN_SHA256.json', dict(sha256=sha(OUT / 'PLAN.json')))
    verify(plan)
    write(OUT / 'PREPARATION_AUDIT.json', dict(status='PASSED', input_cases=20, same_saved_public_inputs=True,
        shared_estimated_operators_rebuilt=20, observation_only_noise_estimates_checked=20,
        selected_ten_layer_epoch=1, plan_sha256=sha(OUT / 'PLAN.json')))
    status('PREPARED')


def setup():
    import torch
    from threadpoolctl import threadpool_limits
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    threadpool_limits(4)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cudnn.benchmark = False
    return torch


class Adapter:
    def __init__(self, method, plan):
        import torch
        self.method, self.plan, self.scale = method, plan, plan['scale']
        if method == LEGACY:
            sys.path.insert(0, str(ROOT / 'src'))
            from afdm_jadcedd.algorithm.proposed.receiver import Receiver
            self.model = Receiver(plan['legacy_configuration'], device='cuda')
            self.networks = [self.model.model.first, self.model.model.second, self.model.evidence.network]
            self.checkpoint_bytes = sum((ROOT / plan['legacy_configuration'][k]).stat().st_size for k in ('first_checkpoint','second_checkpoint','evidence_checkpoint'))
            return
        bound = plan['models'][method]
        run = Path(bound['run'])
        os.environ['AFDM_LSTMP_ROOT'] = str(ROOT)
        os.environ['AFDM_LSTMP_CONFIG'] = bound['config']
        sys.path.insert(0, str(run / 'source_code'))
        from experiments.lstmp_candidate_20261019 import common, data
        assert common.OUT.resolve() == run.resolve()
        receiver = importlib.import_module('experiments.' + bound['package'] + '.receiver')
        state = torch.load(bound['checkpoint'], map_location='cpu', weights_only=False, mmap=True)
        assert state['depth'] == bound['depth'] and state['epoch'] == bound['selected_epoch']
        if method == NEW:
            assert state['manifest_sha256'] == bound['manifest_sha256']
        else:
            assert state['scale'] == self.scale
        self.data, self.depth = data, bound['depth']
        self.model = receiver.Receiver()
        for _ in range(self.depth):
            self.model.add_layer(None)
        self.model.load_state_dict(state['state'], strict=True)
        self.model.cuda().eval()
        self.model.use_checkpoint = False
        if hasattr(self.model, 'graphs_enabled'):
            self.model.graphs_enabled = False
        self.networks, self.checkpoint_bytes = [self.model], Path(bound['checkpoint']).stat().st_size

    def prepare(self, public):
        if self.method == LEGACY:
            return public
        values = dict(y=public.observation, a=public.operator, noise=public.noise_variance, rho=public.activity_prior)
        # These internal flags consume the common estimated operator and noise;
        # they do not grant either receiver access to simulated truth.
        return self.data.prepare_public(values, self.scale, 'cuda', phase_mode='known', noise_mode='known')[0]

    def infer(self, prepared):
        if self.method == LEGACY:
            return self.model.infer(prepared)
        import torch
        before = self.model.score_evaluations
        outputs, diagnostics = self.model(prepared)
        final = outputs[-1]
        x, logits = (final['estimate'], final['logits']) if isinstance(final, dict) else final
        value = x.cpu().numpy()
        arrays = dict(estimate=(value[:,0].astype(np.float64)+1j*value[:,1].astype(np.float64))*self.scale,
                      probabilities=torch.sigmoid(logits).cpu().numpy())
        record = dict(iterations=self.depth, converged=None, stopping_reason=f'FIXED_{self.depth}_LAYERS',
            first_score_calls=self.model.score_evaluations-before, first_score_samples=self.depth*40,
            second_score_calls=0, second_score_samples=0, classifier_calls=self.depth, classifier_samples=self.depth*40,
            diagnostics=diagnostics)
        return arrays, record


def worker(method):
    plan = read(OUT / 'PLAN.json')
    verify(plan)
    folder = OUT / method
    if folder.exists():
        raise FileExistsError('Method outputs already exist; never repeat inference silently: ' + method)
    folder.mkdir()
    torch = setup()
    core = module(OUT / 'source/paired_core.py', 'standard_gpu_core')
    start = time.perf_counter()
    adapter = Adapter(method, plan)
    torch.cuda.synchronize()
    overhead = dict(**core.model_size(adapter.networks), checkpoint_file_bytes=adapter.checkpoint_bytes,
                    model_load_seconds=time.perf_counter()-start)
    write(folder / 'OVERHEAD.json', overhead)
    write(folder / 'BINDING.json', dict(method=method, model=plan['models'].get(method, plan['legacy_configuration']),
        plan_sha256=sha(OUT / 'PLAN.json'), device='cuda', gpu=torch.cuda.get_device_name(), torch=torch.__version__,
        cuda=torch.version.cuda, python=platform.python_version(), tf32=False, cpu_threads=4, optimizer_updates=0,
        phase_mode='estimated', noise_mode='estimated', shared_cached_frontend=True))
    from afdm_jadcedd.system.observation import load_input
    status('WARMUP', method=method)
    core.timed_inference(adapter, load_input(OUT / 'cases/000/input.npz'))
    for case in plan['cases']:
        i = case['index']
        status('EVALUATING', method=method, scene=i+1, total=20)
        arrays, record, times = core.timed_inference(adapter, load_input(OUT / f'cases/{i:03d}/input.npz'))
        with np.load(OUT / f'cases/{i:03d}/truth.npz', allow_pickle=False) as truth:
            scores = core.score_arrays(arrays['estimate'], arrays['probabilities'], truth['channel'], truth['activity'], threshold=.5)
        np.savez_compressed(folder / f'{i:03d}.npz', **arrays)
        write(folder / f'{i:03d}_trace.json', record)
        row = dict(status='COMPLETE', case_index=i, seed=case['seed'], input_sha256=case['input_sha256'],
            prediction_sha256=sha(folder / f'{i:03d}.npz'), **scores, **times,
            **{k:record[k] for k in ('iterations','converged','stopping_reason','first_score_calls','second_score_calls','classifier_calls')})
        write(folder / f'{i:03d}.json', row)
        print(json.dumps(dict(method=method, completed=i+1, nmse_db=10*np.log10(scores['nmse']),
            misses=scores['misses'], false_alarms=scores['false_alarms'], seconds=times['total_seconds'])), flush=True)
    verify(plan)
    write(folder / 'COMPLETE.json', dict(status='COMPLETE', scenes=20, plan_sha256=sha(OUT / 'PLAN.json')))


def report():
    plan = read(OUT / 'PLAN.json')
    verify(plan)
    core = module(OUT / 'source/paired_core.py', 'standard_report_core')
    paired, summaries = {}, {}
    for method in METHODS:
        assert read(OUT / method / 'COMPLETE.json')['scenes'] == 20
        rows=[]
        for case in plan['cases']:
            i=case['index']; folder=OUT/method
            row=read(folder/f'{i:03d}.json')
            assert row['case_index']==i and row['seed']==case['seed'] and row['input_sha256']==case['input_sha256']
            assert sha(folder/f'{i:03d}.npz')==row['prediction_sha256']
            with np.load(folder/f'{i:03d}.npz',allow_pickle=False) as pred, np.load(OUT/f'cases/{i:03d}/truth.npz',allow_pickle=False) as truth:
                score=core.score_arrays(pred['estimate'],pred['probabilities'],truth['channel'],truth['activity'],threshold=.5)
            assert all(np.isclose(score[k],row[k],rtol=1e-12,atol=1e-12) for k in score)
            if method!=LEGACY:
                assert row['iterations']==plan['models'][method]['depth']
            rows.append(row)
        paired[method]=rows
        s=dict(core.summarize(rows),**read(OUT/method/'OVERHEAD.json'))
        s.update(missed_detection_rate=s['misses']/s['active'],false_alarm_rate=s['false_alarms']/s['inactive'],
            fixed_depth_scenes=sum(r['stopping_reason'].startswith('FIXED_') for r in rows))
        summaries[method]=s
    indices=np.random.default_rng(plan['bootstrap']['seed']).integers(0,20,(10000,20))
    boot={}
    for method,rows in paired.items():
        total=lambda k:np.asarray([r[k] for r in rows])[indices].sum(1)
        boot[method]=dict(pooled_nmse_db=10*np.log10(total('error_energy')/total('truth_energy')),
            aer=(total('misses')+total('false_alarms'))/(total('active')+total('inactive')),
            missed_detection_rate=total('misses')/total('active'),false_alarm_rate=total('false_alarms')/total('inactive'))
    comparisons={}
    for method in METHODS[1:]:
        delta=[dict(case_index=a['case_index'],seed=a['seed'],nmse_db_delta=float(10*np.log10(a['nmse']/b['nmse'])),
            misses_delta=a['misses']-b['misses'],false_alarms_delta=a['false_alarms']-b['false_alarms']) for a,b in zip(paired[NEW],paired[method])]
        comparisons[method]=dict(new_minus_reference={k:summaries[NEW][k]-summaries[method][k] for k in boot[NEW]},
            paired_95_percentile={k:np.quantile(boot[NEW][k]-boot[method][k],[.025,.975]).tolist() for k in boot[NEW]},
            lower_nmse_scenes=sum(d['nmse_db_delta']<0 for d in delta),per_scene=delta)
    summary=dict(status='COMPLETE',condition=plan['condition'],phase_mode='estimated',noise_mode='estimated',
        methods=summaries,comparisons=comparisons,timing=plan['timing'],scope=plan['scope'],
        legacy_configuration_difference=plan['legacy_difference_from_5db'],plan_sha256=sha(OUT/'PLAN.json'))
    write(OUT/'SUMMARY.json',summary)
    for name,rows in (('summary.csv',[dict(method=m,**summaries[m]) for m in METHODS]),
                      ('per_scene.csv',[dict(method=m,**r) for m in METHODS for r in paired[m]])):
        with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.DictWriter(f,list(dict.fromkeys(k for r in rows for k in r)));w.writeheader();w.writerows(rows)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(2,3,figsize=(15,8),constrained_layout=True)
    keys=('pooled_nmse_db','aer','missed_detection_rate','false_alarm_rate','mean_seconds','peak_allocated_bytes')
    titles=('Channel NMSE (dB)','Activity error (%)','Missed detection (%)','False alarm (%)','Receiver seconds / scene','Peak allocated GPU memory (MiB)')
    for ax,key,title,scale in zip(axes.flat,keys,titles,(1,100,100,100,1,1/2**20)):
        bars=ax.bar(('V3 ten','Prior seven','Prior five','Legacy'),[summaries[m][key]*scale for m in METHODS],color=('#227C9D','#65A879','#9B80B4','#ED8B3A'))
        ax.bar_label(bars,fmt='%.3f',padding=3,fontsize=9);ax.set_title(title);ax.margins(y=.25)
        ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
        if key=='mean_seconds': ax.set_yscale('log')
    fig.suptitle('Same 20 formal scenes | K40 / Q16 / p0.1 / 0 dB | Estimated phase and noise\nAll four newly run on RTX5080, FP32 / TF32 off; shared cached frontend excluded',fontsize=12)
    fig.savefig(OUT/'comparison.png',dpi=180);fig.savefig(OUT/'comparison.pdf');plt.close(fig)
    lines=['标准工况：十层、七层、五层和旧三网络的20场景配对比较','',
        '40用户、16导频、0 dB、活动概率0.1；估计相位和噪声；活动门限0.5。',
        '全部方法在同一5080上依次重新推断，FP32且关闭TF32；使用原验证选定权重，十层为第1轮。',
        '复用全部20个历史物理场景和共同估计前端，种子202610180400001至202610180400020。',
        '旧三网络正式阻尼0.2，最多600次，保留原收敛规则；上一组5dB已知相位比较的阻尼是0.1。','',
        '方法 | 信道NMSE/dB | AER | 漏检率 | 虚警率 | 漏检/虚警 | 平均秒/场景 | 峰值已分配显存/MiB']
    for method,label in zip(METHODS,LABELS):
        s=summaries[method]
        lines.append(f"{label} | {s['pooled_nmse_db']:.4f} | {s['aer']:.3%} | {s['missed_detection_rate']:.3%} | {s['false_alarm_rate']:.3%} | {s['misses']}/{s['false_alarms']} | {s['mean_seconds']:.4f} | {s['peak_allocated_bytes']/2**20:.1f}")
    lines += ['', '十层减参考方法的差值与10000次按场景配对重抽样的95%描述性区间：']
    for method,label in zip(METHODS[1:],LABELS[1:]):
        c=comparisons[method]
        lines.append(f"{label}：NMSE更低 {c['lower_nmse_scenes']}/20场景")
        for k in boot[NEW]:
            lines.append(f"  {k}: {c['new_minus_reference'][k]:.8g}; 95% {c['paired_95_percentile'][k]}")
    lines += ['', '计时不含共同相位/噪声估计前端、磁盘读写、模型加载、预热和评分；不是完整端到端时延。桌面背景仍在。',
        '这是已揭示的小样本单工况比较；不得声称新的独立确认、等精度加速或将差异单独归因于层数。',
        '原始全部场景、预测、逐场景结果、配对差值、权重和源码哈希均保留。']
    (OUT/'REPORT.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    write(OUT/'RESULT_AUDIT.json',dict(status='PASSED',predictions_rescored=80,all_twenty_retained=True,
        same_observation_and_estimated_frontend=True,all_four_new_cuda_inferences=True,tf32=False,
        plan_sha256=sha(OUT/'PLAN.json'),summary_sha256=sha(OUT/'SUMMARY.json'),checked_unix=time.time()))
    write(OUT/'COMPLETE.json',dict(status='COMPLETE',completed_unix=time.time(),scene_counts=dict.fromkeys(METHODS,20),
        plan_sha256=sha(OUT/'PLAN.json'),summary_sha256=sha(OUT/'SUMMARY.json'),audit_sha256=sha(OUT/'RESULT_AUDIT.json')))


def run():
    plan=read(OUT/'PLAN.json');verify(plan)
    if (OUT/'COMPLETE.json').exists():
        print('ALREADY_COMPLETE');return
    if (OUT/'RUNNING.lock').exists():
        raise RuntimeError('Existing comparison lock; inspect its process before proceeding')
    if any((OUT/m).exists() for m in METHODS):
        raise RuntimeError('Prior method outputs found; preserve and inspect before any resume')
    guard=module(OUT/'source/gpu_preflight.py','standard_gpu_preflight')
    check=guard.check_gpu_idle(OUT)
    if not check['ready']:
        status('WAITING_FOR_GPU',reasons=check['reasons'],evidence_file=check['evidence_file']);return
    lock=OUT/'RUNNING.lock';fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    os.write(fd,str(os.getpid()).encode());os.close(fd)
    started=time.time()
    try:
        for method in METHODS:
            subprocess.run([sys.executable,str(OUT/'source'/Path(__file__).name),'--worker',method],cwd=ROOT,check=True)
        report()
        write(OUT/'EXECUTION.json',dict(started_unix=started,ended_unix=time.time(),duration_seconds=time.time()-started,
            process_id=os.getpid(),exit_code=0,methods=list(METHODS),preflight_evidence=check['evidence_file']))
        status('COMPLETE',output=str(OUT))
    except BaseException as error:
        write(OUT/f'FAILURE_{time.time_ns()}.json',dict(error=repr(error),traceback=traceback.format_exc()))
        status('FAILED',error=repr(error));raise
    finally:
        lock.unlink(missing_ok=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--prepare',action='store_true');parser.add_argument('--run',action='store_true')
    parser.add_argument('--worker',choices=METHODS);parser.add_argument('--report',action='store_true')
    args=parser.parse_args()
    if args.prepare:prepare()
    elif args.worker:worker(args.worker)
    elif args.run:run()
    elif args.report:report()
    else:parser.error('Choose --prepare or --run')
