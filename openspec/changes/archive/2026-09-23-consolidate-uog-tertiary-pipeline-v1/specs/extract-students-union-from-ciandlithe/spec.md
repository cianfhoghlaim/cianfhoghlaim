# extract-students-union-from-ciandlithe Specification

## Purpose

Codify the extraction of the Students' Union ADK agent package from
the ciandlithe sister-repo to cianfhoghlaim's tertiary pipeline. The
SU package (`agents/adk/students_union/`) is UoG-specific and was
misfiled in ciandlithe per the case-study-sister design. Per the
user's reverted-split directive, the SU package moves to
`agents/meaisinfhoghlaim/educational/students_union/` and becomes
the 13th specialist in the 12-agent fleet.

The 14 affected files:
- `__init__.py` + `root_agent.py` + `config.py`
- 5 specialist agent files (`clubs_socs_agent.py` + `grants_funding_agent.py` + `class_rep_aggregator_agent.py` + `complaints_welfare_agent.py` + `elections_agent.py`)
- 5 pure-Python tools (`class_rep_themer.py` + `clubs_socs_validator.py` + `complaint_router.py` + `election_validator.py` + `grants_matcher.py`)
- `tools/__init__.py`
- 2 marimo notebooks (`students_union_adk_case_studies.py` + `students_union_kcg_integration.py`)
- 2 smoke tests (`_smoke_test.py` + `_smoke_test_cross_repo.py` — the latter is deleted as cross-repo no longer applies)

## Requirements

## ADDED Requirements

### Requirement: SU package moves wholesale

The system SHALL move all 14 files from `ciandlithe/agents/adk/students_union/`
to `cianfhoghlaim/agents/meaisinfhoghlaim/educational/students_union/`,
preserving the internal module structure (agents + tools + tests).

#### Scenario: SU package imports cleanly after the move
- **WHEN** the operator runs `python -c "from agents.meaisinfhoghlaim.educational.students_union import root_agent, students_union_app"`
- **THEN** the import succeeds without errors
- **AND** the 5 specialist agents + the root orchestrator construct cleanly

### Requirement: SU smoke test passes after the move

The system SHALL preserve the smoke test at
`tests/agents/students_union/test_smoke.py` (moved from
`ciandlithe/agents/adk/students_union/_smoke_test.py`) such that it
exits 0 with "All 5 SU case-study tools + 5 agents + root_agent +
classifier pass."

#### Scenario: SU smoke test exits 0
- **WHEN** the operator runs `python tests/agents/students_union/test_smoke.py`
- **THEN** the script exits 0
- **AND** stdout contains the expected pass message

### Requirement: ciandlithe's SU deletion lands clean

The system SHALL delete the SU package from ciandlithe via a
separate openspec change
(`openspec/changes/<YYYY-MM-DD>-remove-students-union-from-ciandlithe-v1/`)
that archives AFTER the cianfhoghlaim umbrella change.

#### Scenario: ciandlithe grep returns 0 matches for SU references
- **WHEN** the operator archives the ciandlithe removal change
- **THEN** `git grep students_union` in ciandlithe returns 0 (only in updated README/AGENTS/LICENSE pointers)
- **AND** `ls ciandlithe/agents/adk/students_union/` fails (dir removed)

### Requirement: SU root registers as 13th fleet specialist

The system SHALL update `agents/agent_registry.py` to register the
SU root orchestrator as the 13th specialist in the 12-agent fleet
(per `agent-fleet-orchestration/SKILL.md`).

#### Scenario: agent_registry.py includes the SU root
- **WHEN** the operator reads `agents/agent_registry.py`
- **THEN** the 13 specialists are: `curriculum_agent`, `translation_agent`,
  `corpus_agent`, `research_agent`, `geospatial_agent`, `statistics_agent`,
  `curriculum_comparison_agent`, `mcp_curriculum_agent`, `tuatha_root_agent`,
  `celtic_grammar_agent`, `celtic_morphology_agent`, `academic_history_agent`,
  **`students_union_root_agent`** (the new 13th)

### Requirement: SU license re-papered

The system SHALL replace the `BUSL-1.1 v2 CIANDLITHE edition` license
references in the moved SU files with `BUSL-1.1 Cianfhoghlaim edition`
references (per `LICENSE.md` at the cianfhoghlaim repo root).

#### Scenario: SU files cite the cianfhoghlaim licence
- **WHEN** the operator runs `git grep "CIANDLITHE edition" agents/meaisinfhoghlaim/educational/students_union/`
- **THEN** the command returns 0 matches
- **AND** the docstrings at the top of each SU file cite "BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md)"
