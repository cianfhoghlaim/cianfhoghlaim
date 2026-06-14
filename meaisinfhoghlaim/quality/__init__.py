"""
Quality Assessment.

Completeness scoring and content quality metrics for curriculum documents.
Audio alignment validation for speech datasets.
"""
from .canuint_validator import (
    ValidationReport,
    ValidationResult,
    export_splits,
    generate_splits,
    load_and_validate,
    validate_alignment_consistency,
    validate_canuint_dataset,
    validate_dialect_balance,
    validate_duration_distribution,
    validate_phoneme_coverage,
    validate_speaker_diversity,
)
from .completeness import CompletenessScorer, ContentQuality
from .content_quality import ContentQualityAssessor

__all__ = [
    "CompletenessScorer",
    "ContentQuality",
    "ContentQualityAssessor",
    # Canuint alignment validation
    "ValidationReport",
    "ValidationResult",
    "validate_canuint_dataset",
    "validate_duration_distribution",
    "validate_alignment_consistency",
    "validate_phoneme_coverage",
    "validate_dialect_balance",
    "validate_speaker_diversity",
    "generate_splits",
    "export_splits",
    "load_and_validate",
]
