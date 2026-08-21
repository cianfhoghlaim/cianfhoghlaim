"""
DLT Kafka Source for Confluent Cloud Integration.

Provides incremental Kafka consumption with DLT for:
- Curriculum content streams (curriculum.pages, curriculum.*)
- Embedding completion events (embeddings.generated)
- ML training events (ml.training_jobs, ml.model_artifacts)
- Celtic language processing (celtic.*)

Based on research from taighde/Kafka _ dlt Docs.md:
- Supports pagination types: page_number, offset, cursor, start_from
- Incremental loading with cursor tracking
- Batch processing for high-throughput (batch_size: 3000, timeout: 3)

Usage:
    # Run curriculum pipeline
    from streaming import run_curriculum_pipeline
    run_curriculum_pipeline(topics=["edu.curriculum.pages"])

    # Use as DLT source
    from streaming import confluent_curriculum_source
    pipeline = dlt.pipeline(
        pipeline_name="curriculum_stream",
        destination="duckdb",
    )
    pipeline.run(confluent_curriculum_source())
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Iterator

import dlt
from dlt.sources import DltResource

logger = logging.getLogger(__name__)


@dataclass
class KafkaSourceConfig:
    """Configuration for DLT Kafka source."""

    # Confluent Cloud settings
    bootstrap_servers: str = field(
        default_factory=lambda: os.getenv(
            "CONFLUENT_BOOTSTRAP_SERVERS",
            "pkc-xxxxx.europe-west1.gcp.confluent.cloud:9092",
        )
    )
    api_key: str = field(default_factory=lambda: os.getenv("CONFLUENT_API_KEY", ""))
    api_secret: str = field(default_factory=lambda: os.getenv("CONFLUENT_API_SECRET", ""))

    # Schema Registry
    schema_registry_url: str = field(
        default_factory=lambda: os.getenv(
            "CONFLUENT_SCHEMA_REGISTRY_URL",
            "https://psrc-xxxxx.europe-west1.gcp.confluent.cloud",
        )
    )
    schema_registry_key: str = field(default_factory=lambda: os.getenv("CONFLUENT_SR_API_KEY", ""))
    schema_registry_secret: str = field(
        default_factory=lambda: os.getenv("CONFLUENT_SR_API_SECRET", "")
    )

    # Consumer settings (optimized from research)
    group_id: str = "dlt-curriculum-consumer"
    batch_size: int = 3000  # Optimal batch size from research
    batch_timeout: float = 3.0  # Seconds to wait for batch
    auto_offset_reset: str = "earliest"
    max_poll_records: int = 500

    # Incremental settings
    cursor_field: str = "timestamp"
    initial_cursor: str = field(default_factory=lambda: datetime(2024, 1, 1).isoformat())

    @property
    def consumer_config(self) -> dict[str, Any]:
        """Get confluent-kafka consumer config."""
        return {
            "bootstrap.servers": self.bootstrap_servers,
            "security.protocol": "SASL_SSL",
            "sasl.mechanisms": "PLAIN",
            "sasl.username": self.api_key,
            "sasl.password": self.api_secret,
            "group.id": self.group_id,
            "auto.offset.reset": self.auto_offset_reset,
            "enable.auto.commit": False,
            "max.poll.records": self.max_poll_records,
        }

    def is_configured(self) -> bool:
        """Check if Confluent credentials are configured."""
        return bool(self.api_key and self.api_secret)


def _create_consumer(config: KafkaSourceConfig, topics: list[str]):
    """Create Confluent Kafka consumer."""
    try:
        from confluent_kafka import Consumer, KafkaError

        consumer = Consumer(config.consumer_config)
        consumer.subscribe(topics)
        return consumer

    except ImportError:
        logger.error("confluent-kafka not installed. Install with: pip install confluent-kafka")
        raise


def _deserialize_message(msg, use_avro: bool = False) -> dict[str, Any] | None:
    """Deserialize Kafka message value."""
    if msg.error():
        from confluent_kafka import KafkaError

        if msg.error().code() == KafkaError._PARTITION_EOF:
            return None
        logger.error(f"Kafka error: {msg.error()}")
        return None

    try:
        value = msg.value()
        if value is None:
            return None

        # Try JSON first
        try:
            data = json.loads(value.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Fall back to string
            data = {"raw_value": value.decode("utf-8", errors="replace")}

        # Add message metadata
        data["_kafka_topic"] = msg.topic()
        data["_kafka_partition"] = msg.partition()
        data["_kafka_offset"] = msg.offset()
        data["_kafka_timestamp"] = msg.timestamp()[1] if msg.timestamp()[0] else None
        data["_kafka_key"] = msg.key().decode("utf-8") if msg.key() else None

        return data

    except Exception as e:
        logger.warning(f"Failed to deserialize message: {e}")
        return None


@dlt.source(name="kafka")
def kafka_source(
    topics: list[str],
    config: KafkaSourceConfig | None = None,
    max_messages: int | None = None,
) -> Iterator[DltResource]:
    """
    DLT source for Confluent Kafka topics.

    Args:
        topics: List of Kafka topics to consume
        config: Kafka configuration
        max_messages: Maximum messages to consume (None for unlimited)

    Yields:
        DltResource for each topic with consumed messages
    """
    if config is None:
        config = KafkaSourceConfig()

    if not config.is_configured():
        logger.warning("Kafka not configured, yielding empty resource")
        yield dlt.resource([], name="kafka_empty")
        return

    @dlt.resource(
        name="kafka_messages",
        write_disposition="append",
        primary_key=["_kafka_topic", "_kafka_partition", "_kafka_offset"],
    )
    def consume_messages() -> Iterator[dict[str, Any]]:
        """Consume messages from Kafka topics."""
        consumer = _create_consumer(config, topics)

        try:
            messages_consumed = 0
            batch = []
            batch_start = datetime.now()

            while True:
                # Check message limit
                if max_messages and messages_consumed >= max_messages:
                    logger.info(f"Reached max_messages limit: {max_messages}")
                    break

                # Poll for message
                msg = consumer.poll(timeout=1.0)

                if msg is not None:
                    data = _deserialize_message(msg)
                    if data:
                        batch.append(data)
                        messages_consumed += 1

                # Check if batch is ready
                batch_elapsed = (datetime.now() - batch_start).total_seconds()
                if len(batch) >= config.batch_size or batch_elapsed >= config.batch_timeout:
                    if batch:
                        logger.info(f"Yielding batch of {len(batch)} messages")
                        yield from batch
                        consumer.commit()
                        batch = []
                        batch_start = datetime.now()

                # Check for timeout with no messages
                if msg is None and batch_elapsed >= config.batch_timeout * 2:
                    if batch:
                        yield from batch
                        consumer.commit()
                    break

        except KeyboardInterrupt:
            logger.info("Consumer interrupted")
        finally:
            consumer.close()

    yield consume_messages()


@dlt.source(name="confluent_curriculum")
def confluent_curriculum_source(
    config: KafkaSourceConfig | None = None,
    nations: list[str] | None = None,
) -> Iterator[DltResource]:
    """
    DLT source for curriculum streams from Confluent.

    Consumes:
    - edu.curriculum.pages - Raw curriculum pages
    - edu.curriculum.{nation} - Nation-specific curriculum
    - edu.documents.ingested - Document ingestion events

    Args:
        config: Kafka configuration
        nations: List of nations to consume (default: all)

    Yields:
        DltResource with curriculum data
    """
    if config is None:
        config = KafkaSourceConfig(group_id="dlt-curriculum-consumer")

    if nations is None:
        nations = ["ireland", "england", "scotland", "wales", "northern_ireland"]

    topics = [
        "edu.curriculum.pages",
        "edu.documents.ingested",
    ] + [f"edu.curriculum.{nation}" for nation in nations]

    @dlt.resource(
        name="curriculum_events",
        write_disposition="merge",
        primary_key="id",
    )
    @dlt.defer
    def curriculum_events() -> Iterator[dict[str, Any]]:
        """Consume curriculum events with incremental loading."""
        if not config.is_configured():
            logger.warning("Kafka not configured")
            return

        consumer = _create_consumer(config, topics)

        try:
            messages = 0
            while messages < 10000:  # Safety limit per batch
                msg = consumer.poll(timeout=1.0)

                if msg is None:
                    # No more messages
                    if messages > 0:
                        consumer.commit()
                    break

                data = _deserialize_message(msg)
                if data:
                    # Normalize curriculum event
                    event = {
                        "id": data.get("id", f"{data['_kafka_topic']}_{data['_kafka_offset']}"),
                        "topic": data["_kafka_topic"],
                        "nation": _extract_nation(data["_kafka_topic"]),
                        "content": data.get("content", data.get("text", "")),
                        "url": data.get("url"),
                        "title": data.get("title"),
                        "subject": data.get("subject"),
                        "level": data.get("level"),
                        "metadata": {k: v for k, v in data.items() if not k.startswith("_kafka")},
                        "kafka_timestamp": data["_kafka_timestamp"],
                        "created_at": datetime.utcnow().isoformat(),
                    }
                    yield event
                    messages += 1

        finally:
            consumer.close()

        logger.info(f"Consumed {messages} curriculum events")

    yield curriculum_events()


@dlt.source(name="confluent_embeddings")
def confluent_embedding_source(
    config: KafkaSourceConfig | None = None,
) -> Iterator[DltResource]:
    """
    DLT source for embedding completion events.

    Consumes:
    - edu.embeddings.generated - Embedding batch completion events
    - edu.embeddings.* - Domain-specific embedding events

    Args:
        config: Kafka configuration

    Yields:
        DltResource with embedding completion events
    """
    if config is None:
        config = KafkaSourceConfig(group_id="dlt-embeddings-consumer")

    topics = [
        "edu.embeddings.generated",
    ]

    @dlt.resource(
        name="embedding_events",
        write_disposition="append",
        primary_key=["batch_id", "timestamp"],
    )
    @dlt.defer
    def embedding_events() -> Iterator[dict[str, Any]]:
        """Consume embedding completion events."""
        if not config.is_configured():
            return

        consumer = _create_consumer(config, topics)

        try:
            while True:
                msg = consumer.poll(timeout=1.0)
                if msg is None:
                    consumer.commit()
                    break

                data = _deserialize_message(msg)
                if data:
                    event = {
                        "batch_id": data.get("batch_id", data["_kafka_offset"]),
                        "table": data.get("table", "unknown"),
                        "documents_processed": data.get("documents", 0),
                        "embeddings_created": data.get("embeddings", 0),
                        "model": data.get("model", "BAAI/bge-m3"),
                        "dimensions": data.get("dimensions", 1024),
                        "status": data.get("status", "completed"),
                        "timestamp": data["_kafka_timestamp"],
                    }
                    yield event

        finally:
            consumer.close()

    yield embedding_events()


@dlt.source(name="confluent_ml_events")
def confluent_ml_events_source(
    config: KafkaSourceConfig | None = None,
) -> Iterator[DltResource]:
    """
    DLT source for ML training events.

    Consumes:
    - edu.ml.training_jobs - Training job status events
    - edu.ml.training_metrics - Training metrics (loss, accuracy)
    - edu.ml.model_artifacts - Model artifact events

    Args:
        config: Kafka configuration

    Yields:
        DltResource with ML events
    """
    if config is None:
        config = KafkaSourceConfig(group_id="dlt-ml-events-consumer")

    topics = [
        "edu.ml.training_jobs",
        "edu.ml.training_metrics",
        "edu.ml.model_artifacts",
    ]

    @dlt.resource(
        name="ml_training_events",
        write_disposition="append",
    )
    @dlt.defer
    def ml_events() -> Iterator[dict[str, Any]]:
        """Consume ML training events."""
        if not config.is_configured():
            return

        consumer = _create_consumer(config, topics)

        try:
            while True:
                msg = consumer.poll(timeout=1.0)
                if msg is None:
                    consumer.commit()
                    break

                data = _deserialize_message(msg)
                if data:
                    event_type = data["_kafka_topic"].split(".")[-1]
                    event = {
                        "event_type": event_type,
                        "job_id": data.get("job_id"),
                        "model_name": data.get("model_name"),
                        "status": data.get("status"),
                        "metrics": data.get("metrics", {}),
                        "artifacts": data.get("artifacts", []),
                        "timestamp": data["_kafka_timestamp"],
                        "raw_data": data,
                    }
                    yield event

        finally:
            consumer.close()

    yield ml_events()


def _extract_nation(topic: str) -> str:
    """Extract nation from topic name."""
    nation_map = {
        "ireland": "ireland",
        "england": "england",
        "scotland": "scotland",
        "wales": "wales",
        "northern_ireland": "northern_ireland",
        "ni": "northern_ireland",
    }

    parts = topic.split(".")
    for part in parts:
        if part.lower() in nation_map:
            return nation_map[part.lower()]

    return "unknown"


def run_curriculum_pipeline(
    topics: list[str] | None = None,
    destination: str = "duckdb",
    dataset_name: str = "curriculum_stream",
    max_messages: int | None = None,
) -> dict[str, Any]:
    """
    Run curriculum streaming pipeline.

    Args:
        topics: Topics to consume (default: curriculum topics)
        destination: DLT destination (duckdb, lancedb, etc.)
        dataset_name: Dataset name for destination
        max_messages: Maximum messages to consume

    Returns:
        Pipeline run info
    """
    if topics is None:
        topics = [
            "edu.curriculum.pages",
            "edu.curriculum.ireland",
            "edu.documents.ingested",
        ]

    pipeline = dlt.pipeline(
        pipeline_name="curriculum_kafka_stream",
        destination=destination,
        dataset_name=dataset_name,
    )

    config = KafkaSourceConfig(
        group_id=f"dlt-{dataset_name}-{datetime.now().strftime('%Y%m%d')}",
    )

    # Run pipeline
    info = pipeline.run(kafka_source(topics=topics, config=config, max_messages=max_messages))

    logger.info(f"Pipeline completed: {info}")

    return {
        "pipeline_name": pipeline.pipeline_name,
        "destination": destination,
        "dataset_name": dataset_name,
        "topics": topics,
        "load_info": str(info),
    }
