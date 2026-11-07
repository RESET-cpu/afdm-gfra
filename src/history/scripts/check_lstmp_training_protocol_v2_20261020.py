"""Numerical checks of protocol algebra and illustrative gradient paths.

No receiver, checkpoint, training optimizer, or GPU is loaded.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/lstmp_training_protocol_v2_20261020"
CHECKS = {}


def check(name, error, tolerance):
    value = float(error)
    CHECKS[name] = dict(error=value, tolerance=tolerance, passed=value <= tolerance)
    assert value <= tolerance, (name, value, tolerance)


def derivative(f, x, step=1e-6):
    result = np.zeros_like(x, dtype=float)
    for i in range(len(x)):
        delta = np.zeros_like(x, dtype=float)
        delta[i] = step
        result[i] = (f(x + delta) - f(x - delta)) / (2 * step)
    return result


def bce(a, p):
    return -a * np.log(p) - (1 - a) * np.log1p(-p)


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def risk_checks():
    # One fixed query, a synthetic conditional distribution of (activity, H).
    w = np.array([.7, .1, .08, .12])
    a = np.array([0., 1., 1., 1.])
    h = np.array([0., -1., 2., 4.])
    pi = float(w @ a)
    mean = float((w * a) @ h / pi)
    kappa = 1.7
    var_h = (w * a) @ (h - mean) ** 2 / pi
    constant = pi * var_h / kappa + bce(pi, pi)

    def risk(p, mu):
        return float(w @ (a * (mu - h) ** 2 / kappa + bce(a, p)))

    errors = []
    excess = []
    for p in (.01, .1, pi, .7, .99):
        for mu in (-2., 0., mean, 4.):
            kl = bce(pi, p) - bce(pi, pi)
            expanded = constant + pi * (mu - mean) ** 2 / kappa + kl
            errors.append(abs(risk(p, mu) - expanded))
            excess.append(risk(p, mu) - risk(pi, mean))
    check("T6_conditional_risk_identity", max(errors), 1e-12)
    check("T6_nonnegative_excess_on_grid", max(0., -min(excess)), 1e-12)
    g = derivative(lambda z: risk(z[0], z[1]), np.array([pi, mean]))
    check("T6_zero_gradient_at_correct_outputs", np.max(np.abs(g)), 1e-8)

    check("T7_product_equals_effective_conditional_mean", abs(pi * mean - w @ (a * h)), 1e-14)

    p, mu, target = 1e-4, .3, 2.
    analytic = 2 * (mu - target) / kappa
    actual = derivative(
        lambda z: (z[0] - target) ** 2 / kappa,
        np.array([mu]))[0]
    check("conditional_mean_supervision_gradient", abs(analytic - actual), 1e-8)
    return dict(pi=pi, conditional_mean=mean, direct_gradient_at_low_p=analytic,
                squared_error_only_gradient=2 * p * (p * mu - target) / kappa)


def weighting_checks():
    # Different user counts and different active counts, fixed dataset energy.
    truth = [np.array([1., 0.]), np.array([0., 2., 0., 3., 0.])]
    activity = [(x != 0).astype(float) for x in truth]
    means = [np.array([.8, .5]), np.array([.2, 2.1, .7, 2.8, .1])]
    probabilities = [np.array([.7, .2]), np.array([.1, .8, .3, .9, .2])]
    energy = sum(np.sum(x * x) for x in truth)
    total = sum(len(x) for x in truth)
    n = len(truth)
    errors_x = [np.sum((p * m - x) ** 2) for x, m, p in zip(truth, means, probabilities)]
    errors_h = [np.sum(a * (m - x) ** 2) for x, m, a in zip(truth, means, activity)]
    ce = [np.sum(bce(a, p)) for a, p in zip(activity, probabilities)]
    dataset = np.array([sum(errors_x) / energy, sum(errors_h) / energy, sum(ce) / total])
    scene_mean = np.mean([[ex / (energy / n), eh / (energy / n), c / (total / n)]
                         for ex, eh, c in zip(errors_x, errors_h, ce)], axis=0)
    check("T8_uniform_scene_estimator_identity", np.max(np.abs(dataset - scene_mean)), 1e-14)
    check("receiver_update_budget", abs(4800 * 7 * 3 - 100800), 0)


def gradient_checks():
    # theta1, theta2, phi1, phi2, beta1, beta2: illustrative two-layer map.
    params = np.array([.8, 1.1, -.4, .2, .15, .7])

    def outputs(v, detached_head_means=None):
        t1, t2, f1, f2, beta1, _ = v
        mu1 = t1 * 1.2
        h1 = mu1 if detached_head_means is None else detached_head_means[0]
        p1 = sigmoid(f1 + .24 + .7 * h1)
        x1 = p1 * mu1
        r2 = 1.7 - .6 * x1 + beta1 * x1
        mu2 = t2 * r2
        h2 = mu2 if detached_head_means is None else detached_head_means[1]
        p2 = sigmoid(f2 + .3 * r2 + .2 * h2)
        return np.array([mu1, mu2]), np.array([p1, p2])

    def losses(v, detached_head_means=None):
        mu, p = outputs(v, detached_head_means)
        weights = np.array([.8, 1.]) / 1.8
        return np.array([weights @ (p * mu - 1.3) ** 2,
                         weights @ (mu - 1.3) ** 2, weights @ bce(1., p)])

    gradients = np.array([derivative(lambda v: losses(v)[i], params) for i in range(3)])
    raw_full = gradients[1] + gradients[2]
    raw_control = raw_full.copy()
    raw_control[:2] = gradients[1, :2]
    check("T10_non_score_raw_gradients_unchanged",
          np.max(np.abs(raw_control[2:] - raw_full[2:])), 0)
    check("T10_score_raw_gradient_difference_is_BCE",
          np.max(np.abs(raw_full[:2] - raw_control[:2] - gradients[2, :2])), 1e-14)
    check("terminal_feedback_parameter_is_unused", np.max(np.abs(gradients[:, -1])), 0)
    check("same_layer_conditional_loss_not_direct_to_head", abs(gradients[1, 3]), 1e-10)
    assert abs(gradients[1, 2]) > 1e-5, "Missing earlier-head path from later conditional loss"
    assert np.all(np.abs(gradients[2, :2]) > 1e-5), "Missing score paths from BCE"
    fixed_means, _ = outputs(params)
    local_detach_bce = derivative(lambda v: losses(v, fixed_means)[2], params)
    assert abs(local_detach_bce[0]) > 1e-5, "Toy should retain a cross-layer query path"
    return dict(parameter_order=["theta1", "theta2", "phi1", "phi2", "beta1", "beta2"],
                loss_order=["effective_channel_control", "conditional_channel", "activity_BCE"],
                gradients_by_loss=gradients.tolist(),
                local_mu_detach_still_has_BCE_to_theta1=float(local_detach_bce[0]),
                raw_gradients_before_global_clipping=True)


def main():
    risk = risk_checks()
    weighting_checks()
    gradients = gradient_checks()
    OUT.mkdir(parents=True, exist_ok=True)
    result = dict(status="PASSED", deterministic_checks=CHECKS,
                  conditional_risk=risk, illustrative_gradient_paths=gradients,
                  scope=dict(synthetic_mathematics=True, receiver_forwards=0,
                             optimizer_updates=0, checkpoint_loads=0,
                             does_not_validate_receiver_gradient_implementation=True),
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (OUT / "MATH_CHECKS.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
