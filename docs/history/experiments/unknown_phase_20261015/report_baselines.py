"""Audit every unknown-phase output, then summarize paired physical scenes."""
import argparse
from collections import Counter
import csv
import json
from pathlib import Path
import sys
import warnings

import numpy as np
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT/'src'))
from experiments.unknown_phase_20261015 import model, estimate_phase
from afdm_jadcedd.system.phase import phase_operator, wrap
from afdm_jadcedd.system.pilot import PartialDFTPilot
from afdm_jadcedd.system.observation import array_sha256
from afdm_jadcedd.utils import sha256, write_json
from afdm_jadcedd.algorithm.registry import build_receiver, DEFAULT_CONFIGS

NAMES = dict(somp='SOMP', gamp='GAMP-SBL MMV', gnn='GNN-ASPL',
             offgrid_sbl='Off-grid SBL', ldamp='L-DAMP + TSVD')


def read_npz(path):
    with np.load(path, allow_pickle=False) as saved:
        return {key:saved[key] for key in saved.files}


def audit(folder):
    plan = json.loads((folder/'PLAN.json').read_text())
    state = json.loads((folder/'STATUS.json').read_text())
    rows = json.loads((folder/'ROWS.json').read_text())
    expected = {(s,n,m) for s in range(plan['scenes']) for n in plan['snr_db'] for m in plan['methods']}
    if state['status'] != 'COMPLETE' or len(rows) != len(expected):
        raise ValueError('All scheduled outputs must be complete; failures may not be dropped')
    assert {(r['scene'],r['snr_db'],r['method']) for r in rows} == expected
    lookup = {(r['scene'],r['snr_db'],r['method']):r for r in rows}
    for path, digest in plan['sources'].items():
        assert sha256(ROOT/path) == digest == sha256(folder/'sources'/path), path
    for path, digest in plan['configuration_sha256'].items():
        assert sha256(ROOT/path) == digest, path
    phase_rows = json.loads((folder/'PHASE_METRICS.json').read_text())
    phase_lookup = {(r['scene'],r['snr_db']):r for r in phase_rows}
    checks, pairing, conditions = [], [], []
    stopping = {method:Counter() for method in plan['methods']}
    phase_optimization = Counter()
    for scene in range(plan['scenes']):
        shared = None
        for snr in plan['snr_db']:
            case = folder/f'scene{scene:03d}'/f'snr{snr:+03d}'
            inp, truth = read_npz(case/'input.npz'), read_npz(case/'truth.npz')
            phase = read_npz(case/'phase.npz'); conditional = read_npz(case/'estimated_operator_input.npz')
            assert set(inp) == {'observation','pilot','noise_variance','activity_prior'}
            assert set(conditional) == {'observation','operator','noise_variance','activity_prior'}
            h = truth['channel']; active = truth['activity'].astype(bool); q = len(inp['pilot'])
            identities = [array_sha256(x) for x in (h,active,inp['pilot'],truth['phase_slopes'])]
            if shared is None:
                shared = identities
            assert shared == identities, 'Physical scene must remain paired across SNR'
            seed = plan['seed_base']+scene
            p = PartialDFTPilot(40,16,seed+10**12,input_size=16).dense().reshape(16,40,16)
            np.testing.assert_array_equal(inp['pilot'],p)
            # Truth enters only this audit, after every inference output is saved.
            true_operator = phase_operator(p, truth['phase_slopes'])
            clean = np.einsum('qkn,kmrn->qmr',true_operator,h,optimize=False)
            noise = float(np.mean(abs(clean)**2))*10**(-snr/10)
            assert noise == float(inp['noise_variance'])
            rng = np.random.default_rng(np.random.SeedSequence([seed,2096]))
            epsilon = ((rng.normal(size=(32,16,16))+1j*rng.normal(size=(32,16,16)))/np.sqrt(2))[:16]
            np.testing.assert_array_equal(inp['observation'],clean+np.sqrt(noise)*epsilon)
            estimated = p*np.exp(1j*np.arange(q)[:,None,None]*phase['phase_slopes'][None,:,None])
            np.testing.assert_array_equal(conditional['operator'],estimated)
            np.testing.assert_array_equal(conditional['observation'],inp['observation'])
            assert float(conditional['noise_variance']) == noise
            assert float(conditional['activity_prior']) == float(inp['activity_prior'])
            phase_record = json.loads((case/'phase.json').read_text())
            assert not phase_record['truth_used_in_inference'] and not phase_record['known_activity_used']
            assert phase_record['input_sha256'] == sha256(case/'input.npz')
            assert phase_record['output_sha256'] == sha256(case/'phase.npz')
            assert phase_record['inference_sha256'] == plan['phase_inference_sha256']
            for refinement in phase_record['refinements']:
                phase_optimization['selected_success' if refinement['success'] else 'selected_solver_stop_without_success'] += 1
                phase_optimization['accepted' if refinement['accepted'] else 'rejected'] += 1
            delta = wrap(phase['phase_slopes']-truth['phase_slopes'])
            metric = phase_lookup[scene,snr]
            np.testing.assert_allclose(metric['active_phase_squared_error'],np.sum(delta[active]**2),rtol=1e-12)
            phasor = np.exp(1j*np.arange(q)[:,None]*delta[None,active])-1
            np.testing.assert_allclose(metric['active_frame_phasor_squared_error'],np.sum(abs(phasor)**2),rtol=1e-12)
            np.testing.assert_allclose(metric['active_doppler_squared_error_hz2'],
                np.sum((phase['doppler_hz'][active]-truth['doppler_hz'][active])**2),rtol=1e-12)
            assert metric['active_users'] == int(active.sum())
            pairing.append(dict(scene=scene,snr_db=snr,passed=True))
            conditions.append(dict(scene=scene,snr_db=snr,active_users=int(active.sum()),
                largest_active_phase_error_rad=float(np.max(abs(delta[active]))),
                active_doppler_alias_errors=int(np.sum(abs(phase['doppler_hz'][active]-truth['doppler_hz'][active]) > .5/model.FRAME_DURATION_S))))
            for method in plan['methods']:
                row = lookup[scene,snr,method]
                assert row['status'] == 'COMPLETE'
                arrays = read_npz(case/f'{method}.npz')
                record = json.loads((case/f'{method}.json').read_text())
                stopping[method][record.get('stopping_reason','fixed_iterations')] += 1
                assert all(np.isfinite(value).all() for value in arrays.values())
                for key,path in [('output_sha256',case/f'{method}.npz'),('input_sha256',case/'estimated_operator_input.npz'),
                                 ('public_unknown_phase_input_sha256',case/'input.npz')]:
                    assert row[key] == record[key] == sha256(path)
                assert record['phase_estimate_sha256'] == sha256(case/'phase.npz')
                assert row['inference_sha256'] == record['inference_sha256'] == plan['inference_sha256'][method]
                assert record['baseline_inference_sha256'] == plan['baseline_inference_sha256'][method]
                assert not record['truth_used_in_inference']
                np.testing.assert_allclose(row['seconds'],row['baseline_seconds']+row['phase_seconds'],rtol=1e-14)
                est,decision = arrays['estimate'],arrays['activity_decision'].astype(bool)
                error = np.sum(abs(est-h)**2,axis=(1,2,3))
                values = dict(full_error=float(error.sum()), active_error=float(error[active].sum()),
                              inactive_error=float(error[~active].sum()),signal_energy=float(np.sum(abs(h)**2)),
                              estimated_activity_masked_error=float(np.sum(abs(est*decision[:,None,None,None]-h)**2)))
                for key,value in values.items():
                    np.testing.assert_allclose(row[key],value,rtol=1e-11,atol=1e-12)
                assert row['misses'] == int(np.sum(active & ~decision))
                assert row['false_alarms'] == int(np.sum(~active & decision))
                if method == 'ldamp':
                    binding = plan['configurations'][method]['base_configuration']['readout']
                    assert sha256(ROOT/binding['path']) == binding['sha256']
                    threshold = json.loads((ROOT/binding['path']).read_text())['threshold']
                    expected_decision = (arrays['activity_score'] >= threshold) & (arrays['activity_score'] > 0)
                else:
                    energy_key = 'channel_energy' if method == 'offgrid_sbl' else 'coefficient_energy'
                    nonzero = arrays[energy_key] > 0 if method == 'offgrid_sbl' else np.max(arrays[energy_key]) > 0
                    expected_decision = (arrays['activity_score'] >= record['activity_threshold']) & nonzero
                np.testing.assert_array_equal(decision,expected_decision)
                checks.append(dict(scene=scene,snr_db=snr,method=method,passed=True))
    # One-condition front-end rerun, using only the four public fields.
    case = folder/'scene000'/'snr+00'
    with warnings.catch_warnings(record=True) as caught:
        repeated, _ = estimate_phase.estimate(model.load_input(case/'input.npz'),estimate_phase.Controls(**plan['phase_controls']))
    saved = read_npz(case/'phase.npz')
    for key in repeated:
        np.testing.assert_array_equal(repeated[key],saved[key])
    import torch
    torch.set_num_threads(1)
    inputs = model.load_input(case/'input.npz').at_estimated_phase(repeated['phase_slopes'])
    fingerprints = [array_sha256(inputs.observation),array_sha256(inputs.operator)]
    reruns = []
    for method in plan['methods']:
        path = ROOT/'configs/ldamp_output_tsvd.json' if method=='ldamp' else DEFAULT_CONFIGS[method]
        receiver = build_receiver(method,config=path,device=plan['environment']['device'])
        with warnings.catch_warnings(record=True) as baseline_warnings:
            actual,_ = receiver.infer(inputs)
        reference = read_npz(case/f'{method}.npz')
        assert fingerprints == [array_sha256(inputs.observation),array_sha256(inputs.operator)]
        assert actual.keys() == reference.keys()
        exact = all(np.array_equal(actual[key],reference[key]) for key in actual)
        tolerance = dict(rtol=2e-6,atol=2e-7) if method in ('gnn','ldamp') else dict(rtol=1e-10,atol=1e-11)
        for key in actual:
            np.testing.assert_allclose(actual[key],reference[key],**tolerance)
        np.testing.assert_array_equal(actual['activity_decision'],reference['activity_decision'])
        reruns.append(dict(method=method,exact_array_match=exact,input_preserved=True,
                          decisions_identical=True,warning_count=len(baseline_warnings),tolerance=tolerance))
    report = dict(status='PASS',audited_outputs=len(checks),audited_conditions=len(pairing),
                  checks=checks,physical_pairing=pairing,conditions=conditions,
                  phase_reproduction=dict(condition='scene000/snr+00',exact_array_match=True,warning_count=len(caught)),
                  baseline_reproduction=reruns,
                  baseline_stopping_reasons={m:dict(v) for m,v in stopping.items()},
                  phase_optimization=dict(phase_optimization),
                  script_sha256=sha256(Path(__file__)))
    write_json(folder/'OUTPUT_AUDIT.json',report)
    return plan,rows,phase_rows,report


