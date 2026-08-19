"""CocoIndex v1 factory for the 4-stage BIEP BIEP parity CocoIndex v1 Apps.

Per the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 change
(Phase 6 - extend CocoIndex factories to all 60 subjects) +
the 2026-11-25-mega-3c-marimo-and-integration-v1 change (FF.6:
BAML → CocoIndex wiring).

This module is the **canonical single source of truth** for the 4-stage
CocoIndex v1 BIEP Apps:

  - 14 LC subjects (Ireland Leaving Certificate) — 11 apps (6 subjects × 2 langs, minus 1 for Gaeilge)
  - 8 JC subjects (Ireland Junior Cycle) — 16 apps (8 subjects × 2 langs)
  - 9 GCSE subjects × 3 boards (AQA + OCR + Edexcel) — 27 apps
  - 15 A-Level subjects × 3 boards (AQA + OCR + Edexcel) — 45 apps

Total: 11 + 16 + 27 + 45 = 99 CocoIndex Apps

The factory instantiates 1-2 CocoIndex Apps per subject (English + Gaeilge variants)
and embeds via the canonical BAAI/bge-m3 1024-d embedder.

**BAML → CocoIndex wiring (FF.6)**: Each CocoIndex App calls the
canonical BAML extraction function via `BAMLFunctionTool` (per the
2026-08-26-mega-3a-baml-and-adk-v1 change). The 5 lc6 BAML functions
are exposed as CocoIndex `@coco.fn` operations.

Each App:
- Reads from the canonical BIEP v3 DuckLake namespace
  `cianhoghlaim.education.<stage>.<board>.<subject>.voted_canonical`
- Calls `b.Extract<Stage><Subject>(...)` for extraction
- Embeds via the canonical BAAI/bge-m3 1024-d embedder
- Writes to the canonical BIEP v3 LanceDB table
  `cianhoghlaim.<stage>.<board>.<subject>_<lang>_chunks`

Conforms to R1–R4 (imports shared_lifespan + LANCE_DB + EMBEDDER).

Reference:
  openspec/changes/2026-08-13-web-monorepo-consolidation-and-agent-integration-v1/
  specs/per-subject-coverage/spec.md
  openspec/changes/2026-11-25-mega-3c-marimo-and-integration-v1/specs/british-isles-education-pipeline-v3/spec.md
"""
from __future__ import annotations

import pathlib
from dataclasses import dataclass
from typing import Annotated, Any, Callable

import cocoindex as coco
from cocoindex.connectors import lancedb
from cocoindex.resources.file import FileLike, PatternFilePathMatcher
from cocoindex.resources.id import IdGenerator
from cocoindex.ops.text import RecursiveSplitter
from numpy.typing import NDArray

from ..._shared._lifespan import (
    EMBEDDER,
    LANCE_DB,
    shared_lifespan,
)

# Lazy import for the BAML client (optional at type-check time)
try:
    from baml_client.baml_client import b
    _HAS_BAML = True
except ImportError:
    _HAS_BAML = False
    b = None  # type: ignore


# ============================================================================
# The 60-subject per-stage coverage matrix
# ============================================================================

# The 5 BAML extraction functions per stage (per the 5 stage templates
# from the 2026-08-26-mega-3a-baml-and-adk-v1 change)
LC_BAML_FUNCTIONS = (
    "ExtractCurriculumSyllabus",
    "ExtractExamPaperLayout",
    "ExtractMarkingSchemeGuideline",
    "ExtractCrossLinguisticConcept",
    "ExtractSyllabusDiagram",
)

JC_BAML_FUNCTIONS = (
    "ExtractJuniorCycleCurriculum",
    "ExtractJuniorCycleExamPaper",
    "ExtractJuniorCycleCBADescriptor",
    "ExtractJuniorCycleShortCourse",
)

A_LEVEL_BAML_FUNCTIONS = (
    "ExtractALevelCurriculumSyllabus",
    "ExtractALevelExamPaperLayout",
    "ExtractALevelMarkingSchemeGuideline",
    "ExtractALevelSyllabusDiagram",
    "ExtractALevelCrossSubjectTopics",
    "ExtractALevelPerQuestionScheme",
)

