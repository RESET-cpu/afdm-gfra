"""SNR comparison with an optional complete small-training-bank Proposed."""
from _common import main, DEFAULTS, SNR_VALUES

# Reuse the completed panel at matching conditions; 8 dB is outside this sweep.
EXPERIMENT = dict(
    DEFAULTS,
    description=__doc__, variable='snr_db', xlabel='SNR (dB)',
    values=list(SNR_VALUES), seed=202610172000001,
    training_sample_comparison=True, reuse_completed_snr=True,
)

if __name__ == '__main__':
    from _suite_entry import dispatch
    raise SystemExit(dispatch(__file__))
