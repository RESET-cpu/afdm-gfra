# Chapter IV preparation (2026-10-30)

Read-only preparation completed before subsection authors are started. The chapter lead read the authoring contract, root AGENTS/README, current IV, current III interfaces, and VI training settings. Canonical files have not been edited.

## Planned independent subsection assignments

- IV-A: Establish the real representation, conditional-mean/score relation, covariance-weighted denoising objective, and matrix extension of scalar network preconditioning. Keep all four equation labels. Explain that the population minimizer is the conditional mean and the trained map approximates it. The score-matching equivalence is covariance weighted: substituting S_theta = Sigma^{-1}(f_theta-u) yields the norm of Sigma^{1/2} times the difference between network score and conditional perturbation score.
- IV-B: Derive average complex-coordinate variance from the output-by-input conditional-mean Jacobian, then introduce the actual sign-vector, covariance-scaled centered finite difference. Retain the two equation labels, denominator D rather than 2D outside the real covariance, fixed covariance, full mean-map differentiation, fixed direction within a block, and the three-pass cost for L_z=1.
- IV-C: Define a in {0,1} explicitly, formulate balanced binary classification, distinguish the ideal population logit from the finite trained classifier, and connect prior correction to III. Keep both equation labels and frozen-mean features.
- IV-D: Explain clean-channel data, covariance sampling, tensor-to-network representation, sequential training, and deployment inputs. Keep numerical optimizer/sample settings in VI. Preserve current fixed-M,N / variable-K,Q scope. Do not import older three-network designs.

The chapter opening will directly identify the three quantities required by GPJD: conditional mean, conditional variance, and activity density ratio. A and B deliver channel moments; C delivers activity evidence; D explains offline training of the two networks.

## Primary-source verification performed

1. Dytso--Poor--Shamai, arXiv:2104.01883, direct original PDF https://arxiv.org/pdf/2104.01883, PDF p.5, IV, Proposition 1, equation (22). The source defines its input-by-output Jacobian in II-A, equation (9), PDF p.4. Its identity uses that convention: J_y E[X|Y=y] = K_N^{-1} Var(X|Y=y). With manuscript output-by-input convention, P = J_m Sigma is the corresponding transpose convention. Equation (3), PDF p.2, supports the vector Tweedie identity. The manuscript derivative estimator is an approximation obtained by replacing the exact conditional mean with the trained map.
2. Metzler--Maleki--Baraniuk, From Denoising to Compressed Sensing, arXiv:1406.4175v2, direct original HTML https://arxiv.org/html/1406.4175v2, V-B, equation (21). Source uses Gaussian directions and a one-sided finite difference; M=1 costs one extra denoiser call. Manuscript uses sign directions with identity second moment, covariance scaling, and a centered difference, hence two extra calls. Do not attribute these implementation choices literally to Metzler or claim closed-loop unbiasedness for a reused direction.
3. Menon--Ong, ICML 2016, direct original PDF https://proceedings.mlr.press/v48/menon16.pdf, PDF pp.2-3 / printed pp.305-306: II.2 logistic link, III equations (6)-(8), IV.2 equations (16)-(17). Class posterior odds equal density ratio times class prior odds. Conditional application at a common sampled v yields the manuscript logit relation. A finite trained classifier estimates this relation.
4. Karras et al., Elucidating the Design Space of Diffusion-Based Generative Models, local reference/literature/karras2022_edm.pdf, PDF p.8, section 5, equations (7)-(8); Table 1 on PDF p.3. The original describes scalar input, skip, and output preconditioning; the manuscript is an explicit matrix-covariance extension. Do not present the full present objective as EDM's complete training recipe.

## Review priorities

- Preserve all equations, labels, and existing citation keys unless a substantive problem is reported to root first.
- Add a short bridge for why a channel-mean network supports both mean and variance outputs.
- Avoid calling the trained posterior moments exact or the empirical classifier optimally calibrated.
- Do not expand engineering numerical settings or repeat the two differences excluded by the user.
- Check tensor ordering, complex-real factor of two, prior correction, and training order across subsections.

## Current status

Prepared for four independent subsection writers. No writers have been launched in this preparation round, per root's concurrency instruction. No canonical edits, experiments, training, or compilation performed.
