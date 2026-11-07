"""Keep the frozen pool, with bounded retries only for worker state I/O."""
import argparse
from contextlib import contextmanager
import json
import os
import time
from unittest.mock import patch

from evaluation.white_phase_pool_io_20261106 import run as previous

pool = previous.pool
MODULE = 'evaluation.white_phase_pool_stateio_20261107.run'
REV = pool.REV / 'state_io_recovery_20261107'
READ, WRITE = previous.READ, pool.g.write_json
ATTEMPTS, DELAY_SECONDS = 11, 0.05


def log_retry(path, operation, failures, outcome):
    event = dict(path=str(path), operation=operation, permission_errors=failures,
                 outcome=outcome, checked_unix=time.time(), pid=os.getpid())
    with (REV / f'STATE_IO_RETRIES_{os.getpid()}.jsonl').open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(event) + '\n')


def state_io(path, operation, call):
    if not previous.is_worker_state(path):
        return call()
    for attempt in range(ATTEMPTS):
        try:
            value = call()
        except PermissionError:
            if attempt == ATTEMPTS - 1:
                log_retry(path, operation, ATTEMPTS, 'EXHAUSTED')
                raise
            time.sleep(DELAY_SECONDS)
        else:
            if attempt:
                log_retry(path, operation, attempt, 'RECOVERED')
            return value


def read_state_retry(path):
    return state_io(path, 'read', lambda: READ(path))


def write_state_retry(path, value):
    return state_io(path, 'write', lambda: WRITE(path, value))


def verify():
    amendment = READ(REV / 'AMENDMENT.json')
    pool.g.checked(previous.REV / 'AMENDMENT.json', amendment['previous_io_amendment_sha256'])
    for file, digest in amendment['assets'].items():
        pool.g.checked(file, digest)
    return previous.verify()


@contextmanager
def adapter():
    # MODULE selects the new worker bootstrap and records its actual entry point;
    # worker(), execute_case(), inference and result publication remain unchanged.
    with patch.object(pool, 'MODULE', MODULE), \
            patch.object(pool, 'TOKENS', (MODULE, previous.MODULE) + pool.TOKENS), \
            patch.object(pool.g, 'read_json', read_state_retry), \
            patch.object(pool.g, 'write_json', write_state_retry):
        yield


def coordinate():
    verify()
    with adapter():
        pool.coordinate()


def worker(session, slot):
    verify()
    with adapter():
        pool.worker(session, slot)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('coordinate', 'worker', 'inspect'))
    parser.add_argument('--session')
    parser.add_argument('--slot', type=int)
    args = parser.parse_args()
    if args.command == 'coordinate':
        coordinate()
    elif args.command == 'worker':
        worker(args.session, args.slot)
    else:
        print(pool.g.require_ready())
        print(verify()['planned'])
