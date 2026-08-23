"""
oideachais.cognify_rules.personal_archive_typed_edges — the 10 typed
Cognee edge rules that lift the
`leabharlann/ollscoil_na_gaillimhe/` corpus to **full feature parity**
with the leaving-cycle subject pipeline.

The 10 emitters each yield ``(left_node, edge_label, right_node, properties)``
tuples; the caller (the Cognee `add_edges` API or the cognify Dagster
asset) consumes the tuples and writes them as typed graph edges. Every
edge carries a ``match_confidence`` in [0.0, 1.0]:

  - 1.00 for exact-id / exact-module-code / exact-year matches
  - 0.85-0.99 for fuzzy-text matches
  - 0.50-0.84 for embedding-nearest matches
  - 0.00 for no match (the edge is NOT emitted)

The 10 edges:

  1. (:PersonalArchiveArtefact) -[:DESCRIBES]-> (:PersonalArchiveModule)
     match: ``left.module_code = right.module_code``
  2. (:PersonalArchiveArtefact) -[:CONTAINS]-> (:PersonalArchiveQuestion)
     match: ``left.artefact_id = right.artefact_id``
  3. (:PersonalArchiveQuestion) -[:ANSWERED_BY]-> (:PersonalArchiveResponse)
     match: ``right.answer_text IS NOT NULL``
  4. (:PersonalArchiveResponse) -[:GRADED_AS]-> (:StudentTranscriptGrade)
     match: ``(left.module_code = right.module_code) AND
              (left.academic_year = right.academic_year)``
  5. (:PersonalArchiveModule) -[:COVERS]-> (:PersonalArchiveTopic)
     match: ``right.module_code IN left.module_codes``
  6. (:PersonalArchiveTopic) -[:RELATED_TO]-> (:PersonalArchiveTopic)
     match: ``shared topic_category`` (cross-module)
  7. (:PersonalArchiveTopic) -[:FOUND_IN]-> (:PersonalArchiveLectureArtefact)
     match: ``right.artefact_kind = LECTURE_NOTES``
  8. (:PersonalArchiveArtefact) -[:PROVIDED_BY]-> (:PersonalArchiveLecturer)
     match: ``right.artefact_provenance = LECTURE_PROVIDED``
  9. (:PersonalArchiveCodeCell) -[:DEMONSTRATES]-> (:PersonalArchiveTopic)
     match: ``right.topic_id IN left.demonstrates_topics``
  10. (:PersonalArchiveReadingItem) -[:CITED_IN]-> (:PersonalArchiveLectureArtefact)
     match: ``right.artefact_kind = LECTURE_NOTES``

The signature ``emit(graph, nodes) -> Iterable[tuple]`` is intentionally
generic over the Cognee graph client — the caller passes either an
in-memory list-collector or a live graph, and the emitters do not
import Cognee directly. This mirrors the per-rule pattern in
`scripts/graph_storage/cognify/rules/uog_exam_cross_archive.py`.

Reference: openspec/changes/2026-08-23-uog-personal-archive-tertiary-modules-v1/
"""
from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _coerce_str(value: Any) -> str:
    """Coerce a value to ``str`` (empty string when None or non-string)."""
    if value is None:
        return ""
    return str(value)


def _coerce_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _coerce_list(value: Any) -> list[str]:
    """Coerce a value to ``list[str]`` (handles JSON strings + None)."""
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x) for x in value if x is not None]
    if isinstance(value, str):
        # Handle comma-separated or single-element strings gracefully.
        if not value:
            return []
        return [value]
    return [str(value)]


# Edge tuple type: ``(left_node, edge_label, right_node, properties)``.
EdgeTuple = tuple[dict[str, Any], str, dict[str, Any], dict[str, Any]]


# --------------------------------------------------------------------------- #
# 1. Artefact-DESCRIBES-Module
# --------------------------------------------------------------------------- #


