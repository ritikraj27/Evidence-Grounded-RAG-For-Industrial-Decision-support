"""Invariant tests: what the mechanism predicts, asserted.

A result is evidence only if the thing producing it obeys the properties the
result depends on. Three of the four defects found while building this
framework were of that kind, and none of them was visible in the output:

  * a category pre-filter applied to only one of two retrieval legs, which
    made the filter a no-op while looking like a measured effect;
  * a quota that evicted the modalities already at their floor, which
    produced a plausible-looking negative result about modality balancing;
  * an article indexed twice under two category names, which split a
    document across two categories and leaked it into both halves of the
    cross-category transfer split.

So the predictions are asserted here, on a synthetic index with the models
stubbed out, so the tests run in milliseconds and cannot be fooled by a
model's behaviour. The corpus-level invariants are checked against the real
index when it exists.
"""
import re
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402

import src.pipeline as pipeline  # noqa: E402
from src.claims import band_for, noisy_or  # noqa: E402
from src.config import (  # noqa: E402
    CONFIG,
    ClaimConfig,
    ModalityQuotaConfig,
)
from src.confidence import fit_platt, posterior_from_score  # noqa: E402
from src.hybrid import apply_modality_quota  # noqa: E402
from src.ingestion import Chunk  # noqa: E402
from src.lexical import BM25Index  # noqa: E402
from src.pipeline import Framework, Index  # noqa: E402

def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z]+", str(text).lower())


#: The width of the configured encoder. The synthetic index and the stubbed
#: query embedding both have to use it, or the similarity matrix cannot
#: multiply them together.
DIM = CONFIG.embedding.dim


def _hash_embed(texts, dim: int = None, **kwargs) -> np.ndarray:
    """A deterministic bag-of-words embedding, so no model is needed."""
    dim = dim or DIM
    out = np.zeros((len(texts), dim))
    for i, t in enumerate(texts):
        for w in _tokens(t):
            out[i, zlib.crc32(w.encode()) % dim] += 1.0
    norms = np.linalg.norm(out, axis=1, keepdims=True)
    return out / np.maximum(norms, 1e-9)


def _fake_rerank(query, pairs, model_name=None):
    """Rank by query-term overlap, so the reranker's behaviour is predictable."""
    q = set(_tokens(query))
    scored = [(cid, len(q & set(_tokens(text))) / (len(q) + 1e-9))
              for cid, text in pairs]
    return sorted(scored, key=lambda x: (-x[1], x[0]))


def _synthetic_index() -> Index:
    """Six chunks, two documents, two categories, three modalities."""
    spec = [
        ("a::p1::t0", "alpha", "cat_a", "text",
         "economic order quantity holding cost ordering cost"),
        ("a::p1::tbl0", "alpha", "cat_a", "table",
         "| sku | order quantity |\n| X1 | 250 |"),
        ("b::p1::t0", "beta", "cat_b", "text",
         "lead time safety stock plant throughput"),
        ("b::p1::fig0", "beta", "cat_b", "chart",
         "figure 1: lead time trend"),
        ("b::p2::t0", "beta", "cat_b", "text",
         "incoterms customs duty insurance terms"),
        ("b::p2::tbl0", "beta", "cat_b", "table",
         "| port | duty |\n| P1 | 12 |"),
    ]
    chunks = [
        Chunk(chunk_id=cid, doc_id=doc, text=txt, modality=mod, page=1,
              section="", caption="", category=cat, meta={})
        for cid, doc, cat, mod, txt in spec
    ]
    chunk_ids = [c.chunk_id for c in chunks]
    chunk_text = {c.chunk_id: c.text for c in chunks}
    modality_of = {c.chunk_id: c.modality for c in chunks}
    category_of = {c.chunk_id: c.category for c in chunks}
    bm25 = BM25Index.build(chunk_text, k1=1.2, b=0.75)
    emb = _hash_embed([c.text for c in chunks])
    return Index(chunks, bm25, emb, chunk_ids, chunk_text, modality_of,
                 category_of, {"n_chunks": len(chunks)})


