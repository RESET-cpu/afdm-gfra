"""Pilot-resource experiment: vary frames at fixed users, activity and SNR."""
from _common import main

# Planned sweep; these defaults are not an already completed experiment.
EXPERIMENT = dict(
    description=__doc__, variable='frames', xlabel='Pilot frames',
    values=[8, 16, 24, 32, 40, 48], scenes=500, seed=202610180100001,
    snr_db=0., users=40, frames=16, activity_probability=.1,
)

if __name__ == '__main__':
    raise SystemExit(main(EXPERIMENT))