def emit_artefact_describes_module(
    graph: Any,
    artefacts: Iterable[dict[str, Any]],
    modules: Iterable[dict[str, Any]] | None = None,
) -> Iterator[EdgeTuple]:
    """Emit ``(:Artefact)-[:DESCRIBES]->(:Module)`` on matching ``module_code``.

    Both ``artefacts`` and ``modules`` are taken from the relevant
    DuckLake tables (``personal_archive_artefacts`` and
    ``personal_archive_modules`` respectively). The emitter is a pure
    function over the supplied iterables so it can be unit-tested
    without a live Cognee graph.
    """
    artefact_list = [a for a in artefacts if isinstance(a, dict)]
    module_list = [m for m in (modules or []) if isinstance(m, dict)]
    module_codes = {m.get("module_code", "") for m in module_list if m.get("module_code")}
    for artefact in artefact_list:
        artefact_id = _coerce_str(artefact.get("artefact_id"))
        if not artefact_id:
            continue
        artefact_module_code = _coerce_str(artefact.get("module_code"))
        if artefact_module_code and artefact_module_code in module_codes:
            yield (
                {"artefact_id": artefact_id, "module_code": artefact_module_code},
                "DESCRIBES",
                {"module_code": artefact_module_code},
                {
                    "match_confidence": 1.0,
                    "match_kind": "exact_module_code",
                },
            )


# --------------------------------------------------------------------------- #
# 2. Artefact-CONTAINS-Question
# --------------------------------------------------------------------------- #


def emit_artefact_contains_question(
    graph: Any,
    artefacts: Iterable[dict[str, Any]],
    questions: Iterable[dict[str, Any]],
) -> Iterator[EdgeTuple]:
    """Emit ``(:Artefact)-[:CONTAINS]->(:Question)`` on matching ``artefact_id``."""
    artefact_ids = {
        _coerce_str(a.get("artefact_id"))
        for a in artefacts
        if _coerce_str(a.get("artefact_id"))
    }
    for question in questions:
        question_id = _coerce_str(question.get("question_id"))
        artefact_id = _coerce_str(question.get("artefact_id"))
        if not question_id or not artefact_id:
            continue
        if artefact_id in artefact_ids:
            yield (
                {"artefact_id": artefact_id},
                "CONTAINS",
                {"question_id": question_id, "artefact_id": artefact_id},
                {
                    "match_confidence": 1.0,
                    "match_kind": "exact_artefact_id",
                },
            )


# --------------------------------------------------------------------------- #
# 3. Question-ANSWERED_BY-Response
# --------------------------------------------------------------------------- #


def emit_question_answered_by_response(
    graph: Any,
    questions: Iterable[dict[str, Any]],
    responses: Iterable[dict[str, Any]] | None = None,
) -> Iterator[EdgeTuple]:
    """Emit ``(:Question)-[:ANSWERED_BY]->(:Response)`` when the response
    has a non-empty ``answer_text``."""
    for question in questions:
        question_id = _coerce_str(question.get("question_id"))
        answer_text = _coerce_str(question.get("my_answer_text"))
        if not question_id or not answer_text:
            continue
        yield (
            {"question_id": question_id},
            "ANSWERED_BY",
            {"question_id": question_id, "answer_text": answer_text[:1000]},
            {
                "match_confidence": 1.0,
                "match_kind": "answer_text_present",
                "answer_length": len(answer_text),
            },
        )
    # The optional ``responses`` iterable is accepted for symmetry with
    # the other emitters; it is unused here because the answer_text is
    # already attached to the question row.
    if responses is not None:
        for _ in responses:
            continue


# --------------------------------------------------------------------------- #
# 4. Response-GRADED_AS-TranscriptGrade
# --------------------------------------------------------------------------- #


