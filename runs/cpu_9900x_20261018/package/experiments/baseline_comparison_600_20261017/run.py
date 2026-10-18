"""Resumable paired 600-scene experiment, launched only after phase qualification."""
from pathlib import Path
import sys,os,json,gzip,time,hashlib,subprocess,traceback,warnings
from collections import Counter
import numpy as np
import torch
from threadpoolctl import threadpool_limits
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OUT=ROOT/'results/baseline_comparison_600_20261017'
PHASE=ROOT/'results/phase_optimization_20261017'
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from afdm_jadcedd.algorithm import phase_estimation_optimized as phase
from afdm_jadcedd.algorithm.unknown_phase_model import UnknownPhaseInput
from afdm_jadcedd.algorithm.registry import build_receiver
from afdm_jadcedd.algorithm.baselines.baseline_noise import EstimatedNoiseBaselineReceiver
from afdm_jadcedd.algorithm.proposed_noise_candidate import EstimatedNoiseProposedReceiver
from afdm_jadcedd.experiment.unknown_phase import generate_case
from afdm_jadcedd.system.phase import phase_operator
from afdm_jadcedd.system.observation import array_sha256,ReceiverInput
from experiments.proposed_original_snr8_10_20261016.analyze import score
METHODS=['proposed','offgrid_sbl','gnn','gamp','somp']
CONFIGS={'proposed':'configs/proposed.json','offgrid_sbl':'configs/offgrid_baselines.json',
         'gnn':'configs/baselines.json','gamp':'configs/baselines.json','somp':'configs/baselines.json'}

def read(path):
 with (gzip.open(path,'rt') if str(path).endswith('.gz') else Path(path).open()) as f:return json.load(f)
def save(path,value):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 temp=path.with_name(path.name+f'.{os.getpid()}.tmp')
 with (gzip.open(temp,'wt') if path.suffix=='.gz' else temp.open('w')) as f:json.dump(value,f,ensure_ascii=False,allow_nan=False)
 os.replace(temp,path)
def arrays(path):
 with np.load(path,allow_pickle=False) as z:return dict(z)
def save_arrays(path,value):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_name(path.name+f'.{os.getpid()}.tmp')
 with temp.open('wb') as f:np.savez_compressed(f,**value)
 os.replace(temp,path)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(value):return {k:array_sha256(v) for k,v in value.items()}
def plan():return read(OUT/'PLAN.json')

