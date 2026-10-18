#!/usr/bin/env python3
"""Run frozen complete score denoising in the fixed L-DAMP recurrence."""
import argparse,json,sys
from pathlib import Path
import torch
from threadpoolctl import threadpool_limits
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from afdm_jadcedd.algorithm.baselines.ldamp_score.receiver import LDAMPScoreReceiver,load_configuration

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',required=True);parser.add_argument('--output',required=True)
    parser.add_argument('--config');parser.add_argument('--device',choices=['auto','cpu','mps'],default='auto')
    args=parser.parse_args();torch.set_num_threads(1)
    with threadpool_limits(1):
        result=LDAMPScoreReceiver(load_configuration(args.config),device=args.device).run(args.input,args.output)
    print(json.dumps({key:result[key] for key in ('method','status','iterations','error','seconds')},indent=2))
    return 0 if result['status']=='COMPLETE' else 2

if __name__=='__main__':raise SystemExit(main())
