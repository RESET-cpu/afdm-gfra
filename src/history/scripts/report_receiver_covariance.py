"""Report receiver-only covariance accuracy and its limits by stage."""
from pathlib import Path
import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import validate_receiver_covariance as development
import confirm_receiver_covariance as confirmation

P=development.P;ROOT=development.ROOT


def aggregate(rows):
    results=[]
    for stage in ('first','later'):
        stage_rows=[r for r in rows if (r['iteration']==1)==(stage=='first')]
        methods=sorted({x['method'] for r in stage_rows for x in r['results']})
        for method in methods:
            for group in ('all','active','inactive'):
                values=[x['groups'][group] for r in stage_rows for x in r['results'] if x['method']==method and group in x['groups']]
                if not values:continue
                metrics={}
                for key in ('shape_relative_error','trace_ratio','full_relative_error','top3_error_energy_recovery'):
                    data=[x[key] for x in values]
                    metrics[key]=dict(min=float(min(data)),median=float(np.median(data)),max=float(max(data)))
                strong=[x['top3_error_energy_recovery'] for x in values if x['strong_correlation']]
                if method=='nominal_isotropic':
                    # A scalar identity covariance has no identified principal directions.
                    metrics['top3_error_energy_recovery']=None
                    strong=[]
                results.append(dict(stage=stage,method=method,group=group,cases=len(values),
                    practical_screen_passes=sum(x['practical_screen_pass'] for x in values),
                    strong_correlation_cases=len(strong),strong_correlation_energy_recovery_min=float(min(strong)) if strong else None,
                    metrics=metrics))
    return results