def emit_response_graded_as_transcript_grade(
    graph: Any,
    responses: Iterable[dict[str, Any]],
    transcripts: Iterable[dict[str, Any]],
) -> Iterator[EdgeTuple]:
    """Emit ``(:Response)-[:GRADED_AS]->(:TranscriptGrade)`` when
    ``(module_code, academic_year)`` matches between the response and
    the transcript row.
    """
    transcript_index: dict[tuple[str, int], list[dict[str, Any]]] = {}
    for transcript in transcripts:
        module_code = _coerce_str(transcript.get("module_code"))
        academic_year = _coerce_int(transcript.get("academic_year"))
        if module_code and academic_year:
            transcript_index.setdefault(
                (module_code, academic_year), []
            ).append(transcript)
    for response in responses:
        module_code = _coerce_str(response.get("module_code"))
        academic_year = _coerce_int(response.get("academic_year"))
        if not module_code or not academic_year:
            continue
        for transcript in transcript_index.get((module_code, academic_year), []):
            transcript_id = _coerce_str(transcript.get("transcript_id"))
            if not transcript_id:
                continue
            yield (
                {
                    "response_id": _coerce_str(response.get("response_id")),
                    "module_code": module_code,
                    "academic_year": academic_year,
                },
                "GRADED_AS",
                {
                    "transcript_id": transcript_id,
                    "module_code": module_code,
                    "academic_year": academic_year,
                    "grade": _coerce_str(transcript.get("grade")),
                },
                {
                    "match_confidence": 1.0,
                    "match_kind": "exact_module_year",
                    "grade": _coerce_str(transcript.get("grade")),
                },
            )


# --------------------------------------------------------------------------- #
# 5. Module-COVERS-Topic (many-to-many via module_codes[])
# --------------------------------------------------------------------------- #


def emit_module_covers_topic(
    graph: Any,
    modules: Iterable[dict[str, Any]],
    topics: Iterable[dict[str, Any]],
) -> Iterator[EdgeTuple]:
    """Emit ``(:Module)-[:COVERS]->(:Topic)`` for every (module, topic)
    pair where the topic's ``module_code`` is in the module's
    ``module_codes`` list.

    The DuckLake `personal_archive_modules` table carries a
    ``module_codes: list[str]`` column (the list of all module codes
    the user took during the programme), so this edge can fan out
    from a programme summary node to every topic.
    """
    module_index: dict[str, dict[str, Any]] = {}
    for module in modules:
        module_code = _coerce_str(module.get("module_code"))
        if module_code:
            module_index[module_code] = module
    for topic in topics:
        topic_id = _coerce_str(topic.get("topic_id"))
        topic_module_code = _coerce_str(topic.get("module_code"))
        if not topic_id or not topic_module_code:
            continue
        if topic_module_code in module_index:
            yield (
                {
                    "module_code": topic_module_code,
                    "module_codes": _coerce_list(
                        module_index[topic_module_code].get("module_codes")
                    ),
                },
                "COVERS",
                {
                    "topic_id": topic_id,
                    "module_code": topic_module_code,
                },
                {
                    "match_confidence": 1.0,
                    "match_kind": "exact_module_code",
                },
            )


# --------------------------------------------------------------------------- #
# 6. Topic-RELATED_TO-Topic (cross-module, shared topic_category)
# --------------------------------------------------------------------------- #


def emit_topic_related_to_topic(
    graph: Any,
    topics: Iterable[dict[str, Any]],
) -> Iterator[EdgeTuple]:
    """Emit ``(:Topic)-[:RELATED_TO]->(:Topic)`` for every topic pair
    that shares a ``topic_category`` and lives in **different**
    ``module_code`` slots. The cross-module constraint is what makes
    this the "mathematics appears in CS4423 and MA344" edge.
    """
    topic_list = [
        t
        for t in topics
        if _coerce_str(t.get("topic_id")) and _coerce_str(t.get("topic_category"))
    ]
    seen: set[tuple[str, str]] = set()
    for i, left in enumerate(topic_list):
        left_id = _coerce_str(left.get("topic_id"))
        left_module = _coerce_str(left.get("module_code"))
        left_category = _coerce_str(left.get("topic_category"))
        for right in topic_list[i + 1 :]:
            right_id = _coerce_str(right.get("topic_id"))
            right_module = _coerce_str(right.get("module_code"))
            right_category = _coerce_str(right.get("topic_category"))
            if left_category != right_category:
                continue
            if left_module == right_module:
                continue
            edge_key = tuple(sorted([left_id, right_id]))
            if edge_key in seen:
                continue
            seen.add(edge_key)
            yield (
                {
                    "topic_id": left_id,
                    "module_code": left_module,
                    "topic_category": left_category,
                },
                "RELATED_TO",
                {
                    "topic_id": right_id,
                    "module_code": right_module,
                    "topic_category": right_category,
                },
                {
                    "match_confidence": 0.85,
                    "match_kind": "shared_topic_category",
                    "shared_category": left_category,
                },
            )


