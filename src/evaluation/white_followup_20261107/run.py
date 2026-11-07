"""Explicit public entry for the authorized staged white-network replacements."""
import argparse
import json
from .common import OUT
from utils import read_json


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['inspect','prepare','coordinate','summarize'])
    parser.add_argument('--stage',choices=['channel_denoising','pilot_frames','user_count','activity_probability','cross_channel'])
    args=parser.parse_args(argv)
    if args.command=='inspect':
        from project import ROOT
        stages=[]
        for name in read_json(OUT/'REQUEST.json')['sequence']:
            folder=ROOT/f'result/{name}/data/white_mainline_500_20261107'
            stages.append(dict(stage=name,status=read_json(folder/'STATUS.json') if (folder/'STATUS.json').exists() else 'NOT_STARTED',
                               adopted=(folder/'ADOPTION.json').exists()))
        print(json.dumps(stages,ensure_ascii=False,indent=2));return 0
    if args.stage is None:parser.error('--stage is required for execution')
    if args.stage=='channel_denoising':
        from . import denoising
        if args.command=='prepare':denoising.prepare()
        elif args.command=='coordinate':denoising.run()
        else:denoising.summarize(denoising.verify_plan(denoising.DEST))
    else:
        from .receivers import main as receivers
        return receivers([args.command,'--stage',args.stage])
    return 0


if __name__=='__main__':raise SystemExit(main())
