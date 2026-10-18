"""SNR comparison: Proposed and four baselines, estimated phase and noise."""
from _common import main

# Same seeds, scene count and conditions as the completed 500-scene panel.
EXPERIMENT = dict(
    description=__doc__, variable='snr_db', xlabel='SNR (dB)',
    values=[-4, -2, 0, 2, 4, 6, 8], scenes=500, seed=202610172000001,
    snr_db=0., users=40, frames=16, activity_probability=.1,
)

if __name__ == '__main__':
    raise SystemExit(main(EXPERIMENT))
