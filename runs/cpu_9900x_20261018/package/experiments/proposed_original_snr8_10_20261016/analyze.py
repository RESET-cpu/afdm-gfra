"""Prespecified offline scoring: ten reused physical scenes, eight paired SNR values.

No receiver is called here. Full saved estimates are scored without masking.
The one scene bootstrap draw is shared across all SNRs and method comparisons.
"""
from collections import Counter
from pathlib import Path
import csv
import hashlib
import importlib.util
import json

import numpy as np


SNRS = (-4, -2, 0, 2, 4, 6, 8, 10)
SCENES = tuple(range(10))
METHODS = ['proposed', 'somp', 'gamp', 'gnn', 'offgrid_sbl']
ALL_METHODS = METHODS
LABELS = dict(proposed='Proposed', somp='SOMP', gamp='GAMP-SBL MMV',
              gnn='GNN-ASPL', offgrid_sbl='Off-grid SBL')
BOOTSTRAP = dict(seed=202610168199999, repetitions=20000, unit='physical_scene')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def db(numerator, denominator):
    """A zero error has ratio zero and dB=-infinity, encoded as null in JSON."""
    require(denominator > 0 and numerator >= 0, 'Invalid NMSE energies')
    return float(10 * np.log10(numerator / denominator)) if numerator else None


def score(arrays, truth):
    """Independent direct energy/count formulas; never threshold the estimate."""
    h = np.asarray(truth['channel'])
    estimate = np.asarray(arrays['estimate'])
    active = np.asarray(truth['activity'], bool)
    decision = np.asarray(arrays['activity_decision'])
    require(h.shape == estimate.shape and h.shape[0] == 40, 'Channel shape mismatch')
    require(active.shape == decision.shape == (40,), 'Activity shape mismatch')
    require(np.isin(decision, [0, 1]).all(), 'Nonbinary saved activity decision')
    require(np.isfinite(h).all() and np.isfinite(estimate).all(), 'Nonfinite channel')
    decision = decision.astype(bool)
    require(np.count_nonzero(h[~active]) == 0, 'Inactive truth channel is not zero')
    with np.errstate(over='raise', invalid='raise'):
        delta = estimate - h
        axes = tuple(range(1, h.ndim))
        error = np.sum(delta.real**2 + delta.imag**2, axis=axes, dtype=np.float64)
        energy = np.sum(h.real**2 + h.imag**2, axis=axes, dtype=np.float64)
    total, signal = float(error.sum()), float(energy.sum())
    require(np.isfinite(total) and np.isfinite(signal) and signal > 0, 'Invalid energy')
    md = np.flatnonzero(active & ~decision).tolist()
    fa = np.flatnonzero(~active & decision).tolist()
    ae, ie = float(error[active].sum()), float(error[~active].sum())
    return dict(active=int(active.sum()), inactive=int((~active).sum()), users=40,
                misses=len(md), false_alarms=len(fa), full_error=total,
                signal_energy=signal, active_error=ae, inactive_error=ie,
                nmse_ratio=total/signal, nmse_db=db(total, signal),
                active_nmse_db=db(ae, signal), exact_zero_full_error=total == 0,
                aer=(len(md)+len(fa))/40, mdr=len(md)/int(active.sum()),
                far=len(fa)/int((~active).sum()),
                active_users=np.flatnonzero(active).tolist(), missed_users=md,
                false_alarm_users=fa, per_user_error=error.tolist(),
                decisions=decision.tolist())


