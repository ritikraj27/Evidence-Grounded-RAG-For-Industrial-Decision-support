#!/usr/bin/env python3
"""Prepare a generator sheet, and score the answers that come back.

**Why this exists.** The RO5 measurement on the industrial corpus needs
generated answers, and the provider account that produced the focus
corpus's answers hit its token-plan limit. The measurement is not blocked
on the provider: it needs *a* generator, and the framework's generator is
injected. So this script prepares the sheet a generator needs -- the
question and the retrieved passages, in the same format and with the same
prompt as the shipped generation -- and then scores the answers that come
back with the framework's own claim machinery.

The substitution is recorded, not hidden: the answers come from a different
model family on a different corpus, so this run is a *replication* of the
RO5 measurement rather than a second measurement of the same thing. What it
tests is whether the relationship between the confidence band and claim
correctness is a property of the evidence or of one generator.

Usage:
    prepare_generator_sheet.py sheet --out <sheet.json> --n 60
    prepare_generator_sheet.py score --sheet <sheet.json> \
        --answers <answers.json> --out <claims.json>
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "scripts"))

os.environ.setdefault("MTP_VARIANT", "industrial")

from common import load_benchmark, load_index  # noqa: E402
from run_generation_eval import _rag_context, _retrieve  # noqa: E402

#: The shipped generator's system prompt, verbatim. A replication that
#: changed the prompt would not be a replication.
CAUTIOUS = (
    "You answer questions about industrial engineering documentation. "
    "Answer only from the documents given. If the documents do not contain "
    "the answer, say that the documents do not contain it. Be brief."
)


def build_sheet(out: Path, n: int) -> None:
    index = load_index()
    bench = load_benchmark()
    fw = _framework(index)

    items = []
    for q in bench["queries"]:
        if not q["gold"]:
            continue
        trace = _retrieve(fw, q["query"], q["category"])
        evidence_ids = list(trace.reranked[:10])
        items.append({
            "index": len(items),
            "query": q["query"],
            "context": _rag_context(index, evidence_ids),
            "evidence_ids": evidence_ids,
        })
        if len(items) >= n:
            break

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "schema": "mtp.generator-sheet/1",
        "system_prompt": CAUTIOUS,
        "corpus": "InduSight industrial regulatory corpus (eCFR)",
        "n_items": len(items),
        "items": items,
    }, indent=2), encoding="utf-8")
    print(f"[gen] {len(items)} items -> {out}")


def _framework(index):
    from src.pipeline import Framework

    return Framework(index)


def score(sheet_path: Path, answers_path: Path, out: Path) -> None:
    from src.claims import split_into_claims
    from run_generation_eval import _claim_support

    sheet = json.loads(sheet_path.read_text(encoding="utf-8"))
    answers = json.loads(answers_path.read_text(encoding="utf-8"))
    index = load_index()

    raw = answers.get("answers", answers)
    if isinstance(raw, dict):
        raw = [{"index": k, "answer": v} for k, v in raw.items()]
    by_index = {str(a["index"]): a.get("answer", "") for a in raw}
    claims = []
    for item in sheet["items"]:
        text = by_index.get(str(item["index"]))
        if not text:
            continue
        parts = split_into_claims(text)
        bare = not parts
        if bare and text.strip():
            parts = [text.strip()]
        scored = _claim_support(index, parts, item["evidence_ids"], bare=bare)
        for ci, (c, s) in enumerate(zip(parts, scored)):
            claims.append({
                "key": _key(item["query"], c),
                "query": item["query"],
                "claim_index": ci,
                "claim": c,
                "candidates": item["evidence_ids"],
                "support": float(s.get("support", 0.0)),
                "band": _band(float(s.get("support", 0.0))),
                "shipped_supported": bool(s.get("supported", False)),
                "bare": bare,
                "is_refusal": bool(_REFUSAL_RE.search(c)),
                "n_claims_in_answer": len(parts),
                "claim_position": ci,
            })

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "schema": "mtp.generated-claims/1",
        "generator": answers.get("generator", "unspecified"),
        "arm": "rag_nogate",
        "n_claims": len(claims),
        "claims": claims,
    }, indent=2), encoding="utf-8")
    print(f"[gen] {len(claims)} claims from "
          f"{len({c['query'] for c in claims})} answers -> {out}")


def _band(q: float) -> str:
    from src.config import CONFIG

    if q >= CONFIG.claim.grounded_threshold:
        return "grounded"
    if q >= CONFIG.claim.inferred_threshold:
        return "inferred"
    return "uncertain"


def judge_sheets(claims_path: Path, bench_path: Path, outdir: Path,
                 prefix: str = "exp19") -> None:
    """Write the two judge sheets for the industrial claims.

    One shows the benchmark's gold passage (the correctness question), the
    other shows the passages the band was computed over (the scoring
    question). The same claims, two questions.
    """
    from src.config import ARTIFACT_DIR
    from src.pipeline import Index

    claims_doc = json.loads(claims_path.read_text(encoding="utf-8"))
    bench = json.loads(bench_path.read_text(encoding="utf-8"))
    by_query = {q["query"]: q for q in bench["queries"]}
    index = Index.load(ARTIFACT_DIR / "index")
    chunk_text = index.chunk_text

    items_gold, items_retrieved = [], []
    for c in claims_doc["claims"]:
        bq = by_query.get(c["query"], {})
        gold_answer = bq.get("answer") or ""
        gold_text = ""
        for gid in bq.get("gold") or []:
            if gid in chunk_text:
                gold_text = chunk_text[gid]
                break
        retrieved = "\n\n".join(chunk_text[cid] for cid in c["candidates"]
                                 if cid in chunk_text)
        items_gold.append({"key": c["key"], "claim": c["claim"],
                           "evidence": gold_text[:4000],
                           "gold_answer": str(gold_answer)[:600]})
        items_retrieved.append({"key": c["key"], "claim": c["claim"],
                                "evidence": retrieved[:4000],
                                "gold_answer": str(gold_answer)[:600]})

    rubric = (
        "Decide how well the reference passage supports the claim.\n\n"
        "* `supported` -- the reference passage entails the claim: everything "
        "the claim asserts is stated by the passage.\n"
        "* `partially_supported` -- the passage supports part of the claim "
        "and the claim adds something the passage does not state.\n"
        "* `unsupported` -- the passage does not state what the claim "
        "asserts. The claim may still be true; the passage simply does not "
        "say it.\n"
        "* `contradicted` -- the passage states something that cannot be "
        "true at the same time as the claim.\n\n"
        "Paraphrase is not unsupported: a claim that restates the passage in "
        "different words is `supported`. A claim that is true but broader "
        "than the passage is `partially_supported`.\n")
    outdir.mkdir(parents=True, exist_ok=True)
    for name, items in (("gold", items_gold), ("retrieved", items_retrieved)):
        path = outdir / f"{prefix}_judge_input_{name}.json"
        path.write_text(json.dumps({
            "schema": "mtp.claim-judge-input/1",
            "rubric": rubric,
            "labels_allowed": ["supported", "partially_supported", "unsupported",
                               "contradicted"],
            "items": items,
        }, indent=2), encoding="utf-8")
        print(f"[gen] judge sheet ({name}): {len(items)} items -> {path.name}")


_REFUSAL_RE = __import__("re").compile(
    r"do(es)? not contain|cannot be (determined|computed|answered)|"
    r"not (stated|specified|provided|given)|no (information|answer|value)|"
    r"insufficient information", __import__("re").IGNORECASE)


def _key(query: str, claim: str) -> str:
    import hashlib

    return hashlib.sha1(f"{query}\x00{claim}".encode("utf-8")).hexdigest()[:16]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sheet")
    s.add_argument("--out", required=True)
    s.add_argument("--n", type=int, default=60)
    sc = sub.add_parser("score")
    sc.add_argument("--sheet", required=True)
    sc.add_argument("--answers", required=True)
    sc.add_argument("--out", required=True)
    js = sub.add_parser("judge-sheets")
    js.add_argument("--claims", required=True)
    js.add_argument("--bench", required=True)
    js.add_argument("--outdir", required=True)
    js.add_argument("--prefix", default="exp19")
    args = ap.parse_args()
    if args.cmd == "sheet":
        build_sheet(Path(args.out), args.n)
    elif args.cmd == "score":
        score(Path(args.sheet), Path(args.answers), Path(args.out))
    else:
        judge_sheets(Path(args.claims), Path(args.bench), Path(args.outdir),
                     prefix=args.prefix)
    return 0


if __name__ == "__main__":
    sys.exit(main())
