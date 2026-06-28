"""
Streaming Integration for Celtic Education Platform.

Provides:
- DLT Kafka source for Confluent Cloud ingestion
- Incremental loading with cursor tracking
- Schema Registry integration for BAML schemas
- Topic routing for curriculum, OCR, and ML events
"""
from .kafka_dlt_source import (
    KafkaSourceConfig,
    confluent_curriculum_source,
    confluent_embedding_source,
    confluent_ml_events_source,
    kafka_source,
    run_curriculum_pipeline,
)

__all__ = [
    "KafkaSourceConfig",
    "confluent_curriculum_source",
    "confluent_embedding_source",
    "confluent_ml_events_source",
    "kafka_source",
    "run_curriculum_pipeline",
]
