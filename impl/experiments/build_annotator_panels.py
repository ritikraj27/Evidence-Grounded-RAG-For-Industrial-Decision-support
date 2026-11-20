#!/usr/bin/env python3
"""Build the per-regime annotation sheets for the contradiction pairs.

**Why a panel.** The first RO4 measurement was annotated by two readers, and
they disagreed on 68 of 240 pairs — one cell: whether a pair that is
recognisably the same rule at two issues counts as *supersession* or as *no
conflict*. That single ambiguity moved the measured precision of the
detector's semantic branch from 0.075 to 0.675, so the annotation, not the
detector, was the binding constraint on the measurement.

Three things are done here, and they are separable on purpose.

1. **The rubric is sharpened** so that the supersession branch is
   *operational* rather than a judgement call. The new branch asks whether
   the two passages are two issues of the same rule, and it says explicitly
   that this is a structural question — answered by recognising the same
   requirement in the same terms — and that a version marker is one way to
   see it, not the only way. It also says what supersession does *not*
   mean: one of the two is not thereby wrong.

2. **The pairs are assigned to a regulatory regime**, so that each pair can
   be read by someone who knows that regime. Judging whether two OSHA
   respiratory-protection provisions conflict is a different task from
   judging whether two DOT packaging provisions conflict, and a reader who
   knows only one of them will guess.

3. **A generalist sheet is produced as well**, on the same sharpened
   rubric. Without it the rubric's contribution and the specialisation's
   contribution cannot be separated: the panel's agreement with the
   reference could be attributable to either change.

Usage:
    python experiments/build_annotator_panels.py \
        --pairs ../results_industrial/exp14_pairs.json \
        --outdir ../results_industrial/panels
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

#: The regimes, with what each governs and what the reader needs to know.
REGIMES = {
    "occupational_safety": {
        "title": "OSHA general industry",
        "governs": "workplace safety in general industry: machine guarding, "
                   "personal protective equipment, walking-working surfaces, "
                   "exit routes, welding, compressed gas, materials handling "
                   "and storage, powered industrial trucks and overhead "
                   "cranes.",
        "reader_note": (
            "General-industry rules are written as performance requirements "
            "('shall', 'must') with the engineering standard specified "
            "elsewhere, usually by citing a named consensus standard and an "
            "edition (ANSI, ASTM, NFPA, IEEE). Two provisions that cite the "
            "same standard at different editions are two issues of the same "
            "requirement, not a contradiction — that is a supersession. Two "
            "provisions that require different amounts of the same thing "
            "from the same employer at the same time are a contradiction."),
        "parts": "29 CFR 1910",
    },
    "process_safety": {
        "title": "Catastrophic-risk management (OSHA PSM and EPA RMP)",
        "governs": "the standards that manage low-frequency, high-consequence "
                   "events: process safety management, hazardous waste "
                   "operations, permit-required confined spaces, "
                   "lockout/tagout, hazard communication, and EPA's risk "
                   "management programme rule.",
        "reader_note": (
            "These rules are unusually explicit about scope and about "
            "exemptions, and they are the rules most likely to contain "
            "genuine, simultaneous, irreconcilable requirements — a process "
            "safety management programme and a hazard communication programme "
            "can demand different things of the same employer at the same "
            "time. Read them for whether both can be obeyed together, not "
            "for whether they sound different."),
        "parts": "29 CFR 1910 subparts G, Z; 40 CFR 112",
    },
    "environmental_control": {
        "title": "Environmental control (OSHA air contaminants and EPA new source performance standards)",
        "governs": "workplace air contaminants and their exposure limits, and "
                   "emission standards for stationary sources: cement plants, "
                   "petroleum refineries, storage vessels, smelters, grain "
                   "elevators, metallic mineral processing, equipment leaks.",
        "reader_note": (
            "This is the numeric regime. Almost every conflict here is a "
            "quantity conflict: the same substance, the same measured "
            "quantity, two different numbers. Be careful about *scope* "
            "before calling it a conflict — the same substance routinely has "
            "different limits for general industry and for construction, for "
            "an 8-hour average and for a 15-minute excursion, and for "
            "different equipment. A difference in scope is not a conflict; a "
            "difference in the limit applied to the same scope is."),
        "parts": "29 CFR 1910 subpart Z; 40 CFR 60",
    },
    "hazmat_transport": {
        "title": "Hazardous materials in transport (DOT)",
        "governs": "how hazardous materials are classified, described, "
                   "packaged, marked and placarded for transport: packing "
                   "groups, packaging performance standards, quantity limits "
                   "per package and per vehicle, and the tables that pair a "
                   "material with its packaging.",
        "reader_note": (
            "DOT's tables are reference tables. A row that pairs a material "
            "with a packaging requirement is a requirement; two rows that "
            "pair the *same* material with *different* packagings for "
            "different modes of transport are not a contradiction, because "
            "they apply to different situations. Look for the *same* "
            "material under the *same* condition with different values."),
        "parts": "49 CFR 173",
    },
}

RUBRIC = """\
# Rubric for labelling pairs of industrial regulatory passages

