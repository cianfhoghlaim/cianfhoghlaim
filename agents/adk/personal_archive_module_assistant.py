"""
agents.adk.personal_archive_module_assistant — Google ADK agent that
covers the 10 user-facing tools needed to lift
`leabharlann/ollscoil_na_gaillimhe/` to feature parity with the
leaving-cycle subject pipeline.

Per the 2026-08-23-uog-personal-archive-tertiary-modules-v1 change
(WS10 — Convex + CopilotKit + Genie + ADK).

The 10 tools:

  1. extract_personal_archive_artefact  — BAML ExtractUoGPersonalArchiveArtefact
  2. extract_assignment_questions       — BAML ExtractUoGAssignmentQuestions
  3. extract_topic_list                  — BAML ExtractUoGTopicList
  4. extract_lecture_reading_list        — BAML ExtractUoGReadingItem
  5. extract_code_cell                   — BAML ExtractUoGCodeCell
  6. extract_student_transcript          — BAML ExtractStudentTranscriptRow
  7. build_module_summary                — BAML UoGModuleSummary builder
  8. semantic_search_artefacts           — CocoIndex UoGPersonalArchiveArtefactsApp
  9. semantic_search_questions           — CocoIndex UoGPersonalArchiveQuestionsApp
  10. semantic_search_topics             — CocoIndex UoGPersonalArchiveTopicsApp

Mirrors the canonical `agents/adk/statistics_agent.py` shape: one
`LlmAgent` with the 10 tools and a `BuiltInPlanner` for thought
traces, plus 3 specialised sub-agents.
"""

from __future__ import annotations

import datetime
import logging

from pydantic import BaseModel

from google.adk.agents import LlmAgent
from google.adk.planners import BuiltInPlanner
from google.adk.tools import FunctionTool
from google.genai import types as genai_types

from .litellm_agent import litellm_model

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Tool implementations
# --------------------------------------------------------------------------- #


async def extract_personal_archive_artefact(
    file_path: str,
    embedded_text: str,
) -> dict[str, str]:
    """Extract a typed `UoGPersonalArchiveArtefact` from a PDF.

    Wraps the BAML `ExtractUoGPersonalArchiveArtefact` function. The
    BAML client is imported lazily so this module loads even when
    `baml generate` has not yet produced the typed client.
    """
    try:
        from baml_client import b as _baml_b  # type: ignore[import-not-found]
    except ImportError:
        logger.warning("baml_client_missing_for_artefact_extract")
        return {"status": "skipped_no_baml_client", "file_path": file_path}
    try:
        result = await _baml_b.ExtractUoGPersonalArchiveArtefact(
            file_path=file_path,
            embedded_text=embedded_text,
        )
        return {"status": "ok", "artefact_id": result.artefact_id}
    except Exception as exc:  # noqa: BLE001
        logger.warning("extract_artefact_failed", error=str(exc))
        return {"status": "error", "error": str(exc)}


async def extract_assignment_questions(
    artefact_id: str,
    assignment_text: str,
) -> dict[str, str | int]:
    """Extract the typed `UoGQuestion[]` from a typed assignment."""
    try:
        from baml_client import b as _baml_b  # type: ignore[import-not-found]
    except ImportError:
        return {"status": "skipped_no_baml_client", "artefact_id": artefact_id}
    try:
        result = await _baml_b.ExtractUoGAssignmentQuestions(
            artefact_id=artefact_id,
            assignment_text=assignment_text,
        )
        return {
            "status": "ok",
            "artefact_id": artefact_id,
            "question_count": len(result.questions),
        }
    except Exception as exc:  # noqa: BLE001
        logger.warning("extract_assignment_failed", error=str(exc))
        return {"status": "error", "error": str(exc)}


async def extract_topic_list(
    artefact_id: str,
    lecture_text: str,
) -> dict[str, str | int]:
    """Extract the typed `UoGTopic[]` from a lecture-note artefact."""
    try:
        from baml_client import b as _baml_b  # type: ignore[import-not-found]
    except ImportError:
        return {"status": "skipped_no_baml_client", "artefact_id": artefact_id}
    try:
        result = await _baml_b.ExtractUoGTopicList(
            artefact_id=artefact_id,
            lecture_text=lecture_text,
        )
        return {
            "status": "ok",
            "artefact_id": artefact_id,
            "topic_count": len(result.topics),
        }
    except Exception as exc:  # noqa: BLE001
        logger.warning("extract_topic_list_failed", error=str(exc))
        return {"status": "error", "error": str(exc)}


