# Independent score-prior training result

Training completed 30,000 steps in 565.5 seconds.
The selected checkpoint is step 27,000, with held-out weighted
objective 0.117853. The declared validation
plateau criterion was not reached before the step limit.
This is an empirical denoising result, not a receiver-performance or convergence guarantee.

The model has 198,322 parameters and was independently initialized.
Training/validation scene overlap is 0.
The final denoising check uses 512 validation
channels and all sixteen beams, with exact 0.1/0.9 activity-mixture weighting.

| Complex noise variance | Mixture NMSE (dB) | Active-only NMSE (dB) | Inactive real MSE |
|---|---:|---:|---:|
| 0.001–0.01 | -28.898 | -28.958 | 1.01467e-06 |
| 0.01–0.1 | -21.478 | -21.597 | 1.11021e-05 |
| 0.1–1 | -14.976 | -15.092 | 4.79231e-05 |
| 1–10 | -9.220 | -9.324 | 0.000162193 |
| 10–100 | -4.155 | -4.272 | 0.000585385 |

For comparison, the scalar linear shrinkage using the same mixed training
variance gives the following on exactly the same validation inputs:

| Complex noise variance | Linear mixture NMSE (dB) | Linear active-only NMSE (dB) | Linear inactive real MSE |
|---|---:|---:|---:|
| 0.001–0.01 | -14.457 | -22.865 | 0.0017581 |
| 0.01–0.1 | -5.972 | -10.092 | 0.00888139 |
| 0.1–1 | -1.315 | -2.337 | 0.00887778 |
| 1–10 | -0.173 | -0.313 | 0.00175387 |
| 10–100 | -0.018 | -0.032 | 0.000194213 |

The zero estimator has 0 dB mixture NMSE, 0 dB active-only NMSE, and zero inactive
MSE in every interval. These component results make the contribution of the
inactive majority explicit. The scalar linear reference is not a full
covariance-aware channel estimator.

The activity mixture is part of the learned marginal prior; no oracle activity
is supplied at inference. The training importance sampler uses known training
labels only. No receiver test truth or old network weight is used.

`best.pt` is the selected inference checkpoint; `last.pt` preserves the last
optimization state. `MODEL.json` binds the checkpoint hash and normalization.
`PLAN.json`, `HISTORY.json`, `TRAINING.json`, `VALIDATION.json`, and frozen source
copies record provenance. `VERIFICATION.json` records score/MSE equivalence,
batch independence, finite-difference versus automatic derivative checks, and
CPU/MPS parity. `BASELINES.json` records zero and linear references separately.
The learning curves are in `TRAINING_CURVE.png` and `.pdf`.

The next required test is the complete AMP receiver on independent AFDM scenes.
The shared per-beam marginal model does not explicitly exploit common activity
or channel correlations across beams. Gaussian denoising validation alone does
not establish AWGN decoupling or stable AMP iteration for the structured pilot
matrix.
