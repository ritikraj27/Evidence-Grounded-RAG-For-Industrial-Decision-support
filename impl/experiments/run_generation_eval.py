#!/usr/bin/env python3
"""Experiment 8 -- the generator-side comparison: does the framework reduce hallucination?

Everything measured so far in this project is retrieval-side: recall, ordering,
whether the gate refuses. The framework's central claim is about *answers* --
that it answers fewer questions it should not -- and that claim has never been
tested with a generator in the loop. This experiment puts one generator behind
five arms and scores every claim it produces:

  rag_nogate        the top-10 reranked chunks, no confidence gate
  rag@fitted        the framework at the operating point chosen on this benchmark
  rag@random        a control that refuses as many questions as rag@fitted did,
                    but picks them at random and ignores the confidence score
  rag@transferred   the framework at the threshold transferred unchanged from the
                    cross-category half -- the held-out operating point
  long_context      the whole corpus in the prompt

The arms share the generator, the prompt wording, the question set and the
scorer, so a difference between them is attributable to the context and the
gate, and to nothing else. `rag_nogate` is what isolates the gate: it is the
same retrieval with the gate removed, so the difference between the two is the
gate's contribution and not the retrieval's.

The prompt wording is a second axis, because one prompt cannot show the gate
what it does. Under the `cautious` instruction the generator refuses most
unanswerable questions on its own, so the gate's refusals are redundant and
the two arms cannot be told apart -- a real property of the deployed system,
and the reason the gate's contribution has to be measured a second way. Under
the `answering` instruction, which differs from `cautious` by one sentence,
the generator must answer from whatever context it is given, and the gate is
the only thing standing between it and a fabricated answer. Both conditions
are run and both are reported: the first says what the system does, the
second says what the gate buys.

Scoring uses the entailment machinery the rest of the suite uses
(src/models.py): an answer is split into atomic claims, each claim is checked
for entailment by the corpus chunks it could have come from, and the headline
is the fraction of claims that no chunk in the corpus supports.

Two rates are reported on the unanswerable questions, because they answer
different questions:

  answer_rate        how often the arm answers at all when the answer does not
                     exist -- the *opportunity* for hallucination
  claim_hallucination_rate
                     of the claims it did produce, how many are supported by
                     nothing in the corpus -- fabrication

A system that refuses everything scores zero on the second and is useless, so
the first is the headline and the second is only ever read next to it.

The corpus, the benchmark and the label standard are untouched. This
experiment only puts a generator behind them.
"""
from __future__ import annotations

import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.request
from math import comb
from pathlib import Path

import numpy as np

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("OMP_NUM_THREADS", "4")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import load_benchmark, load_index, write_result  # noqa: E402
from run_long_context import _tokenizer, build_long_context, count_tokens  # noqa: E402
from src.claims import split_into_claims  # noqa: E402
from src.config import CONFIG, RESULTS_DIR  # noqa: E402
from src.models import embed_texts, nli_probs  # noqa: E402
from src.pipeline import Framework  # noqa: E402

#: How many times a single request is retried before the arm is
#: abandoned. Every failure seen so far was transient -- a TLS record
#: error, a DNS resolution failure, and a provider overload (HTTP 529) --
#: and each one discarded four arms that had already answered every
#: question. The delay grows with the attempt, so a provider that is
#: momentarily overloaded gets room to recover.
_retries = int(os.environ.get("MTP_LLM_RETRIES", "6"))
_retry_delay = float(os.environ.get("MTP_LLM_RETRY_DELAY", "10"))

#: After this many attempts on one request, the output budget is raised
#: rather than the request being abandoned. A reasoning model can spend the
#: whole budget thinking and return no text; that is a property of the
#: model, not of the question, and it must not be counted as either an
#: answer or a refusal. Zero disables the escalation, which is the right
#: setting for a model that does not reason.
_escalate_after = int(os.environ.get("MTP_LLM_ESCALATE_AFTER", "0"))
_max_token_ceiling = int(os.environ.get("MTP_LLM_MAX_TOKENS_CEILING", "8192"))

SEED = 20261118

#: The generator instruction, as an axis of the experiment.
#:
#: The comparison cannot see the gate if the generator declines on its own.
#: Under the cautious instruction below, MiniMax-M3 refused 140 of the 144
#: unanswerable questions with no gate in front of it, so the gate's 115
#: refusals were redundant with what the prompt had already produced and the
#: two arms could not be told apart. That is a real property of the deployed
#: system and it is reported -- but it measures the *system*, not the *gate*.
#:
#: The second instruction is the same sentence with the permission to decline
#: removed. Everything else -- the model, the questions, the retrieval, the
#: scorer, the requested temperature -- is identical, so the difference
#: between the arms within this condition is the gate's marginal
#: contribution, measured against a generator that answers rather than one
#: that refuses.
#:
#: The condition is realistic rather than adversarial. Industrial decision
#: support needs an answer: a system that declines every question is not
#: deployable, and the operator is exactly the person a confident number
#: with nothing behind it harms.
CONDITIONS = {
    "cautious": (
        "You answer questions about industrial engineering documentation. "
        "Answer only from the documents given. If the documents do not contain "
        "the answer, say that the documents do not contain it. Be brief."
    ),
    "answering": (
        "You answer questions about industrial engineering documentation. "
        "Answer only from the documents given. Always give your best answer "
        "from the documents: do not decline, and do not say that the "
        "information is missing. Be brief."
    ),
}

#: A claim that says the evidence is absent is a refusal, not an answer. The
#: test is applied per claim rather than to the whole answer, so an answer
#: that states a refusal *and* asserts something is scored on the assertion.
_REFUSAL_RE = re.compile(
    r"do(?:es)? not (?:contain|provide|specify|mention|state|include|answer|appear|give|list)"
    r"|(?:cannot|can't|could not|unable to|will not) (?:be )?"
    r"(?:answer|determine|find|provide|answer)"
    r"|no (?:information|mention|answer|value|indication|reference|specific|details)"
    r"|not (?:specified|mentioned|stated|provided|available|found|present|given|listed"
    r"|defined|documented|covered|answered|included)"
    r"|there is no\b"
    r"|insufficient (?:information|evidence|context|data)"
    r"|does not (?:exist|apply|appear)"
    r"|not in the (?:documents?|corpus|text|provided)"
    r"|(?:nothing|none) (?:in|of) the (?:documents?|corpus|text)",
    re.IGNORECASE,
)

