"""Launch one declared evaluation, retain logs, enforce timeout, never retry."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from project import ROOT
from utils import write_json, read_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    logs = out.with_name(out.name+'_launch')
    logs.mkdir(parents=True, exist_ok=False)
    config = read_json(ROOT/'src/configs/experiments/colored_denoising_20261025.json')
    command = [sys.executable, '-B', '-u', '-m', 'evaluation.colored_noise_experiment_20261025',
               '--output', str(out), '--scenes', str(config['scenes']),
               '--receiver-cases', str(config['receiver_cases'])]
    env = dict(os.environ, PYTHONPATH=str(ROOT/'src'), PYTHONIOENCODING='utf-8')
    started = time.time()
    with (logs/'stdout.log').open('w', encoding='utf-8') as stdout, (logs/'stderr.log').open('w', encoding='utf-8') as stderr:
        process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=stdout, stderr=stderr,
                                   creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
        write_json(logs/'LAUNCH.json', dict(supervisor_pid=os.getpid(), worker_pid=process.pid,
            command=command, started_unix=started, hard_timeout_seconds=config['hard_timeout_seconds'],
            automatic_retry=False, output=str(out)))
        while process.poll() is None:
            elapsed = time.time()-started
            write_json(logs/'HEARTBEAT.json', dict(worker_alive=True, worker_pid=process.pid,
                       updated_unix=time.time(), elapsed_seconds=elapsed))
            if elapsed > config['hard_timeout_seconds']:
                if os.name=='nt':
                    subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'], capture_output=True, check=False)
                else:
                    process.kill()
                process.wait()
                write_json(logs/'EXIT.json', dict(status='TIMEOUT', exit_code=process.returncode, elapsed_seconds=elapsed))
                return 124
            time.sleep(30)
    write_json(logs/'EXIT.json', dict(status='EXITED', exit_code=process.returncode, elapsed_seconds=time.time()-started))
    return process.returncode


if __name__ == '__main__':
    raise SystemExit(main())
