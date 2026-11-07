"""Proposed and five baselines, with the original figure's receivers frozen."""
import json
from pathlib import Path

from afdm_jadcedd.algorithm.baselines import receiver as baselines
from afdm_jadcedd.algorithm.proposed import configuration as proposed
from afdm_jadcedd.utils import sha256
from afdm_jadcedd.project import CONFIGS, repository_path, configuration_paths

ALGORITHMS = ('proposed', 'somp', 'gamp', 'gnn', 'offgrid_sbl', 'ldamp')
DEFAULT_CONFIGS = {name: CONFIGS/'baselines.json' for name in ALGORITHMS[1:]}
DEFAULT_CONFIGS['proposed'] = proposed.DEFAULT_CONFIG
DEFAULT_CONFIGS['offgrid_sbl'] = CONFIGS/'offgrid_baselines.json'
DEFAULT_CONFIGS['ldamp'] = CONFIGS/'ldamp.json'


def build_receiver(algorithm='proposed', *, config=None, device='auto'):
    if algorithm not in ALGORITHMS:
        raise ValueError('Select one mainline algorithm: '+', '.join(ALGORITHMS))
    config = repository_path(config or DEFAULT_CONFIGS[algorithm])
    if algorithm == 'proposed':
        configuration = proposed.load_configuration(config)
        if configuration.get('schema') == 'afdm-proposed-estimated-phase-v2':
            from afdm_jadcedd.algorithm.proposed_frontend_candidate import FrontendReceiver
            return FrontendReceiver(configuration, device=device)
        if configuration.get('schema') == 'afdm-proposed-estimated-phase-projected-energy-v1':
            from afdm_jadcedd.algorithm.proposed_projected_energy import ProjectedEnergyReceiver
            return ProjectedEnergyReceiver(configuration, device=device)
        if configuration.get('schema') == 'afdm-proposed-estimated-phase-projected-v1':
            from afdm_jadcedd.algorithm.proposed_projected import ProjectedPhaseReceiver
            return ProjectedPhaseReceiver(configuration, device=device)
        if configuration.get('schema') == 'afdm-proposed-estimated-phase-average-v1':
            from afdm_jadcedd.algorithm.proposed_average import AveragedPhaseReceiver
            return AveragedPhaseReceiver(configuration, device=device)
        if configuration.get('schema') == 'afdm-proposed-iterative-phase-v1':
            from afdm_jadcedd.algorithm.proposed_phase import IterativePhaseReceiver
            return IterativePhaseReceiver(configuration, device=device)
        if configuration.get('schema') == 'afdm-proposed-estimated-phase-v1':
            from afdm_jadcedd.algorithm.proposed.unknown_phase import UnknownPhaseReceiver
            return UnknownPhaseReceiver(configuration, device=device)
        from afdm_jadcedd.algorithm.proposed.receiver import Receiver
        return Receiver(configuration, device=device)
    if algorithm == 'offgrid_sbl':
        from afdm_jadcedd.algorithm.baselines.offgrid.receiver import OffGridReceiver,load_configuration
        return OffGridReceiver(configuration_paths(load_configuration(config)),algorithm)
    if algorithm == 'ldamp':
        path = config or DEFAULT_CONFIGS['ldamp']
        configuration = json.loads(Path(path).read_text())
        if configuration.get('schema') == 'afdm-ldamp-output-tsvd-v1':
            from afdm_jadcedd.algorithm.baselines.ldamp_output import LDAMPOutputReceiver
            return LDAMPOutputReceiver(configuration, device=device)
        if configuration.get('schema') == 'afdm-ldamp-joint-v1':
            from afdm_jadcedd.algorithm.baselines.ldamp_joint.receiver import LDAMPJointReceiver, load_configuration
            return LDAMPJointReceiver(load_configuration(path), device=device)
        from afdm_jadcedd.algorithm.baselines.ldamp.receiver import LDAMPReceiver, load_configuration
        return LDAMPReceiver(load_configuration(config), device=device)
    return baselines.BaselineReceiver(configuration_paths(baselines.load_configuration(config)), algorithm)


def verify_algorithms():
    manifest = json.loads((CONFIGS/'mainline_assets.json').read_text())
    if tuple(manifest['methods']) != ALGORITHMS:
        raise ValueError('Mainline selection differs from the frozen comparison')
    for relative, expected in manifest['sha256'].items():
        if sha256(repository_path(relative)) != expected:
            raise ValueError('Frozen mainline asset changed: '+relative)
    report = {'proposed': proposed.verify()}
    for method in ALGORITHMS[1:]:
        if method == 'ldamp':
            from afdm_jadcedd.algorithm.baselines.ldamp.receiver import verify
            report[method] = verify()
            continue
        receiver = build_receiver(method)
        validation = receiver.configuration.get('validation_status','SELECTED')
        report[method] = dict(status='PASS', network_queries=0,
            inference_sha256=receiver.signature,
            validation_status=validation)
    return report