def freeze(noise_mode='known'):
 if (OUT/'PLAN.json').exists():raise FileExistsError('Plan already frozen; resume existing run')
 if read(PHASE/'QUALIFICATION_STATUS.json')['status']!='PAIRED_GATES_PASSED':raise ValueError('Phase validation must pass before the 600-scene batch')
 selection=read(PHASE/'SELECTION.json')
 assert selection['source_sha256']==sha(Path(phase.__file__))
 if noise_mode not in ['known','estimated']:raise ValueError(noise_mode)
 decision=read(PHASE/'NOISE_DECISION.json')
 if decision['selected_mode']!=noise_mode:raise ValueError('Noise mode must follow the paired Proposed noise experiment')
 preflight=read(PHASE/'batch_preflight/CHECKS.json')
 if preflight['status']!='PASS' or preflight['real_receiver_runs']!=10:
  raise ValueError('All five real receivers must pass the known/estimated noise pipeline preflight')
 public=read(PHASE/'PUBLIC_INTEGRATION.json')
 if public['status']!='PASS' or public['noise_mode']!=noise_mode:
  raise ValueError('Selected public entry must pass its native-output comparisons')
 if read(OUT/'PREFLIGHT.json')['status']!='PASS':raise ValueError('600-scene extension checks must pass')
 import platform,scipy
 sources=(list((ROOT/'src/afdm_jadcedd').rglob('*.py'))+list(HERE.glob('*'))
          +list((ROOT/'configs').rglob('*.json'))
          +[ROOT/'experiments/proposed_original_snr8_10_20261016/analyze.py'])
 source_hashes={str(p.relative_to(ROOT)):sha(p) for p in sources if p.is_file()}
 weights={str(p.relative_to(ROOT)):sha(p) for directory in ['models/proposed','models/gnn'] for p in (ROOT/directory).rglob('*') if p.is_file()}
 spec=dict(scenes=600,seeds=list(range(202610172000001,202610172000601)),snr_db=list(range(-4,9,2)),methods=METHODS,
   configurations=CONFIGS,scale=read(ROOT/'configs/proposed.json')['scale'],users=40,frames=16,antennas=16,
   noise_mode=noise_mode,phase_mode='estimated',phase_controls=selection['controls'],phase_selection_sha256=sha(PHASE/'SELECTION.json'),
   qualification_status_sha256=sha(PHASE/'QUALIFICATION_STATUS.json'),
   noise_decision_sha256=sha(PHASE/'NOISE_DECISION.json'),
   real_pipeline_preflight_sha256=sha(PHASE/'batch_preflight/CHECKS.json'),
   public_integration_sha256=sha(PHASE/'PUBLIC_INTEGRATION.json'),
   expected_conditions=4200,expected_receiver_runs=21000,full_prediction_scenes=[0,200],
   primary_metrics=['full_channel_nmse','aer'],threads_per_worker=1,proposed_device='auto',proposed_workers=2,
   source_sha256=source_hashes,weight_sha256=weights,created_unix=time.time(),
   environment=dict(python=sys.version,numpy=np.__version__,scipy=scipy.__version__,torch=torch.__version__,
                    platform=platform.platform(),mps_available=torch.backends.mps.is_available()),
   pairing='Same physical scene, original pilot and standard noise across SNR; same phase/operator across methods',
   storage='All scalar/vector outputs and per-user error energies; complete native arrays for scene000 and scene200; full-output hashes for every run')
 spec['reused_prefix']=dict(scenes=200, source='results/baseline_comparison_200_20261017', plan_sha256=sha(ROOT/'results/baseline_comparison_200_20261017/PLAN.json'))
 spec['extension_preflight_sha256']=sha(OUT/'PREFLIGHT.json')
 OUT.mkdir(parents=True,exist_ok=True)
 save(OUT/'PLAN.json',spec)
 import shutil
 for relative in source_hashes:
  target=OUT/'sources'/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/relative,target)
 print('FROZEN',spec['expected_receiver_runs'],flush=True)

def verify_sources():
 spec=plan()
 for name,expected in {**spec['source_sha256'],**spec['weight_sha256']}.items():
  if sha(ROOT/name)!=expected:raise ValueError('Frozen experiment source or weight changed: '+name)
 return spec

def prepare_scene(scene,spec):
 folder=OUT/'scenes'/f'scene{scene:03d}'
 if (folder/'READY.json').exists():return folder
 public,truth,meta=generate_case(spec['seeds'][scene],0,spec['scale'])
 clean=np.einsum('qkn,kmrn->qmr',phase_operator(public['pilot'],truth['phase_slopes']),truth['channel'],optimize=False)
 power=float(np.mean(abs(clean)**2));epsilon=(public['observation']-clean)/np.sqrt(public['noise_variance'])
 save_arrays(folder/'truth.npz',truth)
 save_arrays(folder/'pairing.npz',dict(pilot=public['pilot'],clean=clean,standard_noise=epsilon))
 save(folder/'generation.json.gz',meta)
 save(folder/'READY.json',dict(seed=spec['seeds'][scene],power=power,activity_prior=float(public['activity_prior']),
   truth_sha256=sha(folder/'truth.npz'),pairing_sha256=sha(folder/'pairing.npz')))
 return folder

def public_input(folder,snr):
 pairing=arrays(folder/'pairing.npz');meta=read(folder/'READY.json')
 assert sha(folder/'pairing.npz')==meta['pairing_sha256']
 sigma=meta['power']*10**(-snr/10)
 return UnknownPhaseInput(pairing['clean']+np.sqrt(sigma)*pairing['standard_noise'],pairing['pilot'],sigma,meta['activity_prior'])

