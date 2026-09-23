"""UoG Programmes CocoIndex flow.

Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.

Embeds every UoG programme row into LanceDB for semantic search.
Mirrors cocoindex_flows/british_isles/ireland/education/lc/_shared.py
pattern (per-subject embedding scaled up to per-programme).

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

from dlt_sources.british_isles.ireland.tertiary.uog import programmes_pipeline

LANCEDB_TABLE = "uog_programmes"
LANCEDB_URI = "stedding/lancedb/uog.lance"
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBED_DIM = 1024


@coco.function(
    name="uog_programmes_flow",
    data_sources={"programmes": programmes_pipeline.programmes},
)
def uog_programmes_flow(flow_builder: coco.FlowBuilder, programmes: coco.DataSource) -> None:
    with flow_builder.read_data("programmes"):
        rows = flow_builder.add_classes(ProgrammeRecord)
    with rows.row() as row:
        flow_builder.embed(
            row["embedding"],
            coco.structured_data(
                row["title_english"],
                row["title_irish"] or "",
                row["entry_requirements"],
            ),
        )
        flow_builder.export(
            row["programme_id"],
            row["programme_code"],
            row["school_id"],
            row["title_english"],
            row["title_irish"],
            row["nfq_level"],
            row["stage"],
            row["duration_months"],
            row["mode"],
            row["total_ects"],
            row["cao_code"],
            row["module_codes"],
            row["entry_requirements"],
            row["delivery_language"],
            row["embedding"],
        )


class ProgrammeRecord(coco.Record):
    programme_id: str
    programme_code: str
    school_id: str
    title_english: str
    title_irish: str | None
    nfq_level: int
    stage: str
    duration_months: int
    mode: str
    total_ects: int
    cao_code: str | None
    module_codes: list[str]
    entry_requirements: str
    delivery_language: str
    embedding: coco.Vector[1024]


def main() -> None:
    print("uog_programmes_flow: starting")
    flow = uog_programmes_flow.setup()
    flow.update()
    print(f"uog_programmes_flow: complete. Output → {LANCEDB_TABLE} @ {LANCEDB_URI}")


if __name__ == "__main__":
    main()
