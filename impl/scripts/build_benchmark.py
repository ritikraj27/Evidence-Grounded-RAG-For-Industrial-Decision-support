#!/usr/bin/env python3
"""Generate the evaluation benchmark from the corpus.

Label standard: SILVER
-----------------------
The thesis's own benchmark (SupplyChainQA v7, 300 queries) is expert-annotated
with Cohen's kappa >= 0.7. That corpus is proprietary, so the shipped
implementation derives a *silver* benchmark from the public corpus instead.
Silver labels are mechanically derived from the document itself rather than
assigned by a human, so they are cheap, perfectly reproducible, and slightly
optimistic in one specific way: the gold chunk is guaranteed to contain the
answer *somewhere*, whereas an expert annotator might have judged the chunk
to be insufficient.

That optimistic bias is stated everywhere the numbers are reported, because it
inflates absolute recall. It does not bias the *comparison* between systems,
which is what the ablation actually tests -- every system is scored against
the same silver labels.

Three question families are generated, and each one tests a different part of
the framework:

1. **Table-derived questions** ("What is the quantity for SKU A-104?").
   These test the modality story: the answer lives in a table, so a
   text-biased retriever will miss it. They are the direct test of design
   move D2.

2. **Definitional questions** ("What is a safety stock?"). These test
   ordinary semantic retrieval and give the hybrid/BM25 leg something to do
   that dense retrieval is strong at.

3. **Unanswerable questions** (questions on topics deliberately absent from
   the corpus). These test design move D1. A system that answers everything
   scores 100% recall and 0% hallucination; the gate exists to convert some
   of those "answers" into correct refusals. Without this family, no
   confidence-gating experiment is meaningful.
"""
from __future__ import annotations

import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import unanswerable_repair  # noqa: E402
from src.ingestion import ingest_corpus  # noqa: E402
from src.config import CORPUS_DIR, BENCHMARK_DIR  # noqa: E402

SEED = 20261118

#: Topics that are certainly not in an industrial-engineering corpus.
#: Used to build the out-of-domain unanswerable set.
UNANSWERABLE_TOPICS = [
    ("What is the recommended daily intake of vitamin D for adults?", "health"),
    ("Who won the 1998 FIFA World Cup final?", "sports"),
    ("What is the boiling point of water at 2000 metres altitude?", "physics"),
    ("How do I convert a PNG file to a JPEG?", "software"),
    ("What was the population of Paris in 1850?", "history"),
    ("What is the molecular weight of sucrose?", "chemistry"),
    ("How do I change the tyre pressure on a bicycle?", "sports"),
    ("What is the average depth of the Mariana Trench?", "geography"),
    ("Who wrote the opera The Magic Flute?", "arts"),
    ("What is the tax rate in a country named Freedonia?", "fiction"),
    ("How do I make sourdough bread rise faster?", "cooking"),
    ("What is the freezing point of ethanol in Fahrenheit?", "chemistry"),
    ("What is the half-life of the isotope carbon-14?", "physics"),
    ("Who painted the ceiling of the Sistine Chapel?", "arts"),
    ("What is the capital city of Mongolia?", "geography"),
    ("How many bones are in the adult human hand?", "biology"),
    ("What is the speed of light in a vacuum?", "physics"),
    ("What is the recommended word count for a college essay?", "education"),
    ("Who was the first person to set foot on Antarctica?", "history"),
    ("What is the chemical formula for table salt?", "chemistry"),
    ("How do I train for a marathon in eight weeks?", "health"),
    ("What is the tallest building in South America?", "geography"),
    ("Who composed the Brandenburg Concertos?", "arts"),
    ("What is the currency of Switzerland?", "finance"),
    ("How do I plant a hedge in a clay soil?", "gardening"),
    ("What is the boiling point of diesel fuel?", "chemistry"),
    ("Which planet has the shortest day?", "astronomy"),
    ("What is the legal age to vote in Japan?", "law"),
    ("How do I remove a coffee stain from a wool sweater?", "cleaning"),
    ("What is the deepest point in the Atlantic Ocean?", "geography"),
    ("Who wrote the play A Doll's House?", "literature"),
    ("What is the rate of photosynthesis in wheat?", "biology"),
    ("How do I weld aluminium to steel?", "fabrication"),
    ("What is the warranty period on a diesel generator?", "other"),
]

#: Near-miss templates. Each asks for a value that the corpus would answer for
#: a *different* identifier, so the surface form is exactly that of an
#: answerable question but the answer is absent. This is the hard case for a
#: confidence gate: a lexical retriever will happily return the passage about
#: SKU A-104 when asked about SKU A-771, and only the gate can stop the system
#: from answering.




