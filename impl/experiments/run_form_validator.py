#!/usr/bin/env python3
"""Experiment 10 -- does the runtime form check reject malformed requests, and what does it cost?

The confidence gate decides whether the *evidence* supports an answer. It never
asks whether the request was a question at all, and the form probe
(`run_form_probe.py`) measures that: at the fitted operating point the gate
lets most malformed queries through, because a malformed query still retrieves
plausible passages and the evidence can look fine.

So the two checks answer different questions, and this experiment measures
the second one. The runtime form check (`src/query_form.py`) refuses a request
before retrieval if it is not a well-formed question. Its failure mode is the
opposite of the gate's: a *false rejection* is a refusal of a question the
corpus could have answered, which is the one failure this framework is built
to avoid. So the numbers that matter are paired -- how much malformed input
does it catch, and how much well-formed input does it refuse.

Four populations are measured:

1. **The benchmark's own queries.** Every one of them is a well-formed
   question by construction, so any refusal here is a false rejection. This
   is the largest and the least biased population available.
2. **A hand-authored set of well-formed queries**, deliberately including the
   cases the benchmark's own filter rejects -- an acronym subject, a
   hyphenated subject, a gerund noun, a bare keyword, a statement rather
   than a question, and a well-formed question that is out of the corpus's
   domain.
3. **A hand-authored set of malformed queries**, with the reason each one is
   malformed, including two keyboard mashes that the check is documented not
   to catch.
4. **The stems the benchmark generator produces and rejects**, harvested from
   the corpus and labelled by hand. This is the only population of malformed
   text that is not written by the author of the rule.

Population 4 also carries the counterfactual that justifies not reusing the
benchmark's own filter: that filter is a rule about *subjects*, and applied to
these subjects it rejects many perfectly good questions. The number it would
have cost is computed here, on the same labelled stems.

Run:
    MTP_VARIANT=focus .venv/bin/python impl/experiments/run_form_validator.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "scripts"))

import build_benchmark as bb  # noqa: E402
from common import (  # noqa: E402
    RESULTS_DIR,
    load_benchmark,
    markdown_table,
    write_result,
)
from form_stems import harvest_stems  # noqa: E402
from src.config import CORPUS_DIR, CONFIG  # noqa: E402
from src.query_form import assess_query_form  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures"
LABELS = ROOT / "experiments" / "data" / "harvested_stem_labels.json"

#: How many times the check is timed on one query. The check is a handful of
#: set lookups; the point of the timing is to show that it costs nothing
#: against the retrieval it precedes.
TIMING_REPEATS = 2000


def _fixture(name: str) -> list[dict]:
    return json.loads((FIXTURES / f"{name}_queries.json").read_text(
        encoding="utf-8"))["queries"]


def _labels() -> dict[str, str]:
    return {e["query"]: e["label"] for e in
            json.loads(LABELS.read_text(encoding="utf-8"))["labels"]}


def _score(queries: list[str]) -> dict:
    """How many of `queries` the check refuses, and which rule fired."""
    rejected = []
    rules: dict[str, int] = {}
    for q in queries:
        a = assess_query_form(q)
        if a.rejected:
            rejected.append(q)
            rules[a.rule] = rules.get(a.rule, 0) + 1
    n = len(queries)
    return {
        "n": n,
        "n_rejected": len(rejected),
        "rejection_rate": round(len(rejected) / n, 4) if n else float("nan"),
        "by_rule": rules,
        "rejected_queries": rejected,
    }


def _rate(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else float("nan")


def main() -> int:
    print("[exp10] measuring the runtime form check ...", flush=True)

    # -- 1. the benchmark's own queries ---------------------------------
    bench = load_benchmark()
    bench_queries = [q["query"] for q in bench["queries"]]
    bench_score = _score(bench_queries)
    by_family: dict[str, dict] = {}
    for q in bench["queries"]:
        fam = by_family.setdefault(q["family"], {"n": 0, "n_rejected": 0})
        fam["n"] += 1
        if assess_query_form(q["query"]).rejected:
            fam["n_rejected"] += 1
    print(f"[exp10] benchmark: {bench_score['n_rejected']}/{bench_score['n']} "
          f"well-formed queries refused", flush=True)

    # -- 2. the hand-authored well-formed set ---------------------------
    valid = _fixture("valid")
    valid_score = _score([e["query"] for e in valid])
    print(f"[exp10] hand-authored well-formed: {valid_score['n_rejected']}/"
          f"{valid_score['n']} refused", flush=True)

    # -- 3. the hand-authored malformed set ------------------------------
    malformed = _fixture("malformed")
    malformed_score = _score([e["query"] for e in malformed])
    expected_rejected = sum(1 for e in malformed
                            if e.get("expect", "reject") == "reject")
    misses = [e["query"] for e in malformed
              if e.get("expect", "reject") == "reject"
              and not assess_query_form(e["query"]).rejected]
    print(f"[exp10] hand-authored malformed: {malformed_score['n_rejected']}/"
          f"{expected_rejected} refused ({len(misses)} documented misses)",
          flush=True)

    # -- 4. the harvested, hand-labelled stems ---------------------------
    stems = harvest_stems()
    labels = _labels()
    labelled = [s for s in stems if s["query"] in labels]
    unlabelled = [s["query"] for s in stems if s["query"] not in labels]
    mal = [s for s in labelled if labels[s["query"]] == "malformed"]
    good = [s for s in labelled if labels[s["query"]] == "well_formed"]
    mal_rejected = [s for s in mal if assess_query_form(s["query"]).rejected]
    good_rejected = [s for s in good if assess_query_form(s["query"]).rejected]
    print(f"[exp10] harvested stems: {len(labelled)} labelled "
          f"({len(unlabelled)} unlabelled); "
          f"{len(mal_rejected)}/{len(mal)} malformed refused, "
          f"{len(good_rejected)}/{len(good)} well-formed refused", flush=True)

    # -- 5. the counterfactual: the benchmark's own rule -----------------
    # `_subject_is_usable` is a rule about subjects. Applied to the subject
    # of each harvested stem, it is the check a runtime validator would have
    # had if the benchmark's filter had been reused.
    cf_rejected_good = [s for s in good
                        if not bb._subject_is_usable(s["subject"])]
    cf_rejected_mal = [s for s in mal
                       if not bb._subject_is_usable(s["subject"])]
    print(f"[exp10] counterfactual (the benchmark's own rule): "
          f"{len(cf_rejected_good)}/{len(good)} well-formed stems refused",
          flush=True)

    # -- 6. what the check costs ----------------------------------------
    probe = bench_queries[0] if bench_queries else "what is the reorder point?"
    t0 = time.perf_counter()
    for _ in range(TIMING_REPEATS):
        assess_query_form(probe)
    per_query_us = (time.perf_counter() - t0) / TIMING_REPEATS * 1e6
    print(f"[exp10] cost: {per_query_us:.1f} microseconds per query", flush=True)

    payload = {
        "experiment": "form validator",
        "question": "Does the runtime query-form check reject malformed "
                    "requests, and what does it cost in false rejections?",
        "corpus": str(CORPUS_DIR),
        "rules": ["empty", "no_words", "no_content", "incomplete"],
        "benchmark": {
            "description": "every query the benchmark generator produced; "
                           "well formed by construction, so any refusal is a "
                           "false rejection",
            "n": bench_score["n"],
            "n_rejected": bench_score["n_rejected"],
            "false_rejection_rate": bench_score["rejection_rate"],
            "by_family": by_family,
            "rejected_queries": bench_score["rejected_queries"],
        },
        "hand_authored_well_formed": {
            "description": "well-formed queries written to include the cases "
                           "the benchmark's own filter rejects -- acronym, "
                           "hyphen, gerund, bare keyword, statement, and "
                           "out-of-domain but well formed",
            "n": valid_score["n"],
            "n_rejected": valid_score["n_rejected"],
            "false_rejection_rate": valid_score["rejection_rate"],
            "rejected_queries": valid_score["rejected_queries"],
        },
        "hand_authored_malformed": {
            "description": "malformed queries written by hand, with the "
                           "reason each is malformed; two keyboard mashes are "
                           "expected misses, because the check has no "
                           "dictionary and no language model",
            "n": malformed_score["n"],
            "n_rejected": malformed_score["n_rejected"],
            "n_expected_rejected": expected_rejected,
            "rejection_rate": _rate(malformed_score["n_rejected"],
                                    expected_rejected),
            "documented_misses": misses,
            "by_rule": malformed_score["by_rule"],
        },
        "harvested_stems": {
            "description": "the question stems the benchmark generator emits "
                           "and rejects, harvested from the corpus and "
                           "labelled by hand; the only population of "
                           "malformed text not written by the author of the "
                           "rule",
            "n_harvested": len(stems),
            "n_labelled": len(labelled),
            "n_unlabelled": len(unlabelled),
            "unlabelled_queries": unlabelled,
            "n_malformed": len(mal),
            "n_malformed_rejected": len(mal_rejected),
            "rejection_rate_on_malformed": _rate(len(mal_rejected), len(mal)),
            "n_well_formed": len(good),
            "n_well_formed_rejected": len(good_rejected),
            "false_rejection_rate_on_well_formed": _rate(len(good_rejected),
                                                          len(good)),
            "false_rejected_queries": [s["query"] for s in good_rejected],
            "missed_malformed_queries": [s["query"] for s in mal
                                         if not assess_query_form(s["query"]).rejected],
            "by_rule": _score([s["query"] for s in labelled])["by_rule"],
        },
        "counterfactual_benchmark_rule": {
            "description": "what a runtime check that reused the benchmark's "
                           "own `_subject_is_usable` filter would have done "
                           "to the same stems; the filter is a rule about "
                           "subjects, so it is evaluated on the subject",
            "n_well_formed": len(good),
            "n_well_formed_rejected": len(cf_rejected_good),
            "false_rejection_rate_on_well_formed": _rate(len(cf_rejected_good),
                                                          len(good)),
            "n_malformed": len(mal),
            "n_malformed_rejected": len(cf_rejected_mal),
            "rejection_rate_on_malformed": _rate(len(cf_rejected_mal), len(mal)),
            "false_rejected_examples": [s["query"] for s in cf_rejected_good][:10],
        },
        "cost": {
            "microseconds_per_query": round(per_query_us, 1),
            "timing_repeats": TIMING_REPEATS,
            "note": "the check runs before retrieval, so a request it refuses "
                    "costs no embedding pass, no cross-encoder pass and no "
                    "model call",
        },
    }

    payload["retrieval_placement"] = CONFIG.modality.position
    write_result("exp10_form_validator", payload)

    rows = [
        ["benchmark queries (all well formed)",
         f"{payload['benchmark']['n']}",
         f"{payload['benchmark']['n_rejected']}",
         f"{payload['benchmark']['false_rejection_rate']:.3f}"],
        ["hand-authored well formed",
         f"{payload['hand_authored_well_formed']['n']}",
         f"{payload['hand_authored_well_formed']['n_rejected']}",
         f"{payload['hand_authored_well_formed']['false_rejection_rate']:.3f}"],
        ["hand-authored malformed",
         f"{payload['hand_authored_malformed']['n_expected_rejected']}",
         f"{payload['hand_authored_malformed']['n_rejected']}",
         f"{payload['hand_authored_malformed']['rejection_rate']:.3f}"],
        ["harvested stems, hand-labelled malformed",
         f"{payload['harvested_stems']['n_malformed']}",
         f"{payload['harvested_stems']['n_malformed_rejected']}",
         f"{payload['harvested_stems']['rejection_rate_on_malformed']:.3f}"],
        ["harvested stems, hand-labelled well formed",
         f"{payload['harvested_stems']['n_well_formed']}",
         f"{payload['harvested_stems']['n_well_formed_rejected']}",
         f"{payload['harvested_stems']['false_rejection_rate_on_well_formed']:.3f}"],
        ["counterfactual: the benchmark's own rule, on well-formed stems",
         f"{payload['counterfactual_benchmark_rule']['n_well_formed']}",
         f"{payload['counterfactual_benchmark_rule']['n_well_formed_rejected']}",
         f"{payload['counterfactual_benchmark_rule']['false_rejection_rate_on_well_formed']:.3f}"],
    ]
    table = markdown_table(
        ["Population", "n", "refused", "rate"], rows)
    (RESULTS_DIR / "exp10_form_validator.md").write_text(
        "# Experiment 10 -- Runtime query-form validation\n\n"
        "The check refuses a request before retrieval if it is not a well-formed\n"
        "question. A refusal is only acceptable if it is rare on well-formed\n"
        "input, so both rates are reported together.\n\n"
        + table + "\n\n"
        f"Cost: {payload['cost']['microseconds_per_query']:.1f} microseconds per "
        "query.\n",
        encoding="utf-8")
    print(f"[exp10] wrote {RESULTS_DIR / 'exp10_form_validator.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
