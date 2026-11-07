"""Explicit union of the formal one-variable sweeps; no Cartesian product."""

SNR_VALUES = [-4, -2, 0, 2, 4, 6]
USERS = [20, 40, 60, 80, 100]
FRAMES = [8, 16, 24, 32, 40, 48]
ACTIVITY_PROBABILITIES = [.05, .1, .15, .2, .25]
TRAIN_PER_CONDITION = 250
VALIDATION_PER_CONDITION = 100
MAXIMUM_DEPTH = 10
EPOCHS_PER_DEPTH = 3


def conditions():
    default = dict(users=40, frames=16, activity_probability=.1, snr_db=0)
    result = []
    seen = set()
    for field, values in (
        ('snr_db', SNR_VALUES),
        ('users', USERS),
        ('frames', FRAMES),
        ('activity_probability', ACTIVITY_PROBABILITIES),
    ):
        for value in values:
            row = dict(default, **{field: value})
            key = tuple(sorted(row.items()))
            if key not in seen:
                result.append(row)
                seen.add(key)
    assert len(result) == 19
    return result


def planned_updates():
    return len(conditions()) * TRAIN_PER_CONDITION * MAXIMUM_DEPTH * EPOCHS_PER_DEPTH