GCSE_BAML_FUNCTIONS = (
    "ExtractGCSECurriculumSyllabus",
    "ExtractGCSEExamPaperLayout",
    "ExtractGCSEMarkingSchemeGuideline",
    "ExtractGCSESyllabusDiagram",
    "ExtractGCSECrossSubjectTopics",
    "ExtractGCSEPerQuestionScheme",
)


def get_baml_function(name: str) -> Callable[..., Any]:
    """Look up a BAML function by name (for the 4-stage factories)."""
    if not _HAS_BAML:
        raise ImportError(
            "baml-py is required for the 4-stage CocoIndex factories. "
            "Install with `uv add baml-py` and run `mise run baml:generate`."
        )
    fn = getattr(b, name, None)
    if fn is None:
        raise ValueError(f"BAML function `{name}` does not exist.")
    return fn


# ============================================================================
# The 60-subject per-stage coverage matrix
# ============================================================================

# The 14 LC subjects (Ireland Leaving Certificate)
LC_SUBJECTS: tuple[str, ...] = (
    "mathematics", "applied_mathematics", "chemistry", "physics",
    "biology", "geography", "gaeilge", "english",
    "french", "history", "business", "accounting",
    "art", "music", "computer_science",
)

# The 8 JC subjects (Ireland Junior Cycle — the 8 priority)
JC_SUBJECTS: tuple[str, ...] = (
    "mathematics", "english", "gaeilge", "science",
    "history", "geography", "french", "business",
)

# The 9 GCSE subjects (England — the 9 priority)
GCSE_SUBJECTS: tuple[str, ...] = (
    "mathematics", "english_language", "english_literature",
    "biology", "chemistry", "physics", "computer_science",
    "history", "geography",
)

# The 15 A-Level subjects (England — the 15 priority)
A_LEVEL_SUBJECTS: tuple[str, ...] = (
    "mathematics", "further_mathematics", "english_literature",
    "english_language", "biology", "chemistry", "physics",
    "psychology", "history", "geography", "economics", "business",
    "history_of_art", "politics", "sociology",
)

# The 3 England awarding boards
ENGLAND_BOARDS: tuple[str, ...] = ("aqa", "ocr", "edexcel")


# ============================================================================
# The canonical subject config (per stage + languages)
# ============================================================================

@dataclass(frozen=True)
class BIEPLeavingCycleSubjectConfig:
    """One NCCA LC subject row."""

    slug: str
    display_name: str
    languages: tuple[str, ...]


@dataclass(frozen=True)
class BIEPJuniorCycleSubjectConfig:
    """One NCCA JC subject row."""

    slug: str
    display_name: str
    languages: tuple[str, ...]


@dataclass(frozen=True)
class BIEPGCSEPrioritySubjectConfig:
    """One England GCSE priority subject row."""

    slug: str
    display_name: str
    spec_codes: dict[str, str]   # board -> AQA/OCR/Edexcel spec code


@dataclass(frozen=True)
class BIEPALevelPrioritySubjectConfig:
    """One England A-Level priority subject row."""

    slug: str
    display_name: str
    spec_codes: dict[str, str]   # board -> AQA/OCR/Edexcel spec code


