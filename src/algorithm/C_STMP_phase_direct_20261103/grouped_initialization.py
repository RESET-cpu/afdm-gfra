"""Wrapped-slope initialization using grouped training covariance marginals.

All groups share the same nonnegative user powers and phase slopes. Their
Gaussian marginal objectives are summed; dependence between groups is omitted.
Grouping uses only the fixed training second moment, never observations or
physical path parameters. A single group retains the full training moment.
"""
import time

import numpy as np
from scipy.cluster.hierarchy import leaves_list, linkage
from scipy.optimize import minimize
from scipy.spatial.distance import squareform

from project import ROOT
from utils import sha256
from algorithm.proposed.phase_math import observed_covariances, stationary_maximum
from algorithm.STMP.fast_initialization import _MemoizedObjective, _Sample, factor_value


def training_groups(moment, rows, columns, group_size=4):
    """Deterministic average-linkage grouping of output-row covariance blocks."""
    moment = np.asarray(moment, complex)
    if moment.shape != (rows*columns, rows*columns):
        raise ValueError('Training moment and channel dimensions differ')
    if (type(group_size) is not int or group_size < 1 or rows % group_size
            or not np.isfinite(moment).all()):
        raise ValueError('Finite training moment and group size dividing output rows required')
    blocks = moment.reshape(rows, columns, rows, columns)
    weight = np.sum(abs(blocks)**2, axis=(1, 3))
    weight = (weight+weight.T)/2
    if np.any(np.diag(weight) <= 0):
        raise ValueError('Positive training energy in every output row required')
    if group_size == rows:
        order = np.arange(rows)
    else:
        denominator = np.sqrt(np.diag(weight)[:, None]*np.diag(weight)[None])
        similarity = np.sqrt(np.clip(weight/denominator, 0., 1.))
        distance = 1-similarity
        np.fill_diagonal(distance, 0.)
        order = leaves_list(linkage(squareform(distance, checks=False), method='average'))
    groups = [np.sort(order[start:start+group_size]) for start in range(0, rows, group_size)]
    groups.sort(key=lambda group: tuple(group.tolist()))
    retained = sum(weight[np.ix_(group, group)].sum() for group in groups)/weight.sum()
    return groups, dict(groups=[group.tolist() for group in groups], group_size=group_size,
        grouping='Average linkage of normalized training output-row block Frobenius norms',
        grouping_uses_observation=False, retained_covariance_squared_frobenius_fraction=float(retained))


def grouped_problem(observation, pilot, moment, noise, groups):
    """Construct each Q*group_size marginal with antenna columns as replicates."""
    y, p, moment = (np.asarray(value, complex) for value in (observation, pilot, moment))
    if y.ndim != 3 or p.ndim != 3 or y.shape[0] != p.shape[0]:
        raise ValueError('Expected observation[Q,M,R] and pilot[Q,K,N]')
    q, _, n = p.shape
    rows = y.shape[2]
    if (moment.shape != (rows*n, rows*n) or not groups
            or len({len(group) for group in groups}) != 1
            or sorted(int(row) for group in groups for row in group) != list(range(rows))
            or not all(np.isfinite(value).all() for value in (y, p, moment))
            or not np.isfinite(noise) or noise <= 0):
        raise ValueError('Finite compatible arrays, positive noise and a partition of rows required')
    grams, samples = [], []
    for group in groups:
        group = np.asarray(group, dtype=int)
        index = (group[:, None]*n+np.arange(n)).ravel()
        grams.append(observed_covariances(p, moment[np.ix_(index, index)]))
        samples.append(_Sample(y[:, :, group].transpose(0, 2, 1).reshape(q*len(group), -1)))
    return np.stack(grams), tuple(samples), np.repeat(np.arange(q), len(groups[0]))


def _factors(covariances, samples, *, weight_required=True):
    value, inverses, weights = 0., [], []
    for covariance, sample in zip(covariances, samples):
        current, inverse, weight = factor_value(covariance, sample, weight_required=weight_required)
        value += current
        inverses.append(inverse)
        if weight_required:
            weights.append(weight)
    return float(value), np.stack(inverses), np.stack(weights) if weight_required else None


def objective(parameters, grams, samples, noise, frames, power_scale, phase_scale):
    """Sum of marginal logdet + trace objectives and its analytic gradient."""
    k = grams.shape[1]
    power, beta = parameters[:k]*power_scale, parameters[k:]/phase_scale
    phase = np.exp(1j*beta[:, None]*frames)
    rotated = grams*phase[None, :, :, None]*phase[None, :, None, :].conj()
    covariance = noise*np.eye(len(frames))[None]+np.einsum('k,gkij->gij', power, rotated)
    value, _, weight = _factors(covariance, samples)
    power_gradient = power_scale*np.einsum('gji,gkij->k', weight, rotated).real
    derivative = 1j*(frames[:, None]-frames[None])*rotated
    phase_gradient = power/phase_scale*np.einsum('gji,gkij->k', weight, derivative).real
    return value, np.r_[power_gradient, phase_gradient]


