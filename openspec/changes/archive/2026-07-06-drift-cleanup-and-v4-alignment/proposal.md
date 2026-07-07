# Change: 2026-07-06-drift-cleanup-and-v4-alignment

## Why

The 2026-07-06 audit (see `docs/audits/2026-07-06-drift-audit.md`) found that the
Cianfhoghlaim monorepo — after the v4 consolidation on 2026-06-28 — still
contains substantial drift in three surfaces that affect every agent run:

1. **`.agents/skills/` (58 skills remaining)** — ~20 skills reference
   pre-v4 `sruth/<quadrant>/...` paths (now dead), and many link to broken
   cross-references (12 ghost skills, all backed up at `.agents/skills_backup/`).
   The `secrets-management` skill still uses `infisical://dev-baile/sruth/oideachais/...`
   URIs that no longer resolve.
2. **`openspec/` (66 pending changes, 56 capability specs)** — 30 changes are
   fully done or fully superseded by v4 and need ARCHIVE; 30 capability specs
   have stale `sruth/*` ghost paths; 12 specs have `Purpose: TBD` placeholder;
   2 phantom specs (`celtic-data-engineering-pipeline`, `gradio-ensemble-pattern`)
   are advertised in AGENTS.md + project.md but have no spec dir.
3. **`cianfhoghlaim/notebooks/` (91 notebook files)** — only 3 of 91 are
   healthy. 17 hardcoded secrets (Garage keys, PG `devpassword`), 13 hardcoded
   `/Users/cianmacandeisigh/dev/...` paths, 88 of 91 lack PEP 723 inline deps,
   50 use `pandas` instead of DuckDB + Ibis, and only 3 use `mo.sql(engine=md:oideachais)`.

The drift matters because:

- **Skills are agent context.** Every `sruth/<quadrant>/...` reference in a
  `frontmatter.description:` field biases the agent harness toward searching
  paths that no longer exist, costing 30–90 s of `ccc search` per agent call.
- **Notebooks are the teacher-facing surface.** 17 hardcoded secrets in
  notebooks are a **security incident**; hardcoded `/Users/...` paths mean
  the notebooks don't work on any other developer machine; pandas-only
  analytics mean the data never reaches the DuckLake lakehouse that the rest
  of the stack is built around.
- **OpenSpec is the change-management surface.** 30 stale changes inflate
  `openspec list` output and make the active changes harder to find.

This change eliminates all three classes of drift without changing any
system behaviour. It is a pure refactor.

## What changes

### A.1 Skills cleanup (all 58 remaining)

For every skill in `.agents/skills/`:

- **Rewrite `sruth/<quadrant>/...` → `cianfhoghlaim/<area>/...`** in body
  text and frontmatter `description:` (where the path appears in the trigger
  phrases). Targets: `change-detection`, `dlt`, `cocoindex`, `dagster`,
  `baml`, `secrets-management`, `agent-fleet-orchestration`,
  `agent-memory-systems`, `agent-observability`, `agentic-frontend-frameworks`.
- **Fix Infisical URI references** — `infisical://dev-baile/sruth/oideachais/...`
  → `infisical://dev-baile/oideachais/...` in `secrets-management` (L33, L200).
- **Remove broken cross-references** to the 12 ghost skills now backed up at
  `.agents/skills_backup/` (do not reference these as live):
  `oideachais-baml-schemas` → `baml`; `oideachais-storage` →
  `motherduck` + `iceberg-lakekeeper`; `oideachais-marimo-dashboards` →
  `marimo`; `oideachais-cognify-knowledge-graph` → `cognee`;
  `embedding-pipeline` → `cocoindex`; `stack-ops` → `infrastructure-stacks`;
  `monorepo` → `AGENTS.md`; `cross-domain-registry` → `agent-memory-systems`;
  `kcg-pangolin-stack` → `pangolin`; `kcg-infrastructure-audit` →
  `infrastructure-stacks`; `pydantic-ai` → `pydantic/building-pydantic-ai-agents`;
  `browser` → `browser-tools`.
- **Update `frontmatter.description:`** to reflect the project's current
  British-Isles Education pipeline goals where relevant.
- **Add canonical example blocks** to: `dlt`, `baml`, `cocoindex`, `dagster`,
  `marimo`, `motherduck`, `duckdb`, `ducklake`, `ibis`, `lancedb` — show the
  post-v4 pattern (`from cianfhoghlaim.dlt...`, `mo.sql(engine=md:oideachais)`,
  `lancedb.mount_table_target`, `@coco.lifespan` + `@coco.fn`).
- **Add deprecation banner** to `dlthub`, `dlthub-router`, `setup-secrets`,
  `ccc`, `graphiti-core` — pointing at the canonical replacement the user
  chose to retain.
