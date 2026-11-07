"""Inspect the exact live identities of a follow-up, including Windows launchers.

Run outside the filesystem sandbox when the experiment was launched outside it;
an isolated process view is not evidence that the real process has exited.
"""
import argparse
import time
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'src'))
from evaluation.white_followup_20261107 import receivers as r

parser = argparse.ArgumentParser()
parser.add_argument('stage', choices=r.STAGES)
parser.add_argument('--record', action='store_true')
args = parser.parse_args()
folder = r.stage_folder(args.stage)
start = r.read_json(folder/'START.json')
status = r.state_read(folder/'STATUS.json')
workers = []
for path in (folder/'sessions'/start['session']).glob('*/STATE.json'):
    state = r.state_read(path)
    workers.append(dict(path=str(path), state=state, identity_live=r.is_live(state)))
result = dict(checked_unix=time.time(), coordinator=start,
              coordinator_identity_live=r.is_live(start), status=status, workers=workers,
              failure=r.read_json(folder/'FAILURE.json') if (folder/'FAILURE.json').exists() else None,
              stop_exists=(folder/'STOP.json').exists(), lock_exists=(folder/'RUNNING.lock').exists())
if args.record:
    destination = folder/'monitoring'/f"CHECK_{time.time_ns()}.json"
    destination.parent.mkdir(exist_ok=True)
    r.write_json(destination, result)
    print('receipt',destination)
print(result)