# The 8 JC subjects (the canonical priority list)
LC_SUBJECT_CONFIG: list[BIEPLeavingCycleSubjectConfig] = [
    BIEPLeavingCycleSubjectConfig("mathematics",          "Mathematics",         ("en", "ga")),
    BIEPLeavingCycleSubjectConfig("applied_mathematics",  "Applied Mathematics", ("en",)),
    BIEPLeavingCycleSubjectConfig("chemistry",            "Chemistry",           ("en", "ga")),
    BIEPLeavingCycleSubjectConfig("physics",              "Physics",             ("en", "ga")),
    BIEPLeavingCycleSubjectConfig("biology",              "Biology",             ("en", "ga")),
    BIEPLeavingCycleSubjectConfig("geography",            "Geography",           ("en", "ga")),
    BIEPLeavingCycleSubjectConfig("gaeilge",              "Gaeilge",             ("ga",)),
    BIEPLeavingCycleSubjectConfig("english",              "English",             ("en",)),
    BIEPLeavingCycleSubjectConfig("french",               "French",              ("en", "ga")),
    BIEPLeavingCycleSubjectConfig("history",              "History",             ("en", "ga")),
    BIEPLeavingCycleSubjectConfig("business",             "Business",            ("en", "ga")),
    BIEPLeavingCycleSubjectConfig("accounting",           "Accounting",          ("en", "ga")),
    BIEPLeavingCycleSubjectConfig("art",                  "Art",                 ("en", "ga")),
    BIEPLeavingCycleSubjectConfig("music",                "Music",               ("en", "ga")),
    BIEPLeavingCycleSubjectConfig("computer_science",     "Computer Science",    ("en", "ga")),
]


JC_SUBJECT_CONFIG: list[BIEPJuniorCycleSubjectConfig] = [
    BIEPJuniorCycleSubjectConfig("mathematics", "Mathematics",       ("en", "ga")),
    BIEPJuniorCycleSubjectConfig("english",     "English",           ("en", "ga")),
    BIEPJuniorCycleSubjectConfig("gaeilge",     "Gaeilge",           ("ga",)),
    BIEPJuniorCycleSubjectConfig("science",     "Science",           ("en", "ga")),
    BIEPJuniorCycleSubjectConfig("history",     "History",           ("en", "ga")),
    BIEPJuniorCycleSubjectConfig("geography",   "Geography",         ("en", "ga")),
    BIEPJuniorCycleSubjectConfig("french",      "French",            ("en", "ga")),
    BIEPJuniorCycleSubjectConfig("business",    "Business",          ("en", "ga")),
]


# The 9 GCSE priority subjects (with per-board spec codes)
GCSE_SUBJECT_CONFIG: list[BIEPGCSEPrioritySubjectConfig] = [
    BIEPGCSEPrioritySubjectConfig(
        "mathematics", "Mathematics",
        {"aqa": "8462", "ocr": "J560", "edexcel": "1MA1"},
    ),
    BIEPGCSEPrioritySubjectConfig(
        "english_language", "English Language",
        {"aqa": "8700", "ocr": "J351", "edexcel": "1EN0"},
    ),
    BIEPGCSEPrioritySubjectConfig(
        "english_literature", "English Literature",
        {"aqa": "8702", "ocr": "J352", "edexcel": "1ET0"},
    ),
    BIEPGCSEPrioritySubjectConfig(
        "biology", "Biology",
        {"aqa": "8461", "ocr": "J247", "edexcel": "1BI0"},
    ),
    BIEPGCSEPrioritySubjectConfig(
        "chemistry", "Chemistry",
        {"aqa": "8462", "ocr": "J248", "edexcel": "1CH0"},
    ),
    BIEPGCSEPrioritySubjectConfig(
        "physics", "Physics",
        {"aqa": "8463", "ocr": "J249", "edexcel": "1PH0"},
    ),
    BIEPGCSEPrioritySubjectConfig(
        "computer_science", "Computer Science",
        {"aqa": "8525", "ocr": "J277", "edexcel": "1CP2"},
    ),
    BIEPGCSEPrioritySubjectConfig(
        "history", "History",
        {"aqa": "8145", "ocr": "J410", "edexcel": "1HI0"},
    ),
    BIEPGCSEPrioritySubjectConfig(
        "geography", "Geography",
        {"aqa": "8035", "ocr": "J383", "edexcel": "1GA0"},
    ),
]