def aggregate(rows):
    complete = [r for r in rows if r['status'] == 'COMPLETE']
    out = dict(planned=len(rows), completed=len(complete),
               status='COMPLETE' if len(complete) == len(rows) == 10 else 'INCOMPLETE',
               failed_cases=[r['key'] for r in rows if r['status'] != 'COMPLETE'])
    if out['status'] != 'COMPLETE':
        return out
    for key in ['active', 'inactive', 'users', 'misses', 'false_alarms',
                'full_error', 'signal_energy', 'active_error', 'inactive_error', 'warning_count']:
        out[key] = sum(r[key] for r in rows)
    out.update(nmse_ratio=out['full_error']/out['signal_energy'],
               nmse_db=db(out['full_error'], out['signal_energy']),
               active_nmse_db=db(out['active_error'], out['signal_energy']),
               exact_zero_full_error=out['full_error'] == 0,
               aer=(out['misses']+out['false_alarms'])/out['users'],
               mdr=out['misses']/out['active'], far=out['false_alarms']/out['inactive'],
               stopping_reasons=dict(Counter(str(r['stopping_reason']) for r in rows)),
               converged_true=sum(r['converged'] is True for r in rows),
               converged_false=sum(r['converged'] is False for r in rows),
               convergence_flag_not_reported=sum(r['converged'] is None for r in rows),
               max_iterations_stops=sum(str(r['stopping_reason']).upper() == 'MAX_ITERATIONS' for r in rows),
               outside_noise_support_calls=sum(r.get('outside_noise_support_calls') or 0 for r in rows),
               proposed_unsupported_user_queries=sum(r.get('proposed_unsupported_user_queries') or 0 for r in rows),
               seconds_median=float(np.median([r['seconds'] for r in rows])))
    return out


def paired(a, b, indices):
    """Proposed minus comparator, pooling energies/counts inside each resample."""
    require([r['scene'] for r in a] == [r['scene'] for r in b] == list(SCENES), 'Unpaired scenes')
    if any(r['status'] != 'COMPLETE' for r in a+b):
        return dict(status='INCOMPLETE', planned=10,
                    incomplete_scenes=[x['scene'] for x, y in zip(a, b)
                                       if x['status'] != 'COMPLETE' or y['status'] != 'COMPLETE'])
    for x, y in zip(a, b):
        require(all(x[k] == y[k] for k in ('seed', 'snr_db', 'input_sha256',
                                          'truth_sha256', 'signal_energy', 'active', 'inactive')),
                'Pair identity mismatch')
    ea, eb = [np.array([r['full_error'] for r in rr]) for rr in (a, b)]
    md = np.array([x['misses']-y['misses'] for x, y in zip(a, b)])
    fa = np.array([x['false_alarms']-y['false_alarms'] for x, y in zip(a, b)])
    active = np.array([r['active'] for r in a])
    inactive = np.array([r['inactive'] for r in a])
    counts = dict(aer=(md+fa, active+inactive), mdr=(md, active), far=(fa, inactive))
    out = dict(status='COMPLETE', physical_scenes=10,
               nmse_difference_db=db(float(ea.sum()), float(eb.sum())) if eb.sum() > 0 else None,
               misses_difference=int(md.sum()), false_alarms_difference=int(fa.sum()),
               lower_nmse_scenes=int(np.sum(ea < eb)), equal_nmse_scenes=int(np.sum(ea == eb)),
               higher_nmse_scenes=int(np.sum(ea > eb)),
               fewer_detection_error_scenes=int(np.sum(md+fa < 0)),
               equal_detection_error_scenes=int(np.sum(md+fa == 0)),
               more_detection_error_scenes=int(np.sum(md+fa > 0)))
    sa, sb = ea[indices].sum(1), eb[indices].sum(1)
    if np.all(sa > 0) and np.all(sb > 0):
        out['nmse_difference_percentile95_db'] = np.quantile(10*np.log10(sa/sb), [.025, .975]).tolist()
    else:
        out['nmse_difference_percentile95_db'] = None
        out['nmse_interval_note'] = 'At least one exact-zero error sum; no finite dB interval reported'
    for name, (numerator, denominator) in counts.items():
        out[name+'_difference'] = float(numerator.sum()/denominator.sum())
        draws = numerator[indices].sum(1)/denominator[indices].sum(1)
        out[name+'_difference_percentile95'] = np.quantile(draws, [.025, .975]).tolist()
    return out


