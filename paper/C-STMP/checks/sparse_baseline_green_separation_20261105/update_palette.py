"""Apply the author's more distinct green-family baseline colors."""
from pathlib import Path
from copy import deepcopy
import hashlib
import json
import shutil

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
CONFIG=ROOT/'src/configs/plots/manuscript.json'
PALETTE={'gnn':'#00a0a0','gamp':'#2e8b57','somp':'#123d2a'}

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,data): p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

assert not (OUT/'BEFORE_HASHES.json').exists(), 'Preserve original backup'
config=read(CONFIG); before=deepcopy(config)
figures=[name for name,cfg in config['figures'].items() if any(m in cfg.get('methods',[]) for m in PALETTE)]
files=[CONFIG,ROOT/'FINAL.json',ROOT/'MAINLINE.json',ROOT/'paper/C-STMP/main.pdf',ROOT/'paper/C-STMP/main_full.pdf']
files+=list((ROOT/'paper/C-STMP/figures').glob('*.pdf'))
files+=[ROOT/'paper/C-STMP/figures/snr_comparison.png']
files+=list((ROOT/'paper/C-STMP/sections').glob('*.tex'))
hashes={}
for p in files:
    rel=p.relative_to(ROOT); target=OUT/'before'/rel
    target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,target)
    hashes[rel.as_posix()]=sha(p)
save(OUT/'BEFORE_HASHES.json',hashes)
changes=[]
for name in figures:
    cfg=config['figures'][name]
    for container in [cfg]+([cfg['panel_config']] if 'panel_config' in cfg else []):
        for method,color in PALETTE.items():
            if method in container.get('styles',{}):
                old=container['styles'][method]['color']
                container['styles'][method]['color']=color
                changes.append(dict(figure=name,method=method,old=old,new=color))
restored=deepcopy(config)
for name in figures:
    for key in PALETTE:
        restored['figures'][name]['styles'][key]['color']=before['figures'][name]['styles'][key]['color']
        if 'panel_config' in restored['figures'][name]:
            restored['figures'][name]['panel_config']['styles'][key]['color']=before['figures'][name]['panel_config']['styles'][key]['color']
assert restored==before, 'Only requested colors may change'
save(CONFIG,config)
save(OUT/'PALETTE.json',dict(palette=PALETTE,figures=figures,changes=changes,only_three_colors_changed=True))
print(json.dumps(dict(figures=figures,palette=PALETTE,style_entries_changed=len(changes))))
