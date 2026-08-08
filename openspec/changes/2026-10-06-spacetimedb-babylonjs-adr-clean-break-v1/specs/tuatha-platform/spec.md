## ADDED Requirements

### Requirement: Pent-Elemental Cosmology Content Mapping

The system SHALL provide the canonical mapping from the 25 deities in the
Pent-Elemental Cosmology (5 elements × 5 nations) to the 8 NCCA subject
specialists.

#### Scenario: Deity-to-subject mapping exists
- **WHEN** the user invokes `pent_elemental_mapping.lookup_subject("Brigid")`
- **THEN** the function returns the relevant subject list

### Requirement: Babylon.js Client Retired

The system SHALL NOT use Babylon.js in any active web app.

#### Scenario: Babylon.js not used in tuatha-ui
- **WHEN** the user runs `grep -r "@babylonjs" web/apps/tuatha-ui/`
- **THEN** the command SHALL return 0 results

#### Scenario: babylonjs skill marked DEPRECATED
- **WHEN** the user reads `.agents/skills/babylonjs/SKILL.md`
- **THEN** the file SHALL contain a DEPRECATED notice in the first 30 lines

### Requirement: SpacetimeDB Backend Rejected

The system SHALL NOT use SpacetimeDB in any active code path. The
orphaned Rust crate scaffolding SHALL be archived.

#### Scenario: SpacetimeDB crates archived
- **WHEN** the user runs `ls agents/api/_rust_crates/`
- **THEN** the directory SHALL NOT contain `stdb-modules/` or `solana/`

#### Scenario: Archived crates in IaC archive
- **WHEN** the user runs `ls bonneagar/iac/_archive/rust-crates-2026-10/`
- **THEN** the directory SHALL contain `stdb-modules/` and `solana/`

### Requirement: 8 NCCA Subject Specialists Wired Through AGENT_REGISTRY

The system SHALL have the 8 NCCA subject specialists registered in
`agents/agent_registry.py:AGENT_REGISTRY`.

#### Scenario: NCCA subjects in registry
- **WHEN** the user runs `python -c "from cianfhoghlaim.agents import AGENT_REGISTRY; print(len(AGENT_REGISTRY))"`
- **THEN** the script SHALL print `≥20`