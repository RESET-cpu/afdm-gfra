# Running the code and reproducing results

The repository is public. The current proposed receivers are **GP-MP** and **GP-MP-EP** (estimated phase). Run the source through `python run_experiments.py` from the repository root. The paper is in [paper/](paper/README.md); licensing is described in [RIGHTS.md](RIGHTS.md).

## Download and dependencies

Install [Git LFS](https://git-lfs.com/), then download the source and weights:

```text
git lfs install
git clone https://github.com/RESET-cpu/afdm-gfra.git
cd afdm-gfra
git lfs pull
```

ZIP archives may contain LFS pointers instead of model bytes. The asset checker identifies these as `LFS_POINTER`; the clone procedure above retrieves the actual files.

Use Python 3.11 or newer. The tested environment is Python 3.13.1 on Windows 11; exact versions are recorded in [ENVIRONMENT.json](ENVIRONMENT.json). Other platforms and a fresh dependency installation have not been independently validated. A virtual environment is optional:

```text
python -m venv .venv
```

Activate it with `.venv\Scripts\Activate.ps1` in PowerShell or `source .venv/bin/activate` in a POSIX shell. Install dependencies:

```text
python -m pip install -r requirements.txt
```

[requirements-tested.txt](requirements-tested.txt) records tested direct dependency versions and can be supplied with `-c requirements-tested.txt`. For GPU execution, choose a PyTorch build compatible with the GPU; the recorded reference uses PyTorch 2.7.1+cu128 on an RTX 5080.

## Check the setup

```text
python run_experiments.py list
python run_experiments.py demo --output result/demo_first
python -m pytest -q
```

Use a new output directory. The demo generates a synthetic two-device, 32-frame, four-antenna AFDM scene and runs known-phase least squares. It saves `SUMMARY.json` and `channel.png`, loads no weights, and does not evaluate GP-MP or activity detection. The default tests also need no weights; their scope is described in [src/tests/README.md](src/tests/README.md).

## Run GP-MP with the published weights

Eight model assets (about 404 MB) are distributed through Git LFS: the GP-MP and STMP networks, GNN checkpoint, classifier initialization and shared STMP phase calibration. Their exact paths and SHA-256 values are in [weights.json](src/configs/release/weights.json). [FINAL.json](FINAL.json) identifies the current GP-MP binding; the [model catalog](src/configs/organized/models.json) identifies STMP.

Validate the downloaded assets:

```text
python run_experiments.py assets --scope models --verify
python run_experiments.py assets --scope gp-mp --verify
```

The second command also verifies the required provenance records and scene registry. Exit code 1 indicates a missing, changed or pointer-only asset. These commands check files; they do not download them.

Run one GP-MP diagnostic with independent diagnostic seeds:

```text
python run_experiments.py snr_comparison plan --config src/configs/release/gp_mp_diagnostic.json --smoke --device cpu --output result/gp_mp_diagnostic
python run_experiments.py snr_comparison inspect --output result/gp_mp_diagnostic
python run_experiments.py snr_comparison run --output result/gp_mp_diagnostic
```

This exact workflow was completed in an independently downloaded source tree with the published weights and an existing validated Python environment: one scene, one SNR condition, 60 receiver iterations, saved scores and plots. Receiver inference took about 49 seconds on that CPU setup, excluding warmup. This verifies the workflow, not a manuscript performance curve or a universal runtime target.

For a larger or different experiment, create a new plan and output directory as described in [the experiment guide](src/experiment/README.md). A run verifies its saved configuration and asset hashes before execution.

## Figures and numerical reproduction

```text
python run_experiments.py plot --list
python run_experiments.py plot --figures snr_comparison --output result/snr_figure_preview
```

The [manuscript reproduction map](paper/docs/REPRODUCTION.md) identifies each figure's source and adopted result. Rendering saved aggregates and recomputing receiver outputs are separate operations. `plot --check` compares temporary renders with retained manuscript figures. Exact pixel matching needs the recorded plotting versions and Times New Roman fonts.

The first three method figures also require their configured source PDFs, compiled equation labels and channel example. Downloaded third-party papers and the raw channel-example array are not distributed; the finished figures are included.

## Distributed and local assets

| Included in this repository | Kept in the full local research workspace |
|---|---|
| Current source, configurations and tests | Original training/validation channel banks |
| Paper source, PDFs and finished figures | Per-scene predictions, traces and run logs |
| Selected plans, aggregate results and provenance | Historical candidate weights and some initialization banks |
| Eight selected model assets through Git LFS | Third-party paper PDFs and the raw figure-3 example |

[GITHUB_MANIFEST.json](GITHUB_MANIFEST.json) lists published file sizes and hashes, excluding itself. LFS entries describe original binary bytes. Published status records are snapshots; local `STATUS.json` files track active experiments. The manifest describes the current tree, while older Git commits retain historical content.

New inference scenes can be generated by the code. Exact replay of a saved historical batch needs its original inputs and bindings. The explicitly isolated [frozen source archive](archive/frozen_reproduction_20261107/README.md) and [migration validation](archive/code_cleanup_20261107/README.md) explain source identity and path relocation. Do not rewrite a frozen plan to bypass its checks.

## Training

Training entry points and data requirements are documented in [src/training/README.md](src/training/README.md):

```text
python run_experiments.py train gp-mp-first --help
python run_experiments.py train gp-mp-activity --help
python run_experiments.py train stmp --help
python run_experiments.py train gnn --help
```

Retraining requires channel banks, initialization and provenance records beyond the selected inference assets. New generated banks require a separately recorded recipe. No full retraining or complete manuscript recomputation is claimed by the download check. Current adoption and pending studies are tracked in [the result index](result/README.md).
