"""Paired frozen baselines, using the same prepared public inputs and metrics."""
import copy
import json
import time
import numpy as np
import torch

from .common import ROOT,OUT,CONFIG,sha,save_json,real_tensor,check_budget,status
from .data import Cases
from .receiver import metrics,summarize_rows,summarize_conditions,synchronize


def binding(spec):
    path=ROOT/spec['configuration']
    cfg=copy.deepcopy(json.loads(path.read_text(encoding='utf-8')))
    cfg['ep']['damping']=spec['damping']
    hashes={key:sha(ROOT/cfg[key]) for key in ('first_checkpoint','second_checkpoint','evidence_checkpoint')}
    for key,value in hashes.items():
        if key+'_sha256' in cfg and cfg[key+'_sha256']!=value:
            raise ValueError('Baseline checkpoint binding changed: '+key)
    return cfg,dict(name=spec['name'],configuration_sha256=sha(path),
        applied_configuration=cfg,checkpoint_sha256=hashes)


def evaluate_baselines(scale,device,started,common_identity,load_progress):
    from afdm_jadcedd.algorithm.proposed.receiver import Receiver as OriginalReceiver
    count=CONFIG['receiver']['test_scenes']
    for spec in CONFIG['baseline_comparisons']:
        cfg,bound=binding(spec)
        identity=dict(common_identity,method='frozen_baseline',**bound)
        path=OUT/'results'/f"baseline_{spec['name']}.json"
        rows=load_progress(path,identity,count)
        if len(rows)==count: continue
        original=OriginalReceiver(cfg,device=device)
        cases=Cases('test',scale,device)
        for index in range(len(rows),count):
            check_budget(started);synchronize(device);before=time.perf_counter()
            public,labels,info=cases[index]
            inputs=public['physical_input']
            synchronize(device);ready=time.perf_counter()
            result,record=original.infer(inputs)
            synchronize(device);finished=time.perf_counter()
            if not all(np.isfinite(value).all() for value in result.values()):
                raise FloatingPointError(f'Nonfinite baseline output for case {index}; no case discarded')
            # logit comparison preserves the project's fixed probability threshold.
            p=torch.as_tensor(result['probabilities'],device=device)
            logits=torch.logit(p)
            output=(real_tensor(result['estimate']/scale,device),logits)
            row=dict(**info,case_index=index,case_sha256=identity['case_hashes'][index],
                **metrics([output],labels),iterations=record['iterations'],stopping_reason=record['stopping_reason'],
                preparation_seconds=ready-before,inference_seconds=finished-ready,total_seconds=finished-before)
            rows.append(row)
            save_json(path,dict(status='COMPLETE' if len(rows)==count else 'PARTIAL',identity=identity,
                rows=rows,summary=summarize_rows(rows),by_condition=summarize_conditions(rows)))
            status('FROZEN_BASELINE_TEST',baseline=spec['name'],scene=index+1,total=count)
