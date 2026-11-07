"""Use the frozen phase computation with the verified white-network loader."""
from project import ROOT
from utils import read_json, sha256
from system.receiver.unknown_phase import UnknownPhaseInput
from algorithm.C_STMP_phase_frontend_marginal_20261104.receiver import Receiver as PhaseReceiver
from algorithm.C_STMP_phase_init_marginal_20261104 import initialization
from evaluation.white_matched_20261105.receiver import Receiver as WhiteReceiver


class Receiver(PhaseReceiver, WhiteReceiver):
    def __init__(self, configuration, *, device='cuda', noise_mode='estimated'):
        binding = read_json(configuration)
        if binding['schema'] != 'c-stmp-marginal-phase-frontend-20261104-v1':
            raise ValueError('Explicit frozen phase binding required')
        for key in ('receiver_configuration', 'phase_configuration', 'initializer_source'):
            if sha256(ROOT / binding[key]) != binding[key + '_sha256']:
                raise ValueError('Changed phase binding: ' + key)
        self.frontend_binding = binding
        self.phase_controls = initialization.Controls(
            **read_json(ROOT / binding['phase_configuration'])['phase_estimation'])
        # PhaseReceiver.__init__ uses the colored-only provenance verifier.
        # Its unchanged infer method instead resolves super() through WhiteReceiver.
        WhiteReceiver.__init__(self, ROOT / binding['receiver_configuration'],
                               device=device, noise_mode=noise_mode)

    def infer(self, inputs, *, observer=None, phase_observer=None):
        if not isinstance(inputs, UnknownPhaseInput):
            raise TypeError('Estimated-phase evaluation requires raw observation and original pilots')
        return super().infer(inputs, observer=observer, phase_observer=phase_observer)
