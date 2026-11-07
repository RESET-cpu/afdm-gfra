# Running the source and reproducing results

This is a research source snapshot. Its current proposed method is **GP-MP**;
the receiver with estimated phase is **GP-MP-EP**. The paper remains under
`paper/C-STMP`. Copyright is retained; see [RIGHTS.md](RIGHTS.md).

The source does not include trained weights, training arrays, or per-scene
predictions. A small CPU example and the default tests work without them.
Running the example does not reproduce a GP-MP performance curve.

## Download the source and prepare dependencies

Download the repository ZIP from GitHub and extract it, or clone the repository. Use Python 3.11 or newer in a new environment. The measured reference setup
is Python 3.13.1 on Windows 11; exact dependency and hardware versions are in
[ENVIRONMENT.json](ENVIRONMENT.json). Other operating systems and Python
versions have not been validated by this preparation run.

```text
python -m venv .venv
```

Activate it with `.venv\Scripts\Activate.ps1` in PowerShell, or
`source .venv/bin/activate` in a POSIX shell, then run from the repository root:

```text
python -m pip install -r requirements.txt
python run_experiments.py list
python run_experiments.py demo --output result/demo_first
python -m pytest -q
```

`demo_first` must be a new or empty directory. The example saves
`SUMMARY.json` and `channel.png`. It uses one synthetic two-device, 32-frame,
four-antenna AFDM scene and known-phase least squares. It loads no weights,
does not run an activity detector, and is not a manuscript result. The
default seed is `2026110701`; the measured reference NMSE is about
`-29.290865 dB`. This is a setup check, not a performance target.

All commands run directly from the extracted repository through
`python run_experiments.py`. Keep `src/`, the configurations and the root script
together; paths are resolved relative to the script directory.

The default test set is `src/tests/public`: mathematical identities, channel
reconstruction, scoring, current configuration contracts, portable asset
paths, and command behavior. It does not require local research assets.
[Research tests](src/tests/README.md) remain available separately, including
historical checks whose assumptions no longer match the current mainline.

For comparison with the measured environment, use the version constraints:

```text
python -m pip install -c requirements-tested.txt -r requirements.txt
```

These constraints cover direct dependencies, not a universal lock file. The
recorded GPU run used PyTorch `2.7.1+cu128` on an RTX 5080. Select a PyTorch
build appropriate to the intended device; the CPU example needs no CUDA.
Neither dependency installation nor a fresh full training run is certified
across all platforms by this snapshot.

## Check the assets before inference

```text
python run_experiments.py assets --scope gp-mp
python run_experiments.py assets --scope gp-mp --verify --report result/asset_check.json
```

The first command checks file presence. `--verify` streams SHA-256 checks
without loading checkpoints. Exit code 1 means missing or changed assets,
not that an experiment ran. The expected paths, sizes, and hashes are in
[assets.json](src/configs/release/assets.json). No command downloads assets.

The two current weights are identified in [FINAL.json](FINAL.json):

- Conditional mean: `result/channel_denoising/data/white_preconditioned_matched_20261104/first_best.pt`.
- Activity classifier: `result/snr_comparison/data/white_preconditioned_classifier_matched_20261104/evidence_best.pt`.

The binding also needs its prior definition, training specifications,
completion/history records and scene registry. The inventory lists these
alongside the weights. Restore the same directory structure from an
author-supplied, authorized asset copy and verify the hashes. There is no
public download endpoint in this snapshot. Do not substitute arbitrary
weights and label the output a reproduction of the frozen manuscript.
Comparator weights and calibration records are additional dependencies;
`--scope gp-mp` does not certify every baseline.

The working receiver resolves the known old `D:\afdm-gfra\...` prefix to the
current checkout. Frozen JSON files are not rewritten. Other external paths
are not silently redirected. Run the inventory command from the extracted repository root.

## Run a new diagnostic with restored GP-MP assets

The following commands are for the reader to execute after asset validation.
They were not used to start a formal experiment during release preparation.
They create a new one-scene, one-condition diagnostic using independent
smoke-test seeds, not the manuscript's scene panel:

```text
python run_experiments.py snr_comparison plan --config src/configs/release/gp_mp_diagnostic.json --smoke --device cpu --output result/gp_mp_diagnostic
python run_experiments.py snr_comparison inspect --output result/gp_mp_diagnostic
python run_experiments.py snr_comparison run --output result/gp_mp_diagnostic
```

Use a new output directory when changing settings. Planning records the
configuration and source/asset hashes; the run command checks them before
execution. Wall time for this full receiver diagnostic has not been measured
in the publication preparation run. The measured weight-free example and
test timings are recorded in the validation report.

## Reproduce figures and understand their status

Figure-by-figure sources, commands, sample budgets and current replacement
status are listed in [the manuscript reproduction map](paper/C-STMP/docs/REPRODUCTION.md).
Saved-aggregate plotting is distinct from rerunning receivers and retraining.
The latter two require assets excluded from the source snapshot.

```text
python run_experiments.py plot --list
python run_experiments.py assets --scope figures
python run_experiments.py plot --figures snr_comparison --output result/snr_figure_preview
```

`plot --check` renders into a temporary directory and compares against the
retained manuscript PDFs; it does not replace them. Exact pixel comparison
requires the recorded plotting versions and Times New Roman fonts. The first
three method figures additionally need the source PDFs, compiled labels and
channel example described in the reproduction map. PyMuPDF is listed in
`requirements.txt`; no personal cache directory is used by the working plotter.

## Training and the submission snapshot

The white denoiser and classifier recipes are retained at
`src/configs/training/white_preconditioned_matched_20261104.json` and
`src/configs/training/white_activity_matched_20261104.json`. Their original
entry points are `training.colored_preconditioned_20261024.formal` and
`training.colored_activity_20261025.run`; the historical module names do not
change the white-noise setting in these recipes. Both expose `--help` and
`prepare`, `preflight`, `train` stages.

These are frozen research recipes: they require the original 50,000/5,000
channel banks, initialization and provenance records. The current classifier
recipe also checks protected historical-run records. They are not a tested
fresh-install, from-scratch training tutorial. The generic data-bank builder
is `training.organized.stmp.data.build_bank`; its source record differs from
the original generator record, so a newly generated bank must be validated
and rebound in a separate candidate recipe. This preparation does not claim
that retraining regenerates the original weight hashes.

The agreed white-network replacements are still in progress. The current
code snapshot is suitable for review; an immutable submission tag should be
created after the final figure/model/configuration set is adopted. The
preparation does not resume the failed pilot-frame sweep or declare the
remaining sweeps complete.
