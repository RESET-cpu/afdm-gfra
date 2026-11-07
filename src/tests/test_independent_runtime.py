"""Optional model checks using the published current asset inventory."""
import hashlib
import json
from workspace import ROOT, repository_path

def test_selected_inference_assets_are_inside_project():
    manifest = json.loads((ROOT/'src/configs/release/weights.json').read_text())
    for asset in manifest['files']:
        path = repository_path(asset['path'])
        assert path.is_file()
        assert path.resolve().is_relative_to(ROOT)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == asset['sha256']
