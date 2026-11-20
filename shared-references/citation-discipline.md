# Citation Discipline

> **Status: not published upstream.** This file is referenced by 4 sites across 2 installed skills
> (`citation-audit`, `paper-write`), but the upstream suite
> `github.com/Chanw-research/claude-code-paper-writing` never published it. This
> document was written locally to keep those references resolvable; it does not
> restate upstream policy.

> **中文摘要：** 本文档是本地补写的指针，上游从未发布。先走 DBLP → CrossRef 链路；仍取不到则标 `% [VERIFY]`，绝不编造条目或元数据。

## What this reference governs

`paper-write/SKILL.md:36` loads it "only when the built-in DBLP/CrossRef workflow is
insufficient", and `paper-write/SKILL.md:307` repeats that as "load
`citation-discipline.md` for stricter fallback rules before adding placeholders".
`paper-write/SKILL.md:561` scopes it as "stricter fallback for ambiguous citations";
`citation-audit/SKILL.md:492` scopes it as the "protocol document for citation
hygiene". It is therefore the fallback tier below the in-skill DBLP → CrossRef → `[VERIFY]`
chain: what to do when an entry cannot be verified.

## Where the operative guidance actually lives

- **`.claude/skills/paper-write/SKILL.md:283-307`** — the in-skill chain this reference
  extends: Step A DBLP (`dblp.org/search/publ/api` → `dblp.org/rec/{key}.bib`), Step B
  CrossRef DOI (`curl -H "Accept: application/x-bibtex" https://doi.org/{doi}`), Step C
  mark `% [VERIFY]` and do not fabricate. Follow this chain first; reach for this
  reference only when it comes up empty.
- **`.claude/skills/conference-paper-writing/references/citation-workflow.md`** — the real
  citation-hygiene document in this install: the 5-step verified workflow, API selection
  guide, BibTeX vs BibLaTeX, citation-key conventions, a verification checklist, and
  common citation formats.
- **`.claude/skills/citation-audit/SKILL.md`** — the audit protocol: per-entry verdicts
  `KEEP / FIX / REPLACE / REMOVE` across three axes (EXISTENCE, METADATA, CONTEXT), the
  `--uncited` opt-in, and the known-limitations notes (DBLP's ~2-week coverage gap,
  preprint-vs-published preference, Anthology vs OpenReview).
- **`shared-references/citation-verification.md`** — the **published upstream** document
  that states the same discipline for the sibling EmpiricalWiki suite: authoritative
  sources only (DBLP → CrossRef → Semantic Scholar), the `UNCONFIRMED_` key prefix and
  `% [UNCONFIRMED]` comment, the citation-key convention, and a hard blocker on
  submitting with unmarked entries. Read it for the reasoning and the marker mechanics;
  note that this suite's marker is `% [VERIFY]`, not `[UNCONFIRMED]`.

## How to proceed

1. Run the in-skill DBLP → CrossRef chain first. That is the normal path.
2. If it comes up empty, do **not** fabricate. Mark the entry `% [VERIFY]` with whatever
   metadata you have, and flag it — `paper-write/SKILL.md` lists "No `[VERIFY]` markers
   left unchecked" as a pre-flight item, and `citation-audit` will `REMOVE` a hallucinated
   entry.
3. Never write an entry that is not actually cited, and never use `\nocite{*}`; `paper-write`
   filters `references.bib` down to the cited keys only.
4. For the mechanics of an unverified marker, `shared-references/citation-verification.md`
   is the closest published precedent — but keep this suite's `% [VERIFY]` spelling.
