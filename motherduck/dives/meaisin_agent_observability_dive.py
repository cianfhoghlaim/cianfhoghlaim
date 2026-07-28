"""meaisinfhoghlaim Agent Observability Dive — BIEP v3 MotherDuck Dive.

Per the meaisinfhoghlaim v5 umbrella spec.

The BIEP v3 Agent Observability Dive. Surfaces per-agent Langfuse traces
+ token usage + observability state.

Dive name: ``meaisin_agent_observability_dive``
DuckLake tables read:
  - ``md:cianfhoghlaim.education.meaisin.agent.<name>.trace.runs``
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


AGENTS = (
    "root", "curriculum", "translation", "corpus", "geospatial",
    "statistics", "research", "curriculum_comparison", "bunchloch_research",
    "ag_ui_curriculum", "site_analysis", "hitl_agent",
)


@dataclass
class DiveSpec:
    name: str
    description: str
    sql: str
    charts: list[dict[str, Any]] = field(default_factory=list)
    filters: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "sql": self.sql,
            "charts": self.charts,
            "filters": self.filters,
        }


DIVE_SQL = """
WITH agent_obs AS (
    {' UNION ALL BY NAME '.join(
        f"SELECT '{a}' AS agent_name, "
        f"COUNT(*) AS trace_count, "
        f"AVG(latency_ms) AS avg_latency_ms, "
        f"AVG(token_count) AS avg_token_count, "
        f"AVG(cost_usd) AS avg_cost_usd "
        f"FROM cianfhoghlaim.education.meaisin.agent.{a}.trace.runs"
        for a in AGENTS
    )}
)
SELECT * FROM agent_obs
ORDER BY agent_name
"""


MEASIN_AGENT_OBSERVABILITY_DIVE = DiveSpec(
    name="meaisin_agent_observability_dive",
    description=(
        "BIEP v3 — meaisinfhoghlaim 12-agent observability. "
        "Surfaces per-agent Langfuse trace count, avg latency, "
        "avg token count, and avg cost."
    ),
    sql=DIVE_SQL,
    charts=[
        {
            "type": "bar",
            "title": "Trace count per agent (bar chart)",
            "x": "agent_name",
            "y": "trace_count",
        },
        {
            "type": "bar",
            "title": "Avg latency per agent (bar chart)",
            "x": "agent_name",
            "y": "avg_latency_ms",
        },
        {
            "type": "bar",
            "title": "Avg cost per agent (bar chart)",
            "x": "agent_name",
            "y": "avg_cost_usd",
        },
    ],
    filters=[
        {"column": "agent_name", "type": "multi_select", "options": list(AGENTS)},
    ],
)


def save_dive_definition() -> dict[str, Any]:
    return MEASIN_AGENT_OBSERVABILITY_DIVE.to_dict()


if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(json.dumps(save_dive_definition(), indent=2))
    else:
        print(f"Dive: {MEASIN_AGENT_OBSERVABILITY_DIVE.name}")
        print(f"Description: {MEASIN_AGENT_OBSERVABILITY_DIVE.description}")
        print(f"Charts: {len(MEASIN_AGENT_OBSERVABILITY_DIVE.charts)}")
        print(f"Filters: {len(MEASIN_AGENT_OBSERVABILITY_DIVE.filters)}")
