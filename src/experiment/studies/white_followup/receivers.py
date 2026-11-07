"""Paired white-network follow-up stages; each stage waits for figure adoption.

Only this module's new stage folders are written. Historical inputs and completed
main-SNR predictions are read and independently rescored before reuse.
"""
import argparse
from collections import Counter
from copy import deepcopy
import csv
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback

import psutil

from experiment.studies.provenance import execution_identity
from .common import (ROOT, OUT, ARCHIVE, CONFIG, PHASE_CONFIG, checked, publish,
                     identity, acquire, verify_plan, read_json, write_json, sha256)

MODULE = 'experiment.studies.white_followup.receivers'
STAGES = ('pilot_frames', 'user_count', 'activity_probability', 'cross_channel')
SOURCES = {
    'pilot_frames': 'c_stmp_variance_em_1000_20261026',
    'user_count': 'stmp_500_k60_k80_k100_beta01_20261027',
    'activity_probability': 'stmp_c_stmp_500_20261026',
    'cross_channel': 'stmp_c_stmp_500_20261026',
}
REFERENCES = {
    'GP_MP': 'white_preconditioned_matched_fp32_1000_snr_20261105',
    'GP_MP_EP': 'white_phase_frontend_marginal_1000_20261106',
    'offgrid13': 'offgrid_search_budgets_1000_cpu_20261105',
    'offgrid25': 'offgrid_search_budgets_1000_cpu_20261105',
}
NATIVE = Path('E:/afdm-gfra-results/white_followup_20261107')
FIELDS = ('full_error', 'signal_energy', 'active_error', 'inactive_error',
          'active', 'inactive', 'misses', 'false_alarms')


def stage_folder(stage):
    if stage not in STAGES:
        raise ValueError('Unknown follow-up stage')
    return ROOT / 'result' / stage / 'data/white_mainline_500_20261107'


def methods_for(stage):
    return ['GP_MP'] if stage == 'cross_channel' else list(REFERENCES)


def task_key(method, case):
    return f"{method}_scene{case['scene']:04d}_condition{case['index']:02d}"


def input_key(case):
    return str(case['ready']).replace('\\', '/').lower()


def state_read(path):
    """Retry only STATE/STATUS sharing violations, never malformed JSON."""
    path = Path(path)
    for attempt in range(11):
        try:
            return read_json(path)
        except PermissionError:
            if path.name not in ('STATE.json', 'STATUS.json') or attempt == 10:
                raise
            time.sleep(.05)


def job_read(path):
    """Allow up to two seconds for a published job's Windows sharing lock."""
    for attempt in range(41):
        try:
            return read_json(path)
        except PermissionError:
            if attempt == 40:
                raise
            time.sleep(.05)


def is_live(token):
    try:
        p = psutil.Process(token['pid'])
        return (abs(p.create_time() - token['created_unix']) < .01
                and p.cmdline() == token['command'])
    except psutil.NoSuchProcess:
        return False


def no_other_execution(folder):
    current = psutil.Process(os.getpid())
    own = {current.pid: current.create_time()}
    command = current.cmdline()
    child = current
    # Windows venv launchers remain as parents with the same full command.
    # Exempt only this verified ancestry, never another coordinator or worker.
    while True:
        parent = child.parent()
        if parent is None:
            break
        created = parent.create_time()
        if (parent.cmdline() != command
                or Path(parent.exe()).name.lower() not in ('python.exe', 'pythonw.exe')
                or created > child.create_time()
                or psutil.Process(parent.pid).create_time() != created):
            break
        own[parent.pid] = created
        child = parent
    for p in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
        try:
            cmd = p.info['cmdline'] or []
            same_identity = (p.pid in own and p.info['create_time'] == own[p.pid])
            if not same_identity and MODULE in cmd and folder.parts[-3] in cmd:
                raise RuntimeError('Existing follow-up process: ' + str(p.info))
        except psutil.NoSuchProcess:
            pass


def add_assets(assets, path):
    """Bind a configuration and its explicitly hashed dependencies recursively."""
    path = Path(path)
    path = path if path.is_absolute() else ROOT / path
    name = str(path.relative_to(ROOT))
    if name in assets:
        return
    assets[name] = sha256(path)
    if path.suffix.lower() != '.json':
        return
    value = read_json(path)
    if not isinstance(value, dict):
        return
    for key, digest in value.items():
        base = key[:-7] if key.endswith('_sha256') else None
        if base and isinstance(digest, str) and isinstance(value.get(base), str):
            candidate = Path(value[base])
            # Training records also hash states labelled e.g. "random";
            # only path-valued fields name a dependency to open.
            if not candidate.suffix and '/' not in value[base] and '\\' not in value[base]:
                continue
            candidate = candidate if candidate.is_absolute() else ROOT / candidate
            checked(candidate, digest)
            add_assets(assets, candidate)


