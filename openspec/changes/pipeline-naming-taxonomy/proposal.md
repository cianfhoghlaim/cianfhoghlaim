## Why

The data-platform naming surface has drifted in ways that cost real
agent and contributor time: three spellings of the flagship pipeline
(`biep`/`biiep`/`bie`) living side by side in the same directories,
unnormalised `pipeline_name=` string literals (one literally `foo`),
and no documented contract for the `orchestration/defs/` vs
`orchestration/pipelines/` two-tree split. None of this blocks
anything today, but each additional pipeline added under the current
ambiguity increases the eventual rename's blast radius. This change
establishes the naming law once, in one spec, so every subsequent
rename task cites the same authority.

## What Changes

- Establish **one naming law** (this change's spec) covering: the
  canonical BIEP spelling, the `pipeline_name=` template
  (`<domain>_<source>_pipeline`), the `orchestration/defs/` vs
  `orchestration/pipelines/` division of labour requirement on the
  AGENTS.md, the deprecation-shim expiry policy (dated, not
  indefinite), and the sibling-sprawl nesting threshold.
- **Adopt, not duplicate, in-flight rename work** as the execution
  vehicle for legacy renames. This change's spec supplies the
  naming-law authority those tasks should conform to; it does not
  re-derive a competing task list.
- **BREAKING** (naming convention, not immediate code): every future
  pipeline addition MUST follow the naming law in this change's
  spec; existing pipelines are renamed incrementally, not in one mass
  commit.

## Capabilities

### New Capabilities
- `pipeline-naming-taxonomy`: the canonical naming law for pipeline
  identifiers, directory structure, and deprecation-shim lifecycle
  across `dlt_sources/`, `orchestration/`, and `cocoindex_flows/`.

### Modified Capabilities
(none — this change establishes the law; execution against existing
pipelines happens via separate, in-flight changes, each of which
carries its own spec delta against the specific capability it touches)

## Impact

- **Affected code** (not touched by this change; scoped as tasks):
  `dlt_sources/`, `orchestration/`, `cocoindex_flows/` files. Each
  rename is a follow-up change.
- **Affected skills**: the `dlt`, `dagster`, `cocoindex`, and
  `data-engineering-pipeline-documentation` skills may need cross-
  references updated once this change archives.

## Dependencies

`Blocked by: none`
`Blocked by (soft): none`
`Affected repos: cianfhoghlaim`