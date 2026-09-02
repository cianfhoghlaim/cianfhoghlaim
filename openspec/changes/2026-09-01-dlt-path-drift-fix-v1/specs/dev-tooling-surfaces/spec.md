## ADDED Requirements

### Requirement: All Python imports MUST reference the Wave 1 DLT path

The Cianfhoghlaim dev-tooling-surfaces capability MUST enforce
that all Python imports referencing the British Isles DLT sources
use the Wave 1 NEW path:

```
dlt_sources.education.<jurisdiction>.british_isles.<rest>
```

NOT the Wave 0 OLD path:

```
dlt_sources.british_isles.<jurisdiction>.<rest>  # DEPRECATED
```

Per the 2026-09-01-dlt-path-drift-fix-v1 change (Step 1 of the
cianfhoghlaim-nua v6 era plan).

The 9 jurisdiction-specific paths are:
- `dlt_sources.education.ireland.british_isles.education.*`
- `dlt_sources.education.england.british_isles.education.*`
- `dlt_sources.education.scotland.british_isles.education.*`
- `dlt_sources.education.wales.british_isles.education.*`
- `dlt_sources.education.northern_ireland.british_isles.education.*`
- `dlt_sources.education.isle_of_man.british_isles.education.*`
- `dlt_sources.education.jersey.british_isles.education.*`
- `dlt_sources.education.guernsey.british_isles.education.*`
- `dlt_sources.education.crown_dependencies.british_isles.education.*`

Plus the university subpath (no `education.` between
`british_isles` and `university`):
- `dlt_sources.education.ireland.british_isles.university.*`
- `dlt_sources.education.england.british_isles.university.*`

#### Scenario: A new subject DLT source is added

- **WHEN** a developer adds `dlt_sources/education/scotland/british_isles/education/sqa_mathematics.py`
- **THEN** the developer SHALL import it via `dlt_sources.education.scotland.british_isles.education.sqa_mathematics`
- **AND** the developer SHALL NOT use the old path
  `dlt_sources.british_isles.scotland.education.sqa_mathematics` (it's empty)

#### Scenario: The grep guard

- **WHEN** the developer runs `grep -rln 'dlt_sources\.british_isles\.\(ireland\|england\|scotland\|wales\|northern_ireland\|isle_of_man\|jersey\|guernsey\|crown_dependencies\)\.education' --include='*.py' .`
- **THEN** the output is empty (no remaining old-path references)