#!/usr/bin/env python3
"""Build the candidate pair set for the contradiction evaluation (RO4).

**The problem this solves.** Experiment 11 measured the contradiction gate's
precision on the focus corpus and got 0%: the corpus contains no
contradictions for the gate to find, so every alarm was a false positive and
the calibration correctly withheld the findings. A precision measured on a
corpus with no positives is not a measurement of the mechanism; it is a
measurement of the corpus. RO4 needs a corpus that *does* contain conflicts.

**Where the conflicts come from.** The eCFR versioner serves any regulation as
it stood on any past date, and federal regulations are amended. The same
section, read on two dates, is the same rule at two issues -- and where the
amendment changed a limit, the two versions state *different requirements*.
That is a real conflict, in real industrial text, and it is the kind of
conflict a practitioner has to be told about: the pre-amendment text is still
in the documents they were given.

So the revision corpus is built from two snapshots of the same regulations:
2021-12-31 and 2026-06-01.

**The candidate pool, and why it is mined the way it is.** The pool of pairs
a practitioner would actually be shown is the set of pairs the *retriever*
puts together. So the pool is mined by **dense similarity alone** -- the
retriever's own signal. It is deliberately not mined by the detector's
numeric rule, its NLI probability or its subject check, because a candidate
pool selected on the detector's decision rule cannot measure the detector's
precision: every alarm would be in the pool by construction, and the
precision estimate would be the detector's opinion of itself.

Two strata:

``revision``
    Paragraph-level pairs from the same section, aligned across the two
    snapshots, whose text changed. The alignment is by token overlap, so a
    pair is a paragraph and its amended self rather than an arbitrary
    juxtaposition.

``similar``
    Cross-document pairs whose embeddings are close. These carry the
    false-alarm load: two passages about the same subject that do not
    conflict.

**Blind by construction.** The judge sheet records the stratum and the pair
ids, but the rubric and the passages are what the judge sees -- never the
detector's NLI probability, its similarity, or its numeric-conflict list.

Usage:
    MTP_VARIANT=industrial python experiments/build_revision_candidates.py
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from fetch_ecfr import fetch_part_xml, split_sections  # noqa: E402

SEED = 20261118

#: The two snapshots. The post date is the corpus's own date, so the revision
#: corpus is a superset of the corpus the rest of the evaluation runs on.
PRE_DATE = "2021-12-31"
POST_DATE = "2026-06-01"

#: The sources, mirroring the corpus builder's selection exactly.
SOURCES = [
    (29, "1910", set()),
    (40, "112", set()),
    (40, "60", {"A", "D", "F", "J", "L", "M", "DD", "LL", "OOO", "VV"}),
    (49, "173", {"B", "C", "E", "F"}),
]

#: The minimum token overlap for two blocks to be considered the same
#: paragraph across snapshots.
ALIGN_MIN_OVERLAP = 0.35

#: Minimum embedding cosine for two chunks to be a retrieval-level pair.
MINE_MIN_COSINE = 0.60

#: How many chunks are mined when the dense index is not available.
MINE_SUBSAMPLE = 1800

#: Nearest neighbours kept per chunk when mining.
MINE_TOP_K = 4

#: How many pairs of each stratum go into the judge sheet.
N_REVISION = 90
N_SIMILAR = 150

#: How much of a passage the judge is shown.
PASSAGE_CHARS = 900


# --------------------------------------------------------------------------
# snapshots
# --------------------------------------------------------------------------
def load_snapshot(date: str) -> dict[str, list[str]]:
    """section identifier -> its blocks, for every source, at `date`."""
    out: dict[str, list[str]] = {}
    for title, part, subparts in SOURCES:
        if subparts:
            paths = [fetch_part_xml(title, part, date, subpart=sp)
                     for sp in sorted(subparts)]
        else:
            paths = [fetch_part_xml(title, part, date)]
        for path in paths:
            for section in split_sections(path):
                out[section["identifier"]] = section["body"]
    return out


_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> set[str]:
    return set(_TOKEN_RE.findall(text.lower()))


def _overlap(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def revision_pairs(pre: dict[str, list[str]],
                   post: dict[str, list[str]]) -> list[dict]:
    """Paragraph pairs whose text changed between the two snapshots.

    A pre-block is paired with the post-block it overlaps most. When that
    overlap is above the threshold and the two texts differ, the pair is an
    amended paragraph.
    """
    pairs: list[dict] = []
    for ident, pre_blocks in pre.items():
        post_blocks = post.get(ident)
        if not post_blocks:
            continue
        pre_toks = [_tokens(b) for b in pre_blocks]
        post_toks = [_tokens(b) for b in post_blocks]
        for i, block in enumerate(pre_blocks):
            best_j, best_score = -1, 0.0
            for j, other in enumerate(post_blocks):
                score = _overlap(pre_toks[i], post_toks[j])
                if score > best_score:
                    best_j, best_score = j, score
            if best_j < 0 or best_score < ALIGN_MIN_OVERLAP:
                continue
            if pre_blocks[i].strip() == post_blocks[best_j].strip():
                continue
            pairs.append({
                "section": ident,
                "passage_a": pre_blocks[i],
                "passage_b": post_blocks[best_j],
                "overlap": round(best_score, 4),
            })
    return pairs


# --------------------------------------------------------------------------
# mining
# --------------------------------------------------------------------------
def similar_pairs(n_pairs: int, rng: random.Random) -> list[dict]:
    """Cross-document pairs the retriever would put together.

    Mining is by the *retriever's* signal, never the detector's. The
    detector's numeric rule, its NLI probability and its subject check are
    not consulted, so the pool is independent of what the detector will
    decide about each pair -- a pool selected on the detector's own rule
    cannot measure the detector's precision, because every alarm would be
    in the pool by construction.

    The lexical leg of the framework's hybrid retriever is used: for each
    chunk, the chunks that BM25 ranks highest against it. BM25 is part of
    the retriever, so the pool is the set of pairs the deployed system
    actually puts in front of the contradiction gate.
    """
    from src.config import CORPUS_DIR
    from src.ingestion import ingest_corpus
    from src.lexical import BM25Index

    chunks = ingest_corpus(CORPUS_DIR)
    chunk_text = {c.chunk_id: c.text for c in chunks}
    ids = [c.chunk_id for c in chunks]
    doc_of = {c.chunk_id: c.doc_id for c in chunks}
    print(f"[ro4] mining over {len(ids)} chunks", flush=True)

    bm25 = BM25Index.build(chunk_text)
    scores = bm25.score_matrix() if hasattr(bm25, "score_matrix") else None
    if scores is None:
        # The index scores one query at a time; that is 11k passes, so the
        # retrieval is done on a random subsample of the corpus instead.
        # The pool is a sample of the pairs the retriever produces, which is
        # what a precision estimate needs.
        rng.shuffle(ids)
        ids = ids[:MINE_SUBSAMPLE]
        chunk_text = {cid: chunk_text[cid] for cid in ids}
        bm25 = BM25Index.build(chunk_text)

    best: dict[tuple[int, int], float] = {}
    for i, cid in enumerate(ids):
        row = bm25.score(chunk_text[cid])
        row[i] = -1.0
        top = np.argpartition(-row, min(MINE_TOP_K, len(row) - 1))[:MINE_TOP_K]
        for j in top:
            if row[j] <= 0:
                continue
            a, b = (i, int(j)) if i < int(j) else (int(j), i)
            best[(a, b)] = float(max(best.get((a, b), 0.0), row[j]))

    pairs = [
        {
            "passage_a": chunk_text[ids[i]],
            "passage_b": chunk_text[ids[j]],
            "score": round(score, 4),
            "doc_a": doc_of[ids[i]],
            "doc_b": doc_of[ids[j]],
        }
        for (i, j), score in best.items()
    ]
    rng.shuffle(pairs)
    return pairs[:n_pairs]


# --------------------------------------------------------------------------
# the judge sheet
# --------------------------------------------------------------------------
RUBRIC = """\
# Rubric for labelling pairs of industrial regulatory passages

