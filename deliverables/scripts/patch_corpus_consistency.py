#!/usr/bin/env python3
"""Make the encoder before/after quote one corpus throughout.

The deliverables report the focus domain, so the "before" numbers in the
prose must be the focus domain's "before" numbers. The text was mixing the
multi-category baseline with the focus domain's "after" numbers, which is
the kind of comparison that looks reasonable and means nothing.

The verdict token had the same fault; it now reads the focus baseline.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# --------------------------------------------------------------------------
# 1. The verdict token reads the focus baseline.
# --------------------------------------------------------------------------
p = ROOT / "deliverables" / "scripts" / "substitute_tokens.py"
s = p.read_text(encoding="utf-8")
old = '''    before_gap = num("BASE_MC_R_A") - num("BASE_MC_R_B")
    after_gap = num("R_A") - num("R_B")
    before_order = num("BASE_MC_NDCG_A") - num("BASE_MC_NDCG_C")
    after_order = num("NDCG_A") - num("NDCG_C")'''
new = '''    before_gap = num("BASE_F_R_A") - num("BASE_F_R_B")
    after_gap = num("R_A") - num("R_B")
    before_order = num("BASE_F_NDCG_A") - num("BASE_F_NDCG_C")
    after_order = num("NDCG_A") - num("NDCG_C")'''
assert s.count(old) == 1, s.count(old)
s = s.replace(old, new, 1)

old2 = '''    if "R_B" in v and "BASE_MC_R_B" in v:'''
new2 = '''    if "R_B" in v and "BASE_F_R_B" in v:'''
assert s.count(old2) == 1
s = s.replace(old2, new2, 1)
p.write_text(s, encoding="utf-8")
print("  the verdict token reads the focus baseline")

# --------------------------------------------------------------------------
# 2. The guide's Section C.3 quotes the focus baseline throughout.
# --------------------------------------------------------------------------
p = ROOT / "deliverables" / "templates" / "Deliverable_1_Part1_Content.md"
s = p.read_text(encoding="utf-8")
for old_t, new_t in (
    ("{{BASE_MC_R_B}} against plain BM25's {{BASE_MC_R_A}} (paired Wilcoxon,\n"
     "p = {{BASE_MC_P_AB}}), and the fused system's ordering was *worse* than the\n"
     "lexical leg's — nDCG@10 {{BASE_MC_NDCG_C}} against {{BASE_MC_NDCG_A}}.",
     "{{BASE_F_R_B}} against plain BM25's {{BASE_F_R_A}} (paired Wilcoxon,\n"
     "p = {{BASE_F_P_AB}}), and the fused system's ordering was *worse* than the\n"
     "lexical leg's — nDCG@10 {{BASE_F_NDCG_C}} against {{BASE_F_NDCG_A}}."),
):
    assert s.count(old_t) == 1, s.count(old_t)
    s = s.replace(old_t, new_t, 1)
p.write_text(s, encoding="utf-8")
print("  the guide's C.3 quotes the focus baseline")

# --------------------------------------------------------------------------
# 3. The guide's results generator: Finding 1 and the baseline variables.
# --------------------------------------------------------------------------
p = ROOT / "deliverables" / "scripts" / "make_results_md.py"
s = p.read_text(encoding="utf-8")
old3 = '''    _b = json.loads(_bp.read_text(encoding="utf-8"))["multi_category"]'''
new3 = '''    _b = json.loads(_bp.read_text(encoding="utf-8"))["focus"]'''
assert s.count(old3) == 1
s = s.replace(old3, new3, 1)
p.write_text(s, encoding="utf-8")
print("  the guide's results generator reads the focus baseline")

# --------------------------------------------------------------------------
# 4. The README quotes the focus baseline throughout.
# --------------------------------------------------------------------------
p = ROOT / "README.md"
s = p.read_text(encoding="utf-8")
old4 = """dense-only retrieval reached Recall@10 {{BASE_MC_R_B}} against plain BM25's
{{BASE_MC_R_A}} (p = {{BASE_MC_P_AB}}), and the fusion's ordering was *worse* than
the lexical leg's — the fusion was spending the lexical leg's slots on the
dense leg's worse candidates. Replacing it with a retrieval-trained encoder
(`{{EMBED_MODEL}}`) moved the dense leg to {{R_B}} and cut that ordering deficit
from {{BASE_MC_NDCG_A}} - {{BASE_MC_NDCG_C}} to {{NDCG_A}} - {{NDCG_C}}. The"""
new4 = """dense-only retrieval reached Recall@10 {{BASE_F_R_B}} against plain BM25's
{{BASE_F_R_A}} (p = {{BASE_F_P_AB}}), and the fusion's ordering was *worse* than
the lexical leg's — the fusion was spending the lexical leg's slots on the
dense leg's worse candidates. Replacing it with a retrieval-trained encoder
(`{{EMBED_MODEL}}`) moved the dense leg to {{R_B}} and cut that ordering deficit
from {{BASE_F_NDCG_A}} - {{BASE_F_NDCG_C}} to {{NDCG_A}} - {{NDCG_C}}. The"""
assert s.count(old4) == 1, s.count(old4)
s = s.replace(old4, new4, 1)
p.write_text(s, encoding="utf-8")
print("  the README quotes the focus baseline")