def source_cases(stage):
    source = ROOT / 'result' / stage / 'data' / SOURCES[stage]
    plan = read_json(source / 'PLAN.json')
    conditions = plan['conditions']
    cases = []
    for original in read_json(source / 'INPUTS.json'):
        if original['scene'] >= 500:
            continue
        case = {k: deepcopy(original[k]) for k in ('scene', 'index', 'ready', 'ready_sha256', 'files')}
        case['parameters'] = deepcopy(conditions[case['index']])
        cases.append(case)
    validate_coverage(cases, conditions)
    return source, conditions, cases


def validate_coverage(cases, conditions):
    actual = [(c['scene'], c['index']) for c in cases]
    expected = [(s, i) for s in range(500) for i in range(len(conditions))]
    if actual != expected:
        raise ValueError('Inputs must cover each scene 0..499 and each condition exactly once')
    for c in cases:
        if c['parameters'] != conditions[c['index']]:
            raise ValueError('Condition metadata mismatch')


def make_tasks(cases, methods, reference_cases, reference_folders):
    tasks = []
    mappings = {m: {input_key(c): c for c in reference_cases[m]} for m in methods}
    for method in methods:
        for position, case in enumerate(cases):
            task = dict(key=task_key(method, case), method=method, position=position)
            ref = mappings[method].get(input_key(case))
            if ref is not None:
                if ref['files'] != case['files'] or ref['ready_sha256'] != case['ready_sha256']:
                    raise ValueError('Equal input path with different bound bytes')
                prefix = f"budget{method[7:]}_" if method.startswith('offgrid') else ''
                name = f"{prefix}scene{ref['scene']:04d}_condition{ref['index']:02d}.json"
                pointer = reference_folders[method] / 'results' / name
                task['reuse'] = dict(pointer=str(pointer), sha256=sha256(pointer),
                                     scene=ref['scene'], index=ref['index'])
            tasks.append(task)
    return tasks


def prepare(stage):
    folder = stage_folder(stage)
    if (folder / 'PLAN.json').exists():
        return verify_plan(folder)
    request = OUT / 'REQUEST.json'
    validation = ARCHIVE / 'VALIDATION.json'
    if read_json(validation)['status'] != 'PASS':
        raise RuntimeError('White mainline relocation validation must pass first')
    read_json(request)
    source, conditions, cases = source_cases(stage)
    methods = methods_for(stage)
    refs, refdirs = {}, {}
    assets = {}
    for path in (request, validation, CONFIG, PHASE_CONFIG, source/'PLAN.json', source/'INPUTS.json'):
        add_assets(assets, path)
    for method in methods:
        refdir = ROOT / 'result/snr_comparison/data' / REFERENCES[method]
        completion = read_json(refdir / 'COMPLETION.json')
        if completion['status'] != 'PASS':
            raise RuntimeError('Incomplete main-SNR reference')
        checked(refdir / 'SUMMARY.json', completion['summary_sha256'])
        for name in ('COMPLETION.json', 'SUMMARY.json', 'PLAN.json', 'INPUTS.json'):
            add_assets(assets, refdir / name)
        refs[method], refdirs[method] = read_json(refdir/'INPUTS.json'), refdir
    tasks = make_tasks(cases, methods, refs, refdirs)
    configurations = dict(GP_MP=str(CONFIG.relative_to(ROOT)), GP_MP_EP=str(PHASE_CONFIG.relative_to(ROOT)),
                          offgrid13='src/configs/candidates/offgrid_sbl_budget13_20261105.json',
                          offgrid25='src/configs/candidates/offgrid_sbl_budget25_20261105.json')
    for method in methods:
        add_assets(assets, configurations[method])
    if any(m.startswith('offgrid') for m in methods):
        for name in ('offgrid_sbl.json','offgrid_readout_policy.json','baseline_noise.json'):
            add_assets(assets, ROOT/'src/configs/final'/name)
    for part in ('receiver/gp_mp', 'receiver/stmp', 'receiver/baseline', 'scenario', 'waveform', 'channel', 'networks'):
        for path in (ROOT/'src'/part).rglob('*.py'):
            add_assets(assets, path)
    for name in ('fileio.py', 'workspace.py', 'experiment/metrics.py', 'experiment/storage.py',
                 'receiver/baseline/search_budget.py',
                 'experiment/studies/white_followup/common.py',
                 'experiment/studies/white_followup/receivers.py'):
        add_assets(assets, ROOT/'src'/name)
    if not (ROOT/'src/receiver/gp_mp/receiver.py').is_file():
        raise RuntimeError('White mainline implementation is not installed')
    folder.mkdir(parents=True, exist_ok=True)
    for name in ('results', 'sessions'):
        (folder/name).mkdir(exist_ok=True)
    write_json(folder/'INPUTS.json', cases)
    write_json(folder/'TASKS.json', tasks)
    add_assets(assets, folder/'INPUTS.json')
    add_assets(assets, folder/'TASKS.json')
    snapshots = {m: read_json(ROOT/configurations[m]) for m in methods}
    plan = dict(schema='white-followup-500-v1', stage=stage, scene_count=500, conditions=conditions,
                methods=methods, planned=len(tasks), new=sum('reuse' not in t for t in tasks),
                reused=sum('reuse' in t for t in tasks), configurations=configurations,
                configuration_snapshots=snapshots, receiver_configuration=read_json(CONFIG),
                reference_plan_hashes={m:sha256(refdirs[m]/'PLAN.json') for m in methods},
                native_directory=str(NATIVE/stage), source=str(source), assets=assets,
                runtime=dict(max_workers=3, threads_per_worker=2, worker_peak_budget_gib=2.5,
                             cpu_worker_peak_budget_gib=1.8, minimum_free_ram_gib=1.25,
                             gpu_budget_gib_per_worker=6., minimum_free_gpu_gib=1.,
                             input_timeout_seconds=7200, total_timeout_seconds=14*86400,
                             minimum_free_disk_gib=10., poll_seconds=.2),
                automatic_retry=False, training=False, phase_policy='GP_MP_EP uses only raw observation and pilot; estimate once and hold fixed',
                user_count_policy='White GP_MP and GP_MP_EP use beta=.4 for every input, including K80 scene372 and all K100; historical exceptions are not adopted.',
                baseline_policy='Existing baseline curves remain unchanged; this stage does not claim old retired predictions were rescored.',
                adoption_required=True, created_unix=time.time())
    write_json(folder/'PLAN.json', plan)
    write_json(folder/'PLAN_HASH.json', dict(sha256=sha256(folder/'PLAN.json')))
    publish(folder/'STATUS.json', dict(stage='PREPARED', planned=len(tasks), completed=0,
                                     new=plan['new'], reused=plan['reused'], updated_unix=time.time()))
    return plan


