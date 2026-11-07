"""Prepare an independently recorded, validated CUDA-graph continuation."""
import argparse
import json
from pathlib import Path
import shutil
import train_proposed_50000 as training


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--from-run',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--validation',type=Path,required=True)
    args=parser.parse_args()
    parent,output=args.from_run.resolve(),args.output.resolve()
    if not output.is_relative_to(training.ROOT/'runs'):
        raise ValueError('Use an independent runs directory')
    validation=json.loads(args.validation.read_text())
    assert validation['deterministic_validation']
    assert all(row['pass'] for rows in validation['numerical'].values() for row in rows)
    assert {'current','current_repeat','graph'} <= validation['numerical'].keys()
    assert Path(validation['checkpoint']).resolve()==parent/'model/first/last.pt'
    training.prepare_cuda_continuation(output,parent)
    config=training.sizes.read(output/'training.json')
    config['cuda_execution']['first']['cuda_graph']=True
    config['cuda_execution']['validation_execution_unchanged']=True
    training.sizes.save(output/'training.json',config)
    plan=training.sizes.read(output/'PLAN.json')
    plan['configuration_sha256']=training.sizes.sha(output/'training.json')
    plan['source_sha256'][training.sizes.relative(Path(__file__))]=training.sizes.sha(__file__)
    plan['cuda_graph_validation']=dict(path=training.sizes.relative(args.validation.resolve()),
        sha256=training.sizes.sha(args.validation),
        note='Deterministic diagnostic only. Production retains previous backend settings. Nondeterministic comparisons are retained separately.')
    training.sizes.save(output/'PLAN.json',plan)
    if (parent/'SMALL_MODEL.json').exists():
        shutil.copy2(parent/'SMALL_MODEL.json',output/'SMALL_MODEL.json')
    training.verify(output)
    print('PASS: independent continuation prepared')


if __name__=='__main__':
    main()
