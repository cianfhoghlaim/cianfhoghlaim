"""
Dagster Assets for Irish Education Pipeline.

Provides materialized assets for curriculum processing:
- Grammar validation with Gramadóir
- PDF extraction benchmarking with PDFStract patterns
- HTR model comparison
- Syntactic parsing with UD treebanks
- Model conversion (HuggingFace → GGUF) for llama-swap
"""

from .grammar_validation import (
    GramadoirValidator,
    GrammarIssue,
    GrammarValidationResult,
    grammar_validated_curriculum,
)
from .pdf_benchmark import (
    PDFBenchmarkResult,
    PDFExtractorComparison,
    pdf_extraction_benchmark,
)
from .syntactic_parsing import (
    IrishSyntacticParser,
    ParseResult,
    Sentence,
    Token,
    get_treebank_stats,
    load_treebank,
    syntactic_parsed_curriculum,
)
from .model_conversion import (
    ConversionResult,
    model_conversion_assets,
    hf_models_downloaded,
    gguf_qwen2_5_math_7b,
    gguf_uccix_13b,
    gguf_gemma_2_9b,
    gguf_qwen2_5_vl_7b,
    gguf_deepseek_ocr,
    gguf_z_image_turbo,
    gguf_qwen_image,
    gguf_qwen_image_edit,
    gguf_flux2_dev,
)
from .asset_generation import (
    asset_generation_assets,
    image_prompts_designed,
    fibo_configs_built,
    study_assets_rendered,
    study_assets_published,
)

__all__ = [
    # Grammar validation
    "GramadoirValidator",
    "GrammarIssue",
    "GrammarValidationResult",
    "grammar_validated_curriculum",
    # PDF benchmarking
    "PDFBenchmarkResult",
    "PDFExtractorComparison",
    "pdf_extraction_benchmark",
    # Syntactic parsing
    "IrishSyntacticParser",
    "Token",
    "Sentence",
    "ParseResult",
    "load_treebank",
    "get_treebank_stats",
    "syntactic_parsed_curriculum",
    # Model conversion (HF → GGUF for llama-swap)
    "ConversionResult",
    "model_conversion_assets",
    "hf_models_downloaded",
    "gguf_qwen2_5_math_7b",
    "gguf_uccix_13b",
    "gguf_gemma_2_9b",
    "gguf_qwen2_5_vl_7b",
    "gguf_deepseek_ocr",
    "gguf_z_image_turbo",
    "gguf_qwen_image",
    "gguf_qwen_image_edit",
    "gguf_flux2_dev",
    # Asset generation (BAML → image gen → Garage S3)
    "asset_generation_assets",
    "image_prompts_designed",
    "fibo_configs_built",
    "study_assets_rendered",
    "study_assets_published",
]
