#!/usr/bin/env python3
"""Render an office document to PDF through pandoc and tectonic.

The department report is a Word document built to the department's own
house template -- a bordered title page with the institute logo, a
certificate page, a hand-set table of contents, filled table headers and
page numbers. That document is the submission, and it is built by
`make_docx.py` as a `.docx` because that is what the template is a Word
template for.

This script produces a **reading copy** of the same document as a PDF: the
same content, the same tables, the same logo, rendered in the project's
LaTeX template so that it sits with the other PDFs. It is not a
pixel-perfect rendering of the Word page furniture -- the borders and the
certificate page are Word constructs -- and the `.docx` remains the
document the department receives.

Usage:
    python3 deliverables/scripts/docx_to_pdf.py SOURCE.docx OUTPUT.pdf
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "deliverables" / "templates" / "report_template.tex"
EXIT_NO_ENGINE = 3


def _which(name: str) -> str | None:
    return shutil.which(name)


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: docx_to_pdf.py SOURCE.docx OUTPUT.pdf")
        return 2
    src = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2]).resolve()
    if not src.exists():
        print(f"  ✗ {src} not found")
        return 1

    pandoc = _which("pandoc")
    tectonic = _which("tectonic")
    if not pandoc or not tectonic:
        missing = " and ".join(n for n, p in (("pandoc", pandoc),
                                             ("tectonic", tectonic)) if not p)
        print(f"  -- no PDF engine ({missing} not on PATH); skipping "
              f"{out.name}")
        return EXIT_NO_ENGINE

    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="mtp-docx-pdf-") as tmp:
        tmpdir = Path(tmp)
        media = tmpdir / "media"
        tex = tmpdir / (out.stem + ".tex")

        cmd = [
            pandoc, str(src),
            "-f", "docx", "-t", "latex",
            "--standalone",
            "--template", str(TEMPLATE),
            "--extract-media", str(media),
            "--resource-path", str(src.parent),
            "--output", str(tex),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  ✗ pandoc failed on {src.name}")
            for line in ((r.stdout or "") + (r.stderr or "")).splitlines()[-12:]:
                print("    " + line)
            return 1

        # The extracted media is referenced by absolute path; it has to ship
        # beside the PDF and be referenced relatively, or the PDF is broken
        # for anyone who receives it without this directory.
        text = tex.read_text(encoding="utf-8")
        shipped_root = out.parent / f"{out.stem}_media"
        if shipped_root.exists():
            shutil.rmtree(shipped_root)
        if media.exists():
            for path in sorted(media.rglob("*")):
                if not path.is_file():
                    continue
                # Each file is addressed by where pandoc *extracted* it, and
                # replaced by where it is *shipped*, relative to the folder
                # the PDF sits in.
                _abs = str(path)
                _rel = f"{shipped_root.name}/{path.relative_to(media)}"
                text = text.replace(_abs, _rel)
                _dest = out.parent / _rel
                _dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, _dest)
                # The compile runs in a temporary directory, so the file
                # also has to be there under the same relative name.
                _mirror = tmpdir / _rel
                _mirror.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, _mirror)
                if not _mirror.exists():
                    print(f"  [docx-pdf] WARNING: the mirror of "
                          f"{_rel} is missing from the compile directory")
        tex.write_text(text, encoding="utf-8")

        r = subprocess.run([tectonic, "-X", "compile", str(tex)],
                           capture_output=True, text=True, cwd=str(tmpdir))
        produced = tex.with_suffix(".pdf")
        if r.returncode != 0 or not produced.exists():
            print(f"  ✗ tectonic did not compile {out.name}")
            for line in ((r.stdout or "") + (r.stderr or "")).splitlines()[-15:]:
                print("    " + line)
            return 1

        if out.exists():
            out.unlink()
        shutil.copy2(produced, out)
        print(f"  [docx-pdf] {src.name} -> {out.name} "
              f"({out.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
