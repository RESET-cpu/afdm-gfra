# III-C writer notes

## Scope and deliverable

- Draft: `III_C_initial.tex`; canonical manuscript files were not edited.
- Approved title: **Generative-Prior-Aided Joint Denoising**. GPJD is the author-approved descriptive name of this paper's module, not a method name attributed to a reference.
- Added `sec:gpjd`; retained `sec:variance-update` directly under the same subsection heading. Removed the separate variance/extrinsic-update heading in the draft only.
- Read the current II–V text, main preamble, relevant VI settings, root instructions, and relevant terminology entries. Historical three-network and phase-candidate descriptions were not adopted.

## Source checks

1. **Cai et al., local `reference/literature/cai2026.pdf`, PDF pp.6–8 / journal pp.3580–3582, §III-B.** Read original PDF text. Equations (16)–(23) explicitly distinguish active-channel Gaussian input and conditional channel denoising. Equations (24)–(27) give the Gaussian division for channel extrinsic messages; (32)–(38) give the activity mixture, conditional moments, and scalar covariance averaging; (39)–(42) give the final extrinsic feedback. These support the sequence and existing Gaussian-message operations. The present generic-prior activity density ratio, learned classifier, derivative-based variance, and scalar input-variance adaptation are not attributed to Cai's original algorithm. Its state-evolution statement was not imported as a guarantee for the present finite multi-frame receiver.

2. **Liu and Yu, local `reference/literature/liu2018_massive_mimo.pdf`, PDF pp.5–6, §III-B–D.** Read original PDF text. Equation (17) provides the activity-masked local observation; §III-C equations (18)–(21) express the MMSE mean as an activity factor times an active-channel conditional estimate. The activity-uncertainty contribution is also visible in §III-D equation (29). The existing general covariance decomposition in this draft follows the laws of conditional expectation and covariance; it is not presented as an arbitrary-prior formula copied from Liu's Gaussian-channel specialization. The explicit definitions of `m` and `Sigma_H` conditioned on `alpha=1` clarify the existing mathematics.

3. **Vehtari et al., [JMLR official PDF](https://jmlr.org/papers/volume21/18-817/18-817.pdf), PDF p.5, §2.1 after equation (1).** Independently opened and checked the official PDF text. A site approximates one target factor; the new site is obtained by dividing the approximation to the tilted distribution by the cavity distribution. This supports the term *Gaussian site approximation* and the factor-division interpretation. The requirement for a positive scalar site precision and the retain-previous-site rule are this manuscript's existing implementation choices, not universal requirements of expectation propagation.

4. **Vila and Schniter, local `reference/literature/vila_schniter_2013.pdf`, PDF p.4 / journal p.4661, §III-A equations (22)–(27).** Read extracted prose and visually inspected `reference/reviews/c_stmp_variance_math_audit_20261025/vila_schniter_2013_page4.png` because the extracted mathematical symbols were incomplete. Equation (26) is the average posterior expected squared residual; equation (27) splits it into squared residual of the posterior mean plus posterior variance. The manuscript applies that Gaussian variance calculation to its local denoising model with its current approximate posterior held fixed. It does not claim exact EM, monotone likelihood improvement, or exact neural posterior moments.

5. **Cross-chapter interfaces.** The current IV supplies the existing conditional-mean derivative and classifier prior-correction derivations; III-C therefore points to `sec:conditional-error`, `sec:density-ratio`, and `sec:learning` without duplicating their training objectives. V owns initialization, damping, and out-of-training-range Gaussian activity evidence through `sec:schedule`. The draft retains the current two-network design and same-current-variance / next-iteration-scale-factor timing.

## Editorial changes

- Reorganized the prose into local model and exact moments, learned channel moments, Gaussian site, activity probability and mixture moments, extrinsic feedback, and variance adaptation, all in one subsection.
- Made the activity conditioning of the exact channel mean/covariance explicit; described learned and site-derived quantities as approximations.
- Stated that the activity classifier uses the current network mean `F_k` even if the previous site is retained, rather than substituting the recombined mean `mu_k`.
- Retained variance pooling before flooring, all acceptance/retention conditions, the activity-uncertainty covariance term, clipped scalar feedback, and fixed physical noise variance.
- Kept engineering prose short and referred scheduling details to V. Did not re-emphasize the two issues the user excluded.

## Checks and limitations

A direct comparison against the original two subsections found **14 equation environments in both versions, identical byte-for-byte**. All 14 equation labels were retained; `sec:variance-update` moved to the merged subsection heading and `sec:gpjd` was added. The draft contains one subsection and no lower-level headings. No algorithm, configuration, training, experiments, or compilation was run by this writer. Chapter-lead review and root compilation remain pending.

## Chapter-lead review response

The chapter lead accepted the formulas and argument sequence and returned three wording/source-location issues. All three are addressed in `III_C_revised.tex`; `III_C_initial.tex` is preserved.

1. Expanded the Liu citation to §§III-C–III-D, covering the channel/activity mean in (18)–(21) and activity-uncertainty term in (29). Replaced “activity-aware denoising formulations” with the direct description “activity-weighted moments”; this is a description of the cited formulas, not a named method.
2. Replaced “classifier provides the activity probability” with “we estimate the activity probability from the output of the separately trained classifier,” distinguishing the learned estimate from the exact local probability `p^star`.
3. Restricted the current-mean feature statement to “When evaluated, the classifier uses ...,” preserving the within-training-range context and avoiding any implication that the classifier is evaluated during the Gaussian fallback in V.

A repeated comparison found all **14 equation environments unchanged byte-for-byte** between initial and revised drafts. No mathematical definitions, equation labels, or algorithm rules changed in this review round. Final chapter-lead acceptance and root compilation remain pending.
