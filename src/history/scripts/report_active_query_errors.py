"""Aggregate frozen active-user diagnosis and exact cross-user feedback terms."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import diagnose_active_query_errors as d

P=d.P;ROOT=d.ROOT;OUT=d.OUT;SRC=d.SRC
REPORT=ROOT/'results/active_query_error_diagnosis_20261019'

def main():
    protocol=d.verify();config=protocol['config'];stats=P.read(OUT/'STATISTICS.json');decomp=P.read(OUT/'DECOMPOSITION.json')
    assert len(stats)==32 and len(decomp)==6
    summary={}
    for label in ('first','later'):
        rows=[x for x in stats if (x['iteration']==1)==(label=='first')]
        users=[u for x in rows for u in x['per_user']]
        summary[label]=dict(snapshots=len(rows),user_snapshots=len(users),metrics={})
        for metric in users[0]['oracle_per_user_gaussian_reference']:
            v=[u['oracle_per_user_gaussian_reference'][metric] for u in users]
            summary[label]['metrics'][metric]=dict(median=float(np.median([x['actual'] for x in v])),
                above_reference_q975=sum(x['actual']>x['reference_q975'] for x in v),
                interpretation='User-snapshots are dependent observations, not independent experimental replicates.')
    detailed=[];trajectories={};max_error=0.
    for scene in (0,1):
        name=f'scene{scene:03d}_users20';bank=SRC/'bank/development'/name
        data=P.arrays(bank/'input.npz');truth=P.arrays(bank/'truth.npz')
        h=truth['channel']/config['scale'];active=truth['activity'].astype(bool);idx=np.flatnonzero(active)
        y=data['observation']/config['scale'];noise,_=d.source.old.estimate_spatial_noise(data['observation']);noise/=config['scale']**2
        linear=d.SpatialLinear(data['operator'],16,noise);a=linear.a;x=linear.pack(h)
        last=None;hist=[]
        for folder in sorted((OUT/'replay'/name).glob('iteration*')):
            state=P.arrays(folder/'state.npz');iteration=int(folder.name[9:]);c=d.tr(state['prior_covariance'])/16
            gain=linear.s*c/(noise+linear.s**2*c);f=np.sum(linear.s*gain)/len(x)
            L=(linear.v*(gain/f))@linear.uh;prior=linear.pack(state['prior'])
            # Algebraic attribution only. True interference uses truth; feedback is saved receiver state.
            true_other=L@(a@x);negative_other_prior=-L@(a@prior)
            for k in range(len(h)):
                sl=slice(16*k,16*(k+1));block=L[sl]@a[:,sl]
                true_other[sl]-=block@x[sl]
                negative_other_prior[sl]+=block@prior[sl]
            raw=np.stack([linear.unpack(true_other),linear.unpack(negative_other_prior)])
            parts=raw if last is None else .9*last+.1*raw;last=parts
            e=state['query']-h;he=np.sum(abs(h[idx])**2,axis=(1,2,3))
            beta=np.sum(h[idx].conj()*e[idx],axis=(1,2,3))/he
            hist.append(dict(iteration=iteration,users=idx.tolist(),probabilities=state['probability'][idx].tolist(),
                signal_response_real=(1+beta.real).tolist(),signal_response_imag=beta.imag.tolist(),
                other_feedback_projection_real=(np.sum(h[idx].conj()*parts[1,idx],axis=(1,2,3))/he).real.tolist(),
                false_alarms=int(np.sum(state['probability'][~active]>=.5))))
            if iteration!=30:continue
            saved=P.arrays(OUT/'decomposition'/name/'iteration030.npz')['other_users_component']
            relative=float(np.linalg.norm(parts.sum(axis=0)-saved)/np.linalg.norm(saved));max_error=max(max_error,relative)
            assert relative<1e-10
            chat=P.arrays(SRC/name/'iteration030'/'receiver_estimates.npz')['lower_half_query_second_moment']
            residual=e.copy();peruser=[]
            for k in idx:
                per=[]
                for parity in (0,1):
                    hh=h[k,:,parity::2,:];ee=e[k,:,parity::2,:]
                    b=np.vdot(hh,ee)/np.sum(abs(hh)**2)
                    residual[k,:,1-parity::2,:]-=b*h[k,:,1-parity::2,:]
                    per.append(dict(real=float(b.real),imag=float(b.imag)))
                he0=np.sum(abs(h[k])**2)
                peruser.append(dict(user=int(k),projection_fitted_row_halves=per,
                    true_other_signal_projection_real=float((np.vdot(h[k],parts[0,k])/he0).real),
                    negative_other_prior_signal_projection_real=float((np.vdot(h[k],parts[1,k])/he0).real)))
            detailed.append(dict(scene=scene,iteration=30,active_users=idx.tolist(),
                cross_user_split_relative_error=relative,per_user=peruser,
                active_covariance_original=d.compare(chat,d.second_moment(e[active])),
                active_covariance_after_oracle_cross_row_projection_removal=d.compare(chat,d.second_moment(residual[active])),
                oracle_projection_error_energy_reduction=float(1-np.sum(abs(residual[active])**2)/np.sum(abs(e[active])**2)),
                note='Uses true channel to diagnose signal-dependent component. Row halves share a physical channel and observation; not an independent physical-scene validation or usable correction.'))
        trajectories[name]=hist;P.save(OUT/'replay'/name/'SIGNAL_RESPONSE_HISTORY.json',hist)
    # Verify every bound input, the original frozen experiment assets and weights after analysis.
    for path,digest in P.read(OUT/'PROTOCOL.json')['assets_sha256'].items():assert P.sha(Path(path))==digest,path
    preserved=P.read(ROOT/'runs/stability_repair_20261019/PRESERVATION.json')
    for path,digest in preserved.items():assert P.sha(ROOT/path)==digest,path
    d.verify()
    report=dict(status='COMPLETE',training_started=False,formal_experiments='PAUSED',
        report_script_sha256=P.sha(Path(__file__)),statistics_sha256=P.sha(OUT/'STATISTICS.json'),decomposition_sha256=P.sha(OUT/'DECOMPOSITION.json'),
        scope=dict(physical_scenes=4,snapshots=32,first_query_snapshots=20,later_query_snapshots=12,
            replayed_physical_scenes=2,replayed_iterations=sum(len(x) for x in trajectories.values()),gaussian_repeats=199),
        conclusions=[
            'Shared antenna covariance captures pooled error structure but not all active-user conditional errors.',
            'Both K20 iteration-30 failures exceed finite-sample independent-column Gaussian reference variation.',
            'Even per-user oracle antenna second moments do not explain signal-error alignment: all five target users exceed the simulated upper reference range.',
            'Exact decomposition identifies negative signal projection mainly in other-user feedback. In the one-active-user scene, all other true channels are zero, so this term is entirely from inactive-user receiver feedback.',
            'Signal attenuation is transient in these two trajectories; active probabilities and NMSE recover later. Do not present iteration-30 behavior as terminal performance.',
            'Fourth-moment diagnostics do not show a broad heavy-tail problem. Lack of independent additive noise is stronger evidence here than a claim of gross marginal non-Gaussianity.',
            'Covariance-conditioned training may help but is not established as sufficient. A correct covariance does not by itself repair conditional mean distortion or feedback dependence.',
        ],aggregate=summary,focused_cases=detailed,exact_decomposition=decomp,
        maximum_split_algebra_relative_error=max_error,preserved_files_verified=len(preserved),
        caveats=['Oracle quantities used only offline.','No matched network was trained; no achieved performance improvement is claimed.',
                 'Monte Carlo reference intervals condition on fitted covariance and fixed signal; not scene-population confidence intervals.',
                 'The measurement residual includes estimated-operator mismatch and thermal noise together.',
                 'No proof that every richer covariance model fails; the tested model is shared or per-user antenna covariance with independent Gaussian channel coordinates.'])
    P.save(REPORT/'REPORT.json',report)
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(2,2,figsize=(11.4,7),sharex='col')
    for col,(name,rows) in enumerate(trajectories.items()):
        t=[r['iteration'] for r in rows];users=rows[0]['users']
        for j,k in enumerate(users):
            color=plt.get_cmap('tab10')(j)
            ax[0,col].plot(t,[r['signal_response_real'][j] for r in rows],label=f'User {k}',color=color)
            ax[1,col].plot(t,[r['probabilities'][j] for r in rows],color=color)
        ax[0,col].axhline(1,color='black',linestyle='--',linewidth=1,label='Unit response reference')
        ax[0,col].set_title(f'Scene {col}: {len(users)} active user(s), K=20')
        ax[0,col].set_ylabel('Signal projection (real)')
        ax[1,col].set_ylabel('Activity probability');ax[1,col].set_xlabel('Receiver iteration')
        ax[1,col].set_ylim(-.03,1.03)
        for a0 in ax[:,col]:a0.axvline(30,color='#666666',linestyle=':',linewidth=1);a0.grid(alpha=.2)
        ax[0,col].legend(fontsize=8)
    fig.suptitle('Active-user error diagnosis: signal attenuation develops during feedback',fontsize=14)
    fig.text(.5,.015,'Truth-assisted signal projection; unchanged networks. Two development trajectories, not formal performance results.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.04,1,.95));REPORT.mkdir(parents=True,exist_ok=True)
    fig.savefig(REPORT/'active_error_diagnosis.png',dpi=170);fig.savefig(REPORT/'active_error_diagnosis.pdf');plt.close(fig)
    P.save(OUT/'STATUS.json',dict(status='COMPLETE',snapshots=32,training_started=False,weights_unchanged=True,
        preserved_files_verified=len(preserved),formal_experiments='PAUSED',report=str(REPORT/'REPORT.json')))
    print('Complete. Preserved files:',len(preserved),'split relative error:',max_error,flush=True)
    for x in detailed:
        print('scene',x['scene'],'shape',x['active_covariance_original']['shape_relative_error'],'after oracle projection',
            x['active_covariance_after_oracle_cross_row_projection_removal']['shape_relative_error'],'energy reduction',x['oracle_projection_error_energy_reduction'],flush=True)

if __name__=='__main__':
    with d.threadpool_limits(1):main()
