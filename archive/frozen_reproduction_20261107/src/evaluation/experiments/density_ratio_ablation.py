"""STMP evidence ablation, deferred by user."""
from evaluation.scenes import DEFAULT

NAME = 'density_ratio_ablation'
DESCRIPTION = 'STMP evidence ablation, deferred by user'
KIND = 'receiver'


def conditions(config, args):
    values = args.values if args.values is not None else config['values']
    return [dict(DEFAULT, snr_db=v) for v in values]


def main(argv=None):
    from evaluation.suite import main as execute
    return execute(NAME, argv)


if __name__ == '__main__':
    raise SystemExit(main())
