---
title: "dlthub run vs serve — diagnostic runbook"
description: "Diagnose and recover the 5 most common dlthub CLI errors; document the batch/interactive split; the canonical happy-path from `dlthub init` to `dlthub run`."
category: agents
status: living
created: 2026-07-06
last_updated: 2026-07-06
openspec_change: 2026-07-06-wire-dlthub-platform-toolkits-and-deployment
openspec_spec: dlthub-platform-integration
---

# dlthub run vs serve — diagnostic runbook

This runbook is the entry point when the `dlthub` CLI does something
unexpected. It pairs with the `.agents/skills/dlthub/SKILL.md` agent router
(which is installed alongside it) and with the 4 dlthub-platform workbench
skills that get installed into Claude Code by `dlthub ai toolkit install
dlthub-platform` (see §5 below for the cross-link map).

## 1. The split (read this first)

The `dlthub` CLI has **two verbs** that run jobs, and they are not
interchangeable:

| Verb | Purpose | What it runs | Decorator |
|:--|:--|:--|:--|
| `dlthub run <name\|file>` | **Batch** — execute a pipeline or script | Pipelines, scripts, anything with `if __name__ == "__main__":` | `@run.pipeline(name)` or `@run.job` |
| `dlthub serve <name>` | **Interactive** — long-running notebook / dashboard / API server | marimo notebooks, FastAPI apps, anything that's an HTTP service | `@run.interactive` or `import <notebook_module>` |

The CLI auto-matches a bare name (e.g. `dlthub run` with no arg) against
the `__all__` entries in `__deployment__.py`. If the only match is an
interactive job, it fails loudly with a clear pointer:

```text
Matched jobs are interactive (not allowed here): jobs.workspace.dashboard.
Use the `serve` command instead.
```

That is the correct behavior — `dlthub run` is for batch only. The fix
is either to use `dlthub serve`, or to pass an explicit script path
which bypasses the matcher entirely.

## 2. The 5 most common errors (and the recovery)

### Error 1 — `Matched jobs are interactive (not allowed here)` (the headline bug)

```text
$ dlthub run
Matched jobs are interactive (not allowed here): jobs.workspace.dashboard.
Use the `serve` command instead.
```

**Root cause**: the deployment manifest is empty (or only has interactive
jobs), so the auto-matcher falls back to the system-provided
`jobs.workspace.dashboard`, which is interactive.

**Recovery** (3 options, pick by intent):
- `dlthub serve jobs.workspace.dashboard` ← you want to look at data
- `dlthub run cianfhoghlaim/dlt/jobs/<your_batch_script>.py` ← you want
  to ingest
- populate `__all__` in `cianfhoghlaim/__deployment__.py` with your
  `@run.pipeline(...)` batch jobs, then `dlthub run <job_name>`

### Error 2 — `No module named 'cianfhoghlaim'` when `dlthub workspace info` runs

```text
Failed to import '/Users/.../cianfhoghlaim/__deployment__.py':
ModuleNotFoundError: No module named 'cianfhoghlaim'
```

**Root cause**: the editable-install `.pth` file is malformed (just path
text, missing `import sys; sys.path.insert(0, '…')`), or the path
inserted points at the wrong dir (the package lives at
`kings_college_galway/cianfhoghlaim/`, so sys.path needs the PARENT dir
`kings_college_galway/`).

**Recovery**:
1. Check `.venv/lib/python3.13/site-packages/_editable_impl_cianfhoghlaim.pth`
2. It must contain exactly:
   ```text
   import sys; sys.path.insert(0, '/Users/cianmacandeisigh/dev/kings_college_galway')
   ```
3. Re-run `uv sync` to regenerate it if it was clobbered.

### Error 3 — `Workspace not yet initialized (dlthub init not yet run)`

**Root cause**: the heuristic check looks for recent `.dlt/config.toml`
or a v1.28+ init pattern; a pre-v1.28 marker file trips a false
positive.

**Recovery**: from inside the workspace root:
```bash
cd cianfhoghlaim
dlthub init --name cianfhoghlaim     # idempotent (refuses to overwrite)
# or with --force if the existing config is broken
```

### Error 4 — `FastMCP server support is not installed`

**Root cause**: `fastmcp-slim[server]` is missing from the active venv.

**Recovery**:
```bash
uv sync --directory cianfhoghlaim --extra dlthub-platform
# then re-run
dlthub ai mcp run --stdio
```

### Error 5 — `No toolkit with workflow is installed!`

**Root cause**: `dlthub ai init` was never run, or was run for the wrong
agent (Cursor vs Claude Code).

