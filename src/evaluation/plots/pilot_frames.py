"""Pilot-frame sweep from saved paired results."""
from common import execute_public as execute
from style import receiver_sweep


def draw(data, out, args):
    return receiver_sweep(data, out, 'pilot_frames', 'frames', 'Number of pilot frames', args.aer_scale)


if __name__ == '__main__':
    raise SystemExit(execute('pilot_frames', draw))
