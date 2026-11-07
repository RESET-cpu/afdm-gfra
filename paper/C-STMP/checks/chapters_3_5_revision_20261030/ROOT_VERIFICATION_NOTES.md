# Root verification notes

## Current implementation and complexity

Read on 2026-10-30 without running experiments:

- `src/algorithm/C_STMP_variance_em_20261025/receiver.py`: constructs the frozen mean/classifier receiver, fixes estimated physical noise, and calls the scalar-variance-adapting iterations.
- `src/algorithm/C_STMP_variance_em_20261025/iterations.py`: current scalar interface requires `covariance_mode == isotropic`; retains the raw linear variance history separately from calibrated v; derives posterior expected residual energy; updates the variance ratio for the next iteration; uses common STMP linear and extrinsic routines.
- `src/algorithm/STMP/linear.py`: `SpatialLinear.update` still eigendecomposes the M x M covariance and applies antenna rotations, even for isotropic input. Thus the existing per-iteration O(M^3) term is supported by the current implementation, although it could be avoided by a specialized scalar implementation. The M x M rotations and per-user spatial Gram products support O(K M^2 N^2).
- `src/algorithm/STMP/denoiser.py`: conditional covariance and activity uncertainty form the spatial moments; scalar pooling, retained sites, training-range classification and Gaussian fallback follow existing manuscript operations.
- `src/algorithm/C_STMP/moments.py`: finite difference evaluates the complete conditional-mean network at the center and two offsets per direction. With one direction the cost is three mean-network passes per terminal, plus the activity classifier, as stated in the manuscript.
- `src/algorithm/STMP/activity.py::EvidenceNetwork.inputs` (lines 62–99): checked the IV-D feature clarification directly. Real/imaginary observation and mean maps use sqrt(2/(1+v)); energy and real-inner-product features are normalized by Dv before log1p, the inner product uses sign(t) log1p(abs(t)), and the log variance is scaled by 1/5. The shorter manuscript description of these operations is faithful to this implementation.

Do not remove the per-iteration M^3 term solely because the mathematical scalar update could be optimized. Complexity prose can call it the implemented spatial-matrix operations; do not invent a new matrix algorithm.

### Follow-up correction from V-B review

The earlier check supports the M^3 eigendecomposition term but does **not** bound every current implementation instruction by that term. V-B's author identified `src/algorithm/STMP/gaussian.py:30`, which evaluates `ij,jk,kl->il` with `optimize=False`. Root confirmed that the current variance-EM loop calls this routine (`iterations.py:58`). NumPy's contraction-plan analysis on shapes (3,3), without executing receiver inference or a runtime benchmark, reports scaling 4 for this contraction, versus scaling 3 for pairwise products. The literal current implementation therefore includes an additional O(M^4) contraction cost.

Decision within the authorized manuscript-only scope: preserve the existing equations as the **algorithm arithmetic cost using standard matrix products and decompositions, with three-matrix products evaluated pairwise**, and state that convention explicitly in V-B. Do not characterize these equations as a strict cost audit of each current NumPy instruction. The author must receive and implement this wording clarification; the chapter lead records the original and corrected draft. No code, timing result, experiment, or weight is changed. An implementation optimization remains outside this manuscript revision, and no speedup has been measured or claimed.

## Protected scope

`run_baseline.json` captures current hashes immediately before the approved chapter work. The only difference from the earlier preparation snapshot was an externally appended TERMINOLOGY.md update. Preserve that current text, and append this revision's terminology entry only after all source notes are reviewed.

Root owns the final diagram, compilation, equation/reference checks, artifact rendering, and canonical integration. No inference, training, parameter changes, or experiment reruns are part of this task.
