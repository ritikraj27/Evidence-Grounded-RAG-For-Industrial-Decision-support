#!/usr/bin/env python3
"""Does the confidence gate reject *malformed* questions?

The gate is an evidence gate: it decides whether the retrieved context is
sufficient to answer. It never asks whether the query is well-formed. That
distinction is easy to state and easy to hand-wave, so this measures it.

The malformed queries are not invented here. They are the question stems the
benchmark's own generator produced and then rejected under `_subject_is_usable`
-- the fragments the generator emitted by matching mid-clause or after a
truncated word, such as "a teep" or "since manufacturing in an existing
plant". The population is harvested by re-running the generator's extraction
over the corpus and keeping exactly the candidates its own quality filter
discards.

The measurement answers one question: at the fitted operating point, what
fraction of malformed queries does the gate let through? A high fraction
means the gate cannot be credited with rejecting invalid questions -- which is
a limitation of the claim, and belongs in the deliverables as one.

Run:
    MTP_VARIANT=focus .venv/bin/python impl/experiments/run_form_probe.py
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from form_stems import harvest_stems  # noqa: E402
from src.config import ARTIFACT_DIR, CONFIG, CORPUS_DIR, RESULTS_DIR  # noqa: E402
from src.pipeline import Framework, Index  # noqa: E402

#: How many malformed queries to push through the pipeline. Each one costs a
#: cross-encoder pass over the candidate pool, so this is a budget, not a
#: sample size.
N_PROBE = 30
SEED = 20261118


def harvest_malformed() -> list[str]:
    """Re-run the generator's extraction and keep what its quality filter drops.

    This is the same population the benchmark builder rejected: the query
    stems it would have emitted if `_subject_is_usable` were not applied.
    The harvest itself lives in `form_stems.py`, because the form validator
    measures on the same population and the two sets of numbers are only
    comparable if the population is identical.
    """
    return [s["query"] for s in harvest_stems()]


def main() -> int:
    print("[form] harvesting malformed question stems ...", flush=True)
    candidates = harvest_malformed()
    print(f"[form] {len(candidates)} malformed stems in the corpus", flush=True)
    if not candidates:
        print("[form] no malformed stems found; nothing to measure")
        return 1

    rng = random.Random(SEED)
    pool = candidates[:] if len(candidates) <= N_PROBE else rng.sample(candidates, N_PROBE)

    index = Index.load(ARTIFACT_DIR / "index")
    fw = Framework(index)
    tau = float(fw.gate_model.get("tau", 0.5)) if fw.gate_model else None

    print(f"[form] running {len(pool)} probes through the gate ...", flush=True)
    records = []
    for i, q in enumerate(pool, 1):
        trace = fw.retrieve(q, category=None)
        records.append({
            "query": q,
            "accepted": not trace.gate_rejected,
            "posterior": round(max(trace.posterior) if trace.posterior else 0.0, 4),
            "n_accepted_chunks": len(trace.accepted),
        })
        if i % 10 == 0:
            print(f"[form]   {i}/{len(pool)}", flush=True)

    n = len(records)
    accepted = sum(1 for r in records if r["accepted"])
    rate = accepted / n if n else float("nan")
    mean_pos = sum(r["posterior"] for r in records) / n if n else float("nan")

    payload = {
        "experiment": "form probe",
        "question": "At the fitted operating point, what fraction of "
                    "malformed queries does the retrieval-confidence gate "
                    "let through?",
        "corpus": str(CORPUS_DIR),
        "n_candidates_harvested": len(candidates),
        "n_probed": n,
        "n_accepted_by_gate": accepted,
        "acceptance_rate": round(rate, 4),
        "mean_posterior": round(mean_pos, 4),
        "tau": tau,
        "seed": SEED,
        "population": "question stems the benchmark generator itself rejected "
                      "under _subject_is_usable -- mid-clause fragments and "
                      "truncated words, harvested by re-running the "
                      "generator's extraction over the corpus",
        "per_query": records,
        "retrieval_placement": CONFIG.modality.position,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DIR / "exp9_form_probe.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"[form] gate accepted {accepted}/{n} malformed queries "
          f"({rate:.1%}), mean posterior {mean_pos:.3f} against tau {tau}")
    for r in records[:8]:
        print(f"[form]   {'ACCEPT' if r['accepted'] else 'REFUSE'}  "
              f"p={r['posterior']:.3f}  {r['query'][:78]}")
    print(f"[form] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
