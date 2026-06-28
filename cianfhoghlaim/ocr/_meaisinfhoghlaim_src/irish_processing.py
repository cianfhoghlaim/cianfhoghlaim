"""
Irish Language OCR Processing Module.

Provides specialized processing for Irish (Gaeilge) documents:
- Fada (síneadh fada) accuracy validation
- Dialect detection (Connacht, Munster, Ulster)
- Spelling standard detection (pre-reform vs modern)
- Model fallback for poor Irish quality
- UCCIX integration for best Irish support

Models for Irish:
- UCCIX-Llama2-13B-Instruct: Best Irish language model
- Qwen2.5-VL: Strong multilingual with decent Irish
- GaBERT: Irish BERT for validation

Usage:
    from sruth.oideachais.ocr.irish_processing import IrishOCRProcessor

    processor = IrishOCRProcessor()
    result = await processor.process_with_fallback(image_bytes, "qwen3-vl")
    analysis = processor.analyze_irish_quality(ocr_text)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

# ============================================================================
# Configuration
# ============================================================================


class IrishDialect(str, Enum):
    """Irish regional dialects."""

    CONNACHT = "connacht"  # Galway, Mayo
    MUNSTER = "munster"  # Cork, Kerry, Waterford
    ULSTER = "ulster"  # Donegal
    STANDARD = "standard"  # Caighdeán Oifigiúil
    UNKNOWN = "unknown"


class SpellingStandard(str, Enum):
    """Irish spelling standards."""

    PRE_REFORM = "pre_reform"  # Pre-1948
    MODERN = "modern"  # Post-reform
    MIXED = "mixed"
    UNKNOWN = "unknown"


# Irish-capable models (ordered by Irish quality)
IRISH_MODELS = [
    "uccix-13b",  # Best for Irish (trained on Irish data)
    "qwen2.5-vl-7b",  # Good multilingual with Irish
    "qwen3-vl",  # Decent Irish support
    "glm-4.6v-flash",  # Basic Irish
]

# Fadas (síneadh fada)
FADAS = {"á", "é", "í", "ó", "ú", "Á", "É", "Í", "Ó", "Ú"}
VOWELS = {"a", "e", "i", "o", "u", "A", "E", "I", "O", "U"}

# Common Irish words that require fadas
FADA_WORDS = {
    # Very common
    "tá": "ta",
    "bí": "bi",
    "mé": "me",
    "tú": "tu",
    "sé": "se",
    "sí": "si",
    "siad": "siad",  # No fada needed
    "ná": "na",
    "nó": "no",
    "agus": "agus",  # No fada
    "lá": "la",
    "bá": "ba",
    "fá": "fa",
    "ó": "o",
    "í": "i",
    "é": "e",
    "á": "a",
    "ú": "u",
    # Common nouns
    "cáin": "cain",
    "múinteoir": "muinteoir",
    "scoláire": "scolaire",
    "léamh": "leamh",
    "scríobh": "scriobh",
    "oíche": "oiche",
    "gaeilge": "gaeilge",  # Often Gaeilge
    "béarla": "bearla",
    "cúrsa": "cursa",
    "páipéar": "paipear",
    "scrúdú": "scrudu",
    # Verbs
    "bíonn": "bionn",
    "bhí": "bhi",
    "déan": "dean",
    "téigh": "teigh",
    "faigh": "faigh",  # No fada
    "tabhair": "tabhair",  # No fada
    "abair": "abair",  # No fada
    "feic": "feic",  # No fada
    "clois": "clois",  # No fada
    "bí": "bi",
}

# Pre-reform spellings
PRE_REFORM_INDICATORS = [
    r"\bmhaith\b",  # Now: maith (in some contexts)
    r"\bsgeul\b",  # Now: scéal
    r"\bcinn\b",  # Now: ceann
    r"\bmhór\b",  # Now: mór (in some contexts)
    r"\b-san\b",  # Old emphatic suffix
    r"\b-se\b",  # Old emphatic suffix
    r"ċ",  # Dotted c (old script)
    r"ṡ",  # Dotted s (old script)
    r"ḃ",  # Dotted b (old script)
    r"ṫ",  # Dotted t (old script)
]

# Modern spelling indicators
MODERN_INDICATORS = [
    r"\bmaith\b",
    r"\bscéal\b",
    r"\bceann\b",
    r"\bmór\b",
    r"\b-sa\b",  # Modern emphatic
    r"\bseo\b",  # Modern demonstrative
]

# Dialect vocabulary
DIALECT_VOCABULARY = {
    IrishDialect.CONNACHT: [
        (r"\bmuid\b", "we (Connacht)"),
        (r"\bfuil\b", "is/are (Connacht form)"),
        (r"\bgoidé\b", "what (Connacht)"),
        (r"\bcéard\b", "what (Connacht)"),
    ],
    IrishDialect.MUNSTER: [
        (r"\bsinn\b", "we (Munster)"),
        (r"\bis ea\b", "it is (Munster)"),
        (r"\b-ís\b", "verbal noun ending (Munster)"),
        (r"\bcho\b", "so/as (Munster)"),
    ],
    IrishDialect.ULSTER: [
        (r"\bchan\b", "not (Ulster)"),
        (r"\bfá\b", "about (Ulster)"),
        (r"\bachan\b", "every (Ulster)"),
        (r"\bgoitse\b", "come (Ulster)"),
    ],
}


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class FadaAnalysis:
    """Analysis of fada usage in text."""

    total_fadas: int
    expected_fadas: int
    missing_fadas: list[dict[str, Any]] = field(default_factory=list)
    incorrect_fadas: list[dict[str, Any]] = field(default_factory=list)
    accuracy: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_fadas": self.total_fadas,
            "expected_fadas": self.expected_fadas,
            "missing_fadas": self.missing_fadas,
            "incorrect_fadas": self.incorrect_fadas,
            "accuracy": self.accuracy,
        }


@dataclass
class DialectAnalysis:
    """Analysis of dialect indicators."""

    detected_dialect: IrishDialect
    confidence: float
    indicators: list[dict[str, Any]] = field(default_factory=list)
    mixed_dialects: list[IrishDialect] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "detected_dialect": self.detected_dialect.value,
            "confidence": self.confidence,
            "indicators": self.indicators,
            "mixed_dialects": [d.value for d in self.mixed_dialects],
        }


@dataclass
class IrishContentAnalysis:
    """Complete analysis of Irish language content."""

    is_irish: bool
    irish_percentage: float
    fada_analysis: FadaAnalysis
    dialect_analysis: DialectAnalysis
    spelling_standard: SpellingStandard
    quality_score: float
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_irish": self.is_irish,
            "irish_percentage": self.irish_percentage,
            "fada_analysis": self.fada_analysis.to_dict(),
            "dialect_analysis": self.dialect_analysis.to_dict(),
            "spelling_standard": self.spelling_standard.value,
            "quality_score": self.quality_score,
            "recommendations": self.recommendations,
        }


# ============================================================================
# Irish OCR Processor
# ============================================================================


class IrishOCRProcessor:
    """
    Processor for Irish language OCR with quality validation.

    Provides:
    - Fada accuracy checking
    - Dialect detection
    - Spelling standard identification
    - Model fallback for poor quality
    """

    def __init__(
        self,
        fallback_models: list[str] | None = None,
        quality_threshold: float = 0.7,
    ):
        self.fallback_models = fallback_models or IRISH_MODELS
        self.quality_threshold = quality_threshold

    async def process_with_fallback(
        self,
        image: bytes,
        primary_model: str,
        prompt: str | None = None,
    ) -> dict[str, Any]:
        """
        Process image with Irish-aware fallback.

        If primary model produces poor Irish quality,
        falls back to UCCIX or other Irish-capable models.

        Args:
            image: Image bytes
            primary_model: Primary OCR/vision model to use
            prompt: Custom prompt (defaults to Irish-aware prompt)

        Returns:
            Dict with OCR result and quality analysis
        """
        from .vision_comparison import compare_vision_models

        # Default Irish-aware prompt
        if prompt is None:
            prompt = (
                "Extract all text from this document. "
                "This may contain Irish (Gaeilge) text - preserve all "
                "fadas (síneadh fada: á, é, í, ó, ú) accurately. "
                "Maintain original formatting."
            )

        # Try primary model first
        results = await compare_vision_models(
            image,
            models=[primary_model],
            prompt=prompt,
        )

        primary_result = results.get(primary_model)
        if not primary_result or primary_result.status != "success":
            # Primary failed, try fallback
            return await self._run_fallback(image, prompt, primary_model)

        # Analyze Irish quality
        analysis = self.analyze_irish_quality(primary_result.text)

        if analysis.is_irish and analysis.quality_score < self.quality_threshold:
            # Poor Irish quality, try fallback models
            fallback_result = await self._run_fallback(
                image, prompt, primary_model
            )
            # Compare and return best
            fallback_analysis = self.analyze_irish_quality(
                fallback_result.get("text", "")
            )
            if fallback_analysis.quality_score > analysis.quality_score:
                return {
                    "text": fallback_result["text"],
                    "model_id": fallback_result["model_id"],
                    "model_name": fallback_result["model_name"],
                    "analysis": fallback_analysis.to_dict(),
                    "fallback_used": True,
                    "primary_quality": analysis.quality_score,
                }

        return {
            "text": primary_result.text,
            "model_id": primary_result.model_id,
            "model_name": primary_result.model_name,
            "analysis": analysis.to_dict(),
            "fallback_used": False,
        }

    async def _run_fallback(
        self,
        image: bytes,
        prompt: str,
        exclude_model: str,
    ) -> dict[str, Any]:
        """Run fallback models and return best result."""
        from .vision_comparison import compare_vision_models

        # Filter out the failed primary model
        fallback_models = [
            m for m in self.fallback_models if m != exclude_model
        ]

        if not fallback_models:
            return {"text": "", "model_id": "", "model_name": "", "error": "No fallback models"}

        # Try fallback models
        results = await compare_vision_models(
            image,
            models=fallback_models[:2],  # Limit to 2 fallbacks
            prompt=prompt,
            parallel=False,  # Sequential for GPU memory
        )

        # Find best result
        best_result = None
        best_quality = 0.0

        for model_id, result in results.items():
            if result.status != "success":
                continue

            analysis = self.analyze_irish_quality(result.text)
            if analysis.quality_score > best_quality:
                best_quality = analysis.quality_score
                best_result = {
                    "text": result.text,
                    "model_id": result.model_id,
                    "model_name": result.model_name,
                    "quality": best_quality,
                }

        return best_result or {"text": "", "model_id": "", "model_name": ""}

    def analyze_irish_quality(self, text: str) -> IrishContentAnalysis:
        """
        Analyze Irish language quality in OCR text.

        Args:
            text: OCR output text

        Returns:
            IrishContentAnalysis with quality metrics
        """
        if not text:
            return IrishContentAnalysis(
                is_irish=False,
                irish_percentage=0.0,
                fada_analysis=FadaAnalysis(0, 0),
                dialect_analysis=DialectAnalysis(IrishDialect.UNKNOWN, 0.0),
                spelling_standard=SpellingStandard.UNKNOWN,
                quality_score=0.0,
            )

        # Detect Irish content
        is_irish, irish_pct = self._detect_irish_content(text)

        # Analyze fadas
        fada_analysis = self._analyze_fadas(text)

        # Detect dialect
        dialect_analysis = self._detect_dialect(text)

        # Detect spelling standard
        spelling_standard = self._detect_spelling_standard(text)

        # Calculate overall quality
        quality_score = self._calculate_quality_score(
            is_irish, irish_pct, fada_analysis, dialect_analysis
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            fada_analysis, dialect_analysis, spelling_standard
        )

        return IrishContentAnalysis(
            is_irish=is_irish,
            irish_percentage=irish_pct,
            fada_analysis=fada_analysis,
            dialect_analysis=dialect_analysis,
            spelling_standard=spelling_standard,
            quality_score=quality_score,
            recommendations=recommendations,
        )

    def _detect_irish_content(self, text: str) -> tuple[bool, float]:
        """Detect if text contains Irish and estimate percentage."""
        if not text:
            return False, 0.0

        text_lower = text.lower()
        words = text_lower.split()
        total_words = len(words)

        if total_words == 0:
            return False, 0.0

        # Common Irish words
        irish_words = {
            "an", "na", "agus", "le", "ar", "i", "go", "de", "do", "is",
            "ní", "ba", "bí", "tá", "bhí", "sé", "sí", "mé", "tú", "muid",
            "siad", "iad", "sin", "seo", "nach", "mar", "ach", "nó", "más",
            "dá", "cá", "cé", "cén", "cad", "conas", "cathain", "ceart",
            "amháin", "fós", "anois", "ansin", "anseo", "anocht",
        }

        irish_count = sum(1 for w in words if w in irish_words)

        # Also count fadas as Irish indicator
        fada_count = sum(1 for c in text if c in FADAS)

        # Calculate Irish percentage
        irish_pct = (irish_count + fada_count * 0.5) / total_words

        # Threshold for Irish detection
        is_irish = irish_pct > 0.1 or fada_count > 5

        return is_irish, min(1.0, irish_pct)

    def _analyze_fadas(self, text: str) -> FadaAnalysis:
        """Analyze fada usage and accuracy."""
        total_fadas = sum(1 for c in text if c in FADAS)

        missing = []
        incorrect = []

        text_lower = text.lower()

        # Check known fada words
        for correct, wrong in FADA_WORDS.items():
            # Find instances of wrong spelling
            pattern = r"\b" + re.escape(wrong) + r"\b"
            for match in re.finditer(pattern, text_lower):
                missing.append({
                    "word": wrong,
                    "position": match.start(),
                    "expected": correct,
                    "found": wrong,
                })

        # Estimate expected fadas based on text length and Irish content
        words = text_lower.split()
        expected_fadas = int(len(words) * 0.08)  # ~8% of words should have fadas

        # Calculate accuracy
        if expected_fadas > 0:
            accuracy = min(1.0, total_fadas / expected_fadas)
        else:
            accuracy = 1.0 if total_fadas == 0 else 0.5

        return FadaAnalysis(
            total_fadas=total_fadas,
            expected_fadas=expected_fadas,
            missing_fadas=missing[:10],  # Limit to 10
            incorrect_fadas=incorrect[:10],
            accuracy=accuracy,
        )

    def _detect_dialect(self, text: str) -> DialectAnalysis:
        """Detect Irish dialect from text."""
        text_lower = text.lower()
        dialect_scores: dict[IrishDialect, float] = {}
        all_indicators = []

        for dialect, patterns in DIALECT_VOCABULARY.items():
            score = 0.0
            for pattern, description in patterns:
                matches = len(re.findall(pattern, text_lower))
                if matches > 0:
                    score += matches
                    all_indicators.append({
                        "dialect": dialect.value,
                        "pattern": pattern,
                        "description": description,
                        "count": matches,
                    })
            dialect_scores[dialect] = score

        # Determine primary dialect
        if all(s == 0 for s in dialect_scores.values()):
            return DialectAnalysis(
                detected_dialect=IrishDialect.UNKNOWN,
                confidence=0.0,
            )

        total_score = sum(dialect_scores.values())
        best_dialect = max(dialect_scores, key=lambda d: dialect_scores[d])
        confidence = dialect_scores[best_dialect] / total_score if total_score > 0 else 0.0

        # Detect mixed dialects
        mixed = [
            d for d, s in dialect_scores.items()
            if s > 0 and d != best_dialect
        ]

        return DialectAnalysis(
            detected_dialect=best_dialect,
            confidence=confidence,
            indicators=all_indicators,
            mixed_dialects=mixed,
        )

    def _detect_spelling_standard(self, text: str) -> SpellingStandard:
        """Detect whether text uses pre-reform or modern spelling."""
        text_lower = text.lower()

        pre_reform_count = sum(
            len(re.findall(p, text_lower)) for p in PRE_REFORM_INDICATORS
        )
        modern_count = sum(
            len(re.findall(p, text_lower)) for p in MODERN_INDICATORS
        )

        if pre_reform_count == 0 and modern_count == 0:
            return SpellingStandard.UNKNOWN
        elif pre_reform_count > modern_count * 2:
            return SpellingStandard.PRE_REFORM
        elif modern_count > pre_reform_count * 2:
            return SpellingStandard.MODERN
        else:
            return SpellingStandard.MIXED

    def _calculate_quality_score(
        self,
        is_irish: bool,
        irish_pct: float,
        fada: FadaAnalysis,
        dialect: DialectAnalysis,
    ) -> float:
        """Calculate overall Irish content quality score."""
        if not is_irish:
            return 0.0

        # Weight components
        fada_weight = 0.5
        dialect_weight = 0.2
        content_weight = 0.3

        # Fada accuracy is critical
        fada_score = fada.accuracy

        # Dialect detection indicates good Irish
        dialect_score = dialect.confidence

        # Content percentage
        content_score = min(1.0, irish_pct * 2)

        return (
            fada_score * fada_weight +
            dialect_score * dialect_weight +
            content_score * content_weight
        )

    def _generate_recommendations(
        self,
        fada: FadaAnalysis,
        dialect: DialectAnalysis,
        spelling: SpellingStandard,
    ) -> list[str]:
        """Generate improvement recommendations."""
        recommendations = []

        if fada.accuracy < 0.7:
            recommendations.append(
                "Low fada accuracy detected. Consider using UCCIX model for Irish text."
            )

        if fada.missing_fadas:
            words = [m["word"] for m in fada.missing_fadas[:3]]
            recommendations.append(
                f"Potentially missing fadas in: {', '.join(words)}"
            )

        if spelling == SpellingStandard.MIXED:
            recommendations.append(
                "Mixed pre-reform and modern spelling detected. Document may need normalization."
            )

        if dialect.mixed_dialects:
            dialects = [d.value for d in dialect.mixed_dialects]
            recommendations.append(
                f"Multiple dialect indicators found: {dialect.detected_dialect.value}, {', '.join(dialects)}"
            )

        return recommendations


# ============================================================================
# Convenience Functions
# ============================================================================


def detect_irish_content(text: str) -> bool:
    """Quick check if text contains Irish content."""
    processor = IrishOCRProcessor()
    analysis = processor.analyze_irish_quality(text)
    return analysis.is_irish


def get_fada_accuracy(text: str) -> float:
    """Get fada accuracy score for text."""
    processor = IrishOCRProcessor()
    analysis = processor.analyze_irish_quality(text)
    return analysis.fada_analysis.accuracy


def get_irish_quality_score(text: str) -> float:
    """Get overall Irish quality score for text."""
    processor = IrishOCRProcessor()
    analysis = processor.analyze_irish_quality(text)
    return analysis.quality_score
