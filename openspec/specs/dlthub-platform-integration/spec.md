# Spec: `dlthub-platform-integration`

## Purpose

The Cianfhoghlaim `dlthub` Platform integration is the deployment surface
between the BIEP / lakehouse / CocoIndex pipelines running locally on
`bunchloch` (MacBook M4) and the dltHub Platform managed runtime. Without
this integration, pipelines run only via the local Dagster UI
(`mise run dagster:oideachais`) and never reach the cloud runtime, the
managed MotherDuck instance, or the workspace dashboard.

This spec defines the **5 contracts** that hold the integration together:

1. A dlthub Platform workspace rooted at `cianfhoghlaim/` (the `.dlt/`
   marker, the `config.toml` workspace_id, the gitignored `secrets.toml`)
2. The 8 production AI workbench toolkits (`init` + 7) installed into
   Claude Code via `dlthub ai toolkit install`
3. A deployment manifest at `cianfhoghlaim/__deployment__.py` that
   registers `@run.pipeline` decorated batch jobs under `__all__`
4. The `dlthub run` vs `dlthub serve` hygiene rule (batch ≠ interactive)
5. A runbook at `docs/agents/dlthub-run-vs-serve.md` that captures the 5
   most common error messages and their recovery

The canonical error this spec eliminates is:

```
Matched jobs are interactive (not allowed here): jobs.workspace.dashboard.
Use the `serve` command instead.
```

## Capability summary

| Concern | Tool / Contract | Storage |
|:--|:--|:--|
| Auth + workspace connect | `dlthub login` → device-code OAuth | `.dlt/.workspace` (zero-byte marker) |
| Workspace identity | `dlthub workspace connect` | `.dlt/config.toml` `[runtime] workspace_id` + `[runtime] organization_id` |
| Access token | Auto-refreshed at runtime | `.dlt/secrets.toml` (gitignored) |
| AI toolkit install | `dlthub ai toolkit install <name>` | Claude Code `.claude/` plugins dir |
| MCP server | `dlthub ai mcp run --stdio` | stdio transport; 8 tools (`list_tables`, `preview_table`, `execute_sql_query`, `get_row_counts`, `display_schema`, `get_local_pipeline_state`, `secrets_view_redacted`, `secrets_update_fragment`) |
| Deployment manifest | `@run.pipeline(name)` in `__deployment__.py` `__all__` | remote workspace |
| Local simulation | `dlthub local run <job>` | local workspace |
| Cloud run / serve | `dlthub run <job>` (batch) / `dlthub serve <job>` (interactive) | remote runtime |
| Dashboard | `dlthub serve jobs.workspace.dashboard` (interactive) / `dlthub show` (web UI) | remote runtime |

## Non-goals

- This spec does NOT add new Docker Compose stacks (the 94-stack fleet at `bonneagar/stacks/` is owned by the `infrastructure-stacks` spec).
- This spec does NOT introduce new BAML extraction schemas (owned by `cianfhoghlaim-baml-schemas`).
- This spec does NOT replace the local Dagster UI (`mise run dagster:oideachais`) — it sits *alongside* it for the deployment half of the workflow.
- This spec does NOT mutate the Infisical + Locket + mise secrets contract (owned by the `secrets-management` skill).

## Cross-references

- `openspec/changes/2026-07-06-wire-dlthub-platform-toolkits-and-deployment/`
- `openspec/changes/2026-07-06-british-isles-education-pipeline-v1/` (the BIEP change that consumes this integration)
- `cianfhoghlaim/dlthub-ai-workbench/workbench/dlthub-platform/skills/{setup-runtime,prepare-deployment,deploy-workspace,debug-deployment}/SKILL.md`
- `cianfhoghlaim/__deployment__.py` (the live manifest)
- `docs/agents/dlthub-run-vs-serve.md` (the runbook)
- `.agents/skills/dlthub/SKILL.md` (KCG-side skill frontmatter)
- `.claude/skills/dlt-workbench-init/SKILL.md` (the workbench's own `init` plugin — installed by `dlthub ai init`)

## Requirements

### Requirement: Workspace Initialisation

The system SHALL maintain a dlthub Platform workspace rooted at `cianfhoghlaim/` with `.dlt/.workspace` (marker file), `.dlt/config.toml` containing `[runtime] workspace_id` and `[runtime] organization_id`, and `.dlt/secrets.toml` containing the dltHub access token (gitignored).

#### Scenario: Workspace init succeeds

- **WHEN** the user runs `cd cianfhoghlaim && dlthub init --name cianfhoghlaim`
- **THEN** `.dlt/.workspace`, `.dlt/config.toml`, and `.dlt/secrets.toml` are created under `cianfhoghlaim/.dlt/`

### Requirement: AI Workbench Toolkits Installed

The system SHALL have the 8 production dlthub AI toolkits installed into the Claude Code plugin directory via `dlthub ai toolkit install <name>` (`init`, `rest-api-pipeline`, `sql-database-pipeline`, `filesystem-pipeline`, `dlthub-platform`, `data-exploration`, `data-quality`, `transformations`).

### Requirement: MCP Server Support

The system SHALL include `fastmcp-slim[server]` as a runtime dependency in `pyproject.toml` so the `dlthub ai mcp run` command can launch the dlt-workspace MCP server.

### Requirement: Workbench Vendoring

The system SHALL vendor a copy of the upstream `dlt-hub/dlthub-ai-workbench` repository at `cianfhoghlaim/dlthub-ai-workbench/`, kept in lock-step with upstream release tags.

### Requirement: Deployment Manifest Authoring

The system SHALL maintain a deployment manifest at `cianfhoghlaim/__deployment__.py` that registers every BIEP batch pipeline as a `@run.pipeline(name)` decorated function from `dlt.hub` and lists them in `__all__`.

### Requirement: Run vs Serve Hygiene

The system SHALL distinguish batch jobs (`@run.pipeline` / `@run.job`) from interactive jobs (`@run.interactive` / marimo modules), and SHALL fail predictably when `dlthub run` is called on an interactive job or vice versa.

### Requirement: Runbook for Diagnosing dlthub CLI Errors

The system SHALL provide a runbook at `docs/agents/dlthub-run-vs-serve.md` documenting the `run`/`serve` split, the 5 most common error messages and their recovery, the 5-step `dlthub ai status` health check, and the canonical happy-path workflow.
