"""Independently audit saved paired outputs and report scene-level uncertainty."""
import argparse,csv,json,sys
from pathlib import Path
import numpy as np
from threadpoolctl import threadpool_limits
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from afdm_jadcedd.utils import sha256,write_json
from report_ldamp_joint import statistics


def audit(folder):
    plan=json.loads((folder/'PLAN.json').read_text());state=json.loads((folder/'STATUS.json').read_text());rows=json.loads((folder/'ROWS.json').read_text())
    assert plan['stage']=='evaluate' and state['status']=='COMPLETE'
    expected={(s,n,m) for s in range(plan['scenes']) for n in plan['snr_db'] for m in plan['methods']}
    assert len(rows)==len(expected) and {(r['scene'],r['snr_db'],r['method']) for r in rows}==expected
    for path,digest in plan['sources'].items():assert sha256(ROOT/path)==digest==sha256(folder/'sources'/path),path
    checks=[];pairing=[]
    readout=json.loads((ROOT/plan['configuration']['readout']['path']).read_text())
    assert sha256(ROOT/plan['configuration']['readout']['path'])==plan['configuration']['readout']['sha256']
    original_rule=plan['configuration']['base_configuration']['readout'];original_readout=json.loads((ROOT/original_rule['path']).read_text())
    assert sha256(ROOT/original_rule['path'])==original_rule['sha256']
    for scene in range(plan['scenes']):
        hashes=None
        for snr in plan['snr_db']:
            case=folder/f'scene{scene:03d}'/f'snr{snr:+03d}'
            with np.load(case/'input.npz') as inp,np.load(case/'truth.npz') as truth:
                assert set(inp.files)=={'observation','operator','noise_variance','activity_prior'}
                h=truth['channel'];active=truth['activity'].astype(bool);a=inp['operator'];y=inp['observation']
                identities=[sha_array(x) for x in [h,active,a]]
                if hashes is None:hashes=identities
                assert hashes==identities
                metadata=json.loads((case/'generation.json').read_text());seed=plan['seed_base']+scene
                assert metadata['seed']==seed and metadata['path_direction_rms_deg']==0.
                clean=np.einsum('qkn,kmrn->qmr',a,h,optimize=False)
                variance=np.mean(abs(clean)**2)*10**(-snr/10)
                assert variance==float(inp['noise_variance'])
                rng=np.random.default_rng(np.random.SeedSequence([seed,2096]));shape=(32,16,16)
                eps=((rng.normal(size=shape)+1j*rng.normal(size=shape))/np.sqrt(2))[:16]
                assert np.array_equal(y,clean+np.sqrt(variance)*eps)
                pairing.append(dict(scene=scene,snr_db=snr,input_sha256=sha256(case/'input.npz'),truth_sha256=sha256(case/'truth.npz'),passed=True))
            with np.load(case/'original.npz') as original:
                raw=original['estimate'];u,s,vh=np.linalg.svd(raw.reshape(len(raw),16,-1),full_matrices=False)
                independent_projection=(u[:,:,:1]*s[:,None,:1])@vh[:,:1,:];independent_projection=independent_projection.reshape(raw.shape)
                original_decision=original['activity_decision']
            for method in plan['methods']:
                row=next(r for r in rows if (r['scene'],r['snr_db'],r['method'])==(scene,snr,method));assert row['status']=='COMPLETE'
                record=json.loads((case/f'{method}.json').read_text())
                assert row['input_sha256']==record['input_sha256']==sha256(case/'input.npz')
                assert row['output_sha256']==record['output_sha256']==sha256(case/f'{method}.npz')
                assert row['inference_sha256']==plan['inference_sha256'][method]
                with np.load(case/f'{method}.npz') as pred:
                    est=pred['estimate'];decision=pred['activity_decision'];assert np.isfinite(est).all()
                    if method!='original':np.testing.assert_allclose(est,independent_projection,rtol=1e-10,atol=1e-11)
                    e=np.sum(abs(est-h)**2,axis=(1,2,3));values=dict(full_error=float(e.sum()),active_error=float(e[active].sum()),inactive_error=float(e[~active].sum()),signal_energy=float(np.sum(abs(h)**2)),estimated_activity_masked_error=float(np.sum(abs(est*decision[:,None,None,None]-h)**2)))
                    for key,value in values.items():assert np.isclose(row[key],value,rtol=1e-11,atol=1e-12),(method,key)
                    assert row['misses']==int(np.sum(active&~decision)) and row['false_alarms']==int(np.sum(~active&decision))
                    if method=='candidate':expected_decision=pred['activity_score']>=readout['threshold']
                    elif method=='original':expected_decision=pred['activity_score']>=original_readout['threshold']
                    else:expected_decision=original_decision
                    assert np.array_equal(decision,expected_decision)
                checks.append(dict(scene=scene,snr_db=snr,method=method,passed=True))
    write_json(folder/'OUTPUT_AUDIT.json',dict(status='PASS',checks=checks,conditions=pairing,independent_projection_reference='NumPy full SVD; inference uses eigendecomposition of spatial Gram matrix',script_sha256=sha256(Path(__file__))))
    return plan,rows


