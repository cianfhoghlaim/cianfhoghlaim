## ADDED Requirements

### Requirement: Workspace Initialisation

The system SHALL maintain a dlthub Platform workspace rooted at `cianfhoghlaim/` with `.dlt/.workspace` (marker file), `.dlt/config.toml` containing `[runtime] workspace_id` and `[runtime] organization_id`, and `.dlt/secrets.toml` containing the dltHub access token (gitignored).

The `workspace_id` and `organization_id` SHALL match the connected dltHub Platform organisation "cianfhoghlaim" (workspace id `03d1920f-00dd-40cb-a617-95d7bbfef20f`, organisation id `3b017615-31d6-4a58-a7e3-05fd3eb7ac85`).

#### Scenario: Workspace init succeeds

- **WHEN** the user runs `cd cianfhoghlaim && dlthub init --name cianfhoghlaim`
- **THEN** `.dlt/.workspace`, `.dlt/config.toml`, and `.dlt/secrets.toml` are created under `cianfhoghlaim/.dlt/`
- **AND** `dlthub info` prints the connected workspace name `cianfhoghlaim` and organisation id `03d1920f-00dd-40cb-a617-95d7bbfef20f`

#### Scenario: Re-init is idempotent

- **WHEN** `dlthub init` is run on a workspace that already has `.dlt/.workspace` populated
- **THEN** the CLI SHALL refuse to overwrite the existing config
- **OR** SHALL accept `--force` and back up the previous `.dlt/config.toml` to `.dlt/config.toml.bak` before regeneration

### Requirement: AI Workbench Toolkits Installed

The system SHALL have the 8 production dlthub AI toolkits installed into the Claude Code plugin directory via `dlthub ai toolkit install <name>`:

1. `init` (shared rules + secrets handling + dlt-workspace MCP)
2. `rest-api-pipeline`
3. `sql-database-pipeline`
4. `filesystem-pipeline`
5. `dlthub-platform`
6. `data-exploration`
7. `data-quality`
8. `transformations`

The vendor source SHALL be `cianfhoghlaim/dlthub-ai-workbench/.claude-plugin/marketplace.json` (the local mirror of `dlt-hub/dlthub-ai-workbench`).

#### Scenario: All 8 toolkits report installed

- **WHEN** the user runs `dlthub ai status` after installation
- **THEN** the output SHALL list all 8 toolkits under "Installed toolkits"
- **AND** SHALL NOT print the warning "No toolkit with workflow is installed!"

#### Scenario: MCP server starts

- **WHEN** the user runs `dlthub ai mcp run --stdio`
- **THEN** the FastMCP server SHALL start without the "FastMCP server support is not installed" warning
- **AND** SHALL announce the 8 dlt-workspace MCP tools (`list_tables`, `preview_table`, `execute_sql_query`, `get_row_counts`, `display_schema`, `get_local_pipeline_state`, `secrets_view_redacted`, `secrets_update_fragment`)

### Requirement: MCP Server Support

The system SHALL include `fastmcp-slim[server]` as a runtime dependency (or under a `dlthub-platform` optional-dependency group) in `pyproject.toml` so the `dlthub ai mcp run` command can launch the dlt-workspace MCP server.

#### Scenario: fastmcp importable after uv sync

- **WHEN** the user runs `uv sync` followed by `python -c "import fastmcp"`
- **THEN** the import SHALL succeed without `ModuleNotFoundError`

#### Scenario: MCP tools discoverable after install

- **WHEN** Claude Code restarts with `claude` after `dlthub ai init`
- **THEN** the dlt-workspace MCP server SHALL appear in the assistant's tool registry
- **AND** SHALL expose all 8 tools (the 6 data tools + 2 secrets tools)

### Requirement: Workbench Vendoring

The system SHALL vendor a copy of the upstream `dlt-hub/dlthub-ai-workbench` repository at `cianfhoghlaim/dlthub-ai-workbench/`.

The vendored copy SHALL include the marketplace catalog (`.claude-plugin/marketplace.json` listing all 11 toolkits), the `workbench/` tree (one directory per toolkit, each with `.claude-plugin/{plugin,toolkit}.json`, `skills/`, `commands/`, `rules/`), and the 4 supporting root files (`CLAUDE.md`, `README.md`, `Makefile`, `pyproject.toml`).

The vendor copy SHALL stay in lock-step with the upstream `dlt-hub/dlthub-ai-workbench` release tag (currently v0.1.1 marketplace, v0.1.3 dlthub-platform plugin per the vendored `marketplace.json`).

#### Scenario: Vendor catalogue is discoverable

- **WHEN** the user runs `dlthub ai toolkit list` with the vendored marketplace on disk
- **THEN** the CLI SHALL list all 11 toolkits (the 8 production + `bootstrap` + `quick-start` + `one-shot`)

#### Scenario: Vendor drift detection

