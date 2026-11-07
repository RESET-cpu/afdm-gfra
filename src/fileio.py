"""Artifact hashes and JSON records."""
from pathlib import Path
import gzip
import hashlib
import json
import os
import time
from workspace import frozen_read_path

def sha256(path):
    digest = hashlib.sha256()
    with frozen_read_path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def json_digest(value):
    """Hash a JSON value independently of key order or display formatting."""
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def read_json(path):
    path = frozen_read_path(path)
    if path.suffix == '.gz':
        with gzip.open(path, 'rt', encoding='utf-8-sig') as stream:
            return json.load(stream)
    return json.loads(path.read_text(encoding='utf-8-sig'))

def state_sha(model):
    h=hashlib.sha256()
    for key,value in model.state_dict().items():
        h.update(key.encode());h.update(value.detach().cpu().contiguous().numpy().tobytes())
    return h.hexdigest()

def write_json(path, value):
    """Publish a complete UTF-8 record using an atomic file replacement."""
    content = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + f'.{os.getpid()}.tmp')
    temp.write_text(content, encoding='utf-8')
    temp.replace(path)

def event(folder,stage,**values):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    row=dict(stage=stage,time=time.time(),**values)
    with (folder/"events.jsonl").open("a", encoding='utf-8') as f:f.write(json.dumps(row,ensure_ascii=False)+"\n")
    print(json.dumps(row,ensure_ascii=False),flush=True)
