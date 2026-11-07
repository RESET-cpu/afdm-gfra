"""Paired fixed-power colored denoising and a separate saved-query diagnostic."""
import argparse
import csv
import importlib.util
import json
import os
from pathlib import Path
import sys
import time
import traceback

import numpy as np
import torch
from threadpoolctl import threadpool_limits

from project import ROOT, source_files
from utils import read_json, write_json, sha256
from evaluation.denoising import clean_channels, FirstChannelMean, denoising_metrics
from evaluation.colored_denoising import PretrainedColoredFirst
from evaluation.receivers import setup
from evaluation.append_colored_denoising_20261025 import publish_progress
from system.observation import array_sha256
from training.colored_score_20261024.noise import Covariance
from training.colored_preconditioned_20261024.operators import Spectral

CONFIG = ROOT/'src/configs/experiments/colored_denoising_20261025.json'
HELPER = ROOT/'result/channel_denoising/data/actual_query_denoising_refresh_20261024/run.py'
SOURCE = ROOT/'result/snr_comparison/data/low_snr_query_check_20261024'
METHODS = ('noisy', 'old_white', 'new_identity', 'new_covariance')
LABELS = ('Noisy input', 'Old score, vI', 'New network, vI', 'New network, C')
STAGES = ('iteration001', 'iteration020', 'final')


def factor_bases(seed, batch, size=16, rank=4):
    rng = np.random.default_rng(seed)
    result = []
    for _ in range(2):
        g = (rng.normal(size=(batch, size, rank))+1j*rng.normal(size=(batch, size, rank)))/np.sqrt(2)
        gram = g @ g.conj().transpose(0, 2, 1)
        result.append(gram*(size/np.trace(gram, axis1=-2, axis2=-1).real)[:, None, None])
    return result


def root_factor(matrix):
    values, vectors = np.linalg.eigh(matrix)
    if not np.all(values > 0):
        raise ValueError('Nonpositive covariance eigenvalue')
    return (vectors*np.sqrt(values)[:, None, :]) @ vectors.conj().transpose(0, 2, 1)


def colored_noise(epsilon, bases, strength):
    """Complex covariance in C-order is Ra kron I_output kron Rc."""
    ra, rc = [(1-strength)*np.eye(g.shape[-1])+strength*g for g in bases]
    if strength == 0:
        return epsilon.copy(), ra, rc
    noise = np.einsum('baj,bjok,bik->baoi', root_factor(ra), epsilon, root_factor(rc), optimize=True)
    return noise, ra, rc


@torch.inference_mode()
def infer_covariance(adapter, query, variance, ra, rc):
    """Only query and declared/estimated C enter inference, never channel truth."""
    variance = np.broadcast_to(np.asarray(variance, float), (len(query),))
    outputs = []
    for start in range(0, len(query), adapter.batch_size):
        end = min(start+adapter.batch_size, len(query))
        q = query[start:end]
        x = torch.as_tensor(np.stack((q.real, q.imag), 1)*adapter.scale_ratio,
                            dtype=torch.float32, device=adapter.device)
        cov = Covariance(torch.as_tensor(variance[start:end]*adapter.scale_ratio**2, dtype=x.dtype, device=x.device),
                         torch.tensor(ra[start:end], dtype=torch.complex64, device=x.device),
                         torch.tensor(rc[start:end], dtype=torch.complex64, device=x.device))
        value = adapter.network(x, cov, Spectral.from_covariance(cov)).cpu().numpy().astype(float)
        outputs.append((value[:, 0]+1j*value[:, 1])/adapter.scale_ratio)
    return np.concatenate(outputs)


def predictions(old, new, query, variance, ra, rc, identity=False):
    plain = new.infer(query, variance, priors=None)[0]
    return (query, old.infer(query, variance).mean, plain,
            plain.copy() if identity else infer_covariance(new, query, variance, ra, rc))


