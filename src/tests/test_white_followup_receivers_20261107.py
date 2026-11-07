"""CPU-only integrity and dispatch boundary checks for the follow-up stages."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch, Mock

import numpy as np

from evaluation.white_followup_20261107 import receivers as r


class FollowupChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_root = r.ROOT/'result/tmp/white_followup_tests_20261107'
        cls.temp_root.mkdir(parents=True, exist_ok=True)

    def test_public_main_dispatches_explicit_arguments(self):
        with patch.object(r, 'prepare') as prepare:
            self.assertEqual(r.main(['prepare', '--stage', 'pilot_frames']), 0)
            prepare.assert_called_once_with('pilot_frames')

    def test_asset_hash_labels_are_not_paths_but_missing_files_fail(self):
        with tempfile.TemporaryDirectory(dir=self.temp_root) as temp:
            p = Path(temp)/'record.json'
            p.write_text(json.dumps({'initialization':'random','initialization_sha256':'a'*64}))
            assets = {}
            r.add_assets(assets, p)
            self.assertIn(str(p.relative_to(r.ROOT)), assets)
            p.write_text(json.dumps({'weight':'missing.pt','weight_sha256':'b'*64}))
            with self.assertRaises(FileNotFoundError):r.add_assets({}, p)

    def test_launcher_ancestry_is_not_another_execution(self):
        cmd = ['python.exe', '-m', r.MODULE, 'coordinate', '--stage', 'pilot_frames']
        def process(pid, created, parent=None):
            p = Mock(pid=pid)
            p.create_time.return_value = created
            p.cmdline.return_value = cmd
            p.exe.return_value = 'C:/Python/python.exe'
            p.parent.return_value = parent
            p.info = dict(pid=pid, create_time=created, cmdline=cmd)
            return p
        launcher = process(10, 1.)
        current = process(11, 2., launcher)
        foreign = process(12, 3.)
        with patch.object(r.os, 'getpid', return_value=11), patch.object(r.psutil, 'Process', side_effect=lambda pid: {10:launcher,11:current}[pid]):
            with patch.object(r.psutil, 'process_iter', return_value=[launcher,current]):
                r.no_other_execution(r.stage_folder('pilot_frames'))
            with patch.object(r.psutil, 'process_iter', return_value=[launcher,current,foreign]):
                with self.assertRaises(RuntimeError):r.no_other_execution(r.stage_folder('pilot_frames'))
            # PID equality alone cannot authorize an unrelated replacement.
            recycled = process(10, 5.)
            with patch.object(r.psutil, 'process_iter', return_value=[recycled,current]):
                with self.assertRaises(RuntimeError):r.no_other_execution(r.stage_folder('pilot_frames'))

    def test_import_does_not_initialize_torch(self):
        program = ('import sys; import evaluation.white_followup_20261107.receivers; '
                   'assert "torch" not in sys.modules; assert "algorithm.GP_MP.receiver" not in sys.modules')
        subprocess.run([sys.executable,'-B','-c',program],check=True)

    def test_coverage_rejects_duplicate_missing_and_changed_condition(self):
        conditions = [dict(users=40),dict(users=80)]
        cases = [dict(scene=s,index=i,parameters=c) for s in range(500) for i,c in enumerate(conditions)]
        r.validate_coverage(cases,conditions)
        for bad in (cases[:-1],cases+[cases[0]],list(reversed(cases))):
            with self.assertRaises(ValueError):r.validate_coverage(bad,conditions)
        bad=deepcopy(cases);bad[0]['parameters']['users']=1
        with self.assertRaises(ValueError):r.validate_coverage(bad,conditions)

    def test_reuse_requires_identical_saved_input_hashes(self):
        with tempfile.TemporaryDirectory(dir=self.temp_root) as temp:
            home=Path(temp);(home/'results').mkdir()
            pointer=home/'results/scene0000_condition02.json';pointer.write_text('{}')
            case=dict(scene=0,index=1,ready='D:\\data\\READY.json',ready_sha256='a',files={'raw.npz':'x'})
            ref=dict(case,index=2,ready='d:/data/READY.json')
            tasks=r.make_tasks([case],['GP_MP'],{'GP_MP':[ref]},{'GP_MP':home})
            self.assertEqual(tasks[0]['reuse']['index'],2)
            bad=dict(ref,files={'raw.npz':'changed'})
            with self.assertRaises(ValueError):
                r.make_tasks([case],['GP_MP'],{'GP_MP':[bad]},{'GP_MP':home})
            tasks=r.make_tasks([dict(case,ready='D:/other/READY.json')],['GP_MP'],{'GP_MP':[ref]},{'GP_MP':home})
            self.assertNotIn('reuse',tasks[0])

    def test_sbl_reuse_uses_correct_budget(self):
        with tempfile.TemporaryDirectory(dir=self.temp_root) as temp:
            home=Path(temp);(home/'results').mkdir()
            (home/'results/budget25_scene0000_condition02.json').write_text('{}')
            c=dict(scene=0,index=2,ready='D:/data/READY.json',ready_sha256='a',files={})
            t=r.make_tasks([c],['offgrid25'],{'offgrid25':[c]},{'offgrid25':home})[0]
            self.assertIn('budget25_',t['reuse']['pointer'])

    def test_mutable_io_retry_is_bounded_and_does_not_hide_bad_json(self):
        with patch.object(r,'read_json',side_effect=[PermissionError(),{'stage':'READY'}]) as read, patch.object(r.time,'sleep') as sleep:
            self.assertEqual(r.state_read('STATE.json')['stage'],'READY')
            self.assertEqual(read.call_count,2);sleep.assert_called_once_with(.05)
        with patch.object(r,'read_json',side_effect=PermissionError()) as read, patch.object(r.time,'sleep'):
            with self.assertRaises(PermissionError):r.state_read('STATE.json')
            self.assertEqual(read.call_count,11)
        with patch.object(r,'read_json',side_effect=PermissionError()) as read, patch.object(r.time,'sleep'):
            with self.assertRaises(PermissionError):r.state_read('RESULT.json')
            self.assertEqual(read.call_count,1)
        with patch.object(r,'read_json',side_effect=json.JSONDecodeError('bad','x',0)) as read:
            with self.assertRaises(json.JSONDecodeError):r.state_read('STATE.json')
            self.assertEqual(read.call_count,1)

    def test_phase_input_reads_raw_and_never_public_operator(self):
        with tempfile.TemporaryDirectory(dir=self.temp_root) as temp:
            p=Path(temp)
            np.savez(p/'raw.npz',y=np.ones((2,3,16),complex),pilot=np.ones((2,4,16),complex),rho=.1)
            # Deliberately invalid public file proves it is never opened for EP.
            (p/'public.npz').write_bytes(b'not a numpy file')
            value=r.receiver_input('GP_MP_EP',p)
            self.assertEqual(value.activity_prior,.1)
            self.assertFalse(hasattr(value,'operator'))

    def example(self,ep=False):
        configuration=dict(ep=dict(damping=.4))
        plan=dict(receiver_configuration=configuration,configuration_snapshots={'GP_MP_EP':{'fixed':'binding'}})
        prediction=dict(estimate=np.zeros((1,16,16,16),complex),probabilities=np.array([.6]),activity_decision=np.array([True]))
        record=dict(configuration=configuration,denoiser_training_noise='white Gaussian',receiver_truth_used=False,
                    noise_truth_used=False,iterations=60,phase_mode='known',oracle_phase_supplied=True)
        if ep:
            prediction.update(phase=np.ones(2),initial_phase=np.ones(2),phase_slopes=np.zeros(2),initial_phase_slopes=np.zeros(2))
            record.update(frontend_binding={'fixed':'binding'},oracle_phase_supplied=False,phase_mode='estimated',
                          supplied_phase_operator_used=False,initializer_gain_or_power_forwarded=False,
                          phase_updates_inside_receiver=0,phase_initialization={'truth_used_in_inference':False},
                          input_fields=['observation','pilot','activity_prior'])
        return prediction,record,plan,dict(parameters=dict(users=1))

    def test_uniform_beta_and_known_phase_truth_boundary(self):
        pred,record,plan,case=self.example()
        r.validate_numerics('GP_MP',pred,record,plan,case)
        changed=deepcopy(record);changed['configuration']['ep']['damping']=.2
        with self.assertRaises(ValueError):r.validate_numerics('GP_MP',pred,changed,plan,case)
        changed=deepcopy(record);changed['receiver_truth_used']=True
        with self.assertRaises(ValueError):r.validate_numerics('GP_MP',pred,changed,plan,case)

    def test_estimated_phase_rejects_oracle_and_internal_updates(self):
        pred,record,plan,case=self.example(True)
        r.validate_numerics('GP_MP_EP',pred,record,plan,case)
        for key,value in [('oracle_phase_supplied',True),('phase_updates_inside_receiver',1),('input_fields',['observation','operator'])]:
            changed=deepcopy(record);changed[key]=value
            with self.assertRaises(ValueError):r.validate_numerics('GP_MP_EP',pred,changed,plan,case)
        changed=deepcopy(pred);changed['phase'][0]=2
        with self.assertRaises(AssertionError):r.validate_numerics('GP_MP_EP',changed,record,plan,case)

    def test_nonfinite_or_wrong_activity_decision_is_not_success(self):
        pred,record,plan,case=self.example()
        changed=deepcopy(pred);changed['estimate'][0,0,0,0]=np.nan
        with self.assertRaises(FloatingPointError):r.validate_numerics('GP_MP',changed,record,plan,case)
        changed=deepcopy(pred);changed['activity_decision'][0]=False
        with self.assertRaises(AssertionError):r.validate_numerics('GP_MP',changed,record,plan,case)

    def test_energy_aggregation_and_all_device_aer_keep_iteration_caps(self):
        rows=[]
        for error,power,misses in [(1.,1.,1),(9.,99.,0)]:
            metrics=dict(full_error=error,signal_energy=power,active_error=error,inactive_error=0.,
                         active=1,inactive=9,misses=misses,false_alarms=0)
            rows.append(dict(metrics=metrics,iterations=600,stopping_reason='MAX_ITERATIONS'))
        result=r.aggregate(rows)
        self.assertAlmostEqual(result['nmse_db'],-10.)
        self.assertAlmostEqual(result['aer'],.05)
        self.assertEqual(result['iteration_caps'],2)

    def test_disk_reserve_and_high_user_count_prediction_budget(self):
        rt={'minimum_free_disk_gib':10.}
        with tempfile.TemporaryDirectory(dir=self.temp_root) as temp:
            plan=dict(native_directory=temp,runtime=rt)
            with patch.object(r.shutil,'disk_usage',return_value=type('D',(),{'free':11*2**30})()):
                self.assertTrue(r.disk_ready(plan,2**30))
                self.assertFalse(r.disk_ready(plan,2**30+1))
        t={'method':'GP_MP'}
        self.assertEqual(r.estimated_bytes(t,{'parameters':{'users':100}}),15*2**20)

    def test_methods_and_adoption_gate_are_stage_specific(self):
        self.assertEqual(r.methods_for('cross_channel'),['GP_MP'])
        self.assertEqual(len(r.methods_for('pilot_frames')),4)
        with patch.object(r,'read_json',return_value={'status':'WAITING'}) as read:
            with self.assertRaises(RuntimeError):r.adoption_gate('user_count')
            self.assertIn('pilot_frames',str(read.call_args.args[0]))
        with patch.object(r,'read_json',return_value={'status':'PASS'}):
            r.adoption_gate('pilot_frames')


if __name__=='__main__':
    unittest.main()