def validate_plan(lock):
    require(lock['descriptive_bootstrap'] == BOOTSTRAP, 'Bootstrap differs from prespecification')
    require(list(lock['methods']) == METHODS and lock['scenes'] == 10, 'Method/scene plan mismatch')
    require(lock['expected_receiver_runs'] == 400 and lock['expected_plain_outputs'] == 0,
            'Inference counts differ from plan')
    require(not lock['retraining'] and not lock['recalibration'], 'Training or recalibration not allowed')
    cases = lock['cases']
    require(len(cases) == 80, 'Exactly eighty planned inputs required')
    pairs = {(c['scene'], c['snr_db']) for c in cases}
    require(pairs == {(s, v) for s in SCENES for v in SNRS}, 'Missing/duplicate scene-SNR condition')
    for c in cases:
        require(c['branch'] == 'original' and c['panel'] == 'paired10_snr8', 'Wrong panel or pilot')
        require(c['key'] == f"paired10_snr8/scene{c['scene']:03d}/snr{c['snr_db']:+03d}", 'Wrong case key')
    for s in SCENES:
        group = [c for c in cases if c['scene'] == s]
        require(len({c['seed'] for c in group}) == len({c['truth'] for c in group}) == 1,
                'Eight SNR conditions must share one physical scene/truth')
    require(len({c['seed'] for c in cases}) == 10, 'Scene seeds are not unique')


def verify_analysis_freeze(rt):
    """The scoring source must be frozen against this exact input manifest."""
    path = rt.OUT/'ANALYSIS_FREEZE.json'
    frozen = rt.load(path)
    require(frozen['freeze_sha256'] == rt.sha(rt.OUT/'FREEZE.json'),
            'Analysis freeze refers to a different input FREEZE.json')
    source = rt.relative(Path(__file__).resolve())
    require(frozen['sources'].get(source) == rt.sha(Path(__file__)),
            'Current analyze.py differs from the prespecified analysis source')
    return dict(path=rt.relative(path), sha256=rt.sha(path),
                input_freeze_sha256=frozen['freeze_sha256'], analysis_source=source)


