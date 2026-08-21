"""
Curriculum Translation Flow.

Auto-translates curriculum content to all Celtic languages on ingestion.

Translation Pipeline:
    Source (DuckDB) → Language Detection → Translation → Storage (LanceDB + DuckDB)

Models:
    - NLLB-200: Best for en↔ga, en↔cy, en↔gd (Facebook's 200-language model)
    - Opus-MT: Helsinki-NLP models for Celtic pairs
    - M2M-100: Fallback for less common pairs (gv, kw, br)

Target Languages:
    - ga: Irish
    - gd: Scottish Gaelic
    - cy: Welsh
    - gv: Manx
    - kw: Cornish
    - br: Breton
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Iterator

import structlog

logger = structlog.get_logger(__name__)

# CocoIndex imports (when available)
try:
    import cocoindex
    from cocoindex import DuckDBSource, LanceDBSink, Transform
    COCOINDEX_AVAILABLE = True
except ImportError:
    COCOINDEX_AVAILABLE = False


# ============================================================================
# Configuration
# ============================================================================

CELTIC_LANGUAGES = ["ga", "gd", "cy", "gv", "kw", "br"]

TRANSLATION_MODELS = {
    # NLLB-200 pairs (best quality for high-resource)
    ("en", "ga"): "facebook/nllb-200-distilled-600M",
    ("en", "gd"): "facebook/nllb-200-distilled-600M",
    ("en", "cy"): "facebook/nllb-200-distilled-600M",
    ("ga", "en"): "facebook/nllb-200-distilled-600M",
    # Opus-MT pairs (direct translation)
    ("en", "ga_opus"): "Helsinki-NLP/opus-mt-en-ga",
    ("ga", "en_opus"): "Helsinki-NLP/opus-mt-ga-en",
    ("en", "cy_opus"): "Helsinki-NLP/opus-mt-en-cy",
    # M2M-100 fallback (for low-resource)
    "fallback": "facebook/m2m100_418M",
}

NLLB_CODES = {
    "en": "eng_Latn",
    "ga": "gle_Latn",
    "gd": "gla_Latn",
    "cy": "cym_Latn",
    "br": "bre_Latn",
}


# ============================================================================
# Translation Transform
# ============================================================================

@dataclass
class CurriculumTranslationConfig:
    """Configuration for curriculum translation flow."""

    source_table: str = "education.curriculum_pages"
    output_table: str = "education.translations"
    lancedb_table: str = "oideachas.curriculum_multilingual"
    batch_size: int = 10
    max_text_length: int = 2000
    target_languages: list[str] = field(default_factory=lambda: CELTIC_LANGUAGES)


class CurriculumTranslationTransform:
    """
    Transform that translates curriculum content to Celtic languages.

    Flow:
        1. Read curriculum pages from DuckDB
        2. Detect source language
        3. Translate to all target languages
        4. Store translations in DuckDB and LanceDB
    """

    def __init__(self, config: CurriculumTranslationConfig | None = None):
        self.config = config or CurriculumTranslationConfig()
        self._translator = None

    def _get_translator(self):
        """Lazy-load translator."""
        if self._translator is None:
            from ..agents.translation import CelticTranslator
            self._translator = CelticTranslator()
        return self._translator

    def detect_language(self, text: str) -> str:
        """Detect source language of text."""
        # Simple heuristic based on common patterns
        irish_markers = ["an ", "na ", "ag ", "le ", "ó ", "ar ", "i ", "agus "]
        welsh_markers = ["y ", "yr ", "a ", "ac ", "yn ", "o ", "i ", "mae "]

        text_lower = text.lower()

        irish_score = sum(1 for m in irish_markers if m in text_lower)
        welsh_score = sum(1 for m in welsh_markers if m in text_lower)

        if irish_score > 3:
            return "ga"
        if welsh_score > 3:
            return "cy"

        return "en"  # Default to English

    def translate_to_celtic(
        self,
        text: str,
        source_lang: str,
    ) -> dict[str, dict[str, Any]]:
        """
        Translate text to all Celtic languages.

        Returns dict of {lang: {text, model, confidence}}
        """
        translator = self._get_translator()
        translations = {}

        # Truncate long texts
        text = text[: self.config.max_text_length]

        for target_lang in self.config.target_languages:
            if target_lang == source_lang:
                continue

            try:
                result = translator.translate_with_pivot(text, source_lang, target_lang)
                translations[target_lang] = {
                    "text": result.translated_text,
                    "model": result.model_used,
                    "confidence": result.confidence,
                }
            except (RuntimeError, ValueError, ConnectionError, TimeoutError) as e:
                logger.warning("translation_failed", source_lang=source_lang, target_lang=target_lang, error=str(e))
                translations[target_lang] = {
                    "text": "",
                    "model": "error",
                    "confidence": 0.0,
                    "error": str(e),
                }

        return translations

    def process_batch(
        self,
        rows: list[dict[str, Any]],
    ) -> Iterator[dict[str, Any]]:
        """
        Process a batch of curriculum pages.

        Yields translation records for storage.
        """
        for row in rows:
            text = row.get("content") or row.get("text", "")
            if not text or len(text) < 50:
                continue

            source_lang = row.get("language") or self.detect_language(text)
            page_id = row.get("id") or row.get("page_url", "unknown")

            translations = self.translate_to_celtic(text, source_lang)

            for lang, trans in translations.items():
                yield {
                    "source_id": page_id,
                    "source_lang": source_lang,
                    "source_text": text[:500],  # Truncated for storage
                    "target_lang": lang,
                    "translated_text": trans.get("text", ""),
                    "model_used": trans.get("model", "unknown"),
                    "confidence": trans.get("confidence", 0.0),
                }


# ============================================================================
# CocoIndex Flow Definition
# ============================================================================

def create_translation_flow(
    duckdb_path: str = "./storage/data/celtic_education.duckdb",
    lancedb_path: str = "./storage/data/lancedb",
) -> Any:
    """
    Create CocoIndex flow for curriculum translation.

    Flow:
        DuckDB (curriculum_pages) → Translate → DuckDB + LanceDB (multilingual)
    """
    if not COCOINDEX_AVAILABLE:
        raise ImportError("cocoindex not available - install with: pip install cocoindex")

    config = CurriculumTranslationConfig()
    transform = CurriculumTranslationTransform(config)

    @cocoindex.flow(name="curriculum_translation")
    def curriculum_translation_flow():
        # Source: Read curriculum pages
        source = DuckDBSource(
            database=duckdb_path,
            query=f"""
                SELECT
                    id,
                    page_url,
                    title,
                    content,
                    language,
                    source
                FROM {config.source_table}
                WHERE content IS NOT NULL
                  AND LENGTH(content) > 50
                  AND NOT EXISTS (
                      SELECT 1 FROM {config.output_table} t
                      WHERE t.source_id = {config.source_table}.id
                  )
                LIMIT 100
            """,
        )

        # Transform: Translate to Celtic languages
        translated = source.transform(
            Transform(
                name="translate_to_celtic",
                fn=transform.process_batch,
                batch_size=config.batch_size,
            )
        )

        # Sink: Store in DuckDB
        translated.sink(
            DuckDBSink(
                database=duckdb_path,
                table=config.output_table,
            )
        )

        # Sink: Store embeddings in LanceDB
        translated.sink(
            LanceDBSink(
                database=lancedb_path,
                table=config.lancedb_table,
                embedding_column="translated_text",
                embedding_model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            )
        )

    return curriculum_translation_flow


# ============================================================================
# Standalone Execution
# ============================================================================

async def run_translation_batch(
    duckdb_path: str = "./storage/data/celtic_education.duckdb",
    batch_size: int = 20,
) -> dict[str, int]:
    """
    Run translation for a batch of curriculum pages.

    Standalone function for use without CocoIndex.
    """
    import duckdb

    conn = duckdb.connect(duckdb_path)
    config = CurriculumTranslationConfig(batch_size=batch_size)
    transform = CurriculumTranslationTransform(config)

    # Ensure output table exists
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {config.output_table} (
            source_id VARCHAR,
            source_lang VARCHAR,
            source_text VARCHAR,
            target_lang VARCHAR,
            translated_text VARCHAR,
            model_used VARCHAR,
            confidence DOUBLE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Get untranslated pages
    query = f"""
        SELECT
            id,
            page_url,
            title,
            content,
            language,
            source
        FROM {config.source_table}
        WHERE content IS NOT NULL
          AND LENGTH(content) > 50
          AND id NOT IN (
              SELECT DISTINCT source_id FROM {config.output_table}
          )
        LIMIT {batch_size}
    """

    try:
        rows = conn.execute(query).fetchall()
        columns = ["id", "page_url", "title", "content", "language", "source"]
        pages = [dict(zip(columns, row)) for row in rows]
    except (duckdb.Error, ValueError, KeyError) as e:
        logger.warning("translation_query_failed", error=str(e))
        pages = []

    if not pages:
        return {"processed": 0, "translations": 0}

    # Process translations
    translation_count = 0
    for record in transform.process_batch(pages):
        conn.execute(f"""
            INSERT INTO {config.output_table}
            (source_id, source_lang, source_text, target_lang,
             translated_text, model_used, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [
            record["source_id"],
            record["source_lang"],
            record["source_text"],
            record["target_lang"],
            record["translated_text"],
            record["model_used"],
            record["confidence"],
        ])
        translation_count += 1

    conn.close()

    return {
        "processed": len(pages),
        "translations": translation_count,
    }


# ============================================================================
# CLI Entry Point
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run curriculum translation")
    parser.add_argument("--database", default="./storage/data/celtic_education.duckdb")
    parser.add_argument("--batch-size", type=int, default=20)
    args = parser.parse_args()

    result = asyncio.run(run_translation_batch(
        duckdb_path=args.database,
        batch_size=args.batch_size,
    ))

    print(f"Processed {result['processed']} pages, created {result['translations']} translations")
