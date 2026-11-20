#!/usr/bin/env bash
#
# install_aris.sh - install or refresh the local ARIS checkout and publish the
# environment manifest that the ARS / paper-writing skills read.
#
# Contract (from the skills that call it):
#
#   arxiv/SKILL.md:192, alphaxiv/SKILL.md:137, deepxiv/SKILL.md:205,
#   exa-search/SKILL.md:156, idea-creator/SKILL.md:40,
#   research-lit/SKILL.md:374, semantic-scholar/SKILL.md:167
#
#     ARIS_REPO="${ARIS_REPO:-$(awk -F'\t' '$1=="repo_root"{print $2; exit}' \
#                    .aris/installed-skills.txt 2>/dev/null)}"
#
#   So <root>/.aris/installed-skills.txt is a TSV manifest and the row
#   "repo_root<TAB><absolute path to the repo>" is read by column key.
#
#   The paper-write / paper-plan / paper-poster / paper-slides /
#   paper-illustration / grant-proposal / paper-writing skills also tell the
#   user to "re-run 'bash tools/install_aris.sh' to refresh the '.aris/tools'
#   symlink", so this script maintains <root>/.aris/tools -> <repo>/tools.
#
# Everything is idempotent: re-running refreshes the checkout and rewrites the
# manifest in place.
#
set -euo pipefail

SCRIPT_NAME="install_aris.sh"
SCRIPT_VERSION="1.0"

DEFAULT_ARIS_URL="https://github.com/Imbad0202/academic-research-skills"
DEFAULT_REPO_DIRNAME="academic-research-skills"

# ---------------------------------------------------------------- usage ----

usage() {
  cat <<'USAGE'
install_aris.sh - install/refresh the ARIS repo and write the local manifest.

Usage:
  bash tools/install_aris.sh [options]

Options:
  -h, --help            Show this help and exit 0.
  -r, --repo <path>     Existing ARIS checkout to install/refresh.
                        Default: $ARIS_REPO, else <root>/<default repo dirname>.
  -i, --install-dir <d> Directory to clone into when the repo is missing.
                        Default: <root>/<default repo dirname>.
  -u, --url <url>       Git URL used when cloning.
                        Default: https://github.com/Imbad0202/academic-research-skills
      --root <dir>      Project root that owns .aris/.
                        Default: $ARIS_ROOT, else the current directory when it
                        looks like a project root, else this script's parent dir.
      --no-clone        Never clone; fail if the repo directory is missing.
      --no-refresh      Skip "git pull --ff-only" on an existing checkout.
      --link-tools      Also symlink helper scripts that are missing from
                        <root>/tools into <root>/tools from <repo>/tools.
                        Existing files are never overwritten.
      --dry-run         Print what would be done; write nothing.
      --check           Read-only environment check. Exit 1 when broken.
  -q, --quiet           Only print warnings and errors.

Artifacts written (unless --dry-run / --check):
  <root>/.aris/installed-skills.txt   TSV manifest. First row is
                                      "repo_root<TAB><absolute repo path>".
  <root>/.aris/tools                  symlink -> <repo>/tools
  <root>/.aris/env.sh                 sourceable "export ARIS_REPO=..."

Exit codes:
  0  success (or environment healthy in --check mode)
  1  usage error, missing repo with --no-clone, or broken environment in
     --check mode
USAGE
}

die() {
  printf '%s: error: %s\n' "$SCRIPT_NAME" "$*" >&2
  exit 1
}

warn() {
  printf '%s: warning: %s\n' "$SCRIPT_NAME" "$*" >&2
}

say() {
  [ "$QUIET" -eq 1 ] || printf '%s\n' "$*"
}

now_iso() { date -u +%Y-%m-%dT%H:%M:%SZ; }

# ------------------------------------------------------------ arg parse ----

REPO=""
INSTALL_DIR=""
REPO_URL="$DEFAULT_ARIS_URL"
ROOT=""
DO_CLONE=1
DO_REFRESH=1
DO_LINK_TOOLS=0
DRY_RUN=0
CHECK_ONLY=0
QUIET=0

