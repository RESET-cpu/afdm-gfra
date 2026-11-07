"""Activity-probability sweep from saved paired results."""
from common import execute_public as execute
from style import receiver_sweep


def draw(data, out, args):
    return receiver_sweep(data, out, 'activity_probability', 'activity_probability',
                          'Activity probability', args.aer_scale)


if __name__ == '__main__':
    raise SystemExit(execute('activity_probability', draw))
