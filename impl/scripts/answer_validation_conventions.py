#!/usr/bin/env python3
"""How much of the answer-accuracy column is a property of the scoring convention.

Two questions the thesis reports both columns for but never measured:

* **G19** -- how often do the two shipped tests (``correct_nli`` and
  ``correct_keyterm``) disagree, question by question? The count is the
  direct measure of how much the convention matters for a given question.
* **G18** -- what happens to the arm-level comparison under a scoring
  convention taken from the literature, rather than one of the two
  already in the code?

Nothing is re-run. The generator answers are in the shipped result files
and the gold strings are in the benchmark, so both questions are answerable
from what already exists.

The added conventions are the two standard lexical ones:

* **SQuAD 2.0** -- normalised exact match and token-level F1. The
  normalisation is the one in ``evaluate-v2.0.py``: lowercase, strip
  punctuation, drop the articles ``a|an|the``, collapse whitespace.
* **PopQA** -- containment: "any substring of the prediction is an exact
  match of any of the gold answers" (arXiv:2212.10511, section 3.1).

The fifth convention an LLM judge on semantic equivalence (BrowseComp's
rule) is **not** applied here; it is recorded as not done, in
``research/18_answer_validation_conventions.md``.

Usage:
    python impl/scripts/answer_validation_conventions.py
"""
from __future__ import annotations

import json
import random
import re
import string
import sys
from itertools import combinations
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "impl"))
from src.config import CONFIG  # noqa: E402

RES = ROOT / "impl" / "results_focus"
BENCH = ROOT / "impl" / "data" / "benchmark_focus" / "benchmark.json"

CONDITIONS = [
    ("cautious", "exp8_generation.json"),
    ("answering", "exp8_generation_answering.json"),
]

#: The five arms the generator-side comparison is reported over.
ARMS = ["rag_nogate", "rag@fitted", "rag@random", "rag@transferred",
        "long_context"]

#: The arm the framework is compared against, and the other paired
#: comparisons the thesis reports.
PAIRS = [
    ("rag@fitted", "rag_nogate"),
    ("rag@transferred", "rag_nogate"),
    ("rag@random", "rag_nogate"),
    ("rag_nogate", "long_context"),
]

_PUNCT = set(string.punctuation)
_ARTICLES = re.compile(r"\b(a|an|the)\b")


# --------------------------------------------------------------------------
# The scoring conventions
# --------------------------------------------------------------------------

def squad_normalize(s: str) -> str:
    """The normalisation in SQuAD 2.0's ``evaluate-v2.0.py``.

    Lowercase, remove the articles, remove all punctuation, collapse
    whitespace. It does not convert units, rescale or round: ``"69%"``
    normalises to ``"69"`` and ``"69 percent"`` normalises to
    ``"69 percent"``, and the two stay unequal.
    """
    s = s.lower()
    s = "".join(ch for ch in s if ch not in _PUNCT)
    s = _ARTICLES.sub(" ", s)
    return " ".join(s.split())


def squad_exact(answer: str, gold: str) -> bool:
    """SQuAD ``compute_exact``: normalised string equality."""
    return squad_normalize(answer) == squad_normalize(gold)


def squad_f1(answer: str, gold: str) -> float:
    """SQuAD token-level F1 over the normalised strings."""
    p = squad_normalize(answer).split()
    g = squad_normalize(gold).split()
    if not p or not g:
        return float(p == g)
    common: dict[str, int] = {}
    for tok in p:
        if tok in g and g.count(tok) > common.get(tok, 0):
            common[tok] = common.get(tok, 0) + 1
    same = sum(common.values())
    if same == 0:
        return 0.0
    precision = same / len(p)
    recall = same / len(g)
    return 2 * precision * recall / (precision + recall)


def popqa_containment(answer: str, gold: str) -> bool:
    """PopQA's rule: the gold appears somewhere in the prediction.

    PopQA states it as "any substring of the prediction is an exact match
    of any of the gold answers", which is the gold being contained in the
    prediction. The match is case-insensitive, as in PopQA's own scorer.
    """
    return gold.strip().lower() in answer.lower()


#: The conventions, keyed by the name they are reported under. The first
#: two are the shipped ones, read out of the record rather than recomputed.
#: The third and fourth are added here.
CONVENTIONS = [
    "nli", "keyterm", "squad_nem", "squad_f1", "popqa_containment",
]
NEW_CONVENTIONS = ["squad_nem", "squad_f1", "popqa_containment"]

F1_THRESHOLD = 0.5
"""The threshold at which a token-level F1 counts as a correct answer.

SQuAD reports F1 as a continuous score and reports the exact-match
figure beside it; it does not threshold F1. A binary rule is needed here
only to put F1 on the same footing as the other four conventions in the
paired tests, and 0.5 is the midpoint of the score's range and the same
value the project's own support threshold uses.
"""


