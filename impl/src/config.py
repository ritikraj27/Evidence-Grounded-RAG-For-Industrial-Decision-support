"""Single source of truth for every hyperparameter in the framework.

Design rule: no magic numbers in the pipeline. Anything a reviewer could ask
"where did this come from?" lives here with a provenance note.
"""
import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _variant(base: str) -> Path:
    """Resolve a data path, honouring a variant environment override.

    The framework is evaluated on more than one corpus: the full six-category
    corpus that carries the cross-category transfer experiment, and a
    single-domain (focus) corpus that carries the headline demonstration.
    Setting `MTP_VARIANT=focus` points every path at `data/corpus_focus`,
    `data/benchmark_focus`, `artifacts_focus` and `results_focus`, so both
    evaluations run from the same code without a single conditional.
    """
    variant = os.environ.get("MTP_VARIANT", "").strip()
    if not variant:
        return ROOT / base
    stem = Path(base).name
    parent = Path(base).parent.name
    return ROOT / parent / f"{stem}_{variant}"


CORPUS_DIR = _variant("data/corpus")
BENCHMARK_DIR = _variant("data/benchmark")
ARTIFACT_DIR = _variant("artifacts")
RESULTS_DIR = _variant("results")


@dataclass(frozen=True)
class EmbeddingConfig:
    """Dense retrieval configuration (design move D3).

    The encoder is a retrieval-trained multilingual model. The previous one,
    `all-MiniLM-L6-v2`, is a *general-purpose sentence encoder* trained with a
    symmetric similarity objective, whereas retrieval is asymmetric: a passage
    is not similar to a question, it answers it. That mismatch was measurable
    here — dense-only retrieval was significantly worse than plain BM25 — and
    the thesis named replacing it as its highest-value change.

    `BAAI/bge-m3` is the replacement: 1024 dimensions, CLS pooling, a
    normalisation module, and a long-document training strategy that handles
    the query/passages asymmetry natively.

    **On the query instruction.** BGE-v1.5 and the small instruction-tuned
    encoders (E5, GTE) expect a query prefix such as "Represent this sentence
    for searching relevant passages: ". BGE-M3 does not: its model card states
    that the model "no longer requires adding instructions to the queries",
    because the asymmetry is handled in training rather than in the prompt.
    `query_prefix` is therefore empty here. It is kept configurable because the
    next encoder may well want one.
    """

    model: str = "BAAI/bge-m3"
    #: 1024 for bge-m3. The vector column width in Postgres must match.
    dim: int = 1024
    #: L2-normalisation makes inner product == cosine similarity. The model
    #: ships a Normalize module, so this agrees with its own configuration.
    normalize: bool = True
    #: Batch size for the encoder forward pass. 16 rather than 64 because
    #: bge-m3 is an XLM-RoBERTa-large: 1024 dimensions across 24 layers is a
    #: much larger activation footprint than the previous 384-dim MiniLM.
    batch_size: int = 16
    #: Whether the query and the document are prefixed differently. Empty for
    #: bge-m3 -- see the class docstring.
    query_prefix: str = ""
    #: The tokenised length the encoder is allowed to see. None means the
    #: model's own limit, which for bge-m3 is 8,192 -- far more than any
    #: chunk in these corpora needs, and an order of magnitude more
    #: expensive to encode. 512 is the same window the cross-encoder uses,
    #: so setting it makes the dense leg see the same text the reranker
    #: will. It is part of the embedding cache key, and None is the default
    #: so that the corpora already encoded keep their vectors.
    max_seq_length: int | None = None


@dataclass(frozen=True)
class LexicalConfig:
    """BM25 configuration.

    Provenance: Robertson & Zaragoza (2009), "The Probabilistic Relevance
    Framework: BM25 and Beyond", FnTIR 3(4). k1 and b are the standard
    defaults recommended by Robertson et al. and used by Lucene since 8.x.
    """

    k1: float = 1.2
    b: float = 0.75
    #: Robertson's IDF variant with the +1 inside the log, which keeps IDF
    #: non-negative even for terms present in more than half the documents.
    idf_variant: str = "robertson_plus1"


