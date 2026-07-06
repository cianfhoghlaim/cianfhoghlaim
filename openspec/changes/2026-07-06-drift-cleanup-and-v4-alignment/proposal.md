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