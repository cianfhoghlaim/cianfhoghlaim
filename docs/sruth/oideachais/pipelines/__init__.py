"""
End-to-End Pipelines for Celtic Education Platform.

Provides complete processing pipelines for:
- Irish document scanning (handwriting, exams, curriculum)
- HTR dataset generation from Dúchas.ie
- VLM model comparison and fine-tuning
- Mobile deployment with federated learning

Each pipeline integrates:
- DLT for data ingestion
- Dagster for orchestration
- Modal for GPU compute
- LanceDB Cloud + local lakehouse
- Confluent Kafka for streaming
- MLflow for experiment tracking
"""

from .irish_document_scanner import (
    IrishDocumentScanner,
    ScannerConfig,
    ScanResult,
    PageResult,
    LineResult,
    DocumentType,
    Language,
    create_scanner,
)

__all__ = [
    "IrishDocumentScanner",
    "ScannerConfig",
    "ScanResult",
    "PageResult",
    "LineResult",
    "DocumentType",
    "Language",
    "create_scanner",
]