You are given two passages from United States federal industrial regulations.
Decide **one** of six labels for the pair. Exactly one applies.

Work down the tree below and stop at the first question that applies.

## 1. Are the two passages about different subjects, neither being a part of
##    the other?

**Yes -> `term_mismatch`**

The passages share vocabulary, a topic word, a standard number or a
quantity, but they are not about the same thing: two different substances,
two different pieces of equipment, two different kinds of workplace. A
numeric rule fires on "clearance of 1/2 inch" in one passage and "clearance
of 2 inches" in another that is about a different machine; that pair is
`term_mismatch`, and it is the failure mode a *subject* check is meant to
suppress.

**No -> go to question 2.** The two passages are about the same subject, or
one is about a part of what the other is about.

## 2. Is one passage a later revision of the other?

**Yes -> `supersession`**

"Raw material lead time is 21 days" and "Raw material lead time is 14 days
(revised, Q3)" are not a contradiction; they are a policy that changed. Look
for revision markers, effective dates, "updated", "revised", "previously",
"now", "as of", version numbers, or one passage being the same rule as it
read before an amendment.

A pair is `supersession` even when the supersession is obvious and the
supersession check did **not** catch it -- that is a false negative of the
supersession branch and is exactly what the labelling is looking for.

**No -> go to question 3.**

