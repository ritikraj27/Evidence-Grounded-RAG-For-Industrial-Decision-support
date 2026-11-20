# Prior Art Databases

> **Status: not published upstream.** This file is referenced by 1 installed skill
> (`prior-art-search`), but the upstream suite
> `github.com/Chanw-research/claude-code-paper-writing` never published it. This
> document was written locally to keep those references resolvable; it does not
> restate upstream policy.

> **中文摘要：** 本文档是本地补写的指针，上游从未发布。数据库清单见 `prior-art-search` 自身；IPC／CPC 编码表无法从安装内容还原，须查真实专利文档核实，不可凭记忆臆造。

## What this reference governs

`prior-art-search/SKILL.md:30` is the only reference site: "Load
`prior-art-databases.md` for search strategy templates and IPC/CPC classification
guidance." The reference is expected to supply (a) the set of patent and academic
databases to search and how to query each, (b) search-strategy templates, and (c) an
IPC/CPC classification guide for predicting and organising results.

**What could not be determined from the referencing skills:** the referencing skill
already names its own databases and access methods in full — `PATENT_DATABASES =
"google-patents, espacenet"` (`prior-art-search/SKILL.md:19`), Google Patents via
`WebSearch "site:patents.google.com ..."`, Espacenet via `WebFetch`, Google Scholar via
`WebSearch`, plus arXiv and Semantic Scholar (`prior-art-search/SKILL.md:46-75`). It
also states the IPC/CPC expectation as a *predict-then-record* step
(`prior-art-search/SKILL.md:40, 57, 65, 89`) with only the examples `G06N` and `G06F`.
No IPC/CPC code table exists anywhere in this install — **the classification guide
cannot be recovered from the referencing skills**, and inventing a code list would
produce confident-looking but unverifiable classification codes.

## Where the operative guidance actually lives

- **`.claude/skills/prior-art-search/SKILL.md`** — the database list, the per-database
  query syntax, the search-concept extraction step, the overlap-risk scale
  (HIGH/MEDIUM/LOW), the freedom-to-operate assessment, and the `PRIOR_ART_REPORT.md`
  output template. This is the operative guidance in this install.
- `.claude/skills/arxiv/SKILL.md` and `.claude/skills/semantic-scholar/SKILL.md` — the
  academic-source skills `prior-art-search` delegates to for arXiv and Semantic Scholar.
- `.claude/skills/conference-paper-writing/references/citation-workflow.md` — the
  general source-verification approach (authoritative sources, no fabrication) that
  applies to the academic half of the search.

## How to proceed

1. Use the databases and query syntax exactly as `prior-art-search/SKILL.md` specifies —
   that list is complete for this install.
2. For IPC/CPC codes, **predict and verify rather than recall**. Search
   `patents.google.com` for a representative patent in the area and read the codes it
   actually carries; report only codes you have seen on a real document. If no code can
   be confirmed, say so instead of guessing.
3. Never fabricate patent numbers or citations. Mark anything uncertain with `[VERIFY]`,
   per the skill's key rules, and keep the disclaimer that this is a preliminary
   assessment, not a freedom-to-operate opinion.
4. Report the databases actually searched in `PRIOR_ART_REPORT.md`, so the reader can
   judge coverage.
