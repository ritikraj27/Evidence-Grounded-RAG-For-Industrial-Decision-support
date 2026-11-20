# Wiki Helper Resolution

> **Status: not published upstream.** This file is referenced by 6 installed skills
> (`alphaxiv`, `arxiv`, `deepxiv`, `exa-search`, `research-lit`, `semantic-scholar`), but the upstream suite
> `github.com/Chanw-research/claude-code-paper-writing` never published it. This
> document was written locally to keep those references resolvable; it does not
> restate upstream policy.

> **中文摘要：** 本文档是本地补写的指针，上游从未发布。按 canonical chain 解析 `$WIKI_SCRIPT`；找不到则打印 WARN、置空、跳过 wiki 步骤，但技能本身照常完成。

## What this reference governs

The 6 sites are the "Update Research Wiki" steps of the literature-search skills. Each
one says to resolve `$WIKI_SCRIPT` "per the canonical chain" at this reference, and each
names the behaviour it wants: "Variant B — warn-and-skip"
(`arxiv/SKILL.md:185`, `alphaxiv/SKILL.md:131`, `deepxiv/SKILL.md:197`,
`exa-search/SKILL.md:148`, `research-lit/SKILL.md:369`,
`semantic-scholar/SKILL.md:159`). The reference is expected to define the canonical
chain of candidate locations for the helper, plus the variants (at least a "warn-and-skip"
one; the skills name it "Variant B", implying a Variant A exists).

**What could not be determined from the referencing skills:** the "Variant A" behaviour is
never described anywhere in this install — only "Variant B — warn-and-skip" appears. The
resolution chain itself is fully recoverable and is reproduced below.

## Where the operative guidance actually lives

The chain is written out inline, identically, in all 6 referencing skills — read it there
rather than trusting a paraphrase:

```bash
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" || exit 1
ARIS_REPO="${ARIS_REPO:-$(awk -F'\t' '$1=="repo_root"{print $2; exit}' .aris/installed-skills.txt 2>/dev/null)}"
WIKI_SCRIPT=".aris/tools/research_wiki.py"
[ -f "$WIKI_SCRIPT" ] || WIKI_SCRIPT="tools/research_wiki.py"
[ -f "$WIKI_SCRIPT" ] || { [ -n "${ARIS_REPO:-}" ] && WIKI_SCRIPT="$ARIS_REPO/tools/research_wiki.py"; }
[ -f "$WIKI_SCRIPT" ] || {
  echo "WARN: research_wiki.py not found; ... wiki ingest will be skipped. Fix: bash tools/install_aris.sh, export ARIS_REPO, or cp <ARIS-repo>/tools/research_wiki.py tools/." >&2
  WIKI_SCRIPT=""
}
```

In this install, `tools/research_wiki.py` exists as a symlink into the EmpiricalWiki
clone, so the second candidate resolves. `integration-contract.md` governs what to do
with the helper once it is found.

## How to proceed

1. Run the chain above, in order, from the repo root. It is the canonical order.
2. Variant B behaviour when the helper is not found anywhere: print the WARN line to
   stderr, set `WIKI_SCRIPT=""`, skip the wiki step, and **continue the skill's own
   work** — arXiv results, literature synthesis, or the single-paper read are still
   reported. Never abort the skill because the wiki helper is missing.
3. Never hand-write `papers/<slug>.md` as a fallback; see `integration-contract.md`.
4. If a paper was missed, backfill with
   `python3 "$WIKI_SCRIPT" sync research-wiki/ --arxiv-ids <id1>,<id2>,...` once the
   helper is available.
