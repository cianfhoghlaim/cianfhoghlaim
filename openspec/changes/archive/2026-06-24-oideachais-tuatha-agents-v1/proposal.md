# Change: oideachais-tuatha-agents-v1

## Why

Phase 5 of the 6-phase refactor plan. Phases 1-3 brought the
*codebase indexer* (phase 1), *infrastructure indexer* (phase 2),
and *embedding* (phase 3) surfaces onto v1 CocoIndex + oideachais.
Phase 4 was **removed** (routes stay in tuatha).

Phase 5 brings the 4 tuatha ADK agents onto oideachais. The user
decided: "all 4 tuatha agents stay as thin wrappers importing from
`sruth/oideachais/agents/adk/`". The 4 specialists + the root agent move
their canonical `LlmAgent` construction to
`oideachais.agents.adk.*`; the `tuatha.agents.adk.*` files become
backwards-compatible re-exports.

The 5 tools (curriculum_search, mythology_query, player_progress,
spatial_query, translation) and the TuathAgentConfig dataclass
move with the agents (per the user's plan: v1 v0 imports stay in
oideachais). The 30-day v0 deprecation window keeps the v0 file
structure intact in `tuatha.agents.*` as thin re-exports.

Net effect:

- 11 files move from `sruth/tuatha/agents/` to `sruth/oideachais/agents/adk/`:
  5 agent modules (celtic_tutor, mythology_narrator, quest_guide,
  research_assistant, tuatha_root_agent), 5 tool modules
  (tuatha_curriculum_search, tuatha_mythology_query,
  tuatha_player_progress, tuatha_spatial_query, tuatha_translation),
  1 config module (tuatha_config).
- 5 thin wrapper files at `sruth/tuatha/agents/adk/*.py` re-export from
  `oideachais.agents.adk.*` (12-30 lines each, vs. 161-191 lines
  in the v0).
- `sruth/tuatha/agents/orchestrator.py` keeps working without changes
  (the thin wrappers preserve `from .adk.root_agent import
  celtic_tutor_agent, ...`).
- `sruth/oideachais/agents/adk/__init__.py` re-exports the 5 new modules.

## What Changes

### 1. `sruth/oideachais/agents/adk/celtic_tutor_agent.py` (NEW — moved from `sruth/tuatha/agents/adk/celtic_tutor.py`)

The canonical LlmAgent construction for the Celtic language tutor
(Irish, Scottish Gaelic, Welsh). Uses 4 tools
(`search_curriculum_tool`, `get_vocabulary_tool`,
`translate_text_tool`, `get_learning_outcomes_tool`) and 1 config
(`tuatha_config.config`).

### 2. `sruth/oideachais/agents/adk/mythology_narrator_agent.py` (NEW — moved from `sruth/tuatha/agents/adk/mythology_narrator.py`)

The canonical LlmAgent construction for the Celtic mythology
narrator. Uses 3 tools (`search_mythology_tool`,
`get_character_info`, `get_location_info`).

### 3. `sruth/oideachais/agents/adk/quest_guide_agent.py` (NEW — moved from `sruth/tuatha/agents/adk/quest_guide.py`)

The canonical LlmAgent construction for the quest guide. Uses
4 tools (`get_quest_hints_tool`, `get_player_progress_tool`,
`search_related_curriculum`, `get_learning_outcomes_for_quest`).

### 4. `sruth/oideachais/agents/adk/research_assistant_agent.py` (NEW — moved from `sruth/tuatha/agents/adk/research_assistant.py`)

The canonical LlmAgent construction for the research assistant.
Uses 3 tools (`research_curriculum`, `research_mythology`,
`compare_languages`).

### 5. `sruth/oideachais/agents/adk/tuatha_root_agent.py` (NEW — moved from `sruth/tuatha/agents/adk/root_agent.py`)

The root orchestrator. Imports the 4 specialist agents + the
`tuatha_config.config`. Also constructs the `google.adk.apps.app.App`
and exports the `classify_query` helper.

### 6. `sruth/oideachais/agents/adk/tools/tuatha_*.py` (NEW — moved from `sruth/tuatha/agents/tools/`)

5 tool modules. Each preserves the v0 public API
(`search_curriculum`, `search_mythology`, `get_player_progress`,
`spatial_query`, `translate_text`).

### 7. `sruth/oideachais/agents/adk/tuatha_config.py` (NEW — moved from `sruth/tuatha/agents/config.py`)

The `AgentConfig` dataclass with the Celtic-language-specific
models (gemini-2.0-flash, uccix-llama2-13b, qwen2.5-72b-instruct,
bge-m3) and the x402 payment settings.

### 8. `sruth/tuatha/agents/adk/*.py` (MODIFIED — thin wrappers)

5 files become 10-30 line re-exports of the canonical oideachais
modules. Net: 838 lines deleted, 43 lines added across the 5
files.

### 9. `sruth/oideachais/agents/adk/__init__.py` (MODIFIED)

5 new import statements + 5 new entries in `__all__` for the
4 specialist agents + the root agent.

### 10. `sruth/oideachais/STATUS.md` (MODIFIED)

§2 (Data flows) — add a `agent` row in the Dagster asset table for
the tuatha agent code-location.

## Impact

- Affected specs: `oideachais-pipeline` (5 ADDED Requirements)
- Affected code:
  - 5 new files in `sruth/oideachais/agents/adk/`
  - 5 new files in `sruth/oideachais/agents/adk/tools/`
  - 1 new file in `sruth/oideachais/agents/adk/tuatha_config.py`
  - 5 thin wrappers in `sruth/tuatha/agents/adk/`
  - 1 thin `sruth/tuatha/agents/adk/__init__.py`
  - 1 modified `sruth/oideachais/agents/adk/__init__.py`
- Net line change: -795 lines (838 deleted, 43 added)
- Backwards compatibility: `from tuatha.agents.adk.celtic_tutor
  import celtic_tutor_agent` still works (the thin wrapper
  re-exports from `oideachais.agents.adk.celtic_tutor_agent`)
- `tuatha.agents.orchestrator.AgentRegistry.initialize_defaults()`
  keeps working (it imports from `.adk.root_agent`)

## Success criteria

- `oideachais.agents.adk.celtic_tutor_agent.celtic_tutor_agent` is
  constructible (loads, no ImportError)
- `oideachais.agents.adk.tuatha_root_agent.root_agent` has
  `sub_agents = [celtic_tutor_agent, mythology_narrator_agent,
  quest_guide_agent, research_assistant_agent]`
- `tuatha.agents.adk.celtic_tutor.celtic_tutor_agent` is the same
  object as `oideachais.agents.adk.celtic_tutor_agent.celtic_tutor_agent`
  (the thin wrapper re-exports)
- `tuatha.agents.orchestrator.AgentRegistry.initialize_defaults()`
  registers all 4 agents without errors
- `openspec validate oideachais-tuatha-agents-v1 --strict` passes