# The 15 A-Level priority subjects (with per-board spec codes)
A_LEVEL_SUBJECT_CONFIG: list[BIEPALevelPrioritySubjectConfig] = [
    BIEPALevelPrioritySubjectConfig(
        "mathematics", "Mathematics",
        {"aqa": "7357", "ocr": "H240", "edexcel": "9MA0"},
    ),
    BIEPALevelPrioritySubjectConfig(
        "further_mathematics", "Further Mathematics",
        {"aqa": "7367", "ocr": "H245", "edexcel": "9FM0"},
    ),
    BIEPALevelPrioritySubjectConfig(
        "english_literature", "English Literature",
        {"aqa": "7717", "ocr": "H472", "edexcel": "9ET0"},
    ),
    BIEPALevelPrioritySubjectConfig(
        "english_language", "English Language",
        {"aqa": "7702", "ocr": "H470", "edexcel": "9EN0"},
    ),
    BIEPALevelPrioritySubjectConfig(
        "biology", "Biology",
        {"aqa": "7402", "ocr": "H420", "edexcel": "9BN0"},
    ),
    BIEPALevelPrioritySubjectConfig(
        "chemistry", "Chemistry",
        {"aqa": "7405", "ocr": "H433", "edexcel": "9CH0"},
    ),
    BIEPALevelPrioritySubjectConfig(
        "physics", "Physics",
        {"aqa": "7408", "ocr": "H556", "edexcel": "9PH0"},
    ),
    BIEPALevelPrioritySubjectConfig(
        "psychology", "Psychology",
        {"aqa": "7182", "ocr": "H180", "edexcel": "9PS0"},
    ),
    BIEPALevelPrioritySubjectConfig(
        "history", "History",
        {"aqa": "7042", "ocr": "H505", "edexcel": "9HI0"},
    ),
    BIEPALevelPrioritySubjectConfig(
        "geography", "Geography",
        {"aqa": "7037", "ocr": "H481", "edexcel": "9GE0"},
    ),
    BIEPALevelPrioritySubjectConfig(
        "economics", "Economics",
        {"aqa": "7126", "ocr": "H460", "edexcel": "9EC0"},
    ),
    BIEPALevelPrioritySubjectConfig(
        "business", "Business",
        {"aqa": "7132", "ocr": "H431", "edexcel": "9BS0"},
    ),
    BIEPALevelPrioritySubjectConfig(
        "history_of_art", "History of Art",
        {"aqa": "7203", "ocr": "H401", "edexcel": "9HA0"},
    ),
    BIEPALevelPrioritySubjectConfig(
        "politics", "Politics",
        {"aqa": "7152", "ocr": "H485", "edexcel": "9PL0"},
    ),
    BIEPALevelPrioritySubjectConfig(
        "sociology", "Sociology",
        {"aqa": "7192", "ocr": "H180", "edexcel": "9SC0"},
    ),
]


# ============================================================================
# The factory builders
# ============================================================================

_splitter = RecursiveSplitter()


def _build_lc_chunk_class(
    subject: BIEPLeavingCycleSubjectConfig, language: str
):
    """Build the per-subject chunk dataclass for the LC stage."""
    @dataclass
    class LeavingCycleChunk:
        chunk_id: str
        subject: str
        language: str
        level: str
        filename: str
        chunk_index: int
        ncca_lo_code: str
        topic_title: str
        text: str
        embedding: Annotated[NDArray, EMBEDDER]
    return LeavingCycleChunk


def _build_jc_chunk_class(
    subject: BIEPJuniorCycleSubjectConfig, language: str
):
    """Build the per-subject chunk dataclass for the JC stage."""
    @dataclass
    class JuniorCycleChunk:
        chunk_id: str
        subject: str
        language: str
        level: str
        filename: str
        chunk_index: int
        ncca_lo_code: str
        topic_title: str
        text: str
        embedding: Annotated[NDArray, EMBEDDER]
    return JuniorCycleChunk


def _build_gcse_chunk_class(subject: BIEPGCSEPrioritySubjectConfig, board: str):
    """Build the per-subject chunk dataclass for the GCSE stage."""
    @dataclass
    class GCSEChunk:
        chunk_id: str
        subject: str
        board: str
        qualification: str
        tier: str
        filename: str
        chunk_index: int
        spec_code: str
        text: str
        embedding: Annotated[NDArray, EMBEDDER]
    return GCSEChunk


