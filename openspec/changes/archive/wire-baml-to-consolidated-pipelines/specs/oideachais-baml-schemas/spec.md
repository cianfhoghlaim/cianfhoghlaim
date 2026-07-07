## MODIFIED Requirements

### Requirement: BAML consumer wiring contract

The system SHALL document that consumer code uses the canonical
`from cianfhoghlaim.baml_client import b` import (the BAML-generated
client namespace), NOT the source-file paths under `baml/`. The
BAML-generated client exposes a single namespace `b` with all 250+
functions from all 60+ source `.baml` files, regardless of which cluster
(`education/`, `celtic/`, `processing/`) or sub-directory
(`stages/`, `subjects/`, `pdfs/`, `gaois/`, etc.) the source file
came from.

Consumer docstrings + comments that previously referenced the old
flat `baml_src/X.baml` paths SHALL be updated to reference the new
cluster paths (`baml/education/`, `baml/celtic/`, `baml/processing/`)
per the `baml-reorganize-by-cluster` change. This is a documentation
update only — the runtime BAML client interface is unchanged.

#### Scenario: A consumer docstring references the old flat path

- **GIVEN** a Python file in `dlt/`, `dagster/`, `agents/`, `cocoindex/`,
  or `notebooks/` that has a docstring containing
  `baml_src/aistear.baml` or similar old flat-path references
- **WHEN** the `openspec/changes/wire-baml-to-consolidated-pipelines/`
  change is applied
- **THEN** the docstring is updated to reference the new cluster path
  (e.g. `baml/education/stages/aistear.baml` for the merged aistear
  file)
- **AND** `ccc search "baml_src/"` returns 0 hits in the consumer
  subtrees (only hits in `openspec/` itself)

#### Scenario: A consumer uses the canonical baml_client namespace

- **GIVEN** a consumer file with
  `from cianfhoghlaim.baml_client import b`
- **WHEN** it calls `b.ExtractAistearFramework(text=text, language="en")`
- **THEN** the call resolves to the function defined in
  `baml/education/stages/aistear.baml` (post-`baml-reorganize-by-cluster`)
- **AND** the function signature matches
  `ExtractAistearFrameworkFromText(text, language)` OR the backward-compat
  alias `ExtractAistearFramework(text, language)` (both defined in the
  merged file)

### Requirement: BAML project config for regeneration

The system SHALL provide a BAML project config file that enables future
regeneration of the BAML client from the new cluster taxonomy. The
config SHALL be at `cianfhoghlaim/baml/baml.toml` with 2 generators:

- `lang_py` → `output_type = "python/pydantic"`,
  `output_dir = "../baml/shared/baml_client"`, `version = "0.222.0"`
- `lang_ts` → `output_type = "typescript"`,
  `output_dir = "../baml/shared/baml_client_ts"`, `version = "0.222.0"`

A symlink `cianfhoghlaim/baml_src → cianfhoghlaim/baml` SHALL be created
so that the BAML CLI (which hardcodes `baml_src/` as the source directory)
can discover the new cluster taxonomy without renaming any files. The
symlink SHALL be in `.gitignore` (it's a regen-time artifact, not a
runtime dependency).

#### Scenario: The BAML CLI is run to regenerate the client

- **GIVEN** the BAML project config at `cianfhoghlaim/baml/baml.toml`
  with the 2 generators + the `baml_src` symlink
- **WHEN** `baml-cli generate --from cianfhoghlaim/baml_src` is run
- **THEN** the BAML compiler discovers the 60+ `.baml` files at the
  new cluster paths (`education/`, `celtic/`, `processing/`)
- **AND** the generated Python client is written to
  `cianfhoghlaim/baml/shared/baml_client/`
- **AND** the generated TypeScript client is written to
  `cianfhoghlaim/baml/shared/baml_client_ts/`

### Requirement: Pre-existing BAML syntax errors (documented gap)

The system MUST document that the BAML client at `baml/shared/baml_client/`
is currently a STUB
that does NOT include the 250+ BAML functions. The system SHALL
document this as a pre-existing gap in the spec:

- **Root cause**: the original `.baml` files used Python-style colon
  syntax (`name: string` instead of BAML syntax `name string`).
  The BAML compiler rejects this with 1480+ validation errors.
- **Affected files**: ~51 of the 60+ `.baml` files (per a
  `grep -rln ": string\b\|: int\b\|: bool\b\|: float\b"` audit).
- **Workaround in place**: most consumer code uses
  `try/except ImportError` graceful degradation, so they no-op when
  the BAML client is not generated.
- **Follow-up issue**: `fix-pre-existing-baml-syntax-errors` —
  rewrites the ~51 BAML files that use colon syntax to use BAML
  syntax (drop the colon, add space). This unblocks BAML
  regeneration and restores the runtime BAML client.

#### Scenario: A developer tries to regenerate the BAML client today

- **WHEN** `baml-cli generate --from cianfhoghlaim/baml_src` is run
- **THEN** the BAML compiler reports 1480+ validation errors
  (mostly "No type specified for field `X`" due to colon syntax)
- **AND** the build fails before any generated code is written
- **AND** the spec points the developer at the
  `fix-pre-existing-baml-syntax-errors` follow-up issue

#### Scenario: The fix-pre-existing-baml-syntax-errors follow-up is applied

- **WHEN** the 51 BAML files with colon syntax are rewritten (drop the
  colon, add space — e.g. `name: string` → `name string`)
- **THEN** `baml-cli generate --from cianfhoghlaim/baml_src` succeeds
- **AND** the generated Python client at
  `baml/shared/baml_client/` contains all 250+ functions
- **AND** consumer code calling `b.ExtractAistearFramework(text, language)`
  resolves to the function at runtime (no more `try/except ImportError`)