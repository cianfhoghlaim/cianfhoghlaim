"""cocoindex_flows.british_isles.ireland.tertiary.uog.reading_list_flow
-- per-module reading list embedding.

Per openspec/changes/2026-09-23-uog-tertiary-real-data-upgrade-v1/.

Embeds the per-module reading list items (3-10 essential + recommended
readings per module) into LanceDB.

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

from dlt_sources.british_isles.ireland.tertiary.uog import reading_lists_pipeline

LANCEDB_TABLE = "uog_reading_lists"
LANCEDB_URI = "stedding/lancedb/uog.lance"
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBED_DIM = 1024


@coco.function(
    name="uog_reading_lists_flow",
    data_sources={"reading_lists": reading_lists_pipeline.reading_lists},
)
def uog_reading_lists_flow(
    flow_builder: coco.FlowBuilder,
    reading_lists: coco.DataSource,
) -> None:
    with flow_builder.read_data("reading_lists"):
        rows = flow_builder.add_classes(ReadingListRecord)
    with rows.row() as row:
        flow_builder.embed(
            row["embedding"],
            coco.structured_data(
                row["module_code"],
                "UOG module reading list",
            ),
        )
        flow_builder.export(
            row["module_code"],
            row["scraped_at"],
            row["embedding"],
        )


class ReadingListRecord(coco.Record):
    module_code: str
    scraped_at: str
    embedding: coco.Vector[1024]


def main() -> None:
    print("uog_reading_lists_flow: starting")
    flow = uog_reading_lists_flow.setup()
    flow.update()
    print(f"uog_reading_lists_flow: complete. Output → {LANCEDB_TABLE} @ {LANCEDB_URI}")


if __name__ == "__main__":
    main()
