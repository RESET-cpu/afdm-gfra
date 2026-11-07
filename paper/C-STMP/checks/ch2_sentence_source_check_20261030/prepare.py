from pathlib import Path
import hashlib, json, re

root = Path(__file__).resolve().parent
paper = root.parent.parent
src = paper / 'sections/02_system_model.tex'
text = src.read_text(encoding='utf-8')
rows = []
for m in re.finditer(r'\S[\s\S]*?(?=\n\s*\n|\Z)', text):
    chunk = m.group()
    if chunk.startswith(('\\section{', '\\subsection{')):
        continue
    row = {'id': f'P{len(rows)+1:02}', 'start_char': m.start(), 'end_char': m.end(),
           'start_line': text[:m.start()].count('\n')+1,
           'end_line': text[:m.end()].count('\n')+1, 'text': chunk}
    rows.append(row)
    (root / (row['id'] + '.input.txt')).write_text(chunk, encoding='utf-8')
(root / 'source_snapshot.tex').write_bytes(src.read_bytes())
manifest = {'source_file': str(src), 'source_sha256': hashlib.sha256(src.read_bytes()).hexdigest(), 'paragraph_count': len(rows), 'paragraphs': rows}
(root / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
sources = json.loads((paper/'checks/strict_sentence_reaudit_20261029/SOURCES.json').read_text(encoding='utf-8-sig'))
for s in sources:
    s['current_sha256'] = hashlib.sha256(Path(s['pdf']).read_bytes()).hexdigest()
    s['current_hash_matches'] = s['sha256'] == s['current_sha256']
assert all(s['current_hash_matches'] for s in sources)
(root / 'SOURCES.json').write_text(json.dumps(sources, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'paragraph_count': len(rows), 'paragraphs': [{k:r[k] for k in ['id','start_line','end_line']} for r in rows], 'source_sha256':manifest['source_sha256']}, ensure_ascii=False))
