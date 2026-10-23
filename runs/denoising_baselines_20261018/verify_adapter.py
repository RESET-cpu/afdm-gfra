"""Compare the direct-AWGN adapter with unchanged native receiver entry points."""
from copy import deepcopy
import warnings
from run import OUT, INPUT, RUN, read, save, sha, np, Denoisers
from afdm_jadcedd.algorithm.baselines.receiver import BaselineReceiver
from afdm_jadcedd.algorithm.baselines.offgrid.receiver import OffGridReceiver


def main():
    checks = []
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        engine = Denoisers(read(INPUT / 'PLAN.json')['experiment']['scale'])
        cfg = read(RUN / 'runtime/configs/baselines.json')
        native = {method: BaselineReceiver(deepcopy(cfg), method) for method in ['somp', 'gamp', 'gnn']}
        native['offgrid_sbl'] = OffGridReceiver(engine.off, 'offgrid_sbl')
        for condition in [0, 3, 5]:
            folder = INPUT / f'scene000/condition{condition:02}'
            variance = read(folder / 'INPUT.json')['variance']
            with np.load(folder / 'query.npz', allow_pickle=False) as data:
                query = data['query'][0]
            for method, receiver in native.items():
                first, details = engine.infer(method, query, variance)
                arrays, record = receiver.infer(engine.inputs(query, variance))
                second = arrays['estimate'][0] / engine.scale
                relative = float(np.linalg.norm(first-second)/max(np.linalg.norm(second), 1e-30))
                np.testing.assert_allclose(first, second, rtol=1e-11, atol=1e-12)
                assert details['iterations'] == record['iterations']
                assert details['stopping_reason'] == record['stopping_reason']
                checks.append(dict(method=method, condition=condition, variance=variance,
                    maximum_absolute_difference=float(abs(first-second).max()), relative_l2_difference=relative,
                    iterations_equal=True, stopping_reason_equal=True))
    save(OUT / 'ADAPTER_VERIFICATION.json', dict(status='PASS', checks=checks,
        script_sha256=sha(RUN / 'verify_adapter.py'),
        source='Frozen native BaselineReceiver and OffGridReceiver entry points.',
        warnings=sorted(set(str(w.message) for w in caught))))
    print('PASS: 12 native receiver comparisons; channel estimates, iteration counts and stopping states agree.')


if __name__ == '__main__':
    main()
