#!/usr/bin/env python3
"""Put the quota placement back where it was, in one command.

The placement was moved from ``post_rerank`` to ``pre_rerank`` on 16 November
2026 and everything that depends on it was re-measured. If that turn out to
be the wrong call, reverting it has to restore *both* halves of the change:

  * the measurements, from the snapshot taken before anything was touched,
    and
  * the shipped configuration, because the measurements on disk are only
    comparable to a configuration that produced them.

Reverting one half alone leaves the two disagreeing, and nothing in the
build would notice: the guard reads the configuration, not the results. So
this script does both, and refuses to run while a re-measurement is in
flight -- a suite still writing into ``impl/results*`` would overwrite the
restored files.

    python3 deliverables/scripts/revert_quota_placement.py
    python3 deliverables/scripts/revert_quota_placement.py --check
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / ".snapshot_preswap"
CONFIG = ROOT / "impl" / "src" / "config.py"

#: What the snapshot holds, and where each piece goes back to.
PAIRS = (
    ("results", ROOT / "impl" / "results"),
    ("results_focus", ROOT / "impl" / "results_focus"),
    ("results_industrial", ROOT / "impl" / "results_industrial"),
    ("artifacts", ROOT / "impl" / "artifacts"),
    ("artifacts_focus", ROOT / "impl" / "artifacts_focus"),
    ("artifacts_industrial", ROOT / "impl" / "artifacts_industrial"),
)

SUITE_SCRIPTS = ("scripts/rerun_all.sh", "scripts/rerun_focus.sh",
                 "scripts/run_industrial_suite.sh")


def suites_running() -> list[str]:
    """The re-measurement suites currently in flight."""
    out = subprocess.run(["ps", "-Ao", "command"], capture_output=True, text=True)
    running = []
    for line in out.stdout.splitlines():
        line = line.strip()
        # The suite scripts are launched as `bash scripts/<name>.sh`; the
        # shell wrapper that launched them mentions the same name inside a
        # longer command, so match the invocation and not the mention.
        if line.startswith("bash ") and any(s in line for s in SUITE_SCRIPTS):
            running.append(line)
    return running


def shipped_position() -> str | None:
    """The position the configuration currently ships."""
    for line in CONFIG.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("position:"):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def set_position(value: str) -> None:
    text = CONFIG.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.strip().startswith("position:"):
            lines[i] = f'    position: str = "{value}"\n'
            break
    else:
        raise SystemExit("could not find the position setting in config.py")
    CONFIG.write_text("".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="report what a revert would do, and change nothing")
    args = ap.parse_args()

    print(f"the configuration ships: {shipped_position()}")
    missing = [name for name, _ in PAIRS if not (SNAPSHOT / name).exists()]
    if missing:
        print(f"the snapshot is missing: {', '.join(missing)}")
        return 1

    running = suites_running()
    if running and not args.check:
        print("a re-measurement is still running, so the restore would be "
              "overwritten:")
        for line in running:
            print(f"  {line}")
        print("wait for it to finish, or stop it, and run this again")
        return 1

    if args.check:
        print(f"the snapshot holds: {', '.join(name for name, _ in PAIRS)}")
        print("a revert would restore those and set the position to "
              "post_rerank")
        if running:
            print(f"note: {len(running)} suite(s) are running, so a revert "
                  f"would have to wait for them")
        return 0

    for name, target in PAIRS:
        source = SNAPSHOT / name
        if not target.exists():
            target.mkdir(parents=True)
        shutil.rmtree(target)
        shutil.copytree(source, target)
        print(f"  restored {target.relative_to(ROOT)} "
              f"({sum(1 for _ in source.rglob('*') if _.is_file())} files)")

    set_position("post_rerank")
    print("  the configuration now ships: post_rerank")
    print("\nreverted. Rebuild with: python3 deliverables/scripts/build_all.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
