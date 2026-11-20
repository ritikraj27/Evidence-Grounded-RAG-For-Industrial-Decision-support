"""End-to-end pipeline: ingest -> index -> retrieve -> rerank -> gate -> answer.

The pipeline is deliberately explicit about *where* each design decision sits,
because the thesis's contribution is the arrangement, and a reviewer should be
able to see that removing any one stage changes the system's behaviour in a
predictable way.

    STAGE 1  INGESTION        (offline, once per document)
        parse -> chunk -> tag modality + category -> embed -> index

    STAGE 2  RETRIEVAL       (online, per query)
        category pre-filter -> BM25 + dense -> RRF -> modality quota
                                            -> cross-encoder rerank
                                            -> Bayesian confidence gate

    STAGE 3  GENERATION      (online, per accepted query)
        per-claim tagging -> citation -> contradiction flag -> answer

Two properties are load-bearing.

**(a) The gate sits between reranking and generation, and nothing can bypass
it.** The `answer()` method returns a no-evidence response when the gate
rejects; it does not call the generator, and no argument lets a caller
override that. The generator is *injected* into the framework rather than
called by a harness, so the framework -- not the caller -- decides when it
runs: the model is reached at exactly one line in `answer()`, after the gate
has accepted. This is the difference between "the model was told to be
careful" (an instruction, which a model can ignore) and "the model was never
called" (a control-flow fact).

**(b) The category pre-filter runs before retrieval, not after.** Filtering
after retrieval means the retriever already paid to score documents that were
going to be discarded, and -- more importantly -- the discarded documents
still influenced the fusion. Filtering before retrieval means the candidate
pool contains only in-category material, so the dense model's top-k and the
reranker's ranking are computed on the correct sub-corpus.

BM25 is the exception, and the exception is worth stating: BM25 scores the
whole corpus and the filter is applied to the candidate list afterwards, so
BM25's IDF statistics are *not* computed on the sub-corpus. This is not a
pedantic distinction. It is why a soft prior cannot reproduce the filter's
benefit: a prior promotes the in-category chunks in the fused ranking but
leaves the pool whole, whereas a filter removes the out-of-category chunks
the reranker would have ranked highly. Measured in
`research/20_soft_prior.md`.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import numpy as np

from . import claims as claims_mod
from . import contradiction as contradiction_mod
from .config import ARTIFACT_DIR, Config, CONFIG
from .confidence import (
    NO_EVIDENCE_MESSAGE,
    apply_gate,
    posterior_from_score,
)
from .evaluate import aggregate_generation, evaluate_retrieval
from .hybrid import apply_modality_quota, reciprocal_rank_fusion
from .ingestion import Chunk, corpus_statistics, ingest_corpus
from .lexical import BM25Index
from .models import dense_top_k, embed_texts, rerank

#: Cross-encoder scores, cached by (model, query, candidate pool).
#:
#: The ablation evaluates seven configurations over the same queries, and
#: four of them rerank the *same* pool of fifty. Without this cache the
#: cross-encoder scores the same pairs four times, which is the single
#: largest cost in the suite. The cache is keyed on the identity of the
#: pool, so a different pool is a different key and cannot collide.
_RERANK_CACHE: dict[tuple, list[tuple[str, float]]] = {}


def _rerank_cached(query: str, pairs, model_name: str):
    """Cross-encoder scores for a query and a candidate pool, cached."""
    key = (model_name, query, tuple(cid for cid, _ in pairs))
    hit = _RERANK_CACHE.get(key)
    if hit is None:
        hit = rerank(query, pairs, model_name=model_name)
        _RERANK_CACHE[key] = hit
    return hit


def _apply_category_prior(fused: dict[str, float], category_of: dict[str, str],
                          category: str, weight: float, k: int) -> dict[str, float]:
    """Promote the in-category chunks without removing the others.

    The in-category chunks are ranked as a third list over their current
    order, and each one gains ``weight / (k + rank)`` -- the same shape as
    the reciprocal-rank-fusion term the two retrieval legs contribute. A
    weight of 1.0 is exactly one extra RRF list; a weight of 2.0 is two.

    The hard pre-filter and this prior differ in one way that matters: a
    chunk outside the category cannot be retrieved at all under the hard
    filter, and under the prior it can -- it is only demoted.
    """
    ranked = [cid for cid, _ in sorted(fused.items(), key=lambda kv: -kv[1])]
    prior_list = [cid for cid in ranked if category_of.get(cid) == category]
    prior = reciprocal_rank_fusion([prior_list], k=k)
    out = dict(fused)
    for cid, s in prior.items():
        out[cid] = out.get(cid, 0.0) + weight * s
    return out


#: The fitted gate model, written by `run_gate.py`. Absent until the gate
#: has been calibrated on a held-out query split.
GATE_MODEL_PATH = ARTIFACT_DIR / "gate_model.json"


@dataclass
class Index:
    """The offline index built from a corpus."""

    chunks: list[Chunk]
    bm25: BM25Index
    embeddings: np.ndarray
    chunk_ids: list[str]
    chunk_text: dict[str, str]
    modality_of: dict[str, str]
    category_of: dict[str, str]
    stats: dict = field(default_factory=dict)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        np.save(path.with_suffix(".npy"), self.embeddings)
        path.with_suffix(".json").write_text(
            json.dumps(
                {
                    "chunks": [c.to_dict() for c in self.chunks],
                    "stats": self.stats,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: Path, config: Config = CONFIG) -> "Index":
        data = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
        chunk_dicts = data["chunks"]
        chunks = [
            Chunk(
                chunk_id=c["chunk_id"],
                doc_id=c["doc_id"],
                text=c["text"],
                modality=c["modality"],
                page=c["page"],
                section=c.get("section", ""),
                caption=c.get("caption", ""),
                category=c.get("category", "general"),
                meta=c.get("meta", {}),
            )
            for c in chunk_dicts
        ]
        chunk_ids = [c.chunk_id for c in chunks]
        chunk_text = {c.chunk_id: c.text for c in chunks}
        modality_of = {c.chunk_id: c.modality for c in chunks}
        category_of = {
            c.chunk_id: (c.category or c.meta.get("category", "general")) for c in chunks
        }
        bm25 = BM25Index.build(
            chunk_text,
            k1=config.lexical.k1,
            b=config.lexical.b,
        )
        embeddings = np.load(path.with_suffix(".npy"))
        return cls(chunks, bm25, embeddings, chunk_ids, chunk_text, modality_of,
                   category_of, data.get("stats", {}))


def build_index(corpus_dir: Path | None = None, config: Config = CONFIG) -> Index:
    """Stage 1 -- ingestion and indexing."""
    from .config import CORPUS_DIR

    corpus_dir = corpus_dir or CORPUS_DIR
    chunks = ingest_corpus(corpus_dir)
    if not chunks:
        raise SystemExit(f"No documents found under {corpus_dir}")
    chunk_ids = [c.chunk_id for c in chunks]
    chunk_text = {c.chunk_id: c.text for c in chunks}
    bm25 = BM25Index.build(chunk_text, k1=config.lexical.k1, b=config.lexical.b)
    embeddings = embed_texts(
        [c.text for c in chunks],
        model_name=config.embedding.model,
        batch_size=config.embedding.batch_size,
        normalize=config.embedding.normalize,
        dim=config.embedding.dim,
        max_seq_length=config.embedding.max_seq_length,
    )
    modality_of = {c.chunk_id: c.modality for c in chunks}
    category_of = {
        c.chunk_id: (c.category or c.meta.get("category", "general")) for c in chunks
    }
    stats = corpus_statistics(chunks)
    return Index(
        chunks=chunks,
        bm25=bm25,
        embeddings=embeddings,
        chunk_ids=chunk_ids,
        chunk_text=chunk_text,
        modality_of=modality_of,
        category_of=category_of,
        stats=stats,
    )


@dataclass
class RetrievalTrace:
    """Everything that happened for one query, kept for auditability."""

    query: str
    category: str
    dense: list[str]
    lexical: list[str]
    fused: list[str]
    reranked: list[str]
    accepted: list[str]
    posterior: list[float]
    gate_rejected: bool
    message: str = ""
    modality_counts: dict = field(default_factory=dict)
    quota_note: str = ""
    #: The five query-level signals the gate is calibrated on.
    features: list = field(default_factory=list)
    #: The full reranked ranking, before the final-context truncation.
    #: The reranker scores a pool of `rerank.top_n` candidates and the system
    #: delivers the best ten of them; keeping the whole ranking means
    #: Recall@20 is a measurement rather than an artefact of the truncation
    #: (for a ten-item list, Recall@20 == Recall@10 by construction).
    reranked_full: list[str] = field(default_factory=list)
    #: True when the request was refused before retrieval, because it was not
    #: a well-formed question. The retrieval never ran, so everything above
    #: is empty and `gate_rejected` is False -- the gate did not reject it.
    form_rejected: bool = False


@dataclass
class AnswerResult:
    """The framework's full output for one query."""

    query: str
    answer: str
    accepted: bool
    trace: RetrievalTrace
    claim_assessments: list = field(default_factory=list)
    #: The conflict findings that are *surfaced* to the practitioner. A
    #: finding whose branch has a measured precision below the calibration
    #: floor is recorded but withheld, and appears in
    #: ``contradictions_withheld`` instead.
    contradictions: list = field(default_factory=list)
    #: The findings that were recorded and withheld, with the reason.
    contradictions_withheld: list = field(default_factory=list)
    contradiction_summary: dict = field(default_factory=dict)
    #: Why the request was refused: "form" if the query was not a
    #: well-formed question, "evidence" if the gate rejected the retrieved
    #: passages, and empty if it was answered.
    refusal: str = ""


