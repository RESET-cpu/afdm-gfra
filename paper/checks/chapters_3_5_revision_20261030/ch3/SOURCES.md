# Chapter III source map

Date: 2026-10-30. This map records the sources actually consulted for the scoped rewrite. The subsection notes distinguish local original PDFs, original papers accessed online, and manuscript-specific algebra. It is not a claim that all current receiver choices appear in a cited paper.

| Draft content | Original source and locator | Scope of use |
|---|---|---|
| Functional organization and module interfaces | Shen, local `reference/literature/shen2025.pdf`, PDF pp.6–7, III-A, Eq.(20), Figs.2–3 | Organizational reference; no Shen GAMP/MRF algorithm or module name is imported. |
| TMP organization, Gaussian linear posterior and extrinsic messages | Cai, local `reference/literature/cai2026.pdf`, PDF pp.5–6 / printed pp.3579–3580, III opening and III-A, Eqs.(6)–(11); [Ma 2015 author PDF](https://lsec.cc.ac.cn/~mjj/papers/Ma2015b.pdf), PDF pp.1–3, II-A/B, Fig.1 and Eqs.(11a)–(11b) | Standard message structure and quotient. The full-Gram matrix expressions and AFDM dimensions are retained from this manuscript, not represented as Cai's row-orthogonal formula. |
| Gaussian approximation and factor quotient | [Minka 2001 author PDF](https://tminka.github.io/papers/ep/minka-ep-uai.pdf), PDF pp.2–3, Sections 2–3, Eqs.(5)–(6), (8) | Moment approximation and posterior/cavity division. Spherical/trace approximation is explicitly identified in the manuscript. |
| General linear estimator and SVD terminology | Ma and Ping, local `reference/literature/ma2017_oamp_v3.pdf`, PDF p.3, III-A, Eqs.(12)–(15c) | Corroborating terminology checked by III-B writer; no new bibliography entry or OAMP claim added. |
| Conditional channel denoising and activity-weighted moments | Cai, PDF pp.6–8, III-B, Eqs.(16)–(42); Liu and Yu, local `reference/literature/liu2018_massive_mimo.pdf`, PDF pp.5–6, III-B/C/D, Eqs.(17)–(29) | Local Gaussian denoising, activity probability, mean and uncertainty decomposition. This manuscript's general `q_tr` formulas follow Bayes' rule and conditional moments; Liu's specific Rayleigh prior is not imported. |
| Gaussian site terminology and quotient | [Vehtari et al., official JMLR PDF](https://jmlr.org/papers/volume21/18-817/18-817.pdf), PDF p.5, Section 2.1, site definition after Eq.(1), cavity/tilted definitions and updated-site quotient; p.6, Section 2.2 | Local Gaussian approximation to a factor and subtraction of natural parameters. Current retained-site and positivity rules remain manuscript implementation choices. |
| Posterior expected residual variance | Vila and Schniter, local `reference/literature/vila_schniter_2013.pdf`, PDF p.4 / printed p.4661, III-A, Eqs.(22)–(27) | Expected residual energy equals squared residual of the mean plus posterior variance. Applying it to the local query model is explicitly this manuscript's adaptation; no global EM monotonicity or exact-neural-posterior claim. |

MFLE (**Multi-Frame Linear Estimation**) and GPJD (**Generative-Prior-Aided Joint Denoising**) are author-approved descriptive names for this manuscript's modules. Their combined names/abbreviations are not attributed to an existing paper. Root maintains the shared terminology record.

## Detailed subsection records

- `III_A_sources.md`: actual passages read, message-interface checks, and response to the lead's precision correction.
- `III_B_sources.md`: actual passages read, exact equation-preservation check, phase-inner-product and GPJD-input corrections.
- `III_C_sources.md`: local denoising, mixture, site, and residual-variance source checks, plus the three precision/citation corrections returned to the same writer.

The Ma/Minka original PDFs were accessed online because matching local PDFs were not found. Their online formula extraction is partly garbled; section/paragraph support is distinguished from the unchanged manuscript algebra. The Vila PDF's text extraction omits many formula symbols, so the lead also inspected the existing rendered original page. Full reading of every reference or independent publication-readiness certification is not claimed.
