# Chapter V lead review

Date: 2026-10-30. Chapter lead: `chapter5_lead`.

## Writers and review sequence

The two approved subsections had separate writers, started in parallel only after root released Chapter IV. All drafts and review records remain inside `ch5/`; no writer or chapter lead changed the canonical manuscript, bibliography, terminology file, code, configuration, or results.

| Subsection | Writer | Initial record | Returned issue | Final disposition |
|---|---|---|---|---|
| V-A Overall Algorithm | `chapter5_lead/v_a_writer` | `a_overall_algorithm.initial.tex`, `a_sources.initial.md` | The positive-variance statement could be read as applying to raw pooled tau rather than the value after flooring. The first GPJD input assignments were implied but not explicit in the pseudocode. | The same writer clarified that the lower bound ensures tau > 0 and wrote the first-iteration R and raw-variance assignments explicitly. Lead reread the returned text and accepts it. |
| V-B Computational Complexity Analysis | `chapter5_lead/v_b_writer` | `b_complexity.initial.tex`, `b_sources.initial.md` | The writer identified an unoptimized three-matrix NumPy contraction whose implementation count exceeds the standard matrix-product count. Root confirmed the contraction plan and required an explicit pairwise counting convention while preserving the two formulas. | The same writer added the standard dense/pairwise counting convention at the beginning and recorded the implementation limitation in its sources. Lead reread the returned text and accepts it under that stated convention. |

The lead supplied only `00_chapter_opening.tex`, then assembled the actual returned drafts in `chapter_reviewed.tex`. No extra subsection was inserted. Initial records were not overwritten during the corrections. This is a concrete two-writer/one-lead review, not a claim of independent external peer review or full manuscript certification.

## Content and interfaces checked

- The approved structure is exactly V-A Overall Algorithm and V-B Computational Complexity Analysis. There are no independent engineering, frontend, damping, or stopping headings.
- Former III-A preprocessing moves into V-A with its variable-projection and MDL citations and appendix links. Existing assumptions remain fixed within the block. No later phase-selection candidate is imported.
- MFLE/GPJD naming and references match canonical revised III and reviewed IV. The mean, fixed-covariance derivative, classifier, and extrinsic message use the same current input variance; the newly computed ratio is used only in the next iteration.
- Fixed training-scale normalization, initial prior and sites, raw linear variance history, and first-message behavior remain unchanged.
- Supported-range site rejection does not skip the classifier. Out-of-range input retains sites and uses Gaussian evidence. In both cases conditional moments combine the current query with the current retained/updated site.
- Stopping preserves separate successive activity-probability changes and current probabilities compared with the previous smoothed history. Accepted-site precision/natural-parameter stability, minimum iterations, consecutive-condition counts, decision-window count, and iteration limit remain. Numerical thresholds stay in VI.
- Returned estimates are rescaled, probabilities remain unscaled, and the activity threshold remains one half.
- The V-B neural arithmetic uses one center plus two offset mean passes per direction, reuses the center mean for classification, and distinguishes supported-range neural calls from Gaussian fallback. No unintroduced standalone MP abbreviation remains in this chapter.

## Equations and labels

The four V-A and two V-B numbered equations are retained without mathematical changes; `verification.json` compares complete equation environments after removing whitespace. No new numbered equation or equation label is introduced.

- V-A: `eq:input-damping`, `eq:gaussian-evidence`, `eq:output-damping`, `eq:variance-stopping`.
- V-B: `eq:iteration-complexity`, `eq:total-complexity`.
- `sec:overall` remains at the chapter. `sec:schedule`, `sec:frontend`, and `sec:damping` all resolve to V-A. The first two old subsection identities are merged without changing their referring text's intended target. The former III-A frontend contained no numbered equation to move.

## Complexity qualification and correction of preparation notes

The initial `PREPARATION.md` and root preparation correctly located M-by-M factorizations but did not cover the entire NumPy contraction path. During V-B authorship, the writer found `STMP/gaussian.py`'s whitening expression `np.einsum("ij,jk,kl->il", ..., optimize=False)`. Root confirmed with contraction-plan analysis, without receiver inference or performance measurement, that this unoptimized contraction has scaling 4, versus scaling 3 when evaluated pairwise. Thus the unchanged implementation contains an additional O(M^4) cost at that operation.

The manuscript now explicitly counts standard dense matrix products/factorizations, with three-matrix products evaluated pairwise. Its retained M^3 term and the two complexity formulas are the algorithmic cost under that stated algebraic convention, not a strict bound on the unchanged NumPy instruction path. This is a material counting qualification, not a code optimization or measured performance result. It supersedes any implication in the initial preparation that the displayed formula had already been established as a strict whole-implementation count. No code or experiment has been changed.

## Verification and handoff

`verify_chapter.py` assembles the final draft and checks the two headings, all six preserved equations, compatibility-label uniqueness in the combined manuscript, chapter cross-references/citations, initial-draft records, and unchanged code/VI hashes. Results are in `verification.json`; edits are in `chapter5.diff`.

Root retains responsibility for canonical integration, the final cross-chapter check, LaTeX compilation, and visual layout verification. The chapter lead did not compile or render. No training, inference, runtime test, parameter change, or experimental rerun was performed.
