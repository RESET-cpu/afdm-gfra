"""User-count sweep."""
from scenario.catalog import DEFAULT

NAME = 'user_count'
DESCRIPTION = 'User-count sweep'
KIND = 'receiver'


def conditions(config, args):
    values = args.values if args.values is not None else config['values']
    return [dict(DEFAULT, users=v) for v in values]


def main(argv=None):
    from experiment.suite import main as execute
    return execute(NAME, argv)


if __name__ == '__main__':
    raise SystemExit(main())
