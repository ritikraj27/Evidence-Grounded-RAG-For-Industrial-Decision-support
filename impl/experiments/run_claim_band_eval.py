#!/usr/bin/env python3
"""Measure what the per-claim confidence band buys (RO5).

**The problem.** The framework decomposes an answer into atomic claims and
tags each one `grounded`, `inferred` or `uncertain`, cut on a noisy-OR of
NLI entailment probabilities over the retrieved passages. The tag is
shipped, its extraction is validated, and its labels are audited. What is
not measured is what the tag *does*: whether a practitioner who trusts only
the `grounded` claims is safer than one who reads the whole answer.

**The measurement.** A claim is either right or wrong, and the framework has
no independent way to say which. Its own "claim hallucination rate" is
computed from the same entailment scores the band is cut from, so a claim the
NLI does not entail is by that computation a hallucination: the rate
measures the detector, not the answer.

So the labels come from outside the band:

* a **judge** (a model, blind to the band) reads each claim beside the
  benchmark's gold evidence and says whether the evidence supports it;
* a **rule** reads each claim beside the benchmark's gold answer string and
  says whether the claim states that answer.

The rule is the independent check on the judge, and it is the one that
decides the headline number, because it is mechanical and reproducible.

**The value test.** Keeping only the `grounded` claims is obviously better
than keeping none of them. The comparison that matters is against keeping
the *same number* of claims by some rule that does not use the band:

* ``random``  -- keep a random subset of the same size;
* ``shortest``-- keep the shortest claims of the same size (a surface
  artefact: short claims are simpler and more often right);
* ``first``   -- keep the first claims of the same size (a position
  artefact: generators front-load the safe claims).

If the band is doing work, its risk curve lies below all three at matched
coverage. If it does not, the tagging is decoration.

**Per answer, not per corpus.** The decision a practitioner makes is
"which sentences of *this* answer do I act on". So the policies are applied
within an answer, and the coverage is the fraction of that answer's claims
kept.

Usage:
    python experiments/run_claim_band_eval.py input \
        --generation ../results_focus/exp8_generation.json \
        --bench ../data/benchmark_focus/benchmark.json \
        --out-prefix ../results_focus/exp15

    python experiments/run_claim_band_eval.py eval \
        --generation ../results_focus/exp8_generation.json \
        --bench ../data/benchmark_focus/benchmark.json \
        --labels ../results_focus/exp15_judge_labels.json \
        --out ../results_focus/exp15_claim_band_eval.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# The entailment pass is the expensive step -- hundreds of (passage, claim)
# pairs at the model's full window -- and it is embarrassingly parallel.
# Torch's default thread count leaves most of the machine idle.
try:
    import torch

    torch.set_num_threads(int(os.environ.get(
        "MTP_TORCH_THREADS", "0") or 0) or (os.cpu_count() or 4))
except Exception:  # pragma: no cover - torch is always present
    pass

from src.config import ARTIFACT_DIR, CONFIG  # noqa: E402
from src.stats import bootstrap_ci, cohens_kappa, wilcoxon_signed_rank  # noqa: E402

SEED = 20261118

#: The rubric the judge follows.
RUBRIC = """\
Decide how well the reference passage supports the claim.

* `supported` -- the reference passage entails the claim. Everything the
  claim asserts is stated by the passage.
* `partially_supported` -- the passage supports part of the claim and the
  claim adds something the passage does not state.
* `unsupported` -- the passage does not state what the claim asserts. The
  claim may still be true; the passage simply does not say it.
* `contradicted` -- the passage states something that cannot be true at the
  same time as the claim.

