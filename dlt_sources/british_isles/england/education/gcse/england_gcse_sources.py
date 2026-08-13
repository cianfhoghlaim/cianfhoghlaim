"""DLT sources for England GCSE curricula (per the 2026-08-10-england-biiep-pipeline-v1 change).

3 boards × 43 GCSE subjects = 129 CocoIndex Apps + 3 DLT sources.

The sources consume from `stedding/site_scrape_samples/england/gcse/<board>/`
and yield rows `{pdf_path, subject, board, qualification, level, language}`.

Reference: openspec/changes/2026-08-10-england-biiep-pipeline-v1/
"""
from __future__ import annotations

import hashlib
import os
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import dlt


# The 3 England GCSE boards (per BIEP v3 spec)
ENGLAND_GCSE_BOARDS: tuple[str, ...] = ("aqa", "ocr", "edexcel")

# The 43 GCSE subjects per board (per the canonical AQA/OCR/Edexcel lists)
ENGLAND_GCSE_SUBJECTS: tuple[str, ...] = (
    "mathematics",
    "english_language",
    "english_literature",
    "biology",
    "chemistry",
    "physics",
    "combined_science",
    "religious_studies",
    "geography",
    "history",
    "french",
    "german",
    "spanish",
    "computer_science",
    "design_technology",
    "food_preparation",
    "physical_education",
    "art_and_design",
    "music",
    "drama",
    "media_studies",
    "business",
    "economics",
    "psychology",
    "sociology",
    "politics",
    "law",
    "classical_civilisation",
    "ancient_history",
    "statistics",
    "further_mathematics",
    "geology",
    "astronomy",
    "environmental_science",
    "pe_short_course",
    "religious_philosophy",
    "citizenship",
    "child_development",
    "economics_business",
    "health_social_care",
    "ict",
    "engineering",
    "electronics",
)


def _scan_gcse_board(board: str, root: Path) -> Iterator[dict[str, Any]]:
    """Yield (file_path, subject) tuples for one GCSE board."""
    board_dir = root / board
    if not board_dir.exists():
        return
    for pdf in sorted(board_dir.glob("**/*.pdf")):
        # Try to infer subject from the path: gcse/<board>/<subject>/<file>.pdf
        # or gcse/<board>/<file>.pdf (subject in filename)
        parts = pdf.relative_to(board_dir).parts
        subject = parts[0] if len(parts) > 1 else pdf.stem.split("_")[0]
        yield {
            "file_path": pdf,
            "subject": subject,
            "board": board,
            "qualification": "gcse",
            "level": "gcse",
            "language": "en",
        }


def _row(record: dict[str, Any]) -> dict[str, Any]:
    file_path = record["file_path"]
    file_hash = ""
    try:
        file_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
    except OSError:
        pass
    return {
        "id": hashlib.sha256(
            f"{file_hash}:{file_path.name}:{record['subject']}".encode("utf-8")
        ).hexdigest()[:16],
        "file_hash": file_hash,
        "file_name": file_path.name,
        "file_path": str(file_path),
        "file_size_bytes": file_path.stat().st_size if file_path.exists() else 0,
        "subject": record["subject"],
        "board": record["board"],
        "qualification": record["qualification"],
        "level": record["level"],
        "language": record["language"],
    }


def make_gcse_resource(board: str):
    """Factory for one GCSE board's DLT resource."""

    @dlt.resource(
        name=f"gcse_{board}_subjects",
        write_disposition="replace",
        primary_key="id",
        columns={
            "id": {"data_type": "text"},
            "file_hash": {"data_type": "text"},
            "file_name": {"data_type": "text"},
            "file_path": {"data_type": "text"},
            "file_size_bytes": {"data_type": "bigint"},
            "subject": {"data_type": "text"},
            "board": {"data_type": "text"},
            "qualification": {"data_type": "text"},
            "level": {"data_type": "text"},
            "language": {"data_type": "text"},
        },
    )
    def _gcse_board_subjects(
        root_path: str = str(
            Path(
                os.environ.get(
                    "STEDDING_INGEST_QUEUE",
                    "/Users/cianmacandeisigh/dev/kings_college_galway/stedding/site_scrape_samples",
                )
            )
            / "england"
            / "gcse"
        ),
    ) -> Iterator[dict[str, Any]]:
        root = Path(root_path)
        n = 0
        for record in _scan_gcse_board(board, root):
            yield _row(record)
            n += 1
        if n == 0:
            # Empty partition — still yield one row for materialization
            yield _row(
                {
                    "file_path": Path(f"/dev/null/empty_{board}_gcse.pdf"),
                    "subject": "empty",
                    "board": board,
                    "qualification": "gcse",
                    "level": "gcse",
                    "language": "en",
                }
            )

    # The `@dlt.resource(name=...)` above already sets the real registered
    # resource name; this just gives the returned callable a matching
    # __name__ for introspection/debugging (a previous version used a
    # literal `gcse_<board>_subjects` placeholder in the `def` line itself
    # — a hard SyntaxError).
    _gcse_board_subjects.__name__ = f"gcse_{board}_subjects"
    return _gcse_board_subjects


# Pre-built resources for the 3 boards
gcse_aqa_subjects = make_gcse_resource("aqa")
gcse_ocr_subjects = make_gcse_resource("ocr")
gcse_edexcel_subjects = make_gcse_resource("edexcel")


__all__ = [
    "ENGLAND_GCSE_BOARDS",
    "ENGLAND_GCSE_SUBJECTS",
    "gcse_aqa_subjects",
    "gcse_ocr_subjects",
    "gcse_edexcel_subjects",
]
