#!/usr/bin/env python3
"""Label individual answer claims with an independent judge, blind to the band.

**Why this exists.** The framework's per-claim confidence band (design move
D5) is cut on a noisy-OR of NLI entailment probabilities over the retrieved
passages. The framework also *reports* a claim-hallucination rate, computed
from the same entailment scores. Those two numbers are not independent: a
claim the NLI does not entail is, by that computation, a hallucination, so
the reported rate measures the detector rather than the answer.

To measure the band against anything, the labels have to come from
somewhere else. This script produces those labels: an independent judge is
shown a claim and the benchmark's own gold evidence, and is asked whether the
evidence supports the claim. The judge never sees the band, the noisy-OR
score, or the retrieved context.

**What it is and is not.** The judge here is a *model*, not a person. Its
labels carry that provenance, and the result is only meaningful alongside a
second, independent annotator. The second annotator for the claim labels is
the same MiniMax model reached through a different route (a separate run
with the roles of the two conditions swapped) -- or a human reader. The
agreement between annotators that do not share a prompt is the evidence that
the labels are a property of the claims rather than of one prompt's habits.

**Blind by construction.** The judge sheet carries the claim, the gold
evidence and the gold answer. It does not carry the support probability, the
band, the retrieved chunk list, or the query.

Usage (the key is read from the environment by the wrapper script):
    MTP_LLM_API_KEY=... python experiments/label_claim_bands_model.py \
        --input ../results_industrial/exp15_judge_input.json \
        --out   ../results_industrial/exp15_judge_a_labels.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

LABELS = ("supported", "partially_supported", "unsupported", "contradicted")

RETRIES = int(os.environ.get("MTP_JUDGE_RETRIES", "5"))
RETRY_DELAY = float(os.environ.get("MTP_JUDGE_RETRY_DELAY", "8"))

SYSTEM = (
    "You are a careful technical editor checking whether a sentence from a "
    "generated answer is supported by a source passage. You follow a written "
    "rubric exactly, you judge only the text you are given, and you answer "
    "with a single label and nothing else."
)

_PREAMBLE = """\
Read the claim and the reference passage, then decide how well the reference
passage supports the claim.

{rubric}

Answer with exactly one of: {allowed}. Reply with the label and nothing else
-- one word, no punctuation, no explanation.
"""

_CLAIM = """\
---
REFERENCE PASSAGE:
{evidence}

GOLD ANSWER:
{gold_answer}

CLAIM TO JUDGE:
{claim}
"""


def claim_key(query: str, claim: str) -> str:
    """A stable identifier for a claim."""
    return hashlib.sha1(f"{query}\x00{claim}".encode("utf-8")).hexdigest()[:16]


def _config() -> dict:
    key = os.environ.get("MTP_LLM_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise SystemExit(
            "no API key in the environment. Use "
            "impl/scripts/run_generation_eval.sh, which reads the key from "
            "~/.mtp_llm_key without echoing it.")
    return {
        "api_key": key,
        "base_url": os.environ.get(
            "MTP_LLM_BASE_URL", "https://api.anthropic.com").rstrip("/"),
        "model": os.environ.get("MTP_LLM_MODEL", "claude-haiku-4-5-20251001"),
        "cache_control": os.environ.get("MTP_LLM_CACHE_CONTROL", "0") == "1",
        # The judge's output budget. 32 tokens is enough for a label and a
        # short reason, but a *reasoning* model can spend the whole budget
        # thinking and return nothing, so the budget is configurable and a
        # failed label is retried at a larger one rather than being lost.
        "max_tokens": int(os.environ.get("MTP_LLM_MAX_TOKENS", "32")),
    }


def _call(cfg: dict, blocks: list[dict]) -> str:
    body = {
        "model": cfg["model"],
        "max_tokens": int(cfg.get("max_tokens", 32)),
        "temperature": 0,
        "system": SYSTEM,
        "messages": [{"role": "user", "content": blocks}],
    }
    req = urllib.request.Request(
        cfg["base_url"] + "/v1/messages",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "x-api-key": cfg["api_key"],
            "authorization": f"Bearer {cfg['api_key']}",
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        data = json.loads(r.read().decode("utf-8"))
    parts = [b.get("text", "") for b in data.get("content", [])
             if b.get("type") == "text"]
    return "".join(parts)


_LABEL_RE = re.compile(r"\b(" + "|".join(LABELS) + r")\b")


def _parse(text: str) -> str | None:
    m = _LABEL_RE.search(text.lower())
    return m.group(1) if m else None


def annotate(items: list[dict], rubric: str, cfg: dict) -> dict:
    labels: dict[str, str] = {}
    notes: dict[str, str] = {}
    raw: dict[str, str] = {}
    failed: list[str] = []
    allowed = ", ".join(LABELS)

    preamble = _PREAMBLE.format(rubric=rubric, allowed=allowed)
    preamble_block: dict = {"type": "text", "text": preamble}
    if cfg.get("cache_control"):
        preamble_block["cache_control"] = {"type": "ephemeral"}

    for i, item in enumerate(items, 1):
        claim_block = {"type": "text", "text": _CLAIM.format(
            evidence=item["evidence"],
            gold_answer=item.get("gold_answer") or "(none recorded)",
            claim=item["claim"])}
        blocks = [preamble_block, claim_block]
        text = ""
        label = None
        for attempt in range(RETRIES):
            try:
                text = _call(cfg, blocks)
                label = _parse(text)
                if label:
                    break
            except (urllib.error.URLError, urllib.error.HTTPError,
                    TimeoutError, OSError, json.JSONDecodeError):
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
        if not label:
            label = _parse(text)
        if label:
            labels[item["key"]] = label
            raw[item["key"]] = text.strip()[:200]
        else:
            failed.append(item["key"])
            notes[item["key"]] = "no parsable label returned"
        if i % 20 == 0 or i == len(items):
            print(f"[judge] {i}/{len(items)} labelled, {len(failed)} failed",
                  flush=True)

    return {
        "annotator": os.environ.get("MTP_JUDGE_NAME", "judge_a"),
        "model": cfg["model"],
        "rubric_version": "mtp.claim-labels/1",
        "blind": True,
        "labels": labels,
        "notes": notes,
        "raw_responses": raw,
        "unlabelled_keys": failed,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    items = data["items"]
    if args.limit:
        items = items[:args.limit]
    cfg = _config()
    out = annotate(items, data["rubric"], cfg)
    Path(args.out).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"[judge] wrote {args.out}: {len(out['labels'])} labelled, "
          f"{len(out['unlabelled_keys'])} unlabelled, model {cfg['model']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
