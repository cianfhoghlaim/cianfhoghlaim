"""
Celtic Tutor Agent — thin re-export (round 7 phase 5).

The canonical LlmAgent construction lives in
`oideachais.agents.adk.celtic_tutor_agent` per the 6-phase refactor
plan. This file is a backwards-compatible re-export so consumers
like `tuatha.agents.orchestrator.AgentRegistry` can keep doing
`from .adk.celtic_tutor import celtic_tutor_agent`.
"""
from oideachais.agents.adk.celtic_tutor_agent import celtic_tutor_agent

__all__ = ["celtic_tutor_agent"]
