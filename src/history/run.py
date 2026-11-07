"""Run the AFDM JADCE mainline from this checkout."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'src'))
from afdm_jadcedd.experiment.run import main
if __name__=='__main__':raise SystemExit(main())