def score_record(rec: dict, gold: str) -> dict[str, float | bool]:
    """The five verdicts on one answered question."""
    answer = rec.get("answer_text") or ""
    f1 = squad_f1(answer, gold)
    return {
        "nli": bool(rec.get("correct_nli")),
        "keyterm": bool(rec.get("correct_keyterm")),
        "squad_nem": squad_exact(answer, gold),
        "squad_f1": f1 >= F1_THRESHOLD,
        "popqa_containment": popqa_containment(answer, gold),
    }


# --------------------------------------------------------------------------
# The statistics
# --------------------------------------------------------------------------

def mcnemar(b: int, c: int) -> float:
    """Exact two-sided McNemar: 2*P(X <= min(b,c)), X ~ Binom(b+c, 0.5)."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) * (0.5 ** n))


def cohen_kappa(pairs: list[tuple[bool, bool]]) -> float | None:
    """Cohen's kappa for two binary raters over the same items."""
    n = len(pairs)
    if n == 0:
        return None
    both = sum(1 for a, b in pairs if a and b)
    first = sum(1 for a, _ in pairs if a)
    second = sum(1 for _, b in pairs if b)
    po = both / n
    pe = (first / n) * (second / n)
    if abs(1 - pe) < 1e-12:
        return None
    return (po - pe) / (1 - pe)


def bootstrap_mean_diff(xs: list[float], ys: list[float],
                         n_boot: int = 10000, seed: int = 20261112
                         ) -> tuple[float, float, float]:
    """Paired bootstrap for the mean of ``x - y``.

    Returns (mean difference, low 95%, high 95%). The resampling is over
    *pairs*, and the seed is fixed, so the interval is reproducible.
    """
    diffs = [x - y for x, y in zip(xs, ys)]
    n = len(diffs)
    if n == 0:
        return 0.0, 0.0, 0.0
    rng = random.Random(seed)
    means = []
    for _ in range(n_boot):
        sample = [diffs[rng.randrange(n)] for _ in range(n)]
        means.append(sum(sample) / n)
    means.sort()
    lo = means[int(0.025 * n_boot)]
    hi = means[min(n_boot - 1, int(0.975 * n_boot))]
    return sum(diffs) / n, lo, hi


def agreement_matrix(scored: dict[str, list[dict]]) -> dict:
    """The paired agreement of every pair of conventions, per arm.

    For each pair this is the contingency table of the two verdicts on
    the same question, Cohen's kappa, and the exact McNemar p-value for
    the discordant pairs.
    """
    out: dict = {}
    for x, y in combinations(CONVENTIONS, 2):
        key = f"{x}_vs_{y}"
        out[key] = {}
        for arm, rows in scored.items():
            pairs = [(r[x], r[y]) for r in rows]
            b = sum(1 for p, q in pairs if p and not q)
            c = sum(1 for p, q in pairs if q and not p)
            both = sum(1 for p, q in pairs if p and q)
            neither = len(pairs) - b - c - both
            out[key][arm] = {
                "n": len(pairs),
                "both_true": both,
                "x_only": b,
                "y_only": c,
                "both_false": neither,
                "disagreement_rate": round((b + c) / len(pairs), 6)
                if pairs else None,
                "cohen_kappa": cohen_kappa(pairs),
                "mcnemar_p": mcnemar(b, c),
            }
    return out


def paired_comparison(scored: dict[str, list[dict]],
                      arm_a: str, arm_b: str) -> dict:
    """One arm against another under every convention.

    For the binary conventions the test is the exact McNemar on the
    discordant pairs; for token-level F1 the score is continuous, so the
    comparison is the paired bootstrap of the mean difference.
    """
    by_q_a = {r["query"]: r for r in scored.get(arm_a, [])}
    by_q_b = {r["query"]: r for r in scored.get(arm_b, [])}
    shared = sorted(set(by_q_a) & set(by_q_b))
    out: dict = {"n_pairs": len(shared), "tests": {}}
    for conv in CONVENTIONS:
        if conv == "squad_f1":
            a = [squad_f1(by_q_a[q]["answer_text"], by_q_a[q]["gold"])
                 for q in shared]
            b = [squad_f1(by_q_b[q]["answer_text"], by_q_b[q]["gold"])
                 for q in shared]
            mean, lo, hi = bootstrap_mean_diff(a, b)
            out["tests"][conv] = {
                "mean_a": round(sum(a) / len(a), 6) if a else None,
                "mean_b": round(sum(b) / len(b), 6) if b else None,
                "mean_difference": round(mean, 6),
                "ci95_low": round(lo, 6),
                "ci95_high": round(hi, 6),
                "excludes_zero": bool(lo > 0 or hi < 0),
            }
            continue
        b_only = sum(1 for q in shared if by_q_a[q][conv] and not by_q_b[q][conv])
        a_only = sum(1 for q in shared if by_q_b[q][conv] and not by_q_a[q][conv])
        out["tests"][conv] = {
            "arm_a_only": b_only,
            "arm_b_only": a_only,
            "p_value": mcnemar(b_only, a_only),
        }
    return out


