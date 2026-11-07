"""Off-grid SBL: posterior, offset updates, noise learning and receiver."""
from copy import deepcopy
from dataclasses import dataclass, replace
from pathlib import Path
import json
import time
import numpy as np
from scipy.linalg import cho_factor, cho_solve
from project import ROOT, CONFIGS
from utils import sha256, write_json
from system.observation import ReceiverInput, load_input
from system.receiver.atoms import (
    MAX_FREQUENCY, coarse_dictionary, delay_bounds, sensed_atom,
    stack_observation, reconstruct, activity_score)
from ._common import nearest_node, public_snr_db
from ._validation import inference_sources, inference_signature

@dataclass(frozen=True)
class Settings:
    iterations: int = 120
    tolerance: float = 1e-4
    rho: float = 1e-3
    candidates_per_user: int = 12
    offset_candidates: int = 48
    offset_sweeps: int = 5
    warmup: int = 5
    doppler_step: float = .5

    def __post_init__(self):
        if (any(type(v) is not int or v < 1 for v in (self.iterations,
                self.candidates_per_user,self.offset_candidates,self.offset_sweeps,self.warmup))
                or not all(np.isfinite(v) and v > 0 for v in
                           (self.tolerance,self.rho,self.doppler_step))):
            raise ValueError("positive finite SBL controls required")


def posterior(a,y,variance,noise):
    """Woodbury posterior without constructing the full dictionary covariance."""
    c = (a*variance)@a.conj().T+noise*np.eye(a.shape[0])
    factor = cho_factor(c,lower=True,check_finite=False)
    inv_a = cho_solve(factor,a,check_finite=False)
    mean = variance[:,None]*(a.conj().T@cho_solve(factor,y,check_finite=False))
    diagonal = variance-variance**2*np.real(np.sum(a.conj()*inv_a,axis=0))
    if diagonal.min() < -1e-8*variance.max():
        raise FloatingPointError("negative posterior variance beyond roundoff")
    return mean,np.maximum(diagonal,0.),inv_a


def variance_update(second_moment,antennas,rho):
    # Positive root of rho*alpha²+M*alpha-sum_m E|x_m|²=0.
    return 2*second_moment/(antennas+np.sqrt(antennas**2+4*rho*second_moment))


def offset_quadratic(a,y,mean,variance,inv_a,derivatives,selected,noise):
    """Expected residual quadratic for increments in selected offsets.

Ordering is [selected delays, selected Dopplers]. This includes posterior
cross-covariances and coupling to unselected columns, not just the mean fit.
"""
    m = y.shape[1]
    sub = variance[selected]
    covariance = np.diag(sub)-(sub[:,None]*(a[:,selected].conj().T@inv_a[:,selected]))*sub[None,:]
    covariance = (covariance+covariance.conj().T)/2
    moment = mean[selected]@mean[selected].conj().T+m*covariance
    # A Sigma[:,S] = sigma² C^{-1} A[:,S] Lambda_S.
    cross = (y-a@mean)@mean[selected].conj().T-m*noise*inv_a[:,selected]*sub
    derivative = np.column_stack([derivatives[0][:,selected],derivatives[1][:,selected]])
    repeated_moment = np.tile(moment,(2,2))
    b = np.real(np.sum(derivative.conj()*np.tile(cross,(1,2)),axis=0))
    q = np.real((derivative.conj().T@derivative)*repeated_moment.T)
    return (q+q.T)/2,b


def bounded_quadratic(q,b,lower,upper,sweeps):
    """Coordinate minimization of d^T Q d - 2 b^T d under box constraints."""
    delta = np.zeros(len(b))
    for _ in range(sweeps):
        for j in range(len(delta)):
            if q[j,j] > 1e-14:
                delta[j] = np.clip((b[j]-q[j]@delta+q[j,j]*delta[j])/q[j,j],lower[j],upper[j])
    return delta


