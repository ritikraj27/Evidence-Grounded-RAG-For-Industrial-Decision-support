#!/usr/bin/env bash
# Rebuild the .claude/skills wiring from the three upstream clones.
#
# Two kinds of entry:
#
#   plain   - .claude/skills/<name> is a symlink straight to the upstream skill dir.
#             Used when the upstream skill needs no local files.
#
#   wrapper - .claude/skills/<name> is a real directory holding:
#               SKILL.md -> symlink to upstream SKILL.md  (so `git pull` still updates it)
#               <subdir> -> symlink to upstream subdir, for any upstream subdir that exists
#               <extra>  -> symlink from the EXTRAS list below
#             Used when a skill needs a local file upstream does not ship
#             (e.g. the ppw family's shared references/ tree).
#
# Claude Code identifies a project skill by its DIRECTORY name, not by the
# frontmatter `name:` field, so upstream names like `ppw:caption` need no rewriting.
#
# Written for bash 3.2 (the macOS default): no associative arrays.
#
# Usage:  bash scripts/sync_skills.sh          # rebuild the wiring
#         bash scripts/sync_skills.sh --check  # report differences, change nothing

set -eu
cd "$(dirname "$0")/.."
ROOT="$PWD"
CLONE_PPW="claude-code-paper-writing"
CLONE_ARS="academic-research-skills"
CLONE_KARPATHY="andrej-karpathy-skills"
PPW_PARENT="$CLONE_PPW/skills/writing-polish/paper-polish-workflow"
SKILLS_DIR="$ROOT/.claude/skills"

CHECK=0
[ "${1:-}" = "--check" ] && CHECK=1

note() { echo "  $*"; }

rel() {  # repo-root path -> path relative to .claude/skills/
  echo "../../${1#"$ROOT/"}"
}

relw() { # repo-root path -> path relative to .claude/skills/<name>/
  echo "../../../${1#"$ROOT/"}"
}

# --- wrapper skills: "name|upstream-dir-relative-to-repo-root" -----------------
WRAPPERS="
deep-research-lit|$CLONE_PPW/skills/literature-review/deep-research
comm-lit-review|$CLONE_PPW/skills/literature-review/comm-lit-review
"
for name in ppw-abstract ppw-caption ppw-cover-letter ppw-de-ai ppw-experiment \
            ppw-literature ppw-logic ppw-polish ppw-repo-to-paper \
            ppw-reviewer-simulation ppw-team ppw-translation ppw-update ppw-visualization; do
  WRAPPERS="$WRAPPERS
$name|$PPW_PARENT/.claude/skills/$name"
done

# Extra links: "skill|link-name|target-relative-to-repo-root"
EXTRAS="
ppw-abstract|references|$PPW_PARENT/references
ppw-caption|references|$PPW_PARENT/references
ppw-cover-letter|references|$PPW_PARENT/references
ppw-de-ai|references|$PPW_PARENT/references
ppw-experiment|references|$PPW_PARENT/references
ppw-literature|references|$PPW_PARENT/references
ppw-logic|references|$PPW_PARENT/references
ppw-polish|references|$PPW_PARENT/references
ppw-repo-to-paper|references|$PPW_PARENT/references
ppw-reviewer-simulation|references|$PPW_PARENT/references
ppw-team|references|$PPW_PARENT/references
ppw-translation|references|$PPW_PARENT/references
ppw-update|references|$PPW_PARENT/references
ppw-visualization|references|$PPW_PARENT/references
"

is_wrapper() {
  echo "$WRAPPERS" | grep -q "^$1|"
}

# Upstream directories that are installed under a DIFFERENT name, so they must
# not be linked a second time under their upstream basename. The PPW suite's
# literature-review/deep-research collides with the ARS `deep-research` skill
# in the flat .claude/skills namespace; it is installed as `deep-research-lit`.
SKIP_UPSTREAM="$CLONE_PPW/skills/literature-review/deep-research"

# --- plain symlinks ------------------------------------------------------------
LIST="$(mktemp)"
find "$CLONE_PPW/skills" -mindepth 2 -maxdepth 2 -type d \
     -exec test -f "{}/SKILL.md" \; -print 2>/dev/null | sort > "$LIST"
find "$CLONE_ARS" -mindepth 1 -maxdepth 1 -type d \
     -exec test -f "{}/SKILL.md" \; -print 2>/dev/null | sort >> "$LIST"
