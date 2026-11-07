"""Validate this literature delivery without loading project models or data."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import pypdfium2 as pdfium

LIBRARY = Path(__file__).resolve().parent
ROOT = LIBRARY.parent.parent
manifest = json.loads((LIBRARY / "DOWNLOAD_MANIFEST.json").read_text(encoding="utf-8"))
checks = []
for entry in manifest["papers"]:
    if entry["status"] != "available":
        continue
    file = LIBRARY / entry["pdf"]
    data = file.read_bytes()
    extracted = (LIBRARY / entry["text"]).read_text(encoding="utf-8")
    document = pdfium.PdfDocument(file)
    pages = len(document)
    page = document[pages - 1]
    size = page.get_size()
    page.close()
    document.close()
    record = {
        "id": entry["id"],
        "header_ok": data.startswith(b"%PDF"),
        "sha256_ok": hashlib.sha256(data).hexdigest() == entry["sha256"],
        "bytes_ok": len(data) == entry["bytes"],
        "pdfium_pages": pages,
        "pages_match": pages == entry["pages"],
        "text_page_markers": len(re.findall(r"^=== PDF PAGE \d+ ===", extracted, re.M)),
        "last_page_size": list(size),
    }
    record["text_pages_match"] = record["text_page_markers"] == entry["pages"]
    record["pass"] = all(record[key] for key in
                         ("header_ok", "sha256_ok", "bytes_ok", "pages_match", "text_pages_match"))
    checks.append(record)

paths = [
    ROOT / "paper/docs/STMP_PAPER_READING_NOTES_20261024.md",
    ROOT / "paper/docs/STMP_MESSAGE_AWGN_REVIEW_20261024.md",
    LIBRARY / "README.md",
    *sorted((LIBRARY / "notes").glob("download_followup_*.md")),
]
docs = []
for file in paths:
    content = file.read_text(encoding="utf-8")
    missing = []
    for target in re.findall(r"\[[^\]\n]*\]\(([^)]+)\)", content):
        if target.startswith(("http:", "https:", "mailto:", "#")):
            continue
        target = target.split("#")[0].strip("<>")
        if target == "DOWNLOAD_VALIDATION.json":
            continue  # This script writes it below.
        if not (file.parent / target).resolve().exists():
            missing.append(target)
    controls = [ord(char) for char in content if ord(char) < 32 and char not in "\n\r\t"]
    docs.append({
        "file": file.relative_to(ROOT).as_posix(),
        "sha256": hashlib.sha256(file.read_bytes()).hexdigest(),
        "missing_local_links": missing,
        "control_chars": controls,
        "inline_math_balanced": content.count(r"\(") == content.count(r"\)"),
        "display_math_balanced": content.count(r"\[") == content.count(r"\]"),
    })

coverage = {
    entry["id"]: [
        file.relative_to(LIBRARY).as_posix()
        for file in paths
        if file.parent == LIBRARY / "notes"
        and entry["id"] in file.read_text(encoding="utf-8")
    ]
    for entry in manifest["papers"] if entry["status"] == "available"
}
result = {
    "verified_utc": datetime.now(timezone.utc).isoformat(),
    "summary": manifest["summary"],
    "pdf_checks": checks,
    "document_checks": docs,
    "reading_note_coverage": coverage,
    "all_available_pdfs_pass": all(record["pass"] for record in checks),
    "all_local_links_pass": all(not record["missing_local_links"] for record in docs),
    "all_math_and_control_checks_pass": all(
        record["inline_math_balanced"] and record["display_math_balanced"]
        and not record["control_chars"] for record in docs
    ),
    "all_available_pdfs_have_reading_note": all(coverage.values()),
    "limitations": [
        "Selective reading of methods, assumptions and experiments, not a complete proof audit.",
        "Cheng 2021 full text not obtained; Djelouat 2024 journal version not obtained, 2023 preprint retained.",
        "The original VALIDATION.json is historical and its report hash predates this revision.",
    ],
    "validator_repair": "Initial one-off invocation used an unsupported negative PDFium page index; corrected to pages-1.",
    "training_or_receiver_runs_this_turn": False,
}
(LIBRARY / "DOWNLOAD_VALIDATION.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({key: value for key, value in result.items() if key.startswith("all_")}))
print("missing_links:", [(record["file"], record["missing_local_links"])
                         for record in docs if record["missing_local_links"]])
print("uncovered:", [key for key, value in coverage.items() if not value])
