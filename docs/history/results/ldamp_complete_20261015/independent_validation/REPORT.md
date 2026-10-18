# Frozen L-DAMP comparison

10 independent physical scenes, reused across 6 SNRs and all methods. Every case is retained.
Raw full-channel NMSE includes inactive-user error and is the primary channel metric. Ratios pool squared errors and true channel energy before converting to dB.
Uncertainty uses 5,000 paired physical-scene bootstrap replicates. It is conditional on the fixed trained model, inference seed and calibrated activity rule.
Zero observed activity errors can yield a degenerate bootstrap interval; this does not establish a zero population error rate.

Physical scope: `known_phase_geometry_v4`, 40 candidate users, 16 observations, 4 × 4 UPA, nominal activity probability 0.1 conditioned on a nonempty scene, and intra-user path direction spread 0.0°. The effective measurement operator is supplied exactly to every receiver. Geometry and noise conventions are retained in each case's `generation.json`.

## Frozen solver settings

| Method | Settings |
|---|---|
| Proposed | At most 600 iterations; minimum 60; damping 0.2; covariance mode isotropic |
| L-DAMP joint | 10 iterations; 4 user-row directions; inference seed 202610150201 |
| L-DAMP original | 10 iterations; 8 matrix probes; inference seed 202610146201 |
| Off-grid SBL | At most 120 iterations; 48 offset candidates; 5 offset sweeps |
| GNN-ASPL | 10 AMP steps; 9 GNN updates; frozen mixed-SNR/grid checkpoint |
| GAMP-SBL | At most 1000 iterations; tolerance 1e-06; stopping rule paper_absolute_mean |
| SOMP | At most 64 atoms; stopping rule noise_discrepancy |

Iteration/probe counts refer to different operations and are not equal computational budgets.

GNN checkpoint metadata records `TRAINED_UNQUALIFIED` and `formal_qualification=False`; preliminary training is `False`. Its loader checks the declared training contract, but this comparison does not establish full reproduction of the reference paper. This status is not an observed inference failure.

![Paired comparison](comparison.png)

## Full-channel NMSE (dB)

| Method | -4 | -2 | 0 | 2 | 4 | 6 |
|---|---:|---:|---:|---:|---:|---:|
| Proposed | -8.417 | -10.216 | -11.597 | -12.827 | -14.179 | -15.394 |
| L-DAMP joint | -3.199 | -3.798 | -4.905 | -6.050 | -6.607 | -6.940 |
| L-DAMP original | -3.009 | -3.686 | -4.853 | -5.896 | -6.475 | -6.864 |
| Off-grid SBL | -6.099 | -7.560 | -8.834 | -9.574 | -9.673 | -9.960 |
| GNN-ASPL | -4.682 | -5.293 | -5.871 | -6.412 | -6.916 | -7.274 |
| GAMP-SBL | -3.367 | -4.211 | -4.933 | -5.546 | -6.054 | -6.403 |
| SOMP | -2.971 | -3.525 | -3.960 | -4.228 | -4.548 | -4.554 |

## Activity error rate (%)

| Method | -4 | -2 | 0 | 2 | 4 | 6 |
|---|---:|---:|---:|---:|---:|---:|
| Proposed | 0.50 | 0.25 | 0.25 | 0.25 | 0.00 | 0.00 |
| L-DAMP joint | 0.75 | 0.50 | 0.25 | 0.25 | 0.25 | 0.25 |
| L-DAMP original | 0.50 | 0.50 | 0.25 | 0.25 | 0.25 | 0.25 |
| Off-grid SBL | 0.50 | 0.50 | 0.50 | 0.50 | 0.50 | 0.50 |
| GNN-ASPL | 0.75 | 0.50 | 0.75 | 0.50 | 0.25 | 0.25 |
| GAMP-SBL | 1.00 | 1.00 | 0.75 | 0.75 | 0.50 | 0.25 |
| SOMP | 0.75 | 1.00 | 1.00 | 1.00 | 0.75 | 0.50 |

## Misses / false alarms

Counts are shown separately because active and inactive user populations differ. Their denominators and conditional rates are in `STATISTICS.csv`.

| Method | -4 | -2 | 0 | 2 | 4 | 6 |
|---|---:|---:|---:|---:|---:|---:|
| Proposed | 2 / 0 | 1 / 0 | 1 / 0 | 1 / 0 | 0 / 0 | 0 / 0 |
| L-DAMP joint | 3 / 0 | 2 / 0 | 1 / 0 | 1 / 0 | 1 / 0 | 1 / 0 |
| L-DAMP original | 2 / 0 | 2 / 0 | 1 / 0 | 1 / 0 | 1 / 0 | 1 / 0 |
| Off-grid SBL | 2 / 0 | 2 / 0 | 2 / 0 | 2 / 0 | 2 / 0 | 2 / 0 |
| GNN-ASPL | 3 / 0 | 2 / 0 | 2 / 1 | 1 / 1 | 1 / 0 | 1 / 0 |
| GAMP-SBL | 2 / 2 | 2 / 2 | 2 / 1 | 2 / 1 | 1 / 1 | 1 / 0 |
| SOMP | 2 / 1 | 2 / 2 | 2 / 2 | 2 / 2 | 2 / 1 | 2 / 0 |

