"""cocoindex_flows.british_isles.ireland.tertiary.uog.module_handbook_flow
-- per-module PDF handbook embedding + 4-path OCR ensemble.

Per openspec/changes/2026-09-23-uog-tertiary-real-data-upgrade-v1/.

Embeds the per-module PDF handbooks (the canonical 6-12 sections per
module) into LanceDB using the BIEP v2 4-path OCR ensemble
(BAML/Docling + Unstract + qwen3-vl-8b + gemma-4-26B-A4B) + RAGAS voting.

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

from dlt_sources.british_isles.ireland.tertiary.uog import module_handbooks_pipeline

LANCEDB_TABLE = "uog_module_handbooks"
LANCEDB_URI = "stedding/lancedb/uog.lance"
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBED_DIM = 1024
OCR_ENSEMBLE = "biep_v2_4path"  # BAML/Docling + Unstract + qwen3-vl-8b + gemma-4-26B-A4B
RAGAS_THRESHOLD = 0.70


@coco.function(
    name="uog_module_handbooks_flow",
    data_sources={"handbooks": module_handbooks_pipeline.module_handbooks},
)
def uog_module_handbooks_flow(
    flow_builder: coco.FlowBuilder,
    handbooks: coco.DataSource,
) -> None:
    with flow_builder.read_data("handbooks"):
        rows = flow_builder.add_classes(HandbookRecord)
    with rows.row() as row:
        flow_builder.embed(
            row["embedding"],
            coco.structured_data(
                row["module_code"],
                row["pdf_url"],
                "UOG module handbook",
            ),
        )
        flow_builder.export(
            row["module_code"],
            row["pdf_url"],
            row["total_pages"],
            row["scraped_at"],
            row["confidence"],
            row["embedding"],
        )


class HandbookRecord(coco.Record):
    module_code: str
    pdf_url: str
    total_pages: int
    scraped_at: str
    confidence: float
    embedding: coco.Vector[1024]


def main() -> None:
    print("uog_module_handbooks_flow: starting")
    flow = uog_module_handbooks_flow.setup()
    flow.update()
    print(f"uog_module_handbooks_flow: complete. Output → {LANCEDB_TABLE} @ {LANCEDB_URI}")


if __name__ == "__main__":
    main()
