"""UoG Governance Minutes CocoIndex flow.

Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.

Embeds every UoG governance minute (University Council + Academic
Council) into LanceDB for semantic search ("find all funding-policy
changes from 2024", etc.). Mirrors the KCG
cocoindex_flows/uog/governance_flow.py pattern with the embedder
upgraded from all-MiniLM-L6-v2 (384-d) to BAAI/bge-m3 (1024-d
multilingual).

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import cocoindex as coco

from dlt_sources.british_isles.ireland.tertiary.uog import governance_minutes_pipeline

LANCEDB_TABLE = "uog_governance_minutes"
LANCEDB_URI = "stedding/lancedb/uog.lance"
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBED_DIM = 1024


@coco.function(
    name="uog_governance_flow",
    data_sources={"governance_minutes": governance_minutes_pipeline.governance_minutes},
)
def uog_governance_flow(flow_builder: coco.FlowBuilder, governance_minutes: coco.DataSource) -> None:
    with flow_builder.read_data("governance_minutes"):
        rows = flow_builder.add_classes(GovernanceMinuteRecord)
    with rows.row() as row:
        flow_builder.embed(
            row["embedding"],
            coco.structured_data(
                " ".join(row["agenda_items"]),
                " ".join(row["decisions"]),
                " ".join(row["policy_changes"]),
            ),
        )
        flow_builder.export(
            row["meeting_date_iso"],
            row["body"],
            row["agenda_items"],
            row["decisions"],
            row["policy_changes"],
            row["attendees"],
            row["source_url"],
            row["embedding"],
        )


class GovernanceMinuteRecord(coco.Record):
    meeting_date_iso: str
    body: str
    agenda_items: list[str]
    decisions: list[str]
    policy_changes: list[str]
    attendees: list[str]
    source_url: str
    embedding: coco.Vector[1024]


def main() -> None:
    print("uog_governance_flow: starting")
    flow = uog_governance_flow.setup()
    flow.update()
    print(f"uog_governance_flow: complete. Output → {LANCEDB_TABLE} @ {LANCEDB_URI}")


if __name__ == "__main__":
    main()
