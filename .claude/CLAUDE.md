# Project context — Academic Research Skills (ARS)

The ARS suite is installed here as Claude Code **project skills** (the "skills-copy" channel).
Upstream: https://github.com/Imbad0202/academic-research-skills — suite v3.24.0, CC-BY-NC-4.0.

## Where the ARS repository lives

The suite is installed from a git clone kept inside this project:

```
academic-research-skills/
```

`.claude/skills/<skill>` are symlinks into that clone, and `.claude/skills/{shared,scripts,docs}`
plus `MODE_REGISTRY.md` are symlinks to the clone's repository-root entries. Keep the clone:
several skills shell out to Python under `academic-research-skills/scripts/` and read schemas
under `academic-research-skills/shared/`.

**Resolving repository-root-relative paths.** Skill instructions name repository-root files
without a prefix — e.g. `shared/references/routing_core.md`, `scripts/run_ledger.py`. Resolve
those against the clone root, not the project root:

```
shared/references/routing_core.md  ->  academic-research-skills/shared/references/routing_core.md
scripts/run_ledger.py             ->  academic-research-skills/scripts/run_ledger.py
```

## Installed skills

| Skill | Path | Modes |
|---|---|---|
| `deep-research` | `.claude/skills/deep-research/` | full, quick, socratic, review, lit-review, three-way-scan, fact-check, systematic-review |
| `academic-paper` | `.claude/skills/academic-paper/` | full, plan, outline-only, revision, revision-coach, abstract-only, lit-review, format-convert, citation-check, disclosure, rebuttal-audit |
| `academic-paper-reviewer` | `.claude/skills/academic-paper-reviewer/` | full, re-review, quick, methodology-focus, guided, calibration |
| `academic-pipeline` | `.claude/skills/academic-pipeline/` | orchestrates research -> write -> integrity check -> review -> revise -> re-review -> finalize |
| `sr-screener` | `.claude/skills/sr-screener/` | protocol, quick, pilot, ta-screen, ft-screen, adjudicate, audit, report |

Supporting agent: `.claude/agents/screening_reviewer_agent.md`, required by `sr-screener` for
dual-review screening runs.

## Paper-writing skills (Chanw repo)

A second suite is installed here from a clone kept inside this project:

```
claude-code-paper-writing/
```

Upstream: https://github.com/Chanw-research/claude-code-paper-writing — curated skills across
7 categories (literature-review, figures, data-analysis, slides, document-handling,
writing-polish, paper-discipline).

### How the wiring works

`.claude/skills/<name>` has two shapes, both of which keep tracking `git pull`:

- **plain** — a symlink straight to the upstream skill directory (95 skills).
- **wrapper** — a real directory whose `SKILL.md` is a symlink to the upstream `SKILL.md`,
  plus symlinks to the upstream `references/`, `scripts/` and `assets/` subdirectories
  (16 skills: the 14 `ppw-*`, `deep-research-lit`, `comm-lit-review`). Wrappers exist where
  the skill needs a local file upstream does not ship — chiefly the `ppw` family's shared
  `references/` tree.

Rebuild the wiring with `bash scripts/sync_skills.sh` (add `--check` to report differences
without changing anything).

**Claude Code identifies a project skill by its DIRECTORY name, not by the frontmatter
`name:` field.** Upstream's `ppw:caption` therefore needs no rewriting: the skill is invoked
as `ppw-caption` while the skill list shows `ppw-caption (ppw:caption)`. Three upstream names
are still installed under a different directory name, to avoid a collision or a colon:

| Installed as | Upstream | Why |
|---|---|---|
| `deep-research-lit` | `deep-research` | `deep-research` is already the ARS skill above |
| `ppw-abstract` … `ppw-visualization` (14) | `ppw:abstract` … | upstream nests these inside `paper-polish-workflow/.claude/skills/`, which Claude Code does not discover; the `ppw:` namespace also contains a colon |
| `comm-lit-review` | `comm-lit-review-claude-single` | upstream frontmatter name differs from its directory name |

`edit` is a local standalone skill (a research-wiki helper that adds or removes `raw/` sources
and updates `wiki/` pages). It comes from neither repo and has no upstream to pull from.

### Local patches to that clone

