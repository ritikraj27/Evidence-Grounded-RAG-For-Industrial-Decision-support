#!/usr/bin/env python3
"""Answer a generator sheet with the provider-hosted generator.

**Why this exists.** The RO5 replication on the industrial corpus was
underpowered: the account that produced the focus corpus's answers had hit
its token-plan limit, so the replication ran with in-session agents as the
generator, and 93% of their claims were supported. A base rate that high
gives the comparison no power to discriminate. The provider is reachable
again, so the replication can be run with **the same generator that produced
the focus corpus's answers** -- which is what makes it a replication rather
than a different experiment.

**What is reused, verbatim.** The request itself: the shipped system prompt
(`run_generation_eval.CONDITIONS["cautious"]`), the shipped context
formatting, the shipped request shape, temperature, seed and output budget.
`run_generation_eval._call` is called directly rather than reimplemented, so
the two corpora are answered by the same code path.

**Empty completions.** A reasoning model can spend its whole output budget
thinking and return no text. That is neither an answer nor a refusal, so it
is recorded as its own status and retried once at a larger budget. It is
never counted as a refusal.

Usage:
    python scripts/run_generator_api.py --sheet <sheet.json> \
        --out <answers.json> [--concurrency 6]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "scripts"))

os.environ.setdefault("MTP_VARIANT", "industrial")

from run_generation_eval import (  # noqa: E402
    CONDITIONS, EmptyCompletion, _call, _llm_config,
)


def answer_one(cfg: dict, item: dict) -> dict:
    """One request, with retries: a larger budget for an empty completion, and
    backoff for a rate-limited request.

    A rate-limited request is not a refusal and not an empty answer, so it is
    retried rather than recorded. A request that still fails is recorded as
    a failure with its reason, and is never counted as an answer.
    """
    question = item["query"]
    context = item["context"]
    delay = 5.0
    for attempt in range(6):
        try:
            resp = _call(cfg, context, question)
            text = _text_of(resp)
            if text.strip():
                return {"index": item["index"], "answer": text, "status": "ok"}
            raise EmptyCompletion("empty completion")
        except EmptyCompletion:
            retry = dict(cfg)
            retry["max_tokens"] = int(cfg.get("max_tokens", 1024)) * 4
            try:
                resp = _call(retry, context, question)
                text = _text_of(resp)
                if text.strip():
                    return {"index": item["index"], "answer": text,
                            "status": "ok_after_retry"}
            except Exception:
                pass
            return {"index": item["index"], "answer": "", "status": "empty"}
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 500, 502, 503, 529) and attempt < 5:
                time.sleep(delay)
                delay = min(delay * 2, 60.0)
                continue
            return {"index": item["index"], "answer": "", "status": "error",
                    "error": f"HTTPError: HTTP Error {exc.code}"}
        except Exception as exc:  # a transport or provider error
            if attempt < 5:
                time.sleep(delay)
                delay = min(delay * 2, 60.0)
                continue
            return {"index": item["index"], "answer": "", "status": "error",
                    "error": f"{type(exc).__name__}: {exc}"[:300]}


def _text_of(resp: dict) -> str:
    parts = []
    for block in resp.get("content", []) or []:
        if block.get("type") == "text":
            parts.append(block.get("text", ""))
    return "".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sheet", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--concurrency", type=int, default=2)
    ap.add_argument("--condition", default="cautious")
    ap.add_argument("--resume", default=None,
                    help="an answers file to resume from: its successful "
                         "answers are kept and only the failures are retried")
    args = ap.parse_args()

    cfg = _llm_config()
    if cfg is None:
        print("[gen-api] no API credential found; nothing to do.")
        return 2
    cfg["system"] = CONDITIONS[args.condition]

    sheet = json.loads(Path(args.sheet).read_text(encoding="utf-8"))
    items = sheet["items"]

    done: dict[int, dict] = {}
    if args.resume:
        prev = json.loads(Path(args.resume).read_text(encoding="utf-8"))
        for rec in prev.get("answers", []):
            if rec.get("status") == "ok" or rec.get("status") == "ok_after_retry":
                done[int(rec["index"])] = rec
        items = [it for it in items if int(it["index"]) not in done]
        print(f"[gen-api] resuming: {len(done)} answers already succeeded, "
              f"{len(items)} to request", flush=True)

    print(f"[gen-api] {len(items)} items, model={cfg['model']}, "
          f"concurrency={args.concurrency}", flush=True)

    done_count = 0
    records: list[dict] = []
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        for record in pool.map(lambda it: answer_one(cfg, it), items):
            records.append(record)
            done_count += 1
            if done_count % 20 == 0 or done_count == len(items):
                print(f"[gen-api] {done_count}/{len(items)}", flush=True)
    records.extend(done.values())
    records.sort(key=lambda r: r["index"])

    statuses: dict[str, int] = {}
    for rec in records:
        statuses[rec["status"]] = statuses.get(rec["status"], 0) + 1
    payload = {
        "schema": "mtp.generator-answers/1",
        "generator": cfg["model"],
        "base_url": cfg["base_url"],
        "condition": args.condition,
        "system_prompt": cfg["system"],
        "max_tokens": cfg.get("max_tokens", 1024),
        "n_items": len(records),
        "status_counts": statuses,
        "answers": records,
    }
    Path(args.out).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"[gen-api] statuses: {statuses} -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