def solve(inputs,settings=Settings()):
    p = np.asarray(inputs.operator,complex)
    y = stack_observation(inputs.observation)
    coarse,norms,coordinates,spacing = coarse_dictionary(p,settings.doppler_step)
    score = np.sum(abs(coarse.conj().T@y)**2,axis=1).reshape(p.shape[1],-1)
    count = min(settings.candidates_per_user,len(coordinates))
    indices = np.concatenate([u*len(coordinates)+np.argsort(-score[u],kind="stable")[:count]
                              for u in range(p.shape[1])])
    users = indices//len(coordinates)
    centers = coordinates[indices%len(coordinates)].copy()
    scales = norms[indices]
    a0 = coarse[:,indices].copy()
    coarse_columns = coarse.shape[1]
    del coarse,score,norms
    derivatives = np.empty((2,a0.shape[0],a0.shape[1]),complex)
    for j,(u,position) in enumerate(zip(users,centers)):
        derivatives[:,:,j] = sensed_atom(p,u,position,True)[1]/scales[j]
    bounds = np.array([delay_bounds(d)-d for d in centers[:,0]])
    lower = np.column_stack([bounds[:,0],np.maximum(-spacing/2,-MAX_FREQUENCY-centers[:,1])])
    upper = np.column_stack([bounds[:,1],np.minimum(spacing/2,MAX_FREQUENCY-centers[:,1])])
    offsets = np.zeros_like(centers)
    noise = float(inputs.noise_variance)
    initial = max((np.sum(abs(y)**2)-y.size*noise)/(y.shape[1]*a0.shape[1]),noise*1e-3)
    variance = np.full(a0.shape[1],initial)
    trace,status = [],"MAX_ITERATIONS"
    for iteration in range(1,settings.iterations+1):
        a = a0+derivatives[0]*offsets[:,0]+derivatives[1]*offsets[:,1]
        mean,diagonal,inv_a = posterior(a,y,variance,noise)
        updated = variance_update(np.sum(abs(mean)**2,axis=1)+y.shape[1]*diagonal,y.shape[1],settings.rho)
        updated = np.maximum(updated,np.finfo(float).eps*max(1.,initial))
        delta_size = 0.
        if iteration > settings.warmup:
            selected = np.argsort(-updated,kind="stable")[:settings.offset_candidates]
            q,b = offset_quadratic(a,y,mean,variance,inv_a,derivatives,selected,noise)
            low = (lower[selected]-offsets[selected]).T.reshape(-1)
            high = (upper[selected]-offsets[selected]).T.reshape(-1)
            delta = bounded_quadratic(q,b,low,high,settings.offset_sweeps).reshape(2,-1).T
            offsets[selected] += delta
            delta_size = float(np.max(abs(delta),initial=0.))
        relative = float(np.linalg.norm(updated-variance)/np.linalg.norm(variance))
        variance = updated
        trace.append(dict(iteration=iteration,variance_relative_change=relative,
                          max_offset_increment=delta_size))
        if iteration > settings.warmup and relative < settings.tolerance and delta_size < settings.tolerance:
            status = "HYPERPARAMETER_CHANGE"
            break
    a = a0+derivatives[0]*offsets[:,0]+derivatives[1]*offsets[:,1]
    mean,_,_ = posterior(a,y,variance,noise)
    positions = centers+offsets
    gains = mean/scales[:,None]
    h = reconstruct(p.shape[1],y.shape[1],users,positions,gains)
    exact_observation = np.einsum("qkn,kmrn->qmr",p,h,optimize=True)
    exact_y = stack_observation(exact_observation)
    return dict(estimate=h,user_ids=users,positions=positions,gains=gains,
        iterations=iteration,stopping_reason=status,trace=trace,coarse_columns=coarse_columns,
        screened_columns=len(indices),residual_energy=float(np.sum(abs(y-exact_y)**2)),
        linearization_relative_error=float(np.linalg.norm(exact_y-a@mean)/max(np.linalg.norm(exact_y),1e-30)))

