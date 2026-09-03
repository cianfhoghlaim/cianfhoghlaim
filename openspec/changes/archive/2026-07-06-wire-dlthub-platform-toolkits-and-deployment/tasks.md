# Tasks: 2026-07-06-wire-dlthub-platform-toolkits-and-deployment

> **Implementation note (post-mortem)**: this change was implemented on
> 2026-07-06. All 6 phases below are completed. The 3 implementation
> **deviations from the original plan** are noted inline:
>
> 1. The job lives at `cianfhoghlaim/dlt/jobs/government_circulars_job.py`
>    (NOT `cianfhoghlaim/dlt/british_isles/ireland/education/`) — the
>    parent `education/__init__.py` has stale `from common.firecrawl_source
>    import …` lines that fail when imported in isolation. Sidestepped by
>    putting the job in a fresh `dlt/jobs/` sub-package.
> 2. A `common` sys.modules alias was added to
>    `cianfhoghlaim/dlt/common/__init__.py` to match the existing `shared`
>    alias pattern. The legacy `from common.firecrawl_source import …`
>    imports in `education/_oide_helpers.py` now resolve.
> 3. The `dlthub ai init` + toolkit-install commands MUST be run from
>    inside `cianfhoghlaim/` (the workspace root), not the repo root.
>    Otherwise `dlthub ai status` warns "No toolkit with workflow is
>    installed!" because it scopes `.claude/` to the workspace root.

## Phase 1 — Workspace init + dependency hardening (10 min) ✅

- [x] 1.1 Verify `.dlt/.workspace`, `.dlt/config.toml`, `.dlt/secrets.toml` exist under `cianfhoghlaim/`
- [x] 1.2 Add `fastmcp-slim[server]` to the `dlthub-platform` optional-dependency group in `cianfhoghlaim/pyproject.toml`
- [x] 1.3 Run `uv sync --directory cianfhoghlaim --extra dlthub-platform`; `python -c "import fastmcp"` exits 0
- [x] 1.4 `dlthub login` + `dlthub workspace connect` confirmed (workspace `cianfhoghlaim / 03d1920f-...`)
- [x] 1.5 `dlthub workspace info` prints the connected workspace + organisation id

## Phase 2 — Install the 8 production toolkits (10 min) ✅

- [x] 2.1 `cd cianfhoghlaim && dlthub ai init --agent claude` (installs `init` toolkit = rules + secrets + dlt-workspace MCP)
- [x] 2.2 `dlthub ai toolkit install rest-api-pipeline`
- [x] 2.3 `dlthub ai toolkit install sql-database-pipeline`
- [x] 2.4 `dlthub ai toolkit install filesystem-pipeline`
- [x] 2.5 `dlthub ai toolkit install dlthub-platform`
- [x] 2.6 `dlthub ai toolkit install data-exploration`
- [x] 2.7 `dlthub ai toolkit install data-quality`
- [x] 2.8 `dlthub ai toolkit install transformations`
- [x] 2.9 `dlthub ai status` reports 7 toolkits (`init` is the dep) + no warnings (run from workspace root)
- [ ] 2.10 Restart Claude Code (`claude`) — *deferred to user; not automatable from agent session*

## Phase 3 — Register the first BIEP batch pipeline (15 min) ✅

- [x] 3.1 Create `cianfhoghlaim/dlt/jobs/government_circulars_job.py` — `@run.pipeline("government_circulars_ingest")` reading cached Oide circulars from `stedding/site_scrape_samples/oide.ie/`
- [x] 3.2 Update `cianfhoghlaim/__deployment__.py` to import `government_circulars_job` and add it to `__all__`
- [x] 3.3 `dlthub workspace info` confirms 2 jobs: `government_circulars_job` + `dashboard` (the system-provided interactive)
- [x] 3.4 `dlthub local run jobs.government_circulars_job --dry-run` succeeds — `job_type: batch`, profile `dev`
- [ ] 3.5 `dlthub deploy` to sync to remote — *deferred; the workspace hasn't been live-deployed yet (only local pre-flight)*

## Phase 4 — Document the run/serve split (15 min) ✅

- [x] 4.1 Create `docs/agents/dlthub-run-vs-serve.md` — 5 sections (the run/serve split, the 5 most common error messages and recovery, the 5-step `dlthub ai status` health check, the canonical happy-path workflow, cross-references)
- [x] 4.2 Create `.agents/skills/dlthub/SKILL.md` — frontmatter required (name, description), points at `setup-runtime`, `prepare-deployment`, `deploy-workspace`, `debug-deployment` workbench skills
- [x] 4.3 `mise run lint:skills` still passes (53/53 — new skill slots into the existing headroom)

## Phase 5 — Spec + openspec artifacts (10 min) ✅

- [x] 5.1 Create `openspec/specs/dlthub-platform-integration/spec.md` (the canonical 38th spec)
- [x] 5.2 Add the 7 ADDED Requirements under `openspec/changes/2026-07-06-wire-dlthub-platform-toolkits-and-deployment/specs/dlthub-platform-integration/spec.md`
- [x] 5.3 Update `openspec/project.md` — added a row for `dlthub-platform-integration` under "Cianfhoghlaim core"; bumped counts from 37 → 38 specs and 13 → 14 cianfhoghlaim-core specs
- [x] 5.4 Cross-reference `.agents/skills/dlthub/SKILL.md` + the runbook in the new spec

## Phase 6 — Validate + commit + archive ✅ (partial)

- [x] 6.1 `openspec validate 2026-07-06-wire-dlthub-platform-toolkits-and-deployment --strict` passes
- [x] 6.2 `dlthub ai status` (from workspace root) reports 7 toolkits installed + no warnings (init done + fastmcp installed)
- [x] 6.3 `dlthub workspace info` shows `government_circulars_job` registered as the first user job
- [x] 6.4 `dlthub local run jobs.government_circulars_job --dry-run` succeeds — `job_type: batch`
- [ ] 6.5 `dlthub serve jobs.workspace.dashboard` — *deferred; requires interactive browser session*
- [x] 6.6 Staged commits + commit `03b09de38` + pushed to `origin/main`
- [ ] 6.7 `openspec archive 2026-07-06-wire-dlthub-platform-toolkits-and-deployment --yes` — *deferred; per the proposal, archive after Phase 5 of `british-isles-education-pipeline-v1` wires the rest of the BIEP jobs (i.e. when the deployment manifest stops being a 1-job placeholder)*

## Out-of-scope follow-ups (for the BIEP-v1 change)

- Wire the remaining 5+ BIEP batch jobs (`lc5_<subject>_ingested`,
  `lc5_<subject>_cognified`, etc.) into
  `cianfhoghlaim/__deployment__.py`
- Add `b.ExtractCircular` + `LinkCircularToSyllabus` to
  `baml/processing/circular_extraction.baml` so the gov.ie ingest has the
  full BAML extraction pipeline (Phase 3.3 of BIEP-v1)
- Schedule `government_circulars_ingest` with
  `trigger=trigger.schedule("0 4 * * *")` (daily 04:00 UTC)