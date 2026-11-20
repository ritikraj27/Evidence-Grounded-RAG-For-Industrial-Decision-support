"""The population of malformed question stems, harvested from the corpus.

Two experiments use it and must use the *same* population, or their numbers
are not comparable: `run_form_probe.py` measures what the confidence gate
does with these queries, and `run_form_validator.py` measures what the
runtime form check does with them. So the harvest lives here.

The stems are not invented. They are the question stems the benchmark's own
generator produced and then rejected under `_subject_is_usable` -- the
fragments it emits by matching mid-clause or after a truncated word. The
harvest re-runs the generator's extraction over the corpus and keeps exactly
the candidates its own quality filter discards.

One thing the population is not: a set of malformed questions. Most of the
stems it contains are perfectly good questions -- the generator's filter
rejects a subject for eight different reasons and six of them are cosmetic
("FMEA" for being one word, "root-cause analysis" for the hyphen, "pick and
pack warehousing" for ending in "-ing"). `run_form_validator.py` labels the
stems by hand, and that labelling is what turns this population into
something the rates can be computed over.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import build_benchmark as bb  # noqa: E402

from src.config import CORPUS_DIR  # noqa: E402
from src.ingestion import ingest_corpus  # noqa: E402


def harvest_stems(corpus_dir=None) -> list[dict]:
    """Every question stem the generator emits and then rejects.

    Returns one dict per stem, with the query the generator would have
    emitted and the subject it was rejected on. The subject matters: the
    generator's rule is a rule about subjects, so the counterfactual --
    "what if the runtime check had reused that rule?" -- is defined on it.
    """
    corpus_dir = corpus_dir or CORPUS_DIR
    found: list[dict] = []
    seen: set[str] = set()
    for chunk in ingest_corpus(corpus_dir):
        for sent in bb._sentences(chunk.text):
            m = bb.DEFINITION_RE.search(sent)
            if m:
                subject, copula = m.group(1).strip(), m.group(2)
                if len(subject.split()) <= 7 and not bb._subject_is_usable(subject):
                    q = f"What {copula} {bb._subject_for_question(subject)}?"
                    if q not in seen:
                        seen.add(q)
                        found.append({"query": q, "subject": subject,
                                      "family": "definition"})
            m = bb.NUMERIC_RE.search(sent)
            if m:
                subject = m.group(1).strip()
                if len(subject.split()) <= 6 and not bb._subject_is_usable(subject):
                    q = bb.clean_query(
                        f"What value is stated for "
                        f"{bb._subject_for_question(subject)} in the "
                        f"source documentation?")
                    if q not in seen:
                        seen.add(q)
                        found.append({"query": q, "subject": subject,
                                      "family": "numeric"})
    return found
