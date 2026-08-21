"""
Celtic Translation Agent - Multi-language translation.

Supports translation between Celtic languages and English:
- Irish ↔ English
- Scottish Gaelic ↔ English
- Welsh ↔ English
- Inter-Celtic (Irish ↔ Scottish Gaelic, Welsh ↔ Breton)

Uses multiple translation backends:
- OPUS-MT (Helsinki-NLP)
- M2M100 (Facebook)
- NLLB-200 (Meta)
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from .config import config, get_language_name, get_translation_models


# Structured output models
class TranslationRequest(BaseModel):
    """A translation request between Celtic languages."""

    source_text: str = Field(description="Text to translate")
    source_language: str = Field(description="Source language code (ga, gd, cy, etc.)")
    target_language: str = Field(description="Target language code")
    domain: Optional[str] = Field(
        default=None, description="Domain hint (legal, medical, folklore, etc.)"
    )
    preserve_formatting: bool = Field(default=True, description="Whether to preserve formatting")


class TranslationResult(BaseModel):
    """Result of a Celtic language translation."""

    translated_text: str = Field(description="Translated text")
    source_language: str = Field(description="Source language code")
    target_language: str = Field(description="Target language code")
    model_used: str = Field(description="Translation model used")
    confidence: float = Field(description="Confidence score (0-1)")
    terminology_notes: Optional[list[str]] = Field(
        default=None, description="Notes on terminology choices"
    )


class TerminologyLookup(BaseModel):
    """Terminology lookup result from Téarma.ie."""

    term_ga: str = Field(description="Irish term")
    term_en: str = Field(description="English term")
    domain: Optional[str] = Field(default=None, description="Domain/field")
    definition: Optional[str] = Field(default=None, description="Definition if available")


# Agent instructions
MODEL_SELECTOR_INSTRUCTION = """You are a Celtic translation model selector.

Given a translation request, select the best model:

1. OPUS-MT (Helsinki-NLP)
   - Best for: Irish ↔ English, Welsh ↔ English
   - Strengths: High quality, fast
   - Limitations: Limited language pairs

2. M2M100 (Facebook)
   - Best for: Any pair including inter-Celtic
   - Strengths: 100 languages, cross-lingual
   - Limitations: Larger, slower

3. NLLB-200 (Meta)
   - Best for: Low-resource languages, long text
   - Strengths: 200 languages, quality
   - Limitations: Very large

Consider:
- Language pair support
- Text length and domain
- Quality vs speed requirements

Output the recommended model and reasoning."""


TRANSLATOR_INSTRUCTION = """You are a Celtic language translation expert.

Translate the provided text between Celtic languages with high accuracy.

Guidelines:
1. Preserve meaning and nuance
2. Handle Celtic-specific features:
   - Initial mutations (lenition, eclipsis)
   - VSO word order
   - Prepositional pronouns
   - Dialect variations
3. Use appropriate register (formal/informal)
4. Maintain terminology consistency
5. Note any ambiguities or alternatives

For technical/specialized text:
- Use Téarma.ie terminology where applicable
- Note domain-specific terms

For folklore/cultural text:
- Preserve cultural references
- Explain untranslatable concepts

Output the translation with any relevant notes."""


TERMINOLOGY_INSTRUCTION = """You are a Celtic terminology specialist.

When translating technical or specialized text, look up terms in:
- Téarma.ie (Irish terminology database)
- An Seotal (Scottish Gaelic education terms)
- Y Termiadur Addysg (Welsh education terms)

Provide:
- Standard translations for technical terms
- Domain-specific alternatives
- Notes on usage

Ensure consistency with official terminology databases."""


# Utility functions for translation
async def translate_text(
    text: str,
    source_lang: str,
    target_lang: str,
    domain: Optional[str] = None,
) -> TranslationResult:
    """
    Translate text between Celtic languages.

    Args:
        text: Text to translate
        source_lang: Source language code (ga, gd, cy, etc.)
        target_lang: Target language code
        domain: Optional domain hint

    Returns:
        TranslationResult with translated text and metadata
    """
    # Get available models for this pair
    available_models = get_translation_models(source_lang, target_lang)
    selected_model = available_models[0] if available_models else "m2m100"

    # Placeholder implementation - would use actual model
    return TranslationResult(
        translated_text=f"[Translation of '{text}' from {source_lang} to {target_lang}]",
        source_language=source_lang,
        target_language=target_lang,
        model_used=selected_model,
        confidence=0.85,
        terminology_notes=None,
    )


def get_supported_pairs() -> list[tuple[str, str]]:
    """Get list of supported translation pairs."""
    from .config import TRANSLATION_PAIRS

    return list(TRANSLATION_PAIRS.keys())


def validate_language_pair(source: str, target: str) -> bool:
    """Check if a language pair is supported."""
    from .config import TRANSLATION_PAIRS

    return (source, target) in TRANSLATION_PAIRS


def get_language_info(code: str) -> dict:
    """Get information about a language."""
    return {
        "code": code,
        "name": get_language_name(code),
        "is_supported": code in config.supported_languages,
    }
