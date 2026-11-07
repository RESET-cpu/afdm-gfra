from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
PAPER=ROOT/'paper/C-STMP'
files=[PAPER/'main.tex',PAPER/'main_full.tex',PAPER/'main.pdf',PAPER/'main_full.pdf',
       PAPER/'references.bib',PAPER/'README.md',ROOT/'FINAL.json',ROOT/'MAINLINE.json',
       ROOT/'src/configs/final/phase.json',ROOT/'src/configs/plots/manuscript.json',
       *PAPER.joinpath('sections').glob('*'),*PAPER.joinpath('figures').glob('*.pdf')]
hashes={}
for p in files:
    if not p.is_file():continue
    rel=p.relative_to(ROOT);dest=OUT/'before'/rel
    assert not dest.exists(),dest
    dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
    hashes[rel.as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
(OUT/'BEFORE_HASHES.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
p=PAPER/'sections/appendix_parameter_estimation.tex'
dest=PAPER/'docs/derivations/phase_estimation.tex'
assert not dest.exists()
p.rename(dest)
print('Backed up current manuscript; original phase appendix retained in docs/derivations.')
