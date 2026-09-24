"""aistear_embedding — CocoIndex v1 App for Aistear (Early Childhood).

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.
One of the 3 long-planned primary stages CocoIndex flows (per
british-isles-education-pipeline-v3/spec.md:712-721).

Embeds every Aistear principle + learning goal into LanceDB for
semantic search ("find Aistear goals on wellbeing for toddlers").

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

from dlt_sources.british_isles.ireland.education.aistear import (
    aistear_learning_goals,
    aistear_principles,
)

LANCEDB_TABLE = "k12_aistear"
LANCEDB_URI = "stedding/lancedb/k12.lance"
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBED_DIM = 1024


@coco.function(
    name="aistear_embedding",
    data_sources={
        "principles": aistear_principles,
        "learning_goals": aistear_learning_goals,
    },
)
def aistear_embedding(
    flow_builder: coco.FlowBuilder,
    principles: coco.DataSource,
    learning_goals: coco.DataSource,
) -> None:
    with flow_builder.read_data("principles"):
        principles_rows = flow_builder.add_classes(AistearPrincipleRecord)
    with principles_rows.row() as row:
        flow_builder.embed(
            row["embedding"],
            coco.structured_data(row["name_en"], row["name_ga"] or "", row["description_en"]),
        )
        flow_builder.export(
            row["principle_id"], row["theme"], row["age_band"],
            row["name_en"], row["name_ga"], row["embedding"],
        )
    with flow_builder.read_data("learning_goals"):
        goals_rows = flow_builder.add_classes(AistearGoalRecord)
    with goals_rows.row() as row:
        flow_builder.embed(
            row["embedding"],
            coco.structured_data(row["text_en"], row["text_ga"] or "", row["parent_tip_en"] or ""),
        )
        flow_builder.export(
            row["goal_id"], row["theme"], row["age_band"],
            row["text_en"], row["parent_tip_en"], row["linked_primary_outcome"] or "",
            row["embedding"],
        )


class AistearPrincipleRecord(coco.Record):
    principle_id: str
    theme: str
    age_band: str
    name_en: str
    name_ga: str | None
    embedding: coco.Vector[1024]


class AistearGoalRecord(coco.Record):
    goal_id: str
    theme: str
    age_band: str
    text_en: str
    parent_tip_en: str | None
    linked_primary_outcome: str | None
    embedding: coco.Vector[1024]


def main() -> None:
    print("aistear_embedding: starting")
    flow = aistear_embedding.setup()
    flow.update()
    print(f"aistear_embedding: complete. Output → {LANCEDB_TABLE} @ {LANCEDB_URI}")


if __name__ == "__main__":
    main()
