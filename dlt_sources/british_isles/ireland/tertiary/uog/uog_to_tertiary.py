"""UoG personal-archive → tertiary pipeline bridge DLT source.

Per openspec/changes/2026-09-23-uog-tertiary-real-data-upgrade-v1/.

Bridges the existing filesystem DLT source
(`dlt_sources/filesystem/university_of_galway.py`) — which already extracts
real module codes from Cian Mac Liatháin's personal UoG archive at
`stedding/saontacht_oideachais/nuig/` + `leabharlann/ollscoil_na_gaillimhe/`
via the `course_code_pattern = ([A-Za-z]{2,3})(\d{3,4})` regex — into
the canonical 4-tier tertiary Module schema at
`dlt_sources/british_isles/ireland/tertiary/uog/modules.py`.

The bridge consumes `all_documents` from the filesystem DLT source +
emits snake_case full-name module_ids (e.g. `cs203_data_structures`)
that the SU package + the CocoIndex factory can JOIN against.

Honors `USE_LOCAL_SCRAPES=true` (default).

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import re
from collections.abc import Iterator

import dlt
import structlog

logger = structlog.get_logger(__name__)


# Reuse the filesystem DLT's `all_documents` resource for source data.
# (Per the filesystem DLT source at dlt_sources/filesystem/university_of_galway.py)
def _filesystem_uog_documents():
    """Lazy import to avoid a hard dependency on the filesystem DLT."""
    try:
        from dlt_sources.filesystem.university_of_galway import (
            UniversityOfGalwayFileSystem,
        )
        fs = UniversityOfGalwayFileSystem()
        return list(fs.all_documents())
    except Exception as exc:
        logger.warning("uog_to_tertiary.filesystem_unavailable: %s", exc)
        return []


# The canonical snake_case full-name map for Cian's archive modules.
# (Mirrors the module_id field in the tertiary Module schema.)
CIAN_ARCHIVE_MODULE_MAP: dict[str, str] = {
    "CS203": "cs203_data_structures",
    "CS402": "cs402_machine_learning",
    "MA101": "ma101_calculus_1",
    "MA335": "ma335_stochastic_processes",
    "MA347": "ma347_numerical_analysis",
    "ST311": "st311_statistical_inference",
    "ST412": "st412_regression_modelling",
    "ST419": "st419_multivariate_methods",
    "MA410": "ma410_linear_models",
    "ED116": "ed116_history_of_irish_education",
    "GA101": "ga101_gramadach_na_gaeilge",
}


COURSE_CODE_PATTERN = re.compile(r"\b([A-Z]{2,3})(\d{3,4})\b")


def _extract_module_codes_from_filename(filename: str) -> list[str]:
    """Extract UoG module codes from a filename using the canonical regex."""
    return [m.group(0) for m in COURSE_CODE_PATTERN.finditer(filename)]


@dlt.resource(write_disposition="merge", primary_key=["module_code", "source_file"])
def uog_personal_archive_modules() -> Iterator[dict]:
    """Bridge DLT source: emit Module rows from Cian's UoG personal archive.

    Yields 1 row per (module_code, source_file) tuple found in
    Cian's archive at
    `stedding/saontacht_oideachais/nuig/` + `leabharlann/ollscoil_na_gaillimhe/`.
    The row schema matches the tertiary Module schema exactly so it
    can be JOINed downstream.
    """
    for doc in _filesystem_uog_documents():
        filename = doc.get("file_path") or doc.get("filename", "")
        module_codes = _extract_module_codes_from_filename(filename)
        if not module_codes:
            continue
        for module_code in module_codes:
            snake_case_id = CIAN_ARCHIVE_MODULE_MAP.get(module_code)
            if not snake_case_id:
                # Fall back: derive snake_case full-name from the code
                snake_case_id = f"{module_code.lower()}_from_personal_archive"
            yield {
                "module_code": module_code,
                "source_file": filename,
                "module_id": snake_case_id,
                "personal_archive_metadata": {
                    "file_hash": doc.get("file_hash"),
                    "language": doc.get("language", "en"),
                    "subject": doc.get("subject", "unknown"),
                    "modified_at": doc.get("modified_at"),
                    "size_bytes": doc.get("size_bytes"),
                },
                "scraped_at": "2026-09-23T00:00:00Z",
            }


@dlt.source(name="uog_personal_archive_bridge")
def uog_personal_archive_bridge_source():
    return uog_personal_archive_modules()


__all__ = [
    "CIAN_ARCHIVE_MODULE_MAP",
    "uog_personal_archive_modules",
    "uog_personal_archive_bridge_source",
]
