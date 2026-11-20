#!/usr/bin/env python3
"""Build the industrial benchmark (RO6).

Label standard: SILVER, corpus-anchored -- the same standard as the
existing benchmarks, with two differences forced by the corpus.

**The same standard.** Answerable questions are derived mechanically from the
document that answers them, so a gold chunk is guaranteed to contain the
answer somewhere. The bias this introduces is stated wherever the numbers are
reported. Unanswerable questions are drawn from the same stems, from the same
documents, and labelled by the complement of the answerable extraction tests,
so the two classes differ in one respect only: whether the corpus states the
answer.

**The differences.** The existing benchmark's extraction patterns were written
against Wikipedia prose. Applied to regulatory text they produce questions no
practitioner would ask:

* every table question asks for the *next* column, which in the air-contaminant
  tables is always "CAS No. (c)" -- 486 questions that test one column;
* the numeric branch captures a clause rather than a subject, so the questions
  read "What value is stated for only for a maximum period in the source
  documentation?";
* the definition branch matches mid-clause, so the questions read "What is
  because inorganic arsenic?".

So this module writes extraction patterns for the register a regulation is
written in, while keeping the *label standard* -- mechanical, corpus-derived,
reproducible, and no more optimistic than the existing one. It reuses the
existing corpus-anchored unanswerable generator unchanged; that module is
corpus-agnostic by design and it works.

Two further decisions:

* **Column diversity.** The table family is capped per (document, column), so
  the benchmark covers the tables it draws from rather than one column of one
  table a thousand times.
* **The out-of-domain unanswerable class is the thesis's own original
  domain.** The existing benchmark's out-of-domain class asks about vitamin D
  and the 1998 FIFA final, which a question-only classifier separates from
  the industrial corpus trivially. This one asks about the industrial
  engineering topics the framework was originally built for -- economic order
  quantity, safety stock, Six Sigma, takt time, ASME Section IX -- none of
  which a federal *regulation* contains. The class is therefore drawn from
  the corpus's own subject area, and a system that refuses on the shape of
  the question rather than on the evidence has nothing to hide behind.

Usage:
    MTP_VARIANT=industrial python scripts/build_industrial_benchmark.py
"""
from __future__ import annotations

import json
import os
import random
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

os.environ.setdefault("MTP_VARIANT", "industrial")

import build_benchmark as bb  # noqa: E402
import unanswerable_repair as ur  # noqa: E402
from src.config import BENCHMARK_DIR, CORPUS_DIR  # noqa: E402
from src.ingestion import ingest_corpus  # noqa: E402

SEED = 20261118

#: How many questions to draw from each answerable family.
N_DEFINITION = 110
N_NUMERIC = 90
N_TABLE = 130

#: How many corpus-anchored and out-of-domain unanswerable questions.
N_UNANSWERABLE_ANCHORED = 150
N_UNANSWERABLE_OOD = 50

#: Cap on table questions per (document, column). Without it, one column of
#: one table fills the family.
MAX_PER_COLUMN = 12


