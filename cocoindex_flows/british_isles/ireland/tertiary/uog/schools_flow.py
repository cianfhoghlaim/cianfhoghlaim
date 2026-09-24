"""cocoindex_flows.british_isles.ireland.tertiary.uog.schools_flow
-- the UoG tertiary 18-school CocoIndex v1 App.

Per openspec/changes/2026-09-23-uog-tertiary-real-data-upgrade-v1/.

Embeds the 18 real UoG schools (Firecrawl-verified 2026-09-23) into
LanceDB. The schools are the second tier of the College → School →
Programme → Module hierarchy.

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

from dlt_sources.british_isles.ireland.tertiary.uog import schools_pipeline

LANCEDB_TABLE = "uog_schools"
LANCEDB_URI = "stedding/lancedb/uog.lance"
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBED_DIM = 1024


@coco.function(
    name="uog_schools_flow",
    data_sources={"schools": schools_pipeline.schools},
)
def uog_schools_flow(flow_builder: coco.FlowBuilder, schools: coco.DataSource) -> None:
    with flow_builder.read_data("schools"):
        rows = flow_builder.add_classes(SchoolRecord)
    with rows.row() as row:
        flow_builder.embed(
            row["embedding"],
            coco.structured_data(
                row["school_name_english"],
                row["school_name_irish"] or "",
                row["head_of_school"] or "",
            ),
        )
        flow_builder.export(
            row["school_id"],
            row["college_id"],
            row["school_name_english"],
            row["school_name_irish"],
            row["head_of_school"],
            row["n_students"],
            row["n_staff"],
            row["research_centres"],
            row["source_url"],
            row["embedding"],
        )


class SchoolRecord(coco.Record):
    school_id: str
    college_id: str
    school_name_english: str
    school_name_irish: str | None
    head_of_school: str | None
    n_students: int | None
    n_staff: int | None
    research_centres: list[str]
    source_url: str
    embedding: coco.Vector[1024]


def main() -> None:
    print("uog_schools_flow: starting")
    flow = uog_schools_flow.setup()
    flow.update()
    print(f"uog_schools_flow: complete. Output → {LANCEDB_TABLE} @ {LANCEDB_URI}")


if __name__ == "__main__":
    main()
