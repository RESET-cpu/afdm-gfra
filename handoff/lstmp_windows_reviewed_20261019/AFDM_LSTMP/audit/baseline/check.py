"""Two-iteration packaging smoke check; not a baseline performance experiment."""
from pathlib import Path
import hashlib,json,os,sys
import numpy as np
import torch
from threadpoolctl import threadpool_limits
ROOT=Path(__file__).resolve().parents[2]
os.environ['AFDM_LSTMP_ROOT']=str(ROOT)
sys.path.insert(0,str(ROOT/'runs/lstmp_fresh_20261019/source_experiment'))
from common import CONFIG
from afdm_jadcedd.algorithm.proposed.receiver import Receiver
from afdm_jadcedd.system.observation import ReceiverInput
from afdm_jadcedd.experiment.generate import generate_case
torch.set_num_threads(1);threadpool_limits(1)
config_path=ROOT/'configs/proposed.json'
before=hashlib.sha256(config_path.read_bytes()).hexdigest()
config=json.loads(config_path.read_text())
config['ep'].update(iterations=2,min_iterations=2)  # In-memory smoke cap only.
seed=CONFIG['seed']+85000000
inputs,_,_=generate_case(seed,0.,1.)
model=Receiver(config,device='cpu')
output,record=model.infer(ReceiverInput(inputs['observation'],inputs['operator'],inputs['noise_variance'],inputs['activity_prior']))
assert all(np.isfinite(v).all() for v in output.values())
assert record['iterations']==2 and record['first_score_calls']>0 and record['second_score_calls']>0
assert hashlib.sha256(config_path.read_bytes()).hexdigest()==before
report=dict(status='PASS',scope='Frozen baseline load and two-iteration packaging smoke check only; not performance evaluation',
            debug_seed=seed,iterations=record['iterations'],first_score_calls=record['first_score_calls'],
            second_score_calls=record['second_score_calls'],classifier_calls=record['classifier_calls'],
            finite_outputs=True,configuration_file_unchanged=True,formal_training_resumed=False)
(Path(__file__).parent/'RESULTS.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
