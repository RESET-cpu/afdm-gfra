"""Apply the author's accepted terminology edits, with exact before-state checks."""
from pathlib import Path
import difflib
import hashlib
import json
import re

RUN = Path(__file__).resolve().parent
PAPER = RUN.parents[1]
baseline = json.loads((RUN / "BASELINE.json").read_text(encoding="utf-8"))
changes = {}

def replace(text, old, new, count=1):
    assert text.count(old) == count, (old, text.count(old), count)
    return text.replace(old, new)

for rel in ["main.tex"] + [s + ".tex" for s in baseline["active_inputs"]]:
    p = PAPER / rel
    before = p.read_bytes()
    assert hashlib.sha256(before).hexdigest() == baseline["files"][rel], rel
    # Preserve each file's existing line ending convention.
    newline = "\r\n" if b"\r\n" in before else "\n"
    text = before.decode("utf-8").replace("\r\n", "\n")
    original = text
    for old, new in [("terminals", "devices"), ("terminal", "device"),
                     ("Terminals", "Devices"), ("Terminal", "Device")]:
        text = re.sub(r"\b" + old + r"\b", new, text)
    text = text.replace("pre-compensation", "precompensation")
    text = text.replace("pre-compensate", "precompensate")
    text = text.replace("sub-carriers", "subcarriers").replace("sub-carrier", "subcarrier")
    text = text.replace("mean network", "channel denoiser")
    text = text.replace("channel network", "channel denoiser")
    text = text.replace("mean-network passes", "channel-denoiser passes")
    text = text.replace("user-count", "device-count").replace("User-Count-Specific", "Device-Count-Specific")
    text = text.replace("all user counts", "all candidate device counts")
    if rel == "main.tex":
        text = replace(text, "denotes a proper complex Gaussian law.",
                       "denotes a proper complex Gaussian law \\cite{neeser1993}.")
    if rel.endswith("01_introduction.tex"):
        text = replace(text, "identifies active users", "identifies active devices")
    if rel.endswith("02_system_model.tex"):
        text = replace(text, "maximum channel delay spread", "maximum differential delay")
    if rel.endswith("06_simulation_results.tex"):
        text = replace(text, "AFDM block length $N$", "Number of chirp subcarriers $N$")
        text = replace(text, "Residual-delay support", "Differential-delay range")
        text = replace(text, "The first-order network uses Adam", "The channel denoiser uses Adam")
        text = replace(text, "denoiser is trained with a covariance-weighted loss.",
                       "denoiser is trained using the loss in \\eqref{eq:first-loss}.")
        text = replace(text,
                       "balanced binary cross-entropy, batch size $32$, initial learning rate\n"
                       "$3\\times10^{-4}$, and $100$ epochs, with the checkpoint selected by validation.\n"
                       "Its training queries use $C=v\\I$ and the frozen conditional-mean features.\n"
                       "The receiver evaluations also use this scalar query covariance.",
                       "binary cross-entropy with equally likely active and inactive training labels.\n"
                       "It uses a batch size of $32$, an initial learning rate of $3\\times10^{-4}$,\n"
                       "and $100$ epochs, with the checkpoint selected by validation.\n"
                       "The classifier uses inputs generated with noise covariance $C=v\\I$\n"
                       "and features from the frozen channel denoiser. Receiver evaluations\n"
                       "use the same covariance form.")
        text = replace(text, "cross-channel comparisons", "cross-profile comparisons")
        text = replace(text, "Effect of User Count", "Effect of Candidate Device Count")
        text = replace(text, "Effect of Activity Probability", "Effect of Nominal Activity Probability")
        text = replace(text, "Comparison Across Channel Models", "Comparison Across Channel Profiles")
        text = replace(text, "channel models D, A, B, and C", "NTN-TDL profiles D, A, B, and C")
        text = replace(text, "$24$ channel--SNR", "$24$ profile--SNR")
    if rel.endswith("appendix_afdm_channel_model.tex"):
        text = replace(text,
                       "For normalized time $\\xi$, define\n"
                       "$w_\\xi=\\langle\\xi\\rangle_N$ and\n"
                       "$\\zeta_n(w)=\\lfloor2c_1w+n/N\\rfloor$.\n"
                       "The AFDM basis waveform with frequency wrapping \\cite{huang2026}\n"
                       "and chirp-periodic extension \\cite{bemani2022} is",
                       "Fractional-delay AFDM channels are considered in \\cite{huang2026}.\n"
                       "To specify the waveform between sample times, for normalized time\n"
                       "$\\xi$, define $w_\\xi=\\langle\\xi\\rangle_N$ and\n"
                       "$\\zeta_n(w)=\\lfloor2c_1w+n/N\\rfloor$. We use the AFDM basis waveform")
        text = replace(text, "\\eqref{eq:cpp}. This specifies the waveform between sample times,\n"
                       "which is required for evaluating a noninteger delay.",
                       "\\eqref{eq:cpp} \\cite{bemani2022}. This waveform is used to evaluate\n"
                       "a noninteger delay.")
    if text != original:
        p.write_bytes(text.replace("\n", newline).encode("utf-8"))
        changes[rel] = "".join(difflib.unified_diff(original.splitlines(True), text.splitlines(True),
                                                  fromfile="before/" + rel, tofile=rel))

p = PAPER / "references.bib"
assert hashlib.sha256(p.read_bytes()).hexdigest() == baseline["files"]["references.bib"]
original = p.read_text(encoding="utf-8")
assert "neeser1993" not in original
entry = r'''
@article{neeser1993,
  author = {Fredy D. Neeser and James L. Massey},
  title = {Proper Complex Random Processes with Applications to Information Theory},
  journal = {IEEE Transactions on Information Theory},
  volume = {39},
  number = {4},
  pages = {1293--1302},
  year = {1993},
  month = jul,
  doi = {10.1109/18.243446},
  url = {https://www.isiweb.ee.ethz.ch/archive/massey_pub/pdf/BI437.pdf}
}
'''
with p.open("a", encoding="utf-8", newline="") as out:
    out.write(entry.replace("\n", "\r\n") if b"\r\n" in p.read_bytes() else entry)
changes["references.bib"] = "".join(difflib.unified_diff(original.splitlines(True), (original + entry).splitlines(True),
                                                     fromfile="before/references.bib", tofile="references.bib"))
(RUN / "MANUSCRIPT.diff").write_text("\n".join(changes.values()), encoding="utf-8")
print(json.dumps({"changed_files": list(changes), "acronym_expansions_added": False}))