def collect(rt, lock):
    audit = dict(status='PASS', analysis_sha256=rt.sha(Path(__file__)),
                 freeze_sha256=rt.sha(rt.OUT/'FREEZE.json'), hash_mismatches=[],
                 output_errors=[], outputs={}, documentation_changes={},
                 activity_mask_applied=False,
                 proposed_probability_weighted_mean_max_relative_error=0.)
    for section in ('sources', 'inputs'):
        require(section in lock and bool(lock[section]), 'Missing frozen '+section)
        for path, expected in lock[section].items():
            p = rt.ROOT/path
            actual = rt.sha(p) if p.is_file() else None
            if actual != expected:
                audit['hash_mismatches'].append(dict(section=section, path=path, expected=expected, actual=actual))
    for path, expected in lock.get('documentation', {}).items():
        p = rt.ROOT/path
        actual = rt.sha(p) if p.is_file() else None
        if actual != expected:
            audit['documentation_changes'][path] = dict(before=expected, after=actual)
    audit['progress_complete'] = {m: (rt.OUT/'progress'/f'{m}_complete.json').is_file() for m in METHODS}
    audit['frozen_sources_checked'] = len(lock['sources'])
    audit['frozen_inputs_checked'] = len(lock['inputs'])
    rows = []
    for case in sorted(lock['cases'], key=lambda c: (c['snr_db'], c['scene'])):
        truth_path = rt.ROOT/case['truth']
        truth_hash = rt.sha(truth_path) if truth_path.is_file() else None
        for method in ALL_METHODS:
            native = method
            folder = rt.OUT/'runs'/case['key']/native
            prefix = ''
            pred_path, rec_path = folder/(prefix+'prediction.npz'), folder/(prefix+'receiver.json')
            common = dict(panel=case['panel'], key=case['key'], scene=case['scene'], seed=case['seed'],
                          snr_db=case['snr_db'], branch=case['branch'], method=method,
                          input_sha256=case['input_sha256'], truth_sha256=truth_hash,
                          actual_receive_snr_db=case['metadata']['actual_receive_snr_db'])
            row = dict(**common, status='MISSING', warning_count=None)
            for p in [folder/'RUN.json', folder/'warnings.json', pred_path, rec_path]:
                if p.is_file(): audit['outputs'][rt.relative(p)] = rt.sha(p)
            try:
                if (folder/'warnings.json').is_file():
                    ww = rt.load(folder/'warnings.json')
                    row['warning_count'] = sum(w.get('count', 1) for w in ww)
                    row['warning_categories'] = {}
                    for w in ww:
                        name = w.get('category', 'not_reported')
                        row['warning_categories'][name] = row['warning_categories'].get(name, 0)+w.get('count', 1)
                if not (folder/'RUN.json').is_file():
                    row['error'] = 'Planned RUN.json absent'
                    rows.append(row)
                    continue
                attempt = rt.load(folder/'RUN.json')
                row['native_status'] = attempt['status']
                row['run_seconds'] = attempt.get('seconds')
                require(attempt['method'] == native and attempt['case'] == case['key'], 'Attempt identity mismatch')
                if attempt['status'] != 'COMPLETE':
                    row.update(status='INCOMPLETE', error=attempt.get('error', 'Native inference not complete'),
                               stopping_reason=attempt.get('stopping_reason'), iterations=attempt.get('iterations'))
                    rows.append(row)
                    continue
                require(not audit['hash_mismatches'], 'Frozen source/input hash mismatch; scoring invalid')
                require(lock['inputs'].get(case['input']) == case['input_sha256'], 'Case input digest differs from frozen inputs')
                require(all(p in lock['inputs'] for p in (case['truth'], case['phase'], case['phase_record'])),
                        'Case truth/phase files absent from frozen inputs')
                require(row['warning_count'] is not None, 'Missing warnings record')
                arrays, record, truth = rt.read(pred_path), rt.load(rec_path), rt.read(truth_path)
                require(all(np.isfinite(a).all() for a in arrays.values()), 'Nonfinite saved output')
                require(record['input_sha256'] == case['input_sha256'], 'Receiver input hash mismatch')
                require(record['output_sha256'] == rt.sha(pred_path), 'Prediction hash mismatch')
                require(record['shared_phase_sha256'] == rt.sha(rt.ROOT/case['phase']), 'Phase mismatch')
                require(record['benchmark_inference_truth_loaded'] is False, 'Truth loaded by inference')
                require(record['supplied_noise_mode'] == 'known', 'Physical noise information changed')
                if method == 'proposed':
                    cfg = record['configuration'].copy()
                    require(cfg.pop('device') in ('cpu', 'mps'), 'Unexpected device')
                    require(cfg.pop('activity_prior') == case['metadata']['activity_prior'], 'Prior changed')
                    wanted = rt.load(rt.ROOT/rt.CONFIGS['proposed'])
                    require(cfg == wanted and cfg['decision_threshold'] == .5, 'Proposed configuration changed')
                    p = np.asarray(arrays['probabilities'])
                    require(p.shape == (40,) and np.all((p >= 0) & (p <= 1)), 'Invalid probabilities')
                    np.testing.assert_array_equal(arrays['activity_decision'], p >= .5)
                    weighted = p[:, None, None, None]*arrays['conditional_matrix']
                    difference = float(np.linalg.norm(arrays['estimate']-weighted)/max(np.linalg.norm(weighted), 1e-30))
                    require(difference < 1e-12, 'Estimate is not saved full probability-weighted mean')
                    audit['proposed_probability_weighted_mean_max_relative_error'] = max(
                        audit['proposed_probability_weighted_mean_max_relative_error'], difference)
                else:
                    signature = lock['inference_signatures'][method]
                    require(record['inference_sha256'] == signature, 'Inference signature changed')
                metrics = score(arrays, truth)
                row.update(status='COMPLETE', **metrics, seconds=record['seconds'],
                           phase_seconds=rt.load(rt.ROOT/case['phase_record'])['seconds'],
                           iterations=record.get('iterations'), converged=record.get('converged'),
                           stopping_reason=record.get('stopping_reason'),
                           outside_noise_support_calls=record.get('outside_noise_support_calls'),
                           proposed_unsupported_user_queries=record.get('unsupported_user_queries'),
                           prediction=rt.relative(pred_path), receiver=rt.relative(rec_path))
            except Exception as exc:
                row.update(status='AUDIT_FAILED', error=repr(exc))
                audit['output_errors'].append(dict(key=case['key'], method=method, error=repr(exc)))
            rows.append(row)
    require(len(rows) == 400, 'Every planned output must have a row')
    audit['finite_complete_outputs'] = sum(r['status'] == 'COMPLETE' for r in rows)
    if (audit['hash_mismatches'] or audit['output_errors'] or
            audit['finite_complete_outputs'] != 400 or not all(audit['progress_complete'].values())):
        audit['status'] = 'INCOMPLETE'
    return rows, audit


