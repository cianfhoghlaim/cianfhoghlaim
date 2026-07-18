## MODIFIED Requirements

### Requirement: BIEP v3 preflight bug fixes (P0)

The system SHALL have:

1. Valid YAML in `motherduck/flights/config.yaml` (4 BIEP v3 flights
   indented under `flights:` key).
2. `BIEPV3ExtractStrong` BAML client uses a non-VLM text model
   (`gemma-3-27b-it`) per the user's audit decision.
3. `dlt/common/motherduck_snapshots.py` makes real HTTPS POST requests
   to `api.motherduck.com` for snapshot/share/attach (NOT stub dict
   factories).
4. `seed_registry()` asserts 3,780 rows (matches actual loader output).
5. All 4 BIEP v3 jurisdiction pipelines inherit from
   `JurisdictionPipelineBase` (eliminating ~120 LOC of duplicated
   boilerplate).

#### Scenario: MotherDuck flight YAML loads correctly

- **WHEN** `python -c "import yaml; yaml.safe_load(open('motherduck/flights/config.yaml'))"` runs
- **THEN** the call succeeds without a `yaml.YAMLError`
- **AND** the `flights` key contains exactly 13 entries (9 daily-sync + 4 BIEP v3)

#### Scenario: All 4 BIEP v3 flights discoverable

- **WHEN** `dg list jobs | grep -E "(ireland|england|sct_wls_ni|crown_dependencies)_full_coverage_flight"` runs
- **THEN** exactly 4 BIEP v3 flight names are listed

#### Scenario: BIEPV3ExtractStrong uses non-VLM text model

- **WHEN** `baml_src/clients_biep_v3.py` is inspected
- **THEN** `BIEPV3ExtractStrong` SHALL equal `"gemma-3-27b-it"` (not a VLM model)

#### Scenario: snapshot_database makes a real POST

- **WHEN** `snapshot_database("snap_2026_08_10", "oideachais")` is called
- **THEN** a real HTTPS POST to `https://api.motherduck.com/v1/databases/oideachais/snapshots` is made
- **AND** the response is returned as a dict
- **AND** the call uses `MOTHERDUCK_TOKEN` from the env for auth

#### Scenario: create_share makes a real POST

- **WHEN** `create_share("share_biep_v3", "oideachais")` is called
- **THEN** a real HTTPS POST to `https://api.motherduck.com/v1/shares` is made
- **AND** the response includes a `share_url` field

#### Scenario: attach_share makes a real POST

- **WHEN** `attach_share(share_url, "biiep_v3_share")` is called
- **THEN** a real HTTPS POST to `https://api.motherduck.com/v1/shares/attach` is made
- **AND** the call succeeds with HTTP 200 or 201

#### Scenario: seed_registry asserts 3,780 rows

- **WHEN** `seed_registry()` is called
- **THEN** the function returns a counts dict with a total of 3,780 rows
- **AND** an `AssertionError` is raised if the row count drifts

#### Scenario: Per-jurisdiction breakdown

- **WHEN** `seed_registry()` is called
- **THEN** the returned counts dict MUST include:
  - ireland: 544
  - england: 276
  - scotland: 600
  - wales: 640
  - northern_ireland: 280
  - jersey: 480
  - guernsey: 480
  - isle_of_man: 480

#### Scenario: All 4 pipelines inherit from JurisdictionPipelineBase

- **WHEN** any of the 4 BIEP v3 jurisdiction pipelines is loaded
- **THEN** the pipeline class MUST be a subclass of `JurisdictionPipelineBase`
- **AND** `isinstance(pipeline_obj, JurisdictionPipelineBase)` returns `True`

#### Scenario: Boilerplate eliminated

- **WHEN** comparing pre-refactor vs post-refactor
- **THEN** the 4 pipeline files SHALL contain ~30 LOC less boilerplate each
- **AND** the shared `subject_to_row()` and `build_pipeline()` methods MUST be on the base class