# --------------------------------------------------------------------------
# out-of-domain unanswerable questions
# --------------------------------------------------------------------------
#: Industrial engineering topics that a federal regulation does not contain.
#: These are the questions the framework was originally built for, asked of a
#: corpus that does not answer them.
OOD_QUESTIONS = [
    "What is the economic order quantity for a purchased part?",
    "What safety stock level should be held for a slow-moving spare?",
    "What are the six sigma belt definitions used in a quality programme?",
    "What is the takt time for a production line with a given demand?",
    "What cycle time should a workstation be designed for?",
    "What is the lead time for an outsourced component?",
    "How is the bill of materials for an assembly structured?",
    "What is the theory of constraints applied to a production system?",
    "What does the kanban method require of the pull system?",
    "What is just-in-time purchasing in a supply chain?",
    "What is the material requirements planning lot-sizing rule?",
    "What is the total productive maintenance approach to equipment care?",
    "What is the overall equipment effectiveness metric composed of?",
    "What is a failure mode and effects analysis used for?",
    "What is the standard work instruction for a machine operator?",
    "What is the little's law relationship between utilisation and queue length?",
    "What is the line balancing takt constraint for a mixed model line?",
    "What is a value stream mapping exercise?",
    "What is the difference between a forecast and a demand plan?",
    "What is the policy for strategic sourcing of a new supplier?",
    "How is a third party logistics provider selected and evaluated?",
    "What is the standard qualification procedure for a welding procedure?",
    "What is the qualification requirement for a brazing operator?",
    "What is the required forging die temperature for a given alloy?",
    "What is the standard casting defect acceptance tolerance?",
    "What is the heat treatment specification for a given steel grade?",
    "What is the surface roughness requirement for a machined bore?",
    "What is the tolerance grade for a turned shaft dimension?",
    "What is the recommended maintenance interval for a centrifugal pump bearing?",
    "What is the vibration acceptance criterion for a rotating machine bearing?",
    "What is the thermodynamic efficiency of a given steam turbine stage?",
    "What is the heat transfer coefficient of an insulated pipe wall?",
    "What is the pressure drop across a pipe fitting at a given flow rate?",
    "What is the network model of a multi-echelon inventory system?",
    "What is the queueing delay at a single server under Poisson arrivals?",
    "What is the cost of holding one unit of inventory for a year?",
    "What is the service level target of an ABC inventory policy?",
    "What is the scrap rate target of a pilot production run?",
    "What is the machine learning accuracy of a predictive maintenance model?",
    "What is the standard deviation of a measurement process capability index?",
    "What is the coefficient of variation of a batch of measurements?",
    "What is the number of control chart limits used for a six sigma process?",
    "What is the detection limit of an analytical instrument?",
    "What is the wavelength of light used in a spectrophotometer?",
    "What is the concentration of a solution prepared from a stock standard?",
    "What is the throughput of a bottling line at a stated speed?",
    "What is the changeover time between two product families?",
    "What is the OEE availability factor of a plant at a given uptime?",
    "What is the standard working week used for a headcount calculation?",
]


# --------------------------------------------------------------------------
# quality filters
# --------------------------------------------------------------------------
#: Words that cannot end a subject phrase.
_BAD_TAIL = frozenset("""
the a an of in on at to for and or but with by from as this that these those
its their his her our your my not no also than into onto over under about
after before between during through against within is are was were be been
has have had will would could should shall must may can any all both each
such same other others many most more less new old such than then when
where while because if so such per via which who whom whose what how
""".split())

#: Words that cannot begin a subject phrase.
_BAD_HEAD = frozenset("""
the a an of in on at to for and or but with by from as this that these those
is are was were has have had will would could should shall must may can
because when where while if so such each any all both no not
""".split())

#: A subject must not contain these: they mark a requirement rather than a
#: term being defined, and a question about a requirement is not a question a
#: practitioner asks of a glossary.
_REQUIREMENT_WORDS = frozenset("""
shall must employer employee owner operator manufacturer user installer
supplier carrier shipper packer facility workplace
""".split())

#: Demonstratives that the generic definition pattern happily captures.
_DEMONSTRATIVE = frozenset("""
latter former above below following preceding subsequent such same
""".split())


def _clean_subject(subject: str) -> str | None:
    """Return the subject if it reads like a noun phrase a person would ask
    about, and None otherwise."""
    subject = subject.strip(" ,;:.()")
    if len(subject) < 3 or len(subject) > 70:
        return None
    words = subject.split()
    if len(words) < 1 or len(words) > 8:
        return None
    lowered = [w.lower().strip(",;:'\"()") for w in words]
    if not all(lowered):
        return None
    if lowered[-1] in _BAD_TAIL:
        return None
    if lowered[0] in _BAD_HEAD:
        return None
    if lowered[-1] in _DEMONSTRATIVE:
        return None
    if any(w in _REQUIREMENT_WORDS for w in lowered):
        return None
    # A subject is either a noun phrase of at least two words, or an
    # acronym. One ordinary word ("use", "crusher") is too thin to be a
    # question worth asking, and "any matrix" is not a noun phrase at all.
    is_acronym = len(words) == 1 and words[0].isupper() and len(words[0]) >= 2
    if len(words) < 2 and not is_acronym:
        return None
    if any(w in ("any", "all", "such", "one", "some") for w in lowered):
        return None
    # Every word must be a word, not a number or a unit.
    if not all(w.replace("-", "").replace("/", "").replace("(", "").isalpha()
               or re.match(r"^[A-Z][A-Za-z0-9\-/()]*$", w) for w in words):
        return None
    return subject


