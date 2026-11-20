# Integration Contract (research-wiki ingest)

> **Status: not published upstream.** This file is referenced by 6 installed skills
> (`arxiv`, `alphaxiv`, `deepxiv`, `exa-search`, `research-lit`, `semantic-scholar`), but the upstream suite
> `github.com/Chanw-research/claude-code-paper-writing` never published it. This
> document was written locally to keep those references resolvable; it does not
> restate upstream policy.

> **中文摘要：** 本文档是本地补写的指针，上游从未发布。核心规则：业务逻辑在 `tools/research_wiki.py`，不得手写 `papers/<slug>.md`；辅助脚本不可达时记录缺口，留待 `sync` 回补。

## What this reference governs

The 6 sites are all "Update Research Wiki" steps. `research-lit/SKILL.md:363` states the
contract explicitly: "this step follows the canonical ingest contract — business logic
lives in `tools/research_wiki.py`, not in this prose." Each of the other 5 sites repeats
the operative clauses: the helper owns metadata fetch, slug generation, dedup, page
creation, index rebuild, query-pack rebuild, and log append, and agents must **not**
hand-write `papers/<slug>.md`. The reference is the canonical statement of that rule.

## Where the operative guidance actually lives

- `tools/research_wiki.py` — the canonical helper the contract defers to. Read its
  `--help` / docstring for the real subcommand surface (`ingest_paper`, `add_edge`,
  `sync`).
- The `## Update Research Wiki` step in each of the 6 referencing skills, which spells
  out the same contract inline: `.claude/skills/arxiv/SKILL.md`,
  `.claude/skills/alphaxiv/SKILL.md`, `.claude/skills/deepxiv/SKILL.md`,
  `.claude/skills/exa-search/SKILL.md`, `.claude/skills/research-lit/SKILL.md`,
  `.claude/skills/semantic-scholar/SKILL.md`.
- `research-lit/SKILL.md:361-420` is the most complete version — it lists the full
  `ingest_paper` / `add_edge` call shapes and the manual-metadata fallback for
  non-arXiv sources.

## How to proceed

1. Never hand-write `papers/<slug>.md`. Call `tools/research_wiki.py` and let it own the
   page, the index, the query pack, and the log.
2. Prefer `--arxiv-id` when the source has one (`arxiv`, `alphaxiv`, `deepxiv`, and
   `semantic-scholar` results with `externalIds.ArXiv`). Use the manual
   `--title/--authors/--year/--venue` form otherwise (`exa-search` web hits, IEEE/ACM
   venue-only papers).
3. Add edges for real relationships with `add_edge --from/--to/--type/--evidence`; an
   edge without evidence is not worth writing.
4. If the helper is unreachable, log the gap and backfill later with
   `python3 "$WIKI_SCRIPT" sync research-wiki/ --arxiv-ids <id1>,<id2>,...` rather than
   hand-editing pages. See `wiki-helper-resolution.md` for how `$WIKI_SCRIPT` is
   resolved.