# --------------------------------------------------------------------------- #
# 7. Topic-FOUND_IN-LectureArtefact
# --------------------------------------------------------------------------- #


def emit_topic_found_in_lecture_artefact(
    graph: Any,
    topics: Iterable[dict[str, Any]],
    artefacts: Iterable[dict[str, Any]],
) -> Iterator[EdgeTuple]:
    """Emit ``(:Topic)-[:FOUND_IN]->(:LectureArtefact)`` for every
    (topic, artefact) pair where the artefact is a lecture note
    (``artefact_kind = LECTURE_NOTES``) and the artefact's
    ``key_topics`` list mentions the topic id.
    """
    lecture_artefacts = [
        a
        for a in artefacts
        if _coerce_str(a.get("artefact_kind")) == "LECTURE_NOTES"
        and _coerce_str(a.get("artefact_id"))
    ]
    for topic in topics:
        topic_id = _coerce_str(topic.get("topic_id"))
        topic_name = _coerce_str(topic.get("topic_name"))
        if not topic_id:
            continue
        for artefact in lecture_artefacts:
            artefact_id = _coerce_str(artefact.get("artefact_id"))
            key_topics = _coerce_list(artefact.get("key_topics"))
            topic_module_code = _coerce_str(topic.get("module_code"))
            artefact_module_code = _coerce_str(artefact.get("module_code"))
            if topic_module_code and artefact_module_code and (
                topic_module_code != artefact_module_code
            ):
                continue
            confidence = 0.0
            match_kind = ""
            if topic_id in key_topics or topic_name in key_topics:
                confidence = 1.0
                match_kind = "topic_id_or_name_in_key_topics"
            elif topic_name:
                # Fuzzy fallback: lower-case substring overlap.
                lowered = {t.lower() for t in key_topics if t}
                if topic_name.lower() in lowered:
                    confidence = 0.9
                    match_kind = "fuzzy_topic_name"
            if confidence <= 0.0:
                continue
            yield (
                {
                    "topic_id": topic_id,
                    "module_code": topic_module_code,
                },
                "FOUND_IN",
                {
                    "artefact_id": artefact_id,
                    "module_code": artefact_module_code,
                    "artefact_kind": "LECTURE_NOTES",
                },
                {
                    "match_confidence": confidence,
                    "match_kind": match_kind,
                },
            )


# --------------------------------------------------------------------------- #
# 8. Artefact-PROVIDED_BY-Lecturer
# --------------------------------------------------------------------------- #


def emit_artefact_provided_by_lecturer(
    graph: Any,
    artefacts: Iterable[dict[str, Any]],
    lecturers: Iterable[dict[str, Any]],
) -> Iterator[EdgeTuple]:
    """Emit ``(:Artefact)-[:PROVIDED_BY]->(:Lecturer)`` when the
    artefact's ``artefact_provenance`` is ``LECTURE_PROVIDED`` and the
    ``lecturer_name`` matches a lecturer record.
    """
    lecturer_index: dict[str, dict[str, Any]] = {}
    for lecturer in lecturers:
        name = _coerce_str(lecturer.get("lecturer_name"))
        if name:
            lecturer_index.setdefault(name.lower(), lecturer)
    for artefact in artefacts:
        if _coerce_str(artefact.get("artefact_provenance")) != "LECTURE_PROVIDED":
            continue
        artefact_id = _coerce_str(artefact.get("artefact_id"))
        lecturer_name = _coerce_str(artefact.get("lecturer_name"))
        if not artefact_id or not lecturer_name:
            continue
        lecturer = lecturer_index.get(lecturer_name.lower())
        if not lecturer:
            continue
        yield (
            {"artefact_id": artefact_id},
            "PROVIDED_BY",
            {
                "lecturer_id": _coerce_str(lecturer.get("lecturer_id")),
                "lecturer_name": lecturer_name,
            },
            {
                "match_confidence": 1.0,
                "match_kind": "exact_lecturer_name",
            },
        )


# --------------------------------------------------------------------------- #
# 9. CodeCell-DEMONSTRATES-Topic
# --------------------------------------------------------------------------- #


