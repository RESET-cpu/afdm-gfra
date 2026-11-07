# Chapter II structural revision — 2026-10-29

## Authority and scope

The author approved the preceding structural diagnosis and requested implementation, allowing a new subsection if necessary. The existing three subsections are sufficient and have been retained. This is a scoped structural revision, not a new claim that every sentence is a source quotation.

## Changes

1. II-A now uses continuous time `t_c`; II-B and Appendix B retain the integer sample index `t`. II-B defines the sampling interval before IDAFT and explicitly gives `t_c=(g+t)T_s`.
2. The pilot matrix and its existing energy/row-orthogonality constraint have moved beside the pilot-vector definition in II-B. Their mathematical content is unchanged.
3. II-B gives the post-CPP starting sample `g_q` and the cross-frame relation before explaining the multiple observations of `H_k`. The former “Fortunately” paragraph has been removed because it blurred the distinction between `H_k=H_k^(0)` and the phase-varying `H_k^(q)`.
4. II-C now begins with activity variables, effective pilots, and the received signal. It proceeds through matrix stacking and dimensions to `Q<KN`, device block sparsity, and Bayesian JADCE.
5. The one-pilot/multiple-pilot claim has been replaced with the actual condition `Q<KN`. The full-channel statement explicitly concerns the coefficients of `H_k`; the separate block-sparsity statement concerns inactive devices in `X`. The existing prior retains dependencies within each channel.
6. Four occurrences of “access block” in Sections III, IV, VI, and Appendix B have been aligned to “transmission block”; those files have no other textual or mathematical changes.

## Source correspondence

- Shen, local PDF pp. 4–5, Section II-B/C: phase rotation across frames, collecting Q frames, and received-model/problem-formulation order. The explicit AFDM relation and starting-sample identity are this manuscript's model and existing Appendix B, not Shen's OTFS formula.
- Cai, local journal PDF pp. 4–5, Section II-A/B: pilot matrix, partial orthogonal pilots, activity indicator, block-sparsity structure, Bayesian objective and posterior factorization. Reordered passages retain their existing wording.
- Huang, local PDF pp. 2–3, Section II: effective channel matrix, fractional delay/Doppler power leakage, full-channel estimation, sparsity assumptions and underdetermination. The tensor dimensions and the condition Q<KN belong to this manuscript.
- Ding, local PDF p. 2, Section II: IDAFT and sampling interval. Existing modulation wording and equations remain unchanged.
- “transmission block” is the existing Cai-based terminology recorded in `docs/TERMINOLOGY.md`.

The new time/index and cross-frame linking sentences directly describe this manuscript's equations. They are necessary adaptations, not reported as complete verbatim sentences from a reference. Previous strict source-audit reports apply to their recorded hashes, not automatically to this revised version.

## Verification

- All 14 numbered Chapter II equations and their labels are retained. Equation contents match the baseline after normalizing the continuous-time dummy symbol in the physical channel equation.
- No missing Chapter II reference/citation keys or duplicate labels in the active manuscript.
- Main file (including abstract), introduction and bibliography unchanged; subsequent sections changed only by the four terminology substitutions above.
- One independent reviewer checked the revised source and baseline diff: no necessary corrections remained.
- Acronym check on the introduction and Chapter II found no actionable findings; the checker reports partial coverage for IoT, GFRA, MMSE, TSL and CPP. These existing expansions were also inspected in the rendered manuscript.
- Tectonic compilation succeeded: 14 pages. Chapter II on PDF pages 2–4 was rendered and visually checked. No clipping, overlapping equations, missing citations or undefined cross-references were observed. The log retains underfull-box warnings outside Chapter II and an amsmath bracket-group warning for the unchanged indexing formula; the formula renders correctly.
- No experiments, training, model parameters, reported results or frozen assets were changed.

See `verification.json`, `02_system_model.diff`, and `acronyms.json` for the recorded checks.
