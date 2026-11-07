"""Verify the factor-graph derivation and preserve the existing receiver equations."""
from pathlib import Path
import hashlib
import json
import re

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BEFORE = ROOT / "history/before_factor_graph_20261021"
NAMES = ["02_system_model", "03_bayesian_receiver_design",
         "04_receiver_training", "05_unfolded_algorithm"]


def read(path):
    return path.read_text(encoding="utf-8-sig")


def equations(source):
    result = {}
    for match in re.finditer(r"\\begin\{(equation|align|gather)\}(.*?)\\end\{\1\}", source, re.S):
        for label in re.findall(r"\\label\{([^}]+)\}", match.group()):
            result[label] = re.sub(r"\s+", "", match.group())
    return result


preserved, added, counts = [], [], {}
for name in NAMES:
    old = equations(read(BEFORE / "sections" / (name + ".tex")))
    new = equations(read(ROOT / "sections" / (name + ".tex")))
    assert all(new.get(key) == value for key, value in old.items()), name
    preserved.extend(old)
    added.extend(sorted(new.keys() - old.keys()))
    counts[name] = len(new)
assert len(preserved) == 51
assert set(added) == {"eq:twc-factor-definitions", "eq:twc-linear-belief",
                      "eq:twc-denoiser-message", "eq:twc-feedback-message"}
unchanged = ["main.tex", "references.bib", "sections/01_introduction.tex",
             "sections/02_system_model.tex", "sections/04_receiver_training.tex",
             "sections/05_unfolded_algorithm.tex", "sections/appendix_parameter_estimation.tex"]
for path in unchanged:
    assert (ROOT / path).read_bytes() == (BEFORE / path).read_bytes(), path


def expand(path):
    source = re.sub(r"(?<!\\)%.*", "", read(path))
    return re.sub(r"\\input\{([^}]+)\}",
                  lambda m: expand(ROOT / (m.group(1) + ".tex")), source)


source = expand(ROOT / "main.tex")
labels = re.findall(r"\\label\{([^}]+)\}", source)
assert len(labels) == len(set(labels)), "Duplicate labels"
refs = set(re.findall(r"\\(?:eqref|ref)\{([^}]+)\}", source))
assert not refs - set(labels), refs - set(labels)
cites = {key.strip() for group in re.findall(r"\\cite(?:\[[^\]]*\])?\{([^}]+)\}", source)
         for key in group.split(",")}
bibkeys = set(re.findall(r"@\w+\s*\{\s*([^,\s]+)", read(ROOT / "references.bib")))
assert not cites - bibkeys, cites - bibkeys

# Deterministic complex-valued algebra checks, independent of training or data.
rng = np.random.default_rng(20261021)
cn = lambda shape: (rng.standard_normal(shape) + 1j * rng.standard_normal(shape)) / np.sqrt(2)
K, N, M, Q = 3, 2, 2, 4
J, C, D = K * N, M * N, M * N * N
A, Y, mean_in = cn((Q, J)), cn((Q, C)), cn((J, C))
w, sigma2 = 0.8, 0.35
precision = np.eye(J) / w + A.conj().T @ A / sigma2
cov = np.linalg.inv(precision)
mean = mean_in + cov @ A.conj().T @ (Y - A @ mean_in) / sigma2
errors = {}

def log_belief(x):
    return -np.linalg.norm(Y - A @ x) ** 2 / sigma2 - np.linalg.norm(x - mean_in) ** 2 / w


def log_gaussian(x):
    d = x - mean
    return -np.vdot(d, precision @ d).real


constant = log_belief(mean) - log_gaussian(mean)
errors["linear_belief_quadratic"] = max(
    abs(log_belief(x) - log_gaussian(x) - constant) for x in [cn((J, C)) for _ in range(6)])
t = np.trace(cov).real / J
v0 = 1 / (1 / t - 1 / w)
r0 = v0 * (mean / t - mean_in / w)
errors["linear_gaussian_division"] = float(np.max(np.abs(
    (v0 * mean_in + w * r0) / (w + v0) - mean)))

# A column-wise Gaussian and its user-block reorganization have the same energy.
X, R = cn((J, C)), cn((J, C))
as_users = lambda x: x.reshape(K, N, M, N).transpose(0, 2, 3, 1).reshape(K, D)
errors["column_user_message_reorganization"] = abs(
    np.linalg.norm(X - R) ** 2 - sum(np.linalg.norm(x - r) ** 2 for x, r in zip(as_users(X), as_users(R))))

# Explicit summation over a finite channel prior checks the local activity belief.
prior = np.array([0.2, 0.3, 0.5])
channels, r = cn((3, D)), cn((D,))
rho, v = 0.2, 1.7
q0 = np.exp(-np.linalg.norm(r) ** 2 / v)
component_likelihood = np.exp(-np.sum(abs(channels - r) ** 2, axis=1) / v)
q1 = prior @ component_likelihood
joint = np.stack([(1 - rho) * prior * q0, rho * prior * component_likelihood])
joint /= joint.sum()
p = rho * q1 / ((1 - rho) * q0 + rho * q1)
mu = (prior * component_likelihood) @ channels / q1
errors["activity_marginal"] = abs(p - joint[1].sum())
errors["effective_channel_mean"] = float(np.max(np.abs(joint[1] @ channels - p * mu)))

# The outgoing message is the quotient of the chosen Gaussian output and input.
estimate = cn((J, C))
quotient_errors = []
for ratio in [0.1, 0.5, 0.95]:
    variance_out = v * ratio / (1 - ratio)
    mean_out = (estimate - ratio * R) / (1 - ratio)
    def log_quotient(x):
        return -np.linalg.norm(x - estimate) ** 2 / (v * ratio) + np.linalg.norm(x - R) ** 2 / v
    def log_return(x):
        return -np.linalg.norm(x - mean_out) ** 2 / variance_out
    offset = log_quotient(mean_out) - log_return(mean_out)
    for x in [np.zeros((J, C)), cn((J, C))]:
        quotient_errors.append(abs(log_quotient(x) - log_return(x) - offset))
errors["return_gaussian_division"] = max(quotient_errors)
assert max(errors.values()) < 1e-10, errors

report = {
    "status": "PASS", "preserved_numbered_equations_II_V": len(preserved),
    "added_numbered_equations": added, "equation_counts_II_V": counts,
    "total_numbered_equations_with_appendix": len(equations(source)),
    "unchanged_files": unchanged, "missing_references": [], "missing_citation_keys": [],
    "deterministic_algebra_max_absolute_errors": errors,
    "training_or_performance_experiments_run": False,
    "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in [ROOT / "sections/03_bayesian_receiver_design.tex",
                                ROOT / "figures/posterior_factor_graph.tex"]},
}
(HERE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