def main():
    output=ROOT/'results/receiver_covariance_20261019';output.mkdir(exist_ok=True)
    old=P.read(development.OUT/'RESULTS.json');old_summary=aggregate(old)
    fresh_path=confirmation.OUT/'RESULTS.json'
    if not fresh_path.exists():
        P.save(output/'REPORT.json',dict(status='CONFIRMATION_RUNNING',development=old_summary,training_started=False))
        print('Confirmation still running',flush=True);return
    fresh=P.read(fresh_path);assert len(fresh)==32
    summaries=aggregate(fresh)
    protocol=P.read(confirmation.OUT/'PROTOCOL.json')
    for path,digest in protocol['source_and_weight_sha256'].items():assert P.sha(ROOT/path)==digest,path
    gates={}
    for method in protocol['primary_estimators']:
        subsets=[x for x in summaries if x['method']==method and x['group']=='all']
        gates[method]={x['stage']:dict(passed=x['practical_screen_passes']>=protocol['practical_screen'][f'{x["stage"]}_query_minimum_passes'] if x['stage']=='first' else x['practical_screen_passes']>=protocol['practical_screen']['later_minimum_passes'],
            passed_cases=x['practical_screen_passes'],cases=x['cases']) for x in subsets}
    split_summary=[]
    for method in protocol['primary_estimators']:
        for stage in ('first','later'):
            values=[z for r in fresh if (r['iteration']==1)==(stage=='first') for x in r['results'] if x['method']==method for z in x['split_checks']]
            split_summary.append(dict(method=method,stage=stage,comparisons=len(values),
                passed=sum(x['practical_screen_pass'] for x in values),
                shape_max=max(x['shape_relative_error'] for x in values),
                trace_range=[min(x['trace_ratio'] for x in values),max(x['trace_ratio'] for x in values)]))
    preservation=P.read(ROOT/'runs/stability_repair_20261019/PRESERVATION.json')
    for path,digest in preservation.items():assert P.sha(ROOT/path)==digest,path
    report=dict(status='COMPLETE',created_unix=time.time(),development=old_summary,confirmation=summaries,
        frozen_primary_screens=gates,user_split_checks=split_summary,
        development_physical_scenes=4,development_trajectory_physical_scenes=1,
        confirmation_new_physical_scenes=4,confirmation_trajectory_physical_scenes=2,confirmation_snapshots=32,
        signal_to_error_trace_range=[min(r['signal_to_error_trace_ratio'] for r in fresh),max(r['signal_to_error_trace_ratio'] for r in fresh)],
        error_mean_energy_fraction_max=max(r['error_mean_energy_fraction'] for r in fresh),
        training_started=False,formal_experiments='PAUSED',preserved_files_verified=len(preservation),
        estimator_timing=P.read(development.OUT/'ESTIMATOR_TIMING.json'),
        estimator_definition='Average R_k R_k^H/(N*P), either across all users or the half with smallest observed query energies; no true activity or channel is used.',
        caveats=['Covariance means uncentered spatial error second moment under a zero-mean working model.',
            'A common matrix can match pooled users while missing active-user-specific error structure.',
            'Current scope is Q=16, SNR=0 dB, activity probability 0.1, K=20..100 and the frozen 50000-sample receiver with damping 0.1.',
            'Principal-direction agreement and covariance accuracy do not prove Gaussianity or independence from the signal.',
            'An isotropic matrix has no identified principal directions; its arbitrary eigenbasis is not plotted as a directional estimate.',
            'User splits share the received observation; they are not independent physical trials.',
            'Matching current frozen-receiver messages does not guarantee calibration after retraining or changing message updates.',
            'No full receiver correction, whitening-based network input or training was started.'])
    P.save(output/'REPORT.json',report)
    P.save(output/'CONFIRMATION_GATE.json',dict(gates=gates,thresholds=protocol['practical_screen'],training_started=False))
    plt.rcParams.update({'font.family':'Microsoft YaHei','axes.unicode_minus':False})
    fig,axes=plt.subplots(1,3,figsize=(13,4.5),layout='constrained')
    styles=[('nominal_isotropic','原标量方差','#d55e00'),('query_second_moment','全部用户当前消息','#0072b2'),
        ('lower_half_query_second_moment','能量较低半数用户的当前消息','#009e73')]
    for mi,(method,label,color) in enumerate(styles):
        for si,stage in enumerate(('first','later')):
            group=[x['groups']['all'] for r in fresh if (r['iteration']==1)==(stage=='first') for x in r['results'] if x['method']==method]
            position=si+(mi-1)*.2
            for ax,key in zip(axes,['shape_relative_error','trace_ratio','top3_error_energy_recovery']):
                if key=='top3_error_energy_recovery' and method=='nominal_isotropic':continue
                values=[x[key] for x in group if key!='top3_error_energy_recovery' or x['strong_correlation']]
                if not values:continue
                median=float(np.median(values))
                ax.errorbar(position,median,yerr=[[median-min(values)],[max(values)-median]],fmt='o',color=color,capsize=4,label=label if si==0 else None)
                ax.scatter(np.full(len(values),position),values,s=10,color=color,alpha=.35)
    for ax in axes:
        ax.set_xticks([0,1],['首轮：20 个条件','中后期：12 个快照']);ax.grid(alpha=.25)
    axes[0].set_ylabel('归一化协方差形状的相对误差');axes[0].axhline(.25,ls='--',lw=.8,color='gray')
    axes[1].set_ylabel('估计总功率／实际误差总功率');axes[1].axhline(1,ls='--',lw=.8,color='gray')
    axes[2].set_ylabel('主要三个方向捕获的误差能量／最优值');axes[2].set_ylim(0,1.04)
    axes[2].axhline(.9,ls='--',lw=.8,color='gray')
    fig.legend(*axes[0].get_legend_handles_labels(),loc='outside lower center',ncol=3,fontsize=9)
    fig.suptitle('接收端协方差估计：4 个新场景首轮，并跟踪其中 2 个场景的中后期\n点为中位数、竖线为全部范围；右图仅统计相关性明显的快照；真值只参与评分',fontsize=11)
    for ext in ['png','pdf']:fig.savefig(output/f'confirmation.{ext}',dpi=180)
    plt.close(fig)
    print(dict(gates=gates,split_checks=split_summary,signal_to_error_trace_range=report['signal_to_error_trace_range']),flush=True)


if __name__=='__main__':main()
