# Chapter V preparation

Prepared by `chapter5_lead` on 2026-10-30. This is a read-only preparation record except for this file. No writers have been started, no canonical manuscript or shared terminology/reference file has been edited, and no experiment, training, inference, or compilation has been run.

## Scope and planned structure

Follow `AUTHORING_CONTRACT.md` and `ROOT_VERIFICATION_NOTES.md` in the parent directory. The only two subsections are:

1. A. Overall Algorithm.
2. B. Computational Complexity Analysis.

V-A absorbs the current III parameter-estimation paragraph, current V message scheduling, and current V stopping criteria. Preserve `sec:overall` for the chapter and put the compatibility labels `sec:schedule`, `sec:frontend`, and `sec:damping` at V-A. Do not introduce a new engineering, damping, stopping, or parameter-estimation heading. Use MFLE and GPJD consistently with the reviewed III draft; do not re-derive their posterior or extrinsic equations. IV supplies the mean map, its finite-difference variance, and classifier.

## Sources directly inspected

The current II–V sections, VI simulation settings, `main.tex`, the frontend appendix, relevant bibliographic entries, and existing terminology/source records were read. III and IV are still being revised by their owners, so final integration must use their reviewed drafts rather than assume these initial texts are final.

- **Shen (`reference/literature/shen2025.pdf`), PDF pp.9–10, end of III-C and Algorithm 1:** p.9 connects the derived messages and EM updates to the algorithm. P.10 briefly mentions initialization and damping, then discusses computational cost by module. Algorithm 1, line 19 places the relative squared channel-change termination test inside the loop; its inputs include maximum iterations and the termination threshold. This supports concise engineering discussion and explicit pseudocode placement. It does not justify importing Shen's GAMP, phase-update schedule, stopping metric, or complexity into this method.
- **Cai (`reference/literature/cai2026.pdf`), PDF p.8 / printed p.3582, Algorithm 1:** each module's posterior and extrinsic computations are included in sequence, with the stopping condition in line 16. PDF pp.9–10 / printed pp.3583–3584, V-B and Algorithm 2: damping and channel-power normalization are separately elaborated, and the stopping condition appears in line 18. V-C begins pilot design and complexity. Our chapter should use the sequential algorithm presentation, while following the user's explicit preference for a shorter engineering treatment than Cai. In particular, Cai's query-dependent normalization is not our fixed training scale.
- The pre-existing frontend citations (`oleary2013`, `nadakuditi2008`) and appendix derivations remain unchanged in substance. This preparatory pass checked their manuscript/BibTeX linkage, not their entire external original articles; do not claim a new full original-source verification for them.

No source sentence is planned for verbatim reuse. Locators support organization and existing terms, not novelty claims for this paper's MFLE/GPJD descriptive abbreviations.

## Implementation interfaces and rules that must survive compression

The applicable implementation is `src/algorithm/C_STMP_variance_em_20261025`, not the separate 2026-10-30 phase candidate mentioned at the top of the root README.

- `receiver.py` constructs the frozen mean/classifier receiver, obtains the observation-based physical noise estimate when configured, sets the initial variance to activity prior times normalized training second moment, and returns scaled joint/conditional means and probabilities. Its record explicitly distinguishes approximate neural updates from exact EM monotonicity guarantees.
- `iterations.py::run_spatial_score` keeps the operator and estimated physical noise fixed. It divides the observation by the fixed training scale and noise by its square; initial prior mean is zero, initial covariance is the activity-weighted training second moment, and the query-variance ratio is one. It performs linear update, input damping, query variance scaling, denoising, expected-residual calculation, next-ratio update, extrinsic computation, output damping, and stopping check in that order.
- Input damping retains raw linear variance history separately from calibrated denoiser variance. The current ratio is used throughout the current denoising/extrinsic calculations; the newly calculated ratio is used in the next iteration. Do not accidentally feed calibrated variance back into the raw damping history.
- `STMP/iterations.py::moment_damp` uses the undamped first message when its previous value is absent. Both the first input message and first outgoing feedback message bypass damping; this must remain explicit even if equations stay compact.
- `STMP/denoiser.py` initializes channel sites to mean zero and variance one. Within the supported query-variance interval it evaluates the mean and derivative variance, pools the variance before flooring, and accepts the new Gaussian site only when the pooled positive variance is below the query variance. The current classifier is still evaluated if the site update is rejected. Outside the interval the old site is retained and Gaussian evidence is used. Do not describe rejection as freezing all outputs or suppressing classifier evaluation.
- The Gaussian evidence formula uses the retained prior site together with the current query and variance. Current conditional means and variances must therefore be recomputed even when a site is held.
- `STMP/iterations.py::_iteration_changes` compares joint channel estimates and input covariance between successive iterates, plus the maximum successive activity-probability change. `C_STMP_variance_em_20261025/iterations.py` also checks the posterior-residual variance target using the existing relative residual.
- `STMP/denoiser.py::message_is_fresh` additionally requires an accepted site update, stable site precision/natural parameter, and activity stability relative to a smoothed history in the current default. The smoothed history is used only for stopping and is separate from the successive probability comparison. The implementation compares current probability with the previous smoothed history and then updates that history; the writer must not introduce an inconsistent index.
- `STMP/iterations.py::_stopping_step` requires the minimum iterations, two consecutive-condition counters (estimate stability and fresh/stable sites), and hard-decision stability. The decision window counts consecutive iterates, not the number of matching transitions. Otherwise the final iterate is returned at the iteration limit. Numerical tolerances/window lengths remain in VI.
- `C_STMP/moments.py` evaluates the complete conditional mean at the center and two fixed-covariance offsets per random direction, using one block-fixed sign vector per terminal in the configured case. The classifier reuses the center mean; it does not require another mean-network pass.

