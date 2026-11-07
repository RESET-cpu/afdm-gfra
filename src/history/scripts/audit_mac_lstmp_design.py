"""Read-only algorithm checks for the Mac L-STMP source snapshot.

No trained network, optimizer, physical evaluation bank, or checkpoint is used.
The feedback statements are executed from the reviewed source, without editing it.
"""
from pathlib import Path
import ast
import hashlib
import json
import math

import numpy as np
import torch
from torch.nn import functional as F


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "tmp/mac_lstmp_review_20261019/AFDM_LSTMP"
SOURCE = PACKAGE / "runs/lstmp_fresh_20261019/source_experiment"
OUT = ROOT / "results/mac_lstmp_design_audit_20261019"
CONFIG = json.loads((SOURCE / "config.json").read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def feedback_statements():
    tree = ast.parse((SOURCE / "receiver.py").read_text(encoding="utf-8"))
    receiver = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "Receiver")
    method = next(node for node in receiver.body if isinstance(node, ast.FunctionDef) and node.name == "forward")
    loop = next(node for node in method.body if isinstance(node, ast.For))
    start = next(i for i, node in enumerate(loop.body)
                 if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
                 and node.targets[0].id == "raw")
    stop = next(i for i, node in enumerate(loop.body)
                if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Attribute)
                and isinstance(node.value.func.value, ast.Name)
                and node.value.func.value.id == "outputs")
    module = ast.Module(body=loop.body[start:stop], type_ignores=[])
    return compile(module, str(SOURCE / "receiver.py"), "exec")


FEEDBACK = feedback_statements()


def evaluate_feedback(raw_before_beta, log_beta, v=1.0):
    # Synthetic real block matrix with ||A_complex||_F^2 = 16.
    a = torch.zeros(32, 1280, dtype=torch.float64)
    a[:16, :16] = torch.eye(16, dtype=torch.float64)
    a[16:, 640:656] = torch.eye(16, dtype=torch.float64)
    # For the exactly-zero case use binary-exact energy/noise arithmetic;
    # sqrt(0.05)**2 would otherwise leave a rounding residual amplified by beta.
    noise = 2.0 if raw_before_beta == 0 else max(0.1, -raw_before_beta)
    residual = torch.full((32, 256), math.sqrt(max(0.0, (raw_before_beta + noise) / 2)),
                          dtype=torch.float64)
    c = torch.tensor([0.0, 0.0, log_beta], dtype=torch.float64, requires_grad=True)
    estimate = torch.tensor(0.0, dtype=torch.float64, requires_grad=True)
    context = dict(torch=torch, F=F, CONFIG=CONFIG, a=a, residual=residual,
                   public={"noise": noise}, v=torch.tensor(v, dtype=torch.float64),
                   c=c, r=torch.tensor(0.0, dtype=torch.float64), estimate=estimate)
    exec(FEEDBACK, context)
    derivative = torch.autograd.grad(context["post_v"], c, retain_graph=True)[0][2]
    mean_gain = torch.autograd.grad(context["prior"], estimate)[0]
    return dict(raw_before_beta=raw_before_beta, log_beta=log_beta,
                feedback_variance=float(context["post_v"].detach()),
                variance_ratio=float(context["feedback_ratio"].detach()),
                derivative_wrt_log_beta=float(derivative),
                mean_gain=float(mean_gain))