def receiver_helper():
    spec = importlib.util.spec_from_file_location('saved_query_covariance_helper', HELPER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prepare(out, cfg, scenes, cases, device):
    if out.exists():
        raise FileExistsError('Preserve existing batches; choose a new directory')
    binding = read_json(ROOT/cfg['binding'])
    if sha256(ROOT/cfg['first_checkpoint']) != cfg['first_checkpoint_sha256']:
        raise ValueError('Candidate checkpoint identity changed')
    if sha256(ROOT/binding['first_checkpoint']) != binding['first_checkpoint_sha256']:
        raise ValueError('Old checkpoint identity changed')
    prior = read_json(ROOT/binding['prior_definition'])
    seeds = set(range(cfg['base_seed'], cfg['base_seed']+scenes))
    for split in ('train', 'validation'):
        if seeds.intersection(prior['dataset_identities'][split]['scene_seeds']):
            raise ValueError('Evaluation scene overlaps a training or validation scene')
    helper = receiver_helper()
    source_plan = read_json(SOURCE/'PLAN.json')
    paths = set(source_files()) | {CONFIG, HELPER, SOURCE/'PLAN.json', ROOT/cfg['binding'],
        ROOT/cfg['first_checkpoint'], ROOT/binding['first_checkpoint'], ROOT/binding['prior_definition'],
        ROOT/'FINAL.json', ROOT/'MAINLINE.json',
        ROOT/'src/tests/test_colored_noise_experiment_20261025.py',
        ROOT/'result/snr_comparison/data/linear_covariance_interface_20261024/benchmark.py',
        ROOT/'result/snr_comparison/data/linear_covariance_interface_20261024/audit.py',
        ROOT/'paper/docs/COLORED_COVARIANCE_RELATIVE_CHECK_20261024.md'}
    plan = dict(configuration=cfg, binding=binding, scenes=scenes, receiver_cases=cases,
        device=device, methods=METHODS, scale=binding['scale'], batch_size=cfg['batch_size'],
        figure_output=str(ROOT/'result/channel_denoising/figures'/out.name),
        mode='FORMAL' if scenes == cfg['scenes'] and cases == cfg['receiver_cases'] else 'PREFLIGHT',
        authorization='2026-10-25 user: 可以，请你开始跑吧; accepted colored-noise and saved-query comparisons.',
        assets={str(p.relative_to(ROOT)): sha256(p) for p in sorted(paths)},
        receiver_configuration=source_plan['configuration'], cases=source_plan['cases'][:cases],
        test_scene_overlap_with_training_or_validation=0,
        noise_scope='Known synthetic covariance; family motivated by prior receiver-error diagnostics, not measured hardware noise. Independent covariance/base-noise draws; no per-realization noise normalization.',
        receiver_scope='Reuse 12 uniform and 12 failure-enriched diagnostic scenes separately, -4/0 dB. C=v*I_antenna kron I_output kron Rc. Normalize Rc to trace/d=1 and use the SAME original scalar v in all branches; no truth for C or inference. No feedback.',
        statistics='Pooled NMSE, sum errors / sum truth energies. Four candidates share a physical scene. Point estimates only; no significance or independent confirmation claims.')
    out.mkdir(parents=True)
    write_json(out/'PLAN.json', plan)
    for p in sorted(paths):
        if p.suffix == '.py' or p == CONFIG:
            dest = out/'source'/p.relative_to(ROOT)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(p.read_bytes())
    return plan, helper


def save_receipt(path, arrays, metadata):
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, **arrays)
    write_json(path.with_suffix('.json'), dict(**metadata, compact_sha256=sha256(path), status='COMPLETE'))


def verify_receipts(out, folder, count):
    paths = sorted((out/folder).glob('*.npz'))
    if len(paths) != count:
        raise ValueError('Incomplete output count: '+folder)
    for path in paths:
        if sha256(path) != read_json(path.with_suffix('.json'))['compact_sha256']:
            raise ValueError('Output receipt mismatch')


