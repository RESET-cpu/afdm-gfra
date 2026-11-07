"""Download the scoped STMP bibliography; validate PDF files and retain provenance."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import io
import json
import logging
import shutil
import urllib.request
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parents[1]
CATALOG = [
    ("01_ma2017_oamp", "Orthogonal AMP", "Ma; Ping", "2017; arXiv v3", "https://arxiv.org/pdf/1602.06509v3", "main_sources/ma2017_oamp_v3.pdf"),
    ("02_rangan2019_vamp", "Vector Approximate Message Passing", "Rangan; Schniter; Fletcher", "2019; arXiv v2", "https://arxiv.org/pdf/1610.03082v2", ""),
    ("03_fletcher2019_nonseparable_vamp", "Plug-in Estimation in High-Dimensional Linear Inverse Problems: A Rigorous Analysis", "Fletcher; Pandit; Rangan; Sarkar; Schniter", "JSTAT 2019", "https://phil-schniter.web.app/pdf/jstat19.pdf", "main_sources/fletcher2019_nonseparable_vamp.pdf"),
    ("04_xue2016_doamp", "D-OAMP: A Denoising-Based Signal Recovery Algorithm for Compressed Sensing", "Xue; Ma; Yuan", "2016; arXiv v1", "https://arxiv.org/pdf/1610.05991v1", ""),
    ("05_xue2017_dturbo", "Denoising-based Turbo Compressed Sensing", "Xue; Ma; Yuan", "2017; arXiv v1", "https://arxiv.org/pdf/1703.08756v1", ""),
    ("06_liu2018_massive_mimo", "Massive Connectivity with Massive MIMO—Part I: Device Activity Detection and Channel Estimation", "Liu; Yu", "2018; arXiv v2", "https://arxiv.org/pdf/1706.06438v2", "../activity_threshold_review_20261023/liu2018_amp.pdf"),
    ("07_hannak2018_mmv", "Performance Analysis of Approximate Message Passing for Distributed Compressed Sensing", "Hannak; Perelli; Goertz; Matz; Davies", "2018; arXiv v2", "https://arxiv.org/pdf/1712.04893v2", ""),
    ("08_djelouat2021_correlated_amp", "User Activity Detection and Channel Estimation of Spatially Correlated Channels via AMP in Massive MTC", "Djelouat; Marata; Leinonen; Alves; Juntti", "2021; arXiv v1", "https://arxiv.org/pdf/2112.04295v1", ""),
    ("09_kunde2026_complex_amp", "Complex Approximate Message Passing with Non-separable Denoising", "Kunde; Mirri; Chamberland; Paolini", "2026; arXiv v1", "https://arxiv.org/pdf/2604.21115v1", ""),
    ("10_djelouat2024_hierarchical_ep", "Hierarchical MTC User Activity Detection and Channel Estimation with Unknown Spatial Covariance", "Djelouat; Sillanpaa; Leinonen; Juntti", "TWC 2024; arXiv 2023 v1", "https://arxiv.org/pdf/2310.10204v1", ""),
    ("11_liu2022_memory_amp", "Memory AMP", "Liu; Huang; Kurkoski", "2022; arXiv v7", "https://arxiv.org/pdf/2012.10861v7", ""),
    ("12_liu2023_ssmamp", "Sufficient-Statistic Memory AMP", "Liu; Huang; Yang; Zhang; Kurkoski", "2023; arXiv v4", "https://arxiv.org/pdf/2112.15327v4", ""),
    ("13_takeuchi2022_long_memory", "On the Convergence of Orthogonal/Vector AMP: Long-Memory Message-Passing Strategy", "Takeuchi", "2022; arXiv v2", "https://arxiv.org/pdf/2111.05522v2", ""),
    ("14_cheng2023_oamp_mmv", "Orthogonal AMP for Problems with Multiple Measurement Vectors and/or Multiple Transforms", "Cheng; Liu; Liang; Manton; Ping", "TSP 2023; arXiv v1", "https://arxiv.org/pdf/2304.08038v1", ""),
    ("15_liu2023_orthogonal_principle", "On Orthogonal Approximate Message Passing", "Liu; Cheng; Liang; Manton; Ping", "TCOM 2023, published as On OAMP: Impact of the Orthogonal Principle; arXiv v2", "https://arxiv.org/pdf/2203.00224v2", ""),
    ("16_millard2020_vdamp", "Approximate Message Passing with a Colored Aliasing Model for Variable Density Fourier Sampled Images", "Millard; Hess; Mailhe; Tanner", "2020; arXiv v3", "https://arxiv.org/pdf/2003.02701v3", ""),
    ("17_metzler2020_dvdamp", "D-VDAMP: Denoising-based Approximate Message Passing for Compressive MRI", "Metzler; Wetzstein", "2020; arXiv v1", "https://arxiv.org/pdf/2010.13211v1", ""),
    ("18_shastri2022_dgec", "Denoising Generalized Expectation-Consistent Approximation for MR Image Recovery", "Shastri; Ahmad; Metzler; Schniter", "2022; arXiv v2", "https://arxiv.org/pdf/2206.05049v2", ""),
    ("19_sarkar2020_ddvamp", "MRI Image Recovery using Damped Denoising Vector AMP", "Sarkar; Ahmad; Schniter", "ICASSP 2021; arXiv 2020 v1", "https://arxiv.org/pdf/2010.11321v1", ""),
    ("20_bendel2025_fire", "Solving Inverse Problems using Diffusion with Iterative Colored Renoising", "Bendel; Shastri; Ahmad; Schniter", "TMLR 2025; arXiv v4", "https://arxiv.org/pdf/2501.17468v4", ""),
    ("21_metzler2017_ldamp", "Learned D-AMP: Principled Neural Network based Compressive Image Recovery", "Metzler; Mousavi; Baraniuk", "NeurIPS 2017; arXiv v4, 2017-11-06", "https://arxiv.org/pdf/1704.06625v4", ""),
    ("22_cheng2021_massive_access", "Orthogonal AMP for Massive Access in Channels With Spatial and Temporal Correlations", "Cheng; Liu; Ping", "JSAC 2021", "", ""),
    ("23_cai2026_stmp", "Joint Activity Detection and Channel Estimation for Massive Connectivity: Where Message Passing Meets Score-Based Generative Priors", "Cai; Jiang; Yuan; Zhang", "2026; arXiv v2", "https://arxiv.org/pdf/2506.00581v2", "main_sources/cai2026_stmp_v2.pdf"),
    ("24_wei2026_lstmp", "Learned Score-Based Turbo Message Passing for Channel Recovery From Spatially Compressed Measurements", "Wei; Yuan", "2026; arXiv v1", "https://arxiv.org/pdf/2610.17785v1", "../literature/wei_yuan_2026_lstmp_v1.pdf"),
    ("25_lovig2026_universality", "On Universality of Non-Separable Approximate Message Passing Algorithms", "Lovig; Wang; Fan", "2026; arXiv v2; supplementary scope check", "https://arxiv.org/pdf/2506.23010v2", ""),
]

def validate(data):
    if not data.startswith(b"%PDF"):
        raise ValueError("Response is not a PDF")
    reader = PdfReader(io.BytesIO(data))
    pages = [p.extract_text() or "" for p in reader.pages]
    if not pages or len(pages[0]) < 40:
        raise ValueError("Empty or non-text first page")
    return pages

def acquire(row):
    name, title, authors, version, url, reuse = row
    record = dict(id=name, title=title, authors=authors, version=version, requested_url=url,
                  retrieved_utc=datetime.now(timezone.utc).isoformat(), attempts=[])
    target = ROOT / "papers" / (name + ".pdf")
    source = (ROOT / reuse).resolve() if reuse else None
    try:
        if target.exists():
            data = target.read_bytes()
            pages = validate(data)
            record.update(acquisition="existing_validated")
        elif source is not None and source.exists():
            data = source.read_bytes()
            pages = validate(data)
            shutil.copyfile(source, target)
            record.update(acquisition="reused_local", reused_from=str(source))
        elif url:
            data = None
            for attempt in range(2):
                try:
                    request = urllib.request.Request(url, headers={"User-Agent": "Research-PDF-Archive/1.0"})
                    with urllib.request.urlopen(request, timeout=45) as response:
                        candidate = response.read()
                        resolved_url = response.geturl()
                    pages = validate(candidate)
                    data = candidate
                    record["resolved_url"] = resolved_url
                    record["attempts"].append(dict(attempt=attempt + 1, status="ok"))
                    break
                except Exception as exc:
                    record["attempts"].append(dict(attempt=attempt + 1, error=str(exc)))
            if data is None:
                raise RuntimeError("Both download attempts failed")
            target.write_bytes(data)
            record["acquisition"] = "downloaded"
        else:
            record.update(status="pending_source", reason="Author/institution full text being located")
            return record
        text_path = ROOT / "text" / (name + ".txt")
        text_path.write_text("\n\n".join(f"=== PDF PAGE {i+1} ===\n{t}" for i,t in enumerate(pages)), encoding="utf-8")
        record.update(status="available", pdf=target.relative_to(ROOT).as_posix(),
                      text=text_path.relative_to(ROOT).as_posix(), pages=len(pages),
                      bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                      first_page_excerpt=pages[0][:700])
    except Exception as exc:
        record.update(status="failed", error=str(exc))
    return record

def main():
    logging.getLogger("pypdf").setLevel(logging.ERROR)
    for sub in ["papers", "text", "notes", "page_checks"]:
        (ROOT / sub).mkdir(exist_ok=True)
    records = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(acquire, row): row[0] for row in CATALOG}
        for future in as_completed(futures):
            record = future.result()
            records.append(record)
            print(record["id"], record["status"], record.get("pages", ""), flush=True)
            save(records)
    save(records)

def save(records):
    payload = dict(scope="24 discussed and foundational papers plus one previously located universality paper",
                   updated_utc=datetime.now(timezone.utc).isoformat(),
                   papers=sorted(records, key=lambda r:r["id"]))
    (ROOT / "DOWNLOAD_MANIFEST.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")

if __name__ == "__main__":
    main()