#: A proposition is supported when some chunk entails it with at least this
#: much probability. 0.5 is the same threshold src/claims.py uses to decide
#: whether a claim carries a citation.
SUPPORT_THRESHOLD = 0.5

#: Words that carry no evidentiary content, excluded from the bare-value
#: test so that a chunk which states a value without the article ("lead time
#: 14 days") still counts as containing it ("the lead time is 14 days").
_STOPWORDS = frozenset("""
a an and any are as at be been both but by can could did do does each for
from further had has have he her his how i if in into is it its just may
me might more most much must no nor not of off on once one only or other
our out over own same she should so some such than that the their them then
there these they this those through to too under until up very was we were
what when where which while who whom why will with would you your
""".split())


def _content_tokens(text: str) -> list[str]:
    """The content words and numbers of a piece of text."""
    return [t for t in re.findall(r"[a-z0-9][a-z0-9.%/-]*", text.lower())
            if t not in _STOPWORDS
            and (len(t) > 2 or any(c.isdigit() for c in t))]


#: The corpus, lowercased once. The literal test scans the evidence, and the
#: long-context arm's evidence is every chunk, so lowercasing 735 chunks once
#: per question would dominate the run.
_LOWER_CACHE: dict[int, dict[str, str]] = {}


def _lower_chunks(index) -> dict[str, str]:
    key = id(index)
    cached = _LOWER_CACHE.get(key)
    if cached is None:
        cached = {cid: text.lower() for cid, text in index.chunk_text.items()}
        _LOWER_CACHE[key] = cached
    return cached


def _stated_in_evidence(index, text: str, evidence_ids: list[str]) -> bool:
    """Does the evidence the arm was shown state this, word for word?

    A claim is supported if the evidence entails it, or if the evidence
    states it literally. The second test is not a fallback for a weak
    instrument -- it is the only one that works on the two kinds of answer
    this benchmark produces. The NLI model will not entail a bare "69%" from
    a chunk that says 69%, because an entailment hypothesis is supposed to
    be a proposition and a bare number is not one; and it will not entail a
    definitional fragment like "use of automated production lines in the
    beverage industry" either. Meanwhile the entailment model *will* endorse
    a bare number against any chunk that happens to contain a number, so
    entailment alone cannot tell a fabricated value from a real one.

    The literal test requires every content word and every number of the
    claim to appear in the *same* chunk of the evidence, which is what "the
    evidence states this" means. A fabricated value fails it, because the
    number is not there to be found.
    """
    tokens = _content_tokens(text)
    if not tokens:
        return False
    # Word boundaries, not plain substring: "3" must not be found inside
    # "3.05" or "37", and "69%" must not be found inside "169%". A period
    # only blocks a match when a digit follows it, so a claim that ends a
    # sentence ("... to be done.") is still found.
    pats = [re.compile(r"(?<![\w])" + re.escape(t) + r"(?![\w])(?!\.\d)")
            for t in tokens]
    lower = _lower_chunks(index)
    for cid in evidence_ids:
        low = lower.get(cid, "")
        if low and all(p.search(low) for p in pats):
            return True
    return False

#: How many corpus chunks are checked per claim. Two shortlists are unioned:
#: the nearest neighbours of the claim in the corpus embedding, which catches
#: paraphrase, and the highest-scoring chunks under BM25, which catches
#: verbatim overlap that the embedding can miss. The gold chunk is always
#: added. Checking every chunk against every claim is not affordable -- the
#: NLI model runs at ~16 pairs/s on this machine, so the exhaustive version of
#: this experiment would take hours -- and a claim that neither shortlist
#: surfaces is one no corpus chunk states in those words anyway.
CANDIDATES_PER_CLAIM = 8

#: The most chunks any one claim is put to the NLI model with. A retrieval
#: arm's evidence is about ten chunks and goes through in full; the
#: long-context arm's evidence is the whole corpus and is shortlisted down
#: to this many before the entailment check.
NLI_MAX_CHUNKS = 32


#: The generator's sampling behaviour, recorded in the payload so that no
#: deliverable can imply the answers were greedy or reproducible. MiniMax
#: documents `temperature` as ignored (its models always sample at 1);
#: Anthropic honours it. Either way the harness asks for 0 and the payload
#: records what the provider actually did.
SAMPLING_NOTE = os.environ.get(
    "MTP_LLM_SAMPLING_NOTE",
    "provider-determined; the temperature parameter is advisory only",
)


def _prices() -> dict:
    """The provider's rates, per million tokens.

    These are configuration, not measurement. The tokens are what was sent
    and what the provider billed; the price table is the provider's at the
    time of the run, and it is recorded in the payload so that the
    arithmetic can be checked rather than taken on trust. The defaults are
    MiniMax-M3's published rates, and every one of them can be overridden,
    because a price table that is baked into the code silently goes stale.
    """
    inp = float(os.environ.get("MTP_LLM_PRICE_INPUT_PER_M", "0.30"))
    return {
        "input_per_m": inp,
        "output_per_m": float(os.environ.get("MTP_LLM_PRICE_OUTPUT_PER_M", "0.30")),
        "cache_read_per_m": float(
            os.environ.get("MTP_LLM_PRICE_CACHE_READ_PER_M", "0.06")),
        "cache_write_per_m": float(
            os.environ.get("MTP_LLM_PRICE_CACHE_WRITE_PER_M",
                           str(round(inp * 1.25, 6)))),
    }


