"""meaisinfhoghlaim Agent Memory Dive — BIEP v3 MotherDuck Dive.

Per the meaisinfhoghlaim v5 umbrella spec.

The BIEP v3 Agent Memory Dive. Surfaces per-agent memory backend state
(Letta, Cognify, Graphiti).

Dive name: ``meaisin_agent_memory_dive``
DuckLake tables read:
  - ``md:cianfhoghlaim.education.meaisin.agent.<name>.memory.runs``
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
WITH agent_memory AS (
    {' UNION ALL BY NAME '.join(
        f"SELECT '{a}' AS agent_name, "
        f"memory_backend, "
        f"COUNT(*) AS memory_state_count, "
        f"AVG(memory_size_bytes) AS avg_memory_size_bytes "
        f"FROM cianfhoghlaim.education.meaisin.agent.{a}.memory.runs"
        for a in AGENTS
    )}
)
SELECT * FROM agent_memory
ORDER BY agent_name
"""


MEASIN_AGENT_MEMORY_DIVE = DiveSpec(
    name="meaisin_agent_memory_dive",
    description=(
        "BIEP v3 — meaisinfhoghlaim 12-agent memory backend state. "
        "Surfaces per-agent memory backend (Letta, Cognify, Graphiti) + "
        "memory state count + avg memory size."
    ),
    sql=DIVE_SQL,
    charts=[
        {
            "type": "bar",
            "title": "Memory state count per agent (bar chart)",
            "x": "agent_name",
            "y": "memory_state_count",
        },
        {
            "type": "bar",
            "title": "Avg memory size per agent (bar chart)",
            "x": "agent_name",
            "y": "avg_memory_size_bytes",
        },
    ],
    filters=[
        {"column": "agent_name", "type": "multi_select", "options": list(AGENTS)},
    ],
)


def save_dive_definition() -> dict[str, Any]:
    return MEASIN_AGENT_MEMORY_DIVE.to_dict()


if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(json.dumps(save_dive_definition(), indent=2))
    else:
        print(f"Dive: {MEASIN_AGENT_MEMORY_DIVE.name}")
        print(f"Description: {MEASIN_AGENT_MEMORY_DIVE.description}")
        print(f"Charts: {len(MEASIN_AGENT_MEMORY_DIVE.charts)}")
        print(f"Filters: {len(MEASIN_AGENT_MEMORY_DIVE.filters)}")