def directional_phase(grams, weights, frames, previous):
    """Numerical stationary candidates of the zero-power directional derivative."""
    q = int(frames.max()+1)
    rows = len(frames)//q
    cross = np.sum(grams.conj().reshape(-1, q, rows, q, rows)
                   *(-weights).reshape(-1, q, rows, q, rows), axis=(0, 2, 4))
    coefficients = np.array([np.trace(cross, offset=-lag) for lag in range(q)])
    return stationary_maximum(coefficients, previous)


def _local_objective(parameters, grams, bases, samples, frames, power_scale, phase_scale):
    power, beta = parameters[0]*power_scale, parameters[1]/phase_scale
    phase = np.exp(1j*frames*beta)
    rotated = grams*phase[None, :, None]*phase[None, None, :].conj()
    value, _, weight = _factors(bases+power*rotated, samples)
    derivative = 1j*(frames[:, None]-frames[None])*rotated
    return value, np.array([
        power_scale*np.einsum('gji,gij->', weight, rotated).real,
        power/phase_scale*np.einsum('gji,gij->', weight, derivative).real])


def coordinate(grams, samples, noise, frames, rho, *, sweeps=1, local_maxiter=8):
    """Nonnegative-power coordinate fitting from the noise-only covariance."""
    groups, k, length, _ = grams.shape
    span = float(max(frames.max(), 1))
    beta, power, rotated = np.zeros(k), np.zeros(k), grams.copy()
    covariance = np.broadcast_to(noise*np.eye(length), (groups, length, length)).astype(complex).copy()
    initial, _, weight = _factors(covariance, samples)
    priority = [directional_phase(grams[:, user], weight, frames, 0.)[1] for user in range(k)]
    order = np.argsort(-np.asarray(priority), kind='stable')
    trace, records = [initial], []
    for sweep in range(sweeps):
        for user in order:
            before = trace[-1]
            base = covariance-power[user]*rotated[:, user]
            base = (base+base.conj().transpose(0, 2, 1))/2
            zero_value, inverse, weight = _factors(base, samples)
            proposal, score, roots = directional_phase(grams[:, user], weight, frames, beta[user])
            phase = np.exp(1j*frames*proposal)
            proposal_gram = grams[:, user]*phase[None, :, None]*phase[None, None, :].conj()
            weighted = inverse@proposal_gram
            curvature = float(np.einsum('gij,gji->', weighted, weighted).real)
            proposed_power = max(0., score)/curvature if curvature > 0 else 0.
            candidates = [(before, beta[user], power[user], 'previous'),
                          (zero_value, proposal, 0., 'zero_power_direction')]
            starts = []
            if power[user] > 0:
                starts.append((power[user], beta[user], 'current_start'))
            if proposed_power > 0:
                starts.append((proposed_power, proposal, 'directional_start'))
            optimizers = []
            for start_power, start_beta, label in starts:
                evaluate = _MemoizedObjective(_local_objective,
                    (grams[:, user], base, samples, frames, float(rho), span))
                solved = minimize(evaluate, np.array([start_power/rho, start_beta*span]),
                    jac=True, method='L-BFGS-B', bounds=[(0., None), (None, None)],
                    options=dict(maxiter=local_maxiter, maxls=30, ftol=1e-11, gtol=1e-7))
                value, _ = evaluate(solved.x)
                candidates.append((value, solved.x[1]/span, solved.x[0]*rho, label))
                optimizers.append(dict(start=label, iterations=int(solved.nit),
                    success=bool(solved.success), message=str(solved.message),
                    objective_evaluations=evaluate.evaluations))
            if power[user] == 0 and zero_value == before:
                candidates[0] = candidates[1]
            _, selected_beta, selected_power, chosen = min(candidates, key=lambda item: item[0])
            beta[user] = (selected_beta+np.pi)%(2*np.pi)-np.pi
            power[user] = selected_power
            phase = np.exp(1j*frames*beta[user])
            rotated[:, user] = grams[:, user]*phase[None, :, None]*phase[None, None, :].conj()
            covariance = base+power[user]*rotated[:, user]
            actual, _, _ = _factors(covariance, samples, weight_required=False)
            if actual > before+1e-8*max(1., abs(before)):
                raise FloatingPointError('Grouped coordinate objective increased')
            trace.append(actual)
            records.append(dict(sweep=sweep+1, user=int(user), before=before, after=actual,
                chosen=chosen, power=float(power[user]), slope=float(beta[user]),
                null_power_negative_derivative=float(score), stationary_roots=roots,
                starting_power=float(proposed_power), optimizers=optimizers))
    return beta, power, dict(objective=trace, coordinates=records, coordinate_order=order.tolist(),
                             sweeps=sweeps, local_maxiter=local_maxiter)