find "$CLONE_KARPATHY/skills" -mindepth 1 -maxdepth 1 -type d \
     -exec test -f "{}/SKILL.md" \; -print 2>/dev/null | sort >> "$LIST"

while IFS= read -r up; do
  [ -n "$up" ] || continue
  name="$(basename "$up")"
  is_wrapper "$name" && continue
  [ "$up" = "$SKIP_UPSTREAM" ] && continue
  dest="$SKILLS_DIR/$name"
  want="$(rel "$up")"
  if [ -L "$dest" ] && [ "$(readlink "$dest")" = "$want" ]; then continue; fi
  if [ -e "$dest" ] || [ -L "$dest" ]; then
    if [ "$CHECK" = 1 ]; then note "would replace $name (not a plain symlink)"; continue; fi
    rm -f "$dest"        # -f on a symlink removes the link, never the target
  fi
  ln -s "$want" "$dest"
  note "linked  $name"
done < "$LIST"
rm -f "$LIST"

# --- wrapper dirs --------------------------------------------------------------
echo "$WRAPPERS" | while IFS='|' read -r name up_rel; do
  [ -n "$name" ] || continue
  up="$ROOT/$up_rel"
  [ -f "$up/SKILL.md" ] || { echo "WARN: upstream missing for $name ($up_rel)"; continue; }
  dest="$SKILLS_DIR/$name"

  if [ ! -d "$dest" ] || [ -L "$dest" ]; then
    if [ "$CHECK" = 1 ]; then note "would rebuild wrapper $name"; continue; fi
    if [ -L "$dest" ]; then rm -f "$dest"; fi
    rm -rf "$dest"
    mkdir -p "$dest"
    note "wrapper $name"
  fi

  want_skill="$(relw "$up_rel")/SKILL.md"
  if [ ! -L "$dest/SKILL.md" ] || [ "$(readlink "$dest/SKILL.md")" != "$want_skill" ]; then
    if [ "$CHECK" = 1 ]; then note "would link $name/SKILL.md"; continue; fi
    rm -f "$dest/SKILL.md"
    ln -s "$want_skill" "$dest/SKILL.md"
    note "link    $name/SKILL.md"
  fi

  for sub in "$up"/*/; do
    [ -d "$sub" ] || continue
    sname="$(basename "$sub")"
    want="$(relw "$up_rel")/$sname"
    if [ -L "$dest/$sname" ] && [ "$(readlink "$dest/$sname")" = "$want" ]; then continue; fi
    if [ "$CHECK" = 1 ]; then note "would link $name/$sname"; continue; fi
    rm -rf "$dest/$sname"
    ln -s "$want" "$dest/$sname"
    note "link    $name/$sname"
  done
done

# --- extra links ---------------------------------------------------------------
echo "$EXTRAS" | while IFS='|' read -r name lname target; do
  [ -n "$name" ] || continue
  dest="$SKILLS_DIR/$name"
  [ -d "$dest" ] || continue
  want="$(relw "$target")"
  if [ -L "$dest/$lname" ] && [ "$(readlink "$dest/$lname")" = "$want" ]; then continue; fi
  if [ "$CHECK" = 1 ]; then note "would link $name/$lname"; continue; fi
  rm -rf "$dest/$lname"
  ln -s "$want" "$dest/$lname"
  note "link    $name/$lname"
done

# --- shared references dirs ----------------------------------------------------
# `../shared-references/<file>.md` from a skill means <skills-root>/shared-references/.
# The `../../references/<file>.md` form (used by some upstream skills) means
# <project>/.claude/references/, which points at the ppw family's shared tree.
if [ ! -e "$SKILLS_DIR/shared-references" ]; then
  if [ "$CHECK" = 1 ]; then note "would link shared-references"; else
    ln -s "../../shared-references" "$SKILLS_DIR/shared-references"
    note "link    shared-references"
  fi
fi

# `../../references/<file>.md` from a skill dir -> <project>/.claude/references/
if [ ! -e "$ROOT/.claude/references" ]; then
  if [ "$CHECK" = 1 ]; then note "would link .claude/references"; else
    ln -s "../claude-code-paper-writing/skills/writing-polish/paper-polish-workflow/references" \
         "$ROOT/.claude/references"
    note "link    .claude/references"
  fi
fi

echo
if [ "$CHECK" = 1 ]; then echo "check complete (differences listed above)"; else echo "sync complete"; fi