def _question_subject(subject: str) -> str:
    """Render a subject for a question, preserving the case of acronyms."""
    words = subject.split()
    if not words:
        return subject
    if words[0].lower() in ("the", "a", "an"):
        return subject[:1].lower() + subject[1:]
    if any(len(w) >= 2 and w.isalpha() and w.isupper() for w in words):
        return subject
    return subject[:1].lower() + subject[1:]


# --------------------------------------------------------------------------
# answerable extraction
# --------------------------------------------------------------------------
#: "X means ...", "X is defined as ...", "X refers to ...", "X is any ...".
#: These are the forms a regulation uses to define a term. The generic
#: benchmark pattern only recognises "X is a/an/the ...", which on regulatory
#: text finds a fifth of what is there.
_DEFINITION_PATTERNS = [
    re.compile(r"^(?P<subject>[A-Z][^.;:]{1,70}?)\s+(?:means|refers to)\s+"
               r"(?P<answer>[^.;]{15,300})"),
    re.compile(r"^(?P<subject>[A-Z][^.;:]{1,70}?)\s+is defined (?:as|to be|to "
               r"mean|for)\s+(?P<answer>[^.;]{15,300})"),
    re.compile(r"^(?P<subject>[A-Z][^.;:]{1,70}?)\s+is (?:any|either)\s+"
               r"(?P<answer>[^.;]{15,300})"),
    re.compile(r"^(?P<subject>[A-Z][^.;:]{1,70}?)\s+is\s+(?:a|an|the)\s+"
               r"(?P<answer>[^.;]{15,300})"),
]

#: The units a regulatory limit is expressed in. The list is a declared
#: vocabulary, not a fitted one: the unit is what makes a number a
#: *measurement* rather than a count, a year or a section number.
_UNITS = [
    "micrograms per cubic meter", "milligrams per cubic meter",
    "grams per cubic meter", "parts per million", "pounds per square inch",
    "pounds per hour", "square feet", "square inches", "cubic feet",
    "cubic meters", "degrees fahrenheit", "degrees celsius", "percent",
    "ppm", "psig", "psi", "inches", "inch", "feet", "foot", "miles",
    "hours", "hour", "days", "day", "months", "month", "years", "year",
    "minutes", "minute", "seconds", "second", "volts", "volt", "amperes",
    "watts", "decibels", "db", "pounds", "kilograms", "tons", "gallons",
    "liters", "degrees", "parts", "units", "grams", "litres",
]
_UNIT_RE = "|".join(re.escape(u) for u in sorted(_UNITS, key=len, reverse=True))

#: A number with an optional unit, for the numeric family. The value is
#: captured as a number followed by a unit from the vocabulary above, because
#: a regulatory limit names its unit in full ("5 micrograms per cubic meter")
#: and a regex that stops at the first word would miss most of them.
_NUM_VALUE = re.compile(
    r"^(?P<num>\d[\d,]*(?:\.\d+)?(?:/\d+)?)\s*"
    r"(?P<unit>" + _UNIT_RE + r")?$", re.IGNORECASE)

#: A value whose unit is a bare number is too generic to be an answer unless
#: it carries a unit.
_GENERIC_VALUE = re.compile(r"^\d{1,3}$")

#: The limit verb and the value that follows it.
_LIMIT_RE = re.compile(
    r"\b(?:shall not exceed|must not exceed|may not exceed|does not exceed|"
    r"do not exceed|not exceed|shall not be greater than|"
    r"shall not be more than|must not be greater than|"
    r"is limited to|are limited to|shall be no|must be no|"
    r"is|are)\s+"
    r"(?P<num>\d[\d,]*(?:\.\d+)?(?:/\d+)?)\s*"
    r"(?P<unit>" + _UNIT_RE + r")\b")

