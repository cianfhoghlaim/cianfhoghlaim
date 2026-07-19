#!/usr/bin/env python3
"""Run all 8 BIEP v3 jurisdiction pipelines end-to-end.

Per the 2026-08-13 BIEP v3 lakehouse full activation plan (Phase 2).

For each of the 8 jurisdictions, this script:
1. Instantiates the corresponding jurisdiction pipeline class
2. Iterates the resource to collect all cohort rows
3. Loads them into DuckLake via `pipeline.run(...)`

Writes to `s3://ducklake-cianfhoghlaim/{namespace}/{dataset}/...`
via local Postgres-backed DuckLake + Garage S3.
"""
from __future__ import annotations

import json
import os
import sys
import time

import dlt

# Import all 4 pipeline classes
from dlt_sources.british_isles.ireland.education.ireland_jurisdiction_pipeline import (
    IrelandJurisdictionPipeline,
)
from dlt_sources.british_isles.england.education.england_jurisdiction_pipeline import (
    EnglandJurisdictionPipeline,
)
from dlt_sources.british_isles.sct_wls_ni.education.sct_wls_ni_jurisdiction_pipeline import (
    SctWlsNiJurisdictionPipeline,
)
from dlt_sources.british_isles.crown_dependencies.education.crown_dependencies_jurisdiction_pipeline import (
    CrownDependenciesJurisdictionPipeline,
)


PIPELINES = [
    ("ireland", IrelandJurisdictionPipeline("ireland")),
    ("england", EnglandJurisdictionPipeline("england")),
    ("scotland", SctWlsNiJurisdictionPipeline("scotland")),
    ("wales", SctWlsNiJurisdictionPipeline("wales")),
    ("northern_ireland", SctWlsNiJurisdictionPipeline("northern_ireland")),
    ("jersey", CrownDependenciesJurisdictionPipeline("jersey")),
    ("guernsey", CrownDependenciesJurisdictionPipeline("guernsey")),
    ("isle_of_man", CrownDependenciesJurisdictionPipeline("isle_of_man")),
]


def run_one(jurisdiction: str, pipeline) -> dict:
    """Run one pipeline; return load summary dict."""
    t0 = time.time()
    rows = list(pipeline.build_pipeline_resource())
    n_rows = len(rows)
    if n_rows == 0:
        print(f"  [{jurisdiction}] no rows in registry")
        return {"jurisdiction": jurisdiction, "rows": 0, "duration_s": 0}

    pipeline_obj = pipeline.build_pipeline()

    @dlt.resource(
        name=f"{jurisdiction}_subjects",
        write_disposition="merge",
        primary_key=["content_hash"],
    )
    def resource():
        for row in rows:
            yield row

    load_info = pipeline_obj.run(resource())
    duration = time.time() - t0
    n_packages = len(load_info.load_packages) if load_info.load_packages else 0
    print(f"  [{jurisdiction}] {n_rows} rows in {duration:.1f}s → {n_packages} package(s) loaded")
    return {"jurisdiction": jurisdiction, "rows": n_rows, "duration_s": duration}


def main() -> int:
    t_total = time.time()
    results = []
    for j, p in PIPELINES:
        try:
            results.append(run_one(j, p))
        except Exception as e:
            print(f"  [{j}] ERROR: {e}")
            results.append({"jurisdiction": j, "rows": 0, "error": str(e)})

    print()
    print("=" * 60)
    print(f"Total: {sum(r['rows'] for r in results)} rows across {len(results)} jurisdictions in {time.time()-t_total:.1f}s")
    print("=" * 60)
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())