while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    -r|--repo)        [ $# -ge 2 ] || die "--repo requires a path"; REPO="$2"; shift 2 ;;
    --repo=*)        REPO="${1#*=}"; shift ;;
    -i|--install-dir) [ $# -ge 2 ] || die "--install-dir requires a path"; INSTALL_DIR="$2"; shift 2 ;;
    --install-dir=*) INSTALL_DIR="${1#*=}"; shift ;;
    -u|--url)        [ $# -ge 2 ] || die "--url requires a URL"; REPO_URL="$2"; shift 2 ;;
    --url=*)         REPO_URL="${1#*=}"; shift ;;
    --root)          [ $# -ge 2 ] || die "--root requires a path"; ROOT="$2"; shift 2 ;;
    --root=*)        ROOT="${1#*=}"; shift ;;
    --no-clone)      DO_CLONE=0; shift ;;
    --no-refresh)    DO_REFRESH=0; shift ;;
    --link-tools)    DO_LINK_TOOLS=1; shift ;;
    --dry-run)       DRY_RUN=1; shift ;;
    --check)         CHECK_ONLY=1; shift ;;
    -q|--quiet)      QUIET=1; shift ;;
    --)              shift; break ;;
    -*)              printf '%s: error: unknown option: %s\n' "$SCRIPT_NAME" "$1" >&2
                      usage >&2; exit 1 ;;
    *)               printf '%s: error: unexpected argument: %s\n' "$SCRIPT_NAME" "$1" >&2
                      usage >&2; exit 1 ;;
  esac
done

# ----------------------------------------------------------- resolve root ---

