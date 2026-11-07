"""Frozen small receiver evaluation after both matched networks finish training."""
from copy import deepcopy
import numpy as np
from project import ROOT
from utils import read_json, write_json, sha256
from system.observation import ReceiverInput
from evaluation.metrics import score_arrays


def aggregate(rows, method):
    selected=[r[method] for r in rows]
    e=sum(r['metrics']['full_error'] for r in selected)
    s=sum(r['metrics']['signal_energy'] for r in selected)
    return dict(inputs=len(selected),nmse_db=float(10*np.log10(e/s)),
        misses=sum(r['metrics']['misses'] for r in selected),
        false_alarms=sum(r['metrics']['false_alarms'] for r in selected),
        average_iterations=float(np.mean([r['iterations'] for r in selected])),
        not_converged=sum(not r['converged'] for r in selected))


def run_evaluation(cfg,out,spec):
    from .run import status, check_sources
    from algorithm.C_STMP_column_20261025.receiver import Receiver
    from algorithm.C_STMP_retrained.receiver import Receiver as Original
    from evaluation.suite import prepared_case
    folder=out/'evaluation';folder.mkdir(exist_ok=True)
    candidate=deepcopy(cfg['receiver']);candidate.update(scale=cfg['scale'])
    for stage in ('first','activity'):
        candidate[stage+'_checkpoint']=str(out/stage/'best.pt')
        candidate[stage+'_sha256']=sha256(out/stage/'best.pt')
    write_json(out/'RECEIVER.json',candidate)
    earlier=read_json(ROOT/'result/snr_comparison/data/c_stmp_query_repair_20261025/PLAN.json')
    generation=deepcopy(earlier['generation'])
    generation.update(base_seed=cfg['evaluation']['base_seed'],cache=str(folder/'cache'))
    plan=dict(configuration=candidate,development=earlier['development_cases'],generation=generation,
        independent_tasks=[dict(scene=s,index=i) for s in range(cfg['evaluation']['scenes']) for i in cfg['evaluation']['conditions']],
        selection='All 10 old problem inputs; independent seeds and SNR fixed in training specification before training',
        no_threshold_fit=True,retain_nonconverged=True,full_snr_resume=False)
    if (folder/'PLAN.json').exists(): assert read_json(folder/'PLAN.json')==plan
    else: write_json(folder/'PLAN.json',plan)
    tasks=[dict(**c,panel='development') for c in plan['development']]
    from pathlib import Path
    for t in plan['independent_tasks']:
        _,_,receipt,path=prepared_case(generation,t['scene'],generation['conditions'][t['index']])
        tasks.append(dict(**t,panel='independent',ready=str(path/'READY.json'),ready_sha256=sha256(path/'READY.json'),
            files=receipt['files'],snr_db=generation['conditions'][t['index']]['snr_db']))
    write_json(folder/'INPUTS.json',tasks)
    model=Receiver(candidate);original=Original(ROOT/'src/configs/candidates/C_STMP_retrained_20261025.json',device='cuda')
    results=[]
    for item in tasks:
        if (out/'STOP.json').exists(): status(out,'STOPPED_BY_USER',network='evaluation',completed=len(results));return False
        stem=folder/f'{item["panel"]}_scene{item["scene"]:04d}_condition{item["index"]:02d}'
        result_path=stem.with_suffix('.json')
        if result_path.exists():
            row=read_json(result_path)
            assert row['input']==item
            for method,values in row.items():
                if method in ('candidate','original') and 'prediction_path' in values:
                    assert sha256(values['prediction_path'])==values['prediction_sha256']
            results.append(row);continue
        ready=Path(item['ready']);assert sha256(ready)==item['ready_sha256']
        for name,digest in item['files'].items():assert sha256(ready.parent/name)==digest
        with np.load(ready.parent/'public.npz') as z: inputs=ReceiverInput(z['y'],z['a'],float(z['noise_variance']),float(z['rho']))
        outputs={}
        new_arrays,new_record=model.infer(inputs)
        outputs['candidate']=(new_arrays,new_record)
        if item['panel']=='independent': outputs['original']=original.infer(inputs)
        with np.load(ready.parent/'truth.npz') as z: truth=dict(z)
        row=dict(input=item)
        for method,(arrays,record) in outputs.items():
            if not all(np.isfinite(a).all() for a in arrays.values()):raise FloatingPointError('Nonfinite receiver output')
            target=stem.with_name(stem.name+'_'+method)
            if target.with_suffix('.npz').exists():raise ValueError('Uncommitted output exists; inspect, do not overwrite')
            np.savez_compressed(target.with_suffix('.npz'),**arrays)
            write_json(target.with_suffix('.record.json'),record)
            with np.load(target.with_suffix('.npz')) as z: saved=dict(z)
            row[method]=dict(metrics=score_arrays(saved,truth),iterations=record['iterations'],converged=record['converged'],
                prediction_path=str(target.with_suffix('.npz')),prediction_sha256=sha256(target.with_suffix('.npz')),
                record_sha256=sha256(target.with_suffix('.record.json')))
        if item['panel']=='development':
            old=read_json(item['classifier']['result']);assert sha256(item['classifier']['result'])==item['classifier']['sha256']
            row['original']=dict(metrics=old['metrics'],iterations=old['iterations'],
                                 converged=old['stopping_reason']=='CONVERGED')
        write_json(result_path,row);results.append(row)
        status(out,'EVALUATING',completed=len(results),planned=len(tasks),scene=item['scene'],snr_db=item['snr_db'],
               candidate=row['candidate']['metrics'],original=row['original']['metrics'])
    summary={panel:{method:aggregate([r for r in results if r['input']['panel']==panel],method)
                    for method in ('original','candidate')} for panel in ('development','independent')}
    write_json(folder/'SUMMARY.json',summary)
    report=['# 统一列消息 C-STMP：小场景完整接收评估','',
        '两套网络使用同一消息条件；原10个错误输入与4个新物理场景分开报告。保留全部有限未收敛输出，未按性能筛选。', '',
        '| 面板 | 方法 | NMSE (dB) | 漏检 | 虚警 | 平均迭代 | 未收敛 |',
        '|---|---|---:|---:|---:|---:|---:|']
    for panel,methods in summary.items():
        for method,r in methods.items():
            report.append(f'| {panel} | {method} | {r["nmse_db"]:.4f} | {r["misses"]} | {r["false_alarms"]} | {r["average_iterations"]:.2f} | {r["not_converged"]} |')
    report+=['','错误面板为回顾性诊断；独立面板仅4个物理场景，不代表1000场景总体性能。原完整SNR仍暂停。']
    (folder/'REPORT.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
    check_sources(spec)
    write_json(folder/'COMPLETE.json',dict(status='COMPLETE',inputs=len(results),summary_sha256=sha256(folder/'SUMMARY.json'),
        outputs={str(p.relative_to(folder)):sha256(p) for p in folder.glob('*') if p.is_file() and p.name!='COMPLETE.json'}))
    return True
