"""senior_cycle_embedding — CocoIndex v1 App for Senior Cycle (ages 15-18).

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.

Embeds the 40+ NCCA senior cycle subjects into LanceDB. Reads from
the `_sc_subjects.yaml` factory config (40 rows).

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

from dlt_sources.british_isles.ireland.education.senior_cycle import sc_subjects

LANCEDB_TABLE = "k12_senior_cycle"
LANCEDB_URI = "stedding/lancedb/k12.lance"
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBED_DIM = 1024


@coco.function(
    name="senior_cycle_embedding",
    data_sources={"sc_subjects": sc_subjects},
)
def senior_cycle_embedding(flow_builder: coco.FlowBuilder, sc_subjects: coco.DataSource) -> None:
    with flow_builder.read_data("sc_subjects"):
        rows = flow_builder.add_classes(ScSubjectRecord)
    with rows.row() as row:
        flow_builder.embed(
            row["embedding"],
            coco.structured_data(row["name_en"], row["level"]),
        )
        flow_builder.export(
            row["subject_slug"], row["name_en"], row["level"],
            row["embedding"],
        )


class ScSubjectRecord(coco.Record):
    subject_slug: str
    name_en: str
    level: str
    embedding: coco.Vector[1024]


def main() -> None:
    print("senior_cycle_embedding: starting")
    flow = senior_cycle_embedding.setup()
    flow.update()
    print(f"senior_cycle_embedding: complete. Output → {LANCEDB_TABLE} @ {LANCEDB_URI}")


if __name__ == "__main__":
    main()
