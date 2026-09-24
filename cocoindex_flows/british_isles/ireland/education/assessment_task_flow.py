"""assessment_task_flow — CocoIndex v1 App for per-task assessment records.

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.

Embeds the assessment tasks scored by the `assessment_scorer_agent`.

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

LANCEDB_TABLE = "k12_assessment_tasks"
LANCEDB_URI = "stedding/lancedb/k12.lance"
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBED_DIM = 1024


@coco.function(name="assessment_task_flow")
def assessment_task_flow(flow_builder: coco.FlowBuilder) -> None:
    with flow_builder.read_data("assessment_task_inputs"):
        rows = flow_builder.add_classes(AssessmentTaskRecord)
    with rows.row() as row:
        flow_builder.embed(
            row["embedding"],
            coco.structured_data(row["subject"], row["cba_type"] or "", row["task_description"]),
        )
        flow_builder.export(
            row["task_id"], row["subject"], row["subject_stage"],
            row["task_description"], row["learning_outcomes_assessed"],
            row["level"], row["marks_available"], row["marks_awarded"] or 0,
            row["teacher_comment"] or "", row["embedding"],
        )


class AssessmentTaskRecord(coco.Record):
    task_id: str
    subject: str
    subject_stage: str
    task_description: str
    learning_outcomes_assessed: list[str]
    level: str
    marks_available: int
    marks_awarded: int
    teacher_comment: str | None
    embedding: coco.Vector[1024]


def main() -> None:
    print("assessment_task_flow: starting")
    flow = assessment_task_flow.setup()
    flow.update()
    print(f"assessment_task_flow: complete. Output → {LANCEDB_TABLE} @ {LANCEDB_URI}")


if __name__ == "__main__":
    main()