## Inactive-user share of full-channel squared error (%)

This is an error decomposition using truth only for offline scoring; it is not an inference mask or an alternative primary metric.

| Method | -4 | -2 | 0 | 2 | 4 | 6 |
|---|---:|---:|---:|---:|---:|---:|
| Proposed | 0.64 | 0.08 | 0.01 | 0.00 | 0.00 | 0.00 |
| L-DAMP joint | 23.22 | 24.27 | 20.98 | 17.56 | 14.75 | 14.40 |
| L-DAMP original | 25.69 | 25.08 | 22.67 | 19.44 | 15.76 | 15.03 |
| Off-grid SBL | 32.19 | 25.79 | 20.13 | 14.56 | 9.72 | 7.02 |
| GNN-ASPL | 0.69 | 0.47 | 1.02 | 0.89 | 0.71 | 1.29 |
| GAMP-SBL | 26.07 | 22.04 | 19.17 | 17.26 | 16.40 | 16.85 |
| SOMP | 20.19 | 21.26 | 22.10 | 25.66 | 27.65 | 33.12 |

## Candidate minus original L-DAMP

Negative differences favor the joint candidate. Intervals use the same sampled scenes for both methods.

| SNR | NMSE difference / dB | 95% interval | AER difference / percentage points | 95% interval |
|---:|---:|---|---:|---|
| -4 | -0.190 | [-0.275, -0.081] | 0.25 | [0.00, 0.75] |
| -2 | -0.112 | [-0.197, -0.017] | 0.00 | [0.00, 0.00] |
| 0 | -0.052 | [-0.154, 0.093] | 0.00 | [0.00, 0.00] |
| 2 | -0.153 | [-0.261, -0.093] | 0.00 | [0.00, 0.00] |
| 4 | -0.131 | [-0.240, -0.068] | 0.00 | [0.00, 0.00] |
| 6 | -0.076 | [-0.161, -0.027] | 0.00 | [0.00, 0.00] |

## Computation and scope

| Method | Mean inference seconds | Recorded runtime warnings | Variance-range flags |
|---|---:|---:|---:|
| Proposed | 17.43 | 51120 | — |
| L-DAMP joint | 103.00 | 0 | 0 |
| L-DAMP original | 14.91 | 0 | 2 |
| Off-grid SBL | 1.11 | 147420 | — |
| GNN-ASPL | 0.14 | 0 | — |
| GAMP-SBL | 0.69 | 170940 | — |
| SOMP | 0.04 | 30084 | — |

Timings are receiver-reported solve/readout times, excluding model loading and data generation. Small input checks and record-building boundaries differ across receivers; the evaluation did not separately time the entire public call. Method order is fixed for every condition. Device and thread settings, exact model/configuration identities and source snapshots are in `PLAN.json`; warnings retain counts and source locations in each case.
Proposed and both L-DAMP versions use MPS for their neural networks with CPU numerical operations. SOMP, GAMP-SBL, GNN-ASPL and Off-grid SBL use their frozen CPU implementations. These are measured implementation runtimes on this host, not equal-hardware or asymptotic complexity comparisons.
The original eight matrix probes and candidate four user-row probes have different computational costs. The candidate retains a stochastic correction approximation; two development seeds produced 8.5%–23.0% relative channel differences despite small aggregate NMSE changes.
The denoiser uses per-beam residual variances and does not model the full correlated error distribution. These empirical results do not prove state evolution or convergence for the structured AFDM operator.
Both selected branch checkpoints occur at the final saved validation evaluation. Training optimization convergence has not been established; these are fixed-budget trained candidates. The complete standalone branch histories and their limits are reported in `../TRAINING_TRAJECTORY_AUDIT.json` and `../training_trajectories.png`.
Evaluation seeds were checked against 13 recorded training, validation and readout/development cohorts in `../COMPARISON_SEED_AUDIT.json`, with no overlap. Two historical shared-readout configuration references are missing; their hashes were not marked verified. Seed-bearing plans/certificates and the actual configurations used here remain available. This does not establish complete reproduction of that historical workflow.
Range flags have different definitions: the joint candidate counts mean variance outside [0.001, 1000]; the original counts any beam outside [0.001, 100]. No flags does not establish that the complete error distribution matches training.
Secondary error after each method’s own activity-decision mask is in `STATISTICS.csv`; it never replaces raw full-channel NMSE. No true activity mask is used for that operation.
This report does not itself promote a model or establish rare-event or cross-training-seed reliability.