@dataclass(frozen=True)
class FusionConfig:
    """Reciprocal Rank Fusion configuration (design move D3).

    Provenance: Cormack, Clarke & Buettcher (2009), SIGIR. The paper evaluates
    k = 60 as the default and reports it is not sensitive for k > 10.
    """

    rrf_k: int = 60
    #: How many candidates each retriever contributes before fusion.
    #: Deep pools cost more but give fusion more evidence to work with.
    dense_top_k: int = 20
    lexical_top_k: int = 20


@dataclass(frozen=True)
class RerankConfig:
    """Cross-encoder reranking configuration.

    Provenance: ms-marco-MiniLM-L-6-v2, the cross-encoder distilled from the
    MS MARCO ranking task. See the Sept 2026 report: on the
    production_scheduling sub-category this model REGRESSED retrieval by
    5.34 points relative to RRF alone, which is why the gate downstream is
    not optional.
    """

    model: str = "cross-encoder/ms-marco-MiniLM-L6-v2"
    #: How many fused candidates are handed to the cross-encoder. This is
    #: NOT a cosmetic setting: a reranker can only reorder what it is shown,
    #: so a pool the size of the final context cannot improve recall -- it can
    #: only permute what is already there, and can lose the relevant chunk
    #: that was sitting just below the cut. See Experiment 5.
    top_n: int = 50
    #: Chunks above this score are passed to the generator.
    top_k_final: int = 10


@dataclass(frozen=True)
class GateConfig:
    """Confidence-gate configuration (design move D1).

    The posterior is a calibrated probability that a chunk is *relevant to the
    user's question*, not a similarity score. The threshold tau is the
    operating point; everything below it triggers the no-evidence response.
    """

    #: Operating threshold on the calibrated posterior.
    tau: float = 0.50
    #: Logistic-regression coefficients on the raw reranker score.
    #: Defaults are placeholders until `fit_gate` is run on the calibration set;
    #: `impl/experiments/run_calibration.py` overwrites them with fitted values.
    beta0: float = 2.943
    beta1: float = 1.680
    #: Number of equal-width probability bins for the reliability diagram.
    n_bins: int = 10


@dataclass(frozen=True)
class ModalityQuotaConfig:
    """Modality-balanced retrieval configuration (design move D2).

    The quota is a *floor* on the share of non-text chunks, not a ceiling on
    text. Rationale: in industrial corpora the binding requirement usually sits
    in a table (EOQ, Incoterms, safety stock, acceptance criteria), while the
    top-k dense ranking is dominated by prose because text chunks are the
    majority of the corpus and are also the most self-similar.
    """

    #: Minimum fraction of the final context that must come from tables.
    min_table_share: float = 0.15
    #: Minimum fraction of the final context that must come from charts/figures.
    min_chart_share: float = 0.05
    #: How many extra candidates to pull per modality when filling a quota.
    quota_depth: int = 10
    #: Where the quota is applied relative to the cross-encoder.
    #:
    #: ``pre_rerank`` fixes the *membership* of the final ten before the
    #: reranker sees them, so the reranker can reorder those ten but cannot
    #: change which ten they are, and a forced table chunk survives.
    #: ``post_rerank`` lets the reranker choose the ten and then imports a
    #: chunk it already ranked below the cut, which tends to displace a good
    #: one.
    #:
    #: The ablation measures both: the pre-rerank placement is better on the
    #: focus domain and on the six-category corpus, the post-rerank one is
    #: marginally better on the industrial corpus, and none of the
    #: differences is statistically significant. Which one ships is a
    #: project decision, and the deliverables read this value rather than
    #: asserting it, so the two cannot drift apart.
    position: str = "pre_rerank"