def sha_array(a):
    import hashlib
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--results',type=Path,required=True);args=parser.parse_args();f=args.results
    with threadpool_limits(1):
        plan,rows=audit(f)
    # Reuse a tested paired-scene bootstrap routine with an internal name map.
    mapping={'original':'original','candidate':'joint','candidate_original_decision':'control'}
    p=dict(plan,methods=[mapping[m] for m in plan['methods']]);r=[dict(x,method=mapping[x['method']]) for x in rows]
    summary,contrasts=statistics(p,r)
    reverse={v:k for k,v in mapping.items()}
    for x in summary:x['method']=reverse[x['method']]
    for x in contrasts:x['reference']=reverse[x['reference']]
    write_json(f/'PAIRED_CONTRASTS.json',dict(results=contrasts,replicates=5000,unit='physical scene',seed=202610150301))
    with (f/'STATISTICS.csv').open('w',newline='') as h:
        writer=csv.DictWriter(h,fieldnames=list(summary[0]));writer.writeheader();writer.writerows(summary)
    import matplotlib
    matplotlib.use('Agg');import matplotlib.pyplot as plt
    fig,axs=plt.subplots(1,2,figsize=(10,4),layout='constrained')
    names={'original':'Original L-DAMP','candidate':'TSVD, recalibrated decisions','candidate_original_decision':'TSVD, original decisions'}
    for m,color in [('original','#666666'),('candidate','#1261a0'),('candidate_original_decision','#008568')]:
        v=[x for x in summary if x['method']==m];snrs=[x['snr_db'] for x in v]
        for ax,key,scale in [(axs[0],'nmse',1),(axs[1],'aer',100)]:
            if key=='nmse' and m=='candidate':continue
            style='--o' if m=='candidate_original_decision' and key=='aer' else '-o'
            label='L-DAMP + output TSVD' if key=='nmse' and m!='original' else names[m]
            ax.plot(snrs,[x['nmse_db' if key=='nmse' else key]*scale for x in v],style,label=label,color=color)
            ax.fill_between(snrs,[x[key+'_low']*scale for x in v],[x[key+'_high']*scale for x in v],color=color,alpha=.12)
    for ax in axs:ax.set_xlabel('SNR (dB)');ax.set_xticks(plan['snr_db']);ax.grid(alpha=.2);ax.legend(fontsize=8)
    axs[0].set_ylabel('Full-channel NMSE (dB)');axs[1].set_ylabel('Activity error rate (%)');axs[1].set_ylim(bottom=-.02)
    fig.suptitle('10 new paired scenes; pointwise 95% scene bootstrap',fontsize=11)
    fig.savefig(f/'comparison.png',dpi=180);fig.savefig(f/'comparison.svg');plt.close(fig)
    lines=['# L-DAMP 输出 TSVD 独立验证','','## Material Passport','','- Type: Experiment Result; mode: run','- Status: VERIFIED saved outputs and physical pairing; conditional statistical evidence','- Scope: 10 new physical scenes, fixed base DnCNN, frozen TSVD/readout; no retraining','- Provenance: PLAN.json, configuration.json, sources/, OUTPUT_AUDIT.json','','同一条件只运行一次原 L-DAMP，候选随后仅用估计信道作每用户 16×256 展开的秩一近似。候选活动阈值在八个旧开发场景上标定。原版判决控制使用相同的候选信道估计、保留原活动判决，用来区分信道改进与判决变化。主指标未按活动决策置零，包含非活跃用户误差。','','![比较图](comparison.png)','','| SNR/dB | 原版 NMSE/dB | 候选 NMSE/dB | 差值/dB | 配对 95% 区间 | 原版漏检/虚警 | 候选漏检/虚警 |','|---:|---:|---:|---:|---|---|---|']
    for snr in plan['snr_db']:
        a=next(x for x in summary if x['method']=='original' and x['snr_db']==snr);b=next(x for x in summary if x['method']=='candidate' and x['snr_db']==snr);c=next(x for x in contrasts if x['reference']=='original' and x['snr_db']==snr)
        lines.append(f"| {snr} | {a['nmse_db']:.3f} | {b['nmse_db']:.3f} | {c['delta_nmse_db']:.3f} | [{c['delta_nmse_95'][0]:.3f}, {c['delta_nmse_95'][1]:.3f}] | {a['misses']}/{a['false_alarms']} | {b['misses']}/{b['false_alarms']} |")
    means={m:float(np.mean([x['seconds'] for x in rows if x['method']==m])) for m in plan['methods']}
    extra=float(np.mean([x['postprocessing_seconds'] for x in rows if x['method']=='candidate']))
    lines+=['', '**活动规则判断：上述“候选漏检/虚警”列对应重新标定的投影能量阈值，它在六档 SNR 均增加漏检，未获得活动检测改进。** 预先设置的“保留原判决”对照使用完全相同的 TSVD 信道估计，漏检/虚警逐项等于原版列；图中其活动曲线与原版重合。公开命令默认使用这个原判决模式，新阈值作为显式选项保留。未根据新场景重调任何阈值、网络、递推或投影参数。该采用建议形成于比较之后，并非采用决定之后又进行了一次新的盲测。', '',f"原版平均 {means['original']:.4f} s，候选平均 {means['candidate']:.4f} s，附加处理平均 {extra:.6f} s。两者共享同一次基础推断，时间不包括模型加载和数据生成。",'', '全部完整输出、活动计数、输入物理配对及 TSVD 结果均独立核验。推断用空间 Gram 矩阵特征分解，独立参考使用完整 SVD。', '', '限制：十个独立物理场景，单次训练权重及固定校正种子；逐点 bootstrap 区间未作多重比较校正，零观测错误不等于总体零错误率。只覆盖已知有效测量算子、4×4 阵列、40 用户、16 次观测及零用户内路径方向扩展条件。秩一近似的最小二乘性质不保证其是最优后验均值，也不解决 DnCNN 训练扰动与实际误差的失配。没有 AFDM 状态演化或迭代收敛保证。','', '结构操作来源：Gavish–Donoho §1 式(2)后的 Truncated SVD 定义；记录于 docs/TERMINOLOGY.md。本实验是明确说明的 L-DAMP 输出处理，不作为原论文逐项复现。','']
    (f/'REPORT.md').write_text('\n'.join(lines))
    print(json.dumps(dict(status='PASS',cases=len(rows),conditions=len(rows)//3,mean_seconds=means,postprocessing_seconds=extra)))


if __name__=='__main__':main()
