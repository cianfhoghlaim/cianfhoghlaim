# Spec Delta — oideachais-leabharlann

This delta documents the openspec drift cleanup in the `oideachais-leabharlann` capability. No spec-text edits were made (the only `sruth.*` refs in this spec are historical "formerly" refs which were preserved verbatim). One new requirement codifies the v4 namespace convention.

## ADDED Requirements

### Requirement: Openspec spec text uses v4 namespace convention (no `sruth.X` drift)

The `oideachais-leabharlann` capability spec SHALL use the v4 namespace convention throughout. Concretely:

1. **Canonical Python import paths** in scenarios SHALL use the v4 form: `from cianfhoghlaim.<module> import <symbol>` (e.g. `from cianfhoghlaim.pipelines.ingest.leabharlann.books import books_source`) or the quadrant-namespace shorthand `from oideachais.<module> import <symbol>` (e.g. `from oideachais.pipelines.ingest.leabharlann.books import books_source`).
2. **Historical refs** (e.g. "formerly `sruth.oideachais.dlt_sources.leabharlann.*`") SHALL be preserved verbatim — they document the v3 → v4 transition.
3. **Bare `oideachais.X` refs** for CLI invocations (e.g. `oideachais.cocoindex_flows.leabharlann_embedding`) are the legitimate post-v4 namespace and SHALL be preserved.

#### Scenario: A spec contributor edits the oideachais-leabharlann spec

- **GIVEN** a contributor wants to add a new scenario to the oideachais-leabharlann spec at `openspec/specs/oideachais-leabharlann/spec.md`
- **WHEN** the contributor writes a Python import statement in the scenario
- **THEN** the import SHALL use the v4 form: `from oideachais.pipelines.ingest.leabharlann.<source> import <symbol>` (the canonical post-v4 path)
- **AND** if the contributor wants to document the v3 → v4 transition, they SHOULD use the parenthetical "(formerly `sruth.oideachais.dlt_sources.leabharlann.*`)" form
- **AND** the contributor SHALL NOT use bare `from sruth.oideachais.X import Y` (the v3 namespace)

#### Scenario: The historical "formerly" refs are preserved

- **GIVEN** the existing spec lines 365-366 document the v3 → v4 rename:
  > "the dlt source module is `cianfhoghlaim.pipelines.ingest.leabharlann.{books,...}` (formerly `sruth.oideachais.dlt_sources.leabharlann.*`)"
  > "the CocoIndex embedding flow is `cianfhoghlaim.embeddings.leabharlann` (formerly `sruth.oideachais.cocoindex_flows.leabharlann_embedding`)"
- **WHEN** the openspec drift cleanup audit runs
- **THEN** these historical refs are preserved verbatim
- **AND** `grep -rn "sruth\.oideachais\.dlt_sources\.leabharlann" openspec/specs/oideachais-leabharlann/spec.md` returns 1 match (the "formerly" reference, not an active import path)

#### Scenario: The openspec drift cleanup baseline is preserved

- **GIVEN** the `2026-07-13-openspec-drift-cleanup-v1` change has landed
- **WHEN** `grep -rn "sruth\.[a-z]" openspec/specs/oideachais-leabharlann/spec.md` runs
- **THEN** the count of `sruth.*` refs is 0 (all `sruth.*` refs in this spec were historical "formerly" refs that the audit preserved)
- **AND** `openspec validate oideachais-leabharlann --strict` returns valid (the spec was already valid before this drift cleanup)