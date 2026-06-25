"""
End-to-End Pipelines for Celtic Education Platform.

Provides complete processing pipelines for:
- Irish document scanning (handwriting, exams, curriculum)
- HTR dataset generation from Dúchas.ie
- VLM model comparison and fine-tuning
- Mobile deployment with federated learning
- Real-time audio streaming (ASR + TTS via Pipecat)

Each pipeline integrates:
- DLT for data ingestion
- Dagster for orchestration
- Modal for GPU compute
- LanceDB Cloud + local lakehouse
- **RisingWave** for streaming (sources, sinks, materialized views, Iceberg)
  — Replaces Confluent Kafka per the RisingWave refactor. See
  `infrastructure/stacks/risingwave/` for the stack
  and `docs/data_engineering/risingwave-*.md` for the patterns.
- MLflow for experiment tracking
"""

from .dialect_classifier import (
    AcousticDialectClassifier,
    DialectClassifier,
    DialectClassifierConfig,
    DialectPrediction,
    IrishDialect,
    LinguisticDialectClassifier,
    Wav2Vec2DialectClassifier,
    batch_classify,
    classify_audio_file,
)
from .irish_document_scanner import (
    DocumentType,
    IrishDocumentScanner,
    Language,
    LineResult,
    PageResult,
    ScannerConfig,
    ScanResult,
    create_scanner,
)
from .transcript_aligner import (
    AlignedPhoneme,
    AlignedWord,
    AlignerConfig,
    AlignmentMethod,
    AlignmentResult,
    CTCAligner,
    DTWAligner,
    TranscriptAligner,
    WhisperXAligner,
    align_audio_file,
    batch_align,
)

__all__ = [
    # Document Scanner
    "IrishDocumentScanner",
    "ScannerConfig",
    "ScanResult",
    "PageResult",
    "LineResult",
    "DocumentType",
    "Language",
    "create_scanner",
    # Dialect Classifier
    "DialectClassifier",
    "DialectClassifierConfig",
    "DialectPrediction",
    "IrishDialect",
    "AcousticDialectClassifier",
    "Wav2Vec2DialectClassifier",
    "LinguisticDialectClassifier",
    "classify_audio_file",
    "batch_classify",
    # Transcript Aligner
    "TranscriptAligner",
    "AlignerConfig",
    "AlignmentResult",
    "AlignedWord",
    "AlignedPhoneme",
    "AlignmentMethod",
    "CTCAligner",
    "DTWAligner",
    "WhisperXAligner",
    "align_audio_file",
    "batch_align",
]
