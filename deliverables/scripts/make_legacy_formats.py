#!/usr/bin/env python3
"""Write the legacy Office formats: the report as .doc, the deck as .ppt.

The Word 97-2003 and PowerPoint 97-2003 formats are the ones a department
that asks for "a .doc file" means. Neither format can be written from Python:
Word's binary format has no writer, and neither is documented. The two
applications that can write them can, however, be asked, and this script asks
them once, opens nothing else, and closes what it opens.

The alternative, macOS's own converter, was tried and rejected: it strips
every image and every equation, so the emblem, the six figures and the 103
formulas all come out as nothing.

Both applications need an HFS path for `save ... in`, and the POSIX path that
works everywhere else is silently accepted and then written nowhere. That is
the reason for the conversion below.

Usage:
    python3 deliverables/scripts/make_legacy_formats.py
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DELIV = ROOT / "deliverables"

DOCX = DELIV / "MTP_Report.docx"
DOC = DELIV / "MTP_Report.doc"
PPTX = DELIV / "MTP_Report_Presentation.pptx"
PPT = DELIV / "MTP_Report_Presentation.ppt"

#: The two scripts. The application, the command, and the format enum.
SAVE_WORD = """on run argv
  set dst to item 1 of argv
  tell application "Microsoft Word"
    with timeout of 240 seconds
      set d to active document
      save as d file name dst file format format document97
      close d saving no
    end timeout
  end tell
  return "ok"
end run
"""

SAVE_POWERPOINT = """on run argv
  set dst to item 1 of argv
  tell application "Microsoft PowerPoint"
    with timeout of 240 seconds
      set p to active presentation
      save p in dst as save as presentation
      close p saving no
    end timeout
  end tell
  return "ok"
end run
"""


def hfs(path: Path) -> str:
    """The HFS form of a path, volume included.

    PowerPoint's `save ... in` wants this and quietly accepts a POSIX path
    without writing anything. The volume has to be named too, or the path is
    read as relative to the default volume.
    """
    try:
        vol = subprocess.run(
            ["osascript", "-e", 'return name of startup disk'],
            capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception:
        vol = ""
    vol = vol or "Macintosh HD"
    return ":".join([vol] + [p for p in str(path).split("/") if p])


def warm_up(app: str) -> None:
    """Start the application and wait until it answers an AppleEvent.

    Word and PowerPoint both take a while to come up, and a document opened
    against an application that is still starting is either refused or left
    waiting behind the start screen. Asking it a trivial question first and
    waiting for the answer is the reliable way to be sure it is ready.
    """
    import time

    for _ in range(60):
        try:
            r = subprocess.run(
                ["osascript", "-e",
                 f'tell application "{app}" to return name'],
                capture_output=True, text=True, timeout=20)
            if r.returncode == 0 and r.stdout.strip():
                # It answers now; give it a moment to finish painting its
                # start screen before a document is sent at it.
                time.sleep(3)
                return
        except Exception:
            pass
        time.sleep(1)


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


def _wait_for_document(app: str, timeout: int = 180) -> bool:
    """Wait until the application has the document open."""
    import time

    probe = ('tell application "Microsoft Word" to return (count of documents)'
             if app == "Microsoft Word" else
             'tell application "Microsoft PowerPoint" to return '
             '(count of presentations)')
    end = time.time() + timeout
    while time.time() < end:
        try:
            r = subprocess.run(["osascript", "-e", probe],
                               capture_output=True, text=True, timeout=30)
            if (r.returncode == 0 and r.stdout.strip().isdigit()
                    and int(r.stdout.strip()) > 0):
                time.sleep(3)
                return True
        except Exception:
            pass
        time.sleep(2)
    return False


def convert(src: Path, dst: Path, script: str, *, app: str,
            path_form: str = "posix") -> bool:
    if not shutil.which("osascript"):
        print(f"  -- osascript is not on PATH; skipping {dst.name}")
        return False
    if not Path(f"/Applications/{app}.app").exists():
        print(f"  -- {app} is not installed; skipping {dst.name}")
        return False
    warm_up(app)
    # The document is opened through the shell rather than through an
    # AppleEvent. Asking the application to open a file itself hangs on this
    # machine; handing it a file that is already open and asking it to save
    # that file is immediate. The source file is not modified: `save as`
    # writes the new file and leaves the original where it is.
    close_open_documents(app)
    subprocess.run(["open", "-a", app, str(src)], capture_output=True)
    if not _wait_for_document(app):
        print(f"  x {app} never opened the document; {dst.name} not written",
              flush=True)
        return False
    with tempfile.TemporaryDirectory(prefix="mtp-legacy-") as tmp:
        tmpdir = Path(tmp)
        scpt = tmpdir / "save.scpt"
        scpt.write_text(script, encoding="utf-8")
        try:
            target = hfs(dst) if path_form == "hfs" else str(dst)
            r = subprocess.run(["osascript", str(scpt), target],
                               capture_output=True, text=True, timeout=280)
        except subprocess.TimeoutExpired:
            print(f"  x {app} did not answer in time; {dst.name} not written", flush=True)
            return False
        if r.returncode != 0:
            print(f"  x {app} refused: {(r.stderr or '').strip()[:160]}", flush=True)
            return False
    if not dst.exists():
        print(f"  x {app} reported success but {dst.name} was not written", flush=True)
        return False
    print(f"  wrote {dst.name} ({dst.stat().st_size:,} bytes)", flush=True)
    return True


def main() -> int:
    ok = True
    if DOCX.exists():
        ok &= convert(DOCX, DOC, SAVE_WORD, app="Microsoft Word",
                      path_form="posix")
    else:
        print(f"  -- {DOCX.name} not found; skipping")
    if PPTX.exists():
        ok &= convert(PPTX, PPT, SAVE_POWERPOINT, app="Microsoft PowerPoint",
                      path_form="hfs")
    else:
        print(f"  -- {PPTX.name} not found; skipping")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
