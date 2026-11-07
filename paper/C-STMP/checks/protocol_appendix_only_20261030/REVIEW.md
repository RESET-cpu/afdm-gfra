# Protocol relocation review

Reviewed the applied canonical sources on 2026-10-30. This record concerns the authorized relocation of experimental process notes to Appendix C; it does not endorse independent validation or claim that retrospective development did not occur.

## Source and disclosure review

- The executed migration audit passed 67 checks. Chapter VI contains only the six authorized edits. Its formulas, parameter table, figure commands, labels, citations, numerical comparisons, and remaining scientific interpretation are unchanged.
- Appendix C adds only the single-scene actual stopping records (60 as the imposed minimum, 85 for STMP, actual displayed endpoints). Every preexisting Appendix C sentence remains. Development/evaluation overlap, retrospective damping, selected scene-372 replacement, diagnostic reuse, Q=8 capped-run counts, and finite-output retention remain explicitly recorded there.
- Searched and read the appendix/protocol-related matches in chapters I-VI. Neither body text nor figure captions contain an Appendix C reference, its label/name, or a general pointer to that protocol appendix. The remaining appendix references concern the AFDM model, phase/noise estimation, implementation, or the cited source paper. The main file still includes Appendix C.
- Moving the Q=8 paragraph does not introduce a stronger pilot claim: the remaining result uses the tested 24-versus-32-frame threshold at fixed per-frame energy. Moving the actual stopping records does not introduce a new stopping-speed claim: the main text still describes approximately 30 iterations approaching final accuracy in one scene. High-SNR reversals and the off-grid AER/NMSE counterexample remain unchanged.

## Actual visual inspection

Opened `previews/final-09.png`, `previews/final-10.png`, and `previews/final-11.png` with `view_image`; no text extraction was used as a substitute for these inspections.
- Page 9: Figure 2, legends, caption, metrics, and text fit normally. The former protocol paragraph is absent; the transition to denoising and convergence remains readable.
- Page 10: Figures 3-5, axes, legends, shortened captions, and scientific analysis have no clipping or overlap. No stop-record or Q=8 run-count notice remains in the prose/captions.
- Page 11: Figures 6-7 and captions are intact; the user-count caption contains no Appendix C pointer. Text flows normally into the cross-profile discussion and Appendix A, with no conspicuous unintended whitespace or visibly unresolved reference.

No canonical sources, figures, or data were written during this review. No experiment, training, or compilation was performed by this reviewer. The first audit invocation exposed the dataset's nested iteration-field location; the reader was corrected and all 67 checks then executed successfully. No historical audit was modified.

## Inspected source bindings

- `sections/06_simulation_results.tex`: `471871aefc97400a0ae9f4ccbfca32480afdef65225479a9221f88b99bf527b8`
- `sections/appendix_evaluation_protocol.tex`: `aa33238783a0f1e37a6ba8bd217ac238d16301230721ec7b97c5f45ca6470a95`

## Inspected image bindings

- `final-09.png`: `5dbd377f2493e3b99252122fcab15407b54988328263cc61d4a6372758ac7c72`
- `final-10.png`: `90061367a73f1b99fe789838f6464f103f06f2bcdc2976fdaf2e8ab1a690554a`
- `final-11.png`: `d0f8c6ab0c892e29ebdfc16de288f37e6592d16133c9b93ce4775c99714df845`