def main():
    original = {str(path.relative_to(PACKAGE)): digest(path)
                for path in PACKAGE.rglob("*") if path.is_file() and "__pycache__" not in path.parts}
    rows = [evaluate_feedback(raw, beta) for raw in (-0.1, -0.0001, 0.0, 0.1, 1.0, 10.0)
            for beta in (-12.0, -4.0, 0.0, 4.0, 12.0)]
    temperature = CONFIG["receiver"]["variance_soft_floor_temperature_ratio"]
    ceiling = CONFIG["receiver"]["maximum_feedback_variance_ratio"]
    # v=1 in this sweep. The +1e-6 term is in variance units, not relative units.
    negative_upper_bound = ceiling * math.tanh((temperature * math.log(2) + 1e-6) / ceiling)
    for row in rows:
        if row["raw_before_beta"] <= 0:
            assert row["variance_ratio"] <= negative_upper_bound + 1e-12
        if row["raw_before_beta"] == 0:
            assert row["derivative_wrt_log_beta"] == 0

    # Exact Gaussian calculation, not a result for a trained AFDM receiver.
    # A has 16 nonzero singular values and 640 unknown complex coefficients.
    q, n, prior_variance, noise_variance = 16, 640, 0.1, 0.001
    eigenvalues = np.linspace(0.5, 1.5, q) ** 2
    denom = noise_variance + prior_variance * eigenvalues
    posterior_mse = prior_variance - prior_variance**2 / n * np.sum(eigenvalues / denom)
    expected_residual_energy = noise_variance**2 * np.sum(1 / denom)
    expected_noise_energy = q * noise_variance
    expected_raw = (expected_residual_energy - expected_noise_energy) / eigenvalues.sum()
    query_variance = posterior_mse * prior_variance / (prior_variance - posterior_mse)
    bound = ceiling * query_variance * math.tanh(
        (temperature * query_variance * math.log(2) + 1e-6) / (ceiling * query_variance))
    assert expected_raw < 0 < posterior_mse

    # Dense diagonal Gaussian posterior independently verifies the trace expression.
    precision = np.full(n, 1 / prior_variance)
    precision[:q] += eigenvalues / noise_variance
    dense_reference_mse = float(np.mean(1 / precision))
    assert abs(posterior_mse - dense_reference_mse) < 1e-14

    # A local change proposed for comparison: positive calibration AFTER positivity.
    # This only removes the sign-based range restriction, not residual-proxy bias.
    positive_base = temperature * math.log1p(math.exp(-0.1 / temperature)) + 1e-6
    proposed_rows = [dict(log_beta=b, variance_ratio=ceiling * math.tanh(
        math.exp(b) * positive_base / ceiling)) for b in (0.0, 4.0, 8.0)]

    mac_check = json.loads((PACKAGE / "runs/lstmp_fresh_20261019/check_cpu.json").read_text(encoding="utf-8"))
    gaussian = dict(scope="Synthetic matched Gaussian LMMSE; analytical expectations per observation column",
                    observation_rows=q, unknown_coefficients=n,
                    prior_variance=prior_variance, noise_variance=noise_variance,
                    exact_posterior_mse=float(posterior_mse),
                    independently_checked_mse=dense_reference_mse,
                    expected_residual_energy=float(expected_residual_energy),
                    expected_noise_energy=expected_noise_energy,
                    expected_raw_residual_variance=float(expected_raw),
                    scalar_extrinsic_query_variance=float(query_variance),
                    nonpositive_raw_feedback_variance_upper_bound=float(bound),
                    note="The bound applies when a sample raw residual is nonpositive. An expectation is not a claim that every sample is negative. The averaged Gaussian covariance does not prove actual extrinsic errors are white.")
    unchanged = all(digest(PACKAGE / name) == value for name, value in original.items())
    assert unchanged
    report = dict(source_commit="fdaeec3cea7c6ee165c4ccf56c72897b2a7e3cef",
                  scope="Source review and synthetic algebra/autodiff only; no optimizer or trained network invoked",
                  source_hashes={name: digest(SOURCE / name) for name in
                                 ("receiver.py", "data.py", "train.py", "backbone.py", "config.json")},
                  nonpositive_raw_variance=dict(query_variance=1.0, exact_upper_ratio=negative_upper_bound,
                                                sweep=rows),
                  gaussian_reference=gaussian,
                  positive_after_calibration_example=dict(scope="Proposed scalar operation only, not implemented or performance validated", rows=proposed_rows),
                  feedback_mean_gain_upper_bound=1 / (1 - ceiling),
                  mac_existing_check=dict(scope="Read from Mac check_cpu.json, not a new receiver run",
                     seed=mac_check["physical_receiver"]["debug_seed"],
                     query_variances=[x["query_variance"] for x in mac_check["physical_receiver"]["diagnostics"]],
                     negative_raw_layers=[i + 1 for i, x in enumerate(mac_check["physical_receiver"]["diagnostics"])
                                          if x["negative_raw_variance"]]),
                  reviewed_files_unchanged=len(original), training_started=False,
                  optimizer_called=False, original_pause_file_preserved=(PACKAGE / "runs/lstmp_fresh_20261019/pause.request").exists())
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "CHECKS.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(dict(nonpositive_raw_upper_ratio=negative_upper_bound,
                          gaussian_reference=gaussian, feedback_mean_gain_bound=1 / (1 - ceiling),
                          source_files_unchanged=len(original), training_started=False), indent=2))


if __name__ == "__main__":
    main()
