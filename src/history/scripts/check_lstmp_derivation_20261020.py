"""Deterministic checks for the receiver derivation, without model inference.

All examples are synthetic mathematical controls. They do not estimate AFDM
receiver performance, train networks, select checkpoints, or change thresholds.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np


def logsumexp(values):
    maximum = np.max(values)
    return float(maximum + np.log(np.exp(values - maximum).sum()))


def local_posterior(r, variance, rho, atoms, weights):
    """Real coordinates; variance is per complex coordinate."""
    c = variance / 2
    dimension = len(r)
    log_kernel = -np.sum((atoms - r) ** 2, axis=1) / (2 * c)
    normalizer = dimension * math.log(2 * math.pi * c) / 2
    log_q1 = logsumexp(np.log(weights) + log_kernel) - normalizer
    log_q0 = -float(r @ r) / (2 * c) - normalizer
    active_weights = np.exp(np.log(weights) + log_kernel
                            - logsumexp(np.log(weights) + log_kernel))
    mean = active_weights @ atoms
    centered = atoms - mean
    covariance = (centered.T * active_weights) @ centered
    joint_atoms = np.vstack((np.zeros(dimension), atoms))
    log_joint = np.concatenate((
        [math.log1p(-rho) + log_q0],
        math.log(rho) + np.log(weights) + log_kernel - normalizer,
    ))
    joint_weights = np.exp(log_joint - logsumexp(log_joint))
    probability = float(joint_weights[1:].sum())
    joint_mean = joint_weights @ joint_atoms
    joint_centered = joint_atoms - joint_mean
    joint_covariance = (joint_centered.T * joint_weights) @ joint_centered
    return dict(log_q1=log_q1, log_qx=logsumexp(log_joint),
                log_ratio=log_q1-log_q0,
                mean=mean, covariance=covariance, probability=probability,
                joint_mean=joint_mean, joint_covariance=joint_covariance)


def jacobian(function, point, step=1e-5):
    eye = np.eye(len(point))
    return np.stack([(function(point + step*e)-function(point - step*e))/(2*step)
                     for e in eye], axis=-1)


def hessian(function, point, step=2e-4):
    eye = np.eye(len(point))
    size = len(point)
    result = np.zeros((size, size))
    center = function(point)
    for i in range(size):
        result[i, i] = (function(point+step*eye[i])-2*center
                        + function(point-step*eye[i]))/step**2
        for j in range(i):
            result[i, j] = result[j, i] = (
                function(point+step*(eye[i]+eye[j]))
                - function(point+step*(eye[i]-eye[j]))
                - function(point+step*(-eye[i]+eye[j]))
                + function(point-step*(eye[i]+eye[j]))
            )/(4*step**2)
    return result


def run_checks():
    checks = []

    def record(name, error, tolerance, **details):
        checks.append(dict(name=name, maximum_absolute_error=float(error),
                           tolerance=tolerance, passed=bool(error <= tolerance),
                           **details))

    rng = np.random.default_rng(20261020)
    a = (rng.normal(size=(3, 5))+1j*rng.normal(size=(3, 5)))/np.sqrt(10)
    prior = rng.normal(size=(5, 2))+1j*rng.normal(size=(5, 2))
    y = rng.normal(size=(3, 2))+1j*rng.normal(size=(3, 2))
    w, noise = 0.7, 0.2
    covariance = np.linalg.inv(np.eye(5)/w+a.conj().T@a/noise)
    mean = covariance@(prior/w+a.conj().T@y/noise)
    woodbury = prior+w*a.conj().T@np.linalg.solve(
        noise*np.eye(3)+w*a@a.conj().T, y-a@prior)
    singular = np.linalg.svd(a, compute_uv=False)
    fraction = ((5-len(singular))+(noise/(noise+w*singular**2)).sum())/5
    tau = float(np.trace(covariance).real/5)
    v = 1/(1/tau-1/w)
    r = v*(mean/tau-prior/w)
    recovered_mean = (prior/w+r/v)/(1/w+1/v)
    record("general_complex_gaussian_conditioning",
           np.max(np.abs(mean-woodbury)), 2e-13)
    record("linear_trace_includes_nullspace", abs(tau-w*fraction), 2e-13)
    record("gaussian_message_division_recombines_projected_moments",
           max(np.max(np.abs(recovered_mean-mean)),
               abs(1/(1/w+1/v)-tau)), 2e-13)

    atoms = np.array([[1.0, 0.1, -0.3, 0.8], [-0.8, 0.6, 0.1, -0.2],
                      [0.2, -0.7, 1.1, 0.3], [0.5, 0.9, -0.4, -0.6],
                      [-0.3, -0.2, 0.7, 0.9]])
    weights = np.array([0.13, 0.27, 0.16, 0.24, 0.20])
    errors = {name: 0.0 for name in (
        "tweedie_mean", "tweedie_covariance", "log_odds_gradient",
        "conditional_mean_jacobian", "joint_mixture_mean",
        "joint_mixture_covariance", "joint_mean_jacobian",
        "complex_variance_trace_factor", "conditional_risk_decomposition",
        "effective_channel_mixture_score", "activity_gate_calibration_placement")}
    for variance in (0.4, 1.3, 3.0):
        for rho in (0.1, 0.5):
            for point in (np.array([0.2, -0.1, 0.1, 0.3]),
                          np.array([-0.5, 0.3, 0.4, -0.2])):
                c, complex_dimension = variance/2, 2
                post = local_posterior(point, variance, rho, atoms, weights)
                get = lambda r: local_posterior(r, variance, rho, atoms, weights)
                gradient = jacobian(lambda r: np.array(get(r)["log_q1"]), point)
                mixture_gradient = jacobian(lambda r: np.array(get(r)["log_qx"]), point)
                curvature = hessian(lambda r: get(r)["log_q1"], point)
                odds_gradient = jacobian(lambda r: np.array(get(r)["log_ratio"]), point)
                mean_jacobian = jacobian(lambda r: get(r)["mean"], point)
                joint_jacobian = jacobian(lambda r: get(r)["joint_mean"], point)
                p, mu, cov = post["probability"], post["mean"], post["covariance"]
                active_score = (mu-point)/c
                mixed_score = p*active_score-(1-p)*point/c
                calibration_error = max(
                    np.max(np.abs(
                        point+alpha*c*(prob*active_score-(1-prob)*point/c)
                        - prob*(point+alpha*c*active_score)
                        - (1-alpha)*(1-prob)*point))
                    for alpha in (0.4, 1.0, 1.7)
                    for prob in (0.0, p, 1.0))
                bias = np.array([0.1, -0.2, 0.3, 0.05])
                fitted = mu+bias
                logits = np.log(weights)-np.sum((atoms-point)**2, axis=1)/(2*c)
                posterior_weights = np.exp(logits-logsumexp(logits))
                risk = float(posterior_weights@np.sum((atoms-fitted)**2, axis=1))
                values = {
                    "tweedie_mean": np.max(np.abs(point+c*gradient-mu)),
                    "tweedie_covariance": np.max(np.abs(c*np.eye(4)+c*c*curvature-cov)),
                    "log_odds_gradient": np.max(np.abs(odds_gradient-mu/c)),
                    "conditional_mean_jacobian": np.max(np.abs(c*mean_jacobian-cov)),
                    "joint_mixture_mean": np.max(np.abs(p*mu-post["joint_mean"])),
                    "joint_mixture_covariance": np.max(np.abs(
                        p*cov+p*(1-p)*np.outer(mu, mu)-post["joint_covariance"])),
                    "joint_mean_jacobian": np.max(np.abs(c*joint_jacobian-post["joint_covariance"])),
                    "complex_variance_trace_factor": abs(
                        variance*np.trace(joint_jacobian)/(2*complex_dimension)
                        - np.trace(post["joint_covariance"])/complex_dimension),
                    "conditional_risk_decomposition": abs(risk-np.trace(cov)-bias@bias),
                    "effective_channel_mixture_score": max(
                        np.max(np.abs(mixture_gradient-mixed_score)),
                        np.max(np.abs(point+c*mixture_gradient-post["joint_mean"]))),
                    "activity_gate_calibration_placement": calibration_error,
                }
                for name, error in values.items():
                    errors[name] = max(errors[name], float(error))
    for name, error in errors.items():
        tolerance = 2e-6 if name == "tweedie_covariance" else 2e-8
        if name in ("joint_mixture_mean", "joint_mixture_covariance",
                    "conditional_risk_decomposition", "activity_gate_calibration_placement"):
            tolerance = 2e-13
        record(name, error, tolerance, local_queries=12)

    post = local_posterior(np.zeros(2), 1., .99,
                           np.array([[2., 0.], [-2., 0.]]), np.array([.5, .5]))
    joint_tau = float(np.trace(post["joint_covariance"]))
    checks.append(dict(name="pointwise_posterior_variance_can_exceed_noise",
                       variance=joint_tau, noise_variance=1.,
                       raw_extrinsic_precision=1/joint_tau-1,
                       passed=bool(joint_tau > 1)))

    prior_variance, noise_variance = .7, .2
    posterior_mse = prior_variance*noise_variance/(prior_variance+noise_variance)
    expected_raw_residual = noise_variance**2/(prior_variance+noise_variance)-noise_variance
    record("optimal_gaussian_mean_has_negative_noise_subtracted_residual",
           abs(expected_raw_residual+posterior_mse), 2e-15,
           expected_raw_residual=expected_raw_residual, posterior_mse=posterior_mse)

    truth = np.array([1., 2.])
    truth_weights = np.array([.5, .5])
    ordinary_mean = float(truth_weights@truth)
    nmse_weights = truth_weights/truth**2
    relative_error_optimum = float(nmse_weights@truth/nmse_weights.sum())
    record("sample_normalized_mse_changes_conditional_mean_target",
           abs(relative_error_optimum-1.2), 2e-15,
           ordinary_mean=ordinary_mean, relative_error_optimum=relative_error_optimum)

    p, true_mean, active_covariance, fitted_mean = .3, 2., .5, 1.
    active_risk = active_covariance+(fitted_mean-true_mean)**2
    surrogate = p*active_risk+p*(1-p)*fitted_mean**2
    actual_risk = (p*active_covariance+p*(1-p)*true_mean**2
                   +(p*fitted_mean-p*true_mean)**2)
    record("conditional_risk_is_not_central_covariance_in_mixture_formula",
           max(abs(surrogate-.66), abs(actual_risk-1.08)), 2e-15,
           surrogate_mixture_variance=surrogate, actual_joint_risk=actual_risk)

    eta, prediction = .3, .6
    bce = lambda p: -eta*math.log(p)-(1-eta)*math.log1p(-p)
    kl = eta*math.log(eta/prediction)+(1-eta)*math.log((1-eta)/(1-prediction))
    record("bce_excess_conditional_risk_is_bernoulli_kl",
           abs(bce(prediction)-bce(eta)-kl), 2e-15)
    for f in (.3, .8, .99):
        gamma = 1.
        record(f"uncalibrated_extrinsic_parameterizations_agree_f_{f}",
               abs(gamma*f/(1-f)-gamma*f/(1-gamma*f)), 2e-15)
    return checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    checks = run_checks()
    report = {
        "scope": "Deterministic synthetic mathematical checks; no AFDM data or model inference.",
        "numpy_version": np.__version__,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "checks": checks,
        "passed": all(item["passed"] for item in checks),
        "interpretation": "These checks support algebra and factors, not receiver accuracy or convergence.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n",
                           encoding="utf-8")
    print(json.dumps(dict(passed=report["passed"], checks=len(checks),
                          failures=[c for c in checks if not c["passed"]],
                          output=str(args.output.resolve())), ensure_ascii=False))
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
