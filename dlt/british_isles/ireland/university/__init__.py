"""
Ireland Tertiary (18+) University DLT source package.

The 5 DLT sources in this package cover the **Tertiary 18+** stage of
the K-12 → university pipeline:

  - `universities.py`  — the **8 universities** (TCD, UCD, UCC, UoG,
                                  UL, DCU, Maynooth, RCSI)
  - `tus.py`           — the **5 Technological Universities** (TUD,
                                  MTU, TUS, ATU, SETU)
  - `qqi_awards.py`    — the **QQI awards** at NFQ 6-10
  - `cao.py`           — the **CAO** Central Applications Office
  - `solas.py`         — the **SOLAS** Further Education + Training
                                  Authority

All 5 sources follow the BIEP v1 DLT pattern (per `ncca.py` from
commit `9e97ca0ca` + `primary_jc_combined.py` from the
`2026-07-14-ireland-primary-jc-dlt-baml-v1` dispatch):

  - `@dlt.resource(name="tertiary_<area>", write_disposition="merge",
                  primary_key=["url"|"<id>"])`
  - structlog observability
  - honors `USE_LOCAL_SCRAPES=true` (default)
  - registry tables ship Phase 1 rows; Phase 2 layer BAML-extracted
    rows on top from `/stedding/ingest_queue/university/<area>/`.

Together with the upstream packages:

  - `primary.py` + `junior_cycle.py`        ← `ireland-primary-jc-dlt-baml`
  - `ncca.py` + `examinations.py`           ← `british-isles-education-pipeline`

the 5 sources here complete the full **K-12 → university** pipeline
(NFQ 1-10) for the Republic of Ireland. Northern Ireland, Scotland,
Wales, England are out of scope (covered by the sister
`dlt/british_isles/<nation>/` packages).

Cross-references:
  - `openspec/specs/oideachais-university-deep-extraction/spec.md`
  - `openspec/changes/2026-07-15-oideachais-university-deep-extraction-v1/`
  - `cianfhoghlaim/baml/education/university/university_extraction.baml`
    (the 5+ Pydantic classes + 4+ enums + 1+ function for Tertiary)
  - `cianfhoghlaim/orchestration/defs/1_ingestion/university/defs.yaml`
    (the daily 06:00 UTC cron asset for all 5 sources)
"""

from __future__ import annotations

from .cao import (
    CAO_CACHE_DIR,
    CAO_ROUNDS,
    create_ireland_tertiary_cao_pipeline,
    ireland_tertiary_cao_source,
    tertiary_cao_application_rounds,
    tertiary_cao_courses,
)
from .qqi_awards import (
    QQI_AWARD_CATALOG,
    QQI_CACHE_DIR,
    QQI_LEVELS,
    create_ireland_tertiary_qqi_pipeline,
    ireland_tertiary_qqi_source,
    tertiary_qqi_awards,
    tertiary_qqi_providers,
)
from .solas import (
    SOLAS_CACHE_DIR,
    SOLAS_ETBS,
    create_ireland_tertiary_solas_pipeline,
    ireland_tertiary_solas_source,
    tertiary_solas_apprenticeships,
    tertiary_solas_courses,
)
from .tus import (
    TU_CACHE_DIR,
    TU_INSTITUTIONS,
    create_ireland_tertiary_tus_pipeline,
    ireland_tertiary_tus_source,
    tertiary_tu_campuses,
    tertiary_tus,
)
from .universities import (
    UNIVERSITY_CACHE_DIR,
    UNIVERSITY_INSTITUTIONS,
    create_ireland_tertiary_universities_pipeline,
    ireland_tertiary_universities_source,
    tertiary_universities,
    tertiary_university_faculties,
)

__all__ = [
    # 8 universities (universities.py)
    "UNIVERSITY_CACHE_DIR",
    "UNIVERSITY_INSTITUTIONS",
    "create_ireland_tertiary_universities_pipeline",
    "ireland_tertiary_universities_source",
    "tertiary_universities",
    "tertiary_university_faculties",
    # 5 TUs (tus.py)
    "TU_CACHE_DIR",
    "TU_INSTITUTIONS",
    "create_ireland_tertiary_tus_pipeline",
    "ireland_tertiary_tus_source",
    "tertiary_tus",
    "tertiary_tu_campuses",
    # QQI awards (qqi_awards.py)
    "QQI_AWARD_CATALOG",
    "QQI_CACHE_DIR",
    "QQI_LEVELS",
    "create_ireland_tertiary_qqi_pipeline",
    "ireland_tertiary_qqi_source",
    "tertiary_qqi_awards",
    "tertiary_qqi_providers",
    # CAO (cao.py)
    "CAO_CACHE_DIR",
    "CAO_ROUNDS",
    "create_ireland_tertiary_cao_pipeline",
    "ireland_tertiary_cao_source",
    "tertiary_cao_application_rounds",
    "tertiary_cao_courses",
    # SOLAS (solas.py)
    "SOLAS_CACHE_DIR",
    "SOLAS_ETBS",
    "create_ireland_tertiary_solas_pipeline",
    "ireland_tertiary_solas_source",
    "tertiary_solas_apprenticeships",
    "tertiary_solas_courses",
]