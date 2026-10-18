"""Run all authorized stages, then verify identities and exact epoch budgets."""
from pathlib import Path
import fcntl
import json
import os
import subprocess
import sys
import time
import traceback

RUN = Path(__file__).resolve().parent
sys.path.insert(0, str(RUN/'runtime/src'))
from afdm_jadcedd.utils import sha256
from afdm_jadcedd.experiment.training.proposed.auxiliary import atomic_json
from afdm_jadcedd.experiment.training.proposed.cli import main as train


def main():
    # A second invocation must not write the same checkpoints concurrently.
    lock = (RUN/'pipeline.lock').open('w')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    manifest = json.loads((RUN/'MANIFEST.json').read_text())
    started = time.time()

    def status(state, **values):
        row = dict(status=state, pid=os.getpid(), started_unix=started,
                   updated_unix=time.time(), **values)
        atomic_json(RUN/'PIPELINE_STATUS.json', row)
        print(json.dumps(row, ensure_ascii=False), flush=True)

    caffeinate = None
    try:
        assert sha256(RUN/'recipe.json') == manifest['recipe_sha256']
        assert sha256(RUN/'driver.py') == manifest['driver_sha256']
        for relative, expected in manifest['runtime_sha256'].items():
            assert sha256(RUN/relative) == expected, relative
        for item in manifest['preserved']:
            assert sha256(item['preserved']) == item['sha256'], item['preserved']
        status('RUNNING', target_epochs=manifest['target_epochs'], stage_order=['first', 'second', 'activity', 'bind'])
        if Path('/usr/bin/caffeinate').exists():
            caffeinate = subprocess.Popen(['/usr/bin/caffeinate', '-i', '-w', str(os.getpid())])
        code = train(['--config', str(RUN/'recipe.json'), '--stage', 'all',
                      '--output', str(RUN/'training'), '--device', 'mps'])
        if code != 0:
            status('PAUSED' if code == 2 else 'FAILED', exit_code=code, resumable=True)
            return code
        records = {}
        for stage, target in manifest['target_epochs'].items():
            record = json.loads((RUN/'training'/stage/'complete.json').read_text())
            assert record['status'] == 'COMPLETED' and record['epochs'] == target, stage
            records[stage] = record
        originals = []
        for item in manifest['preserved']:
            current = sha256(item['source'])
            originals.append(dict(path=item['source'], original_sha256=item['sha256'],
                                  current_sha256=current, unchanged=current == item['sha256']))
        assert all(row['unchanged'] for row in originals), 'An original input changed; preserved copies remain available'
        report = dict(status='COMPLETED', stages=records, originals=originals,
                      receiver_configuration=str(RUN/'training/receiver.json'),
                      receiver_performance_evaluated=False, elapsed_seconds=time.time()-started)
        atomic_json(RUN/'COMPLETION_VERIFICATION.json', report)
        lines = ['# 三网络训练完成', '', '已完成累计一阶 200 轮、新二阶 100 轮及活动分类器 100 轮。', '',
                 '| 网络 | 完成轮数 | 验证集选择轮数 | 验证损失 |', '|---|---:|---:|---:|']
        for stage, record in records.items():
            lines.append(f"| {stage} | {record['epochs']} | {record['selected_epoch']} | {record['validation']['loss']:.8g} |")
        lines += ['', '原权重、数据与原断点的 SHA 均未改变。最优与最后一轮权重分别保存。', '',
                  '本次接收机配置为 [receiver.json](training/receiver.json)。尚未进行新权重的接收机性能评价。', '']
        (RUN/'COMPLETION.md').write_text('\n'.join(lines))
        status('COMPLETED', elapsed_seconds=time.time()-started,
               report=str(RUN/'COMPLETION_VERIFICATION.json'), receiver_performance_evaluated=False)
        return 0
    except BaseException as error:
        status('FAILED', error_type=type(error).__name__, error=str(error),
               resumable_checkpoint_preserved=True)
        traceback.print_exc()
        return 1
    finally:
        if caffeinate is not None:
            caffeinate.terminate()
            caffeinate.wait()
        lock.close()


if __name__ == '__main__':
    raise SystemExit(main())
