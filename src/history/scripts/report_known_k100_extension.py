"""Describe extended single-case convergence without changing acceptance gates."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import extend_known_k100_damping01_v2 as run

P=run.P;ROOT=run.ROOT;OUT=run.OUT
REPORT=ROOT/'results/known_k100_damping01_extension_20261019'

def window(rows):
    result=dict(start=rows[0]['iteration'],end=rows[-1]['iteration'],count=len(rows))
    bounds={'estimate_change':.003,'activity_change':1e-4,'input_covariance_change':.003,
        'raw_site_residual':.01,'activity_weight_residual':1e-4}
    for key,limit in bounds.items():
        v=np.array([r[key] for r in rows if r[key] is not None],float)
        result[key]=dict(min=float(v.min()),median=float(np.median(v)),max=float(v.max()),
            fraction_below_original_limit=float(np.mean(v<limit)),limit=limit)
    p=np.array([r['probabilities'] for r in rows]);span=np.ptp(p,axis=0)
    result['max_probability_range']=float(span.max());result['largest_probability_range_user']=int(span.argmax())
    result['max_fresh_iterations']=max(r['fresh_iterations'] for r in rows)
    result['max_stable_iterations']=max(r['stable_iterations'] for r in rows)
    result['decision_changes']=sum(r['decision_changes'] or 0 for r in rows)
    return result

def main():
    summary=P.read(OUT/'SUMMARY.json');assert summary['status']=='COMPLETE'
    rows=[json.loads(line) for line in (OUT/'progress.jsonl').read_text().splitlines()]
    assert len(rows)==summary['iterations']
    scores=P.read(OUT/'CHECKPOINT_SCORES.json');t=np.array([r['iteration'] for r in rows])
    probability=np.array([r['probabilities'] for r in rows]);truth=P.arrays(run.BANK/'truth.npz')['activity'].astype(bool)
    blocksize=500;blocks=[window(rows[a:min(a+blocksize,len(rows))]) for a in range(0,len(rows),blocksize) if len(rows[a:min(a+blocksize,len(rows))])>=50]
    tail=probability[-min(1000,len(rows)):];span=np.ptp(tail,axis=0);selected=np.argsort(span)[-5:][::-1]
    # Describe recurrence empirically; a finite trajectory cannot prove a limit cycle.
    centered=tail-tail.mean(axis=0,keepdims=True);variance=float(np.sum(centered**2))
    lags=[]
    for lag in range(20,min(500,len(tail)//2)+1):
        numerator=float(np.sum(centered[:-lag]*centered[lag:]));den=np.linalg.norm(centered[:-lag])*np.linalg.norm(centered[lag:])
        lags.append((lag,numerator/den if den else 0.))
    best=max(lags,key=lambda x:x[1]) if lags else None
    comparisons={}
    for label,path in [('old_1200',run.OLD/'SUMMARY.json'),('same_case_sbl',run.d.OUT/'evaluations/acceptance/offgrid_sbl/scene005_users100/SUMMARY.json')]:
        record=P.read(path);comparisons[label]={k:record['metrics'][k] for k in ('nmse_db','misses','false_alarms','active','inactive')}
    comparisons['extended']={k:summary['metrics'][k] for k in ('nmse_db','misses','false_alarms','active','inactive')}
    old_output=P.arrays(run.OLD/'prediction.npz');new_output=P.arrays(OUT/'prediction.npz')
    changed=np.flatnonzero(old_output['activity_decision']!=new_output['activity_decision'])
    report=dict(status='COMPLETE',iterations=summary['iterations'],converged=summary['converged'],
        conclusion='Reached the unchanged native stopping criteria at iteration 2262 after nonmonotonic transients. This is not evidence of an endless oscillation; it is also not a proof of a fixed point for unlimited future iterations. Recovery deteriorated as two inactive users became false positives. More iterations resolve the stopping-budget failure in this known case but do not establish an accurate receiver or a new independent acceptance pass.',
        weights_description='Existing newly trained 50,000-sample bundle, unchanged throughout; not an older historical bundle.',
        changed_decisions=[dict(user=int(k),truly_active=bool(truth[k]),old_probability=float(old_output['probabilities'][k]),final_probability=float(new_output['probabilities'][k])) for k in changed],
        cost_note='seconds measures the successful inference run. An earlier diagnostic-output field check stopped a replay at 1200; that run and its failure record remain in runs/known_k100_damping01_extension_20261019.',
        stopping_reason=summary['stopping_reason'],seconds=summary['seconds'],prefix_1200_exact=summary['prefix_1200_exact'],
        stopping_thresholds_unchanged=True,training_started=False,formal_experiments='PAUSED',independent_acceptance=False,
        windows=blocks,final_500=window(rows[-min(500,len(rows)):]),comparisons=comparisons,
        final=rows[-1],moving_users=[dict(user=int(k),active=bool(truth[k]),tail_probability_range=float(span[k]),final_probability=float(probability[-1,k])) for k in selected],
        recurrence=dict(tail_length=len(tail),centered_energy=variance,best_lag_over_20_to_500=best,
            caution='Descriptive normalized recurrence, not proof of a periodic orbit. Smooth drift also creates autocorrelation.'),
        all_queries_supported=all(r['unsupported_users']==0 for r in rows),all_sites_accepted=all(r['site_accepted'] for r in rows),
        clipped_feedback_iterations=sum(r['projected_eigenvalues']>0 for r in rows),
        preserved_files_verified=summary['preserved_files_verified'],
        script_sha256=P.sha(Path(__file__)),progress_sha256=P.sha(OUT/'progress.jsonl'),summary_sha256=P.sha(OUT/'SUMMARY.json'))
    P.save(REPORT/'REPORT.json',report)
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(2,2,figsize=(11.5,7.5))
    score_t=[x['iteration'] for x in scores];nmse=[x['metrics']['nmse_db'] for x in scores]
    ax[0,0].plot(score_t,nmse,color='#2776b5',marker='.',markersize=4,label='Proposed, damping 0.1')
    ax[0,0].axhline(comparisons['same_case_sbl']['nmse_db'],color='#777777',linestyle='--',label='Same-case SBL')
    ax[0,0].set_ylim(-1.5,1.5);ax[0,0].set_title('Recovery error (zoom; initial outlier omitted from axis)');ax[0,0].set_ylabel('NMSE (dB)');ax[0,0].legend(fontsize=8)
    for key,label in [('activity_change','Consecutive activity change'),('activity_weight_residual','Smoothed activity residual')]:
        values=[np.nan if r[key] is None else max(r[key],1e-12) for r in rows]
        ax[0,1].semilogy(t,values,label=label,linewidth=.8)
    ax[0,1].axhline(1e-4,color='black',linestyle='--',label='Original threshold');ax[0,1].set_ylim(1e-6,1);ax[0,1].set_title('Activity convergence checks');ax[0,1].legend(fontsize=8)
    for k in selected:
        ax[1,0].plot(t,probability[:,k],linewidth=.9,label=f'User {k} ({"active" if truth[k] else "inactive"})')
    ax[1,0].set_ylim(0,min(1.,float(tail[:,selected].max())*1.2+.005));ax[1,0].set_title('Users with largest probability variation in final 1,000 steps');ax[1,0].set_ylabel('Activity probability');ax[1,0].legend(fontsize=7)
    a=np.array([r['activity_weight_residual'] for r in rows]);ax[1,1].semilogy(t[-len(tail):],np.maximum(a[-len(tail):],1e-12),color='#dd7a21',linewidth=.9)
    ax[1,1].axhline(1e-4,color='black',linestyle='--');ax[1,1].set_title('Smoothed activity residual: final 1,000 steps');ax[1,1].set_ylabel('Residual')
    for a0 in ax.flat:
        a0.grid(alpha=.2);a0.set_xlabel('Iteration')
        if a0 is not ax[1,1]:a0.axvline(1200,color='#777777',linestyle=':',linewidth=1)
    fig.suptitle(f'Known K=100 case: unchanged weights and damping 0.1, {summary["iterations"]} iterations',fontsize=13)
    fig.text(.5,.015,'Single known-failure diagnostic. Stopping thresholds unchanged; original failed acceptance retained.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.04,1,.95));fig.savefig(REPORT/'extension_diagnosis.png',dpi=170);fig.savefig(REPORT/'extension_diagnosis.pdf');plt.close(fig)
    print({k:report[k] for k in ('iterations','converged','seconds','comparisons','final_500')})

if __name__=='__main__':main()
