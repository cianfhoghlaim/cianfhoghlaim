"""Cross-subject competency v1 CocoIndex Embedding App.

Embeds the 5 NCCA Key Competencies × 8 NCCA subjects × 3 levels × 2 languages
= 240 cross-subject mastery vectors into LanceDB. The table is
`oideachais.lc.cross_subject.competencies.<level>_<lang>`.

The 5 NCCA Key Competencies are the foundation of the Brown Ajah
theming: they are the 5 surviving gifts of the Tuatha Dé Danann
(Communicating = Brigid, Personal Effectiveness = Dian Cecht,
Information Processing = Ogma, Working with Others + Critical &
Creative Thinking = Lugh's samildanach).

Follows the canonical v1 pattern from `leabharlann_embedding.py` and
`_lifespan.py`.

Per `openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/
ncca-leaving-cert-root-pdfs/spec.md` + `cianfhoghlaim-leaving-cert-portal/
spec.md` Requirement R3.
"""

from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator
from typing import Annotated, Any

import structlog

logger = structlog.get_logger(__name__)

try:
    import cocoindex as coco
    from cocoindex.connectors import lancedb
    from cocoindex.ops.sentence_transformers import (
        SentenceTransformerEmbedder,
    )
    from cocoindex.resources.id import IdGenerator

    COCOINDEX_AVAILABLE = True
except ImportError as e:
    logger.warning("cocoindex_v1_not_available: %s", e)
    COCOINDEX_AVAILABLE = False
    coco = None
    lancedb = None
    SentenceTransformerEmbedder = None
    IdGenerator = None


from ._lifespan import (  # noqa: E402
    LANCE_DB,
    EMBEDDER,
    RESOLVED_FILE_REGISTRY,
    lifespan,
)


# 8 NCCA subjects × 5 NCCA Key Competencies × 3 levels × 2 languages
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

# The Trí Dé Dána → 3 Key Competencies emphasis (per docs/BROWN_AJAH_THEMING.md)
TRI_DE_DANA_MAPPING = {
    "communicating": "Brigid (poetry + healing)",
    "personal-effectiveness": "Dian Cecht (medicine)",
    "information-processing": "Ogma (eloquence + learning)",
}


if COCOINDEX_AVAILABLE:
    app = coco.App(
        name="cross_subject_competency_embedding",
        description="Embeds the 5 NCCA Key Competencies × 8 subjects × 3 levels × 2 languages = 240 cross-subject mastery vectors into LanceDB",
    )

    @coco.lifespan
    async def cross_subject_competency_lifespan() -> AsyncIterator[None]:
        async with lifespan():
            yield

    @coco.fn
    def process_cross_subject_competency(
        content_key: Annotated[str, coco.ResolvedKey],
        content: Annotated[dict, coco.source_files],
    ) -> Annotated[dict, lancedb.target_fields]:
        """Process one cross-subject competency into a LanceDB row.

        The 240 vectors are:
          - 8 NCCA subjects
          - × 5 NCCA Key Competencies (information-processing, communicating,
            working-with-others, personal-effectiveness, critical-creative-thinking)
          - × 4 levels (hl, ol, fl, jc)
          - × 2 languages (en, ga)
          = 320 vectors

        Per the Brown Ajah theming, the 3 Key Competencies that map to
        the Trí Dé Dána are emphasised:
          - communicating ↔ Brigid (poetry + healing)
          - personal-effectiveness ↔ Dian Cecht (medicine)
          - information-processing ↔ Ogma (eloquence + learning, inventor of Ogham)
        """
        subject, competency, level, language = content_key.split("__")
        return {
            "id": content_key,
            "subject": subject,
            "competency": competency,
            "level": level,
            "language": language,
            "tri_de_dana": TRI_DE_DANA_MAPPING.get(competency, ""),
            "content": str(content),
            "metadata": {
                "subject_color": f"var(--ci-subject-{subject.replace('_', '-')})",
                "competency_color": f"var(--ci-competency-{competency.split('-')[0]})",
            },
        }

    @app.target(
        name="oideachais.lc.cross_subject.competencies",
        fields={
            "id": str,
            "subject": str,
            "competency": str,
            "level": str,
            "language": str,
            "tri_de_dana": str,
            "content": str,
            "metadata": dict,
        },
    )
    def cross_subject_table(
        embedder: Annotated[Any, EMBEDDER],
        lance_db: Annotated[Any, LANCE_DB],
    ) -> lancedb.TableTarget:
        return lancedb.TableTarget(
            db=lance_db,
            table_name="oideachais.lc.cross_subject.competencies",
            embedding=embedder.embedding(),
        )
else:
    app = None
    logger.warning("cross_subject_competency_app_disabled: cocoindex_not_available")


async def update_cross_subject_competencies_async() -> None:
    if not COCOINDEX_AVAILABLE or app is None:
        logger.warning("cross_subject_competency_update_skipped")
        return

    async def _run_update() -> None:
        logger.info("cross_subject_competency_update_started")
        try:
            await app.update()
            logger.info("cross_subject_competency_update_complete")
        except Exception as e:
            logger.error("cross_subject_competency_update_failed: %s", e)
            raise

    await _run_update()


def update_cross_subject_competencies() -> None:
    asyncio.run(update_cross_subject_competencies_async())


if __name__ == "__main__":
    update_cross_subject_competencies()