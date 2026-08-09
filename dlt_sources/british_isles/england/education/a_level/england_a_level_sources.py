"""DLT sources for England A-Level curricula (per the 2026-08-10-england-biiep-pipeline-v1 change).

3 boards × 49 A-Level subjects = 147 CocoIndex Apps + 3 DLT sources.
"""
from __future__ import annotations

import hashlib
import os
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import dlt


# The 3 England A-Level boards
ENGLAND_A_LEVEL_BOARDS: tuple[str, ...] = ("aqa", "ocr", "edexcel")

# The 49 A-Level subjects per board
ENGLAND_A_LEVEL_SUBJECTS: tuple[str, ...] = (
    "mathematics",
    "further_mathematics",
    "english_language",
    "english_literature",
    "biology",
    "chemistry",
    "physics",
    "geography",
    "history",
    "french",
    "german",
    "spanish",
    "italian",
    "russian",
    "chinese",
    "japanese",
    "latin",
    "greek",
    "classical_civilisation",
    "ancient_history",
    "religious_studies",
    "religious_philosophy",
    "theology",
    "philosophy",
    "psychology",
    "sociology",
    "politics",
    "government_and_politics",
    "economics",
    "business",
    "accounting",
    "law",
    "computer_science",
    "design_technology",
    "food_technology",
    "art_and_design",
    "fine_art",
    "graphic_design",
    "photography",
    "textile_design",
    "3d_design",
    "music",
    "music_technology",
    "drama",
    "theatre_studies",
    "media_studies",
    "film_studies",
    "physical_education",
    "dance",
    "statistics",
)


def _scan_a_level_board(board: str, root: Path) -> Iterator[dict[str, Any]]:
    board_dir = root / board
    if not board_dir.exists():
        return
    for pdf in sorted(board_dir.glob("**/*.pdf")):
        parts = pdf.relative_to(board_dir).parts
        subject = parts[0] if len(parts) > 1 else pdf.stem.split("_")[0]
        yield {
            "file_path": pdf,
            "subject": subject,
            "board": board,
            "qualification": "a_level",
            "level": "a_level",
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


def make_a_level_resource(board: str):
    """Factory for one A-Level board's DLT resource."""

    @dlt.resource(
        name=f"a_level_{board}_subjects",
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
    def a_level_<board>_subjects(
        root_path: str = str(
            Path(
                os.environ.get(
                    "STEDDING_INGEST_QUEUE",
                    "/Users/cianmacandeisigh/dev/kings_college_galway/stedding/site_scrape_samples",
                )
            )
            / "england"
            / "a_level"
        ),
    ) -> Iterator[dict[str, Any]]:
        root = Path(root_path)
        n = 0
        for record in _scan_a_level_board(board, root):
            yield _row(record)
            n += 1
        if n == 0:
            yield _row(
                {
                    "file_path": Path(f"/dev/null/empty_{board}_a_level.pdf"),
                    "subject": "empty",
                    "board": board,
                    "qualification": "a_level",
                    "level": "a_level",
                    "language": "en",
                }
            )

    a_level_<board>_subjects.__name__ = f"a_level_{board}_subjects"
    return a_level_<board>_subjects


# Pre-built resources for the 3 boards
a_level_aqa_subjects = make_a_level_resource("aqa")
a_level_ocr_subjects = make_a_level_resource("ocr")
a_level_edexcel_subjects = make_a_level_resource("edexcel")


__all__ = [
    "ENGLAND_A_LEVEL_BOARDS",
    "ENGLAND_A_LEVEL_SUBJECTS",
    "a_level_aqa_subjects",
    "a_level_ocr_subjects",
    "a_level_edexcel_subjects",
]
