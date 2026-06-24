# Tasks: oideachais-tuatha-agents-v1

## 1. Move tools (5 files)

- [x] `git mv tuatha/agents/tools/curriculum_search.py oideachais/agents/adk/tools/tuatha_curriculum_search.py`
- [x] `git mv tuatha/agents/tools/mythology_query.py oideachais/agents/adk/tools/tuatha_mythology_query.py`
- [x] `git mv tuatha/agents/tools/player_progress.py oideachais/agents/adk/tools/tuatha_player_progress.py`
- [x] `git mv tuatha/agents/tools/spatial_query.py oideachais/agents/adk/tools/tuatha_spatial_query.py`
- [x] `git mv tuatha/agents/tools/translation.py oideachais/agents/adk/tools/tuatha_translation.py`
- [x] `rm -rf tuatha/agents/tools/` (empty after moves)

## 2. Move config (1 file)

- [x] `git mv tuatha/agents/config.py oideachais/agents/adk/tuatha_config.py`

## 3. Move agent modules (5 files)

- [x] `git mv tuatha/agents/adk/celtic_tutor.py oideachais/agents/adk/celtic_tutor_agent.py`
- [x] `git mv tuatha/agents/adk/mythology_narrator.py oideachais/agents/adk/mythology_narrator_agent.py`
- [x] `git mv tuatha/agents/adk/quest_guide.py oideachais/agents/adk/quest_guide_agent.py`
- [x] `git mv tuatha/agents/adk/research_assistant.py oideachais/agents/adk/research_assistant_agent.py`
- [x] `git mv tuatha/agents/adk/root_agent.py oideachais/agents/adk/tuatha_root_agent.py`

## 4. Fix imports in moved agent modules

- [x] `celtic_tutor_agent.py`: `from ..config` → `from .tuatha_config`,
      `from ..tools.X` → `from .tools.tuatha_X`
- [x] `mythology_narrator_agent.py`: same pattern
- [x] `quest_guide_agent.py`: same pattern
- [x] `research_assistant_agent.py`: same pattern
- [x] `tuatha_root_agent.py`: `from .X import Y` → `from .X_agent import Y`,
      `from ..config` → `from .tuatha_config`

## 5. Make tuatha wrappers (5 files)

- [x] `tuatha/agents/adk/celtic_tutor.py` (12 lines, thin re-export)
- [x] `tuatha/agents/adk/mythology_narrator.py` (12 lines)
- [x] `tuatha/agents/adk/quest_guide.py` (12 lines)
- [x] `tuatha/agents/adk/research_assistant.py` (12 lines)
- [x] `tuatha/agents/adk/root_agent.py` (28 lines, re-exports all 4 specialists + app + classify_query)
- [x] `tuatha/agents/adk/__init__.py` (new, 22 lines, package docstring)

## 6. Update oideachais/agents/adk/__init__.py

- [x] 5 new import statements for the 4 specialist agents + root_agent
- [x] 5 new entries in `__all__`

## 7. Verify import chain

- [x] All 5 canonical agent modules load and construct successfully
- [x] `tuatha.agents.adk.root_agent` (thin) re-exports all 4 specialists + app + classify_query
- [x] `classify_query("translate hello")` returns "tutor"
- [x] `classify_query("tell me about Cú Chulainn")` returns "mythology"
- [x] root_agent.sub_agents = [celtic_tutor_agent, mythology_narrator_agent, quest_guide_agent, research_assistant_agent]

## 8. Update oideachais/STATUS.md

- [x] §2 (Data flows) — add a `agent` row in the Dagster asset table for
      the tuatha agent code-location

## 9. OpenSpec change

- [x] Create `openspec/changes/oideachais-tuatha-agents-v1/proposal.md`
- [x] Create `openspec/changes/oideachais-tuatha-agents-v1/tasks.md`
- [x] Create `openspec/changes/oideachais-tuatha-agents-v1/specs/oideachais-pipeline/spec.md`
  (5 ADDED Requirements, 2 Scenarios each)
- [x] `openspec validate oideachais-tuatha-agents-v1 --strict`
- [x] `openspec archive oideachais-tuatha-agents-v1 --yes`
- [x] Commit + push to `q3-2026-oideachais-consolidation`
