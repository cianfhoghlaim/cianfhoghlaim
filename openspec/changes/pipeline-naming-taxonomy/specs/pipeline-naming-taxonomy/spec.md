## Purpose

Defines the single naming law for pipeline identifiers, directory
structure, and deprecation-shim lifecycle shared across `dlt_sources/`,
`orchestration/`, and `cocoindex_flows/`, so future pipelines are added
consistently and existing drift has a documented target to converge
on.

## ADDED Requirements

### Requirement: The flagship pipeline uses one canonical spelling

The canonical spelling for the British Isles Education Pipeline SHALL
be `bep` in all new code, file names, and identifiers. `biiep` and
`bie-` SHALL NOT be used in new code; existing occurrences are
migrated incrementally per the in-flight rename work.

#### Scenario: A new file for this pipeline uses the canonical spelling
- **WHEN** a contributor adds a new module for the British Isles
  Education Pipeline
- **THEN** the module name, any function/class names referencing the
  pipeline, and any string literals use `bep`
- **AND** a search for `biiep` or `bie-` outside
  `openspec/changes/archive/` returns no new occurrences in code added
  after this change archives

### Requirement: `pipeline_name=` literals follow one template

Every dlt `pipeline_name=` string literal SHALL follow the template
`<domain>_<source>_pipeline` (e.g. `leabharlann_books_pipeline`,
`ireland_lc_pipeline`). Placeholder values (e.g. `foo`) SHALL NOT be
committed. Semantically identical pipelines SHALL NOT have more than
one `pipeline_name` value.

#### Scenario: A new dlt source follows the naming template
- **WHEN** a contributor adds a new `@dlt.source`-decorated pipeline
- **THEN** its `pipeline_name=` argument matches
  `^[a-z][a-z0-9_]*_pipeline$`
- **AND** it is not a duplicate of an existing pipeline's name under a
  different string

### Requirement: The three pipeline trees stay cross-referenceable

For any dlt source with a corresponding Dagster Component and/or
CocoIndex embedding flow, the three trees (`dlt_sources/`,
`orchestration/pipelines/`, `cocoindex_flows/`) SHALL use a
discoverable naming correspondence (matching top-level directory name,
or an explicit cross-reference in each tree's `AGENTS.md`) such that an
agent can determine whether a given pipeline has ingestion, Dagster,
and embedding coverage without exhaustively grepping all three trees.

#### Scenario: Parity is checkable
- **WHEN** a contributor asks "does pipeline X have a Dagster asset and
  an embedder?"
- **THEN** the answer is derivable from a single generated index (e.g.
  `orchestration/pipelines/INDEX.md` or a `mise run pipelines:parity-check`
  task) rather than requiring a manual 3-tree grep

### Requirement: The `defs/` vs `pipelines/` two-tree division of labour is documented

`orchestration/AGENTS.md` SHALL state explicitly which concerns belong
in the horizontal `defs/` tree (5-layer Component model) versus the
vertical `pipelines/` tree (per-pipeline Component model), such that a
contributor adding a new pipeline knows which tree to add it to without
guessing.

#### Scenario: A contributor knows where to add a new pipeline's Dagster Component
- **WHEN** a contributor adds Dagster asset definitions for a new dlt
  source
- **THEN** `orchestration/AGENTS.md` states unambiguously whether the
  new Component belongs under `defs/<layer>/` or `pipelines/<domain>/`

### Requirement: Deprecation shims declare an expiry date

Every entry in `dlt_sources/LEGACY_ALIASES.md` and
`cocoindex_flows/LEGACY_ALIASES.md` SHALL declare an `expires:
YYYY-MM-DD` date. A shim past its expiry date SHALL be flagged by a
lint gate rather than persisting indefinitely.

#### Scenario: An expired shim is flagged
- **WHEN** a shim's declared `expires:` date has passed
- **AND** the shim has not been removed or its expiry extended with a
  documented reason
- **THEN** the lint gate reports it as a failure

### Requirement: Sibling directories for one domain are nested, not flat

When multiple top-level `dlt_sources/` directories cover sub-concerns
of a single domain (e.g. `crypteolas*`, `media*`, `cv`/`artwork`/
`labels`/`portfolio`), they SHALL be nested under one parent directory
rather than existing as independent flat siblings, once that domain
has 3 or more such sub-concern directories.

#### Scenario: A domain crossing the 3-sibling threshold gets nested
- **WHEN** a domain accumulates a 3rd flat sibling directory (e.g. a
  3rd `crypteolas_*` directory)
- **THEN** the existing siblings are nested under one parent directory
  in the same change that adds the 3rd