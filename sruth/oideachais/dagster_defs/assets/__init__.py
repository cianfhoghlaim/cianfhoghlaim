"""
Dagster Assets for Celtic Education Platform.

Asset Groups:
- ireland_education: Irish curriculum, exams, PDFs
- uk_education: UK nations education statistics
- celtic_language: Folklore, pronunciation, treebanks
- geospatial: Boundaries and locations
- cross_domain: Enriched cross-domain assets
- search_indexes: Unified search indexes
- embeddings: Vector embeddings with observability
- evaluation: RAG quality and agent metrics
- ml_training: OCR model training pipeline

All assets support independent execution via partitions.

Observability:
- MLflow experiment tracking
- Langfuse LLM tracing
- Ragas RAG evaluation
- Kafka event streaming
"""
# Note: Removed future annotations for Dagster compatibility

# NOTE: ie_education_assets removed - replaced by unified curriculum assets
from .uk_education_assets import uk_education_assets
from .celtic_language_assets import celtic_language_assets
from .geospatial_assets import geospatial_assets
from .enriched_assets import enriched_assets
from .search_assets import search_assets
from .embedding_assets import embedding_assets
from .ml_training import ml_training_assets
from .duchas_assets import (
    duchas_assets,
    duchas_county_partitions,
    duchas_volume_partitions,
    duchas_county_job,
    duchas_full_pipeline_job,
)
# NOTE: sec_exams_assets removed - replaced by unified curriculum assets
from .ocr_comparison_assets import (
    ocr_source_documents,
    ocr_model_comparison,
    vision_model_comparison,
    ocr_irish_validation,
    ocr_embeddings,
    ocr_comparison_report,
    ocr_comparison_job,
    ocr_comparison_daily_schedule,
    document_source_partitions,
    ocr_model_partitions,
    vision_model_partitions,
)
from .modal_assets import (
    modal_assets,
    modal_curriculum_embeddings,
    modal_ocr_embeddings,
    modal_irish_llm_finetune,
    modal_irish_llm_evaluation,
    ModalEmbeddingConfig,
    ModalFinetuneConfig,
)
from .htr_training_assets import (
    htr_training_assets,
    duchas_pages,
    segmented_lines,
    training_dataset,
    vlm_finetune,
    model_comparison,
    mobile_deployment,
    htr_training_job,
    htr_daily_schedule,
    county_partitions,
    vlm_partitions,
    HTRDatasetConfig,
    VLMFinetuneConfig,
)
from .multi_nation_curriculum_assets import (
    multi_nation_curriculum_assets,
    ireland_ncca_curriculum,
    ireland_oide_cpd,
    england_national_curriculum,
    england_exam_boards,
    scotland_cfe,
    scotland_sqa,
    wales_curriculum,
    wales_wjec,
    northern_ireland_curriculum,
    northern_ireland_ccea_quals,
    curriculum_structured_extraction,
    curriculum_unified_embeddings,
    curriculum_outcome_alignments,
    curriculum_comparison_report,
)

# OCR comparison assets
ocr_comparison_assets = [
    ocr_source_documents,
    ocr_model_comparison,
    vision_model_comparison,
    ocr_irish_validation,
    ocr_embeddings,
    ocr_comparison_report,
]

# Combine all assets
# NOTE: ireland_education_assets and sec_exam_assets removed - use unified curriculum assets
all_assets = [
    *uk_education_assets,
    *celtic_language_assets,
    *geospatial_assets,
    *enriched_assets,
    *search_assets,
    *embedding_assets,
    *ml_training_assets,
    *ocr_comparison_assets,
    *duchas_assets,
    *modal_assets,
    *htr_training_assets,
    *multi_nation_curriculum_assets,
]

__all__ = [
    "all_assets",
    # NOTE: ireland_education_assets removed
    "uk_education_assets",
    "celtic_language_assets",
    "geospatial_assets",
    "enriched_assets",
    "search_assets",
    "embedding_assets",
    "ml_training_assets",
    "ocr_comparison_assets",
    # OCR comparison exports
    "ocr_source_documents",
    "ocr_model_comparison",
    "vision_model_comparison",
    "ocr_irish_validation",
    "ocr_embeddings",
    "ocr_comparison_report",
    "ocr_comparison_job",
    "ocr_comparison_daily_schedule",
    "document_source_partitions",
    "ocr_model_partitions",
    "vision_model_partitions",
    # Dúchas.ie exports
    "duchas_assets",
    "duchas_county_partitions",
    "duchas_volume_partitions",
    "duchas_county_job",
    "duchas_full_pipeline_job",
    # NOTE: SEC Exams exports removed - use unified curriculum assets
    # Modal GPU exports
    "modal_assets",
    "modal_curriculum_embeddings",
    "modal_ocr_embeddings",
    "modal_irish_llm_finetune",
    "modal_irish_llm_evaluation",
    "ModalEmbeddingConfig",
    "ModalFinetuneConfig",
    # HTR Training exports
    "htr_training_assets",
    "duchas_pages",
    "segmented_lines",
    "training_dataset",
    "vlm_finetune",
    "model_comparison",
    "mobile_deployment",
    "htr_training_job",
    "htr_daily_schedule",
    "county_partitions",
    "vlm_partitions",
    "HTRDatasetConfig",
    "VLMFinetuneConfig",
    # Multi-nation curriculum exports
    "multi_nation_curriculum_assets",
    "ireland_ncca_curriculum",
    "ireland_oide_cpd",
    "england_national_curriculum",
    "england_exam_boards",
    "scotland_cfe",
    "scotland_sqa",
    "wales_curriculum",
    "wales_wjec",
    "northern_ireland_curriculum",
    "northern_ireland_ccea_quals",
    "curriculum_structured_extraction",
    "curriculum_unified_embeddings",
    "curriculum_outcome_alignments",
    "curriculum_comparison_report",
]
