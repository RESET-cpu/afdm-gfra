"""Isolated paired validation. It never edits FINAL or launches a full suite.

Use --prepare to freeze plan and hashes, --run to execute, --summarize to
rebuild descriptive reports from retained predictions. Truth is confined
to this evaluator and never passed to the candidate phase estimator.
"""
import argparse
import csv
import json
import os
from pathlib import Path
import sys
import time
import traceback

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import numpy as np

from project import ROOT, source_files
from utils import read_json, sha256, write_json
from algorithm.registry import load_models
from algorithm.proposed.inference import ProposedReceiver
from algorithm.proposed import shen_phase
from evaluation.metrics import score_arrays
from evaluation.observations import observation
from evaluation.profiles import generate_profile_case
from evaluation.receivers import setup, synchronize
from evaluation.storage import arrays, save_arrays
from system.observation import ReceiverInput, array_sha256
from system.phase import phase_operator
from system.receiver import phase_estimation

CONFIG = ROOT/'src/configs/candidates/shen_phase_20261021.json'
DEFAULT_OUT = ROOT/'result/candidates/shen_phase_20261021'


def verify(plan):
    for path, expected in plan['files'].items():
        resolved = ROOT/path
        if not resolved.exists():
            receipt = DEFAULT_OUT/'SOURCE_CHANGES.json'
            mapping = read_json(receipt)['archived_execution_sources'] if receipt.exists() else {}
            if path in mapping:
                resolved = ROOT/mapping[path]
        if sha256(resolved) != expected:
            raise ValueError('Frozen pilot source or model changed: '+path)


def prepare(out):
    if (out/'PLAN.json').exists():
        plan = read_json(out/'PLAN.json'); verify(plan)
        return plan
    config = read_json(CONFIG)
    binding = load_models()
    paths = set(source_files()) | {CONFIG, ROOT/'FINAL.json', ROOT/'MAINLINE.json',
        ROOT/'src/configs/final/models.json', ROOT/'src/configs/final/STMP.json',
        ROOT/binding['proposed']['config'], Path(binding['proposed']['checkpoint']),
        ROOT/binding['phase_configuration'], ROOT/'src/tests/test_shen_phase.py'}
    plan = dict(config=config, model_binding=binding, created_unix=time.time(),
        authorization='User requested implementation and conditional full-run adoption on adequate phase validation',
        files={p.relative_to(ROOT).as_posix():sha256(p) for p in sorted(paths)},
        primary_metrics='Mean per-scene full-channel NMSE dB; pooled AER and missed-active rate; active unit-phase MSE over q>0',
        statistical_scope='20 paired independent pilot scenes, 10000 paired resamples. Descriptive intervals; no population equivalence proof.')
    write_json(out/'PLAN.json', plan)
    return plan


def phase_score(phase, truth):
    phase = np.asarray(phase)
    true_phase = np.exp(1j*np.arange(len(phase))[:, None]*truth['phase_slopes'][None])
    active = np.asarray(truth['activity'], bool)
    errors = phase[1:, active]*true_phase[1:, active].conj()
    return dict(phase_mse=float(np.mean(abs(errors-1)**2)),
        phase_rmse_rad=float(np.sqrt(np.mean(np.angle(errors)**2))),
        phase_error_count=int(errors.size), phase_squared_error_sum=float(np.sum(abs(errors-1)**2)),
        active_user_phase_mse=np.mean(abs(errors-1)**2, axis=0).tolist())


def metrics(output, truth):
    result = score_arrays(output, truth)
    result.update(phase_score(output['phase'], truth))
    return result


def checkpoint_row(out, folder, method, output, record, truth, iterations, peak):
    path = folder/(method+'.npz')
    save_arrays(path, output)
    result = metrics(output, truth)
    if metrics(arrays(path), truth) != result:
        raise ValueError('Serialized prediction did not rescore identically')
    row = dict(method=method, status='COMPLETE', metrics=result, record=record,
        prediction_sha256=sha256(path), rescoring='PASSED', iterations=iterations, peak_allocated_mib=peak)
    write_json(folder/(method+'.json'), row)
    return row