def joint(grams, samples, noise, frames, beta, power, rho, *, maxiter=30):
    """Fit one shared power and slope per user across all groups."""
    k, span = len(beta), float(max(frames.max(), 1))
    parameters = np.r_[power/rho, beta*span]
    evaluate = _MemoizedObjective(objective, (grams, samples, noise, frames, float(rho), span))
    trace = [evaluate(parameters)[0]]
    solved = minimize(evaluate, parameters, jac=True, method='L-BFGS-B',
        bounds=[(0., None)]*k+[(None, None)]*k,
        options=dict(maxiter=maxiter, maxls=40, ftol=1e-11, gtol=1e-7),
        callback=lambda current: trace.append(evaluate(current)[0]))
    value, gradient = evaluate(solved.x)
    trace.append(value)
    if np.max(np.diff(trace), initial=0.) > 1e-8*max(1., abs(trace[0])):
        raise FloatingPointError('Grouped joint objective increased')
    projected = gradient.copy()
    projected[:k] = np.where((solved.x[:k] == 0)&(gradient[:k] > 0), 0., gradient[:k])
    return (solved.x[k:]/span+np.pi)%(2*np.pi)-np.pi, solved.x[:k]*rho, dict(
        objective=trace, iterations=int(solved.nit), success=bool(solved.success),
        message=str(solved.message), projected_gradient_max=float(np.max(abs(projected))),
        objective_evaluations=evaluate.evaluations, reused_objective_evaluations=evaluate.hits)


def estimate(inputs, policy, receiver_configuration):
    """Observation-only initialization using a hash-bound training second moment."""
    started = time.perf_counter()
    if policy.get('method', 'grouped_covariance') != 'grouped_covariance':
        raise ValueError('Expected grouped_covariance initialization')
    sweeps, local_iterations, joint_iterations = (policy.get(key, default) for key, default in
        [('sweeps', 1), ('local_iterations', 8), ('joint_iterations', 30)])
    if any(type(value) is not int or value < 1 for value in (sweeps, local_iterations, joint_iterations)):
        raise ValueError('Positive integer optimization budgets required')
    path = ROOT/policy['training_second_moment']
    if sha256(path) != policy['training_second_moment_sha256']:
        raise ValueError('Frozen training moment changed')
    scale = float(receiver_configuration['scale'])
    if not np.isfinite(scale) or scale <= 0 or not 0 < inputs.activity_prior < 1:
        raise ValueError('Positive channel scale and an activity prior between zero and one required')
    q, k, n = inputs.pilot.shape
    with np.load(path, allow_pickle=False) as saved:
        moment = np.asarray(saved['second_moment'], complex)/scale**2
    groups, grouping = training_groups(moment, inputs.observation.shape[2], n, policy.get('group_size', 4))
    noise = inputs.noise_variance/scale**2
    grams, samples, frames = grouped_problem(inputs.observation/scale, inputs.pilot, moment, noise, groups)
    setup_seconds = time.perf_counter()-started
    beta, power, coordinates = coordinate(grams, samples, noise, frames, inputs.activity_prior,
        sweeps=sweeps, local_maxiter=local_iterations)
    beta, power, optimization = joint(grams, samples, noise, frames, beta, power, inputs.activity_prior,
        maxiter=joint_iterations)
    return beta, dict(method='grouped_covariance_marginal_objective', seconds=time.perf_counter()-started,
        setup_seconds=setup_seconds, **grouping, covariance_orders=[q*len(group) for group in groups],
        training_moment_sha256=policy['training_second_moment_sha256'],
        coordinates=coordinates, optimization=optimization, fitted_powers=power.tolist(),
        shared_user_powers=True, shared_user_slopes=True, physical_path_search_used=False,
        phase_grid_used=False, truth_used=False,
        objective='sum_g logdet(C_g) + trace(C_g^-1 Y_g Y_g^H)/M',
        initial_covariance='Noise only; slopes enter through marginal power directional derivatives',
        limitation='Cross-group dependence is omitted; antenna columns are treated as replicates. '
                   'The training Gaussian model is an approximation to the physical channel prior.')
