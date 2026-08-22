## ADDED Requirements

### Requirement: mise-tool-version-pinning

The `mise.toml [tools]` block SHALL pin **all tools that participate in
the BIEP pipeline** (uv, bun, dagger, pulumi, infisical, duckdb,
opencode-ai) to **exact versions** (e.g., `"0.12.5"`, `"1.4.0"`).
**External infrastructure tools** (gh, cloudflared, gcloud, oci, sops,
aqua, zoxide) MAY remain pinned to `"latest"` because their release
cadence and breaking-change frequency don't directly affect the
pipeline.

Exact-version pinning is required because the mise `aqua:` backend
doesn't support caret range syntax (`^X.Y.Z`) as of 2026-08-22 —
caret notation is interpreted as a literal tag and fails with 404
errors. Exact pins give full determinism and work with all backends
(`aqua:`, `core:`, `github:`, `npm:`, etc.).

#### Scenario: pipeline-critical tools pinned to exact versions

- **WHEN** a pipeline-critical tool (uv, bun, dagger, pulumi,
  infisical, duckdb, opencode-ai) is added to `[tools]`
- **THEN** the pin SHALL be an exact `X.Y.Z` version (e.g., `"0.12.5"`)
- **AND** the pin SHALL be updated via an openspec change that
  documents the new version + any breaking changes

#### Scenario: external infrastructure tools may use latest

- **WHEN** a tool is an external infrastructure CLI (gh, cloudflared,
  gcloud, oci, sops, aqua, zoxide) is added to `[tools]`
- **THEN** the pin MAY remain `"latest"`
- **AND** the tool SHALL be tracked via a separate audit cycle (the
  `core:tool-versions:check-stale` task + the Firecrawl upstream
  monitoring)

#### Scenario: external infrastructure tools may use latest

- **WHEN** a tool is an external infrastructure CLI (gh, cloudflared,
  gcloud, oci, sops, aqua, zoxide) is added to `[tools]`
- **THEN** the pin MAY remain `"latest"`
- **AND** the tool SHALL be tracked via a separate audit cycle (the
  `core:tool-versions:check-stale` task + the Firecrawl upstream
  monitoring)

### Requirement: tool-version-observability

The dev environment SHALL expose 2 observability tasks that report +
check the resolved toolchain:

- `core:tool-versions:report` — emits a structured table of all
  installed tools + their resolved versions
- `core:tool-versions:check-stale` — queries the latest released
  version for each pinned tool + emits a warning per stale tool +
  exits 1 if any tool is > 1 major behind

#### Scenario: tool-versions:report exits 0

- **WHEN** `mise run core:tool-versions:report` runs
- **THEN** the command MUST exit 0
- **AND** the output MUST contain at least 14 rows (one per `[tools]`
  entry)
- **AND** each row MUST show `name@version`

#### Scenario: tool-versions:check-stale exits 1 for stale tools

- **WHEN** `mise run core:tool-versions:check-stale` runs
- **AND** any pinned tool is > 1 major behind the latest
- **THEN** the command MUST exit 1
- **AND** the output MUST list each stale tool + the gap

#### Scenario: tool-versions:check-stale is a CI gate

- **WHEN** the change author opens an openspec change that updates a
  pinned tool range
- **THEN** the change SHALL include the result of
  `mise run core:tool-versions:check-stale` (exit 0 expected)
- **AND** the CI gate SHALL validate that no warning is emitted for
  the tool being upgraded
