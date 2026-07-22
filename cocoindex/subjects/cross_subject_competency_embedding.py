"""Cross-subject competency v1 CocoIndex Embedding App (canonical R1–R4).

Embeds the 5 NCCA Key Competencies × 8 NCCA subjects × 4 levels × 2 languages
= 320 cross-subject mastery vectors into LanceDB. The table is
`cianfhoghlaim.lc.cross_subject.competencies`.

The 5 NCCA Key Competencies are the foundation of the cross-subject
mastery narrative: Communicating, Personal Effectiveness,
Information Processing, Working with Others, Critical & Creative
Thinking.

Follows the canonical v1 pattern (R1–R4 conformance contract):

- **R1** — `from .._shared._lifespan import shared_lifespan` (delegates to the
  shared lifespan in `_lifespan.py`)
- **R2** — Imports the canonical `LANCE_DB` + `EMBEDDER` from `_lifespan`;
  declares `cross_subject_competency_app = coco.App(coco.AppConfig(name=...))`
  at module scope.
- **R3** — `lancedb.mount_table_target(LANCE_DB, ...)` for the output target.
- **R4** — `target_table.declare_vector_index(column="embedding")`.

Per `openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/
ncca-leaving-cert-root-pdfs/spec.md` + `cianfhoghlaim-leaving-cert-portal/
spec.md` Requirement R3.

Migrated to R1-R4 conformance by the
`2026-07-09-cocoindex-v1-remaining-apps-v1` change.
"""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from typing import Annotated

import structlog
from numpy.typing import NDArray

logger = structlog.get_logger(__name__)

try:
    import cocoindex as coco  # type: ignore[import-not-found]
    from cocoindex.connectors import lancedb  # type: ignore[import-not-found]
    from cocoindex.resources.id import IdGenerator  # type: ignore[import-not-found]

    COCOINDEX_AVAILABLE = True
except ImportError as e:
    logger.warning("cocoindex_v1_not_available: %s", e)
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    lancedb = None  # type: ignore[assignment]
    IdGenerator = None  # type: ignore[assignment]


# R1: shared lifespan + canonical ContextKeys from `._lifespan`.
from .._shared._lifespan import (  # noqa: E402
    EMBEDDER,
    LANCE_DB,
    shared_lifespan,
)


# 8 NCCA subjects × 5 NCCA Key Competencies × 4 levels × 2 languages
NCCA_SUBJECTS = (
    "mathematics",
    "applied_mathematics",
    "chemistry",
    "geography",
    "history",
    "english",
    "gaeilge",
    "computer_science",
)

NCCA_KEY_COMPETENCIES = (
    "information-processing",
    "communicating",
    "working-with-others",
    "personal-effectiveness",
    "critical-creative-thinking",
)

NCCA_LEVELS = ("hl", "ol", "fl", "jc")  # Higher, Ordinary, Foundation, Junior Cycle
LANGUAGES = ("en", "ga")

# Number of cross-subject mastery vectors: 8 × 5 × 4 × 2 = 320 rows
TOTAL_COMPETENCY_VECTORS = (
    len(NCCA_SUBJECTS) * len(NCCA_KEY_COMPETENCIES)
    * len(NCCA_LEVELS) * len(LANGUAGES)
)

LANCEDB_TABLE = "cianfhoghlaim.lc.cross_subject.competencies"


# ============================================================================
# Row schema (the @dataclass that drives the LanceDB target table)
# ============================================================================

if COCOINDEX_AVAILABLE:

    @dataclass
    class CrossSubjectCompetency:
        """One cross-subject mastery vector for the LanceDB target table."""

        id: str
        subject: str
        competency: str
        level: str
        language: str
        tri_de_dana: str
        text: str
        embedding: Annotated[NDArray, EMBEDDER]


# ============================================================================
# v1 App: CrossSubjectCompetencyEmbedding
# ============================================================================

if COCOINDEX_AVAILABLE:

    @coco.fn(memo=True)
    async def process_competency_row(
        subject: str,
        competency: str,
        level: str,
        language: str,
        target_table: lancedb.TableTarget[CrossSubjectCompetency],  # type: ignore[type-var]
    ) -> None:
        """Embed one (subject, competency, level, language) tuple into LanceDB."""
        embedder = await coco.use_context(EMBEDDER)  # type: ignore[arg-type]
        tri_de_dana = ""
        # The 3 Key Competencies that map to the Túatha Dé Danann are
        # emphasised in the embedding text (the canonical Celtic theming).
        if competency == "communicating":
            tri_de_dana = "Brigid (poetry + healing)"
        elif competency == "personal-effectiveness":
            tri_de_dana = "Dian Cecht (medicine)"
        elif competency == "information-processing":
            tri_de_dana = "Ogma (eloquence + learning)"

        text = (
            f"NCCA Key Competency '{competency}' for subject '{subject}' "
            f"at level '{level}' (language: {language}). "
            f"Cross-subject mastery vector. {tri_de_dana}"
        )
        vec = await embedder.embed(text)  # type: ignore[attr-defined]
        chunk_id = f"{subject}__{competency}__{level}__{language}"
        target_table.declare_row(
            row=CrossSubjectCompetency(
                id=chunk_id,
                subject=subject,
                competency=competency,
                level=level,
                language=language,
                tri_de_dana=tri_de_dana,
                text=text,
                embedding=vec,
            )
        )

    @coco.fn
    async def cross_subject_competency_app_main() -> None:
        """Cross-subject competency v1 CocoIndex App entry point.

        Walks the 8 subjects × 5 competencies × 4 levels × 2 languages
        = 320 cross-subject mastery vectors, embeds each via the
        shared BGE-M3 embedder, and writes to
        `cianfhoghlaim.lc.cross_subject.competencies`.
        """
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name=LANCEDB_TABLE,
            table_schema=await lancedb.TableSchema.from_class(
                CrossSubjectCompetency, primary_key=["id"]
            ),
        )
        target_table.declare_vector_index(column="embedding")

        # The 320 vectors are emitted in 100-row batches
        # (the canonical HNSW-DROP-THRESHOLD rule).
        all_keys = [
            (subject, competency, level, language)
            for subject in NCCA_SUBJECTS
            for competency in NCCA_KEY_COMPETENCIES
            for level in NCCA_LEVELS
            for language in LANGUAGES
        ]
        for subject, competency, level, language in all_keys:
            await process_competency_row(
                subject, competency, level, language, target_table
            )

    cross_subject_competency_app = coco.App(
        coco.AppConfig(name="CrossSubjectCompetencyEmbedding"),
        cross_subject_competency_app_main,
    )

else:
    cross_subject_competency_app = None
    logger.warning("cross_subject_competency_app_disabled: cocoindex_not_available")


# ============================================================================
# Ad-hoc update helper (the public API used by Dagster assets)
# ============================================================================


async def update_cross_subject_competencies_async() -> None:
    if not COCOINDEX_AVAILABLE or cross_subject_competency_app is None:
        logger.warning("cross_subject_competency_update_skipped")
        return

    async def _run_update() -> None:
        logger.info("cross_subject_competency_update_started")
        try:
            await cross_subject_competency_app.update()
            logger.info("cross_subject_competency_update_complete")
        except Exception as e:
            logger.error("cross_subject_competency_update_failed: %s", e)
            raise

    await _run_update()


def update_cross_subject_competencies() -> None:
    asyncio.run(update_cross_subject_competencies_async())


if __name__ == "__main__":
    update_cross_subject_competencies()