@dataclass(frozen=True)
class ContradictionConfig:
    """Contradiction-surfacing configuration (design move D4).

    Two gates must agree before a contradiction is reported:
      (a) an NLI model says the two chunks conflict, AND
      (b) a topical check says the two chunks are about the same subject.
    Gate (b) is what suppresses the false positives that a bare NLI gate
    produces when two passages discuss different sub-topics.

    **The two profiles.** The measurement vocabulary -- the nouns that turn a
    number into a *quantity* -- and the version vocabulary -- the markers that
    say which issue of a named standard a passage describes -- are declared
    priors, not fitted parameters. They were written for operations and
    supply-chain prose ("eoq", "safety stock", "lead time", "Incoterms 2020").

    A regulatory corpus binds on entirely different nouns ("permissible
    exposure limit", "clearance", "flash point") and carries entirely
    different version markers ("ASTM A47-68", "ISO 817:2014"). The
    `measurement_profile` and `standard_profile` settings select which
    vocabulary applies, so that the mechanism can be *measured* on both
    corpora with the same code. The default is the shipped vocabulary, so
    the focus corpus's fitted calibration is unaffected by the existence of
    the alternative.
    """

    nli_model: str = "cross-encoder/nli-deberta-v3-small"
    #: Minimum NLI contradiction probability to consider a conflict.
    nli_threshold: float = 0.70
    #: Minimum embedding cosine similarity for two chunks to count as "same subject".
    topic_threshold: float = 0.55
    #: Minimum Jaccard overlap of numbers/entities between the two chunks.
    entity_overlap_min: float = 0.10
    #: Maximum number of pairwise comparisons per query (quadratic in context size).
    max_pairs: int = 60
    #: Which measurement vocabulary applies: "operations" (the shipped one)
    #: or "regulatory" (the one the industrial-corpus measurement
    #: motivated).
    measurement_profile: str = "operations"
    #: Which version vocabulary applies: "commercial" (the shipped one) or
    #: "regulatory" (standard citations with their edition).
    standard_profile: str = "commercial"
    #: How far back from the number the measurement term may sit. 0 is the
    #: shipped rule: the term must be the token immediately before the
    #: number, which fits "the reorder point was set to 40 units". A
    #: regulation writes "the permissible exposure limit for cadmium is 5
    #: micrograms per cubic meter", where the noun phrase is separated from
    #: the number by the thing being limited and the copula, so the
    #: regulatory measurement needs a look-back of 3.
    #:
    #: The default is 0, so the shipped behaviour -- and the focus corpus's
    #: fitted calibration -- are unchanged. The two changes are reported
    #: separately, because they are separable: one widens the rule, the
    #: other changes the vocabulary it draws on.
    measurement_lookback: int = 0
    #: Whether a single trailing capital letter is kept inside a proper
    #: name. "Plant A" and "Plant B" are two instances, and the instance
    #: check is the only thing that tells them apart -- but "A" is on the
    #: stop list as the English article, so without this rule the instance
    #: identifier disappears at the start of a passage and two plants
    #: become one.
    #:
    #: It is off by default because it is not free: on the focus corpus the
    #: single capital letters are mostly *author initials* ("Eliyahu M" for
    #: Goldratt), and keeping them changes which pairs the instance check
    #: treats as the same instance. The default therefore leaves the
    #: shipped behaviour unchanged by construction, and the industrial
    #: measurement turns it on.
    instance_identifier: bool = False


@dataclass(frozen=True)
class ClaimConfig:
    """Per-claim confidence tagging configuration (design move D5).

    Bands are cut on the probability that the retrieved set entails the claim.
    The information gain of a claim is 1 - H_b(q): a fully supported claim
    (q = 1) carries 1 bit of information, an unsupported one (q = 0) carries 0.
    """

    #: q >= grounded_threshold  -> "grounded"
    grounded_threshold: float = 0.80
    #: q >= inferred_threshold  -> "inferred", else "uncertain"
    inferred_threshold: float = 0.45
    nli_model: str = "cross-encoder/nli-deberta-v3-small"


@dataclass(frozen=True)
class ExperimentConfig:
    """Evaluation harness configuration."""

    #: RRF vs BM25 vs dense vs hybrid rerank.
    ablations: tuple = ("bm25_only", "dense_only", "hybrid_rrf", "hybrid_rrf_rerank")
    #: Bootstrap resamples for confidence intervals.
    n_bootstrap: int = 10_000
    #: Random seed for every stochastic component.
    seed: int = 20261118


@dataclass(frozen=True)
class Config:
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    lexical: LexicalConfig = field(default_factory=LexicalConfig)
    fusion: FusionConfig = field(default_factory=FusionConfig)
    rerank: RerankConfig = field(default_factory=RerankConfig)
    gate: GateConfig = field(default_factory=GateConfig)
    modality: ModalityQuotaConfig = field(default_factory=ModalityQuotaConfig)
    contradiction: ContradictionConfig = field(default_factory=ContradictionConfig)
    claim: ClaimConfig = field(default_factory=ClaimConfig)
    experiment: ExperimentConfig = field(default_factory=ExperimentConfig)


CONFIG = Config()
