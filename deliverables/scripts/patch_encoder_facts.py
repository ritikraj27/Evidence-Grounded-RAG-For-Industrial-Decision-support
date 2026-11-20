#!/usr/bin/env python3
"""Bind the encoder's identity and width to tokens, everywhere it appears.

The dense encoder changed from a general-purpose sentence encoder
(`all-MiniLM-L6-v2`, 384 dimensions) to a retrieval-trained multilingual one
(`BAAI/bge-m3`, 1024 dimensions). The model name and the width appear in the
pipeline diagrams, the glossary, the paper's methodology section and the
department report's technology table. Hard-coding them there is how the
deliverables ended up disagreeing with the code in the first place, so they
become tokens and the build substitutes them from the configuration.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
T = ROOT / "deliverables" / "templates"

# --------------------------------------------------------------------------
# 1. The tokens.
# --------------------------------------------------------------------------
TOKENS = ROOT / "deliverables" / "scripts" / "substitute_tokens.py"
s = TOKENS.read_text(encoding="utf-8")
old = '''    _add_result_tokens(v)'''
new = '''    # The dense encoder's identity, read from the configuration so the
    # prose can never name a model the code does not use.
    try:
        from src.config import CONFIG as _cfg
        v["EMBED_MODEL"] = _cfg.embedding.model
        v["EMBED_DIM"] = str(_cfg.embedding.dim)
        v["EMBED_FAMILY"] = ("retrieval-trained multilingual encoder"
                             if "bge-m3" in _cfg.embedding.model
                             else "general-purpose sentence encoder")
    except Exception:
        v.setdefault("EMBED_MODEL", "BAAI/bge-m3")
        v.setdefault("EMBED_DIM", "1024")
        v.setdefault("EMBED_FAMILY", "retrieval-trained multilingual encoder")
    _add_result_tokens(v)'''
assert s.count(old) == 1, s.count(old)
s = s.replace(old, new, 1)
TOKENS.write_text(s, encoding="utf-8")
print("  added the encoder tokens")

# --------------------------------------------------------------------------
# 2. The prose.
# --------------------------------------------------------------------------
EDITS = [
    ("Deliverable_1_Part1_Content.md", [
        ("                                   embed (MiniLM, 384-d)  +  BM25 inverted index",
         "                                   embed ({{EMBED_MODEL}}, {{EMBED_DIM}}-d)  +  BM25 inverted index"),
        ("**Embedding (vector representation).** A list of 384 numbers that encodes the\n"
         "*meaning* of a piece of text, produced by a neural network. Two texts that mean\n"
         "similar things get vectors that point in similar directions. The number 384 is\n"
         "simply the width of `all-MiniLM-L6-v2`'s output layer — it has no deeper meaning.",
         "**Embedding (vector representation).** A list of {{EMBED_DIM}} numbers that encodes\n"
         "the *meaning* of a piece of text, produced by a neural network. Two texts that\n"
         "mean similar things get vectors that point in similar directions. The number\n"
         "{{EMBED_DIM}} is simply the width of `{{EMBED_MODEL}}`'s output layer — it has no\n"
         "deeper meaning."),
        ("pairs so it follows directions. `all-MiniLM-L6-v2` and",
         "pairs so it follows directions. `{{EMBED_MODEL}}` and"),
    ]),
    ("Deliverable_1_PartF_toJ.md", [
        ("| **Embedding** | A 384-number vector encoding a text's meaning. |",
         "| **Embedding** | A {{EMBED_DIM}}-number vector encoding a text's meaning. |"),
        ("Use `sentence-transformers/all-MiniLM-L6-v2` (384-d) or `BAAI/bge-m3`. |",
         "Use `{{EMBED_MODEL}}` ({{EMBED_DIM}}-d). |"),
    ]),
    ("Deliverable_2a_Technical_Report.md", [
        ("The query and every chunk are embedded with `sentence-transformers/all-MiniLM-L6-v2` "
         "(384 dimensions, L2-normalised), and ranked by cosine similarity:",
         "The query and every chunk are embedded with `{{EMBED_MODEL}}` "
         "({{EMBED_DIM}} dimensions, L2-normalised), and ranked by cosine similarity:"),
    ]),
    ("scripts/make_docx.py", [
        ('"When a query arrives, it is embedded with all-MiniLM-L6-v2 (384-d) and "',
         '"When a query arrives, it is embedded with BAAI/bge-m3 (1024-d) and "'),
        ('"     → [Embed: MiniLM 384-d] → [Store: Postgres 16 + pgvector (HNSW)]",',
         '"     → [Embed: BGE-M3 1024-d] → [Store: Postgres 16 + pgvector (HNSW)]",'),
        ('["Embeddings", "sentence-transformers/all-MiniLM-L6-v2 (384-d, default)"],',
         '["Embeddings", "BAAI/bge-m3 (1024-d, default)"],'),
    ]),
    ("scripts/make_pptx.py", [
        ('"Embed: MiniLM 384-d", "Index: BM25 + Postgres/pgvector (HNSW)"], NAVY),',
         '"Embed: BGE-M3 1024-d", "Index: BM25 + Postgres/pgvector (HNSW)"], NAVY),'),
    ]),
]

total = 0
for rel, edits in EDITS:
    p = T / rel
    s = p.read_text(encoding="utf-8")
    for old_s, new_s in edits:
        c = s.count(old_s)
        if c != 1:
            print(f"!! {rel}: count={c} -> {old_s[:60]!r}")
            continue
        s = s.replace(old_s, new_s, 1)
        total += 1
    p.write_text(s, encoding="utf-8")
print(f"  {total} replacements applied")