#: Words trimmed from the left of a candidate subject until the subject is a
#: noun phrase rather than a clause.
_LEADING_TRIM = frozenset("""
the a an of in on at to for and or but with by from as this that these those
is are was were be been being shall must may can could would should will
has have had do does did ensure ensures ensuring provide provides providing
when where while if unless because since so such each any all both
""".split())


def _sentences(text: str) -> list[str]:
    """Well-formed sentences, with the leading caption markers removed."""
    out: list[str] = []
    for part in re.split(r"(?<=[.!?])\s+", text):
        part = part.strip()
        part = re.sub(r"^\[.*?\]\s*", "", part)
        part = re.sub(r"^\*\*", "", part)
        if len(part) < 40 or len(part.split()) < 8:
            continue
        if not part[:1].isupper():
            continue
        out.append(part)
    return out


def definition_questions(chunks, rng: random.Random) -> list[dict]:
    """'What is X?' for terms the document defines."""
    out: list[dict] = []
    seen: set[str] = set()
    for ch in chunks:
        if ch.modality == "table":
            continue
        for sent in _sentences(ch.text):
            for pattern in _DEFINITION_PATTERNS:
                m = pattern.match(sent)
                if not m:
                    continue
                subject = _clean_subject(m.group("subject"))
                answer = m.group("answer").strip()
                if subject is None:
                    continue
                if len(answer.split()) < 4:
                    continue
                if answer[0].isupper() and answer.split()[0] in _REQUIREMENT_WORDS:
                    continue
                query = bb.clean_query(
                    f"What is {_question_subject(subject)}?")
                if query in seen:
                    continue
                seen.add(query)
                out.append({
                    "query": query,
                    "gold": [ch.chunk_id],
                    "category": ch.category,
                    "family": "definition",
                    "modality_target": "text",
                    "answer": answer[:220],
                })
                break
    rng.shuffle(out)
    # Spread the family over the corpus rather than taking the first few
    # documents that happen to sort early.
    out.sort(key=lambda r: (r["category"], r["query"]))
    rng.shuffle(out)
    return out


def _trailing_subject(prefix: str) -> str | None:
    """The noun phrase immediately before a limit verb.

    A regulatory limit sentence usually opens with a condition rather than
    with the quantity: "The employer shall ensure that exposure to airborne
    asbestos fibers does not exceed 0.2 fibers per cubic centimeter". The
    subject of the question is "exposure to airborne asbestos fibers", which
    is the trailing noun phrase before the verb, not the sentence's opening
    clause. Taking the clause produces the question "What value is stated
    for the employer shall ensure that exposure to airborne asbestos fibers
    in the source documentation?", which nobody asks.
    """
    words = prefix.rstrip().split()
    if not words:
        return None
    candidate = words[-8:]
    # Trim from the left until the phrase starts on a content word.
    while candidate:
        head = candidate[0].lower().strip(",;:()[]\"'")
        if head in _LEADING_TRIM or head in _REQUIREMENT_WORDS:
            candidate = candidate[1:]
            continue
        break
    if not candidate:
        return None
    return _clean_subject(" ".join(candidate))


def numeric_questions(chunks, rng: random.Random) -> list[dict]:
    """'What value is stated for X in the source documentation?'"""
    out: list[dict] = []
    seen: set[str] = set()
    for ch in chunks:
        if ch.modality == "table":
            continue
        for sent in _sentences(ch.text):
            hit = None
            for m in _LIMIT_RE.finditer(sent):
                subject = _trailing_subject(sent[:m.start()])
                if subject is None:
                    continue
                if re.search(r"\d", subject):
                    # A subject that reads "for a 1.6 mg/m3 exposure" has the
                    # answer in it.
                    continue
                unit = m.group("unit")
                value = f"{m.group('num')} {unit}".strip() if unit \
                    else m.group("num")
                if not unit and _GENERIC_VALUE.match(value):
                    continue
                hit = (subject, value)
                break
            if not hit:
                continue
            subject, value = hit
            query = bb.clean_query(
                f"What value is stated for {_question_subject(subject)} "
                f"in the source documentation?")
            if query in seen:
                continue
            seen.add(query)
            out.append({
                "query": query,
                "gold": [ch.chunk_id],
                "category": ch.category,
                "family": "numeric_fact",
                "modality_target": "text",
                "answer": value[:120],
            })
    rng.shuffle(out)
    out.sort(key=lambda r: (r["category"], r["query"]))
    rng.shuffle(out)
    return out


