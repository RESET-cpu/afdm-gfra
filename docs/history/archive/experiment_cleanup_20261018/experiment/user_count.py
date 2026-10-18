"""Candidate-user experiment: fixed sampling probability and pilot frames."""
from _common import main

# Planned sweep; increasing users also increases the expected active count.
EXPERIMENT = dict(
    description=__doc__, variable='users', xlabel='Candidate users',
    values=[20, 40, 60, 80, 100], scenes=500, seed=202610180200001,
    snr_db=0., users=40, frames=16, activity_probability=.1,
)

if __name__ == '__main__':
    raise SystemExit(main(EXPERIMENT))