Judge only the claim and the passage. Do not reward a claim for being
plausible, and do not penalise one for being terse.
"""

_BAND_RE = re.compile(r"[^a-z0-9]+")


def _norm(text: str) -> str:
    return _BAND_RE.sub(" ", (text or "").lower()).strip()


def claim_key(query: str, claim: str) -> str:
    return hashlib.sha1(f"{query}\x00{claim}".encode("utf-8")).hexdigest()[:16]


def wilson(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for a proportion."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = successes / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, centre - half), min(1.0, centre + half))


def band_for(q: float) -> str:
    cfg = CONFIG.claim
    if q >= cfg.grounded_threshold:
        return "grounded"
    if q >= cfg.inferred_threshold:
        return "inferred"
    return "uncertain"


# --------------------------------------------------------------------------
# input
# --------------------------------------------------------------------------
def build_input(generation_paths: list[Path], bench_path: Path,
                out_prefix: Path, arm: str = "all",
                evidence_mode: str = "gold",
                sample: int = 0) -> tuple[Path, Path]:
    """Write the blind judge sheet and the full claim index.

    `generation_paths` may be several files, and `arm` may be "all"; the
    claims are pooled across them and de-duplicated by their content hash.
    A claim's text is the same whichever arm produced it, but the *evidence*
    differs, so the pooling is over distinct claims and the first
    occurrence (in a fixed file and arm order) supplies the observation.

    `evidence_mode` chooses what the judge is shown:

    ``gold``
        the benchmark's gold passage -- the passage the answer was supposed
        to come from. This is the *correctness* question: is this claim
        right?
    ``retrieved``
        the passages the band itself was computed over -- the arm's own
        candidates. This is the *scoring* question: does the band agree
        with an independent reader on the same evidence?

    Both are asked because a band that disagrees with a judge could be
    wrong in two different ways: it might not track correctness, or its
    entailment scorer might not agree with another reader on the same
    text. One protocol cannot tell them apart.
    """
    bench = json.loads(bench_path.read_text(encoding="utf-8"))
    by_query = {q["query"]: q for q in bench["queries"]}

    # The gold evidence, for the judge. It is read from the index, so the
    # judge sees the same passage the benchmark's label came from.
    from src.pipeline import Index

    index = Index.load(ARTIFACT_DIR / "index")
    chunk_text = index.chunk_text

    items: list[dict] = []
    claims: list[dict] = []
    seen: set[str] = set()
    for path in generation_paths:
        gen = json.loads(path.read_text(encoding="utf-8"))
        arms = gen.get("records", {})
        if arm != "all":
            arms = {k: v for k, v in arms.items() if k == arm}
        for arm_name, records in arms.items():
            for rec in records:
                q = rec.get("query", "")
                bq = by_query.get(q)
                if bq is None:
                    continue
                gold_answer = bq.get("answer")
                golds = bq.get("gold") or []
                if not golds or not gold_answer:
                    continue
                gold_text = ""
                for gid in golds:
                    if gid in chunk_text:
                        gold_text = chunk_text[gid]
                        break
                if not gold_text:
                    continue
                for ci, c in enumerate(rec.get("claims", [])):
                    text = c.get("claim", "")
                    if not text or c.get("is_refusal"):
                        continue
                    key = claim_key(q, text)
                    if key in seen:
                        continue
                    seen.add(key)
                    support = float(c.get("support", 0.0))
                    candidates = c.get("candidates", [])
                    retrieved = "\n\n".join(
                        chunk_text[cid] for cid in candidates if cid in chunk_text)
                    claims.append({
                        "key": key,
                        "query": q,
                        "claim_index": ci,
                        "claim": text,
                        "support": support,
                        "band": band_for(support),
                        "shipped_supported": bool(c.get("supported", False)),
                        "answerable": True,
                        "candidates": candidates,
                        "arm": arm_name,
                        "source_file": path.name,
                        "gold_in_candidates": bool(set(golds) & set(candidates)),
                        "n_claims_in_answer": rec.get("n_claims", 0),
                        "claim_position": ci,
                    })
                    evidence = gold_text if evidence_mode == "gold" else retrieved
                    items.append({
                        "key": key,
                        "claim": text,
                        "evidence": evidence[:4000],
                        "gold_answer": str(gold_answer)[:600],
                    })

    if sample and len(items) > sample:
        # A deterministic subsample: sorted by the claim's content hash, so
        # the same claims are drawn whatever order the files were read in.
        items.sort(key=lambda it: it["key"])
        keep = {it["key"] for it in items[:sample]}
        items = items[:sample]
        claims = [c for c in claims if c["key"] in keep]
        claims.sort(key=lambda c: c["key"])

    out_prefix.parent.mkdir(parents=True, exist_ok=True)
    judge_path = out_prefix.parent / f"{out_prefix.name}_judge_input.json"
    judge_path.write_text(json.dumps({
        "schema": "mtp.claim-judge-input/1",
        "rubric": RUBRIC,
        "labels_allowed": ["supported", "partially_supported", "unsupported",
                           "contradicted"],
        "items": items,
    }, indent=2), encoding="utf-8")

    claims_path = out_prefix.parent / f"{out_prefix.name}_claims.json"
    claims_path.write_text(json.dumps({
        "arm": arm,
        "generation": [str(p) for p in generation_paths],
        "evidence_mode": evidence_mode,
        "n_claims": len(claims),
        "claims": claims,
    }, indent=2), encoding="utf-8")

    print(f"[ro5] {len(items)} distinct claims "
          f"(evidence: {evidence_mode})")
    print(f"[ro5] judge sheet -> {judge_path}")
    print(f"[ro5] claim index -> {claims_path}")
    return judge_path, claims_path


# --------------------------------------------------------------------------
# the rule-based reference
# --------------------------------------------------------------------------
#: The gold answer must be a distinctive string for the rule to apply.
_MIN_GOLD_CHARS = 3


def rule_label(claim: str, gold_answer: str) -> str | None:
    """Does the claim state the benchmark's gold answer?

    Mechanical and independent of the band: a string comparison against the
    silver label the benchmark already carries.

    * ``supported``   -- the claim contains the gold answer.
    * ``contradicted``-- the claim contains a *different* number for the same
      measurement term as the gold answer.
    * ``None``        -- the rule does not apply, or the claim neither states
      nor contradicts the answer.
    """
    c = _norm(claim)
    g = _norm(gold_answer)
    if len(g) < _MIN_GOLD_CHARS:
        return None
    if g in c:
        return "supported"
    # A different number for the same measurement term.
    gold_numbers = re.findall(r"\d[\d,.]*", gold_answer)
    claim_numbers = re.findall(r"\d[\d,.]*", claim)
    if not gold_numbers or not claim_numbers:
        return None
    gold_terms = {w for w in re.findall(r"[A-Za-z]{3,}", gold_answer.lower())}
    claim_terms = {w for w in re.findall(r"[A-Za-z]{3,}", claim.lower())}
    if not (gold_terms & claim_terms):
        return None
    if set(gold_numbers) & set(claim_numbers):
        return None
    if gold_terms & claim_terms:
        return "contradicted"
    return None


# --------------------------------------------------------------------------
# evaluation
# --------------------------------------------------------------------------
def _risk(coverage: float, kept_correct: int, kept: int) -> float:
    return 1.0 - (kept_correct / kept) if kept else float("nan")


def evaluate(generation_paths: list[Path], bench_path: Path,
             label_paths: list[Path], out_path: Path, claims_path: Path,
             recompute: bool = False) -> dict:
    bench = json.loads(bench_path.read_text(encoding="utf-8"))
    by_query = {q["query"]: q for q in bench["queries"]}
    label_sets: dict[str, dict] = {}
    for path in label_paths:
        doc = json.loads(path.read_text(encoding="utf-8"))
        name = doc.get("annotator") or path.stem
        label_sets[name] = doc.get("labels", {})
    claims_doc = json.loads(claims_path.read_text(encoding="utf-8"))
    claims = claims_doc["claims"]

    # -- the band the practitioner actually sees --------------------------
    # The framework's band is a noisy-OR of the entailment probabilities
    # over the retrieved passages (`src/claims.py::assess_claims`). The
    # generation experiment records a *different* number: the maximum
    # entailment over the same candidates, thresholded at 0.5
    # (`run_generation_eval.py::_claim_support`). Two different functions
    # of the same evidence, and only the first one is what the answer
    # shows the practitioner. When `--recompute` is given, the framework's
    # band is recomputed here so that what is measured is what ships.
    if recompute:
        claims = _recompute_bands(claims)

    # -- the two references ----------------------------------------------
    # The rule is mechanical and independent of the band; the judges are
    # independent of the band. The rule wins where it applies, because it
    # is reproducible and it cannot drift.
    rows = []
    for c in claims:
        bq = by_query.get(c["query"], {})
        gold_answer = bq.get("answer") or ""
        rule = rule_label(c["claim"], gold_answer)
        votes = {name: ls.get(c["key"]) for name, ls in label_sets.items()}
        votes = {k: v for k, v in votes.items() if v}
        distinct = set(votes.values())
        # The consensus is the **majority** label, not the unanimous one.
        # With three annotators -- two readers and an adjudicator who saw
        # only the pairs the readers disagreed about -- a majority is what
        # resolves a contested claim, and it is what the adjudicator was
        # called for. A claim with no majority is left unlabelled, because
        # a reference the annotators could not agree on is not a reference.
        tally = Counter(votes.values())
        best, best_n = tally.most_common(1)[0] if tally else (None, 0)
        consensus = best if best_n > len(votes) / 2 else None
        ref = None
        ref_source = None
        if rule == "supported":
            ref, ref_source = "supported", "rule"
        elif consensus:
            ref, ref_source = consensus, "judge_majority"
        elif len(distinct) == 1:
            ref, ref_source = consensus, "judge_single"
        row = dict(c)
        row["judge_votes"] = votes
        row["judge_consensus"] = consensus
        row["contested"] = len(distinct) > 1
        row["rule_label"] = rule
        row["reference"] = ref
        row["reference_source"] = ref_source
        row["reference_correct"] = (ref == "supported") if ref else None
        rows.append(row)

    labelled = [r for r in rows if r["reference"] is not None]
    payload: dict = {
        "schema": "mtp.claim-band-eval/1",
        "generation": [str(p) for p in generation_paths],
        # The band is computed over retrieved passages, so the result sits on
        # the retrieval configuration it was taken under. The stamp lets the
        # build say so rather than assume it.
        "retrieval_placement": CONFIG.modality.position,
        "arm": claims_doc.get("arm"),
        "evidence_mode": claims_doc.get("evidence_mode"),
        "n_claims_total": len(rows),
        "n_claims_labelled": len(labelled),
        "n_claims_by_reference_source": dict(
            defaultdict(int, {k: sum(1 for r in rows
                                      if r["reference_source"] == k)
                              for k in {r["reference_source"] for r in rows}})),
    }

    # -- the agreement between the annotators ---------------------------
    names = sorted(label_sets)
    if len(names) >= 2:
        pairwise: dict[str, dict] = {}
        for i, a_name in enumerate(names):
            for b_name in names[i + 1:]:
                common = [r["key"] for r in rows
                          if label_sets[a_name].get(r["key"])
                          and label_sets[b_name].get(r["key"])]
                if not common:
                    continue
                a = [label_sets[a_name][k] for k in common]
                b = [label_sets[b_name][k] for k in common]
                kappa, lo, hi = cohens_kappa(a, b)
                crosstab: dict[str, int] = defaultdict(int)
                for x, y in zip(a, b):
                    crosstab[f"{x} | {y}"] += 1
                pairwise[f"{a_name} vs {b_name}"] = {
                    "n_labelled_by_both": len(common),
                    "cohens_kappa": kappa,
                    "ci95": [lo, hi],
                    "agreement_rate": sum(1 for x, y in zip(a, b) if x == y)
                    / len(common),
                    "crosstab": dict(crosstab),
                }
        payload["annotator_agreement"] = {
            "annotators": names,
            "pairwise": pairwise,
            "n_contested_claims": sum(1 for r in rows if r["contested"]),
            "n_unlabelled_claims": sum(1 for r in rows if not r["reference"]),
        }

    # -- M1: agreement between the band and the reference -----------------
    band_order = ["grounded", "inferred", "uncertain"]
    ref_to_band = {
        "supported": "grounded",
        "partially_supported": "inferred",
        "unsupported": "uncertain",
        "contradicted": "uncertain",
    }
    three = [(band_order.index(ref_to_band[r["reference"]]),
              band_order.index(r["band"]))
             for r in labelled
             if r["reference"] in ref_to_band]
    if three:
        a = [x[0] for x in three]
        b = [x[1] for x in three]
        kappa, lo, hi = cohens_kappa(a, b)
        payload["agreement_3class"] = {
            "n": len(three),
            "cohens_kappa": kappa,
            "ci95": [lo, hi],
            "bands": band_order,
            "note": "reference mapped to a band: supported->grounded, "
                    "partially_supported->inferred, "
                    "unsupported/contradicted->uncertain",
        }
    binary = [(1 if r["band"] == "grounded" else 0,
               1 if r["reference"] == "supported" else 0)
              for r in labelled]
    if binary:
        kappa, lo, hi = cohens_kappa([x[0] for x in binary],
                                      [x[1] for x in binary])
        payload["agreement_binary"] = {
            "n": len(binary),
            "cohens_kappa": kappa,
            "ci95": [lo, hi],
            "note": "band==grounded against reference==supported",
        }

    # -- M2: per-band error rate ----------------------------------------
    per_band = {}
    for band in band_order:
        sel = [r for r in labelled if r["band"] == band]
        n = len(sel)
        correct = sum(1 for r in sel if r["reference_correct"])
        # The Wilson interval is computed for the *correct* rate, so the
        # error rate's interval is its complement, reversed.
        lo, hi = wilson(correct, n)
        per_band[band] = {
            "n": n,
            "n_correct": correct,
            "error_rate": (n - correct) / n if n else None,
            "error_rate_ci95": [1.0 - hi, 1.0 - lo] if n else None,
            "correct_rate_ci95": [lo, hi] if n else None,
            "mean_support": float(np.mean([r["support"] for r in sel])) if n else None,
        }
    payload["per_band"] = per_band

    # -- M3/M4: the value test ------------------------------------------
    payload["value_test"] = _value_test(labelled, rng=random.Random(SEED))

    # -- M5: the circularity audit --------------------------------------
    shipped_hallucination = None
    arm_summary = {}
    wanted = claims_doc.get("arm")
    for path in generation_paths:
        gen = json.loads(path.read_text(encoding="utf-8"))
        arms = gen.get("arms", {})
        if wanted in arms:
            arm_summary = arms[wanted]
            break
        # The claim index may pool every arm; the shipped rate is reported
        # for one of them, and the one the index was built from is named.
        if not arm_summary and arms:
            for name in ("rag_nogate", next(iter(arms))):
                if name in arms:
                    arm_summary = arms[name]
                    break
    for scope in ("answerable", "overall"):
        block = arm_summary.get(scope)
        if isinstance(block, dict) and "hallucination_rate" in block:
            shipped_hallucination = {
                "scope": scope,
                "shipped_hallucination_rate": block["hallucination_rate"],
                "shipped_claim_support_rate": block.get("claim_support_rate"),
            }
            break
    if shipped_hallucination:
        n = len(labelled)
        incorrect = sum(1 for r in labelled if not r["reference_correct"])
        lo, hi = wilson(incorrect, n)
        shipped_hallucination["reference_hallucination_rate"] = (
            incorrect / n if n else None)
        shipped_hallucination["reference_hallucination_rate_ci95"] = [lo, hi]
        shipped_hallucination["n"] = n
        shipped_hallucination["note"] = (
            "the shipped rate counts a claim as a hallucination when the NLI "
            "does not entail it over the retrieved passages; the reference "
            "rate counts it when an independent judge reading the evidence "
            "this run used does not find the claim supported. The two are "
            "not the same measurement, and the gap between them is the size "
            "of the circularity.")
        shipped_hallucination["evidence_mode"] = claims_doc.get(
            "evidence_mode", "gold")
    payload["circularity_audit"] = shipped_hallucination

    # -- the per-answer decision statistic -------------------------------
    payload["answer_level"] = _answer_level(labelled)

    # -- the two band definitions ----------------------------------------
    if recompute:
        crosstab: dict[str, int] = defaultdict(int)
        for r in rows:
            crosstab[f'{r.get("band_generation")}->{r["band"]}'] += 1
        payload["band_definitions"] = {
            "framework": "noisy-OR of the per-chunk entailment "
                         "probabilities over the retrieved passages "
                         "(src/claims.py::assess_claims). This is the band "
                         "the answer shows the practitioner.",
            "experiment": "maximum entailment over the same candidates, "
                          "thresholded at 0.5 "
                          "(run_generation_eval.py::_claim_support). This is "
                          "the claim-support rate the papers report.",
            "n_bands_differ": sum(
                v for k, v in crosstab.items()
                if k.split("->")[0] != k.split("->")[1]),
            "crosstab": dict(crosstab),
            "note": "the two are different functions of the same evidence. "
                    "The noisy-OR assumes the witnesses fail independently, "
                    "which they do not -- ten passages about the same "
                    "subject are not ten independent trials -- so it "
                    "saturates where the maximum does not.",
        }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, default=float),
                         encoding="utf-8")
    print(f"[ro5] wrote {out_path}")
    return payload


def _cluster_bootstrap(values: list[float], clusters: list[int],
                       n_bootstrap: int = 2000, seed: int = SEED
                       ) -> tuple[float, float, float]:
    """A paired cluster bootstrap: resample the clusters, not the rows.

    The same answer appears at many coverage points, and the same answer
    contributes many rows to the gap array, so the rows are not
    independent. Resampling the rows as if they were would treat thirty
    answers as several hundred and report an interval several times too
    narrow. Here the answer is the resampling unit: a bootstrap draw takes a
    set of answers with replacement and keeps every row belonging to them.
    """
    if not values:
        return (float("nan"), float("nan"), float("nan"))
    arr = np.asarray(values, dtype=np.float64)
    groups = np.asarray(clusters, dtype=np.int64)
    unique = np.unique(groups)
    index_by_cluster = {int(g): np.flatnonzero(groups == g) for g in unique}
    rng = np.random.default_rng(seed)
    draws = np.empty(n_bootstrap, dtype=np.float64)
    for b in range(n_bootstrap):
        picked = rng.choice(unique, size=unique.size, replace=True)
        rows = np.concatenate([index_by_cluster[int(g)] for g in picked])
        draws[b] = arr[rows].mean()
    lo, hi = np.quantile(draws, [0.025, 0.975])
    return (float(arr.mean()), float(lo), float(hi))


def _value_test(labelled: list[dict], rng: random.Random) -> dict:
    """The claim-level risk-coverage comparison against the baselines.

    The policies are applied *within* an answer: for an answer of m claims,
    each policy orders the claims and the risk is measured over the first k
    of them, for k = 1..m.

    **The resampling unit is the answer, twice over.** The random baseline
    produces many orderings of the *same* answers, so its per-coverage
    values are correlated; they are averaged within the answer first. And
    the same answer then appears at every coverage point, so the comparison
    between two policies is bootstrapped with the answer as the cluster.
    """
    by_answer: dict[str, list[dict]] = defaultdict(list)
    for r in labelled:
        by_answer[r["query"]].append(r)
    answers = [v for v in by_answer.values() if len(v) >= 2]
    if not answers:
        return {"n_answers": 0}

    policies = ("band", "random", "shortest", "longest", "first")
    n_draws = 100

    # coverage -> policy -> one value per answer (that answer's mean risk at
    # that coverage).
    per_answer: dict[float, dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list))
    for ans in answers:
        m = len(ans)
        orders: dict[str, list[list[dict]]] = {}
        orders["band"] = [sorted(ans, key=lambda r: -r["support"])]
        orders["shortest"] = [sorted(ans, key=lambda r: len(r["claim"]))]
        orders["longest"] = [sorted(ans, key=lambda r: -len(r["claim"]))]
        orders["first"] = [sorted(ans, key=lambda r: r["claim_position"])]
        random_orders = []
        for _ in range(n_draws):
            shuffled = list(ans)
            rng.shuffle(shuffled)
            random_orders.append(shuffled)
        orders["random"] = random_orders

        for pol in policies:
            draws: dict[float, list[float]] = defaultdict(list)
            for seq in orders[pol]:
                kept_correct = 0
                for k, r in enumerate(seq, start=1):
                    kept_correct += 1 if r["reference_correct"] else 0
                    draws[k / m].append(1.0 - kept_correct / k)
            for cov, vals in draws.items():
                per_answer[cov][pol].append(float(np.mean(vals)))

    # Aggregate per answer, then bootstrap over answers.
    summary = {}
    for pol in policies:
        pts = []
        for cov in sorted(per_answer):
            vals = per_answer[cov][pol]
            if not vals:
                continue
            arr = np.asarray(vals)
            mean, lo, hi = bootstrap_ci(arr, n_bootstrap=2000)
            pts.append({"coverage": round(cov, 4), "risk": round(mean, 4),
                        "risk_ci95": [round(lo, 4), round(hi, 4)],
                        "n_answers": int(arr.size)})
        summary[pol] = pts

    # The comparison that matters: at matched coverage, is the band below the
    # baselines? The gap is computed per answer, and the interval is a
    # paired cluster bootstrap over answers.
    comparisons = {}
    for baseline in ("random", "shortest", "longest", "first"):
        gaps: list[float] = []
        clusters: list[int] = []
        for cov in sorted(per_answer):
            b = per_answer[cov]["band"]
            s = per_answer[cov].get(baseline) or []
            if not b or not s:
                continue
            n = min(len(b), len(s))
            for i in range(n):
                gaps.append(float(b[i]) - float(s[i]))
                clusters.append(i)
        if gaps:
            mean, lo, hi = _cluster_bootstrap(gaps, clusters)
            comparisons[f"band_minus_{baseline}"] = {
                "mean_risk_gap": mean,
                "mean_risk_gap_ci95": [lo, hi],
                "coverage_points": len(gaps),
                "note": "negative means the band's risk is lower than the "
                        "baseline's at matched coverage; the gap is computed "
                        "per answer and the interval is a paired cluster "
                        "bootstrap over answers",
            }

    # A paired test over answers at a fixed k, for the headline comparison.
    paired = {}
    for baseline in ("random", "shortest", "longest", "first"):
        band_errors: list[float] = []
        base_errors: list[float] = []
        for ans in answers:
            k = max(1, len(ans) // 2)
            band_seq = sorted(ans, key=lambda r: -r["support"])[:k]
            if baseline == "random":
                shuffled = list(ans)
                rng.shuffle(shuffled)
                other = shuffled[:k]
            elif baseline == "shortest":
                other = sorted(ans, key=lambda r: len(r["claim"]))[:k]
            elif baseline == "longest":
                other = sorted(ans, key=lambda r: -len(r["claim"]))[:k]
            else:
                other = sorted(ans, key=lambda r: r["claim_position"])[:k]
            band_errors.append(
                float(sum(1 for r in band_seq if not r["reference_correct"])))
            base_errors.append(
                float(sum(1 for r in other if not r["reference_correct"])))
        test = wilcoxon_signed_rank(band_errors, base_errors)
        paired[f"band_vs_{baseline}"] = {
            "n_answers": len(band_errors),
            "k": "half the claims of each answer",
            "mean_kept_errors_band": float(np.mean(band_errors)),
            "mean_kept_errors_baseline": float(np.mean(base_errors)),
            "wilcoxon_statistic": test.statistic,
            "wilcoxon_p": test.p_value,
            "cohens_dz": test.effect_size,
            "note": "a negative difference means the band kept fewer wrong "
                    "claims than the baseline at the same k",
        }

    # Is position confounded with length? If the generator writes its safe
    # claims first *and* writes short claims first, then "keep the first
    # claims" and "keep the short claims" are the same policy wearing two
    # hats, and the band is being beaten by a length artefact rather than by
    # an ordering one.
    confound = _position_length_confound(answers)

    return {
        "n_answers": len(answers),
        "n_claims": sum(len(a) for a in answers),
        "random_draws_per_answer": n_draws,
        "bootstrap_unit": "answer (paired cluster bootstrap)",
        "curves": summary,
        "comparisons": comparisons,
        "paired": paired,
        "position_length_confound": confound,
    }


def _position_length_confound(answers: list[list[dict]]) -> dict:
    """Is the position of a claim confounded with its length?

    If the generator writes short claims first, then "keep the first claims"
    and "keep the shortest claims" are one policy in two costumes, and a
    claim that the band loses to position is not evidence that ordering
    matters.
    """
    from scipy import stats

    positions: list[float] = []
    lengths: list[float] = []
    first_half_len: list[float] = []
    second_half_len: list[float] = []
    for ans in answers:
        ordered = sorted(ans, key=lambda r: r["claim_position"])
        for r in ordered:
            positions.append(float(r["claim_position"]))
            lengths.append(float(len(r["claim"].split())))
        half = len(ordered) // 2
        if half:
            first_half_len.append(float(np.mean(
                [len(r["claim"].split()) for r in ordered[:half]])))
            second_half_len.append(float(np.mean(
                [len(r["claim"].split()) for r in ordered[half:]])))
    rho, p = stats.spearmanr(positions, lengths) if len(positions) > 2 \
        else (float("nan"), float("nan"))
    out = {
        "spearman_position_vs_length": float(rho),
        "p_value": float(p),
        "n_claims": len(positions),
        "mean_words_first_half": float(np.mean(first_half_len))
        if first_half_len else None,
        "mean_words_second_half": float(np.mean(second_half_len))
        if second_half_len else None,
        "note": "a negative correlation means later claims are shorter, so "
                "position and length are not the same policy; a positive "
                "one means they are",
    }
    if first_half_len and second_half_len:
        diffs = [a - b for a, b in zip(first_half_len, second_half_len)]
        arr = np.asarray(diffs)
        mean, lo, hi = bootstrap_ci(arr, n_bootstrap=2000)
        out["first_minus_second_half_words"] = mean
        out["ci95"] = [lo, hi]
    return out


def _answer_level(labelled: list[dict]) -> dict:
    """The decision a practitioner actually faces.

    For each answer: how many of its claims are wrong, and how many of them
    are `grounded`. Then the two numbers that matter: the fraction of
    answers with no wrong claim at all, and the fraction of answers that are
    clean once only the `grounded` claims are kept.
    """
    by_answer: dict[str, list[dict]] = defaultdict(list)
    for r in labelled:
        by_answer[r["query"]].append(r)
    answers = list(by_answer.values())
    if not answers:
        return {"n_answers": 0}
    clean_all = sum(1 for a in answers
                    if all(r["reference_correct"] for r in a))
    clean_grounded = sum(1 for a in answers
                         if all(r["reference_correct"] for r in a
                                if r["band"] == "grounded"))
    total_claims = sum(len(a) for a in answers)
    grounded_claims = sum(1 for a in answers for r in a if r["band"] == "grounded")
    return {
        "n_answers": len(answers),
        "n_claims": total_claims,
        "answers_with_no_wrong_claim": clean_all,
        "answers_with_no_wrong_claim_rate": clean_all / len(answers),
        "answers_clean_after_keeping_grounded_only": clean_grounded,
        "answers_clean_after_keeping_grounded_only_rate":
            clean_grounded / len(answers),
        "grounded_claim_share": grounded_claims / total_claims,
        "note": "an answer with no grounded claim at all is vacuously clean "
                "under the grounded-only rule; the claim share is reported "
                "alongside so the rate is not read on its own",
    }


def _recompute_bands(claims: list[dict]) -> list[dict]:
    """Recompute the framework's own band for every claim.

    `src/claims.py::assess_claims` aggregates the per-chunk entailment
    probabilities with a noisy-OR, which is what the answer the practitioner
    reads is tagged with. The generation run records the maximum instead.

    The result is cached on disk. The entailment pass over a few thousand
    long pairs is the slowest step in the measurement and it is
    deterministic, so a re-run with a different label set should not pay for
    it twice.
    """
    import hashlib

    from src.claims import noisy_or
    from src.models import nli_probs
    from src.pipeline import Index
    from src.config import ARTIFACT_DIR

    index = Index.load(ARTIFACT_DIR / "index")
    chunk_text = index.chunk_text

    cache_path = Path(ARTIFACT_DIR) / "claim_band_cache.json"
    cache: dict = {}
    if cache_path.exists():
        try:
            cache = json.loads(cache_path.read_text(encoding="utf-8"))
        except Exception:
            cache = {}

    def cache_key(claim: str, cands: list[str]) -> str:
        blob = json.dumps([claim, cands, CONFIG.claim.nli_model])
        return hashlib.sha1(blob.encode("utf-8")).hexdigest()[:20]

    # One batched NLI call for every claim that is not already cached.
    # Calling the model once per claim costs the tokeniser and the padding
    # setup hundreds of times over, and the per-call overhead dominates the
    # actual inference.
    pairs: list[tuple[str, str]] = []
    spans: list[tuple[int, int]] = []
    keys: list[str] = []
    for c in claims:
        candidates = [cid for cid in c.get("candidates", []) if cid in chunk_text]
        start = len(pairs)
        for cid in candidates:
            pairs.append((chunk_text[cid], c["claim"]))
        spans.append((start, len(pairs)))
        keys.append(cache_key(c["claim"], candidates))

    missing = [i for i, k in enumerate(keys) if k not in cache]
    if missing:
        subset: list[tuple[str, str]] = []
        offsets: dict[int, tuple[int, int]] = {}
        for i in missing:
            start = len(subset)
            subset.extend(pairs[spans[i][0]:spans[i][1]])
            offsets[i] = (start, len(subset))
        probs = nli_probs(subset, CONFIG.claim.nli_model) if subset else []
        for i, (start, end) in offsets.items():
            q = noisy_or([p["entailment"] for p in probs[start:end]])
            cache[keys[i]] = q
        try:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(json.dumps(cache), encoding="utf-8")
        except Exception:
            pass

    out = []
    for c, key in zip(claims, keys):
        c = dict(c)
        c["band_generation"] = c["band"]
        c["support_generation"] = c["support"]
        q = cache.get(key)
        if q is None:
            c["band"] = c["band_generation"]
            c["support"] = c["support_generation"]
        else:
            c["support"] = q
            c["band"] = band_for(q)
        out.append(c)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    i = sub.add_parser("input")
    i.add_argument("--generation", required=True,
                   help="one or more generation result files, comma-separated")
    i.add_argument("--bench", required=True)
    i.add_argument("--out-prefix", required=True)
    i.add_argument("--arm", default="all",
                   help="a single arm, or 'all' to pool every arm")
    i.add_argument("--evidence", default="gold", choices=["gold", "retrieved"])
    i.add_argument("--sample", type=int, default=0,
                   help="cap the number of distinct claims (deterministic)")

    e = sub.add_parser("eval")
    e.add_argument("--generation", required=True)
    e.add_argument("--bench", required=True)
    e.add_argument("--labels", required=True,
                   help="one or more annotation files, comma-separated")
    e.add_argument("--claims", required=True)
    e.add_argument("--out", required=True)
    e.add_argument("--recompute", action="store_true",
                   help="recompute the framework's own noisy-OR band over the "
                        "recorded candidates, rather than using the "
                        "generation run's max-entailment support value")

    args = ap.parse_args()
    if args.cmd == "input":
        paths = [Path(p.strip()) for p in args.generation.split(",") if p.strip()]
        build_input(paths, Path(args.bench), Path(args.out_prefix),
                    arm=args.arm, evidence_mode=args.evidence,
                    sample=args.sample)
        return 0
    gen_paths = [Path(p.strip()) for p in args.generation.split(",") if p.strip()]
    lab_paths = [Path(p.strip()) for p in args.labels.split(",") if p.strip()]
    evaluate(gen_paths, Path(args.bench), lab_paths,
             Path(args.out), Path(args.claims), recompute=args.recompute)
    return 0


if __name__ == "__main__":
    sys.exit(main())
