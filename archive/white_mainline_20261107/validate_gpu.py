"""Compare the extracted white package with adopted saved FP32 predictions."""
from pathlib import Path
import sys
import time
import traceback

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from utils import read_json,write_json,sha256,state_sha
from evaluation.white_followup_20261107.common import setup,checked,CONFIG,PHASE_CONFIG


def main():
    import numpy as np
    import torch
    from threadpoolctl import threadpool_limits
    from evaluation.storage import arrays,save_arrays
    from evaluation.metrics import score_arrays
    from system.observation import ReceiverInput
    from system.receiver.unknown_phase import UnknownPhaseInput
    from algorithm.GP_MP.receiver import Receiver
    from algorithm.GP_MP.phase_receiver import PhaseReceiver
    out=Path(__file__).resolve().parent
    assert not (out/'VALIDATION.json').exists()
    setup();reports=[]
    for mode,cls,config,source,positions in [
        ('known',Receiver,CONFIG,'white_preconditioned_matched_fp32_1000_snr_20261105',[0,5]),
        ('estimated',PhaseReceiver,PHASE_CONFIG,'white_phase_frontend_marginal_1000_20261106',[0,72,5,0])]:
        root=ROOT/'result/snr_comparison/data'/source
        completion=read_json(root/'COMPLETION.json')
        assert completion['status']=='PASS'
        checked(root/'SUMMARY.json',completion['summary_sha256'])
        cases=read_json(root/'INPUTS.json')
        receiver=cls(config,device='cuda',noise_mode='estimated')
        before=[state_sha(receiver.model.network),state_sha(receiver.evidence.network)]
        for order,pos in enumerate(positions):
            case=cases[pos];folder=Path(case['ready']).parent
            checked(case['ready'],case['ready_sha256'])
            for name,digest in case['files'].items():checked(folder/name,digest)
            raw=arrays(folder/('public.npz' if mode=='known' else 'raw.npz'))
            public=(ReceiverInput(raw['y'],raw['a'],1.,float(raw['rho'])) if mode=='known' else
                    UnknownPhaseInput(raw['y'],raw['pilot'],1.,float(raw['rho'])))
            tick=time.time()
            with threadpool_limits(2):prediction,record=receiver.infer(public)
            dest=out/'gpu_validation'/f'{mode}_{order:02d}_{pos:04d}';dest.mkdir(parents=True,exist_ok=False)
            save_arrays(dest/'prediction.npz',prediction);write_json(dest/'record.json',record)
            ptr=read_json(root/'results'/f'scene{pos//6:04d}_condition{pos%6:02d}.json')
            checked(ptr['result'],ptr['sha256']);old=read_json(ptr['result'])
            for name,digest in old['files'].items():checked(name,digest)
            saved=arrays(Path(ptr['result']).parent/'prediction.npz')
            assert prediction.keys()==saved.keys()
            differences={}
            for key in prediction:
                a,b=prediction[key],saved[key]
                assert a.shape==b.shape and a.dtype==b.dtype
                differences[key]=float(np.max(abs(a.astype(complex)-b.astype(complex))))
                if key in ('activity_decision','phase','initial_phase','phase_slopes','initial_phase_slopes'):
                    np.testing.assert_array_equal(a,b)
                else:np.testing.assert_allclose(a,b,rtol=2e-6,atol=2e-7)
            assert old['iterations']==record['iterations'] and old['stopping_reason']==record['stopping_reason']
            assert record['phase_mode']==mode and record['oracle_phase_supplied']==(mode=='known')
            assert not record['noise_truth_used']
            truth=arrays(folder/'truth.npz');metrics=score_arrays(prediction,truth)
            assert metrics['misses']==old['metrics']['misses'] and metrics['false_alarms']==old['metrics']['false_alarms']
            assert before==[state_sha(receiver.model.network),state_sha(receiver.evidence.network)]
            row=dict(mode=mode,position=pos,iterations=record['iterations'],seconds=time.time()-tick,
                stopping_reason=record['stopping_reason'],maximum_absolute_difference=differences,
                all_arrays_identical=all(v==0 for v in differences.values()),
                reference_result=ptr['result'],reference_sha256=ptr['sha256'],
                prediction_sha256=sha256(dest/'prediction.npz'))
            reports.append(row);print(row,flush=True)
        del receiver;torch.cuda.empty_cache()
    assert not [m for m in sys.modules if m.startswith(('algorithm.C_STMP','training.colored','evaluation.white_matched'))]
    extraction=read_json(out/'EXTRACTION.json')
    write_json(out/'VALIDATION.json',dict(status='PASS',completed_unix=time.time(),gpu_cases=reports,
        all_arrays_identical=all(r['all_arrays_identical'] for r in reports),models_unchanged=True,
        no_colored_runtime_imports=True,extraction_sha256=sha256(out/'EXTRACTION.json'),
        counted_in_formal_experiments=False,
        new_sources={str(p.relative_to(ROOT)):sha256(p) for p in (ROOT/'src/algorithm/GP_MP').glob('*.py')}))


if __name__=='__main__':
    try:main()
    except Exception:
        write_json(Path(__file__).resolve().parent/'VALIDATION_FAILURE.json',dict(traceback=traceback.format_exc(),automatic_retry=False))
        raise
