## ADDED Requirements

### Requirement: Root README depth and discoverability

The root `README.md` MUST present the platform as an integrated
system, not just a topology table, and MUST make the personal
credential corpus, the family-history narrative, the leabharlann
corpus, and the per-area hub READMEs discoverable from a single
scroll.

The file MUST land between **400 and 500 lines inclusive**, and the
sections MUST appear in the order declared in the
`2026-08-19-readme-restore-depth-and-cross-link-to-leabharlaim-v1`
proposal.

#### Scenario: A first-time visitor lands on the repo

- **WHEN** a first-time visitor opens `README.md`
- **THEN** the file MUST walk them through:
  1. What the project is (the TL;DR 5-stage flow: Ingests → Extracts → Embeds → Surfaces → Hosts)
  2. Where the canonical source-of-truth artifacts live (the Centralized Registries section, with the 4 + 4 canonical artifacts named)
  3. How the monorepo is laid out (Monorepo Topology with TypeScript + Python + IaC sub-tables)
  4. The 5-stage Dagster architecture (`1_ingestion/` → `5_agent_ops/`)
  5. The British Isles Education Pipeline (BIEP) flagship description
  6. The 12-row Personal credential corpus table, each row linking to a verified PDF under `cian_mac_an_déisigh_uí_liatháin/`
  7. The 7-row leabharlann subdir summary table, each row linking to the matching `leabharlann/<dir>/` path
  8. The 1-paragraph Family history summary linking to `cian_mac_an_déisigh_uí_liatháin/FAMILY_HISTORY.md`
  9. The 3-row Repository constellation (cianfhoghlaim / bonneagar / leabharlann)
  10. The Cross-cutting concerns block (OpenSpec + Secrets + CCC/Cognee + agentic dev)
  11. The Licensing section with the full jurisdictions list

#### Scenario: Every sub-README referenced from the root must exist

- **WHEN** any link from `README.md` resolves to a sub-README (`agents/README.md`, `orchestration/README.md`, `meaisinfhoghlaim/README.md`, `bonneagar/README.md`, `cian_mac_an_déisigh_uí_liatháin/README.md`, `cian_mac_an_déisigh_uí_liatháin/FAMILY_HISTORY.md`, `leabharlann/README.md`, `LICENSE.md`, `docs/CHOP_AND_CHANGE_GUIDE.md`)
- **THEN** that target file MUST exist in the working tree at the same commit

#### Scenario: The credential corpus table in the root is consistent with the cian_mac_an_déisigh_uí_liatháin index

- **WHEN** `README.md` lists a credential as a verified PDF
- **THEN** the linked path under `cian_mac_an_déisigh_uí_liatháin/` MUST exist in the working tree at the same commit
- **AND** the credential entry MUST appear in BOTH the root `README.md` table AND the `cian_mac_an_déisigh_uí_liatháin/README.md` index
- **AND** the two tables MUST list the same set of credentials (single source of truth)

#### Scenario: The leabharlann subdir list matches the filesystem

- **WHEN** `README.md` lists a leabharlann subdirectory in the per-subdir table
- **THEN** that subdirectory MUST exist under `leabharlann/` in the current commit
- **AND** every top-level directory under `leabharlann/` MUST appear in the table (no omissions, no additions)

#### Scenario: The family-history section links to the deep narrative

- **WHEN** `README.md` references the family history
- **THEN** the file MUST include a 1-paragraph summary of the Triple Crown synthesis (the Deacy / Lyons / Morris / Conroy kindreds)
- **AND** the section MUST contain a link to `cian_mac_an_déisigh_uí_liatháin/FAMILY_HISTORY.md` for the full discursive narrative
- **AND** the section MUST NOT inline more than 30 lines of the family-history narrative (the long form stays in `FAMILY_HISTORY.md`)
