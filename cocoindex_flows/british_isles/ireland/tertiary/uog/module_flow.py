"""cocoindex_flows.british_isles.ireland.tertiary.uog.module_flow
-- the per-module CocoIndex factory flow (the tertiary flagship).

Per openspec/changes/2026-09-23-uog-tertiary-real-data-upgrade-v1/.

This flow embeds every per-module row from
`dlt_sources/british_isles.ireland.tertiary.uog.modules` into
LanceDB for semantic search ("find modules that teach X").

The flow uses the canonical snake_case full-name module_id
(e.g. `cs203_data_structures`) as the primary key, which is the
same key the SU package uses for JOINs.

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

from dlt_sources.british_isles.ireland.tertiary.uog import modules_pipeline

LANCEDB_TABLE = "uog_modules"
LANCEDB_URI = "stedding/lancedb/uog.lance"
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBED_DIM = 1024


@coco.function(
    name="uog_modules_flow",
    data_sources={"modules": modules_pipeline.modules},
)
def uog_modules_flow(flow_builder: coco.FlowBuilder, modules: coco.DataSource) -> None:
    with flow_builder.read_data("modules"):
        rows = flow_builder.add_classes(ModuleRecord)
    with rows.row() as row:
        flow_builder.embed(
            row["embedding"],
            coco.structured_data(
                row["title_english"],
                row["title_irish"] or "",
                row["description_short"] or "",
                " ".join(row["learning_outcomes"] or []),
            ),
        )
        flow_builder.export(
            row["module_id"],
            row["module_code"],
            row["programme_ids"],
            row["school_id"],
            row["title_english"],
            row["title_irish"],
            row["level"],
            row["year_of_study"],
            row["semester"],
            row["ects_credits"],
            row["delivery_language"],
            row["academic_year"],
            row["learning_outcomes"],
            row["prerequisite_module_codes"],
            row["syllabus_url"],
            row["embedding"],
        )


class ModuleRecord(coco.Record):
    module_id: str
    module_code: str
    programme_ids: list[str]
    school_id: str
    title_english: str
    title_irish: str | None
    level: str
    year_of_study: int | None
    semester: str | None
    ects_credits: int
    delivery_language: str
    academic_year: str
    learning_outcomes: list[str]
    prerequisite_module_codes: list[str]
    syllabus_url: str | None
    embedding: coco.Vector[1024]


def main() -> None:
    print("uog_modules_flow: starting")
    flow = uog_modules_flow.setup()
    flow.update()
    print(f"uog_modules_flow: complete. Output → {LANCEDB_TABLE} @ {LANCEDB_URI}")


if __name__ == "__main__":
    main()