def _llm_config() -> dict | None:
    key = os.environ.get("MTP_LLM_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return None
    return {
        "api_key": key,
        "base_url": os.environ.get("MTP_LLM_BASE_URL",
                                   "https://api.anthropic.com").rstrip("/"),
        "model": os.environ.get("MTP_LLM_MODEL", "claude-haiku-4-5-20251001"),
        "context_limit": int(os.environ.get("MTP_LLM_CONTEXT_LIMIT", "200000")),
        "max_input_tokens": int(os.environ.get("MTP_LLM_MAX_INPUT_TOKENS",
                                               "20000000")),
        "max_queries": int(os.environ.get("MTP_LLM_MAX_QUERIES", "0") or 0),
        # 0 means every unanswerable question in the benchmark is asked.
        "unanswerable": int(os.environ.get("MTP_GEN_UNANSWERABLE", "0") or 0),
        # Prompt caching is a cost optimisation, not part of the measurement.
        # MiniMax's Anthropic-compatible route does not advertise
        # `cache_control`, and an unsupported marker is a 400 rather than a
        # silent no-op, so the marker is opt-in and the payload records it.
        "cache_control": os.environ.get("MTP_LLM_CACHE_CONTROL", "0") == "1",
        # The output budget. It is a configuration, not a measurement, and it
        # has to be recorded in the payload: a reasoning model can spend the
        # whole budget thinking and return no text at all, and a comparison
        # between two generators is only like-for-like when the budget is the
        # same.
        "max_tokens": int(os.environ.get("MTP_LLM_MAX_TOKENS", "1024")),
        "seed": SEED,
    }


class EmptyCompletion(RuntimeError):
    """The model returned no text -- it spent the whole budget thinking.

    This is neither a refusal nor an answer, and recording it as either
    would corrupt the arm's answer rate, so it is its own failure and the
    request is retried rather than counted.
    """


def _call(cfg: dict, context: str, question: str) -> dict:
    """One generation request.

    The corpus is the identical prefix across every query in the long-context
    arm, so it is sent as a cached block when the provider supports prompt
    caching -- that is what such a system would actually pay. The retrieval
    arms send their short context without it: there is nothing to cache across
    queries, and a cache breakpoint on a short block is below the minimum
    cacheable length.

    The corpus travels in the user message rather than in `system`, because
    MiniMax documents `system` as a plain system prompt and every one of its
    examples sends a string; the block-list form that the Anthropic API also
    accepts is not relied on. The order -- corpus first, question last -- is
    identical across all five arms, which is what the comparison needs.
    """
    content: list[dict] = []
    if context:
        block: dict = {"type": "text", "text": context}
        if cfg.get("cache_control"):
            block["cache_control"] = {"type": "ephemeral"}
        content.append(block)
    content.append({"type": "text", "text": question})
    body = {
        "model": cfg["model"],
        "max_tokens": cfg.get("max_tokens", 1024),
        "temperature": 0,
        "system": cfg["system"],
        "messages": [{"role": "user", "content": content}],
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
    # The socket timeout is a per-request bound, and the harness retries.
    # At 600 s a hung request cost an hour before the run gave up; a
    # request that has not answered in three minutes is not going to.
    with urllib.request.urlopen(req, timeout=180) as r:
        resp = json.loads(r.read().decode("utf-8"))
    if not _text_of(resp).strip():
        # A model that spends the whole budget on reasoning blocks returns
        # no text at all. Recording that as "did not answer" would silently
        # understate the arm's answer rate, so it fails the run instead.
        raise EmptyCompletion(
            f"empty completion (stop_reason={resp.get('stop_reason')!r}, "
            f"content types={[b.get('type') for b in resp.get('content', [])]})"
        )
    return resp


def _text_of(resp: dict) -> str:
    return "".join(b.get("text", "") for b in resp.get("content", [])
                   if b.get("type") == "text")


def _usage_of(resp: dict) -> dict:
    """The provider's own token accounting.

    A provider that serves a cached prefix reports the cached part separately
    from the input it actually processed: MiniMax answers a cached request
    with `input_tokens: 1` and `cache_read_input_tokens: 28181`. The
    uncached figure alone is therefore not the size of the prompt, and the
    total is kept alongside it so that the cost of the long-context arm is
    reported as what was actually billed.
    """
    u = resp.get("usage", {}) or {}
    inp = int(u.get("input_tokens", 0))
    read = int(u.get("cache_read_input_tokens", 0))
    create = int(u.get("cache_creation_input_tokens", 0))
    return {
        "input_tokens": inp,
        "output_tokens": int(u.get("output_tokens", 0)),
        "cache_read_tokens": read,
        "cache_creation_tokens": create,
        "total_input_tokens": inp + read + create,
    }


# --------------------------------------------------------------------------
# Scoring
# --------------------------------------------------------------------------
def _claim_support(index, claims: list[str],
                   evidence_ids: list[str], bare: bool = False) -> list[dict]:
    """For each claim, the strongest support the arm's own evidence gives it.

    The evidence is what the arm was shown: the retrieved chunks for a
    retrieval arm, the whole corpus for the long-context arm. Scoring a
    claim against the evidence the generator actually had is the standard
    definition of faithfulness, and it keeps the five arms comparable -- the
    scoring rule is the same for each, and the evidence differs exactly as
    the arms differ. Nothing outside the evidence can support a claim: the
    gold chunk is not force-added, because a chunk the arm never saw cannot
    be the reason it did not make the thing up.

    A claim is supported when a candidate chunk entails it -- the same NLI
    model and the same 0.5 threshold src/claims.py uses to decide whether a
    claim carries a citation -- or when the evidence states it literally.

    A bare value is scored by the literal test alone. The entailment model
    treats a bare number as an easy entailment: it endorsed a fabricated
    "37.412%" against a chunk that never mentions the quantity, so asking it
    about a value that is not a proposition cannot distinguish the real from
    the invented. The literal test is exact there -- the value is either in
    the evidence or it is not.
    """
    if not claims:
        return []
    vecs = embed_texts(
        claims,
        model_name=CONFIG.embedding.model,
        batch_size=16,
        dim=CONFIG.embedding.dim,
    )
    ev_pos = {cid: j for j, cid in enumerate(index.chunk_ids)}
    ev_rows = np.array([ev_pos[c] for c in evidence_ids if c in ev_pos],
                        dtype=int)
    sims = vecs @ index.embeddings.T
    out = []
    for i, claim in enumerate(claims):
        # The candidates the NLI model sees: the evidence itself when it is
        # small, and the nearest evidence chunks when it is not.
        if len(evidence_ids) <= NLI_MAX_CHUNKS:
            ids = list(evidence_ids)
        else:
            ids = []
            if len(ev_rows):
                order = np.argsort(sims[i][ev_rows])[::-1][:CANDIDATES_PER_CLAIM]
                ids.extend(evidence_ids[j] for j in order)
            for doc_id, _ in index.bm25.top_k(claim, CANDIDATES_PER_CLAIM):
                if doc_id in evidence_ids and doc_id not in ids:
                    ids.append(doc_id)
        pairs = [(index.chunk_text[c], claim) for c in ids]
        probs = nli_probs(pairs, CONFIG.claim.nli_model)
        best = max((p["entailment"] for p in probs), default=0.0)
        stated = _stated_in_evidence(index, claim, evidence_ids)
        supported = stated if bare else (best >= SUPPORT_THRESHOLD or stated)
        out.append({
            "claim": claim,
            "bare": bool(bare),
            "support": float(best),
            "stated_in_evidence": bool(stated),
            "supported": bool(supported),
            "candidates": ids,
        })
    return out


def _answer_is_correct(answer_text: str, gold_answer: str) -> tuple[bool, bool]:
    """Two independent correctness tests on an answerable question.

    The NLI test asks whether the generated answer entails the gold answer.
    The key-term test asks whether the gold answer's content words appear in
    the generated answer. They fail differently -- the NLI test is strict
    about paraphrase, the key-term test is strict about exact wording -- so
    reporting both keeps a single brittle test from deciding the result.
    """
    if not gold_answer:
        return False, False
    entail = nli_probs([(answer_text, gold_answer)], CONFIG.claim.nli_model)
    by_nli = bool(entail and entail[0]["entailment"] >= SUPPORT_THRESHOLD)
    # The key terms of the gold answer, filtered the same way the verbatim
    # test filters them: a bare value like "69%" is a content term and has to
    # count, or every short numeric answer would score as incorrect.
    terms = [t for t in re.findall(r"[a-z0-9][a-z0-9.%/-]*",
                                    str(gold_answer).lower())
             if t not in _STOPWORDS
             and (len(t) > 2 or any(c.isdigit() for c in t))][:6]
    by_key = bool(terms) and sum(
        1 for t in terms if t in answer_text.lower()
    ) >= max(1, len(terms) // 2)
    return by_nli, by_key


def _grounded_in_gold(index, answer_text: str, gold_ids: list[str]) -> float:
    """Strongest entailment the *gold* evidence gives the whole answer."""
    ids = [g for g in gold_ids if g in index.chunk_text]
    if not ids or not answer_text:
        return 0.0
    probs = nli_probs([(index.chunk_text[g], answer_text) for g in ids],
                      CONFIG.claim.nli_model)
    return float(max((p["entailment"] for p in probs), default=0.0))


# --------------------------------------------------------------------------
# The arms
# --------------------------------------------------------------------------
def _retrieve(fw, question: str, category: str | None):
    return fw.retrieve(question, category=category)


def _rag_context(index, chunk_ids: list[str]) -> str:
    parts = []
    for cid in chunk_ids:
        doc = cid.split("::")[0].replace("-", " ")
        parts.append(f"### {doc}\n{index.chunk_text[cid]}")
    return "\n\n".join(parts)


def run_arm(arm: str, fw, index, corpus: str, questions: list[dict],
            cfg: dict, budget: dict,
            random_refusals: set[str] | None = None) -> list[dict]:
    """Run one arm over the question set."""
    records = []
    for n, q in enumerate(questions, 1):
        if budget["exhausted"]:
            break
        question = q["query"]
        answerable = q["category"] != "unanswerable"
        category = q["category"] if answerable else None

        # -- decide what the arm is allowed to see, and whether it answers at all
        if arm == "long_context":
            context = corpus
            evidence_ids = list(index.chunk_ids)
        else:
            trace = _retrieve(fw, question, category)
            if arm == "rag_nogate":
                evidence_ids = list(trace.reranked[:10])
                context = _rag_context(index, evidence_ids)
            elif arm == "rag@random":
                # The control arm. It refuses exactly as many questions as
                # the fitted gate refused, but picks them at random and
                # ignores the confidence score entirely. It answers the
                # question the gate-versus-no-gate comparison cannot: how
                # much of the gate's effect comes from refusing at all, and
                # how much from refusing the *right* ones. The random set is
                # drawn from every question, because a gate that does not
                # know which questions are answerable cannot do better.
                if question in (random_refusals or set()):
                    records.append(_refusal_record(arm, q, "random_gate_refused"))
                    continue
                evidence_ids = list(trace.reranked[:10])
                context = _rag_context(index, evidence_ids)
            elif arm in ("rag@fitted", "rag@transferred"):
                if trace.gate_rejected:
                    records.append(_refusal_record(arm, q, "gate_refused"))
                    continue
                evidence_ids = list(trace.accepted)
                context = _rag_context(index, evidence_ids)
            else:
                raise ValueError(f"unknown arm: {arm}")

        if budget["input_tokens"] >= cfg["max_input_tokens"]:
            budget["exhausted"] = True
            break

        # A transient network failure must not cost the whole experiment.
        # Both failures seen so far were transient -- a TLS record error and a
        # DNS resolution failure -- and each one discarded four arms that had
        # already answered every question. The retry is what makes the
        # measurement robust; the strict guard below is what keeps it honest.
        resp = None
        _last_err = None
        for _attempt in range(1, _retries + 1):
            # A reasoning model can spend the whole output budget thinking and
            # return no text. That is neither a refusal nor an answer, so the
            # request is retried with a larger budget rather than counted.
            # The escalation is applied identically in every arm and its
            # count is recorded, so a reader can see how often it fired.
            _cfg = cfg
            if _escalate_after and _attempt > _escalate_after:
                _bumped = min(cfg.get("max_tokens", 1024) * 4,
                              _max_token_ceiling)
                if _bumped != cfg.get("max_tokens", 1024):
                    _cfg = {**cfg, "max_tokens": _bumped}
                    budget["escalated"] = budget.get("escalated", 0) + 1
            try:
                resp = _call(_cfg, context, question)
                break
            except EmptyCompletion as e:
                _last_err = e
                if _attempt < _retries:
                    print(f"[exp8] {arm}: {e} on query {n}, retrying "
                          f"({_attempt}/{_retries})"
                          + (f" with a larger output budget"
                             if _cfg is not cfg else ""), flush=True)
                    time.sleep(_retry_delay * _attempt)
                    continue
                break
            except urllib.error.HTTPError as e:
                _last_err = e
                # 429 is the rate limiter; 5xx are the provider's own
                # transient failures; 529 is the provider saying it is
                # overloaded, which is the same instruction: come back in a
                # moment. None of them is a statement about the request.
                if (e.code in (429, 500, 502, 503, 504, 529)
                        and _attempt < _retries):
                    print(f"[exp8] {arm}: HTTP {e.code} on query {n}, "
                          f"retrying ({_attempt}/{_retries})", flush=True)
                    time.sleep(_retry_delay * _attempt)
                    continue
                break
            except Exception as e:  # noqa: BLE001
                _last_err = e
                if _attempt < _retries:
                    print(f"[exp8] {arm}: {e} on query {n}, retrying "
                          f"({_attempt}/{_retries})", flush=True)
                    time.sleep(_retry_delay * _attempt)
                    continue
                break
        if resp is None:
            e = _last_err
            if isinstance(e, urllib.error.HTTPError):
                body = e.read().decode("utf-8", "replace")
                # The provider's own message, not its raw envelope: this
                # string ends up quoted in the deliverables, so it has to read.
                try:
                    msg = json.loads(body).get("error", {}).get("message") or ""
                except Exception:
                    msg = ""
                if not msg:
                    msg = body[:120]
                print(f"[exp8] {arm}: HTTP {e.code} on query {n}: {msg}", flush=True)
                budget["errors"].append(f"HTTP {e.code} -- {msg}")
                budget["exhausted"] = True
                break
            else:
                print(f"[exp8] {arm}: request failed on query {n}: {e}", flush=True)
                budget["errors"].append(f"{arm}: {e}")
                budget["exhausted"] = True
                break

        usage = _usage_of(resp)
        budget["input_tokens"] += usage["total_input_tokens"]
        answer_text = _text_of(resp)

        claims = split_into_claims(answer_text)
        # An answer too short to decompose -- a bare value like "69%" -- is
        # scored as a single bare claim. Without this it would be recorded as
        # "did not answer" when it did answer, which would understate the
        # answer rate on exactly the questions the benchmark asks most often.
        bare = not claims
        if bare and answer_text.strip():
            claims = [answer_text.strip()]
        scored = _claim_support(index, claims, evidence_ids, bare=bare)
        for c, s in zip(claims, scored):
            s["is_refusal"] = bool(_REFUSAL_RE.search(c))

        substantive = [s for s in scored if not s["is_refusal"]]
        answered = bool(substantive)
        # An answer that declines *and* asserts something -- "the documents do
        # not contain the demand for this SKU, so the EOQ cannot be computed;
        # in general EOQ = sqrt(2DK/h)" -- is counted as an answer, because it
        # is scored on the assertion. The count is recorded because the
        # classification is a judgement call and the reader is entitled to
        # see how many answers it affects. It is deliberately the reading that
        # gives the gate less credit: a mixed answer raises the arm's answer
        # rate, and the answer rate is what the gate is credited on lowering.
        mixed = bool(substantive) and len(substantive) < len(scored)

        rec = {
            "arm": arm,
            "query": question,
            "category": q["category"],
            "answerable": answerable,
            "answered": answered,
            "declined_with_content": mixed,
            "n_claims": len(scored),
            "n_bare_claims": sum(1 for s in scored if s.get("bare")),
            "n_substantive_claims": len(substantive),
            "n_supported": sum(1 for s in substantive if s["supported"]),
            "claims": scored,
            "answer_text": answer_text[:2000],
            "usage": usage,
        }
        if answerable and answered:
            by_nli, by_key = _answer_is_correct(answer_text, q.get("answer"))
            rec["correct_nli"] = by_nli
            rec["correct_keyterm"] = by_key
            rec["grounded_in_gold"] = _grounded_in_gold(
                index, answer_text, q.get("gold") or [])
        records.append(rec)

        if n % 10 == 0:
            print(f"[exp8] {arm}: {n}/{len(questions)} "
                  f"({budget['input_tokens']:,} input tokens so far)", flush=True)
    return records


def _mcnemar_exact(b: int, c: int) -> float:
    """Exact two-sided McNemar: 2*P(X <= min(b,c)), X ~ Binom(b+c, 0.5).

    Two paired binary outcomes, so the discordant pairs are all that
    matters, and the binomial is the exact null. With a few dozen
    discordant pairs the normal approximation to it is exactly the wrong
    thing to reach for.
    """
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) * (0.5 ** n))


def _paired_effects(records: dict[str, list[dict]]) -> dict:
    """The gate's effect, paired question by question.

    The arm that isolates the gate is `rag_nogate`: the same retrieval with
    the gate taken out. The arms are paired by *query*, not by position.

    Position-pairing was correct while every arm was measured on the same
    benchmark in the same order, and it still is when they are. It stops
    being correct when one arm is carried over from an archive and the
    benchmark has been rebuilt in between: the rebuilt benchmark holds the
    same questions in a different order, so the two lists pair against the
    wrong questions. Pairing by query makes that explicit instead -- a
    question held by one arm and not the other is simply not paired, and
    `n_unpaired_queries` says how many there were.

    On the unanswerable questions, "the gate answered where the ungated arm
    did not" is the gate doing its job and "the ungated arm answered where
    the gate did not" is the gate costing coverage. On the answerable
    questions the two directions swap meaning: there, an answer the ungated
    arm did not produce is an answer the gate *lost*.
    """
    out: dict = {}
    baseline = records.get("rag_nogate") or []
    base_by_query = {r["query"]: r for r in baseline}
    for arm, recs in records.items():
        if arm == "rag_nogate":
            continue
        arm_by_query = {r["query"]: r for r in recs}
        shared = [q for q in base_by_query if q in arm_by_query]
        block: dict = {}
        for name in ("unanswerable", "answerable"):
            pairs = [(base_by_query[q], arm_by_query[q]) for q in shared
                     if base_by_query[q]["answerable"] == (name == "answerable")]
            b = sum(1 for x, y in pairs if x["answered"] and not y["answered"])
            c = sum(1 for x, y in pairs if not x["answered"] and y["answered"])
            block[name] = {
                "n_pairs": len(pairs),
                "baseline_answered_arm_refused": b,
                "baseline_refused_arm_answered": c,
                "both_answered": sum(1 for x, y in pairs
                                     if x["answered"] and y["answered"]),
                "neither_answered": sum(1 for x, y in pairs
                                        if not x["answered"] and not y["answered"]),
                "p_value": _mcnemar_exact(b, c),
            }
        block["n_unpaired_queries"] = len(base_by_query) - len(shared)
        out[arm] = block
    return out


def _refusal_record(arm: str, q: dict, reason: str) -> dict:
    return {
        "arm": arm,
        "query": q["query"],
        "category": q["category"],
        "answerable": q["category"] != "unanswerable",
        "answered": False,
        "refused_by": reason,
        "n_claims": 0,
        "n_bare_claims": 0,
        "declined_with_content": False,
        "n_substantive_claims": 0,
        "n_supported": 0,
        "claims": [],
        "answer_text": "",
        "usage": {"input_tokens": 0, "output_tokens": 0,
                  "cache_read_tokens": 0, "cache_creation_tokens": 0,
                  "total_input_tokens": 0},
    }


# --------------------------------------------------------------------------
# Aggregation
# --------------------------------------------------------------------------
def summarise(records: list[dict]) -> dict:
    ans = [r for r in records if r["answerable"]]
    unans = [r for r in records if not r["answerable"]]

    def _claims(rs):
        return [c for r in rs for c in r["claims"] if not c["is_refusal"]]

    def _rate(num, den):
        return num / den if den else 0.0

    out: dict = {"n_records": len(records)}

    for name, rs in (("answerable", ans), ("unanswerable", unans)):
        if not rs:
            continue
        answered = [r for r in rs if r["answered"]]
        cl = _claims(answered)
        n_cl = len(cl)
        n_sup = sum(1 for c in cl if c["supported"])
        # Who did the refusing. The gate refuses before the generator is
        # called at all; the generator refuses in prose; and a third case is
        # a refusal that goes on to assert something anyway, which is
        # counted as an answer and scored on the assertion.
        n_gate = sum(1 for r in rs if r.get("refused_by"))
        n_prose = sum(1 for r in rs
                      if not r.get("refused_by")
                      and r.get("n_claims", 0) > 0
                      and r.get("n_substantive_claims", 0) == 0)
        block = {
            "n": len(rs),
            "n_answered": len(answered),
            "answer_rate": _rate(len(answered), len(rs)),
            "n_refused_by_gate": n_gate,
            "n_refused_in_prose": n_prose,
            "n_declined_with_content": sum(1 for r in rs
                                           if r.get("declined_with_content")),
            "n_claims": n_cl,
            "n_bare_claims": sum(1 for r in rs for c in r["claims"]
                                 if c.get("bare")),
            "mean_claims_per_answer": _rate(n_cl, len(answered)),
            "claim_support_rate": _rate(n_sup, n_cl),
            "claim_hallucination_rate": _rate(n_cl - n_sup, n_cl),
        }
        if name == "answerable":
            block["accuracy_nli"] = _rate(
                sum(1 for r in answered if r.get("correct_nli")), len(answered))
            block["accuracy_keyterm"] = _rate(
                sum(1 for r in answered if r.get("correct_keyterm")), len(answered))
            block["grounded_in_gold_rate"] = _rate(
                sum(1 for r in answered if (r.get("grounded_in_gold") or 0) >= SUPPORT_THRESHOLD),
                len(answered))
            block["mean_grounded_in_gold"] = _rate(
                sum(r.get("grounded_in_gold") or 0.0 for r in answered),
                len(answered))
        out[name] = block

    all_cl = _claims(records)
    n_all = len(all_cl)
    n_all_sup = sum(1 for c in all_cl if c["supported"])
    out["overall"] = {
        "n_claims": n_all,
        "claim_support_rate": _rate(n_all_sup, n_all),
        "hallucination_rate": _rate(n_all - n_all_sup, n_all),
    }
    out["tokens"] = {
        "input": sum(r["usage"]["input_tokens"] for r in records),
        "output": sum(r["usage"]["output_tokens"] for r in records),
        "cache_read": sum(r["usage"]["cache_read_tokens"] for r in records),
        "cache_creation": sum(r["usage"]["cache_creation_tokens"] for r in records),
        "total_input": sum(r["usage"].get("total_input_tokens", 0)
                           for r in records),
    }
    # What the tokens cost. The input tokens dominate, and for the
    # long-context arm most of them are cache *reads*, which the provider
    # bills at a fraction of the base rate -- so the token ratio and the
    # cost ratio are different numbers, and only the second one is a cost.
    prices = _prices()
    m = 1_000_000.0
    tk = out["tokens"]
    uncached = tk["input"] * prices["input_per_m"] / m
    read = tk["cache_read"] * prices["cache_read_per_m"] / m
    write = tk["cache_creation"] * prices["cache_write_per_m"] / m
    gen = tk["output"] * prices["output_per_m"] / m
    out["cost"] = {
        "input_usd": uncached + read + write,
        "uncached_input_usd": uncached,
        "cache_read_usd": read,
        "cache_write_usd": write,
        "output_usd": gen,
        "total_usd": uncached + read + write + gen,
    }
    # How much of the prefix was actually served from the cache. If the
    # cache did not hold, the corpus was re-written on every query and the
    # cached price never applied -- so this number is what makes the cost
    # figure above meaningful.
    out["cache"] = {
        "read": tk["cache_read"],
        "written": tk["cache_creation"],
        "hit_rate": (tk["cache_read"] / tk["total_input"]
                     if tk["total_input"] else 0.0),
    }
    return out


def _markdown(payload: dict) -> str:
    condition = payload.get("condition", "cautious")
    lines = [
        "# Experiment 8 -- generator-side comparison",
        "",
        "One generator, five arms, the same questions and the same scorer.",
        "",
        f"- condition: `{condition}`",
        f"- model: `{payload['model']}`",
        f"- answerable questions: {payload['n_answerable']}, "
        f"unanswerable questions: {payload['n_unanswerable']}",
        "",
        "| Arm | Unanswerable answered | Unanswerable claim hallucination | "
        "Answerable answered | Answerable accuracy (NLI) | Claim support (all) |",
        "|---|---|---|---|---|---|",
    ]
    for arm, s in payload["arms"].items():
        un = s.get("unanswerable", {})
        an = s.get("answerable", {})
        ov = s.get("overall", {})
        lines.append(
            f"| {arm} | {un.get('answer_rate', 0):.3f} "
            f"({un.get('n_answered', 0)}/{un.get('n', 0)}) "
            f"| {un.get('claim_hallucination_rate', 0):.3f} "
            f"| {an.get('answer_rate', 0):.3f} "
            f"| {an.get('accuracy_nli', 0):.3f} "
            f"| {ov.get('claim_support_rate', 0):.3f} |"
        )
    lines += [
        "",
        "**The two unanswerable columns answer different questions.** "
        "`answer_rate` is how often the arm answers at all when the answer "
        "does not exist -- the opportunity for hallucination. "
        "`claim_hallucination_rate` is of the claims it did produce, how many "
        "are supported by nothing in the corpus -- fabrication. A system that "
        "refuses everything scores zero on the second and is useless, so the "
        "first is the headline.",
        "",
    ]
    paired = payload.get("paired") or {}
    if paired:
        lines += [
            "**The gate's effect, paired question by question.** `b` is the "
            "number of questions the ungated arm answered and the gated arm "
            "refused; `c` is the reverse; `p` is the exact two-sided "
            "McNemar test on the discordant pairs.",
            "",
            "| Arm | Set | n | b | c | p |",
            "|---|---|---|---|---|---|",
        ]
        for arm, blk in paired.items():
            for name in ("unanswerable", "answerable"):
                d = blk.get(name) or {}
                lines.append(
                    f"| {arm} | {name} | {d.get('n_pairs', 0)} "
                    f"| {d.get('baseline_answered_arm_refused', 0)} "
                    f"| {d.get('baseline_refused_arm_answered', 0)} "
                    f"| {d.get('p_value', 1.0):.4f} |"
                )
        lines.append("")
    return "\n".join(lines)


def _resummarise(result_name: str = "exp8_generation") -> int:
    """Rebuild the per-arm summary blocks from the stored records.

    The per-question records are the measurement; the per-arm summary is
    derived from them by `summarise()`. When a field is added to the
    summary, the blocks can be rebuilt from the records already on disk
    without spending another request.
    """
    path = RESULTS_DIR / f"{result_name}.json"
    if not path.exists():
        print(f"[exp8] no result file at {path}")
        return 2
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("status") != "run":
        print("[exp8] the stored run is not a completed run; nothing to "
              "re-summarise")
        return 2
    records = payload.get("records") or {}
    arms = payload.setdefault("arms", {})
    for arm, recs in records.items():
        block = summarise(recs)
        block["seconds"] = (arms.get(arm) or {}).get("seconds", 0)
        arms[arm] = block
    payload["paired"] = _paired_effects(records)
    write_result(result_name, payload)
    (RESULTS_DIR / f"{result_name}.md").write_text(_markdown(payload),
                                                    encoding="utf-8")
    print(f"[exp8] re-summarised {len(records)} arms from the stored records")
    return 0


def _random_refusals(fitted_records: list[dict], questions: list[dict],
                      seed: int) -> set[str]:
    """The control arm's refusal set: as many questions as the fitted gate
    refused, chosen at random.

    The gate's own comparison -- with and without the gate -- cannot separate
    two things: refusing at all, and refusing the right questions. A control
    that refuses the same *number* of questions but picks them without using
    the confidence score separates them. The draw is from every question,
    because a gate that does not know which questions are answerable cannot
    do better than chance, and it is seeded so the arm is reproducible.
    """
    n = sum(1 for r in fitted_records if r.get("refused_by") == "gate_refused")
    if n <= 0:
        return set()
    rng = random.Random(seed)
    pool = [q["query"] for q in questions]
    return set(rng.sample(pool, min(n, len(pool))))


def _selected_arms() -> list[str]:
    """The arms to run, in the order they are reported.

    `MTP_GEN_ARMS` narrows the list, which is what a smoke test or a
    budget-limited re-measurement needs. The default is all of them, because a
    comparison missing an arm is not the comparison.
    """
    every = ["rag_nogate", "rag@fitted", "rag@random", "rag@transferred",
             "long_context"]
    sel = os.environ.get("MTP_GEN_ARMS", "").strip()
    if not sel:
        return every
    wanted = [a.strip() for a in sel.split(",") if a.strip()]
    unknown = [a for a in wanted if a not in every]
    if unknown:
        raise ValueError(f"unknown arms requested: {unknown}")
    return [a for a in every if a in wanted]


def main() -> int:
    condition = "cautious"
    if "--condition" in sys.argv:
        i = sys.argv.index("--condition")
        condition = sys.argv[i + 1].strip() if i + 1 < len(sys.argv) else ""
    if condition not in CONDITIONS:
        print(f"[exp8] unknown condition {condition!r}; choose one of "
              f"{', '.join(CONDITIONS)}")
        return 2
    # A tag separates one measurement from another when the same condition is
    # run more than once -- on a second generator, say. Without it the second
    # run would overwrite the first, and the first is the measurement.
    tag = ""
    if "--tag" in sys.argv:
        i = sys.argv.index("--tag")
        tag = sys.argv[i + 1].strip() if i + 1 < len(sys.argv) else ""
    # The cautious condition is the deployed system and keeps the original
    # file name; the other conditions are additional measurements beside it.
    result_name = ("exp8_generation" if condition == "cautious"
                   else f"exp8_generation_{condition}")
    if tag:
        result_name = f"{result_name}_{tag}"

    if "--resummarise" in sys.argv:
        return _resummarise(result_name)

    cfg = _llm_config()
    if cfg is None:
        print("[exp8] no API credential found; the generator-side comparison "
              "cannot be run.")
        print("       set MTP_LLM_API_KEY (and MTP_LLM_BASE_URL / "
              "MTP_LLM_MODEL if not the default) and re-run.")
        write_result(result_name, {
            "status": "not_run",
            "reason": "no API credential reachable from this machine",
            "condition": condition,
            "arms": {},
        })
        return 2
    cfg["system"] = CONDITIONS[condition]

    print("[exp8] loading index and benchmark ...", flush=True)
    index = load_index()
    bench = load_benchmark()
    fw = Framework(index)
    corpus, _ = build_long_context(fw)

    corpus_tokens = count_tokens(_tokenizer(), corpus)
    fits = corpus_tokens < cfg["context_limit"]
    print(f"[exp8] corpus is {corpus_tokens:,} tokens; the model's context "
          f"window is assumed to be {cfg['context_limit']:,} -> "
          f"{'fits' if fits else 'DOES NOT FIT'}", flush=True)

    answerable = [q for q in bench["queries"] if q["category"] != "unanswerable"]
    unanswerable = [q for q in bench["queries"] if q["category"] == "unanswerable"]
    n_unanswerable_total = len(unanswerable)
    if cfg["unanswerable"] and cfg["unanswerable"] < len(unanswerable):
        rng = random.Random(cfg["seed"])
        unanswerable = rng.sample(unanswerable, cfg["unanswerable"])
    sampled = len(unanswerable) < n_unanswerable_total
    questions = answerable + unanswerable

    print(f"[exp8] {len(answerable)} answerable + {len(unanswerable)} "
          f"unanswerable questions, model {cfg['model']}", flush=True)

    # The transferred operating point: the threshold the cross-category
    # experiment fitted on its tuning half and carried over unchanged.
    fitted_tau = float((fw.gate_model or {}).get("tau", CONFIG.gate.tau))
    transferred_tau = float(os.environ.get("MTP_GEN_TRANSFERRED_TAU", "0.5"))

    budget = {"input_tokens": 0, "exhausted": False, "errors": [], "escalated": 0}
    arms: dict[str, dict] = {}
    per_arm_records: dict[str, list[dict]] = {}

    for arm in _selected_arms():
        if fw.gate_model is not None:
            fw.gate_model = {**fw.gate_model, "tau": fitted_tau}
        run_cfg = dict(cfg)
        if arm == "rag@transferred":
            if fw.gate_model is not None:
                fw.gate_model = {**fw.gate_model, "tau": transferred_tau}
        if arm == "long_context":
            if not fits:
                arms[arm] = {
                    "status": "corpus_does_not_fit",
                    "corpus_tokens": corpus_tokens,
                    "context_limit": cfg["context_limit"],
                    "note": "the corpus is larger than this model's context "
                            "window, so the long-context arm cannot be run "
                            "against it; a larger-window model is required",
                }
                print(f"[exp8] long_context skipped: the corpus "
                      f"({corpus_tokens:,} tokens) does not fit a "
                      f"{cfg['context_limit']:,}-token window", flush=True)
                continue
            run_cfg["cache_control"] = bool(cfg["cache_control"])
            print(f"[exp8] long_context: corpus is {corpus_tokens:,} tokens"
                  f"{', sent as a cached prefix' if cfg['cache_control'] else ''}",
                  flush=True)
        print(f"[exp8] running arm: {arm}", flush=True)
        t0 = time.time()
        random_refusals = None
        if arm == "rag@random":
            random_refusals = _random_refusals(
                per_arm_records.get("rag@fitted") or [], questions, cfg["seed"])
            print(f"[exp8] rag@random: control refusing "
                  f"{len(random_refusals)} questions at random", flush=True)
        recs = run_arm(arm, fw, index, corpus, questions, run_cfg, budget,
                       random_refusals=random_refusals)
        per_arm_records[arm] = recs
        arms[arm] = summarise(recs)
        arms[arm]["seconds"] = round(time.time() - t0, 1)
        print(f"[exp8] {arm}: {len(recs)} records in {arms[arm]['seconds']}s "
              f"| unanswerable answered "
              f"{arms[arm].get('unanswerable', {}).get('answer_rate', 0):.3f}",
              flush=True)

    # An arm that was cut short -- a rejected request, an exhausted budget --
    # is not a measurement. If any arm that was supposed to run did not ask
    # every question, the whole comparison is recorded as not run rather than
    # as a result, so that no deliverable can quote a rate that was never
    # measured. The long-context arm is exempt when the corpus simply does
    # not fit the model's window: that is a recorded outcome, not a failure.
    expected_ans = len(answerable)
    expected_un = len(unanswerable)
    incomplete: list[str] = []
    for arm, blk in arms.items():
        if blk.get("status") == "corpus_does_not_fit":
            continue
        got_ans = (blk.get("answerable") or {}).get("n", 0)
        got_un = (blk.get("unanswerable") or {}).get("n", 0)
        if got_ans != expected_ans or got_un != expected_un:
            incomplete.append(
                f"{arm} asked {got_ans}/{expected_ans} answerable and "
                f"{got_un}/{expected_un} unanswerable questions")
    if budget["errors"]:
        incomplete.extend(budget["errors"][:3])
    if incomplete:
        if budget["errors"]:
            reason = ("the generator rejected the requests, so no arm asked "
                      "any question and no rate from it is reported: "
                      + budget["errors"][0])
        else:
            reason = ("the comparison did not complete, so no rate from it is "
                      "reported: " + "; ".join(incomplete))
        print(f"[exp8] NOT RUN -- {reason}", flush=True)
        payload = {
            "status": "not_run",
            "reason": reason,
            "model": cfg["model"],
            "n_answerable": expected_ans,
            "n_unanswerable": expected_un,
            "n_unanswerable_total": n_unanswerable_total,
            "arms": {},
        }
        write_result(result_name, payload)
        return 2

    payload = {
        "status": "run",
        "condition": condition,
        "model": cfg["model"],
        # The measurement records the retrieval configuration it was taken
        # under, so the build can tell whether this result sits on the
        # shipped configuration or on an earlier one. Every arm except the
        # long-context one retrieves, so the placement changes what the
        # generator was shown.
        "retrieval_placement": CONFIG.modality.position,
        "generator": {
            "base_url": cfg["base_url"],
            "sampling": SAMPLING_NOTE,
            "temperature_requested": 0,
            "cache_control": bool(cfg["cache_control"]),
            "max_tokens": cfg.get("max_tokens", 1024),
            "escalate_after": _escalate_after,
            "max_tokens_ceiling": _max_token_ceiling,
            "requests_escalated": budget.get("escalated", 0),
            "prices_per_million": _prices(),
        },
        "n_answerable": len(answerable),
        "n_unanswerable": len(unanswerable),
        "n_unanswerable_total": n_unanswerable_total,
        "unanswerable_sampled": sampled,
        "corpus_tokens": corpus_tokens,
        "context_limit": cfg["context_limit"],
        "fits_context_window": fits,
        "fitted_tau": fitted_tau,
        "transferred_tau": transferred_tau,
        "support_threshold": SUPPORT_THRESHOLD,
        "candidates_per_claim": CANDIDATES_PER_CLAIM,
        "arms": arms,
        "paired": _paired_effects(per_arm_records),
        "records": per_arm_records,
    }
    write_result(result_name, payload)
    (RESULTS_DIR / f"{result_name}.md").write_text(_markdown(payload),
                                                    encoding="utf-8")
    print(f"[exp8] wrote {RESULTS_DIR / (result_name + '.json')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
