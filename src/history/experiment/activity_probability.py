"""Activity-load experiment: change Bernoulli probability at fixed user count."""
from _common import main, DEFAULTS

# Nonempty activity draws; the receiver gets the conditional marginal prior.
EXPERIMENT = dict(
    DEFAULTS,
    description=__doc__, variable='activity_probability', xlabel='Activity sampling probability',
    values=[.05, .1, .15, .2, .25], seed=202610180300001,
)

if __name__ == '__main__':
    from _suite_entry import dispatch
    raise SystemExit(dispatch(__file__))
