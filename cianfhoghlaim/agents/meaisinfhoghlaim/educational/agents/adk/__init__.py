"""
Thin re-exports for the Tuatha ADK agents (round 7 phase 5).

The canonical LlmAgent construction lives in
`oideachais.agents.adk.*` per the 6-phase refactor plan. Each file
in this package is a backwards-compatible re-export so consumers
like `tuatha.agents.orchestrator.AgentRegistry` can keep doing
`from .adk.celtic_tutor import celtic_tutor_agent` and similar.

Per-file contents:
- `celtic_tutor.py`     → `celtic_tutor_agent`
- `mythology_narrator.py` → `mythology_narrator_agent`
- `quest_guide.py`      → `quest_guide_agent`
- `research_assistant.py` → `research_assistant_agent`
- `root_agent.py`       → `root_agent` + the 4 specialist agents +
  `app` + `classify_query` (the public surface of the v0 root_agent)

The 30-day deprecation window for the v0 implementation is in
`openspec/changes/archive/2026-06-24-oideachais-tuatha-agents-v1/`.
"""
