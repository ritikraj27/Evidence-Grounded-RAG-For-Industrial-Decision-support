#!/usr/bin/env bash
# Clone the three third-party skill suites the project wiring expects, then
# rebuild the .claude/skills symlinks. Run from the project root.
set -euo pipefail
clone() { [ -d "$2/.git" ] || git clone --depth 1 "$1" "$2"; }
clone https://github.com/imbad0202/academic-research-skills.git academic-research-skills
clone https://github.com/multica-ai/andrej-karpathy-skills.git andrej-karpathy-skills
clone https://github.com/Chanw-research/claude-code-paper-writing.git claude-code-paper-writing
bash scripts/sync_skills.sh
