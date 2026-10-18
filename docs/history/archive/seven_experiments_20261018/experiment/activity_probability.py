"""Activity-load experiment: change Bernoulli probability at fixed user count."""
from _common import main

# Nonempty activity draws; the receiver gets the conditional marginal prior.
EXPERIMENT = dict(
    description=__doc__, variable='activity_probability', xlabel='Activity sampling probability',
    values=[.05, .1, .15, .2, .25], scenes=500, seed=202610180300001,
    snr_db=0., users=40, frames=16, activity_probability=.1,
)

if __name__ == '__main__':
    raise SystemExit(main(EXPERIMENT))