def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:60]



_MD_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
_MD_IMAGE = re.compile(r"!\[([^\]]*)\]\([^)]*\)")


def clean_query(text: str) -> str:
    """Strip markdown link and image syntax from a generated query.

    The corpus is markdown, so a question derived from a linked phrase
    carries the raw link markup ("the Person for [Henry Ford](/wiki/...)").
    That is retrieval noise in the query string and would look wrong in a
    report table, so the visible text is kept and the markup dropped.
    """
    text = _MD_IMAGE.sub(r"\1", text)
    text = _MD_LINK.sub(r"\1", text)
    return re.sub(r"\s{2,}", " ", text).strip()

def _clean_label(v: str, max_words: int) -> bool:
    """True when a table cell reads as a label a person could quote.

    A header cell can contain markup -- "the for **How to change?**" -- and a
    row cell can contain a fragment of a sentence. Either produces a lookup
    question with no answer anyone would recognise.
    """
    if not v or len(v) > 60:
        return False
    # Markdown syntax only. Parentheses, slashes and hashes are legitimate
    # in a label ("Mean throughput (units/day)"); asterisks and brackets are
    # not.
    if any(ch in v for ch in "*[]{}|"):
        return False
    words = v.split()
    if not words or len(words) > max_words:
        return False
    lowered = [w.lower().strip(",;:") for w in words]
    if lowered[0] in _BAD_EDGE and lowered[0] not in ("the", "a", "an"):
        return False
    if any(w in _VERB_LIKE for w in lowered):
        return False
    return True


def questions_from_table(text: str, chunk_id: str, category: str, rng: random.Random) -> list[dict]:
    """Derive lookup questions from a markdown table chunk.

    Only informative value cells are used. A cell whose value is "1", "Yes",
    "-" or a single character identifies a *row label* rather than an answer a
    practitioner could quote, so those are skipped -- otherwise the benchmark
    fills up with questions whose gold answer is meaningless.
    """
    out = []
    lines = [ln for ln in text.splitlines() if ln.strip().startswith("|")]
    if len(lines) < 3:
        return out
    def cells(line: str) -> list[str]:
        return [c.strip() for c in line.strip().strip("|").split("|")]

    header = cells(lines[0])
    if len(header) < 2:
        return out
    # Skip separator rows like |---|---|.
    if all(set(c) <= set("-: ") for c in header):
        return out

    UNINFORMATIVE = {
        "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "0", "-", "--",
        "yes", "no", "n/a", "na", "t", "f", "true", "false", "none", "null",
    }

    def informative(val: str) -> bool:
        v = val.strip().lower()
        if not v or v in UNINFORMATIVE:
            return False
        if len(v) < 2:
            return False
        if v.replace(".", "").replace("-", "").isdigit() and len(v) <= 2:
            return False
        return True

    for line in lines[1:]:
        row = cells(line)
        if len(row) != len(header):
            continue
        # Find a row with one distinctive key cell and one informative value.
        for k in range(len(header)):
            key = row[k]
            # The answer is the cell in the NEXT column, so the question must
            # name THAT column. Naming the key's own column asks for the key
            # back, and stores a label that does not match its question --
            # which is how 10 of the benchmark's answer labels came to be
            # attached to the wrong question.
            d = (k + 1) % len(header)
            val = row[d]
            if (
                3 < len(key) <= 60
                and informative(val)
                and val not in header
                and len(val) <= 80
                and not set(val) <= set("-:")
                and _clean_label(header[d], 4)
                and _clean_label(key, 5)
            ):
                q = clean_query(
                    f"According to the table in the source document, what is the "
                    f"{header[d]} for {key}?")
                out.append(
                    {
                        "query": q,
                        "gold": [chunk_id],
                        "category": category,
                        "family": "table_lookup",
                        "modality_target": "table",
                        "answer": val,
                    }
                )
                break
    rng.shuffle(out)
    return out[:2]


#: The copula is captured so the question agrees with the source sentence:
#: "What is problem statements?" is ungrammatical, and "What are problem
#: statements?" is not.
DEFINITION_RE = re.compile(
    r"\b([A-Z][A-Za-z0-9 \-]{3,55}?)\s+(is|are|was|were)\s+"
    r"(?:a|an|the|any|one of)\s+([^.!?]{25,220})"
)