`git -C claude-code-paper-writing diff` shows them; `git checkout -- <path>` reverts one.
They are all upstream defects:

- `plotly/SKILL.md` linked `reference/` where the files live under `references/`.
- Four `literature-review/*/SKILL.md` files began with a UTF-8 BOM that can break frontmatter
  parsing.
- `deep-research` (`skills/literature-review/deep-research/`) referenced `/Users/lingzhi/...`
  absolute paths from another machine; those now point at `scripts/`, `references/` and
  `tools/paper_finder.py` in this project.
- `literature-review/SKILL.md` and `figure-generation/SKILL.md` linked skill directories that
  upstream never created (`../literature-search/`, `../data-analysis/`, …); those now link the
  installed equivalents.
- `alphaxiv/SKILL.md` and `prior-art-search/SKILL.md` gained concrete fetch commands
  (see the Scrapling section).

### Shared references

`../shared-references/<file>.md` from a skill means `.claude/skills/shared-references/`, a
symlink to `shared-references/` in the project root. Three files are copied verbatim from
upstream (`academic-writing.md`, `citation-verification.md`, `cross-model-review.md`); the
other thirteen were never published upstream and are **honest placeholders** — each states
that it is unpublished and points at the guidance that actually governs the behaviour. Do not
treat them as upstream policy.

## Coding guidelines (Karpathy repo)

A third suite, installed the same way — git clone inside the project, symlink into
`.claude/skills/`:

```
andrej-karpathy-skills/
```

Upstream: https://github.com/multica-ai/andrej-karpathy-skills — one skill, MIT.

| Skill | Path | Notes |
|---|---|---|
| `karpathy-guidelines` | `andrej-karpathy-skills/skills/karpathy-guidelines/` | plain symlink; the skill ships a single `SKILL.md` |

It is a **plain** entry — the upstream skill directory holds only `SKILL.md`, with no
`references/`, `scripts/` or `assets/` subdirectories, so no wrapper is needed.

Upstream also publishes a plugin marketplace (`karpathy-skills`) and a per-project
`CLAUDE.md` install path. Neither is used here: this project uses the skills-copy
channel, so the repo carries its own copy that tracks `git pull` and does not depend
on a marketplace install:

```
git -C andrej-karpathy-skills pull
```

Two upstream files are deliberately **not** wired in:

- `andrej-karpathy-skills/CLAUDE.md` — the same guidelines as the skill's `SKILL.md`,
  but as a root `CLAUDE.md`. Claude Code loads only the project-root `CLAUDE.md` and
  `.claude/CLAUDE.md`, so this copy is never read. The same guidelines are already
  in force via the user's global `~/.claude/CLAUDE.md`, which carries them verbatim.
- `.cursor/rules/karpathy-guidelines.mdc` — a Cursor rule, inert under Claude Code.