def write_csv(path, rows):
    with path.open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def plot_results(out, synth, receiver, strengths, mode):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family': 'serif', 'font.size': 10, 'pdf.fonttype': 42})
    styles = [dict(color='#888888', marker='x', ls=':'), dict(color='#bd2626', marker='o'),
              dict(color='#da8c00', marker='s', ls='--'), dict(color='#145eb0', marker='^')]
    fig, axes = plt.subplots(1, len(strengths), figsize=(10.2, 3.5), sharey=True)
    for ax, alpha in zip(axes, strengths):
        for method, label, style in zip(METHODS, LABELS, styles):
            rows = [r for r in synth if r['strength']==alpha and r['method']==method]
            ax.plot([r['snr_db'] for r in rows], [r['nmse_db'] for r in rows], label=label,
                    markersize=5, markerfacecolor='none', **style)
        ax.set(title=f'Correlation parameter alpha = {alpha:g}', xlabel='Nominal denoising SNR (dB)')
        ax.grid(True, ls=':', alpha=.5)
        ax.set_xticks([-20, -10, 0, 10, 20, 30])
    axes[0].set_ylabel('NMSE (dB)')
    fig.legend(*axes[0].get_legend_handles_labels(), loc='lower center', ncol=4, bbox_to_anchor=(.5, -.015))
    fig.suptitle(f'{mode}: synthetic Gaussian noise, known covariance, equal average power', fontsize=11)
    fig.tight_layout(rect=[0, .07, 1, .93])
    for suffix in ('png', 'pdf', 'svg'):
        fig.savefig(out/f'colored_denoising.{suffix}', dpi=300, bbox_inches='tight')
    plt.close(fig)
    if receiver:
        fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.5), sharey=True)
        for ax, snr in zip(axes, (-4, 0)):
            for method, label, style in zip(METHODS[1:], LABELS[1:], styles[1:]):
                rows = [r for r in receiver if r['group']=='uniform' and r['snr_db']==snr and r['method']==method]
                if rows:
                    ax.plot([r['stage'] for r in rows], [r['nmse_db'] for r in rows], label=label,
                            markersize=5, markerfacecolor='none', **style)
            ax.set(title=f'Receiver SNR = {snr} dB', xlabel='Saved receiver stage')
            ax.grid(True, ls=':', alpha=.5)
        axes[0].set_ylabel('Active-user NMSE (dB)')
        fig.legend(*axes[0].get_legend_handles_labels(), loc='lower center', ncol=3, bbox_to_anchor=(.5, -.015))
        fig.suptitle(f'{mode}: reused uniform diagnostic scenes, estimated C, equal power', fontsize=10)
        fig.tight_layout(rect=[0, .07, 1, .93])
        for suffix in ('png', 'pdf', 'svg'):
            fig.savefig(out/f'receiver_queries.{suffix}', dpi=300, bbox_inches='tight')
        plt.close(fig)


