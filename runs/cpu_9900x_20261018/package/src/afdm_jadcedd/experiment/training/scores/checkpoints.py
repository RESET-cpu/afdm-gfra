"""Explicitly labelled population-RMS or unit-sample-power score serialization."""
from dataclasses import asdict
from pathlib import Path
import torch


def save_direct_checkpoint(path, model, *, scale, metadata, normalization='population_rms'):
    if normalization not in ('population_rms', 'per_sample_power'):
        raise ValueError('unknown score normalization')
    unit_schemas = ('afdm-channel-unit-power-score-v1',)
    if normalization == 'per_sample_power' and getattr(model, 'checkpoint_schema', '') not in unit_schemas:
        raise ValueError('unit-power scores require their explicit checkpoint schema')
    if getattr(model, 'checkpoint_schema', '') in unit_schemas and normalization != 'per_sample_power':
        raise ValueError('unit-power score schema requires per-sample normalization')
    path = Path(path)
    temporary = path.with_suffix('.tmp')
    torch.save(dict(schema=getattr(model, 'checkpoint_schema', 'afdm-cai-direct-score-v1'), order=model.order,
        config=asdict(model.config), global_complex_rms=float(scale), metadata=metadata,
        normalization=normalization,
        state_dict={key: value.detach().cpu() for key, value in model.state_dict().items()}), temporary)
    temporary.replace(path)