class Framework:
    """The evidence-grounded RAG framework.

    Two checks stand between a request and the language model, and the
    framework owns both of them rather than trusting the caller to apply
    them:

    * a **form check** (`src/query_form.py`) before retrieval, which refuses
      a request that is not a well-formed question at all;
    * the **confidence gate** (`src/confidence.py`) after retrieval, which
      refuses a request whose retrieved passages do not support an answer.

    They answer different questions and neither substitutes for the other: the
    form check cannot tell whether the corpus contains the answer, and the
    gate cannot tell whether the question was ever a question.
    """

    #: Set once the un-calibrated fallback has been announced, so the warning
    #: is emitted a single time rather than on every query.
    _gate_warned = False
    def __init__(self, index: Index, config: Config = CONFIG,
                 generator: Callable[[str, str], str] | None = None):
        """`generator` is the language model, as `generator(query, context) -> str`.

        It is injected rather than called from a harness because the gate's
        non-bypassability has to be a property of the framework, not a
        convention each caller is trusted to follow. When a generator is
        supplied, `answer()` calls it itself, and only after the gate has
        accepted. There is no path through this class that reaches the model
        without passing the gate first.
        """
        self.index = index
        self.config = config
        self.generator = generator
        # chunk_id -> row in the embedding matrix
        self._pos = {cid: i for i, cid in enumerate(index.chunk_ids)}
        self._embed_cache: dict[str, np.ndarray] = {}
        self.gate_model = None
        if GATE_MODEL_PATH.exists():
            self.gate_model = json.loads(GATE_MODEL_PATH.read_text(encoding="utf-8"))

    # -- Stage 2 ---------------------------------------------------------
    def retrieve(
        self,
        query: str,
        category: str | None = None,
        apply_quota: bool = True,
        apply_rerank: bool = True,
        use_dense: bool = True,
        use_lexical: bool = True,
        quota_position: str | None = None,
        rerank_pool: int | None = None,
        category_prior: float = 0.0,
    ) -> RetrievalTrace:
        cfg = self.config
        pool = self.index.chunk_ids
        if category and category != "general" and category_prior <= 0:
            pool = [c for c in pool if self.index.category_of.get(c) == category]
            if not pool:
                pool = self.index.chunk_ids

        qvec = embed_texts(
            [query],
            model_name=cfg.embedding.model,
            normalize=cfg.embedding.normalize,
            query_prefix=cfg.embedding.query_prefix,
            is_query=True,
            dim=cfg.embedding.dim,
        )

        dense_list: list[str] = []
        if use_dense:
            pool_vecs = self.index.embeddings[[self._pos[c] for c in pool]]
            dense_list = [
                cid for cid, _ in dense_top_k(qvec, pool_vecs, pool, cfg.fusion.dense_top_k)
            ]

        lexical_list: list[str] = []
        if use_lexical:
            scores = self.index.bm25.score(query)
            # The category pre-filter must be applied to the lexical leg too.
            # Filtering only the dense leg is a silent no-op: BM25 dominates
            # the fusion, so an unfiltered lexical list floods the fused
            # ranking with out-of-category documents and the filter's effect
            # disappears. (This is the same failure mode as a pgvector
            # metadata filter applied to only one of two indexes.)
            allowed = set(pool)
            order = np.argsort(-scores)
            lexical_list = [
                self.index.chunk_ids[i]
                for i in order
                if scores[i] > 0 and self.index.chunk_ids[i] in allowed
            ][: cfg.fusion.lexical_top_k]

        fused = reciprocal_rank_fusion(
            [dense_list, lexical_list], k=cfg.fusion.rrf_k, doc_ids=pool
        )
        if category and category != "general" and category_prior > 0:
            # The soft prior. The whole corpus stays in the pool -- an
            # out-of-category chunk can still be retrieved if it is the
            # only evidence -- and the in-category chunks are promoted in
            # the fused ranking instead of being the only candidates. The
            # promotion is one extra reciprocal-rank-fusion term over the
            # in-category chunks in their current order, weighted by
            # `category_prior`; a weight of 1.0 is exactly one extra RRF
            # list. The default of 0 leaves the hard pre-filter above
            # untouched.
            fused = _apply_category_prior(
                fused, self.index.category_of, category, category_prior,
                cfg.fusion.rrf_k)
        fused_ranked = sorted(fused.items(), key=lambda kv: -kv[1])
        fused_ids = [cid for cid, _ in fused_ranked]

        # Where the quota sits is a configuration value, so the deliverables
        # can read what the system actually does rather than being told.
        if quota_position is None:
            quota_position = cfg.modality.position
        if quota_position not in ("pre_rerank", "post_rerank"):
            raise ValueError(
                f"quota_position must be 'pre_rerank' or 'post_rerank', "
                f"not {quota_position!r}")

        # Modality quota operates on the fused ranking, before reranking, so
        # that the reranker sees a context that already respects the corpus's
        # modality imbalance.
        modality_counts: dict[str, int] = {}
        quota_note = ""

        # The quota can sit at two points in the pipeline, and the choice
        # matters more than the threshold does:
        #
        #   pre_rerank  -- the quota proposes a MEMBERSHIP for the final
        #                  ten: the reranker then scores those ten and can
        #                  reorder them but cannot change which ten they
        #                  are, so a forced table chunk survives and the
        #                  floor binds.
        #
        #   post_rerank -- the reranker ranks first and chooses the final
        #                  ten itself, and the quota then adjusts that
        #                  context, typically by importing a chunk the
        #                  reranker already ranked below the cut. It tends
        #                  to import the wrong chunk and to displace a good
        #                  one.
        #
        # The ablation measures both, and it inverts the rule this framework
        # was designed on: the pre-rerank placement is the better one. The
        # system shipped the post-rerank placement until 16 November 2026,
        # because that was the September 2026 design and every measurement
        # before that date was taken with it. The default now lives in
        # `ModalityQuotaConfig.position`, and it is the placement the
        # ablation recommends.
        pre_quota_candidates: list[str] | None = None
        if apply_quota and quota_position == "pre_rerank":
            pool_for_quota = fused_ids[: cfg.rerank.top_n]
            q = apply_modality_quota(pool_for_quota, self.index.modality_of, cfg.modality)
            pre_quota_candidates = q.selected
            modality_counts = q.counts
            quota_note = q.note

        # --- reranking -------------------------------------------------
        # The cross-encoder always scores the same bounded pool (top-N of the
        # fused ranking), so every candidate the quota might swap in already
        # carries a score. That keeps the score vector aligned with the final
        # context and the gate honest.
        pool_size = rerank_pool if rerank_pool is not None else cfg.rerank.top_n
        rerank_pool = (
            pre_quota_candidates
            if pre_quota_candidates is not None
            else fused_ids[:pool_size]
        )
        score_map: dict[str, float] = {}
        reranked_ids: list[str] = []
        reranked_full: list[str] = []
        if apply_rerank and rerank_pool:
            pairs = [(cid, self.index.chunk_text[cid]) for cid in rerank_pool]
            scored = _rerank_cached(query, pairs, cfg.rerank.model)
            score_map = {cid: s for cid, s in scored}
            reranked_full = [cid for cid, _ in scored]
            reranked_ids = reranked_full[: cfg.rerank.top_k_final]
        elif rerank_pool:
            reranked_full = list(rerank_pool)
            reranked_ids = reranked_full[: cfg.rerank.top_k_final]

        # --- post-rerank quota -----------------------------------------
        if apply_quota and quota_position == "post_rerank" and reranked_ids:
            # Donors come from the scored pool, so a swapped-in chunk always
            # has a reranker score.
            donor_pool = list(score_map.keys()) or reranked_ids
            q = apply_modality_quota(donor_pool, self.index.modality_of, cfg.modality)
            reranked_ids = q.selected
            modality_counts = q.counts
            quota_note = q.note

        raw_scores = np.array([score_map.get(cid, 0.0) for cid in reranked_ids], dtype=np.float64)

        # --- the confidence gate ---------------------------------------
        # The gate makes a QUERY-level decision: "does this retrieved context
        # contain sufficient evidence to answer at all?" Its probability is
        # produced by a logistic model over five signals of the retrieved set,
        # fitted on a held-out query split by `run_gate.py` and loaded from
        # `artifacts/gate_model.json`.
        #
        # If no calibrated model is present the framework falls back to the
        # chunk-level posterior, which is strictly weaker -- it is the
        # degenerate solution described in confidence.py, and it is why the
        # query-level design exists. The fallback is logged loudly so it
        # cannot be mistaken for the calibrated path.
        from .confidence import (
            apply_gate,
            detectability_features,
            detectability_posterior,
        )

        all_scores = sorted(score_map.values(), reverse=True)
        bm25_all = self.index.bm25.score(query)
        bm25_max = float(bm25_all.max()) if bm25_all.size else 0.0
        features = detectability_features(
            top1_rerank=all_scores[0] if all_scores else -10.0,
            mean_top3_rerank=float(np.mean(all_scores[:3])) if all_scores else -10.0,
            top1_bm25=bm25_max,
            max_rrf=max(fused.values()) if fused else 0.0,
            n_candidates_above_bar=float(sum(1 for s in all_scores if s > 0.0)),
        )

        gate_model = self.gate_model
        if gate_model is not None:
            sufficiency = detectability_posterior(features, gate_model)
            posterior = np.array([sufficiency] * len(reranked_ids), dtype=np.float64)
            # Use the operating point that was selected when the model was
            # fitted, not the configuration default: the calibration and the
            # threshold are two halves of one fitted artefact, and mixing a
            # fitted posterior with a different threshold silently changes
            # the operating point the calibration was measured at.
            tau = float(gate_model.get("tau", cfg.gate.tau))
            decision = apply_gate(reranked_ids, posterior, tau=tau)
            if not decision.accept:
                decision.message = NO_EVIDENCE_MESSAGE.format(
                    posterior=sufficiency, tau=tau
                )
        else:
            if not Framework._gate_warned:
                Framework._gate_warned = True
                print("[gate] WARNING: no calibrated gate model found at "
                      f"{GATE_MODEL_PATH}; falling back to the un-calibrated "
                      "chunk-level posterior. Run impl/experiments/run_gate.py "
                      "first.")
            if apply_rerank and reranked_ids:
                posterior = posterior_from_score(raw_scores, cfg.gate.beta0,
                                                cfg.gate.beta1)
            else:
                posterior = np.ones(len(reranked_ids), dtype=np.float64)
            decision = apply_gate(reranked_ids, posterior, tau=cfg.gate.tau)
            if not decision.accept:
                # The fallback is NOT a calibrated sufficiency probability --
                # it is an un-calibrated chunk-level posterior. Say so, rather
                # than presenting a number as something it is not.
                decision.message = (
                    "No evidence in the indexed documentation supports an answer "
                    "to this question. The retrieval-confidence gate rejected the "
                    "retrieved passages (un-calibrated chunk-level posterior "
                    f"{float(posterior.max()):.3f} < threshold {cfg.gate.tau:.3f}). "
                    "No answer has been generated, because generating one would "
                    "mean inventing it. NOTE: this gate is running on the "
                    "un-calibrated fallback; run impl/experiments/run_gate.py to "
                    "fit and load the calibrated model."
                )

        return RetrievalTrace(
            query=query,
            category=category or "general",
            dense=dense_list,
            lexical=lexical_list,
            fused=fused_ids,
            reranked=reranked_ids,
            reranked_full=reranked_full,
            accepted=decision.accepted_chunks,
            posterior=[float(p) for p in posterior],
            gate_rejected=not decision.accept,
            message=decision.message,
            modality_counts=modality_counts,
            quota_note=quota_note,
            features=features,
        )

    # -- Stage 3 ---------------------------------------------------------
    def answer(
        self,
        query: str,
        category: str | None = None,
        answer_text: str | None = None,
        check_form: bool = True,
    ) -> AnswerResult:
        """Run the full pipeline and produce the tagged answer.

        `answer_text` is the generator's output, if the caller already has one.
        In the full system this comes from an LLM; the framework passes it in so
        that the confidence, contradiction and per-claim machinery can be
        evaluated independently of the generator, which is what makes the
        ablation clean. If it is None and the framework was given a
        `generator`, the framework calls the generator itself -- after the gate
        has accepted, and with only the accepted passages as evidence. If
        there is no generator either, an extractive answer is synthesised from
        the accepted chunks.

        `check_form` runs the query-form check first. It is on by default and
        the framework applies it itself, for the same reason it owns the
        generator: a request that is not a question cannot produce an answer,
        and the guarantee has to be a property of the framework rather than a
        convention each caller is trusted to follow. The flag exists so the
        ablation can turn it off and measure what it is worth.
        """
        from .confidence import apply_gate
        from .query_form import FORM_REFUSAL_MESSAGE, assess_query_form

        # The form check comes before retrieval, so a request that is not a
        # question costs no retrieval, no cross-encoder pass and no model
        # call.
        if check_form:
            form = assess_query_form(query)
            if form.rejected:
                return AnswerResult(
                    query=query,
                    answer=FORM_REFUSAL_MESSAGE.format(detail=form.detail),
                    accepted=False,
                    trace=RetrievalTrace(
                        query=query,
                        category=category or "",
                        dense=[],
                        lexical=[],
                        fused=[],
                        reranked=[],
                        accepted=[],
                        posterior=[],
                        gate_rejected=False,
                        message=FORM_REFUSAL_MESSAGE.format(detail=form.detail),
                        form_rejected=True,
                    ),
                    refusal="form",
                )

        trace = self.retrieve(query, category=category)
        if trace.gate_rejected:
            return AnswerResult(
                query=query,
                answer=trace.message,
                accepted=False,
                trace=trace,
                refusal="evidence",
            )

        accepted = trace.accepted
        context_texts = [self.index.chunk_text[c] for c in accepted]
        context_ids = accepted

        # The model is reached here and nowhere else: after the gate has
        # accepted, with the accepted passages as its evidence.
        if answer_text is None and self.generator is not None:
            answer_text = self.generator(query, "\n\n".join(context_texts))

        assessments = claims_mod.assess_claims(
            claims_mod.split_into_claims(answer_text or ""),
            context_texts,
            context_ids,
            self.config.claim,
        )

        findings = contradiction_mod.detect_contradictions(
            context_texts,
            context_ids,
            embeddings=np.array([self.index.embeddings[self._pos[c]] for c in accepted]),
            config=self.config.contradiction,
        )

        rendered = claims_mod.render_answer(assessments, self.index.chunk_text)
        if answer_text is None:
            rendered = self._extractive_answer(accepted, assessments, findings)

        return AnswerResult(
            query=query,
            answer=rendered,
            accepted=True,
            trace=trace,
            claim_assessments=assessments,
            contradictions=[f for f in findings if f.flagged and f.surfaced],
            contradictions_withheld=[f for f in findings
                                      if f.flagged and not f.surfaced],
            contradiction_summary=contradiction_mod.contradiction_summary(findings),
        )

    def _extractive_answer(self, accepted: list[str], assessments, findings) -> str:
        """A generator-free answer for pipeline testing.

        It concatenates the accepted passages with their confidence tags. It
        is NOT the production generator -- it exists so that the retrieval,
        gating and contradiction machinery can be tested without an LLM in
        the loop, which keeps the ablations interpretable.
        """
        lines = []
        # Only a *surfaced* finding reaches the practitioner. A finding
        # whose branch has a measured precision below the calibration floor
        # is recorded and withheld, and a withheld finding must not leave a
        # mark on the answer.
        flagged = {f.chunk_a for f in findings if f.flagged and f.surfaced} | {
            f.chunk_b for f in findings if f.flagged and f.surfaced
        }
        for cid in accepted:
            marker = " [CONTRADICTION DETECTED IN THIS GROUP]" if cid in flagged else ""
            lines.append(f"{self.index.chunk_text[cid]}{marker}")
        return "\n\n".join(lines)
