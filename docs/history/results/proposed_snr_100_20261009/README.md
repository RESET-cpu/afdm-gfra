# Proposed SNR performance — 100 paired scenes per point

SNR: −4, −2, 0, 2, 4, 6 dB. Both on-grid and off-grid, proposed only; 1200 inferences from 100 independent base seeds. K=40, Q=16, activity probability=0.1.

The receiver uses the verified accelerated stopping parameters and unchanged FP32 weights. The runtime directory contains the frozen source, configuration and checkpoint copies.

Read STATUS.json for current progress, SUMMARY.json / SNR_METRICS.csv for each SNR/grid point, MODEL_LOADS.json for separate loading cost, and RUN.log for completed cases. SNR_PERFORMANCE.png is generated when the queue finishes. Incomplete point metrics are null; completed subsets, failures and MAX_ITERATIONS remain explicit.

Each grid/point/scene directory retains public input, separate truth, three primary receiver outputs, the full native trace, grouped warnings, and an attempt receipt with file hashes.

To pause at a case boundary, create PAUSE in this directory. To resume pending cases, remove PAUSE and rerun the exact command array saved in LAUNCH.json. Finished and failed attempts are preserved; failures are not retried automatically.
