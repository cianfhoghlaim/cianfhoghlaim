"""
Research Assistant Agent — thin re-export (round 7 phase 5).

The canonical LlmAgent construction lives in
`oideachais.agents.adk.research_assistant_agent` per the 6-phase
refactor plan. This file is a backwards-compatible re-export.
"""
from oideachais.agents.adk.research_assistant_agent import (
    research_assistant_agent,
)

__all__ = ["research_assistant_agent"]
