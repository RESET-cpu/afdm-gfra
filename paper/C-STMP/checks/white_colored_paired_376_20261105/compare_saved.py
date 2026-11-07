"""Recheck a fixed 376-scene completed prefix without running inference."""
from pathlib import Path
import importlib.util

OUT = Path(__file__).resolve().parent
SOURCE = OUT.parent / 'white_mainline_revision_20261105' / 'compare_saved.py'
spec = importlib.util.spec_from_file_location('paired_audit', SOURCE)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
audit.OUT = OUT
audit.N = 376
audit.SEED = 202611051800

if __name__ == '__main__':
    audit.audit(SOURCE)
    audit.audit(Path(__file__))
    audit.main()
