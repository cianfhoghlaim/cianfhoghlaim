"""primary_embedding — CocoIndex v1 App for Primary Curriculum (ages 4-12).

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.

Embeds the 12 NCCA primary curriculum areas into LanceDB for semantic
search. Reads from the `_primary_modules.yaml` factory config (50 rows).

Embedder: BAAI/bge-m3 (1024-d).

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import cocoindex as coco

from dlt_sources.british_isles.ireland.education.primary import primary_curriculum_areas

LANCEDB_TABLE = "k12_primary"
LANCEDB_URI = "stedding/lancedb/k12.lance"
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBED_DIM = 1024


@coco.function(
    name="primary_embedding",
    data_sources={"primary_areas": primary_curriculum_areas},
)
def primary_embedding(flow_builder: coco.FlowBuilder, primary_areas: coco.DataSource) -> None:
    with flow_builder.read_data("primary_areas"):
        rows = flow_builder.add_classes(PrimaryAreaRecord)
    with rows.row() as row:
        flow_builder.embed(
            row["embedding"],
            coco.structured_data(
                row["name_en"], row["name_ga"] or "",
                row["rationale_en"], row["rationale_ga"] or "",
                " ".join(row["strands"] or []),
            ),
        )
        flow_builder.export(
            row["area_code"], row["name_en"], row["name_ga"],
            row["rationale_en"], row["rationale_ga"],
            row["strands"], row["integration_links"],
            row["source_url"], row["document_year"],
            row["embedding"],
        )


class PrimaryAreaRecord(coco.Record):
    area_code: str
    name_en: str
    name_ga: str | None
    rationale_en: str
    rationale_ga: str | None
    strands: list[str]
    integration_links: list[str]
    source_url: str
    document_year: int
    embedding: coco.Vector[1024]


def main() -> None:
    print("primary_embedding: starting")
    flow = primary_embedding.setup()
    flow.update()
    print(f"primary_embedding: complete. Output → {LANCEDB_TABLE} @ {LANCEDB_URI}")


if __name__ == "__main__":
    main()
