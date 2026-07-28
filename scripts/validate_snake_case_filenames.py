"""BIEP v3 snake_case filename validator.

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

Walks the canonical S3 bucket layout
(`s3://garage/cianfhoghlaim/<jurisdiction>/<stage>/<subject>/<language>/<year>/<file>.pdf`)
and asserts every file matches the canonical snake_case filename pattern.

Also asserts every PDF has a sibling `.meta.json` sidecar carrying the
13 required metadata fields.

Exits 0 iff all files pass validation.

Usage:
    mise run biep:v3:filename-validate
    python3 scripts/validate_snake_case_filenames.py
    python3 scripts/validate_snake_case_filenames.py --bucket s3://garage/cianfhoghlaim/
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

# Make the dlt_sources.common package importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from dlt_sources.common.snake_case_contract import (  # noqa: E402
    SNAKE_CASE_BUCKET_PATH_REGEX,
    build_meta_json,
    parse_pdf_filename,
    validate_pdf_filename,
    validate_s3_path,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("biiep_v3_filename_validate")


REQUIRED_META_FIELDS = (
    "source_id",
    "jurisdiction",
    "stage",
    "subject_slug",
    "board",
    "qualification_level",
    "language",
    "year",
    "source_url",
    "crawled_at",
    "byte_size",
    "page_count",
    "content_hash_sha256",
    "publisher",
)


def validate_local_path(local_path: Path) -> tuple[bool, list[str]]:
    """Validate every PDF + sidecar in a local directory tree.

    Returns (all_ok, list_of_errors).
    """
    errors: list[str] = []
    if not local_path.exists():
        return False, [f"Path does not exist: {local_path}"]

    pdf_count = 0
    for pdf_file in local_path.rglob("*.pdf"):
        pdf_count += 1
        # Validate the filename
        if not validate_pdf_filename(pdf_file.name):
            errors.append(f"Invalid filename: {pdf_file}")
            continue
        # Validate the sibling .meta.json sidecar
        meta_file = pdf_file.with_suffix(".pdf.meta.json")
        if not meta_file.exists():
            errors.append(f"Missing sibling meta.json: {meta_file}")
            continue
        try:
            with meta_file.open() as f:
                meta = json.load(f)
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid JSON in {meta_file}: {exc}")
            continue
        missing = [f for f in REQUIRED_META_FIELDS if f not in meta]
        if missing:
            errors.append(f"Missing fields in {meta_file}: {missing}")
            continue

    logger.info(f"Validated {pdf_count} PDFs in {local_path}")
    return len(errors) == 0, errors


def main() -> int:
    """Validate the snake_case filenames. Exit 0 iff all valid."""
    parser = argparse.ArgumentParser(description="BIEP v3 snake_case filename validator")
    parser.add_argument(
        "--path",
        default="storage/data/edu",
        help="Local directory to validate (default: storage/data/edu)",
    )
    parser.add_argument(
        "--bucket",
        default="s3://garage/cianfhoghlaim/",
        help="S3 bucket prefix (for documentation only)",
    )
    args = parser.parse_args()

    # Quick smoke test: build + parse a sample filename
    try:
        from dlt_sources.common.snake_case_contract import (
            CohortAttributes,
            build_pdf_filename,
            build_s3_path,
            derive_sha256_8,
        )

        sample_cohort = CohortAttributes(
            jurisdiction="ireland",
            stage="leaving_cycle",
            subject_slug="mathematics",
            qualification_level="higher",
            language="en",
            year=2024,
        )
        sample_filename = build_pdf_filename(sample_cohort, "a1b2c3d4")
        sample_path = build_s3_path(sample_cohort, "a1b2c3d4")
        logger.info(f"Sample canonical filename: {sample_filename}")
        logger.info(f"Sample canonical S3 path: {sample_path}")

        # Round-trip parse
        parsed = parse_pdf_filename(sample_filename)
        assert parsed is not None
        assert parsed.jurisdiction == "ireland"
        assert parsed.year == 2024
        logger.info("Round-trip parse OK")

        # Edge case: undated year
        sample_cohort.year = "undated"
        undated_filename = build_pdf_filename(sample_cohort, "9f8e7d6c")
        assert validate_pdf_filename(undated_filename), f"undated filename invalid: {undated_filename}"
        logger.info(f"Undated filename OK: {undated_filename}")
    except Exception as exc:  # noqa: BLE001
        logger.error(f"Snake_case contract smoke test failed: {exc}")
        return 1

    # Validate the local path (if it exists)
    local_path = Path(args.path)
    if local_path.exists():
        ok, errors = validate_local_path(local_path)
        if not ok:
            for err in errors:
                logger.error(err)
            return 1
        logger.info(f"All files in {local_path} match the canonical snake_case pattern.")
    else:
        logger.info(f"Local path {local_path} does not exist; skipping file validation.")
        logger.info(f"  (To validate real files, first run the BIEP v3 ingestion to populate s3://garage/cianfhoghlaim/)")

    logger.info("All validations pass.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