def expected_residual_energy(a, y, mean, diagonal, variance, noise):
    """E||Y-AX||², with all posterior cross-covariances in the trace identity."""
    residual = float(np.sum(abs(y-a@mean)**2))
    uncertainty = y.shape[1]*noise*float(np.sum(1-diagonal/variance))
    if uncertainty < -1e-10*max(residual, noise*y.size):
        raise FloatingPointError('Negative posterior observation uncertainty')
    return residual+max(uncertainty, 0.)

def solve_estimated_noise(inputs, settings, *, noise_shape=1e-4, noise_rate=1e-4,
          initial_noise_fraction=.01):
    p = np.asarray(inputs.operator, complex)
    y = stack_observation(inputs.observation)
    coarse, norms, coordinates, spacing = coarse_dictionary(p, settings.doppler_step)
    score = np.sum(abs(coarse.conj().T@y)**2, axis=1).reshape(p.shape[1], -1)
    count = min(settings.candidates_per_user, len(coordinates))
    indices = np.concatenate([u*len(coordinates)+np.argsort(-score[u], kind='stable')[:count]
                              for u in range(p.shape[1])])
    users = indices//len(coordinates)
    centers = coordinates[indices % len(coordinates)].copy()
    scales = norms[indices]
    a0 = coarse[:, indices].copy()
    coarse_columns = coarse.shape[1]
    del coarse, score, norms
    derivatives = np.empty((2, a0.shape[0], a0.shape[1]), complex)
    for j, (u, position) in enumerate(zip(users, centers)):
        derivatives[:, :, j] = sensed_atom(p, u, position, True)[1]/scales[j]
    bounds = np.array([delay_bounds(d)-d for d in centers[:, 0]])
    lower = np.column_stack([bounds[:, 0], np.maximum(-spacing/2, -MAX_FREQUENCY-centers[:, 1])])
    upper = np.column_stack([bounds[:, 1], np.minimum(spacing/2, MAX_FREQUENCY-centers[:, 1])])
    offsets = np.zeros_like(centers)
    noise = initial_noise_fraction*float(np.mean(abs(y)**2))
    if noise <= 0 or noise_rate <= 0 or y.size+noise_shape-1 <= 0:
        raise ValueError('Positive observed energy and valid Gamma noise prior required')
    initial_noise = noise
    initial = max((np.sum(abs(y)**2)-y.size*noise)/(y.shape[1]*a0.shape[1]), noise*1e-3)
    variance = np.full(a0.shape[1], initial)
    trace, status = [], 'MAX_ITERATIONS'
    for iteration in range(1, settings.iterations+1):
        a = a0+derivatives[0]*offsets[:, 0]+derivatives[1]*offsets[:, 1]
        mean, diagonal, inv_a = posterior(a, y, variance, noise)
        expected = expected_residual_energy(a, y, mean, diagonal, variance, noise)
        next_noise = (expected+noise_rate)/(y.size+noise_shape-1)
        updated = variance_update(np.sum(abs(mean)**2, axis=1)+y.shape[1]*diagonal,
                                  y.shape[1], settings.rho)
        updated = np.maximum(updated, np.finfo(float).eps*max(1., initial))
        delta_size = 0.
        if iteration > settings.warmup:
            selected = np.argsort(-updated, kind='stable')[:settings.offset_candidates]
            q, b = offset_quadratic(a, y, mean, variance, inv_a, derivatives, selected, noise)
            low = (lower[selected]-offsets[selected]).T.reshape(-1)
            high = (upper[selected]-offsets[selected]).T.reshape(-1)
            delta = bounded_quadratic(q, b, low, high, settings.offset_sweeps).reshape(2, -1).T
            offsets[selected] += delta
            delta_size = float(np.max(abs(delta), initial=0.))
        relative = float(np.linalg.norm(updated-variance)/np.linalg.norm(variance))
        noise_change = abs(next_noise-noise)/noise
        variance, noise = updated, float(next_noise)
        if not np.isfinite(noise) or noise <= 0:
            raise FloatingPointError('Nonfinite or nonpositive learned noise variance')
        trace.append(dict(iteration=iteration, variance_relative_change=relative,
            max_offset_increment=delta_size, noise_variance=noise,
            noise_relative_change=noise_change, expected_residual_energy=expected))
        if (iteration > settings.warmup and relative < settings.tolerance
                and delta_size < settings.tolerance and noise_change < settings.tolerance):
            status = 'HYPERPARAMETER_CHANGE'
            break
    a = a0+derivatives[0]*offsets[:, 0]+derivatives[1]*offsets[:, 1]
    mean, _, _ = posterior(a, y, variance, noise)
    positions = centers+offsets
    gains = mean/scales[:, None]
    h = reconstruct(p.shape[1], y.shape[1], users, positions, gains)
    exact_y = stack_observation(np.einsum('qkn,kmrn->qmr', p, h, optimize=False))
    return dict(estimate=h, user_ids=users, positions=positions, gains=gains,
        iterations=iteration, stopping_reason=status, trace=trace,
        coarse_columns=coarse_columns, screened_columns=len(indices),
        noise_variance=noise, initial_noise_variance=initial_noise,
        residual_energy=float(np.sum(abs(y-exact_y)**2)),
        linearization_relative_error=float(np.linalg.norm(exact_y-a@mean)/max(np.linalg.norm(exact_y), 1e-30)))

