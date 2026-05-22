"""
Bilingual Alignment Module for Irish-English Parallel Corpus.

Provides sentence-level and paragraph-level alignment between Irish (ga)
and English (en) educational content for creating training datasets.
"""

from .aligner import (
    AlignmentMethod,
    AlignmentResult,
    IrishEnglishAligner,
    ParallelPair,
)

# ColPali visual alignment
from .colpali_aligner import (
    AlignedLine,
    BoundingBox,
    ColPaliAligner,
)

# Dataset generation
from .dataset_generator import (
    DatasetGenerator,
    TrainingSample,
)
from .export import (
    export_to_huggingface,
    export_to_jsonl,
    export_to_parquet,
    export_to_tmx,
)
from .quality import (
    AlignmentQualityMetrics,
    calculate_quality_score,
    validate_alignment,
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
