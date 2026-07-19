"""
Ireland QQI Awards DLT source — Tertiary 18+ stage.

Covers **QQI (Quality and Qualifications Ireland)** awards at the
**6 NFQ levels relevant to Tertiary** (NFQ 6 — Higher Certificate →
NFQ 10 — Doctoral Degree). QQI was established under the
Qualifications and Quality Assurance (Education and Training) Act 2012
to consolidate the 4 legacy FETAC / HETAC / NQAI / IUQB bodies.

QQI Level mapping (per the Irish NFQ — National Framework of
Qualifications):

  NFQ 6  — Higher Certificate         (60 ECTS, 1 year)
  NFQ 7  — Ordinary Bachelor Degree   (180 ECTS, 3 years)
  NFQ 8  — Honours Bachelor Degree    (240 ECTS, 4 years)
  NFQ 9  — Masters Degree             (90 ECTS, 1.5 years taught)
  NFQ 10 — Doctoral Degree            (Ph.D., variable)

Note: NFQ 1-5 are pre-tertiary (the ireland-primary-jc-dlt-baml +
british-isles-education-pipeline specs cover NFQ 1-5). This source
covers NFQ 6-10 only — the **Tertiary 18+** bracket.

Honors `USE_LOCAL_SCRAPES=true` (default) to read from
`/stedding/ingest_queue/university/qqi/`; live scraping is Phase 2.

Source URLs:
  - https://www.qqi.ie
  - https://www.nfq.ie (the National Framework of Qualifications site)

Datasets produced (2 resources):
  tertiary_qqi_awards    — one row per (award_code, language)
  tertiary_qqi_providers — one row per (provider_id, language)

BAML extraction (per `baml/education/university/university_extraction.baml`):
  b.ExtractQQIAward(text, award_code) -> QQIAward
"""

from __future__ import annotations

import hashlib
import os
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import dlt
import structlog

logger = structlog.get_logger(__name__)

QQI_CACHE_DIR = Path(
    os.getenv("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue")
) / "university" / "qqi"

# Canonical NFQ 6-10 levels (Tertiary 18+).
QQI_LEVELS: tuple[str, ...] = ("NFQ_6", "NFQ_7", "NFQ_8", "NFQ_9", "NFQ_10")
"""The 5 NFQ levels for the Tertiary 18+ stage. NFQ 1-5 are pre-tertiary."""

# Award categories per QQI's awardsystem — the 14 award-types at
# Tertiary 6-10. `ects` is the canonical ECTS for the full award.
QQI_AWARD_CATALOG: tuple[dict[str, Any], ...] = (
    {
        "award_code": "NFQ6-HC",
        "award_title": "Higher Certificate",
        "qqi_level": "NFQ_6",
        "ects": 60,
        "duration_months": 12,
        "category": "certificate",
        "issuing_body": "QQI",
    },
    {
        "award_code": "NFQ7-BA",
        "award_title": "Bachelor Degree (Ordinary)",
        "qqi_level": "NFQ_7",
        "ects": 180,
        "duration_months": 36,
        "category": "degree",
        "issuing_body": "QQI",
    },
    {
        "award_code": "NFQ8-BA-HONS",
        "award_title": "Bachelor Degree (Honours)",
        "qqi_level": "NFQ_8",
        "ects": 240,
        "duration_months": 48,
        "category": "degree_hons",
        "issuing_body": "QQI",
    },
    {
        "award_code": "NFQ8-HDIP",
        "award_title": "Higher Diploma",
        "qqi_level": "NFQ_8",
        "ects": 60,
        "duration_months": 12,
        "category": "higher_diploma",
        "issuing_body": "QQI",
    },
    {
        "award_code": "NFQ8-GDIP",
        "award_title": "Graduate Diploma",
        "qqi_level": "NFQ_8",
        "ects": 60,
        "duration_months": 12,
        "category": "graduate_diploma",
        "issuing_body": "QQI",
    },
    {
        "award_code": "NFQ9-PG-CERT",
        "award_title": "Postgraduate Certificate",
        "qqi_level": "NFQ_9",
        "ects": 30,
        "duration_months": 6,
        "category": "postgrad_cert",
        "issuing_body": "QQI",
    },
    {
        "award_code": "NFQ9-PG-DIP",
        "award_title": "Postgraduate Diploma",
        "qqi_level": "NFQ_9",
        "ects": 60,
        "duration_months": 12,
        "category": "postgrad_dip",
        "issuing_body": "QQI",
    },
    {
        "award_code": "NFQ9-MASTERS",
        "award_title": "Masters Degree (taught or research)",
        "qqi_level": "NFQ_9",
        "ects": 90,
        "duration_months": 18,
        "category": "masters",
        "issuing_body": "QQI",
    },
    {
        "award_code": "NFQ10-PHD",
        "award_title": "Doctoral Degree (Ph.D., DPhil)",
        "qqi_level": "NFQ_10",
        "ects": 0,  # variable, not ECTS-anchored
        "duration_months": 48,
        "category": "doctoral",
        "issuing_body": "QQI",
    },
    {
        "award_code": "NFQ10-DPROF",
        "award_title": "Professional Doctorate (e.g. D.Ed., D.B.A.)",
        "qqi_level": "NFQ_10",
        "ects": 0,  # variable
        "duration_months": 48,
        "category": "professional_doctorate",
        "issuing_body": "QQI",
    },
)
"""The canonical 10 QQI award types at the Tertiary 18+ bracket (NFQ 6-10).

Cross-references:
  - NFQ 1-5 (pre-tertiary) — `ireland-primary-jc-dlt-baml` +
    `british-isles-education-pipeline`
  - The 8 universities + 5 TUs that issue these awards (see
    `universities.py` + `tus.py`)
"""


