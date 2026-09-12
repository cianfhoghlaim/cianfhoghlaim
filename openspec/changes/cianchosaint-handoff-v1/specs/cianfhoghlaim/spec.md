## ADDED Requirements

### Requirement: Canonical-1 — British-Isles Education Pipeline (BIEP) is the cianfhoghlaim flagship
The system SHALL keep the British-Isles Education Pipeline (BIEP) in cianfhoghlaim as the flagship surface for the 6 Irish Leaving Certificate priority subjects (Mathematics, Chemistry, Geography, Gaeilge, English, Computer Science) + gov.ie circulars, structured as 7 CocoIndex flows + 42 Dagster assets + 6 marimo notebooks + 4 MotherDuck Dives + 1 daily Flight.

#### Scenario: BIEP CocoIndex flows are present
- **WHEN** an agent enumerates `cocoindex_flows/british_isles/{england,guernsey,ireland,isle_of_man,jersey,northern_ireland,scotland,wales}/`
- **THEN** the system SHALL expose at least 7 v1 CocoIndex flow modules covering the 6 Irish LC subjects + gov.ie circulars
- **AND** the system SHALL NOT have moved any BIEP flow to a sister repo

#### Scenario: BIEP Dagster assets are present
- **WHEN** an agent enumerates `orchestration/defs/2_materials/{ireland_education,england_education,scotland_education,wales_education,guernsey_education,jersey_education,isle_of_man_education,northern_ireland_education,biiep_v3}/`
- **THEN** the system SHALL expose ≥42 Dagster assets (the BIEP milestone-1 milestone-3 budget)
- **AND** the system SHALL keep the BIEP `biiep_v3/m0_foundation_assets.py` as the canonical milestone-0 entrypoint

#### Scenario: BIEP marimo notebooks + MotherDuck Dives + daily Flight are present
- **WHEN** an agent enumerates `notebooks/10_biep_pipeline_lakehouse_*.py`
- **THEN** the system SHALL expose ≥6 marimo notebooks for the BIEP operators
- **AND** the system SHALL keep `motherduck/dives/{ciancheiltis_en_*_dive, ...}` for BIEP coverage dashboards
- **AND** the system SHALL keep `motherduck/flights/british_isles_daily_sync_flight.py` for the daily BIEP sync

### Requirement: Canonical-2 — CIANCHEILTIS Celtic bilingual umbrella is a cianfhoghlaim-owned surface
The system SHALL keep the CIANCHEILTIS umbrella marker (`ciancheiltis/` directory + `openspec/specs/ciancheiltis/spec.md`) in cianfhoghlaim as the platform-hub reference for the 5 Celtic bilingual pairs (en-cy, en-ga-ROI, en-ga-NI, en-gd, en-gv) + the EU-level en-ga dimension, per the `2026-09-06-ciancheiltis-v1` change. The system SHALL also keep the carved-out `~/dev/ciancheiltis/` sister as the runtime surface for pure Irish + non-educational Celtic pipelines.

#### Scenario: Ciancheiltis CocoIndex flows are present in cianfhoghlaim
- **WHEN** an agent enumerates `cocoindex_flows/british_isles/uk/ciancheiltis_*.py`
- **THEN** the system SHALL expose exactly 6 v1 CocoIndex flows (ciancheiltis_en_cy_embedding, ciancheiltis_en_ga_roi_embedding, ciancheiltis_en_ga_ni_embedding, ciancheiltis_en_gd_embedding, ciancheiltis_en_gv_embedding, ciancheiltis_en_ga_eu_embedding)
- **AND** the system SHALL keep the 6 ciancheiltis marimo notebooks under `notebooks/ciancheiltis_*.py`

#### Scenario: Ciancheiltis MotherDuck Dives + Flights are present
- **WHEN** an agent enumerates `motherduck/dives/ciancheiltis_*_dive.py`
- **THEN** the system SHALL expose 6 Dives (one per Celtic pair + EU)
- **AND** the system SHALL expose 6 daily Flights under `motherduck/flights/ciancheiltis_*_flight.py`
- **AND** the system SHALL NOT have moved any ciancheiltis Dive/Flight to a sister repo

