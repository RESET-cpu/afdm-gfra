"""Separate experiment namespace for a fixed, convergence-selected retry rule."""
import argparse
from copy import deepcopy
from pathlib import Path
import shutil
import time
import repair_stability_development as d
from stability_damping_retry import RetryReceiver

OLD=d.OUT
OUT=d.ROOT/'runs/stability_repair_retry_20261019'
NAME='damping_retry_fp32'
d.OUT=OUT
d.SEEDS={'development':202610191000001,'acceptance':202610193000001}


def prepare():
    if (OUT/'PROTOCOL.json').exists():return
    protocol=deepcopy(d.paired.read(OLD/'PROTOCOL.json'))
    protocol.update(created_unix=time.time(),seed_bases=d.SEEDS,
        candidate_family='Fixed order 0.1 then 0.05; both attempts use FP32, original stopping tolerances, and a 1200-iteration cap. Select the first converged attempt without reading truth. Count all attempts in runtime and iterations.',
        candidate_selection='The order uses original development evidence: 0.1 is faster and passed all 20 development cases; 0.05 is a smaller update already examined there. The previous acceptance set is rejected evidence only, and is not reused to tune this rule or validate it.',
        acceptance_exclusions={'previous_acceptance_seed_base':202610192000001,'scenes':12},
        verification='Check full GPU state reset on original development scene 1, K=100, using reverse order 0.05 then 0.1 to exercise a genuine failed attempt followed by convergence. Final policy order remains 0.1 then 0.05.',
        original_development_results_reused=True,
        acceptance_gates=dict(protocol['acceptance_gates']))
    assert not set(range(d.SEEDS['acceptance'],d.SEEDS['acceptance']+12)) & set(range(202610192000001,202610192000013))
    d.paired.save(OUT/'PROTOCOL.json',protocol)
    d.paired.save(OUT/'configs'/f'{NAME}.json',d.paired.read(OLD/'configs/damping0.1_budget1200_fp32.json'))
    shutil.copy2(OLD/'PRESERVATION.json',OUT/'PRESERVATION.json')
    shutil.copy2(OLD/'PRECISION_AUDIT.json',OUT/'PRECISION_AUDIT.json')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--split',choices=['development','acceptance'],default='development')
    parser.add_argument('--scene',type=int,default=0)
    parser.add_argument('--users',type=int,default=20)
    parser.add_argument('--method',choices=[NAME,'offgrid_sbl'],default=NAME)
    parser.add_argument('--reverse-order-check',action='store_true')
    args=parser.parse_args();prepare()
    if args.prepare:raise SystemExit(0)
    candidate=args.method
    if args.reverse_order_check:
        if args.split!='development' or (args.scene,args.users)!=(1,100):raise ValueError('Development integration check only')
        RetryReceiver.order=(.05,.1)
        candidate='damping_retry_reverse_check_fp32'
        d.paired.save(OUT/'configs'/f'{candidate}.json',d.paired.read(OUT/'configs'/f'{NAME}.json'))
    if candidate!='offgrid_sbl':d.paired.EstimatedNoiseProposedReceiver=RetryReceiver
    with d.threadpool_limits(1):d.run(args.split,args.scene,args.users,candidate)
    if candidate!='offgrid_sbl':
        folder=OUT/'evaluations'/args.split/candidate/f'scene{args.scene:03d}_users{args.users}'
        instance=RetryReceiver.last_instance
        for i,(arrays,record) in enumerate(instance.attempts):
            d.paired.save(folder/'attempts'/f'attempt{i}.json',record)
            d.paired.save_arrays(folder/'attempts'/f'attempt{i}.npz',arrays)
