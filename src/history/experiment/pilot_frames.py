"""Pilot-resource experiment: vary frames at fixed users, activity and SNR."""
from _common import main, DEFAULTS

# Planned sweep; these defaults are not an already completed experiment.
EXPERIMENT = dict(
    DEFAULTS,
    description=__doc__, variable='frames', xlabel='Pilot frames',
    values=[8, 16, 24, 32, 40, 48], seed=202610180100001,
)

if __name__ == '__main__':
    from _suite_entry import dispatch
    raise SystemExit(dispatch(__file__))
