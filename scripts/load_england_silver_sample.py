"""Land England's first real BAML-extracted content into silver.

Per the local-lakehouse plan's Phase 7/gap-closing follow-up: reuse the
generic ExtractUKQualSpec(pdf_text, board, subject, qualification_level)
-> UKQualificationSpec BAML function (client BIEPV3Extract, MiniMax
primary) against the real OCR GCSE Mathematics specification page landed
in Phase 6 (cianfhoghlaim.bronze.england_curriculum.ocr_pages) — the
aqa_pages row was tried first but turned out to be a JS-rendered soft-404
shell (350 chars, "This page was not found"), not real content; OCR's
per-subject specification page has substantial real markdown (3,518
chars) instead.

Run: mise exec -- .venv/bin/python3 scripts/load_england_silver_sample.py
"""

from __future__ import annotations

import hashlib

import dlt

from dlt_sources.common.destinations_cianfhoghlaim import get_dlt_destination
from dlt_sources.filesystem.lc6_cross_check import _load_baml


def main() -> int:
    dest = get_dlt_destination(use_ducklake=True)

    bronze = dlt.pipeline(
        pipeline_name="england_curriculum",
        destination=dest,
        dataset_name="cianfhoghlaim.bronze.england_curriculum",
    )
    with bronze.sql_client() as client:
        (markdown,) = next(
            iter(
                client.execute_sql(
                    "SELECT markdown FROM ocr_pages WHERE url LIKE '%mathematics-j560%'"
                )
            )
        )

    b = _load_baml()
    if b is None:
        print("baml_client unavailable")
        return 1

    from baml_client.baml_client import types

    print(f"extracting from {len(markdown)} chars of real OCR GCSE Maths spec page content")
    try:
        spec = b.ExtractUKQualSpec(
            markdown[:30_000], types.ExamBoard.OCR, "mathematics", "GCSE"
        )
    except Exception as e:  # noqa: BLE001
        print("primary extraction failed:", str(e)[:400])
        return 1

    row = {
        "id": hashlib.sha256(b"england:ocr:gcse-mathematics-j560").hexdigest()[:16],
        "board": "OCR",
        "qualification_level": "GCSE",
        "source_url": "https://www.ocr.org.uk/qualifications/gcse/mathematics-j560-from-2015/specification-at-a-glance/",
        "spec_code": getattr(spec, "specification_code", None),
        "total_marks": getattr(spec, "total_marks", None),
        "subject": getattr(spec, "subject", None),
        "status": "primary_only",
    }
    print(row)

    silver = dlt.pipeline(
        pipeline_name="england_silver_sample",
        destination=dest,
        dataset_name="cianfhoghlaim.silver.england_curriculum_extracted",
    )
    load_info = silver.run(
        [row], table_name="qual_spec_extractions", write_disposition="merge", primary_key="id"
    )
    print(load_info)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
