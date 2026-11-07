"""Gaussian-site activity evidence with the shared STMP moment/site updates."""
from receiver.stmp.denoiser import Denoiser as STMPDenoiser


class Denoiser(STMPDenoiser):
    @staticmethod
    def validate_evidence(moments, evidence):
        if evidence is not None:
            raise ValueError('Gaussian-site ablation does not use a classifier')