- **WHEN** the upstream `dlt-hub/dlthub-ai-workbench` `marketplace.json` is updated
- **THEN** a vendor bump PR SHALL be filed against `cianfhoghlaim/dlthub-ai-workbench/.claude-plugin/marketplace.json` reflecting the new toolkit set
- **AND** the 8 installed toolkits SHALL be re-run via `dlthub ai toolkit install <name> --force` to pick up the new skill versions

### Requirement: Deployment Manifest Authoring

The system SHALL maintain a deployment manifest at `cianfhoghlaim/__deployment__.py` that registers every BIEP batch pipeline as a `@run.pipeline(name)` decorated function from `dlt.hub` and lists them in `__all__`.

The manifest SHALL be importable as a Python module — `from cianfhoghlaim.__deployment__ import __all__` SHALL succeed without side effects beyond decorator registration.

The root `__deployment__.py` SHALL be a stub (`__all__: list[str] = []`) — the canonical manifest lives under `cianfhoghlaim/` so the dlthub workspace root and the Python package root are co-located.

#### Scenario: Manifest resolves cleanly

- **WHEN** the user runs `dlthub deploy --dry-run`
- **THEN** the CLI SHALL print a summary listing every job in `__all__` with its `@run.pipeline` name
- **AND** SHALL print 0 errors

#### Scenario: Empty manifest degrades gracefully

- **WHEN** the manifest `__all__` is empty
- **THEN** `dlthub deploy --dry-run` SHALL print "0 jobs to deploy" and exit 0
- **AND** `dlthub run` with no argument SHALL fail with `Matched jobs are interactive (not allowed here): jobs.workspace.dashboard. Use the serve command instead.` — pointing the user at `dlthub serve` for interactive jobs or at populating the manifest for batch jobs

### Requirement: Run vs Serve Hygiene

The system SHALL distinguish batch jobs (pipelines + scripts, decorated with `@run.pipeline` or `@run.job`) from interactive jobs (notebooks + dashboards, decorated with `@run.interactive` or imported as marimo modules).

The deployment manifest SHALL NOT register interactive notebooks alongside batch pipelines in the same `__all__`. Interactive jobs SHALL live in a sibling module (e.g. `cianfhoghlaim/__interactive__.py`) referenced from a separate `dlthub serve` invocation.

#### Scenario: dlthub run on an interactive job fails predictably

- **WHEN** the user runs `dlthub run jobs.workspace.dashboard` (the system-provided interactive dashboard)
- **THEN** the CLI SHALL exit non-zero with the message `Matched jobs are interactive (not allowed here): jobs.workspace.dashboard. Use the serve command instead.`
- **AND** SHALL print a help pointer to `dlthub serve jobs.workspace.dashboard`

#### Scenario: dlthub serve on a batch job fails predictably

- **WHEN** the user runs `dlthub serve <batch_pipeline_name>` for a registered `@run.pipeline` job
- **THEN** the CLI SHALL exit non-zero with the message `Matched jobs are batch (not allowed here): <batch_pipeline_name>. Use the run command instead.`

#### Scenario: Explicit script path bypasses the auto-matcher

- **WHEN** the user runs `dlthub run cianfhoghlaim/dlt/british_isles/ireland/education/gov_ie_circulars.py`
- **THEN** the CLI SHALL sync the script to the workspace and execute it as a one-shot batch job
- **AND** SHALL NOT consult `__deployment__.py` or the system `jobs.workspace.dashboard` registry

### Requirement: Runbook for Diagnosing dlthub CLI Errors

The system SHALL provide a runbook at `docs/agents/dlthub-run-vs-serve.md` documenting:

1. The `dlthub run` vs `dlthub serve` split (batch vs interactive)
2. The 5 most common error messages and their recovery (interactive-matched, no-script, missing-profile, no-workspace, missing-toolkit)
3. The 5-step `dlthub ai status` health check sequence
4. The canonical happy-path workflow from `dlthub init` → `dlthub ai init` → toolkit install → manifest author → `dlthub deploy --dry-run` → `dlthub run`

#### Scenario: Runbook resolves the reported error

- **WHEN** the user encounters `Matched jobs are interactive (not allowed here): jobs.workspace.dashboard. Use the serve command instead.`
- **THEN** the runbook SHALL prescribe `dlthub serve jobs.workspace.dashboard` as the first recovery step
- **AND** SHALL prescribe `dlthub run <explicit_script.py>` as the second recovery step (when the user actually wants to run a batch job)
- **AND** SHALL cross-link the `(setup-runtime)`, `(prepare-deployment)`, `(deploy-workspace)`, and `(debug-deployment)` skills from `cianfhoghlaim/dlthub-ai-workbench/workbench/dlthub-platform/skills/`

#### Scenario: Runbook kept current

- **WHEN** `mise run lint:skills` runs and any dlthub-related skill fails the 4-rule metadata lint
- **THEN** the offending skill SHALL be updated within the same change to satisfy the lint
- **AND** the runbook's cross-link to the skill SHALL be re-verified
