"""Read completed depth-six evidence while depth seven runs; CPU only.

No receiver inference, receiver gradients, data regeneration or run mutations.
The only optimizer demonstration operates on three synthetic CPU scalars.
"""
import os
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import csv
import hashlib
import json
from pathlib import Path
import time

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
RUN = Path(r'D:\afdm-gfra-cpu\runs\lstmp_refinenet_depth7_20261020')
PARENT = RUN.parent / 'lstmp_refinenet_50000_epoch6_20261020'
OUT = ROOT / 'results/lstmp_depth6_readonly_analysis_20261020'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def scalar_adam_check():
    x = torch.nn.Parameter(torch.zeros(3, dtype=torch.float64))
    optimizer = torch.optim.Adam([x], lr=.001, foreach=False)
    for _ in range(4800):
        x.grad = torch.tensor([0., 0., 1.], dtype=torch.float64)
        optimizer.step()
    before = x.detach().clone()
    x.grad = torch.ones(3, dtype=torch.float64)
    optimizer.step()
    delta = (before-x.detach()).tolist()
    fresh = torch.nn.Parameter(torch.zeros(1, dtype=torch.float64))
    fresh_optimizer = torch.optim.Adam([fresh], lr=.001, foreach=False)
    fresh.grad = torch.ones(1, dtype=torch.float64)
    fresh_optimizer.step()
    reference = float(-fresh.detach()[0])
    theoretical = .1 * np.sqrt(1-.999**4801) / (1-.9**4801) / np.sqrt(.001)
    ratio = delta[0]/reference
    assert np.isclose(ratio, theoretical, rtol=1e-6)
    return dict(steps_with_mask=4800, first_unmasked_update=delta[0],
                fresh_adam_first_update=reference, ratio=ratio,
                theoretical_ratio_ignoring_epsilon=theoretical,
                already_active_component_update=delta[2],
                scope='Synthetic CPU scalars, not measured receiver parameter updates; causal performance impact untested.')


def decompose(result):
    rows = result['rows']
    depth = len(rows[0]['layer_metrics'])
    weight = np.array([.8/(depth-1)]*(depth-1)+[1.])/1.8
    nmse = np.array([[m['nmse'] for m in row['layer_metrics']] for row in rows])
    bce = np.array([[m['activity_bce'] for m in row['layer_metrics']] for row in rows])
    residual = np.max(np.abs(nmse@weight+.1*(bce@weight)-[r['loss'] for r in rows]))
    assert residual < 1e-6
    return dict(weighted_nmse=float(np.mean(nmse@weight)),
                weighted_bce=float(np.mean(bce@weight)),
                weighted_bce_contribution=float(.1*np.mean(bce@weight)),
                bce_fraction_of_total=float(.1*np.mean(bce@weight)/result['summary']['loss']),
                reconstruction_max_abs=float(residual),
                layers=[dict(layer=i+1, mean_nmse=float(nmse[:, i].mean()), mean_bce=float(bce[:, i].mean()),
                     pooled_nmse_db=float(10*np.log10(sum(r['layer_metrics'][i]['error_energy'] for r in rows)/
                                                      sum(r['layer_metrics'][i]['truth_energy'] for r in rows))),
                     misses=sum(r['layer_metrics'][i]['misses'] for r in rows),
                     false_alarms=sum(r['layer_metrics'][i]['false_alarms'] for r in rows)) for i in range(depth)])


