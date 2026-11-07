"""Prepare a partial prose-only view; manual acronym review remains necessary."""
from pathlib import Path
import re

RUN = Path(__file__).resolve().parent
PAPER = RUN.parents[1]
parts = []
for source in sorted((PAPER / 'sections').glob('0[1-6]_*.tex')):
    text = source.read_text(encoding='utf-8')
    text = re.sub(r'(?m)%.*$', '', text)
    for env in ['figure', 'figure*', 'table', 'table*', 'equation', 'equation*', 'align', 'align*', 'tikzpicture']:
        text = re.sub(r'\\begin\{' + re.escape(env) + r'\}.*?\\end\{' + re.escape(env) + r'\}', ' ', text, flags=re.S)
    text = re.sub(r'(?<!\\)\$.*?(?<!\\)\$', ' ', text, flags=re.S)
    text = re.sub(r'\\\[.*?\\\]', ' ', text, flags=re.S)
    text = re.sub(r'\\(?:label|eqref|ref|autoref)\{[^}]*\}', ' ', text)
    text = re.sub(r'\\cite\w*(?:\[[^\]]*\]){0,2}\{[^}]*\}', ' ', text)
    text = re.sub(r'\\(?:sub)*section\{[^}]*\}', '\n\n', text)
    text = re.sub(r'\\(?:begin|end)\{[^}]*\}(?:\[[^\]]*\])?', ' ', text)
    text = re.sub(r'\\(?:textit|textbf|emph|texttt)\{([^{}]*)\}', r'\1', text)
    text = re.sub(r'\\[A-Za-z]+\*?(?:\[[^\]]*\])?', ' ', text)
    text = text.replace('~', ' ').replace('{', '').replace('}', '').replace('\\', ' ')
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n(?:\s*\n)+', '\n\n', text)
    parts.append(f'## {source.stem}\n\n{text.strip()}')

out = RUN / 'acronym_input.md'
out.write_text('\n\n'.join(parts) + '\n', encoding='utf-8')
print(out)
print('Coverage limitation: TeX prose extraction of Sections I-VI; equations, figures, tables, abstract, and appendices excluded.')
