# Chapter IV source and terminology record

Date: 2026-10-30. This chapter uses existing bibliography keys and introduces no new method names or abbreviations. MFLE and GPJD are the author-approved names defined in III, not names attributed to these sources. Individual author records retain source-access details and precise adaptation boundaries.

| Manuscript use | Primary source and locator | Attribution boundary |
|---|---|---|
| Conditional mean / score; Tweedie's formula | Dytso--Poor--Shamai, arXiv:2104.01883, PDF p.2, equation (3); Efron 2011, PDF p.4, section 2, equations (2.7)--(2.8) | Dytso supplies the vector arbitrary-covariance identity; the manuscript applies it after its existing complex-to-real transformation. |
| Denoising score matching | Vincent 2011, PDF pp.6--7 / printed pp.1666--1667, section 4.2, equations (4.3)--(4.5) | The manuscript's covariance-weighted score residual follows by algebra from its retained mean loss. It is not presented as Vincent's original isotropic loss unchanged. |
| Correlated-noise conditioning | Shastri et al., local `reference/literature/shastri2022_dgec.pdf`, PDF pp.15--16, section III-B, equations (38)--(41) | Supports supplying noise statistics for correlated-noise training. Its independent noise-realization input differs from the manuscript's explicit covariance input. |
| Network preconditioning | Karras et al., local `reference/literature/karras2022_edm.pdf`, PDF p.8, section 5, equations (7)--(8); Table 1 on PDF p.3 | Scalar input, skip, and output preconditioning are the source; their matrix-covariance extension is explicitly this manuscript's adaptation. |
| Conditional covariance from the mean Jacobian | Dytso et al., PDF p.4, II-A, equation (9), and PDF p.5, IV, Proposition 1, equation (22) | The source uses input-by-output Jacobians. Transposition to this manuscript's output-by-input convention gives P = J Sigma. Complex-coordinate normalization divides the real covariance trace by D. |
| Monte Carlo divergence / random-direction trace approximation | Metzler--Maleki--Baraniuk, arXiv:1406.4175v2, V-B, equation (21) and following paragraphs | Original: Gaussian probes and one-sided differences. Manuscript: sign probes, covariance scaling, centered differences, and fixed per-terminal probes within a block. The adaptation and resulting three mean-network passes are stated; no exact learned covariance or closed-loop unbiasedness is claimed. |
| Binary classification, density ratio, prior odds correction | Menon--Ong 2016, PDF pp.2--3 / printed pp.305--306, II.2, III equations (6)--(8), IV.2 equations (16)--(17) | The source links class probabilities and density ratios. Conditioning on the common variance-sampling model yields the current logit equation. The trained classifier is an estimate of the population optimum. |
| Conditional RefineNet backbone | Song--Ermon, arXiv:1907.05600v3, PDF p.14, Appendix A.3; conditional normalization in Appendix A.1 | Supports the architecture family. Local `DirectCaiNetwork` / `NCSN` implementation independently supplies width 128 and the current conditioned trunk; covariance inputs and classifier features are manuscript design choices. |

Original links:

- Dytso: https://arxiv.org/pdf/2104.01883
- Efron author copy: https://efron.ckirby.su.domains/papers/2011TweediesFormula.pdf
- Vincent journal article inspected through a mirror after the university URL denied access: https://gwern.net/doc/ai/nn/diffusion/2011-vincent.pdf
- Metzler: https://arxiv.org/html/1406.4175v2
- Menon--Ong publisher copy: https://proceedings.mlr.press/v48/menon16.pdf
- Song--Ermon original: https://arxiv.org/pdf/1907.05600

Detailed subsection records: `section4a_sources.md`, `section4b_sources.md`, `section4c_sources.md`, and `section4d_sources.md`. The last record identifies the actual current conditioned backbone and distinguishes it from a different `channel_score.py` architecture path. Current classifier features were checked in `src/algorithm/STMP/activity.py`; the signed logarithmic inner-product wording describes the retained code.

All new explanatory statements clarify existing equations or implementation choices. No numerical results, training procedures, loss formula, network count, or receiver operation are changed.