def run(out, plan):
    import torch
    from threadpoolctl import threadpool_limits
    verify(plan)
    if (out/'COMPLETE.json').exists():
        for name, expected in read_json(out/'COMPLETE.json')['files'].items():
            if sha256(out/name) != expected:
                raise ValueError('Completed pilot report changed: '+name)
        print('ALREADY_COMPLETE', flush=True)
        return
    if 'src/evaluation/experiments/shen_phase_validation.py' in plan['files']:
        raise ValueError('Historical execution entry was archived; use a new output folder for a new run')
    # An existing formal run must be stopped/resolved by the calling agent;
    # do not delete its lock or execute concurrently to contaminate timings.
    formal_lock = ROOT/'result/final2000/shared/RUNNING.lock'
    if formal_lock.exists():
        raise RuntimeError('Formal experiment lock exists; resolve its process before candidate inference')
    lock_path = out/'RUNNING.lock'
    with lock_path.open('x', encoding='utf-8') as stream:
        json.dump(dict(pid=os.getpid(), started_unix=time.time()), stream)
    try:
        config = plan['config']; binding = plan['model_binding']
        device = setup('cuda')
        with threadpool_limits(4):
            receiver = ProposedReceiver(binding, device)
            warmed = set()
            for i in range(config['scene_count']):
                for c, condition in enumerate(config['conditions']):
                    folder = out/f'scene{i:04d}'/f'condition{c:02d}'
                    folder.mkdir(parents=True, exist_ok=True)
                    seed = config['base_seed']+i
                    if (folder/'INPUT.json').exists():
                        identity = read_json(folder/'INPUT.json')
                        if identity['seed'] != seed or identity['condition'] != condition:
                            raise ValueError('Changed input identity')
                        for name, expected in identity['files'].items():
                            if sha256(folder/name) != expected:
                                raise ValueError('Input bytes changed')
                        raw = arrays(folder/'raw.npz'); truth = arrays(folder/'truth.npz')
                    else:
                        inputs, truth, generation = observation(seed, condition, receiver.scale,
                                                               generator=generate_profile_case)
                        raw = dict(y=inputs.observation, pilot=inputs.pilot, rho=np.array(inputs.activity_prior))
                        save_arrays(folder/'raw.npz', raw); save_arrays(folder/'truth.npz', truth)
                        write_json(folder/'INPUT.json',dict(seed=seed, condition=condition, generation=generation,
                            files={name:sha256(folder/name) for name in ('raw.npz','truth.npz')}))
                    y, pilot, rho = raw['y'], raw['pilot'], float(raw['rho'])
                    warm_key = pilot.shape
                    if warm_key not in warmed:
                        warm, _, _ = observation(config['warmup_seed'], condition, receiver.scale,
                                                  generator=generate_profile_case)
                        receiver.infer(ReceiverInput(warm.observation, warm.pilot, 1., warm.activity_prior))
                        warmed.add(warm_key)
                    methods = ['physical', 'oracle_phase', *config['candidates']]
                    for method in methods:
                        existing = folder/(method+'.json')
                        if existing.exists():
                            row = read_json(existing)
                            if sha256(folder/(method+'.npz')) != row['prediction_sha256']:
                                raise ValueError('Changed saved prediction')
                            if metrics(arrays(folder/(method+'.npz')), truth) != row['metrics']:
                                raise ValueError('Changed saved metrics')
                            continue
                        synchronize(device); torch.cuda.reset_peak_memory_stats()
                        if method in ('physical', 'oracle_phase'):
                            phase_seconds = 0.
                            if method == 'physical':
                                from system.receiver.unknown_phase import UnknownPhaseInput
                                controls = phase_estimation.Controls(**read_json(ROOT/binding['phase_configuration'])['phase_estimation'])
                                fitted, front = phase_estimation.estimate(UnknownPhaseInput(y, pilot, 1., rho), controls)
                                beta = fitted['phase_slopes']; phase_seconds = front['seconds']
                                save_arrays(folder/'physical_front.npz', fitted)
                                write_json(folder/'PHYSICAL_FRONT.json', front)
                            else:
                                beta = truth['phase_slopes']  # Labeled oracle diagnostic, never a candidate input.
                            phase = np.exp(1j*np.arange(len(pilot))[:, None]*beta[None])
                            started = time.perf_counter()
                            output, record = receiver.infer(ReceiverInput(y, pilot*phase[:, :, None], 1., rho))
                            synchronize(device)
                            record = dict(record, seconds=time.perf_counter()-started+phase_seconds,
                                oracle_phase_supplied=method=='oracle_phase', phase_seconds=phase_seconds,
                                truth_used_in_inference=method=='oracle_phase')
                            output = dict(output, phase=phase, phase_slopes=beta)
                            iteration_rows = []
                        else:
                            iteration_rows = []
                            def observe(outer, phase, values, conditional):
                                iteration_rows.append(dict(outer=outer,
                                    metrics=metrics(dict(values, phase=phase), truth)))
                                if outer == 0 and not (folder/'zero_phase.json').exists():
                                    checkpoint_row(out, folder, 'zero_phase', dict(values,phase=phase),
                                        dict(conditional,phase_seconds=0.,oracle_phase_supplied=False), truth, [],
                                        torch.cuda.max_memory_allocated()/2**20)
                            controls = shen_phase.Controls(**config['controls'],
                                phase_constraint='frame' if method=='shen_frame' else 'slope')
                            output, record = shen_phase.infer(receiver, y, pilot, rho, controls, observer=observe)
                        if not all(np.isfinite(v).all() for v in output.values()):
                            raise FloatingPointError('Nonfinite output; failing scene is retained')
                        row = checkpoint_row(out, folder, method, output, record, truth, iteration_rows,
                                             torch.cuda.max_memory_allocated()/2**20)
                        status = dict(stage='RUNNING', pid=os.getpid(), scene=i+1, scenes=config['scene_count'],
                                      condition=c+1, method=method, updated_unix=time.time())
                        write_json(out/'STATUS.json', status)
                        print(json.dumps(dict(status, nmse_db=row['metrics']['nmse_db'],
                                              phase_mse=row['metrics']['phase_mse'])), flush=True)
            verify(plan)
            summarize(out, plan)
    except BaseException:
        write_json(out/'failures'/f'{time.time_ns()}.json', dict(status='FAILED', traceback=traceback.format_exc()))
        write_json(out/'STATUS.json', dict(stage='FAILED', pid=os.getpid(), updated_unix=time.time()))
        raise
    finally:
        lock_path.unlink()