def main():
    torch.set_num_threads(1)
    if OUT.exists():
        raise FileExistsError(OUT)
    start_state = read(RUN/'STATUS.json')
    manifest_hash = sha(RUN/'MANIFEST.json')
    manifest = read(RUN/'MANIFEST.json')
    assert all(sha(path) == digest for path, digest in manifest['snapshot_hashes'].items())
    folder = RUN/'checkpoints/depth_6'
    receipt = read(folder/'COMPLETE.json')
    assert receipt['status'] == 'COMPLETE' and receipt['steps'] == 9600
    paths = {f'epoch{i}': folder/f'validation_epoch_{i}.json' for i in range(3)}
    paths['five'] = PARENT/'checkpoints/depth_5/best_validation.json'
    inputs = {name: dict(path=str(path), sha256=sha(path)) for name, path in paths.items()}
    values = {name: read(path) for name, path in paths.items()}
    first = values['epoch1']; second = values['epoch2']; initialization = values['epoch0']
    for name, value in values.items():
        assert len(value['rows']) == 1200
        for row, reference in zip(value['rows'], first['rows']):
            assert (row['seed'], row['condition'], row['active'], row['inactive']) == (
                reference['seed'], reference['condition'], reference['active'], reference['inactive'])
            assert np.isclose(row['truth_energy'], reference['truth_energy'], rtol=1e-12)
    summaries = {name: value['summary'] for name, value in values.items()}
    components = {name: decompose(value) for name, value in values.items()}
    condition_rows = []
    for a, b in zip(first['by_condition'], second['by_condition']):
        assert a['condition'] == b['condition']
        condition_rows.append(dict(**a['condition'],
            epoch1_nmse_db=a['pooled_nmse_db'], epoch2_nmse_db=b['pooled_nmse_db'],
            delta_nmse_db=b['pooled_nmse_db']-a['pooled_nmse_db'],
            delta_misses=b['misses']-a['misses'], delta_false_alarms=b['false_alarms']-a['false_alarms'],
            delta_error_energy=b['error_energy']-a['error_energy'],
            delta_inactive_error_energy=b['inactive_error_energy']-a['inactive_error_energy'],
            delta_bce=b['mean_scene_activity_bce']-a['mean_scene_activity_bce']))
    s1, s2, s0, s5 = [summaries[k] for k in ('epoch1', 'epoch2', 'epoch0', 'five')]
    energy_delta = s2['error_energy']-s1['error_energy']
    fa_delta = s2['false_alarms']-s1['false_alarms']
    attribution = dict(
        worse_nmse_scenes=sum(b['nmse']>a['nmse'] for a, b in zip(first['rows'], second['rows'])),
        worse_nmse_conditions=sum(x['delta_nmse_db']>0 for x in condition_rows),
        error_energy_increase=energy_delta,
        inactive_error_energy_fraction=(s2['inactive_error_energy']-s1['inactive_error_energy'])/energy_delta,
        k100_false_alarm_increase=sum(x['delta_false_alarms'] for x in condition_rows if x['users']==100),
        k100_false_alarm_fraction=sum(x['delta_false_alarms'] for x in condition_rows if x['users']==100)/fa_delta,
        k100_error_energy_fraction=sum(x['delta_error_energy'] for x in condition_rows if x['users']==100)/energy_delta,
        adaptation_gain_inactive_fraction_vs_initialization=(s0['inactive_error_energy']-s1['inactive_error_energy'])/(s0['error_energy']-s1['error_energy']),
        adaptation_gain_inactive_fraction_vs_five=(s5['inactive_error_energy']-s1['inactive_error_energy'])/(s5['error_energy']-s1['error_energy']),
        mean_weighted_nmse_increase=components['epoch2']['weighted_nmse']-components['epoch1']['weighted_nmse'],
        mean_weighted_bce_increase=components['epoch2']['weighted_bce']-components['epoch1']['weighted_bce'])
    # Read only tiny tensors from memory-mapped immutable completed checkpoints.
    checkpoint_info = {}
    for name in ('best', 'last'):
        path = folder/f'{name}.pt'
        saved = torch.load(path, map_location='cpu', mmap=True, weights_only=False)
        selected = {k: v.tolist() for k, v in saved['state'].items()
                    if k.endswith('.calibration') or k.endswith('activity.head.2.bias')}
        checkpoint_info[name] = dict(path=str(path), size=path.stat().st_size,
                                     epoch=saved['epoch'], selected_tensors=selected)
        if name == 'last':
            optimizer = saved['optimizer']
            checkpoint_info[name]['optimizer'] = [dict(
                lr=g['lr'], betas=g['betas'], weight_decay=g['weight_decay'],
                parameters=len(g['params']),
                distinct_steps=sorted(set(float(optimizer['state'][i]['step']) for i in g['params'] if i in optimizer['state']))
                ) for g in optimizer['param_groups']]
            checkpoint_info[name]['calibration_steps'] = [float(optimizer['state'][i]['step']) for i in optimizer['param_groups'][-1]['params']]
        del saved
    log_rows = []
    for path in RUN.glob('stdout_*.log'):
        for line in path.read_text(encoding='utf-8', errors='replace').splitlines():
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if row.get('stage') == 'PROGRESSIVE_RECEIVER_TRAINING' and row.get('depth') == 6:
                log_rows.append(row)
    training = {}
    for epoch in (1, 2):
        rows = [r for r in log_rows if r['epoch']==epoch]
        gradient = np.array([r['gradient_norm'] for r in rows])
        training[str(epoch)] = dict(sample_count=len(rows),
            gradient_quantiles=np.quantile(gradient, [0, .5, .9, .99, 1]).tolist(),
            fraction_over_clip_threshold=float(np.mean(gradient>1)),
            note='Every eighth step plus the first step; gradient norms are BEFORE clipping and not proof that the learning rate is too high.')
    numerical = {}
    for name in ('epoch1', 'epoch2'):
        rows = values[name]['rows']
        numerical[name] = dict(
            scenes_with_any_query_outside_pretraining_support=sum(any(d['out_of_pretraining_support'] for d in r['diagnostics']) for r in rows),
            nonfinite_final_nmse=sum(not np.isfinite(r['nmse']) for r in rows),
            layer_damped_scenes=[sum(r['diagnostics'][i]['damping']<1 for r in rows) for i in range(6)],
            layer_query_variance_median=[float(np.median([r['diagnostics'][i]['query_variance'] for r in rows])) for i in range(6)])
    cpu_check = scalar_adam_check()
    end_state = read(RUN/'STATUS.json')
    assert sha(RUN/'MANIFEST.json') == manifest_hash
    assert all(sha(path) == digest for path, digest in manifest['snapshot_hashes'].items())
    assert all(sha(item['path']) == item['sha256'] for item in inputs.values())
    assert not torch.cuda.is_initialized()
    report = dict(schema='depth6-readonly-diagnosis-v1', created_unix=time.time(),
        inputs=inputs, scene_pairing_verified=True, scene_count=1200,
        summaries=summaries, loss_decomposition=components, condition_changes=condition_rows,
        attribution=attribution, selected_checkpoint_epoch=receipt['selected_epoch'],
        selected_checkpoint_sha256_from_receipt=receipt['checkpoint_sha256'],
        checkpoint_info=checkpoint_info, sampled_training_gradients=training,
        numerical_checks=numerical, scalar_adam_check=cpu_check,
        safeguards=dict(receiver_inferences=0, receiver_optimizer_updates=0, cuda_initialized=False,
            frozen_source_hashes_unchanged=True, training_manifest_unchanged=True,
            completed_validation_files_unchanged=True, active_run_files_written=0,
            start_status={k:v for k,v in start_state.items() if k!='diagnostics'},
            end_status={k:v for k,v in end_state.items() if k!='diagnostics'}),
        limitations=['Observational completed-checkpoint comparisons do not establish learning-rate causality.',
            'No stored per-user logits or branch-specific gradients; threshold sensitivity and gradient competition were not measured.',
            'Online epoch-average training losses are not fixed-checkpoint train-set evaluations.',
            'The scalar Adam result is an update-rule check, not an attribution of receiver NMSE.',
            'No change to ongoing seven-layer training or to held-out test inputs.'])
    write(OUT/'REPORT.json', report)
    with (OUT/'condition_changes.csv').open('w', newline='', encoding='utf-8-sig') as stream:
        writer=csv.DictWriter(stream, fieldnames=list(condition_rows[0]))
        writer.writeheader();writer.writerows(condition_rows)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(14, 3.9), constrained_layout=True)
    for name, label, color in [('epoch1','After adaptation','#217a9a'),('epoch2','After joint training','#d47931')]:
        axes[0].plot(range(1,7), [r['pooled_nmse_db'] for r in components[name]['layers']], 'o-', label=label, color=color)
    axes[0].set(xlabel='Output layer', ylabel='Pooled NMSE (dB)', title='Same 1,200 validation scenes')
    axes[0].legend(fontsize=8)
    x=np.arange(3)
    axes[1].bar(x-.18, [summaries[k]['misses'] for k in ('five','epoch1','epoch2')], .36, label='Misses', color='#217a9a')
    axes[1].bar(x+.18, [summaries[k]['false_alarms'] for k in ('five','epoch1','epoch2')], .36, label='False alarms', color='#d47931')
    axes[1].set_xticks(x, ['Frozen five','Six: adaptation','Six: joint'])
    axes[1].tick_params(axis='x', labelsize=8)
    axes[1].set(title='Activity decisions at threshold 0.5', ylabel='Count');axes[1].legend(fontsize=8)
    changes=np.array([r['delta_nmse_db'] for r in condition_rows]).reshape(6,4)
    heat=axes[2].imshow(changes, aspect='auto', cmap='YlOrRd',vmin=0,vmax=.85)
    axes[2].set_xticks(range(4),[-5,0,5,10]);axes[2].set_yticks(range(6),['20 / 8 / .05','40 / 16 / .1','100 / 24 / .2','100 / 8 / .1','20 / 24 / .1','40 / 12 / .2'])
    axes[2].set(xlabel='SNR (dB)',ylabel='K / Q / activity p',title='Joint minus adaptation NMSE (dB)')
    for i in range(6):
        for j in range(4):axes[2].text(j,i,f'{changes[i,j]:+.2f}',ha='center',va='center',fontsize=8)
    fig.colorbar(heat,ax=axes[2],shrink=.75)
    for ax in axes[:2]:ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
    fig.savefig(OUT/'diagnosis.png',dpi=180)
    plt.close(fig)
    print(json.dumps(dict(output=str(OUT),attribution=attribution,scalar_adam_check=cpu_check,
                         gpu_used=False,receiver_training_started=False),ensure_ascii=False))


if __name__ == '__main__':
    main()
