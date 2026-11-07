"""Launch one of the GNN-ASPL training recipes."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from afdm_jadcedd.experiment.training.gnn.cli import main

if __name__ == "__main__":
    main()