def scene_pairs(selected):
    rows = []
    for snr in SNRS:
        for method in ALL_METHODS[1:]:
            for a, b in zip(selected[snr]['proposed'], selected[snr][method]):
                row = dict(scene=a['scene'], seed=a['seed'], snr_db=snr, comparator=method,
                           status='COMPLETE' if a['status'] == b['status'] == 'COMPLETE' else 'INCOMPLETE',
                           proposed_status=a['status'], comparator_status=b['status'])
                if row['status'] == 'COMPLETE':
                    row.update(proposed_full_error=a['full_error'], comparator_full_error=b['full_error'],
                               signal_energy=a['signal_energy'], active=a['active'], inactive=a['inactive'],
                               nmse_difference_db=db(a['full_error'], b['full_error']) if b['full_error'] else None,
                               misses_difference=a['misses']-b['misses'],
                               false_alarms_difference=a['false_alarms']-b['false_alarms'])
                    row.update(aer_difference=(row['misses_difference']+row['false_alarms_difference'])/40,
                               mdr_difference=row['misses_difference']/a['active'],
                               far_difference=row['false_alarms_difference']/a['inactive'])
                rows.append(row)
    return rows


def write_csv(path, rows, leading):
    fields = leading + sorted(set().union(*(r.keys() for r in rows))-set(leading))
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v
                             for k, v in row.items()})


def figure(rt, summary):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 2, figsize=(11, 8), sharex=True)
    colors = ['#007F86', '#D18B18', '#7B5EA7', '#C84C42', '#4A7A36', '#3F6BA7', '#777777']
    for method, color in zip(ALL_METHODS, colors):
        for ax, metric, title in zip(axes.flat, ('nmse_db', 'aer', 'mdr', 'far'),
                                    ('Full-channel NMSE (dB)', 'Activity error rate', 'Missed-detection rate', 'False-alarm rate')):
            values = [summary['aggregates'][str(s)][method].get(metric) for s in SNRS]
            values = [np.nan if value is None else value for value in values]
            ax.plot(SNRS, values, marker='o', markersize=4, color=color,
                    linestyle='-', label=LABELS[method])
            ax.set_ylabel(title)
            ax.set_xticks(SNRS)
            ax.grid(alpha=.2)
            if metric != 'nmse_db': ax.set_ylim(bottom=0)
    for ax in axes[-1]: ax.set_xlabel('Prespecified received SNR (dB)')
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', ncol=4, fontsize=9, frameon=False)
    title = '10 reused physical scenes | Original pilots | Estimated phase | Known thermal variance'
    if summary['status'] != 'COMPLETE': title += '\nINCOMPLETE: missing or invalid groups are not scored'
    fig.suptitle(title, fontsize=11)
    fig.tight_layout(rect=(0, .09, 1, .94))
    fig.savefig(rt.OUT/'comparison.png', dpi=200)
    fig.savefig(rt.OUT/'comparison.pdf')
    plt.close(fig)


