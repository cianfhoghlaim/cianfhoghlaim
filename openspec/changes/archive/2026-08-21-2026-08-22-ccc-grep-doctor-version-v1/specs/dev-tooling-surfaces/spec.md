# dev-tooling-surfaces — ccc grep + ccc doctor + ccc version (delta)

## Purpose

This delta extends `dev-tooling-surfaces` with the canonical usage
of cocoindex-code 0.2.37+ new subcommands: `ccc grep` (structural
search), `ccc doctor` (system health), `ccc version` (version), and
`ccc search --json` (JSON output for tool integration).

## ADDED Requirements

### Requirement: ccc-grep-doctor-version-gates

The dev environment SHALL provide 4 cocoindex-code-related tasks
in the `core` namespace, all reachable via `mise run` and reflecting
the canonical ccc 0.2.40+ surface.

The ccc gates SHALL cover at minimum:

1. `core:ccc:grep` — structural search by example (no daemon needed)
2. `core:ccc:doctor` — system health check (index freshness + daemon)
3. `core:ccc:version` — print the installed cocoindex-code version
4. `core:ccc:search:json` — semantic search emitting JSON on stdout

#### Scenario: ccc grep is daemon-free

- **WHEN** `mise run core:ccc:grep "def <pattern>(" orchestration/` runs
- **THEN** the command MUST invoke `ccc grep` with the pattern + path
- **AND** it MUST NOT require the daemon to be running
- **AND** it MUST return matches in <2 seconds for repos <100k LOC

#### Scenario: ccc doctor is the health gate

- **WHEN** `mise run core:ccc:doctor` runs
- **THEN** the command MUST invoke `ccc doctor`
- **AND** exit 1 if the index is >7d stale
- **AND** exit 1 if the daemon has unhandled exceptions
- **AND** exit 0 if the system is healthy

#### Scenario: ccc version is the canonical version probe

- **WHEN** `mise run core:ccc:version` runs
- **THEN** the command MUST invoke `ccc version`
- **AND** print the exact installed version (e.g. `0.2.41`)
- **AND** exit 0

#### Scenario: ccc search:json emits structured JSON

- **WHEN** `mise run core:ccc:search:json "dagster asset"` runs
- **THEN** the command MUST invoke `ccc search --json`
- **AND** emit a JSON array of results on stdout
- **AND** each result MUST include `file_path`, `start_line`, `end_line`, `score`

#### Scenario: agent .md files reference ccc grep

- **WHEN** any of the 9 domain-specific agent `.md` files are read
- **THEN** the "Direct references (mirrors guides.yml)" section MUST
  mention `ccc grep` as the recommended tool for structural code searches
- **AND** the `mise run core:ccc:grep` invocation example MUST be present

## Cross-references

- `bun.lock` (ccc 0.2.41 already installed)
- `opencode.json` (the `cocoindex-code` MCP server is enabled)
- `.cocoindex_code/guides.yml` — the ccc concept guide
- https://github.com/cocoindex-io/cocoindex-code — ccc upstream docs
- `openspec/specs/dev-tooling-surfaces/spec.md` — the canonical contract
