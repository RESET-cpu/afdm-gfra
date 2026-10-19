"""Bounded synthetic lifecycle tests; no formal training or held-out scene use."""
import copy, json, os, sys, tempfile, time, unittest
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
BASE=HERE.parents[1]
PACKAGE=BASE if (BASE/'run_windows.py').exists() else BASE/'AFDM_LSTMP'
os.environ['AFDM_LSTMP_ROOT']=str(PACKAGE)
sys.path.insert(0,str(PACKAGE/'runs/lstmp_fresh_20261019/source_experiment'))
import numpy as np
import torch
import common, data, train, receiver

torch.set_num_threads(1)

class ToyScore(torch.nn.Module):
    def __init__(self,**kwargs):super().__init__();self.weight=torch.nn.Parameter(torch.tensor(.1));self.calls=0
    def forward(self,x,v):self.calls+=1;return self.weight*x

class ToyCases:
    device='cpu'
    def __init__(self,*args):self.seen=[]
    def __len__(self):return 3
    def __getitem__(self,i):
        self.seen.append(i)
        return {'x':torch.ones(2,2)},dict(x=torch.ones(2,2),active=torch.tensor([1.,0.])),dict(seed=100+i,snr=0.)

class ToyReceiver(torch.nn.Module):
    constructions=0
    def __init__(self):super().__init__();ToyReceiver.constructions+=1
    def add_layer(self,*args):pass
    def forward(self,p):return [(p['x']*.5,torch.zeros(2))],[]

