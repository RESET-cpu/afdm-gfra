"""Post-hoc mechanism controls on one already exposed failed physical case.

No fitting/selection. These are not new held-out acceptance measurements.
"""
import time
import traceback
import numpy as np
import torch
from threadpoolctl import threadpool_limits
import validate_message_calibration as S
from afdm_jadcedd.algorithm.proposed.moments import MatrixMomentEstimate


class Remember:
    def __init__(self, original):
        self.original=original;self.last_value=None

    def __getattr__(self, key):return getattr(self.original,key)

    def infer(self,*args):
        self.last_value=self.original.infer(*args)
        return self.last_value


class Components(S.CalibratedMoments):
    def __init__(self, original, evidence, model, enabled):
        super().__init__(Remember(original),Remember(evidence),model)
        self.enabled=enabled

    def infer(self, query, variance):
        calibrated=super().infer(query,variance)
        raw=self.original.last_value
        if not self.enabled[2]:
            r,v,_=self.cache
            self.cache=(r,v,np.array(self.original_evidence.last_value,copy=True))
        return MatrixMomentEstimate(calibrated.mean if self.enabled[0] else raw.mean,
                                    calibrated.variance if self.enabled[1] else raw.variance)


def main():
    protocol=S.verify();full=S.P.read(S.OUT/'physical/SUMMARY.json')
    assert len(full['results'])==32, 'Finish all prespecified comparisons first'
    output=S.OUT/'component_diagnosis';assert not output.exists()
    case='seed00_condition02';bank=S.OUT/'bank'/case
    ready=S.P.read(bank/'READY.json')
    for file,digest in ready['sha256'].items():assert S.P.sha(bank/file)==digest
    inp=S.P.ReceiverInput(**S.P.arrays(bank/'input.npz'))
    cfg=protocol['configuration'];obj=S.receiver(cfg)
    original=obj.base.model;evidence=obj.base.evidence
    path=S.OUT/'models/correlation/best.pt'
    assert S.P.sha(path)==S.P.read(S.OUT/'FROZEN_MODELS.json')['models']['correlation']
    modes=dict(mean_only=(True,False,False),variance_only=(False,True,False),
               evidence_only=(False,False,True),mean_and_evidence=(True,False,True))
    S.P.save(output/'PROTOCOL.json',dict(case=case,model='correlation',enabled_components=modes,
        selection='Post-hoc choice of the first failed high-load configuration; no generalization or acceptance claim.',
        fitting=False,iterations=300,source_sha256=S.P.sha(__file__),
        original_protocol_sha256=S.P.sha(S.OUT/'PROTOCOL.json'),checkpoint_sha256=S.P.sha(path)))
    rows=[]
    for name,enabled in modes.items():
        model=S.Calibration('correlation');model.load_state_dict(torch.load(path,weights_only=False)['state_dict'])
        adapter=Components(original,evidence,model,enabled)
        obj.base.model=adapter;obj.base.evidence=S.CalibratedEvidence(adapter)
        dest=output/name;snaps=[];started=time.monotonic()
        def observer(row,state,*unused):
            if row['iteration'] in (1,5,10,20,30,60,120,180,240,300):
                snaps.append((row['iteration'],dict(estimate=(state.mean*cfg['scale']).copy(),
                    probabilities=state.activity.copy(),activity_decision=(state.activity>=.5).copy())))
            if row['iteration']%100==0:
                print('COMPONENT',name,row['iteration'],round(time.monotonic()-started,1),flush=True)
        try:
            prediction,record=obj.infer(inp,observer=observer)
            assert all(np.isfinite(x).all() for x in prediction.values())
            S.P.save(dest/'record.json',record);S.P.save_arrays(dest/'prediction.npz',prediction)
            truth=S.P.arrays(bank/'truth.npz')
            bad=[r for r in record['trace'] if r['unsupported_users']]
            result=dict(variant=name,status='COMPLETE',metrics=S.P.score_arrays(prediction,truth),
                unsupported_iterations=len(bad),first_unsupported=bad[0]['iteration'] if bad else None,
                maximum_query_variance=max(r['query_variance_min'] for r in record['trace']),
                trace=[dict(iteration=i,**S.P.score_arrays(x,truth)) for i,x in snaps],seconds=record['seconds'])
            del truth,snaps
        except Exception:
            result=dict(variant=name,status='FAILED',traceback=traceback.format_exc())
        S.P.save(dest/'SUMMARY.json',result);rows.append(result)
        print('FINISHED COMPONENT',name,result.get('metrics',{}).get('nmse_db'),flush=True)
    S.verify()
    S.P.save(S.RESULT/'COMPONENT_DIAGNOSIS.json',dict(case=case,post_hoc=True,
        fitting=False,results=rows,checkpoint='correlation/best.pt',
        references=[r for r in full['results'] if r['case']==case and r['variant'] in ('baseline','correlation')]))


if __name__=='__main__':
    with threadpool_limits(1):main()
