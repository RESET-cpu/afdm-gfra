"""CPU portability check; synthetic queries are not performance evidence."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT / "src"))
os.environ["MPLBACKEND"] = "Agg"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["PYTHONPATH"] = str(ROOT / "src")

import numpy as np
import torch
from afdm_jadcedd.algorithm.proposed.configuration import load_configuration, verify
from afdm_jadcedd.algorithm.proposed.receiver import Receiver

torch.set_num_threads(1)
config = load_configuration()
verified = verify(config)
receiver = Receiver(config, device="cpu")
rng = np.random.default_rng(20261018)
r = (rng.standard_normal((2,16,16,16)) + 1j*rng.standard_normal((2,16,16,16)))/np.sqrt(2)
v = np.array([.1, 1.])
moments = receiver.model.infer(r, v)
log_ratio = receiver.evidence.infer(r, v, moments.mean)
assert moments.mean.shape == r.shape
assert moments.variance.shape == (2,) and log_ratio.shape == (2,)
assert all(np.isfinite(a).all() for a in (moments.mean, moments.variance, log_ratio))
subprocess.run([sys.executable, "-m", "pytest", "-q",
    "tests/test_density_ratio_ablation.py", "tests/test_array_transforms.py",
    "tests/test_evaluation_metrics.py"], check=True)
with tempfile.TemporaryDirectory(prefix="jadcedd-plan-") as directory:
    subprocess.run([sys.executable, "experiment/density_ratio_ablation.py", "plan",
        "--output", directory, "--scenes", "1", "--values", "0", "--device", "cpu", "--fresh"], check=True)
report = dict(status="PASS", platform=sys.platform, python=sys.version.split()[0],
    torch=torch.__version__, numpy=np.__version__, device="cpu",
    checkpoint_verification=verified, synthetic_network_queries=2,
    unit_tests=7, fresh_ablation_plan="PASS", full_receiver_experiment_run=False)
(ROOT / "cloud/VALIDATION.local.json").write_text(json.dumps(report, indent=2)+"\n")
print(json.dumps(report, indent=2))
