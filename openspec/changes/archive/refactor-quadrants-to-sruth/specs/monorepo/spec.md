## ADDED Requirements

### Requirement: sruth/ directory convention

The system SHALL place each sruth's Python source tree under `sruth/<flow>/`
where `<flow>` ∈ {`codeolas`, `oideachais`, `meaisinfhoghlaim`, `tuatha`,
`crypteolas`, `croilar`}.

#### Scenario: All 5 sruthanna live under sruth/

- **GIVEN** the top-level directory listing
- **WHEN** running `ls sruth/`
- **THEN** the output contains exactly: `codeolas/`, `sruth/crypteolas/`,
  `sruth/croilar/`, `sruth/meaisinfhoghlaim/`, `sruth/oideachais/`, `sruth/tuatha/`
- **AND** no top-level directory outside `sruth/` has the same name
- **AND** no sruth directory exists at the repo root (e.g. no `sruth/oideachais/`
  at root)

#### Scenario: Cross-cutting dirs remain at root

- **GIVEN** the cross-cutting infrastructure, personal archive, and tooling
- **WHEN** running `ls` at the repo root
- **THEN** the output includes `infrastructure/`, `leabharlann/`,
  `openspec/`, `spaces/`, `dlthub/`, `archive/`, `scripts/`,
  `cian_mac_an_déisigh_uí_liatháin/`, `.agents/skills/` at the root
  level (NOT under `sruth/`)

#### Scenario: Per-sruth pyproject.toml present

- **GIVEN** each sruth that ships Python source
- **WHEN** checking for a workspace member declaration
- **THEN** `sruth/<flow>/pyproject.toml` exists with a `[project]` block,
  a `[tool.uv]` block (or root-level equivalent), and the sruth is
  declared in the root `pyproject.toml`'s `[tool.uv.workspace] members`
  list as `"sruth/<flow>"`

### Requirement: 4 atomic commits per refactor

The system SHALL split any future filesystem refactor that moves sruthanna or restructures workspace membership into atomic commits such that each commit moves exactly one sruth (or a related cluster like `tuatha` + `crypteolas` + `croilar` when moving them in sequence is operationally cheap). Each commit MUST leave the repository in a buildable state and MUST be independently revertable via `git revert <sha>`.

#### Scenario: Commit granularity

- **GIVEN** a refactor that moves ≥2 sruthanna
- **WHEN** writing the refactor commits
- **THEN** no single commit moves more than one independent sruth
  (the `tuatha` + `crypteolas` + `croilar` cluster is the only allowed
  exception, documented in `refactor-quadrants-to-sruth/tasks.md`
  Phase E)
- **AND** each commit leaves the repository in a buildable state
  (`mise run py:typecheck` passes after each commit)
- **AND** each commit is independently revertable via `git revert <sha>`

### Requirement: baml_src distribution per sruth

The system SHALL keep BAML extraction schemas inside each sruth's own
`baml_src/` directory; the root `baml_src/` directory SHALL NOT exist
in the final state.

#### Scenario: Per-sruth baml_src

- **GIVEN** the post-refactor filesystem
- **WHEN** running `ls -d sruth/*/baml_src/`
- **THEN** the output lists `sruth/oideachais/baml_src/`,
  `sruth/meaisinfhoghlaim/baml_src/`, `sruth/tuatha/baml_src/`,
  `sruth/croilar/baml_src/`, `sruth/crypteolas/baml_src/`
- **AND** `ls baml_src/` returns "No such file or directory"
- **AND** `ls sruth/codeolas/baml_src/` returns "No such file or directory"
  (codeolas is a pure Python library; no BAML)

#### Scenario: 3 merged BAML files live in sruth/oideachais

- **GIVEN** the merged BAML corpus
- **WHEN** reading `sruth/oideachais/baml_src/clients.baml`,
  `sruth/oideachais/baml_src/curriculum_extraction.baml`,
  `sruth/oideachais/baml_src/official_media.baml`
- **THEN** each file contains all `client` blocks from both the original
  root copy and the original `sruth/oideachais/baml_src/` copy (no client
  blocks lost; duplicate client names deduplicated with `_v2` suffix)

#### Scenario: gaois/ BAML files in sruth/meaisinfhoghlaim

- **GIVEN** the 4 gaois BAML files moved from oideachais → meaisinfhoghlaim
- **WHEN** checking `sruth/meaisinfhoghlaim/baml_src/gaois/`
- **THEN** the output contains `duchas.baml`, `folklore_extraction.baml`,
  `logainm.baml`, `tearma.baml`
- **AND** no copy of these files exists in `sruth/oideachais/baml_src/gaois/`

### Requirement: Root baml_src deletion gate

The system SHALL NOT delete the root `baml_src/` directory until every
file in it has been verified to have a corresponding file in some
`sruth/<flow>/baml_src/`.

#### Scenario: Verification step before deletion

- **GIVEN** the refactor is in progress and root `baml_src/` still exists
- **WHEN** running the Phase F gate from
  `refactor-quadrants-to-sruth/tasks.md`
- **THEN** every `.baml` file at root has a destination in some
  `sruth/<flow>/baml_src/`
- **AND** every `.md` file at root (`README.md`, `SCHEMAS_AND_TYPES.md`)
  has been either deleted (if its content is redundant) or archived
  into an openspec spec (e.g. `openspec/specs/baml-extraction/`)
- **AND** only THEN is `git rm -r baml_src` executed (commit 5)

### Requirement: Explicit sruth.<flow>. import prefix

The system SHALL use explicit `sruth.<flow>.` Python imports rather than
relying on PYTHONPATH manipulation, sys.path injection, or relative-only
imports across sruth boundaries.

#### Scenario: Cross-sruth import uses sruth. prefix

- **GIVEN** the file `sruth/meaisinfhoghlaim/agents/curriculum_agent.py`
- **WHEN** importing a function from `sruth.oideachais`
- **THEN** the import is `from sruth.oideachais.baml_src.X import Y`
  (explicit, namespaced, works from any sruth without PYTHONPATH changes)

#### Scenario: No quadrant-only imports remain

- **GIVEN** the post-refactor codebase
- **WHEN** running `git grep "from oideachais\."` or any of the 5 other
  quadrants
- **THEN** the output is empty (zero matches)
- **AND** running `git grep "import tuatha\."` is also empty
- **AND** running `git grep "import meaisinfhoghlaim\."` is also empty
- **AND** running `git grep "import croilar\."` is also empty
- **AND** running `git grep "import crypteolas\."` is also empty
- **AND** running `git grep "import codeolas\."` is also empty