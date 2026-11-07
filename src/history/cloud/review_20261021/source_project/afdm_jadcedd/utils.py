"""Artifact hashes and JSON records."""
from pathlib import Path
import hashlib,json,time

def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(4*1024*1024), b''):
            digest.update(block)
    return digest.hexdigest()

def state_sha(model):
    h=hashlib.sha256()
    for key,value in model.state_dict().items():
        h.update(key.encode());h.update(value.detach().cpu().contiguous().numpy().tobytes())
    return h.hexdigest()

def write_json(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+"\n")

def event(folder,stage,**values):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    row=dict(stage=stage,time=time.time(),**values)
    with (folder/"events.jsonl").open("a") as f:f.write(json.dumps(row,ensure_ascii=False)+"\n")
    print(json.dumps(row,ensure_ascii=False),flush=True)
