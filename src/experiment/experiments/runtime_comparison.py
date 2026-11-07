"""Runtime and accuracy on the shared 1000-scene evaluation prefix."""
from scenario.catalog import DEFAULT

NAME = 'runtime_comparison'
DESCRIPTION = 'Runtime and accuracy, 1000 shared scenes'
KIND = 'receiver'


def conditions(config, args):
    values = args.snr if args.snr is not None else config['snr_db']
    return [dict(DEFAULT, snr_db=v) for v in values]


def main(argv=None):
    from experiment.suite import main as execute
    return execute(NAME, argv)


if __name__ == '__main__':
    raise SystemExit(main())
