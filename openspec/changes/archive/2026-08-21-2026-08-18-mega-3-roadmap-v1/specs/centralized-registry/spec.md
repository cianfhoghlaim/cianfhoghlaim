## ADDED Requirements

### Requirement: Mega-3 4-stage plane architecture

The system SHALL provide a unified 4-stage plane architecture across
the 5 canonical packages (BAML + CocoIndex + Google ADK + CopilotKit +
Marimo) covering the 4 British Isles education stages: Leaving Cycle
(Ireland LC), Junior Cycle (Ireland JC, ages 12-15), A-Level
(England GCE Advanced Level), GCSE (England General Certificate of
Secondary Education).

For each of the 4 stages, the system SHALL provide exactly 1 BAML
template file (parameterised by subject) that drives 1 CocoIndex
factory + 1 Marimo dashboard + 1 ADK agent, ensuring the same
extraction surface across the 5 packages.

#### Scenario: Each stage has a BAML template + CocoIndex factory + Marimo dashboard + ADK agent

- **GIVEN** the 4 stages are Leaving Cycle (14 subjects), Junior Cycle
  (8 subjects), A-Level (15 subjects), GCSE (9 subjects)
- **WHEN** the operator runs `ccc:search "stage_template"` or
  `firecrawl_search "BIEP stage template"`
- **THEN** the system returns 4 template files:
  - `baml_src/british_isles/_shared/lc_extraction_template.baml`
  - `baml_src/british_isles/_shared/junior_cycle_template.baml`
  - `baml_src/british_isles/_shared/alevel_extraction_template.baml`
  - `baml_src/british_isles/_shared/gcse_extraction_template.baml`
- **AND** 4 CocoIndex factory files (one per stage)
- **AND** 4 Marimo dashboard files (one per stage)
- **AND** 4 ADK agent files (one per stage, auto-generated from the BAML templates)

#### Scenario: The 5-step Mega-3 rollout sequence is documented

- **GIVEN** the Mega-3 roadmap at `openspec/changes/2026-08-18-mega-3-roadmap-v1/proposal.md`
- **WHEN** the operator reads the proposal
- **THEN** the system SHALL document the 5-step rollout:
  1. `2026-08-18-mega-3-roadmap-v1` (narrative)
  2. `2026-08-18-mega-3-fast-follow-v1` (5 helpers + 12 crown jewels + 6 dedup wins, -8,833 LOC net)
  3. `2026-08-26-mega-3a-baml-and-adk-v1` (BAML + ADK + 4 stage templates + 8 NCCA JC, -9,700 LOC net)
  4. `2026-09-30-mega-3b-cocoindex-and-copilotkit-v1` (CocoIndex + CopilotKit + 4 stage factories + european_nations, -1,200 LOC net)
  5. `2026-11-25-mega-3c-marimo-and-integration-v1` (Marimo + Integration + 4 stage dashboards, -6,066 LOC net)
- **AND** the total net code reduction target is -25,799 LOC while
  adding 558 BAML functions + 12 ADK agents + 47 CocoIndex Apps + 2
  web apps + 8 NCCA Junior Cycle subjects + 60+ integration
  sub-tasks + 90 ADDED spec requirements across 17 specs