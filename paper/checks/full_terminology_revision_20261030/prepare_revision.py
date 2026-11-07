"""Snapshot the authorized terminology revision; never execute experiments."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import urllib.request

RUN = Path(__file__).resolve().parent
PAPER = RUN.parents[1]
ROOT = PAPER.parents[1]
main = (PAPER / "main.tex").read_text(encoding="utf-8")
active = re.findall(r"^\\input\{([^}]+)\}", main, re.M)
files = [PAPER / "main.tex", PAPER / "references.bib", PAPER / "docs/TERMINOLOGY.md"]
files += [PAPER / (p + ".tex") for p in active]
files += list((PAPER / "figures").glob("*.pdf"))
files += list(PAPER.glob("*abstract*"))
protected = [ROOT / "FINAL.json", ROOT / "MAINLINE.json"]
protected += list((ROOT / "src/evaluation/plots/frozen_user_count_20261026").rglob("*.py"))
protected += list((ROOT / "src/evaluation/plots/frozen_user_count_20261026").rglob("*.json"))
old = ROOT / "paper/C-STMP/checks/algorithm_name_20261030/RENDER_VALIDATION.json"
render_record = json.loads(old.read_text(encoding="utf-8"))
for name in ("user_count", "activity_probability", "cross_channel"):
    item = render_record["figures"][name]
    for key in ("source", "source_config"):
        # The project was moved from C: to D:; the project-relative tail is stable.
        rel = item[key].replace("\\", "/").split("/result/", 1)[1]
        protected.append(ROOT / "result" / rel)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

snapshot = {}
for p in files:
    rel = p.relative_to(PAPER)
    out = RUN / "before" / rel
    if out.exists():
        raise FileExistsError(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, out)
    snapshot[str(rel).replace("\\", "/")] = sha(p)
record = {"active_inputs": active, "files": snapshot,
          "reading_pdf_before_sha256": sha(PAPER / "main.pdf"),
          "protected": {str(p.relative_to(ROOT)).replace("\\", "/"): sha(p) for p in protected},
          "authorization": "Implement F01-F07 and U01-U04/U06 from the audit; U05 acronym expansion declined by the author.",
          "abstract_regeneration": False}
(RUN / "BASELINE.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

url = "https://www.isiweb.ee.ethz.ch/archive/massey_pub/pdf/BI437.pdf"
source_dir = RUN / "sources"
source_dir.mkdir(exist_ok=True)
data = urllib.request.urlopen(url, timeout=30).read()
assert data.startswith(b"%PDF"), "Expected a PDF source"
(source_dir / "neeser1993.pdf").write_bytes(data)
(source_dir / "SOURCE.json").write_text(json.dumps({"url": url, "doi": "10.1109/18.243446", "sha256": hashlib.sha256(data).hexdigest()}, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"snapshotted_files": len(files), "protected_files": len(protected), "source_bytes": len(data)}))
