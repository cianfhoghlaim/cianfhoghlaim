# `oideachais-pipeline` MODIFIED — declare 972-LOC ie→ireland duplicate cleanup + acknowledge Wave 1 cleanup

## REMOVED Requirements

### Requirement: Legacy `dlt/british_isles/ie/` namespace

**Reason**: The `dlt/british_isles/ie/` namespace
(the deprecated `ie`-coded sub-tree under
`dlt/british_isles/ie/education/`, `ie/law/`, `ie/medicine/`)
was created during the pre-Wave-1 (pre-`f554711a6`) dlt layout and is now
fully retired.

Wave 1 commit `f554711a6` (2026-07-10, the
`2026-07-10-cleanup-ie-to-ireland-namespace-v1` change) migrated all 17
imports from `dlt_sources.ie.*` to `dlt_sources.ireland.*`, removed the
`dlt/british_isles/ie/` directory entirely, and rewrote the spec
references. The directory has not existed on disk since that commit landed.

The current canonical layout is
`dlt/british_isles/{england,guernsey,ireland,isle_of_man,jersey,northern_ireland,scotland,wales}/`,
where the *nation code* (e.g. `ie`, `england`, `sct`) is the first
path segment.

**Migration**: Any importer that still references
`dlt/british_isles/ie/...` MUST be rewritten to
`dlt/british_isles/ireland/...` (the Wave 1 commit handled 17 such
imports; any residual references are bugs). The canonical Python package
is `cianfhoghlaim.dlt.british_isles.ireland.{education,law,medicine,...}`,
matching the spec's "single `oideachais` DB with per-domain schemas"
Requirement.

## ADDED Requirements

### Requirement: No legacy 972-LOC ie-namespace duplicate pairs remain in `dlt/british_isles/ireland/education/`

The `dlt/british_isles/ireland/education/` package SHALL NOT
contain byte-identical or near-identical duplicate files. Specifically
the legacy duplicate pair:

- `curriculum_source.py` (972 LOC, byte-identical to `curriculum.py` per
  MD5 `c098f82f94909f9ffccee0387b600d9f`) — DELETED
- `exam_source_update.py` (0-byte stub) — DELETED

…is removed entirely, and the 11 importers that referenced the deleted
files are rewritten to point at `curriculum.py` (the kept surface).

#### Scenario: Filesystem directory contains no legacy duplicates

- **WHEN** a developer runs `ls dlt/british_isles/ireland/education/`
- **THEN** zero entries SHALL match `*curriculum_source*`
- **AND** zero entries SHALL match `*exam_source_update*`
- **AND** the directory listing SHALL contain exactly one `curriculum.py`
      (the canonical 972-LOC surface)

#### Scenario: Import graph is consolidated against `curriculum.py`

- **GIVEN** `curriculum.py` defines `_crawl_source` at line 57 +
      `crawl_source()` + `parallel_scrape_subject()` + `_classify_pdf()` +
      `crawl_cycle()` + `crawl_subject()` + `build_subject_urls()` and the
      `curriculum_source` `@dlt.source` function at line 600
- **WHEN** a developer runs `grep -rn "from cianfhoghlaim.dlt.british_isles.ireland.education.curriculum_source\|from cianfhoghlaim.dlt.british_isles.ireland.education.exam_source_update" cianfhoghlaim/`
- **THEN** zero matches SHALL appear (excluding the historical openspec
      archive under `openspec/changes/archive/*`)

#### Scenario: The 11 importers work against `curriculum.py`

- **WHEN** any of the 11 importers imports `_crawl_source`
- **THEN** `from cianfhoghlaim.dlt.british_isles.ireland.education.curriculum import _crawl_source`
      SHALL succeed (the kept surface defines the symbol)
- **AND** each importer SHALL continue to expose the same domain
      behaviour as before the duplicate-file deletion (WRC pages, courts
      forms, judgements, citizens info, etc.)

## Cross-references

- [`british-isles-education-pipeline`](../british-isles-education-pipeline/spec.md) — the BIEP v1 flagship; the duplicate-removal delta in section "No duplicate DLT source files (curriculum_source.py deleted)" is the same declaration viewed from the BIEP layer
- [Wave 1 commit `f554711a6`](https://github.com/cianfhoghlaim/kings_college_galway/commit/f554711a6) — the `2026-07-10-cleanup-ie-to-ireland-namespace-v1` change that removed the `dlt/british_isles/ie/` directory
- [openspec change `2026-07-10-cleanup-ie-to-ireland-namespace-v1`](../../../changes/archive/2026-07-10-cleanup-ie-to-ireland-namespace-v1/proposal.md) — the archived spec change that the REMOVED requirement above references
