# GP-MP

This package provides the white-noise-trained mainline receiver independently of
the historical `algorithm.C_STMP*`, `training.colored*` and experiment adapter
packages. Existing code and results remain at their original paths.

## Interfaces

- `algorithm.GP_MP.receiver:Receiver(configuration, device='auto', noise_mode='estimated')`
  accepts the public known-phase `ReceiverInput`.
- `algorithm.GP_MP.phase_receiver:PhaseReceiver(configuration, device='auto', noise_mode='estimated')`
  accepts only `UnknownPhaseInput`, estimates phase once from observations and
  original pilots, and holds it fixed during the conditional receiver iterations.
- `algorithm.GP_MP.denoising:Denoiser(configuration, device='auto', batch_size=4)` implements
  `infer(query, variance, priors=None)` for complete complex channels of shape
  `[batch,16,16,16]`. It returns `(mean, metadata)` in the same normalized
  coordinates as its query; the complex noise variance uses those coordinates.
  Truth-dependent priors are rejected. Finite-difference variance probes are not
  evaluated by this denoising-only interface. A positive integer batch size is
  required; four preserves the earlier channel-denoising experiment batch size.

Both receiver constructors accept the existing verified white configuration
paths (or equivalent binding dictionaries). The default `device='auto'` selects
CUDA when available and CPU otherwise. Experiment runners remain responsible for
their declared thread counts, FP32 settings and disabled TF32/cuDNN benchmark.

The network loader retains the checkpoint's exact historical serialized schema,
parameterization and state-dictionary keys, and requires training covariance
strength `max_strength=0`. The complete binding validator also verifies the
training specifications, completed budgets, selected checkpoints, classifier
teacher and scientific receiver controls. Historical paths inside those immutable
provenance records are not runtime imports of historical code or a request to
load its network weights.

The scalar message equations, activity classifier architecture and numeric record
types reuse common `algorithm.STMP` modules. This reuse does not load STMP score
checkpoints. The adopted white first network and its matching classifier are the
only inference networks loaded.

Numerical extraction and mechanical class-renaming evidence is recorded in
`archive/white_mainline_20261107/EXTRACTION.json`. CPU checks are in
`src/tests/test_gp_mp_mainline_20261107.py`; their synthetic observations are test
fixtures, not experiment results. GPU equivalence and batch launch remain the
separate mainline adoption task.