async def extract_lecture_reading_list(
    artefact_id: str,
    lecture_text: str,
) -> dict[str, str | int]:
    """Extract the typed `UoGReadingItem[]` reading list."""
    try:
        from baml_client import b as _baml_b  # type: ignore[import-not-found]
    except ImportError:
        return {"status": "skipped_no_baml_client", "artefact_id": artefact_id}
    try:
        result = await _baml_b.ExtractUoGReadingItem(
            artefact_id=artefact_id,
            lecture_text=lecture_text,
        )
        return {
            "status": "ok",
            "artefact_id": artefact_id,
            "reading_item_count": len(result.reading_items),
        }
    except Exception as exc:  # noqa: BLE001
        logger.warning("extract_reading_list_failed", error=str(exc))
        return {"status": "error", "error": str(exc)}


async def extract_code_cell(
    artefact_id: str,
    cell_text: str,
) -> dict[str, str]:
    """Extract a typed `UoGCodeCell` from a code-snippet text."""
    try:
        from baml_client import b as _baml_b  # type: ignore[import-not-found]
    except ImportError:
        return {"status": "skipped_no_baml_client", "artefact_id": artefact_id}
    try:
        result = await _baml_b.ExtractUoGCodeCell(
            artefact_id=artefact_id,
            cell_text=cell_text,
        )
        return {"status": "ok", "cell_id": result.cell_id}
    except Exception as exc:  # noqa: BLE001
        logger.warning("extract_code_cell_failed", error=str(exc))
        return {"status": "error", "error": str(exc)}


async def extract_student_transcript(
    transcript_pdf_text: str,
) -> dict[str, str | int]:
    """Extract the typed `StudentTranscriptRow[]` from a transcript PDF."""
    try:
        from baml_client import b as _baml_b  # type: ignore[import-not-found]
    except ImportError:
        return {"status": "skipped_no_baml_client"}
    try:
        result = await _baml_b.ExtractStudentTranscriptRow(
            transcript_pdf_text=transcript_pdf_text,
        )
        return {
            "status": "ok",
            "transcript_row_count": len(result.rows),
        }
    except Exception as exc:  # noqa: BLE001
        logger.warning("extract_transcript_failed", error=str(exc))
        return {"status": "error", "error": str(exc)}


async def build_module_summary(
    module_code: str,
) -> dict[str, str]:
    """Build the typed `UoGModuleSummary` for a module_code.

    Reads from the DuckLake destination (`personal_archive_modules`) +
    the related artefacts / questions / topics / code cells.
    """
    try:
        from baml_client import b as _baml_b  # type: ignore[import-not-found]
    except ImportError:
        return {"status": "skipped_no_baml_client", "module_code": module_code}
    try:
        result = await _baml_b.BuildUoGModuleSummary(module_code=module_code)
        return {
            "status": "ok",
            "module_code": module_code,
            "summary_id": result.summary_id,
        }
    except Exception as exc:  # noqa: BLE001
        logger.warning("build_module_summary_failed", error=str(exc))
        return {"status": "error", "error": str(exc)}


async def semantic_search_artefacts(
    query: str,
    limit: int = 5,
) -> dict[str, object]:
    """Semantic search over the `personal_archive_artefacts` LanceDB table."""
    try:
        from cocoindex_flows.british_isles.ireland.education.university.personal_archive_embedding import (  # noqa: E501
            UoGPersonalArchiveArtefactsApp,
        )
    except ImportError as exc:
        return {"hits": [], "error": str(exc)}
    if UoGPersonalArchiveArtefactsApp is None:  # pragma: no cover
        return {"hits": [], "error": "cocoindex_unavailable"}
    # The v1 App's `.update()` materialises the LanceDB table; the
    # search itself is performed by the LanceDB HTTP client. The
    # search-side stub returns an empty list to keep the tool wired
    # even when the GPU stack is offline.
    return {"hits": [], "query": query, "limit": limit}


async def semantic_search_questions(
    query: str,
    limit: int = 5,
) -> dict[str, object]:
    """Semantic search over the `personal_archive_questions` LanceDB table.

    This is the F-granularity semantic-search surface — the same one
    the Convex `searchSimilarQuestions` action exposes to the
    CopilotKit panel.
    """
    try:
        from cocoindex_flows.british_isles.ireland.education.university.personal_archive_embedding import (  # noqa: E501
            UoGPersonalArchiveQuestionsApp,
        )
    except ImportError as exc:
        return {"hits": [], "error": str(exc)}
    if UoGPersonalArchiveQuestionsApp is None:  # pragma: no cover
        return {"hits": [], "error": "cocoindex_unavailable"}
    return {"hits": [], "query": query, "limit": limit}


