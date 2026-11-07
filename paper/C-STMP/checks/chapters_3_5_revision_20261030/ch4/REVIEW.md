# Chapter IV lead review

Date: 2026-10-30. Chapter lead: `/root/chapter4_lead`. Scope: chapter drafting and source/argument review; root performs canonical integration, full compilation, and visual checks.

## IV-A: Channel Denoising with Colored Gaussian Noise

- Independent writer: `/root/chapter4_lead/section4a_writer`.
- Initial draft/source record preserved as `section4a.initial.tex` and `section4a_sources.initial.md`.
- Lead read the complete submitted draft and source notes. Checked the fixed-C population minimizer, weighted residual/score algebra, the complex-to-real factor of two, unchanged four numbered equations, matrix-preconditioning attribution, and continuity to GPJD.
- Disposition: accepted. No substantive or wording correction required after review. The added score residual identity is an algebraic explanation of the existing loss, not an algorithm change.

## IV-B: Variance from Conditional-Mean Derivatives

- Independent writer: `/root/chapter4_lead/section4b_writer`.
- Initial draft/source record preserved as `section4b.initial.tex` and `section4b_sources.initial.md`.
- Lead read the complete draft and source notes, checked Dytso's original Jacobian orientation against the stated output-by-input convention, the real-to-complex trace factor, fixed-covariance differentiation of the full map, sign-vector second moment, centered-difference denominator, direction reuse, pooling interface, and three-pass cost.
- Disposition: accepted. The trained-mean derivative is explicitly an approximation; the Monte Carlo construction is described as an adaptation, without a closed-loop unbiasedness claim. No correction required.

## IV-C: Density Ratio Estimation

- Independent writer: `/root/chapter4_lead/section4c_writer`.
- Initial draft/source record preserved as `section4c.initial.tex` and `section4c_sources.initial.md`.
- Lead checked explicit activity labels, common variance sampling, the conditional densities, frozen deterministic features, unrestricted population logit, and prior correction. Both numbered equations are preserved.
- Round 1 disposition: language revision requested. Four citations to the same short Menon argument and a repeated statement of the common variance law interrupt the otherwise continuous derivation. The author is asked to retain at most two suitable in-text source anchors and use the already-defined sampling model when introducing Bayes' rule. Precise original-source locators remain in the source note. No mathematical change requested.
- Round 2 disposition: accepted after the original author revised the draft. The lead reread the actual revision: two source anchors remain, the repeated sampling-law statement is replaced by a direct bridge, and both equations are unchanged.

## IV-D: Offline Training

- Independent writer: `/root/chapter4_lead/section4d_writer`.
- Initial draft/source record preserved as `section4d.initial.tex` and `section4d_sources.initial.md`.
- Lead read the complete draft and its source/implementation notes. Checked clean-channel sampling and scene separation against VI, the existing covariance ordering, 2M-channel representation, retained width 128, sequential two-network training, current classifier input scaling and signed-log inner-product description, and the fixed-M,N / variable-K,Q scope.
- Disposition: accepted. The classifier feature wording is a clarification of the unchanged implementation. Architecture attribution is confined to the RefineNet family; covariance conditioning and feature choices remain manuscript design choices. No correction required.

## Assembled-chapter review and verification

- Deliverable: `chapter_reviewed.tex`, assembled from the lead's short chapter opening and the four reviewed independent drafts. The opening explicitly connects the chapter to the three statistics required by GPJD, without redefining either approved module abbreviation.
- All four subsections have independent writers. IV-C was returned to its original writer for focused language correction and rereviewed. Initial drafts and source notes remain available for all four writers.
- Mathematical review: the fixed-covariance mean target, weighted score residual, complex-real convention, conditional covariance identity, approximate derivative calculation, class-prior correction, and sequential training remain consistent across A--D and with III.
- Automated text checks in `verification.json`: 8 of 8 numbered equation bodies are identical ignoring whitespace; all equation and subsection labels retained; no missing chapter references or citation keys; no duplicate chapter labels; exactly four approved subsection titles. No numbered equation moved or changed. New inline expressions only make existing definitions, equivalent algebra, or current input features explicit.
- Canonical IV remained byte-identical to its saved baseline throughout this authoring task. No shared terminology, bibliography, model, weight, configuration, result, or other manuscript section was edited by this lead or its writers.
- Source record: `SOURCES.md`, with per-author detailed notes. No unresolved wording/source gaps. Vincent was inspected as the original journal article via a mirror after its university URL denied access; this is recorded transparently.
- Disposition: ready for root integration. Root owns full-paper compilation and rendered-page checks; they have not been claimed or performed here. No training, inference, or experiments were run.