def _row_hash(*parts: str) -> str:
    """Deterministic SHA-256 for DLT merge keys (uniform across resources)."""
    sha = hashlib.sha256()
    sha.update("|".join(parts).encode("utf-8"))
    return sha.hexdigest()


@dlt.resource(
    name="tertiary_qqi_awards",
    write_disposition="merge",
    primary_key=["award_code", "language"],
)
def tertiary_qqi_awards() -> Iterator[dict[str, Any]]:
    """One row per (award_code, language) for QQI awards at NFQ 6-10.

    This is the **registry-of-record** view; Phase 2 will enrich with
    BAML-extracted programme details (entry requirements, etc.).
    """
    for award in QQI_AWARD_CATALOG:
        yield {
            "award_code": award["award_code"],
            "award_title": award["award_title"],
            "qqi_level": award["qqi_level"],
            "ects": award["ects"],
            "duration_months": award["duration_months"],
            "category": award["category"],
            "issuing_body": award["issuing_body"],
            "language": "en",
            "row_hash": _row_hash(award["award_code"], "en"),
            "kind": "qqi_award",
            "stage": "tertiary",
            "sector": "ie_qqi",
            "source_url": (
                f"https://www.qqi.ie/what-we-do/qualifications/"
                f"{award['award_code'].lower()}"
            ),
            "extracted_at": datetime.now(UTC).isoformat(),
            "baml_extraction_status": "registry",
        }

    if QQI_CACHE_DIR.exists():
        for json_file in sorted(QQI_CACHE_DIR.glob("**/*.json")):
            try:
                import json as _json

                rows = _json.loads(json_file.read_text())
                if isinstance(rows, dict):
                    rows = [rows]
                for row in rows:
                    if not isinstance(row, dict):
                        continue
                    row.setdefault("kind", "qqi_award")
                    row.setdefault("stage", "tertiary")
                    row.setdefault("sector", "ie_qqi")
                    row.setdefault("baml_extraction_status", "baml")
                    row.setdefault("extracted_at", datetime.now(UTC).isoformat())
                    yield row
            except (OSError, ValueError) as e:
                logger.warning(
                    "qqi_cache_read_failed",
                    path=str(json_file),
                    error=str(e),
                )


@dlt.resource(
    name="tertiary_qqi_providers",
    write_disposition="merge",
    primary_key=["provider_id", "language"],
)
def tertiary_qqi_providers() -> Iterator[dict[str, Any]]:
    """One row per QQI-registered provider.

    The 13 canonical QQI providers: 8 universities (see `universities.py`)
    + 5 TUs (see `tus.py`). This resource mirrors the union of those
    two for downstream joining.
    """
    from .universities import UNIVERSITY_INSTITUTIONS
    from .tus import TU_INSTITUTIONS

    for inst in UNIVERSITY_INSTITUTIONS:
        yield {
            "provider_id": inst["institution_id"],
            "provider_name": inst["institution_name"],
            "provider_kind": "university",
            "home_url": inst["home_url"],
            "language": inst["language"],
            "row_hash": _row_hash(inst["institution_id"], inst["language"]),
            "kind": "qqi_provider",
            "stage": "tertiary",
            "sector": "ie_qqi",
            "source_url": inst["home_url"],
            "extracted_at": datetime.now(UTC).isoformat(),
        }
    for tu in TU_INSTITUTIONS:
        yield {
            "provider_id": tu["tu_id"],
            "provider_name": tu["tu_name"],
            "provider_kind": "technological_university",
            "home_url": tu["home_url"],
            "language": tu["language"],
            "row_hash": _row_hash(tu["tu_id"], tu["language"]),
            "kind": "qqi_provider",
            "stage": "tertiary",
            "sector": "ie_qqi",
            "source_url": tu["home_url"],
            "extracted_at": datetime.now(UTC).isoformat(),
        }


@dlt.source(name="ireland_tertiary_qqi")
def ireland_tertiary_qqi_source(
    base_path: str | Path = QQI_CACHE_DIR,
) -> Iterator[Any]:
    """Ireland Tertiary (QQI awards) DLT source.

    Args:
        base_path: Local cache root (default
            `/stedding/ingest_queue/university/qqi/`).
    """
    yield tertiary_qqi_awards()
    yield tertiary_qqi_providers()


def create_ireland_tertiary_qqi_pipeline(
    destination: str = "duckdb",
    dataset_name: str = "ireland_tertiary_qqi",
) -> dlt.Pipeline:
    return dlt.pipeline(
        pipeline_name="ireland_tertiary_qqi_pipeline",
        destination=destination,
        dataset_name=dataset_name,
    )


__all__ = [
    "QQI_AWARD_CATALOG",
    "QQI_CACHE_DIR",
    "QQI_LEVELS",
    "create_ireland_tertiary_qqi_pipeline",
    "ireland_tertiary_qqi_source",
    "tertiary_qqi_awards",
    "tertiary_qqi_providers",
]