"""Report retained development controls and independent acceptance separately."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import repair_stability_development as d
import validate_stability_candidate as validation


def run():
    output=d.ROOT/'results/stability_repair_20261019'
    output.mkdir(exist_ok=True)
    plt.rcParams.update({'font.family':'Microsoft YaHei','axes.unicode_minus':False})
    fig,axes=plt.subplots(2,3,figsize=(14,7),layout='constrained')
    cases=[('damping0.2','原设置：更新幅度 0.2，TF32','#d95f02'),
           ('damping0.1','更新幅度 0.1，TF32','#7570b3'),
           (validation.TARGET,'候选：更新幅度 0.1，完整 FP32','#0072b2')]
    sources={}
    for column,users in enumerate((20,60,100)):
        for candidate,label,color in cases:
            path=d.OUT/'evaluations/development'/candidate/f'scene000_users{users}'/'TRACE.json'
            if not path.exists():continue
            trace=d.paired.read(path);sources[str(path)]=d.paired.sha(path)
            x=[r['iteration'] for r in trace]
            axes[0,column].plot(x,[r['nmse_db'] for r in trace],color=color,label=label,lw=1.4)
            values=[r['raw_site_residual'] if r['raw_site_residual'] is not None else np.nan for r in trace]
            axes[1,column].semilogy(x,values,color=color,lw=1.3)
            if candidate==validation.TARGET:
                axes[0,column].plot(x[-1],trace[-1]['nmse_db'],'o',color=color,ms=4)
        path=d.OUT/'evaluations/development/offgrid_sbl'/f'scene000_users{users}'/'SUMMARY.json'
        sbl=d.paired.read(path)['metrics']['nmse_db'];sources[str(path)]=d.paired.sha(path)
        axes[0,column].axhline(sbl,ls='--',lw=1,color='#009e73',label='同场景 SBL')
        axes[1,column].axhline(.01,ls='--',color='black',lw=1)
        axes[0,column].set_title(f'{users} 用户')
        axes[1,column].set_xlabel('迭代次数')
        axes[1,column].set_ylim(1e-5,3)
        for row in range(2):axes[row,column].grid(alpha=.25)
    axes[0,0].set_ylabel('完整信道 NMSE（dB）')
    axes[1,0].set_ylabel('Gaussian site 更新的相对变化')
    axes[0,0].legend(fontsize=8)
    fig.suptitle('独立开发场景 0：同观测、同 50,000 样本权重，SNR = 0 dB\n下排虚线为原残差阈值 0.01；完整停止条件还包含估计、活动概率和连续稳定轮数',fontsize=12)
    for suffix in ('png','pdf'):fig.savefig(output/f'development_controls.{suffix}',dpi=180)
    plt.close(fig)
    attempts=[]
    for folder in sorted((d.OUT/'evaluations/development').iterdir()):
        rows=[d.paired.read(path) for path in folder.glob('scene*/SUMMARY.json')]
        if rows:
            attempts.append(dict(candidate=folder.name,cases=len(rows),
                converged=sum(r['stopping_reason']=='CONVERGED' for r in rows),
                results=str(folder),scope='Development only; all recorded attempts retained'))
    report=dict(development=validation.evaluate('development'),
        acceptance=validation.evaluate('acceptance'),
        development_candidate_attempts=attempts,
        precision=d.paired.read(d.OUT/'PRECISION_AUDIT.json'),
        plot_source_sha256=sources,
        formal_status=d.paired.read(d.ROOT/'results/new_models_paired_20261019_stability_fp32/STATUS.json')
          if (d.ROOT/'results/new_models_paired_20261019_stability_fp32/STATUS.json').exists() else 'NOT_RESUMED',
        changes=dict(weights='UNCHANGED',damping=[.2,.1],max_iterations=[600,1200],
            cudnn_allow_tf32=[True,False],stopping_tolerances='UNCHANGED'),
        caveats=['Development curves are tuning evidence, not formal test results.',
            'The zero-output 0 dB original K=100 case is not a successful convergence.',
            'No universal convergence guarantee or statistical significance claim.',
            'Only user-count settings are covered; cross-channel requires separate validation.'])
    d.paired.save(output/'REPORT.json',report)
    print(output,flush=True)

if __name__=='__main__':run()
