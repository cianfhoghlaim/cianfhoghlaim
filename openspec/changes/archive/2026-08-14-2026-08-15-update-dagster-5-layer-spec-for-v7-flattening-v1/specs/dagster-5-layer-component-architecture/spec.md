## ADDED Requirements

### Requirement: After the v7 flattening, `registry_modules` uses the repo-root `orchestration.components` path

The system MUST declare `pyproject.toml:[tool.dg].registry_modules = ["orchestration.components"]` so the `dg` CLI auto-discovers the 5 KCG Components (and the 5 BIEP v3 jurisdiction-scoped + 3 deferred-L3 components) from the repo-root path. The pre-v7 form `["cianfhoghlaim.dagster.components"]` MUST NOT appear in the file. The system MUST NOT introduce a new path under `cianfhoghlaim.dagster.*` because that namespace was retired by the post-v7 flattening (per the `2026-07-17-v7-flatten-cianfhoghlaim-merge-bonneagar-rewrite-readme-license-v1` openspec change).

#### Scenario: `dg list components` discovers the 14 components

- **WHEN** `dg list components` runs after `mise install`
- **THEN** the output lists 14 component types (the 5 layer components
  + the 5 BIEP v3 jurisdiction-scoped + the 4 deferred-L3 components),
  all imported via the `orchestration.components.*` namespace

#### Scenario: The post-v7 footnote is present in pyproject.toml

- **WHEN** `grep -A3 "registry_modules" pyproject.toml` runs
- **THEN** the matching lines reference `["orchestration.components"]`
- **AND** a comment block (per the post-v7 flattening convention)
  explains the historical shift from `["cianfhoghlaim.dagster.components"]`

#### Scenario: The legacy `cianfhoghlaim.dagster.components` path is absent

- **WHEN** `grep -r "cianfhoghlaim.dagster.components" pyproject.toml`
- **THEN** zero matches appear
- **AND** `dg list components` exits 0 (the registry discovered the
  components from the canonical post-v7 path)