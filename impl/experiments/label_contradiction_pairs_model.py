#!/usr/bin/env python3
"""Annotate the contradiction pairs with a model judge, blind to the detector.

**Why this exists.** The contradiction gate's precision cannot be computed
from any proxy available on this corpus: every proxy is defined by one of the
gate's own branches, so a proxy cannot credit an alarm that the other branch
raised. The only way to put a number on the precision is to put the pairs in
front of readers. `label_contradiction_pairs.py` is the instrument; this is
one of the readers.

**What it is and is not.** The annotator here is a *model*, not a person. Its
labels are therefore reported with that provenance attached, and the result
is only meaningful alongside a second, independent annotator: the agreement
between two annotators that do not share a model is the evidence that the
labels are a property of the pairs rather than of one annotator's habits.
This script writes annotator A's labels; annotator B's are written by a
separate run and the two are compared by `--score`.

**Blind by construction.** The judge is shown the rubric and the two
passages and nothing else. It does not see the detector's NLI probability,
its topical similarity, its numeric-conflict list, or the stratum the pair
came from, so it cannot anchor on what the detector concluded. The stratum
is recorded in the output for scoring, not sent to the judge.

Usage (the key is read from the environment by the wrapper script):

    MTP_LLM_API_KEY=... python experiments/label_contradiction_pairs_model.py \
        --input ../results_focus/exp11_judge_input.json \
        --out   ../results_focus/exp11_judge_a_labels.json
"""
from __future__ import annotations

import argparse
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

#: The five labels a judge may assign. The order is the rubric's order, but
#: it is not used for matching -- only the set is.
#:
#: `MTP_JUDGE_LABELS` overrides the set, which is how the industrial-corpus
#: experiment's six-label rubric -- the same tree with the contradiction
#: branch split into its numeric and qualitative forms -- is run through this
#: same instrument.
LABELS = tuple(
    os.environ.get(
        "MTP_JUDGE_LABELS",
        "contradiction,granularity,supersession,term_mismatch,no_conflict",
    ).split(","))

#: How many times one pair is retried before it is recorded as unlabelled.
RETRIES = int(os.environ.get("MTP_JUDGE_RETRIES", "5"))

#: Seconds between retries. The delay grows with the attempt so a provider
#: that is momentarily overloaded gets room to recover.
RETRY_DELAY = float(os.environ.get("MTP_JUDGE_RETRY_DELAY", "8"))

SYSTEM = (
    "You are a careful technical editor judging whether two passages from "
    "industrial documentation contradict each other. You follow a written "
    "rubric exactly, you judge only the passages you are given, and you "
    "answer with a single label and nothing else."
)

#: The instruction block. It is identical for every pair, so it is sent as a
#: cached prefix when the provider supports prompt caching: the rubric is
#: charged once for the whole sheet rather than 158 times.
_PREAMBLE = """\
Read the two passages and decide what label from the rubric applies.

{instructions}

{rubric}

Answer with exactly one of: {allowed}. Reply with the label and nothing else
-- one word, no punctuation, no explanation. If you are uncertain, still give
the closest label; the uncertainty is recorded separately by the harness.
"""

_PAIR = """\
---
PASSAGE A:
{passage_a}

---
PASSAGE B:
{passage_b}
"""


def _config() -> dict:
    key = os.environ.get("MTP_LLM_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise SystemExit(
            "no API key in the environment. Use "
            "impl/scripts/run_contradiction_labeling.sh, which reads the key "
            "from ~/.mtp_llm_key without echoing it.")
    return {
        "api_key": key,
        "base_url": os.environ.get(
            "MTP_LLM_BASE_URL", "https://api.anthropic.com").rstrip("/"),
        "model": os.environ.get("MTP_LLM_MODEL", "claude-haiku-4-5-20251001"),
        "cache_control": os.environ.get("MTP_LLM_CACHE_CONTROL", "0") == "1",
    }


def _call(cfg: dict, blocks: list[dict]) -> str:
    body = {
        "model": cfg["model"],
        "max_tokens": 64,
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


def annotate(pairs: list[dict], rubric: str, instructions: str,
             cfg: dict) -> dict:
    labels: dict[str, str] = {}
    notes: dict[str, str] = {}
    raw: dict[str, str] = {}
    failed: list[int] = []
    allowed = ", ".join(LABELS)

    preamble = _PREAMBLE.format(instructions=instructions, rubric=rubric,
                                 allowed=allowed)
    preamble_block: dict = {"type": "text", "text": preamble}
    if cfg.get("cache_control"):
        preamble_block["cache_control"] = {"type": "ephemeral"}

    for i, p in enumerate(pairs, 1):
        pair_block = {"type": "text", "text": _PAIR.format(
            passage_a=p["passage_a"], passage_b=p["passage_b"])}
        blocks = [preamble_block, pair_block]
        text = ""
        label = None
        for attempt in range(RETRIES):
            try:
                text = _call(cfg, blocks)
                label = _parse(text)
                if label:
                    break
            except (urllib.error.URLError, urllib.error.HTTPError,
                    TimeoutError, OSError, json.JSONDecodeError) as exc:
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
        if not label:
            label = _parse(text)
        if label:
            labels[str(p["pair_id"])] = label
            raw[str(p["pair_id"])] = text.strip()[:200]
        else:
            failed.append(p["pair_id"])
            notes[str(p["pair_id"])] = "no parsable label returned"
        if i % 10 == 0 or i == len(pairs):
            print(f"[judge] {i}/{len(pairs)} labelled, {len(failed)} failed",
                  flush=True)

    return {
        "annotator": os.environ.get("MTP_JUDGE_NAME", "judge_a"),
        "model": cfg["model"],
        "rubric_version": "mtp.contradiction-labels/1",
        "blind": True,
        "labels": labels,
        "notes": notes,
        "raw_responses": raw,
        "unlabelled_pair_ids": failed,
        "strata": {str(p["pair_id"]): p["stratum"] for p in pairs},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True,
                    help="the blind judge input sheet")
    ap.add_argument("--out", required=True,
                    help="where the annotations are written")
    ap.add_argument("--limit", type=int, default=0,
                    help="label only the first N pairs (a smoke test)")
    args = ap.parse_args()

    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    pairs = data["pairs"]
    if args.limit:
        pairs = pairs[:args.limit]
    cfg = _config()
    out = annotate(pairs, data["rubric"], data["instructions"], cfg)
    Path(args.out).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"[judge] wrote {args.out}: {len(out['labels'])} labelled, "
          f"{len(out['unlabelled_pair_ids'])} unlabelled, model {cfg['model']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
