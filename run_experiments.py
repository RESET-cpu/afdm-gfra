"""Public entry for the white-network mainline and explicit historical replay."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))
from evaluation import suite
from evaluation.cli import main as suite_main

# New default plans must never select a previously frozen colored/DU batch.
suite.DEFAULT_OUTPUT = Path(__file__).resolve().parent / 'result/white_mainline_default_20261107'


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == 'white_followup':
        from evaluation.white_followup_20261107.run import main as followup
        return followup(argv[1:])
    return suite_main(argv)

if __name__ == '__main__':
    raise SystemExit(main())
