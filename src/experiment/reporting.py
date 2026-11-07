"""Audited pooled metrics, paired scene bootstrap and standalone scientific plots."""
import csv
import json
from pathlib import Path
import numpy as np
from fileio import read_json
from fileio import write_json
from fileio import sha256


def rate(numerator, denominator):
    """An empty reference class has an undefined rate, not a zero error rate."""
    return numerator / denominator if denominator else None


def rate_array(numerator, denominator):
    numerator = np.asarray(numerator, dtype=float)
    return np.divide(numerator, denominator, out=np.full_like(numerator, np.nan),
                     where=np.asarray(denominator) != 0)


def percent(value):
    return 'N/A' if value is None else f'{value:.3%}'


def write_csv(path, rows):
    if not rows:
        return
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open('w', newline='', encoding='utf-8-sig') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)


def pair_intervals(a, b, plan):
    data = np.asarray([[r['metrics'][k] for k in ('full_error','signal_energy','misses','false_alarms','active','inactive')]
                       + [s['metrics'][k] for k in ('full_error','misses','false_alarms')]
                       for r,s in zip(a,b,strict=True)])
    def delta(t):
        return np.stack([10*np.log10(t[...,0]/t[...,6]),
            (t[...,2]+t[...,3]-t[...,7]-t[...,8])/(t[...,4]+t[...,5]),
            rate_array(t[...,2]-t[...,7], t[...,4]),
            rate_array(t[...,3]-t[...,8], t[...,5])],axis=-1)
    observed = delta(data.sum(axis=0))
    result = dict(zip(['delta_nmse_db','delta_aer','delta_miss_rate','delta_false_alarm_rate'],
                       [float(v) if np.isfinite(v) else None for v in observed]))
    differences=np.asarray([r['metrics']['nmse_db']-s['metrics']['nmse_db'] for r,s in zip(a,b,strict=True)])
    result.update(nmse_scene_better=int((differences < -1e-12).sum()), nmse_scene_worse=int((differences > 1e-12).sum()),
                  nmse_scene_difference_min=float(differences.min()),nmse_scene_difference_max=float(differences.max()))
    ta=np.asarray([r['receiver_seconds'] for r in a]);tb=np.asarray([r['receiver_seconds'] for r in b])
    ea=np.asarray([r['end_to_end_seconds'] for r in a]);eb=np.asarray([r['end_to_end_seconds'] for r in b])
    result.update(mean_receiver_seconds_difference=float((ta-tb).mean()),
                  mean_receiver_time_ratio=float(ta.mean()/tb.mean()),
                  mean_end_to_end_seconds_difference=float((ea-eb).mean()),
                  mean_end_to_end_time_ratio=float(ea.mean()/eb.mean()))
    if len(data)<2:
        return dict(result, interval='Omitted for one-scene smoke check')
    rng=np.random.default_rng(plan['bootstrap_seed'])
    boot=[];time_boot=[];end_time_boot=[]
    for start in range(0,plan['bootstrap_replicates'],100):
        selected=rng.integers(0,len(data),size=(min(100,plan['bootstrap_replicates']-start),len(data)))
        boot.append(delta(data[selected].sum(axis=1)))
        time_boot.append((ta[selected]-tb[selected]).mean(axis=1))
        end_time_boot.append((ea[selected]-eb[selected]).mean(axis=1))
    samples = np.concatenate(boot)
    low,high=np.quantile(samples,[.025,.975],axis=0)
    for i,key in enumerate(['nmse_db','aer','miss_rate','false_alarm_rate']):
        result['delta_'+key+'_ci95']=([float(low[i]),float(high[i])]
                                    if np.isfinite([low[i],high[i]]).all() else None)
        undefined = int(np.count_nonzero(~np.isfinite(samples[:,i])))
        if undefined:
            result['delta_'+key+'_undefined_resamples'] = undefined
    result['mean_receiver_seconds_difference_ci95']=np.quantile(np.concatenate(time_boot),[.025,.975]).tolist()
    result['mean_end_to_end_seconds_difference_ci95']=np.quantile(np.concatenate(end_time_boot),[.025,.975]).tolist()
    return result