def _table_rows(text: str) -> tuple[list[str], list[list[str]]]:
    """The header and body rows of a markdown table chunk."""
    lines = [ln for ln in text.splitlines() if ln.strip().startswith("|")]
    if len(lines) < 3:
        return [], []

    def cells(line: str) -> list[str]:
        return [c.strip() for c in line.strip().strip("|").split("|")]

    header = cells(lines[0])
    if len(header) < 2 or all(set(c) <= set("-: ") for c in header):
        return [], []
    rows = []
    for line in lines[1:]:
        r = cells(line)
        if len(r) == len(header):
            rows.append(r)
    return header, rows


def _distinctive(value: str) -> bool:
    """Is this cell a value a practitioner could quote?"""
    v = value.strip()
    if not v or len(v) > 80:
        return False
    if v in {"-", "--", "—", "N/A", "NA", "See footnote"}:
        return False
    if len(v) < 2:
        return False
    if set(v) <= set("-: ."):
        return False
    return True


def _readable_row_label(key: str) -> bool:
    """Is this row label something a person would name in a question?

    A regulatory table's first column holds three kinds of thing: a name
    ("Acetaldehyde"), a size ("3/8"), and a code ("CCCC"). Only the first
    makes a question, and the other two produce the nonsense rows the
    generic generator produces: "what is the Nominal outside diameter for
    3/8?".
    """
    key = key.strip()
    if len(key) < 3 or len(key) > 60:
        return False
    if not re.search(r"[A-Za-z]{3}", key):
        return False
    if re.match(r"^[\d\s./,°-]+$", key):
        return False
    if not all(ch.isalnum() or ch in " .,-()/&'°%" for ch in key):
        return False
    return True


def table_questions(chunks, rng: random.Random) -> list[dict]:
    """'According to the table ..., what is the {column} for {row}?'

    One question per (document, column) is capped, and the column is drawn
    at random among the informative ones, so the family tests the tables it
    comes from rather than one column of one table.
    """
    out: list[dict] = []
    seen: set[str] = set()
    per_column: Counter = Counter()
    for ch in chunks:
        if ch.modality != "table":
            continue
        header, rows = _table_rows(ch.text)
        if not header:
            continue
        candidates: list[tuple[int, int]] = []
        for ri, row in enumerate(rows):
            for ci in range(len(header)):
                if ci >= len(row):
                    continue
                key, value = row[0], row[ci]
                if ci == 0:
                    continue
                if not _distinctive(value):
                    continue
                if not bb._clean_label(header[ci], 4):
                    continue
                if not bb._clean_label(key, 5):
                    continue
                if not _readable_row_label(key):
                    continue
                if value == header[ci]:
                    continue
                candidates.append((ri, ci))
        if not candidates:
            continue
        rng.shuffle(candidates)
        for ri, ci in candidates:
            key = rows[ri][0]
            value = rows[ri][ci]
            column = header[ci]
            bucket = (ch.doc_id, column)
            if per_column[bucket] >= MAX_PER_COLUMN:
                continue
            query = bb.clean_query(
                f"According to the table in the source document, what is the "
                f"{column} for {key}?")
            if query in seen:
                continue
            seen.add(query)
            per_column[bucket] += 1
            out.append({
                "query": query,
                "gold": [ch.chunk_id],
                "category": ch.category,
                "family": "table_lookup",
                "modality_target": "table",
                "answer": value[:120],
            })
    rng.shuffle(out)
    return out


