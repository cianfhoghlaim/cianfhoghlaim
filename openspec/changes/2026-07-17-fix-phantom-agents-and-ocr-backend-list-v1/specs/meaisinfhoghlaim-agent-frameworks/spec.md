# Spec Delta — meaisinfhoghlaim-agent-frameworks

This delta adds one new requirement to the existing
`meaisinfhoghlaim-agent-frameworks` capability. Existing requirements are
preserved unchanged.

## ADDED Requirements

### Requirement: 8 per-subject ADK specialists resolve to `agents/tuatha/<slug>_agent.py` and dispatch via `select_optimal_for_m4_max`

The system SHALL wire the 8 NCCA subject specialists in the ADK root
agent (`cianfhoghlaim/agents/adk/root_agent.py`) to the canonical
per-subject modules at `cianfhoghlaim/agents/tuatha/<slug>_agent.py`,
where `<slug>` is one of
`math`, `appm`, `chem`, `geog`, `hist`, `engl`, `gael`, `comp`.

The canonical module paths SHALL be exposed as
`cianfhoghlaim.agents.tuatha.<slug>_agent` (Python module imports)
— NOT the legacy phantom path
`cianfhoghlaim.agents.meaisinfhoghlaim.educational.<slug>_agent`,
which does not exist on disk.

The canonical M4-Max dispatch helper SHALL be
`select_optimal_for_m4_max()` from
`cianfhoghlaim.meaisinfhoghlaim.ocr.models.registry`. The legacy
name `get_default_for_m4_max()` is preserved as a deprecated
back-compat alias that emits `DeprecationWarning` and delegates to
`select_optimal_for_m4_max()`.

#### Scenario: root_agent dispatches a Mathematics query to the tuatha math_agent

- **GIVEN** the ADK `RootAgent` is constructed
- **AND** `RootAgent._get_agent(AgentDomain.MATH)` is called
- **WHEN** the per-subject wrapper's `_ensure_loaded()` runs
- **THEN** it imports `cianfhoghlaim.agents.tuatha.math_agent`
- **AND** the module imports resolve without `ModuleNotFoundError`
- **AND** the attribute lookup for the math specialist agent succeeds

#### Scenario: the 8 canonical module paths are all importable

- **WHEN** `python -c "from importlib import import_module; [import_module(f'cianfhoghlaim.agents.tuatha.{s}_agent') for s in ['math', 'appm', 'chem', 'geog', 'hist', 'engl', 'gael', 'comp']]"`
- **THEN** the command exits 0 with no `ModuleNotFoundError`
- **AND** all 8 modules resolve to physical files under
  `cianfhoghlaim/agents/tuatha/`

#### Scenario: select_optimal_for_m4_max is the canonical M4-Max helper

- **WHEN** `from cianfhoghlaim.meaisinfhoghlaim.ocr.models.registry import select_optimal_for_m4_max`
- **THEN** the import succeeds
- **AND** `select_optimal_for_m4_max()` returns `"gemma-4-26B-A4B"`

#### Scenario: get_default_for_m4_max back-compat alias emits DeprecationWarning

- **WHEN** `from cianfhoghlaim.meaisinfhoghlaim.ocr.models.registry import get_default_for_m4_max`
- **AND** `get_default_for_m4_max()` is called with
  `warnings.simplefilter('error', DeprecationWarning)` active
- **THEN** a `DeprecationWarning` is raised
- **AND** the warning message references `select_optimal_for_m4_max` as the replacement

#### Scenario: no phantom `meaisinfhoghlaim.educational` paths remain in `root_agent.py`

- **WHEN** `grep -nE "meaisinfhoghlaim\.educational" cianfhoghlaim/agents/adk/root_agent.py`
- **THEN** the output SHALL be empty (0 matches)