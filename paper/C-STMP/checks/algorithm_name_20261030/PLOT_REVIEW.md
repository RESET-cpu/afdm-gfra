# Plot display-name revision — 2026-10-30

The six staged PDF figures replace the C-STMP legend label with the approved
name **GP-CCD-MP-DRE**. The baseline STMP label, all method identifiers, source
JSON files, curve colors, markers, line styles, numerical values, and figure
filenames remain unchanged. No training or receiver evaluation was run.

`render_named_figures.py` replays the four NMSE-only figures from the previous
audited renderer and the SNR/pilot NMSE+AER figures with the read-only frozen
plot engine. The style label override exists only in the rendering process.

All 493 plotted x/y pairs were checked against the saved data without tolerance:
421 NMSE values and 72 AER values. Each source row is plotted once per retained
metric; the four NMSE-only figures' styles and data also match the preceding
revision exactly. Ten frozen engine files were verified before and after
rendering. SNR and pilot source data contain no zero AER values, and their
existing separate-zero-strip display policy is retained.

The figure sizes stay 3.5 × 2.65 inches for convergence, user count, and activity
probability; 7 × 2.6 inches for the four-channel comparison; and 3.5 × 2.2 inches
for SNR and pilot frames. The larger label fits existing legend placements.
Constrained-layout panel positions for SNR and pilot frames are settled and
frozen before PDF/PNG export to avoid backend-dependent movement of the central
axis labels. No axis limits or curve points were altered.

Visual review completed for all six exported PDFs after rendering them through
Poppler. No clipped text, panel overlap, legend truncation, or curve-obscuring
legend placement was found. All six PDFs contain GP-CCD-MP-DRE and STMP, contain
no C-STMP display label, and have the intended dimensions (1e-10-inch tolerance
for decimal PDF MediaBox conversion). `RENDER_VALIDATION.json` and
`PLOT_PDF_VALIDATION.json` record the checks. The staged PDFs are ready for the
parent agent to publish into the canonical manuscript figure directory.
