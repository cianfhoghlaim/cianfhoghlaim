"""cocoindex_flows.british_isles.ireland.tertiary.uog.research_outputs_flow
-- the UoG research outputs CocoIndex v1 App.

Per openspec/changes/2026-09-23-uog-tertiary-real-data-upgrade-v1/.

Embeds the 7 real UoG research outputs (Firecrawl-verified 2026-09-23)
into LanceDB.

Embedder: BAAI/bge-m3 (1024-d).

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import cocoindex as coco

from dlt_sources.british_isles.ireland.tertiary.uog import research_outputs_pipeline

LANCEDB_TABLE = "uog_research_outputs"
LANCEDB_URI = "stedding/lancedb/uog.lance"
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBED_DIM = 1024


@coco.function(
    name="uog_research_outputs_flow",
    data_sources={"research_outputs": research_outputs_pipeline.research_outputs},
)
def uog_research_outputs_flow(
    flow_builder: coco.FlowBuilder,
    research_outputs: coco.DataSource,
) -> None:
    with flow_builder.read_data("research_outputs"):
        rows = flow_builder.add_classes(ResearchOutputRecord)
    with rows.row() as row:
        flow_builder.embed(
            row["embedding"],
            coco.structured_data(
                row["title"],
                row["abstract"] or "",
                row["authors"] or [],
                row["journal"] or "",
            ),
        )
        flow_builder.export(
            row["url"],
            row["title"],
            row["type"],
            row["authors"],
            row["year"],
            row["doi"],
            row["journal"],
            row["abstract"],
            row["related_school_id"],
            row["scraped_at"],
            row["embedding"],
        )


class ResearchOutputRecord(coco.Record):
    url: str
    title: str
    type: str
    authors: list[str]
    year: int
    doi: str | None
    journal: str | None
    abstract: str | None
    related_school_id: str | None
    scraped_at: str
    embedding: coco.Vector[1024]


def main() -> None:
    print("uog_research_outputs_flow: starting")
    flow = uog_research_outputs_flow.setup()
    flow.update()
    print(f"uog_research_outputs_flow: complete. Output → {LANCEDB_TABLE} @ {LANCEDB_URI}")


if __name__ == "__main__":
    main()