def verify_inputs(case, hashes=None):
    folder = Path(case['ready']).parent
    checked(case['ready'], case['ready_sha256'])
    if hashes is not None:
        hashes[case['ready']] = case['ready_sha256']
    for name, digest in case['files'].items():
        checked(folder/name, digest)
        if hashes is not None:
            hashes[str(folder/name)] = digest
    ready = read_json(case['ready'])
    if ready['identity']['condition'] != case['parameters']:
        raise ValueError('Saved condition differs from stage plan')
    return folder


def same_metrics(saved, actual):
    import numpy as np
    for key in ('active', 'inactive', 'misses', 'false_alarms', 'decisions'):
        if saved[key] != actual[key]:
            raise ValueError('Changed decision count: ' + key)
    for key in ('full_error', 'signal_energy', 'active_error', 'inactive_error', 'per_user_error'):
        np.testing.assert_allclose(saved[key], actual[key], rtol=1e-11, atol=1e-12)


def validate_numerics(method, prediction, record, plan, case):
    import numpy as np
    if not all(np.isfinite(a).all() for a in prediction.values()):
        raise FloatingPointError('Nonfinite saved prediction')
    users = case['parameters']['users']
    if prediction['estimate'].shape != (users,16,16,16) or prediction['activity_decision'].shape != (users,):
        raise ValueError('Prediction shape differs from public condition')
    if method.startswith('GP_MP'):
        if record['configuration'] != plan['receiver_configuration']:
            raise ValueError('Receiver controls or white binding differ')
        if record['denoiser_training_noise'] != 'white Gaussian':
            raise ValueError('White trained network required')
        if record['receiver_truth_used'] or record['noise_truth_used']:
            raise ValueError('Unexpected channel/activity/noise truth use')
        if record['iterations'] > 600 or record['configuration']['ep']['damping'] != .4:
            raise ValueError('Changed iteration budget or damping')
        p = prediction['probabilities']
        if p.shape != (users,) or np.any((p < 0) | (p > 1)):
            raise ValueError('Invalid activity probabilities')
        np.testing.assert_array_equal(prediction['activity_decision'], p >= .5)
        if method == 'GP_MP_EP':
            if record['frontend_binding'] != plan['configuration_snapshots'][method]:
                raise ValueError('Changed phase frontend binding')
            for key in ('oracle_phase_supplied', 'supplied_phase_operator_used', 'initializer_gain_or_power_forwarded'):
                if record[key]:
                    raise ValueError('Unexpected phase truth/operator forwarding')
            if record['phase_mode'] != 'estimated' or record['phase_updates_inside_receiver'] != 0:
                raise ValueError('Estimated phase must remain fixed')
            if record['phase_initialization']['truth_used_in_inference']:
                raise ValueError('Phase initialization used truth')
            if record['input_fields'] != ['observation', 'pilot', 'activity_prior']:
                raise ValueError('Wrong estimated-phase inputs')
            np.testing.assert_array_equal(prediction['phase'], prediction['initial_phase'])
            np.testing.assert_array_equal(prediction['phase_slopes'], prediction['initial_phase_slopes'])
        elif record['phase_mode'] != 'known' or not record['oracle_phase_supplied']:
            raise ValueError('Known-phase operator must be declared')
    else:
        if record['budget_configuration'] != plan['configuration_snapshots'][method]:
            raise ValueError('Changed SBL budget')
        if record['iterations'] > 120 or record['noise_truth_used'] or record['truth_used_in_inference']:
            raise ValueError('Changed SBL budget or unexpected truth use')
        if record['backend'] != 'cpu' or record['new_threshold_calibration']:
            raise ValueError('SBL must use CPU and unchanged adopted readout')


