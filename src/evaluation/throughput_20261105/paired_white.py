"""Share runtime overhead for two unchanged white-SNR receiver evaluations."""
import argparse
import ast
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import inspect
from pathlib import Path
import time

import psutil
import torch
from threadpoolctl import threadpool_limits

from evaluation.white_matched_fp32_20261105 import run as native
from utils import read_json, write_json, sha256


def shared_worker(benchmark_output=None):
    tree = ast.parse(inspect.getsource(native.worker))
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
    assert sorted(removed) == ['set_num_interop_threads', 'set_num_threads']
    ast.fix_missing_locations(tree)
    namespace = dict(native.__dict__)
    if benchmark_output is not None:
        def benchmark_plan():
            plan = deepcopy(native.verify())
            plan['native_directory'] = str(benchmark_output/'native')
            return plan
        namespace.update(OUT=benchmark_output, verify=benchmark_plan)
    exec(compile(tree, '<shared-runtime-original-white-worker>', 'exec'), namespace)
    return namespace['worker']


def run(specification):
    spec = read_json(specification)
    positions = spec['positions']
    if not 1 <= len(positions) <= 2:
        raise ValueError('One or two independent inputs per process required')
    plan = native.verify()
    threads = plan['runtime']['threads_per_worker']
    torch.set_num_threads(threads)
    torch.set_num_interop_threads(1)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cudnn.benchmark = False
    torch.cuda.init()
    worker = shared_worker(Path(spec['benchmark_output']) if 'benchmark_output' in spec else None)
    began = time.time()

    def one(position):
        with torch.cuda.stream(torch.cuda.Stream()):
            worker(position)
            torch.cuda.current_stream().synchronize()

    with threadpool_limits(limits=threads):
        with ThreadPoolExecutor(max_workers=len(positions)) as pool:
            list(pool.map(one, positions))
    process = psutil.Process()
    write_json(Path(specification).with_suffix('.complete.json'), dict(status='COMPLETE', positions=positions,
        elapsed_seconds=time.time()-began, peak_ram_gib=process.memory_info().peak_wset/2**30,
        peak_cuda_reserved_gib=torch.cuda.max_memory_reserved()/2**30,
        adapter_sha256=sha256(__file__), original_worker_sha256=sha256(native.__file__), tf32=False,
        threads=threads, fresh_process_after_group=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('specification', type=Path)
    run(parser.parse_args().specification)