script_dir() {
  local src="$1" dir
  while [ -L "$src" ]; do
    dir="$(cd -P "$(dirname "$src")" && pwd)"
    src="$(readlink "$src")"
    case "$src" in
      /*) ;;
      *) src="$dir/$src" ;;
    esac
  done
  cd -P "$(dirname "$src")" && pwd
}

SELF_DIR="$(script_dir "$0")"

if [ -z "$ROOT" ]; then
  if [ -n "${ARIS_ROOT:-}" ]; then
    ROOT="$ARIS_ROOT"
  elif [ -d "$PWD/.claude" ] || [ -d "$PWD/tools" ] || [ -d "$PWD/.aris" ]; then
    ROOT="$PWD"
  else
    ROOT="$(cd "$SELF_DIR/.." && pwd)"
  fi
fi
[ -d "$ROOT" ] || die "--root '$ROOT' is not a directory"
ROOT="$(cd "$ROOT" && pwd)"

# ---------------------------------------------------------- resolve repo ----

if [ -z "$REPO" ]; then
  REPO="${ARIS_REPO:-}"
fi
if [ -z "$REPO" ]; then
  if [ -z "$INSTALL_DIR" ]; then
    INSTALL_DIR="$ROOT/$DEFAULT_REPO_DIRNAME"
  fi
  REPO="$INSTALL_DIR"
fi
if [ -z "$INSTALL_DIR" ]; then
  INSTALL_DIR="$REPO"
fi

ARIS_DIR="$ROOT/.aris"
MANIFEST="$ARIS_DIR/installed-skills.txt"
TOOLS_LINK="$ARIS_DIR/tools"
ENV_SH="$ARIS_DIR/env.sh"

# ----------------------------------------------------------- check mode ----

if [ "$CHECK_ONLY" -eq 1 ]; then
  status=0
  say "ARIS environment check"
  say "  root            : $ROOT"

  m_repo=""
  if [ -f "$MANIFEST" ]; then
    m_repo="$(awk -F'\t' '$1=="repo_root"{print $2; exit}' "$MANIFEST" 2>/dev/null || true)"
  fi
  if [ -n "$m_repo" ]; then
    say "  manifest repo_root: $m_repo"
    if [ -d "$m_repo" ]; then
      say "    [ok]   repo directory exists"
    else
      say "    [FAIL] repo directory is missing"
      status=1
    fi
  else
    say "  manifest repo_root: <none>"
    say "    [FAIL] $MANIFEST has no repo_root row"
    status=1
  fi

  if [ -L "$TOOLS_LINK" ]; then
    say "  .aris/tools      -> $(readlink "$TOOLS_LINK")"
    if [ -e "$TOOLS_LINK" ]; then
      say "    [ok]   symlink resolves"
    else
      say "    [FAIL] symlink is dangling"
      status=1
    fi
  elif [ -d "$TOOLS_LINK" ]; then
    say "  .aris/tools      : (directory)"
    say "    [ok]   present"
  else
    say "  .aris/tools      : <missing>"
    say "    [FAIL] .aris/tools symlink is missing"
    status=1
  fi

  say "  helper scripts:"
  for helper in extract_paper_style.py save_trace.sh verify_paper_audits.sh; do
    if [ -f "$ROOT/tools/$helper" ]; then
      say "    [ok]   tools/$helper"
    else
      say "    [MISS] tools/$helper"
    fi
  done

  if [ "$status" -eq 0 ]; then
    say "  result: healthy"
  else
    say "  result: broken"
  fi
  exit "$status"
fi

# ------------------------------------------------------------- install -----

if [ -n "$REPO" ] && [ ! -d "$REPO" ]; then
  if [ "$DO_CLONE" -eq 0 ]; then
    die "ARIS repo '$REPO' not found and --no-clone was given"
  fi
  say "ARIS repo not found at '$REPO' - cloning from $REPO_URL"
  if [ "$DRY_RUN" -eq 1 ]; then
    say "  [dry-run] would run: git clone $REPO_URL $REPO"
  else
    parent="$(dirname "$REPO")"
    mkdir -p "$parent"
    git clone --depth 1 "$REPO_URL" "$REPO" || die "git clone failed for $REPO_URL"
  fi
fi

if [ -n "$REPO" ]; then
  REPO="$(cd "$REPO" && pwd)"
fi

if [ "$DO_REFRESH" -eq 1 ] && [ -d "$REPO" ] && [ -d "$REPO/.git" ]; then
  if [ "$DRY_RUN" -eq 1 ]; then
    say "  [dry-run] would run: git -C $REPO pull --ff-only"
  else
    if git -C "$REPO" pull --ff-only >/dev/null 2>&1; then
      say "ARIS repo refreshed: $REPO"
    else
      warn "could not refresh '$REPO' (dirty tree, detached HEAD, or offline); using it as-is"
    fi
  fi
else
  say "ARIS repo: $REPO"
fi

# ------------------------------------------------------------- manifest ----

manifest_body() {
  printf 'repo_root\t%s\n' "$REPO"
  printf 'skills_root\t%s\n' "$ROOT/.claude/skills"
  printf 'tools_root\t%s\n' "$ROOT/tools"
  printf 'installed_at\t%s\n' "$(now_iso)"
  printf 'installer\t%s\n' "$SCRIPT_NAME"
  printf 'installer_version\t%s\n' "$SCRIPT_VERSION"
  printf 'repo_url\t%s\n' "$REPO_URL"
  # One "skill<TAB><name>" row per installed skill (dirs with a SKILL.md).
  if [ -d "$ROOT/.claude/skills" ]; then
    for d in "$ROOT/.claude/skills"/*; do
      [ -d "$d" ] || continue
      [ -f "$d/SKILL.md" ] || continue
      printf 'skill\t%s\n' "$(basename "$d")"
    done
  fi
}

if [ "$DRY_RUN" -eq 1 ]; then
  say "[dry-run] would write $MANIFEST with:"
  manifest_body | sed 's/^/    /'
  say "[dry-run] would refresh symlink $TOOLS_LINK -> $REPO/tools"
  say "[dry-run] would write $ENV_SH"
  exit 0
fi

mkdir -p "$ARIS_DIR"
manifest_body > "$MANIFEST"

# ---------------------------------------------------------- tools symlink --

if [ -d "$REPO/tools" ]; then
  if [ -L "$TOOLS_LINK" ]; then
    current="$(readlink "$TOOLS_LINK" 2>/dev/null || true)"
    if [ "$current" != "$REPO/tools" ]; then
      rm -f "$TOOLS_LINK"
      ln -s "$REPO/tools" "$TOOLS_LINK"
      say "refreshed symlink $TOOLS_LINK -> $REPO/tools"
    else
      say "symlink $TOOLS_LINK already current"
    fi
  elif [ -e "$TOOLS_LINK" ]; then
    warn "$TOOLS_LINK exists and is not a symlink; leaving it alone"
  else
    ln -s "$REPO/tools" "$TOOLS_LINK"
    say "created symlink $TOOLS_LINK -> $REPO/tools"
  fi
else
  warn "no tools/ directory inside '$REPO'; skipping the .aris/tools symlink"
fi

# -------------------------------------------------------------- env.sh ----

cat > "$ENV_SH" <<EOF
# Generated by $SCRIPT_NAME on $(now_iso). Source this to pick up ARIS_REPO.
export ARIS_REPO="$REPO"
export ARIS_ROOT="$ROOT"
EOF

# ---------------------------------------------------- optional tool links --

if [ "$DO_LINK_TOOLS" -eq 1 ] && [ -d "$REPO/tools" ]; then
  mkdir -p "$ROOT/tools"
  for src in "$REPO/tools"/*; do
    [ -e "$src" ] || continue
    base="$(basename "$src")"
    [ -e "$ROOT/tools/$base" ] && continue
    ln -s "$src" "$ROOT/tools/$base"
    say "linked $ROOT/tools/$base -> $src"
  done
fi

say "ARIS installation complete."
say "  repo      : $REPO"
say "  manifest  : $MANIFEST"
say "  tools     : $TOOLS_LINK"
say "  env       : $ENV_SH"
say ""
say "Add this to your shell profile (or 'source $ENV_SH'):"
say "  export ARIS_REPO=\"$REPO\""

exit 0