def run(out, cfg, scenes, cases, device):
    started = time.monotonic()
    plan, helper = prepare(out, cfg, scenes, cases, device)
    def progress(stage, done, total, **extra):
        status = dict(status='RUNNING', stage=stage, pid=os.getpid(), completed=done, total=total,
                      elapsed_seconds=time.monotonic()-started, **extra)
        publish_progress(out/'STATUS.json', status)
        if done % 10 == 0 or done == total or done == 1:
            print(json.dumps(status), flush=True)
        if time.monotonic()-started > cfg['hard_timeout_seconds']:
            raise TimeoutError('Declared hard timeout reached')
    try:
        progress('loading', 0, 1)
        setup(device)
        binding = plan['binding']
        old = FirstChannelMean(plan['scale'], ROOT/binding['first_checkpoint'], device=device, batch_size=cfg['batch_size'])
        new = PretrainedColoredFirst(binding, ROOT/cfg['first_checkpoint'], cfg['first_checkpoint_sha256'],
                                     device=device, batch_size=cfg['batch_size'])
        errors = np.zeros((scenes, len(cfg['strengths']), len(cfg['snr_db']), len(METHODS), cfg['candidates']))
        energy = np.zeros((scenes, cfg['candidates']))
        identity_check = None
        for scene in range(scenes):
            seed = cfg['base_seed']+scene
            clean, users = clean_channels(seed, cfg['users'], cfg['candidates'])
            truth = clean/plan['scale']
            rng = np.random.default_rng(np.random.SeedSequence([seed, 8240]))
            epsilon = (rng.normal(size=truth.shape)+1j*rng.normal(size=truth.shape))/np.sqrt(2)
            bases = factor_bases(np.random.SeedSequence([cfg['shape_seed'], scene]), len(truth), rank=cfg['rank'])
            receipts = []
            examples = {}
            for ai, alpha in enumerate(cfg['strengths']):
                noise, ra, rc = colored_noise(epsilon, bases, alpha)
                np.testing.assert_allclose(np.trace(ra, axis1=-2, axis2=-1), 16, atol=1e-12)
                np.testing.assert_allclose(np.trace(rc, axis1=-2, axis2=-1), 16, atol=1e-12)
                for si, snr in enumerate(cfg['snr_db']):
                    variance = 10.**(-snr/10)
                    query = truth+np.sqrt(variance)*noise
                    output = predictions(old, new, query, variance, ra, rc, identity=alpha==0)
                    if scene==0 and alpha==0 and snr==0:
                        alternate = infer_covariance(new, query, variance, ra, rc)
                        np.testing.assert_allclose(alternate, output[2], rtol=1e-5, atol=1e-5)
                        repeat = infer_covariance(new, query, variance, ra, rc)
                        np.testing.assert_array_equal(alternate, repeat)
                        identity_check = dict(max_abs=float(np.max(abs(alternate-output[2]))), repeat_bitwise_equal=True)
                    for mi, mean in enumerate(output):
                        metric = denoising_metrics(mean, truth)
                        errors[scene, ai, si, mi] = metric['error']
                        energy[scene] = metric['energy']
                    receipts.append(dict(strength=alpha, snr_db=snr, variance=variance,
                        query_sha256=array_sha256(query), ra_sha256=array_sha256(ra), rc_sha256=array_sha256(rc),
                        realized_noise_power=float(np.mean(abs(query-truth)**2))))
                    if scene == 0:
                        examples[f'a{ai}_s{si}_query'] = query
                        examples[f'a{ai}_s{si}_means'] = np.stack(output[1:])
                if scene == 0:
                    examples[f'a{ai}_ra'], examples[f'a{ai}_rc'] = ra, rc
            save_receipt(out/'synthetic'/f'scene{scene:04d}.npz', dict(error=errors[scene], energy=energy[scene]),
                dict(scene=scene, seed=seed, users=users.tolist(), inputs=receipts,
                     truth_sha256=array_sha256(truth), epsilon_sha256=array_sha256(epsilon)))
            if scene == 0:
                np.savez_compressed(out/'synthetic_scene0000.npz', truth=truth, epsilon=epsilon, **examples)
            progress('synthetic', scene+1, scenes)
        synth = []
        for ai, alpha in enumerate(cfg['strengths']):
            for si, snr in enumerate(cfg['snr_db']):
                for mi, method in enumerate(METHODS):
                    err = float(errors[:, ai, si, mi].sum()); signal = float(energy.sum())
                    synth.append(dict(strength=alpha, snr_db=snr, method=method, scenes=scenes,
                        samples=scenes*cfg['candidates'], error=err, energy=signal, nmse_db=float(10*np.log10(err/signal))))
        write_csv(out/'SYNTHETIC.csv', synth)
        write_json(out/'SYNTHETIC.json', synth)
        # Preserve the batch shape used by the saved receiver trajectory.
        old.batch_size = new.batch_size = cfg['receiver_batch_size']
        receiver_rows, checks = [], []
        for ci, case in enumerate(plan['cases']):
            folder, covs, check = helper.reconstruct(case, plan['receiver_configuration'])
            predicted = {}
            inputs = []
            with np.load(folder/'QUERIES.npz', allow_pickle=False) as z:
                for stage in STAGES:
                    query, variance = z[stage+'_query'], z[stage+'_variance']
                    _, rc, _, _, iteration = covs[stage]
                    rc = rc/(np.trace(rc, axis1=-2, axis2=-1).real/16)[:, None, None]
                    ra = np.broadcast_to(np.eye(16), rc.shape)
                    if np.any((variance < .001) | (variance > 100)):
                        raise ValueError('Receiver query outside network variance support')
                    output = predictions(old, new, query, variance, ra, rc)
                    if ci == 0:
                        saved = z[stage+'_first_mean']
                        relative = float(np.linalg.norm(output[1]-saved)/np.linalg.norm(saved))
                        if relative > 2e-5:
                            raise ValueError('Old saved-query mean reproduction failed')
                        check[stage+'_old_mean_relative_error'] = relative
                    predicted[stage] = output
                    inputs.append(dict(stage=stage, iteration=iteration, query_sha256=array_sha256(query),
                        variance_sha256=array_sha256(variance), rc_sha256=array_sha256(rc)))
                # Targets and activity labels are accessed only after all inference.
                truth, active = z['true_normalized_channel'], z['truth_activity'].astype(bool)
                signals = np.sum(abs(truth)**2, axis=(1, 2, 3))
                if not np.all(signals[~active] == 0):
                    raise ValueError('Inactive receiver target must be zero')
                per_case = []
                for stage in STAGES:
                    err = np.stack([denoising_metrics(mean, truth)['error'] for mean in predicted[stage]])
                    per_case.append(err)
                    for mi, method in enumerate(METHODS):
                        receiver_rows.append(dict(scene=case['scene'], group=case['group'], snr_db=case['snr_db'],
                            stage=stage, method=method, error=float(err[mi, active].sum()), energy=float(signals[active].sum()),
                            active_users=int(active.sum()), inactive_users=int((~active).sum()),
                            inactive_error=float(err[mi, ~active].sum())))
                save_receipt(out/'receiver'/f'case{ci:03d}.npz', dict(error=np.stack(per_case), energy=signals, active=active),
                             dict(scene=case['scene'], condition=case['condition'], inputs=inputs, check=check))
            checks.append(check)
            progress('receiver_queries', ci+1, cases)
        receiver = []
        for group in ('uniform', 'failure_enriched'):
            for snr in (-4, 0):
                for stage in STAGES:
                    for method in METHODS:
                        rows = [r for r in receiver_rows if (r['group'], r['snr_db'], r['stage'], r['method']) == (group, snr, stage, method)]
                        if not rows:
                            continue
                        err, sig = sum(r['error'] for r in rows), sum(r['energy'] for r in rows)
                        inactive = sum(r['inactive_users'] for r in rows)
                        receiver.append(dict(group=group, snr_db=snr, stage=stage, method=method, scenes=len(rows),
                            error=err, energy=sig, nmse_db=float(10*np.log10(err/sig)),
                            inactive_output_power=sum(r['inactive_error'] for r in rows)/(4096*inactive)))
        write_json(out/'RECEIVER_ROWS.json', receiver_rows)
        write_json(out/'RECEIVER.json', receiver)
        write_csv(out/'RECEIVER.csv', receiver)
        verify_receipts(out, 'synthetic', scenes)
        verify_receipts(out, 'receiver', cases)
        for name, digest in plan['assets'].items():
            if sha256(ROOT/name) != digest:
                raise ValueError('Bound asset changed: '+name)
        figure_output = Path(plan['figure_output'])
        figure_output.mkdir(parents=True, exist_ok=False)
        plot_results(figure_output, synth, receiver, cfg['strengths'], plan['mode'])
        write_json(out/'VERIFICATION.json', dict(status='PASS', mode=plan['mode'], scenes=scenes,
            synthetic_conditions=scenes*len(cfg['strengths'])*len(cfg['snr_db']), receiver_cases=cases,
            receiver_stages=cases*3, excluded_samples=0, identity_covariance_check=identity_check,
            source_weight_binding_hashes_unchanged=True, all_receipts_verified=True, finite_outputs=True,
            receiver_truth_used_for_inference=False, covariance_checks=checks,
            plan_sha256=sha256(out/'PLAN.json'), synthetic_sha256=sha256(out/'SYNTHETIC.json'),
            receiver_sha256=sha256(out/'RECEIVER.json')))
        report = ['# 有色噪声与接收机输入去噪实验', '', '## Material Passport',
                  '- origin_skill: academic-research-suite / experiment-agent', '- origin_mode: run',
                  '- origin_date: 2026-10-25', '- verification_status: ANALYZED', '',
                  f"状态：{plan['mode']} 完成。{scenes} 个物理场景，6 档 SNR，3 档相关强度；{cases} 组已保存接收机条件。", '',
                  '旧、新一阶网络均固定 epoch 200；无二阶网络、活动分类器或输出反馈。',
                  '合成实验的 C 已知，族结构有接收机误差诊断依据，但随机形状分布不是实测或精确接收机误差分布。',
                  '所有方法使用相同输入和平均噪声功率。alpha 是两因子的混合参数，不等同于固定的相关系数。',
                  '接收机 C 的列相关形状来自公开导频、噪声估计和保存轨迹，按同一原始标量 v 归一；与先前每用户功率 C 的比较不同。',
                  '接收机样本是重复使用的开发诊断集；均匀与失败富集分开，不宣称独立确认、闭环改善或显著性。', '',
                  f'[合成有色去噪图](../../figures/{out.name}/colored_denoising.png) · [接收机输入图](../../figures/{out.name}/receiver_queries.png)', '',
                  '| alpha | SNR | 旧网络 | 新 vI | 新 C | 新 C − 新 vI |', '|---:|---:|---:|---:|---:|---:|']
        for alpha in cfg['strengths']:
            for snr in cfg['snr_db']:
                values = {r['method']: r['nmse_db'] for r in synth if r['strength']==alpha and r['snr_db']==snr}
                report.append(f"| {alpha:g} | {snr} | {values['old_white']:.3f} | {values['new_identity']:.3f} | {values['new_covariance']:.3f} | {values['new_covariance']-values['new_identity']:+.3f} |")
        (out/'REPORT.md').write_text('\n'.join(report)+'\n', encoding='utf-8')
        publish_progress(out/'STATUS.json', dict(status='COMPLETE', mode=plan['mode'], scenes=scenes,
            receiver_cases=cases, elapsed_seconds=time.monotonic()-started))
    except BaseException:
        write_json(out/'FAILURE.json', dict(traceback=traceback.format_exc(), elapsed_seconds=time.monotonic()-started))
        publish_progress(out/'STATUS.json', dict(status='FAILED', details='FAILURE.json; no automatic retry'))
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--scenes', type=int, default=1000, choices=(1, 1000))
    parser.add_argument('--receiver-cases', type=int, default=48, choices=(1, 48))
    parser.add_argument('--device', default='cuda', choices=('cuda', 'cpu'))
    args = parser.parse_args()
    with threadpool_limits(1):
        run(args.output.resolve(), read_json(CONFIG), args.scenes, args.receiver_cases, args.device)
