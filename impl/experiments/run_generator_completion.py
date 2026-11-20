"""Can the available generators answer this benchmark at all?

Experiment 8's replication on a second generator could not be run: the
harness recorded the run as not-run because the generator returned no text
on one question and the retries could not rescue it. An empty completion is
neither an answer nor a refusal, so it must not be counted as either -- and
the question this asks is which generators can answer the benchmark's own
questions, and on which families they fail.

The measurement is one request per question per model, at the output budget
the shipped run used, with the same context the pipeline would give the
generator. Where a request comes back empty, it is asked again with a larger
budget, because "the model needed more room to think" and "the model loops"
are different diagnoses and only one of them is fixable by configuration.
"""
from __future__ import annotations

import json
import os
import random
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "impl"))
sys.path.insert(0, str(ROOT / "impl" / "experiments"))

from src.config import CONFIG, RESULTS_DIR  # noqa: E402

import run_generation_eval as exp8  # noqa: E402

SEED = 20261118
MODELS = [m.strip() for m in os.environ.get(
    "MTP_GEN_COMPLETION_MODELS", "MiniMax-M3,MiniMax-M3.1-Flash").split(",")
    if m.strip()]
BASE = os.environ.get("MTP_LLM_BASE_URL", "https://api.minimax.io/anthropic")
MAX_TOKENS = int(os.environ.get("MTP_LLM_MAX_TOKENS", "1024"))
BIG_TOKENS = int(os.environ.get("MTP_GEN_COMPLETION_BIG_TOKENS", "4096"))
N_CONTROL = int(os.environ.get("MTP_GEN_COMPLETION_CONTROL", "22"))

KEY = Path(os.path.expanduser(
    os.environ.get("MTP_LLM_KEY_FILE", "~/.mtp_llm_key"))).read_text().strip()


def _call(model: str, context: str, question: str, max_tokens: int) -> dict:
    body = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": 0,
        "system": exp8.CONDITIONS["answering"],
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": context},
            {"type": "text", "text": question}]}],
    }
    req = urllib.request.Request(
        BASE + "/v1/messages", data=json.dumps(body).encode("utf-8"),
        headers={"content-type": "application/json", "x-api-key": KEY,
                 "authorization": f"Bearer {KEY}",
                 "anthropic-version": "2023-06-01"}, method="POST")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            resp = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"empty": True, "error": f"HTTP {e.code}", "seconds": 0.0}
    except Exception as e:  # noqa: BLE001
        return {"empty": True, "error": repr(e)[:120], "seconds": 0.0}
    usage = resp.get("usage", {})
    text = exp8._text_of(resp)
    return {
        "empty": not text.strip(),
        "stop_reason": resp.get("stop_reason"),
        "output_tokens": usage.get("output_tokens"),
        "thinking_tokens": (usage.get("output_tokens_details")
                            or {}).get("thinking_tokens", 0),
        "n_text_blocks": sum(1 for b in resp.get("content", [])
                             if b.get("type") == "text"),
        "seconds": round(time.time() - t0, 1),
    }


def main() -> int:
    index = exp8.load_index()
    bench = exp8.load_benchmark()
    fw = exp8.Framework(index)

    # The harness asks the answerable questions first, so its question order
    # is not the benchmark's.
    answerable = [q for q in bench["queries"] if q["category"] != "unanswerable"]
    unanswerable = [q for q in bench["queries"] if q["category"] == "unanswerable"]
    questions = answerable + unanswerable

    # The table family is where the failure concentrates, so it is measured in
    # full and a sample of the rest is measured as a control.
    table = [q for q in questions if "table" in q["family"]]
    others = [q for q in questions if "table" not in q["family"]]
    rng = random.Random(SEED)
    control = rng.sample(others, min(N_CONTROL, len(others)))
    sample = table + control

    print(f"[exp13] {len(table)} table questions + {len(control)} control "
          f"questions, models {MODELS}", flush=True)

    records: list[dict] = []
    for model in MODELS:
        print(f"[exp13] model {model} ...", flush=True)
        for n, q in enumerate(sample, 1):
            trace = exp8._retrieve(
                fw, q["query"],
                q["category"] if q["category"] != "unanswerable" else None)
            context = exp8._rag_context(index, list(trace.reranked[:10]))
            r = _call(model, context, q["query"], MAX_TOKENS)
            rec = {"model": model, "family": q["family"],
                   "query": q["query"], "max_tokens": MAX_TOKENS,
                   "empty": r["empty"], "stop_reason": r.get("stop_reason"),
                   "output_tokens": r.get("output_tokens"),
                   "thinking_tokens": r.get("thinking_tokens"),
                   "seconds": r.get("seconds")}
            if r.get("error"):
                rec["error"] = r["error"]
            # The follow-up: does a bigger budget rescue it?
            if r["empty"] and not r.get("error"):
                r2 = _call(model, context, q["query"], BIG_TOKENS)
                rec["empty_at_big_budget"] = r2["empty"]
                rec["big_budget_output_tokens"] = r2.get("output_tokens")
                rec["big_budget_thinking_tokens"] = r2.get("thinking_tokens")
            records.append(rec)
            if n % 10 == 0 or r["empty"]:
                print(f"[exp13]   {model} {n}/{len(sample)} "
                      f"{'EMPTY' if r['empty'] else 'ok'}", flush=True)

    summary: dict = {}
    for model in MODELS:
        mine = [r for r in records if r["model"] == model]
        tab = [r for r in mine if "table" in r["family"]]
        ctl = [r for r in mine if "table" not in r["family"]]
        empties = [r for r in mine if r["empty"]]
        rescued = [r for r in empties if r.get("empty_at_big_budget") is False]
        summary[model] = {
            "n_questions": len(mine),
            "n_empty": len(empties),
            "empty_rate": len(empties) / len(mine) if mine else None,
            "n_table": len(tab),
            "n_empty_table": sum(1 for r in tab if r["empty"]),
            "n_control": len(ctl),
            "n_empty_control": sum(1 for r in ctl if r["empty"]),
            "n_rescued_by_bigger_budget": len(rescued),
            "n_empty_even_at_big_budget": sum(
                1 for r in empties
                if r.get("empty_at_big_budget") is True),
            "mean_thinking_tokens": (
                sum(r.get("thinking_tokens") or 0 for r in mine) / len(mine)
                if mine else None),
        }

    payload = {
        "seed": SEED,
        "design": ("one request per question per generator, at the output "
                   "budget the shipped run used, with the context the "
                   "pipeline gives the generator; an empty completion is "
                   "retried once with a larger budget"),
        "models": MODELS,
        "max_tokens": MAX_TOKENS,
        "big_budget_tokens": BIG_TOKENS,
        "prompt_condition": "answering",
        "n_table_questions": len(table),
        "n_control_questions": len(control),
        "summary": summary,
        "records": records,
        # The questions are retrieved, so the result sits on the retrieval
        # configuration it was taken under. The stamp lets the build say so
        # rather than assume it.
        "retrieval_placement": CONFIG.modality.position,
    }
    out = RESULTS_DIR / "exp13_generator_completion.json"
    out.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    print(f"[exp13] wrote {out}", flush=True)
    for m, s in summary.items():
        print(f"[exp13] {m}: {s['n_empty']}/{s['n_questions']} empty "
              f"(table {s['n_empty_table']}/{s['n_table']}, control "
              f"{s['n_empty_control']}/{s['n_control']}), "
              f"{s['n_rescued_by_bigger_budget']} rescued by a bigger budget",
              flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
