#!/usr/bin/env python3
"""Ablate the per-claim confidence band's own input, and re-measure it (RO5).

**What the first RO5 measurement found.** On the focus corpus, the band and
an independent judge agree on individual claims at a rate indistinguishable
from chance: Cohen's kappa 0.003 on the binary form and 0.063 on the
three-class form, over 76 claims. The `grounded` band had a *higher* error
rate (46%) than the `inferred` band (18%). A band that is not monotone in
correctness is not a confidence signal.

**What this script tests.** A band is only as good as the number it is cut
from, and that number is an NLI entailment probability computed on the claim
as the generator produced it. The generator produces Markdown: a claim can
read "SF handled a total of **3.05 billion shipments** in 2017", and the
asterisks go into the entailment model verbatim. The model has never seen
emphasis markers, and the measurement of the first RO5 run contains exactly
that case -- a verbatim quote of the source scored at 0.006.

So the ablation recomputes the support probability for every claim twice:
once on the raw claim text (what the framework ships) and once on the claim
text with Markdown stripped (what it should have been), and re-measures the
band's agreement with the judge labels each time.

If stripping the markers moves the agreement, the defect is an input
hygiene problem and the fix is one line. If it does not, the defect is in the
scoring model or in what "supported" is being asked, and the honest report
says so.

Usage:
    MTP_VARIANT=focus python experiments/run_claim_band_ablation.py \
        --claims ../results_focus/exp15_claims.json \
        --labels ../results_focus/exp15_judge_labels.json \
        --out     ../results_focus/exp16_claim_band_ablation.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import ARTIFACT_DIR, CONFIG  # noqa: E402
from src.claims import noisy_or  # noqa: E402
from src.models import nli_probs  # noqa: E402
from src.stats import cohens_kappa  # noqa: E402

#: Markdown constructs the generator emits inside a claim.
_MARKDOWN_RE = re.compile(
    r"(\*\*|__|\*|_|`|#+\s|~~|\[|\]|\(|\))")


def strip_markdown(text: str) -> str:
    """The claim with its Markdown emphasis removed.

    The emphasis is not the claim. It is the generator's rendering of the
    claim, and feeding it to an entailment model that was never trained on
    it is the same class of mistake as feeding the model a page number.
    """
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"__([^_]+)__", r"\1", text)
    text = re.sub(r"(?<!\w)\*([^*\n]+)\*(?!\w)", r"\1", text)
    text = re.sub(r"(?<!\w)_([^_\n]+)_(?!\w)", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"^#+\s*", "", text)
    text = re.sub(r"\*\*|__|~~|`", "", text)
    return re.sub(r"\s+", " ", text).strip()


def band_for(q: float) -> str:
    cfg = CONFIG.claim
    if q >= cfg.grounded_threshold:
        return "grounded"
    if q >= cfg.inferred_threshold:
        return "inferred"
    return "uncertain"


def _agreement(rows: list[dict], band_key: str) -> dict:
    """Agreement between the band and the reference labels."""
    labelled = [r for r in rows if r.get("reference") is not None]
    if not labelled:
        return {"n": 0}
    band_order = ["grounded", "inferred", "uncertain"]
    ref_to_band = {"supported": "grounded", "partially_supported": "inferred",
                   "unsupported": "uncertain", "contradicted": "uncertain"}
    three = [(band_order.index(ref_to_band[r["reference"]]),
              band_order.index(r[band_key]))
             for r in labelled if r["reference"] in ref_to_band]
    binary = [(1 if r[band_key] == "grounded" else 0,
               1 if r["reference"] == "supported" else 0)
              for r in labelled]
    kappa3, lo3, hi3 = cohens_kappa([x[0] for x in three], [x[1] for x in three])
    kappa2, lo2, hi2 = cohens_kappa([x[0] for x in binary], [x[1] for x in binary])
    per_band = {}
    for band in band_order:
        sel = [r for r in labelled if r[band_key] == band]
        n = len(sel)
        correct = sum(1 for r in sel if r["reference_correct"])
        per_band[band] = {
            "n": n,
            "error_rate": (n - correct) / n if n else None,
        }
    return {
        "n": len(labelled),
        "kappa_3class": kappa3, "kappa_3class_ci95": [lo3, hi3],
        "kappa_binary": kappa2, "kappa_binary_ci95": [lo2, hi2],
        "per_band_error_rate": per_band,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--claims", required=True)
    ap.add_argument("--labels", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    claims_doc = json.loads(Path(args.claims).read_text(encoding="utf-8"))
    labels = json.loads(Path(args.labels).read_text(encoding="utf-8"))["labels"]
    claims = claims_doc["claims"]

    from src.pipeline import Index

    index = Index.load(ARTIFACT_DIR / "index")
    chunk_text = index.chunk_text

    rows = []
    n_pairs = 0
    for c in claims:
        ref = labels.get(c["key"])
        if not ref:
            continue
        candidates = [cid for cid in c.get("candidates", []) if cid in chunk_text]
        row = dict(c)
        row["reference"] = ref
        row["reference_correct"] = (ref == "supported")
        if not candidates:
            row["support_raw"] = c["support"]
            row["support_stripped"] = c["support"]
            row["band_raw"] = band_for(c["support"])
            row["band_stripped"] = band_for(c["support"])
            rows.append(row)
            continue

        passages = [chunk_text[cid] for cid in candidates]
        raw = c["claim"]
        stripped = strip_markdown(raw)
        pairs = []
        for p in passages:
            pairs.append((p, raw))
            pairs.append((p, stripped))
        probs = nli_probs(pairs, CONFIG.claim.nli_model)
        n = len(passages)
        raw_e = [probs[i]["entailment"] for i in range(n)]
        strip_e = [probs[n + i]["entailment"] for i in range(n)]
        n_pairs += len(pairs)
        row["support_raw"] = noisy_or(raw_e)
        row["support_stripped"] = noisy_or(strip_e)
        row["band_raw"] = band_for(row["support_raw"])
        row["band_stripped"] = band_for(row["support_stripped"])
        row["markdown_present"] = raw != stripped
        rows.append(row)

    print(f"[ro5] recomputed {n_pairs} NLI pairs over {len(rows)} claims")

    payload = {
        "schema": "mtp.claim-band-ablation/1",
        "n_claims": len(rows),
        "n_pairs_scored": n_pairs,
        "n_claims_with_markdown": sum(1 for r in rows
                                      if r.get("markdown_present")),
        "markdown_strip_only": _agreement(rows, "band_stripped"),
        "as_shipped": _agreement(rows, "band_raw"),
        "shipped_support_from_generation": _agreement(rows, "band"),
        "band_shift_counts": dict(Counter(
            f'{r["band_raw"]}->{r["band_stripped"]}' for r in rows)),
        "note": "'shipped_support_from_generation' uses the support values "
                "recorded by the generation run, which scored the raw claim "
                "over a possibly different candidate set; 'as_shipped' "
                "recomputes it here over the same candidates so that the "
                "only difference between the two rows is the Markdown.",
    }

    # The paired comparison: how many claims change band, and do they
    # change toward agreement?
    changed = [r for r in rows if r["band_raw"] != r["band_stripped"]]
    improved = sum(
        1 for r in changed
        if (r["band_stripped"] == "grounded") == (r["reference"] == "supported")
        and not ((r["band_raw"] == "grounded") == (r["reference"] == "supported")))
    payload["n_band_changed_by_stripping"] = len(changed)
    payload["n_band_changed_toward_agreement"] = improved

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, default=float), encoding="utf-8")
    print(json.dumps({k: v for k, v in payload.items()
                      if k in ("n_claims", "n_claims_with_markdown",
                               "n_band_changed_by_stripping",
                               "n_band_changed_toward_agreement",
                               "band_shift_counts")}, indent=2))
    for key in ("as_shipped", "markdown_strip_only"):
        block = payload[key]
        print(f"[ro5] {key}: kappa3={block['kappa_3class']:.4f} "
              f"kappa2={block['kappa_binary']:.4f} "
              f"per_band_error={ {k: (round(v['error_rate'], 3) if v['error_rate'] is not None else None) for k, v in block['per_band_error_rate'].items()} }")
    print(f"[ro5] wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
