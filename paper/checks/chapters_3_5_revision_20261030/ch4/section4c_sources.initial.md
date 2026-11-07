# IV-C author draft and source verification

Writer scope: only `section4c.tex` and this note. No canonical manuscript edits, training, experiments, or compilation were performed.

## Primary source inspected

Menon and Ong, *Linking losses for density ratio and class-probability estimation*, ICML 2016, primary publisher PDF: https://proceedings.mlr.press/v48/menon16.pdf (read directly on 2026-10-30).

- PDF p.2 / printed p.305, §2.2: logistic loss has the log-odds link; its Bayes-optimal scorer is the link applied to the class posterior. The source uses labels in {−1,+1}. The manuscript's label a in {0,1} is the equivalent coding y=2a−1, yielding log(1+exp(z))−az.
- PDF p.2 / printed p.305, §3, equations (6)–(8): posterior odds equal the density ratio multiplied by prior odds. Conditioning on v gives the manuscript equation `eq:ideal-logit` because the variance sampling distribution is identical for the two classes. This conditioning is the present model's application of Bayes' rule, not an additional theorem attributed to the source.
- PDF p.3 / printed p.306, §4.2, equations (16)–(17): distinguish the ratio recovered from the Bayes-optimal scorer from the density-ratio estimator formed using a fitted scorer. The logistic example immediately after equation (17) has estimated ratio exp(s(x)) for balanced classes. This supports the manuscript's distinction between ideal population logit and trained approximation.

## Draft changes and interfaces

1. Lead directly from the density ratio required by GPJD in III-C.
2. Define a∈{0,1}, a=1 active, and Pr(a=1)=π_tr=1/2 before the loss.
3. State active/inactive query construction and the common variance sampling law before the classifier objective. Gaussian noise is independent of the clean channel, consistently with `eq:query-densities`.
4. Retain the complete `(R,v,F_theta(R,vI_D))` classifier argument. The frozen channel estimate is a deterministic feature of R and v; no additional independent information or empirical performance is claimed.
5. State the population relationship for unrestricted logits, then the learned approximation and prior correction. Do not claim exact calibration of a trained finite network.

Existing equations `eq:classifier-loss` and `eq:ideal-logit` are preserved verbatim. The subsection label `sec:density-ratio` is preserved. Cross-references are `eq:query-densities` and `eq:activity-probability`, both present in current canonical III-C. The only citation key is the existing `menon2016`; no new terminology, algorithm names, or bibliography entries are introduced.

## Checks

The author compared both complete equation environments against canonical IV-C and checked the referenced equation labels and citation key. Chapter-level review and root compilation remain separate steps.
