# Chapter VI prose review

Reviewed canonical `paper/C-STMP/sections/06_simulation_results.tex` after application on 2026-10-30. Its contents equal the reviewed staged candidate; SHA-256: `c71e8eb09a58415a9a8e57e5e263cdd863c1a626f59686affc1012adda7ca21f`.

This is a close reading of the edits and their retained context, separate from the executed numerical checks in `NUMERICAL_VERIFICATION.json`. It is not a new experiment or full-paper review. The actual visual inspection performed later is recorded separately below.

- The shortened AER/NMSE sentence preserves the adverse comparison at -4 dB. Its statement that correct activity decisions alone do not ensure accurate channel estimates explains the distinct metrics; it does not assign a new cause to the measured performance gap.
- Removing the convergence paragraph's final qualification does not turn the example into a general convergence claim: the section still identifies one paired scene, describes its nonmonotone trajectory, and states that 60 iterations is the imposed minimum.
- Removing repeated damping qualifications does not hide retrospective selection. The main evaluation protocol still discloses development/evaluation overlap and retrospective user-count damping selection; the user-count caption points directly to unchanged Appendix C. That appendix still describes the selected scene-372 replacement, diagnostic reuse, and retained capped outputs.
- The pilot comparison still fixes per-frame energy, reports 462/500 versus two capped runs at Q=8, and bases the pilot saving on Q>=16. The 24-versus-32-frame and 80-versus-40-candidate comparisons remain expressly limited to the evaluated grid/configuration.
- The prose retains high-SNR reversals in direct denoising and channel profiles A/B, and the genie reference's information advantage. It retains the qualified interpretation of sparse-representation limitations and the statement that both principal receivers use learned priors. No edit attributes the receiver gain specifically to DRE, covariance conditioning, damping, or a single component.
- Exact normalization, selected checkpoints, derivative settings, and stopping constants are present in Appendix D and linked from the settings. The underlying training budgets and validation-selection rules remain in Chapter VI.

No newly strengthened causal claim or removed material limitation was found in these edits. The numerical audit freshly executed 97 checks against canonical sources and saved datasets, with zero failures; its scope does not certify every possible numerical statement in the full manuscript.

## Visual verification of rendered pages 9-11

On 2026-10-30, opened and visually inspected each actual page image using `view_image`: `previews/final-09.png`, `previews/final-10.png`, and `previews/final-11.png`. This inspection did not substitute extracted PDF text for images.

- Page 9: Figure 2, both legends, its caption, the two metric equations, and two-column text are intact. Appendix C/D references and numbered equation references render normally. The space below the figure caption is ordinary float separation, with no abrupt blank region.
- Page 10: Figures 3-5, axis labels, plotted endpoints, legends, and captions are readable and do not overlap one another or the prose. The short captions and transitions among convergence, SNR, and pilot-frame discussions fit without clipping.
- Page 11: Figures 6-7 and their lower legends/captions fit within their columns. User-count, activity-probability, and cross-profile paragraphs flow normally. The transition into Appendix A is properly spaced. No unresolved-reference marker is visible on these pages.

Result: no clipping, overlapping figures/text, conspicuous unintended whitespace, or visibly broken references found on pages 9-11. Other pages were not part of this visual check.
