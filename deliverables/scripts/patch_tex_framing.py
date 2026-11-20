#!/usr/bin/env python3
"""Apply the reframing to the two LaTeX papers.

Same three moves as the technical report: reframe the contribution around the
measurement, add the corpus characterisation to the abstract, and state the
label correction where the protocol is defined.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
T = ROOT / "deliverables" / "templates"

# --------------------------------------------------------------------------
# IEEE paper
# --------------------------------------------------------------------------
IEEE_OLD_CONTRIB = """We propose a framework with five mechanisms and evaluate it. We state the
contribution in three parts because they differ in strength. The
\\emph{architectural} contribution is incremental: the mechanisms have published
prior art, which we position against explicitly rather than claim priority
over. The \\emph{empirical} contribution is a failure-mode characterisation,
including two results that contradict the framework's original specification.
The \\emph{methodological} contribution is an evaluation protocol that treats
the confidence gate as a selective-prediction policy, reporting a
risk--coverage curve and a false-positive rate at a stated operating point
with always-flag and never-flag baselines."""

IEEE_NEW_CONTRIB = """We measure which reliability mechanisms pay for themselves in industrial text,
and report where they break. The contribution is stated in three parts, in that
order deliberately: the measurement is the contribution, not the architecture.
The \\emph{architectural} contribution is incremental, and by late 2026 the closest
prior art is close enough that the architecture cannot be the argument --- a
code-level, pre-generation gate with a calibrated decision policy is published
(Sieve and Sage; BITEM; HALT-RAG), set-level sufficiency verification and
structural certificates are published (SURE-RAG; Certify), and the argument that
modality routing is performed at the wrong decision point is published
(Modality Relevance is not Modality Utility). We position ours against that
prior art explicitly rather than claim priority over it. The \\emph{empirical}
contribution is a failure-mode characterisation, and several of its results are
negative: the modality quota is a trade and not a gain, the dense leg can cost
recall when fused with a strong lexical leg on a corpus whose questions are
derived from the documents themselves, and the confidence gate cannot separate
absence of evidence from retrieval failure, so it is an answer-in-context
detector rather than a sufficiency judge. The \\emph{methodological} contribution
is an evaluation protocol that treats the confidence gate as a
selective-prediction policy, reporting a risk--coverage curve and a
false-positive rate at a stated operating point against the two degenerate
policies --- never refuse and always refuse --- as baselines, rather than the
endpoints of the threshold sweep, which are not baselines."""

IEEE_OLD_ABSTRACT = """We identify two design properties that the original specification had wrong --- a
modality quota binds only when applied \\emph{after} the reranker rather than
before it, and a category pre-filter applied to only one of two retrieval legs
is a no-op."""

IEEE_NEW_ABSTRACT = """We identify design properties that the original specification had wrong --- a
category pre-filter applied to only one of two retrieval legs is a no-op, and a
modality quota binds only when applied \\emph{after} the reranker rather than
before it. We state plainly what our corpus is: industrial-engineering
\\emph{encyclopaedic} text from English Wikipedia, shipped in full with
per-document provenance, and not the operating manuals and supplier
specifications a practitioner actually uses; claims that depend on such
documents are not made."""

# --------------------------------------------------------------------------
# Journal paper
# --------------------------------------------------------------------------
JOURNAL_OLD_CONTRIB_MARK = "### 1.4 Contributions"  # placeholder, replaced below
JOURNAL_OLD_ABSTRACT = """The framework is evaluated on an independently constructed public industrial corpus of {{N_CHUNKS_TEX}}
chunks spanning {{N_CATEGORIES_WORD}} categories, with a {{N_QUERIES}}-query silver-standard benchmark
that includes a deliberate unanswerable class, with supply chain management as the
single industrial domain the work focuses on."""

JOURNAL_NEW_ABSTRACT = """The framework is evaluated on an independently constructed public industrial corpus of {{N_CHUNKS_TEX}}
chunks spanning {{N_CATEGORIES_WORD}} categories, with a {{N_QUERIES}}-query silver-standard benchmark
that includes a deliberate unanswerable class, with supply chain management as the
single industrial domain the work focuses on. The corpus is industrial-engineering
\\emph{encyclopaedic} text from English Wikipedia, shipped in full with per-document
provenance; it is not the operating manuals, control plans and supplier
specifications a practitioner actually uses, and claims that depend on such
documents are not made."""


def sub(path: Path, old: str, new: str) -> bool:
    s = path.read_text(encoding="utf-8")
    if s.count(old) != 1:
        print(f"!! {path.name}: count={s.count(old)} -> {old[:60]!r}")
        return False
    path.write_text(s.replace(old, new, 1), encoding="utf-8")
    return True


def main() -> int:
    ok = True
    ieee = T / "Deliverable_2b_IEEE_Conference_Paper.tex"
    ok &= sub(ieee, IEEE_OLD_CONTRIB, IEEE_NEW_CONTRIB)
    ok &= sub(ieee, IEEE_OLD_ABSTRACT, IEEE_NEW_ABSTRACT)

    jour = T / "Deliverable_2c_Journal_Style_Paper.tex"
    ok &= sub(jour, JOURNAL_OLD_ABSTRACT, JOURNAL_NEW_ABSTRACT)

    print("\nall replacements applied" if ok else "\nsome replacements failed")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
