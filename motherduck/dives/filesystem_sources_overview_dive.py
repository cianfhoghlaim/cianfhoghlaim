"""
Filesystem Sources Overview Dive — BIEP v3 MotherDuck Dive.

Per the 2026-08-13-biep-v3-filesystem-and-language-pipelines-v1 change.

The BIEP v3 Filesystem Sources Overview Dive. Reads the 11 canonical
filesystem DLT sources at `dlt_sources/filesystem/` and surfaces the
per-source row count + total size + last-materialised-at.

Dive name: ``filesystem_sources_overview``
DuckLake tables read:
  - ``md:cianfhoghlaim.education.filesystem.<source>.rows``
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


FILESYSTEM_SOURCES: tuple[str, ...] = (
    "leabharlann_books",
    "gemini_deep_research",
    "google_takeout",
    "takeout_v1",
    "email_inbox",
    "leaving_cert_source",
    "university_of_galway",
    "zotero",
    "gemini_corpus_source",
    "pdf_download_source",
    "previews",
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
WITH filesystem_sources AS (
    {' UNION ALL BY NAME '.join(
        f"SELECT '{s}' AS source, COUNT(*) AS row_count, MAX(ingested_at) AS last_ingested "
        f"FROM cianfhoghlaim.education.filesystem.{s}.rows"
        for s in FILESYSTEM_SOURCES
    )}
)
SELECT * FROM filesystem_sources
ORDER BY source
"""


FILESYSTEM_SOURCES_OVERVIEW_DIVE = DiveSpec(
    name="filesystem_sources_overview",
    description=(
        "BIEP v3 — Filesystem sources overview. 11 canonical DLT sources "
        "at `dlt_sources/filesystem/` with per-source row count + last "
        "ingested timestamp."
    ),
    sql=DIVE_SQL,
    charts=[
        {
            "type": "bar",
            "title": "Row count per filesystem source",
            "x": "source",
            "y": "row_count",
        },
    ],
    filters=[
        {"column": "source", "type": "multi_select", "options": list(FILESYSTEM_SOURCES)},
    ],
)


def save_dive_definition() -> dict[str, Any]:
    return FILESYSTEM_SOURCES_OVERVIEW_DIVE.to_dict()


if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(json.dumps(save_dive_definition(), indent=2))
    else:
        print(f"Dive: {FILESYSTEM_SOURCES_OVERVIEW_DIVE.name}")
        print(f"Description: {FILESYSTEM_SOURCES_OVERVIEW_DIVE.description}")
        print(f"Charts: {len(FILESYSTEM_SOURCES_OVERVIEW_DIVE.charts)}")
        print(f"Filters: {len(FILESYSTEM_SOURCES_OVERVIEW_DIVE.filters)}")
