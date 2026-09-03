# F-44 — BrowserBase Research → Code Generation Workflow (research-codegen mode)

**Agent 44 of 44 (synthesis-tier, late Wave 2) — 2026-06-29**
**Cross-references:** `synthesis/27-feature-backlog.md` F-08 (the *original* feature brief), `agent-01-dlt.md` (gold-standard 7-section template), `SHARED_DISCOVERY_LOG.md` (29 wave-1 entries, append-only protocol), `synthesis/26-refactor-prioritizer.md` (refactor scoring rubric), `synthesis/29-integration-mapper.md` (cross-package glue gaps), all 8 `refactors/3N-*.md` (the §8 output format that must be implementable).

---

## 1. TL;DR

Stand up a `research-codegen` mode of the existing `research` subagent that takes **(package + version + scope)** and emits a single Markdown that is **the 7-section research report concatenated with an 8th §8 "implementable refactor spec"** — every refactor item is pinned to `file:line` and verified by `ccc:search` so an implementation agent can land it without re-investigation. The new mode is the closing-the-loop for the 43 wave-1 prompts: it automates the Agent 01 / Agent 15 / Agent 19 pattern so any new dependency we adopt gets a versioned research note + a ready-to-execute refactor plan in one BrowserBase session (~25 min wall clock, ~250 credits).

---

## 2. The loop

```
  ┌─────────────┐    1. brief (pkg, version, scope)   ┌──────────────────────┐
  │   user      │ ──────────────────────────────────▶│  research subagent    │
  └─────────────┘                                     │  (new mode: codegen)  │
        ▲                                             └──────────┬───────────┘
        │                                                        │
        │ 6. report (7 sections + §8 implementable refactor)     │ 2. plan (read SHARED_DISCOVERY_LOG
        │                                                        │    + 5 spec deltas, pick 1-3 anchors)
        │                                                        ▼
        │                                            ┌────────────────────────┐
        │                                            │ BrowserBase (Stagehand) │
        │                                            │ + Firecrawl MCP + CCC   │
        │                                            │ + Cognee (cognify)      │
        │                                            └──────────┬─────────────┘
        │                                                       │ 3. extract code patterns
        │                                                       │ 4. cross-ref with SHARED_DISCOVERY_LOG
        │                                                       │ 5. compute file:line refactor anchors
        │                                                       ▼
        │                                            ┌────────────────────────┐
        └────────────────────────────────────────────│  append entry to       │
            (markdown, 7 + §8 + RAGAS every 5th)     │  SHARED_DISCOVERY_LOG  │
                                                     └────────────────────────┘
```

**Step 1 — User brief.** Single line in the agent's normal interface:
> `research-codegen dlt 1.28.1 --scope=ingest,destination,test`

Three positional args (`package`, `version`, `--scope`); the scope flag tells the agent which sub-areas of the package to investigate and which specs in `openspec/specs/` are authoritative (e.g. `--scope=ingest,destination,test` for dlt maps to `oideachais-pipeline` + `meaisínfhoghlaim-platform`).

**Step 2 — Plan (≤2 min, no BrowserBase credits).** Read:
- `SHARED_DISCOVERY_LOG.md` — the 29 wave-1 entries. If the package is already covered (e.g. `dlt` → Agent 01, `BAML` → Agent 15, `Cognee` → Agent 09), the codegen mode **does NOT re-extract**; it inherits the wave-1 findings and **re-verifies them + adds the §8 refactor anchors** (the part the wave-1 agents did not produce). If the package is *not* covered, full extraction as per step 3.
- The 1-3 relevant `openspec/specs/<x>/spec.md` deltas — read the `## ADDED Requirements` and `## MODIFIED Requirements` blocks to learn the contract the refactor must preserve.
- 1 `ccc:search` for the package name to enumerate the 5-50 call sites in `cianfhoghlaim/`.

