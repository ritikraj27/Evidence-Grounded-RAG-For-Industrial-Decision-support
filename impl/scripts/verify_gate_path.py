"""Prove, executably, that the confidence gate is on the only path to the generator.

The deliverables claim a *code-level, non-bypassable* retrieval-confidence
gate: a question whose evidence is insufficient must never reach the language
model. A claim like that is worth nothing unless it can be demonstrated, so
this script demonstrates it rather than asserting it.

What it shows
-------------
1. The fitted gate artefact: the five query-level signals, the operating
   point tau, and the split it was fitted on.
2. The stage order of the online path, read off a real query's trace.
3. That on a rejected query the generator is never called -- asserted by
   instrumenting the call itself, not by reading the source.
4. That everything downstream of the gate (claim assessment, contradiction
   detection) is also skipped, so a refused query costs no model call at all.
5. The two paths in the evaluation harness that deliberately bypass the gate,
   named explicitly so a reviewer sees they are baselines and not holes.

Run:
    MTP_VARIANT=focus .venv/bin/python impl/scripts/verify_gate_path.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import ARTIFACT_DIR, BENCHMARK_DIR, RESULTS_DIR  # noqa: E402
from src import claims as claims_mod  # noqa: E402
from src import contradiction as contradiction_mod  # noqa: E402
from src.pipeline import Framework, Index  # noqa: E402


def rule(title: str) -> None:
    print(f"\n{'=' * 74}\n{title}\n{'=' * 74}")


def main() -> int:
    index = Index.load(ARTIFACT_DIR / "index")
    bench = json.loads((BENCHMARK_DIR / "benchmark.json").read_text(encoding="utf-8"))
    fw = Framework(index)

    queries = bench["queries"]
    answerable = [q for q in queries if q["gold"]]
    unanswerable = [q for q in queries if not q["gold"]]

    # -- 1. the fitted artefact -----------------------------------------
    rule("1. THE FITTED GATE ARTEFACT")
    gm = fw.gate_model
    if gm is None:
        print("NO CALIBRATED GATE MODEL -- the framework is on its fallback path.")
        return 1
    print(f"  artefact        : {ARTIFACT_DIR / 'gate_model.json'}")
    print(f"  signals         : {', '.join(gm['feature_names'])}")
    print(f"  operating point : tau = {gm['tau']}")
    print(f"  fitted on       : {gm['fitted_on']['n_queries']} queries, "
          f"base rate {gm['fitted_on']['base_rate']:.3f}")
    print("  the decision is a function of the retrieved set only -- no text "
          "from the model is consulted.")

    # -- 2. the stage order on one real query ----------------------------
    rule("2. THE ONLINE PATH, READ OFF A REAL QUERY")
    sample = answerable[0]
    trace = fw.retrieve(sample["query"], category=sample.get("category"))
    stages = [
        ("category pre-filter", f"pool -> {len([c for c in index.chunk_ids if index.category_of.get(c) == sample.get('category')])} chunks"),
        ("dense leg", f"{len(trace.dense)} candidates"),
        ("lexical leg (BM25)", f"{len(trace.lexical)} candidates"),
        ("reciprocal rank fusion", f"{len(trace.fused)} fused"),
        ("modality quota", trace.quota_note or "(no swap)"),
        ("cross-encoder rerank", f"{len(trace.reranked_full)} scored -> {len(trace.reranked)} final"),
        ("CONFIDENCE GATE", f"posterior {max(trace.posterior):.3f} vs tau {gm['tau']} -> "
                           f"{'ACCEPT' if not trace.gate_rejected else 'REJECT'}"),
        ("generation", "only reached if the gate accepted"),
    ]
    for i, (name, detail) in enumerate(stages, 1):
        print(f"  {i}. {name:<24} {detail}")

    # -- 3/4. instrument the generator and the post-gate stages -----------
    rule("3. THE GATE IS THE ONLY PATH TO THE GENERATOR")
    calls = {"generator": 0, "claims": 0, "contradiction": 0}
    real_assess = claims_mod.assess_claims
    real_detect = contradiction_mod.detect_contradictions

    def counting_assess(*a, **k):
        calls["claims"] += 1
        return real_assess(*a, **k)

    def counting_detect(*a, **k):
        calls["contradiction"] += 1
        return real_detect(*a, **k)

    claims_mod.assess_claims = counting_assess
    contradiction_mod.detect_contradictions = counting_detect

    def fake_generator(query: str, context: str) -> str:
        """Stands in for the LLM. If this ever runs on a refused query, the
        gate is not non-bypassable and the script must fail."""
        calls["generator"] += 1
        return "a generated answer"

    # The generator is injected into the framework, so the framework -- not
    # this script -- decides when it runs. This is what makes the guarantee
    # structural rather than a convention each caller has to remember.
    fw.generator = fake_generator

    checked = answerable[:3] + unanswerable[:3]
    accepted = refused = 0
    for q in checked:
        cat = q.get("category") if q["gold"] else None
        trace = fw.retrieve(q["query"], category=cat)
        if trace.gate_rejected:
            refused += 1
        else:
            accepted += 1
        # The framework makes the call, or does not.
        result = fw.answer(q["query"], category=cat)
        if trace.gate_rejected:
            assert result.accepted is False, "answer() returned an answer on a refused query"
            assert result.trace.accepted == [], "a refused query still carried accepted chunks"

    claims_mod.assess_claims = real_assess
    contradiction_mod.detect_contradictions = real_detect

    print(f"  queries checked         : {len(checked)} "
          f"({accepted} accepted by the gate, {refused} refused)")
    print(f"  generator calls         : {calls['generator']}  "
          f"(expected {accepted})")
    print(f"  claim-assessment calls  : {calls['claims']}  "
          f"(expected {accepted})")
    print(f"  contradiction calls     : {calls['contradiction']}  "
          f"(expected {accepted})")
    ok = (calls["generator"] == accepted
          and calls["claims"] == accepted
          and calls["contradiction"] == accepted)
    print(f"  VERDICT: {'PASS' if ok else 'FAIL'} -- a refused query reached no model call.")

    # -- 5. the deliberate bypasses, named -------------------------------
    rule("4. THE ONLY PATHS THAT BYPASS THE GATE (ALL ARE BASELINES)")
    print("  impl/experiments/run_generation_eval.py  arm 'rag_nogate'   -- "
          "the ablation arm that removes the gate")
    print("  impl/experiments/run_generation_eval.py  arm 'long_context' -- "
          "the whole-corpus baseline")
    print("  impl/experiments/run_long_context.py     generative_arm   -- "
          "the same whole-corpus baseline")
    print("  These are comparison arms, not production paths: each is named")
    print("  for what it removes and each is reported as a separate result.")

    # -- 6. what happens to an invalid question --------------------------
    rule("5. AN INVALID (MALFORMED) QUESTION")
    print("  There is NO runtime query validator in impl/src/. The")
    print("  malformed-question filter (_subject_is_usable) lives in")
    print("  impl/scripts/build_benchmark.py and rejects bad questions when")
    print("  the BENCHMARK is built. A question typed by a user at runtime is")
    print("  not validated for form; it is only judged on evidence.")
    probe = RESULTS_DIR / "exp9_form_probe.json"
    if probe.exists():
        d = json.loads(probe.read_text(encoding="utf-8"))
        print(f"  Measured (impl/experiments/run_form_probe.py): of {d['n_probed']} "
              f"malformed stems harvested from the generator's own rejections,")
        print(f"  the gate ACCEPTED {d['n_accepted_by_gate']} "
              f"({d['acceptance_rate']:.1%}), mean posterior "
              f"{d['mean_posterior']:.3f} against tau {d['tau']}.")
        for r in d["per_query"][:5]:
            print(f"    {'ACCEPT' if r['accepted'] else 'REFUSE'}  "
                  f"p={r['posterior']:.3f}  {r['query'][:70]}")
    print("  The gate is an EVIDENCE gate, not a FORM gate. The deliverables")
    print("  state this as a limitation and do not claim otherwise.")

    rule("SUMMARY")
    print("  The gate sits at impl/src/confidence.py:apply_gate(), applied at")
    print("  impl/src/pipeline.py in retrieve(), and enforced by an early")
    print("  return in answer(). Every framework component runs before it or")
    print("  after it; nothing runs around it.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
