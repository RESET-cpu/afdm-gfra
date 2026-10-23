"""Direct AWGN channel observations passed to the selected baseline kernels."""
from pathlib import Path
import os
import sys
for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ[key] = '1'
RUNTIME = Path(__file__).resolve().parent / 'runtime'
sys.path.insert(0, str(RUNTIME / 'src'))
import json
import numpy as np
import torch
from threadpoolctl import threadpool_limits
threadpool_limits(1)
torch.set_num_threads(1)
from afdm_jadcedd.system.dictionary import AFDMGrid
from afdm_jadcedd.system.observation import ReceiverInput
from afdm_jadcedd.algorithm.baselines.somp import solve_somp
from afdm_jadcedd.algorithm.baselines.gamp_sbl_mmv import MMVControls, solve_mmv
from afdm_jadcedd.algorithm.baselines.gnn_aspl import GNNASPLReceiver
from afdm_jadcedd.algorithm.baselines.offgrid import sbl


class Denoisers:
    def __init__(self, scale):
        self.scale = scale
        self.cfg = json.loads((RUNTIME / 'configs/baselines.json').read_text())
        self.off = json.loads((RUNTIME / 'configs/offgrid_baselines.json').read_text())
        self.operator = np.eye(16, dtype=complex)[:, None, :]
        self.grid = AFDMGrid.from_operator(self.operator, **self.cfg['dictionary'])
        self.design = np.ascontiguousarray(self.grid.design * self.grid.norms[None, :])
        self.cfg['methods']['gnn_aspl_ding2026']['checkpoint_path'] = str(RUNTIME / 'models/gnn/checkpoint.pt')
        self.gnn = GNNASPLReceiver(self.cfg)
        self.settings = sbl.Settings(**self.off['methods']['offgrid_sbl']['solver'])

    def inputs(self, query, variance):
        # H[antenna,output,input] -> Y[input,antenna,output]. No linear mixing.
        # Restore physical coordinates for the training-fitted GNN slab variance.
        observation = np.ascontiguousarray(query.transpose(2, 0, 1) * self.scale)
        return ReceiverInput(observation, self.operator, variance * self.scale**2)

    def infer(self, method, query, variance):
        inputs = self.inputs(query, variance)
        y = self.grid.stack(inputs.observation)
        if method == 'somp':
            result = solve_somp(self.grid.design, y, inputs.noise_variance,
                                **self.cfg['methods']['somp']['solver'])
            estimate = self.grid.reconstruct(result['mean'])[0]
            status = result['status']
        elif method == 'gamp':
            controls = MMVControls(**self.cfg['methods']['gamp_sbl_mmv']['solver'],
                noise_shape=1+y.size, noise_rate=y.size*inputs.noise_variance)
            result = solve_mmv(self.design, y, controls)
            estimate = self.grid.reconstruct(result['mean']*self.grid.norms[:, None])[0]
            status = result['stopping_reason']
        elif method == 'gnn':
            with torch.no_grad():
                result = self.gnn.model(torch.as_tensor(self.design), torch.as_tensor(y),
                    inputs.noise_variance, 1, collect_trace=False)
            estimate = self.grid.reconstruct(result['mean'].cpu().numpy()*self.grid.norms[:, None])[0]
            status = 'fixed_unfolding_depth'
        elif method == 'offgrid_sbl':
            result = sbl.solve(inputs, self.settings)
            estimate = result['estimate'][0]
            status = result['stopping_reason']
        else:
            raise ValueError(method)
        estimate = estimate / self.scale
        assert estimate.shape == query.shape and np.isfinite(estimate).all()
        details = dict(iterations=result['iterations'], stopping_reason=status)
        for key in ('noise_variance', 'linearization_relative_error', 'screened_columns'):
            if key in result:
                details[key] = result[key]
        return estimate, details
