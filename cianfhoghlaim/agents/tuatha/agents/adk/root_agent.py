"""
Tuatha Root Agent — thin re-export (round 7 phase 5).

The canonical LlmAgent + google.adk.apps.app.App construction lives
in `oideachais.agents.adk.tuatha_root_agent` per the 6-phase
refactor plan. This file is a backwards-compatible re-export that
preserves the 4 specialist agents + the `app` + `classify_query`
helper that consumers like `tuatha.agents.orchestrator` rely on.
"""
from cianfhoghlaim.agents.adk.tuatha_root_agent import (
    app,
    celtic_tutor_agent,
    classify_query,
    mythology_narrator_agent,
    quest_guide_agent,
    research_assistant_agent,
    root_agent,
)

__all__ = [
    "app",
    "celtic_tutor_agent",
    "classify_query",
    "mythology_narrator_agent",
    "quest_guide_agent",
    "research_assistant_agent",
    "root_agent",
]
