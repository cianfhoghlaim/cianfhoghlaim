"""Land the Ireland NCCA/examinations.ie local-scrape-cache corpus into
the local DuckLake bronze layer.

Per the local-lakehouse plan's Phase 4
(/Users/cianmacandeisigh/.claude/plans/after-recent-plans-and-enumerated-cosmos.md):
unlock the ~15,800-file cache at stedding/site_scrape_samples/ that
Phase 1's STEDDING_INGEST_QUEUE fix made reachable. `leaving_cert_source()`
(dlt_sources/british_isles/ireland/education/leaving_cert.py) already reads
this cache correctly for the 7 priority Leaving Cert subjects (mathematics,
irish, biology, french, history, business, construction-studies) via 4
resources (syllabus, past_papers, marking_schemes, examiner_reports) —
confirmed live: 237 syllabus + 74 exam-materials records, all
cache-sourced, zero network calls.

This is a deliberately separate bronze stream from Phase 3's
`leaving_certificate/<subject>/{en,ga}/` local-PDF corpus and from
`ireland_jurisdiction_pipeline.py`'s registry-metadata-only stream — it
answers a different question (what does the existing NCCA/examinations.ie
site-scrape cache already contain for these subjects).

Run: mise exec -- .venv/bin/python3 scripts/load_ireland_ncca_cache.py
"""

from __future__ import annotations

import dlt

from dlt_sources.british_isles.ireland.education.leaving_cert import (
    leaving_cert_source,
)
from dlt_sources.common.destinations_cianfhoghlaim import get_dlt_destination


def main() -> int:
    pipeline = dlt.pipeline(
        pipeline_name="ireland_ncca_cache",
        destination=get_dlt_destination(use_ducklake=True),
        dataset_name="cianfhoghlaim.bronze.ireland_ncca_cache",
    )
    load_info = pipeline.run(leaving_cert_source())
    print(load_info)
    with pipeline.sql_client() as client:
        for resource in ("syllabus", "past_papers", "marking_schemes", "examiner_reports"):
            try:
                rows = list(
                    client.execute_sql(
                        f"SELECT subject, COUNT(*) AS n FROM {resource} "
                        "GROUP BY subject ORDER BY subject"
                    )
                )
            except Exception as e:  # table may not exist if a resource yielded 0 rows
                print(f"{resource}: (no table — {e})")
                continue
            print(f"=== {resource} ===")
            for row in rows:
                print(row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
