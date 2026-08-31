# cianfhoghlaim-british-isles-tertiary-factory Specification

## Purpose

Generalises `UniversityDeepExtractionConfig` to the full British
Isles tertiary universe (Republic of Ireland, Northern Ireland,
England, Wales, Scotland, IoM, Cornwall, Channel Islands).

Each constituent is addressable through a single
`BITertiaryDeepExtractionConfig`. The factory emits a 6-resource
DLT source (extends the existing 5 resources with `sso_required`)
plus a sister CocoIndex `bitertiary_universities_app_factory()`.

## ADDED Requirements

### Requirement: `BITertiaryDeepExtractionConfig` schema

The system SHALL provide `BITertiaryDeepExtractionConfig` at
`dlt_sources/british_isles/university/british_isles_tertiary_factory.py`:

```python
class BITertiaryDeepExtractionConfig(BaseModel):
    university_id: str                       # kebab-case
    institution_name: str
    base_url: HttpUrl
    nation: str = Field(pattern=r"^(ie|ni|gb-wls|gb-eng|gb-sct|iom|jkc|cor)$")
    catalogue_paths: list[str] = []
    school_subdomain_paths: list[str] = []
    official_docs_paths: list[str] = []
    exam_papers_paths: list[str] = []
    handbook_root_path: str = "/handbooks/"
    academic_year: int = 2025
    programme_code_regex: str = r"[A-Z]{2,4}\d{3,4}"
    ects_field_label: str = "ECTS"
    sso_required: bool = False                # new in this change
    sso_secret_keys: dict[str, str] = {}     # {"SSO_LOGIN": "UNIVERSITY_SSO_USERNAME", ...}
    prefer_free_browser: bool = True
```

#### Scenario: A new British Isles university is added in 6 lines of `sources.yaml`

- **GIVEN** a developer appends to `pyproject.toml :: [tool.dlt.sources.bitertiary_universities]`:
  ```toml
  [[tool.dlt.sources.bitertiary_universities.entries]]
  university_id = "ie-university-maynooth"
  institution_name = "Maynooth University"
  base_url = "https://www.maynoothuniversity.ie"
  nation = "ie"
  catalogue_paths = ["/study/**"]
  ```
- **WHEN** the source factory is loaded
- **THEN** the new `bitertiary_universities_factory()` is registered
- **AND** the developer did NOT need to write any new Python code

### Requirement: 6-resource DLT factory

The factory SHALL emit 6 `@dlt.resource` rows for any
`BITertiaryDeepExtractionConfig`:
- `course_pages` (re-used from existing factory)
- `module_pages` (re-used from existing factory)
- `programme_pages` (re-used from existing factory)
- `handbook_pdfs` (re-used from existing factory)
- `official_documents` (NEW in this change — the
  `official_docs_paths` list)
- `exam_papers` (NEW — the `exam_papers_paths` list;
  requires `sso_required=True`)

#### Scenario: A university WITHOUT SSO gets 5 resources, not 6

- **GIVEN** `sso_required=False`
- **WHEN** `bitertiary_universities_factory(config)` returns
- **THEN** the factory emits 5 resources (no `exam_papers`)

#### Scenario: QUB gets 6 resources with SSO

- **GIVEN** `university_id="ni-qub"`, `sso_required=True`, AND
  `INFISICAL_TOKEN=…`
- **WHEN** the factory returns
- **THEN** the factory emits 6 resources including `exam_papers`
- **AND** the `exam_papers` resource routes through
  `UoGSsoLogin.login()` with the QUB-specific `university_id`

### Requirement: Off-by-default behaviour

The factory SHALL be **off by default** in CI. The user must
opt in by adding a `[[tool.dlt.sources.bitertiary_universities.entries]]`
block to `pyproject.toml`. No `pyproject.toml` change → 0 DLT
sources registered.

#### Scenario: CI without config block → no DLT scrape

- **GIVEN** the CI runner has no
  `[[tool.dlt.sources.bitertiary_universities.entries]]` block in
  `pyproject.toml`
- **WHEN** `dagster asset materialize --select bitertiary_*` runs
- **THEN** Dagster returns "0 assets found" (not an error)
- **AND** no `BackendRouter` HTTP traffic is generated

## Receipt of approver feedback

N/A — first proposal.
