"""professional_learning_flow — CocoIndex v1 App for OIDE/PDST modules.

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.

Embeds the OIDE/PDST professional learning modules recommended by the
`professional_learning_agent`.

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

LANCEDB_TABLE = "k12_professional_learning"
LANCEDB_URI = "stedding/lancedb/k12.lance"
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBED_DIM = 1024


@coco.function(name="professional_learning_flow")
def professional_learning_flow(flow_builder: coco.FlowBuilder) -> None:
    with flow_builder.read_data("pro_learning_inputs"):
        rows = flow_builder.add_classes(ProLearningRecord)
    with rows.row() as row:
        flow_builder.embed(
            row["embedding"],
            coco.structured_data(row["name_en"], row["provider"], row["format"]),
        )
        flow_builder.export(
            row["module_id"], row["name_en"], row["provider"],
            row["target_stage"], row["subjects"], row["duration_hours"],
            row["format"], row["url"], row["embedding"],
        )


class ProLearningRecord(coco.Record):
    module_id: str
    name_en: str
    provider: str
    target_stage: str
    subjects: list[str]
    duration_hours: int
    format: str
    url: str
    embedding: coco.Vector[1024]


def main() -> None:
    print("professional_learning_flow: starting")
    flow = professional_learning_flow.setup()
    flow.update()
    print(f"professional_learning_flow: complete. Output → {LANCEDB_TABLE} @ {LANCEDB_URI}")


if __name__ == "__main__":
    main()
