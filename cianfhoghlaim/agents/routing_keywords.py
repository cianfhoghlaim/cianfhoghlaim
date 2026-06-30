"""
Routing Keywords for the 12-agent fleet.

This module is the canonical home for the L5 `ROUTING_KEYWORDS` dict
used by `CelticAgentOpsComponent` to verify each agent is routable
in the root_agent.

Moved out of `adk/root_agent.py` so it can be imported independently
of the ADK dependency (which may not be installed in every env).
The seed values mirror the agent-fleet-orchestration skill's
"12-bucket" map. The L5 Components append at scaffold time
(CelticAgentOpsComponent._append_routing_keywords) so a new agent
becomes routable without touching this file.

The canonical 12-agent fleet (per the agent-fleet-orchestration skill):
- root_agent (custom)
- 8 ADK agents: curriculum, translation, corpus, research, geospatial,
  statistics, curriculum_comparison, mcp_curriculum
- 3 Agno agents: education_research, bunchloch_research, agui_curriculum
(Voice agent / pipecat is deferred to a follow-on change.)
"""
from __future__ import annotations

from typing import Dict, List

# The seed values. L5 Components extend this dict at build time.
ROUTING_KEYWORDS: Dict[str, List[str]] = {
    "root_agent": [],
    "curriculum_agent": [
        "curriculum", "spec", "learning outcome", "ncca", "cfe", "cfw",
        "ccea", "sqa", "leaving cert", "gcse", "a-level",
    ],
    "translation_agent": [
        "translate", "gaeilge", "irish", "scottish gaelic", "welsh",
        "cymraeg", "brezhoneg", "cornish", "manx",
    ],
    "corpus_agent": [
        "corpus", "duchas", "gaois", "tearma", "logainm", "canuint",
        "foclóir",
    ],
    "research_agent": ["research", "paper", "cite", "doi", "arxiv"],
    "education_research_agent": [
        "policy", "report", "oecd", "european commission", "unesco",
    ],
    "bunchloch_research_agent": [
        "m4", "macbook", "local model", "federated", "on-device",
    ],
    "geospatial_agent": [
        "geospatial", "lsoa", "data zone", "map", "school location",
    ],
    "statistics_agent": [
        "statistics", "metric", "benchmark", "performance", "kpi",
    ],
    "curriculum_comparison_agent": [
        "compare", "cross-nation", "side-by-side", "uk vs ireland",
    ],
    "agui_curriculum_agent": ["ag-ui", "streaming", "copilot", "react"],
    "mcp_curriculum_agent": ["mcp", "model context protocol", "tool"],
}


__all__ = ["ROUTING_KEYWORDS"]
