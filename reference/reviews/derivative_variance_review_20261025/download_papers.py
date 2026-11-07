"""Archive the three derivative-covariance papers discussed on 2026-10-25."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import io
import json
import re
import urllib.request

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
CATALOG = [
    dict(id="01_manor_michaeli_2024_posterior", title="On the Posterior Distribution in Denoising: Application to Uncertainty Quantification",
         version="arXiv:2309.13598v2", url="https://arxiv.org/pdf/2309.13598v2",
         identity=["posterior", "distribution", "manor", "michaeli", "2309.13598v2"]),
    dict(id="02_boys_2024_tmpd", title="Tweedie Moment Projected Diffusions for Inverse Problems",
         version="arXiv:2310.06721v3", url="https://arxiv.org/pdf/2310.06721v3",
         identity=["tweedie", "moment", "projected", "boys", "2310.06721v3"]),
    dict(id="03_shastri_2022_dgec", title="Denoising Generalized Expectation-Consistent Approximation for MR Image Recovery",
         version="arXiv:2206.05049v2", url="https://arxiv.org/pdf/2206.05049v2",
         reuse="../stmp_message_awgn_review_20261024/papers/18_shastri2022_dgec.pdf",
         identity=["denoising", "generalized", "expectation", "shastri", "2206.05049v2"]),
]


def validate(data, row):
    if not data.startswith(b"%PDF-"):
        raise ValueError("Not a PDF response")
    reader = PdfReader(io.BytesIO(data))
    pages = [page.extract_text() or "" for page in reader.pages]
    first = re.sub(r"\s+", "", pages[0]).lower() if pages else ""
    missing = [token for token in row["identity"] if token.lower() not in first]
    if missing:
        raise ValueError(f"First-page identity mismatch: {missing}")
    return pages


def acquire(row):
    record = {key: value for key, value in row.items() if key != "identity"}
    record["checked_utc"] = datetime.now(timezone.utc).isoformat()
    target = ROOT / "papers" / (row["id"] + ".pdf")
    try:
        if target.exists():
            data = target.read_bytes()
            record["acquisition"] = "existing_validated"
        elif row.get("reuse"):
            source = (ROOT / row["reuse"]).resolve()
            data = source.read_bytes()
            record.update(acquisition="reused_local", reused_from=str(source))
        else:
            request = urllib.request.Request(row["url"], headers={"User-Agent": "Research-PDF-Archive/1.0"})
            with urllib.request.urlopen(request, timeout=45) as response:
                data = response.read()
                record["resolved_url"] = response.geturl()
            record["acquisition"] = "downloaded"
        pages = validate(data, row)
        if not target.exists():
            with target.open("xb") as handle:
                handle.write(data)
        text_path = ROOT / "text" / (row["id"] + ".txt")
        text_path.write_text("\n\n".join(f"=== PDF PAGE {i + 1} ===\n{page}" for i, page in enumerate(pages)), encoding="utf-8")
        record.update(status="available", pages=len(pages), bytes=len(data),
                      sha256=hashlib.sha256(data).hexdigest(),
                      pdf=target.relative_to(ROOT).as_posix(), text=text_path.relative_to(ROOT).as_posix(),
                      identity_verified=True, all_pages_parsed=True, first_page_excerpt=pages[0][:1000])
    except Exception as exc:
        record.update(status="failed", error=str(exc))
    return record


def main():
    for name in ("papers", "text"):
        (ROOT / name).mkdir(exist_ok=True)
    records = []
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(acquire, row) for row in CATALOG]
        for future in as_completed(futures):
            record = future.result()
            records.append(record)
            print(json.dumps({key: record.get(key) for key in ("id", "status", "acquisition", "pages", "bytes", "error")}), flush=True)
            (ROOT / "DOWNLOAD_MANIFEST.json").write_text(json.dumps({
                "scope": "Three papers explicitly requested after the derivative-variance literature discussion",
                "updated_utc": datetime.now(timezone.utc).isoformat(),
                "papers": sorted(records, key=lambda item: item["id"]),
            }, ensure_ascii=False, indent=2), encoding="utf-8")
    if any(record["status"] != "available" for record in records):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
