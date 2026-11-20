#!/usr/bin/env python3
"""Add the focus-domain case study as an appendix to the department report.

The report's §9.0 promises a worked before-and-after case study. This
appends it, rendered from the experiment's own markdown so the report and the
experiment cannot disagree.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "deliverables" / "templates" / "scripts" / "make_docx.py"

FOCUS_MD = ROOT / "impl" / "results_focus" / "exp6_focus_case.md"

APPENDIX = '''
    # ------------------------------------------------------------ APPENDIX A
    if FOCUS_CASE_MD.exists():
        page_break(doc)
        heading(doc, None, "Appendix A — Focus-Domain Case Study")
        para(doc,
             "The aggregate tables in Section 9 say what the mechanisms change. "
             "This appendix shows what they changed, on real supply-chain "
             "questions, with every intermediate artefact written out: the two "
             "retrieval legs, the fused ranking, the reranked ranking, the gate's "
             "decision and the signals behind it, the modality mix of the "
             "accepted context, how each claim was banded, and whether any two "
             "accepted chunks contradict each other. It is generated from the "
             "experiment's own output, so it cannot disagree with it.",
             align=WD_ALIGN_PARAGRAPH.JUSTIFY)
        _text = FOCUS_CASE_MD.read_text(encoding="utf-8")
        # Strip the markdown heading and render the rest as plain paragraphs;
        # the table is reproduced as monospaced rows.
        _lines = _text.splitlines()
        _skip = 0
        for _i, _ln in enumerate(_lines):
            if _ln.startswith("# "):
                _skip = _i + 1
            if _ln.startswith("## "):
                _skip = _i + 1
                break
        _body = _lines[_skip:]
        for _ln in _body:
            _s = _ln.rstrip()
            if not _s:
                continue
            if _s.startswith("### "):
                subheading(doc, None, _s[4:].strip())
            elif _s.startswith("|"):
                p = doc.add_paragraph()
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.0
                style_run(p.add_run(_s.replace("**", "")), size=Pt(8),
                          font="Consolas")
            elif _s.startswith("**") or _s.startswith("- "):
                p = doc.add_paragraph()
                p.paragraph_format.space_after = Pt(3)
                p.paragraph_format.line_spacing = 1.2
                style_run(p.add_run(_s.replace("**", "")), size=Pt(9.5))
            else:
                p = doc.add_paragraph()
                p.paragraph_format.space_after = Pt(5)
                p.paragraph_format.line_spacing = 1.25
                style_run(p.add_run(_s.replace("`", "")), size=Pt(9.5))

'''

OLD = "    doc.save(OUT)"
NEW = APPENDIX + "\n    doc.save(OUT)"


def main() -> int:
    s = TARGET.read_text(encoding="utf-8")
    if "APPENDIX A" in s:
        print("  the appendix is already wired in")
        return 0
    if OLD not in s:
        print("!! the save call not found")
        return 1
    s = s.replace(OLD, NEW, 1)
    if "FOCUS_CASE_MD =" not in s:
        s = s.replace(
            "FOCUS_BENCH = ROOT / \"impl\" / \"data\" / \"benchmark_focus\" / \"benchmark.json\"",
            "FOCUS_BENCH = ROOT / \"impl\" / \"data\" / \"benchmark_focus\" / \"benchmark.json\"\n"
            "FOCUS_CASE_MD = ROOT / \"impl\" / \"results_focus\" / \"exp6_focus_case.md\"",
            1)
    TARGET.write_text(s, encoding="utf-8")
    print("  added the focus-domain case study as Appendix A")
    return 0


if __name__ == "__main__":
    sys.exit(main())
