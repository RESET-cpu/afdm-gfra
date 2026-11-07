"""Candidate-user experiment: fixed sampling probability and pilot frames."""
from _common import main, DEFAULTS

# Planned sweep; increasing users also increases the expected active count.
EXPERIMENT = dict(
    DEFAULTS,
    description=__doc__, variable='users', xlabel='Candidate users',
    values=[20, 40, 60, 80, 100], seed=202610180200001,
)

if __name__ == '__main__':
    from _suite_entry import dispatch
    raise SystemExit(dispatch(__file__))
