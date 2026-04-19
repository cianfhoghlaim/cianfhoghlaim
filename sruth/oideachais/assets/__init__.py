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
from .canuint_alignment_assets import (
    CanuintAlignmentConfig,
    canuint_alignment_assets,
    canuint_alignment_embeddings,
    canuint_audio_slices,
    canuint_character_alignments,
    canuint_huggingface_dataset,
    canuint_ljspeech_dataset,
    canuint_multi_format_export,
    canuint_phoneme_alignments,
    canuint_recording_metadata,
    canuint_word_alignments,
)
from .celtic_language_assets import celtic_language_assets
from .duchas_assets import (
    duchas_assets,
    duchas_county_job,
    duchas_county_partitions,
    duchas_full_pipeline_job,
    duchas_volume_partitions,
)
from .embedding_assets import embedding_assets
from .enriched_assets import enriched_assets
from .geospatial_assets import geospatial_assets
from .htr_training_assets import (
    HTRDatasetConfig,
    VLMFinetuneConfig,
    county_partitions,
    duchas_pages,
    htr_daily_schedule,
    htr_training_assets,
    htr_training_job,
    mobile_deployment,
    model_comparison,
    segmented_lines,
    training_dataset,
    vlm_finetune,
    vlm_partitions,
)
from .ml_training import ml_training_assets
from .modal_assets import (
    ModalEmbeddingConfig,
    ModalFinetuneConfig,
    modal_assets,
    modal_curriculum_embeddings,
    modal_irish_llm_evaluation,
    modal_irish_llm_finetune,
    modal_ocr_embeddings,
)
from .multi_nation_curriculum_assets import (
    curriculum_comparison_report,
    curriculum_outcome_alignments,
    curriculum_structured_extraction,
    curriculum_unified_embeddings,
    england_exam_boards,
    england_national_curriculum,
    ireland_ncca_curriculum,
    ireland_oide_cpd,
    multi_nation_curriculum_assets,
    northern_ireland_ccea_quals,
    northern_ireland_curriculum,
    scotland_cfe,
    scotland_sqa,
    wales_curriculum,
    wales_wjec,
)

# NOTE: sec_exams_assets removed - replaced by unified curriculum assets
from .ocr_comparison_assets import (
    document_source_partitions,
    ocr_comparison_daily_schedule,
    ocr_comparison_job,
    ocr_comparison_report,
    ocr_embeddings,
    ocr_irish_validation,
    ocr_model_comparison,
    ocr_model_partitions,
    ocr_source_documents,
    vision_model_comparison,
    vision_model_partitions,
)
from .search_assets import search_assets
from .uk_education_assets import uk_education_assets
from .unified_audio_dataset_assets import (
    EdcoLearningExtractionConfig,
    SECTranscriptConfig,
    UnifiedAudioConfig,
    dialect_balanced_split,
    edcolearning_audio_extraction,
    huggingface_dataset_export,
    sec_aural_transcripts,
    unified_audio_assets,
    unified_combined_dataset,
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
    *canuint_alignment_assets,
    *unified_audio_assets,
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
    # Canuint alignment exports
    "canuint_alignment_assets",
    "canuint_word_alignments",
    "canuint_recording_metadata",
    "canuint_character_alignments",
    "canuint_phoneme_alignments",
    "canuint_audio_slices",
    "canuint_ljspeech_dataset",
    "canuint_huggingface_dataset",
    "canuint_multi_format_export",
    "canuint_alignment_embeddings",
    "CanuintAlignmentConfig",
    # Unified audio dataset exports
    "unified_audio_assets",
    "edcolearning_audio_extraction",
    "sec_aural_transcripts",
    "unified_combined_dataset",
    "dialect_balanced_split",
    "huggingface_dataset_export",
    "UnifiedAudioConfig",
    "EdcoLearningExtractionConfig",
    "SECTranscriptConfig",
]