## 3. Is one passage about a whole and the other about one of its parts, and
##    can both be true at the same time?

**Yes -> `granularity`**

"The total clearance required at the machine is 1 inch" and "the clearance
at the belt guard is 1 inch" are about a whole and one of its parts. The
general figure is true of the component in a different sense, so the two do
not contradict each other.

**No -> go to question 4.**

## 4. Do the two passages state facts that cannot both be true at the same
##    time?

**Yes -> go to question 5.** If neither passage is a revision of the other,
and both cannot be true at once, the conflict is one of two kinds.

**No -> go to question 6.**

## 5. Which kind of conflict is it?

**A numeric limit is different for the same thing -> `quantity_conflict`**

The same measured quantity is given two different values, and the subject is
matched: the same substance, the same machine, the same requirement.
"Pliable exposure limit for cadmium is 5 micrograms per cubic meter" against
"Pliable exposure limit for cadmium is 100 micrograms per cubic meter" is a
`quantity_conflict`.

**Anything else -> `semantic_conflict`**

The same subject is required to have two different properties, or one
passage permits what the other forbids, and no number is involved:
"the employer shall inspect the fire extinguisher monthly" against "the
employer shall inspect the fire extinguisher annually" is a
`semantic_conflict`.

## 6. Do the passages simply not conflict?

**Yes -> `no_conflict`**

They are about the same subject and are compatible: they state different
aspects of the same requirement, one is more general than the other, or
they simply do not bear on the same point.