## Equation and label preservation

All six current V numbered equations can remain mathematically unchanged:

| Label | Placement / role |
|---|---|
| `eq:input-damping` | V-A, compact input update after initialization |
| `eq:gaussian-evidence` | V-A, retained-site fallback |
| `eq:output-damping` | V-A, feedback update |
| `eq:variance-stopping` | V-A, stopping paragraph after algorithm |
| `eq:iteration-complexity` | V-B, one iteration |
| `eq:total-complexity` | V-B, total online computation |

The old III-A frontend contains no equation to move. Keep its references to `eq:effective-pilot`, `app:frontend`, and `frontend:eq:noise-mdl`, with its citations. Keep `sec:frontend` only once after integration, now in V-A, because II and other text already reference it. `sec:schedule` still resolves normalized-coordinate and damping references. `sec:damping` remains a compatible label despite removal of the old independent stopping subsection.

## Complexity evidence

Do not simplify the implementation to an ideal scalar kernel. The inspected `STMP/linear.py::SpatialLinear.update` eigendecomposes an M-by-M matrix, rotates spatial coordinates, and applies cached thin-SVD factors. `STMP/gaussian.py::gaussian_extrinsic` also performs matrix eigendecompositions/inversions. Therefore the existing per-iteration M^3 term is supported by the actual implementation even though a specialized scalar realization could remove it. No such optimization belongs to this manuscript-editing task.

- Thin SVD of the Q-by-KN effective pilot matrix: O(KNQ^2) for Q <= KN, once per block.
- Noise sample covariance and eigendecomposition: O(QNM^2 + M^3), once per block.
- Phase front end: retain C_phase as the cost of the appendix's coarse search, local refinement, and gain refits; do not fold in the separate new phase-candidate algorithm.
- MFLE transforms: O(QKMN^2); spatial matrix products/rotations and per-user Gram matrices: O(KM^2N^2); implemented spatial factorizations: O(M^3).
- Neural cost per supported iteration: K[(1+2L_z)C_theta+C_phi], or K(3C_theta+C_phi) at L_z=1. The existing expression can be described as the cost when the learned denoisers are evaluated, or as an upper bound for a complete iteration because unsupported-variance fallback iterations omit network calls.
- Query-variance update: O(KD) with D=MN^2, already dominated by listed terms and requiring no new network call.
- Retain existing asymptotic memory O(QKN+KMN^2+KM^2), explicitly excluding trained parameters and network activations. No memory measurements or empirical timing claims are available from this preparation.

No substantive mathematical correction is proposed in this preparation. Any later writer proposal that changes a displayed complexity expression or update must be reported to root before integration.

## Future writer assignments and chapter review

Start these two distinct writers only after root signals available concurrency and final III/IV interfaces:

1. **V-A writer:** write `ch5/a_overall_algorithm.tex` and `ch5/a_sources.md`, covering frontend, normalization, initialization, MFLE/GPJD sequence, current-site/current-query rules, the four V-A equations above, concise pseudocode, outputs, and complete but compact stopping rules. Include three compatibility section labels. Do not repeat III/IV derivations. Use the actual source labels from their reviewed drafts. Place the fixed-scale/noise and damping discussion in short paragraphs without additional headings.
2. **V-B writer:** write `ch5/b_complexity.tex` and `ch5/b_sources.md`, covering one-time setup, supported-iteration/upper-bound cost, network calls, total online cost, and memory. Preserve both complexity equations and explicitly ground the M^3 term in implemented spatial-matrix operations. Do not claim a measured runtime improvement or prove convergence.

The chapter lead will preserve each first draft, inspect every equation/label and source note, return concrete issues to the same writer, and assemble `ch5/05_overall_algorithm.reviewed.tex`. Review must check exactly two subsection headings; completeness of preprocessing and stopping; no current-/next-iteration mismatch; no false classifier fallback trigger; no accidental shift from fixed normalization to Cai's adaptive normalization; and consistency with the reviewed III/IV interface. Root remains responsible for canonical integration, cross-chapter reference checks, compilation, and visual inspection.
