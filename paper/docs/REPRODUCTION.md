# Manuscript reproduction map

This map describes the **current working manuscript**, checked on 2026-11-14.
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
The commands use saved sources; neither runs a receiver. For an author-supplied
PDF, the plotting entry verifies its source hash and copies the published asset;
this verifies figure identity, not numerical recomputation.

| Figure | Identifier | Saved source | Current status / sample budget |
|---|---|---|---|
| 1 | `system_multiframe` | `src/plotting/manuscript/system.py` and geometric symbols in `artwork.py` | Method illustration; not a numerical experiment |
| 2 | `factor_graph` | `src/plotting/manuscript/factor.py` | Method illustration drawn from the posterior factorization |
| 3 | `learned_receiver` | `result/channel_denoising/figures/white_mainline_500_20261107/scene000_example.npz`, geometric network symbol in `artwork.py`, `main.aux` | Adopted white-network example from one saved scene; not an aggregate performance curve |
| 4 | `channel_denoising` | `result/channel_denoising/figures/white_mainline_500_20261107/PLOT_DATA.json` | White GP-MP adopted; 500 scenes × 4 channels × 6 noise levels = 12,000 GP-MP queries |
| 5 | `convergence` | `result/convergence/figures/current/convergence.pdf` | Author-supplied two-method PDF adopted from `6c965cc`; GP-MP and STMP, iterations 1–150. See its adoption record for source verification. |
| 6 | `snr_comparison` | `result/snr_comparison/figures/main_snr_white_20261107/PLOT_DATA.json` | White GP-MP and GP-MP-EP adopted; 1,000 scenes at each of six SNR values |
| 7 | `pilot_frames` | `result/pilot_frames/latest_20261109/SUMMARY.json` | Adopted white GP-MP/GP-MP-EP; nine curves, Q = 8, 12, 16, 20, 24; 500 paired scenes per point; channel NMSE only |
| 8 | `user_count` | `result/user_count/latest_20261109/user_count_nmse.pdf` | Author-supplied PDF updated from `043455b` (retrieved at `33cbaf3`); nine curves, K = 20, 40, 60, 80, 100. This commit contains figures only; sample counts, model bindings, and raw-result verification are not independently established by the image. |
| 9 | `activity_probability` | `result/activity_probability/latest_20261109/activity_probability_nmse.pdf` | Author-supplied PDF adopted from `6013d47`; nine curves, nominal activity probability 0.05–0.25. This commit contains figures only; sample counts, model bindings, and raw-result verification are not independently established by the image. |
| 10 | `cross_channel` | `result/cross_channel/figures/white_known_ep_500/cross_channel_ABC_nmse.pdf` | Author-supplied ABC vector PDF updated from `6c965cc`; seven curves including GP-MP-EP, with a single-row legend. Source identity and manuscript integration verified; numerical records are separate. |

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
The user-count figure was adopted on 2026-11-09 at the author's request from
GitHub commit `cf7fa010dc7ef2e35831d2ca25167d5ea0fce83e`; see
[its adoption record](../../result/user_count/latest_20261109/ADOPTION.json).
The previous figure and plotting configuration are preserved in
`archive/user_count_figure_adoption_20261109/before/`. This is a figure adoption;
the earlier device-count protocol and C1 records do not establish the
provenance of the newly supplied curves.
The layouts of Figures 7 and 8 were updated from `043455b1edc6501c4981e8e1545f94567bafe9d6`,
retrieved at `33cbaf3029ce2c8fbc07ab2c0a32eb2b892b6759`. The pilot aggregate
file is byte-identical to the prior adopted summary. The integrated pilot renderer
uses the revised axes and legend positions; Figure 8 uses the supplied PDF.
The previous assets and adoption records are preserved in
`archive/sweep_figure_update_20261109_33cbaf3/before/`.
The activity-probability figure was adopted on 2026-11-10 at the author's request
from GitHub commit `6013d4791ef0b5b45590014fd2536e9968f0bff7`; see
[its adoption record](../../result/activity_probability/latest_20261109/ADOPTION.json).
The supplied vector PDF contains nine curves, including GP-MP-EP and three
Off-grid SBL settings. Its size remains 3.5 × 2.65 inches. The previous figure
and source configuration are preserved in
`archive/activity_figure_update_20261110_6013d47/before/`.
The commit contains PDF/PNG assets only, so this adoption verifies figure
identity and manuscript integration, not the underlying numerical experiment.
The cross-channel figure was replaced on 2026-11-14 with the ABC comparison
from `ddb9f8668e9ec801ca00f72a6616b72aa4b9bdb6`, including GP-MP-EP.
See [the adoption record](../../result/cross_channel/figures/white_known_ep_500/ADOPTION.json)
and [the result index](../../result/README.md) for status. Successful source checks and saved-aggregate rendering do not establish
complete numerical reproduction or retraining.

Figures 5 and 10 were updated from `6c965cc436559d9757209657796df478325e09d4`
on 2026-11-14. Figure 5 displays iterations 1–150 for GP-MP and STMP;
Figure 10 uses a single-row legend. Current source verification is recorded
in [the convergence adoption](../../result/convergence/figures/current/ADOPTION.json)
and [the cross-channel adoption](../../result/cross_channel/figures/white_known_ep_500/ADOPTION.json).