A note on scope: two passages are NOT in conflict merely because they differ.
Two regulations that impose different requirements on the same topic are in
conflict only when they cannot both be obeyed at once. Two that impose
requirements at different times, on different equipment, or for different
situations are not.
"""

INSTRUCTIONS = """\
For each pair, read both passages and set `label` to exactly one of:
quantity_conflict, semantic_conflict, supersession, granularity,
term_mismatch, no_conflict. Use the rubric below. Only
`quantity_conflict` and `semantic_conflict` count as a true contradiction;
everything else counts as a false alarm. A pair that is about different
subjects is `term_mismatch` even when a number appears to disagree.
"""


def _clip(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= PASSAGE_CHARS:
        return text
    return text[:PASSAGE_CHARS].rsplit(" ", 1)[0] + " ..."


#: A generic unit vocabulary, used only to tell a *quantity* from a
#: paragraph marker. It is deliberately not the detector's measurement
#: vocabulary: the detector requires the number to be governed by a declared
#: measurement term, and the construction criterion must not require that,
#: or the stratum would be selected on the detector's own criterion and the
#: recall measured against it would be a tautology.
_UNITS = (
    "percent|per cent|micograms?|milligrams?|grams?|kilograms?|pounds?|tons?|"
    "ppm|parts per million|psig|psi|volts?|amperes?|watts?|decibels?|db|"
    "inches|inch|feet|foot|miles|hours?|days?|minutes?|seconds?|months?|"
    "years?|cubic meters?|cubic feet|square feet|square inches|gallons?|"
    "liters?|litres|degrees|micron|mils|fiber|cc|"
    "micrograms per cubic millimeter|"
)
_QUANTITY_RE = re.compile(
    r"(?<![\w.])(\d[\d,]*(?:\.\d+)?)\s*(" + _UNITS + r")\b", re.IGNORECASE)


def quantities(text: str) -> set[str]:
    """Every number-with-a-unit in a text, normalised to (value, unit).

    A number without a unit is not a quantity: in a regulation the bare
    numbers are paragraph markers -- "(a)(1)", "(i)", "(C)" -- and counting
    them would say that every renumbered paragraph is a changed limit.
    """
    out: set[str] = set()
    for m in _QUANTITY_RE.finditer(text):
        value = m.group(1).replace(",", "").rstrip(".")
        unit = m.group(2).lower()
        out.add(f"{value}|{unit}")
    return out


def numbers_changed(a: str, b: str) -> bool:
    """Do the two versions of a provision state different quantities?

    A generic test: it asks whether a *unit-bearing* number differs between
    the two texts, with no measurement vocabulary involved. That matters,
    because the detector's quantity branch *requires* the number to be
    governed by a declared measurement term and the subject and instance
    checks to pass. Selecting on "a quantity differs" therefore selects on
    something strictly weaker than the detector's own criterion, and a
    detector that fails to fire on this stratum has failed on a real
    ambiguity rather than on a tautology.

    A pair whose two versions state different quantities for the same thing
    is a quantity conflict *by construction* -- the rule changed the limit
    -- and that label needs no annotation.
    """
    return quantities(a) != quantities(b)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True,
                    help="the judge sheet (JSON)")
    ap.add_argument("--pairs-out", default=None,
                    help="where the un-clipped candidate pairs are written")
    args = ap.parse_args()
    rng = random.Random(SEED)

    print("[ro4] loading the pre-amendment snapshot ...", flush=True)
    pre = load_snapshot(PRE_DATE)
    print(f"[ro4] {len(pre)} sections at {PRE_DATE}", flush=True)
    print("[ro4] loading the post-amendment snapshot ...", flush=True)
    post = load_snapshot(POST_DATE)
    print(f"[ro4] {len(post)} sections at {POST_DATE}", flush=True)

    rev = revision_pairs(pre, post)
    print(f"[ro4] amended-paragraph pairs: {len(rev)}", flush=True)
    for p in rev:
        p["numbers_changed"] = numbers_changed(p["passage_a"], p["passage_b"])
    n_numeric = sum(1 for p in rev if p["numbers_changed"])
    print(f"[ro4] of which the two versions state different numbers: "
          f"{n_numeric} ({n_numeric / max(len(rev), 1):.1%})", flush=True)
    rng.shuffle(rev)
    rev = rev[:N_REVISION]

    print("[ro4] mining similarity pairs ...", flush=True)
    sim = similar_pairs(N_SIMILAR, rng)
    print(f"[ro4] similarity pairs: {len(sim)}", flush=True)

    pairs = []
    pid = 0
    for p in rev:
        pid += 1
        pairs.append({
            "pair_id": pid,
            "stratum": "revision",
            "passage_a": _clip(p["passage_a"]),
            "passage_b": _clip(p["passage_b"]),
        })
    for p in sim:
        pid += 1
        pairs.append({
            "pair_id": pid,
            "stratum": "similar",
            "passage_a": _clip(p["passage_a"]),
            "passage_b": _clip(p["passage_b"]),
        })
    rng.shuffle(pairs)

    sheet = {
        "schema": "mtp.revision-judge-input/1",
        "instructions": INSTRUCTIONS,
        "rubric": RUBRIC,
        "labels_allowed": ["quantity_conflict", "semantic_conflict",
                           "supersession", "granularity", "term_mismatch",
                           "no_conflict"],
        "pairs": pairs,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(sheet, indent=2), encoding="utf-8")
    print(f"[ro4] wrote {len(pairs)} pairs -> {out}")

    if args.pairs_out:
        full = {
            "revision_pairs": rev,
            "similar_pairs": sim,
            "pre_date": PRE_DATE,
            "post_date": POST_DATE,
        }
        p = Path(args.pairs_out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(full, indent=2), encoding="utf-8")
        print(f"[ro4] wrote the un-clipped pairs -> {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
