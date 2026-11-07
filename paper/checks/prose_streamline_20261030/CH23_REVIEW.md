# Chapters II–III streamlining: preservation checklist

Prepared by the independent II–III reviewer on 2026-10-30. Read-only review of canonical manuscript; post-edit review below covers Chapters II–III against `before/sections`.

## Chapter II

- Retain the definitions of the normalized path delay `d = tau/T_s`, the useful-interval starting sample `g` measured from the block start, and the reference-frame value `g_0 = N_CPP`. These can be one sentence plus an Appendix reference. If `eq:path-operator-system` remains in the main text, `g` and `varphi_n` must not become undefined there.
- Retain `B_d[t,n] = varphi_n(t-d)` and identify `varphi_n` briefly as the AFDM basis waveform with CPP extension; its full construction, frequency wrapping, and multi-symbol-delay discussion already reside in `appendix_afdm_channel_model.tex` (`eq:continuous-waveform`, `eq:path-operator`, `eq:integer-prefix-phase`). No new derivation is required.
- Preserve the frame timing and interface: `T_frame = (N + N_CPP)T_s`, `g_q = N_CPP + q(N + N_CPP)`, `H_k = H_k^(0)`, `H_k^(q) = exp(j q beta_k) H_k`, and `beta_k = wrap(2 pi nu_k T_frame)`. The shared-path Doppler assumption and block-constant parameters justify this relation.
- Preserve `eq:channel`, `eq:path-operator-system`, `eq:twc-frame-channel`, `eq:effective-pilot`, the dimensions/indexing of `Y = A X + W`, and the distinction between full channel coefficients and activity-induced block sparsity.
- Compress the Bayesian transition while retaining `q_tr`, independent device/activity priors, the fixed estimated likelihood inputs `Ahat` and `sigmahat^2`, the factorization `eq:working-posterior`, and the targets `eq:targets`. `q` is the posterior associated with those stated inputs and training prior; do not relabel it as an exact physical posterior.
- Current `main.tex` Appendix order is parameter estimation A, AFDM channel matrix B, evaluation protocol C. Refer by `app:afdm-model`, not a hard-coded “Appendix A.” New implementation appendix will be D if added after C.

## Chapter III

- The shortened structure introduction must still define MFLE and GPJD, Gaussian mean/scalar-variance exchange, and the two modules' roles. Keep the algorithm name GP-CCD-MP-DRE and the existing diagram interfaces.
- Retain the explanation for the full Gram matrix: terminal-dependent phase rotations need not preserve the row orthogonality of the original pilot matrix. Preserve `eq:linear-mean`, `eq:linear-variance` and `eq:linear-extrinsic`, including `t_L = tr(Sigma_L)/(KN)`.
- Move the complete SVD equivalence block to `app:implementation`: the factorization of `Ahat`, the definition of `s_i`, `f_L`, `t_L = gamma(1-f_L)`, `v_L = t_L/f_L`, and the equivalent extrinsic mean. Retain label `eq:linear-fraction` exactly once. State SVD reuse once. Algorithm 1 currently cites `eq:linear-mean`--`eq:linear-fraction`; after migration that range would run from Chapter III into Appendix D, so replace it by explicit main-text references plus a separate Appendix/SVD reference.
- Retain the definition/bridge from raw linear outputs `(R_L, v_L)` to damped `(R_k, bar v)` and the GPJD variance `v = kappa bar v`, even if detailed scheduling is only in Chapter V. Otherwise the interface changes symbols without explanation.
- Preserve local density definitions, local Bayes activity probability, and the exact conditional-moment decomposition (`eq:query-densities`, `eq:local-activity`, `eq:exact-local-moments`). Its activity uncertainty term is central, not an implementation detail.
- Preserve `F_k`, fixed-covariance derivative variance, pooling/floor formula, the site `(E_k,c_k)`, and site admissibility conditions. The statements explaining positive precision, averaging-before-flooring, and accepted-versus-retained identities may be removed when their operations remain explicit in formulas/schedule.
- Preserve the classifier input `(R_k,v,F_k)` in `eq:activity-probability`, the training-prior correction and definitions of `pi_tr`, logit, and sigmoid. Site-retention input reuse need only be said once in Chapter V.
- Preserve the Gaussian mixture, `U_k` reshape convention, spatial covariance and pooled scalar variance, clipping definition and interval, outgoing extrinsic formulas, and both residual and posterior-uncertainty contributions to `v_tar`. Removing explanatory repetition must not remove these interfaces.
- Preserve `bar v^(i)`, `kappa`, `eta` definitions/links for `eq:query-variance-update`. The common-current-variance and next-iteration schedule can live once in Chapter V. Keep local exactness versus learned approximation clear at their first definitions without repeated disclaimers.

