# Educational Geography Curriculum Capability

## Purpose

`educational-geography-curriculum` is the canonical spec for the
8-jurisdiction geography curriculum (NCEA + SQA + WJEC + CCEA +
JCQ + IoM + Jersey + Guernsey). It pairs with
`geospatial-british-isles-twin` and emits BAML extractions for
every geography syllabus outcome.

This capability is referenced by:
- `openspec/changes/2026-09-22-geospatial-british-isles-twin-v1`

## Requirements

### Requirement: 8-jurisdiction coverage

The capability SHALL cover all 8 jurisdictions' geography curricula,
emitting structured `LearningOutcome` rows with bilingual invariant
+ difficulty 1-5 + evidence PDF citations.

### Requirement: Cross-jurisdiction bridges

The capability SHALL emit `query_cross_jurisdiction_bridges` rows
that link equivalent LOs across jurisdictions (e.g. NCEA LC
geography LO 1.1 ↔ SQA Higher geography LO 1.1).

### Requirement: Seasonal Celtic festival overlay

The capability SHALL emit rows for the 4 seasonal Celtic festivals
(Imbolc, Bealtaine, Lúnasa, Samhain) and bind each to a curriculum
LO + a geospatial location.
