from pathlib import Path
import sys,json,hashlib,re
sys.path.append(str(Path.home()/'.cache/codex-pymupdf'))
import pymupdf as fitz
root=Path('D:/afdm-gfra'); check=root/'paper/C-STMP/checks/white_denoising_adopted_20261107'
result={}
for name in ['main','main_full']:
    new=fitz.open(root/f'paper/C-STMP/{name}.pdf')
    old=fitz.open(check/f'before/paper/C-STMP/{name}.pdf')
    assert len(new)==len(old)
    changed=[]
    for i,(a,b) in enumerate(zip(new,old)):
        assert a.rect==b.rect
        pa,pb=a.get_pixmap(dpi=100,alpha=False),b.get_pixmap(dpi=100,alpha=False)
        if pa.samples!=pb.samples:
            changed.append(i+1)
            a.get_pixmap(dpi=140,alpha=False).save(check/f'{name}_page{i+1:02d}.png')
    log=(root/f'paper/C-STMP/{name}.log').read_text(encoding='utf-8',errors='replace')
    assert 'Overfull' not in log and 'undefined references' not in log and 'Missing character' not in log
    result[name]={'pages':len(new),'changed_pages':changed,'no_overfull_missing_or_undefined':True,'sha256':hashlib.sha256((root/f'paper/C-STMP/{name}.pdf').read_bytes()).hexdigest()}
(check/'PDF_CHECK.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(result)
