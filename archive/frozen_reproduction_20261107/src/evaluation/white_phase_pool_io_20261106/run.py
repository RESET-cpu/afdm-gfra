"""Retry only transient PermissionError when the coordinator reads worker state."""
import argparse
import json
import os
from pathlib import Path
import time
from unittest.mock import patch

from evaluation.white_phase_pool_20261106 import run as pool

MODULE = 'evaluation.white_phase_pool_io_20261106.run'
REV = pool.REV / 'io_recovery_20261106'
READ = pool.g.read_json
ATTEMPTS = 11
DELAY_SECONDS = 0.05


def is_worker_state(path):
    path = Path(path).resolve()
    try:
        relative = path.relative_to((pool.REV / 'sessions').resolve())
    except ValueError:
        return False
    parts = relative.parts
    return (len(parts) == 3 and parts[0].isdigit()
            and parts[1].startswith('worker') and parts[1][6:].isdigit()
            and parts[2] == 'STATE.json')


def log_retry(path, failures, outcome):
    event = dict(path=str(path), permission_errors=failures, outcome=outcome,
                 checked_unix=time.time(), coordinator_pid=os.getpid())
    with (REV / f'STATE_READ_RETRIES_{os.getpid()}.jsonl').open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(event) + '\n')


def read_state_retry(path):
    if not is_worker_state(path):
        return READ(path)
    for attempt in range(ATTEMPTS):
        try:
            value = READ(path)
        except PermissionError:
            if attempt == ATTEMPTS - 1:
                log_retry(path, ATTEMPTS, 'EXHAUSTED')
                raise
            time.sleep(DELAY_SECONDS)
        else:
            if attempt:
                log_retry(path, attempt, 'RECOVERED')
            return value


def verify():
    amendment = READ(REV / 'AMENDMENT.json')
    pool.g.checked(pool.REV / 'AMENDMENT.json', amendment['runtime_pool_amendment_sha256'])
    pool.g.checked(pool.OUT / 'PLAN.json', amendment['original_plan_sha256'])
    for file, digest in amendment['assets'].items():
        pool.g.checked(file, digest)
    return pool.verify()


def coordinate():
    verify()
    # Include this coordinator in duplicate detection; workers still use the
    # original, hash-bound module and unchanged numerical validation.
    with patch.object(pool, 'TOKENS', (MODULE,) + pool.TOKENS), \
            patch.object(pool.g, 'read_json', read_state_retry):
        pool.coordinate()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('coordinate', 'inspect'))
    args = parser.parse_args()
    if args.command == 'coordinate':
        coordinate()
    else:
        print(pool.g.require_ready())
        print(verify()['planned'])
