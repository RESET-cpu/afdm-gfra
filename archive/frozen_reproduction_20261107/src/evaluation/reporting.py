"""Audited pooled metrics, paired scene bootstrap and standalone scientific plots."""
import csv
import json
from pathlib import Path
import numpy as np
from utils import read_json, write_json, sha256


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
            (t[...,2]-t[...,7])/t[...,4], (t[...,3]-t[...,8])/t[...,5]],axis=-1)
    observed = delta(data.sum(axis=0))
    result = dict(zip(['delta_nmse_db','delta_aer','delta_miss_rate','delta_false_alarm_rate'],observed.tolist()))
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
    low,high=np.quantile(np.concatenate(boot),[.025,.975],axis=0)
    for i,key in enumerate(['nmse_db','aer','miss_rate','false_alarm_rate']):
        result['delta_'+key+'_ci95']=[float(low[i]),float(high[i])]
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
                    miss_rate=totals['misses']/totals['active'],false_alarm_rate=totals['false_alarms']/totals['inactive'],
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
    plot(out,plan,rows,all_records)
    text=['# 实验结果','',f"状态：COMPLETE；用途：{plan['mode']}；每工况 {plan['scene_count']} 个物理场景。",'',
          '本次配置方法：'+ '、'.join(labels[m] for m in plan['methods'])+'。',
          '不在测试场景上选择模型或门限。','',
          '以下信道 NMSE 为误差能量与信号能量汇总后的比值；不同实验共用的场景不是独立重复实验。','']
    if 'proposed' in plan['methods']:
        text += ['十层固定使用验证集选择的 epoch 1、10 层权重。','']
    if denoise:
        text += ['去噪只评估预训练的一阶网络，不评估逐层网络、二阶网络或活动网络。genie 曲线显式使用真实几何、功率和 LOS 信息。','',
                 '|条件|方法|NMSE (dB)|','|---|---|---:|']
        text += [f"|{r['parameters']}|{r['method']}|{r['nmse_db']:.4f}|" for r in rows]
    else:
        phase_text = '已知相位（使用模拟真值）' if plan['phase_mode']=='known' else '从观测估计相位'
        noise_text = '已知噪声方差（使用模拟真值）' if plan['noise_mode']=='known' else '从观测估计噪声方差'
        text += [f'信息条件：{phase_text}；{noise_text}。','']
        if any(s.get('phase_input')=='raw' for s in plan['algorithm_specs'].values()):
            text += ['Proposed 的内部相位初始化和9次层间更新已计入接收机时间；基线的公共相位前端单独累加。时延比较图与端到端配对区间包含双方全部相位代价。','']
        if plan['noise_mode']=='known' and 'gamp' in plan['methods']:
            text += ['GAMP-SBL 使用给定噪声方差设置原有 Gamma 先验，保留原算法内部噪声更新；known 表示提供真值信息，不表示冻结全部内部更新。','']
        text += ['|条件|方法|NMSE (dB)|AER|漏检率|虚警率|漏检/虚警|接收机内计时秒|端到端秒|显存 MiB|',
                 '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
        for r in rows:
            text.append(f"|{r['parameters']}|{labels[r['method']]}|{r['nmse_db']:.4f}|{r['aer']:.3%}|{r['miss_rate']:.3%}|{r['false_alarm_rate']:.3%}|{r['misses']}/{r['false_alarms']}|{r['mean_receiver_seconds']:.4f}|{r['mean_end_to_end_seconds']:.4f}|{r['peak_allocated_mib']}|")
        text += ['','逐场景差值及 10000 次配对重抽样区间见 paired.csv 和 SUMMARY.json；单场景运行不计算区间。',
                 '实际计算后端逐方法列明；不能把 CPU/GPU 跨后端时延比值归因于算法本身。',
                 f"每个方法和输入形状使用独立场景预热一次；每个测试场景测量 {plan['timing_repeats']} 次取中位数，再按场景汇总均值、P50、P95；统计单位仍为物理场景。",
                 '显存测量前其他接收机已移至 CPU。参数量及显存与时延分别报告，不将运行更快直接写成参数更少。']
        if plan['experiment']=='density_ratio_ablation':
            text += ['密度比消融中，受控对比仅为 STMP 的 learned/Gaussian 两臂；十层为完整模型参考。']
    (out/'REPORT.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
    audit=dict(status='PASSED',method_condition_groups=len(rows),scene_method_results=len(per_scene),
               all_planned_results_present=True,compact_rescoring_passed=True,reference_sha256=references,
               proposed_sha256=plan['model_binding']['proposed']['checkpoint_sha256'],
               original_policy_sha256=plan['formal_panel_sha256'])
    write_json(out/'RESULT_AUDIT.json',audit)
    names=['SUMMARY.json','summary.csv','per_scene.csv','paired.csv','RESULT_AUDIT.json','REPORT.md','comparison.png','comparison.pdf']
    names += ['runtime_accuracy.png','runtime_accuracy.pdf']
    write_json(out/'COMPLETE.json',dict(status='COMPLETE',mode=plan['mode'],files={n:sha256(out/n) for n in names if (out/n).exists()}))
    write_json(out/'STATUS.json',dict(stage='COMPLETE',scene_method_results=len(per_scene)))
    print(json.dumps(dict(status='COMPLETE',experiment=plan['experiment'],results=len(per_scene))),flush=True)
    return 0


def plot(out,plan,rows,records):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    labels={name: spec['label'] for name,spec in plan['algorithm_specs'].items()}
    name=plan['experiment']; denoise=plan['experiment_kind']=='denoiser'
    fig,axes=plt.subplots(1,1 if denoise else 2,figsize=(11,5),layout='constrained',squeeze=False)
    for method in plan['methods']:
        group=[r for r in rows if r['method']==method]
        x=[r['parameters']['variance'] if denoise else r['condition'] for r in group]
        label=labels[method]
        axes[0,0].plot(x,[r['nmse_db'] for r in group],marker='o',label=label)
        if not denoise:axes[0,1].plot(x,[100*r['aer'] for r in group],marker='o',label=label)
    for ax in axes.flat:
        ax.grid(alpha=.25)
        ax.set_xlabel('Known complex AWGN variance' if denoise else 'Condition index (see report)')
    axes[0,0].set_ylabel('Channel NMSE (dB)')
    if denoise:axes[0,0].set_xscale('log')
    else:axes[0,1].set_ylabel('Activity error rate (%)')
    axes[0,-1].legend(fontsize=7,loc='upper left',bbox_to_anchor=(1,1))
    information = '' if denoise else f" | phase: {plan['phase_mode']} | noise: {plan['noise_mode']}"
    fig.suptitle(f"{name} | {plan['scene_count']} scenes/condition | {plan['mode']}"+information,fontsize=10)
    for ext in ('png','pdf'):fig.savefig(out/f'comparison.{ext}',dpi=160)
    plt.close(fig)
    if name!='runtime_comparison':return
    fig,axes=plt.subplots(1,2,figsize=(11,4.5),layout='constrained')
    for method in plan['methods']:
        group=[r for r in rows if r['method']==method]
        label=labels[method]+' / '+group[0]['backend']
        x=[r['mean_end_to_end_seconds'] for r in group]
        axes[0].plot(x,[r['nmse_db'] for r in group],marker='o',label=label)
        axes[1].plot(x,[100*r['aer'] for r in group],marker='o',label=label)
    for ax in axes:
        ax.set_xscale('log');ax.set_xlabel('Mean end-to-end time including phase (s)');ax.grid(alpha=.25)
    axes[0].set_ylabel('Channel NMSE (dB)');axes[1].set_ylabel('Activity error rate (%)')
    axes[1].legend(loc='upper left',bbox_to_anchor=(1,1),fontsize=7)
    fig.suptitle(f"Runtime and accuracy | {plan['mode']} | native backends labelled")
    for ext in ('png','pdf'):fig.savefig(out/f'runtime_accuracy.{ext}',dpi=160)
    plt.close(fig)
