# author-archive-multi-target Specification

## Purpose
TBD - created by archiving change author-archive-multi-target. Update Purpose after archive.
## Requirements
### Requirement: The 3 canonical targets

The system MUST provide 3 canonical `Target` instances:

  - ``DEV``     - ``destination="duckdb"``, dataset prefix
    ``"author_archive_dev"``, no required secrets, ``is_production=False``
  - ``STAGING`` - ``destination="motherduck"``, dataset prefix
    ``"author_archive_staging"``, requires ``MOTHERDUCK_TOKEN``,
    ``is_production=False``
  - ``PROD``    - ``destination="ducklake"``, dataset prefix
    ``"author_archive"``, requires 6 DUCKLAKE_* + ``BUCKET`` env
    vars, ``is_production=True``

#### Scenario: DEV target has no required secrets

- **WHEN** the user reads ``DEV.requires_secrets``
- **THEN** it returns an empty tuple
- **AND** the user can call ``create_pipeline_for_target("dev", ...)``
  without setting any env vars

#### Scenario: STAGING target requires MOTHERDUCK_TOKEN

- **WHEN** the user calls ``validate_target_secrets(STAGING)`` without
  setting ``MOTHERDUCK_TOKEN``
- **THEN** it raises ``EnvironmentError`` with a clear message
  listing the missing var

#### Scenario: PROD target requires 6 env vars

- **WHEN** the user calls ``validate_target_secrets(PROD)`` without
  setting the 6 DUCKLAKE_* + BUCKET vars
- **THEN** it raises ``EnvironmentError`` listing all 6 missing vars
  (or the subset that are missing)

### Requirement: Target selection by name

The system MUST provide a ``get_target(name)`` function that returns
the canonical `Target` for the given name. The function MUST honour
the ``OIDEACHAIS_TARGET`` env var as a CLI-side override.

#### Scenario: Default target is DEV

- **WHEN** the user calls ``get_target()`` without arguments
  AND the ``OIDEACHAIS_TARGET`` env var is not set
- **THEN** it returns the ``DEV`` instance

#### Scenario: Env var override

- **WHEN** the ``OIDEACHAIS_TARGET`` env var is set to ``"prod"``
- **THEN** ``get_target()`` returns the ``PROD`` instance

#### Scenario: Unknown target name raises

- **WHEN** the user calls ``get_target("unknown")``
- **THEN** it raises ``ValueError`` listing the valid target names

### Requirement: Pipeline creation for the named target

The system MUST provide a ``create_pipeline_for_target(target_name,
pipeline_name, dataset_name)`` function that returns a configured
``dlt.Pipeline`` instance.

#### Scenario: Dev pipeline uses local DuckDB

- **WHEN** the user calls ``create_pipeline_for_target("dev", "my_pipe",
  "my_dataset")``
- **THEN** the returned pipeline has ``destination="duckdb"``
- **AND** ``dataset_name == "author_archive_dev_my_dataset"``

#### Scenario: Prod pipeline uses DuckLake

- **WHEN** the user calls ``create_pipeline_for_target("prod", "my_pipe",
  "my_dataset")``
- **THEN** the returned pipeline has ``destination="ducklake"``
- **AND** ``dataset_name == "author_archive_my_dataset"``
- **AND** the function raises ``EnvironmentError`` if any of the
  6 required DUCKLAKE_* + BUCKET vars are missing

### Requirement: make_target.sh CLI helper

The system MUST provide a CLI helper at
``sruth/oideachais/scripts/make_target.sh`` that:

  1. Accepts the target name as ``$1`` (default ``"dev"``)
  2. Sources the ``.env`` file from the repo root
  3. Exports ``OIDEACHAIS_TARGET``
  4. Runs the pre-flight secret check (calls the same
     ``validate_target_secrets`` as the Python factory)
  5. Execs the user-supplied command with the target env set

#### Scenario: Default to dev with no command

- **WHEN** the user runs ``./sruth/oideachais/scripts/make_target.sh`` with
  no arguments
- **THEN** the helper prints the resolved target (DEV) and exits
  with status 0
- **AND** no DLT pipeline is started

#### Scenario: Run a Python command with the prod target

- **WHEN** the user runs
  ``./sruth/oideachais/scripts/make_target.sh prod python -c "print('hi')"``
- **THEN** the helper exports ``OIDEACHAIS_TARGET=prod``
- **AND** the helper sources the ``.env`` file
- **AND** the helper execs the python command with the env set
- **AND** the python command can read ``os.environ["OIDEACHAIS_TARGET"]``
  and get ``"prod"``

