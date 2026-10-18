"""Audit a completed paired panel and render its tables, figures and paired contrasts."""
import argparse
import csv
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from afdm_jadcedd.utils import sha256,write_json

LABELS=dict(joint='L-DAMP joint',original='L-DAMP original',proposed='Proposed',
            somp='SOMP',gamp='GAMP-SBL',gnn='GNN-ASPL',offgrid_sbl='Off-grid SBL')
COLORS=dict(proposed='#c43c39',joint='#2166ac',original='#777777',somp='#e69f00',
            gamp='#8c510a',gnn='#8b5ba5',offgrid_sbl='#009e73')


def check_panel(folder):
    plan=json.loads((folder/'PLAN.json').read_text());status=json.loads((folder/'STATUS.json').read_text())
    rows=json.loads((folder/'ROWS.json').read_text())
    if plan['stage']!='evaluate' or status['status']!='COMPLETE':
        raise ValueError('A completed independent evaluation panel is required')
    expected={(s,n,m) for s in range(plan['scenes']) for n in plan['snr_db'] for m in plan['methods']}
    keys=[(r['scene'],r['snr_db'],r['method']) for r in rows]
    if len(keys)!=len(set(keys)) or set(keys)!=expected or any(r['status']!='COMPLETE' for r in rows):
        raise ValueError('Incomplete, duplicate or failed evaluation cases')
    for relative,digest in plan['source_sha256'].items():
        if sha256(folder/'sources'/relative)!=digest:
            raise ValueError('Saved source snapshot mismatch: '+relative)
    checks=[]
    for scene,snr,method in sorted(expected):
        case=folder/f'scene{scene:03d}'/f'snr{snr:+03d}'
        row=next(r for r in rows if (r['scene'],r['snr_db'],r['method'])==(scene,snr,method))
        record=json.loads((case/f'{method}.json').read_text())
        if row['inference_sha256']!=plan['inference_sha256'][method]:
            raise ValueError('Mixed inference identities')
        if record['input_sha256']!=sha256(case/'input.npz') or record['output_sha256']!=sha256(case/f'{method}.npz'):
            raise ValueError('Input/output identity mismatch')
        if method in ('joint','original') and 'outside_noise_support_calls' not in record:
            raise ValueError('Missing L-DAMP variance-range diagnostics')
        row['outside_support_calls']=record.get('outside_noise_support_calls')
        with np.load(case/'truth.npz') as truth,np.load(case/f'{method}.npz') as pred:
            active=truth['activity'].astype(bool);h=truth['channel'];estimate=pred['estimate'];decision=pred['activity_decision'].astype(bool)
            if not np.isfinite(estimate).all() or estimate.shape!=h.shape:
                raise ValueError('Invalid full-channel output')
            # Recompute active and inactive errors separately, using full precision.
            active_error=float(np.sum(abs(estimate[active].astype(complex)-h[active])**2))
            inactive_error=float(np.sum(abs(estimate[~active].astype(complex))**2))
            power=float(np.sum(abs(h[active].astype(complex))**2))
            target=np.zeros_like(h);target[active]=h[active]
            masked=float(np.sum(abs(estimate.astype(complex)*decision[:,None,None,None]-target)**2))
            tolerance=5e-6 if np.dtype('complex64') in (estimate.dtype,h.dtype) else 1e-11
            for key,value in [('full_error',active_error+inactive_error),('signal_energy',power),
                              ('active_error',active_error),('inactive_error',inactive_error),
                              ('estimated_activity_masked_error',masked)]:
                if not np.isclose(row[key],value,rtol=tolerance,atol=1e-12):
                    raise ValueError('Independent score mismatch: '+key)
            if row['misses']!=int(np.sum(active&~decision)) or row['false_alarms']!=int(np.sum(~active&decision)):
                raise ValueError('Activity accounting mismatch')
            if row['active']!=active.tolist() or row['users']!=len(active):
                raise ValueError('Scene labels or user count mismatch')
        checks.append(dict(scene=scene,snr_db=snr,method=method,passed=True))
    return plan,rows,checks