def validate_result(folder, plan, task, case, *, source=False, hashes=None):
    """Rescore original or new complete arrays; a pointer alone is never success."""
    from experiment.storage import arrays
    from experiment.metrics import score_arrays
    pointer = Path(task['reuse']['pointer']) if source else folder/'results'/(task['key']+'.json')
    if source:
        checked(pointer, task['reuse']['sha256'])
    link = read_json(pointer)
    path = checked(link['result'], link['sha256'])
    row = read_json(path)
    if row['status'] != 'COMPLETE' or row.get('preflight', False):
        raise ValueError('Only complete formal predictions may be reused')
    if row.get('input_files', row.get('input_hashes')) != case['files']:
        raise ValueError('Result is not paired to this saved input')
    if source or link.get('origin') == 'main_snr':
        if row['plan_sha256'] != plan['reference_plan_hashes'][task['method']]:
            raise ValueError('Main-SNR result plan binding differs')
    expected = task['reuse'] if source or link.get('origin') == 'main_snr' else case
    if (row['scene'], row['index']) != (expected['scene'], expected['index']):
        raise ValueError('Result scene or condition differs')
    native = path.parent
    pred = Path(row.get('prediction', native/'prediction.npz'))
    rec = Path(row.get('record', native/'record.json'))
    files = row.get('files', {})
    if not files:
        files = {str(pred): row['prediction_sha256'], str(rec): row['record_sha256']}
    if str(pred) not in files or str(rec) not in files:
        raise ValueError('Result has no bound prediction or record')
    for name, digest in files.items():
        checked(name, digest)
    prediction, record = arrays(pred), read_json(rec)
    method = task['method']
    validate_numerics(method, prediction, record, plan, case)
    if row['iterations'] != record['iterations'] or row['stopping_reason'] != record['stopping_reason']:
        raise ValueError('Result and numerical record disagree')
    if method.startswith('GP_MP'):
        if any(row['environment'][k] for k in ('tf32', 'cudnn_tf32', 'cudnn_benchmark')):
            raise ValueError('FP32 controls changed')
    if not source and link.get('origin') != 'main_snr':
        if native.parent != Path(plan['native_directory']) or native.name != task['key']:
            raise ValueError('New result is outside this stage native directory')
        if row['plan_sha256'] != sha256(folder/'PLAN.json'):
            raise ValueError('Result plan binding changed')
        manifest = read_json(native/'INPUT_MANIFEST.json')
        if manifest['case'] != case or manifest['task'] != task:
            raise ValueError('Result manifest changed')
    input_folder = verify_inputs(case, hashes)
    metrics = score_arrays(prediction, arrays(input_folder/'truth.npz'))
    same_metrics(row['metrics'], metrics)
    if hashes is not None:
        hashes.update(files)
        hashes[str(path)] = link['sha256']
        hashes[str(pointer)] = sha256(pointer)
    return dict(method=method, scene=case['scene'], index=case['index'], metrics=metrics,
                iterations=row['iterations'], stopping_reason=row['stopping_reason'],
                source_result=str(path), origin='main_snr' if source or link.get('origin') == 'main_snr' else 'new')


def build_receiver(method, plan):
    if method == 'GP_MP':
        from receiver.gp_mp.receiver import Receiver
        return Receiver(plan['configurations'][method], device='cuda', noise_mode='estimated')
    if method == 'GP_MP_EP':
        from receiver.gp_mp.phase_receiver import PhaseReceiver
        return PhaseReceiver(plan['configurations'][method], device='cuda', noise_mode='estimated')
    from receiver.baseline.search_budget import Receiver
    return Receiver(plan['configurations'][method])


