"""
Mythology Narrator Agent — thin re-export (round 7 phase 5).

The canonical LlmAgent construction lives in
`oideachais.agents.adk.mythology_narrator_agent` per the 6-phase
refactor plan. This file is a backwards-compatible re-export.
"""
from cianfhoghlaim.agents.adk.mythology_narrator_agent import (
    mythology_narrator_agent,
)

__all__ = ["mythology_narrator_agent"]
