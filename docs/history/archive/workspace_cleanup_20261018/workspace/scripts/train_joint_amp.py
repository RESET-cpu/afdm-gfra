"""Train the independent complete-user joint score and activity network."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from afdm_jadcedd.algorithm.joint_amp.training import main


if __name__ == '__main__':
    main()