# --------------------------------------------------------------------------
def _drop_failing_certificates(chunks, records: list[dict]
                               ) -> tuple[list[dict], int]:
    """Drop the repaired questions whose certificate does not hold.

    The check is the audit's own `_verify_certificates`, re-derived from the
    corpus with a predicate written independently of the generator that
    wrote the certificate. Reusing it rather than reimplementing it means
    the benchmark and the audit cannot drift apart.
    """
    sys.path.insert(0, str(ROOT / "experiments"))
    from audit_unanswerable_class import _verify_certificates

    probe = {"queries": records}
    result = _verify_certificates(probe)
    failing = {f["query"] for f in result.get("failures", [])}
    if not failing:
        return records, 0
    kept = [r for r in records if r["query"] not in failing]
    return kept, len(records) - len(kept)


def main() -> int:
    rng = random.Random(SEED)
    print("[bench] ingesting the industrial corpus ...", flush=True)
    chunks = ingest_corpus(CORPUS_DIR)
    if not chunks:
        print("No chunks found. Run build_industrial_corpus.py first.",
              file=sys.stderr)
        return 1
    print(f"[bench] {len(chunks)} chunks ingested", flush=True)

    defs = definition_questions(chunks, rng)
    nums = numeric_questions(chunks, rng)
    tabs = table_questions(chunks, rng)
    print(f"[bench] candidates: definition={len(defs)} numeric={len(nums)} "
          f"table={len(tabs)}", flush=True)

    answerable = (defs[:N_DEFINITION] + nums[:N_NUMERIC] + tabs[:N_TABLE])
    by_family = {
        "definition": defs[:N_DEFINITION],
        "numeric_fact": nums[:N_NUMERIC],
        "table_lookup": tabs[:N_TABLE],
    }

    print("[bench] corpus-anchored unanswerable class ...", flush=True)
    # The repaired class is matched against *this* corpus's answerable
    # class, not against a replay of the benchmark's own generator: the
    # shape matching (stem, structural features, subject-length quantiles)
    # is only meaningful against the class the repaired questions will be
    # compared with.
    anchored = ur.generate(chunks, n=N_UNANSWERABLE_ANCHORED, seed=SEED,
                           answerable=by_family)
    print(f"[bench] corpus-anchored unanswerable queries: {len(anchored)}",
          flush=True)

    # Every repaired question's certificate is re-checked, independently of
    # the generator that wrote it, and any that fails is dropped. A question
    # whose certificate does not hold is a question the corpus can answer,
    # and leaving it in the unanswerable class would be exactly the defect
    # the audit exists to catch.
    anchored, n_dropped = _drop_failing_certificates(chunks, anchored)
    print(f"[bench] dropped {n_dropped} unanswerable questions whose "
          f"certificate did not hold", flush=True)

    ood = [
        {
            "query": q,
            "gold": [],
            "category": "unanswerable",
            "family": "unanswerable_ood",
            "modality_target": None,
            "answer": None,
            "label_certificate": (
                "the question asks about an industrial engineering topic -- a "
                "production, inventory or maintenance method -- that a "
                "federal regulatory corpus does not contain; the corpus "
                "contains binding requirements, not the methods behind them"),
        }
        for q in OOD_QUESTIONS
    ]

    records = answerable + anchored + ood
    rng.shuffle(records)

    families: Counter = Counter()
    categories: Counter = Counter()
    for r in records:
        families[r["family"]] += 1
        categories[r["category"]] += 1

    BENCHMARK_DIR.mkdir(parents=True, exist_ok=True)
    out_path = BENCHMARK_DIR / "benchmark.json"
    out_path.write_text(json.dumps({
        "label_standard": "silver",
        "seed": SEED,
        "corpus": "InduSight industrial regulatory corpus (eCFR)",
        "n_queries": len(records),
        "n_answerable": len(answerable),
        "n_unanswerable": len(anchored) + len(ood),
        "families": dict(families),
        "categories": dict(categories),
        "queries": records,
    }, indent=2), encoding="utf-8")

    print(f"[bench] wrote {len(records)} queries -> {out_path}")
    print(f"[bench] families: {dict(families)}")
    print(f"[bench] categories: {dict(categories)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
