"""
OCR module for Document Processing and Irish Handwriting Recognition.

Provides:
- ModelRegistry: Registry of OCR models (olmOCR, Qwen2.5-VL, DeepSeek-OCR, etc.)
- ComparisonRunner: Multi-model comparison with CER/WER metrics
- GaelicMetrics: Irish-specific evaluation metrics
- Adapters: Unified interface for PaddleOCR, Docling, Unstract, Dots.OCR
- VisionComparison: LiteLLM-based vision model comparison
- IrishProcessing: Irish language OCR with fada validation
"""

from .adapters import (
    BoundingBox,
    DoclingAdapter,
    DotsOCRAdapter,
    OCRAdapter,
    OCRAdapterRegistry,
    OCRBackend,
    OCRResult,
    PaddleOCRAdapter,
    PageOCRResult,
    UnstractAdapter,
    compare_ocr_models,
    get_adapter,
)
from .comparison_runner import (
    ComparisonResult,
    ComparisonRunner,
    ModelOutput,
)
from .gaelic_metrics import (
    GaelicMetrics,
    calculate_cer,
    calculate_wer,
)
from .irish_htr_dataset import (
    GAELIC_SCRIPT_CHARS,
    IRISH_CHARS,
    DatasetConfig,
    DatasetSample,
    IrishHTRDatasetGenerator,
)
from .irish_processing import (
    DialectAnalysis,
    FadaAnalysis,
    IrishContentAnalysis,
    IrishDialect,
    IrishOCRProcessor,
    SpellingStandard,
    detect_irish_content,
    get_fada_accuracy,
    get_irish_quality_score,
)
from .line_segmentation import (
    BoundingBox as LineBoundingBox,
)
from .line_segmentation import (
    LineSegmenter,
    SegmentationConfig,
    SegmentedLine,
    segment_duchas_page,
)
from .model_registry import (
    OCR_MODELS,
    ModelRegistry,
    OCRModel,
)
from .vision_comparison import (
    OCR_PROMPTS,
    VISION_MODELS,
    VisionModel,
    VisionResult,
    compare_vision_models,
    get_model_config,
    list_vision_models,
)
from .vlm_finetune_comparison import (
    MOBILE_TARGETS,
    VLM_MODELS,
    EvaluationResult,
    FinetuneConfig,
    VLMComparisonPipeline,
)

__all__ = [
    # Legacy
    "OCRModel",
    "ModelRegistry",
    "OCR_MODELS",
    "ComparisonRunner",
    "ComparisonResult",
    "ModelOutput",
    "GaelicMetrics",
    "calculate_cer",
    "calculate_wer",
    # Adapters
    "OCRBackend",
    "OCRResult",
    "PageOCRResult",
    "BoundingBox",
    "OCRAdapter",
    "PaddleOCRAdapter",
    "DoclingAdapter",
    "DotsOCRAdapter",
    "UnstractAdapter",
    "OCRAdapterRegistry",
    "get_adapter",
    "compare_ocr_models",
    # Vision
    "VisionModel",
    "VisionResult",
    "compare_vision_models",
    "VISION_MODELS",
    "OCR_PROMPTS",
    "list_vision_models",
    "get_model_config",
    # Irish Language
    "IrishOCRProcessor",
    "IrishDialect",
    "SpellingStandard",
    "IrishContentAnalysis",
    "FadaAnalysis",
    "DialectAnalysis",
    "detect_irish_content",
    "get_fada_accuracy",
    "get_irish_quality_score",
    # Line Segmentation
    "LineSegmenter",
    "SegmentationConfig",
    "SegmentedLine",
    "LineBoundingBox",
    "segment_duchas_page",
    # Irish HTR Dataset
    "IrishHTRDatasetGenerator",
    "DatasetConfig",
    "DatasetSample",
    "IRISH_CHARS",
    "GAELIC_SCRIPT_CHARS",
    # VLM Fine-tuning Comparison
    "VLMComparisonPipeline",
    "VLM_MODELS",
    "MOBILE_TARGETS",
    "EvaluationResult",
    "FinetuneConfig",
]