#: The trailing negative lookahead keeps an ordinal out of the answer set:
#: "the 4th category" would otherwise yield the gold "4", which is a digit
#: prefix of a longer token in the chunk and so is not the value a reader
#: would find.
NUMERIC_RE = re.compile(
    r"\b([A-Za-z][A-Za-z \-]{3,45}?)\s+(?:is|are|was|were|of|about|around|typically|usually)\s+"
    r"(?:approximately\s+)?(\d[\d,.]*\s?(?:%|percent|hours?|hrs?|days?|weeks?|months?|years?|units?|kg|km|minutes?)?)(?![A-Za-z])"
)


#: A generated question is only usable if its subject is a plausible noun
#: phrase. The permissive regexes above can match mid-clause or after a
#: truncated word, and the result is not a question anybody would ask.
_VERB_LIKE = frozenset("""
    is are was were has have had will can could should would does do did
    been being than that which who whom whose when where while if then
    show shows showed assume assumes assume assume assume arrive arrives
    arrive know knows knew publish publishes published avoid avoids avoided
    host hosts prepared use uses used call calls called known make makes
    made base based define defines defined measure measures measured
    calculate calculates calculated estimate estimates estimated
    increase increases increased decrease decreases decreased require
    requires required provide provides provided mean means means include
    includes included contain contains contained represent represents
    represent depend depends depend apply applies applied refer refers
    refer occur occurs occurred state states stated become becomes became
    result results resulted allow allows allowed enable enables enabled
""".split())

#: Words that cannot be the subject of a "What is X?" question.
_PRONOUN_LIKE = frozenset("""
    there it this that these those they he she we you one some such both
    each many most all several another other others anything something
    nothing everything someone anyone everyone nobody
""".split())

#: Words that cannot begin or end a subject phrase.
_BAD_EDGE = frozenset("""
    the a an of in on at to for and or but with by from as that this these
    those its his her their our your my not no also than into onto over
    under about after before between during through against within
""".split())

#: A number, optionally with a unit, for the numeric-fact branch.
_VALUE_RE = re.compile(
    r"^\d[\d,]*(?:\.\d+)?\s?[^\s]{0,18}$",
    re.IGNORECASE,
)


def _subject_is_usable(subject: str) -> bool:
    """True when the matched subject reads like a noun phrase."""
    words = subject.split()
    if len(words) < 2 or len(words) > 8:
        return False
    lowered = [w.lower().strip(",;:\"'()") for w in words]
    if not all(lowered):
        return False
    if lowered[-1] in _BAD_EDGE:
        return False
    if lowered[-1].endswith("ing"):
        return False
    # An article may begin a subject ("The reorder point ..."), but a
    # preposition or conjunction may not.
    if lowered[0] in _BAD_EDGE and lowered[0] not in ("the", "a", "an"):
        return False
    if any(w in _VERB_LIKE for w in lowered):
        return False
    if lowered[0] in _PRONOUN_LIKE:
        return False
    if any(w in ("he", "she", "it", "they", "we", "you") for w in lowered):
        return False
    # A subject must be words, not markup or punctuation.
    if not all(w.isalpha() for w in words):
        return False
    # A subject made of the same word twice is an artefact.
    if len(set(lowered)) < 2:
        return False
    return True


def _value_is_usable(value: str) -> bool:
    """True when the extracted answer is a number with an optional unit."""
    return bool(_VALUE_RE.match(value.strip()))


def _sentences(prose: str) -> list[str]:
    """Split prose into well-formed sentences.

    A generated question is only usable if its subject is a real subject. The
    permissive regexes below match anywhere in the text, so a match that began
    mid-clause -- or after a word the markdown converter had truncated -- gave
    a subject like "since manufacturing in an existing plant" and a question
    like "What value is stated for a teep in the source documentation?".
    Anchoring the match to the start of a sentence fixes the class of defect
    rather than patching its symptoms.
    """
    out = []
    for part in re.split(r"(?<=[.!?])\s+", prose):
        part = part.strip()
        # A leading marker such as "[FIGURE]" is not part of the sentence.
        part = re.sub(r"^\[.*?\]\s*", "", part)
        if len(part) < 40 or len(part.split()) < 8:
            continue
        if not part[:1].isupper():
            continue
        if "[[" in part or "]]" in part:
            continue
        out.append(part)
    return out


def _subject_for_question(subject: str) -> str:
    """Render a subject for a question, preserving the case of acronyms.

    "TEEP" is an acronym; lower-casing it to "teep" produces a question that
    reads as a typo. "economic order quantity" is ordinary prose and is
    lower-cased so it reads as a phrase rather than a title.
    """
    words = subject.split()
    if not words:
        return subject
    has_acronym = any(len(w) >= 2 and w.isalpha() and w.isupper() for w in words)
    # An article at the front is always lower-cased, acronym or not:
    # "The MTBF" becomes "the MTBF", not "The MTBF".
    if words[0].lower() in ("the", "a", "an"):
        return subject[:1].lower() + subject[1:]
    if has_acronym:
        return subject
    return subject[:1].lower() + subject[1:]


