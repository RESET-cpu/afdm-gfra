from pathlib import Path
import hashlib
import json

repo = Path(__file__).resolve().parents[4]
paper = repo / 'paper/C-STMP'
out = Path(__file__).resolve().parent
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

source = paper / 'sections/02_system_model.tex'
assert sha(source) == '94a99c98c0460c689285ea211827fb07974f935d79a8602cf0edc5b846c8e37a'
protected = list((paper / 'sections').glob('*.tex')) + list((paper / 'figures').glob('*.pdf'))
protected += [paper / 'main.tex', paper / 'references.bib', repo / 'README.md', paper / 'README.md']
protected.remove(source)
manifest = {
    'authority': '用户2026-10-30：那请你修改一下，尤其是没有原词的必须替换。',
    'scope': '第二章英文正文的来源句式修订、无出处原词替换，及其术语记录和PDF更新。',
    'source_sha256': sha(source),
    'base_file': str(out / 'before.tex'),
    'base_audit': 'checks/ch2_sentence_source_check_20261030/FINAL_AUDIT.json',
    'protected_files': {str(p.relative_to(repo)): sha(p) for p in protected},
    'abstract_regenerated': False,
    'experiments_or_training': False,
    'method': '针对TeX原文的精确old/new补丁；原稿独立快照，公式与非目标文件哈希检查；不声称使用Markdown专用ARS补丁链认证。'
}
(out / 'REVISION_MANIFEST.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('snapshot and protected-file hashes recorded')