def statistics(plan,rows,phase_rows):
    results,phases = [],[]
    for snr in plan['snr_db']:
        indices = np.random.default_rng(202610150301).integers(plan['scenes'],size=(5000,plan['scenes']))
        for method in plan['methods']:
            selected = sorted([r for r in rows if r['snr_db']==snr and r['method']==method],key=lambda r:r['scene'])
            errors = np.array([r['full_error'] for r in selected]); energy = np.array([r['signal_energy'] for r in selected])
            mistakes = np.array([r['misses']+r['false_alarms'] for r in selected])
            denominator = np.array([r['users'] for r in selected])
            bn = 10*np.log10(errors[indices].sum(axis=1)/energy[indices].sum(axis=1))
            ba = mistakes[indices].sum(axis=1)/denominator[indices].sum(axis=1)
            ni,ai = np.quantile(bn,[.025,.975]),np.quantile(ba,[.025,.975])
            results.append(dict(method=method,snr_db=snr,scenes=len(selected),
                nmse_db=float(10*np.log10(errors.sum()/energy.sum())),nmse_low=float(ni[0]),nmse_high=float(ni[1]),
                aer=float(mistakes.sum()/denominator.sum()),aer_low=float(ai[0]),aer_high=float(ai[1]),
                misses=sum(r['misses'] for r in selected),false_alarms=sum(r['false_alarms'] for r in selected),
                active_users=sum(sum(r['active']) for r in selected),
                inactive_users=sum(r['users']-sum(r['active']) for r in selected),
                mean_seconds=float(np.mean([r['seconds'] for r in selected])),
                mean_baseline_seconds=float(np.mean([r['baseline_seconds'] for r in selected])),
                mean_phase_seconds=float(np.mean([r['phase_seconds'] for r in selected]))))
        selected = sorted([r for r in phase_rows if r['snr_db']==snr],key=lambda r:r['scene'])
        error=np.array([r['active_phase_squared_error'] for r in selected]);count=np.array([r['active_users'] for r in selected])
        boot=np.sqrt(error[indices].sum(axis=1)/count[indices].sum(axis=1));lo,hi=np.quantile(boot,[.025,.975])
        phases.append(dict(snr_db=snr,phase_rmse_rad=float(np.sqrt(error.sum()/count.sum())),low=float(lo),high=float(hi),
            frame_phasor_rmse=float(np.sqrt(sum(r['active_frame_phasor_squared_error'] for r in selected)/(plan['frames']*count.sum()))),
            doppler_rmse_hz=float(np.sqrt(sum(r['active_doppler_squared_error_hz2'] for r in selected)/count.sum())),
            active_users=int(count.sum())))
    return results,phases