def questions_from_text(text: str, chunk_id: str, category: str, rng: random.Random) -> list[dict]:
    """Derive definitional and numeric-fact questions from a prose chunk."""
    out = []
    sentences = _sentences(text)

    for sent in sentences:
        m = DEFINITION_RE.search(sent)
        if not m:
            continue
        subject = m.group(1).strip()
        copula = m.group(2)
        if len(subject.split()) > 7:
            continue
        if not _subject_is_usable(subject):
            continue
        answer = m.group(3).strip()
        if "[[" in answer or "]]" in answer:
            continue
        out.append(
            {
                "query": f"What {copula} {_subject_for_question(subject)}?",
                "gold": [chunk_id],
                "category": category,
                "family": "definition",
                "modality_target": "text",
                "answer": answer[:200],
            }
        )
        if len(out) >= 2:
            break

    if not out:
        for sent in sentences:
            m = NUMERIC_RE.search(sent)
            if not m:
                continue
            subject = m.group(1).strip()
            value = m.group(2).strip()
            if len(subject.split()) > 6 or not value:
                continue
            if not _subject_is_usable(subject):
                continue
            if not _value_is_usable(value):
                continue
            out.append(
                {
                    "query": clean_query(
                        f"What value is stated for "
                        f"{_subject_for_question(subject)} in the "
                        f"source documentation?"),
                    "gold": [chunk_id],
                    "category": category,
                    "family": "numeric_fact",
                    "modality_target": "text",
                    "answer": value,
                }
            )
            if len(out) >= 1:
                break
    return out



def main() -> int:
    rng = random.Random(SEED)
    print("[bench] ingesting corpus ...", flush=True)
    chunks = ingest_corpus(CORPUS_DIR)
    if not chunks:
        print("No chunks found. Run build_corpus.py first.", file=sys.stderr)
        return 1
    print(f"[bench] {len(chunks)} chunks ingested", flush=True)

    records: list[dict] = []
    for ch in chunks:
        if ch.modality == "table":
            records.extend(questions_from_table(ch.text, ch.chunk_id, ch.category, rng))
        else:
            records.extend(questions_from_text(ch.text, ch.chunk_id, ch.category, rng))

    # De-duplicate by query text.
    seen: set[str] = set()
    unique = []
    for r in records:
        key = r["query"].lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)

    # Unanswerable set, family 1: out-of-domain topics. These have NO gold
    # chunk by construction.
    unanswerable = [
        {
            "query": q,
            "gold": [],
            "category": "unanswerable",
            "family": "unanswerable_ood",
            "modality_target": None,
            "answer": None,
        }
        for q, _ in UNANSWERABLE_TOPICS
    ]

    # Unanswerable set, family 2: the corpus-anchored class. These have the
    # same question stems as the answerable classes, name subjects the
    # corpus genuinely discusses, and ask for something the corpus genuinely
    # does not state -- so their unanswerability is decidable only from the
    # evidence, not from the shape of the question. The class this replaces
    # asked about fabricated identifiers (``SKU A-771``) that no answerable
    # question ever mentions, which made its unanswerability decidable from
    # the question string alone; the audit in
    # `experiments/audit_unanswerable_class.py` measures that.
    corpus_anchored = unanswerable_repair.generate(chunks, n=110, seed=SEED)
    print(f"[bench] corpus-anchored unanswerable queries: "
          f"{len(corpus_anchored)}", flush=True)

    all_records = unique + unanswerable + corpus_anchored
    rng.shuffle(all_records)

    BENCHMARK_DIR.mkdir(parents=True, exist_ok=True)
    out_path = BENCHMARK_DIR / "benchmark.json"
    families: dict[str, int] = {}
    cats: dict[str, int] = {}
    for r in all_records:
        families[r["family"]] = families.get(r["family"], 0) + 1
        cats[r["category"]] = cats.get(r["category"], 0) + 1
    out_path.write_text(
        json.dumps(
            {
                "label_standard": "silver",
                "seed": SEED,
                "n_queries": len(all_records),
                "n_answerable": len(unique),
                "n_unanswerable": len(unanswerable) + len(corpus_anchored),
                "families": families,
                "categories": cats,
                "queries": all_records,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"[bench] wrote {len(all_records)} queries -> {out_path}")
    print(f"[bench] families: {families}")
    print(f"[bench] categories: {cats}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
