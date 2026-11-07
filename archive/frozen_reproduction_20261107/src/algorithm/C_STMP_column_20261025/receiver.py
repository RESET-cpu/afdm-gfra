"""One message law for linear, mean, activity, derivative covariance and feedback."""
from pathlib import Path
import time
import numpy as np
from scipy.special import expit, logit
import torch

from algorithm.C_STMP_column_messages.messages import ColumnLinear, hermitian
from training.column_messages_20261025.interface import (
    load_weight, pack, unpack, numpy_information_query,
)
from system.receiver.noise_estimation import estimate_spatial_noise
from utils import read_json, sha256


def to_physical(x):
    # [K,N,L] -> [K,A,O,N], A=O=16.
    return x.reshape(len(x), 16, 16, 16).transpose(0, 2, 3, 1)


def to_columns(x):
    return x.transpose(0, 3, 1, 2).reshape(len(x), 16, 256)


def proper_orthogonal_probes(rng, users, probes):
    result = []
    for _ in range(probes):
        z = (rng.normal(size=(users, 256, 16))+1j*rng.normal(size=(users, 256, 16)))/np.sqrt(2)
        q, _ = np.linalg.qr(z)
        # Random orthonormal rows, E[xi xi^H]=L I exactly for column-local linear D.
        result.append(q.conj().transpose(0, 2, 1)*16)
    return result


def projected_feedback(mean, fraction, precision_values, precision_vectors, information, floor, ceiling):
    """Proper Gaussian moment projection, same relative bounds as frozen STMP.

    fraction is Lambda^(1/2) V Lambda^(1/2) in the incoming precision eigenbasis.
    Projection is inside every iteration and is recorded, never a final detector
    correction. It is an approximation, not an exact posterior identity.
    """
    eig, basis = np.linalg.eigh(hermitian(fraction))
    used = np.clip(eig, floor, ceiling)
    inverse_fraction = (basis*(1/used)[:, None, :]) @ basis.conj().transpose(0, 2, 1)
    root = np.sqrt(precision_values)
    post_precision_mode = inverse_fraction*root[:, :, None]*root[:, None, :]
    u = precision_vectors
    post_precision = (u @ post_precision_mode) @ u.conj().transpose(0, 2, 1)
    incoming = (u*precision_values[:, None, :]) @ u.conj().transpose(0, 2, 1)
    outgoing = hermitian(post_precision-incoming)
    eta = post_precision @ mean-information
    return outgoing, eta, eig, used


