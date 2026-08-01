"""
Celtic Translation Pipeline for Curriculum Content.

Auto-translates curriculum content to all Celtic languages on ingestion:
- Irish (ga)
- Scottish Gaelic (gd)
- Welsh (cy)
- Manx (gv)
- Cornish (kw)
- Breton (br)

Translation Models:
- NLLB-200: Best for en↔ga, en↔cy, en↔gd (Facebook's 200-language model)
- Opus-MT: Helsinki-NLP models for Celtic pairs
- M2M-100: Fallback for less common pairs (gv, kw, br)

Usage:
    from agents.translation import CelticTranslator

    translator = CelticTranslator()
    translations = await translator.translate_to_all_celtic(
        text="The student will learn...",
        source_lang="en"
    )
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any
from enum import Enum


class CelticLanguage(str, Enum):
    """Celtic languages supported for translation."""

    ENGLISH = "en"
    IRISH = "ga"
    SCOTTISH_GAELIC = "gd"
    WELSH = "cy"
    MANX = "gv"
    CORNISH = "kw"
    BRETON = "br"

    @classmethod
    def celtic_only(cls) -> list["CelticLanguage"]:
        """Return only Celtic languages (excluding English)."""
        return [cls.IRISH, cls.SCOTTISH_GAELIC, cls.WELSH, cls.MANX, cls.CORNISH, cls.BRETON]


# NLLB-200 language codes (BCP-47 style)
NLLB_CODES = {
    "en": "eng_Latn",
    "ga": "gle_Latn",
    "gd": "gla_Latn",
    "cy": "cym_Latn",
    "br": "bre_Latn",
    # Manx and Cornish not in NLLB-200
}

# Opus-MT model mappings (Helsinki-NLP)
OPUS_MT_MODELS = {
    ("en", "ga"): "Helsinki-NLP/opus-mt-en-ga",
    ("ga", "en"): "Helsinki-NLP/opus-mt-ga-en",
    ("en", "cy"): "Helsinki-NLP/opus-mt-en-cy",
    ("cy", "en"): "Helsinki-NLP/opus-mt-cy-en",
    ("en", "gd"): "Helsinki-NLP/opus-mt-en-gd",
    ("gd", "en"): "Helsinki-NLP/opus-mt-gd-en",
}


@dataclass
class TranslationResult:
    """Result of a translation operation."""

    source_text: str
    source_lang: str
    target_lang: str
    translated_text: str
    model_used: str
    confidence: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MultilingualTranslation:
    """Translations to multiple languages."""

    source_text: str
    source_lang: str
    translations: dict[str, TranslationResult] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "source_text": self.source_text,
            "source_lang": self.source_lang,
            "translations": {
                lang: {
                    "text": result.translated_text,
                    "model": result.model_used,
                    "confidence": result.confidence,
                }
                for lang, result in self.translations.items()
            },
        }


class CelticTranslator:
    """
    Translator for Celtic languages using multiple model backends.

    Priority:
    1. NLLB-200 for high-resource pairs (en↔ga, en↔cy, en↔gd)
    2. Opus-MT for direct translation models
    3. M2M-100 for fallback and low-resource pairs
    4. Pivot through English for Celtic↔Celtic when needed
    """

    def __init__(
        self,
        primary_model: str = "facebook/nllb-200-distilled-600M",
        fallback_model: str = "facebook/m2m100_418M",
        device: str = "cpu",
        batch_size: int = 8,
    ):
        self.primary_model = primary_model
        self.fallback_model = fallback_model
        self.device = device
        self.batch_size = batch_size

        self._nllb_pipeline = None
        self._m2m_pipeline = None
        self._opus_models: dict[tuple[str, str], Any] = {}

    def _get_nllb_pipeline(self):
        """Lazy-load NLLB-200 pipeline."""
        if self._nllb_pipeline is None:
            from transformers import pipeline

            self._nllb_pipeline = pipeline(
                "translation",
                model=self.primary_model,
                device=self.device,
            )
        return self._nllb_pipeline

    def _get_m2m_pipeline(self):
        """Lazy-load M2M-100 pipeline."""
        if self._m2m_pipeline is None:
            from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

            self._m2m_tokenizer = M2M100Tokenizer.from_pretrained(self.fallback_model)
            self._m2m_model = M2M100ForConditionalGeneration.from_pretrained(self.fallback_model)
        return self._m2m_model, self._m2m_tokenizer

    def _get_opus_model(self, source_lang: str, target_lang: str):
        """Lazy-load Opus-MT model for language pair."""
        key = (source_lang, target_lang)
        if key not in self._opus_models:
            model_name = OPUS_MT_MODELS.get(key)
            if model_name:
                from transformers import pipeline

                self._opus_models[key] = pipeline(
                    "translation",
                    model=model_name,
                    device=self.device,
                )
            else:
                self._opus_models[key] = None
        return self._opus_models[key]

    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
    ) -> TranslationResult:
        """
        Translate text between languages.

        Args:
            text: Source text to translate
            source_lang: Source language code (e.g., 'en', 'ga')
            target_lang: Target language code

        Returns:
            TranslationResult with translated text and metadata
        """
        if source_lang == target_lang:
            return TranslationResult(
                source_text=text,
                source_lang=source_lang,
                target_lang=target_lang,
                translated_text=text,
                model_used="passthrough",
                confidence=1.0,
            )

        # Try Opus-MT first (best quality for specific pairs)
        opus_pipeline = self._get_opus_model(source_lang, target_lang)
        if opus_pipeline:
            result = opus_pipeline(text, max_length=512)
            return TranslationResult(
                source_text=text,
                source_lang=source_lang,
                target_lang=target_lang,
                translated_text=result[0]["translation_text"],
                model_used=OPUS_MT_MODELS[(source_lang, target_lang)],
                confidence=0.9,
            )

        # Try NLLB-200
        if source_lang in NLLB_CODES and target_lang in NLLB_CODES:
            pipeline = self._get_nllb_pipeline()
            result = pipeline(
                text,
                src_lang=NLLB_CODES[source_lang],
                tgt_lang=NLLB_CODES[target_lang],
                max_length=512,
            )
            return TranslationResult(
                source_text=text,
                source_lang=source_lang,
                target_lang=target_lang,
                translated_text=result[0]["translation_text"],
                model_used=self.primary_model,
                confidence=0.85,
            )

        # Fallback to M2M-100
        model, tokenizer = self._get_m2m_pipeline()
        tokenizer.src_lang = source_lang
        encoded = tokenizer(text, return_tensors="pt")
        generated = model.generate(
            **encoded,
            forced_bos_token_id=tokenizer.get_lang_id(target_lang),
            max_length=512,
        )
        translated = tokenizer.decode(generated[0], skip_special_tokens=True)

        return TranslationResult(
            source_text=text,
            source_lang=source_lang,
            target_lang=target_lang,
            translated_text=translated,
            model_used=self.fallback_model,
            confidence=0.7,
        )

    def translate_with_pivot(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        pivot_lang: str = "en",
    ) -> TranslationResult:
        """
        Translate using pivot language for unsupported direct pairs.

        For example: Irish → Welsh via English pivot.
        """
        if source_lang == target_lang:
            return self.translate(text, source_lang, target_lang)

        # Try direct translation first
        try:
            return self.translate(text, source_lang, target_lang)
        except Exception:
            pass

        # Pivot through English
        intermediate = self.translate(text, source_lang, pivot_lang)
        final = self.translate(intermediate.translated_text, pivot_lang, target_lang)

        return TranslationResult(
            source_text=text,
            source_lang=source_lang,
            target_lang=target_lang,
            translated_text=final.translated_text,
            model_used=f"{intermediate.model_used} → {final.model_used}",
            confidence=intermediate.confidence * final.confidence,
            metadata={"pivot_lang": pivot_lang},
        )

    async def translate_to_all_celtic(
        self,
        text: str,
        source_lang: str = "en",
    ) -> MultilingualTranslation:
        """
        Translate text to all Celtic languages.

        Args:
            text: Source text
            source_lang: Source language code

        Returns:
            MultilingualTranslation with all translations
        """
        result = MultilingualTranslation(
            source_text=text,
            source_lang=source_lang,
        )

        # Translate to each Celtic language concurrently
        async def translate_one(target_lang: str) -> tuple[str, TranslationResult]:
            translation = self.translate_with_pivot(text, source_lang, target_lang)
            return target_lang, translation

        tasks = [
            translate_one(lang.value)
            for lang in CelticLanguage.celtic_only()
            if lang.value != source_lang
        ]

        translations = await asyncio.gather(*tasks)

        for lang, translation in translations:
            result.translations[lang] = translation

        return result

    def translate_batch(
        self,
        texts: list[str],
        source_lang: str,
        target_lang: str,
    ) -> list[TranslationResult]:
        """
        Translate multiple texts efficiently.

        Uses batching for better throughput.
        """
        results = []

        # Process in batches
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]

            # Use NLLB for batch translation if available
            if source_lang in NLLB_CODES and target_lang in NLLB_CODES:
                pipeline = self._get_nllb_pipeline()
                translations = pipeline(
                    batch,
                    src_lang=NLLB_CODES[source_lang],
                    tgt_lang=NLLB_CODES[target_lang],
                    max_length=512,
                )

                for text, trans in zip(batch, translations):
                    results.append(
                        TranslationResult(
                            source_text=text,
                            source_lang=source_lang,
                            target_lang=target_lang,
                            translated_text=trans["translation_text"],
                            model_used=self.primary_model,
                            confidence=0.85,
                        )
                    )
            else:
                # Fall back to individual translations
                for text in batch:
                    results.append(self.translate(text, source_lang, target_lang))

        return results


class CurriculumTranslationPipeline:
    """
    Pipeline for translating curriculum content on ingestion.

    Integrates with the DLT pipeline to automatically translate
    curriculum pages as they are ingested.
    """

    def __init__(
        self,
        translator: CelticTranslator | None = None,
        target_languages: list[str] | None = None,
    ):
        self.translator = translator or CelticTranslator()
        self.target_languages = target_languages or [
            lang.value for lang in CelticLanguage.celtic_only()
        ]

    async def process_curriculum_page(
        self,
        page: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Process a curriculum page and add translations.

        Args:
            page: Curriculum page dict with 'content' and 'language' fields

        Returns:
            Page dict with 'translations' field added
        """
        content = page.get("content", "")
        source_lang = page.get("language", "en")

        if not content:
            return page

        translations = await self.translator.translate_to_all_celtic(
            content, source_lang
        )

        page["translations"] = translations.to_dict()["translations"]
        return page

    def process_batch(
        self,
        pages: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Process a batch of curriculum pages.

        Uses asyncio for concurrent translation.
        """
        async def process_all():
            tasks = [self.process_curriculum_page(page) for page in pages]
            return await asyncio.gather(*tasks)

        return asyncio.run(process_all())


# Quality assessment for translations
def assess_translation_quality(
    source: str,
    translation: str,
    source_lang: str,
    target_lang: str,
) -> dict[str, float]:
    """
    Assess translation quality using multiple metrics.

    Returns:
        Dictionary with quality scores
    """
    # Length ratio (translations should be similar length)
    source_len = len(source.split())
    trans_len = len(translation.split())
    length_ratio = min(source_len, trans_len) / max(source_len, trans_len, 1)

    # Check for common issues
    issues = []

    # Empty translation
    if not translation.strip():
        issues.append("empty_translation")

    # Too short (likely incomplete)
    if trans_len < source_len * 0.3:
        issues.append("too_short")

    # Too long (likely repetition or garbage)
    if trans_len > source_len * 3:
        issues.append("too_long")

    # Repetition detection
    words = translation.split()
    if len(words) > 5:
        unique_ratio = len(set(words)) / len(words)
        if unique_ratio < 0.3:
            issues.append("repetition")

    quality_score = length_ratio
    if issues:
        quality_score *= 0.5 ** len(issues)

    return {
        "quality_score": quality_score,
        "length_ratio": length_ratio,
        "source_words": source_len,
        "translation_words": trans_len,
        "issues": issues,
    }
