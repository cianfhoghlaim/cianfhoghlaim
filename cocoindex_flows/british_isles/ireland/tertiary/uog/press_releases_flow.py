"""cocoindex_flows.british_isles.ireland.tertiary.uog.press_releases_flow
-- the UoG press releases CocoIndex v1 App.

Per openspec/changes/2026-09-23-uog-tertiary-real-data-upgrade-v1/.

Embeds the 5 real UoG press releases (Firecrawl-verified 2026-09-23)
into LanceDB for semantic search ("find UoG press releases about X").

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

from dlt_sources.british_isles.ireland.tertiary.uog import press_releases_pipeline

LANCEDB_TABLE = "uog_press_releases"
LANCEDB_URI = "stedding/lancedb/uog.lance"
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBED_DIM = 1024


@coco.function(
    name="uog_press_releases_flow",
    data_sources={"press_releases": press_releases_pipeline.press_releases},
)
def uog_press_releases_flow(
    flow_builder: coco.FlowBuilder,
    press_releases: coco.DataSource,
) -> None:
    with flow_builder.read_data("press_releases"):
        rows = flow_builder.add_classes(PressReleaseRecord)
    with rows.row() as row:
        flow_builder.embed(
            row["embedding"],
            coco.structured_data(
                row["title_english"],
                row["title_irish"] or "",
                row["body_markdown"],
            ),
        )
        flow_builder.export(
            row["url"],
            row["title_english"],
            row["title_irish"],
            row["published_date_iso"],
            row["category"],
            row["body_markdown"],
            row["authors"],
            row["related_programme_ids"],
            row["scraped_at"],
            row["embedding"],
        )


class PressReleaseRecord(coco.Record):
    url: str
    title_english: str
    title_irish: str | None
    published_date_iso: str
    category: str
    body_markdown: str
    authors: list[str]
    related_programme_ids: list[str]
    scraped_at: str
    embedding: coco.Vector[1024]


def main() -> None:
    print("uog_press_releases_flow: starting")
    flow = uog_press_releases_flow.setup()
    flow.update()
    print(f"uog_press_releases_flow: complete. Output → {LANCEDB_TABLE} @ {LANCEDB_URI}")


if __name__ == "__main__":
    main()
