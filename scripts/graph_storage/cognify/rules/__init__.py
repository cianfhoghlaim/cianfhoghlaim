"""scripts.graph_storage.cognify.rules — the Cognee cross-archive edge rules.

This package hosts the per-corpus Cognee edge emitters that lift
the personal-archive / leabharlann / university / BIEP corpora to
the canonical typed-edge surface. Each rule is a pure function
over input iterables so it can be unit-tested without a live Cognee
graph.

The 10 typed personal-archive edges are imported with a try/except
wrapper because the parallel subagent owns the file
``personal_archive_typed_edges.py``. The wrapper lets the rest of
the cognify pipeline import this package without crashing if the
parallel workstream hasn't landed its file yet.

Reference: openspec/changes/2026-08-23-uog-personal-archive-tertiary-modules-v1/
"""

from __future__ import annotations

import structlog

logger = structlog.get_logger(__name__)

# The 10 typed personal-archive edges are owned by the parallel
# subagent (per the WS7 in
# openspec/changes/2026-08-23-uog-personal-archive-tertiary-modules-v1/tasks.md).
# We import them here with a try/except wrapper so the package can
# still be imported if the file is missing (CI doesn't crash).

try:  # noqa: F401, F403 — wildcard re-export of the 10 emitters
    from .personal_archive_typed_edges import (  # type: ignore[import-not-found]
        PERSONAL_ARCHIVE_EDGES,
        emit_artefact_contains_question,
        emit_artefact_describes_module,
        emit_artefact_provided_by_lecturer,
        emit_code_cell_demonstrates_topic,
        emit_module_covers_topic,
        emit_question_answered_by_response,
        emit_reading_item_cited_in_lecture_artefact,
        emit_response_graded_as_transcript_grade,
        emit_topic_found_in_lecture_artefact,
        emit_topic_related_to_topic,
    )

    _PERSONAL_ARCHIVE_AVAILABLE = True
except ImportError as exc:
    logger.warning(
        "personal_archive_typed_edges_import_failed",
        error=str(exc),
        hint=(
            "The parallel subagent owns personal_archive_typed_edges.py; "
            "this wrapper keeps the package importable until it lands."
        ),
    )
    _PERSONAL_ARCHIVE_AVAILABLE = False
    PERSONAL_ARCHIVE_EDGES: tuple = ()

__all__ = [
    "PERSONAL_ARCHIVE_EDGES",
    "_PERSONAL_ARCHIVE_AVAILABLE",
]
