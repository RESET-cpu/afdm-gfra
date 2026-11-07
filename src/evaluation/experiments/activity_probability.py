"""Activity-probability sweep."""
from evaluation.scenes import DEFAULT

NAME = 'activity_probability'
DESCRIPTION = 'Activity-probability sweep'
KIND = 'receiver'


def conditions(config, args):
    values = args.values if args.values is not None else config['values']
    return [dict(DEFAULT, activity_probability=v) for v in values]


def main(argv=None):
    from evaluation.suite import main as execute
    return execute(NAME, argv)


if __name__ == '__main__':
    raise SystemExit(main())
