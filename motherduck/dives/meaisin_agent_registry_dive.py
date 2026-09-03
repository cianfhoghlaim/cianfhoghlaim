"""meaisinfhoghlaim Agent Registry Dive — BIEP v3 MotherDuck Dive.

Per the meaisinfhoghlaim v5 umbrella spec.

The BIEP v3 Agent Registry Dive. Reads the 12-agent framework
configuration and surfaces per-agent coverage.

Dive name: ``meaisin_agent_registry_dive``
DuckLake tables read:
  - ``md:cianfhoghlaim.education.meaisin.agent.<name>.runs``
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
WITH agent_registry AS (
    {' UNION ALL BY NAME '.join(
        f"SELECT '{a}' AS agent_name, "
        f"COUNT(*) AS run_count, "
        f"AVG(ragas_score) AS avg_ragas_score, "
        f"AVG(latency_ms) AS avg_latency_ms "
        f"FROM cianfhoghlaim.education.meaisin.agent.{a}.runs"
        for a in AGENTS
    )}
)
SELECT * FROM agent_registry
ORDER BY agent_name
"""


MEASIN_AGENT_REGISTRY_DIVE = DiveSpec(
    name="meaisin_agent_registry_dive",
    description=(
        "BIEP v3 — meaisinfhoghlaim 12-agent registry overview. "
        "Surfaces per-agent run count, avg RAGAS score, and avg latency."
    ),
    sql=DIVE_SQL,
    charts=[
        {
            "type": "bar",
            "title": "Run count per agent (bar chart)",
            "x": "agent_name",
            "y": "run_count",
        },
        {
            "type": "bar",
            "title": "Average RAGAS score per agent (bar chart)",
            "x": "agent_name",
            "y": "avg_ragas_score",
        },
    ],
    filters=[
        {"column": "agent_name", "type": "multi_select", "options": list(AGENTS)},
    ],
)


def save_dive_definition() -> dict[str, Any]:
    return MEASIN_AGENT_REGISTRY_DIVE.to_dict()


if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(json.dumps(save_dive_definition(), indent=2))
    else:
        print(f"Dive: {MEASIN_AGENT_REGISTRY_DIVE.name}")
        print(f"Description: {MEASIN_AGENT_REGISTRY_DIVE.description}")
        print(f"Charts: {len(MEASIN_AGENT_REGISTRY_DIVE.charts)}")
        print(f"Filters: {len(MEASIN_AGENT_REGISTRY_DIVE.filters)}")