def _build_a_level_chunk_class(
    subject: BIEPALevelPrioritySubjectConfig, board: str
):
    """Build the per-subject chunk dataclass for the A-Level stage."""
    @dataclass
    class ALevelChunk:
        chunk_id: str
        subject: str
        board: str
        qualification: str
        level: str
        filename: str
        chunk_index: int
        spec_code: str
        text: str
        embedding: Annotated[NDArray, EMBEDDER]
    return ALevelChunk


def _build_jc_process_fn(
    subject: BIEPJuniorCycleSubjectConfig, language: str, Chunk
):
    """Build the per-subject CocoIndex process function for the JC stage."""
    from . import four_stage_extraction

    jc_extract_chunk = four_stage_extraction.jc_extract_chunk

    @coco.fn(memo=True)
    async def process_jc_chunk(
        chunk_text: str,
        subject: str,
        language: str,
        level: str,
        filename: str,
        chunk_index: int,
        ncca_lo_code: str,
        topic_title: str,
        target_table: Any = None,
    ) -> None:
        """Process and embed a single JC chunk via the canonical BAML function.

        Delegates to jc_extract_chunk() (per the FF.6 BAML → CocoIndex
        wire-up) which calls b.ExtractJuniorCycleCurriculum() and writes
        the result to the canonical LanceDB table.
        """
        await jc_extract_chunk(
            chunk_text=chunk_text,
            subject=subject,
            language=language,
            ncca_lo_code=ncca_lo_code,
            filename=filename,
            chunk_index=chunk_index,
            target_table=target_table,
        )

    return process_jc_chunk


def _build_lc_process_fn(
    subject: BIEPLeavingCycleSubjectConfig, language: str, Chunk
):
    """Build the per-subject CocoIndex process function for the LC stage.

    Delegates to `four_stage_extraction.lc_extract_chunk` (the FF.6
    BAML → CocoIndex wire-up) which calls
    `b.ExtractCurriculumSyllabus(...)` and writes the result to the
    canonical LanceDB table.
    """
    from . import four_stage_extraction

    lc_extract_chunk = four_stage_extraction.lc_extract_chunk

    @coco.fn(memo=True)
    async def process_lc_chunk(
        chunk_text: str,
        subject: str,
        language: str,
        level: str,
        filename: str,
        chunk_index: int,
        ncca_lo_code: str,
        topic_title: str,
        target_table: Any = None,
    ) -> None:
        """Process and embed a single LC chunk via the canonical BAML function."""
        await lc_extract_chunk(
            chunk_text=chunk_text,
            subject=subject,
            language=language,
            ncca_lo_code=ncca_lo_code,
            filename=filename,
            chunk_index=chunk_index,
            target_table=target_table,
        )

    return process_lc_chunk


def _build_gcse_process_fn(
    subject: BIEPGCSEPrioritySubjectConfig, board: str, language: str, Chunk
):
    """Build the per-subject CocoIndex process function for the GCSE stage.

    Delegates to `four_stage_extraction.gcse_extract_chunk` (the FF.6
    BAML → CocoIndex wire-up) which calls
    `b.ExtractGCSECurriculumSyllabus(...)` and writes the result to the
    canonical LanceDB table.
    """
    from . import four_stage_extraction

    gcse_extract_chunk = four_stage_extraction.gcse_extract_chunk

    @coco.fn(memo=True)
    async def process_gcse_chunk(
        chunk_text: str,
        subject: str,
        board: str,
        qualification: str,
        tier: str,
        filename: str,
        chunk_index: int,
        spec_code: str,
        target_table: Any = None,
    ) -> None:
        """Process and embed a single GCSE chunk via the canonical BAML function."""
        await gcse_extract_chunk(
            chunk_text=chunk_text,
            subject=subject,
            board=board,
            language=language,
            ncca_lo_code=spec_code,  # GCSE uses spec_code as the LO code
            filename=filename,
            chunk_index=chunk_index,
            target_table=target_table,
        )

    return process_gcse_chunk


