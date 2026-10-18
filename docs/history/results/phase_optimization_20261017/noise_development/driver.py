"""Paired Proposed noise-source check with the optimized phase held fixed."""
import sys,json,time,gzip,warnings
from pathlib import Path
import numpy as np
import torch
from threadpoolctl import threadpool_limits
from study import ROOT,OUT,SAVED,save,read,sha
sys.path.insert(0,str(ROOT))
from afdm_jadcedd.algorithm.proposed_noise_candidate import EstimatedNoiseProposedReceiver
from afdm_jadcedd.algorithm.unknown_phase_model import load_input
from afdm_jadcedd.system.observation import ReceiverInput,array_sha256
from experiments.proposed_original_snr8_10_20261016.analyze import score

def run(panel):
 if panel=='development':
  cases=[f'scene{k:03d}/snr{s:+03d}' for k in range(3) for s in [-4,0,6,10]]
  source=SAVED
 else:
  source=SAVED if panel=='regression' else OUT/'fresh'
  cases=[r['case'] for r in json.loads((OUT/(panel+'_validation')/'PHASE_ROWS.json').read_text())]
 dest=OUT/('noise_'+panel)
 spec=dict(panel=panel,cases=cases,method='Proposed with spatial covariance MDL noise estimate',
  input_fields_used=['observation','estimated_operator','activity_prior'],supplied_variance_used=False,
  phase_held_fixed=True,thresholds_unchanged=True,networks_unchanged=True,
  noise_implementation_sha256=sha(ROOT/'src/afdm_jadcedd/algorithm/proposed_noise_candidate.py'))
 if (dest/'PLAN.json').exists():assert json.loads((dest/'PLAN.json').read_text())==spec
 else:save(dest/'PLAN.json',spec)
 solver=EstimatedNoiseProposedReceiver(json.loads((ROOT/'configs/proposed.json').read_text()))
 rows=[]
 torch.set_num_threads(1)
 with threadpool_limits(1):
  for case in cases:
   folder=dest/case
   if (folder/'metrics.json').exists():rows.append(json.loads((folder/'metrics.json').read_text()));continue
   inp=load_input(source/'inputs'/case/'input.npz')
   if panel=='development':
    phase_path=OUT/'local_more_development'/case/'local_3/phase.npz'
    known_path=OUT/'local_more_development'/case/'local_3/proposed/metrics.json'
    known=json.loads(known_path.read_text())['metrics']
   else:
    phase_path=OUT/(panel+'_validation')/case/'candidate_phase.npz'
    known_path=OUT/(panel+'_validation')/case/'proposed/metrics.json'
    known=json.loads(known_path.read_text())['metrics']['candidate']
   conditional=inp.at_estimated_phase(read(phase_path)['phase_slopes'])
   # A placeholder is supplied; the wrapper must estimate variance from Y.
   blind=ReceiverInput(conditional.observation,conditional.operator,1.,conditional.activity_prior)
   with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter('always',RuntimeWarning)
    arrays,record=solver.infer(blind)
   assert all(np.isfinite(a).all() for a in arrays.values())
   truth=read(source/'inputs'/case.split('/')[0]/'truth.npz')
   metrics=score(arrays,truth)
   folder.mkdir(parents=True,exist_ok=True)
   compact={k:v for k,v in arrays.items() if np.asarray(v).ndim<=1}
   compact.update(per_user_error=np.asarray(metrics['per_user_error']),truth_activity=truth['activity'])
   np.savez_compressed(folder/'compact.npz',**compact)
   if case.startswith('scene000/'):
    np.savez_compressed(folder/'prediction.npz',**arrays)
   record['output_array_sha256']={k:array_sha256(a) for k,a in arrays.items()}
   with gzip.open(folder/'receiver.json.gz','wt') as stream:json.dump(record,stream)
   save(folder/'warnings.json',list(dict.fromkeys(str(w.message) for w in caught)))
   row=dict(case=case,metrics=metrics,known_noise_metrics=known,
     delta_nmse_db=metrics['nmse_db']-known['nmse_db'],
     noise_estimate=float(arrays['noise_variance_estimate']),true_variance_offline_only=float(inp.noise_variance),
     noise_ratio=float(arrays['noise_variance_estimate']/inp.noise_variance),
     phase_sha256=sha(phase_path),known_noise_reference_sha256=sha(known_path),
     changed_decisions=int(np.count_nonzero(np.asarray(metrics['decisions'])!=np.asarray(known['decisions']))))
   save(folder/'metrics.json',row);rows.append(row);save(dest/'ROWS.json',rows)
   print(json.dumps({k:v for k,v in row.items() if k not in ['metrics','known_noise_metrics','phase_sha256','known_noise_reference_sha256']}),flush=True)
 summary=[]
 for snr in sorted({int(r['case'].split('/snr')[1]) for r in rows}):
  group=[r for r in rows if r['case'].endswith(f'snr{snr:+03d}')]
  delta=float(10*np.log10(sum(r['metrics']['full_error'] for r in group)/sum(r['known_noise_metrics']['full_error'] for r in group)))
  md=sum(r['metrics']['misses']-r['known_noise_metrics']['misses'] for r in group)
  fa=sum(r['metrics']['false_alarms']-r['known_noise_metrics']['false_alarms'] for r in group)
  summary.append(dict(snr=snr,cases=len(group),delta_nmse_db=delta,delta_misses=md,delta_false_alarms=fa,
   delta_aer_percentage_points=100*(md+fa)/(40*len(group)),mean_noise_ratio=float(np.mean([r['noise_ratio'] for r in group])),
   passed=bool(delta<=.15 and (md+fa)/(40*len(group))<=.001)))
 save(dest/'SUMMARY.json',summary);print(json.dumps(summary),flush=True)
if __name__=='__main__':run(sys.argv[1])