def report(rt, summary):
    lines = ['# 原导频十场景：−4 至 10 dB 五方法比较', '',
             'Material Passport：Experiment Result + Validation；run + validate。输入与推断设置见 FREEZE.json，分析代码事前身份见 ANALYSIS_FREEZE.json，输出审查见 OUTPUT_AUDIT.json。', '',
             f"分析状态：**{summary['status']}**。计划 400 次推断，完成且通过输出审查 {summary['receiver_completed']} 次；其余 {summary['receiver_incomplete']} 次。", '',
             '每个 SNR 复用相同 10 个物理场景，八个 SNR 共 80 个条件。此前已观察过这些场景的部分结果，本次不是新的独立确认集。',
             '沿用活动概率 0.1 的非空条件生成分布，公开边际先验约 0.1015002635。热噪声方差以原导频下无噪接收功率标定，使 10log10(mean(|Y_clean|²)/sigma²) 等于预定 SNR；同一条件的全部方法使用相同观测、估计相位和给定热噪声方差。',
             'Proposed 为原三网络、原迭代和原门限；四个 baseline 沿用冻结的已知噪声配置。本轮未运行 L-DAMP。', '',
             '| SNR / dB | 方法 | 完整 NMSE / dB | MD | FA | AER | MDR | FAR |',
             '|---:|---|---:|---:|---:|---:|---:|---:|']
    for snr in SNRS:
        for method in ALL_METHODS:
            g = summary['aggregates'][str(snr)][method]
            if g['status'] != 'COMPLETE':
                lines.append(f'| {snr} | {LABELS[method]} | INCOMPLETE | | | | | |')
            else:
                value = '-∞ (exact zero)' if g['nmse_db'] is None else f"{g['nmse_db']:.3f}"
                lines.append(f"| {snr} | {LABELS[method]} | {value} | {g['misses']} | {g['false_alarms']} | {g['aer']:.5f} | {g['mdr']:.5f} | {g['far']:.5f} |")
    lines += ['', f'![SNR comparison]({rt.OUT}/comparison.png)', '',
              '完整 NMSE = 全部用户/场景误差能量之和 ÷ 真信道能量之和，再转 dB；不按检测决定清零，不平均逐场景 dB。活跃与非活跃误差另存于 SUMMARY，完整信道优势不能直接解释成活跃信道重建优势。', '',
              '配对结果在 PAIRED.json/csv。每次抽样保留整个物理场景，同一 20000×10 索引矩阵用于全部 SNR 和比较；MDR/FAR 每次重新汇总活跃/非活跃分母。95% 百分位区间是描述性的，未作多重比较修正，不是同时置信带或非劣检验。', '',
              '仅 10 个独立场景；零观测错误不代表真实错误概率为零，零宽 bootstrap 区间也不证明总体零风险。未收敛、MAX_ITERATIONS、支撑范围外调用和告警均保留，COMPLETE 不代表迭代稳定。缺失/失败组不报告成功子集分数。', '',
              '停止原因、收敛标记及告警见 SUMMARY.execution；逐例指标、用户身份及输出哈希见 ROWS 与 OUTPUT_AUDIT。推断耗时仅描述，不作并行执行下的速度排名。', '',
              '统计解释核查覆盖 11 类：跨 SNR 不合并制造总体结论；以场景而非用户为重采样单位；明示生成分布；不按输出筛样；报告活动基率与条件分母；种子事先固定；保留失败；全部方法与 SNR 一并报告；分析预先冻结；描述配对差异而不声称唯一机制；不按结果反向修改输入。', '']
    (rt.OUT/'REPORT.md').write_text('\n'.join(lines), encoding='utf-8')


