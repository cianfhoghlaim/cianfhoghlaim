"""
Stage 5 of the 6-stage PDF processing pipeline: semantic chunking.

Chunks the validated BAML records + diagram regions into semantically
meaningful units, embeds them with BGE-M3, and writes to LanceDB.

Per `oideachais-pdf-processing/spec.md`:
- Syllabus: chunk by topic (one chunk per SyllabusTopic)
- Past paper: chunk by question (one chunk per PastExamQuestion)
- Marking scheme: chunk by marking point (one chunk per MarkingPoint)
- Diagrams: one chunk per detected figure region (with caption as text)

Chunk size: 256-1024 tokens (within BGE-M3 sweet spot)
Embedder: BAAI/bge-m3 multilingual (1024-dim, batched 100+)
Sink: lancedb://oideachais.pdf_processing_chunks (IVF_HNSW + FTS)
"""

from __future__ import annotations

import logging
import warnings
from dataclasses import dataclass, field
from typing import Any, Literal

from .diagram_detector import DiagramResult

logger = logging.getLogger(__name__)

warnings.warn(
    "pdf_processing.semantic_chunker is the v4 implementation of Stage 5. "
    "It is experimental; the actual CocoIndex v1 + BGE-M3 calls are "
    "stubbed.",
    UserWarning,
    stacklevel=2,
)

ChunkType = Literal["topic", "question", "marking_point", "diagram", "formula", "text"]


@dataclass
class ChunkResult:
    """A single semantic chunk."""

    chunk_id: str
    doc_id: str
    chunk_type: ChunkType
    text: str
    embedding: list[float] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "chunk_type": self.chunk_type,
            "text": self.text,
            "metadata": self.metadata,
            "embedding_dim": len(self.embedding),
        }