class Lifecycle(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='synthetic_lifecycle_')
        self.root=Path(self.temp.name);self.config=copy.deepcopy(common.CONFIG)
        self.config['receiver'].update(test_scenes=3,test_seed=100,snr_db=[0.],maximum_depth=1)
        self.patches=[]
        for module in (common,data,train,receiver):
            for key,value in [('OUT',self.root),('ROOT',self.root),('CONFIG',self.config)]:
                if hasattr(module,key):p=patch.object(module,key,value);p.start();self.patches.append(p)
        for module in (train,data):
            p=patch.object(module,'status',lambda *a,**k:None);p.start();self.patches.append(p)
    def tearDown(self):
        for p in reversed(self.patches):p.stop()
        self.temp.cleanup()
    def arrays(self,seed,snr,scale):
        n=seed-99
        return dict(observation=np.full((16,16,16),complex(n)),operator=np.ones((16,40,16),complex),noise_variance=.1,activity_prior=.1),dict(channel=np.ones((40,16,16,16),complex),activity=np.r_[1,np.zeros(39)]),{}
    def populate(self):
        with patch.object(data,'generate_case',self.arrays):return data.build_cases('test',1.,time.time())
    def test_score_validation_pause_at_microbatch_boundary(self):
        model=ToyScore();bank=np.ones((4,16,16,16),np.complex64);self.config['pretraining']['microbatch']=2
        with patch.object(train,'check_budget',side_effect=[None,InterruptedError('synthetic pause')]):
            with self.assertRaises(InterruptedError):train.validate_score(model,bank,1.,'cpu',0.)
        self.assertEqual(model.calls,1)
    def test_evaluation_pause_and_incremental_resume(self):
        saved=[];cases=ToyCases();model=ToyReceiver()
        with patch.object(receiver,'check_budget',side_effect=[None,InterruptedError('synthetic pause')]):
            with self.assertRaises(InterruptedError):
                receiver.evaluate(model,cases,started=0.,on_row=lambda rows:saved.append(copy.deepcopy(rows)))
        self.assertEqual(cases.seen,[0]);self.assertEqual(len(saved[-1]),1)
        with patch.object(receiver,'check_budget',return_value=None):
            result=receiver.evaluate(model,cases,started=0.,rows=saved[-1])
        self.assertEqual(cases.seen,[0,1,2]);self.assertEqual(len(result['rows']),3)
        self.assertTrue(all(row['total_seconds']>=row['inference_seconds']>=0 for row in result['rows']))
    def test_recorded_scene_tamper_rejected_and_orphan_recovered(self):
        receipt=self.populate();path=data.case_path('test',0);content=path.read_bytes()
        path.write_bytes(content+b'changed')
        with self.assertRaisesRegex(ValueError,'changed'):self.populate()
        path.write_bytes(content)
        # Simulate interruption after scene save but before receipt save.
        entry=receipt['files'].pop(path.name);common.save_json(self.root/'data/receiver_test.json',receipt)
        recovered=self.populate();self.assertEqual(recovered['files'][path.name],entry)
        with np.load(path) as z:values=dict(z)
        values['seed']=999;np.savez_compressed(path,**values)
        receipt['files'].pop(path.name,None);common.save_json(self.root/'data/receiver_test.json',receipt)
        with self.assertRaisesRegex(ValueError,'identity'):self.populate()
    def test_completed_checkpoint_hash_and_plateau_resume(self):
        folder=self.root/'checkpoints/pretrain';folder.mkdir(parents=True)
        (self.root/'data').mkdir();np.save(self.root/'data/prior_train.npy',np.ones((1,2),complex));np.save(self.root/'data/prior_validation.npy',np.ones((1,2),complex))
        model=ToyScore();optimizer=torch.optim.Adam(model.parameters(),lr=.001)
        common.save_torch(folder/'best.pt',dict(state=model.state_dict(),epoch=1))
        common.save_torch(folder/'last.pt',dict(model=model.state_dict(),ema=model.state_dict(),optimizer=optimizer.state_dict(),epoch=2,cursor=0,steps=1,best=.9,stale=1,history=[],loss_sum=0.,samples=0,selected_epoch=1))
        self.config['pretraining'].update(epochs=3,minimum_epochs=1,patience=1)
        with patch.object(train,'FreshScore',ToyScore),patch.object(train,'validate_score',side_effect=AssertionError('plateau resume must not train/validate')):
            train.pretrain(1.,'cpu',time.time())
        self.assertTrue(train.completed_checkpoint(folder))
        self.assertEqual(json.loads((folder/'COMPLETE.json').read_text())['steps'],1)
        with (folder/'best.pt').open('ab') as f:f.write(b'changed')
        with self.assertRaisesRegex(ValueError,'checkpoint changed'):train.completed_checkpoint(folder)
    def setup_final(self):
        receipt=self.populate();(self.root/'MANIFEST.json').write_text('{}')
        folder=self.root/'checkpoints/depth_1';folder.mkdir(parents=True);common.save_torch(folder/'best.pt',{'state':{}})
        cfg={}
        for key in ('first_checkpoint','second_checkpoint','evidence_checkpoint'):
            cfg[key]=key+'.pt';(self.root/cfg[key]).write_bytes(key.encode())
        (self.root/'configs').mkdir();(self.root/'configs/proposed.json').write_text(json.dumps(cfg))
        return receipt
    def test_final_results_resume_skips_completed_scenes_and_depth(self):
        receipt=self.setup_final();calls=[];failed=[False]
        class Original:
            def __init__(self,*a,**k):pass
            def infer(self,inputs):
                index=int(inputs.observation.flat[0].real);calls.append(index)
                if index==2 and not failed[0]:failed[0]=True;raise InterruptedError('synthetic pause')
                return dict(estimate=np.zeros((40,16,16,16),complex),probabilities=np.zeros(40)),dict(iterations=2,stopping_reason='TOY')
        import afdm_jadcedd.algorithm.proposed.receiver as original_module
        ToyReceiver.constructions=0
        with patch.object(train,'build_cases',return_value=receipt),patch.object(train,'Cases',ToyCases),patch.object(train,'Receiver',ToyReceiver),patch.object(original_module,'Receiver',Original):
            with self.assertRaises(InterruptedError):train.final_test(1.,'cpu',time.time())
            path=self.root/'results/original_test.json';partial=json.loads(path.read_text());self.assertEqual(len(partial['rows']),1)
            train.final_test(1.,'cpu',time.time())
            # Simulate a crash after last candidate row but before final summary.
            candidate_path=self.root/'results/test_depth_1.json'
            candidate=json.loads(candidate_path.read_text());candidate['status']='PARTIAL';candidate.pop('summary')
            common.save_json(candidate_path,candidate)
            train.final_test(1.,'cpu',time.time())
            finalized=json.loads(candidate_path.read_text())
            self.assertEqual(finalized['status'],'COMPLETE');self.assertIn('summary',finalized)
        self.assertEqual(calls,[1,2,2,3]);self.assertEqual(ToyReceiver.constructions,1)
        result=json.loads(path.read_text());self.assertEqual(result['status'],'COMPLETE');self.assertEqual(len(result['rows']),3)
        changed=copy.deepcopy(result['identity']);changed['device']='different'
        with self.assertRaisesRegex(ValueError,'identity changed'):train.load_test_progress(path,changed,3)
    def test_nonfinite_original_output_not_committed(self):
        receipt=self.setup_final()
        class Original:
            def __init__(self,*a,**k):pass
            def infer(self,inputs):return dict(estimate=np.full((40,16,16,16),np.nan),probabilities=np.zeros(40)),dict(iterations=1,stopping_reason='TOY')
        import afdm_jadcedd.algorithm.proposed.receiver as original_module
        with patch.object(train,'build_cases',return_value=receipt),patch.object(train,'Cases',ToyCases),patch.object(train,'Receiver',ToyReceiver),patch.object(original_module,'Receiver',Original):
            with self.assertRaisesRegex(FloatingPointError,'Nonfinite original'):train.final_test(1.,'cpu',time.time())
        self.assertFalse((self.root/'results/original_test.json').exists())

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Lifecycle)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    report=dict(scope='Synthetic lifecycle tests only: mocked receivers and temporary cases; no formal training or held-out experiment',tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),passed=result.wasSuccessful())
    (HERE/'RESULTS.json').write_text(json.dumps(report,indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
