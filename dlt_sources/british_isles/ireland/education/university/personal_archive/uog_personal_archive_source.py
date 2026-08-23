"""Transferable personal-archive DLT factory.

Wraps `dlt_sources.filesystem.uog_personal_archive.uog_personal_archive_source`
in a parameterised factory that runs against **any** student's
`leabharlann/<university>/` directory.

The 9 fields of `UniversityPersonalArchiveConfig` mirror the
9 `UNIVERSITY_PERSONAL_ARCHIVE_*` + `DUCKLAKE_DESTINATION` env vars
in `.env.example`:

- `personal_archive_path` (UNIVERSITY_PERSONAL_ARCHIVE_PATH)
- `registry_url` (UNIVERSITY_REGISTRY_URL)
- `university_name` (UNIVERSITY_NAME)
- `institution_id` (UNIVERSITY_INSTITUTION_ID)
- `programme_code_regex` (UNIVERSITY_PROGRAMME_CODE_REGEX)
- `transcript_file_patterns` (UNIVERSITY_TRANSCRIPT_FILE_PATTERNS)
- `assignment_file_pattern` (UNIVERSITY_ASSIGNMENT_FILE_PATTERN)
- `lecture_notes_dir_pattern` (UNIVERSITY_LECTURE_NOTES_DIR_PATTERN)
- `ducklake_destination` (DUCKLAKE_DESTINATION)

The case study (UoG) is provided as a pre-baked config at
`uog_personal_archive_case_study()` so existing callers can keep
using the canonical factory name.

Reference: openspec/changes/2026-08-23-uog-personal-archive-tertiary-modules-v1/
            specs/cianfhoghlaim-personal-archive-typed-modules/spec.md
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

import dlt
import structlog

logger = structlog.get_logger(__name__)


class UniversityPersonalArchiveConfig(BaseModel):
    """The 9-field Pydantic v2 config for the personal-archive factory.

    Mirrors the 9 env vars in `.env.example`. Any future student
    (any future university) can pass a config like:

        UniversityPersonalArchiveConfig(
            personal_archive_path=Path("/home/alice/leabharlann/ucd"),
            registry_url="https://www.ucd.ie",
            university_name="University College Dublin",
            institution_id="ie-ucd",
            programme_code_regex=r"[A-Z]{2,3}\\d{3,4}",
            transcript_file_patterns=("*transcript*.pdf",),
            assignment_file_pattern="*assignment*.pdf",
            lecture_notes_dir_pattern="*Lectures*",
            ducklake_destination="motherduck",
        )
    """

    personal_archive_path: Path = Field(
        default_factory=lambda: Path(
            os.environ.get(
                "UNIVERSITY_PERSONAL_ARCHIVE_PATH",
                "leabharlann/ollscoil_na_gaillimhe",
            )
        ),
        description="Root directory to walk (the student's personal archive).",
    )
    registry_url: str = Field(
        default_factory=lambda: os.environ.get(
            "UNIVERSITY_REGISTRY_URL", "https://www.universityofgalway.ie"
        ),
        description="Canonical registry URL of the university.",
    )
    university_name: str = Field(
        default_factory=lambda: os.environ.get("UNIVERSITY_NAME", "University of Galway"),
        description="Canonical full university name.",
    )
    institution_id: str = Field(
        default_factory=lambda: os.environ.get(
            "UNIVERSITY_INSTITUTION_ID", "ie-university-galway"
        ),
        description="Kebab-case institution id, e.g. 'ie-university-galway'.",
    )
    programme_code_regex: str = Field(
        default_factory=lambda: os.environ.get(
            "UNIVERSITY_PROGRAMME_CODE_REGEX", r"[A-Za-z]{2,3}\d{3,4}"
        ),
        description="Regex matching module codes (e.g. 'CT511', 'MA335').",
    )
    transcript_file_patterns: tuple[str, ...] = Field(
        default_factory=lambda: tuple(
            os.environ.get(
                "UNIVERSITY_TRANSCRIPT_FILE_PATTERNS", "*transcript*.pdf"
            ).split(",")
        ),
        description="Glob patterns that match transcript PDFs (comma-separated).",
    )
    assignment_file_pattern: str = Field(
        default_factory=lambda: os.environ.get(
            "UNIVERSITY_ASSIGNMENT_FILE_PATTERN", "*assignment*.pdf"
        ),
        description="Glob pattern that matches assignment artefacts.",
    )
    lecture_notes_dir_pattern: str = Field(
        default_factory=lambda: os.environ.get(
            "UNIVERSITY_LECTURE_NOTES_DIR_PATTERN", "*Lectures*"
        ),
        description="Glob pattern that matches the lecture-notes directory.",
    )
    ducklake_destination: str = Field(
        default_factory=lambda: os.environ.get("DUCKLAKE_DESTINATION", "local"),
        description="One of 'local', 'motherduck', 'bonneagar'.",
    )

    class Config:
        """Pydantic v2 model config."""

        arbitrary_types_allowed = True


def personal_archive_source(
    university_config: UniversityPersonalArchiveConfig,
    student_id: str | None = None,
) -> Any:
    """Build a DLT source for the given university personal-archive config.

    Args:
        university_config: The 9-field config.
        student_id: Optional kebab-case student id used in
            ``student_transcripts``. Defaults to the institution id.

    Returns:
        A `@dlt.source(...)` with 8 resources, parameterised on the
        given config (the same source as the UoG case study, but
        with the institution_id + paths overridden).
    """
    try:
        from dlt_sources.filesystem.uog_personal_archive import (
            uog_personal_archive_source as _underlying,
        )
    except ImportError as exc:  # pragma: no cover — defensive
        raise ImportError(
            "dlt_sources.filesystem.uog_personal_archive is not importable; "
            "the personal-archive pipeline cannot start."
        ) from exc

    logger.info(
        "personal_archive_source_build",
        institution_id=university_config.institution_id,
        university_name=university_config.university_name,
        destination=university_config.ducklake_destination,
        programme_code_regex=university_config.programme_code_regex,
    )

    # Validate the programme code regex compiles.
    try:
        re.compile(university_config.programme_code_regex)
    except re.error as exc:
        raise ValueError(
            f"Invalid programme_code_regex {university_config.programme_code_regex!r}: {exc}"
        ) from exc

    effective_student_id = student_id or university_config.institution_id

    source = _underlying(
        base_path=university_config.personal_archive_path,
        destination=university_config.ducklake_destination,
        student_id=effective_student_id,
        include_transcripts=True,
    )

    # Stamp the per-institution metadata on the source object so the
    # marimo notebook + the cognify pass can distinguish per-institution
    # runs without re-reading every row. The dlt Source's `name`
    # property reads from `self._schema.name` (per dlt 1.x), so we
    # attach the metadata as plain attributes for downstream consumers.
    setattr(source, "institution_id", university_config.institution_id)
    setattr(source, "university_name", university_config.university_name)
    setattr(source, "registry_url", university_config.registry_url)
    setattr(source, "ducklake_destination", university_config.ducklake_destination)
    setattr(source, "student_id", effective_student_id)

    return source


def uog_personal_archive_case_study() -> Any:
    """The canonical UoG case-study config (the pre-baked default).

    Equivalent to:

        personal_archive_source(UniversityPersonalArchiveConfig())
    """
    return personal_archive_source(UniversityPersonalArchiveConfig())


__all__ = [
    "UniversityPersonalArchiveConfig",
    "personal_archive_source",
    "uog_personal_archive_case_study",
]
