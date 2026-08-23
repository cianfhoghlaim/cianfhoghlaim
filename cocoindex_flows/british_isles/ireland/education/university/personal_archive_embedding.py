"""UoG Personal Archive — 4 CocoIndex v1 Apps for the
`leabharlann/ollscoil_na_gaillimhe/` corpus + the
`cian_mac_an_déisigh_uí_liatháin/achievement/*transcript*.pdf` row.

The 4 v1 Apps embed at F-granularity (artefact, question, topic, lecture-notes)
into LanceDB using BGE-M3 1024-d, reading from the corresponding
`cianfhoghlaim.education.ie.personal_archive_*` DuckLake tables.

  1. `UoGPersonalArchiveArtefactsApp`  — every typed artefact
  2. `UoGPersonalArchiveQuestionsApp`  — every F-granularity question (the
                                          semantic-search surface for
                                          "what past-paper Q is similar to X")
  3. `UoGPersonalArchiveTopicsApp`     — every typed topic
  4. `UoGPersonalArchiveLectureNotesApp` — the subset of artefacts whose
                                          `artefact_kind = LECTURE_NOTES`
                                          (the 4th app isolates lecture-notes
                                          so the citation graph can point
                                          here directly)

Reads from the canonical DuckLake tables populated by the
`dlt_sources/filesystem/uog_personal_archive.py` source and the
`baml_src/british_isles/ireland/education/university/personal_archive_extraction.baml`
schema (parallel subagent). The Apps degrade gracefully when CocoIndex
is not installed (CI runners without the GPU stack).

Reference: openspec/changes/2026-08-23-uog-personal-archive-tertiary-modules-v1/
            specs/cianfhoghlaim-tertiary-personal-archive/spec.md
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Annotated, Any

import structlog

logger = structlog.get_logger(__name__)

try:
    import cocoindex as coco  # type: ignore[import-not-found]
    from cocoindex.connectors import lancedb  # type: ignore[import-not-found]
    from cocoindex.ops.sentence_transformers import (  # type: ignore[import-not-found]
        SentenceTransformerEmbedder,
    )
    from cocoindex.resources.id import IdGenerator  # type: ignore[import-not-found]

    COCOINDEX_AVAILABLE = True
except ImportError as exc:  # pragma: no cover - defensive
    logger.warning(
        "cocoindex_v1_not_available_for_uog_personal_archive: %s", exc
    )
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    lancedb = None  # type: ignore[assignment]
    SentenceTransformerEmbedder = None  # type: ignore[assignment]
    IdGenerator = None  # type: ignore[assignment]


from .._shared._lifespan import (  # noqa: E402
    EMBED_MODEL,
    EMBEDDER,
    LANCE_DB,
)


# --------------------------------------------------------------------------- #
# DuckLake table names (the contract with the parallel subagent)
# --------------------------------------------------------------------------- #

ARTEFACTS_DUCKLAKE_TABLE = (
    "cianfhoghlaim.education.ie.personal_archive_artefacts"
)
QUESTIONS_DUCKLAKE_TABLE = (
    "cianfhoghlaim.education.ie.personal_archive_questions"
)
TOPICS_DUCKLAKE_TABLE = (
    "cianfhoghlaim.education.ie.personal_archive_topics"
)


# --------------------------------------------------------------------------- #
# LanceDB table names (the 4 v1 Apps each own their own table)
# --------------------------------------------------------------------------- #

ARTEFACTS_LANCEDB_TABLE = "personal_archive_artefacts"
QUESTIONS_LANCEDB_TABLE = "personal_archive_questions"
TOPICS_LANCEDB_TABLE = "personal_archive_topics"
LECTURE_NOTES_LANCEDB_TABLE = "personal_archive_lecture_notes"


# --------------------------------------------------------------------------- #
# DuckLake read helper
# --------------------------------------------------------------------------- #


def _read_ducklake_table(table_name: str) -> list[dict[str, Any]]:
    """Read every row from the given DuckLake table.

    Falls back to an empty list when DuckDB or the local file is
    missing. The BAML / DLT side is owned by the parallel subagent;
    we only consume what they wrote.
    """
    try:
        import duckdb  # type: ignore[import-not-found]
    except ImportError:
        logger.warning("duckdb_not_available_for_personal_archive_embedding")
        return []
    db_path = os.environ.get(
        "OOG_LOCAL_DUCKDB_PATH", "/tmp/cianfhoghlaim.duckdb"
    )
    if not os.path.exists(db_path):
        return []
    try:
        con = duckdb.connect(db_path, read_only=True)
        rows = con.execute(f"SELECT * FROM {table_name}").fetchall()
        columns = [d[0] for d in con.description]
        return [dict(zip(columns, r, strict=False)) for r in rows]
    except Exception as exc:
        logger.warning(
            "personal_archive_ducklake_read_failed",
            table=table_name,
            error=str(exc),
        )
        return []


# --------------------------------------------------------------------------- #
# Row dataclasses (one per LanceDB table)
# --------------------------------------------------------------------------- #


@dataclass
class PersonalArchiveArtefactChunk:
    """One row in the `personal_archive_artefacts` LanceDB table."""

    id: str
    artefact_id: str
    artefact_title: str
    artefact_kind: str
    artefact_provenance: str
    module_code: str
    academic_year: int
    key_topics: str
    embedded_text: str
    embedding: Annotated[Any, "SentenceTransformerEmbedder"] = (  # type: ignore[valid-type]
        SentenceTransformerEmbedder(EMBED_MODEL)  # type: ignore[valid-type,call-arg]
    ) if COCOINDEX_AVAILABLE else None  # type: ignore[assignment]


@dataclass
class PersonalArchiveQuestionChunk:
    """One row in the `personal_archive_questions` LanceDB table.

    This is the F-granularity semantic-search surface: every typed
    question from `personal_archive_assignments → questions[]` (BAML
    `UoGQuestion`). The `embedded_text` is
    `question_text + my_answer_text + expected_topic` so a natural
    query like "what questions did I answer about numerical stability"
    returns the right hits.
    """

    id: str
    question_id: str
    artefact_id: str
    module_code: str
    question_text: str
    my_answer_text: str
    expected_topic: str
    bloom_level: str
    marks_available: int
    source_kind: str
    embedded_text: str
    embedding: Annotated[Any, "SentenceTransformerEmbedder"] = (  # type: ignore[valid-type]
        SentenceTransformerEmbedder(EMBED_MODEL)  # type: ignore[valid-type,call-arg]
    ) if COCOINDEX_AVAILABLE else None  # type: ignore[assignment]


@dataclass
class PersonalArchiveTopicChunk:
    """One row in the `personal_archive_topics` LanceDB table."""

    id: str
    topic_id: str
    topic_name: str
    topic_category: str
    module_code: str
    topic_description: str
    source_kind: str
    embedded_text: str
    embedding: Annotated[Any, "SentenceTransformerEmbedder"] = (  # type: ignore[valid-type]
        SentenceTransformerEmbedder(EMBED_MODEL)  # type: ignore[valid-type,call-arg]
    ) if COCOINDEX_AVAILABLE else None  # type: ignore[assignment]


@dataclass
class PersonalArchiveLectureNoteChunk:
    """One row in the `personal_archive_lecture_notes` LanceDB table.

    Filters the `personal_archive_artefacts` DuckLake rows down to
    `artefact_kind = 'LECTURE_NOTES'`. Used as the right-hand endpoint
    for the Cognee `Topic-FOUND_IN-LectureArtefact` and
    `ReadingItem-CITED_IN-LectureArtefact` edges.
    """

    id: str
    artefact_id: str
    artefact_title: str
    module_code: str
    lecturer_name: str
    lecture_week: int
    embedded_text: str
    embedding: Annotated[Any, "SentenceTransformerEmbedder"] = (  # type: ignore[valid-type]
        SentenceTransformerEmbedder(EMBED_MODEL)  # type: ignore[valid-type,call-arg]
    ) if COCOINDEX_AVAILABLE else None  # type: ignore[assignment]


# --------------------------------------------------------------------------- #
# The 4 v1 Apps
# --------------------------------------------------------------------------- #

if COCOINDEX_AVAILABLE:

    # --------------------------------------------------------------------- #
    # App 1 — UoGPersonalArchiveArtefactsApp
    # --------------------------------------------------------------------- #

    @coco.fn(memo=True)
    async def process_artefact_chunk(
        row: dict[str, Any],
        id_gen: IdGenerator,  # type: ignore[valid-type]
        table: Any,  # lancedb.TableTarget
    ) -> None:
        """Process one `personal_archive_artefacts` DuckLake row."""
        embedder = await coco.use_context(EMBEDDER)  # type: ignore[arg-type]
        artefact_id = str(row.get("artefact_id", "") or "")
        if not artefact_id:
            return
        title = str(row.get("artefact_title", "") or "")
        embedded_text = str(row.get("embedded_text", "") or "")[:8000]
        key_topics = row.get("key_topics") or []
        if isinstance(key_topics, list):
            topics_str = ", ".join(
                t for t in key_topics if isinstance(t, str)
            )
        else:
            topics_str = str(key_topics)
        text_blob = " ".join(filter(None, [title, embedded_text, topics_str]))
        if not text_blob.strip():
            return
        embedding = await embedder.embed(text_blob)
        await table.declare_row(
            PersonalArchiveArtefactChunk(
                id=await id_gen.next_id(f"pa-artefact-{artefact_id}"),
                artefact_id=artefact_id,
                artefact_title=title,
                artefact_kind=str(
                    row.get("artefact_kind", "OTHER") or "OTHER"
                ),
                artefact_provenance=str(
                    row.get("artefact_provenance", "PERSONAL_SUBMISSION") or
                    "PERSONAL_SUBMISSION"
                ),
                module_code=str(row.get("module_code", "") or ""),
                academic_year=int(row.get("academic_year", 0) or 0),
                key_topics=topics_str,
                embedded_text=text_blob,
                embedding=embedding,
            )
        )

    @coco.fn
    async def uog_personal_archive_artefacts_app_main() -> None:
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name=ARTEFACTS_LANCEDB_TABLE,
            table_schema=await lancedb.TableSchema.from_class(
                PersonalArchiveArtefactChunk,
                primary_key=["id"],
            ),
        )
        target_table.declare_vector_index(column="embedding")
        rows = _read_ducklake_table(ARTEFACTS_DUCKLAKE_TABLE)
        id_gen = IdGenerator()
        for i in range(0, len(rows), 100):
            batch = rows[i : i + 100]
            await coco.map(process_artefact_chunk, batch, id_gen, target_table)

    UoGPersonalArchiveArtefactsApp = coco.App(
        coco.AppConfig(name="UoGPersonalArchiveArtefactsApp"),
        uog_personal_archive_artefacts_app_main,
    )

    # --------------------------------------------------------------------- #
    # App 2 — UoGPersonalArchiveQuestionsApp (F-granularity)
    # --------------------------------------------------------------------- #

    @coco.fn(memo=True)
    async def process_question_chunk(
        row: dict[str, Any],
        id_gen: IdGenerator,  # type: ignore[valid-type]
        table: Any,  # lancedb.TableTarget
    ) -> None:
        """Process one `personal_archive_questions` DuckLake row.

        This is the row-level (F) embedding surface. The
        `personal_archive_questions` DuckLake table is already
        F-granular (one row per question, populated by BAML
        `UoGQuestion` extraction over each `UoGAssignment`).
        """
        embedder = await coco.use_context(EMBEDDER)  # type: ignore[arg-type]
        question_id = str(row.get("question_id", "") or "")
        if not question_id:
            return
        question_text = str(row.get("question_text", "") or "")
        my_answer_text = str(row.get("my_answer_text", "") or "")[:4000]
        expected_topic = str(row.get("expected_topic", "") or "")
        text_blob = " ".join(
            filter(None, [question_text, my_answer_text, expected_topic])
        )
        if not text_blob.strip():
            return
        embedding = await embedder.embed(text_blob)
        await table.declare_row(
            PersonalArchiveQuestionChunk(
                id=await id_gen.next_id(f"pa-q-{question_id}"),
                question_id=question_id,
                artefact_id=str(row.get("artefact_id", "") or ""),
                module_code=str(row.get("module_code", "") or ""),
                question_text=question_text,
                my_answer_text=my_answer_text,
                expected_topic=expected_topic,
                bloom_level=str(
                    row.get("bloom_level", "UNKNOWN") or "UNKNOWN"
                ),
                marks_available=int(row.get("marks_available", 0) or 0),
                source_kind=str(
                    row.get("source_kind", "PERSONAL_SUBMISSION") or
                    "PERSONAL_SUBMISSION"
                ),
                embedded_text=text_blob,
                embedding=embedding,
            )
        )

    @coco.fn
    async def uog_personal_archive_questions_app_main() -> None:
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name=QUESTIONS_LANCEDB_TABLE,
            table_schema=await lancedb.TableSchema.from_class(
                PersonalArchiveQuestionChunk,
                primary_key=["id"],
            ),
        )
        target_table.declare_vector_index(column="embedding")
        rows = _read_ducklake_table(QUESTIONS_DUCKLAKE_TABLE)
        id_gen = IdGenerator()
        for i in range(0, len(rows), 100):
            batch = rows[i : i + 100]
            await coco.map(process_question_chunk, batch, id_gen, target_table)

    UoGPersonalArchiveQuestionsApp = coco.App(
        coco.AppConfig(name="UoGPersonalArchiveQuestionsApp"),
        uog_personal_archive_questions_app_main,
    )

    # --------------------------------------------------------------------- #
    # App 3 — UoGPersonalArchiveTopicsApp
    # --------------------------------------------------------------------- #

    @coco.fn(memo=True)
    async def process_topic_chunk(
        row: dict[str, Any],
        id_gen: IdGenerator,  # type: ignore[valid-type]
        table: Any,  # lancedb.TableTarget
    ) -> None:
        """Process one `personal_archive_topics` DuckLake row."""
        embedder = await coco.use_context(EMBEDDER)  # type: ignore[arg-type]
        topic_id = str(row.get("topic_id", "") or "")
        if not topic_id:
            return
        topic_name = str(row.get("topic_name", "") or "")
        topic_category = str(row.get("topic_category", "") or "")
        text_blob = " ".join(filter(None, [topic_name, topic_category]))
        if not text_blob.strip():
            return
        embedding = await embedder.embed(text_blob)
        await table.declare_row(
            PersonalArchiveTopicChunk(
                id=await id_gen.next_id(f"pa-topic-{topic_id}"),
                topic_id=topic_id,
                topic_name=topic_name,
                topic_category=topic_category,
                module_code=str(row.get("module_code", "") or ""),
                topic_description=str(
                    row.get("topic_description", "") or ""
                ),
                source_kind=str(
                    row.get("source_kind", "PERSONAL_SUBMISSION") or
                    "PERSONAL_SUBMISSION"
                ),
                embedded_text=text_blob,
                embedding=embedding,
            )
        )

    @coco.fn
    async def uog_personal_archive_topics_app_main() -> None:
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name=TOPICS_LANCEDB_TABLE,
            table_schema=await lancedb.TableSchema.from_class(
                PersonalArchiveTopicChunk,
                primary_key=["id"],
            ),
        )
        target_table.declare_vector_index(column="embedding")
        rows = _read_ducklake_table(TOPICS_DUCKLAKE_TABLE)
        id_gen = IdGenerator()
        for i in range(0, len(rows), 100):
            batch = rows[i : i + 100]
            await coco.map(process_topic_chunk, batch, id_gen, target_table)

    UoGPersonalArchiveTopicsApp = coco.App(
        coco.AppConfig(name="UoGPersonalArchiveTopicsApp"),
        uog_personal_archive_topics_app_main,
    )

    # --------------------------------------------------------------------- #
    # App 4 — UoGPersonalArchiveLectureNotesApp (filtered slice)
    # --------------------------------------------------------------------- #

    @coco.fn(memo=True)
    async def process_lecture_note_chunk(
        row: dict[str, Any],
        id_gen: IdGenerator,  # type: ignore[valid-type]
        table: Any,  # lancedb.TableTarget
    ) -> None:
        """Process one `personal_archive_artefacts` row whose
        `artefact_kind = LECTURE_NOTES`. Mirrors
        `process_artefact_chunk` but writes to the
        `personal_archive_lecture_notes` LanceDB table instead.
        """
        if str(row.get("artefact_kind", "")) != "LECTURE_NOTES":
            return
        embedder = await coco.use_context(EMBEDDER)  # type: ignore[arg-type]
        artefact_id = str(row.get("artefact_id", "") or "")
        if not artefact_id:
            return
        title = str(row.get("artefact_title", "") or "")
        embedded_text = str(row.get("embedded_text", "") or "")[:8000]
        text_blob = " ".join(filter(None, [title, embedded_text]))
        if not text_blob.strip():
            return
        embedding = await embedder.embed(text_blob)
        await table.declare_row(
            PersonalArchiveLectureNoteChunk(
                id=await id_gen.next_id(f"pa-lecture-{artefact_id}"),
                artefact_id=artefact_id,
                artefact_title=title,
                module_code=str(row.get("module_code", "") or ""),
                lecturer_name=str(row.get("lecturer_name", "") or ""),
                lecture_week=int(row.get("lecture_week", 0) or 0),
                embedded_text=text_blob,
                embedding=embedding,
            )
        )

    @coco.fn
    async def uog_personal_archive_lecture_notes_app_main() -> None:
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name=LECTURE_NOTES_LANCEDB_TABLE,
            table_schema=await lancedb.TableSchema.from_class(
                PersonalArchiveLectureNoteChunk,
                primary_key=["id"],
            ),
        )
        target_table.declare_vector_index(column="embedding")
        rows = _read_ducklake_table(ARTEFACTS_DUCKLAKE_TABLE)
        id_gen = IdGenerator()
        for i in range(0, len(rows), 100):
            batch = rows[i : i + 100]
            await coco.map(
                process_lecture_note_chunk, batch, id_gen, target_table
            )

    UoGPersonalArchiveLectureNotesApp = coco.App(
        coco.AppConfig(name="UoGPersonalArchiveLectureNotesApp"),
        uog_personal_archive_lecture_notes_app_main,
    )

else:
    UoGPersonalArchiveArtefactsApp = None  # type: ignore[assignment]
    UoGPersonalArchiveQuestionsApp = None  # type: ignore[assignment]
    UoGPersonalArchiveTopicsApp = None  # type: ignore[assignment]
    UoGPersonalArchiveLectureNotesApp = None  # type: ignore[assignment]


__all__ = [
    "ARTEFACTS_DUCKLAKE_TABLE",
    "ARTEFACTS_LANCEDB_TABLE",
    "COCOINDEX_AVAILABLE",
    "LECTURE_NOTES_LANCEDB_TABLE",
    "PersonalArchiveArtefactChunk",
    "PersonalArchiveLectureNoteChunk",
    "PersonalArchiveQuestionChunk",
    "PersonalArchiveTopicChunk",
    "QUESTIONS_DUCKLAKE_TABLE",
    "QUESTIONS_LANCEDB_TABLE",
    "TOPICS_DUCKLAKE_TABLE",
    "TOPICS_LANCEDB_TABLE",
    "UoGPersonalArchiveArtefactsApp",
    "UoGPersonalArchiveLectureNotesApp",
    "UoGPersonalArchiveQuestionsApp",
    "UoGPersonalArchiveTopicsApp",
]