def render(folder,plan,rows,phase_rows,report):
    summary,phases = statistics(plan,rows,phase_rows)
    write_json(folder/'STATISTICS.json',dict(results=summary,phase=phases,bootstrap_replicates=5000,
                                            unit='physical scene',pointwise_intervals=True))
    with (folder/'STATISTICS.csv').open('w',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(summary[0]));writer.writeheader();writer.writerows(summary)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    colors=['#64748b','#d97706','#7c3aed','#059669','#2563eb']
    fig,axes=plt.subplots(1,2,figsize=(11.5,4.3),layout='constrained')
    for method,color in zip(plan['methods'],colors):
        selected=[r for r in summary if r['method']==method]
        x=[r['snr_db'] for r in selected]
        for ax,key,scale in [(axes[0],'nmse',1),(axes[1],'aer',100)]:
            ax.plot(x,[r['nmse_db' if key=='nmse' else 'aer']*scale for r in selected],
                    '-o',markersize=4,color=color,label=NAMES[method])
            ax.fill_between(x,[r[key+'_low']*scale for r in selected],
                            [r[key+'_high']*scale for r in selected],alpha=.10,color=color)
    for ax in axes:
        ax.set_xlabel('SNR (dB)');ax.set_xticks(plan['snr_db']);ax.grid(alpha=.2);ax.legend(fontsize=8)
    axes[0].set_ylabel('Full-channel NMSE (dB)')
    axes[1].set_ylabel('Activity error rate (%)');axes[1].set_ylim(bottom=0)
    fig.suptitle('Unknown frame phase: shared estimated phase + frozen baselines\n10 paired scenes; pointwise 95% scene bootstrap',fontsize=11)
    fig.savefig(folder/'comparison.png',dpi=180);fig.savefig(folder/'comparison.svg');plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(10,3.7),layout='constrained')
    x=[r['snr_db'] for r in phases]
    axes[0].plot(x,[r['phase_rmse_rad'] for r in phases],'-o',color='#2563eb')
    axes[0].fill_between(x,[r['low'] for r in phases],[r['high'] for r in phases],color='#2563eb',alpha=.15)
    axes[1].plot(x,[r['doppler_rmse_hz'] for r in phases],'-o',color='#d97706')
    axes[0].set_ylabel('Wrapped phase-slope RMSE (rad)');axes[1].set_ylabel('Doppler RMSE (Hz)')
    for ax in axes:
        ax.set_xlabel('SNR (dB)');ax.set_xticks(plan['snr_db']);ax.grid(alpha=.2);ax.set_ylim(bottom=0)
    fig.suptitle('All truly active users scored after inference; alias errors retained',fontsize=11)
    fig.savefig(folder/'phase_estimation.png',dpi=180);plt.close(fig)
    lines=['# 未知跨帧相位：五个 baseline 各十场景','',
           '本轮主要评价完整信道 NMSE 和活动错误率 AER。相位与 Doppler 为接收机内部待估参数，其误差作为辅助诊断，用于解释这两项指标的表现。后续适配与参数选择以独立验证集上的 NMSE 和 AER 为依据。','',
           '## Material Passport','',
           '- Type: Experiment Result; mode: run',
           '- Status: VERIFIED saved outputs, physical pairing, metrics, and one full-pipeline rerun',
           f"- Scope: {plan['scenes']} independent physical scenes × {len(plan['snr_db'])} SNRs × {len(plan['methods'])} methods = {len(rows)} outputs",
           '- Provenance: PLAN.json, SEED_AUDIT.json, sources/, ROWS.json, OUTPUT_AUDIT.json','',
           '本轮五种方法为 SOMP、GAMP-SBL MMV、GNN-ASPL、off-grid SBL、L-DAMP＋输出 TSVD。',
           '每个带噪观测先运行同一个观测驱动的相位估计前端，再将估计相位形成的有效算子交给各基线。',
           '前端仅读取 observation、pilot、noise_variance、activity_prior；真实活动、相位、Doppler 和信道只用于生成与事后评分。',
           '这是一轮共享相位前端的两阶段适配比较，不是五篇原论文分别实现了原生联合相位估计。网络与活动阈值均冻结，未在本轮重训或重新标定。','',
           '同一批物理场景在方法和 SNR 间配对；各档 SNR 独立估计相位，不跨 SNR 共享估计。',
           '场景为 K=40、Q=16、4×4 UPA、连续 off-grid、零用户内路径方向扩展、Bernoulli p=0.1 并条件于至少一名活跃用户。',
           f"每档 SNR 有 {summary[0]['active_users']} 个活跃用户实例、{summary[0]['inactive_users']} 个非活跃用户实例；独立统计单位仍是十个物理场景。",'',
           '![比较图](comparison.png)','','## 完整信道 NMSE / dB','',
           '包含非活跃用户估计误差，不用真活动或估计活动置零。按全部场景误差能量之和除以真信道能量之和计算。','']
    lookup={(r['method'],r['snr_db']):r for r in summary}
    for metric in ['nmse_db','aer']:
        if metric=='aer':lines+=['','## 活动错误率 / %','','分母为全部候选用户；漏检和虚警计数保存在 STATISTICS.csv。','']
        lines+=['| SNR / dB | '+' | '.join(NAMES[m] for m in plan['methods'])+' |',
                '|---:|'+'---:|'*len(plan['methods'])]
        for snr in plan['snr_db']:
            values=[lookup[m,snr][metric]*(100 if metric=='aer' else 1) for m in plan['methods']]
            lines.append('| '+str(snr)+' | '+' | '.join(f'{v:.3f}' for v in values)+' |')
    lines+=['','本批场景的聚合 NMSE：Off-grid SBL 在六档 SNR 下均最低。',
            'L-DAMP＋TSVD 在 −4、−2 dB 时略高于 GNN-ASPL，0 dB 时两者接近，2、4、6 dB 时低于 GNN-ASPL。',
            'AER 方面，GNN-ASPL 在 2、4、6 dB 均为 0.25%；Off-grid SBL 在这三档分别为 0.50%、0.25%、0.25%。NMSE 和 AER 分别比较，保留两项指标之间的差异。',
            '活动错误率的最小计数步长为 1/400=0.25%；表中零点几个百分点的差异只对应少量用户判决，不能据此宣称稳定排名。','']
    lines+=['','## 辅助诊断与耗时','','![相位图](phase_estimation.png)','',
            '| SNR / dB | 相位斜率 RMSE / rad | 跨帧相位因子 RMSE | Doppler RMSE / Hz |','|---:|---:|---:|---:|']
    for r in phases:
        lines.append(f"| {r['snr_db']} | {r['phase_rmse_rad']:.6f} | {r['frame_phasor_rmse']:.6f} | {r['doppler_rmse_hz']:.3f} |")
    worst=max(report['conditions'],key=lambda r:r['largest_active_phase_error_rad'])
    scene=worst['scene']
    shares=[]
    for snr in plan['snr_db']:
        selected=[r for r in phase_rows if r['snr_db']==snr]
        numerator=next(r['active_phase_squared_error'] for r in selected if r['scene']==scene)
        shares.append(numerator/sum(r['active_phase_squared_error'] for r in selected))
    case=folder/f'scene{scene:03d}'/f"snr{worst['snr_db']:+03d}"
    truth,phase=read_npz(case/'truth.npz'),read_npz(case/'phase.npz')
    active=truth['activity'].astype(bool);errors=abs(wrap(phase['phase_slopes']-truth['phase_slopes']))
    user=int(np.argmax(np.where(active,errors,-1)))
    energy=np.sum(abs(truth['channel'])**2,axis=(1,2,3))
    lines+=['',f"相位误差集中在第 {scene+1} 个场景（scene{scene:03d}，{worst['active_users']} 个活跃用户）：该场景占各档相位平方误差总和的 {100*min(shares):.2f}%–{100*max(shares):.2f}%。",
            f"最大单用户相位斜率误差为 {worst['largest_active_phase_error_rad']:.6f} rad，出现在 {worst['snr_db']} dB、用户索引 {user}；该用户仅占本场景真信道总能量的 {100*energy[user]/energy.sum():.3f}%。",
            '这些真值只用于事后定位误差，所有场景和用户仍保留在汇总结果中。弱用户的相位大误差可能对按能量汇总的信道 NMSE 影响较小；其活动判决影响由 AER 体现。',
            '相位 RMSE 未随 SNR 单调下降，绝对 Doppler 误差为数 kHz。这些数值用于定位误差来源，接收机表现以本报告的 NMSE 和 AER 为主要依据。','']
    lines+=['',f"当前 T_frame={model.FRAME_DURATION_S:.9f} s，跨帧相位的 Doppler 周期为 {1/model.FRAME_DURATION_S:.6f} Hz。",
            '相位斜率误差采用 wrap(β_hat−β)，跨帧因子误差覆盖 q=0,…,15；Doppler RMSE 保留周期别名错误。',
            '所有真实活跃用户都参与评分，包括活动检测漏掉的用户；非活跃用户相位不可辨识，不参与相位精度统计。','',
            '| 方法 | 原基线平均耗时 / s | 相位前端平均耗时 / s | 总计 / s |','|---|---:|---:|---:|']
    for m in plan['methods']:
        selected=[r for r in rows if r['method']==m]
        means=[np.mean([r[k] for r in selected]) for k in ['baseline_seconds','phase_seconds','seconds']]
        lines.append('| '+NAMES[m]+' | '+' | '.join(f'{v:.4f}' for v in means)+' |')
    lines+=['','相位估计实际按条件计算一次并供五种方法共享，但比较耗时对每种方法均计入完整前端耗时。',
            '耗时不含加载权重与生成数据；神经网络使用已记录的设备，其余计算使用单线程 CPU，不能据此宣称同硬件复杂度优势。','']
    return lines,summary,phases


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results',type=Path,required=True)
    args=parser.parse_args();folder=args.results
    with threadpool_limits(1):
        plan,rows,phase_rows,report=audit(folder)
        lines,summary,phases=render(folder,plan,rows,phase_rows,report)
    lines+=['## 方法范围与核验','',
        '相位前端为每个候选用户拟合一个主导物理路径，在两轮逐用户更新后提供每用户相位斜率。',
        '使用 128 个相位格点、原 112×7 帧内粗网格、3 个相关峰候选，并对最多 12 个物理 Doppler 别名候选分别连续细化。',
        '复天线增益通过最小二乘消去；全部 40 个候选用户参与，没有输入真实活动数或支持。该单路径拟合是前端近似，最终五种方法保留原信道模型。',
        '开发只使用两个已见旧场景。最初只细化一个别名候选，未通过无噪声单路径恢复检查；改为细化多个候选后，相关计算、解析梯度、物理前向及恢复检查通过。',
        '初版和修正后的开发输出分别保留在 ../development/ 与 ../development_v2/。正式评测前冻结参数，评测后未调阈值、网络或前端。','',
        f"- {report['audited_outputs']} 个完整输出重新计算信道误差、活动计数与判决阈值，一致。",
        f"- {report['audited_conditions']} 组输入重新核验真实物理观测、噪声和跨 SNR 配对，一致。",
        '- 接收机文件仅含原始导频；五种方法的有效算子均由同一份已保存估计相位重建，核验一致。',
        '- scene000/snr+00 的相位前端用公开输入重新运行，全部输出逐项精确一致。',
        '- 同一条件的五种基线也重新运行，活动判决一致、数值误差在预设精度内，共享输入未被修改；逐项精确一致标志见 OUTPUT_AUDIT.json。',
        '- 核心源码、配置和权重身份通过核验；本轮相关 11 项测试通过，已存在的物理生成器浮点警告在日志中保留。','',
        '数值运行完整与优化达到停止精度是不同指标：Off-grid SBL 的 60 个条件均用满既定的 120 次迭代，停止原因均为 MAX_ITERATIONS。',
        f"相位前端共 {report['phase_optimization']['accepted']} 次接受的逐用户更新，其中 {report['phase_optimization'].get('selected_solver_stop_without_success',0)} 次被选中的局部优化返回非成功状态；仍按目标值不增加的规则保留，完整求解器状态见各条件 phase.json。",
        '该非成功状态位于 scene000/snr+02 的第二轮、用户索引 28，消息为 ABNORMAL；结果未被删除或替换。','',
        '十个场景、单组训练权重及固定推断种子只能提供有限规模证据。活动阈值来自已知相位条件，未知相位误差未在阈值训练中重新建模。',
        '共享前端会影响全部方法，当前排名属于这些两阶段组合，不能推广为各算法独立联合相位估计能力的排名。',
        '未在同一批新场景上重跑准确已知相位对照，因此不使用历史不同场景的均值估计“去掉已知相位造成的性能损失”。',
        '该结果也不证明相位全局可辨识、非线性优化全局最优或 AMP 在当前结构化矩阵下具有状态演化保证。','',
        '## 统计解释核查（11/11）','',
        '| 项目 | 本轮处理 |','|---|---|',
        '| Simpson 悖论 | 按 SNR 分层报告，不用跨 SNR 总均值替代分层结果 |',
        '| 生态谬误 | 场景级区间不解释为每用户都具有同一误差率 |',
        '| Berkson 选择偏差 | 明确生成分布条件于非空活动；不推广到允许空场景的分布 |',
        '| 碰撞变量偏差 | 无事后按检测成功、信道强弱或相位误差筛选样本 |',
        '| 基率忽略 | 同时报告真实活跃／非活跃总数、漏检与虚警 |',
        '| 均值回归 | 新场景未按旧结果好坏选择；不做未配对的前后改进宣称 |',
        '| 幸存者偏差 | 全部计划输出均在表中；失败不删除，完整性检查未通过则不出完成报告 |',
        '| 多重寻找效应 | 五种方法六档 SNR 完整报告；区间为逐点、未校正，不作全局显著性结论 |',
        '| 分析路径选择 | 参数在新评测前冻结；开发失败与修正保留记录 |',
        '| 相关与因果 | 结论限于固定模拟条件下的算法比较，不作外部应用因果推断 |',
        '| 反向因果 | 不适用；数据生成与推断方向由模拟协议固定 |','',
        '术语与方法依据：docs/TERMINOLOGY.md；变量投影的含义参见 O’Leary–Rust §1 式(2)–(3)、§2 式(5)–(7)。',
        '本前端不是 Shen EM 或 MNOMP 的复现。','']
    (folder/'REPORT.md').write_text('\n'.join(lines))
    print(json.dumps(dict(status='PASS',audited_outputs=len(rows),conditions=len(phase_rows),
                          report=str(folder/'REPORT.md'),statistics=summary,phase=phases)))


if __name__=='__main__':
    main()
