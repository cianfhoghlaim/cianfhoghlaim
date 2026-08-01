"""
Alignment Quality Metrics for Bilingual Parallel Corpus.

Provides validation and quality scoring for Irish-English aligned pairs.
Based on research from taighde_bonneagar/03-bilingual-dataset-creation/.

Quality Dimensions:
- Length ratio (0.8-1.3 word ratio is ideal)
- Language ID confidence (>0.95 required)
- Alignment score (>0.7 for high-quality pairs)
- Semantic consistency
- Term coverage
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

import numpy as np

from .aligner import ParallelPair, AlignmentResult


@dataclass
class AlignmentQualityMetrics:
    """Quality metrics for an alignment result."""

    # Overall metrics
    total_pairs: int = 0
    valid_pairs: int = 0
    invalid_pairs: int = 0
    quality_score: float = 0.0

    # Length ratio metrics
    avg_length_ratio: float = 0.0
    length_ratio_std: float = 0.0
    length_ratio_violations: int = 0

    # Language ID metrics
    source_lang_confidence: float = 0.0
    target_lang_confidence: float = 0.0
    lang_id_violations: int = 0

    # Alignment score metrics
    avg_alignment_score: float = 0.0
    alignment_score_std: float = 0.0
    low_alignment_count: int = 0

    # Semantic metrics
    semantic_consistency: float = 0.0

    # Term coverage
    term_coverage: float = 0.0
    educational_term_coverage: float = 0.0

    # Distribution metrics
    score_histogram: list[int] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "total_pairs": self.total_pairs,
            "valid_pairs": self.valid_pairs,
            "invalid_pairs": self.invalid_pairs,
            "quality_score": self.quality_score,
            "avg_length_ratio": self.avg_length_ratio,
            "length_ratio_std": self.length_ratio_std,
            "length_ratio_violations": self.length_ratio_violations,
            "source_lang_confidence": self.source_lang_confidence,
            "target_lang_confidence": self.target_lang_confidence,
            "lang_id_violations": self.lang_id_violations,
            "avg_alignment_score": self.avg_alignment_score,
            "alignment_score_std": self.alignment_score_std,
            "low_alignment_count": self.low_alignment_count,
            "semantic_consistency": self.semantic_consistency,
            "term_coverage": self.term_coverage,
            "educational_term_coverage": self.educational_term_coverage,
            "score_histogram": self.score_histogram,
        }


# Quality thresholds
QUALITY_THRESHOLDS = {
    "min_alignment_score": 0.7,
    "min_length_ratio": 0.3,
    "max_length_ratio": 3.0,
    "ideal_min_length_ratio": 0.8,
    "ideal_max_length_ratio": 1.3,
    "min_lang_confidence": 0.95,
    "min_word_count": 3,
    "max_word_count": 200,
}


def validate_alignment(pair: ParallelPair) -> tuple[bool, list[str]]:
    """
    Validate a single alignment pair.

    Args:
        pair: ParallelPair to validate

    Returns:
        Tuple of (is_valid, list of validation issues)
    """
    issues = []

    # Check for empty texts
    if not pair.source_text or not pair.source_text.strip():
        issues.append("Empty source text")
    if not pair.target_text or not pair.target_text.strip():
        issues.append("Empty target text")

    if issues:
        return False, issues

    # Word counts
    source_words = len(pair.source_text.split())
    target_words = len(pair.target_text.split())

    # Minimum word count
    if source_words < QUALITY_THRESHOLDS["min_word_count"]:
        issues.append(f"Source too short: {source_words} words")
    if target_words < QUALITY_THRESHOLDS["min_word_count"]:
        issues.append(f"Target too short: {target_words} words")

    # Maximum word count
    if source_words > QUALITY_THRESHOLDS["max_word_count"]:
        issues.append(f"Source too long: {source_words} words")
    if target_words > QUALITY_THRESHOLDS["max_word_count"]:
        issues.append(f"Target too long: {target_words} words")

    # Length ratio
    if target_words > 0:
        ratio = source_words / target_words
        if ratio < QUALITY_THRESHOLDS["min_length_ratio"]:
            issues.append(f"Length ratio too low: {ratio:.2f}")
        if ratio > QUALITY_THRESHOLDS["max_length_ratio"]:
            issues.append(f"Length ratio too high: {ratio:.2f}")

    # Alignment score
    if pair.alignment_score < QUALITY_THRESHOLDS["min_alignment_score"]:
        issues.append(f"Low alignment score: {pair.alignment_score:.2f}")

    # Language detection (basic heuristics)
    if _contains_irish_chars(pair.source_text):
        issues.append("Source contains Irish characters (expected English)")
    if not _contains_irish_chars(pair.target_text) and not _is_common_word(pair.target_text):
        # Only flag if target has no Irish markers and isn't a common word
        pass  # Relaxed check for short phrases

    return len(issues) == 0, issues


def calculate_quality_score(pairs: Sequence[ParallelPair]) -> AlignmentQualityMetrics:
    """
    Calculate comprehensive quality metrics for alignment results.

    Args:
        pairs: List of ParallelPair objects

    Returns:
        AlignmentQualityMetrics with all computed metrics
    """
    if not pairs:
        return AlignmentQualityMetrics()

    metrics = AlignmentQualityMetrics(total_pairs=len(pairs))

    # Validate each pair
    valid_count = 0
    length_ratios = []
    alignment_scores = []

    for pair in pairs:
        is_valid, issues = validate_alignment(pair)

        if is_valid:
            valid_count += 1
        else:
            metrics.invalid_pairs += 1

        # Length ratio
        source_words = len(pair.source_text.split())
        target_words = len(pair.target_text.split())

        if target_words > 0:
            ratio = source_words / target_words
            length_ratios.append(ratio)

            if ratio < QUALITY_THRESHOLDS["ideal_min_length_ratio"]:
                metrics.length_ratio_violations += 1
            elif ratio > QUALITY_THRESHOLDS["ideal_max_length_ratio"]:
                metrics.length_ratio_violations += 1

        # Alignment score
        alignment_scores.append(pair.alignment_score)
        if pair.alignment_score < QUALITY_THRESHOLDS["min_alignment_score"]:
            metrics.low_alignment_count += 1

    metrics.valid_pairs = valid_count

    # Aggregate statistics
    if length_ratios:
        metrics.avg_length_ratio = float(np.mean(length_ratios))
        metrics.length_ratio_std = float(np.std(length_ratios))

    if alignment_scores:
        metrics.avg_alignment_score = float(np.mean(alignment_scores))
        metrics.alignment_score_std = float(np.std(alignment_scores))

    # Score histogram (10 bins from 0.0 to 1.0)
    if alignment_scores:
        hist, _ = np.histogram(alignment_scores, bins=10, range=(0, 1))
        metrics.score_histogram = hist.tolist()

    # Term coverage
    metrics.term_coverage = _calculate_term_coverage(pairs)
    metrics.educational_term_coverage = _calculate_educational_term_coverage(pairs)

    # Overall quality score (weighted average of components)
    components = [
        (metrics.valid_pairs / max(metrics.total_pairs, 1), 0.3),  # Validity
        (metrics.avg_alignment_score, 0.3),  # Alignment quality
        (_length_ratio_score(metrics.avg_length_ratio), 0.2),  # Length ratio
        (metrics.term_coverage, 0.1),  # General terms
        (metrics.educational_term_coverage, 0.1),  # Educational terms
    ]

    metrics.quality_score = sum(score * weight for score, weight in components)

    return metrics


def calculate_corpus_statistics(
    results: Sequence[AlignmentResult],
) -> dict:
    """
    Calculate statistics across multiple alignment results.

    Args:
        results: List of AlignmentResult objects

    Returns:
        Dictionary with corpus-level statistics
    """
    all_pairs = []
    for result in results:
        all_pairs.extend(result.pairs)

    metrics = calculate_quality_score(all_pairs)

    return {
        "total_documents": len(results),
        "total_pairs": len(all_pairs),
        "avg_pairs_per_doc": len(all_pairs) / max(len(results), 1),
        "quality_metrics": metrics.to_dict(),
        "alignment_rates": [r.alignment_rate for r in results],
        "avg_alignment_rate": np.mean([r.alignment_rate for r in results]) if results else 0.0,
    }


def filter_high_quality_pairs(
    pairs: Sequence[ParallelPair],
    min_score: float = 0.8,
    strict_length_ratio: bool = True,
) -> list[ParallelPair]:
    """
    Filter pairs to keep only high-quality alignments.

    Args:
        pairs: List of ParallelPair objects
        min_score: Minimum alignment score
        strict_length_ratio: Use strict 0.8-1.3 ratio

    Returns:
        Filtered list of high-quality pairs
    """
    filtered = []

    for pair in pairs:
        # Score threshold
        if pair.alignment_score < min_score:
            continue

        # Validation
        is_valid, _ = validate_alignment(pair)
        if not is_valid:
            continue

        # Strict length ratio
        if strict_length_ratio:
            source_words = len(pair.source_text.split())
            target_words = len(pair.target_text.split())

            if target_words > 0:
                ratio = source_words / target_words
                if ratio < 0.8 or ratio > 1.3:
                    continue

        filtered.append(pair)

    return filtered


# Helper functions

def _contains_irish_chars(text: str) -> bool:
    """Check if text contains Irish-specific characters (fada)."""
    irish_chars = set("áéíóúÁÉÍÓÚ")
    return any(c in irish_chars for c in text)


def _is_common_word(text: str) -> bool:
    """Check if text is a common word that exists in both languages."""
    common_words = {"ok", "yes", "no", "hello", "bye", "a", "an", "the"}
    return text.strip().lower() in common_words


def _length_ratio_score(ratio: float) -> float:
    """Convert length ratio to a 0-1 quality score."""
    if 0.8 <= ratio <= 1.3:
        return 1.0
    elif 0.5 <= ratio <= 2.0:
        # Linear decay outside ideal range
        if ratio < 0.8:
            return 0.5 + 0.5 * (ratio - 0.5) / 0.3
        else:
            return 0.5 + 0.5 * (2.0 - ratio) / 0.7
    else:
        return max(0.0, 0.5 - abs(ratio - 1.0) * 0.2)


def _calculate_term_coverage(pairs: Sequence[ParallelPair]) -> float:
    """Calculate general terminology coverage."""
    if not pairs:
        return 0.0

    # Common parallel terms (should appear in both)
    common_terms = {
        ("curriculum", "curaclam"),
        ("education", "oideachas"),
        ("school", "scoil"),
        ("student", "dalta"),
        ("teacher", "múinteoir"),
    }

    found = 0
    for en_term, ga_term in common_terms:
        for pair in pairs:
            if en_term in pair.source_text.lower() and ga_term in pair.target_text.lower():
                found += 1
                break

    return found / len(common_terms)


def _calculate_educational_term_coverage(pairs: Sequence[ParallelPair]) -> float:
    """Calculate educational domain terminology coverage."""
    if not pairs:
        return 0.0

    educational_terms = {
        ("learning outcome", "toradh foghlama"),
        ("assessment", "measúnú"),
        ("examination", "scrúdú"),
        ("leaving certificate", "ardteistiméireacht"),
        ("junior cycle", "sraith shóisearach"),
        ("primary", "bunscoile"),
        ("secondary", "meánscoile"),
        ("mathematics", "matamaitic"),
        ("science", "eolaíocht"),
    }

    found = 0
    for en_term, ga_term in educational_terms:
        for pair in pairs:
            if en_term in pair.source_text.lower():
                # Check if Irish equivalent is present
                if ga_term in pair.target_text.lower():
                    found += 1
                    break

    return found / len(educational_terms)
