# IV-A author draft and source record

Date: 2026-10-30. Author: independent IV-A writer under chapter4_lead.
Scope: `section4a.tex` only; no canonical edits, training, experiments, or compilation.

## Changes and interfaces

- Preserved the four original numbered equations and labels, with no mathematical change: `eq:colored-query`, `eq:tweedie-mean`, `eq:first-loss`, `eq:mean-preconditioning`.
- Made the active clean-channel distribution, independent perturbation, fixed-covariance density, and averaging variables explicit.
- Distinguished the unrestricted population minimizer from the trained approximation. The sentence does not assert convergence of empirical training or exact posterior moments for the finite network.
- Expanded the score substitution by one inline residual identity, showing precisely which covariance weighting remains after substituting `S_theta = Sigma^{-1}(f_theta-u)`.
- Retained explicit attribution of scalar preconditioning to Karras and explicit ownership of its matrix-covariance extension by this manuscript. Preserved nominal real-coordinate variance `sigma_d^2 = 1/2`.
- Retained the receiver interface `F_theta(R,C)` and its evaluation at `C=v I_D` in GPJD, without turning this into a separate limitation discussion.
- Read the current III (MFLE/GPJD and learned-mean interfaces), VI training settings, root AGENTS/README, authoring contract, preparation record, and relevant existing terminology records. The README's newer phase candidate is outside scope.

## Primary-source checks

| Source | Exact location checked | Supported text and adaptation boundary |
|---|---|---|
| Dytso, Poor, Shamai, *A General Derivative Identity for the Conditional Mean Estimator in Gaussian Noise and Some Applications*, arXiv:2104.01883v1; [original PDF](https://arxiv.org/pdf/2104.01883) | PDF p.1, §I, Eq. (1); PDF p.2, Eq. (3) | Independent Gaussian noise with arbitrary positive-definite covariance and vector conditional-mean/score identity. The manuscript applies this real-vector identity after its complex-to-real covariance conversion. |
| Efron, *Tweedie's Formula and Selection Bias*; [author PDF](https://efron.ckirby.su.domains/papers/2011TweediesFormula.pdf) | PDF p.4, §2, Eqs. (2.7)–(2.8); scalar mean also PDF p.2, Eq. (1.4) | Source for Tweedie's formula terminology and posterior mean. The full matrix identity is supported by Dytso, not attributed solely to Efron's scalar formula. |
| Vincent, *A Connection Between Score Matching and Denoising Autoencoders*; [original journal paper mirrored as PDF](https://gwern.net/doc/ai/nn/diffusion/2011-vincent.pdf) | PDF pp.6–7, printed pp.1666–1667, §4.2, Eqs. (4.3)–(4.5); PDF p.8 / printed p.1668, Eq. (4.8) | Denoising score matching uses the conditional perturbation score as target. The manuscript's covariance-weighted objective is its explicit generalization, not Vincent's isotropic Euclidean loss copied unchanged. The author's university PDF URL returned an access-denied page, so the same journal article was inspected via the linked mirror. |
| Karras et al., *Elucidating the Design Space of Diffusion-Based Generative Models*, local `reference/literature/karras2022_edm.pdf` | PDF p.8, §5, Eqs. (7)–(8); PDF p.3, Table 1 | Scalar input, skip, output preconditioning and conditioning variable. The matrix functions of `Sigma` and the present covariance-weighted objective are this manuscript's adaptation; no claim that EDM supplies the full present training recipe. |
| Shastri et al., *Denoising Generalized Expectation-Consistent Approximation for MR Image Recovery*, local `reference/literature/shastri2022_dgec.pdf` | PDF pp.15–16, §III-B, Eqs. (38)–(41) | Training denoisers for correlated Gaussian noise with supplied noise-statistics information. Their corr+corr uses independent same-covariance noise realizations; our explicit covariance input is not called corr+corr, nor is our weighted objective or AFDM receiver attributed to this paper. |

## Algebra checked by the author

For fixed positive-definite `Sigma`, conditional squared-error minimization with the positive-definite weight `Sigma^{-1}` has the same unrestricted minimizer `E[h_R | u,C]`. This follows by expanding the residual about that conditional mean; the cross term has conditional expectation zero.

Writing `s_cond = -Sigma^{-1}(u-h_R)` yields
`Sigma^{-1/2}(f_theta-h_R) = Sigma^{1/2}(S_theta-s_cond)`.
Thus the loss equals the expected squared score residual in the `Sigma` metric, divided by `2D`. This is an algebraic rewriting of the retained objective, not a new estimator or a guarantee about the learned score.

The proper complex covariance conversion retains its `1/2` factor. With `C=v I_D`, the real covariance is `v I_{2D}/2`. No finite-difference or derivative formulas were changed here; those remain IV-B's responsibility.

## Review status

An automated text comparison confirmed that all four numbered equation bodies and their labels are identical to canonical IV-A after whitespace normalization; the five existing citation keys are retained. Submitted to chapter lead for review. No independent reviewer or full-manuscript verification is claimed by this subsection writer.
