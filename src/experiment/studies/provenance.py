"""Record the executed implementation separately from a historical plan."""
from pathlib import Path
import hashlib
import json

from workspace import ROOT

MANIFEST = 'archive/code_cleanup_20261107/CURRENT_SOURCES.json'


def execution_identity():
    path = ROOT / MANIFEST
    document = json.loads(path.read_text(encoding='utf-8'))
    for name, expected in document['sha256'].items():
        actual = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError('Study implementation changed; validate and record a new version: ' + name)
    return dict(source_manifest=MANIFEST,
                source_manifest_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                frozen_plan_sources='Original source bytes retained in the relocation archive',
                executed_sources='Current source inventory; numerical parity evidence linked in the manifest')
