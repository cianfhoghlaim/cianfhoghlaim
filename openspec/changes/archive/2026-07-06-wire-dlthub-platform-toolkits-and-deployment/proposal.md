# Change: 2026-07-06-wire-dlthub-platform-toolkits-and-deployment

## Why

`dlthub run` from the repo root fails with:

```
Matched jobs are interactive (not allowed here): jobs.workspace.dashboard.
Use the `serve` command instead.
```

This is **correct CLI behaviour, not a bug** — but the *user-visible* root cause is that the dlthub platform is only half-wired in this repo. Audit (read-only) of the current state:

| Symptom | Diagnostic finding |
|---|---|
| `dlthub run` auto-matches the system `jobs.workspace.dashboard` interactive job | `cianfhoghlaim/__deployment__.py` and the root `__deployment__.py` are both empty stubs (`__all__: list[str] = []`); with no local jobs registered, the CLI falls back to the workspace-scoped dashboard |
| `dlthub ai status` warns "Workspace not yet initialized" | `.dlt/.workspace` and `.dlt/config.toml` exist but were never produced by the v1.28 CLI flow (the 28-byte `secrets.toml` predates the v1.28 init path) |
| `dlthub ai status` warns "No toolkit with workflow is installed!" | The vendored `cianfhoghlaim/dlthub-ai-workbench/.claude-plugin/marketplace.json` (11 toolkits) has never been copied into Claude Code's `.claude/` plugin dir |
| `dlthub ai status` warns "FastMCP server support is not installed" | `fastmcp-slim[server]` is missing from `pyproject.toml` |

This change closes the loop end-to-end: harden workspace init → install the 8 production toolkits → register the first BIEP batch job → document the `run`/`serve` split so the original error can never silently recur.

## What changes

**A. Workspace init hardening.** Re-run `dlthub init` (idempotent), add `fastmcp-slim[server]` to `pyproject.toml`, confirm `dlthub info` prints the connected workspace.

**B. AI workbench installation.** Point Claude Code at the vendored `cianfhoghlaim/dlthub-ai-workbench/.claude-plugin/marketplace.json` and install the 8 production toolkits (`init`, `rest-api-pipeline`, `sql-database-pipeline`, `filesystem-pipeline`, `dlthub-platform`, `data-exploration`, `data-quality`, `transformations`). Restart Claude Code.

**C. Deployment manifest.** Populate `cianfhoghlaim/__deployment__.py` with `@run.pipeline("government_circulars_ingest")` from `dlt.hub` — the smallest BIEP surface (Phase 3.3 of `2026-07-06-british-isles-education-pipeline-v1`). Root `__deployment__.py` stays a stub. Verify with `dlthub deploy --dry-run`.

**D. Run/serve split runbook.** Document the two CLI verbs at `docs/agents/dlthub-run-vs-serve.md` (5-error diagnostic tree + 5-step `dlthub ai status` health check + happy-path workflow). Cross-link from a new `.agents/skills/dlthub/SKILL.md`.

**E. Spec + openspec artifacts.** Create `openspec/specs/dlthub-platform-integration/spec.md` with 7 ADDED Requirements. Add the spec delta to `openspec/changes/2026-07-06-wire-dlthub-platform-toolkits-and-deployment/specs/dlthub-platform-integration/spec.md`. Update `openspec/project.md` (37 → 38 specs).

## What does NOT change

- The 94-stack Docker Compose fleet (no new stacks; no `infrastructure/stacks/` edits).
- The existing 8 NCCA LC DLT sources or BIEP CocoIndex flows (Phase 1–2 of `british-isles-education-pipeline-v1`).
- The 6 marimo per-subject notebooks (Phase 6 of `british-isles-education-pipeline-v1`).
- The Infisical + Locket + mise secrets contract.

## Files (new + modified)

### New

- `openspec/specs/dlthub-platform-integration/spec.md` (canonical spec)
- `openspec/changes/2026-07-06-wire-dlthub-platform-toolkits-and-deployment/{proposal.md,tasks.md}`
- `openspec/changes/2026-07-06-wire-dlthub-platform-toolkits-and-deployment/specs/dlthub-platform-integration/spec.md`
- `cianfhoghlaim/dlt/british_isles/ireland/education/government_circulars_job.py` (the first `@run.pipeline` decorated job)
- `docs/agents/dlthub-run-vs-serve.md`
- `.agents/skills/dlthub/SKILL.md`

### Modified

- `cianfhoghlaim/__deployment__.py` (empty stub → imports + `__all__`)
- `pyproject.toml` (add `fastmcp-slim[server]` to `dlthub-platform` extra)
- `openspec/project.md` (37 → 38 specs; add row)

## Acceptance

- `openspec validate 2026-07-06-wire-dlthub-platform-toolkits-and-deployment --strict` passes.
- `dlthub ai status` reports zero warnings (init done + 8 toolkits + fastmcp).
- `dlthub deploy --dry-run` shows `government_circulars_ingest` as a registered job.
- `dlthub local run government_circulars_ingest` succeeds (pre-flight simulation).
- `dlthub serve jobs.workspace.dashboard` opens the interactive dashboard.
- `git push` lands the change.
