"""Aggregate by physical scene before summarizing repeated query controls."""
from pathlib import Path
import time
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import validate_message_network_match as m


def summarize(rows):
    cases=[]
    for row in rows:
        kinds=sorted({x['kind'] for x in row['rows']})
        for kind in kinds:
            samples=[x for x in row['rows'] if x['kind']==kind]
            valid=[x for x in samples if x['status']=='COMPLETE']
            if len(valid)!=len(samples):
                cases.append(dict(scene=row['scene'],users=row['users'],iteration=row['iteration'],kind=kind,
                    status='OUTSIDE_SUPPORT',omitted_from_pooled=True))
                continue
            avg=lambda k:float(np.mean([x[k] for x in valid]))
            cases.append(dict(scene=row['scene'],users=row['users'],iteration=row['iteration'],kind=kind,status='COMPLETE',
                repetitions=len(samples),full_error=avg('full_error'),signal_energy=avg('signal_energy'),
                oracle_activity_error=avg('oracle_activity_error'),active=avg('active'),inactive=avg('inactive'),
                misses=avg('misses'),false_alarms=avg('false_alarms'),
                brier_score=avg('brier_score'),active_conditional_mse=avg('active_conditional_mse'),
                active_predicted_variance=avg('active_predicted_variance')))
    pooled=[]
    for users in [20,40,60,80,100]:
        for kind in sorted({x['kind'] for x in cases}):
            group=[x for x in cases if x['iteration']==1 and x['users']==users and x['kind']==kind and x['status']=='COMPLETE']
            if not group:continue
            sums={k:sum(x[k] for x in group) for k in ['full_error','signal_energy','oracle_activity_error','active','inactive','misses','false_alarms']}
            ratio=sum(x['active_conditional_mse']*x['active'] for x in group)/sum(x['active_predicted_variance']*x['active'] for x in group)
            pooled.append(dict(users=users,kind=kind,physical_scenes=len(group),
                nmse_db=float(10*np.log10(sums['full_error']/sums['signal_energy'])),
                oracle_activity_nmse_db=float(10*np.log10(sums['oracle_activity_error']/sums['signal_energy'])),
                false_alarm_rate=sums['false_alarms']/sums['inactive'],miss_rate=sums['misses']/sums['active'],
                aer=(sums['misses']+sums['false_alarms'])/(sums['active']+sums['inactive']),
                active_mse_over_predicted_variance=ratio,**sums))
    return cases,pooled


def main():
    state=m.P.read(m.OUT/'STATUS.json')
    assert state['status']=='COMPLETE' and state['completed']==26
    protocol=m.P.read(m.OUT/'PROTOCOL.json')
    for path,digest in protocol['source_and_weight_sha256'].items():assert m.P.sha(m.d.ROOT/path)==digest,path
    paths=sorted(m.OUT.glob('scene*/diagnosis*.json'));assert len(paths)==26
    rows=[m.P.read(p) for p in paths];cases,pooled=summarize(rows)
    out=m.d.ROOT/'results/message_network_match_20261019';out.mkdir(exist_ok=True)
    # First-query replay matches the existing FP32 native development runs.
    replays=[]
    for row in rows:
        source=m.d.OUT/'evaluations/development/damping0.1_budget1200_fp32'/f'scene{row["scene"]:03d}_users{row["users"]}'/'TRACE.json'
        if source.exists():
            trace=m.P.read(source)
            native=trace[row['iteration']-1]['nmse_db']
            actual=next(x for x in row['rows'] if x['kind']=='actual')['nmse_db']
            replays.append(dict(scene=row['scene'],users=row['users'],iteration=row['iteration'],difference_db=actual-native))
    assert len(replays)==26 and max(abs(x['difference_db']) for x in replays)<1e-7
    historical_cost=[]
    for stage in ['second','activity']:
        path=m.d.ROOT/'runs/proposed_auxiliary_100_cuda_graph_20261019/n50000'/stage/'history.json'
        history=m.P.read(path);times=[x['elapsed_epoch_seconds'] for x in history[-20:] if 'elapsed_epoch_seconds' in x]
        historical_cost.append(dict(stage=stage,training_samples=50000,median_seconds_per_epoch=float(np.median(times)),
            scope='Historical throughput only; altered covariance input, data generation and objectives are not benchmarked'))
    report=dict(status='COMPLETE',created_unix=time.time(),physical_development_scenes=4,
        first_query_conditions=20,later_query_conditions=6,network_evaluations=sum(len(x['rows']) for x in rows),
        training_started=False,weights_unchanged_sha256_verified=True,formal_experiments='PAUSED',
        controls=cases,first_query_pooled=pooled,native_replay_checks=replays,historical_training_cost=historical_cost,
        source_sha256={str(p):m.P.sha(p) for p in paths},
        interpretation=['This is a four-scene exploratory diagnosis, not a formal receiver benchmark or sealed acceptance.',
            'Gaussian repetitions are averaged within each physical scene before pooling; they are not independent physical scenes.',
            'Oracle variance labels, oracle activity masks and covariance-matched noise use ground truth only offline.',
            'Oracle activity masking isolates conditional mean error; it is not a guaranteed NMSE lower bound for every imperfect estimator.',
            'The evidence can motivate matched-data pilot training, but cannot prove retraining is necessary or sufficient.',
            'Correlated Gaussian controls reproduce antenna second moments only, not every dependence in the real iterative messages.',
            'No corrected deployable receiver or universal convergence guarantee is claimed.'])
    m.P.save(out/'REPORT.json',report)
    plt.rcParams.update({'font.family':'Microsoft YaHei','axes.unicode_minus':False})
    fig,axes=plt.subplots(1,3,figsize=(14,4.6),layout='constrained')
    styles=[('actual','真实首轮消息','#d55e00','-'),('white','白高斯噪声对照','#0072b2','-'),
        ('diagonal_antenna','匹配各天线功率、去除相关性','#009e73','--'),
        ('correlated_antenna','匹配天线相关性的高斯噪声','#cc79a7','-'),
        ('actual_oracle_per_user_variance','真实消息＋真值逐用户方差','#666666',':')]
    for kind,label,color,style in styles:
        values=sorted([x for x in pooled if x['kind']==kind],key=lambda x:x['users'])
        x=[z['users'] for z in values]
        for ax,metric in zip(axes,['nmse_db','false_alarm_rate','active_mse_over_predicted_variance']):
            ax.plot(x,[z[metric] for z in values],linestyle=style,marker='o',ms=4,lw=1.5,color=color,label=label)
    axes[0].set_ylabel('单次查询联合估计 NMSE（dB）')
    axes[1].set_ylabel('不活跃用户的误报率');axes[1].set_ylim(-.03,1.06)
    axes[2].set_ylabel('活跃用户实际均方误差／网络方差读数');axes[2].set_yscale('log')
    axes[2].axhline(1,color='black',lw=.8,ls='--')
    for ax in axes:ax.set_xlabel('用户数');ax.set_xticks([20,40,60,80,100]);ax.grid(alpha=.25)
    handles,labels=axes[0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='outside lower center',ncol=3,fontsize=8)
    fig.suptitle('冻结 50,000 样本网络：4 个独立开发场景 × 5 个用户数\n真值辅助的单次查询诊断；不是正式迭代接收机性能',fontsize=12)
    for ext in ['png','pdf']:fig.savefig(out/f'first_query_controls.{ext}',dpi=180)
    plt.close(fig)
    print(json.dumps(dict(report=str(out/'REPORT.json'),first_query_pooled=pooled),ensure_ascii=False),flush=True)


if __name__=='__main__':main()
