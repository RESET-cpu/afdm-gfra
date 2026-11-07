"""SNR comparison: paired NMSE and AER curves."""
from common import execute_public as execute
from style import receiver_sweep


def draw(data, out, args):
    return receiver_sweep(data, out, 'snr_comparison', 'snr_db', 'SNR (dB)', args.aer_scale)


if __name__ == '__main__':
    raise SystemExit(execute('snr_comparison', draw))