class Receiver:
    def __init__(self, configuration, *, device='cuda', verify=True):
        self.config = read_json(configuration) if isinstance(configuration, (str, Path)) else dict(configuration)
        c = self.config
        self.device = device
        if verify:
            for name in ('first', 'activity'):
                assert sha256(c[name+'_checkpoint']) == c[name+'_sha256']
        self.first, first_record = load_weight(c['first_checkpoint'], device)
        self.activity, activity_record = load_weight(c['activity_checkpoint'], device)
        if verify:
            assert activity_record['metadata']['first_sha256'] == c['first_sha256']
            assert first_record['metadata']['specification_sha256'] == activity_record['metadata']['specification_sha256']
        self.last_trace = []

    def nonlinear(self, information, precision, probes):
        x,z,u,lam,u_np,lam_np = numpy_information_query(information,precision,self.device)
        with torch.inference_mode():
            mu_t = self.first(x, z, u, lam)
            score = self.activity(x, u, lam, mu_t).cpu().numpy().astype(float)
            mu = to_columns(unpack(mu_t).cpu().numpy().astype(complex))
            fraction = np.zeros_like(precision)
            epsilon = self.config['variance_estimator']['epsilon']
            for xi in probes:
                # eta perturbation Lambda^(1/2) xi keeps the preconditioned input
                # perturbation bounded even for a nearly singular Lambda.
                dx = u_np @ (np.sqrt(2/(1+lam_np))[:, :, None]*xi)
                dz = u_np @ ((np.sqrt(lam_np)/(1+lam_np))[:, :, None]*xi)
                dx = pack(torch.as_tensor(to_physical(dx), dtype=torch.complex64, device=self.device))
                dz = pack(torch.as_tensor(to_physical(dz), dtype=torch.complex64, device=self.device))
                plus = self.first(x+epsilon*dx,z+epsilon*dz,u,lam)
                minus = self.first(x-epsilon*dx,z-epsilon*dz,u,lam)
                derivative = to_columns(unpack((plus-minus)/(2*epsilon)).cpu().numpy().astype(complex))
                modal = u_np.conj().transpose(0, 2, 1) @ derivative
                fraction += (np.sqrt(lam_np)[:, :, None]*modal) @ xi.conj().transpose(0, 2, 1)/256
            fraction = hermitian(fraction/len(probes))
        return mu, score, fraction, u_np, lam_np

    def infer(self, inputs, *, observer=None):
        c = self.config; scale = c['scale']; controls = c['ep']
        started = time.monotonic()
        y = inputs.observation/scale
        noise, noise_record = estimate_spatial_noise(inputs.observation)
        noise /= scale**2
        linear = ColumnLinear(inputs.operator, noise)
        k = linear.users
        if y.shape[1:] != (16, 16) or linear.columns != 16 or linear.frames < 16:
            raise ValueError('Current trained candidate requires 16x16 channels and full column rank')
        prior_var = inputs.activity_prior*c['initial_second_moment']
        prior_precision = np.broadcast_to(np.eye(16)/prior_var, (k,16,16)).copy().astype(complex)
        prior_eta = np.zeros((k,16,256), complex)
        previous_likelihood = previous_eta = previous_mean = previous_probability = None
        previous_decision = None
        stable = decision_stable = 0
        self.last_trace = []
        probes = proper_orthogonal_probes(np.random.default_rng(c['variance_estimator']['seed']),
                                          k, c['variance_estimator']['probes'])
        beta = controls['damping']; reason = 'MAX_ITERATIONS'
        for iteration in range(1, controls['iterations']+1):
            covariance = np.linalg.inv(prior_precision)
            prior_mean = covariance @ prior_eta
            messages = linear.update(y.reshape(linear.frames, -1), prior_mean, covariance)
            precision = np.stack([m.precision for m in messages])
            information = np.stack([m.information for m in messages])
            if previous_likelihood is not None:
                precision = (1-beta)*previous_likelihood+beta*precision
                information = (1-beta)*previous_eta+beta*information
            conditional, evidence, fraction, u, lam = self.nonlinear(information, precision, probes)
            probability = expit(logit(inputs.activity_prior)+evidence)
            mean = probability[:, None, None]*conditional
            modal = np.sqrt(lam)[:, :, None]*(u.conj().transpose(0,2,1)@conditional)
            joint_fraction = (probability[:, None, None]*fraction
                + (probability*(1-probability))[:, None, None]*(modal@modal.conj().transpose(0,2,1))/256)
            out_precision, out_eta, raw, used = projected_feedback(mean, joint_fraction, lam, u,
                information, controls['variance_fraction_floor'], controls['variance_fraction_ceiling'])
            # Gaussian product damping in natural parameters, on both directions.
            prior_precision = hermitian((1-beta)*prior_precision+beta*out_precision)
            prior_eta = (1-beta)*prior_eta+beta*out_eta
            if not np.isfinite(prior_eta).all() or np.linalg.eigvalsh(prior_precision).min() <= 0:
                raise FloatingPointError('Invalid proper outgoing Gaussian message')
            decision = probability>=c['decision_threshold']
            change = activity_change = covariance_change = feedback_change = None
            if previous_mean is not None:
                change = np.linalg.norm(mean-previous_mean)/max(np.linalg.norm(mean), np.linalg.norm(previous_mean),1e-12)
                activity_change = np.max(abs(probability-previous_probability))
                covariance_change = np.linalg.norm(precision-previous_likelihood)/max(np.linalg.norm(precision),1e-12)
                # Compare raw outgoing natural parameters with their damped state.
                feedback_change = max(np.linalg.norm(out_eta-prior_eta)/max(np.linalg.norm(prior_eta),1e-12),
                    np.linalg.norm(out_precision-prior_precision)/max(np.linalg.norm(prior_precision),1e-12))
                stable = stable+1 if (change<controls['convergence_tolerance']
                    and covariance_change<controls['convergence_tolerance']
                    and activity_change<controls['activity_convergence_tolerance']
                    and feedback_change<controls['raw_site_residual_tolerance']) else 0
                decision_stable = decision_stable+1 if np.array_equal(decision, previous_decision) else 0
            converged = (iteration>=controls['min_iterations'] and stable>=controls['convergence_patience']
                         and decision_stable>=controls['decision_stability_window'])
            row = dict(iteration=iteration, estimate_change=None if change is None else float(change),
                activity_change=None if activity_change is None else float(activity_change),
                precision_change=None if covariance_change is None else float(covariance_change),
                feedback_change=None if feedback_change is None else float(feedback_change),
                projected_low=int(np.sum(raw<controls['variance_fraction_floor'])),
                projected_high=int(np.sum(raw>controls['variance_fraction_ceiling'])),
                raw_fraction_min=float(raw.min()),raw_fraction_max=float(raw.max()),
                conditional_negative_eigenvalues=int(np.sum(np.linalg.eigvalsh(fraction)<0)),
                precision_min=float(lam.min()),precision_max=float(lam.max()),converged=converged)
            self.last_trace.append(row)
            if observer is not None: observer(row, mean, probability)
            previous_likelihood, previous_eta = precision, information
            previous_mean, previous_probability, previous_decision = mean.copy(), probability.copy(), decision.copy()
            if converged: reason='CONVERGED'; break
        arrays = dict(estimate=to_physical(mean)*scale, conditional_matrix=to_physical(conditional)*scale,
            probabilities=probability, activity_decision=decision)
        record = dict(method='C-STMP', candidate='column_messages_20261025', status='COMPLETE',
            configuration=c, truth_loaded=False, noise_estimation=noise_record,
            iterations=len(self.last_trace), converged=reason=='CONVERGED', stopping_reason=reason,
            seconds=time.monotonic()-started, trace=self.last_trace,
            first_calls=len(self.last_trace)*(1+2*len(probes)), classifier_calls=len(self.last_trace),
            limitation='Independent Gaussian messages and projected column covariance are approximations; all projection counts retained.')
        return arrays, record