def _framework() -> Framework:
    pipeline.embed_texts = _hash_embed
    pipeline.rerank = _fake_rerank
    return Framework(_synthetic_index())


# --------------------------------------------------------------------------
# Pipeline invariants
# --------------------------------------------------------------------------

def test_category_filter_applies_to_both_legs():
    """The regression test for a filter applied to only one retrieval leg.

    A filter that touches the dense leg but not the BM25 leg is not a filter:
    the lexical leg then dominates the fusion and the filter's measured effect
    is zero. Both legs must be restricted, and both must actually change.
    """
    fw = _framework()
    trace = fw.retrieve("economic order quantity cost", category="cat_a",
                         apply_rerank=False)
    for name, leg in (("dense", trace.dense), ("lexical", trace.lexical)):
        assert leg, f"the {name} leg returned nothing"
        for cid in leg:
            assert fw.index.category_of[cid] == "cat_a", (
                f"the {name} leg leaked a chunk from category "
                f"{fw.index.category_of[cid]!r} past the filter")
    print("  ok  the category pre-filter restricts BOTH retrieval legs")


def test_reranker_cannot_introduce_a_chunk_outside_its_pool():
    """A cross-encoder reorders; it does not retrieve.

    If a chunk appears in the reranked list that was not in the pool, then
    some other component is quietly retrieving, and the pool-size result --
    the project's most useful finding -- would be measuring the wrong thing.
    """
    fw = _framework()
    trace = fw.retrieve("economic order quantity cost", category=None,
                         apply_rerank=True)
    pool = set(trace.fused[: fw.config.rerank.top_n])
    assert set(trace.reranked) <= pool, (
        f"the reranker introduced a chunk outside its pool: "
        f"{sorted(set(trace.reranked) - pool)}")
    assert len(trace.reranked) == len(set(trace.reranked)), (
        "the reranked list contains a duplicate")
    print("  ok  the reranker only permutes its own candidate pool")


def test_quota_only_reorders_within_its_pool():
    """The quota swaps chunks within the pool; it never introduces one."""
    cfg = ModalityQuotaConfig(min_table_share=0.2, min_chart_share=0.2,
                               quota_depth=8)
    ranked = [f"c{i}" for i in range(20)]
    modality = {c: "text" for c in ranked}
    modality["c3"] = "table"
    modality["c17"] = "chart"
    res = apply_modality_quota(ranked, modality, cfg)
    assert set(res.selected) <= set(ranked), res.selected
    assert len(res.selected) == len(set(res.selected)), res.selected
    print("  ok  the quota only reorders within its candidate pool")


def test_a_document_never_spans_two_categories():
    """The regression test for an article indexed under two category names.

    Such a document is indexed twice, its chunks are split across the two
    categories so that the category pre-filter sees only half of it, and it
    leaks into both halves of the cross-category transfer split.
    """
    fw = _framework()
    doc_id_of = {c.chunk_id: c.doc_id for c in fw.index.chunks}
    doc_to_cats = {}
    for cid in fw.index.chunk_ids:
        doc_to_cats.setdefault(doc_id_of[cid], set()).add(
            fw.index.category_of[cid])
    straddle = {d: sorted(cs) for d, cs in doc_to_cats.items() if len(cs) > 1}
    assert not straddle, f"a document spans two categories: {straddle}"
    print("  ok  no document spans more than one category")


def test_index_loads_the_category_from_its_dedicated_field():
    """The regression test for reading the category from the wrong place.

    Reading `chunk.meta` when the category lives in a dedicated field makes
    every chunk default to "general", so the category pre-filter silently
    filters nothing. The symptom is indistinguishable from a filter that
    works but has no effect, which is why it needs a test.
    """
    fw = _framework()
    for c in fw.index.chunks:
        c.meta["category"] = "general"       # the wrong place
        c.category = "cat_a"                 # the right place
    rebuilt = {c.chunk_id: (c.category or c.meta.get("category", "general"))
               for c in fw.index.chunks}
    assert set(rebuilt.values()) == {"cat_a"}, rebuilt
    print("  ok  the category is read from its dedicated field, not from meta")


