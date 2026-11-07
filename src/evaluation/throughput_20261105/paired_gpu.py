"""Two independent scene receivers share one runtime, then the process exits."""
import argparse
import ast
from concurrent.futures import ThreadPoolExecutor
import inspect
from pathlib import Path
import time

import psutil
import torch
from threadpoolctl import threadpool_limits

from evaluation.convergence_20261105 import run as original
from utils import read_json, write_json, sha256


def shared_worker():
    """Move process-global thread initialization outside the independent workers."""
    source = inspect.getsource(original.worker)
    tree = ast.parse(source)
    removed = []

    class Setup(ast.NodeTransformer):
        def visit_Expr(self, node):
            call = node.value
            if (isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
                    and isinstance(call.func.value, ast.Name) and call.func.value.id == 'torch'
                    and call.func.attr in ('set_num_threads', 'set_num_interop_threads')):
                removed.append(call.func.attr)
                return ast.copy_location(ast.Pass(), node)
            return self.generic_visit(node)

    tree = Setup().visit(tree)
    if sorted(removed) != ['set_num_interop_threads', 'set_num_threads']:
        raise ValueError('Unexpected frozen worker initialization')
    ast.fix_missing_locations(tree)
    namespace = dict(original.__dict__)
    exec(compile(tree, '<shared-runtime-original-convergence-worker>', 'exec'), namespace)
    return namespace['worker']


def run(specification):
    spec = read_json(specification)
    output = Path(spec['output'])
    jobs = spec['jobs']
    if not 1 <= len(jobs) <= 2 or any(j['method'] not in ('STMP', 'GP-MP') for j in jobs):
        raise ValueError('One or two independent GPU cases required')
    plan = original.verify(output, inputs=False)
    torch.set_num_threads(plan['runtime']['threads'])
    torch.set_num_interop_threads(1)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cudnn.benchmark = False
    torch.cuda.init()
    worker = shared_worker()
    started = time.time()

    def one(job):
        # Each receiver owns its model, probe tensor and all iteration state.
        with torch.cuda.stream(torch.cuda.Stream()):
            worker(output, job['method'], job['scene'])
            torch.cuda.current_stream().synchronize()

    with threadpool_limits(limits=plan['runtime']['threads']):
        with ThreadPoolExecutor(max_workers=len(jobs)) as pool:
            list(pool.map(one, jobs))
    process = psutil.Process()
    write_json(Path(specification).with_suffix('.complete.json'), dict(status='COMPLETE',
        jobs=jobs, elapsed_seconds=time.time()-started, pid=process.pid,
        peak_ram_gib=getattr(process.memory_info(), 'peak_wset', process.memory_info().rss)/2**30,
        peak_cuda_reserved_gib=torch.cuda.max_memory_reserved()/2**30,
        original_worker_sha256=sha256(original.__file__), adapter_sha256=sha256(__file__),
        tf32=False, threads=plan['runtime']['threads'], fresh_process_after_group=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('specification', type=Path)
    run(parser.parse_args().specification)