## Cross-reference checks after editing

- Resolve each label exactly once: `app:implementation`, `eq:linear-fraction`, `app:afdm-model`, `eq:path-operator-system`, `sec:variance-update`, `sec:schedule`, `sec:conditional-error`, `sec:density-ratio`.
- Add new implementation input after evaluation protocol in `main.tex` and verify its displayed letter is D.
- Verify Algorithm 1 does not retain a main-to-appendix equation-number range.
- Confirm Appendix B still resolves the CPP, reference channel and inter-frame phase equations; Appendix A still resolves `eq:path-operator`.
- Compare every unchanged core equation against the pre-edit source and compile for duplicate labels and unresolved references.

## Final review

**PASS for the edited Chapters II–III. No required correction found in these two chapters.** Implementation-appendix integration and the updated Chapter V are being completed by their responsible editor and are not included in this pass.

Reviewed source bindings:

- `02_system_model.tex`: SHA-256 `94a99c98c0460c689285ea211827fb07974f935d79a8602cf0edc5b846c8e37a`.
- `03_bayesian_receiver_design.tex`: SHA-256 `c91d06265fa8203b8395b6863342d3f3e460d9dfbf411f1a67ad97a0346b0bc4`.

Actual comparison results:

- Chapter II retains all 14 numbered equation/align environments byte-for-byte apart from whitespace comparison (no mathematical changes, additions or removals). The shortened path-operator introduction still defines the block-relative sample `g`, the reference value `N_CPP`, and the AFDM basis waveform with CPP extension; Appendix B supplies its complete formula. The frame relation and its shared-Doppler justification remain adjacent and intact.
- Chapter II retains the prior independence assumptions, training prior, estimated likelihood inputs, posterior factorization and MMSE/activity targets. The merged transition now proceeds from assumptions to factorization to estimation targets and message passing. It introduces no stronger estimation claim.
- Chapter III retains 16 of its 17 original numbered equation/align environments unchanged. The only removed environment is `eq:linear-fraction`, intentionally migrating with its SVD context and equivalent extrinsic mean to Appendix D. No remaining mathematical expression changed.
- The shortened structure introduction preserves both module names, their responsibilities, Gaussian message representation, fixed block-level likelihood inputs, and the diagram interfaces. Its approximation status remains explicit in the chapter opening and local derivations.
- The MFLE-to-GPJD bridge still defines `bar v`, `v = kappa bar v`, and the role of `kappa`; detailed damping is appropriately referred to Chapter V. The reason for retaining the full Gram matrix remains.
- Training-range gating and `0 < tau < v` remain explicit before the site update, followed by retention otherwise. The pooling/floor order, clipping interval, classifier input tuple, training-prior correction, approximate conditional moments, mixture moments, residual variance target and variance-ratio update are intact. Removed sentences restated formulas or the Chapter V schedule rather than adding distinct conditions.
- Local exact activity/moment identities remain distinguished from learned posterior approximations; the edit adds no empirical, convergence, optimality or generalization claim.

Integration follow-ups already assigned elsewhere:

