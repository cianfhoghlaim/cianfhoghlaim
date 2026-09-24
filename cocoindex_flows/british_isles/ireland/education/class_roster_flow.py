"""class_roster_flow — CocoIndex v1 App for per-class roster.

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.

Embeds the per-student roster from `dlt_sources/.../education/class_roster.py`.

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

from dlt_sources.british_isles.ireland.education.class_roster import class_roster

LANCEDB_TABLE = "k12_class_roster"
LANCEDB_URI = "stedding/lancedb/k12.lance"
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBED_DIM = 1024


@coco.function(name="class_roster_flow", data_sources={"class_roster": class_roster})
def class_roster_flow(flow_builder: coco.FlowBuilder, class_roster: coco.DataSource) -> None:
    with flow_builder.read_data("class_roster"):
        rows = flow_builder.add_classes(ClassRosterRecord)
    with rows.row() as row:
        flow_builder.embed(
            row["embedding"],
            coco.structured_data(
                row["first_name_en"], row["last_name_en"],
                row["class_id"], row["year_level"],
            ),
        )
        flow_builder.export(
            row["student_id"], row["class_id"], row["year_level"],
            row["school_id"],
            row["first_name_en"], row["last_name_en"],
            row["sen_status"], row["english_additional_language"],
            row["attendance_pct_ytd"],
            row["subject_enrolments"], row["embedding"],
        )


class ClassRosterRecord(coco.Record):
    student_id: str
    class_id: str
    year_level: str
    school_id: str
    first_name_en: str
    last_name_en: str
    sen_status: str
    english_additional_language: bool
    attendance_pct_ytd: float
    subject_enrolments: list[str]
    embedding: coco.Vector[1024]


def main() -> None:
    print("class_roster_flow: starting")
    flow = class_roster_flow.setup()
    flow.update()
    print(f"class_roster_flow: complete. Output → {LANCEDB_TABLE} @ {LANCEDB_URI}")


if __name__ == "__main__":
    main()
