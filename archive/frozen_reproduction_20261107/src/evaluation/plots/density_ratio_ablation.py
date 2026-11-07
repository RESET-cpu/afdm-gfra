"""Plot saved ablation results; this does not enable the deferred experiment."""
from common import execute_public as execute
from style import receiver_sweep


def draw(data, out, args):
    outputs, notes = receiver_sweep(data, out, 'density_ratio_ablation', 'snr_db', 'SNR (dB)', args.aer_scale)
    notes.append('The controlled comparison is between the two STMP evidence choices; the ten-layer receiver is a full-model reference.')
    return outputs, notes


if __name__ == '__main__':
    raise SystemExit(execute('density_ratio_ablation', draw))
