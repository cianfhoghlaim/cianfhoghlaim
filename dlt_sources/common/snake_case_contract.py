"""
Snake_case file naming + metadata sidecar contract for BIEP v3.

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change,
every BIEP v3 PDF and metadata sidecar MUST land at the canonical
snake_case path:

    s3://garage/cianfhoghlaim/<jurisdiction>/<stage>/<subject_slug>/<language>/<year_or_undated>/<jurisdiction>__<stage>__<subject_slug>__<board_or_na>__<qual_level_or_untiered>__<language>__<year_or_undated>__<sha256[0:8]>.pdf

with a sibling `<file>.meta.json` sidecar carrying the 13 metadata fields:
    source_id, jurisdiction, stage, subject_slug, board, qualification_level,
    language, year, source_url, crawled_at, byte_size, page_count,
    content_hash_sha256, publisher.

The full path MUST match the regex:
    ^[a-z0-9_]+/[a-z0-9_]+/[a-z0-9_]+/[a-z0-9_]+/[a-z0-9_]+/[a-z0-9_]+__[a-z0-9_]+__[a-z0-9_]+__[a-z0-9_]+__[a-z0-9_]+__[a-z0-9_]+__[a-z0-9_]+__[a-f0-9]{8}\\.pdf$
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ----------------------------------------------------------------------------
# Canonical snake_case filename regex
# ----------------------------------------------------------------------------
# Format: <jurisdiction>__<stage>__<subject_slug>__<board_or_na>__<qual_level_or_untiered>__<language>__<year_or_undated>__<sha256[0:8]>.pdf
#
# - All tokens are lowercase snake_case
# - year_or_undated is either a 4-digit year (2017-2027) or "undated"
# - sha256[0:8] is 8 lowercase hex characters
# - All separators are double underscores between tokens

SNAKE_CASE_FILENAME_REGEX = re.compile(
    r"^[a-z0-9_]+__[a-z0-9_]+__[a-z0-9_]+__[a-z0-9_]+__[a-z0-9_]+__[a-z0-9_]+__[a-z0-9_]+__[a-f0-9]{8}\.pdf$"
)

SNAKE_CASE_BUCKET_PATH_REGEX = re.compile(
    r"^[a-z0-9_]+/[a-z0-9_]+/[a-z0-9_]+/[a-z0-9_]+/[a-z0-9_]+/"
    r"[a-z0-9_]+__[a-z0-9_]+__[a-z0-9_]+__[a-z0-9_]+__[a-z0-9_]+__[a-z0-9_]+__[a-z0-9_]+__[a-f0-9]{8}\.pdf$"
)

# ----------------------------------------------------------------------------
# Token validation
# ----------------------------------------------------------------------------

VALID_JURISDICTIONS = {"ireland", "england", "scotland", "wales", "northern_ireland", "jersey", "guernsey", "isle_of_man"}
VALID_LANGUAGES = {"en", "ga", "gd", "cy", "gv", "kw", "br"}
VALID_STAGES = {"leaving_cycle", "junior_cycle", "primary", "earliest_childhood", "a_level", "gcse"}
VALID_QUAL_LEVELS = {"higher", "ordinary", "foundation", "gcse", "a_level", "untiered", "as_level"}


def _is_valid_token(token: str, valid_set: set[str]) -> bool:
    """Validate that a token is a snake_case slug in the valid set."""
    if not token or not isinstance(token, str):
        return False
    return token in valid_set


def _is_year_or_undated(token: str) -> bool:
    """Validate that a token is either a 4-digit year (2017-2027) or "undated"."""
    if token == "undated":
        return True
    if token.isdigit() and len(token) == 4:
        year = int(token)
        return 2017 <= year <= 2027
    return False


def _is_sha256_8(token: str) -> bool:
    """Validate that a token is an 8-character lowercase hex string."""
    if not token or len(token) != 8:
        return False
    try:
        int(token, 16)
        return True
    except ValueError:
        return False


# ----------------------------------------------------------------------------
# Canonical filename construction
# ----------------------------------------------------------------------------


@dataclass
class CohortAttributes:
    """Canonical attributes for a BIEP v3 cohort PDF."""

    jurisdiction: str
    stage: str
    subject_slug: str
    board: str = "na"
    qualification_level: str = "untiered"
    language: str = "en"
    year: int | str = "undated"  # 2017-2027 or "undated"

    def __post_init__(self) -> None:
        # Validate the 6 tokens
        if not _is_valid_token(self.jurisdiction, VALID_JURISDICTIONS):
            raise ValueError(f"Invalid jurisdiction: {self.jurisdiction!r}")
        if not _is_valid_token(self.stage, VALID_STAGES):
            raise ValueError(f"Invalid stage: {self.stage!r}")
        if not self.subject_slug or not re.match(r"^[a-z0-9_]+$", self.subject_slug):
            raise ValueError(f"Invalid subject_slug: {self.subject_slug!r}")
        if not _is_valid_token(self.language, VALID_LANGUAGES):
            raise ValueError(f"Invalid language: {self.language!r}")
        if not _is_valid_token(self.qualification_level, VALID_QUAL_LEVELS):
            raise ValueError(f"Invalid qualification_level: {self.qualification_level!r}")

    def to_filename_tokens(self) -> list[str]:
        """Return the 7 tokens (without the sha256 + .pdf suffix)."""
        return [
            self.jurisdiction,
            self.stage,
            self.subject_slug,
            self.board,
            self.qualification_level,
            self.language,
            str(self.year) if isinstance(self.year, int) else self.year,
        ]


def derive_sha256_8(content: bytes) -> str:
    """Derive the 8-character lowercase hex SHA256 prefix."""
    return hashlib.sha256(content).hexdigest()[:8]


def build_pdf_filename(cohort: CohortAttributes, content_sha256_8: str) -> str:
    """Build the canonical snake_case PDF filename.

    Example:
        >>> build_pdf_filename(
        ...     CohortAttributes(
        ...         jurisdiction="ireland",
        ...         stage="leaving_cycle",
        ...         subject_slug="mathematics",
        ...         qualification_level="higher",
        ...         language="en",
        ...         year=2024,
        ...     ),
        ...     "a1b2c3d4",
        ... )
        'ireland__leaving_cycle__mathematics__na__higher__en__2024__a1b2c3d4.pdf'
    """
    if not _is_sha256_8(content_sha256_8):
        raise ValueError(f"Invalid SHA256 prefix: {content_sha256_8!r}")
    tokens = cohort.to_filename_tokens()
    tokens.append(content_sha256_8)
    return "__".join(tokens) + ".pdf"


def build_s3_path(cohort: CohortAttributes, content_sha256_8: str) -> str:
    """Build the canonical S3 bucket path.

    Example:
        >>> build_s3_path(
        ...     CohortAttributes(
        ...         jurisdiction="ireland",
        ...         stage="leaving_cycle",
        ...         subject_slug="mathematics",
        ...         qualification_level="higher",
        ...         language="en",
        ...         year=2024,
        ...     ),
        ...     "a1b2c3d4",
        ... )
        's3://garage/cianfhoghlaim/ireland/leaving_cycle/mathematics/en/2024/ireland__leaving_cycle__mathematics__na__higher__en__2024__a1b2c3d4.pdf'
    """
    filename = build_pdf_filename(cohort, content_sha256_8)
    bucket_prefix = (
        f"s3://garage/cianfhoghlaim/"
        f"{cohort.jurisdiction}/{cohort.stage}/{cohort.subject_slug}/{cohort.language}/{cohort.year}"
    )
    return f"{bucket_prefix}/{filename}"


# ----------------------------------------------------------------------------
# Metadata sidecar contract
# ----------------------------------------------------------------------------


@dataclass
class CohortMetadata:
    """The 13 metadata fields for the sibling `<file>.meta.json` sidecar."""

    source_id: str
    jurisdiction: str
    stage: str
    subject_slug: str
    board: str
    qualification_level: str
    language: str
    year: int | str
    source_url: str
    crawled_at: str  # ISO 8601 timestamp
    byte_size: int
    page_count: int
    content_hash_sha256: str
    publisher: str

    def to_dict(self) -> dict[str, Any]:
        """Return the dict representation (JSON-serialisable)."""
        return asdict(self)


def build_meta_json(cohort: CohortAttributes, source_url: str, byte_size: int, page_count: int, content_hash_sha256: str, publisher: str) -> CohortMetadata:
    """Build the canonical metadata sidecar for a cohort PDF.

    The `source_id` is the canonical cross-region-pipeline source_id shape:
    `<region>.<jurisdiction>.<domain>.<source_slug>`.

    The `crawled_at` is the current UTC ISO 8601 timestamp.
    """
    # BIEP v3 jurisdiction pipelines are always in the `british_isles` region;
    # the domain is `education`; the source_slug is
    # `<jurisdiction>_<stage>_<board>_<subject>`.
    source_slug = f"{cohort.jurisdiction}_{cohort.stage}_{cohort.board}_{cohort.subject_slug}"
    source_id = f"british_isles.{cohort.jurisdiction}.education.{source_slug}"
    return CohortMetadata(
        source_id=source_id,
        jurisdiction=cohort.jurisdiction,
        stage=cohort.stage,
        subject_slug=cohort.subject_slug,
        board=cohort.board,
        qualification_level=cohort.qualification_level,
        language=cohort.language,
        year=cohort.year,
        source_url=source_url,
        crawled_at=datetime.now(timezone.utc).isoformat(),
        byte_size=byte_size,
        page_count=page_count,
        content_hash_sha256=content_hash_sha256,
        publisher=publisher,
    )


# ----------------------------------------------------------------------------
# Validation
# ----------------------------------------------------------------------------


def validate_pdf_filename(filename: str) -> bool:
    """Validate that a filename matches the canonical snake_case pattern."""
    return bool(SNAKE_CASE_FILENAME_REGEX.match(filename))


def validate_s3_path(s3_path: str) -> bool:
    """Validate that an S3 path matches the canonical snake_case pattern."""
    return bool(SNAKE_CASE_BUCKET_PATH_REGEX.match(s3_path))


def parse_pdf_filename(filename: str) -> CohortAttributes | None:
    """Parse a canonical snake_case PDF filename into a CohortAttributes.

    Returns None if the filename doesn't match the canonical pattern.
    """
    if not validate_pdf_filename(filename):
        return None
    stem = filename[:-4]  # strip .pdf
    tokens = stem.split("__")
    if len(tokens) != 8:
        return None
    # drop the SHA256 token
    cohort_tokens = tokens[:7]
    return CohortAttributes(
        jurisdiction=cohort_tokens[0],
        stage=cohort_tokens[1],
        subject_slug=cohort_tokens[2],
        board=cohort_tokens[3],
        qualification_level=cohort_tokens[4],
        language=cohort_tokens[5],
        year=int(cohort_tokens[6]) if cohort_tokens[6].isdigit() else cohort_tokens[6],
    )


__all__ = [
    "SNAKE_CASE_FILENAME_REGEX",
    "SNAKE_CASE_BUCKET_PATH_REGEX",
    "VALID_JURISDICTIONS",
    "VALID_LANGUAGES",
    "VALID_STAGES",
    "VALID_QUAL_LEVELS",
    "CohortAttributes",
    "CohortMetadata",
    "derive_sha256_8",
    "build_pdf_filename",
    "build_s3_path",
    "build_meta_json",
    "validate_pdf_filename",
    "validate_s3_path",
    "parse_pdf_filename",
]
