"""Summarize all predeclared activity controls, including adverse cases."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import diagnose_activity_evidence_feedback as D


def main():
    P=D.P;protocol=D.verify()
    null=P.read(D.OUT/'null/SUMMARY.json')
    feedback=P.read(D.OUT/'feedback/SUMMARY.json')
    offline=P.read(D.OUT/'offline/SUMMARY.json')
    assert all(x['status']=='COMPLETE' for x in [null,feedback,offline])
    lookup={(r['case'],r['variant']):r for r in feedback['results']}
    paired=[];checks=[]
    for case in D.CASES:
        a=lookup[case,'baseline'];b=lookup[case,'prior_first30']
        bank=D.D.SOURCE/'bank/development'/case
        active=P.arrays(bank/'truth.npz')['activity'].astype(bool)
        prior=float(P.arrays(bank/'input.npz')['activity_prior'])
        records={variant:P.read(D.OUT/'feedback'/case/variant/'record.json') for variant in ['baseline','prior_first30']}
        raw=records['prior_first30']['original_classifier_logit_trace']
        assert np.array_equal(raw[0],records['baseline']['trace'][0]['classifier_logit_per_user'])
        assert all(np.array_equal(raw[i],records['prior_first30']['trace'][i]['classifier_logit_per_user']) for i in range(30,300))
        checks.append(dict(case=case,first_raw_logits_identical=True,original_logits_restored_after30=True,
            unsupported_user_queries={variant:records[variant]['unsupported_user_queries'] for variant in records},
            rejected_site_iterations={variant:records[variant]['reused_site_iterations'] for variant in records}))
        evidence=[]
        for it in [1,30,31,120,300]:
            item=dict(iteration=it)
            for variant in records:
                record=records[variant]
                l=record['original_classifier_logit_trace'][it-1] if variant=='prior_first30' else record['trace'][it-1]['classifier_logit_per_user']
                snap=P.arrays(D.OUT/'feedback'/case/variant/'checkpoints'/f'iteration{it:04d}.npz')
                q=snap['query'];selected=np.argsort(np.mean(abs(q)**2,axis=(1,2,3)),kind='stable')[:len(q)//2]
                cov=D.second_moment(q[selected]);eigen=np.linalg.eigvalsh(cov)
                item[variant]=dict(raw_network_metrics=D.metrics(l,active,prior),
                    lower_half_query_largest_eigen_fraction=float(eigen[-1]/eigen.sum()))
            evidence.append(item)
        checkpoints=[]
        for it in [1,10,30,31,60,120,300]:
            ra=a['trace'][it-1];rb=b['trace'][it-1]
            checkpoints.append(dict(iteration=it,baseline=ra,prior_first30=rb,
                nmse_gain_db=ra['nmse_db']-rb['nmse_db'],active_nmse_gain_db=ra['active_nmse_db']-rb['active_nmse_db']))
        paired.append(dict(case=case,baseline=a['metrics'],prior_first30=b['metrics'],
            final_gain_db=a['metrics']['nmse_db']-b['metrics']['nmse_db'],checkpoints=checkpoints,
            raw_evidence_and_query_covariance=evidence))
    preservation=P.read(P.ROOT/'runs/stability_repair_20261019/PRESERVATION.json')
    for path,digest in preservation.items():assert P.sha(P.ROOT/path)==digest,path
    P.save(D.RESULT/'REPORT.json',dict(status='COMPLETE',protocol=str(D.OUT/'PROTOCOL.json'),
        training_started=False,weights_unchanged=True,formal_experiments='PAUSED',
        preserved_historical_files=len(preservation),source_hashes_verified=len(protocol['source_and_weight_sha256']),
        physical_scenes=4,physical_conditions=8,paired_runs=16,equal_updates_per_run=300,
        convergence_claim=False,paired=paired,null_controls=null['results'],
        implementation_checks=checks,
        offline_traces=str(D.OUT/'offline/SUMMARY.json'),
        limits=protocol['limits'],truth_policy=protocol['truth_policy'],
        script_sha256=P.sha(Path(__file__))))
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(2,4,figsize=(15,7),sharex=True)
    for ax,pair in zip(axes.flat,paired):
        for variant,color,label in [('baseline','#bd493d','Original activity'),('prior_first30','#24799e','Activity prior for first 30')]:
            rows=lookup[pair['case'],variant]['trace']
            ax.plot([r['iteration'] for r in rows],[r['nmse_db'] for r in rows],color=color,label=label,lw=1.5)
        ax.axvline(30,color='gray',ls=':',lw=1)
        ax.set_title(pair['case'].replace('scene','Seed ').replace('_users',' / K='))
        ax.grid(alpha=.2);ax.set_xlabel('Iteration');ax.set_ylabel('Full-channel NMSE (dB)')
    axes.flat[0].legend(fontsize=8)
    fig.suptitle('Frozen new-50k weights; damping 0.1; same observations; fixed 300 updates\nDevelopment diagnostic only. No convergence or formal acceptance claim.',fontsize=13)
    fig.tight_layout(rect=(0,0,1,.92));D.RESULT.mkdir(parents=True,exist_ok=True)
    fig.savefig(D.RESULT/'feedback_nmse.png',dpi=180);fig.savefig(D.RESULT/'feedback_nmse.pdf');plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(11,4.5))
    first=[r for r in null['results'] if r['iteration']==1]
    x=np.arange(len(first));width=.25
    for offset,kind,label,color in [(-1,'white','White Gaussian','#24799e'),(0,'receiver_correlated','Receiver-estimated correlation','#e69f00'),(1,'actual','Actual inactive users','#bd493d')]:
        rates=[]
        for row in first:
            item=row['actual'] if kind=='actual' else row['controls'][kind]
            rates.append(item['false_alarms']/item['inactive'])
        axes[0].bar(x+offset*width,rates,width,label=label,color=color)
    axes[0].set_xticks(x,[r['case'].replace('scene','S').replace('_users',' K') for r in first],rotation=15)
    axes[0].set_ylabel('Inactive-user false-alarm fraction');axes[0].set_ylim(0,1.18);axes[0].legend(fontsize=8)
    axes[0].set_title('First-query noise-only controls (128 draws each)')
    for row in offline['results']:
        if row['variant']!='estimated_phase_learned_activity':continue
        tr=[r for r in row['trace'] if r['iteration']<=120]
        axes[1].plot([r['iteration'] for r in tr],[r['ranking_pair_probability'] for r in tr],label=row['case'].replace('scene','S').replace('_users',' K'))
    axes[1].axhline(.5,color='gray',ls=':');axes[1].set_ylim(0,1.04)
    axes[1].set_title('Original logit ranking on real messages')
    axes[1].set_xlabel('Iteration');axes[1].set_ylabel('P(active logit > inactive logit), half credit for ties')
    axes[1].legend(fontsize=8);axes[1].grid(alpha=.2)
    fig.tight_layout();fig.savefig(D.RESULT/'activity_diagnosis.png',dpi=180);fig.savefig(D.RESULT/'activity_diagnosis.pdf');plt.close(fig)
    P.save(D.OUT/'STATUS.json',dict(status='COMPLETE',completed=16,expected=16,training_started=False,
        formal_experiments='PAUSED',weights_unchanged_sha256_verified=True))
    for row in paired:
        print(row['case'], 'base',round(row['baseline']['nmse_db'],4),'prior30',round(row['prior_first30']['nmse_db'],4),
            'gain',round(row['final_gain_db'],4),'miss/FA',row['baseline']['misses'],row['baseline']['false_alarms'],
            '->',row['prior_first30']['misses'],row['prior_first30']['false_alarms'],flush=True)


if __name__=='__main__':main()