def finish(out,plan):
    labels={name: spec['label'] for name,spec in plan['algorithm_specs'].items()}
    denoise=plan['experiment_kind']=='denoiser'
    rows, per_scene, paired, missing, all_records=[],[],[],[],{}
    references={}
    for index,condition in enumerate(plan['conditions']):
        for method in plan['methods']:
            records=[]
            for scene in range(plan['scene_count']):
                pointer=out/f'scene{scene:04d}'/f'condition{index:02d}'/(method+'.json')
                if not pointer.exists():
                    missing.append(str(pointer));continue
                ref=read_json(pointer); path=Path(ref['result'])
                if sha256(path)!=ref['sha256']:
                    raise ValueError('Result receipt changed: '+str(path))
                row=read_json(path)
                if row['status']!='COMPLETE' or sha256(path.with_suffix('.npz'))!=row['compact_sha256']:
                    raise ValueError('Incomplete or changed result: '+str(path))
                references[str(pointer)]=sha256(pointer)
                references[str(path)]=ref['sha256']
                references[str(path.with_suffix('.npz'))]=row['compact_sha256']
                with np.load(path.with_suffix('.npz'),allow_pickle=False) as arrays:
                    if denoise:
                        np.testing.assert_allclose([arrays['error'].sum(),arrays['energy'].sum()],
                                                   [row['error'],row['energy']],rtol=1e-12)
                    else:
                        truth=np.asarray(arrays['truth_activity'],bool)
                        decision=np.asarray(arrays['activity_decision'],bool)
                        metrics=row['metrics']
                        assert int(np.sum(truth & ~decision))==metrics['misses']
                        assert int(np.sum(~truth & decision))==metrics['false_alarms']
                        assert int(truth.sum())==metrics['active']
                        np.testing.assert_allclose(arrays['per_user_error'].sum(),metrics['full_error'],rtol=1e-12)
                records.append(row)
                scalar=row if denoise else row['metrics']
                per_scene.append(dict(scene=scene,seed=plan['base_seed']+scene,condition=index,method=method,
                    **{k:v for k,v in scalar.items() if isinstance(v,(int,float))}))
                if not denoise:
                    per_scene[-1].update(receiver_seconds=row['receiver_seconds'], phase_seconds=row['phase_seconds'],
                        end_to_end_seconds=row['end_to_end_seconds'], backend=row['backend'])
            summary=dict(condition=index,parameters=condition,method=method,planned=plan['scene_count'],completed=len(records))
            if len(records)!=plan['scene_count']:
                rows.append(summary);continue
            all_records[index,method]=records
            if denoise:
                error=sum(r['error'] for r in records);energy=sum(r['energy'] for r in records)
                summary.update(error=error,energy=energy,nmse_db=float(10*np.log10(error/energy)),
                               samples=sum(r['samples'] for r in records),error_kind=records[0]['error_kind'])
            else:
                totals={k:sum(r['metrics'][k] for r in records) for k in
                        ('full_error','signal_energy','misses','false_alarms','active','inactive')}
                summary.update(totals,nmse_db=float(10*np.log10(totals['full_error']/totals['signal_energy'])),
                    aer=(totals['misses']+totals['false_alarms'])/(totals['active']+totals['inactive']),
                    miss_rate=rate(totals['misses'],totals['active']),
                    false_alarm_rate=rate(totals['false_alarms'],totals['inactive']),
                    mean_receiver_seconds=float(np.mean([r['receiver_seconds'] for r in records])),
                    p50_receiver_seconds=float(np.median([r['receiver_seconds'] for r in records])),
                    p95_receiver_seconds=float(np.quantile([r['receiver_seconds'] for r in records],.95)),
                    mean_end_to_end_seconds=float(np.mean([r['end_to_end_seconds'] for r in records])),
                    p50_end_to_end_seconds=float(np.median([r['end_to_end_seconds'] for r in records])),
                    p95_end_to_end_seconds=float(np.quantile([r['end_to_end_seconds'] for r in records],.95)),
                    peak_allocated_mib=max(r['peak_allocated_mib'] for r in records) if plan['device']=='cuda' else None,
                    backend=records[0]['backend'], parameter_count=records[0]['parameter_count'],
                    mean_iterations=float(np.mean([r['iterations'] for r in records])))
            rows.append(summary)
        if not denoise:
            reference=plan['reference_method']
            comparisons=[(reference,m) for m in plan['methods'] if m!=reference]
            comparisons += [tuple(pair) for pair in plan['extra_comparisons'] if tuple(pair) not in comparisons]
            for first,second in comparisons:
                if (index,first) in all_records and (index,second) in all_records:
                    paired.append(dict(condition=index,first=first,second=second,
                        **pair_intervals(all_records[index,first],all_records[index,second],plan)))
    summary=dict(status='COMPLETE' if not missing else 'INCOMPLETE',mode=plan['mode'],experiment=plan['experiment'],
                 phase_mode=plan['phase_mode'],noise_mode=plan['noise_mode'],
                 rows=rows,missing=missing,paired_differences=paired,
                 statistics='Pooled counts and energies; pointwise descriptive 95% paired physical-scene percentile bootstrap (10000 resamples), same resample IDs across conditions.',
                 timing=plan['timing'],ablation_scope=plan['ablation_scope'],denoising_scope=plan['denoising_scope'])
    write_json(out/'SUMMARY.json',summary)
    write_csv(out/'summary.csv',rows);write_csv(out/'per_scene.csv',per_scene);write_csv(out/'paired.csv',paired)
    if missing:return 1
    from plotting.summary import plot
    plot(out,plan,rows,all_records)
    text=['# 实验结果','',f"状态：COMPLETE；用途：{plan['mode']}；每工况 {plan['scene_count']} 个物理场景。",'',
          '本次配置方法：'+ '、'.join(labels[m] for m in plan['methods'])+'。',
          '不在测试场景上选择模型或门限。','',
          '以下信道 NMSE 为误差能量与信号能量汇总后的比值；不同实验共用的场景不是独立重复实验。','']
    if denoise:
        text += ['去噪只评估预训练的一阶网络，不评估逐层网络、二阶网络或活动网络。genie 曲线显式使用真实几何、功率和 LOS 信息。','',
                 '|条件|方法|NMSE (dB)|','|---|---|---:|']
        text += [f"|{r['parameters']}|{r['method']}|{r['nmse_db']:.4f}|" for r in rows]
    else:
        phase_text = '已知相位（使用模拟真值）' if plan['phase_mode']=='known' else '从观测估计相位'
        noise_text = '已知噪声方差（使用模拟真值）' if plan['noise_mode']=='known' else '从观测估计噪声方差'
        text += [f'信息条件：{phase_text}；{noise_text}。','']
        if any(s.get('phase_input')=='raw' for s in plan['algorithm_specs'].values()):
            text += ['接收机内部相位处理计入接收机时间，外部相位前端单独累加；端到端时延包含各方法实际使用的全部相位处理。','']
        if plan['noise_mode']=='known' and 'gamp' in plan['methods']:
            text += ['GAMP-SBL 使用给定噪声方差设置原有 Gamma 先验，保留原算法内部噪声更新；known 表示提供真值信息，不表示冻结全部内部更新。','']
        text += ['|条件|方法|NMSE (dB)|AER|漏检率|虚警率|漏检/虚警|接收机内计时秒|端到端秒|显存 MiB|',
                 '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
        for r in rows:
            text.append(f"|{r['parameters']}|{labels[r['method']]}|{r['nmse_db']:.4f}|{r['aer']:.3%}|{percent(r['miss_rate'])}|{percent(r['false_alarm_rate'])}|{r['misses']}/{r['false_alarms']}|{r['mean_receiver_seconds']:.4f}|{r['mean_end_to_end_seconds']:.4f}|{r['peak_allocated_mib']}|")
        text += ['', '无对应活跃/非活跃样本时，漏检率/虚警率记为 N/A（JSON 为 null）。含未定义重抽样值的相应区间不报告，未删除场景或重抽样。']
        text += ['','逐场景差值及 10000 次配对重抽样区间见 paired.csv 和 SUMMARY.json；单场景运行不计算区间。',
                 '实际计算后端逐方法列明；不能把 CPU/GPU 跨后端时延比值归因于算法本身。',
                 f"每个方法和输入形状使用独立场景预热一次；每个测试场景测量 {plan['timing_repeats']} 次取中位数，再按场景汇总均值、P50、P95；统计单位仍为物理场景。",
                 '显存测量前其他接收机已移至 CPU。参数量及显存与时延分别报告，不将运行更快直接写成参数更少。']
        if plan['experiment']=='density_ratio_ablation':
            text += ['密度比消融比较 STMP 的 learned/Gaussian 两种活动证据。']
    (out/'REPORT.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
    audit=dict(status='PASSED',method_condition_groups=len(rows),scene_method_results=len(per_scene),
               all_planned_results_present=True,compact_rescoring_passed=True,reference_sha256=references,
               model_assets_sha256={p: h for p, h in plan['assets'].items()
                                    if Path(p).suffix in ('.pt', '.pth', '.npz')},
               original_policy_sha256=plan['formal_panel_sha256'])
    write_json(out/'RESULT_AUDIT.json',audit)
    names=['SUMMARY.json','summary.csv','per_scene.csv','paired.csv','RESULT_AUDIT.json','REPORT.md','comparison.png','comparison.pdf']
    names += ['runtime_accuracy.png','runtime_accuracy.pdf']
    write_json(out/'COMPLETE.json',dict(status='COMPLETE',mode=plan['mode'],files={n:sha256(out/n) for n in names if (out/n).exists()}))
    write_json(out/'STATUS.json',dict(stage='COMPLETE',scene_method_results=len(per_scene)))
    print(json.dumps(dict(status='COMPLETE',experiment=plan['experiment'],results=len(per_scene))),flush=True)
    return 0