def receiver_input(method, source):
    import numpy as np
    if method == 'GP_MP_EP':
        from channel.unknown_phase import UnknownPhaseInput
        with np.load(source/'raw.npz', allow_pickle=False) as z:
            return UnknownPhaseInput(z['y'], z['pilot'], 1., float(z['rho']))
    from channel.observation import ReceiverInput
    with np.load(source/'public.npz', allow_pickle=False) as z:
        return ReceiverInput(z['y'], z['a'], 1., float(z['rho']))


def execute_case(receiver, folder, plan, task, case):
    from experiment.storage import arrays as load_arrays, save_arrays
    from experiment.metrics import score_arrays
    source = verify_inputs(case)
    inputs = receiver_input(task['method'], source)
    native = Path(plan['native_directory'])/task['key']
    native.mkdir(parents=True, exist_ok=False)
    began = time.time()
    write_json(native/'START.json', dict(identity(), started_unix=began, execution=execution_identity()))
    write_json(native/'INPUT_MANIFEST.json', dict(case=case, task=task, plan_sha256=sha256(folder/'PLAN.json')))
    try:
        prediction, record = receiver.infer(inputs)
        validate_numerics(task['method'], prediction, record, plan, case)
        save_arrays(native/'prediction.npz', prediction)
        write_json(native/'record.json', record)
        # Channel/activity truth is evaluator-only and read after predictions are saved.
        truth = load_arrays(source/'truth.npz')
        metrics = score_arrays(load_arrays(native/'prediction.npz'), truth)
        environment = dict(threads=2, backend='cpu')
        if task['method'].startswith('GP_MP'):
            import torch
            environment.update(backend='cuda', network_dtype='float32',
                               tf32=torch.backends.cuda.matmul.allow_tf32,
                               cudnn_tf32=torch.backends.cudnn.allow_tf32,
                               cudnn_benchmark=torch.backends.cudnn.benchmark)
        row = dict(status='COMPLETE', method=task['method'], scene=case['scene'], index=case['index'],
                   parameters=case['parameters'], phase_mode='estimated' if task['method']=='GP_MP_EP' else 'known',
                   noise_mode='estimated', input_files=case['files'], metrics=metrics,
                   iterations=record['iterations'], stopping_reason=record['stopping_reason'],
                   seconds=time.time()-began, environment=environment, execution=execution_identity(), plan_sha256=sha256(folder/'PLAN.json'),
                   files={str(native/n):sha256(native/n) for n in ('prediction.npz','record.json','INPUT_MANIFEST.json')})
        write_json(native/'RESULT.json', row)
        pointer = folder/'results'/(task['key']+'.json')
        if pointer.exists():
            raise FileExistsError('Preserving existing result pointer')
        write_json(pointer, dict(result=str(native/'RESULT.json'), sha256=sha256(native/'RESULT.json'), origin='new'))
    except Exception:
        write_json(native/'FAILURE.json', dict(status='FAILED', traceback=traceback.format_exc(), automatic_retry=False))
        raise


def worker(stage, session, slot, method):
    from threadpoolctl import threadpool_limits
    folder = stage_folder(stage)
    plan = verify_plan(folder)
    cases, tasks = read_json(folder/'INPUTS.json'), read_json(folder/'TASKS.json')
    home = folder/'sessions'/session/f'{method}_worker{slot}'
    token = identity()
    write_json(home/'IDENTITY.json', token)
    if method.startswith('GP_MP'):
        from .common import setup
        setup()
    else:
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    seq = 0
    def state(stage_name, **extra):
        gpu = 0
        if method.startswith('GP_MP'):
            import torch
            gpu = torch.cuda.memory_reserved()
        publish(home/'STATE.json', dict(token, stage=stage_name, sequence=seq,
                gpu_reserved_bytes=gpu, updated_unix=time.time(), **extra))
    try:
        with threadpool_limits(limits=2):
            receiver = build_receiver(method, plan)
            state('READY')
            while True:
                job = home/f'job{seq:06d}.json'
                if not job.exists():
                    if (home/'EXIT.json').exists() or (folder/'STOP.json').exists() or (folder/'FAILURE.json').exists():
                        break
                    time.sleep(.2)
                    continue
                position = job_read(job)['task_position']
                task = tasks[position]
                if task['method'] != method or 'reuse' in task:
                    raise ValueError('Wrong worker method or dispatch of reusable task')
                state('BUSY', task=task['key'])
                execute_case(receiver, folder, plan, task, cases[task['position']])
                seq += 1
                state('READY', completed=task['key'])
        state('EXITED')
    except Exception:
        failure = dict(token, status='FAILED', method=method, traceback=traceback.format_exc(), automatic_retry=False)
        write_json(home/'FAILURE.json', failure)
        write_json(folder/'FAILURE.json', failure)
        publish(home/'STATE.json', dict(token, stage='FAILED', sequence=seq, updated_unix=time.time()))
        raise


