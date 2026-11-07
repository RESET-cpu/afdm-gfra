"""NTN-TDL profiles."""
from scenario.catalog import DEFAULT

NAME = 'cross_channel'
DESCRIPTION = 'NTN-TDL profiles'
KIND = 'receiver'


def conditions(config, args):
    profiles = args.profiles if args.profiles is not None else config['profiles']
    snr = args.snr if args.snr is not None else config['snr_db']
    if any(p not in ('A', 'B', 'C', 'D') for p in profiles):
        raise ValueError('Unknown channel profile')
    return [dict(DEFAULT, channel_model=p, snr_db=v) for p in profiles for v in snr]


def main(argv=None):
    from experiment.suite import main as execute
    return execute(NAME, argv)


if __name__ == '__main__':
    raise SystemExit(main())