You are given two passages from United States federal industrial
regulations. Decide **one** of six labels for the pair. Exactly one applies.

Work down the tree below and stop at the first question that applies.

## 1. Are the two passages about different subjects, neither being a part of
##    the other?

**Yes -> `term_mismatch`**

The passages share vocabulary, a topic word, an entity name, a standard
number or a quantity, but they are not about the same thing: two different
substances, two different pieces of equipment, two different kinds of
workplace. A numeric rule fires on "clearance of 1/2 inch" in one passage
and "clearance of 2 inches" in another that is about a different machine;
that pair is `term_mismatch`, and it is the failure mode a *subject* check
is meant to suppress.

**No -> go to question 2.** The two passages are about the same subject, or
one is about a part of what the other is about.

## 2. Are the two passages two issues of the same rule?

**Yes -> `supersession`**

The test is **structural**, not a marker test. The two passages address the
same requirement, about the same subject, in the same terms, and differ only
in detail: a renumbered cross-reference, a changed edition of a cited
standard, a rewording that preserves the requirement, an added or removed
paragraph, a changed incorporation-by-reference list. A version marker, an
effective date, a "supersedes" note or an amended cross-reference is one way
to see this; it is **not the only way**. Recognising that two passages are
the same rule as it read at two different times is a reading judgement, and
you are being asked to make it.

**What `supersession` means, and what it does not.** It means the two
passages cannot both be the current rule. It does **not** mean that one of
them is wrong, and it does **not** mean the pair is harmless: a practitioner
holding both has to be told which one governs. If the passages carry no
marker saying which is current, that is a fact worth reporting, not a
reason to call the pair a non-conflict.

**No -> go to question 3.**

## 3. Do the two passages state requirements that cannot both be obeyed?

**A number differs for the same measured quantity, with the subject
matched -> `quantity_conflict`**

The same substance, the same machine, the same requirement, two different
values. "The permissible exposure limit for cadmium is 5 micrograms per
cubic meter of air" against "the permissible exposure limit for cadmium is
100 micrograms per cubic meter of air" is a `quantity_conflict`.

**Anything else -> `semantic_conflict`**

The same subject is required to have two different properties, or one
passage permits what the other forbids, and no number is involved. "The
employer shall inspect the fire extinguisher monthly" against "the
employer shall inspect the fire extinguisher annually" is a
`semantic_conflict`.

**Neither -> `no_conflict`**

They are about the same subject and are compatible: they state different
aspects of the same requirement, one is more general than the other, or
they simply do not bear on the same point.

## A note on scope

Two passages are **not** in conflict merely because they differ. Two
regulations that impose different requirements on the same topic are in
conflict only when they cannot both be obeyed at once. Two that impose
requirements at different times, on different equipment, for different
situations, or for different scopes are not — read the scope before
judging the numbers.
"""

INSTRUCTIONS = """\
For each pair, read both passages and set `label` to exactly one of:
quantity_conflict, semantic_conflict, supersession, granularity,
term_mismatch, no_conflict. Use the rubric below. Follow its decision tree
in order and stop at the first question that applies.

