# White-network estimated-phase main SNR

The explicit request and frozen plan are in
`result/snr_comparison/data/white_phase_frontend_marginal_1000_20261106`.
This package is independent of all existing batches.

- `receiver.py`: verifies native white checkpoint provenance and delegates to the unchanged phase frontend and numerical receiver. Multiple inheritance places the white loader/context before the numerical base; the original phase constructor is bypassed because its verifier accepts only colored checkpoints.
- `common.py`: validates the completed white and four-group ablation receipts, exact per-SNR summary coverage, hashes and predecessor process exit. Also validates new saved outputs.
- `prepare.py`: freezes six-SNR scene coverage, references, controls and source/weight bindings without inference.
- `run.py`: gated full-case preflight and bounded two-worker queue, explicit resume without overwriting incomplete cases.
- `report.py`: re-scores all 18000 predictions for the new white estimated-phase result and two saved references; checks phase reproduction and outputs energy-pooled NMSE, AER, errors and iteration caps.

The actual pretrained models use float32; scalar/linear algebra retains the existing implementation's precision. TF32 and cuDNN benchmark are disabled. No new inference is permitted while either predecessor is incomplete. The final plotting/manuscript update is performed after the batch verifies and its processes exit.
