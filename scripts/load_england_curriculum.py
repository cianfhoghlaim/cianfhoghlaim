"""Land England's first real local corpus into the local DuckLake bronze
layer.

Per the local-lakehouse plan's Phase 6
(/Users/cianmacandeisigh/.claude/plans/after-recent-plans-and-enumerated-cosmos.md):
England has zero real corpus today. The canonical, Dagster-materialized
pipeline (england_jurisdiction_pipeline.py -> generic_england_assets.py)
never fetches anything — it reads a 4-row, AQA-only placeholder registry
seed. But the real crawl code — national_curriculum_source (gov.uk) and
all_exam_boards_source (AQA + Edexcel + OCR) — already exists in the
canonical location (dlt_sources/british_isles/england/education/) and is
already imported/wired in education/__init__.py; it has simply never been
run. This script runs it directly, for the first time, against real
endpoints via Firecrawl.

Page caps are deliberately small (this is a first real run, not a full
crawl — Firecrawl calls are billed) — raise max_pages once this is
confirmed stable and the England registry (Phase 6 item 4 in the plan,
not done in this script) is expanded to match.

Run: mise exec -- .venv/bin/python3 scripts/load_england_curriculum.py
"""

from __future__ import annotations

import dlt

from dlt_sources.british_isles.england.education.all_exam_boards import (
    all_exam_boards_source,
)
from dlt_sources.british_isles.england.education.national_curriculum import (
    national_curriculum_source,
)
from dlt_sources.common.destinations_cianfhoghlaim import get_dlt_destination


def main() -> int:
    pipeline = dlt.pipeline(
        pipeline_name="england_curriculum",
        destination=get_dlt_destination(use_ducklake=True),
        dataset_name="cianfhoghlaim.bronze.england_curriculum",
    )

    load_info = pipeline.run(
        national_curriculum_source(key_stage="key_stage_1", max_pages=5)
    )
    print("=== national_curriculum_source ===")
    print(load_info)

    load_info2 = pipeline.run(
        all_exam_boards_source(qualification_level="gcse", max_pages=9)
    )
    print("=== all_exam_boards_source ===")
    print(load_info2)

    with pipeline.sql_client() as client:
        for table in ("national_curriculum_pages", "all_exam_board_pages", "all_exam_board_pdf_links"):
            try:
                (n,) = next(iter(client.execute_sql(f"SELECT COUNT(*) FROM {table}")))
                print(f"{table}: {n} rows")
            except Exception as e:
                print(f"{table}: (no table — {e})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