def launch(stage, session, slot, method):
    folder = stage_folder(stage)
    home = folder/'sessions'/session/f'{method}_worker{slot}'
    home.mkdir(parents=True, exist_ok=False)
    command = [str(ROOT/'.venv/Scripts/python.exe'), '-X','utf8','-B','-m',MODULE,
               'worker','--stage',stage,'--session',session,'--slot',str(slot),'--method',method]
    env = dict(os.environ, PYTHONPATH=str(ROOT/'src'), OPENBLAS_NUM_THREADS='2',
               MKL_NUM_THREADS='2', OMP_NUM_THREADS='2', NUMEXPR_NUM_THREADS='2')
    if method.startswith('offgrid'):
        env['CUDA_VISIBLE_DEVICES'] = ''
    else:
        env.pop('CUDA_VISIBLE_DEVICES', None)
    with (home/'stdout.log').open('xb') as stdout, (home/'stderr.log').open('xb') as stderr:
        proc = subprocess.Popen(command, cwd=ROOT, env=env, stdout=stdout, stderr=stderr,
                                creationflags=subprocess.CREATE_NO_WINDOW)
    token = dict(pid=proc.pid, created_unix=psutil.Process(proc.pid).create_time(), command=command,
                 method=method, started_unix=time.time())
    write_json(home/'LAUNCH.json', token)
    return dict(proc=proc, token=token, home=home, method=method, assigned=None, sequence=0)


def capacity(plan, workers, method):
    rt = plan['runtime']
    budget = rt['worker_peak_budget_gib'] if method.startswith('GP_MP') else rt['cpu_worker_peak_budget_gib']
    available = psutil.virtual_memory().available/2**30
    reserve = 0.
    for worker in workers:
        try:
            process = psutil.Process(worker['proc'].pid)
            rss = sum(p.memory_info().rss for p in [process]+process.children(recursive=True))/2**30
            reserve += max(0., budget-rss)
        except psutil.NoSuchProcess:
            pass
    if available-reserve < budget+rt['minimum_free_ram_gib']:
        return False
    if method.startswith('GP_MP'):
        result = subprocess.run(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],
                                capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        free = float(result.stdout.strip().splitlines()[0])/1024
        gpu_reserve = 0.
        for worker in workers:
            statepath = worker['home']/'STATE.json'
            state = state_read(statepath) if statepath.exists() else {}
            gpu_reserve += max(0.,rt['gpu_budget_gib_per_worker']-state.get('gpu_reserved_bytes',0)/2**30)
        return free-gpu_reserve >= rt['gpu_budget_gib_per_worker']+rt['minimum_free_gpu_gib']
    return True


def estimated_bytes(task, case):
    # Measured main-SNR predictions: learned ~5.2 MB, SBL ~2.8 MB at K=40.
    per40 = 6*2**20 if task['method'].startswith('GP_MP') else 3*2**20
    return math.ceil(per40*case['parameters']['users']/40)


def disk_ready(plan, bytes_needed):
    path = Path(plan['native_directory'])
    while not path.exists():
        if path.parent == path:
            raise FileNotFoundError('Native results volume is unavailable')
        path = path.parent
    return shutil.disk_usage(path).free >= bytes_needed+plan['runtime']['minimum_free_disk_gib']*2**30


def adoption_gate(stage):
    i = STAGES.index(stage)
    previous = (ROOT/'result/channel_denoising/data/white_mainline_500_20261107'
                if i == 0 else stage_folder(STAGES[i-1]))
    if read_json(previous/'ADOPTION.json')['status'] != 'PASS':
        raise RuntimeError('Previous stage must be verified and adopted before inference')


