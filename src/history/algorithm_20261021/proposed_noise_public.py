"""File entry for the validated observation-only Proposed noise estimate."""
import hashlib,json,time,warnings
from pathlib import Path
import numpy as np
from afdm_jadcedd.algorithm.proposed_noise_candidate import EstimatedNoiseProposedReceiver
from afdm_jadcedd.algorithm.baselines.noise_estimation import load_unknown_noise_input
from afdm_jadcedd.project import ROOT
from afdm_jadcedd.utils import sha256,write_json

class EstimatedNoiseProposedPublicReceiver(EstimatedNoiseProposedReceiver):
    def __init__(self,configuration,*,device='auto'):
        super().__init__(configuration,device=device)
        sources=[Path(__file__),ROOT/'src/afdm_jadcedd/algorithm/proposed_noise_candidate.py',
                 ROOT/'src/afdm_jadcedd/algorithm/baselines/noise_estimation.py']
        self.signature=hashlib.sha256(json.dumps(dict(configuration=configuration,
            sources={str(p.relative_to(ROOT)):sha256(p) for p in sources}),sort_keys=True).encode()).hexdigest()

    def infer(self,inputs,*,observer=None):
        arrays,record=super().infer(inputs,observer=observer)
        record=dict(record,method='proposed_estimated_noise',inference_sha256=self.signature,
                    input_fields=['observation','operator','activity_prior'])
        return arrays,record

    def run(self,input_path,output_path,*,observer=None):
        output=Path(output_path)
        paths=[output,output.with_suffix('.json'),output.with_suffix('.warnings.json')]
        if output.suffix!='.npz' or any(p.exists() for p in paths):
            raise ValueError('Fresh native .npz output required')
        output.parent.mkdir(parents=True,exist_ok=True);caught=[]
        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always',RuntimeWarning)
                inputs=load_unknown_noise_input(input_path,phase_mode='known')
                arrays,record=self.infer(inputs,observer=observer)
                if not all(np.isfinite(v).all() for v in arrays.values()):
                    raise FloatingPointError('Nonfinite Proposed output')
            np.savez_compressed(output,**arrays)
            record.update(input_sha256=sha256(input_path),output_sha256=sha256(output))
            write_json(output.with_suffix('.json'),record)
            return record
        except BaseException as error:
            write_json(output.with_suffix('.json'),dict(status='FAILED',method='proposed_estimated_noise',
                error=repr(error),inference_sha256=self.signature,noise_mode='estimated'))
            raise
        finally:
            write_json(output.with_suffix('.warnings.json'),[dict(category=w.category.__name__,
                message=str(w.message),filename=w.filename,lineno=w.lineno) for w in caught])
