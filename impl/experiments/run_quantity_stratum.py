#!/usr/bin/env python3
"""What is there for the quantity branch to find, and does it find it?

**The question.** The quantity branch of the contradiction gate fires when
two passages attach different values to the same measured quantity. On the
240-pair revision corpus it fired **zero** times, on a stratum that contained
35 pairs where the rule demonstrably changed a limit. Two explanations are
possible and they call for opposite conclusions:

* the branch is broken -- its vocabulary does not cover what regulation
  binds on, and its measurement key cannot reach a limit that sits three
  words away from its number;
* there is nothing to fire on -- federal regulation is internally consistent
  about the numbers it binds, so two authentic documents rarely state
  different values for the same quantity.

**How this settles it.** The corpus is searched directly for cross-document
quantity conflicts: every (measurement term, value) pair in every document,
grouped by term, and a term whose values differ *across documents* is a
candidate conflict. That search uses the branch's own vocabulary but not its
own decision rule, and — more importantly — it is exhaustive over the
corpus rather than sampled, so it answers "how many are there?" exactly.

The candidates are then put to the detector. If the detector stays silent on
pairs the search says are conflicts, the branch is broken; if the search says
there are none, the branch has nothing to do and its zero is a property of
the domain rather than of the code.

Usage:
    MTP_VARIANT=industrial python experiments/run_quantity_stratum.py \
        --out ../results_industrial/exp20_quantity_stratum.json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import ARTIFACT_DIR, CONFIG  # noqa: E402
from src.contradiction import (  # noqa: E402
    _MEASUREMENT_PHRASES_BY_PROFILE,
    _MEASUREMENT_TERMS_BY_PROFILE,
    _NUMBER_RE_BY_PROFILE,
    _title_runs,
    numeric_conflicts,
    shared_instance,
)
from src.models import embed_texts  # noqa: E402
from src.pipeline import Index  # noqa: E402


def _measurement_key(tokens, flagged, before, phrases, terms) -> str:
    """The measurement term governing a number, or ""."""
    idxs = [i for i, (_w, end) in enumerate(tokens) if end <= before]
    if not idxs:
        return ""
    idxs = [i for i in idxs if tokens[i][1] > before - 60]
    best, best_end = "", -1
    for pos, i in enumerate(idxs):
        for gap in range(0, 4):
            end = pos - gap
            if end < 0:
                continue
            for span in (3, 2, 1):
                if end - span + 1 < 0:
                    continue
                first = idxs[end - span + 1]
                phrase = " ".join(tokens[j][0]
                                  for j in idxs[end - span + 1: end + 1])
                known = (phrase in phrases
                         or (span == 1 and phrase in terms))
                if not known:
                    continue
                if span == 1 and first in flagged:
                    continue
                if tokens[end][1] > best_end:
                    best, best_end = phrase, tokens[end][1]
                break
            if best:
                break
    return best


def collect(index, profile: str) -> dict[str, dict[str, set[str]]]:
    """(measurement term) -> (value set) -> (documents that state it)."""
    phrases = _MEASUREMENT_PHRASES_BY_PROFILE[profile]
    terms = _MEASUREMENT_TERMS_BY_PROFILE[profile]
    number_re = _NUMBER_RE_BY_PROFILE[profile]
    by_term: dict[str, dict[str, set[str]]] = defaultdict(
        lambda: defaultdict(set))
    for chunk in index.chunks:
        text = chunk.text
        tokens, flagged = _title_runs(text)
        for m in number_re.finditer(text):
            raw = m.group(1).replace(",", "").rstrip(".")
            unit = (m.group(2) or "").lower()
            try:
                magnitude = float(raw)
            except ValueError:
                continue
            if 1500 <= magnitude <= 2100 and not unit:
                continue
            if magnitude < 100 and not unit:
                continue
            key = _measurement_key(tokens, flagged, m.start(), phrases, terms)
            if not key:
                continue
            by_term[key][f"{raw}|{unit}"].add(chunk.doc_id)
    return by_term


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True)
    ap.add_argument("--profile", default="regulatory")
    args = ap.parse_args()

    index = Index.load(ARTIFACT_DIR / "index")
    by_term = collect(index, args.profile)

    print(f"[ro4] {len(by_term)} measurement terms carry a value in the corpus")

    # A term is a cross-document conflict when the same quantity takes
    # different values in documents that are not the same document.
    conflicts: list[dict] = []
    for term, values in sorted(by_term.items()):
        if len(values) < 2:
            continue
        items = sorted(values.items())
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                v1, d1 = items[i]
                v2, d2 = items[j]
                if v1.split("|")[0] == v2.split("|")[0]:
                    continue          # same number, different unit
                docs = (d1 | d2)
                if len(docs) < 2:
                    continue          # the same document states both
                conflicts.append({
                    "term": term,
                    "value_a": v1, "docs_a": sorted(d1),
                    "value_b": v2, "docs_b": sorted(d2),
                })

    print(f"[ro4] cross-document quantity conflicts: {len(conflicts)}")
    by_term_count = Counter(c["term"] for c in conflicts)
    for term, n in by_term_count.most_common(15):
        print(f"    {term:38s} {n}")

    # Now put the candidates to the detector. Each conflict is scored on the
    # two passages that state the two values.
    passages: list[tuple[str, str]] = []
    chunk_by_doc: dict[str, list[str]] = defaultdict(list)
    for chunk in index.chunks:
        chunk_by_doc[chunk.doc_id].append(chunk.text)
    for c in conflicts[:200]:
        a = next((t for t in chunk_by_doc[c["docs_a"][0]]
                  if c["value_a"].split("|")[0] in t), "")
        b = next((t for t in chunk_by_doc[c["docs_b"][0]]
                  if c["value_b"].split("|")[0] in t), "")
        if a and b:
            passages.append((a, b))

    print(f"[ro4] scoring {len(passages)} candidate pairs with the detector")
    fired = 0
    detail = []
    judged: list[dict] = []
    for a, b in passages:
        conflicts_found = numeric_conflicts(
            a, b, subject_gate=True,
            instance_gate=shared_instance(a, b),
            profile=args.profile, lookback=3)
        if conflicts_found:
            fired += 1
            detail.append({"a": a[:200], "b": b[:200],
                           "conflicts": conflicts_found})
        judged.append({"passage_a": a, "passage_b": b,
                       "detector_fired": bool(conflicts_found),
                       "conflicts": conflicts_found})

    # A judging sheet for the pairs, with the detector's verdict withheld.
    # Every fired pair goes in, plus a sample of the ones it did not fire on,
    # because precision needs the false alarms and recall needs the misses.
    rng = np.random.default_rng(20261118)
    fired_pairs = [j for j in judged if j["detector_fired"]]
    quiet_pairs = [j for j in judged if not j["detector_fired"]]
    n_quiet = min(len(quiet_pairs), max(0, 60 - len(fired_pairs)))
    picked_quiet = [quiet_pairs[i] for i in
                    rng.choice(len(quiet_pairs), size=n_quiet, replace=False)] \
        if n_quiet else []
    sheet_pairs = fired_pairs + picked_quiet
    rng.shuffle(sheet_pairs)
    sheet = {
        "schema": "mtp.quantity-judge-input/1",
        "rubric": (
            "Decide what kind of relationship holds between two passages "
            "from US federal industrial regulations.\n\n"
            "* `quantity_conflict` -- the same measured quantity, about the "
            "same subject, in two different documents, takes two different "
            "values, so the two cannot both be the rule that applies.\n"
            "* `semantic_conflict` -- the same subject is required to have "
            "two different properties, and no number is involved.\n"
            "* `supersession` -- the two passages are two issues of the same "
            "rule, so they cannot both be current.\n"
            "* `granularity` -- one passage is about a whole and the other "
            "about a part of it; both can be true.\n"
            "* `term_mismatch` -- the two passages are about different "
            "subjects. This is the common case for two passages that use the "
            "same word for a measurement but are about different things: a "
            "pressure in one boiler and a pressure in another, a capacity in "
            "one container and a capacity in another.\n"
            "* `no_conflict` -- about the same subject, compatible.\n\n"
            "Read the scope before the numbers. Two passages that state "
            "different values for the same word are in conflict only when "
            "they are about the same subject and the same situation."),
        "labels_allowed": ["quantity_conflict", "semantic_conflict",
                           "supersession", "granularity", "term_mismatch",
                           "no_conflict"],
        "items": [{"pair_id": i + 1,
                   "passage_a": j["passage_a"][:4000],
                   "passage_b": j["passage_b"][:4000]}
                  for i, j in enumerate(sheet_pairs)],
    }
    sheet_path = out_path = Path(args.out).with_name(
        Path(args.out).stem + "_judge_input.json")
    sheet_path.write_text(json.dumps(sheet, indent=2), encoding="utf-8")
    print(f"[ro4] judge sheet: {len(sheet_pairs)} pairs "
          f"({len(fired_pairs)} fired, {len(picked_quiet)} not fired) "
          f"-> {sheet_path.name}")

    print(f"[ro4] the quantity branch fired on {fired} of {len(passages)}")

    payload = {
        "schema": "mtp.quantity-stratum/1",
        "profile": args.profile,
        "n_measurement_terms": len(by_term),
        "n_cross_document_conflicts": len(conflicts),
        "conflicts_by_term": dict(by_term_count),
        "n_pairs_scored": len(passages),
        "n_pairs_the_quantity_branch_fired_on": fired,
        "n_pairs_in_the_judge_sheet": len(sheet_pairs),
        "fired_examples": detail[:10],
        "note": "the search groups every (measurement term, value) pair in the "
                "corpus and keeps the terms whose values differ across "
                "documents. It is exhaustive over the corpus, so the count is "
                "exact rather than sampled; the detector is then put to the "
                "candidates it produced. The search is deliberately "
                "over-inclusive -- two passages about different boilers "
                "share the word 'pressure' -- so the count is an upper bound "
                "on the conflicts that exist, and the judge sheet is what "
                "separates them.",
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"[ro4] wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
