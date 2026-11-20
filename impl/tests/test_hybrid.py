"""Tests for the rank-fusion and quota logic.

Run with:  .venv/bin/python impl/tests/test_hybrid.py

These are the two places where an inverted condition silently produces
plausible-looking but wrong numbers, so they are pinned down explicitly.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import ModalityQuotaConfig
from src.hybrid import apply_modality_quota, reciprocal_rank_fusion


def test_rrf_prefers_agreement():
    dense = ["a", "b", "c"]
    lexical = ["b", "a", "d"]
    scores = reciprocal_rank_fusion([dense, lexical], k=60)
    assert scores["a"] > scores["c"], scores
    assert scores["b"] > scores["d"], scores
    assert abs(scores["a"] - scores["b"]) < 1e-9, scores
    print("  ok  RRF rewards agreement")


def test_rrf_is_scale_free():
    a = reciprocal_rank_fusion([["x", "y"]], k=60)
    b = reciprocal_rank_fusion([["x", "y"]], k=60)
    assert a == b
    print("  ok  RRF depends only on ranks")


def test_quota_does_not_evict_a_modality_at_its_floor():
    """The regression test for the inverted condition.

    The natural top-10 holds one table. The quota also wants a chart. With a
    table floor of 1 the table is AT its floor and must be kept, so the chart
    has to be added without removing it.
    """
    cfg = ModalityQuotaConfig(min_table_share=0.10, min_chart_share=0.10,
                              quota_depth=5)
    ranked = ([f"t{i}" for i in range(9)] + ["tableA"] + ["chartX"]
              + ["t9", "t10"])
    modality = {c: ("table" if c == "tableA" else
                    "chart" if c == "chartX" else "text") for c in ranked}
    res = apply_modality_quota(ranked, modality, cfg)
    assert "tableA" in res.selected, (
        "the table was evicted even though it was at its floor: "
        f"{res.selected}")
    assert "chartX" in res.selected, (
        f"the chart was not added: {res.selected}")
    print("  ok  the quota never evicts a modality that is at its floor")


def test_quota_reports_shortfall():
    cfg = ModalityQuotaConfig(min_table_share=0.30, min_chart_share=0.30)
    ranked = [f"t{i}" for i in range(20)]
    modality = {c: "text" for c in ranked}
    res = apply_modality_quota(ranked, modality, cfg)
    assert not res.quotas_met
    assert "not met" in res.note
    print("  ok  an unsatisfiable quota is reported, not silently ignored")


if __name__ == "__main__":
    print("=== hybrid tests ===")
    test_rrf_prefers_agreement()
    test_rrf_is_scale_free()
    test_quota_does_not_evict_a_modality_at_its_floor()
    test_quota_reports_shortfall()
    print("all hybrid tests passed")