def summarize(out, plan):
    verify(plan)
    config = plan['config']; gate = config['full_run_gate']
    methods = ['physical','zero_phase','shen_frame','shen_slope','oracle_phase']
    rows, summaries, comparisons, issues = [], [], [], []
    all_passed = True
    for c, cond in enumerate(config['conditions']):
        grouped = {}
        for method in methods:
            group = []
            for i in range(config['scene_count']):
                folder = out/f'scene{i:04d}'/f'condition{c:02d}'
                row = read_json(folder/(method+'.json'))
                prediction = arrays(folder/(method+'.npz')); truth = arrays(folder/'truth.npz')
                if sha256(folder/(method+'.npz')) != row['prediction_sha256'] or metrics(prediction, truth) != row['metrics']:
                    raise ValueError('Retained prediction rescoring failed')
                m = row['metrics']
                entry = dict(condition=c, frames=cond['frames'], snr_db=cond['snr_db'], scene=i,
                    seed=config['base_seed']+i, method=method, nmse_db=m['nmse_db'],
                    active=m['active'], inactive=m['inactive'], misses=m['misses'], false_alarms=m['false_alarms'],
                    phase_mse=m['phase_mse'], phase_rmse_rad=m['phase_rmse_rad'],
                    seconds=row['record']['seconds'], peak_allocated_mib=row['peak_allocated_mib'])
                rows.append(entry); group.append(entry)
            grouped[method] = group
            total = lambda key: sum(r[key] for r in group)
            summary = dict(condition=c, frames=cond['frames'], snr_db=cond['snr_db'], method=method, count=len(group),
                nmse_db=float(np.mean([r['nmse_db'] for r in group])),
                aer=(total('misses')+total('false_alarms'))/(total('active')+total('inactive')),
                miss_rate=total('misses')/total('active'), false_alarm_rate=total('false_alarms')/total('inactive'),
                misses=total('misses'), false_alarms=total('false_alarms'), active=total('active'), inactive=total('inactive'),
                phase_mse=float(np.average([r['phase_mse'] for r in group],weights=[r['active'] for r in group])),
                seconds=float(np.mean([r['seconds'] for r in group])),
                peak_allocated_mib=max(r['peak_allocated_mib'] for r in group))
            summaries.append(summary)
        reference = grouped['physical']
        rng = np.random.default_rng(gate['bootstrap_seed']+c)
        draws = rng.integers(len(reference), size=(gate['bootstrap_replicates'],len(reference)))
        for method in config['candidates']:
            candidate = grouped[method]
            vector = lambda group,key: np.asarray([r[key] for r in group])
            nmse_delta = vector(candidate,'nmse_db')-vector(reference,'nmse_db')
            aer_delta = (vector(candidate,'misses')+vector(candidate,'false_alarms')-
                         vector(reference,'misses')-vector(reference,'false_alarms'))/cond['users']
            miss_diff = vector(candidate,'misses')-vector(reference,'misses')
            active = vector(reference,'active')
            phase_diff = vector(candidate,'phase_mse')-vector(reference,'phase_mse')
            distributions = dict(nmse_db=nmse_delta[draws].mean(axis=1), aer=aer_delta[draws].mean(axis=1),
                miss_rate=miss_diff[draws].sum(axis=1)/active[draws].sum(axis=1),
                phase_mse=(phase_diff[draws]*active[draws]).sum(axis=1)/active[draws].sum(axis=1))
            point = dict(nmse_db=float(nmse_delta.mean()), aer=float(aer_delta.mean()),
                         miss_rate=float(miss_diff.sum()/active.sum()), phase_mse=float(np.average(phase_diff,weights=active)))
            intervals = {key:np.quantile(values,[.025,.975]).tolist() for key,values in distributions.items()}
            cand = next(r for r in summaries if r['condition']==c and r['method']==method)
            ref = next(r for r in summaries if r['condition']==c and r['method']=='physical')
            checks = dict(absolute_phase=cand['phase_mse']<=gate['active_cross_frame_phase_mse_max'],
                relative_phase=cand['phase_mse']<=max(gate['phase_mse_reference_floor'],
                                                     gate['phase_mse_reference_ratio_max']*ref['phase_mse']),
                nmse=intervals['nmse_db'][1]<=gate['paired_nmse_db_upper95_max'],
                aer=intervals['aer'][1]<=gate['paired_aer_upper95_max'],
                miss_rate=intervals['miss_rate'][1]<=gate['paired_miss_rate_upper95_max'])
            comparison = dict(condition=c,method=method,delta_candidate_minus_reference=point,
                descriptive_paired_95_interval=intervals, checks=checks, passed=all(checks.values()),
                per_scene_nmse_better=int(np.sum(nmse_delta<0)), per_scene_nmse_worse=int(np.sum(nmse_delta>0)))
            comparisons.append(comparison)
            if method==config['primary_candidate']:
                all_passed &= comparison['passed']
    for filename, values in [('per_scene.csv',rows),('summary.csv',summaries)]:
        with (out/filename).open('w',newline='',encoding='utf-8-sig') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(values[0]));writer.writeheader();writer.writerows(values)
    summary = dict(status='COMPLETE', count_predictions=len(rows), summaries=summaries, comparisons=comparisons,
        full_run_gate_passed=bool(all_passed), primary_candidate=config['primary_candidate'],
        intervals='10000 paired scene resamples; descriptive, not formal equivalence testing',
        full_experiment_launched=False)
    write_json(out/'SUMMARY.json',summary)
    write_json(out/'RESULT_AUDIT.json',dict(status='PASSED', predictions_rescored=len(rows),
        source_and_checkpoint_hashes_verified=True, plan_sha256=sha256(out/'PLAN.json'),
        truth_usage='Evaluation and labeled oracle only; candidate API receives Y/P/rho',
        limitations=['Moment variance is a proxy; not full Shen OTFS reproduction',
                    '20 scenes per condition; no population-level equivalence claim',
                    'Repeated receiver calls execute 110 layers per candidate, not 10']))
    lines=['# Shen 相位更新的 AFDM 候选验证','',
           '## Material Passport','',
           '- Mode: run + descriptive paired analysis',
           '- 来源：本地配对模拟；固定候选配置及 epoch 1 十层权重；未重新训练。',
           '- 已知相位一行仅为 oracle 诊断；所有方法估计噪声。',
           '- 20 个独立诊断场景 × 4 工况；与正式 2000 场景种子不重合。',
           '- 均值/方差替换与相位参数化为 AFDM 适配，不是完整复现 Shen 的 OTFS 接收机。','',
           '**全量启动条件：'+('通过。' if all_passed else '未通过，不启动候选全量主实验。')+'**','',
           '| Q | SNR(dB) | 方法 | NMSE(dB) | AER | 漏检率 | 虚警率 | 漏检/虚警 | 相位 MSE | 时间(s) |',
           '|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|']
    for r in summaries:
        lines.append(f"| {r['frames']} | {r['snr_db']} | {r['method']} | {r['nmse_db']:.3f} | {r['aer']:.2%} | {r['miss_rate']:.2%} | {r['false_alarm_rate']:.2%} | {r['misses']}/{r['false_alarms']} | {r['phase_mse']:.4f} | {r['seconds']:.3f} |")
    lines += ['', 'NMSE 是每场景全信道 NMSE(dB) 的平均。相位 MSE 为活动用户 q>0 的单位相位差平方均值；范围 0–4，零表示相位完全相同。',
              '候选从全 1 相位开始，外层更新 10 次，每次重新执行十层网络，合计 110 层。网络原始反馈方差仅用作明确标记的各向同性方差近似。',
              '', '## 配对差值（候选减物理前端）','']
    for row in comparisons:
        lines.append(f"- 工况 {row['condition']}，{row['method']}：差值 {json.dumps(row['delta_candidate_minus_reference'],ensure_ascii=False)}；描述性 95% 区间 {json.dumps(row['descriptive_paired_95_interval'],ensure_ascii=False)}；检查 {row['checks']}。")
    lines += ['', '全部场景、逐轮诊断和预测均保留。不得以真值挑选轮数、场景、门限或参数；原式投影不保证约束目标单调。',
              '公式来源：[Shen et al., §III-C, (48)–(53)](https://arxiv.org/html/2412.20806v1#S3.SS3)。',
              '详细边界与公式见 [实现说明](../../../paper/docs/SHEN_PHASE_IMPLEMENTATION_20261021.md)。']
    (out/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    report_names=['SUMMARY.json','RESULT_AUDIT.json','summary.csv','per_scene.csv','REPORT.md']
    write_json(out/'COMPLETE.json',dict(status='COMPLETE',finished_unix=time.time(),
        files={name:sha256(out/name) for name in report_names},plan_sha256=sha256(out/'PLAN.json')))
    write_json(out/'STATUS.json',dict(stage='COMPLETE',full_run_gate_passed=bool(all_passed),updated_unix=time.time()))
    print(json.dumps(dict(status='COMPLETE',full_run_gate_passed=bool(all_passed),predictions=len(rows))),flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--prepare',action='store_true');group.add_argument('--run',action='store_true')
    group.add_argument('--summarize',action='store_true')
    parser.add_argument('--output',type=Path,default=DEFAULT_OUT)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    plan=prepare(args.output)
    if args.run:run(args.output,plan)
    elif args.summarize:summarize(args.output,plan)
    else:print(json.dumps(dict(status='PREPARED',plan_sha256=sha256(args.output/'PLAN.json'))),flush=True)


if __name__=='__main__':
    main()