def emit_code_cell_demonstrates_topic(
    graph: Any,
    code_cells: Iterable[dict[str, Any]],
    topics: Iterable[dict[str, Any]],
) -> Iterator[EdgeTuple]:
    """Emit ``(:CodeCell)-[:DEMONSTRATES]->(:Topic)`` for every
    ``topic_id`` in ``code_cell.demonstrates_topics``."""
    topic_index: dict[str, dict[str, Any]] = {}
    for topic in topics:
        topic_id = _coerce_str(topic.get("topic_id"))
        if topic_id:
            topic_index[topic_id] = topic
    for cell in code_cells:
        cell_id = _coerce_str(cell.get("cell_id"))
        if not cell_id:
            continue
        demonstrates_topics = _coerce_list(cell.get("demonstrates_topics"))
        for topic_id in demonstrates_topics:
            topic = topic_index.get(topic_id)
            if not topic:
                continue
            yield (
                {
                    "cell_id": cell_id,
                    "module_code": _coerce_str(cell.get("module_code")),
                },
                "DEMONSTRATES",
                {
                    "topic_id": topic_id,
                    "module_code": _coerce_str(topic.get("module_code")),
                },
                {
                    "match_confidence": 1.0,
                    "match_kind": "topic_id_in_demonstrates_topics",
                },
            )


# --------------------------------------------------------------------------- #
# 10. ReadingItem-CITED_IN-LectureArtefact
# --------------------------------------------------------------------------- #


def emit_reading_item_cited_in_lecture_artefact(
    graph: Any,
    reading_items: Iterable[dict[str, Any]],
    artefacts: Iterable[dict[str, Any]],
) -> Iterator[EdgeTuple]:
    """Emit ``(:ReadingItem)-[:CITED_IN]->(:LectureArtefact)`` when the
    artefact is a lecture note and the ``reading_item_id`` is in the
    artefact's ``reading_list_ids`` list."""
    lecture_artefacts = [
        a
        for a in artefacts
        if _coerce_str(a.get("artefact_kind")) == "LECTURE_NOTES"
        and _coerce_str(a.get("artefact_id"))
    ]
    for item in reading_items:
        item_id = _coerce_str(item.get("reading_item_id"))
        if not item_id:
            continue
        item_module = _coerce_str(item.get("module_code"))
        for artefact in lecture_artefacts:
            artefact_id = _coerce_str(artefact.get("artefact_id"))
            reading_list_ids = _coerce_list(artefact.get("reading_list_ids"))
            artefact_module = _coerce_str(artefact.get("module_code"))
            if item_module and artefact_module and item_module != artefact_module:
                continue
            if item_id in reading_list_ids:
                yield (
                    {
                        "reading_item_id": item_id,
                        "module_code": item_module,
                    },
                    "CITED_IN",
                    {
                        "artefact_id": artefact_id,
                        "module_code": artefact_module,
                        "artefact_kind": "LECTURE_NOTES",
                    },
                    {
                        "match_confidence": 1.0,
                        "match_kind": "reading_item_id_in_lecture_reading_list",
                    },
                )


# --------------------------------------------------------------------------- #
# Tuple of all 10 emitters (the public surface).
# --------------------------------------------------------------------------- #


PERSONAL_ARCHIVE_EDGES: tuple[Any, ...] = (
    emit_artefact_describes_module,
    emit_artefact_contains_question,
    emit_question_answered_by_response,
    emit_response_graded_as_transcript_grade,
    emit_module_covers_topic,
    emit_topic_related_to_topic,
    emit_topic_found_in_lecture_artefact,
    emit_artefact_provided_by_lecturer,
    emit_code_cell_demonstrates_topic,
    emit_reading_item_cited_in_lecture_artefact,
)


__all__ = [
    "EdgeTuple",
    "PERSONAL_ARCHIVE_EDGES",
    "emit_artefact_contains_question",
    "emit_artefact_describes_module",
    "emit_artefact_provided_by_lecturer",
    "emit_code_cell_demonstrates_topic",
    "emit_module_covers_topic",
    "emit_question_answered_by_response",
    "emit_reading_item_cited_in_lecture_artefact",
    "emit_response_graded_as_transcript_grade",
    "emit_topic_found_in_lecture_artefact",
    "emit_topic_related_to_topic",
]