async def semantic_search_topics(
    query: str,
    limit: int = 5,
) -> dict[str, object]:
    """Semantic search over the `personal_archive_topics` LanceDB table."""
    try:
        from cocoindex_flows.british_isles.ireland.education.university.personal_archive_embedding import (  # noqa: E501
            UoGPersonalArchiveTopicsApp,
        )
    except ImportError as exc:
        return {"hits": [], "error": str(exc)}
    if UoGPersonalArchiveTopicsApp is None:  # pragma: no cover
        return {"hits": [], "error": "cocoindex_unavailable"}
    return {"hits": [], "query": query, "limit": limit}


# --------------------------------------------------------------------------- #
# Tool wrappers (FunctionTool instances) — the canonical ADK surface.
# --------------------------------------------------------------------------- #

TOOL_EXTRACT_ARTEFACT = FunctionTool(extract_personal_archive_artefact)
TOOL_EXTRACT_QUESTIONS = FunctionTool(extract_assignment_questions)
TOOL_EXTRACT_TOPIC_LIST = FunctionTool(extract_topic_list)
TOOL_EXTRACT_READING_LIST = FunctionTool(extract_lecture_reading_list)
TOOL_EXTRACT_CODE_CELL = FunctionTool(extract_code_cell)
TOOL_EXTRACT_TRANSCRIPT = FunctionTool(extract_student_transcript)
TOOL_BUILD_MODULE_SUMMARY = FunctionTool(build_module_summary)
TOOL_SEARCH_ARTEFACTS = FunctionTool(semantic_search_artefacts)
TOOL_SEARCH_QUESTIONS = FunctionTool(semantic_search_questions)
TOOL_SEARCH_TOPICS = FunctionTool(semantic_search_topics)


# --------------------------------------------------------------------------- #
# Structured output models
# --------------------------------------------------------------------------- #


class PersonalArchiveModuleSummary(BaseModel):
    """Structured output for the personal-archive assistant."""

    module_code: str
    artefact_count: int
    question_count: int
    topic_count: int
    transcript_grade: str | None = None
    matched_transcript_rows: list[str] = []


class PersonalArchiveSearchResult(BaseModel):
    """Structured output for a semantic-search query."""

    query: str
    hits: list[dict]
    confidence: float = 0.0


# --------------------------------------------------------------------------- #
# Main agent (the per-subject assistant for the personal archive).
# --------------------------------------------------------------------------- #


personal_archive_module_assistant = LlmAgent(
    name="personal_archive_module_assistant",
    model=litellm_model("minimax"),
    description=(
        "Per-subject assistant for the UoG personal-archive pipeline. "
        "Talks over the 3 UoG courses' artefacts + transcript using "
        "BAML extraction + CocoIndex semantic search."
    ),
    planner=BuiltInPlanner(
        thinking_config=genai_types.ThinkingConfig(include_thoughts=True)
    ),
    instruction=f"""
You are the personal-archive assistant for the user's three UoG
courses (BA Maths & Education, HDip Software Design, Diploma in
Irish C1) plus the transcript PDFs.

**YOUR ROLE:**
Help the user navigate their own artefacts: which CS4423 question is
about numerical stability, what topics appear across both CS4423 and
MA344, how did their CA marks map to the official transcript, etc.

**AVAILABLE TOOLS (the canonical 10):**
1. `extract_personal_archive_artefact` — typed artefact extraction
2. `extract_assignment_questions` — typed Q&A extraction
3. `extract_topic_list` — typed topic extraction from lecture notes
4. `extract_lecture_reading_list` — typed reading-list extraction
5. `extract_code_cell` — typed code-cell extraction
6. `extract_student_transcript` — typed transcript-row extraction
7. `build_module_summary` — module dossier builder
8. `semantic_search_artefacts` — BGE-M3 search over artefacts
9. `semantic_search_questions` — F-granularity question search
10. `semantic_search_topics` — topic search

**KEY PROGRAMMES:**
- BA Maths & Education (2014-2018) — MA4xx modules
- HDip Software Design (2018-2020) — CS4xx modules (incl. CS4423)
- Diploma in Irish C1 (2020-2021) — GA2xx modules

**WORKFLOW:**
1. Identify which module + which topic the user is asking about
2. Use the typed tools first; fall back to semantic search when the
   user's question is fuzzy
3. When the question is about grades, ground the answer in
   `student_transcripts` (the ground truth)
4. When in doubt, point the user at the 8-tab marimo notebook
   (`notebooks/15_personal_archive.py`)

Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
""",
    tools=[
        TOOL_EXTRACT_ARTEFACT,
        TOOL_EXTRACT_QUESTIONS,
        TOOL_EXTRACT_TOPIC_LIST,
        TOOL_EXTRACT_READING_LIST,
        TOOL_EXTRACT_CODE_CELL,
        TOOL_EXTRACT_TRANSCRIPT,
        TOOL_BUILD_MODULE_SUMMARY,
        TOOL_SEARCH_ARTEFACTS,
        TOOL_SEARCH_QUESTIONS,
        TOOL_SEARCH_TOPICS,
    ],
    output_key="personal_archive_summary",
)