def main():
    spec = importlib.util.spec_from_file_location('snr8_frozen_runner', Path(__file__).with_name('run.py'))
    rt = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rt)
    require(rt.METHODS == METHODS, 'Runtime method order changed')
    analysis_freeze = verify_analysis_freeze(rt)
    lock = rt.load(rt.OUT/'FREEZE.json')
    validate_plan(lock)
    rows, audit = collect(rt, lock)
    audit['analysis_freeze'] = analysis_freeze
    selected = {s: {m: sorted([r for r in rows if r['snr_db'] == s and r['method'] == m],
                              key=lambda r: r['scene']) for m in ALL_METHODS} for s in SNRS}
    groups = {str(s): {m: aggregate(selected[s][m]) for m in ALL_METHODS} for s in SNRS}
    indices = np.random.default_rng(BOOTSTRAP['seed']).integers(0, 10, size=(BOOTSTRAP['repetitions'], 10))
    comparisons = []
    for s in SNRS:
        for m in ALL_METHODS[1:]:
            comparisons.append(dict(snr_db=s, comparator=m, direction='proposed_minus_comparator',
                                    **paired(selected[s]['proposed'], selected[s][m], indices)))
    pair_rows = scene_pairs(selected)
    bootstrap = dict(**BOOTSTRAP, draws_shape=list(indices.shape),
                     draw_indices_sha256=hashlib.sha256(indices.astype('<i8').tobytes()).hexdigest(),
                     shared_across_all_snr_and_comparisons=True,
                     intervals='descriptive pointwise percentile 95%; no multiplicity adjustment',
                     independent_physical_scenes=10, conditioned_inputs=80)
    native = rows
    execution = {}
    for method in ALL_METHODS:
        rr = [r for r in rows if r['method'] == method]
        done = [r for r in rr if r['status'] == 'COMPLETE']
        execution[method] = dict(status_counts=dict(Counter(r['status'] for r in rr)),
            stopping_reasons=dict(Counter(str(r.get('stopping_reason')) for r in done)),
            converged_true=sum(r.get('converged') is True for r in done),
            converged_false=sum(r.get('converged') is False for r in done),
            convergence_flag_not_reported=sum(r.get('converged') is None for r in done),
            warning_count=sum(r.get('warning_count') or 0 for r in rr),
            missing_warning_records=sum(r.get('warning_count') is None for r in rr),
            outside_noise_support_calls=sum(r.get('outside_noise_support_calls') or 0 for r in done),
            proposed_unsupported_user_queries=sum(r.get('proposed_unsupported_user_queries') or 0 for r in done),
            max_iterations_stops=sum(str(r.get('stopping_reason')).upper() == 'MAX_ITERATIONS' for r in done))
    summary = dict(status='COMPLETE' if audit['status'] == 'PASS' else 'INCOMPLETE',
                   physical_scenes=10, conditions=80, snr_db=list(SNRS), planned_receiver_runs=400,
                   receiver_completed=sum(r['status'] == 'COMPLETE' for r in native),
                   receiver_incomplete=sum(r['status'] != 'COMPLETE' for r in native),
                   evaluation_rows=len(rows), same_inference_plain_outputs=0,
                   phase_mode="estimated", noise_mode="known", pilot="original PartialDFTPilot", reused_scenes=True,
                   aggregates=groups, comparisons=comparisons, descriptive_bootstrap=bootstrap,
                   execution=execution, analysis_sha256=audit['analysis_sha256'],
                   exact_zero_error_db_encoding='null means -infinity, not a finite dB value')
    rt.save(rt.OUT/'OUTPUT_AUDIT.json', audit)
    rt.save(rt.OUT/'ROWS.json', rows)
    rt.save(rt.OUT/'SUMMARY.json', summary)
    rt.save(rt.OUT/'PAIRED.json', dict(status=summary['status'], bootstrap=bootstrap,
                                    comparisons=comparisons, scene_pairs=pair_rows))
    write_csv(rt.OUT/'ROWS.csv', rows, ['scene', 'seed', 'snr_db', 'method', 'status'])
    write_csv(rt.OUT/'PAIRED.csv', pair_rows, ['scene', 'seed', 'snr_db', 'comparator', 'status'])
    figure(rt, summary)
    report(rt, summary)
    print(json.dumps({k: summary[k] for k in ('status', 'physical_scenes', 'conditions',
                                             'receiver_completed', 'receiver_incomplete', 'evaluation_rows')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
