## ADDED Requirements

### Requirement: No legacy ie-namespace duplicate pairs remain

The `dlt/british_isles/ireland/education/` package SHALL NOT contain
byte-identical or near-identical duplicate files. Specifically the
legacy duplicate pair:

- `curriculum_source.py` (972 LOC, byte-identical to `curriculum.py`
  per MD5 `c098f82f94909f9ffccee0387b600d9f`) — DELETED
- `exam_source_update.py` (0-byte stub) — DELETED

…is removed entirely, and the 11 importers that referenced the
deleted files are rewritten to point at `curriculum.py` (the kept
surface).

#### Scenario: Filesystem directory contains no legacy duplicates

- **WHEN** a developer runs `ls dlt/british_isles/ireland/education/`
- **THEN** zero entries SHALL match `*curriculum_source*`
- **AND** zero entries SHALL match `*exam_source_update*`
- **AND** the directory listing SHALL contain exactly one
      `curriculum.py` (the canonical 972-LOC surface)

### Requirement: Cross-references section must enumerate the regional pipelines

The `cianfhoghlaim-pipeline` spec's `## Cross-references` section
SHALL list each regional pipeline capability it interoperates with,
specifically: `british-isles-education-pipeline`,
`european-nations-ukraine-pipeline`,
`european-union-official-language-pipeline`,
`americas-california-pipeline`, `commonwealth-pipeline`, and
`celtic-language-pipeline`. Adding a new regional pipeline requires
adding it to this list within the same change.

#### Scenario: A new regional pipeline obeys the cross-reference contract
- **WHEN** a developer adds a new regional pipeline capability spec
- **THEN** the spec's Cross-references section SHALL include the new
      pipeline
- **AND** `cianfhoghlaim-pipeline`'s Cross-references section SHALL
      be updated in the same change