"""Coalesce GPU work without changing the CPU training-query random stream."""
import numpy as np
import torch
from training.scores.direct_objectives import direct_first_loss


def execution_batches(data, chosen, rng, recipe, make_batch, *, draw_size, execution_size):
    if execution_size < draw_size or execution_size % draw_size:
        raise ValueError('Execution batch must be a positive multiple of the original draw batch')
    for offset in range(0, len(chosen), execution_size):
        selected = chosen[offset:offset + execution_size]
        parts = [make_batch(np.asarray(data[selected[i:i + draw_size]]), rng, recipe)
                 for i in range(0, len(selected), draw_size)]
        yield tuple(np.concatenate([part[j] for part in parts]) for j in range(4))


def first_backward(model, data, chosen, rng, recipe, make_batch, *, device, draw_size, execution_size):
    """The optimizer still takes one update over exactly the original chosen rows."""
    value_sum = 0.
    for arrays in execution_batches(data, chosen, rng, recipe, make_batch,
                                   draw_size=draw_size, execution_size=execution_size):
        h, r, v, labels = [torch.as_tensor(x, device=device) for x in arrays]
        loss = direct_first_loss(model(r, labels), r, h, v)
        value = float(loss.detach().cpu())
        if not np.isfinite(value):
            raise FloatingPointError('Nonfinite DSM loss; saved checkpoint preserved')
        (loss * len(h) / len(chosen)).backward()
        value_sum += value * len(h)
    return value_sum