`quantity_conflict` and `semantic_conflict` are true contradictions.
`supersession` is a real conflict of a different kind: the two passages are
the same rule at two issues, so they cannot both be current.
`term_mismatch`, `granularity` and `no_conflict` are false alarms.
"""


def regime_of(identifier: str) -> str:
    """The regulatory regime a document identifier belongs to."""
    ident = identifier.split("_")[0]
    if ident.startswith("1910."):
        number = int(ident.split(".")[1])
        if 1000 <= number <= 1299:
            return "process_safety" if number in (1200, 1201) \
                else "environmental_control"
        if number in (119, 120, 146, 147):
            return "process_safety"
        return "occupational_safety"
    if ident.startswith("60."):
        return "environmental_control"
    if ident.startswith("112."):
        return "process_safety"
    if ident.startswith("173."):
        return "hazmat_transport"
    return "occupational_safety"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pairs", required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    doc = json.loads(Path(args.pairs).read_text(encoding="utf-8"))

    # Rebuild the pair list in the judge sheet's order so the ids line up.
    records: list[dict] = []
    pid = 0
    for p in doc["revision_pairs"]:
        pid += 1
        records.append({"pair_id": pid, "stratum": "revision",
                        "passage_a": p["passage_a"], "passage_b": p["passage_b"],
                        "section": p.get("section", "")})
    for p in doc["similar_pairs"]:
        pid += 1
        records.append({"pair_id": pid, "stratum": "similar",
                        "passage_a": p["passage_a"], "passage_b": p["passage_b"],
                        "section": ""})

    for r in records:
        if r["section"]:
            r["regime"] = regime_of(r["section"])
        else:
            r["regime"] = regime_of(_doc_of(r["passage_a"]))

    counts = Counter(r["regime"] for r in records)
    print(f"[panel] {len(records)} pairs:", dict(counts))

    # One sheet per regime.
    for regime, meta in REGIMES.items():
        sel = [r for r in records if r["regime"] == regime]
        if not sel:
            continue
        sheet = {
            "schema": "mtp.revision-judge-input/2",
            "regime": regime,
            "regime_title": meta["title"],
            "regime_governs": meta["governs"],
            "reader_note": meta["reader_note"],
            "parts": meta["parts"],
            "instructions": INSTRUCTIONS,
            "rubric": RUBRIC,
            "labels_allowed": ["quantity_conflict", "semantic_conflict",
                               "supersession", "granularity",
                               "term_mismatch", "no_conflict"],
            "pairs": [{"pair_id": r["pair_id"], "passage_a": r["passage_a"],
                       "passage_b": r["passage_b"]} for r in sel],
        }
        path = outdir / f"panel_{regime}.json"
        path.write_text(json.dumps(sheet, indent=2), encoding="utf-8")
        print(f"[panel] {regime:22s} {len(sel):3d} pairs -> {path.name}")

    # The generalist sheet, on the same rubric, over every pair.
    general = {
        "schema": "mtp.revision-judge-input/2",
        "regime": "general",
        "regime_title": "All four regimes, read without a specialism",
        "regime_governs": "occupational safety, process safety, environmental "
                          "control and hazardous-materials transport.",
        "reader_note": "You are reading pairs from four different regulatory "
                       "regimes without a specialism in any of them. Apply "
                       "the rubric as written.",
        "instructions": INSTRUCTIONS,
        "rubric": RUBRIC,
        "labels_allowed": ["quantity_conflict", "semantic_conflict",
                           "supersession", "granularity", "term_mismatch",
                           "no_conflict"],
        "pairs": [{"pair_id": r["pair_id"], "passage_a": r["passage_a"],
                   "passage_b": r["passage_b"]} for r in records],
    }
    path = outdir / "panel_generalist.json"
    path.write_text(json.dumps(general, indent=2), encoding="utf-8")
    print(f"[panel] {'generalist':22s} {len(records):3d} pairs -> {path.name}")

    # The regime assignment travels with the pairs so the scoring can use it.
    labelled = dict(doc)
    labelled["pairs_with_regime"] = [
        {"pair_id": r["pair_id"], "regime": r["regime"], "stratum": r["stratum"]}
        for r in records]
    out = outdir.parent / "exp14_pairs_with_regime.json"
    out.write_text(json.dumps(labelled, indent=2), encoding="utf-8")
    print(f"[panel] regime map -> {out}")
    return 0


def _doc_of(passage: str) -> str:
    """The source document identifier of a passage.

    The passages are the corpus documents themselves, so the identifier is
    recoverable from the text: the markdown carries the section heading, and
    the heading names the CFR section.
    """
    import re

    m = re.search(r"§\s*([0-9]+\.[0-9]+)", passage[:400])
    if m:
        return m.group(1)
    m = re.search(r"\b(1910|1926|60|112|173)\.\d+\b", passage[:400])
    return m.group(0) if m else "1910.1"


if __name__ == "__main__":
    sys.exit(main())
