#!/usr/bin/env python3
"""Put the page numbers into the report's table of contents.

The contents is a live Word field with the headings written into it as its
cached result, so that it is never blank when the document is opened. The
page numbers, though, are the one thing that cannot be written from outside:
the report paginates to a different number of pages in Word than it does in
the PDF reading copy, because the two are laid out by different engines, and
only Word knows where Word will break the pages.

So Word is asked, once, to update the field and save. The document is opened
through the shell rather than through an AppleEvent, because asking the
application to open a file itself hangs on this machine; handing it a file
that is already open and asking it to save that file is immediate.

The numbers that come back are checked before the file is accepted: a
contents list whose page numbers are all the same is a failed update, not a
result.

Usage:
    python3 deliverables/scripts/update_toc_pages.py
"""
from __future__ import annotations

import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCX = ROOT / "deliverables" / "MTP_Report.docx"

SAVE = """on run argv
  tell application "Microsoft Word"
    with timeout of 240 seconds
      set d to active document
      repaginate d
      update (get table of contents 1 of d)
      save d
      close d saving no
    end timeout
  end tell
  return "ok"
end run
"""


def close_open_documents(app: str) -> None:
    """Close anything the application already has open.

    This matters more than it looks. If the application still holds a
    document, then `open -a` on the file does not reload it from disk: the
    application activates the copy it already has. A document edited on disk
    in the meantime is then silently ignored, and saving writes the stale
    copy back over it.
    """
    import subprocess

    if app == "Microsoft Word":
        probe = ('tell application "Microsoft Word" to return '
                 '(count of documents)')
        close = ("tell application \"Microsoft Word\"\n"
                 "  set d to active document\n"
                 "  close d saving no\n"
                 "end tell")
    else:
        probe = ('tell application "Microsoft PowerPoint" to return '
                 '(count of presentations)')
        close = ("tell application \"Microsoft PowerPoint\"\n"
                 "  set p to active presentation\n"
                 "  close p saving no\n"
                 "end tell")
    try:
        for _ in range(20):
            r = subprocess.run(["osascript", "-e", probe],
                               capture_output=True, text=True, timeout=30)
            if not (r.stdout.strip().isdigit() and int(r.stdout.strip()) > 0):
                return
            subprocess.run(["osascript", "-e", close],
                           capture_output=True, timeout=60)
    except Exception:
        pass


def _probe() -> str:
    r = subprocess.run(
        ["osascript", "-e",
         'tell application "Microsoft Word" to return (count of documents)'],
        capture_output=True, text=True, timeout=30)
    return r.stdout.strip()


def _wait_for_document(timeout: int = 180) -> bool:
    end = time.time() + timeout
    while time.time() < end:
        try:
            if _probe().isdigit() and int(_probe()) > 0:
                time.sleep(3)
                return True
        except Exception:
            pass
        time.sleep(2)
    return False


def toc_page_numbers() -> list[int]:
    """The page numbers currently in the contents, in order."""
    import zipfile

    xml = zipfile.ZipFile(DOCX).read("word/document.xml").decode("utf-8")
    i = xml.find("<w:sdtContent>")
    j = xml.find("</w:sdtContent>")
    block = xml[i:j]
    out = []
    for para in re.findall(r"<w:p[ >].*?</w:p>", block, re.S):
        texts = re.findall(r"<w:t[^>]*>([^<]*)</w:t>", para)
        if not texts:
            continue
        last = texts[-1].strip()
        if last.isdigit():
            out.append(int(last))
    return out


def main() -> int:
    if not DOCX.exists():
        print(f"  x {DOCX.name} not found")
        return 1
    import tempfile

    # Word first, and let it settle before it is asked to do anything.
    for _ in range(60):
        try:
            r = subprocess.run(["osascript", "-e",
                                'tell application "Microsoft Word" to return name'],
                               capture_output=True, text=True, timeout=20)
            if r.returncode == 0 and r.stdout.strip():
                time.sleep(3)
                break
        except Exception:
            pass
        time.sleep(1)

    close_open_documents("Microsoft Word")
    subprocess.run(["open", "-a", "Microsoft Word", str(DOCX)], capture_output=True)
    if not _wait_for_document():
        print("  x Word never opened the document")
        return 1

    with tempfile.TemporaryDirectory(prefix="mtp-toc-") as tmp:
        scpt = Path(tmp) / "save.scpt"
        scpt.write_text(SAVE, encoding="utf-8")
        try:
            r = subprocess.run(["osascript", str(scpt)],
                               capture_output=True, text=True, timeout=280)
        except subprocess.TimeoutExpired:
            print("  x Word did not answer in time")
            return 1
        if r.returncode != 0:
            print(f"  x Word refused: {(r.stderr or '').strip()[:160]}")
            return 1

    # Word rewrites the theme when it saves, and writes back the
    # compatibility mode it had in memory. The document has to stay
    # monochrome and in the modern mode, so both treatments are applied
    # again afterwards.
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from monochrome import to_monochrome
        to_monochrome(DOCX)
    except Exception as exc:
        print(f"  -- could not re-apply the monochrome treatment: {exc}")
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from docx_settings import set_compatibility_mode
        set_compatibility_mode(DOCX)
    except Exception as exc:
        print(f"  -- could not re-apply the compatibility mode: {exc}")

    numbers = toc_page_numbers()
    print(f"  contents page numbers: {numbers[:12]}"
          + (" ..." if len(numbers) > 12 else ""))
    if not numbers:
        print("  x the contents list has no page numbers")
        return 1
    if len(set(numbers)) == 1:
        print("  x every page number is the same, so the update did not take")
        return 1
    if numbers != sorted(numbers):
        print("  x the page numbers are not in order")
        return 1
    print(f"  {DOCX.name} updated with {len(numbers)} page numbers")
    return 0


if __name__ == "__main__":
    sys.exit(main())
