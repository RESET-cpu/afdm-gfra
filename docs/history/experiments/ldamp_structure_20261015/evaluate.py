"""Calibrate output TSVD on eight old scenes; compare frozen paired receivers on new scenes."""
import argparse,json,platform,sys,time,warnings
from pathlib import Path
import numpy as np
import torch
from threadpoolctl import threadpool_limits
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from afdm_jadcedd.system.observation import ReceiverInput,load_input
from afdm_jadcedd.experiment.generate import generate_case
from afdm_jadcedd.utils import write_json,sha256
from afdm_jadcedd.algorithm.baselines.ldamp.receiver import load_configuration,signature as base_signature
from evaluate_ldamp_joint import score,warning_summary,summarize
from validate_ldamp import fit_threshold
from structured_receiver import Receiver,signature


def cached_base(source):
    folder=ROOT/'results/ldamp_structure_20261015/development'
    plan=json.loads((folder/'PLAN.json').read_text())
    if plan['original_signature']!=base_signature(load_configuration()):return None
    for row in json.loads((folder/'ROWS.json').read_text()):
        if row['method']=='original' and row['status']=='COMPLETE' and row['input_sha256']==sha256(source/'input.npz'):
            path=folder/f"original_scene{row['scene']:03d}_snr{row['snr_db']:+03d}.npz"
            if sha256(path)!=row['output_sha256']:raise ValueError('Development cache mismatch')
            with np.load(path) as d:arrays={k:d[k] for k in d.files}
            return arrays,dict(seconds=row['seconds'],inference_sha256=plan['original_signature']),str(path.relative_to(ROOT))
    return None


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage',choices=['calibrate','evaluate'],required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--config',type=Path)
    args=parser.parse_args();out=args.output;out.mkdir(parents=True,exist_ok=False)
    torch.set_num_threads(1)
    if args.stage=='calibrate':
        base=load_configuration()
        config=dict(schema='afdm-ldamp-output-tsvd-v1',rank=1,base_configuration=base,
            base_inference_sha256=base_signature(base),readout=None,validation_status='DEVELOPMENT',
            scope='Zero intra-user path direction spread; output TSVD after unchanged L-DAMP; projected energy readout')
        scenes=8;snrs=[-4,0,6];seed_base=2026101452100000
    else:
        if not args.config:raise ValueError('A frozen calibrated configuration is required')
        config=json.loads(args.config.read_text());scenes=10;snrs=[-4,-2,0,2,4,6];seed_base=2026101504100000
        if not config.get('readout'):raise ValueError('Calibrated readout required')
        old=json.loads((ROOT/'results/ldamp_complete_20261015/independent_validation/PLAN.json').read_text())
        assert not set(range(seed_base,seed_base+scenes)) & set(range(old['seed_base'],old['seed_base']+old['scenes']))
    receiver=Receiver(config);identity=receiver.signature
    write_json(out/'configuration.json',config)
    sources=list((ROOT/'src/afdm_jadcedd').rglob('*.py'))+[Path(__file__),Path(__file__).with_name('structure.py'),Path(__file__).with_name('structured_receiver.py'),ROOT/'scripts/evaluate_ldamp_joint.py',ROOT/'scripts/validate_ldamp.py']
    snapshots={str(p.relative_to(ROOT)):sha256(p) for p in sources}
    for path in sources:
        target=out/'sources'/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(path.read_bytes())
    write_json(out/'PLAN.json',dict(stage=args.stage,scenes=scenes,snr_db=snrs,seed_base=seed_base,
        methods=['original','candidate','candidate_original_decision'],configuration=config,
        inference_sha256=dict(original=receiver.base.signature,candidate=identity,candidate_original_decision=identity),
        sources=snapshots,independent_validation=args.stage=='evaluate',
        environment=dict(python=sys.version,numpy=np.__version__,torch=torch.__version__,platform=platform.platform(),device='mps',torch_threads=1,blas_threads=1),
        timing='Base inference shared exactly; candidate time is base plus measured postprocessing. Cold loading/data generation excluded.',
        primary_metric='Unmasked full channel including inactive users',secondary_metric='Own activity-decision masked channel',
        threshold_rule='Minimum pooled development activity errors; largest threshold on ties',
        interpretation='Paired physical scenes; 5000 bootstrap replicates; candidate_original_decision isolates channel refinement from readout calibration.'))
    rows=[];started=time.time()
    for scene in range(scenes):
        for snr in snrs:
            folder=out/f'scene{scene:03d}'/f'snr{snr:+03d}';folder.mkdir(parents=True)
            try:
                cache=None
                if args.stage=='calibrate':
                    source=ROOT/f'results/ldamp_diagnosis_20261014/receiver_pilot/calibration/scene{scene:03d}/snr{snr:+03d}'
                    inputs=load_input(source/'input.npz')
                    with np.load(source/'truth.npz') as d:truth={k:d[k] for k in d.files}
                    metadata=json.loads((source/'generation.json').read_text());cache=cached_base(source)
                else:
                    with warnings.catch_warnings(record=True) as caught,threadpool_limits(1):
                        warnings.simplefilter('always',RuntimeWarning)
                        public,truth,metadata=generate_case(seed_base+scene,snr,config['base_configuration']['scale'],users=40,frames=16,activity_probability=.1,require_active_user=True,grid_mode='off_grid')
                    write_json(folder/'generation_warnings.json',warning_summary(caught))
                    inputs=ReceiverInput(**{k:public[k] for k in ReceiverInput.__dataclass_fields__})
                np.savez_compressed(folder/'input.npz',**inputs.arguments());np.savez_compressed(folder/'truth.npz',channel=truth['channel'],activity=truth['activity']);write_json(folder/'generation.json',metadata)
                with warnings.catch_warnings(record=True) as caught,threadpool_limits(1):
                    warnings.simplefilter('always',RuntimeWarning)
                    if cache:
                        base_arrays,base_record,cache_path=cache
                        arrays,record=receiver.postprocess(base_arrays,base_record)
                    else:
                        arrays,record,base_arrays,base_record=receiver.infer_pair(inputs);cache_path=None
                write_json(folder/'warnings.json',warning_summary(caught))
                control=dict(arrays);control['activity_decision']=base_arrays['activity_decision'].copy()
                control['activity_score']=base_arrays['activity_score'].copy()
                control_record=dict(record,activity_statistic='original_channel_frobenius_energy',
                    activity_rule_configuration=config['base_configuration']['readout'])
                for method,data,rec in [('original',base_arrays,base_record),('candidate',arrays,record),('candidate_original_decision',control,control_record)]:
                    target=folder/f'{method}.npz';np.savez_compressed(target,**data)
                    entry=dict(scene=scene,snr_db=snr,method=method,status='COMPLETE',**score(data,truth),seconds=rec['seconds'],
                        postprocessing_seconds=rec.get('postprocessing_seconds',0.),input_sha256=sha256(folder/'input.npz'),output_sha256=sha256(target),
                        inference_sha256=receiver.base.signature if method=='original' else identity,cache_source=cache_path,warning_count=len(caught))
                    rows.append(entry);write_json(folder/f'{method}.json',dict(**rec,input_sha256=entry['input_sha256'],output_sha256=entry['output_sha256']))
                print(json.dumps(dict(scene=scene,snr_db=snr,status='COMPLETE',base_seconds=base_record['seconds'],postprocessing_seconds=record['postprocessing_seconds'])),flush=True)
            except Exception as exc:
                rows.append(dict(scene=scene,snr_db=snr,method='all',status='FAILED',error=repr(exc)))
                print(json.dumps(rows[-1]),flush=True)
            write_json(out/'ROWS.json',rows);write_json(out/'STATUS.json',dict(status='RUNNING',completed_conditions=(scene*len(snrs)+snrs.index(snr)+1),expected_conditions=scenes*len(snrs),seconds=time.time()-started))
    failures=[r for r in rows if r['status']!='COMPLETE']
    if failures:
        write_json(out/'STATUS.json',dict(status='FAILED',failures=len(failures),completed_rows=len(rows)));raise SystemExit(1)
    if signature(config)!=identity or any(sha256(ROOT/path)!=digest for path,digest in snapshots.items()):raise ValueError('Inference sources changed during run')
    if args.stage=='calibrate':
        selected=[r for r in rows if r['method']=='candidate']
        threshold,errors=fit_threshold(np.concatenate([r['score'] for r in selected]),np.concatenate([r['active'] for r in selected]))
        readout=out/'READOUT.json';write_json(readout,dict(inference_sha256=identity,threshold=threshold,calibration_errors=errors,scenes=scenes,snr_db=snrs,statistic='projected_channel_frobenius_energy',scope='Old development scenes, not validation'))
        config['readout']=dict(path=str(readout.resolve().relative_to(ROOT)),sha256=sha256(readout));config['validation_status']='CALIBRATED_AWAITING_INDEPENDENT_VALIDATION';write_json(out/'receiver.json',config)
        for row in selected:
            active=np.asarray(row['active']);decision=np.asarray(row['score'])>=threshold
            row.update(misses=int(np.sum(active&~decision)),false_alarms=int(np.sum(~active&decision)))
            folder=out/f"scene{row['scene']:03d}"/f"snr{row['snr_db']:+03d}"
            with np.load(folder/'candidate.npz') as d:est=d['estimate']
            with np.load(folder/'truth.npz') as d:truth=d['channel']
            row['estimated_activity_masked_error']=float(np.sum(abs(est*decision[:,None,None,None]-truth)**2))
        write_json(out/'ROWS.json',rows)
    write_json(out/'SUMMARY.json',dict(results=summarize(rows),independent_validation=args.stage=='evaluate'))
    write_json(out/'STATUS.json',dict(status='COMPLETE',conditions=scenes*len(snrs),rows=len(rows),seconds=time.time()-started))


if __name__=='__main__':main()
