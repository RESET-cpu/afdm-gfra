"""User-count paper figure: approved frozen renderer, input/output overrides only."""
from pathlib import Path
import runpy


if __name__ == '__main__':
    runpy.run_path(str(Path(__file__).with_name('frozen_user_count_20261026') / 'render.py'), run_name='__main__')
