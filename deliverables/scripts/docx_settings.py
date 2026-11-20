#!/usr/bin/env python3
"""Settings-level edits on a Word document.

The compatibility mode lives in `word/settings.xml` inside the package, so
that is the only place it can be changed. Word rewrites the file when it
saves, and it writes back the mode it had in memory, so a document that has
to come out of Word in the modern mode has to be set again afterwards.

Why the mode matters: a document that does not declare one is opened by
Word in Word 2007 compatibility mode, because that is what the setting was
worth when the file format last changed. The older engine lays an equation
out by the rules of 2007, and it is the engine that draws a rule around a
formula. A document written in 2026 and opened in a current Word belongs in
the current mode.
"""
from __future__ import annotations

import re
import zipfile
from pathlib import Path

#: Word 2013 and later.
CURRENT_MODE = "15"

#: The identifier Microsoft uses for the setting.
COMPAT_URI = "http://schemas.microsoft.com/office/word"


def _rewrite_settings(docx: Path, change) -> None:
    """Rewrite `word/settings.xml` inside the package."""
    tmp = docx.with_suffix(".settings.docx")
    with zipfile.ZipFile(docx) as zin, \
            zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/settings.xml":
                data = change(data.decode("utf-8")).encode("utf-8")
            zout.writestr(item, data)
    tmp.replace(docx)


def set_compatibility_mode(docx: Path, mode: str = CURRENT_MODE) -> None:
    """Declare the document as being of the given Word version.

    A document that already declares the mode has it rewritten; a document
    that declares nothing gets the setting added, because a missing setting
    is not the same as a modern one.
    """
    existing = (r'(<w:compatSetting w:name="compatibilityMode"[^>]*'
                r'w:val=")\d+(")')

    def change(xml: str) -> str:
        if re.search(existing, xml):
            return re.sub(existing, rf"\g<1>{mode}\g<2>", xml)
        block = ('<w:compat><w:compatSetting w:name="compatibilityMode" '
                 f'w:uri="{COMPAT_URI}" w:val="{mode}"/></w:compat>')
        # In the settings sequence w:compat comes before w:rsids.
        for anchor in ("<w:rsids", "<m:mathPr", "<w:themeFontLang"):
            i = xml.find(anchor)
            if i != -1:
                return xml[:i] + block + xml[i:]
        return xml.replace("</w:settings>", block + "</w:settings>")

    _rewrite_settings(docx, change)
