"""Summarize the preserved paired stability diagnosis and render its evidence."""
import json
import hashlib
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/user_count_stability_20261019'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def main():
    source_paths=[]
    comparisons=[]
    for variant in ('new_networks','old_networks','oracle_both'):
        path=OUT/f'scene000_users60_{variant}'/'SUMMARY.json';source_paths.append(path)
        result=read(path)
        comparisons.append(dict(variant=variant,nmse_db=result['metrics']['nmse_db'],
            iterations=result['iterations'],stopping_reason=result['stopping_reason']))
    query_paths=[OUT/'queries_users60_iteration001/REPORT.json',
        *[OUT/f'queries_scene{i:03d}_users60_iteration001/REPORT.json' for i in (1,2,3)]]
    source_paths.extend(query_paths)
    queries=[read(path) for path in query_paths]
    first_trace=read(OUT/'scene000_users60_new_networks/TRACE.json')[0]
    assert abs(first_trace['nmse_db']-queries[0]['rows'][0]['joint_nmse_db'])<1e-10
    assert all(read(OUT/'scene000_users60_new_networks/SUMMARY.json')['exact_replay'].values())
    paused=read(ROOT/'results/new_models_paired_20261019_cuda_graph/STATUS.json')
    assert paused['status']=='PAUSED_FOR_STABILITY_DIAGNOSIS'
    # Verify every committed formal result remains complete and unchanged internally.
    result_root=ROOT/'results/new_models_paired_20261019_cuda_graph/user_count'
    rows=list(result_root.glob('scene*/condition*/proposed.json'))
    for path in rows:
        row=read(path)
        assert row['status']=='COMPLETE'
        assert hashlib.sha256(path.with_suffix('.npz').read_bytes()).hexdigest()==row['compact_sha256']
    summary=dict(status='DIAGNOSIS_COMPLETE_FORMAL_RUN_PAUSED',preserved_completed_cases=len(rows),
        formal_algorithm_changed=False,cross_channel='QUEUED',comparisons_60users_scene0=comparisons,
        query_diagnosis=dict(physical_scenes=4,noise_repeats_per_scene=3,
            nominal_variances=[q['variance'] for q in queries],
            largest_error_covariance_eigen_fraction=[q['eigen_fraction_largest'] for q in queries],
            white_false_alarms=[r['false_alarms'] for q in queries for r in q['rows'] if r['kind']=='independent_white_gaussian'],
            correlated_false_alarms=[r['false_alarms'] for q in queries for r in q['rows'] if r['kind']=='gaussian_matching_antenna_covariance'],
            inactive_users_per_scene=[q['inactive_users'] for q in queries]),
        interpretation='Antenna correlation alone reproduces large errors and saturated false activity on these fixed-query controls. It is not established as the sole cause of closed-loop instability.',
        limitations=['Post-hoc diagnosis on already observed test cases; do not tune receiver settings on these cases.',
            'Oracle phase/noise and synthetic queries use truth only in explicitly labelled diagnostic controls.',
            'No numerical changes or new training have been adopted; complete 500-scene evaluation remains paused.'],
        source_sha256={str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in source_paths})
    (OUT/'DIAGNOSIS.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    font=Path('C:/Windows/Fonts/msyh.ttc')
    if font.exists():
        font_manager.fontManager.addfont(str(font))
        plt.rcParams['font.family']=font_manager.FontProperties(fname=str(font)).get_name()
    plt.rcParams['axes.unicode_minus']=False
    fig,axes=plt.subplots(1,2,figsize=(12.8,4.6),layout='constrained')
    colors=['#2563eb','#e58b25','#7d4db3']
    labels=['新网络：估计相位与噪声','旧网络：相同输入','新网络：准确相位与噪声（oracle）']
    for variant,label,color in zip(('new_networks','old_networks','oracle_both'),labels,colors):
        trace_path=OUT/f'scene000_users60_{variant}'/'TRACE.json'
        trace=read(trace_path)
        axes[0].plot([r['iteration'] for r in trace],[r['nmse_db'] for r in trace],lw=1.2,label=label,color=color,alpha=.85)
    axes[0].set(title='同一 60 用户场景：完整迭代仍未稳定',xlabel='迭代次数',ylabel='完整信道 NMSE（dB，越低越好）')
    axes[0].legend(fontsize=8,loc='lower right');axes[0].grid(alpha=.2)
    kinds=['actual_receiver_query','independent_white_gaussian','independent_gaussian_matching_antenna_powers','gaussian_matching_antenna_covariance']
    names=['实际首轮输入','独立白噪声','仅匹配各天线噪声功率','匹配天线间噪声相关性']
    for kind,name,color,offset in zip(kinds,names,['#555555','#168579','#319ed1','#c64a51'],[-.18,-.06,.06,.18]):
        values=[];lower=[];upper=[]
        for query in queries:
            selected=np.array([r['joint_nmse_db'] for r in query['rows'] if r['kind']==kind])
            mean=float(10*np.log10(np.mean(10**(selected/10))))
            values.append(mean);lower.append(mean-selected.min());upper.append(selected.max()-mean)
        axes[1].errorbar(np.arange(4)+offset,values,yerr=[lower,upper],fmt='o',capsize=3,label=name,color=color,markersize=5)
    axes[1].set(title='固定噪声总功率：相关性足以复现误判',xlabel='物理场景编号',ylabel='单次联合去噪 NMSE（dB）',xticks=range(4),xticklabels=['0','1','2','3'])
    axes[1].legend(fontsize=8,loc='center right');axes[1].grid(alpha=.2)
    fig.suptitle('稳定性诊断｜正式长跑保持暂停',fontsize=15)
    fig.supxlabel('右图为真值辅助诊断；每场景 3 次合成噪声重复，误差条表示范围，并非置信区间。',fontsize=9)
    fig.savefig(OUT/'stability_diagnosis.png',dpi=160)
    plt.close(fig)
    print(json.dumps({'preserved':len(rows),'comparisons':comparisons,'white_false_alarms':summary['query_diagnosis']['white_false_alarms']}))


if __name__=='__main__':
    main()