**Recovery**:
```bash
dlthub ai init --agent claude                # installs the `init` toolkit
dlthub ai toolkit install dlthub-platform    # installs the platform skill set
# restart Claude Code so the new skills + MCP server take effect
```

## 3. The 5-step `dlthub ai status` health check

Run these in order. Each command has a passing and a failing signature
listed below.

| Step | Command | Passes when | Fails when |
|:--|:--|:--|:--|
| 1 | `dlthub --version` | prints `dlthub 1.28.x` | nothing (the CLI is just broken) |
| 2 | `dlthub workspace info` | shows workspace + no `ModuleNotFoundError` for the manifest | `No module named 'cianfhoghlaim'` → see Error 2 |
| 3 | `dlthub local info` | shows the dev profile + data dirs | profile missing → run `dlthub init` |
| 4 | `dlthub ai status` | lists 8 toolkits + no warnings | see Errors 4 & 5 |
| 5 | `dlthub ai mcp run --stdio` | server announces 8 MCP tools on stderr | `FastMCP server support is not installed` → Error 4 |

## 4. The canonical happy-path workflow

From a fresh clone:

```bash
# 1. One-time toolchain bootstrap
mise install && bun install && uv sync && bun run secrets:env

# 2. dlthub workspace + AI init (idempotent)
cd cianfhoghlaim
dlthub init --name cianfhoghlaim             # creates .dlt/{config,secrets}.toml + .workspace
dlthub login                                  # device-code OAuth
dlthub workspace connect 03d1920f-00dd-40cb-a617-95d7bbfef20f  # cianfhoghlaim

# 3. AI tooling init (the 8 toolkits from .claude/skills/)
dlthub ai init --agent claude
for t in rest-api-pipeline sql-database-pipeline filesystem-pipeline \
          dlthub-platform data-exploration data-quality transformations; do
    dlthub ai toolkit install "$t"
done
uv sync --directory cianfhoghlaim --extra dlthub-platform

# 4. Restart Claude Code so skills + MCP server take effect
claude

# 5. Author your batch pipeline (decorator pattern)
#    cianfhoghlaim/dlt/jobs/my_pipeline.py:
#       @dlt.resource(...)
#       def my_resource(): ... yield {...}
#
#       @run.pipeline("my_pipeline")
#       def my_pipeline_job():
#           p = dlt.pipeline(pipeline_name="my_pipeline", destination="duckdb")
#           p.run(my_resource())
#
#       if __name__ == "__main__":
#           my_pipeline_job()

# 6. Register it in the deployment manifest
#    cianfhoghlaim/__deployment__.py:
#       from cianfhoghlaim.dlt.jobs import my_pipeline
#       __all__ = ["my_pipeline"]

# 7. Verify + sync to remote
dlthub workspace info                # confirm 1+N jobs (your batch + dashboard)
dlthub local run jobs.my_pipeline_job --dry-run    # safe pre-flight
dlthub deploy --dry-run              # show the plan; then `dlthub deploy` to ship

# 8. Run / serve
dlthub run jobs.my_pipeline_job      # batch
dlthub serve jobs.workspace.dashboard  # interactive workspace dashboard
```

## 5. Cross-references

### KCG-side skill (this runbook's frontmatter)

- [`.agents/skills/dlthub/SKILL.md`](../../.agents/skills/dlthub/SKILL.md)
  — agent router (frontmatter-only, points at the workbench skills below)

### dltHub AI workbench skills (installed into `.claude/skills/` by `dlthub ai toolkit install dlthub-platform`)

- `setup-runtime` — the 5-step workspace pre-flight (verify Python,
  `.dlt/.workspace`, `dlt[hub]` dep, login, profile files)
- `prepare-deployment` — split dev/prod secrets, set up production
  destination (canonical: **MotherDuck**), create `__deployment__.py`
- `deploy-workspace` — `dlthub deploy`, `dlthub local run`, `dlthub run`,
  `dlthub serve`, scheduling via `@run.pipeline(trigger=...)`
- `debug-deployment` — `dlthub job list`, `dlthub job logs`,
  `dlthub info`, `dlthub local pipeline list` for the full diagnostic
  tree

### Living example (this repo's first job)

- `cianfhoghlaim/dlt/jobs/government_circulars_job.py` — the BIEP phase-0
  `@run.pipeline("government_circulars_ingest")` job
- `cianfhoghlaim/__deployment__.py` — the manifest
- `openspec/specs/dlthub-platform-integration/spec.md` — the contract
- `openspec/changes/2026-07-06-wire-dlthub-platform-toolkits-and-deployment/`
  — the change record
