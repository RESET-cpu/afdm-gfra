"""Snapshot and start the authorized training pipeline as an independent process."""
import argparse, json, os, shutil, subprocess, sys, time
from pathlib import Path
from common import ROOT, OUT, CONFIG, sha, save_json


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--resume',action='store_true');args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    manifest_path=OUT/'MANIFEST.json'
    if not args.resume:
        if manifest_path.exists():raise FileExistsError('Run already has immutable source; use --resume explicitly')
        preflight=json.loads((OUT/'PREFLIGHT.json').read_text())
        assert preflight['status']=='PASS' and preflight['selected_device']==CONFIG['device']
        experiment=Path(__file__).resolve().parent
        shutil.copytree(experiment,OUT/'source_experiment',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        shutil.copytree(ROOT/'src/afdm_jadcedd',OUT/'source_project/afdm_jadcedd',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        snapshot={str(path.relative_to(OUT)):sha(path) for directory in ('source_experiment','source_project')
                  for path in sorted((OUT/directory).rglob('*')) if path.is_file()}
        protected=['MAINLINE.json','configs/proposed.json','models/proposed/first.pt','models/proposed/second.pt','models/proposed/activity.pt']
        manifest=dict(schema='afdm-lstmp-fresh-run-v1',created=time.time(),configuration=CONFIG,
            snapshot_hashes=snapshot,protected_assets={path:sha(ROOT/path) for path in protected},
            torch_version=__import__('torch').__version__,python=sys.version,
            source_reference='arXiv:2610.17785v1; local references/lstmp_2610_17785',
            pretrained_source='None: new random NCSN++ initialization',
            selection='Pretraining validation DSM; receiver validation weighted NMSE+BCE; no test selection',
            limitations=['AFDM multiuser adaptation, not exact single-user paper reproduction',
                        'Known phase/noise first stage; estimated frontend not evaluated in this run',
                        'Widths, budgets, activity head and variance safeguards are project choices'],
            resume='Run snapshot train.py with --resume; deterministic scene order/noise, optimizer and cursor checkpointed')
        save_json(manifest_path,manifest)
    else:
        assert manifest_path.exists()
    manifest=json.loads(manifest_path.read_text())
    for path,value in manifest['snapshot_hashes'].items():
        assert sha(OUT/path)==value,path
    env=os.environ.copy();env.update(AFDM_LSTMP_ROOT=str(ROOT),PYTHONUNBUFFERED='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
    command=[sys.executable,str(OUT/'source_experiment/train.py')]+(['--resume'] if args.resume else [])
    with (OUT/'run.log').open('ab') as log:
        process=subprocess.Popen(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    # Keep the machine awake for the lifetime of this explicitly requested run.
    caffeinate=None
    if shutil.which('caffeinate'):
        caffeinate=subprocess.Popen(['caffeinate','-i','-w',str(process.pid)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True).pid
    save_json(OUT/'LAUNCH.json',dict(pid=process.pid,caffeinate_pid=caffeinate,started=time.time(),command=command,
              log=str(OUT/'run.log'),status=str(OUT/'STATUS.json'),resume=args.resume))
    print(json.dumps(dict(pid=process.pid,run_directory=str(OUT),status=str(OUT/'STATUS.json')),indent=2))


if __name__=='__main__':main()