def capture(call):
 counts=Counter()
 with warnings.catch_warnings():
  warnings.simplefilter('always',RuntimeWarning)
  old=warnings.showwarning
  warnings.showwarning=lambda message,category,filename,lineno,*a,**kw:counts.update([(category.__name__,str(message),filename,lineno)])
  try:value=call()
  finally:warnings.showwarning=old
 return value,[dict(category=k[0],message=k[1],file=k[2],line=k[3],count=v) for k,v in counts.items()]

def infer_case(scene,snr,method,solver,spec):
 parent=OUT/'scenes'/f'scene{scene:03d}';folder=parent/f'snr{snr:+03d}'
 target=folder/(method+'.metrics.json')
 if target.exists():
  saved=read(target)
  if saved['status']!='COMPLETE':raise ValueError('Preserved failed attempt requires diagnosis: '+str(target))
  assert saved['compact_sha256']==sha(folder/(method+'.compact.npz'))
  return
 inp=public_input(parent,snr);ready=read(folder/'READY.json')
 if digest(inp.arguments())!=ready['public_array_sha256']:raise ValueError('Observation pairing changed')
 assert sha(folder/'phase.npz')==ready['phase_sha256']
 slopes=arrays(folder/'phase.npz')['phase_slopes'];conditional=inp.at_estimated_phase(slopes)
 if spec['noise_mode']=='estimated':
  conditional=ReceiverInput(conditional.observation,conditional.operator,1.,conditional.activity_prior)
 started=time.perf_counter()
 try:
  (result,record),notices=capture(lambda:solver.infer(conditional))
  if not all(np.isfinite(a).all() for a in result.values()):raise FloatingPointError('Nonfinite receiver output')
  # Ground truth is loaded only after the receiver has returned.
  truth=arrays(parent/'truth.npz');metrics=score(result,truth)
  compact={k:v for k,v in result.items() if np.asarray(v).ndim<=1}
  compact.update(per_user_error=np.asarray(metrics['per_user_error']),truth_activity=truth['activity'])
  save_arrays(folder/(method+'.compact.npz'),compact)
  if scene in spec['full_prediction_scenes']:save_arrays(folder/(method+'.prediction.npz'),result)
  record.update(phase_sha256=ready['phase_sha256'],output_array_sha256=digest(result),noise_mode=spec['noise_mode'],benchmark_truth_used_in_inference=False)
  save(folder/(method+'.record.json.gz'),record);save(folder/(method+'.warnings.json'),notices)
  save(target,dict(status='COMPLETE',scene=scene,snr=snr,method=method,seconds=time.perf_counter()-started,
     metrics=metrics,compact_sha256=sha(folder/(method+'.compact.npz')),shared_phase_sha256=ready['phase_sha256'],
     phase_seconds=ready['phase_seconds'],receiver_seconds=record['seconds'],iterations=record.get('iterations')))
 except Exception as error:
  save(target,dict(status='FAILED',scene=scene,snr=snr,method=method,error=repr(error),traceback=traceback.format_exc()))
  raise
 print(json.dumps(dict(scene=scene,snr=snr,method=method,status='COMPLETE')),flush=True)