def coordinate(stage):
    folder = stage_folder(stage)
    plan = verify_plan(folder)
    adoption_gate(stage)
    no_other_execution(folder)
    lock, token = acquire(folder)
    session = str(time.time_ns())
    sessiondir = folder/'sessions'/session
    sessiondir.mkdir()
    write_json(sessiondir/'START.json', dict(token, session=session, started_unix=time.time()))
    write_json(folder/'START.json', dict(token, session=session, started_unix=time.time()))
    cases, tasks = read_json(folder/'INPUTS.json'), read_json(folder/'TASKS.json')
    workers, completed, began = [], set(), time.time()
    def status(stage_name, **extra):
        publish(folder/'STATUS.json', dict(token, stage=stage_name, session=session,
                completed=len(completed), planned=len(tasks), active_workers=len(workers),
                workers=[w['token'] for w in workers], updated_unix=time.time(), **extra))
    try:
        expected = {t['key']+'.json' for t in tasks}
        if any(p.name not in expected for p in (folder/'results').glob('*.json')):
            raise ValueError('Unexpected result pointer')
        native_root = Path(plan['native_directory'])
        allowed_native = {t['key'] for t in tasks if 'reuse' not in t}
        if native_root.exists() and any(p.name not in allowed_native for p in native_root.iterdir()):
            raise ValueError('Unexpected native output; preserve and inspect')
        status('VALIDATING_SAVED_AND_REUSED')
        for i, task in enumerate(tasks):
            case = cases[task['position']]
            pointer = folder/'results'/(task['key']+'.json')
            native = Path(plan['native_directory'])/task['key']
            if pointer.exists():
                validate_result(folder,plan,task,case)
                completed.add(task['key'])
            elif 'reuse' in task:
                validate_result(folder,plan,task,case,source=True)
                old = read_json(task['reuse']['pointer'])
                write_json(pointer, dict(old,origin='main_snr',source_pointer=task['reuse']))
                completed.add(task['key'])
            elif native.exists():
                raise RuntimeError('Unpointed or partial native output retained: '+str(native))
            else:
                verify_inputs(case)
            if (i+1)%100 == 0:
                status('VALIDATING_SAVED_AND_REUSED', checked=i+1)
        write_json(sessiondir/'RESUME_VALIDATION.json', dict(status='PASS', complete=len(completed),
                    checked_inputs=len(tasks), created_unix=time.time()))
        remaining = [t for t in tasks if t['key'] not in completed]
        required = sum(estimated_bytes(t,cases[t['position']]) for t in remaining)
        if not disk_ready(plan,required):
            status('WAITING_FOR_DISK', expected_additional_bytes=required)
            return
        for method in plan['methods']:
            pending = [i for i,t in enumerate(tasks) if t['method']==method and t['key'] not in completed]
            cursor, nextslot = 0, 0
            while cursor < len(pending) or workers:
                stopped = (folder/'STOP.json').exists()
                failed = (folder/'FAILURE.json').exists()
                disk_low = not disk_ready(plan, (len(workers)+1)*6*2**20*max(c['parameters']['users'] for c in cases)/40)
                if time.time()-began > plan['runtime']['total_timeout_seconds']:
                    raise TimeoutError('Stage exceeded frozen wall-clock budget')
                retained = []
                for w in workers:
                    proc, home = w['proc'], w['home']
                    rc = proc.poll()
                    state = state_read(home/'STATE.json') if (home/'STATE.json').exists() else None
                    if state is not None and state['pid'] != w.get('actual_pid',state['pid']):
                        raise RuntimeError('Worker identity changed')
                    if state is not None:
                        w['actual_pid'] = state['pid']
                        actual = {k:state[k] for k in ('pid','created_unix','command')}
                        if rc is None and state['stage'] not in ('EXITED','FAILED') and not is_live(actual) and proc.poll() is None:
                            raise RuntimeError('Live worker identity does not match state')
                    if w['assigned'] is not None and state and state['sequence'] > w['sequence']:
                        task = tasks[w['assigned']]
                        validate_result(folder,plan,task,cases[task['position']])
                        completed.add(task['key'])
                        w['assigned'], w['sequence'] = None, state['sequence']
                    if rc is not None:
                        if rc != 0 or w['assigned'] is not None or not state or state['stage'] != 'EXITED':
                            if not (folder/'FAILURE.json').exists():
                                write_json(folder/'FAILURE.json',dict(status='FAILED',worker=w['token'],exit_code=rc,automatic_retry=False))
                            failed = True
                        continue
                    if w['assigned'] is not None and time.time()-w['assigned_unix'] > plan['runtime']['input_timeout_seconds']:
                        raise TimeoutError('Input exceeded time budget; running process retained')
                    if w['assigned'] is None and state and state['stage']=='READY':
                        if stopped or failed or disk_low or cursor >= len(pending):
                            if not (home/'EXIT.json').exists():
                                write_json(home/'EXIT.json',dict(reason='drain',created_unix=time.time()))
                        else:
                            position = pending[cursor]
                            write_json(home/f"job{w['sequence']:06d}.json",dict(task_position=position))
                            w['assigned'],w['assigned_unix'] = position,time.time()
                            cursor += 1
                    retained.append(w)
                workers = retained
                stopped = (folder/'STOP.json').exists()
                failed = (folder/'FAILURE.json').exists()
                while (not stopped and not failed and not disk_low and cursor < len(pending)
                       and len(workers) < plan['runtime']['max_workers']
                       and len(workers) < len(pending)-cursor
                       and capacity(plan,workers,method)):
                    workers.append(launch(stage,session,nextslot,method)); nextslot += 1
                state_name = ('DRAINING_FAILURE' if failed else 'DRAINING_STOP' if stopped else
                              'DRAINING_DISK' if disk_low else 'RUNNING' if workers else 'WAITING_FOR_MEMORY')
                status(state_name, method=method, method_dispatched=cursor)
                if (stopped or failed or disk_low) and not workers:
                    status('FAILED' if failed else 'PAUSED' if stopped else 'WAITING_FOR_DISK')
                    return
                time.sleep(.2)
        status('VERIFYING')
        summarize(stage)
        status('WAITING_ADOPTION')
    except Exception:
        if not (folder/'FAILURE.json').exists():
            write_json(folder/'FAILURE.json',dict(status='FAILED',traceback=traceback.format_exc(),automatic_retry=False))
        # Active inference finishes its current input, then sees FAILURE and exits.
        status('DRAINING_FAILURE')
        for w in workers:
            home = w['home']
            if not (home/'EXIT.json').exists():
                write_json(home/'EXIT.json',dict(reason='coordinator failure',created_unix=time.time()))
        for w in workers:
            w['proc'].wait(timeout=plan['runtime']['input_timeout_seconds'])
        workers = []
        status('FAILED')
        raise
    finally:
        # Leave the lock if a timed-out worker is still alive: a follow-up must inspect it.
        if not any(w['proc'].poll() is None for w in workers):
            lock.unlink(missing_ok=True)


