"""Fixed iteration adapters. Frozen solver files and module globals stay intact."""
import ast
from copy import deepcopy
from dataclasses import asdict, replace
import inspect
from types import FunctionType, MethodType
import textwrap

import numpy as np


def fixed_loop(function, snapshot=None):
    """Clone one solver; disable its single convergence break, keeping all updates.

    The optional callback receives local state immediately before the original
    stop test and its boolean value. It must only read that state.
    """
    tree = ast.parse(textwrap.dedent(inspect.getsource(function)))
    guards = [node for node in ast.walk(tree) if isinstance(node, ast.If)
              and any(isinstance(child, ast.Break) for child in node.body)]
    if len(guards) != 1:
        raise ValueError('Expected exactly one native early-stopping guard')
    guard = guards[0]
    # Evaluate the original condition for diagnosis, but never take its break.
    guard.test = ast.Call(func=ast.Name(id='_convergence_keep_running', ctx=ast.Load()),
                          args=[guard.test, ast.Call(func=ast.Name(id='locals', ctx=ast.Load()),
                                                    args=[], keywords=[])], keywords=[])
    ast.fix_missing_locations(tree)

    def keep_running(would_stop, state):
        if snapshot is not None:
            snapshot(state, bool(would_stop))
        return False

    namespace = dict(function.__globals__, _convergence_keep_running=keep_running)
    exec(compile(tree, '<fixed-iteration-convergence-adapter>', 'exec'), namespace)
    return namespace[function.__name__]


def bind_fixed_infer(receiver, iterations):
    """Bind a private infer function to one instance, without monkeypatching."""
    native = receiver.infer.__func__
    namespace = dict(native.__globals__)
    namespace['run_spatial_score'] = fixed_loop(namespace['run_spatial_score'])
    cloned = FunctionType(native.__code__, namespace, native.__name__, native.__defaults__, native.__closure__)
    cloned.__kwdefaults__ = native.__kwdefaults__
    receiver.infer = MethodType(cloned, receiver)
    receiver.controls = replace(receiver.controls, iterations=iterations)
    receiver.configuration['ep']['iterations'] = iterations


def infer_mp(method, plan, inputs, collector):
    from algorithm.STMP.noise import EstimatedNoiseSTMPReceiver
    from evaluation.white_matched_fp32_20261105.receiver import Receiver

    base_configuration = deepcopy(plan['configurations'][method])
    if method == 'STMP':
        receiver = EstimatedNoiseSTMPReceiver(base_configuration, device=plan['runtime']['learned_device'])
        numerical = receiver.base
    else:
        receiver = Receiver(base_configuration, device=plan['runtime']['learned_device'])
        numerical = receiver
    bind_fixed_infer(numerical, plan['iterations'])
    c = numerical.configuration

    def observe(row, state, *unused):
        probability = state.activity.copy()
        collector.add(row['iteration'], state.mean * c['scale'], probability >= c['decision_threshold'],
                      dict(row), probability=probability,
                      native_would_stop=bool(row['converged']))

    arrays, record = receiver.infer(inputs, observer=observe)
    record['source_configuration'] = base_configuration
    return arrays, record


def infer_sbl(method, plan, inputs, collector):
    from algorithm.baseline import offgrid_sbl as kernel
    from algorithm.baseline._base import EstimatedNoiseBaselineReceiver
    from evaluation.offgrid_budget_20261105.receiver import Receiver
    from system.receiver.atoms import activity_score
    from system.receiver.noise_estimation import estimate_spatial_noise
    from importlib.util import module_from_spec, spec_from_file_location
    from project import ROOT

    budget = int(method.rsplit('(', 1)[1][:-1])
    original = (EstimatedNoiseBaselineReceiver('offgrid_sbl', device='cpu') if budget == 7
                else Receiver(plan['configurations'][method]).original)
    source_settings = asdict(original.base.settings)
    settings = replace(original.base.settings, iterations=plan['iterations'])
    spec = spec_from_file_location('convergence_adopted_readout', ROOT / plan['activity_readout'])
    readout = module_from_spec(spec)
    spec.loader.exec_module(readout)
    policy = readout.load_policy()
    spatial, noise_record = estimate_spatial_noise(inputs.observation)
    control = original.noise_config['offgrid_sbl']
    prior_count = control['noise_prior_observation_weight'] * inputs.observation.size
    controls = dict(noise_shape=1 + prior_count, noise_rate=prior_count * spatial,
                    initial_noise_fraction=control['initial_noise_fraction'])
    power = float(np.mean(abs(inputs.observation)**2))

    def decide(h, noise):
        score, energy = activity_score(h)
        snr = readout.estimated_snr(power, noise)
        threshold, node = readout.threshold('offgrid_sbl', snr, policy=policy)
        return readout.decide(score, energy, threshold), score, energy, dict(
            activity_threshold=float(threshold), threshold_node=int(node), estimated_snr_db=float(snr))

    def snapshot(state, would_stop):
        # Same posterior/reconstruction as the native return at this iteration.
        a = (state['a0'] + state['derivatives'][0] * state['offsets'][:, 0]
             + state['derivatives'][1] * state['offsets'][:, 1])
        mean, _, _ = kernel.posterior(a, state['y'], state['variance'], state['noise'])
        h = kernel.reconstruct(state['p'].shape[1], state['y'].shape[1], state['users'],
                               state['centers'] + state['offsets'], mean / state['scales'][:, None])
        decision, score, _, rule = decide(h, state['noise'])
        collector.add(state['iteration'], h, decision, dict(state['trace'][-1], **rule),
                      probability=score, native_would_stop=would_stop)

    result = fixed_loop(kernel.solve_estimated_noise, snapshot)(
        replace(inputs, noise_variance=spatial), settings, **controls)
    decision, score, energy, rule = decide(result['estimate'], result['noise_variance'])
    arrays = dict(estimate=result['estimate'], activity_decision=decision, activity_score=score,
                  channel_energy=energy, noise_variance_estimate=np.asarray(result['noise_variance']))
    record = {k: v for k, v in result.items() if k not in ('estimate', 'user_ids', 'positions', 'gains')}
    record.update(source_settings=source_settings, effective_settings=asdict(settings),
                  source_configuration=original.configuration, noise_controls=controls,
                  noise_estimation=noise_record, doppler_points=budget, **rule,
                  activity_rule='Current main-SNR rule transferred without refitting',
                  timing_includes_extra_posterior_reconstruction=True)
    return arrays, record