- **Add British-Isles Education context** to the canonical 5 of each vendor
  family: `motherduck` (router), `cloudflare`, `huggingface`, `marimo`,
  `copilotkit` — call out the 6 LC subjects + gov.ie circulars in the
  "When to Use" section.

### A.2 OpenSpec cleanup (no behaviour change)

- **ARCHIVE ~30 changes** that are fully done or fully superseded by v4
  (single `openspec archive <id> --yes` per change):
  `2026-06-29-bonneagar-v4-canonical-and-stack-migration`,
  `modernize-meaisin-cliste`, `skills-metadata-cleanup`,
  `2026-07-03-specs-and-session-9-health-report`,
  `2026-06-29-restore-heritage-corpus-and-expand-readme`,
  `extend-culture-heritage-to-8-articles`, `ingest-culture-heritage`,
  the 4 `browserbase-phase-{1a,1b,2,3}-decisions`,
  `refactor-quadrants-to-sruth`, `refactor-dlt-dagster-2026-stack-align`,
  `consolidate-external-libs-into-tuatha`,
  `croilar-personas-to-streams`, `lateralise-dlt-sources-to-domains`,
  `ireland-primary-jc-dlt-baml-and-full-stack-demo`,
  `consolidate-embedding-batcher`, `fix-broken-imports-and-baml`,
  `stale-pipelines-cleanup`, `datasets-cleanup`,
  `archive-celtic-baml-orphans`, `oideachais-stack-polish`,
  `oideachais-agent-services`, `complete-cognee-knowledge-graph`,
  `four-directory-indexing-and-standards`,
  `docs-skills-consolidation-pipeline`,
  `celtic-data-engineering-patterns`,
  `refactor-dlt-cocoindex-baml-dagster-with-pdf-pipeline`,
  `croilar-revitalisation`, `baml-reorganize-by-cluster`,
  `dagger-monorepo-integration`, `leaving-cert-2026`.