class OffGridReceiver:
    def __init__(self,configuration,method):
        self.configuration = deepcopy(configuration)
        self.method = method
        if method != 'offgrid_sbl' or configuration.get("schema") != "afdm-offgrid-baselines-v1":
            raise ValueError("registered off-grid method and configuration required")
        self.settings = Settings(**configuration["methods"][method]["solver"])
        self.signature = inference_signature(configuration,method)
        readout = configuration["readout"]
        path = ROOT/readout["path"]
        if sha256(path) != readout["sha256"]:
            raise ValueError("off-grid activity policy SHA256 mismatch")
        self.policy = json.loads(path.read_text())
        if (self.policy.get("schema") != "afdm-offgrid-activity-v1"
                or self.policy.get("statistic") != "relative_channel_frobenius_energy"
                or self.policy["methods"][method]["inference_sha256"] != self.signature):
            raise ValueError("off-grid activity policy is bound to a different inference algorithm")
        self.nodes = np.asarray(self.policy["snr_nodes_db"],float)
        self.thresholds = np.asarray(self.policy["methods"][method]["thresholds"],float)
        if (self.nodes.ndim != 1 or not len(self.nodes) or not np.isfinite(self.nodes).all()
                or np.any(np.diff(self.nodes) <= 0)
                or self.thresholds.shape != self.nodes.shape or not np.isfinite(self.thresholds).all()
                or np.any(self.thresholds < 0)):
            raise ValueError("valid frozen SNR nodes and activity thresholds required")

    def infer(self,inputs,*,observer=None):
        if not isinstance(inputs,ReceiverInput):
            raise TypeError("public four-field ReceiverInput required")
        if observer is not None:
            raise ValueError("off-grid receivers return their native traces")
        if inputs.observation.shape[-1] != 16 or inputs.operator.shape[-1] != 16:
            raise ValueError("current AFDM physical model requires N=16")
        started = time.perf_counter()
        result = solve(inputs,self.settings)
        score,energy = activity_score(result["estimate"])
        index = nearest_node(public_snr_db(inputs),self.nodes)
        threshold = float(self.thresholds[index])
        arrays = dict(estimate=result["estimate"],component_user_ids=result["user_ids"],
            folded_delay_samples=result["positions"][:,0],
            doppler_hz=result["positions"][:,1]*30000.,component_coefficients=result["gains"],
            activity_score=score,channel_energy=energy,
            activity_decision=(score >= threshold)&(energy > 0))
        if not all(np.isfinite(value).all() for value in arrays.values()):
            raise FloatingPointError("nonfinite off-grid receiver output")
        record = {key:value for key,value in result.items()
                  if key not in ("estimate","user_ids","positions","gains")}
        record.update(status="COMPLETE",method=self.method,algorithm_id=self.method,
            seconds=time.perf_counter()-started,configuration=self.configuration,
            inference_sha256=self.signature,source_sha256=inference_sources(self.method),
            activity_threshold=threshold,readout_snr_node_db=float(self.nodes[index]),
            activity_statistic=self.policy["statistic"],activity_comparator=">=",
            validation_status=self.configuration.get("validation_status","DEVELOPMENT"),
            component_coefficient_convention="free complex coefficient of scalar-phase-normalized AFDM atom",
            component_count_meaning="screened dictionary rows",
            supplied_noise_variance_used=True,truth_loaded=False,truth_used_in_inference=False,
            true_snr_or_activity_count_used=False,activity_count_or_truth_used=False,
            continuous_delay_doppler_estimation=True,paper_implementation_scope="AFDM/MMV adaptation")
        return arrays,record

    def run(self,input_path,output_path,*,observer=None):
        output = Path(output_path)
        if output.suffix != ".npz" or output.exists() or output.with_suffix(".json").exists():
            raise ValueError("fresh .npz output required")
        arrays,record = self.infer(load_input(input_path),observer=observer)
        output.parent.mkdir(parents=True,exist_ok=True)
        np.savez_compressed(output,**arrays)
        record.update(input_sha256=sha256(input_path),output_sha256=sha256(output))
        write_json(output.with_suffix(".json"),record)
        return record