def producer():
 spec=verify_sources();controls=phase.Controls(**spec['phase_controls'])
 receivers={m:(EstimatedNoiseBaselineReceiver(m,config=ROOT/CONFIGS[m]) if spec['noise_mode']=='estimated' else build_receiver(m,config=ROOT/CONFIGS[m])) for m in METHODS if m!='proposed'}
 save(OUT/'producer.json',dict(status='RUNNING',pid=os.getpid()))
 try:
  for scene in range(spec['scenes']):
   parent=prepare_scene(scene,spec)
   for snr in spec['snr_db']:
    folder=parent/f'snr{snr:+03d}'
    if not (folder/'READY.json').exists():
     inp=public_input(parent,snr)
     (values,record),notices=capture(lambda:phase.estimate(inp,controls))
     save_arrays(folder/'phase.npz',values);save(folder/'phase.json.gz',record);save(folder/'phase.warnings.json',notices)
     save(folder/'READY.json',dict(public_array_sha256=digest(inp.arguments()),phase_sha256=sha(folder/'phase.npz'),phase_seconds=record['seconds']))
    for method,solver in receivers.items():infer_case(scene,snr,method,solver,spec)
    save(OUT/'producer.json',dict(status='RUNNING',pid=os.getpid(),scene=scene,snr=snr))
  save(OUT/'producer.json',dict(status='COMPLETE',conditions=4200,receiver_runs=16800))
 except BaseException as e:
  save(OUT/'producer.json',dict(status='FAILED',error=repr(e)));raise

def proposed(rank=0):
 spec=verify_sources()
 workers=spec['proposed_workers']
 if not 0<=rank<workers:raise ValueError('Invalid Proposed worker rank')
 state_path=OUT/f'proposed_{rank}.json'
 completed=0
 solver=(EstimatedNoiseProposedReceiver(read(ROOT/CONFIGS['proposed']),device=spec['proposed_device'])
         if spec['noise_mode']=='estimated' else build_receiver('proposed',config=ROOT/CONFIGS['proposed'],device=spec['proposed_device']))
 for scene in range(rank,spec['scenes'],workers):
  for snr in spec['snr_db']:
   ready=OUT/'scenes'/f'scene{scene:03d}'/f'snr{snr:+03d}'/'READY.json'
   while not ready.exists():
    state=read(OUT/'producer.json') if (OUT/'producer.json').exists() else {}
    if state.get('status') in ['FAILED','COMPLETE']:raise RuntimeError('Producer ended without required observation')
    time.sleep(2)
   save(state_path,dict(status='RUNNING',pid=os.getpid(),rank=rank,scene=scene,snr=snr))
   infer_case(scene,snr,'proposed',solver,spec)
   completed+=1
 save(state_path,dict(status='COMPLETE',rank=rank,receiver_runs=completed))

def run():
 spec=verify_sources()
 processes=[]
 roles=[('producer',['producer'])]+[(f'proposed_{rank}',['proposed',str(rank)]) for rank in range(spec['proposed_workers'])]
 save(OUT/'producer.json',dict(status='STARTING'))
 for role,arguments in roles:
  log=(OUT/(role+'.log')).open('a')
  p=subprocess.Popen([sys.executable,'-B',str(Path(__file__)),*arguments],stdout=log,stderr=subprocess.STDOUT)
  processes.append(p)
 save(OUT/'RUN.json',dict(status='RUNNING',pid=os.getpid(),children=[p.pid for p in processes],
  roles=[role for role,_ in roles],started_unix=time.time()))
 while any(p.poll() is None for p in processes):
  failed=[p.returncode for p in processes if p.poll() not in [None,0]]
  if failed:
   for p in processes:
    if p.poll() is None:p.terminate()
   save(OUT/'RUN.json',dict(status='FAILED',exit_codes=[p.wait() for p in processes]));raise SystemExit(1)
  time.sleep(2)
 exit_codes=[p.wait() for p in processes]
 if any(exit_codes):
  save(OUT/'RUN.json',dict(status='FAILED',exit_codes=exit_codes));raise SystemExit(1)
 verify_sources()
 save(OUT/'RUN.json',dict(status='INFERENCE_COMPLETE',receiver_runs=21000,finished_unix=time.time()))

if __name__=='__main__':
 torch.set_num_threads(1)
 with threadpool_limits(1):
  if sys.argv[1]=='freeze':freeze(sys.argv[2] if len(sys.argv)>2 else 'known')
  elif sys.argv[1]=='producer':producer()
  elif sys.argv[1]=='proposed':proposed(int(sys.argv[2]) if len(sys.argv)>2 else 0)
  elif sys.argv[1]=='run':run()
  else:raise ValueError(sys.argv[1])
