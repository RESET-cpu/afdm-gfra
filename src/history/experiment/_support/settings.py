"""Shared physical defaults, receiver bindings and training-sample variants."""
from pathlib import Path
from . import ROOT
from .storage import read, sha
from afdm_jadcedd.algorithm.baselines.baseline_noise import EstimatedNoiseBaselineReceiver
from afdm_jadcedd.algorithm.proposed_noise_candidate import EstimatedNoiseProposedReceiver

DEFAULTS = dict(scenes=500, snr_db=0., users=40, frames=16, activity_probability=.1, device="cpu")
SNR_VALUES = (-4, -2, 0, 2, 4, 6)
PHASE_CONFIG = "configs/proposed_frontend.json"
HISTORICAL_SNR = "results/baseline_comparison_500_20261018/PLAN.json"
METHODS = ['proposed', 'offgrid_sbl', 'gnn', 'gamp', 'somp']
CONFIGS = dict(proposed='configs/proposed.json', offgrid_sbl='configs/offgrid_baselines.json',
               gnn='configs/baselines.json', gamp='configs/baselines.json', somp='configs/baselines.json')
LABELS = dict(proposed='Proposed', offgrid_sbl='Off-grid SBL', gnn='GNN-ASPL', gamp='GAMP-SBL', somp='SOMP')


def proposed_bundles(small_config=None, full_config=None):
    """Bind complete three-network variants; never relabel one set as small-data.

    N_train is the current prior's clean-channel bank size. Prior pretraining
    exposure is deliberately not inferred from that number.
    """
    from afdm_jadcedd.algorithm.proposed.configuration import verify
    bundles, hashes = {}, {}
    full_path = Path(full_config).resolve() if full_config else ROOT / CONFIGS['proposed']
    for name, path in [('proposed', full_path)] + (
            [('proposed_small', Path(small_config).resolve())] if small_config else []):
        config = read(path)
        verify(config)
        prior = read(ROOT / config['prior_definition'])
        count = prior['train_samples']
        if isinstance(count, bool) or not isinstance(count, int) or count < 1:
            raise ValueError('Prior must declare a positive integer train_samples')
        bundles[name] = dict(configuration=config, train_samples=count,
                             label=f'Proposed (N_train={count:,})',
                             sample_scope='Clean-channel bank size; prior initialization exposure not certified')
        for asset in [path, ROOT / config['prior_definition']] + [ROOT / config[k] for k in
                      ('first_checkpoint', 'second_checkpoint', 'evidence_checkpoint')]:
            hashes[str(asset.resolve())] = sha(asset)
    if small_config:
        full, small = [bundles[k] for k in ('proposed', 'proposed_small')]
        if small['train_samples'] >= full['train_samples']:
            raise ValueError('Small-data prior must contain fewer clean training channels')
        for key in ('first_checkpoint', 'second_checkpoint', 'evidence_checkpoint'):
            if full['configuration'][key+'_sha256'] == small['configuration'][key+'_sha256']:
                raise ValueError('Small-data comparison requires independently trained complete weights: '+key)
        import torch
        for key in ('first_checkpoint', 'second_checkpoint', 'evidence_checkpoint'):
            a = torch.load(ROOT / full['configuration'][key], map_location='cpu', weights_only=False)
            b = torch.load(ROOT / small['configuration'][key], map_location='cpu', weights_only=False)
            if a['config'] != b['config']:
                raise ValueError('Sample-size comparison requires identical network architectures: '+key)
        ignored = {'prior_definition', 'prior_definition_sha256', 'initialization'}
        ignored.update(k+s for k in ('first_checkpoint', 'second_checkpoint', 'evidence_checkpoint') for s in ('', '_sha256'))
        controls = lambda c: {k:v for k,v in c.items() if k not in ignored}
        if controls(full['configuration']) != controls(small['configuration']):
            raise ValueError('Sample-size comparison requires equal inference controls and coordinate scale')
    return bundles, hashes


def method_label(spec, method):
    return spec.get('proposed_bundles', {}).get(method, {}).get('label', LABELS.get(method, method))


def solver(method, spec):
    if method in ('proposed', 'proposed_small'):
        config = spec.get('proposed_bundles', {}).get(method, {}).get('configuration')
        if config is None:
            config = read(ROOT / spec.get('receiver_configs', CONFIGS)[method])
        return EstimatedNoiseProposedReceiver(config, device=spec['device'])
    return EstimatedNoiseBaselineReceiver(method, config=ROOT / spec.get('receiver_configs', CONFIGS)[method], device=spec['device'])


def bind_receivers(spec):
    """Store the selected configuration paths and native SBL controls in the plan."""
    spec["receiver_configs"] = {m: CONFIGS[m] for m in spec["methods"] if m in CONFIGS}
    spec["phase_config"] = PHASE_CONFIG
    if "offgrid_sbl" in spec["methods"]:
        receiver = EstimatedNoiseBaselineReceiver("offgrid_sbl", config=ROOT / CONFIGS["offgrid_sbl"], device="cpu")
        spec["offgrid_budget"] = receiver.base.settings.iterations
        spec["offgrid_tolerance"] = receiver.base.settings.tolerance
        spec["offgrid_threshold_status"] = receiver.base.policy.get("threshold_status", "FROZEN")


def validate_seed(seed):
    if not isinstance(seed, int) or isinstance(seed, bool) or seed < 0:
        raise ValueError("Scene seed must be a nonnegative integer")


def validate_methods(methods):
    if not methods or len(set(methods)) != len(methods):
        raise ValueError("Distinct receiver methods required")
