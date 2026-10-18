"""Run frozen L-DAMP followed by an explicitly configured rank-one output approximation."""
import argparse,json,sys,warnings
from pathlib import Path
import numpy as np
import torch
from threadpoolctl import threadpool_limits
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'experiments/ldamp_structure_20261015'))
from structured_receiver import Receiver
from afdm_jadcedd.system.observation import load_input
from afdm_jadcedd.utils import sha256,write_json


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--config',type=Path,default=ROOT/'configs/ldamp_output_tsvd.json')
    parser.add_argument('--device',default='mps',choices=['cpu','mps'])
    parser.add_argument('--activity-rule',default='original',choices=['calibrated','original'],
        help='Use calibrated projected-energy decisions or preserve the original receiver decisions')
    args=parser.parse_args()
    if args.output.suffix!='.npz' or args.output.exists() or args.output.with_suffix('.json').exists():raise ValueError('Fresh .npz and .json output paths required')
    config=json.loads(args.config.read_text());torch.set_num_threads(1)
    receiver=Receiver(config,args.device)
    if receiver.readout is None:raise ValueError('Calibrated activity readout required')
    with warnings.catch_warnings(record=True) as caught,threadpool_limits(1):
        warnings.simplefilter('always',RuntimeWarning)
        arrays,record,base_arrays,_=receiver.infer_pair(load_input(args.input))
    if args.activity_rule=='original':
        arrays['activity_score']=base_arrays['activity_score'].copy()
        arrays['activity_decision']=base_arrays['activity_decision'].copy()
        record['activity_statistic']='original_channel_frobenius_energy'
        record['activity_rule_configuration']=config['base_configuration']['readout']
    else:
        record['activity_rule_configuration']=config['readout']
    record['activity_rule']=args.activity_rule
    args.output.parent.mkdir(parents=True,exist_ok=True);np.savez_compressed(args.output,**arrays)
    record.update(input_sha256=sha256(args.input),output_sha256=sha256(args.output),config_sha256=sha256(args.config),
        runner_sha256=sha256(Path(__file__)),
        warnings=[dict(message=str(w.message),filename=w.filename,line=w.lineno) for w in caught])
    write_json(args.output.with_suffix('.json'),record)
    print(json.dumps(dict(status='COMPLETE',output=str(args.output),seconds=record['seconds'])))


if __name__=='__main__':main()
