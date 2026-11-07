# V-B author sources and changes

Author: `chapter5_lead/v_b_writer`; date: 2026-10-30. Scope: only the V-B draft and this note, with initial copies for chapter review. No canonical manuscript, shared terminology, bibliography, code, experiment, or compiled artifact was changed.

## Structure and original-paper checks

- `reference/literature/shen2025.pdf`, PDF p.10, end of Section III-C immediately before Section IV: complexity is explained by the dominant operation in each module and then combined. This organization motivates describing MFLE transforms, spatial operations, and GPJD network evaluations before their sum. Shen's GAMP, elementwise, and phase-update operation counts are **not** used as this paper's counts. PDF pp.9–10 and Algorithm 1 were read directly using pypdf.
- `reference/literature/cai2026.pdf`, Section V-C, PDF p.11 / printed p.3585: the complexity paragraph separates matrix operations in module A from forward passes in module B and defines the network-forward costs. We adopt only this conventional organization and terminology. Cai's FFT/IFFT count depends on its pilot design and its two-score-network cost is not transferred to this receiver. The V-C opening and Algorithm 2 on PDF p.10 / printed p.3584 were also inspected.
- `paper/C-STMP/sections/03_bayesian_receiver_design.tex`, reviewed canonical III-B and III-C: the thin SVD is reused within the block; GPJD supplies joint spatial covariance and outgoing Gaussian messages; the variance-ratio target uses the existing joint moments.
- `paper/C-STMP/checks/chapters_3_5_revision_20261030/ch4/chapter_reviewed.tex`, IV-B: centered finite differences of the complete fixed-covariance mean map use two offset evaluations per direction in addition to the center evaluation. IV-C receives that same center mean as a classifier feature.
- `paper/C-STMP/sections/appendix_parameter_estimation.tex`, Appendix A, equations `frontend:eq:phase-variable-projection`, `frontend:eq:phase-aliases`, and the following refinement/sweep paragraphs: these define the existing coarse-search, local-refinement, and gain-refit work represented by `C_phase`. No separate recent phase candidate from the README is imported.

These sources were paraphrased without copying sentences. The subsection's costs are direct counts of this manuscript's operations, not results attributed to Shen or Cai. No new citation key or technical method name is introduced; MFLE and GPJD use the approved in-paper module definitions.

## Implementation checks and cost correspondence

| Draft statement | Directly inspected implementation / manuscript locator | Count or qualification |
|---|---|---|
| One thin SVD, reused in MFLE | `src/algorithm/STMP/linear.py`, `MMVLinear.__init__`, lines 23–27; `SpatialLinear.update`, lines 62–68; current III-B `eq:linear-fraction` | Q-by-KN matrix, Q <= KN: O(KNQ^2) setup, O(QKMN^2) transforms per iteration. The smaller U-side multiplication O(Q^2MN) is covered when Q <= KN. |
| Noise covariance spectrum | `src/system/receiver/noise_estimation.py`, lines 18–22, 27–33; Appendix A `frontend:eq:spatial-noise-covariance`–`frontend:eq:noise-mdl` | The manuscript covariance/eigenvalue calculation is O(QNM^2+M^3). Code obtains the same eigenvalues through the singular values of the QN-by-M observation matrix; it does not explicitly form the sample covariance. The displayed bound covers either dense realization. |
| Spatial products and factorizations | `src/algorithm/STMP/linear.py`, lines 54–58, 71–75; `src/algorithm/STMP/gaussian.py`, lines 11–15, 18–36; `src/algorithm/STMP/denoiser.py`, lines 174–184 | Per-user spatial Gram matrices and spatial transformations give O(KM^2N^2); M-by-M eigendecompositions/inverses give O(M^3). We retain these operations because the common spatial routines are invoked by the current scalar receiver, rather than replacing them with a hypothetical specialized scalar routine. |
| 1+2L_z mean passes | `src/algorithm/C_STMP/moments.py`, `trace_variance`, lines 26–31; `ColoredMoments.infer`, lines 78–86 | One center plus two offsets per random direction. Network cost is measured per terminal, so multiply by K; batching does not change this arithmetic-count convention. |
| Classifier reuses center mean; no calls outside support | `src/algorithm/STMP/denoiser.py`, lines 98–110, 139–151, 195–199 | Only supported variances enter the neural branch. The classifier is passed `full_mean`; the fallback branch computes retained-site Gaussian moments instead. The single-iteration formula is therefore written as a full-iteration bound, not as a claim of neural calls during fallback iterations. |
| Variance-ratio update requires no new network | `src/algorithm/C_STMP_variance_em_20261025/iterations.py`, lines 14–21 and 53–58 | The mean squared residual costs O(KD); uncertainty uses spatial traces already available. The target and ratio update reuse `state.mean` and `state.spatial_covariance`. |
| Working storage | `src/algorithm/STMP/linear.py`, lines 25–27, plus tensor/state shapes in the above routines | O(QKN) for pilot/SVD factors (Q^2 covered by QKN), O(KMN^2) for channel messages, O(KM^2) for spatial covariance state. This is algorithm working storage excluding trained parameters/network activations, not a measured total process-memory or diagnostic-history bound. |

## Explicit counting convention and unresolved implementation detail

The displayed expressions use standard dense matrix-operation counts, with a product of three M-by-M matrices evaluated as two matrix multiplications. They are not a per-instruction or per-NumPy-kernel measured count. In particular, `src/algorithm/STMP/gaussian.py:30` expresses the whitening product as `np.einsum("ij,jk,kl->il", ..., optimize=False)`. A direct four-index contraction can scale as O(M^4), although the same matrix expression has a conventional O(M^3) evaluation. This code-level detail was reported to the chapter lead and root for their disposition; no code, equation, or benchmark was changed. The draft makes its standard dense-operation counting convention explicit and assigns the M^3 term to matrix factorizations without claiming that every implementation instruction is bounded separately by M^3.

## Preservation and review status

- Preserved the mathematical contents and labels of `eq:iteration-complexity` and `eq:total-complexity` exactly; no equation is added, moved to another subsection, or deleted.
- Preserved the stated asymptotic storage and the supplied-phase case `C_phase=0`.
- Added the supported-variance/fallback qualification and tied the two module names to their own costs.
- No timing, memory measurement, experimental run, inference, training, or compilation was performed.
- Initial author draft pending chapter-lead review. This note does not claim independent technical certification.
