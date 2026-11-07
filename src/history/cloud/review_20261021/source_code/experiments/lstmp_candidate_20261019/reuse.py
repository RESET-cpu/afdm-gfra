"""Bind the completed 50k first score to a separate joint-training run."""
import json
import torch
from .common import ROOT, OUT, CONFIG, sha, save_json, save_torch
from .backbone import make_score


def prepare_initialization():
    specification = CONFIG['pretrained_score']
    source = ROOT/specification['path']
    digest = sha(source)
    if digest != specification['sha256']:
        raise ValueError('The authorized pretrained score checkpoint changed')
    original = torch.load(source, map_location='cpu', weights_only=False)
    if (original['schema'] != 'afdm-cai-direct-score-v1' or original['order'] != 1
            or original['normalization'] != 'population_rms'
            or original['config'] != CONFIG['backbone']['config']):
        raise ValueError('Pretrained architecture or normalization does not match')
    scale = float(original['global_complex_rms'])
    if scale != specification['global_complex_rms']:
        raise ValueError('Pretrained coordinate scale changed')
    model = make_score()
    model.load_state_dict(original['state_dict'], strict=True)
    folder = OUT/'initialization'
    target = folder/'first_50000.pt'
    receipt_path = folder/'BINDING.json'
    identity = dict(source=str(source.resolve()), source_sha256=digest,
        schema=original['schema'], order=1, config=original['config'], scale=scale,
        normalization=original['normalization'], parameters=sum(p.numel() for p in model.parameters()),
        training_samples=50000, initialization_only=True,
        score_pretraining_performed_in_this_run=False)
    if receipt_path.exists():
        saved = json.loads(receipt_path.read_text(encoding='utf-8'))
        if saved['identity'] != identity or saved['checkpoint_sha256'] != sha(target):
            raise ValueError('Saved initialization binding changed')
    else:
        save_torch(target, dict(state=original['state_dict'], scale=scale, source=identity))
        save_json(receipt_path, dict(identity=identity, checkpoint_sha256=sha(target)))
    save_json(OUT/'data'/'normalization.json', dict(scale=scale, per_sample=False,
        source='Completed 50,000-sample first-score checkpoint; unchanged coordinate convention',
        source_sha256=digest, normalized_training_second_moment=CONFIG['normalized_training_second_moment']))
    return target, scale