**Step 3 — Extract (BrowserBase + Firecrawl, ~150 credits).** For *new* packages:
- `firecrawl_scrape(pypi.org/pypi/<pkg>/json, formats=["json"])` for version metadata.
- `firecrawl_scrape(github.com/<org>/<repo>/releases, formats=["json"], jsonOptions.schema={...})` for the 5 most recent release entries.
- `firecrawl_scrape(<repo>/blob/main/docs/<relevant-page>, formats=["branding","markdown"])` for upstream branding + key code blocks.
- For 1-2 JS-rendered SPA pages (e.g. dlt's dashboard docs), use `browserbase_navigate` + `browserbase_extract` (deferred to the `browser` skill only when Firecrawl returns empty).

**Step 4 — Cross-ref.** For every upstream finding, the agent does a `ccc:search` for the local code that owns it and emits a row in the §2 "Code" table with **two columns**: upstream URL/repo path + downstream `file:line`. Example (from Agent 01, reproduced as the row format codegen will follow):

```markdown
| Upstream (`dlt-hub/dlt` 1.28.1) | Cianfhoghlaim call site |
|:--|:--|
| `dlt/pipeline.py::run(..., refresh="drop_data")` | `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/ie/education/curriculum.py:19` (string `destination="duckdb"`) |
| `dlt/sources/incremental/__init__.py::Incremental` | `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/cross/upstream/blog_post.py:152` |
| `dlt/destinations/impl/ducklake/__init__.py` | `cianfhoghlaim/docs/legacy/crypteolas/dlt_utils/destinations.py:84` (needs migration per CHANGELOG:177) |
```

**Step 5 — Compute refactor anchors.** The §8 output is a numbered list of *concrete* changes. For each item the agent MUST:
1. `ccc:search "<exact upstream API name>"` — verifies the local call site exists; the search result `file:line` IS the refactor target.
2. `ccc:search "<the anti-pattern we have today>"` — finds every duplicate, all of which become refactor sub-bullets.
3. State the diff in 1 line of pseudocode (no full patch — the implementation agent writes the real diff).

**Step 6 — Emit.** Single Markdown at `openspec/research/2026-06-28-browserbase-program-2/features/44-browserbase-research-codegen.md` (this file is itself the spec, not an instance run). Each *instance run* of the mode lands at `openspec/research/<date>/<pkg>-<version>-<scope-slug>.md` and is appended to `SHARED_DISCOVERY_LOG.md` as a single `## Agent 4N+ — <pkg> (<timestamp>)` block with **5-7 findings + cross-references** (not the full 7-section report — the full report is the file at the new path; the log entry is the index).

---

## 3. Input schema

```yaml
research-codegen:
  package: string           # required, e.g. "dlt", "BAML", "Cognee"
  version: string           # required, semver, e.g. "1.28.1", "0.223.0", "1.0.0"
  scope: list[enum]         # optional, default = ["all"]
    # values:
    #   ingest          — @resource, @source, primary_key, write_disposition
    #   destination     — dlt.destinations.*, MotherDuck, DuckLake, Iceberg
    #   test            — testing helpers, fixtures, asset checks
    #   observability   — Langfuse, RAGAS, MLflow, OpenTelemetry
    #   security        — Infisical, Locket, BetterAuth, PocketID
    #   ui              — TanStack Start, CopilotKit, AG-UI
    #   agent           — Agno, Google ADK, Pydantic AI
    #   knowledge       — Cognee, Graphiti, LanceDB, FalkorDB
    #   pipeline        — Dagster, dlt, CocoIndex
    #   infra           — Docker Compose, Pangolin, Komodo, Garage
    #   all             — every scope (default)
  mode: enum                # optional, default = "codegen"
    # values:
    #   codegen         — full 7 + §8 output (the F-44 default)
    #   delta           — only the new-vs-wave-1 diff (cheaper, ~80 credits)
    #   refactor-only   — skip the 7-section research, only emit §8
  ccc_index_refresh: bool   # default true — rebuild .cocoindex_code before search
  ragas_every: int          # default 5 — run RAGAS on every Nth output for drift
```

**Validation rules the agent enforces before starting:**
1. `package` must match `^[a-zA-Z0-9_-]+$` and have ≥1 `ccc:search` hit (no phantom packages).
2. `version` must resolve on PyPI / GitHub; if not, abort with a clear error — codegen does NOT speculate.
3. `scope` values are intersected with the package's known concerns (e.g. `scope=ui` for a CLI tool returns an error).
4. If `mode=delta` and the package is not in `SHARED_DISCOVERY_LOG.md`, return an error directing the user to `mode=codegen` first.

---

## 4. Output schema

The Markdown file has **8 sections** (7 inherited from the wave-1 template + 1 new):

```markdown
# <package> <version> — research-codegen report
**Mode:** codegen | **Scopes covered:** ingest, destination, test | **Wall clock:** ~22 min | **BrowserBase credits:** ~210

## 1. TL;DR
3-line summary naming the package, the upstream release, and the single most consequential drift for Cianfhoghlaim.

## 2. The loop (code locations)
Markdown table — see §4 step 4 of this spec for the column schema. Minimum 8 rows (one per scope * call site).

## 3. Env (Infisical-backed config keys)
Markdown table — Key | Where | Purpose | Source. Minimum 4 rows; only keys actually used by the code in §2.

## 4. CCC anchors (semantic-code-search queries)
Code block of `ccc:search "..."` queries with their expected hit counts. Each query must match ≥1 call site in §2.

## 5. Drift log (what changed since <upstream-version-or-prior-pass>)
Markdown table — Date | Event | Drift vs prior pass. Last row is always the v4 consolidation (path renames).

## 6. Anti-patterns
Markdown table — # | Anti-pattern | Where we have it (file:line). Minimum 5 rows; each row triggers a §8 item.

## 7. Decision matrix
Markdown table — Decision | Choice | Rationale. Last row: "New refactor item for REFACTORING.md — see §8".

## 8. Implementable refactor spec
Numbered list (5-7 items, every item passes the 3 validation gates in §6 of this spec). Each item:

### 8.N <one-line title>
- **file:line:** `<absolute path>:<line>` (target) — verified by `ccc:search "<exact symbol>"` → 1 hit
- **current state:** the 1-3 lines of code we have today (paste from the file, do not paraphrase)
- **target state:** the 1-3 lines of code we should have (pseudocode is fine, the implementation agent writes the real diff)
- **spec gate:** which `openspec/specs/<x>/spec.md` requirement this preserves (e.g. "oideachais-pipeline §REQ-3 incremental loading")
- **risk:** low | medium | high — 1-line justification
- **effort:** <human-time> (e.g. "30 min", "half-day", "1 day")
- **validation:** how the implementation agent will prove it works (e.g. "uv run pytest tests/_oideachais/dlt_sources/domains/uk/test_crown_deps.py:138 passes")
- **cross-ref:** `## Agent {N} relies on: ...` and `## Conflict with Agent {N}: ...` (the SHARED_DISCOVERY_LOG format)

---
**Next research priority:** one paragraph identifying the next 1-2 agents who should cross-check this (mirrors Agent 01 §7's "Agent 02 should verify ..." pattern).
```

**Why the 8-section shape matters:** the wave-1 agents produced §1-§7 but skipped the cross-reference + the diff-validity step. The implementation agents in `refactors/3N-*.md` then had to *re-investigate* to verify the 7 items per refactor. The §8 schema bakes verification into the research step so the implementation step is purely mechanical.

---

## 5. Cross-agent coordination

The new mode participates in the **append-only SHARED_DISCOVERY_LOG.md** protocol that all 29 wave-1 agents followed. Three concrete integrations:

**(a) Append one entry per instance run.** The new mode appends a `## Agent 4N+ — <package> (<timestamp>)` block to `SHARED_DISCOVERY_LOG.md` using the exact format Agent 06 / Agent 17 / Agent 19 used (see `SHARED_DISCOVERY_LOG.md:10-30,36-56,59-86`). The block contains the 5-7 most surprising findings + `## Agent 4N+ relies on: Agent {X}` + `## Conflict with Agent {X}: ...` lines. **Critical:** the log entry is the *index*, not the full report — the full report lives at `openspec/research/<date>/<pkg>-<version>-<scope-slug>.md`. The log entry links to the full report with a relative path.

**(b) Inherit wave-1 findings when `mode=delta` or `mode=refactor-only`.** The mode reads the relevant `## Agent {N} — <package>` block from `SHARED_DISCOVERY_LOG.md` and treats its findings as **prior knowledge** (does NOT re-extract). This is what makes the program *composable* — Agent 01 spent 110 credits establishing dlt's drift; the codegen mode re-uses that for ~60 credits (just the §8 anchors + 1 verification round). Wave-2/3 agents reading the log see the full lineage.

**(c) Cross-link to related `refactors/3N-*.md` items.** If a §8 refactor item is in the same area as an existing `refactors/3N-*.md` plan (e.g. Agent 01's §8.1 "bump `dlt>=1.0.0` → `dlt[hub]>=1.27.0`" overlaps with `refactors/38-cognee-v1-api-migration.md`'s dependency story), the new entry's `cross-ref` field links the two. This builds a **bidirectional index**: research findings → refactor plan → spec delta → implementation.

**(d) Cognee cognify on the instance run.** After the Markdown is written, the new mode calls `cognee_remember(data=<full markdown body>, dataset_name="research_findings", session_id=<run-id>)` so the 7-section + §8 structure is queryable later (see Agent 09 + the `agent-memory-systems` spec). The `session_id` lets `cognee_improve(session_ids=...)` later apply RAGAS drift weights to the §8 anchors.

**(e) RAGAS every 5th output.** The `ragas_every: 5` config triggers `cognee_recall` + a RAGAS `faithfulness` + `answer_relevance` evaluation on every 5th instance run (e.g. after `celtic-asset-generation`, after `oideachais-baml-schemas`, after `meaisínfhoghlaim-platform`). The RAGAS result is appended to `SHARED_DISCOVERY_LOG.md` as a `## RAGAS drift check (<date>)` block — if `faithfulness < 0.7` on any of the 7 sections, the agent rewrites that section before cognify fires.

---

## 6. Validation (the 3 gates every §8 item must pass)

The §8 output is only useful if the implementation agent can land it without re-investigation. Three hard gates:

**Gate 1 — CCC verifiability.** Each item's `file:line` target must be confirmed by a `ccc:search "<exact symbol or string from the current state line>"` call that returns **exactly 1 hit** at that `file:line`. If the search returns 0 hits, the symbol doesn't exist in our code — the item is wrong. If it returns >1 hit, the item is too generic; the agent must narrow the query (e.g. add the resource name) until it returns exactly 1. The ccc command is the canonical truth — line numbers from `grep` or `find` are not accepted because they don't account for the v4 consolidation renames.

**Gate 2 — Exact diff shape.** The `target state` line must be **syntactically valid Python / TypeScript / TOML / YAML** that the implementation agent can paste and only adjust whitespace. Pseudocode is allowed ONLY when the diff touches >20 lines (rare). The diff must NOT introduce a new dependency (no "also add `foo>=2.0`"); if a new dep is needed, the item is split: one item for the dep bump (which is its own gates-1-2-3-validated refactor), one for the code change.

**Gate 3 — Test or assertion exists.** The `validation` field must name **a specific test file or an executable command** the implementation agent will run to prove the refactor works. Examples:
- `uv run pytest tests/_oideachais/dlt_sources/domains/uk/test_crown_deps.py::test_crown_deps_hints -v`
- `cd infrastructure/stacks/garage && docker compose up -d && curl -sf http://localhost:3903/health | jq .status == "healthy"`
- `bun run ccc:search "dlt.sources.incremental.IncrementalCursorProvider" | wc -l` (must equal 0 before, ≥11 after)

If no test/assertion exists, the agent **first** creates a failing test (TDD-style) and then emits the refactor item that makes it pass. The test creation is itself a §8 sub-item.

**Bonus gate (optional but recommended) — spec delta requirement.** The `spec gate` field is mandatory for items that touch a public API (e.g. bumping `dlt>=1.0.0` requires a delta in `openspec/changes/<id>/specs/oideachais-pipeline/spec.md`). Items that are pure internal refactors (rename, move) skip this gate.

---

## 7. Cutover (integrating into the existing `research` subagent prompt)

The `research` subagent currently lives in two places: the 43 prompt files at `openspec/research/2026-06-28-browserbase-credit-program/phase-{1a,1b,2,3}/<prompt-id>.md` (one per BrowserBase credit-program prompt) and the `browserbase-research-codegen` SKILL.md. The cutover is 3 concrete steps:

**Step 1 — Extend the existing `research` subagent prompt** (the system prompt that drives all 43 wave-1/2/3 prompts). Add a `mode` parameter that selects one of `extract | delta | codegen | refactor-only`, and gate the §8 emit on `mode in {codegen, refactor-only}`. The new mode is **not** a separate subagent — it's a parameter, so the existing prompt template re-uses all the credit-saving, RAGAS, Cognee, and CCC wiring. The prompt addition is ~40 lines:

```markdown
### Mode: research-codegen (F-44, the closing-the-loop mode)
- Triggered when the user invokes `research-codegen <package> <version> [--scope=...]`.
- If package is in SHARED_DISCOVERY_LOG.md → mode=delta by default (re-use wave-1 findings, only emit §8 anchors + 1 verification round, ~60 credits).
- If package is new → mode=codegen (full 7 + §8, ~210 credits).
- The 8-section output schema is the canonical output of this mode.
- §8 items MUST pass the 3 validation gates (ccc-verifiable, exact diff, test exists).
- Append the index entry to SHARED_DISCOVERY_LOG.md after writing the file.
- Cognify into `research_findings` dataset.
- RAGAS every 5th run; if `faithfulness < 0.7` on any of §1-§7, rewrite that section before cognify.
```

**Step 2 — Re-run on the 2 F-08 MVP packages.** Once the mode is wired, the immediate MVP run is:
1. `research-codegen celtic-asset-generation 0.1.0 --scope=ingest,ui` → produces `openspec/research/2026-06-29-celtic-asset-generation.md` + appends to `SHARED_DISCOVERY_LOG.md`.
2. `research-codegen oideachais-baml-schemas 0.223.0 --scope=agent,knowledge` → produces the BAML-inline-clients follow-up + appends.

Both are ~210 credits each (~420 total), so the F-44 cutover + MVP fits in the 700-credit reserve per the program's credit budget (see `SHARED_DISCOVERY_LOG.md:5`).

**Step 3 — Promote to a SKILL.md.** The mode's full specification (this file) is mirrored at `.agents/skills/browserbase/research-codegen/SKILL.md` with a 1-paragraph `description:` frontmatter so the OpenCode agent registry picks it up (mirrors the `browserbase-cli`, `autobrowse`, `agent-experience` pattern). The skill becomes the canonical entry point for any future "I need to document a new package" request, and the system reminder at the top of the agent prompt cross-references it.

**Cutover success criteria:**
- 2 MVP instance runs land with all §8 items passing the 3 validation gates.
- RAGAS `faithfulness ≥ 0.8` on both MVPs.
- `openspec/validate <change-id> --strict` passes for any spec deltas the MVP produces.
- The next wave (program 3, whenever scheduled) starts by importing the `research-codegen` skill rather than re-deriving the 7-section template from scratch.

---

## 1-paragraph summary

F-44 adds a `research-codegen` mode to the existing `research` subagent that takes `(package, version, scope)` and emits an 8-section Markdown (the 7 wave-1 sections + a new §8 "implementable refactor spec" with `file:line` targets verified by `ccc:search`), then appends a SHARED_DISCOVERY_LOG entry, cognifies into the `research_findings` Cognee dataset, and runs RAGAS every 5th output — closing the loop on the 43 wave-1 prompts by automating the Agent 01/15/19 pattern so any new dependency gets a versioned research note + ready-to-execute refactor plan in one ~25-min, ~250-credit BrowserBase session; the cutover is a 3-step process (extend the existing subagent prompt with a `mode` parameter, run the 2 F-08 MVP packages — `celtic-asset-generation` + `oideachais-baml-schemas` — and promote the spec to `.agents/skills/browserbase/research-codegen/SKILL.md`), and the 3 validation gates (ccc-verifiability, exact-diff-shape, test-or-assertion-exists) ensure every §8 item is implementable without re-investigation.