class SemanticChunker:
    """Stage 5 semantic chunker.

    Per the v4 spec:
    - Syllabus → chunk by topic (one per SyllabusTopic)
    - Past paper → chunk by question (one per PastExamQuestion)
    - Marking scheme → chunk by marking point (one per MarkingPoint)
    - Diagrams → one chunk per figure region (with caption as text)
    - Embedder: BAAI/bge-m3 (1024-dim)
    - Batched 100+ for HNSW efficiency
    - Sink: lancedb://oideachais.pdf_processing_chunks
    """

    # BGE-M3 sweet spot
    MIN_CHUNK_TOKENS = 256
    MAX_CHUNK_TOKENS = 1024
    BGE_DIM = 1024
    EMBED_BATCH_SIZE = 100

    def __init__(self, embedder: str = "BAAI/bge-m3"):
        """Initialize the semantic chunker.

        Args:
            embedder: HF ID for the embedder model
                (default: `BAAI/bge-m3`)
        """
        self.embedder = embedder

    def chunk(
        self,
        document_type: Literal["syllabus", "past_paper", "marking_scheme"],
        validated_records: list[dict[str, Any]],
        page_diagrams: list[list[DiagramResult]],
    ) -> tuple[list[ChunkResult], dict[str, int]]:
        """Chunk the validated records + diagram regions.

        Args:
            document_type: Type of PDF being chunked
            validated_records: BAML records from Stage 4 (validated)
            page_diagrams: Per-page diagram lists from Stage 2

        Returns:
            Tuple of:
            - chunks: List of ChunkResult records
            - n_by_type: Dict mapping chunk_type → count
        """
        chunks: list[ChunkResult] = []
        n_by_type: dict[str, int] = {}

        if document_type == "syllabus":
            chunks, n_by_type = self._chunk_syllabus(validated_records)
        elif document_type == "past_paper":
            chunks, n_by_type = self._chunk_past_paper(validated_records)
        elif document_type == "marking_scheme":
            chunks, n_by_type = self._chunk_marking_scheme(validated_records)

        # Always append diagram chunks
        diagram_chunks, diagram_n = self._chunk_diagrams(page_diagrams)
        chunks.extend(diagram_chunks)
        n_by_type["diagram"] = diagram_n

        logger.info(
            f"Stage 5 — Chunked into {len(chunks)} chunks: {n_by_type}"
        )
        return chunks, n_by_type

    def _chunk_syllabus(
        self,
        records: list[dict[str, Any]],
    ) -> tuple[list[ChunkResult], dict[str, int]]:
        """Chunk syllabus: one chunk per SyllabusTopic."""
        chunks: list[ChunkResult] = []
        for i, record in enumerate(records):
            topic_name = record.get("name", f"topic_{i}")
            text = self._syllabus_topic_to_text(record)
            chunk = ChunkResult(
                chunk_id=f"syllabus_topic_{i}",
                doc_id=record.get("subject", "unknown"),
                chunk_type="topic",
                text=text,
                metadata={
                    "topic_name": topic_name,
                    "weight_pct": record.get("weightPct", 0),
                    "n_outcomes": len(record.get("learningOutcomes", [])),
                },
            )
            chunks.append(chunk)
        return chunks, {"topic": len(chunks)}

    def _chunk_past_paper(
        self,
        records: list[dict[str, Any]],
    ) -> tuple[list[ChunkResult], dict[str, int]]:
        """Chunk past paper: one chunk per PastExamQuestion."""
        chunks: list[ChunkResult] = []
        for i, record in enumerate(records):
            question_number = record.get("questionNumber", i)
            text = self._past_paper_question_to_text(record)
            chunk = ChunkResult(
                chunk_id=f"past_paper_q_{question_number}",
                doc_id=f"{record.get('subject', 'unknown')}_{record.get('year', 'unknown')}",
                chunk_type="question",
                text=text,
                metadata={
                    "question_number": question_number,
                    "topic": record.get("topic"),
                    "subtopic": record.get("subtopic"),
                    "marks": record.get("marks", 0),
                    "is_optional": record.get("isOptional", False),
                    "topic_validated": record.get("topic_validated", False),
                    "topic_match": record.get("topic_match"),
                },
            )
            chunks.append(chunk)
        return chunks, {"question": len(chunks)}

    def _chunk_marking_scheme(
        self,
        records: list[dict[str, Any]],
    ) -> tuple[list[ChunkResult], dict[str, int]]:
        """Chunk marking scheme: one chunk per MarkingPoint."""
        chunks: list[ChunkResult] = []
        for i, record in enumerate(records):
            qn = record.get("questionNumber", i)
            part = record.get("partLabel", "")
            chunk_id = f"marking_point_{qn}_{part or 'main'}"
            text = self._marking_point_to_text(record)
            chunk = ChunkResult(
                chunk_id=chunk_id,
                doc_id=f"{record.get('subject', 'unknown')}_{record.get('year', 'unknown')}",
                chunk_type="marking_point",
                text=text,
                metadata={
                    "question_number": qn,
                    "part_label": part,
                    "mark_value": record.get("markValue", 0),
                    "mark_type": record.get("markType", "A1"),
                    "is_optional": record.get("isOptional", False),
                    "requires_formula_image": record.get("requiresFormulaImage", False),
                },
            )
            chunks.append(chunk)
        return chunks, {"marking_point": len(chunks)}

    def _chunk_diagrams(
        self,
        page_diagrams: list[list[DiagramResult]],
    ) -> tuple[list[ChunkResult], int]:
        """Chunk diagrams: one chunk per figure region."""
        chunks: list[ChunkResult] = []
        n = 0
        for page_number, diagrams in enumerate(page_diagrams, start=1):
            for j, d in enumerate(diagrams):
                if d.diagram_type not in ("figure", "table", "formula"):
                    continue
                chunk = ChunkResult(
                    chunk_id=f"diagram_p{page_number}_{j}",
                    doc_id=f"page_{page_number}",
                    chunk_type="diagram" if d.diagram_type == "figure" else "formula",
                    text=d.caption or d.caption_en or "(no caption)",
                    metadata={
                        "page_number": page_number,
                        "diagram_type": d.diagram_type,
                        "bbox": list(d.bbox),
                        "caption_en": d.caption_en,
                        "caption_ga": d.caption_ga,
                        "confidence": d.confidence,
                    },
                )
                chunks.append(chunk)
                n += 1
        return chunks, n

    def _syllabus_topic_to_text(self, record: dict[str, Any]) -> str:
        """Convert a SyllabusTopic BAML record to chunk text."""
        parts = [
            f"Topic: {record.get('name', '')}",
            f"Description: {record.get('description', '')}",
            "Learning Outcomes:",
            *[f"  - {lo}" for lo in record.get("learningOutcomes", [])],
        ]
        return "\n".join(parts)

    def _past_paper_question_to_text(self, record: dict[str, Any]) -> str:
        """Convert a PastExamQuestion BAML record to chunk text."""
        parts = [
            f"Question {record.get('questionNumber', '?')}",
            f"Topic: {record.get('topic', '')}",
            f"Marks: {record.get('marks', 0)}",
        ]
        if record.get("subtopic"):
            parts.append(f"Subtopic: {record['subtopic']}")
        if record.get("isOptional"):
            parts.append("(Optional)")
        parts.append(f"Question: {record.get('questionText', '')}")
        return "\n".join(parts)

    def _marking_point_to_text(self, record: dict[str, Any]) -> str:
        """Convert a MarkingPoint BAML record to chunk text."""
        qn = record.get("questionNumber", "?")
        part = record.get("partLabel", "")
        parts = [
            f"Marking Point Q{qn}{part}",
            f"Marks: {record.get('markValue', 0)} ({record.get('markType', 'A1')})",
            f"Answer: {record.get('answerText', '')}",
        ]
        alts = record.get("alternativeAnswers", [])
        if alts:
            parts.append("Alternative answers:")
            parts.extend(f"  - {a}" for a in alts)
        if record.get("requiresFormulaImage"):
            parts.append("(Requires formula image — see diagram_chunks)")
        return "\n".join(parts)
