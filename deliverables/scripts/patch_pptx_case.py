#!/usr/bin/env python3
"""Add the focus-domain before/after slide to the deck.

The ablation table says the mechanisms change recall. This slide shows one
supply-chain question, before and after, so a panel member can see what
changed: what the plain lexical retriever returned, what the full framework
returned instead, what the gate decided and why, and how each claim in the
answer was banded.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "deliverables" / "templates" / "scripts" / "make_pptx.py"

LOADER = '''
def _load_focus(name: str) -> dict | None:
    """Load a result file from the focus-domain (supply chain) run."""
    p = ROOT / "impl" / "results_focus" / f"{name}.json"
    if not p.exists():
        return None
    try:
        payload = json.loads(p.read_text())
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


'''

SLIDE = '''
# ================================================================ SLIDE 12b
_focus = _load_focus("exp6_focus_case")
s = base_slide("One Question, Before and After",
               "The focus domain — a supply-chain question traced through every stage",
               nxt())
if _focus and _focus.get("traces"):
    _traces = _focus["traces"]
    # Prefer a question the plain retriever got wrong and the framework got
    # right: that is the case where the mechanisms visibly did something.
    _t = next((x for x in _traces
               if not x["before"]["gold_in_top10"] and x["after"]["gold_in_accepted"]),
              None)
    if _t is None:
        _t = next((x for x in _traces if x["after"]["gold_in_accepted"]), _traces[0])
    _summ = _focus.get("summary", {})

    tb, tf = textbox(s, Inches(0.55), Inches(1.02), Inches(12.23), Inches(0.42))
    para(tf, f"\\u201c{_t['query']}\\u201d", size=13.5, bold=True, color=NAVY,
         first=True, space_after=0)

    # ---- BEFORE -------------------------------------------------------
    rect(s, Inches(0.55), Inches(1.52), Inches(5.95), Inches(3.55), LIGHT,
         line=RGBColor(0xD5, 0xDB, 0xE5))
    tb, tf = textbox(s, Inches(0.78), Inches(1.68), Inches(5.5), Inches(3.3))
    para(tf, "BEFORE  \\u2014  plain BM25, no rerank, no gate", size=11.5,
         bold=True, color=MUTED, first=True, space_after=6)
    for _c in _t["before"]["chunks"][:4]:
        _mark = "  \\u2190 GOLD" if _c["is_gold"] else ""
        rich(tf, [(f"[{_c['modality']}] ", False, MUTED),
                  (_c["preview"][:120], False, INK)], size=10.5, space_after=4)
        if _mark:
            rich(tf, [(_mark, True, ACCENT)], size=10.5, space_after=6)
    rich(tf, [("Gold chunk found in top 10: ", True, NAVY),
              ("yes" if _t["before"]["gold_in_top10"] else "NO", True,
               GREEN if _t["before"]["gold_in_top10"] else ACCENT)],
         size=11, space_after=0)

    # ---- AFTER --------------------------------------------------------
    rect(s, Inches(6.85), Inches(1.52), Inches(5.93), Inches(3.55),
         RGBColor(0xF2, 0xF6, 0xFB), line=RGBColor(0xB9, 0xC7, 0xDC))
    tb, tf = textbox(s, Inches(7.08), Inches(1.68), Inches(5.47), Inches(3.3))
    para(tf, "AFTER  \\u2014  the full framework", size=11.5, bold=True,
         color=ACCENT, first=True, space_after=6)
    for _c in _t["after"]["chunks"][:4]:
        _mark = "  \\u2190 GOLD" if _c["is_gold"] else ""
        rich(tf, [(f"[{_c['modality']}] ", False, MUTED),
                  (_c["preview"][:120], False, INK)], size=10.5, space_after=4)
        if _mark:
            rich(tf, [(_mark, True, GREEN)], size=10.5, space_after=6)
    _pt = _t["after"].get("posterior_top")
    _mc = _t["after"].get("modality_counts") or {}
    rich(tf, [("Gate: ", True, NAVY),
              ("REFUSED \\u2014 no evidence in the context" if _t["after"]["gate_rejected"]
               else f"answered (posterior {_pt:.3f})" if _pt is not None else "answered",
               True, MUTED)], size=11, space_after=3)
    rich(tf, [("Context: ", True, NAVY),
              (f"{len(_t['after']['accepted'])} chunks, " +
               ", ".join(f"{k} {v}" for k, v in _mc.items()), False, INK)],
         size=11, space_after=0)

    # ---- THE ANSWER ----------------------------------------------------
    rect(s, Inches(0.55), Inches(5.25), Inches(12.23), Inches(1.72), WHITE,
         line=RGBColor(0xD5, 0xDB, 0xE5))
    tb, tf = textbox(s, Inches(0.78), Inches(5.38), Inches(11.8), Inches(1.5))
    para(tf, "THE ANSWER, WITH EVERY CLAIM BANDED", size=11, bold=True,
         color=ACCENT, first=True, space_after=5)
    _claims = _t["answer"]["claims"][:3]
    if _claims:
        for _c in _claims:
            _band = (_c.get("band") or "?").upper()
            _col = {"GROUNDED": GREEN, "INFERRED": ACCENT}.get(_band, MUTED)
            rich(tf, [(f"[{_band}] ", True, _col),
                      ((_c.get("claim") or "")[:150], False, INK)],
                 size=11, space_after=3)
    else:
        para(tf, "The gate refused this question, so no claim was made.", size=11,
             color=MUTED, space_after=0)
    notes(s, "This is one real supply-chain question, and it is the slide I would "
             "go to if the panel asked whether any of this actually works.\\n\\n"
             "On the left is what a plain keyword retriever returned. On the right "
             "is what the framework returned instead: the fused ranking, the "
             "reranked ranking, the context the gate was willing to accept, and "
             "the modality mix of that context.\\n\\n"
             "The point is not that the answer is longer. The point is that every "
             "sentence in the answer is attached to a chunk, every chunk is in the "
             "context the gate accepted, and every claim carries a band saying "
             "whether it is grounded, inferred, or uncertain. A practitioner can "
             "check it. That is the whole thesis.\\n\\n"
             "The full case study, with every stage of several questions, is in "
             "the appendix of the written report.")
else:
    tb, tf = textbox(s, Inches(0.55), Inches(2.0), Inches(12.0), Inches(1.5))
    para(tf, "Focus-domain case study not yet generated", size=18, color=MUTED,
         first=True)

'''

ANCHOR = "# ================================================================ SLIDE 13"


def main() -> int:
    s = TARGET.read_text(encoding="utf-8")
    if "SLIDE 12b" in s:
        print("  the case-study slide is already present")
        return 0
    if ANCHOR not in s:
        print("!! anchor not found")
        return 1
    s = s.replace(ANCHOR, SLIDE.strip("\n") + "\n\n" + ANCHOR, 1)
    if "def _load_focus" not in s:
        s = s.replace("exp1 = _load(\"exp1_ablation\"",
                      LOADER.strip("\n") + "\nexp1 = _load(\"exp1_ablation\"", 1)
    TARGET.write_text(s, encoding="utf-8")
    print("  added the focus-domain before/after slide to the deck")
    return 0


if __name__ == "__main__":
    sys.exit(main())
