# Tasks: 2026-07-06-wire-dlthub-platform-toolkits-and-deployment

## Phase 1 — Workspace init + dependency hardening (10 min)

- [ ] 1.1 Verify `.dlt/.workspace`, `.dlt/config.toml`, `.dlt/secrets.toml` exist under `cianfhoghlaim/`; if any missing, run `cd cianfhoghlaim && dlthub init --name cianfhoghlaim`
- [ ] 1.2 Add `fastmcp-slim[server]` to the `dlthub-platform` optional-dependency group in `pyproject.toml`
- [ ] 1.3 Run `uv sync` from repo root and confirm `python -c "import fastmcp"` exits 0
- [ ] 1.4 Confirm `dlthub login` + `dlthub workspace connect 03d1920f-00dd-40cb-a617-95d7bbfef20f` succeed (already done; re-verify)
- [ ] 1.5 Run `dlthub info` and confirm the workspace name + organisation id match `cianfhoghlaim / 3b017615-31d6-4a58-a7e3-05fd3eb7ac85`

## Phase 2 — Install the 8 production toolkits (10 min)

- [ ] 2.1 Run `dlthub ai init --agent claude` to install the `init` toolkit (shared rules + secrets + dlt-workspace MCP)
- [ ] 2.2 Run `dlthub ai toolkit install rest-api-pipeline`
- [ ] 2.3 Run `dlthub ai toolkit install sql-database-pipeline`
- [ ] 2.4 Run `dlthub ai toolkit install filesystem-pipeline`
- [ ] 2.5 Run `dlthub ai toolkit install dlthub-platform`
- [ ] 2.6 Run `dlthub ai toolkit install data-exploration`
- [ ] 2.7 Run `dlthub ai toolkit install data-quality`
- [ ] 2.8 Run `dlthub ai toolkit install transformations`
- [ ] 2.9 Confirm `dlthub ai status` reports 8 toolkits installed and no "No toolkit with workflow is installed!" warning
- [ ] 2.10 Restart Claude Code (`claude`) to pick up the newly installed skills + rules + MCP server

## Phase 3 — Register the first BIEP batch pipeline (15 min)

- [ ] 3.1 Create `cianfhoghlaim/dlt/british_isles/ireland/education/government_circulars_job.py` — wrap the Phase 3.3 BIEP `government_circulars_ingest` asset with `@run.pipeline("government_circulars_ingest")` from `dlt.hub`
- [ ] 3.2 Update `cianfhoghlaim/__deployment__.py` to import `government_circulars_job` and add `"government_circulars_job"` to `__all__`
- [ ] 3.3 Run `dlthub deploy --dry-run` — confirm `jobs.government_circulars_job.government_circulars_ingest` is registered with 0 errors
- [ ] 3.4 Run `dlthub local run government_circulars_ingest` as a safe pre-flight simulation
- [ ] 3.5 Run `dlthub deploy` to sync the manifest to the workspace

## Phase 4 — Document the run/serve split (15 min)

- [ ] 4.1 Create `docs/agents/dlthub-run-vs-serve.md` — 5 sections (the run/serve split, the 5 most common error messages and recovery, the 5-step `dlthub ai status` health check, the canonical happy-path workflow, cross-references)
- [ ] 4.2 Create `.agents/skills/dlthub/SKILL.md` (or extend the existing one) — frontmatter required (name, description), points at `setup-runtime`, `prepare-deployment`, `deploy-workspace`, `debug-deployment` workbench skills
- [ ] 4.3 Verify `mise run lint:skills` still passes (53/53 → 54/54 after the new skill)

## Phase 5 — Spec + openspec artifacts (10 min)

- [ ] 5.1 Create `openspec/specs/dlthub-platform-integration/spec.md` (the canonical new spec)
- [ ] 5.2 Add the 7 ADDED Requirements under `openspec/changes/2026-07-06-wire-dlthub-platform-toolkits-and-deployment/specs/dlthub-platform-integration/spec.md`
- [ ] 5.3 Update `openspec/project.md` to add a row for `dlthub-platform-integration` under "Cianfhoghlaim core"
- [ ] 5.4 Cross-reference `.agents/skills/dlthub/SKILL.md` in the new spec

## Phase 6 — Validate + commit + archive (10 min)

- [ ] 6.1 `openspec validate 2026-07-06-wire-dlthub-platform-toolkits-and-deployment --strict` passes
- [ ] 6.2 `dlthub ai status` returns no warnings (init done + 8 toolkits + fastmcp installed)
- [ ] 6.3 `dlthub deploy --dry-run` shows `government_circulars_ingest` as the registered job
- [ ] 6.4 `dlthub local run government_circulars_ingest` succeeds end-to-end
- [ ] 6.5 `dlthub serve jobs.workspace.dashboard` opens the workspace dashboard
- [ ] 6.6 Stage commits per area (workspace + toolkits + manifest + runbook + spec)
- [ ] 6.7 `git push`
- [ ] 6.8 `openspec archive 2026-07-06-wire-dlthub-platform-toolkits-and-deployment --yes` (after Phase 5 of `british-isles-education-pipeline-v1` wires the rest of the BIEP jobs)
