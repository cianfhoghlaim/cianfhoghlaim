"""cocoindex_flows.british_isles.ireland.tertiary.uog.past_paper_flow
-- per-module past papers from regexam.nuigalway.ie.

Per openspec/changes/2026-09-23-uog-tertiary-real-data-upgrade-v1/.

Embeds the per-module past papers (each paper_id + module_code + year +
paper_number + pdf_url + marking_scheme_url) into LanceDB.

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

from dlt_sources.british_isles.ireland.tertiary.uog import past_papers_pipeline

LANCEDB_TABLE = "uog_past_papers"
LANCEDB_URI = "stedding/lancedb/uog.lance"
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBED_DIM = 1024


@coco.function(
    name="uog_past_papers_flow",
    data_sources={"past_papers": past_papers_pipeline.past_papers},
)
def uog_past_papers_flow(
    flow_builder: coco.FlowBuilder,
    past_papers: coco.DataSource,
) -> None:
    with flow_builder.read_data("past_papers"):
        rows = flow_builder.add_classes(PastPaperRecord)
    with rows.row() as row:
        flow_builder.embed(
            row["embedding"],
            coco.structured_data(
                row["paper_id"],
                row["module_code"],
                "UOG past paper",
            ),
        )
        flow_builder.export(
            row["paper_id"],
            row["module_code"],
            row["year"],
            row["paper_number"],
            row["pdf_url"],
            row["has_marking_scheme"],
            row["marking_scheme_url"],
            row["scraped_at"],
            row["embedding"],
        )


class PastPaperRecord(coco.Record):
    paper_id: str
    module_code: str
    year: int
    paper_number: int
    pdf_url: str
    has_marking_scheme: bool
    marking_scheme_url: str | None
    scraped_at: str
    embedding: coco.Vector[1024]


def main() -> None:
    print("uog_past_papers_flow: starting")
    flow = uog_past_papers_flow.setup()
    flow.update()
    print(f"uog_past_papers_flow: complete. Output → {LANCEDB_TABLE} @ {LANCEDB_URI}")


if __name__ == "__main__":
    main()
