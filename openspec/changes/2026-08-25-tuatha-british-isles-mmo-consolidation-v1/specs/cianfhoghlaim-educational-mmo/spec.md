# Spec Delta: cianfhoghlaim-educational-mmo (the canonical surface that the new tuatha implements)

## Purpose

`cianfhoghlaim-educational-mmo` is the canonical capability for
the British Isles Formative Assessment MMO. The new `tuatha/`
sub-project (per the
`2026-08-25-tuatha-british-isles-mmo-consolidation-v1` change)
implements this spec.

This delta adds a new requirement to the canonical spec that
documents the new `tuatha/` project as the canonical
implementation surface.

## ADDED Requirements

### Requirement: The new `tuatha/` project is the canonical implementation surface

The system SHALL provide the British Isles Formative Assessment
MMO implementation at the new top-level
`/Users/cianmacandeisigh/dev/kings_college_galway/tuatha/`
sub-project (soon to be the independent GitHub repo at
`github.com/cianmacandeisigh/tuatha.git`).

The 8 NCCA Leaving Certificate subjects (mathematics,
applied_mathematics, chemistry, geography, history, english,
gaeilge, computer_science) SHALL be implemented in the new
`tuatha/subjects/` directory as ADK agents (one per subject)
with the 5 per-subject tools (syllabus_lookup +
past_paper_lookup + marking_scheme_lookup +
formative_item_generate + response_score) in the new
`tuatha/tools/` directory.

The 3 educational agents (academic_history_agent +
celtic_grammar_agent + celtic_morphology_agent) SHALL be
implemented in the new `tuatha/agents/educational/` directory.

The 4 BIEP hackathon features (marking_grader +
adaptive_tutor + equivalency_generator + curriculum_change_sensor)
SHALL be implemented in the new `tuatha/agents/hackathon/`
directory.

The 1 media_intel pipeline (the 10-tool agent) SHALL be
implemented in the new `tuatha/agents/media_intel/` directory.

#### Scenario: A user queries the 8 NCCA subject agents via the new `tuatha/` project

- **GIVEN** the new `tuatha/` project is built + pushed to
  `github.com/cianmacandeisigh/tuatha.git`
- **AND** the parent's `agents/agent_registry.py:AGENT_REGISTRY`
  has been re-routed to point at the new
  `tuatha.agents.media_intel.media_descriptor_agent` module path
  (per the consolidation change)
- **WHEN** the user invokes the new `tuatha/` CLI tool with
  `tuatha ask --subject mathematics --topic "complex numbers"`
- **THEN** the new `tuatha/subjects/mathematics.py` ADK agent
  is dispatched
- **AND** the agent calls the new
  `tuatha/tools/mathematics_syllabus_lookup` tool
- **AND** returns the BAML-extracted syllabus topic with the
  citation linking back to the canonical NCCA Mathematics
  syllabus PDF
- **AND** the response is logged to Langfuse + the
  `oideachais_lc_mathematics` Cognee dataset

#### Scenario: The 5 parent pending changes archive

- **WHEN** the 5 parent pending changes
  (`2026-09-01-celtic-mythology-content-system-v1` +
  `2026-09-08-ogham-celtic-stones-pipeline-v1` +
  `2026-09-22-geospatial-british-isles-twin-v1` +
  `2026-09-29-familiar-dynamic-nft-system-v1` +
  `2026-10-06-spacetimedb-babylonjs-adr-clean-break-v1`) all
  archive
- **THEN** the parent's `openspec/specs/tuatha-platform/`
  spec is deprecated (per the `tuatha-platform` delta in this
  change)
- **AND** the parent's `agents/agent_registry.py:AGENT_REGISTRY`
  re-route is active
- **AND** the new `tuatha/` project's `pyproject.toml` +
  `mise.toml` + the 5 meta docs are committed + pushed

#### Scenario: The `tuatha-platform` spec's 1-release back-compat window closes

- **WHEN** the operator runs `openspec archive
  2026-08-25-tuatha-british-isles-mmo-consolidation-v1 --yes` +
  the 5 parent changes archive
- **THEN** the operator runs `openspec archive tuatha-platform
  --yes` (a subsequent change)
- **AND** the spec moves to
  `openspec/specs/_archive/tuatha-platform/`
- **AND** the back-compat alias is removed
- **AND** the parent's `agents/agent_registry.py` no longer
  carries the `media_descriptor_agent` entry's back-compat
  re-export (the new `tuatha.agents.media_intel` location is
  canonical)
