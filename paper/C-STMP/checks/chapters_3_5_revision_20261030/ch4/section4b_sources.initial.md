# IV-B author notes, 2026-10-30

## Scope and changes

Rewrote only the assigned subsection draft `section4b.tex`. Canonical manuscript and other author files were not edited. The sequence is exact conditional covariance identity, trained-mean variance approximation, covariance-scaled Monte Carlo directional calculation, and GPJD pooling/evaluation cost.

Added an explicit definition of the real conditional covariance and explained the complex-coordinate normalization. Marked the use of the learned mean as an approximation. Described the finite-difference method as an adaptation of the cited Monte Carlo method, rather than attributing the present directions or centered calculation to its original implementation. Clarified that the fixed-covariance derivative includes the full preconditioned mean map.

## Primary-source checks

- Dytso, Poor, and Shamai, *A General Derivative Identity for the Conditional Mean Estimator in Gaussian Noise and Some Applications*, [original PDF](https://arxiv.org/pdf/2104.01883). Read Section II-A, equation (9), PDF p.4, and Section IV, Proposition 1, equation (22), PDF p.5. The source Jacobian has input coordinates as rows and output coordinates as columns. Its expression is `J_source = Sigma^{-1} P`; transposing to the manuscript output-by-input convention gives `J_m = P Sigma^{-1}`, hence `P = J_m Sigma`. The manuscript trace combines real and imaginary errors and divides by the number of complex coordinates D. For proper scalar complex perturbations, real covariance is `(v/2) I`, yielding the preserved `v div(m)/(2D)` expression. These real/complex and convention translations are explicit manuscript algebra, not a different identity attributed to the paper.
- Metzler, Maleki, and Baraniuk, *From Denoising to Compressed Sensing*, [original arXiv v2 HTML](https://arxiv.org/html/1406.4175v2), Section V-B, equation (21) and the next two paragraphs. Directly checked that the source uses Gaussian random directions and a one-sided finite difference; one direction requires one additional denoiser evaluation. Our present calculation preserves the existing independent random sign directions with identity second moment, covariance scaling, and centered difference, requiring two perturbed calls. The adaptation is indicated in the draft. No high-dimensional guarantee, learned-covariance exactness, or unbiasedness of the reused-direction receiver trajectory is claimed.

## Interface and preservation checks

- Preserved two numbered equation blocks and their labels: `eq:mean-derivative-variance` and `eq:derivative-trace`.
- Preserved subsection title and `sec:conditional-error`.
- Preserved numerical definitions `L_z=1` and `delta=10^{-2}`, fixed direction per terminal within a transmission block, fixed covariance during finite differences, and three mean-network evaluations including the center.
- The GPJD interface remains the per-terminal variance estimate followed by device pooling in `eq:pooled-variance`. The pooling floor remains defined in III and is not duplicated here.
- Read current III interfaces, IV source, VI derivative settings, authoring contract, preparation notes, AGENTS, root README, bibliography entries, and existing terminology records. No training, inference, experiments, or compilation performed.
- No substantive mathematical changes and no added method abbreviations or citation keys. Compilation and final rendered verification belong to root.
