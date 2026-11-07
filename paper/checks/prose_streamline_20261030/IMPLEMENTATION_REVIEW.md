# Implementation relocation review

Status: PASS. Read-only review of the applied canonical IV, V, VI, and new Appendix D; only this report was written. No compilation, experiments, or canonical edits were performed.

Scope: parameter relocation from VI, classifier input preservation, and stopping-rule preservation against `before/sections`. This is not a repeat of the whole-manuscript formula audit.

## Preservation findings

1. The full stopping-rule text from the original V, beginning “Stopping requires stable estimates” and ending with the last-iterate return at `I_max`, is identical after whitespace normalization to Appendix D lines 48–69. This preserves every monitored quantity, the requirement for accepted site updates, precision and natural-parameter checks, the previous activity history used in the residual, the order of history updating, initial history equal to rho, separate consecutive-window checks, and the hard activity-vector window.
2. The display formula `eq:variance-stopping` is preserved byte-for-byte as text in Appendix D lines 53–58, including its denominator. No stop threshold, timing, or acceptance condition changed.
3. The original classifier-feature text from IV, from “The classifier takes the real and” through “per terminal.”, is identical after whitespace normalization to Appendix D lines 34–39. Both complex-map inputs, their scale, log variance, input/output/residual energy transforms, Dv normalization, and the sign-preserving logarithmic transform of the real inner product are preserved.
4. The numerical migration below is complete. VI still retains dataset sizes, Adam, batch sizes, learning rates, EMA decay, total training epochs, covariance sampling law, and the validation-selection rule. The selected checkpoint numbers and fine derivative/stopping settings are supplied by D as intended.
5. V explicitly holds the current denoiser variance fixed during the module update and Algorithm 1 still computes the next kappa before forming feedback with the current variance. IV still differentiates the complete mean map with covariance fixed. These operational distinctions remain intact.

## Parameter map

| Original source | Retained value or operation | Applied destination |
|---|---|---|
| VI 87–88 | Training reference scale 0.2647966453 | D 27–28 |
| VI 109 | Channel-network selected epoch 200 | D 28–29 |
| VI 112 | Classifier selected epoch 90; validation selection | D 30–31; VI 111 also retains selection rule |
| IV 201–207 | All exact classifier input maps, transforms, and normalizations | D 34–39 |
| IV 133–134 / VI 137–139 | Lz = 1, delta = 10^-2, one fixed random sign vector per terminal per block | D 41–43 |
| VI 139 | Pooled variance floor 10^-4 | D 43–44 |
| V 131–151 | Full stopping-rule logic and residual equation | D 48–69 |
| VI 133–135 | I_min = 60, I_max = 600, relative-change tolerance 5 x 10^-4 | D 71–72; still summarized in VI 134–135 |
| VI 139–141 | Activity-change 10^-3, site-parameter 0.1, activity-history 10^-3 | D 72–74 |
| VI 141 | zeta = 0.2, Ls = 5, Ld = 10 | D 74 |

## Concision assessment

Appendix D is proportionate: three short subsections, two display equations, and the actual implementation choices removed from the main argument. It does not repeat Appendix C's evaluation bookkeeping or add derivation, caveats, or new algorithm behavior. No further substantive cuts are needed.

Two optional micro-cuts remain, neither required for correctness or readability:

- D 30–31, “the classifier checkpoint is selected by validation”, repeats VI 111. This clause can be removed while retaining the selected epoch 90 and the pointer to VI.
- D 39, “It produces one logit per terminal”, repeats IV's classifier description. It can be removed from D, whose purpose here is exact input transformations.

Keep the D 71–74 parameter paragraph despite partial overlap with VI's broad iteration settings: it completes the stopping specification in one location. Keep the fixed random direction and full feature transformations; these are the content being relocated, not defensive repetition.

## Verification evidence

- Full original stopping text versus D, ignoring only whitespace: PASS.
- Original stopping display equation versus D: exact text PASS.
- Full original classifier input/output description versus D, ignoring only whitespace: PASS.
- 13 parameter/operation presence checks in the appropriate appendix context: PASS.
- Canonical fixed-variance and complete-map differentiation statements: PASS.

Source hashes at review time:

- `04_generative_priors.tex`: `685a92878f3fac68ce550bd4bb5a7c574bbde4bb3b06b0ef063a2908e4250f03`
- `05_overall_algorithm.tex`: `6b509f142ac2d11ad5e9a0e0d5777426d2b110c87808e5fdee44131e7072125d`
- `06_simulation_results.tex`: `c71e8eb09a58415a9a8e57e5e263cdd863c1a626f59686affc1012adda7ca21f`
- `appendix_implementation.tex`: `58d6c0ad11367a271204c99521704ec21b307416fc610c7e9163d4efc631aa36`

## Rendered visual review

Actual visual inspection was performed with `view_image` on all three supplied page renders, after the canonical compilation. This is a visual check of those images, not an inferred layout result.

| Render | Checked content | Result |
|---|---|---|
| `final-06.png` | IV equations (32)–(39), covariance matrix, preconditioning expressions, derivative trace, classifier equations, column transitions | PASS: all equations and equation numbers fit within their columns; no clipping, overlap, missing text, or abnormal blank areas. The offline-training heading at the foot of the right column is followed by text. |
| `final-07.png` | End of IV, V schedule text, Algorithm 1, damping and fallback equations (40)–(42), stopping summary, complexity heading | PASS: the complete algorithm box, title, inputs/outputs, all nine numbered items, and bottom rule are visible. Wrapped lines stay within the box; no equation/body overlap or abnormal blank areas. |
| `final-08.png` | Complexity equations (43)–(44), VI transition, simulation table, pilot/SNR/covariance expressions (45)–(47), training settings | PASS: table labels and values remain inside the table; display equations, equation numbers, and column boundaries are clear. No clipping, overlap, or unexpected whitespace. |

No visual corrections are recommended for these three pages.

Rendered image hashes:

- `final-06.png`: `46ce21eab8576f1a5f0cec1b05998f25380b433683cb992c9c41ea011483d031`
- `final-07.png`: `d6ca47cf3574ed94820a2ae59c6f95f8239fdd52c899fb3784fb416072496f96`
- `final-08.png`: `a8742d51157c0de7cdb53d3763841a12a103e42b6448ef9a7f4ec0139f88b029`
