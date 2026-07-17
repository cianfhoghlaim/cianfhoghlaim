"""Garage S3 PDF-arrival sensor — BIEP v3 P1 hardening.

Polls the canonical cianfhoghlaim Garage S3 bucket for new PDF
arrivals in the per-jurisdiction per-stage per-subject prefixes.
"""
from __future__ import annotations

import logging
from typing import Any

from dagster import (
    RunRequest,
    SensorEvaluationContext,
    SkipReason,
    sensor,
)

logger = logging.getLogger(__name__)


GARAGE_BUCKET_URL = "s3://garage/cianfhoghlaim"

# The 8 BIEP v3 jurisdiction prefixes (one per jurisdiction + stage)
BIEP_V3_PREFIXES = [
    "ireland/lc", "ireland/jc", "ireland/jc_short_course", "ireland/jc_cba",
    "england/gcse", "england/a_level",
    "scotland/national_5", "scotland/higher", "scotland/adv_higher",
    "wales/gcse", "wales/a_level",
    "northern_ireland/gcse", "northern_ireland/a_level",
    "jersey/gcse", "jersey/a_level", "jersey/ib", "jersey/french_bac",
    "guernsey/gcse", "guernsey/a_level", "guernsey/btec", "guernsey/ib",
    "isle_of_man/gcse", "isle_of_man/a_level", "isle_of_man/btec", "isle_of_man/ib",
]


@sensor(
    job_name="garage_pdf_arrival_job",
    description="Poll Garage S3 for new PDF arrivals in the BIEP v3 prefixes.",
    minimum_interval_seconds=300,
)
def garage_pdf_arrival_sensor(context: SensorEvaluationContext) -> Any:
    cursor_data: dict[str, Any] = {}
    if context.cursor:
        try:
            cursor_data = json.loads(context.cursor)
        except Exception:
            cursor_data = {}
    seen_etags: dict[str, str] = cursor_data.get("etags", {})

    try:
        import boto3  # type: ignore[import-not-found]
        s3 = boto3.client("s3")
    except ImportError:
        return SkipReason("boto3 not installed")

    new_runs = []
    for prefix in BIEP_V3_PREFIXES:
        try:
            resp = s3.list_objects_v2(
                Bucket="garage",
                Prefix=f"cianfhoghlaim/{prefix}/",
            )
        except Exception as e:
            logger.warning(f"garage_pdf_arrival: list failed for {prefix}: {e}")
            continue

        for obj in resp.get("Contents", []):
            key = obj["Key"]
            etag = obj["ETag"]
            if seen_etags.get(key) != etag:
                seen_etags[key] = etag
                new_runs.append(RunRequest(
                    run_key=f"pdf_{key}_{etag}",
                    tags={
                        "s3_key": key,
                        "etag": etag,
                        "prefix": prefix,
                    },
                ))

    context.update_cursor(json.dumps({"etags": seen_etags}))
    if new_runs:
        return new_runs
    return SkipReason("No new PDF arrivals in Garage S3 since last poll.")