def statistics(plan,rows):
    summaries=[];contrasts=[]
    for snr in plan['snr_db']:
        indices=np.random.default_rng(202610150301).integers(plan['scenes'],size=(5000,plan['scenes']))
        draws={}
        for method in plan['methods']:
            values=sorted([r for r in rows if r['snr_db']==snr and r['method']==method],key=lambda r:r['scene'])
            errors=np.array([r['full_error'] for r in values]);power=np.array([r['signal_energy'] for r in values])
            active_error=sum(r['active_error'] for r in values);inactive_error=sum(r['inactive_error'] for r in values)
            active_users=sum(sum(r['active']) for r in values)
            masked=np.array([r['estimated_activity_masked_error'] for r in values])
            misses=np.array([r['misses'] for r in values]);false=np.array([r['false_alarms'] for r in values]);users=np.array([r['users'] for r in values])
            nmse=10*np.log10(errors[indices].sum(1)/power[indices].sum(1))
            aer=(misses+false)[indices].sum(1)/users[indices].sum(1)
            point_nmse=float(10*np.log10(errors.sum()/power.sum()));point_aer=float((misses+false).sum()/users.sum())
            draws[method]=(nmse,aer,point_nmse,point_aer)
            summaries.append(dict(method=method,snr_db=snr,scenes=len(values),nmse_db=point_nmse,
                nmse_low=float(np.quantile(nmse,.025)),nmse_high=float(np.quantile(nmse,.975)),aer=point_aer,
                aer_low=float(np.quantile(aer,.025)),aer_high=float(np.quantile(aer,.975)),
                masked_nmse_db=float(10*np.log10(masked.sum()/power.sum())),misses=int(misses.sum()),
                false_alarms=int(false.sum()),users=int(users.sum()),zero_observed_errors=bool((misses+false).sum()==0),
                active_users=int(active_users),inactive_users=int(users.sum()-active_users),
                miss_rate=float(misses.sum()/active_users),false_alarm_rate=float(false.sum()/(users.sum()-active_users)),
                active_error=float(active_error),inactive_error=float(inactive_error),
                inactive_error_fraction=float(inactive_error/errors.sum()),
                mean_seconds=float(np.mean([r['seconds'] for r in values])),warnings=sum(r['warning_count'] for r in values)))
            summaries[-1]['outside_support_calls']=(sum(r['outside_support_calls'] for r in values)
                if all(r.get('outside_support_calls') is not None for r in values) else None)
        if 'joint' in draws:
            for method in plan['methods']:
                if method=='joint':continue
                delta_nmse=draws['joint'][0]-draws[method][0];delta_aer=draws['joint'][1]-draws[method][1]
                contrasts.append(dict(snr_db=snr,reference=method,delta_nmse_db=draws['joint'][2]-draws[method][2],
                    delta_nmse_95=np.quantile(delta_nmse,[.025,.975]).tolist(),
                    delta_aer=draws['joint'][3]-draws[method][3],delta_aer_95=np.quantile(delta_aer,[.025,.975]).tolist()))
    return summaries,contrasts