1. Restore `eq:linear-fraction` exactly once under `app:implementation`, with the SVD definition and equivalent extrinsic mean; include Appendix D in `main.tex`.
2. Replace the old Algorithm 1 range from `eq:linear-mean` to `eq:linear-fraction` by a main-text range and a separate appendix reference.
3. Keep the Chapter V definitions of `eta`, the common current GPJD variance, classifier use of current `F_k`, next-iteration `kappa`, and initialization/fallback behavior in one location. These are intentionally no longer repeated in Chapter III.

This pass does not claim final PDF compilation or layout validation; those are root-level delivery checks.

## Final cross-chapter integration review

**PASS.** The final integrated Chapters II–VI and Appendix D were checked with `validate_static.py`, which was actually executed and produced `STATIC_VALIDATION.json` with **20 checks passed, zero failed**. Its source bindings identify the version checked.

- All **52 displayed mathematical environments** from the original Chapters II–VI are preserved across the revised II–VI plus D: 50 numbered `equation`/`align` environments and two unnumbered bracket displays. Comparison removes whitespace and comments only. No mathematical environment was added, lost, or altered; SVD and stopping displays moved to D.
- All **93 original active manuscript labels** remain and are unique; the new implementation-appendix label brings the total to 94. All **98 cross-reference occurrences** resolve to source labels, and all citation keys exist in the unchanged bibliography.
- The requested original Chapter I, Appendices A/B/C, bibliography and all seven figure PDFs remain byte-identical. The script also protects the inactive conclusion and second-order-training appendix, for **14 protected baseline files** in total.
- Appendix D is the fourth active appendix. It restores the SVD context, equivalent extrinsic mean, finite-difference settings, classifier features and full stopping criteria. Algorithm 1 now uses a main-text equation range plus an Appendix D reference, avoiding a cross-main/appendix range.
- Independently read the IV/V before-after diffs and resulting flow. The removed score-matching line is an intermediate algebraic expansion; the score, target, weighted loss and population qualifications remain. Derivative evaluation still holds covariance fixed and uses the complete mean map. The classifier's current network input and the current-variance/next-ratio ordering remain explicit in Algorithm 1. Out-of-range fallback, site acceptance, initialization and output rescaling remain. No required repair or strengthened empirical/theoretical claim was found.

## Visual review of rendered pages 2–5

All four requested preview images were individually opened with `view_image` and visually inspected. **PASS:** no clipping, overlapping text or mathematics, missing glyphs, unresolved reference markers, or abnormal whitespace were observed.

- Page 2: introduction-to-system-model transition and physical-channel equation fit within the columns.
- Page 3: AFDM transform, CPP, path matrix, frame phase and matrix-indexing displays remain legible and within margins; Appendix B is correctly named.
- Page 4: the module diagram, its arrow labels and caption are intact; posterior and MFLE formulas fit; the implementation pointer displays Appendix D. The diagram floats to the next column in ordinary two-column reading order.
- Page 5: conditional/mixture covariance, site, classifier and variance-update formulas fit; the transition to Chapter IV is clean.

Inspected PDF SHA-256: `e9e66d317e32022575dd31ed2811249e288e70440bb5702f6293b2996bfe23cc`.

Preview bindings:

- `previews/final-02.png`: `a15378ce3e0fa9c7662bd3f6d03ac9339e32ecbd8713955eefda6daef58aad39`
- `previews/final-03.png`: `a6d57bab6f62371b51cd7f51d3f06378de1686966e6935b73f1aae2d710261a1`
- `previews/final-04.png`: `4b2889447d9812694d1a5645882e411cca516863ad359b4a4a0232b1f2a35307`
- `previews/final-05.png`: `fc31164f82f0a8a88846f5cf6fc14116e9867e3fd45a7e2b9732e2064fc43256`

No canonical file was modified and no compilation was performed by this reviewer. Experimental statistics and the remaining PDF pages are assigned to other reviewers.
