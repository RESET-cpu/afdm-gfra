"""Resume unfinished white-SNR inputs with the original two frozen workers."""
import os
import time
import traceback

from evaluation.white_matched_fp32_20261105 import run as native
from utils import read_json, write_json, sha256


def main():
    plan = native.verify()
    out = native.OUT
    audit = out/'throughput_20261105'
    audit.mkdir(exist_ok=True)
    active, failed = [], []
    completed, pending = 0, []
    with (out/'RUNNING.lock').open('x') as handle:
        handle.write(str(os.getpid()))
    try:
        for position in range(6000):
            link = out/'results'/(native.tag(position)+'.json')
            if link.exists():
                saved = read_json(link)
                native.checked(saved['result'], saved['sha256'])
                if read_json(saved['result'])['status'] != 'COMPLETE':
                    raise ValueError('Incomplete existing result')
                completed += 1
            else:
                pending.append(position)
        write_json(audit/'RESUME.json', dict(pid=os.getpid(), started_unix=time.time(),
            authorization='别尝试了，就选一个差不多的快开始跑实验吧，不要耽误时间了',
            completed=completed, pending=len(pending), max_workers=2,
            unchanged_original_workers=True, shared_white_adapter_used=False,
            plan_sha256=sha256(out/'PLAN.json'), automatic_retry=False))
        cursor = 0
        began = time.time()
        while cursor < len(pending) or active:
            remaining = []
            for process, receipt in active:
                code = process.poll()
                if code is None:
                    if time.time()-receipt['started_unix'] > plan['runtime']['input_timeout_seconds']:
                        raise TimeoutError('Worker timeout; retained for inspection')
                    remaining.append((process, receipt))
                elif code:
                    failed.append(dict(receipt, exit_code=code))
                else:
                    link = read_json(out/'results'/(native.tag(receipt['position'])+'.json'))
                    native.checked(link['result'], link['sha256'])
                    if read_json(link['result'])['status'] != 'COMPLETE':
                        raise ValueError('Worker did not save a complete result')
                    completed += 1
            active = remaining
            stopped = (audit/'STOP.json').exists()
            while not failed and not stopped and cursor < len(pending) and len(active) < 2 and native.capacity(plan, active):
                active.append(native.launch_worker(pending[cursor], False, plan))
                cursor += 1
            native.status('DRAINING_FAILURE' if failed else 'DRAINING_STOP' if stopped else
                          'RUNNING' if active else 'WAITING_FOR_MEMORY', active, completed,
                          failed=len(failed), resumed=True, dispatched=completed+len(active))
            if (failed or stopped) and not active:
                native.status('FAILED' if failed else 'PAUSED', [], completed, failed=len(failed))
                return
            if time.time()-began > plan['runtime']['total_timeout_seconds']:
                raise TimeoutError('Queue exceeded total budget')
            time.sleep(.5)
        from evaluation.white_matched_fp32_20261105.report import summarize
        summarize()
        native.status('COMPLETE', [], completed, failed=0)
    except BaseException:
        write_json(audit/'RESUME_FAILURE.json', dict(traceback=traceback.format_exc(),
                   active_workers=[r for _, r in active], automatic_retry=False))
        raise
    finally:
        (out/'RUNNING.lock').unlink(missing_ok=True)


if __name__ == '__main__':
    main()
