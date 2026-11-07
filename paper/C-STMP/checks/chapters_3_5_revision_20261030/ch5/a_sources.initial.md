# V-A author evidence and changes

Author: `v_a_writer`, 2026-10-30. Draft: `a_overall_algorithm.tex`.
This is a scoped prose/organization revision. No canonical manuscript,
shared terminology, bibliography, code, configuration, or result was edited.
No experiment, inference, training, or compilation was run.

## Directly inspected sources

- `reference/literature/shen2025.pdf`, PDF pp. 9–10, final paragraph of
  III-C and Algorithm 1: the final paragraph connects the already-derived
  messages and EM updates to the algorithm; p. 10 briefly notes
  initialization and damping before discussing computational cost.
  Algorithm 1 includes a stopping test on line 19. This informs the
  concise organization, not our numerical algorithm or stopping rule.
- `reference/literature/cai2026.pdf`, PDF p. 8 / printed p. 3582,
  Algorithm 1, especially lines 4–15 and 16: sequential module updates,
  then stopping. PDF pp. 9–10 / printed pp. 3583–3584, V-B1,
  Eqs. (57)–(58), and Algorithm 2: damping of means and variances in
  both message directions. The draft cites this damping practice,
  while preserving our existing running-message damping equations.
  Cai V-B2 uses query-dependent power normalization; that procedure
  was not transferred. Our existing fixed training scale is preserved.
- Current manuscript: II `eq:effective-pilot`, canonical revised III
  module interfaces and equation labels, reviewed IV
  `ch4/chapter_reviewed.tex`, current V, VI simulation settings,
  and Appendix A. Read `main.tex` for the available algorithm-box
  conventions, `references.bib` for the frontend citation keys, and
  existing `TERMINOLOGY.md` source locators for frontend terminology.

The frontend paragraph retains the substance and citations of the former
III-A from `baseline/03_bayesian_receiver_design.tex`:
`oleary2013` for variable projection and `nadakuditi2008` for the
eigenvalue/MDL noise estimate. Appendix A was checked, including its
dominant-path fit and noise covariance. The original external O'Leary–Rust
and Nadakuditi–Edelman articles were not newly reread by this writer;
no new attribution or stronger source claim has been added for them.

## Direct implementation checks

- `src/algorithm/STMP/iterations.py`, `_iteration_changes` and
  `_stopping_step`: separate successive estimate, covariance, and activity
  changes; distinct estimate-stability and accepted-site counters;
  minimum iterations; decision window counts iterates, not transitions.
- `src/algorithm/C_STMP_variance_em_20261025/iterations.py`,
  `run_spatial_score`: the posterior-residual variance check joins the
  estimate/covariance stability condition; current `v` is used for
  denoising and extrinsic formation, and the ratio is advanced afterward.
- `src/algorithm/STMP/denoiser.py`, `message_is_fresh` and the activity
  history update around lines 211–224: compare the current probability
  with the prior smoothed history, then update that history; the history
  is used only for stopping. This is distinct from the successive
  probability difference used by `_iteration_changes`.
- The chapter lead's `PREPARATION.md` and root
  `ROOT_VERIFICATION_NOTES.md` supply the reviewed full initialization,
  acceptance, classifier, Gaussian fallback, and first-message schedule.
  They were read as coordination evidence, not cited as research sources.

## Preserved equations and labels

The four numbered equations are copied without mathematical change:
`eq:input-damping`, `eq:gaussian-evidence`, `eq:output-damping`, and
`eq:variance-stopping`.

The subsection is `Overall Algorithm`. Its labels are `sec:schedule`,
`sec:frontend`, and `sec:damping`; the latter two retain old references
after the old parameter-estimation and stopping headings disappear.
No independent engineering, damping, stopping, or parameter-estimation
heading is added. The chapter-level `sec:overall` remains the lead's
responsibility. No new method name is introduced; MFLE and GPJD follow
the author-approved manuscript terminology.

## Main editorial changes

1. Moved former III-A preprocessing into the first V-A paragraph.
2. Made the fixed normalization and initialization explicit before the
   message loop, with the original scale and parameters unchanged.
3. Used MFLE and GPJD consistently and referenced their equations
   rather than re-deriving posterior or learned-denoising relations.
4. Defined the new-message weight `eta` and restricted both damping
   formulas to iteration 2 onward, explicitly preserving the undamped
   first input and feedback messages.
5. Preserved current classifier evaluation after a rejected site,
   range-only Gaussian fallback, current-query conditional moments,
   and next-iteration-only use of the new variance ratio.
6. Kept engineering discussion in ordinary paragraphs. The algorithm
   box contains the full call sequence and links the stopping test to
   the compact final paragraph.
7. Clarified the prior-history index in the stopping test without
   changing either the successive-probability condition or history
   recursion. Numerical tolerances remain in VI.

No substantive mathematical correction is proposed. No new convergence,
runtime, or performance claim is made. Initial draft copies are retained
as `a_overall_algorithm.initial.tex` and `a_sources.initial.md` before
chapter-lead review.
