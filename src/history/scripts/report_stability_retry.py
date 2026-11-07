"""Summarize all retained acceptance attempts without hiding failed gates."""
from pathlib import Path
import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import repair_stability_retry as r
import validate_stability_candidate as v


def main():
    out = r.d.ROOT/'results/stability_repair_retry_20261019'
    out.mkdir(exist_ok=True)
    gate = v.evaluate('acceptance', candidate=r.NAME)
    previous = r.d.paired.read(r.OLD/'ACCEPTANCE_GATE.json')
    regression_path = r.OUT/'regression_previous_failure/SUMMARY.json'
    regression = r.d.paired.read(regression_path) if regression_path.exists() else {'status':'RUNNING'}
    summaries = list((r.OUT/'evaluations/acceptance'/r.NAME).glob('scene*/SUMMARY.json'))
    records = [r.d.paired.read(p.parent/'record.json') for p in summaries]
    report = dict(updated_unix=time.time(), previous_acceptance=previous,
        independent_acceptance=gate, known_failure_regression=regression,
        completed_candidate_cases=len(summaries), second_attempt_cases=sum(x['attempt_count']>1 for x in records),
        total_attempt_iterations=sum(x['iterations'] for x in records),
        max_total_iterations=max([x['iterations'] for x in records], default=0),
        median_total_iterations=float(np.median([x['iterations'] for x in records])) if records else None,
        message_form_audit=r.d.paired.read(r.d.ROOT/'results/stability_message_form_20261019/AUDIT.json'),
        source_sha256={str(p):r.d.paired.sha(p) for p in summaries},
        interpretation=['The first 60-case acceptance failed (59 converged); it remains a failed attempt.',
            'The new 60 conditions use 12 independent scene seeds, excluded from training, development, prior acceptance and formal tests.',
            'Known-failure regression is post-freeze evidence and is not counted as a new independent test.',
            'FP32 and damping retries change numerical execution, not the Gaussian/AWGN statistical approximation.',
            'All failed attempts count toward time and iterations. No universal convergence or statistical superiority is claimed.',
            'Only user-count resumption is covered. Other experiment families remain unvalidated.'])
    r.d.paired.save(out/'REPORT.json',report)
    if gate['status']=='INCOMPLETE':
        print(dict(status='INCOMPLETE',completed=len(summaries)));return
    plt.rcParams.update({'font.family':'Microsoft YaHei','axes.unicode_minus':False})
    fig,axes=plt.subplots(1,3,figsize=(14,4),layout='constrained')
    x=[c['users'] for c in gate['comparisons']]
    for method,label,color in [(r.NAME,'候选：FP32，按收敛状态重试','#0072b2'),('offgrid_sbl','同观测 SBL','#009e73')]:
        axes[0].plot(x,[c['methods'][method]['nmse_db'] for c in gate['comparisons']],'-o',label=label,color=color)
        axes[1].plot(x,[c['methods'][method]['aer'] for c in gate['comparisons']],'-o',label=label,color=color)
    for k in x:
        group=[r.d.paired.read(p) for p in summaries if r.d.paired.read(p)['users']==k]
        axes[2].scatter([k]*len(group),[z['iterations'] for z in group],s=20,alpha=.7,color='#0072b2')
    for ax in axes:
        ax.set_xlabel('用户数');ax.set_xticks(x);ax.grid(alpha=.25)
    axes[0].set_ylabel('完整信道 NMSE（dB）');axes[1].set_ylabel('活动检测错误率')
    axes[2].set_ylabel('总迭代次数（包括失败重试）');axes[0].legend(fontsize=8)
    fig.suptitle(f'新独立验证：12 个场景 × 5 个用户数，SNR = 0 dB；原验收标准 {gate["status"]}\n点估计，不是正式 500 场景结果；此前失败的 60 条件验证另行保留',fontsize=11)
    for suffix in ['png','pdf']:fig.savefig(out/f'independent_acceptance.{suffix}',dpi=180)
    plt.close(fig)
    print(dict(status=gate['status'],known_failure_regression=regression.get('passed'),output=str(out)),flush=True)


if __name__=='__main__':main()