def infer_estimated(self, inputs):
    if inputs.observation.shape[-1] != 16 or inputs.operator.shape[-1] != 16:
        raise ValueError('Current AFDM physical model requires N=16')
    noise_setting = self.noise_config['offgrid_sbl']
    prior_count = noise_setting['noise_prior_observation_weight']*inputs.observation.size
    controls = dict(noise_shape=1+prior_count, noise_rate=prior_count*inputs.noise_variance,
                    initial_noise_fraction=noise_setting['initial_noise_fraction'])
    result = solve_estimated_noise(inputs, self.base.settings, **controls)
    score, energy = activity_score(result['estimate'])
    value = public_snr_db(replace(inputs, noise_variance=result['noise_variance']))
    index = nearest_node(value, self.base.nodes)
    threshold = float(self.base.thresholds[index])
    arrays = dict(estimate=result['estimate'], component_user_ids=result['user_ids'],
        folded_delay_samples=result['positions'][:, 0], doppler_hz=result['positions'][:, 1]*30000.,
        component_coefficients=result['gains'], activity_score=score, channel_energy=energy,
        activity_decision=(score >= threshold)&(energy > 0))
    record = {key: value for key, value in result.items()
              if key not in ('estimate', 'user_ids', 'positions', 'gains')}
    record.update(activity_threshold=threshold, readout_snr_node_db=float(self.base.nodes[index]),
        public_estimated_snr_db=value, activity_statistic=self.base.policy['statistic'],
        activity_comparator='>=', activity_decision_available=True,
        noise_controls=controls, noise_fixed=False,
        noise_prior_reference_variance=inputs.noise_variance,
        noise_prior_reference_source='Spatial covariance MDL estimate of the same observation',
        noise_prior_observations=prior_count,
        component_coefficient_convention='free complex coefficient of scalar-phase-normalized AFDM atom',
        component_count_meaning='screened dictionary rows', continuous_delay_doppler_estimation=True,
        paper_implementation_scope='AFDM/shared-MMV adaptation of Wei Eqs. (45)-(46), with an observation-estimated Gamma prior scale')
    return arrays, record, [result['initial_noise_variance']]+[
        row['noise_variance'] for row in result['trace']]