#### Scenario: Ciancheiltis sister at ~/dev/ciancheiltis/ is deliberately lean
- **WHEN** an agent enumerates `~/dev/ciancheiltis/{baml_src,cocoindex_flows,orchestration,web,notebooks,bonneagar,motherduck}/`
- **THEN** the system SHALL return `No such file or directory` for all 7 directories (verifies the ciancheiltis sister is intentionally lean — runtime only, no platform patterns)

### Requirement: Canonical-3 — Tuatha BI Educational MMO + 8 NCCA subject agents is the cianfhoghlaim agent fleet
The system SHALL keep the BI Educational MMO + 8 NCCA subject agents in cianfhoghlaim under `agents/tuatha/` (NOT under the standalone `~/dev/tuatha/` sister which is a phase-1 experiment), structured as 8 subject agents (math_agent, chem_agent, geog_agent, engl_agent, gael_agent, hist_agent, appm_agent, comp_agent) + subject_router + orchestrator + cross_subject_agent + cianfhoghlaim_operator + 14 `tools/{sub}_*.py` per the `2026-08-25-tuatha-british-isles-mmo-consolidation-v1` change.

#### Scenario: 8 NCCA subject agents are present in cianfhoghlaim
- **WHEN** an agent enumerates `agents/tuatha/{math_agent,chem_agent,geog_agent,engl_agent,gael_agent,hist_agent,appm_agent,comp_agent,subject_router}.py`
- **THEN** the system SHALL expose all 8 subject agents + the subject_router
- **AND** the system SHALL expose `agents/tuatha/agents/{orchestrator,cross_subject_agent,cianfhoghlaim_operator}.py`

#### Scenario: Tuatha is integrated with the per-subject BAML contracts
- **WHEN** an agent enumerates `agents/tuatha/tools/{sub}_*.py`
- **THEN** the system SHALL expose ≥14 tools files (one BAML contract × the 8 subjects × {syllabus_lookup, past_paper_lookup, marking_scheme_lookup, formative_item_generate, response_score} minus the un-implemented ones)
- **AND** the system SHALL keep `agents/tuatha/subject_router.py` as the canonical NCCA-subject dispatch

#### Scenario: The standalone ~/dev/tuatha/ sister is NOT canonical
- **WHEN** an agent lists `~/dev/tuatha/` last commit
- **THEN** the system SHALL record the standalone repo's MIT-licence + 27-commit history
- **AND** the system SHALL NOT promote the standalone `~/dev/tuatha/tuatha/` Python package to canonical (the in-platform `agents/tuatha/` is canonical per `cianfhoghlaim-educational-mmo` spec)

### Requirement: Canonical-4 — Bonneagar IaC subdirectory is the cianfhoghlaim infrastructure fleet
The system SHALL keep the Bonneagar IaC subdirectory in cianfhoghlaim under `bonneagar/` (95 Docker Compose stacks + Komodo resource-syncs + Pangolin private-resources + Infisical clients + Dagger pipelines + deploy-runbooks) per the `2026-06-29-bonneagar-iac-merge-komodo-pangolin-infisical` archived change + the v7 flatten. The standalone `~/repos/bonneagar/` (with `.git_disabled`) is **NOT canonical** and SHALL be superseded.

#### Scenario: Bonneagar stacks directory carries the canonical 95 stacks
- **WHEN** an agent lists `bonneagar/stacks/`
- **THEN** the system SHALL expose ≥95 Docker Compose stack directories (each carrying the 6-file GOLD_STANDARD pattern: `compose.yaml` + `sidecar.yaml` + `secrets.env` + `pangolin.yaml` + `blueprint.yaml` + `.env.example`)
- **AND** the system SHALL expose `bonneagar/{iac,komodo,pangolin,blueprints,dagger,deploy-runbooks,locket-shim}/` as the IaC sub-surfaces

#### Scenario: The standalone ~/repos/bonneagar/ is disabled
- **WHEN** an agent inspects `~/repos/bonneagar/.git_disabled`
- **THEN** the system SHALL record the existence of the disabled standalone carveout
- **AND** the system SHALL NOT activate the standalone carveout (it is superseded by the in-tree `bonneagar/` subdirectory)