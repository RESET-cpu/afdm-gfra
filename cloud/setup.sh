#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export MPLBACKEND=Agg
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
python -c 'import sys; assert sys.version_info >= (3,10), "Python 3.10+ required"'
if ! git lfs version >/dev/null 2>&1; then
  echo 'Install Git LFS in the environment, then rerun cloud/setup.sh.' >&2
  exit 1
fi
git lfs install --local
git lfs pull
python -m pip install 'torch==2.7.1' --index-url https://download.pytorch.org/whl/cpu
python -m pip install 'numpy==2.2.1' 'scipy==1.15.1' 'pytest>=7.4,<9' -e .
python cloud/check.py
