"""UoG Exam Papers — CocoIndex v1 App.

Co-locates with `university_embedding.py` because the underlying
DuckLake table (`cianfhoghlaim.education.ie.uog_exam_papers`) is the
authenticated side of the same UoG corpus. Embeds the structured
`UoGExamPaper` rows into the `uog_exam_papers` LanceDB table with
BGE-M3 1024-dim embeddings on `question_text + topic + module_title`,
following the canonical v1 App pattern from
`openspec/specs/cianfhoghlaim-cocoindex-v1-migration/spec.md`.

The App degrades gracefully when CocoIndex is not installed (CI
runners without the GPU stack): the symbol still exists, but
`UoGExamPapersApp.update()` raises a clear runtime error.

Reference: openspec/changes/2026-08-23-uog-exam-papers-sso-v1/
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
    logger.warning("cocoindex_v1_not_available_for_uog_exam_embedding: %s", exc)
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

UOG_EXAM_DUCKLAKE_TABLE = "cianfhoghlaim.education.ie.uog_exam_papers"
LANCEDB_TABLE_NAME = "uog_exam_papers"


def _read_uog_exam_ducklake() -> list[dict[str, Any]]:
    """Read `UoGExamPaper` rows from the DuckLake destination."""
    try:
        import duckdb  # type: ignore[import-not-found]
    except ImportError:
        logger.warning("duckdb_not_available_for_uog_exam_embedding")
        return []

    db_path = os.environ.get("DUCKDB_PATH", "/tmp/cianfhoghlaim.duckdb")
    if not os.path.exists(db_path):
        return []
    try:
        con = duckdb.connect(db_path, read_only=True)
        rows = con.execute(f"SELECT * FROM {UOG_EXAM_DUCKLAKE_TABLE}").fetchall()
        columns = [d[0] for d in con.description]
        return [dict(zip(columns, r, strict=False)) for r in rows]
    except Exception as exc:
        logger.warning(
            "uog_exam_ducklake_read_failed",
            table=UOG_EXAM_DUCKLAKE_TABLE,
            error=str(exc),
        )
        return []


@dataclass
class UoGExamQuestionChunk:
    """One row in the `uog_exam_papers` LanceDB table.

    We embed at the **question level** so that semantic search can
    retrieve a specific Q&A pair, not a whole paper.
    """

    id: str
    module_code: str
    module_title: str
    academic_year: int
    sitting: str
    question_number: str
    question_text: str
    topic: str
    marks: int
    bloom_level: str
    programme_codes: str  # JSON array serialised to string
    source_url: str
    embedded_text: str
    embedding: Annotated[Any, "SentenceTransformerEmbedder"] = (  # type: ignore[valid-type]
        SentenceTransformerEmbedder(EMBED_MODEL)  # type: ignore[valid-type,call-arg]
    ) if COCOINDEX_AVAILABLE else None  # type: ignore[assignment]


# --------------------------------------------------------------------------- #
# The 1 v1 App (question-level embedding)
# --------------------------------------------------------------------------- #

if COCOINDEX_AVAILABLE:

    @coco.fn(memo=True)
    async def process_exam_question_chunk(
        row: dict[str, Any],
        id_gen: IdGenerator,  # type: ignore[valid-type]
        table: Any,  # lancedb.TableTarget
    ) -> None:
        """Process one exam-paper row, expanding its `questions[]` list."""
        embedder = await coco.use_context(EMBEDDER)  # type: ignore[arg-type]
        module_code = str(row.get("module_code", ""))
        module_title = str(row.get("module_title", "") or row.get("title", ""))
        academic_year = int(row.get("academic_year", 0) or 0)
        sitting = str(row.get("sitting", "AUTUMN"))
        source_url = str(row.get("source_url", ""))
        programme_codes = str(row.get("programme_codes", "") or "")

        for question in row.get("questions") or []:
            if not isinstance(question, dict):
                continue
            question_text = str(question.get("text", "") or "")
            if not question_text.strip():
                continue
            embedded_text = " ".join(
                filter(
                    None,
                    [
                        module_title,
                        module_code,
                        question_text,
                        str(question.get("topic", "")),
                    ],
                )
            )
            embedding = await embedder.embed(embedded_text)
            await table.declare_row(
                UoGExamQuestionChunk(
                    id=await id_gen.next_id(
                        f"{module_code}-{academic_year}-{sitting}-{question.get('number', '')}"
                    ),
                    module_code=module_code,
                    module_title=module_title,
                    academic_year=academic_year,
                    sitting=sitting,
                    question_number=str(question.get("number", "")),
                    question_text=question_text,
                    topic=str(question.get("topic", "")),
                    marks=int(question.get("marks", 0) or 0),
                    bloom_level=str(
                        question.get("bloom_level", "UNKNOWN") or "UNKNOWN"
                    ),
                    programme_codes=programme_codes,
                    source_url=source_url,
                    embedded_text=embedded_text,
                    embedding=embedding,
                )
            )

    @coco.fn
    async def uog_exam_papers_app_main() -> None:
        """App entry point — called by `cocoindex update`."""
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name=LANCEDB_TABLE_NAME,
            table_schema=await lancedb.TableSchema.from_class(
                UoGExamQuestionChunk,
                primary_key=["id"],
            ),
        )
        target_table.declare_vector_index(column="embedding")
        rows = _read_uog_exam_ducklake()
        id_gen = IdGenerator()
        # Canonical HNSW-DROP-THRESHOLD=50 batch size = 100 rows.
        for i in range(0, len(rows), 100):
            batch = rows[i : i + 100]
            await coco.map(
                process_exam_question_chunk,
                batch,
                id_gen,
                target_table,
            )

    UoGExamPapersApp = coco.App(
        coco.AppConfig(name="UoGExamPapersApp"),
        uog_exam_papers_app_main,
    )
else:
    UoGExamPapersApp = None  # type: ignore[assignment]


__all__ = [
    "COCOINDEX_AVAILABLE",
    "LANCEDB_TABLE_NAME",
    "UOG_EXAM_DUCKLAKE_TABLE",
    "UoGExamPapersApp",
    "UoGExamQuestionChunk",
]