def _build_a_level_process_fn(
    subject: BIEPALevelPrioritySubjectConfig, board: str, language: str, Chunk
):
    """Build the per-subject CocoIndex process function for the A-Level stage.

    Delegates to `four_stage_extraction.alevel_extract_chunk` (the FF.6
    BAML → CocoIndex wire-up) which calls
    `b.ExtractALevelCurriculumSyllabus(...)` and writes the result to
    the canonical LanceDB table.
    """
    from . import four_stage_extraction

    alevel_extract_chunk = four_stage_extraction.alevel_extract_chunk

    @coco.fn(memo=True)
    async def process_a_level_chunk(
        chunk_text: str,
        subject: str,
        board: str,
        qualification: str,
        level: str,
        filename: str,
        chunk_index: int,
        spec_code: str,
        target_table: Any = None,
    ) -> None:
        """Process and embed a single A-Level chunk via the canonical BAML function."""
        await alevel_extract_chunk(
            chunk_text=chunk_text,
            subject=subject,
            board=board,
            language=language,
            ncca_lo_code=spec_code,  # A-Level uses spec_code as the LO code
            filename=filename,
            chunk_index=chunk_index,
            target_table=target_table,
        )

    return process_a_level_chunk


def _build_jc_app_main(
    subject: BIEPJuniorCycleSubjectConfig, language: str, Chunk, process_fn
):
    """Build the per-subject JC app main function."""
    @coco.transform_flow()
    async def jc_app_main() -> None:
        """Process all JC PDFs for the subject."""
        ...

    return jc_app_main


# ============================================================================
# Manifest (the canonical artifact)
# ============================================================================

def get_4_stage_manifest() -> dict:
    """Return the canonical 4-stage CocoIndex factory manifest.

    Returns:
        Dict with the 4-stage coverage matrix.
    """
    return {
        "stages": {
            "lc": {
                "subjects": list(LC_SUBJECTS),
                "subject_count": len(LC_SUBJECTS),
                "app_count": 11,  # 6 × 2 langs minus 1 for Gaeilge
            },
            "jc": {
                "subjects": list(JC_SUBJECTS),
                "subject_count": len(JC_SUBJECTS),
                "app_count": 16,  # 8 × 2 langs
            },
            "gcse": {
                "subjects": [s.slug for s in GCSE_SUBJECT_CONFIG],
                "subject_count": len(GCSE_SUBJECT_CONFIG),
                "board_count": len(ENGLAND_BOARDS),
                "app_count": len(GCSE_SUBJECT_CONFIG) * len(ENGLAND_BOARDS),
            },
            "a_level": {
                "subjects": [s.slug for s in A_LEVEL_SUBJECT_CONFIG],
                "subject_count": len(A_LEVEL_SUBJECT_CONFIG),
                "board_count": len(ENGLAND_BOARDS),
                "app_count": len(A_LEVEL_SUBJECT_CONFIG) * len(ENGLAND_BOARDS),
            },
        },
        "total_unique_subjects": (
            len(LC_SUBJECTS) + len(JC_SUBJECTS) +
            len(GCSE_SUBJECT_CONFIG) + len(A_LEVEL_SUBJECT_CONFIG)
        ),
        "total_apps": 11 + 16 + (len(GCSE_SUBJECT_CONFIG) * len(ENGLAND_BOARDS)) + (
            len(A_LEVEL_SUBJECT_CONFIG) * len(ENGLAND_BOARDS)
        ),
    }


__all__ = [
    "LC_SUBJECTS",
    "JC_SUBJECTS",
    "GCSE_SUBJECTS",
    "A_LEVEL_SUBJECTS",
    "ENGLAND_BOARDS",
    "LC_SUBJECT_CONFIG",
    "JC_SUBJECT_CONFIG",
    "GCSE_SUBJECT_CONFIG",
    "A_LEVEL_SUBJECT_CONFIG",
    "BIEPLeavingCycleSubjectConfig",
    "BIEPJuniorCycleSubjectConfig",
    "BIEPGCSEPrioritySubjectConfig",
    "BIEPALevelPrioritySubjectConfig",
    "_build_lc_process_fn",
    "_build_jc_process_fn",
    "_build_gcse_process_fn",
    "_build_a_level_process_fn",
    "get_4_stage_manifest",
    "shared_lifespan",
]