# --------------------------------------------------------------------------
# The run
# --------------------------------------------------------------------------

def load_bench() -> dict[str, str]:
    bench = json.loads(BENCH.read_text(encoding="utf-8"))
    return {q["query"]: (q.get("answer") or "") for q in bench["queries"]}


def collect(gen: dict, gold_by_query: dict[str, str]) -> dict[str, list[dict]]:
    """The scored rows per arm: answered, answerable questions only.

    A declined answer has no verdict to score, so the conventions are
    only defined on questions the system answered.
    """
    scored: dict[str, list[dict]] = {}
    for arm in ARMS:
        rows = []
        for rec in (gen.get("records") or {}).get(arm, []):
            if not rec.get("answerable") or not rec.get("answered"):
                continue
            gold = gold_by_query.get(rec["query"])
            if not gold:
                continue
            row = {"query": rec["query"], "gold": gold,
                   "answer_text": rec.get("answer_text") or ""}
            row.update(score_record(rec, gold))
            rows.append(row)
        scored[arm] = rows
    return scored


def main() -> int:
    gold_by_query = load_bench()
    report: dict = {
        "status": "run",
        "purpose": "G18 and G19: the answer-accuracy column's dependence "
                   "on the scoring convention, measured on the shipped answers",
        "conventions": CONVENTIONS,
        "new_conventions": NEW_CONVENTIONS,
        "f1_threshold": F1_THRESHOLD,
        "sources": {
            "generation": [f for _, f in CONDITIONS],
            "benchmark": str(BENCH.relative_to(ROOT)),
        },
        "conditions": {},
    }

    for cond, fname in CONDITIONS:
        path = RES / fname
        if not path.exists():
            print(f"  skip {fname} is not present")
            continue
        gen = json.loads(path.read_text(encoding="utf-8"))
        scored = collect(gen, gold_by_query)

        cond_out: dict = {"file": fname, "arms": {}, "pairs": {}}

        for arm, rows in scored.items():
            arm_out: dict = {"n_answered_answerable": len(rows),
                             "accuracy": {}}
            for conv in CONVENTIONS:
                if conv == "squad_f1":
                    vals = [squad_f1(r["answer_text"], r["gold"]) for r in rows]
                    arm_out["accuracy"][conv] = {
                        "mean_f1": round(sum(vals) / len(vals), 6) if vals else None,
                        "n_at_or_above_threshold": sum(
                            1 for v in vals if v >= F1_THRESHOLD),
                        "threshold": F1_THRESHOLD,
                    }
                else:
                    n_ok = sum(1 for r in rows if r[conv])
                    arm_out["accuracy"][conv] = {
                        "n_correct": n_ok,
                        "accuracy": round(n_ok / len(rows), 6) if rows else None,
                    }
            # The spread between the most and the least lenient convention.
            accs = [v["accuracy"] for k, v in arm_out["accuracy"].items()
                    if k != "squad_f1" and v["accuracy"] is not None]
            arm_out["spread_max_minus_min"] = round(max(accs) - min(accs), 6)
            arm_out["best_convention"], arm_out["worst_convention"] = (
                max(((k, v["accuracy"]) for k, v in arm_out["accuracy"].items()
                     if k != "squad_f1" and v["accuracy"] is not None),
                    key=lambda kv: kv[1])[0],
                min(((k, v["accuracy"]) for k, v in arm_out["accuracy"].items()
                     if k != "squad_f1" and v["accuracy"] is not None),
                    key=lambda kv: kv[1])[0],
            )
            cond_out["arms"][arm] = arm_out

        # The agreement between conventions, per arm.
        cond_out["agreement"] = agreement_matrix(scored)

        # The consensus: how many questions every convention calls correct,
        # and how many every convention calls wrong.
        consensus = {}
        for arm, rows in scored.items():
            if not rows:
                continue
            all_true = sum(1 for r in rows if all(r[c] for c in CONVENTIONS))
            all_false = sum(1 for r in rows if not any(r[c] for c in CONVENTIONS))
            consensus[arm] = {
                "n": len(rows),
                "all_conventions_correct": all_true,
                "no_convention_correct": all_false,
                "convention_dependent": len(rows) - all_true - all_false,
            }
        cond_out["consensus"] = consensus

        for arm_a, arm_b in PAIRS:
            cond_out["pairs"][f"{arm_a}_vs_{arm_b}"] = paired_comparison(
                scored, arm_a, arm_b)

        report["conditions"][cond] = cond_out

    out_json = RES / "exp8_answer_validation_conventions.json"
    report["retrieval_placement"] = CONFIG.modality.position

    out_json.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    print(f"wrote {out_json.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
