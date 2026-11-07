"""Public entry for organized research code and explicitly frozen batches."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))
from experiment.commands import main

if __name__ == '__main__':
    raise SystemExit(main())
