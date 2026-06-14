# Spec Delta: `croilar-stream-registry` (NEW CAPABILITY)

## ADDED Requirements

### Requirement: Stream Dataclass

The system SHALL define a `Stream` frozen dataclass in `croilar/_shared/streams.py`.

#### Scenario: Stream has the required fields

- **WHEN** a `Stream` is instantiated
- **THEN** it SHALL have `id: str`, `owner: str`, `owner_display_name: str`, `r2_prefix: str`, `duckdb_dataset: str`, `sources: tuple[StreamSource, ...]`
- **AND** the dataclass SHALL be frozen (immutable)

#### Scenario: Stream source types are enumerated

- **WHEN** a `StreamSource` is instantiated
- **THEN** its `type` SHALL be one of `GITHUB | LINKEDIN | RESEARCHGATE | SPOTIFY | SOUNDCLOUD | LABELS | CV | ARTWORK | FILESYSTEM | ZOTERO_SQL`
- **AND** the enum SHALL be a `StrEnum` (serialises cleanly to YAML / JSON)

#### Scenario: local_only gate

- **WHEN** a `StreamSource` has `local_only=True`
- **THEN** any DLT destination call for that source SHALL skip R2 writes
- **AND** the gate SHALL be checked in a single helper, not duplicated in every destination

### Requirement: Stream Registry

The system SHALL maintain a Stream registry loaded from `croilar/config/sources.yaml`.

#### Scenario: Registry is a single map

- **WHEN** the registry loads
- **THEN** the top-level `streams:` key SHALL be a `dict[str, Stream]`
- **AND** keys SHALL be `Stream.id` (not `Stream.owner`)

#### Scenario: Registry has lookup helpers

- **WHEN** the registry loads
- **THEN** `get_stream(stream_id) -> Stream` SHALL return the matching Stream or raise `KeyError`
- **AND** `list_streams() -> list[Stream]` SHALL return all streams
- **AND** both SHALL be cached with `functools.lru_cache` for the lifetime of the process

#### Scenario: Pydantic validation

- **WHEN** a malformed `sources.yaml` is loaded
- **THEN** the loader SHALL raise a `pydantic.ValidationError` with a clear path to the offending field
- **AND** the loader SHALL NOT silently drop invalid sources

### Requirement: Migration from Persona Model

The system SHALL provide a one-shot migration script that renames persona-keyed files to stream-keyed files.

#### Scenario: Migration script runs idempotently

- **WHEN** `bun run migrate:personas-to-streams` is executed
- **THEN** the script SHALL move `croilar/notebooks/aleyum/` → `croilar/notebooks/streams/music/`
- **AND** `croilar/notebooks/cianfhoghlaim/` → `croilar/notebooks/streams/teaching/`
- **AND** the script SHALL rewrite TS/Python imports for the rekeyed files
- **AND** the script SHALL emit a CSV diff of every changed path for review
- **AND** re-running the script SHALL be a no-op (idempotent)

#### Scenario: carlcashman is removed from data code

- **WHEN** the migration completes
- **THEN** `git grep -nE 'carlcashman' croilar/pipelines croilar/baml croilar/dagster_assets` SHALL return zero matches
- **AND** any `carlcashman` mention in the data layer SHALL be flagged as a follow-up issue
