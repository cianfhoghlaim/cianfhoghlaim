"""
Kafka producers for Celtic education data pipeline.

Produces education data to Confluent Cloud topics:
- edu.curriculum.* - Curriculum content from all nations
- edu.documents.ingested - Document ingestion events
- edu.embeddings.generated - Generated embeddings
- edu.alignment.* - Bilingual alignment events
- celtic.* - Celtic language processing events
"""

import json
import logging
from collections.abc import Iterator
from datetime import datetime
from typing import Any
from uuid import uuid4

from .config import KafkaConfig, get_kafka_config

logger = logging.getLogger(__name__)

# Lazy import to avoid errors when confluent-kafka not installed
Producer = None


def _get_producer_class():
    """Lazy load Producer class."""
    global Producer
    if Producer is None:
        from confluent_kafka import Producer as _Producer

        Producer = _Producer
    return Producer


class EducationProducer:
    """
    Kafka producer for education data with Datadog trace context propagation.

    Produces to Confluent Cloud topics with:
    - JSON serialization (Schema Registry optional)
    - Delivery callbacks for monitoring
    - Trace context in headers for distributed tracing
    - Multi-nation support for Ireland, UK, and Celtic languages
    """

    def __init__(self, config: KafkaConfig | None = None):
        self.config = config or get_kafka_config()
        self._producer = None

    def _ensure_producer(self) -> None:
        """Initialize producer lazily."""
        if self._producer is None:
            if not self.config.is_configured():
                logger.warning("Kafka not configured, skipping producer initialization")
                return
            ProducerClass = _get_producer_class()
            self._producer = ProducerClass(self.config.cluster.producer_config)

    def _delivery_callback(self, err, msg):
        """Handle delivery reports."""
        if err:
            logger.error(f"Delivery failed for {msg.topic()}: {err}")
        else:
            logger.debug(f"Delivered to {msg.topic()} [{msg.partition()}] @ {msg.offset()}")

    def _get_trace_headers(self) -> list[tuple[str, bytes]]:
        """Get Datadog trace context headers for distributed tracing."""
        headers = []
        try:
            from ddtrace import tracer

            span = tracer.current_span()
            if span:
                headers.extend(
                    [
                        ("x-datadog-trace-id", str(span.trace_id).encode()),
                        ("x-datadog-parent-id", str(span.span_id).encode()),
                        ("x-datadog-sampling-priority", b"1"),
                    ]
                )
        except ImportError:
            pass
        return headers

    def produce_curriculum_page(
        self,
        url: str,
        title: str | None,
        markdown: str | None,
        language: str,
        education_level: str | None,
        subject: str | None,
        source: str,
        nation: str = "ireland",
        status: str = "success",
    ) -> None:
        """Produce a crawled curriculum page event."""
        self._ensure_producer()
        if self._producer is None:
            return

        # Route to nation-specific topic if available
        topic_key = f"curriculum_{nation}" if f"curriculum_{nation}" in self.config.topics else "curriculum_pages"
        topic = self.config.topics[topic_key]

        record = {
            "url": url,
            "title": title,
            "markdown": markdown,
            "language": language.upper() if language else "EN",
            "education_level": education_level,
            "subject": subject,
            "source": source,
            "nation": nation,
            "crawled_at": int(datetime.utcnow().timestamp() * 1000),
            "status": status,
        }

        self._producer.produce(
            topic=topic,
            key=url.encode("utf-8"),
            value=json.dumps(record).encode("utf-8"),
            headers=self._get_trace_headers(),
            callback=self._delivery_callback,
        )

    def produce_document_ingested(
        self,
        document_id: str,
        file_path: str,
        document_type: str,
        education_level: str | None,
        subject: str | None,
        extracted_text: str | None,
        nation: str = "ireland",
        language: str = "en",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Produce a document ingestion event."""
        self._ensure_producer()
        if self._producer is None:
            return

        topic = self.config.topics["documents_ingested"]

        record = {
            "document_id": document_id,
            "file_path": file_path,
            "document_type": document_type,
            "education_level": education_level,
            "subject": subject,
            "extracted_text": extracted_text,
            "nation": nation,
            "language": language,
            "metadata": json.dumps(metadata) if metadata else "{}",
            "ingested_at": int(datetime.utcnow().timestamp() * 1000),
        }

        self._producer.produce(
            topic=topic,
            key=document_id.encode("utf-8"),
            value=json.dumps(record).encode("utf-8"),
            headers=self._get_trace_headers(),
            callback=self._delivery_callback,
        )

    def produce_alignment_pair(
        self,
        source_text: str,
        target_text: str,
        source_lang: str,
        target_lang: str,
        alignment_score: float,
        source_url: str | None = None,
        alignment_method: str = "hybrid",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Produce a bilingual alignment pair event."""
        self._ensure_producer()
        if self._producer is None:
            return

        topic = self.config.topics["alignment_pairs"]
        pair_id = str(uuid4())

        record = {
            "pair_id": pair_id,
            "source_text": source_text,
            "target_text": target_text,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "alignment_score": alignment_score,
            "alignment_method": alignment_method,
            "source_url": source_url,
            "metadata": json.dumps(metadata) if metadata else "{}",
            "aligned_at": int(datetime.utcnow().timestamp() * 1000),
        }

        self._producer.produce(
            topic=topic,
            key=pair_id.encode("utf-8"),
            value=json.dumps(record).encode("utf-8"),
            headers=self._get_trace_headers(),
            callback=self._delivery_callback,
        )

    def produce_embedding(
        self,
        document_id: str,
        chunk_index: int,
        text: str,
        embedding: list[float],
        model: str,
        nation: str = "ireland",
        language: str = "en",
    ) -> None:
        """Produce an embedding record."""
        self._ensure_producer()
        if self._producer is None:
            return

        topic = self.config.topics["embeddings_generated"]

        record = {
            "id": f"{document_id}_{chunk_index}",
            "document_id": document_id,
            "chunk_index": chunk_index,
            "text": text[:1000],  # Truncate text for efficiency
            "embedding": embedding,
            "model": model,
            "nation": nation,
            "language": language,
            "created_at": int(datetime.utcnow().timestamp() * 1000),
        }

        self._producer.produce(
            topic=topic,
            key=record["id"].encode("utf-8"),
            value=json.dumps(record).encode("utf-8"),
            headers=self._get_trace_headers(),
            callback=self._delivery_callback,
        )

    def produce_graph_cdc_event(
        self,
        event_type: str,
        node_id: str,
        node_type: str,
        properties: dict[str, Any],
        relationships: list[dict[str, Any]] | None = None,
    ) -> None:
        """Produce a graph CDC event from knowledge graph."""
        self._ensure_producer()
        if self._producer is None:
            return

        topic = self.config.topics["graph_cdc"]

        record = {
            "event_id": str(uuid4()),
            "event_type": event_type,
            "node_id": node_id,
            "node_type": node_type,
            "properties": properties,
            "relationships": relationships or [],
            "timestamp": int(datetime.utcnow().timestamp() * 1000),
        }

        self._producer.produce(
            topic=topic,
            key=node_id.encode("utf-8"),
            value=json.dumps(record).encode("utf-8"),
            headers=self._get_trace_headers(),
            callback=self._delivery_callback,
        )

    def produce_celtic_event(
        self,
        event_type: str,
        content: dict[str, Any],
        language: str,
        source: str,
    ) -> None:
        """Produce a Celtic language processing event."""
        self._ensure_producer()
        if self._producer is None:
            return

        # Route to appropriate Celtic topic
        topic_map = {
            "folklore": "celtic_folklore",
            "pronunciation": "celtic_pronunciation",
            "terminology": "celtic_terminology",
            "translation": "celtic_translation",
        }
        topic_key = topic_map.get(event_type, "celtic_folklore")
        topic = self.config.topics[topic_key]

        event_id = str(uuid4())
        record = {
            "event_id": event_id,
            "event_type": event_type,
            "content": content,
            "language": language,
            "source": source,
            "timestamp": int(datetime.utcnow().timestamp() * 1000),
        }

        self._producer.produce(
            topic=topic,
            key=event_id.encode("utf-8"),
            value=json.dumps(record).encode("utf-8"),
            headers=self._get_trace_headers(),
            callback=self._delivery_callback,
        )

    def produce_batch(
        self,
        topic_key: str,
        records: Iterator[dict[str, Any]],
        key_field: str = "id",
    ) -> int:
        """Produce a batch of records to a topic."""
        self._ensure_producer()
        if self._producer is None:
            return 0

        topic = self.config.topics[topic_key]
        count = 0

        for record in records:
            key = str(record.get(key_field, uuid4()))
            self._producer.produce(
                topic=topic,
                key=key.encode("utf-8"),
                value=json.dumps(record).encode("utf-8"),
                headers=self._get_trace_headers(),
                callback=self._delivery_callback,
            )
            count += 1

            # Flush periodically to avoid buffer overflow
            if count % 1000 == 0:
                self._producer.poll(0)

        return count

    def flush(self, timeout: float = 30.0) -> int:
        """Flush pending messages."""
        if self._producer:
            return self._producer.flush(timeout)
        return 0

    def close(self) -> None:
        """Close the producer."""
        if self._producer:
            self._producer.flush()
            self._producer = None


# Singleton instance
_producer: EducationProducer | None = None


def get_producer() -> EducationProducer:
    """Get the education producer singleton."""
    global _producer
    if _producer is None:
        _producer = EducationProducer()
    return _producer
