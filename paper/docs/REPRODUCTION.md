# Manuscript reproduction map

This map describes the **current working manuscript**, checked on 2026-11-09.
It separates plotting saved aggregates from recomputing numerical results.
The latest adoption records and `src/configs/plots/manuscript.json` determine
the actual data; a historical directory name is not evidence of a new run.

Start with [the installation and asset guide](../../REPRODUCING.md).
The original agreed replacement order and review decisions remain in
[REVIEW_DECISIONS.md](REVIEW_DECISIONS.md). This map does not reopen them.

## The ten figures

For any identifier below, run the following from the repository root,
substituting that identifier for `<name>` and using a new output directory:

```text
python run_experiments.py plot --figures <name> --output result/figure_preview_<name>
```

For a comparison against retained manuscript PDFs, use
`python run_experiments.py plot --check`. This does not replace the figures.
Both commands read saved data; neither runs a receiver.

| Figure | Identifier | Saved source | Current status / sample budget |
|---|---|---|---|
| 1 | `system_multiframe` | Shen artwork in `reference/literature/shen2025.pdf`, reconstructed by `src/plotting/manuscript/system.py` | Method illustration; not a numerical experiment |
| 2 | `factor_graph` | `src/plotting/manuscript/factor.py` | Method illustration; common method-source verification also requires the configured source files |
| 3 | `learned_receiver` | `result/channel_denoising/figures/white_mainline_500_20261107/scene000_example.npz`, Cai artwork, `main.aux` | Adopted white-network example from one saved scene; not an aggregate performance curve |
| 4 | `channel_denoising` | `result/channel_denoising/figures/white_mainline_500_20261107/PLOT_DATA.json` | White GP-MP adopted; 500 scenes × 4 channels × 6 noise levels = 12,000 GP-MP queries |
| 5 | `convergence` | `result/snr_comparison/figures/convergence_first30_300_20261105/PAPER_PLOT_DATA.json` | Adopted 30 paired scenes, 0 dB; three methods, first 150 displayed iterations from 300 saved iterations |
| 6 | `snr_comparison` | `result/snr_comparison/figures/main_snr_white_20261107/PLOT_DATA.json` | White GP-MP and GP-MP-EP adopted; 1,000 scenes at each of six SNR values |
| 7 | `pilot_frames` | `result/pilot_frames/latest_20261109/SUMMARY.json` | Adopted white GP-MP/GP-MP-EP; nine curves, Q = 8, 12, 16, 20, 24; 500 paired scenes per point; channel NMSE only |
| 8 | `user_count` | `result/user_count/figures/redraw_beta01_500_20261028/PLOT_DATA.json` | Historical 500-scene curve retained; agreed white replacement not started |
| 9 | `activity_probability` | `result/activity_probability/figures/stmp_c_stmp_500_20261026/PLOT_DATA.json` | Historical 500-scene curve retained; agreed white replacement not started |
| 10 | `cross_channel` | `result/cross_channel/figures/full_500_paper_20261028/PLOT_DATA.json` | Historical 500-scene curve retained; agreed white replacement not started |

The current nine configurations in the main-SNR plot and each curve's labels
are selected by the plotting configuration, not by the default methods of a
new generic experiment. Saved aggregate reproduction does not prove that all
of these configurations can be recomputed from a source-only download.

The method figures require Times New Roman, PyMuPDF and the configured source
PDFs. Downloaded third-party papers and the raw channel-example array are not
distributed in the source snapshot. Figure 3 reads equation references from
`paper/main.aux`: compile `main.tex` first in a LaTeX environment with
IEEEtran, as described in [the manuscript README](../README.md). For example,
run `latexmk -pdf main.tex` from `paper`, then return to the repository
root for plotting. An updated manuscript may legitimately change label hashes;
review its figure references before refreshing the asset inventory.

## Numerical recomputation

The generic current experiment definitions are under `src/experiment/experiments`
and the configurations under `src/configs/experiments`. Each has `plan`,
`inspect`, `run` and `summarize` stages. Planning writes hashes and selection;
only `run` performs inference. The root reproduction guide gives a separate
one-scene GP-MP diagnostic configuration.

Current source paths use `receiver.gp_mp` and the organized catalog. The
recorded batches retain their original plans and source bindings. The current
pilot sweep additionally records its validated execution-source inventory;
see [the resume record](../../archive/pilot_resume_20261107/README.md).
Other frozen implementations are isolated in the reproduction archive.
Their `PLAN.json` hashes must not be rewritten to bypass validation.
Replaying a saved batch on another machine requires its original inputs and
a documented path/source adaptation.

For the adopted white experiments, the frozen execution records are:

- GP-MP/GP-MP-EP model identity: `FINAL.json` and the two candidate binding
  files named there.
- Main SNR adoption: [paper/checks/white_snr_adopted_20261107/README.md](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/white_snr_adopted_20261107/README.md).
- Denoising and Figure 3 adoption:
  [paper/checks/white_denoising_adopted_20261107/README.md](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/white_denoising_adopted_20261107/README.md).
- Convergence adoption:
  [paper/checks/convergence_30_adopted_20261106/README.md](https://github.com/RESET-cpu/afdm-gfra/blob/9ac940e477d9f2a81ff687c85ba488f5a106f88b/paper/checks/convergence_30_adopted_20261106/README.md).
- Subsequent stage request: `result/white_followup_20261107/REQUEST.json`;
  pilot-frame partial results are preserved; the prior failure is retained in the resume record.

The pilot-frame replacement was adopted on 2026-11-09 from GitHub commit
`07189dbd78c4f4e27636ae6ab2b33663e3b9649e` (plot layout), with unchanged
aggregate data from `50dd757cdca668f5ddf357d8033434b957d1577d`; see
[the adoption and verification record](../../result/pilot_frames/latest_20261109/ADOPTION.json).
The published receipt distinguishes 15,000 full-array rescorings from 7,500
reaggregations of retained per-user errors. The local adoption checks the 45
aggregate NMSE values, curve coordinates, source hashes, and figure reproduction;
it does not repeat the unavailable per-scene prediction checks.
The STMP Q = 8 result is 34.70 dB; the full value is retained in the saved
data and discussed in the manuscript results.
The subsequent user-count, activity and cross-channel replacements remain pending. See [the result index](../../result/README.md)
for status. Successful source checks and saved-aggregate rendering do not establish
complete numerical reproduction or retraining.
