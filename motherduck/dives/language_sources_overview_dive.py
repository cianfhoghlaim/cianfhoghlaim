"""
Language Sources Overview Dive — BIEP v3 MotherDuck Dive.

Per the 2026-08-13-biep-v3-filesystem-and-language-pipelines-v1 change.

The BIEP v3 Language Sources Overview Dive. Reads the 19 canonical
language DLT sources at `dlt_sources/language/` and surfaces the
per-source row count + total size + last-materialised-at.

Dive name: ``language_sources_overview``
DuckLake tables read:
  - ``md:cianfhoghlaim.education.language.<source>.rows``
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


LANGUAGE_SOURCES: tuple[str, ...] = (
    "ainm",
    "canuint",
    "canuint_audio",
    "canuint_dialect_summary",
    "canuint_search",
    "canuint_word_alignment",
    "duchas",
    "duchas_images",
    "gaois",
    "gaois_combined",
    "heritage",
    "hidden_heritages",
    "local_documents_by_subject",
    "local_education_documents",
    "logainm",
    "tearma",
    "tearma_search",
    "universal_dependencies",
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


DIVE_SQL = f"""
WITH language_sources AS (
    {' UNION ALL BY NAME '.join(
        f"SELECT '{s}' AS source, COUNT(*) AS row_count, MAX(ingested_at) AS last_ingested "
        f"FROM cianfhoghlaim.education.language.{s}.rows"
        for s in LANGUAGE_SOURCES
    )}
)
SELECT * FROM language_sources
ORDER BY source
"""


LANGUAGE_SOURCES_OVERVIEW_DIVE = DiveSpec(
    name="language_sources_overview",
    description=(
        "BIEP v3 — Language sources overview. 19 canonical DLT sources "
        "at `dlt_sources/language/` with per-source row count + last "
        "ingested timestamp."
    ),
    sql=DIVE_SQL,
    charts=[
        {
            "type": "bar",
            "title": "Row count per language source",
            "x": "source",
            "y": "row_count",
        },
    ],
    filters=[
        {"column": "source", "type": "multi_select", "options": list(LANGUAGE_SOURCES)},
    ],
)


def save_dive_definition() -> dict[str, Any]:
    return LANGUAGE_SOURCES_OVERVIEW_DIVE.to_dict()


if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(json.dumps(save_dive_definition(), indent=2))
    else:
        print(f"Dive: {LANGUAGE_SOURCES_OVERVIEW_DIVE.name}")
        print(f"Description: {LANGUAGE_SOURCES_OVERVIEW_DIVE.description}")
        print(f"Charts: {len(LANGUAGE_SOURCES_OVERVIEW_DIVE.charts)}")
        print(f"Filters: {len(LANGUAGE_SOURCES_OVERVIEW_DIVE.filters)}")
