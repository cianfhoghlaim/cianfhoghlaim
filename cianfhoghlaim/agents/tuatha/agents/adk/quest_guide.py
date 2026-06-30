"""
Quest Guide Agent — thin re-export (round 7 phase 5).

The canonical LlmAgent construction lives in
`oideachais.agents.adk.quest_guide_agent` per the 6-phase refactor
plan. This file is a backwards-compatible re-export.
"""
from cianfhoghlaim.agents.adk.quest_guide_agent import quest_guide_agent

__all__ = ["quest_guide_agent"]