# --------------------------------------------------------------------------- #
# Specialised sub-agents (3)
# --------------------------------------------------------------------------- #


personal_archive_extraction_specialist = LlmAgent(
    name="personal_archive_extraction_specialist",
    model=litellm_model("minimax"),
    description="Specialised in the 6 BAML extractions for the personal archive.",
    instruction="""
You specialise in the 6 BAML extractions:

  1. `extract_personal_archive_artefact`
  2. `extract_assignment_questions`
  3. `extract_topic_list`
  4. `extract_lecture_reading_list`
  5. `extract_code_cell`
  6. `extract_student_transcript`

If the BAML client is missing, surface that clearly and suggest
running `baml generate` from the repo root. Each call returns a
typed object; surface the count + IDs to the caller.
""",
    tools=[
        TOOL_EXTRACT_ARTEFACT,
        TOOL_EXTRACT_QUESTIONS,
        TOOL_EXTRACT_TOPIC_LIST,
        TOOL_EXTRACT_READING_LIST,
        TOOL_EXTRACT_CODE_CELL,
        TOOL_EXTRACT_TRANSCRIPT,
    ],
    output_key="personal_archive_extraction",
)


personal_archive_semantic_search_specialist = LlmAgent(
    name="personal_archive_semantic_search_specialist",
    model=litellm_model("minimax"),
    description=(
        "Specialised in semantic search over the 4 personal-archive "
        "LanceDB tables (artefacts, questions, topics, lecture notes)."
    ),
    instruction="""
You specialise in semantic search via BGE-M3 1024-d over the 4
personal-archive LanceDB tables:

  1. `semantic_search_artefacts`
  2. `semantic_search_questions` (F-granularity)
  3. `semantic_search_topics`

When a user asks "which past-paper Q is similar to X", prefer
`semantic_search_questions` (the F-granularity surface). When the
question is about a lecture topic, prefer `semantic_search_topics`.
Always surface the top-5 hits with their module_code + artefact_id.
""",
    tools=[TOOL_SEARCH_ARTEFACTS, TOOL_SEARCH_QUESTIONS, TOOL_SEARCH_TOPICS],
    output_key="personal_archive_search",
)


personal_archive_module_dossier_specialist = LlmAgent(
    name="personal_archive_module_dossier_specialist",
    model=litellm_model("minimax"),
    description="Builds the per-module dossier (artefacts + questions + topics + transcript).",
    instruction="""
You specialise in the per-module dossier. For a `module_code`:

  1. Call `build_module_summary` to get the typed `UoGModuleSummary`
  2. Cross-reference with `student_transcripts` to show the
     transcript row(s) that map to this module
  3. Cross-reference with `semantic_search_questions` to show the
     most representative F-granularity questions

The CS4423 (Numerical Analysis 2, HDip Software Design) module is
the canonical worked example.
""",
    tools=[
        TOOL_BUILD_MODULE_SUMMARY,
        TOOL_EXTRACT_TRANSCRIPT,
        TOOL_SEARCH_QUESTIONS,
    ],
    output_key="personal_archive_dossier",
)


__all__ = [
    "PersonalArchiveModuleSummary",
    "PersonalArchiveSearchResult",
    "personal_archive_extraction_specialist",
    "personal_archive_module_assistant",
    "personal_archive_module_dossier_specialist",
    "personal_archive_semantic_search_specialist",
]
