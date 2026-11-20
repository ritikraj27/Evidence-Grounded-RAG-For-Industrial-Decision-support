#!/usr/bin/env python3
"""Ask the framework a question, interactively, and watch every stage decide.

There is no server in this project. The framework is a library
(`src/pipeline.py`), and the experiments are batch scripts that write JSON.
That is the right shape for a thesis -- every measurement has to be
reproducible from a command line -- but it makes the system awkward to poke
at by hand: "what does it actually do with *this* question?" normally means
writing a script, editing it, and running it.

This script is that driver. It loads the index the experiments use, runs the
real online path -- both retrieval legs, fusion, quota, rerank, the confidence
gate, then generation, claim assessment and contradiction detection -- and
prints what each stage produced. It is a read-only viewer: it changes no
artefact, writes no file, and touches neither the corpus nor the benchmark.

Usage
-----
    # one question
    MTP_VARIANT=focus .venv/bin/python impl/scripts/ask.py \
        "what is the economic order quantity?"

    # interactive, with a category pinned to the query
    MTP_VARIANT=focus .venv/bin/python impl/scripts/ask.py --category supply_chain_management

    # with a real generator behind the gate (needs a key; costs money)
    MTP_LLM_API_KEY=... MTP_VARIANT=focus \
        .venv/bin/python impl/scripts/ask.py --llm "what is a safety stock?"

`MTP_VARIANT` selects the corpus exactly as it does everywhere else:
`focus` for the supply-chain domain (the one the thesis is about), unset for
the six-category corpus.

Inside the interactive session:

    /category supply_chain_management   pin the category for the next queries
    /category                            clear the pinned category
    /help                                the same list
    /quit                                leave

The first query loads the embedding model and is slow (tens of seconds on
CPU); later queries are fast. The cross-encoder is loaded with it.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import ARTIFACT_DIR, CORPUS_DIR  # noqa: E402
from src.pipeline import Framework, Index  # noqa: E402

PREVIEW = 160
TOP_N = 5

SYSTEM = (
    "You answer questions about industrial engineering documentation. "
    "Answer only from the documents given. If the documents do not contain "
    "the answer, say that the documents do not contain it. Be brief."
)


def rule(title: str) -> None:
    print(f"\n--- {title} " + "-" * max(0, 72 - len(title)))


def preview(index, chunk_id: str) -> str:
    text = " ".join(index.chunk_text.get(chunk_id, "").split())
    return text[:PREVIEW] + ("…" if len(text) > PREVIEW else "")


def llm_generator() -> "callable | None":
    """A generator over an Anthropic-compatible endpoint, if a key is set.

    The endpoint, the model and the system prompt are the ones
    `experiments/run_generation_eval.py` uses, so a question asked here is
    answered under the same conditions as the measured arm. Without a key
    the framework falls back to its extractive answer, which exercises the
    retrieval, gating, claim and contradiction machinery and nothing else.
    """
    key = os.environ.get("MTP_LLM_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return None
    base = os.environ.get("MTP_LLM_BASE_URL", "https://api.anthropic.com").rstrip("/")
    model = os.environ.get("MTP_LLM_MODEL", "claude-haiku-4-5-20251001")

    def generator(query: str, context: str) -> str:
        body = {
            "model": model,
            "max_tokens": 1024,
            "temperature": 0,
            "system": SYSTEM,
            "messages": [{"role": "user",
                          "content": [{"type": "text", "text": context},
                                      {"type": "text", "text": query}]}],
        }
        req = urllib.request.Request(
            base + "/v1/messages",
            data=json.dumps(body).encode("utf-8"),
            headers={"content-type": "application/json",
                     "x-api-key": key,
                     "authorization": f"Bearer {key}",
                     "anthropic-version": "2023-06-01"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=600) as r:
            resp = json.loads(r.read().decode("utf-8"))
        return "".join(b.get("text", "") for b in resp.get("content", [])
                       if b.get("type") == "text")

    return generator


def show(fw: Framework, query: str, category: str | None) -> None:
    index = fw.index
    result = fw.answer(query, category=category)
    trace = result.trace

    print(f"\n{'=' * 76}\nQUESTION: {query}")
    if category:
        print(f"CATEGORY: {category}")
    print("=" * 76)

    if result.refusal == "form":
        # The request was refused before retrieval: it was not a question.
        rule("FORM CHECK")
        print("  REFUSED -- the request is not a well-formed question.")
        print("  Nothing was retrieved and the model was not called.")
        for line in result.answer.splitlines():
            print(f"    {line}")
        return

    rule("FORM CHECK")
    print("  PASSED -- the request is a well-formed question.")

    rule("RETRIEVAL")
    print(f"  dense candidates    : {len(trace.dense)}")
    print(f"  lexical candidates  : {len(trace.lexical)}")
    print(f"  after RRF fusion    : {len(trace.fused)}")
    print(f"  after rerank        : {len(trace.reranked_full)} scored -> "
          f"{len(trace.reranked)} delivered")
    if trace.quota_note:
        print(f"  modality quota      : {trace.quota_note}")
    for i, cid in enumerate(trace.reranked[:TOP_N], 1):
        mod = index.modality_of.get(cid, "?")
        print(f"    {i}. {cid} [{mod}] {preview(index, cid)}")

    rule("CONFIDENCE GATE")
    posterior = max(trace.posterior) if trace.posterior else float("nan")
    tau = fw.gate_model["tau"] if fw.gate_model else float("nan")
    print(f"  posterior {posterior:.3f}  vs  tau {tau:.3f}  ->  "
          f"{'REFUSE' if trace.gate_rejected else 'ACCEPT'}")
    names = fw.gate_model["feature_names"] if fw.gate_model else []
    for name, value in zip(names, trace.features):
        print(f"    {name:<28} {value:+.4f}")
    if trace.gate_rejected:
        print("\n  REFUSAL MESSAGE SENT TO THE USER:")
        for line in trace.message.splitlines():
            print(f"    {line}")

    if trace.gate_rejected:
        rule("ANSWER")
        print("  (the generator is not reached on a refused query)")
        return

    rule("ANSWER")
    answer = result.answer
    print(answer if len(answer) <= 1200 else answer[:1200] + "\n  …")

    rule("CLAIM TAGGING")
    if result.claim_assessments:
        for a in result.claim_assessments:
            print(f"  [{a.band:<9} p={a.support_prob:.3f}] {a.claim}")
    else:
        # Claims are the generator's propositions, so there is nothing to tag
        # when no generator ran: the framework falls back to an extractive
        # answer. Run with --llm to see this stage do its work.
        print("  (no generator ran, so there are no claims to tag; "
              "use --llm for this stage)")

    if result.contradiction_summary:
        rule("CONTRADICTION DETECTION")
        print(f"  {result.contradiction_summary}")
        # A finding that was recorded and withheld is shown with its
        # reason, so the reader can see that the gate looked and did not
        # speak, rather than wondering whether it ran at all.
        for f in (result.contradictions_withheld or [])[:3]:
            print(f"  withheld: {f.surface_reason}")


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    flags = {a for a in sys.argv[1:] if a.startswith("-")}

    category = None
    if "--category" in sys.argv:
        i = sys.argv.index("--category")
        category = sys.argv[i + 1] if i + 1 < len(sys.argv) else None

    index_path = ARTIFACT_DIR / "index"
    if not index_path.with_suffix(".json").exists():
        print(f"no index at {index_path}. Build it first:\n"
              f"  MTP_VARIANT=focus .venv/bin/python impl/scripts/build_index.py\n"
              f"(corpus: {CORPUS_DIR})")
        return 1

    print(f"[ask] corpus   : {CORPUS_DIR}")
    print(f"[ask] index    : {index_path}")
    print("[ask] loading models (first run takes tens of seconds)...")
    index = Index.load(index_path)
    fw = Framework(index, generator=llm_generator() if "--llm" in flags else None)
    if fw.gate_model is None:
        print("[ask] WARNING: no calibrated gate model; the gate is uncalibrated")
    else:
        print(f"[ask] gate     : tau={fw.gate_model['tau']}, "
              f"fitted on {fw.gate_model['fitted_on']['n_queries']} queries")
    print(f"[ask] generator: {'LLM' if fw.generator else 'extractive (no LLM)'}")

    if args:
        show(fw, args[0], category)
        return 0

    print("\nType a question. /help for commands, /quit to leave.")
    while True:
        try:
            line = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not line:
            continue
        if line in ("/quit", "/exit", ":q"):
            return 0
        if line == "/help":
            print("  /category <name>   pin the category for the next queries")
            print("  /category          clear it")
            print("  /quit              leave")
            continue
        if line.startswith("/category"):
            category = line.split(maxsplit=1)[1].strip() if " " in line else None
            print(f"[ask] category: {category or '(none)'}")
            continue
        show(fw, line, category)


if __name__ == "__main__":
    raise SystemExit(main())
