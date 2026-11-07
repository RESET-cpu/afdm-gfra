# Chapter V consolidated source record

The subsection source notes `a_sources.md` and `b_sources.md` contain the detailed evidence and returned revisions. This record identifies the sources and their limited role for root integration.

## Original papers read directly

| Source | Locator | Use and limit |
|---|---|---|
| Shen, `reference/literature/shen2025.pdf` | PDF pp.9–10, end of III-C; Algorithm 1 on p.10, especially line 19; following complexity paragraph | A compact transition from derivations to the algorithm, a short damping mention, explicit stopping in pseudocode, and operation-wise cost discussion. The current paper's updates, stopping windows, and complexity are not claimed as Shen's algorithm. |
| Cai, `reference/literature/cai2026.pdf` | PDF p.8 / journal p.3582, Algorithm 1; PDF pp.9–10 / journal pp.3583–3584, V-B1, Eqs.(57)–(58), Algorithm 2 | Gaussian means/variances damped in both directions and sequential module scheduling. V-A cites the damping practice. Its equations still implement this receiver's existing running-message damping. Cai's query-dependent channel normalization is not imported. |
| Cai, same PDF | PDF p.11 / journal p.3585, V-C complexity paragraph | Conventional separation of matrix operations and network-forward costs. Lead also directly reread this paragraph. Its FFT-based linear count and two-score-network count are not this paper's costs. |

No paper passage was copied verbatim into Chapter V. MFLE and GPJD are the author-approved descriptive module abbreviations already defined in III, not terminology attributed to these papers.

## Retained frontend sources

The former III-A citations `oleary2013` and `nadakuditi2008` move with the frontend paragraph. Variable projection and the MDL/eigenvalue method keep their pre-existing meaning and appendix equations. Writers and lead checked the existing manuscript, appendix, bibliography, and earlier terminology records; they did not claim a fresh complete rereading of those two external original articles. No new frontend theory is introduced in this revision.

## Mathematical and implementation provenance

All six Chapter V numbered equations were already present in the baseline. Their locations and unchanged mathematical contents are recorded in `REVIEW.md` and `verification.json`. New inline first-iteration assignments and the explicitly indexed activity-history comparison spell out existing code behavior rather than change it.

The main implementation sources inspected are the current `C_STMP_variance_em_20261025/receiver.py` and `iterations.py`, shared `STMP/linear.py`, `gaussian.py`, `iterations.py`, `denoiser.py`, `C_STMP/moments.py`, and the noise-estimation helper. The version's two networks, fixed physical noise, scalar query variance, pooled derivative variance, classification, Gaussian fallback, and stopping checks are the implementation authority. The separate phase-selection candidate in the root README was not imported.

## Complexity convention and known implementation cost

V-B explicitly assumes standard dense matrix-operation costs and pairwise evaluation of three-matrix products. The actual unchanged `STMP/gaussian.py` uses an unoptimized three-input `einsum` for one whitening product. The V-B writer identified it from code; root checked the contraction plan and reported scaling 4 for that path and scaling 3 for pairwise evaluation. This adds an implementation-level O(M^4) operation and means the retained displayed formula is not a strict operation count of every current NumPy kernel. No performance measurements were made. The record is transparent about this distinction, and neither implementation nor displayed equations were changed.

No unresolved source gap affects the scoped prose/organization changes. Frontend original articles rely on existing verified manuscript sourcing rather than new full-paper review in this chapter task. Final publication-level citation certification and empirical runtime claims are outside this work.
