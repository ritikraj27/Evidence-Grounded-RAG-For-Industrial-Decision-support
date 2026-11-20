#!/usr/bin/env python3
"""Rebuild every deliverable from source.

Order matters: the guide's Part E is generated from the experiment JSON, then
spliced into the guide; the department report and the presentation both read
the same JSON, so they cannot disagree.

    python3 deliverables/scripts/build_all.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DELIV = ROOT / "deliverables"
PY = str(ROOT / ".venv" / "bin" / "python")

GUIDE_PART1 = DELIV / "Deliverable_1_Part1_Content.md"
GUIDE_PARTE = DELIV / "Deliverable_1_PartE_Results.md"
GUIDE_PARTD = DELIV / "Deliverable_1_PartD_Code.md"
GUIDE_PARTFJ = DELIV / "Deliverable_1_PartF_toJ.md"
GUIDE_FINAL = DELIV / "Deliverable_1_Complete_Guide.md"


def run(cmd, *, label):
    print(f"\n=== {label} ===", flush=True)
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    for line in out.splitlines():
        if line.strip() and not line.startswith("Warning"):
            print("  " + line)
    if r.returncode != 0:
        print(f"  !! FAILED (exit {r.returncode})")
        return False
    return True


TEMPLATES = DELIV / "templates"

#: Source files restored from the pristine templates before each build. The
#: templates carry tokens such as {{N_QUERIES}}; the build substitutes the
#: measured values into the working copies, so the prose can never drift from
#: the measurements and the templates stay pristine.
RESTORED = [
    (TEMPLATES / "README.md", ROOT / "README.md"),
    (TEMPLATES / "READ_ME_FIRST.md", DELIV / "READ_ME_FIRST.md"),
    (TEMPLATES / "Deliverable_1_Part1_Content.md", DELIV / "Deliverable_1_Part1_Content.md"),
    (TEMPLATES / "Deliverable_1_PartD_Code.md", DELIV / "Deliverable_1_PartD_Code.md"),
    (TEMPLATES / "Deliverable_1_PartF_toJ.md", DELIV / "Deliverable_1_PartF_toJ.md"),
    (TEMPLATES / "Deliverable_2a_Technical_Report.md", DELIV / "Deliverable_2a_Technical_Report.md"),
    (TEMPLATES / "Deliverable_2b_IEEE_Conference_Paper.tex", DELIV / "Deliverable_2b_IEEE_Conference_Paper.tex"),
    (TEMPLATES / "Deliverable_2c_Journal_Style_Paper.tex", DELIV / "Deliverable_2c_Journal_Style_Paper.tex"),
    (TEMPLATES / "scripts" / "make_pptx.py", DELIV / "scripts" / "make_pptx.py"),
    (TEMPLATES / "scripts" / "make_docx.py", DELIV / "scripts" / "make_docx.py"),
    (TEMPLATES / "MTP_Status_Report.md", DELIV / "MTP_Status_Report.md"),
    (TEMPLATES / "MTP_Technical_Documentation.md",
     DELIV / "MTP_Technical_Documentation.md"),
    (TEMPLATES / "MTP_Plain_Language_Guide.md",
     DELIV / "MTP_Plain_Language_Guide.md"),
]


def restore_templates() -> None:
    for src, dst in RESTORED:
        if src.exists():
            dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


def main() -> int:
    ok = True

    # 0. Unit tests, then restore the tokenised sources and substitute the
    #    measured values
    ok &= run([PY, "impl/tests/test_hybrid.py"], label="Unit tests: fusion & quota")
    ok &= run([PY, "impl/tests/test_confidence_and_claims.py"],
              label="Unit tests: gate & claims")
    ok &= run([PY, "impl/tests/test_query_form.py"],
              label="Unit tests: the query-form check")
    ok &= run([PY, "impl/tests/test_invariants.py"],
              label="Invariant tests: the mechanism's predictions")

    restore_templates()
    ok &= run([PY, "deliverables/scripts/substitute_tokens.py"],
              label="Substitute measured values into the prose")

    # 1. Results section of the guide, from the experiment JSON
    ok &= run([PY, "deliverables/scripts/make_results_md.py"], label="Guide Part E")

    # 2. Splice the guide: Part 1 + Part E + Part 2.
    #    Part E is generated from the measured JSON, so the guide always
    #    reports what the experiments produced.
    parts = [GUIDE_PART1, GUIDE_PARTD, GUIDE_PARTE, GUIDE_PARTFJ]
    if all(p.exists() for p in parts):
        texts = [p.read_text(encoding="utf-8") for p in parts]
        GUIDE_FINAL.write_text("\n".join(t.rstrip() for t in texts) + "\n",
                               encoding="utf-8")
        print(f"\n[guide] assembled {GUIDE_FINAL.name} "
              f"({sum(len(t) for t in texts):,} chars) from "
              f"{[p.name for p in parts]}")

    # 3. The paper's Results section, rewritten from the measured JSON
    ok &= run([PY, "deliverables/scripts/make_tex_results.py"],
              label="LaTeX result tables")
    ok &= run([PY, "deliverables/scripts/make_tex_prose.py"],
              label="LaTeX results prose")
    ok &= run([PY, "deliverables/scripts/make_tex_industrial.py"],
              label="LaTeX second-corpus section")
    ok &= run([PY, "deliverables/scripts/make_paper_results.py"],
              label="Paper Section 5 (results)")

    # 4. Paper and guide as DOCX
    ok &= run([PY, "deliverables/scripts/md_to_docx.py",
               "deliverables/Deliverable_2a_Technical_Report.md",
               "deliverables/Deliverable_2a_Technical_Report.docx"],
              label="Deliverable 2a -> DOCX")
    ok &= run([PY, "deliverables/scripts/md_to_docx.py",
               "deliverables/Deliverable_1_Complete_Guide.md",
               "deliverables/Deliverable_1_Complete_Guide.docx"],
              label="Deliverable 1 -> DOCX")

    # 5. Department report DOCX
    ok &= run([PY, "deliverables/scripts/make_docx.py"], label="Deliverable 3 (DOCX)")

    # 6. Presentation
    ok &= run([PY, "deliverables/scripts/make_pptx.py"], label="Deliverable 4 (PPTX)")

    # 6a. The fresh thesis report and defence deck, written from scratch for
    #     the 18 November defence. Both read the same measured-value table as
    #     everything else, so they cannot disagree with the other deliverables
    #     or with each other.
    ok &= run([PY, "deliverables/scripts/make_thesis_report.py"],
              label="Fresh thesis report (DOCX + PDF)")
    # The page numbers in the contents can only be computed by Word, which is
    # the engine that will lay the document out.
    ok &= run([PY, "deliverables/scripts/update_toc_pages.py"],
              label="Contents: the page numbers, computed by Word")
    ok &= run([PY, "deliverables/scripts/make_thesis_deck.py"],
              label="Fresh defence deck (PPTX)")
    # 6a-2. The ten-minute deck, for the slot the defence actually has. It
    #     carries every figure, table and formula the report uses, and the
    #     speaker script that goes with it.
    ok &= run([PY, "deliverables/scripts/make_defence_deck.py"],
              label="Ten-minute defence deck (PPTX)")
    ok &= run([PY, "deliverables/scripts/md_to_docx.py",
               "deliverables/MTP_Defence_Deck_Script.md",
               "deliverables/MTP_Defence_Deck_Script.docx"],
              label="Ten-minute deck: the speaker script (DOCX)")
    ok &= run([PY, "deliverables/scripts/make_script_pdf.py"],
              label="Ten-minute deck: the speaker script (PDF)")
    # The companion to the deck: the vocabulary, the formulas, the slides and
    # the protocol, so the deck is legible to the person presenting it.
    ok &= run([PY, "deliverables/scripts/make_companion.py"],
              label="Ten-minute deck: the companion (PDF)")
    ok &= run([PY, "deliverables/scripts/make_report_companion.py"],
              label="Report deck: the companion (PDF)")
    # The script, explained: why it says what it says, what each slide
    # argues, and how to deliver it in the ten minutes.
    ok &= run([PY, "deliverables/scripts/make_script_guide.py"],
              label="Ten-minute deck: the script, explained (PDF)")
    # The final deck: twenty-five slides for the ten-minute slot, and the
    # complete deck beside it with every table and formula at full size.
    ok &= run([PY, "deliverables/scripts/make_final_mtp_deck.py"],
              label="Final deck: the ten-minute presentation (PPTX)")
    ok &= run([PY, "deliverables/scripts/make_final_mtp_reference.py"],
              label="Final deck: the complete reference (PPTX)")
    # The script for the final deck, slide by slide, and the explanation of
    # it with the answers to the questions a panel asks.
    ok &= run([PY, "deliverables/scripts/make_final_mtp_script.py"],
              label="Final deck: the script, written")
    ok &= run([PY, "deliverables/scripts/make_script_pdf.py",
               "--script", "deliverables/final_mtp_script.md",
               "--deck", "deliverables/final_mtp.pptx",
               "--out", "deliverables/final_mtp_script.pdf"],
              label="Final deck: the script (PDF, the slide above the words)")
    ok &= run([PY, "deliverables/scripts/md_to_docx.py",
               "deliverables/final_mtp_script.md",
               "deliverables/final_mtp_script.docx"],
              label="Final deck: the script (DOCX)")
    ok &= run([PY, "deliverables/scripts/make_final_mtp_script_guide.py"],
              label="Final deck: the script, explained (PDF)")
    ok &= run([PY, "deliverables/scripts/md_to_docx.py",
               "deliverables/final_mtp_script_guide.md",
               "deliverables/final_mtp_script_guide.docx"],
              label="Final deck: the script, explained (DOCX)")
    # The vocabulary of the work: every keyword, in ordinary words and in the
    # technical words, with the number that belongs to it.
    ok &= run([PY, "deliverables/scripts/make_terminology.py"],
              label="Final deck: the terminology guide (PDF)")
    ok &= run([PY, "deliverables/scripts/md_to_docx.py",
               "deliverables/MTP_Terminology.md",
               "deliverables/MTP_Terminology.docx"],
              label="Final deck: the terminology guide (DOCX)")

    # 6a. The paragraphs are whole again. A measured value that lands at the
    #     start of a line reads as a markdown list item, and the DOCX writer
    #     takes it as one, so a paragraph can be cut in two. The generated
    #     documents are written after the substitution, so the guard runs
    #     here rather than inside it.
    ok &= run([PY, "deliverables/scripts/fix_markdown_lists.py"],
              label="Whole paragraphs")

    # 6b. The two prose reports, as PDF. The PDF step needs pandoc and
    #     tectonic; when one of them is absent the step reports the skip and
    #     the build carries on, because a missing optional tool is not a
    #     defect in the document.
    for _src, _pdf in (("deliverables/MTP_Status_Report.md",
                        "deliverables/MTP_Status_Report.pdf"),
                       ("deliverables/MTP_Technical_Documentation.md",
                        "deliverables/MTP_Technical_Documentation.pdf")):
        # The table of contents is what makes a document of this length
        # usable as a reference; the explainer gets one for the same reason.
        ok &= run([PY, "deliverables/scripts/make_pdf.py", _src, _pdf,
                   "--toc"],
                  label=f"PDF: {Path(_pdf).name}")

    # The full explanation: the one document that says what the whole
    # project is, in the words of a reader who has not seen it before. It
    # gets a title block and a table of contents, which the two prose
    # reports do not need.
    ok &= run([PY, "deliverables/scripts/make_pdf.py",
               "research/14_full_explanation.md",
               "deliverables/MTP_Full_Explanation.pdf",
               "--toc", "--strip-first-heading",
               "--metadata", "title=The Whole Thesis, Explained",
               "--metadata",
               "subtitle=An Evidence-Grounded Retrieval-Augmented Generation "
               "Framework for Industrial Decision Support",
               "--metadata",
               "author=Ritik Raj (25IM60R12), Supervisor: Dr. Sri Krishna "
               "Kumar, Department of Industrial and Systems Engineering, "
               "IIT Kharagpur",
               "--metadata", "date=11 November 2026"],
              label="PDF: MTP_Full_Explanation.pdf")

    # The technical report, as a PDF. It is the single-column format of the
    # same paper as the two LaTeX deliverables.
    ok &= run([PY, "deliverables/scripts/make_pdf.py",
               "deliverables/Deliverable_2a_Technical_Report.md",
               "deliverables/Deliverable_2a_Technical_Report.pdf",
               "--toc", "--strip-front-matter",
               "--metadata",
               "title=An Evidence-Grounded Retrieval-Augmented Generation "
               "Framework for Industrial Decision Support",
               "--metadata",
               "subtitle=Architecture, Evaluation Protocol, and "
               "Failure-Mode Characterisation",
               "--metadata",
               "author=Ritik Raj (25IM60R12) — Department of Industrial and "
               "Systems Engineering, IIT Kharagpur — Supervisor: Dr. Sri "
               "Krishna Kumar"],
              label="PDF: Deliverable_2a_Technical_Report.pdf")

    # The plain-language guide: the same ground as the full explanation, in
    # ordinary words, for a reader who has never seen the project. It is the
    # document to read first.
    ok &= run([PY, "deliverables/scripts/md_to_docx.py",
               "deliverables/MTP_Plain_Language_Guide.md",
               "deliverables/MTP_Plain_Language_Guide.docx"],
              label="Plain-language guide -> DOCX")
    ok &= run([PY, "deliverables/scripts/make_pdf.py",
               "deliverables/MTP_Plain_Language_Guide.md",
               "deliverables/MTP_Plain_Language_Guide.pdf",
               "--toc", "--strip-front-matter",
               "--metadata",
               "title=The Whole Thesis in Plain Language",
               "--metadata",
               "subtitle=An all-in-one guide to an evidence-grounded "
               "retrieval-augmented generation framework for industrial "
               "decision support",
               "--metadata",
               "author=Ritik Raj (25IM60R12), Supervisor: Dr. Sri Krishna "
               "Kumar, Department of Industrial and Systems Engineering, "
               "IIT Kharagpur"],
              label="PDF: MTP_Plain_Language_Guide.pdf")

    # The complete guide, as a PDF. The markdown opens with its own title
    # block, which the PDF replaces with a title block of its own, so the
    # markdown's copy is stripped.
    ok &= run([PY, "deliverables/scripts/make_pdf.py",
               "deliverables/Deliverable_1_Complete_Guide.md",
               "deliverables/Deliverable_1_Complete_Guide.pdf",
               "--toc", "--strip-front-matter",
               "--metadata",
               "title=An Evidence-Grounded Retrieval-Augmented Generation "
               "Framework for Industrial Decision Support",
               "--metadata",
               "subtitle=The Complete Guide — every term, every formula, "
               "every line of code, and every number",
               "--metadata",
               "author=Ritik Raj (25IM60R12), Supervisor: Dr. Sri Krishna "
               "Kumar, Department of Industrial and Systems Engineering, "
               "IIT Kharagpur"],
              label="PDF: Deliverable_1_Complete_Guide.pdf")

    # The departmental report. The submission is the .docx, which is built
    # to the department's own Word template -- the bordered title page, the
    # certificate page, the hand-set contents and the filled table headers
    # are Word constructs. This is a reading copy of the same content in the
    # project's LaTeX template, with the institute's logo carried across.
    ok &= run([PY, "deliverables/scripts/docx_to_pdf.py",
               "deliverables/Deliverable_3_Department_Report.docx",
               "deliverables/Deliverable_3_Department_Report.pdf"],
              label="PDF: Deliverable_3_Department_Report.pdf")

    # 7. The dataset itself, with its provenance, shipped alongside
    ok &= run([PY, "impl/scripts/export_dataset.py"], label="Dataset export")

    # 8. Checks: numbers, citations, files, slide layout, LaTeX
    ok &= run([PY, "deliverables/scripts/check_consistency.py"],
              label="Consistency checks")
    ok &= run([PY, "deliverables/scripts/check_slides.py"],
              label="Slide layout check")
    ok &= run([PY, "deliverables/scripts/check_latex.py"],
              label="LaTeX compile check")
    ok &= run([PY, "deliverables/scripts/check_thesis_deliverables.py"],
              label="Fresh deliverables: pages, slides, colour, agreement")
    ok &= run([PY, "deliverables/scripts/check_human_tone.py"],
              label="Prose: dashes, stock phrases, sentence rhythm")
    ok &= run([PY, "deliverables/scripts/check_defence_deck.py"],
              label="Ten-minute deck: slides, overflow, colour, glyphs")
    ok &= run([PY, "deliverables/scripts/check_defence_deck.py",
               "--deck", "deliverables/final_mtp.pptx", "--slides", "20:30",
               "--no-notes"],
              label="Final deck: slides, overflow, colour, glyphs")
    ok &= run([PY, "deliverables/scripts/check_defence_deck.py",
               "--deck", "deliverables/final_mtp_reference.pptx",
               "--slides", "60:90"],
              label="Final reference deck: slides, overflow, colour, glyphs")
    ok &= run([PY, "deliverables/scripts/check_final_script.py"],
              label="Final deck: the script and its guide")
    ok &= run([PY, "deliverables/scripts/check_terminology.py"],
              label="Final deck: the terminology guide")

    print("\n=== deliverables ===")
    for p in sorted(DELIV.glob("*")):
        if p.is_file() and p.name not in ("scripts", "dataset", "templates"):
            print(f"  {p.name:52s} {p.stat().st_size:>9,d} bytes")
    ds = DELIV / "dataset"
    if ds.exists():
        n_files = sum(1 for _ in ds.rglob("*") if _.is_file())
        size = sum(f.stat().st_size for f in ds.rglob("*") if f.is_file())
        print(f"  {'dataset/':52s} {size:>9,d} bytes in {n_files} files")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
