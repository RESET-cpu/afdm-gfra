"""Pilot-frame sweep."""
from scenario.catalog import DEFAULT

NAME = 'pilot_frames'
DESCRIPTION = 'Pilot-frame sweep'
KIND = 'receiver'


def conditions(config, args):
    values = args.values if args.values is not None else config['values']
    return [dict(DEFAULT, frames=v) for v in values]


def main(argv=None):
    from experiment.suite import main as execute
    return execute(NAME, argv)


if __name__ == '__main__':
    raise SystemExit(main())
