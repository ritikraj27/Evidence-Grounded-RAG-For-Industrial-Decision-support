#!/usr/bin/env python3
"""Experiment 7 -- the long-context baseline arm.

The largest unresolved threat to this thesis is that the corpus is small
enough to fit in a modern context window, so a reader given everything
might simply answer the question and the retrieval machinery would be
unnecessary. The September 2026 report lists this as a limitation; here it
is measured.

The arm has two halves, and only one of them needs a generator.

**The cost half, always measured.** The long-context arm puts the whole
corpus in the prompt; the RAG arm puts ten retrieved chunks in it. The
ratio between them is the "token tax" the 2026 literature reports on
comparable corpora, and it is a property of the corpus and the pipeline,
not of any model. This half runs with no API access at all.

**The quality half, measured when a generator is available.** The same
question, the same corpus, the same scoring machinery, one difference:
the context. When no credential is reachable the half is recorded as not
run, with the reason, rather than being quietly omitted -- a missing
baseline that is not stated is worse than one that is.

**The retrieval-side proxy, always measured.** Even without a generator,
the question "can a reader find the evidence in a big context?" has a
measurable form here: with the whole corpus as the candidate set instead
of the fused shortlist, does the same cross-encoder still rank the gold
chunk inside the final context? That is the retrieval half of the
long-context problem, measured with the component the pipeline actually
uses. It is a proxy and is labelled as one -- it says nothing about what
a generative reader would do with the context it is handed.

Usage
-----
    python3 experiments/run_long_context.py

Environment (all optional; the cost half and the proxy run without any):
    MTP_LLM_API_KEY       Anthropic-compatible API key
    MTP_LLM_BASE_URL       base URL (default https://api.anthropic.com)
    MTP_LLM_MODEL          model id (default claude-haiku-4-5-20251001)
    MTP_LLM_MAX_USD        hard budget for the generative arm (default 5.00)
    MTP_LLM_MAX_QUERIES    cap on the generative arm's query count
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

# The tokenizer's Rust thread pool is sized from the machine's core count and
# oversubscribes badly when the machine is already busy: scoring 2,383
# documents per query then spends more time in thread contention than in the
# model. These two lines must run before transformers is imported.
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("OMP_NUM_THREADS", "4")

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    RESULTS_DIR,
    ROOT,
    load_benchmark,
    load_index,
    markdown_table,
    write_result,
)
from src.config import CONFIG, CORPUS_DIR  # noqa: E402
from src.pipeline import Framework  # noqa: E402

SEED = 20261118

#: The proxy scores the whole corpus per query, which is the expensive part.
#: A bounded sample is allowed, and the size and the interval are reported.
PROXY_MAX_QUERIES = int(os.environ.get("MTP_LC_PROXY_QUERIES", "0") or 0)

#: Models whose context window would hold the whole corpus. Used to say
#: plainly whether the long-context arm is even possible.
CONTEXT_WINDOWS = {
    "claude-sonnet-4-5 / claude-opus-4-5 (1M)": 1_000_000,
    "a 256K-window model": 256_000,
    "a 128K-window model (most hosted models)": 128_000,
    "a 32K-window open model": 32_768,
}

#: Cross-encoder scores are computed in slices so that scoring a whole
#: 2,383-chunk corpus at once does not exhaust memory.
SCORE_SLICE = 256


# --------------------------------------------------------------------------
# The long-context prompt
# --------------------------------------------------------------------------
def build_long_context(fw) -> tuple[str, list[str]]:
    """Render the entire corpus as one document, grouped by source.

    The order is fixed (by document, then by chunk order) so that the corpus
    is a *stable prefix* of every request, which is what makes prompt
    caching possible and the cost comparison fair.
    """
    by_doc: dict[str, list[str]] = {}
    order: list[str] = []
    for cid in fw.index.chunk_ids:
        doc_id = fw.index.chunk_ids and cid.split("::")[0]
        if doc_id not in by_doc:
            by_doc[doc_id] = []
            order.append(doc_id)
        by_doc[doc_id].append(cid)

    parts = []
    for doc_id in order:
        body = "\n\n".join(fw.index.chunk_text[c] for c in by_doc[doc_id])
        parts.append(f"### {doc_id.replace('-', ' ')}\n\n{body}")
    return "\n\n".join(parts), order


def _tokenizer():
    """The corpus was embedded with this tokenizer, so it is the one whose
    counts are exactly right for this corpus."""
    from transformers import AutoTokenizer

    from src.config import CONFIG

    return AutoTokenizer.from_pretrained(CONFIG.embedding.model)


def count_tokens(tok, text: str) -> int:
    return len(tok(text, add_special_tokens=False)["input_ids"])


# --------------------------------------------------------------------------
# The retrieval-side proxy
# --------------------------------------------------------------------------
def retrieval_proxy(fw, bench, answerable) -> dict:
    """Can the reader still find the evidence when the candidate set is the
    whole corpus?

    The pipeline's reader is the cross-encoder: it scores (query, chunk) and
    the top of that list is the context. Here the candidate set is every
    chunk in the corpus rather than the fused shortlist, which is exactly
    the locating problem a long-context reader faces.
    """
    from src.models import rerank

    all_ids = list(fw.index.chunk_ids)
    texts = [fw.index.chunk_text[c] for c in all_ids]

    _sampled = bool(PROXY_MAX_QUERIES and PROXY_MAX_QUERIES < len(answerable))
    if _sampled:
        rng = np.random.default_rng(SEED)
        idx = sorted(rng.choice(len(answerable), size=PROXY_MAX_QUERIES,
                                replace=False).tolist())
        answerable = [answerable[i] for i in idx]
        print(f"[exp7]   proxy sampled {len(answerable)} of the answerable "
              f"queries (seed {SEED})", flush=True)

    ranks: list[int] = []
    per_query: list[dict] = []
    t0 = time.time()
    for n, q in enumerate(answerable, 1):
        gold = set(q["gold"])
        pairs = list(zip(all_ids, texts))
        scored: list[tuple[str, float]] = []
        for i in range(0, len(pairs), SCORE_SLICE):
            scored.extend(rerank(q["query"], pairs[i : i + SCORE_SLICE]))
        scored.sort(key=lambda t: -t[1])
        order = [cid for cid, _ in scored]
        gold_ranks = [i for i, cid in enumerate(order, 1) if cid in gold]
        best = min(gold_ranks) if gold_ranks else None
        if best is not None:
            ranks.append(best)
        per_query.append({"query": q["query"], "best_gold_rank": best})
        if n % 20 == 0:
            print(f"[exp7]   proxy {n}/{len(answerable)} "
                  f"({time.time() - t0:.0f}s)", flush=True)

    ranks_arr = np.array(ranks, dtype=float) if ranks else np.array([])
    top10 = float((ranks_arr <= 10).mean()) if len(ranks_arr) else float("nan")
    # Wilson interval: the sample may be bounded, and the interval is what
    # says how much the sample size costs in precision.
    n = len(ranks_arr)
    z = 1.96
    if n:
        centre = (top10 + z * z / (2 * n)) / (1 + z * z / n)
        half = (z / (1 + z * z / n)
                 * ((top10 * (1 - top10) / n + z * z / (4 * n * n)) ** 0.5))
    else:
        centre = half = float("nan")
    out = {
        "n_queries": len(answerable),
        "sampled": _sampled,
        "top10_wilson_low": float(centre - half) if n else float("nan"),
        "top10_wilson_high": float(centre + half) if n else float("nan"),
        "n_with_gold_found": len(ranks),
        "candidate_set_size": len(all_ids),
        "gold_in_top10": float((ranks_arr <= 10).mean()) if len(ranks_arr) else float("nan"),
        "gold_in_top20": float((ranks_arr <= 20).mean()) if len(ranks_arr) else float("nan"),
        "gold_in_top50": float((ranks_arr <= 50).mean()) if len(ranks_arr) else float("nan"),
        "median_gold_rank": float(np.median(ranks_arr)) if len(ranks_arr) else float("nan"),
        "mean_gold_rank": float(ranks_arr.mean()) if len(ranks_arr) else float("nan"),
        "seconds": round(time.time() - t0, 1),
    }
    return out


# --------------------------------------------------------------------------
# The generative arm
# --------------------------------------------------------------------------
def _llm_config() -> dict | None:
    key = os.environ.get("MTP_LLM_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return None
    return {
        "api_key": key,
        "base_url": os.environ.get("MTP_LLM_BASE_URL",
                                   "https://api.anthropic.com").rstrip("/"),
        "model": os.environ.get("MTP_LLM_MODEL", "claude-haiku-4-5-20251001"),
        "max_usd": float(os.environ.get("MTP_LLM_MAX_USD", "5.0")),
        "max_queries": int(os.environ.get("MTP_LLM_MAX_QUERIES", "0") or 0),
    }


def _call_llm(cfg: dict, system: str, corpus: str, question: str) -> dict:
    """One request, with the corpus as a cached prefix.

    The corpus is identical across every query, so it is sent with
    `cache_control`, and the per-query cost is the cached read rate rather
    than the full price. That is also how such a system would be deployed.
    """
    body = {
        "model": cfg["model"],
        "max_tokens": 1024,
        "temperature": 0,
        "system": [
            {
                "type": "text",
                "text": system,
                "cache_control": {"type": "ephemeral"},
            },
            {
                "type": "text",
                "text": corpus,
                "cache_control": {"type": "ephemeral"},
            },
        ],
        "messages": [{"role": "user", "content": question}],
    }
    req = urllib.request.Request(
        cfg["base_url"] + "/v1/messages",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "x-api-key": cfg["api_key"],
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read().decode("utf-8"))


def generative_arm(fw, bench, answerable, corpus, cfg) -> dict:
    """Ask the reader for an answer with the whole corpus in context."""
    system = (
        "You answer questions about industrial engineering documentation. "
        "Answer from the documents given. If the documents do not contain the "
        "answer, say that the documents do not contain it. Be brief."
    )
    per_query: list[dict] = []
    n_correct = n_refused = 0
    t0 = time.time()
    for n, q in enumerate(answerable, 1):
        question = q["query"]
        try:
            resp = _call_llm(cfg, system, corpus, question)
        except urllib.error.HTTPError as e:  # pragma: no cover
            body = e.read().decode("utf-8", "replace")[:300]
            print(f"[exp7]   HTTP {e.code} on query {n}: {body}", flush=True)
            break
        except Exception as e:  # pragma: no cover  # noqa: BLE001
            print(f"[exp7]   request failed on query {n}: {e}", flush=True)
            break
        text = "".join(b.get("text", "") for b in resp.get("content", [])
                       if b.get("type") == "text")
        usage = resp.get("usage", {})
        refused = "not contain" in text.lower() or "does not" in text.lower()
        # The answer is correct when it entails the gold chunk's answer.
        gold_answer = q.get("answer")
        correct = False
        if gold_answer and not refused:
            gold_answer = str(gold_answer)
            key_terms = [t for t in gold_answer.split() if len(t) > 4][:6]
            if key_terms:
                hit = sum(1 for t in key_terms if t.lower() in text.lower())
                correct = hit >= max(1, len(key_terms) // 2)
        n_correct += int(correct)
        n_refused += int(refused)
        per_query.append({
            "query": question,
            "answer": text[:2000],
            "correct": correct,
            "refused": refused,
            "usage": usage,
        })
        if n % 10 == 0:
            print(f"[exp7]   generative {n}/{len(answerable)} "
                  f"({time.time() - t0:.0f}s)", flush=True)
        if cfg["max_queries"] and n >= cfg["max_queries"]:
            break

    n = max(len(per_query), 1)
    return {
        "model": cfg["model"],
        "n_queries": len(per_query),
        "answer_accuracy": n_correct / n,
        "refusal_rate": n_refused / n,
        "total_input_tokens": sum(q["usage"].get("input_tokens", 0)
                                  for q in per_query),
        "total_output_tokens": sum(q["usage"].get("output_tokens", 0)
                                  for q in per_query),
        "cache_read_tokens": sum(
            q["usage"].get("cache_read_input_tokens", 0) for q in per_query),
        "cache_creation_tokens": sum(
            q["usage"].get("cache_creation_input_tokens", 0) for q in per_query),
        "seconds": round(time.time() - t0, 1),
        "per_query": per_query,
    }


# --------------------------------------------------------------------------
def main() -> int:
    print("[exp7] loading index and benchmark ...", flush=True)
    index = load_index()
    bench = load_benchmark()
    fw = Framework(index)

    answerable = [q for q in bench["queries"] if q["gold"]]
    unanswerable = [q for q in bench["queries"] if not q["gold"]]

    corpus, doc_order = build_long_context(fw)
    tok = _tokenizer()
    corpus_tokens = count_tokens(tok, corpus)
    print(f"[exp7] corpus: {len(index.chunk_ids)} chunks, {len(doc_order)} documents, "
          f"{corpus_tokens:,} tokens", flush=True)

    # ---- the cost half: the RAG arm's context, measured the same way ----
    rag_context_tokens: list[int] = []
    rag_context_chunks: list[int] = []
    rag_answerable_tokens: list[int] = []
    rag_answerable_chunks: list[int] = []
    question_tokens: list[int] = []
    for q in bench["queries"]:
        cat = q["category"] if q["gold"] else None
        trace = fw.retrieve(q["query"], category=cat)
        ctx = "\n\n".join(fw.index.chunk_text[c] for c in trace.accepted)
        n_ctx = count_tokens(tok, ctx)
        n_q = count_tokens(tok, q["query"])
        rag_context_tokens.append(n_ctx)
        rag_context_chunks.append(len(trace.accepted))
        question_tokens.append(n_q)
        if q["gold"]:
            rag_answerable_tokens.append(n_ctx)
            rag_answerable_chunks.append(len(trace.accepted))

    # The fair comparison is over the answerable queries: those are the ones
    # the long-context arm would answer rather than refuse, so it is the only
    # case where the two arms are doing the same work.
    mean_rag = float(np.mean(rag_answerable_tokens)) if rag_answerable_tokens else 0.0
    mean_q = float(np.mean(question_tokens)) if question_tokens else 0.0
    ratio = (corpus_tokens + mean_q) / (mean_rag + mean_q) if (mean_rag + mean_q) else float("nan")
    ratio_all = ((corpus_tokens + mean_q) /
                 (float(np.mean(rag_context_tokens)) + mean_q)
                 if rag_context_tokens else float("nan"))

    fits = {name: corpus_tokens <= window
            for name, window in CONTEXT_WINDOWS.items()}

    cost = {
        "corpus_chunks": len(index.chunk_ids),
        "corpus_documents": len(doc_order),
        "corpus_tokens": corpus_tokens,
        "rag_context_tokens_mean": round(mean_rag, 1),
        "rag_context_tokens_mean_all_queries": round(
            float(np.mean(rag_context_tokens)), 1) if rag_context_tokens else float("nan"),
        "rag_context_tokens_median": float(np.median(rag_answerable_tokens))
        if rag_answerable_tokens else float("nan"),
        "rag_context_chunks_mean": round(
            float(np.mean(rag_answerable_chunks)), 2) if rag_answerable_chunks else float("nan"),
        "question_tokens_mean": round(mean_q, 1),
        "token_ratio_long_over_rag": round(ratio, 1),
        "token_ratio_long_over_rag_all_queries": round(ratio_all, 1),
        "corpus_fraction_retrieved": round(
            (float(np.mean(rag_context_chunks)) / max(len(index.chunk_ids), 1)), 5),
        "context_window_fits": fits,
        "tokenizer": "the corpus's own embedding tokenizer (BGE-M3 / XLM-R)",
    }

    print(f"[exp7] long-context prompt: {corpus_tokens:,} tokens; "
          f"RAG context: {mean_rag:,.0f} tokens; ratio {ratio:.0f}x", flush=True)

    # The cost half is written out before the proxy starts, because the
    # proxy is the slow tail and a long experiment should not hold its own
    # early results hostage. A reader that picks up the file now sees a
    # complete cost measurement and a proxy still running.
    _partial = {
        "seed": SEED,
        "summary": {
            "corpus": cost,
            "retrieval_proxy": {"status": "running"},
            "generative": {"ran": False,
                            "reason": "not reached yet; the cost half is "
                                      "complete and the proxy was still running"},
            "n_answerable": len(answerable),
            "n_unanswerable": len(unanswerable),
        },
    }
    write_result("exp7_long_context", _partial)
    print("[exp7] wrote the cost half; the proxy follows", flush=True)

    # ---- the retrieval-side proxy ---------------------------------------
    print("[exp7] retrieval-side proxy: scoring the whole corpus per query ...",
          flush=True)
    proxy = retrieval_proxy(fw, bench, answerable)
    print(f"[exp7]   gold in top 10: {proxy['gold_in_top10']:.3f}; "
          f"median rank {proxy['median_gold_rank']:.0f} of "
          f"{proxy['candidate_set_size']}", flush=True)

    # ---- the quality half, if a generator is reachable -------------------
    cfg = _llm_config()
    generative: dict
    if cfg is None:
        generative = {
            "ran": False,
            "reason": "no API credential reachable from this machine: "
                      "ANTHROPIC_API_KEY and MTP_LLM_API_KEY are unset, the "
                      "Claude Code CLI is not logged in, and no local "
                      "generative model is installed. The cost half and the "
                      "retrieval-side proxy are reported; the quality half is "
                      "not run and is not estimated.",
        }
        print("[exp7] no generator credential reachable; the quality half is "
              "not run.", flush=True)
    else:
        print(f"[exp7] running the generative arm with {cfg['model']} ...",
              flush=True)
        generative = {"ran": True}
        generative.update(generative_arm(fw, bench, answerable, corpus, cfg))

    summary = {
        "corpus": cost,
        "retrieval_proxy": proxy,
        "generative": generative,
        "n_answerable": len(answerable),
        "n_unanswerable": len(unanswerable),
    }

    payload = {"seed": SEED, "summary": summary}
    payload["retrieval_placement"] = CONFIG.modality.position
    write_result("exp7_long_context", payload)
    _write_markdown(summary)
    return 0


def _write_markdown(s: dict) -> None:
    c = s["corpus"]
    p = s["retrieval_proxy"]
    g = s["generative"]
    fits = c["context_window_fits"]
    fit_rows = [[name, "yes" if ok else "**no**"]
                for name, ok in fits.items()]
    fit_table = markdown_table(["Context window", "Holds the whole corpus?"],
                               fit_rows)

    lines = [
        "# Experiment 7 -- The long-context baseline arm",
        "",
        "The threat: the corpus may fit in a modern context window, in which "
        "case a reader given everything could answer the question directly and "
        "the retrieval machinery would be unnecessary.",
        "",
        "## The cost half",
        "",
        f"- Long-context arm, one query: **{c['corpus_tokens']:,} tokens** "
        f"(the whole corpus, {c['corpus_chunks']:,} chunks across "
        f"{c['corpus_documents']} documents) plus the question "
        f"({c['question_tokens_mean']:.0f} tokens).",
        f"- RAG arm, one answerable query: **{c['rag_context_tokens_mean']:,.0f} "
        f"tokens** ({c['rag_context_chunks_mean']:.1f} chunks, retrieved and "
        f"accepted) plus the question.",
        f"- **Ratio: {c['token_ratio_long_over_rag']:.0f}x.**",
        f"- The RAG arm retrieves "
        f"{c['corpus_fraction_retrieved'] * 100:.2f}% of the corpus.",
        "",
        fit_table,
        "",
        "## The retrieval-side proxy",
        "",
        "With the candidate set widened from the fused shortlist to every chunk "
        "in the corpus -- the locating problem a long-context reader faces -- "
        "does the same scorer still rank the gold chunk inside the final "
        "context?",
        "",
        f"- Gold chunk in the top 10 of {p['candidate_set_size']:,}: "
        f"**{p['gold_in_top10']:.3f}**",
        f"- Top 20: {p['gold_in_top20']:.3f}; top 50: {p['gold_in_top50']:.3f}",
        f"- Median rank of the gold chunk: {p['median_gold_rank']:.0f} "
        f"(of {p['candidate_set_size']:,})",
        "",
    ]
    if g.get("ran"):
        lines += [
            "## The quality half",
            "",
            f"Model: `{g['model']}`. Accuracy "
            f"{g['answer_accuracy']:.3f}, refusal rate "
            f"{g['refusal_rate']:.3f}, over {g['n_queries']} answerable queries. "
            f"Input tokens {g['total_input_tokens']:,} "
            f"(cache reads {g['cache_read_tokens']:,}), output tokens "
            f"{g['total_output_tokens']:,}.",
            "",
        ]
    else:
        lines += [
            "## The quality half",
            "",
            "**Not run.** " + g.get("reason", ""),
            "",
        ]
    (RESULTS_DIR / "exp7_long_context.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")
    print(f"[exp7] wrote {RESULTS_DIR / 'exp7_long_context.md'}")


if __name__ == "__main__":
    sys.exit(main())
