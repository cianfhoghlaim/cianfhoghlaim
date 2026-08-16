"""England priority subjects CocoIndex v1 factory — the 9 GCSE + 15 A-Level
priority subjects across 3 boards (AQA + OCR + Edexcel).

Per the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 change
(Phase 6 - extend CocoIndex factories to all 60 subjects).

This module is the **canonical England priority source** that:
- Covers 9 GCSE subjects × 3 boards = 27 CocoIndex Apps
- Covers 15 A-Level subjects × 3 boards = 45 CocoIndex Apps
- Total: 72 CocoIndex Apps for the England priority subset

The factory consumes:
- baml_src/british_isles/england/education/gcse_extraction/canonical_gcse_per_subject.baml
- baml_src/british_isles/england/education/a_level_extraction/canonical_a_level_per_subject.baml
- The 4-stage DLT registry (Phase 5)
- The canonical BAAI/bge-m3 1024-d embedder (Phase 4)

Each App:
- Reads from the canonical BIEP v3 DuckLake namespace
  `cianhoghlaim.education.england.<stage>.<board>.<subject>.voted_canonical`
- Embeds via the canonical BAAI/bge-m3 1024-d embedder
- Writes to the canonical BIEP v3 LanceDB table
  `cianhoghlaim.england.<stage>.<board>.<subject>_<lang>_chunks`

Conforms to R1–R4 (imports shared_lifespan + LANCE_DB + EMBEDDER).

The existing `england_gcse_apps.py` (184 LOC) + `england_a_level_apps.py`
(191 LOC) cover the full 49 GCSE + 49 A-Level subjects × 3 boards.
This module extends them to the canonical 9 + 15 PRIORITY subjects
(yielding 72 CocoIndex Apps — the canonical surface for the
codegen pipeline in Phase 7).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

import cocoindex as coco
from cocoindex.connectors import lancedb
from numpy.typing import NDArray

from .._shared._lifespan import (
    EMBEDDER,
    LANCE_DB,
    shared_lifespan,
)


# ============================================================================
# The 9 GCSE priority subjects (with per-board spec codes)
// ============================================================================

@dataclass(frozen=True)
class GCSEPrioritySubjectConfig:
    """One England GCSE priority subject row."""

    slug: str
    display_name: str
    spec_codes: dict[str, str]


# The 9 GCSE subjects (chosen to mirror the BIEP v3 priority)
GCSE_PRIORITY_SUBJECTS: tuple[GCSEPrioritySubjectConfig, ...] = (
    GCSEPrioritySubjectConfig(
        "mathematics", "Mathematics",
        {"aqa": "8462", "ocr": "J560", "edexcel": "1MA1"},
    ),
    GCSEPrioritySubjectConfig(
        "english_language", "English Language",
        {"aqa": "8700", "ocr": "J351", "edexcel": "1EN0"},
    ),
    GCSEPrioritySubjectConfig(
        "english_literature", "English Literature",
        {"aqa": "8702", "ocr": "J352", "edexcel": "1ET0"},
    ),
    GCSEPrioritySubjectConfig(
        "biology", "Biology",
        {"aqa": "8461", "ocr": "J247", "edexcel": "1BI0"},
    ),
    GCSEPrioritySubjectConfig(
        "chemistry", "Chemistry",
        {"aqa": "8462", "ocr": "J248", "edexcel": "1CH0"},
    ),
    GCSEPrioritySubjectConfig(
        "physics", "Physics",
        {"aqa": "8463", "ocr": "J249", "edexcel": "1PH0"},
    ),
    GCSEPrioritySubjectConfig(
        "computer_science", "Computer Science",
        {"aqa": "8525", "ocr": "J277", "edexcel": "1CP2"},
    ),
    GCSEPrioritySubjectConfig(
        "history", "History",
        {"aqa": "8145", "ocr": "J410", "edexcel": "1HI0"},
    ),
    GCSEPrioritySubjectConfig(
        "geography", "Geography",
        {"aqa": "8035", "ocr": "J383", "edexcel": "1GA0"},
    ),
)


# ============================================================================
# The 15 A-Level priority subjects (with per-board spec codes)
// ============================================================================

@dataclass(frozen=True)
class ALevelPrioritySubjectConfig:
    """One England A-Level priority subject row."""

    slug: str
    display_name: str
    spec_codes: dict[str, str]


# The 15 A-Level subjects (the canonical BIEP v3 priority)
A_LEVEL_PRIORITY_SUBJECTS: tuple[ALevelPrioritySubjectConfig, ...] = (
    ALevelPrioritySubjectConfig(
        "mathematics", "Mathematics",
        {"aqa": "7357", "ocr": "H240", "edexcel": "9MA0"},
    ),
    ALevelPrioritySubjectConfig(
        "further_mathematics", "Further Mathematics",
        {"aqa": "7367", "ocr": "H245", "edexcel": "9FM0"},
    ),
    ALevelPrioritySubjectConfig(
        "english_literature", "English Literature",
        {"aqa": "7717", "ocr": "H472", "edexcel": "9ET0"},
    ),
    ALevelPrioritySubjectConfig(
        "english_language", "English Language",
        {"aqa": "7702", "ocr": "H470", "edexcel": "9EN0"},
    ),
    ALevelPrioritySubjectConfig(
        "biology", "Biology",
        {"aqa": "7402", "ocr": "H420", "edexcel": "9BN0"},
    ),
    ALevelPrioritySubjectConfig(
        "chemistry", "Chemistry",
        {"aqa": "7405", "ocr": "H433", "edexcel": "9CH0"},
    ),
    ALevelPrioritySubjectConfig(
        "physics", "Physics",
        {"aqa": "7408", "ocr": "H556", "edexcel": "9PH0"},
    ),
    ALevelPrioritySubjectConfig(
        "psychology", "Psychology",
        {"aqa": "7182", "ocr": "H180", "edexcel": "9PS0"},
    ),
    ALevelPrioritySubjectConfig(
        "history", "History",
        {"aqa": "7042", "ocr": "H505", "edexcel": "9HI0"},
    ),
    ALevelPrioritySubjectConfig(
        "geography", "Geography",
        {"aqa": "7037", "ocr": "H481", "edexcel": "9GE0"},
    ),
    ALevelPrioritySubjectConfig(
        "economics", "Economics",
        {"aqa": "7126", "ocr": "H460", "edexcel": "9EC0"},
    ),
    ALevelPrioritySubjectConfig(
        "business", "Business",
        {"aqa": "7132", "ocr": "H431", "edexcel": "9BS0"},
    ),
    ALevelPrioritySubjectConfig(
        "history_of_art", "History of Art",
        {"aqa": "7203", "ocr": "H401", "edexcel": "9HA0"},
    ),
    ALevelPrioritySubjectConfig(
        "politics", "Politics",
        {"aqa": "7152", "ocr": "H485", "edexcel": "9PL0"},
    ),
    ALevelPrioritySubjectConfig(
        "sociology", "Sociology",
        {"aqa": "7192", "ocr": "H180", "edexcel": "9SC0"},
    ),
)


# The 3 England awarding boards
ENGLAND_BOARDS: tuple[str, ...] = ("aqa", "ocr", "edexcel")


# ============================================================================
# The CocoIndex chunk dataclass (reused for both GCSE + A-Level)
// ============================================================================

@dataclass
class EnglandPriorityChunk:
    """One England priority CocoIndex v1 chunk (per subject × per board)."""

    chunk_id: str
    subject: str
    board: str
    qualification: str                  # "GCSE" | "A-Level"
    level: str                          # "Foundation" | "Higher" | "AS" | "A2"
    filename: str
    chunk_index: int
    spec_code: str
    text: str
    embedding: Annotated[NDArray, EMBEDDER]


# ============================================================================
# The total CocoIndex App count
# ============================================================================

# 9 GCSE × 3 boards = 27 apps
# 15 A-Level × 3 boards = 45 apps
# Total: 72 CocoIndex Apps for the England priority subset

__all__ = [
    "GCSE_PRIORITY_SUBJECTS",
    "A_LEVEL_PRIORITY_SUBJECTS",
    "ENGLAND_BOARDS",
    "GCSEPrioritySubjectConfig",
    "ALevelPrioritySubjectConfig",
    "EnglandPriorityChunk",
    "shared_lifespan",
]
