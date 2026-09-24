"""cocoindex_flows.british_isles.ireland.tertiary.uog.colleges_flow
-- the UoG tertiary 4-college CocoIndex v1 App.

Per openspec/changes/2026-09-23-uog-tertiary-real-data-upgrade-v1/.

Embeds the 4 real UoG colleges (Firecrawl-verified 2026-09-23) into
LanceDB for semantic search ("find the college that offers X").

Embedder: BAAI/bge-m3 (1024-d, multilingual) per
cocoindex_flows/_shared/_lifespan.py:108.

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import cocoindex as coco

from dlt_sources.british_isles.ireland.tertiary.uog import colleges_pipeline

LANCEDB_TABLE = "uog_colleges"
LANCEDB_URI = "stedding/lancedb/uog.lance"
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBED_DIM = 1024


@coco.function(
    name="uog_colleges_flow",
    data_sources={"colleges": colleges_pipeline.colleges},
)
def uog_colleges_flow(flow_builder: coco.FlowBuilder, colleges: coco.DataSource) -> None:
    with flow_builder.read_data("colleges"):
        rows = flow_builder.add_classes(CollegeRecord)
    with rows.row() as row:
        flow_builder.embed(
            row["embedding"],
            coco.structured_data(
                row["college_name_english"],
                row["college_name_irish"] or "",
                row["dean_name"] or "",
            ),
        )
        flow_builder.export(
            row["college_id"],
            row["college_name_english"],
            row["college_name_irish"],
            row["dean_name"],
            row["source_url"],
            row["nfq_min"],
            row["nfq_max"],
            row["established_year"],
            row["school_count"],
            row["embedding"],
        )


class CollegeRecord(coco.Record):
    college_id: str
    college_name_english: str
    college_name_irish: str | None
    dean_name: str | None
    source_url: str
    nfq_min: int
    nfq_max: int
    established_year: int | None
    school_count: int | None
    embedding: coco.Vector[1024]


def main() -> None:
    print("uog_colleges_flow: starting")
    flow = uog_colleges_flow.setup()
    flow.update()
    print(f"uog_colleges_flow: complete. Output → {LANCEDB_TABLE} @ {LANCEDB_URI}")


if __name__ == "__main__":
    main()