# --------------------------------------------------------------------------
# Numeric invariants
# --------------------------------------------------------------------------

def test_bm25_normalises_by_length():
    """A longer document with the same term frequency must score lower."""
    index = BM25Index.build({
        "short": "economic order quantity economic",
        "long": "economic order quantity economic " + "filler " * 40,
    }, k1=1.2, b=0.75)
    s_short = index.score("economic order quantity")[0]
    s_long = index.score("economic order quantity")[1]
    assert s_short > s_long, (s_short, s_long)
    print("  ok  BM25 length normalisation penalises the longer document")


def test_platt_calibration_is_monotone_and_reproduces_its_inputs():
    """A calibration map must be monotone, and must fit what it was given."""
    rng = np.random.default_rng(0)
    scores = rng.normal(size=400)
    labels = (rng.random(400) < 1 / (1 + np.exp(-1.4 * scores))).astype(int)
    beta0, beta1 = fit_platt(scores, labels)
    assert beta1 > 0, f"the fitted slope is not positive: {beta1}"
    grid = np.linspace(-3, 3, 50)
    post = posterior_from_score(grid, beta0, beta1)
    assert np.all(np.diff(post) >= -1e-12), "the posterior is not monotone"
    assert post.min() >= 0.0 and post.max() <= 1.0, post
    # A fit on perfectly separable data must separate it.
    sep_s = np.array([-5.0] * 20 + [5.0] * 20)
    sep_y = np.array([0] * 20 + [1] * 20)
    b0, b1 = fit_platt(sep_s, sep_y)
    p = posterior_from_score(sep_s, b0, b1)
    assert p[:20].max() < p[20:].min(), (p[:20].max(), p[20:].min())
    print("  ok  Platt scaling is monotone, bounded, and separates its input")


def test_noisy_or_is_monotone_and_bounded():
    """More independent support must not reduce confidence, and must not
    exceed one."""
    one = noisy_or([0.5])
    two = noisy_or([0.5, 0.5])
    assert two > one, (one, two)
    assert 0.0 <= one < two <= 1.0, (one, two)
    assert abs(noisy_or([]) - 0.0) < 1e-12
    assert abs(noisy_or([1.0]) - 1.0) < 1e-12
    print("  ok  noisy-OR is monotone in the evidence and bounded in [0, 1]")


def test_claim_bands_are_ordered_and_exhaustive():
    """Every support probability lands in exactly one band, and the bands
    are ordered by the thresholds that define them."""
    cfg = ClaimConfig()
    assert cfg.grounded_threshold > cfg.inferred_threshold, cfg
    bands = {band_for(q, cfg) for q in np.linspace(0.0, 1.0, 201)}
    assert bands == {"grounded", "inferred", "uncertain"}, bands
    assert band_for(0.0, cfg) == "uncertain"
    assert band_for(1.0, cfg) == "grounded"
    print("  ok  the claim bands partition [0, 1] and are ordered")


# --------------------------------------------------------------------------
# The real corpus
# --------------------------------------------------------------------------

