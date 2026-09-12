## MODIFIED Requirements

### Requirement: Identical absolute repository mount

The Bunchloch OpenChamber development stack SHALL mount the host repository
`/Users/cianmacandeisigh/dev/cianfhoghlaim` at that identical absolute
path inside the container. The stack MUST preserve the path identity used by
the host OpenCode server so session directory filters, worktrees, and git
operations resolve to the same project.

#### Scenario: Session project paths resolve identically

- **WHEN** a user opens the canonical repository from OpenChamber
- **THEN** the external OpenCode server receives
  `/Users/cianmacandeisigh/dev/cianfhoghlaim` as the project path
- **AND** git status and file discovery operate on the host checkout rather
  than a container-only path

#### Scenario: Legacy KCG mount path is retired

- **WHEN** the legacy `/Users/cianmacandeisigh/dev/kings_college_galway`
  directory no longer exists on the host (per the
  `2026-09-12-kcg-legacy-folder-retirement-v1` archive)
- **THEN** the OpenChamber dev container SHALL NOT expect a mount at that
  path
- **AND** all session-directory resolution SHALL fall back to the
  canonical `/Users/cianmacandeisigh/dev/cianfhoghlaim` mount

## ADDED Requirements

### Requirement: Canonical host-path indirection for live code

All cianfhoghlaim live code (DLT sources, Dagster assets, IaC bootstrap,
web app lineage registries, CocoIndex v1 Apps, MCP servers) that needs to
reference the host repository's local filesystem SHALL express that path
as `/Users/cianmacandeisigh/dev/cianfhoghlaim`, never as the legacy
`/Users/cianmacandeisigh/dev/kings_college_galway`. Python files that
expose a `samples_dir` to ingestion pipelines SHALL additionally honour
the `BIEP_SAMPLES_DIR` environment variable (per
`AGENTS.md §2. Respect the Ingestion Cache`) so CI / dev can override
without code changes.

#### Scenario: A DLT source's samples_dir resolves post-KCG-retirement

- **WHEN** any DLT source in `dlt_sources/` declares a `samples_dir` or
  `samples_root` pointing at the legacy KCG path
- **THEN** the live code reads its path from
  `/Users/cianmacandeisigh/dev/cianfhoghlaim/...` (or the
  `BIEP_SAMPLES_DIR` env override)
- **AND** the `FileNotFoundError` that would otherwise surface after
  `/Users/cianmacandeisigh/dev/kings_college_galway/` is deleted
  (per the `2026-09-12-kcg-legacy-folder-retirement-v1` archive)
  never occurs

#### Scenario: IaC bootstrap finds the bonneagar/ tree post-retirement

- **WHEN** an operator runs `iac:bootstrap` (the 8-phase state machine
  that walks `bonneagar/stacks/<name>/`)
- **THEN** the bootstrap script `cd`s into
  `/Users/cianmacandeisigh/dev/cianfhoghlaim/bonneagar/stacks/<name>/`
  rather than the deleted KCG path
- **AND** the iac:health check that follows the bootstrap can locate
  `/Users/cianmacandeisigh/dev/cianfhoghlaim/bonneagar/`

#### Scenario: Leaving Cert lineage-registry resolves real PDFs

- **WHEN** the TanStack Start web app reads the `pdf_path` field of any
  entry in `web/apps/cianfhoghlaim-leaving-cert/apps/web/src/lib/lineage-registry.ts`
- **THEN** every `pdf_path` points to an existing file under
  `/Users/cianmacandeisigh/dev/cianfhoghlaim/leaving_certificate/`
  (the canonical PDF home, not the deleted KCG directory)