The same skill is also reachable at user scope, as `~/.claude/skills/karpathy-guidelines`.
That entry is a **symlink to the same clone target**, not a second copy, and it has to
be: Claude Code resolves a shared skill name with *personal* scope beating *project*
scope, so a separate copy at user scope would shadow this repo's and `git pull` updates
would never reach the invoked skill. Pointing both entries at one target makes Claude
Code load the skill once ("loads the skill once even if several locations point at the
same target"). The trade-off is that the global entry depends on this project folder
existing.

The standalone copy that was previously installed at user scope is kept at
`~/.claude/backups/skills/karpathy-guidelines/` for reference; its content was
byte-identical to the clone.

## Project tools (`tools/`)

`tools/` is the project-root directory the skills reference (`tools/research_wiki.py`,
`tools/semantic_scholar_fetch.py`, …). It mixes symlinks into the upstream
`empirical-research-notes/empirical-wiki/tools/` with locally written tools that upstream
never published. Run them from the project root.

Locally written: `web_fetch.py` (Scrapling), `paper_finder.py` (OpenReview), `install_aris.sh`,
`save_trace.sh`, `verify_paper_audits.sh`, `extract_paper_style.py`, plus the literature
fetchers `arxiv_fetch.py`, `semantic_scholar_fetch.py`, `deepxiv_fetch.py`, `exa_search.py`,
`openalex_fetch.py`.

## Verifying the install

```bash
.venv/bin/python scripts/verify_skills.py      # every skill reference resolves?
bash scripts/sync_skills.sh --check             # is the wiring still in shape?
```

Four references remain unresolved, all benign: two example images in `nature-figure`'s
tutorials, one path inside a JSON schema example, and one duplicate copy of `ppw-update` that
resolves through its installed path.

## Web scraping — Scrapling

Installed for all kinds of web scraping (HTTP, adaptive parsing, stealth browser, crawl, MCP).

- Virtualenv: `.venv/` (Python 3.12, from pyenv `3.12.0`), `scrapling[all]` 0.5.
- Browsers: Chromium via `playwright` + `patchright`, in `~/Library/Caches/ms-playwright`.
- MCP server: registered in `.mcp.json` as `scrapling` (`scrapling mcp`, stdio). 16 tools:
  `make_request`, `browser_open`, `browser_fetch`, `browser_extract`, `browser_actions`,
  `browser_evaluate`, `browser_screenshot`, `browser_network_requests`, session management.

**Always run Scrapling with `.venv/bin/`** — the venv is not on `PATH`:

```bash
.venv/bin/python -c "from scrapling.fetchers import Fetcher; print(Fetcher.get('https://example.com').status)"
.venv/bin/scrapling extract get 'https://quotes.toscrape.com/' out.md --css-selector '.quote'
```

Python API: `scrapling.fetchers` (`Fetcher`, `FetcherSession`, `StealthyFetcher`, `StealthySession`),
`scrapling.parser.Selector`, `scrapling.spiders.Spider`. Async variants live in the same module.

**Timeout units differ by fetcher** (Scrapling 0.5): HTTP fetchers take **seconds**
(`timeout=30`), browser fetchers pass the value straight to Playwright and take
**milliseconds** (`timeout=60000`). Passing `timeout=60` to a browser fetcher means 60 ms.

### The shared fetch tool

`tools/web_fetch.py` is the entry point the skills use. It re-execs itself into `.venv/bin/python`
when Scrapling is not importable, so skills can call `python3 tools/web_fetch.py` unchanged.

```bash
python3 tools/web_fetch.py 'https://example.com' --css-selector 'h1'
python3 tools/web_fetch.py 'https://example.com' --markdown --output page.md
python3 tools/web_fetch.py 'https://espacenet.com/...' --browser --solve-cloudflare
```

`--browser` drives the stealth Chromium; `--solve-cloudflare` is opt-in and only needed for
Cloudflare-protected sites (Espacenet). Exit codes: 0 ok, 1 fetch failure, 2 usage, 3 HTTP >= 400.

### Where Scrapling is (and is not) used

- **Used** where a page is JS-rendered or bot-protected: `prior-art-search` (Espacenet,
  Google Patents), `alphaxiv`, `edit`, and `paper_finder` (openreview.net answers
  unauthenticated API calls with `403 ChallengeRequiredError`, so `tools/paper_finder.py`
  reads the rendered venue page through the stealth browser).
- **Not used** for JSON/XML APIs — arXiv, Semantic Scholar, OpenAlex, Crossref and Exa are
  plain HTTP. Those clients carry rate limits, host allowlists and degradation contracts that
  a scraper would only break.
- **Not used anywhere in `academic-research-skills/`.** That suite documents an explicit
  zero-scraping policy (`deep-research/references/chinese_literature_api_protocol.md`: "Zero
  scraping"), and its CI lints every network-touching script into `docs/DATA_FLOWS.md`.
  The ARS clone is deliberately untouched by any scraping change.

Reinstall or repair:

```bash
uv pip install --python .venv/bin/python "scrapling[all]" && .venv/bin/scrapling install
```

Not wired in this install channel (upstream `docs/CONTROL_AVAILABILITY.md` note 3): the plugin
`PreToolUse` write-scope guard, the SessionStart announce, the `/ars-*` slash commands, and the
plugin agents' tool allowlists. Invoke the skills by their natural-language triggers.

Update the suite with:

```
git -C academic-research-skills pull
```

---
## Routing Discipline (v3.9.2)

**Routing precedence:** This section runs BEFORE Routing Rules 1-5. Once this section settles on a destination, Rules 1-5 apply within that destination's skill family.

The routing core below is the same block as `shared/references/routing_core.md`, which carries it to plugin installs (SessionStart announce) and to every install path (the five `SKILL.md` files), because Claude Code loads this file only for sessions started inside the checkout (#892). `scripts/check_routing_core_sync.py` keeps the copies identical.

<!-- routing-core:begin -->
**Step 0 — Escape hatch check (before any classification):** If the user's first message begins with `[direct-mode]` (case-insensitive byte-0 token, optionally preceded by whitespace/newlines that are stripped on parse), record this fact, strip the prefix and surrounding whitespace from the message, and skip directly to **Step 1 explicit-intent handling** on the stripped content. The literal `[direct-mode]` is NOT passed through to the dispatched agent. If the stripped message itself has no clear skill named, Step 1 falls through to Step 3 clarification (the escape hatch bypasses cross-phase clarification (Step 2), not all routing). When the token is honored and the named agent or skill needs inputs the message does not supply, read that agent's or skill's file and ask for what it requires, in its terms. A `[direct-mode]` token after any other non-whitespace character is not the escape hatch, even when the message asks to skip questions: classify the message through Steps 1-3 as if the token were absent, and do not forward the token. Without the byte-0 token, naming an agent is not explicit intent: such a message goes through Steps 1-3 like any other, so cross-phase materials still get Step 2 clarification.

Otherwise, classify the user's input:

1. **Explicit clear intent** — user invokes a specific skill via `/ars-*` slash command, or uses an unambiguous trigger keyword that maps to a single skill (e.g., "lit-review this", "review my paper", "draft an abstract"):
   → Route directly; no clarification, no orchestrator detour.
   → The request stays explicit when the mode's usual input is absent or a word in it has other everyday senses. A revision request with no reviewer comments is revision mode's "feel certain sections need improvement" case, and "revisar artículo" is the reviewer's trigger. Route to that mode and let the mode handle what is missing; do not reopen the choice of workflow.

2. **Cross-phase materials detected** — user provides artifacts spanning ≥ 2 pipeline phases without naming a specific skill (e.g., pre-written abstract + pre-collected literature; full draft + reviewer comments + bibliography):
   → **Clarify**. Do NOT auto-route to a single-phase agent. List candidate workflows as a-d options in markdown body (NOT via AskUserQuestion tool). See `shared/references/intent_clarification_protocol.md` for the message template.
   → Reason: clarification is the safest action when materials don't unambiguously identify intent. (v3.10 active conductor (#134) will handle this via structured intake; v3.9.2 asks.)

3. **Ambiguous intent, no materials** — user provides no artifacts and no clear request:
   → Clarify per `shared/references/intent_clarification_protocol.md`.

**Screening boundary (sr-screener):** a request to screen records the user already has (database exports, pasted abstracts, full-text PDFs) against a review's eligibility criteria, or to build a screening protocol, pilot the screening, adjudicate screening conflicts, audit exclusions, or report the selection counts, routes to `sr-screener`. A request to write a literature review, or to run a systematic review, meta-analysis, or PRISMA report, does not route to `sr-screener`. Screening starts only when the user asks for it: `deep-research` `systematic-review` mode may mention `sr-screener`, but never hands over to it automatically.

**Anti-pattern (caused #133):** Receiving ambiguous cross-phase materials and silently auto-routing to a single-phase agent based on which phase the materials "look closest to." This bypasses orchestrator-level reconciliation and lets the subagent inherit the full ambiguity without independent oversight.
<!-- routing-core:end -->

**Forward note (v3.10):** Active conductor (#134) will reframe this gate as structured intake with task envelope dispatch. v3.9.2 ships clarification-only as interim hot-fix.

## Routing Rules

1. **academic-pipeline vs individual skills**: academic-pipeline = full pipeline orchestrator (research → write → integrity → review → revise → final integrity → finalize). If the user only needs a single function (just research, just write, just review), trigger the corresponding skill directly without the pipeline.

2. **deep-research vs academic-paper**: Complementary. deep-research = upstream research engine (investigation + fact-checking), academic-paper = downstream publication engine (paper writing + bilingual abstracts). Recommended flow: deep-research → academic-paper.

3. **deep-research socratic vs full**: socratic = guided Socratic dialogue to help users clarify their research question. full = direct production of research report. When the user's research question is unclear, suggest socratic mode.

4. **academic-paper plan vs full**: plan = chapter-by-chapter guided planning via Socratic dialogue. full = direct paper production. When the user wants to think through their paper structure, suggest plan mode.

5. **academic-paper-reviewer guided vs full**: guided = Socratic review that engages the author in dialogue about issues. full = standard multi-perspective review report. When the user wants to learn from the review, suggest guided mode.

6. **rebuttal-audit vs revision-coach (input-shape gate)**: both touch reviewer comments, so route by INPUT SHAPE, not verbs. Route to `academic-paper rebuttal-audit` ONLY when the user supplies BOTH the reviewer comments AND an existing rebuttal/response draft to evaluate (it does advisory QA, generates nothing). If only reviewer comments are present (no draft yet), route to `revision-coach` (it generates a Response Letter Skeleton). If unclear which, clarify rather than guess. `rebuttal-audit` is standalone/advisory and never emits Schema 11 or marks anything verified.
7. **real-committee correspondence vs peer review (#668)**: route to the `revision-coach` committee-correspondence variant only when the user explicitly identifies a real committee or institutional review office. Formal tone and words such as “required” do not establish authority. That branch loads `academic-paper/references/committee_correspondence_protocol.md`, preserves the source, and emits its separate concern tracker; it never emits reviewer priority/severity, Schema 11, a determination, or a resolution claim.
8. **sr-screener vs deep-research systematic-review**: route to `sr-screener` when the user wants eligibility decisions on records they already have (database exports, pasted abstracts, full-text PDFs), or a screening protocol, pilot, conflict adjudication, exclusion audit, or selection-process report. Route to `deep-research` `systematic-review` when the user wants the review itself (question, search, synthesis, PRISMA report). A bare "systematic review" or "PRISMA" request stays with `deep-research`; PRISMA flow numbers for a finished screening go to `sr-screener` `report`. `sr-screener` owns screening decisions; the other skills read its `literature_corpus[]` output and do not re-screen it. Screening starts only when the user asks for it; `systematic-review` mode never hands over to `sr-screener` automatically (routing core, Screening boundary).

## Key Rules

- All claims must have citations
- Evidence hierarchy respected (meta-analyses > RCTs > cohort > case reports > expert opinion)
- Contradictions disclosed with evidence quality comparison
- AI disclosure in all reports
- Default output language matches user input (Traditional Chinese or English)

## Full Academic Pipeline

```
deep-research (socratic/full)
  → academic-paper (plan/full)
    → integrity check (Stage 2.5)
      → academic-paper-reviewer (full/guided)
        → academic-paper (revision)
          → academic-paper-reviewer (re-review, max 2 loops)
            → final integrity check (Stage 4.5)
              → academic-paper (format-convert → final output)
                → Process Summary + AI Self-Reflection Report
```

## Handoff Protocol

### deep-research → academic-paper
Materials: RQ Brief, Methodology Blueprint, Annotated Bibliography, Synthesis Report, INSIGHT Collection

### academic-paper → academic-paper-reviewer
Materials: Complete paper text. field_analyst_agent auto-detects domain and configures reviewers.

### academic-paper-reviewer → academic-paper (revision)
Materials: Editorial Decision Letter, Revision Roadmap, Per-reviewer detailed comments

### deep-research → sr-screener → academic-paper (systematic reviews)
Materials in: screening protocol source (proposal, PROSPERO record, or `systematic-review` mode protocol), database exports (RIS, PubMed .nbib, Web of Science, CSV), full-text PDFs. Materials out: `*_literature_corpus.yaml` (`literature_corpus[]` entries for the Material Passport), PRISMA 2020 counts, methods draft, exclusion reasons, screening log.

## Version Info
- **Suite version**: 3.24.0 (per CHANGELOG.md)
- **Last Updated**: 2026-10-27
- **Author**: Cheng-I Wu
- **License**: CC-BY-NC 4.0
- **Local wiring layer** (this project, 2026-10-31): all three skill suites rewired to track
  `git pull`; `tools/`, `shared-references/`, and the Scrapling install added. The ARS
  upstream suite itself is unmodified — see `git -C academic-research-skills status`.
