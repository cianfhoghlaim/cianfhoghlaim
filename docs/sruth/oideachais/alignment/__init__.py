"""
Bilingual Alignment Module for Irish-English Parallel Corpus.

Provides sentence-level and paragraph-level alignment between Irish (ga)
and English (en) educational content for creating training datasets.
"""

from .aligner import (
    IrishEnglishAligner,
    AlignmentMethod,
    AlignmentResult,
    ParallelPair,
)
from .quality import (
    AlignmentQualityMetrics,
    validate_alignment,
    calculate_quality_score,
)
from .export import (
    export_to_jsonl,
    export_to_parquet,
    export_to_huggingface,
    export_to_tmx,
)

# ColPali visual alignment
from .colpali_aligner import (
    ColPaliAligner,
    BoundingBox,
    AlignedLine,
)

# Dataset generation
from .dataset_generator import (
    DatasetGenerator,
    TrainingSample,
)

__all__ = [
    # Aligner
    "IrishEnglishAligner",
    "AlignmentMethod",
    "AlignmentResult",
    "ParallelPair",
    # Quality
    "AlignmentQualityMetrics",
    "validate_alignment",
    "calculate_quality_score",
    # Export
    "export_to_jsonl",
    "export_to_parquet",
    "export_to_huggingface",
    "export_to_tmx",
    # ColPali Visual Alignment
    "ColPaliAligner",
    "BoundingBox",
    "AlignedLine",
    # Dataset Generation
    "DatasetGenerator",
    "TrainingSample",
]