- **Write `Purpose:`** for the 12 specs with `Purpose: TBD` placeholder.
- **Resolve the 2 phantom specs** by removing the AGENTS.md + project.md
  rows for `celtic-data-engineering-pipeline` and `gradio-ensemble-pattern`
  (the `celtic-data-engineering-patterns` change has 0/28 tasks and will
  itself be ARCHIVE'd by this change).
- **Path-only rewrite** of `specs/infrastructure-stacks/spec.md`:
  `infrastructure/stacks/<x>` → `bonneagar/stacks/<x>` everywhere (~31 hits).
- **Path-only rewrite** of `specs/oideachais-baml-schemas/spec.md`:
  remove the 2 `sruth/*` refs.

### A.3 Notebooks cleanup (all 91 remaining)

For every notebook in `cianfhoghlaim/notebooks/`:

- **Add PEP 723 inline deps** at the top (e.g. `# /// script … # ///`).
- **Remove hardcoded secrets** (17 instances across `lakehouse_inspector.py`,
  `mission_control.py`, `pipeline_e2e_test.py`, `exam_papers_explorer.py`,
  `pdf_download_dashboard.py`, `pdf_ocr_model_comparison.py`) — move all
  reads to `os.environ.get("CIANFHOGHLAIM_INFISICAL_TOKEN")` only.
- **Replace hardcoded `/Users/cianmacandeisigh/...` paths** with env vars
  (`CIANFHOGHLAIM_LEAVING_CERT_ROOT`,
  `CIANFHOGHLAIM_LAKEHOUSE_DUCKDB`, `MOTHERDUCK_TOKEN`).
- **Replace pandas-only analytics with DuckDB + Ibis** where the data lives
  in the lakehouse. Use `mo.sql(engine=md:oideachais)` for federated
  SQL that joins DuckLake tables + LanceDB tables (`lance_scan()`).
- **Wire to live lakehouse tables** (`md:oideachais.leaving_cert.<subject>.*`,
  `md:oideachais.lc.<subject>.<level>_<lang>`) where the source data exists
  in the 6 priority subject pipelines.
- **Update docstrings + comments** to reference the current project name
  (`cianfhoghlaim`), current structure (`v4 consolidated`), and the
  British-Isles Education pipeline goals.

### A.4 Agent cluster cleanup

The tuatha/agents/adk/ cluster was deleted by the user (5 files:
`root_agent.py`, `celtic_tutor.py`, `mythology_narrator.py`,
`quest_guide.py`, `research_assistant.py`). This change:

- Updates `agent-fleet-orchestration` skill to reflect that removal.
- Removes any reference to the deleted agents in the 7 surviving
  `agents/tuatha/agents/agno/*.py` files (if they reference the deleted
  ADK peers).

### A.5 Spec retire — 12 deletes + 4 merges

Delete these 12 spec directories (each maps to an existing canonical that
absorbs the capability via an inline `## Migrated from: <X>` section in the
surviving spec):

- `author-archive-credit-budget` → `official-media-pipeline` (Credit Budget)
- `author-archive-cross-corpus-kg` → `oideachais-cognify-knowledge-graph`
- `author-archive-multi-target` → `oideachais-pipeline` (DLT targets)
- `author-archive-pipeline` → `official-media-pipeline` (Pre-research)
- `author-archive-ui-grounding` → `agent-fleet-orchestration`
- `author-archive-uog-coursework` → `oideachais-university-deep-extraction`
- `author-archive-web-scraping` → `browser-tools` + `official-media-pipeline`
- `chunkhound-code-search` → superseded by `indexing-and-cognition` (explicit)
- `cocoindex-v1-migration` → duplicate of `oideachais-cocoindex-v1-migration`
- `cross-domain-registry` → `agent-memory-systems`
- `stack-audit` → archived `fix-existing-stacks` is done
- `tuatha-platform` → superseded by `cianfhoghlaim-educational-mmo`

Merge these 4 sources into canonical targets:

- `ncca-leaving-cert-root-pdfs` → `oideachais-pipeline` (1 Requirement + 2 Scenarios)
- `retro-game-asset-pipeline` → `retro-game-design-catalogue` (3 Requirements)
- `data-engineering-space` → `data-engineering-pipeline-documentation` (1 Requirement)
- (internal) `cocoindex-v1-migration` body → `oideachais-cocoindex-v1-migration`

### A.6 Spec repair — extract Requirements from 4 zero-req bodies

Currently 4 specs have rich bodies but 0 Requirements (fail strict validation).
Extract Requirements + Scenarios from each body:

- `bonneagar-iac-merge` → 3 Requirements + 5 Scenarios (3 typed clients, 4 source-discoverers, 15 CLI commands, `--with-blueprint-import`)
- `bonneagar-komodo-gitops` → 2 Requirements + 4 Scenarios (3 resource-syncs, 60s interval, 2-host topology, Hetzner-Pulumi-only)
- `oideachais-email-triage` → 4 Requirements + 6 Scenarios (4-account MBOX DLT, `email.baml` 3 functions, 4th CocoIndex App, ADK agent on 7778, marimo)
- `infrastructure-stacks-documentation` → 2 Requirements + 4 Scenarios (per-stack docs contract, 4-section template, `stack-doctor.sh` CI gate)

### A.7 New canonical specs — 4 ADDED

- `british-isles-education-pipeline` — the flagship, aligned with the `2026-07-06-british-isles-education-pipeline-v1` change
- `agent-platform-cluster` — the 8-stack observability + memory + LLM-routing substrate
- `apple-photos-ingestion` — the 5th leabharlann corpus (osxphotos + paperless-ngx + paddleocr)
- `ireland-primary-jc-dlt-baml` — closes a gap in `oideachais-pipeline` for the Primary + Junior Cycle stages

### A.8 Path rewrite — 25 specs, mechanical sweep

Sweep `sruth/<quadrant>/...` → `cianfhoghlaim/...` and `infrastructure/stacks/...`
→ `bonneagar/stacks/...` across the 25 specs identified by
`grep -c "sruth/" openspec/specs/*/spec.md | sort -nr`. Largest targets:
`oideachais-pipeline` (108 hits), `meaisinfhoghlaim-platform` (97),
`tuatha-platform` (61), `croilar-data-engineering` (36), `agentic-frontend-frameworks` (17),
`data-engineering-pipeline-documentation` (15). Plus 19 smaller specs (7-9 hits each).

Replacement table:

| Find | Replace |
|:--|:--|
| `sruth/oideachais/` | `cianfhoghlaim/` |
| `sruth/meaisinfhoghlaim/` | `cianfhoghlaim/` |
| `sruth/tuatha/` | `cianfhoghlaim/` |
| `sruth/croilar/` | `cianfhoghlaim/` |
| `sruth/codeolas/` | `codeolas/` (uv sub-package) |
| `sruth/crypteolas/` | `cianfhoghlaim/docs/legacy/crypteolas/` |
| `infrastructure/stacks/` | `bonneagar/stacks/` |
| `infrastructure/browser/` | `cianfhoghlaim/core/browser/` |
| `oideachais.data_platform` (absolute import) | `dlt_sources` (relative) |
| `infisical://dev-baile/sruth/` | `infisical://dev-baile/` |

### A.9 Root doc sweep

- `openspec/AGENTS.md` (180 + 12 hits of `sruth/` paths): sweep to post-v4; fix spec count from "36/37" → 48; remove the 2 phantom-spec rows (`celtic-data-engineering-pipeline`, `gradio-ensemble-pattern`); drop the deprecated-alias note for `tuatha-platform`
- `openspec/project.md`: refresh §180-202 in-flight changes table (most rows are stale); update spec count to 48; add the 4 new canonicals from A.7

### A.10 Plans directory — refresh + archive 6 of 12

Keep 6 plans as active research/deferred roadmaps (STATUS.md, education_audit_plan.md,
gcp_ai_optimization_strategy.md, infrastructure_deep_dive.md, final_exponential_strategy.md,
package-updates.md) and refresh their frontmatter `superseded_by` paths to point at
current spec names. Archive the 6 plans whose content is fully absorbed into
canonical specs (data_engineering_deep_dive, deployment_and_ai_strategy,
deployment_stack_strategy, exponential_improvement_roadmap, machine_learning_deep_dive,
web_and_dashboards_deep_dive) to
`openspec/plans/archive/2026-07-06-plans-refresh/`.

### A.11 Extended change archive — 12 additional

Archive the 12 stale changes the prior Phase 3 missed:
`add-openclaw-stack-and-channel-fanout`, `add-openchamber-stack-and-opencode-ui`,
`consolidate-cianfhoghlaim-subdirs`, `deploy-llama-swap-v166-stack`,
`deploy-v4-ocr-vlm-on-m4-max`, `wire-6-stage-pdf-pipeline-to-production`,
`wire-baml-to-consolidated-pipelines`, `wire-baml-with-known-consumers`,
`wire-unwired-dlt-sources`, `wire-v4-models-into-litellm-config`, plus
2 verify-duplicates (`celtic-data-engineering-patterns`, `refactor-dlt-cocoindex-baml-dagster-with-pdf-pipeline`).

## What does NOT change

- No code behaviour. No Python imports change. No BAML schemas change.
  No DLT destinations change. No Dagster assets are added/removed.
- No new dependencies in `pyproject.toml`.
- The active LC pipeline change
  (`2026-07-03-leaving-cert-5-subject-pipeline-with-diagrams`) and
  the umbrella (`rewrite-cianfhoghlaim-leaving-cert-v2`) are NOT
  touched. The British-Isles Education pipeline NEW work is the
  separate change `2026-07-06-british-isles-education-pipeline-v1`.

## Files

- 58 skills in `.agents/skills/`: frontmatter + body rewrites.
- 91 notebooks in `cianfhoghlaim/notebooks/`: PEP 723 + env vars + DuckDB
  + Ibis + secret removal.
- ~30 openspec changes: `openspec archive <id> --yes`.
- 12 specs: `Purpose:` paragraphs.
- 2 phantom-spec rows in `AGENTS.md` and `project.md`: deletion.
- `openspec/AGENTS.md` (180 + 12 hits of `sruth/` paths) + `openspec/project.md`
  (similar): path-only rewrites.
- `openspec/specs/infrastructure-stacks/spec.md` (910 LOC, 31 `sruth/` hits):
  path-only rewrite.
- `openspec/specs/oideachais-baml-schemas/spec.md`: 2-path rewrite.
- `.agents/skills/agent-fleet-orchestration/SKILL.md`: rewrite to reflect
  tuatha/agents/adk/ deletion.

## Acceptance

- `openspec validate 2026-07-06-drift-cleanup-and-v4-alignment --strict`
  passes.
- `mise run lint:skills` passes (skill metadata valid).
- `python -m py_compile <each notebook>` parses for all 91 notebooks.
- `marimo parse <each notebook>` succeeds for all marimo notebooks.
- `grep -r 'sruth/' .agents/skills/ cianfhoghlaim/notebooks/ openspec/`
  returns 0 hits in rewritten files (only in `.agents/skills_backup/`).
- `git grep 'infisical://dev-baile/sruth/'` returns 0 hits.
- `git grep -E 'os\.getenv\(.*"GK[A-Z0-9]{20,}"|"0c3ec[a-z0-9]{20,}"|"devpassword"'`
   returns 0 hits in `cianfhoghlaim/notebooks/`.
- `openspec list --specs | wc -l` is 49 (48 canonicals + 1 `__pycache__` line).
- `grep -r 'Purpose: TBD' openspec/specs/` returns 0 hits.
- `grep -r 'sruth/' openspec/specs/` returns 0 hits.
- `grep -r 'infrastructure/stacks/' openspec/specs/` returns 0 hits (other than
  in archived plan bodies).
- `ls openspec/plans/*.md | wc -l` is 6 (was 12).
- `ls openspec/changes/ | wc -l` drops by ~42 (the 30 existing archives +
  the 12 new archives + 3 already-Complete).