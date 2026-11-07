# III-B initial draft: source and change notes

Date: 2026-10-30. Writer: III-B subsection agent. This is an initial draft for chapter-lead review, not a canonical manuscript edit.

## Scope and terminology

- Output: `III_B_initial.tex`; title **Multi-Frame Linear Estimation**, label `sec:mfle`.
- MFLE is the user-approved descriptive name of this paper's module. It is not presented as an established algorithm name or an independent new linear estimator.
- Standard source terms used: linear MMSE estimation, Gaussian message, posterior mean/covariance, extrinsic mean/variance, singular value decomposition.
- Inputs and outputs retain the current manuscript's normalized coordinates, fixed effective pilot matrix/noise estimate, terminal tensor reshaping, and scalar variance interface. No training, experiments, or implementation changes were performed.

## Primary-source verification

| Source | Actually read | Relevant support and boundary |
|---|---|---|
| Cai et al., `reference/literature/cai2026.pdf` | Local PDF pp. 5–6, printed pp. 3579–3580, Sec. III-A, (6)–(11) | Gaussian likelihood times incoming Gaussian message; LMMSE posterior; scalar covariance approximation; posterior-to-prior division and outgoing extrinsic mean/variance. Cai's (7)–(8) exploit row-orthogonal pilots; the full-Gram expressions in this subsection are the existing manuscript's Gaussian linear-estimation formulas, not attributed as Cai's printed equations. |
| Ma, Yuan, and Ping, *Turbo Compressed Sensing with Partial DFT Sensing Matrix* (2015), [author PDF](https://lsec.cc.ac.cn/~mjj/papers/Ma2015b.pdf) | No matching local PDF found. Opened the original PDF online; Sec. II-A, PDF pp. 1–2 / printed pp. 158–159, Fig. 1 and (11a)–(11b); Sec. II-B begins on PDF p. 3 / printed p. 160 | Supports the terminology and use of extrinsic output as the other module's prior input. No partial-DFT state-evolution or optimality claim is imported. The already-present `ma2015` citation is retained at Gaussian extrinsic-message calculation. |
| Minka, *Expectation Propagation for Approximate Bayesian Inference* (2001), [author PDF](https://tminka.github.io/papers/ep/minka-ep-uai.pdf) | No matching local PDF found. Opened the original PDF online; Sec. 2, PDF p. 2, (5)–(6); Sec. 3, PDF p. 3, (8) | Supports Gaussian moment approximation and forming an approximate factor by the ratio of the new posterior to the prior/cavity distribution. The subsection states the actual isotropic trace approximation explicitly. It does not claim that a full covariance is moment matched after replacing it by a scalar. |
| Ma and Ping, `reference/literature/ma2017_oamp_v3.pdf` | Local PDF p. 3, Sec. III-A, (12)–(15c) | Corroborates standard linear-estimation/LMMSE and SVD terminology, including a general Gram-matrix inverse. Not added as a new manuscript citation; no OAMP decorrelation or state-evolution assertion is introduced. |

The notes above are paraphrases and locators. No source passage was copied into the subsection. Web PDF equation text extraction for the Ma/Minka files is partially garbled; the relevant original section labels, surrounding explanation, and equation numbers are readable. The exact algebra retained below is checked against the current manuscript and standard Gaussian identities, rather than claimed to have been transcribed from garbled extraction.

## Changes and cross-chapter interfaces

1. Reordered the opening to identify the incoming GPJD message before explaining the multi-frame effective matrix and its full Gram matrix.
2. Replaced the forward reference to the simulation-only pilot-design equation with the already-defined matrix `P` and `eq:effective-pilot`. Chapter II states `P P^H = K E_p I_Q`; no pilot design is changed.
3. Replaced “per measurement vector” with “for each column of X” to make the `KN` covariance dimension unambiguous.
4. Kept the posterior → trace approximation → extrinsic division → SVD calculation in one continuous argument. The only wording-level clarification is that scalar approximation preserves the trace, not every covariance entry.
5. Ended with the MFLE-to-GPJD interface `R_k`, `bar v`, and `v = kappa bar v`, with scheduling in `sec:schedule` and variance adaptation in the compatible `sec:variance-update` label inside III-C.
6. Read canonical sections II–V, main.tex, relevant bibliography/terminology entries, root AGENTS.md/README.md, and the pilot/settings portions of VI. No parameter-preprocessing material is duplicated here.

## Preserved mathematical content

All original mathematical expressions in the former Linear Estimation subsection are retained. The four labels `eq:linear-mean`, `eq:linear-variance`, `eq:linear-extrinsic`, and `eq:linear-fraction` remain unchanged, as do the SVD definition, positivity condition, alternative expression for the extrinsic mean, and output variance scaling. No additional numbered equation is introduced. No derivation is removed. A mechanical comparison found all three displayed math environments (one align and two equation environments, containing four numbered equations) identical after removing whitespace; the four equation labels also match exactly. No independent compile or rendering was performed.

## Chapter-lead review and revision response

The chapter lead accepted the core derivation and formula preservation and requested two wording corrections. Both are addressed in `III_B_revised.tex`; `III_B_initial.tex` is preserved unchanged.

1. **Locate the phase difference correctly.** The revised opening explicitly places `exp(j(q-q') beta_k)` in the cross-frame inner products. It no longer describes that phase difference as an effective-matrix element; `eq:effective-pilot` has the individual element phase `exp(jq beta_k)`. The conclusion remains that row orthogonality need not carry over to the effective matrix.
2. **Clarify the GPJD interface.** The closing now states that GPJD uses `(R_k,v)`, where `v = kappa bar v`, while `bar v` is retained separately for message scheduling. This agrees with the existing schedule and keeps the variance-adaptation cross-reference.

A second mechanical comparison confirms all three displayed math environments in the revised draft remain identical to the initial draft and, transitively, to the original canonical subsection. No equations, labels, algorithms, or model assumptions changed in this revision.