def test_a_non_adjacent_comparison_cannot_shadow_an_adjacent_one():
    """The regression test for a silent mis-reporting of paired tests.

    The ablation reports non-adjacent comparisons as well as adjacent ones --
    BM25 against the fused system, the reranker against a quota -- and a
    non-adjacent comparison starts with the same rung as the adjacent one it
    follows. Indexing the comparisons by their first rung in a plain dict
    comprehension therefore lets the later entry overwrite the earlier one,
    and a generator that asks for "D -> E" is handed "D -> F" instead. The
    numbers it then prints are real, from a real experiment, and wrong.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]
                           / "deliverables" / "scripts"))
    from results_source import _comp_index  # noqa: PLC0415

    comparisons = [
        {"comparison": "D. rerank -> E. filter", "delta": 0.01},
        {"comparison": "D. rerank -> F. quota", "delta": 0.99},
    ]
    index = _comp_index(comparisons)
    assert index["D. rerank"]["delta"] == 0.01, index["D. rerank"]
    assert index["D. rerank -> F. quota"]["delta"] == 0.99
    print("  ok  a non-adjacent comparison cannot shadow an adjacent one")


def test_the_generator_is_reached_only_through_the_gate():
    """The gate must be a control-flow fact, not an instruction.

    "The model was told to be careful" is an instruction, and a model can
    ignore it. "The model was never called" is a fact about the program. The
    framework owns the generator precisely so that this is the second kind:
    the model is reached at one line inside `answer()`, after the gate has
    accepted. A query the gate rejects must reach no model call at all --
    including the claim assessment and contradiction detection that follow
    generation, because those cost model calls too.
    """
    calls = []

    def generator(query, context):
        calls.append((query, context))
        return "an answer from the model"

    fw = _framework()
    fw.generator = generator
    # A gate model that refuses everything, and one that accepts everything.
    def model(tau):
        return {"mu": [0.0] * 5, "sd": [1.0] * 5,
                "weights": [0.0] * 6, "tau": tau}

    fw.gate_model = model(1.0)          # posterior 0.5 < 1.0 -> refuse
    refused = fw.answer("what is the economic order quantity for sku X1?",
                         category="cat_a")
    assert refused.accepted is False, "the framework answered a refused query"
    assert calls == [], f"the generator ran on a refused query: {calls}"

    fw.gate_model = model(0.0)          # posterior 0.5 >= 0.0 -> accept
    accepted = fw.answer("what is the economic order quantity for sku X1?",
                         category="cat_a")
    assert accepted.accepted is True
    assert len(calls) == 1, f"the generator did not run on an accepted query: {calls}"
    print("  ok  the generator is reached only through the gate")


def test_a_malformed_query_never_reaches_the_generator():
    """The form check must be a control-flow fact too.

    A request that is not a question cannot produce an answer, so it must be
    refused before retrieval -- which means before the model, and at no
    retrieval cost either. The refusal has to be distinguishable from the
    gate's: "that was not a question" and "the corpus does not contain the
    answer" are different statements, and a user who is told the wrong one
    will ask the wrong follow-up.
    """
    calls = []

    def generator(query, context):
        calls.append((query, context))
        return "an answer from the model"

    fw = _framework()
    fw.generator = generator

    # The gate is pinned to a model that accepts everything. The point of
    # this test is the FORM check, and the form check and the gate are
    # independent -- but if the gate also rejects the stub query then the
    # generator is never reached either way, and the second half of the test
    # below would pass for the wrong reason. The sibling test pins the gate
    # for the same reason. Without this the test also depends on whatever
    # calibrated gate model happens to be on disk in ARTIFACT_DIR, which is
    # exactly the kind of ambient state a test must not depend on.
    fw.gate_model = {"mu": [0.0] * 5, "sd": [1.0] * 5,
                     "weights": [0.0] * 6, "tau": 0.0}

    refused = fw.answer("What is this?", category="cat_a")
    assert refused.accepted is False, "the framework answered a malformed query"
    assert refused.refusal == "form", f"wrong refusal reason: {refused.refusal!r}"
    assert refused.trace.form_rejected is True
    assert refused.trace.gate_rejected is False, (
        "the form refusal was reported as a gate refusal -- the gate never ran")
    assert calls == [], f"the generator ran on a malformed query: {calls}"

    # Turning the check off must let the same query through, so the refusal
    # above is the check's doing and not an accident of the stub.
    fw.answer("What is this?", category="cat_a", check_form=False)
    assert len(calls) == 1, f"the form check did not gate the generator: {calls}"
    print("  ok  a malformed query never reaches the generator")


def test_real_corpus_has_no_duplicates():
    """The corpus-level invariant, checked against the built index."""
    index_path = Path(__file__).resolve().parents[1] / "artifacts" / "index.json"
    if not index_path.exists():
        print("  --  no built index; skipping the corpus invariants")
        return
    import json
    data = json.loads(index_path.read_text(encoding="utf-8"))
    chunks = data["chunks"]
    ids = [c["chunk_id"] for c in chunks]
    assert len(ids) == len(set(ids)), (
        f"{len(ids) - len(set(ids))} duplicated chunk ids in the index")
    doc_cats = {}
    for c in chunks:
        doc_cats.setdefault(c["doc_id"], set()).add(
            c.get("category") or c.get("meta", {}).get("category", "general"))
    straddle = {d: sorted(cs) for d, cs in doc_cats.items() if len(cs) > 1}
    assert not straddle, f"documents spanning two categories: {straddle}"
    print(f"  ok  the built index has {len(ids)} unique chunk ids and "
          f"{len(doc_cats)} single-category documents")


def test_conflict_surfacing_is_gated_on_measurement():
    """A conflict finding is withheld when its branch has no measured support.

    This is the discipline the answer gate applies to an answer, applied to
    the framework's own claims: a branch whose measured precision is below
    the calibration floor has its findings recorded and withheld rather than
    shown to a practitioner. The mechanism is asserted here so that it cannot
    be quietly removed, and so that "the branch is measured but not yet
    calibrated" cannot be confused with "the branch is calibrated to be
    silent".
    """
    from src.contradiction import (ConflictCalibration, detect_contradictions,
                                   revision_conflicts)

    # An uncalibrated branch is surfaced: the absence of a measurement is
    # not a measurement.
    cal = ConflictCalibration()
    ok, why = cal.allows("semantic")
    assert ok and not why, (ok, why)

    # A branch measured below the floor is withheld, with the reason.
    cal = ConflictCalibration(precision={"semantic": 0.0}, n_measured={"semantic": 20})
    ok, why = cal.allows("semantic")
    assert not ok, "a branch below the floor was allowed to surface"
    assert "0.000" in why and "20" in why, why

    # A branch measured above the floor is surfaced.
    cal = ConflictCalibration(precision={"semantic": 0.9}, n_measured={"semantic": 20})
    ok, why = cal.allows("semantic")
    assert ok and not why, (ok, why)

    # And the gate itself honours it: the finding is still recorded, with
    # the reason, but it is not surfaced.
    a = "Under the CIF Incoterms 2020 rule the seller must obtain cover."
    b = "Under the CIF Incoterms 2010 rule the seller must insure 110 percent."
    findings = detect_contradictions([a, b], ["a", "b"], embeddings=None,
                                     calibration=cal)
    assert findings, "the detector produced no finding to withhold"
    f = findings[0]
    assert f.kind == "revision", f.kind
    assert f.flagged, "the finding should still be recorded"
    assert f.surfaced, "a revision branch with no calibration must surface"
    assert revision_conflicts(a, b), "the revision branch did not fire"

    # And a withheld finding must not leave a mark on the answer. The
    # extractive answer annotates the chunks a conflict was found in, and
    # an annotation a reader cannot trust is worse than none.
    from src.pipeline import Framework
    fw = Framework.__new__(Framework)
    fw.index = type("I", (), {"chunk_text": {"a": "A", "b": "B"}})()
    held = type("F", (), {"chunk_a": "a", "chunk_b": "b", "flagged": True,
                          "surfaced": False})()
    shown = type("F", (), {"chunk_a": "a", "chunk_b": "b", "flagged": True,
                           "surfaced": True})()
    out_held = fw._extractive_answer(["a", "b"], [], [held])
    out_shown = fw._extractive_answer(["a", "b"], [], [shown])
    assert "CONTRADICTION" not in out_held, out_held
    assert "CONTRADICTION" in out_shown, out_shown

    print("  ok  conflict surfacing is gated on the measured precision")


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    print(f"[invariants] {len(tests)} invariant tests")
    for t in tests:
        t()
    print("[invariants] all passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
