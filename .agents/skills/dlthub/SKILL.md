---
name: dlthub
description: KCG-side routing skill for the dltHub Platform CLI (`dlthub 1.28+`) — deployment manifest authoring, the `dlthub run` vs `dlthub serve` split, the 5 most common CLI errors and their recovery, and the 5-step `dlthub ai status` health check. Use when the user asks about "dlthub", "deploying to dlthub", "the dlthub CLI", "dlt Hub workspace", "jobs.workspace.dashboard", the `dlthub run`/`dlthub serve` verbs, or the `Matched jobs are interactive` error.
---

# dlthub Platform — KCG Routing Skill

This skill is the **KCG-side frontmatter + router** for the dltHub Platform
CLI (`dlthub 1.28+`). The long-form runbook (5-section diagnostic tree,
canonical happy-path workflow, cross-link map) lives at
[`docs/agents/dlthub-run-vs-serve.md`](../../../docs/agents/dlthub-run-vs-serve.md).
The 4 workbench skills below are installed into `.claude/skills/` by
`dlthub ai toolkit install dlthub-platform`.

## When to load

| User says… | Load this skill |
|:--|:--|
| "dlthub run fails with `Matched jobs are interactive`" | Yes (the headline bug) |
| "`dlthub workspace info` shows `No module named 'cianfhoghlaim'`" | Yes |
| "`dlthub ai status` warns about fastmcp" | Yes |
| "How do I deploy a pipeline to dltHub?" | Yes → delegate to `setup-runtime` then `deploy-workspace` |
| "How do I serve the workspace dashboard?" | Yes → `dlthub serve jobs.workspace.dashboard` |
| "Where does the deployment manifest live?" | Yes → `__deployment__.py` |
| "What toolkits should I install?" | Yes → §"Toolkit set" below |

## Decision tree → sub-skill or reference

```text
User wants…
├── "Run a batch pipeline"
│     ├── @run.pipeline("name") in __deployment__.py     ← load (deploy-workspace)
│     ├── dlthub run <script.py>                         ← load (deploy-workspace)
│     └── dlthub local run <job> --dry-run               ← load (deploy-workspace)
│
├── "Serve an interactive notebook / dashboard"
│     ├── @run.interactive  OR  import marimo_module     ← load (prepare-deployment)
│     └── dlthub serve <name>                             ← load (deploy-workspace)
│
├── "Diagnose a CLI error"
│     ├── Interactive-matched error                       ← runbook §2.1
│     ├── No module named 'cianfhoghlaim'                ← runbook §2.2
│     ├── Workspace not yet initialized                   ← runbook §2.3
│     ├── FastMCP support not installed                   ← runbook §2.4
│     └── No toolkit with workflow installed              ← runbook §2.5
│
└── "Set up / verify the workspace"
      ├── First-time init                                 ← load (setup-runtime)
      ├── Production credentials + destination             ← load (prepare-deployment)
      └── Job failed / flaky                              ← load (debug-deployment)
```

## Toolkit set (the 8 production toolkits)

Per the runbook §4 + the dlthub-platform skill, the 8 production toolkits
to install for a full-stack setup are:

```bash
dlthub ai init --agent claude                                   # installs `init` (rules + dlt-workspace MCP)
for t in rest-api-pipeline sql-database-pipeline \
          filesystem-pipeline dlthub-platform \
          data-exploration data-quality transformations; do
    dlthub ai toolkit install "$t"
done
uv sync --directory cianfhoghlaim --extra dlthub-platform       # installs `fastmcp-slim[server]`
claude                                                           # restart so MCP server picks up
```

After install, `dlthub ai status` should list all 8 toolkits and the only
remaining warnings should be the heuristic workspace-marker note (which
disappears once `dlthub init --name cianfhoghlaim` has been run from
inside the workspace root).

## Cross-references

- `docs/agents/dlthub-run-vs-serve.md` — the full diagnostic runbook (5
  sections, 5 error recipes, 5-step health check, canonical happy-path)
- `openspec/specs/dlthub-platform-integration/spec.md` — the contract
- `openspec/changes/2026-07-06-wire-dlthub-platform-toolkits-and-deployment/`
  — the change record
- `dlthub-ai-workbench/.claude-plugin/marketplace.json` —
  the vendored workbench marketplace
- `__deployment__.py` — the deployment manifest
- `dlt/jobs/government_circulars_job.py` — the first
  `@run.pipeline("government_circulars_ingest")` job

## Workbench skills (post-install)

After `dlthub ai init + dlthub ai toolkit install dlthub-platform`,
these 4 skills are available to the assistant:

- `setup-runtime` — first-time workspace check (5 steps)
- `prepare-deployment` — production credentials + destination setup
- `deploy-workspace` — `dlthub deploy` / `dlthub local run` / `dlthub
  run` / `dlthub serve` / scheduling
- `debug-deployment` — `dlthub job list`, `dlthub job logs`,
  `dlthub info`, `dlthub local pipeline list`
