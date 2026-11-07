"""One command for the maintained evaluation suite; execution is always explicit."""
import argparse
import json
import sys
from pathlib import Path

from . import suite, experiments
from utils import read_json, write_json, sha256

DESCRIPTIONS = {name: experiments.get(name).DESCRIPTION for name in experiments.NAMES}


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == 'convergence':
        from .convergence_20261105.run import main as convergence
        return convergence(argv[1:])
    if argv and argv[0] in DESCRIPTIONS:
        return experiments.get(argv[0]).main(argv[1:])
    parser = argparse.ArgumentParser(description='White-network mainline experiment suite')
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('list', help='List experiments without loading models')
    evaluate = commands.add_parser('evaluate', help='Score a saved prediction against its paired truth')
    evaluate.add_argument('--estimate', type=Path, required=True)
    evaluate.add_argument('--truth', type=Path, required=True)
    prepare = commands.add_parser('prepare', help='Freeze all default plans; do not run inference')
    prepare.add_argument('--output', type=Path, default=suite.DEFAULT_OUTPUT)
    prepare.add_argument('--device', choices=['cuda', 'cpu'], default='cuda')
    inspect = commands.add_parser('inspect', help='Verify all default plans and assets; no inference')
    inspect.add_argument('--output', type=Path, default=suite.DEFAULT_OUTPUT)
    commands.add_parser('convergence', help='Historical convergence entry; adopted 30-scene run is closed', add_help=False)
    for name, description in DESCRIPTIONS.items():
        experiment = commands.add_parser(name, help=description, add_help=False)
        experiment.add_argument('arguments', nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    if args.command == 'evaluate':
        from .storage import arrays
        from evaluation.metrics import score_arrays
        output, truth = arrays(args.estimate), arrays(args.truth)
        if 'activity_decision' not in output:
            if 'probabilities' not in output:
                parser.error('Prediction requires an activity decision or calibrated probabilities')
            output['activity_decision'] = output['probabilities'] >= .5
        metrics = score_arrays(output, truth)
        metrics['aer'] = (metrics['misses']+metrics['false_alarms'])/len(truth['activity'])
        print(json.dumps(metrics, ensure_ascii=False))
        return 0
    if args.command == 'list':
        print('white_followup             STAGED             Authorized white-network replacements; explicit stage and adoption gate')
        print('convergence                CLOSED             Adopted 30-scene results; historical entry retained')
        for name, description in DESCRIPTIONS.items():
            _, config = suite.experiment_config(name)
            state = 'ENABLED' if config['execution_status'] == 'READY' else config['execution_status']
            print(f"{name:26} {state:18} {description} | {', '.join(config['methods'])}")
        return 0
    if args.command in DESCRIPTIONS:
        return experiments.get(args.command).main(args.arguments)
    entries = []
    for name in DESCRIPTIONS:
        out = args.output / name
        if args.command == 'prepare' and not (out/'PLAN.json').exists():
            suite.main(name, ['plan', '--output', str(out), '--device', args.device])
        suite.main(name, ['inspect', '--output', str(out)])
        plan = read_json(out/'PLAN.json')
        entries.append(dict(experiment=name, status=plan['execution_status'], scenes=plan['scene_count'],
                            methods=plan['methods'], plan=str((out/'PLAN.json').resolve()),
                            sha256=sha256(out/'PLAN.json')))
    if args.command == 'prepare':
        write_json(args.output/'READINESS.json', dict(status='READY', inference_started=False, entries=entries))
    print(json.dumps(dict(status='PASSED', plans=len(entries),
                         enabled=sum(e['status']=='READY' for e in entries))))
    return 0
