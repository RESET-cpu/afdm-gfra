"""The existing fixed 2000-scene registry and physical defaults."""
from project import ROOT
REGISTRY = ROOT / 'result/lstmp_v3_shared2000_20261021'

COUNT = 2000


BASE_SEED = 202610219100001


PANEL_ID = 'lstmp_v3_shared2000_20261021'


DEFAULT = dict(users=40, frames=16, activity_probability=.1, snr_db=0,
               channel_model='D', pilot='dft')


def condition_key(parameters):
    """An input key is independent of experiment name and receiver method."""
    p = dict(DEFAULT, **parameters)
    return (f"K{int(p['users'])}_Q{int(p['frames'])}_p{p['activity_probability']:g}"
            f"_snr{p['snr_db']:g}_{p['channel_model']}_{p['pilot']}")


def scene_rows():
    return [dict(index=i, scene_id=f'scene{i:04d}', seed=BASE_SEED+i)
            for i in range(COUNT)]