def aggregate(rows):
    total = {k:sum(r['metrics'][k] for r in rows) for k in FIELDS}
    return dict(inputs=len(rows),scenes=len(rows),**total,
                nmse_db=10*math.log10(total['full_error']/total['signal_energy']),
                aer=(total['misses']+total['false_alarms'])/(total['active']+total['inactive']),
                mean_iterations=sum(r['iterations'] for r in rows)/len(rows),
                iteration_caps=sum(r['stopping_reason']=='MAX_ITERATIONS' for r in rows),
                stopping_reasons=dict(Counter(r['stopping_reason'] for r in rows)))


def summarize(stage):
    folder = stage_folder(stage)
    no_other_execution(folder)
    plan = verify_plan(folder)
    cases,tasks = read_json(folder/'INPUTS.json'),read_json(folder/'TASKS.json')
    if {p.name for p in (folder/'results').glob('*.json')} != {t['key']+'.json' for t in tasks}:
        raise ValueError('Incomplete or duplicate coverage')
    rows,hashes = [],{}
    for i,task in enumerate(tasks):
        rows.append(validate_result(folder,plan,task,cases[task['position']],hashes=hashes))
        if (i+1)%100 == 0:
            publish(folder/'STATUS.json',dict(stage='VERIFYING',checked=i+1,planned=len(tasks),updated_unix=time.time()))
    summary = []
    for method in plan['methods']:
        for index,parameters in enumerate(plan['conditions']):
            group = [r for r in rows if r['method']==method and r['index']==index]
            if len(group)!=500 or {r['scene'] for r in group} != set(range(500)):
                raise ValueError('Incomplete 500-scene coverage')
            summary.append(dict(method=method,index=index,parameters=parameters,**parameters,**aggregate(group)))
    with (folder/'PER_CASE.csv').open('w',newline='',encoding='utf-8') as f:
        values = [dict(method=r['method'],scene=r['scene'],index=r['index'],origin=r['origin'],
                       **{k:r['metrics'][k] for k in FIELDS},iterations=r['iterations'],stopping_reason=r['stopping_reason']) for r in rows]
        writer=csv.DictWriter(f,fieldnames=list(values[0]));writer.writeheader();writer.writerows(values)
    write_json(folder/'SUMMARY.json',dict(status='VERIFIED',experiment=stage,rows=summary,
               scene_count=500,methods=plan['methods'],all_device_aer=True,energy_aggregated_nmse=True,
               limitations=[plan['baseline_policy'],'Retrospective paired research scenes, not an untouched test set.',
                            'All finite iteration-cap results retained; no performance acceptance threshold.']))
    write_json(folder/'OUTPUT_HASHES.json',hashes)
    verify_plan(folder)
    write_json(folder/'COMPLETION.json',dict(status='PASS',inputs=len(tasks),new=plan['new'],reused=plan['reused'],
               saved_predictions_rescored=len(tasks),exact_coverage=True,input_and_output_hashes_verified=True,
               summary_sha256=sha256(folder/'SUMMARY.json'),output_hashes_sha256=sha256(folder/'OUTPUT_HASHES.json'),
               per_case_sha256=sha256(folder/'PER_CASE.csv'),completed_unix=time.time(),adoption_pending=True,
               inference_workers_exited=True,
               coordinator_exit_requires_live_followup=True))


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('prepare','coordinate','worker','summarize'))
    parser.add_argument('--stage',required=True,choices=STAGES)
    parser.add_argument('--session')
    parser.add_argument('--slot',type=int)
    parser.add_argument('--method',choices=tuple(REFERENCES))
    args=parser.parse_args(argv)
    if args.command=='worker':
        worker(args.stage,args.session,args.slot,args.method)
    else:
        globals()[args.command](args.stage)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
