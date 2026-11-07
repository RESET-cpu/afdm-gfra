# III-A initial draft and source record

Writer: subsection III-A writer, 2026-10-30. Only the assigned initial draft and this note were written. No canonical manuscript, experiments, or shared terminology file was modified. This is an initial author draft for chapter-lead review, not an independent acceptance decision.

## Scope

- Added `Receiver Structure` and compatibility-free new label `sec:receiver-structure`.
- Defined the author-approved descriptive module abbreviations MFLE and GPJD once. They are names for this manuscript's functions, not method names taken from the references.
- Connected the existing II-C posterior factorization to each module's likelihood/prior responsibilities, complete interface quantities, and extrinsic feedback. No new formula, mathematical definition, or equation label was introduced. As requested by the root through the chapter lead, added a reference to the planned `fig:receiver-structure` and the `% ROOT_RECEIVER_DIAGRAM` insertion marker; the root owns that diagram.
- Kept fixed pilot/noise estimates and normalized-coordinate scheduling as concise cross-references to `sec:schedule`; did not carry over frontend derivations.
- Specified approximation rather than exact global Bayesian recovery. The local Gaussian arithmetic and the learned estimates must not be read as guarantees about the physical residual law or globally exact MMSE estimates.

## Primary passages actually checked

1. **Shen et al., local `reference/literature/shen2025.pdf`, PDF pp.6–7, III-A, Eq.(20), Figs.2–3.** Read the posterior grouping, functional DDAI/JCESD/TSE module descriptions, and the order of incoming soft message, factor used, outgoing soft message, and feedback. This is the organizational inspiration. The draft neither imports the three-module model nor attributes MFLE/GPJD to Shen. No Shen-specific GAMP, MRF, symbol detection, or convergence guarantee is transferred.
2. **Cai et al., local `reference/literature/cai2026.pdf`, PDF pp.5–6 / journal pp.3579–3580, III opening, III-A Eqs.(6)–(11), III-B Eqs.(12)–(17).** Verified that module A uses the observation likelihood plus the incoming message, module B uses the channel/activity priors, and the Gaussian extrinsic message is a posterior-to-input quotient. Eq.(17) explicitly identifies Gaussian moment projection and the scalar variance approximation. The initial draft cites `cai2026` for the TMP organization and Gaussian message basis, while using the manuscript's own multi-frame matrices, tensor blocks, and learned GPJD statistics.
3. **Ma, Yuan, Ping, author-hosted PDF [Turbo Compressed Sensing with Partial DFT Sensing Matrix](https://lsec.cc.ac.cn/~mjj/papers/Ma2015b.pdf), PDF pp.1–3 / journal pp.158–160, II-A opening and Fig.1, II-B.** Read via web because a local `ma2015` original was not found. II-A explicitly describes extrinsic output being the other module's a priori input and iterative processing; II-B distinguishes the proposed turbo algorithm from the standard same-variable sparsity combiner. The draft cites the turbo principle only, not the DFT-specific formula or state evolution conclusion.
4. **Minka, author-hosted PDF [Expectation Propagation for Approximate Bayesian Inference](https://tminka.github.io/papers/ep/minka-ep-uai.pdf), PDF pp.2–3, Section 2 Eqs.(5)–(6), Section 3 Eq.(8).** Read via web because a local `minka2001` original was not found. Verified moment matching for a spherical Gaussian approximation and an approximate factor expressed as a posterior ratio. The draft uses this only as the basis of Gaussian approximation and extrinsic quotient, with no assertion that the trained maps exactly implement EP.

## Internal consistency checks performed

- Read canonical II–V and `main.tex`, relevant `references.bib` entries, root `AGENTS.md`, root README current paper locator, and the TMP/Gaussian-message entries in `docs/TERMINOLOGY.md`.
- `eq:working-posterior`, `sec:schedule`, `sec:learning`, and all cited keys already exist in the current manuscript.
- `fig:receiver-structure` is the root's planned new native diagram label and requires its insertion during integration.
- The current incoming/outgoing symbols match III-B/C and V exactly: MFLE consumes `(Xpri,gamma)`, outputs `(R_L,v_L)`; scheduling forms `(R_k,v)`; GPJD yields `p_k` and joint moments and outputs `(X_out,gamma_out)` before feedback scheduling.
- No compilation performed; root owns integration, compilation, and rendering.

## Review attention

- The chapter lead should ensure its short section opening does not redefine MFLE/GPJD or duplicate the first paragraph.
- The final paragraph describes the core Gaussian quotient; clipping and retained-site rules remain in the detailed GPJD derivation and overall schedule, without implying that those safeguards are exact EP updates.


## Revision response to chapter-lead review

The chapter lead identified that "provides the conditional mean" could imply an exact trained-network output. `III_A_revised.tex` now explicitly states that the network estimates the active-channel conditional mean, that derivatives of this same mean map provide a variance estimate, and that the classifier estimates the activity density ratio. The subsequent approximate joint-moment statement, all interfaces, citations, and diagram marker remain unchanged. `III_A_initial.tex` is preserved as the actual reviewed initial draft.