def render(folder,plan,summaries,contrasts):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(11,4.1),layout='constrained')
    order=[m for m in ['proposed','joint','original','offgrid_sbl','gnn','gamp','somp'] if m in plan['methods']]
    for method in order:
        rows=sorted([r for r in summaries if r['method']==method],key=lambda r:r['snr_db'])
        x=np.array([r['snr_db'] for r in rows]);color=COLORS[method];style='--' if method=='original' else '-'
        for ax,key,scale in [(axes[0],'nmse',1.),(axes[1],'aer',100.)]:
            value=np.array([r['nmse_db' if key=='nmse' else 'aer'] for r in rows])*scale
            lo=np.array([r[key+'_low'] for r in rows])*scale;hi=np.array([r[key+'_high'] for r in rows])*scale
            ax.plot(x,value,marker='o',markersize=3.5,color=color,linestyle=style,label=LABELS[method])
            ax.fill_between(x,lo,hi,color=color,alpha=.07)
    for ax in axes:
        ax.set_xlabel('SNR (dB)');ax.set_xticks(plan['snr_db']);ax.grid(alpha=.25)
    axes[0].set_ylabel('Full-channel NMSE (dB)');axes[1].set_ylabel('Activity error rate (%)');axes[1].set_ylim(bottom=0)
    axes[0].legend(fontsize=8,loc='best');axes[1].legend(fontsize=8,loc='best')
    fig.suptitle(f"Frozen receivers · {plan['scenes']} paired physical scenes · pointwise 95% scene bootstrap",fontsize=10)
    fig.savefig(folder/'comparison.png',dpi=180);fig.savefig(folder/'comparison.svg');plt.close(fig)
    configuration_lines=[]
    experiment_lines=[]
    metadata_path=folder/f"scene000/snr{plan['snr_db'][0]:+03d}/generation.json"
    if metadata_path.exists():
        metadata=json.loads(metadata_path.read_text())
        experiment_lines=[f"Physical scope: `{metadata['generator_version']}`, {metadata['users']} candidate users, {metadata['frames']} observations, {metadata['m_z']} × {metadata['m_y']} UPA, nominal activity probability {metadata['activity_probability']} conditioned on a nonempty scene, and intra-user path direction spread {metadata['path_direction_rms_deg']}°. The effective measurement operator is supplied exactly to every receiver. Geometry and noise conventions are retained in each case's `generation.json`.",'']
    configurations=plan.get('configurations',{})
    if configurations:
        descriptions={}
        for method in order:
            c=configurations[method]
            if method=='proposed':
                s=c['ep'];description=f"At most {s['iterations']} iterations; minimum {s['min_iterations']}; damping {s['damping']}; covariance mode {s['covariance_mode']}"
            elif method=='joint':
                s=c['solver'];description=f"{s['iterations']} iterations; {s['row_probes']} user-row directions; inference seed {s['seed']}"
            elif method=='original':
                s=c['solver'];description=f"{s['iterations']} iterations; {s['probes']} matrix probes; inference seed {s['divergence_seed']}"
            elif method=='somp':
                s=c['methods']['somp']['solver'];description=f"At most {s['max_atoms']} atoms; stopping rule {s['stopping_rule']}"
            elif method=='gamp':
                s=c['methods']['gamp_sbl_mmv']['solver'];description=f"At most {s['iterations']} iterations; tolerance {s['tolerance']}; stopping rule {s['stopping_rule']}"
            elif method=='offgrid_sbl':
                s=c['methods']['offgrid_sbl']['solver'];description=f"At most {s['iterations']} iterations; {s['offset_candidates']} offset candidates; {s['offset_sweeps']} offset sweeps"
            else:
                record=json.loads((folder/f"scene000/snr{plan['snr_db'][0]:+03d}/gnn.json").read_text())
                description=f"{record['iterations']} AMP steps; {record['effective_gnn_updates']} GNN updates; frozen mixed-SNR/grid checkpoint"
            descriptions[method]=description
        configuration_lines=['## Frozen solver settings','','| Method | Settings |','|---|---|']
        configuration_lines += ['| '+LABELS[m]+' | '+descriptions[m]+' |' for m in order]
        configuration_lines += ['','Iteration/probe counts refer to different operations and are not equal computational budgets.','']
        if 'gnn' in order:
            configuration_lines += [f"GNN checkpoint metadata records `{record['training_status']}` and `formal_qualification={record['formal_qualification']}`; preliminary training is `{record['preliminary_training']}`. Its loader checks the declared training contract, but this comparison does not establish full reproduction of the reference paper. This status is not an observed inference failure.",'']
    lines=['# Frozen L-DAMP comparison','',
        f"{plan['scenes']} independent physical scenes, reused across {len(plan['snr_db'])} SNRs and all methods. Every case is retained.",
        'Raw full-channel NMSE includes inactive-user error and is the primary channel metric. Ratios pool squared errors and true channel energy before converting to dB.',
        'Uncertainty uses 5,000 paired physical-scene bootstrap replicates. It is conditional on the fixed trained model, inference seed and calibrated activity rule.',
        'Zero observed activity errors can yield a degenerate bootstrap interval; this does not establish a zero population error rate.','',
        *experiment_lines,
        *configuration_lines,
        '![Paired comparison](comparison.png)','', '## Full-channel NMSE (dB)','',
        '| Method | '+' | '.join(str(n) for n in plan['snr_db'])+' |','|---|'+'---:|'*len(plan['snr_db'])]
    for method in order:
        values=[next(r for r in summaries if r['method']==method and r['snr_db']==s) for s in plan['snr_db']]
        lines.append('| '+LABELS[method]+' | '+' | '.join(f"{r['nmse_db']:.3f}" for r in values)+' |')
    lines+=['','## Activity error rate (%)','','| Method | '+' | '.join(str(n) for n in plan['snr_db'])+' |','|---|'+'---:|'*len(plan['snr_db'])]
    for method in order:
        values=[next(r for r in summaries if r['method']==method and r['snr_db']==s) for s in plan['snr_db']]
        lines.append('| '+LABELS[method]+' | '+' | '.join(f"{100*r['aer']:.2f}" for r in values)+' |')
    lines+=['','## Misses / false alarms','','Counts are shown separately because active and inactive user populations differ. Their denominators and conditional rates are in `STATISTICS.csv`.','',
        '| Method | '+' | '.join(str(n) for n in plan['snr_db'])+' |','|---|'+'---:|'*len(plan['snr_db'])]
    for method in order:
        values=[next(r for r in summaries if r['method']==method and r['snr_db']==s) for s in plan['snr_db']]
        lines.append('| '+LABELS[method]+' | '+' | '.join(f"{r['misses']} / {r['false_alarms']}" for r in values)+' |')
    lines+=['','## Inactive-user share of full-channel squared error (%)','',
        'This is an error decomposition using truth only for offline scoring; it is not an inference mask or an alternative primary metric.','',
        '| Method | '+' | '.join(str(n) for n in plan['snr_db'])+' |','|---|'+'---:|'*len(plan['snr_db'])]
    for method in order:
        values=[next(r for r in summaries if r['method']==method and r['snr_db']==s) for s in plan['snr_db']]
        lines.append('| '+LABELS[method]+' | '+' | '.join(f"{100*r['inactive_error_fraction']:.2f}" for r in values)+' |')
    lines+=['','## Candidate minus original L-DAMP','','Negative differences favor the joint candidate. Intervals use the same sampled scenes for both methods.','',
        '| SNR | NMSE difference / dB | 95% interval | AER difference / percentage points | 95% interval |','|---:|---:|---|---:|---|']
    for row in contrasts:
        if row['reference']=='original':
            lines.append(f"| {row['snr_db']} | {row['delta_nmse_db']:.3f} | [{row['delta_nmse_95'][0]:.3f}, {row['delta_nmse_95'][1]:.3f}] | {100*row['delta_aer']:.2f} | [{100*row['delta_aer_95'][0]:.2f}, {100*row['delta_aer_95'][1]:.2f}] |")
    lines+=['','## Computation and scope','','| Method | Mean inference seconds | Recorded runtime warnings | Variance-range flags |','|---|---:|---:|---:|']
    for method in order:
        values=[r for r in summaries if r['method']==method]
        outside=str(sum(r['outside_support_calls'] for r in values)) if all(r['outside_support_calls'] is not None for r in values) else '—'
        lines.append(f"| {LABELS[method]} | {np.mean([r['mean_seconds'] for r in values]):.2f} | {sum(r['warnings'] for r in values)} | {outside} |")
    lines+=['','Timings are receiver-reported solve/readout times, excluding model loading and data generation. Small input checks and record-building boundaries differ across receivers; the evaluation did not separately time the entire public call. Method order is fixed for every condition. Device and thread settings, exact model/configuration identities and source snapshots are in `PLAN.json`; warnings retain counts and source locations in each case.',
        'Proposed and both L-DAMP versions use MPS for their neural networks with CPU numerical operations. SOMP, GAMP-SBL, GNN-ASPL and Off-grid SBL use their frozen CPU implementations. These are measured implementation runtimes on this host, not equal-hardware or asymptotic complexity comparisons.',
        'The original eight matrix probes and candidate four user-row probes have different computational costs. The candidate retains a stochastic correction approximation; two development seeds produced 8.5%–23.0% relative channel differences despite small aggregate NMSE changes.',
        'The denoiser uses per-beam residual variances and does not model the full correlated error distribution. These empirical results do not prove state evolution or convergence for the structured AFDM operator.',
        'Both selected branch checkpoints occur at the final saved validation evaluation. Training optimization convergence has not been established; these are fixed-budget trained candidates. The complete standalone branch histories and their limits are reported in `../TRAINING_TRAJECTORY_AUDIT.json` and `../training_trajectories.png`.',
        'Evaluation seeds were checked against 13 recorded training, validation and readout/development cohorts in `../COMPARISON_SEED_AUDIT.json`, with no overlap. Two historical shared-readout configuration references are missing; their hashes were not marked verified. Seed-bearing plans/certificates and the actual configurations used here remain available. This does not establish complete reproduction of that historical workflow.',
        'Range flags have different definitions: the joint candidate counts mean variance outside [0.001, 1000]; the original counts any beam outside [0.001, 100]. No flags does not establish that the complete error distribution matches training.',
        'Secondary error after each method’s own activity-decision mask is in `STATISTICS.csv`; it never replaces raw full-channel NMSE. No true activity mask is used for that operation.',
        'This report does not itself promote a model or establish rare-event or cross-training-seed reliability.','']
    (folder/'REPORT.md').write_text('\n'.join(lines))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--results',type=Path,required=True);args=parser.parse_args()
    plan,rows,checks=check_panel(args.results);summary,contrasts=statistics(plan,rows)
    write_json(args.results/'PAIRED_CONTRASTS.json',dict(results=contrasts,bootstrap_seed=202610150301,replicates=5000))
    with (args.results/'STATISTICS.csv').open('w',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(summary[0]));writer.writeheader();writer.writerows(summary)
    render(args.results,plan,summary,contrasts)
    write_json(args.results/'OUTPUT_AUDIT.json',dict(status='PASS',cases=len(checks),checks=checks,
        checked_sources=len(plan['source_sha256']),report_script_sha256=sha256(Path(__file__)),
        scope='Saved input/output/source identities, complete paired panel, independently recomputed errors and activity decisions; report rendering still requires visual inspection'))
    print(json.dumps(dict(status='PASS',cases=len(checks),report=str(args.results/'REPORT.md'))))


if __name__=='__main__':main()
