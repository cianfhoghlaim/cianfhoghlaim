## Superseded by

This change is **superseded by** `2026-08-13-biep-v3-systematic-download-ireland-england-v1` (the BIEP v3 umbrella), which has fully delivered all work proposed here as part of milestones M0-M4 (107/109 tasks done).

See the umbrella change's `tasks.md` for the per-milestone task mapping. The BIEP v3 spec (`openspec/specs/british-isles-education-pipeline-v3/spec.md`) is the authoritative home for the ADDED Requirements originally intended for this change.

## Superseded by

This change is **superseded by** `2026-08-13-biep-v3-systematic-download-ireland-england-v1` (the BIEP v3 umbrella), which has fully delivered all work proposed here as part of milestones M0-M4 (107/109 tasks done).

See the umbrella change's `tasks.md` for the per-milestone task mapping. The BIEP v3 spec (`openspec/specs/british-isles-education-pipeline-v3/spec.md`) is the authoritative home for the ADDED Requirements originally intended for this change.

# 2026-08-05-marimo-wasm-and-cigrunners-v1

## Why

With the 5 BIEP v3 jurisdiction dashboard notebooks
(`notebooks/19..23_*.py`) + the 4-tab companion notebook
(`notebooks/18_*.py`) all shipped in the BIEP v3 followup wave, the
next step is to (1) make them run as WebAssembly (so users can access
the dashboards in a browser without a Python install) and (2) wire
the testRuns.ingest call to the CI runners (so every PR auto-runs
the 99 notebooks as smoke tests).

This change lives in the **cianfhoghlaim repo**.

## What changes

### 1. Marimo WASM delta export + manifest publishing + theme (closes #54)

- Add `scripts/marimo_wasm_export.py` — converts each `.py` notebook
  to a WASM bundle + a JSON manifest
- Output goes to `web/apps/cianfhoghlaim-web/public/notebooks/`
- Add the manifest publisher (`.github/workflows/marimo-wasm-publish.yaml`)
- Apply the canonical Cianfhoghlaim theme to the WASM bundles
- Each `notebooks/{18,19,20,21,22,23,40}_*.py` exports to a route at
  `/notebooks/{18,19,20,21,22,23,40}_*` in the web app
- Run `bun run marimo:wasm:export` + `bun run marimo:wasm:publish`

### 2. Wire testRuns.ingest to CI runners (closes #34)

- Add the `scripts/test_runs_ingest.py` script
- Wires the testRuns.ingest call to the meaisinfhoghlaim agent fleet
- Every CI run on `main` calls `testRuns.ingest(passed=..., failed=..., runtime=...)`
- The testRuns.ingest surfaces in the agent-platform-cluster dashboard
- Add a `.github/workflows/test-runs-ingest.yaml` that fires on every
  CI completion
- Update `AGENTS.md` with the test-runs dashboard URL

## Dependencies

```yaml
Blocked by: 2026-08-03-biep-v3-web-app-routes-hono-endpoints-v1
Blocked by: 2026-08-03-biep-v3-notebook-jurisdiction-dashboards-v1
Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `bun run marimo:wasm:export` produces 5+ WASM bundles in
  `web/apps/cianfhoghlaim-web/public/notebooks/`
- `curl localhost:3000/notebooks/19_ireland_pipeline_dashboard.html`
  returns 200 OK
- `bun run test-runs:ingest --dry-run` returns a valid JSON payload
- The testRuns dashboard shows real CI test history
- `openspec validate 2026-08-05-marimo-wasm-and-cigrunners-v1 --strict` passes

## Cross-references

- `notebooks/18_cianfhoghlaim_subject_registry.py` (the 4-tab companion)
- `notebooks/19..23_*.py` (the 5 jurisdiction dashboards)
- `web/apps/cianfhoghlaim-web/` (the web app)
- `agents/meaisinfhoghlaim/agent_fleet/` (the testRuns.ingest endpoint)
- `.agents/skills/marimo/SKILL.md` (the marimo conventions)
- GitHub issues #34, #54