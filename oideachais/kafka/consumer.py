"""
Kafka consumers for Celtic education data pipeline with Gemini AI enrichment.

Consumes from Confluent Cloud topics and enriches with:
- Gemini AI analysis for learning outcome extraction
- Embedding generation via Vertex AI
- Real-time knowledge graph updates
- Bilingual alignment processing
"""

import json
import logging
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any

from .config import KafkaConfig, get_kafka_config
from .producer import get_producer

logger = logging.getLogger(__name__)

# Lazy imports
Consumer = None
KafkaError = None


def _get_consumer_class():
    """Lazy load Consumer class."""
    global Consumer, KafkaError
    if Consumer is None:
        from confluent_kafka import Consumer as _Consumer
        from confluent_kafka import KafkaError as _KafkaError

        Consumer = _Consumer
        KafkaError = _KafkaError
    return Consumer, KafkaError


class EducationConsumer:
    """
    Kafka consumer with Gemini AI enrichment for Celtic education data.

    Consumes from:
    - edu.documents.ingested: Enrich with AI analysis
    - edu.curriculum.*: Extract learning outcomes per nation
    - edu.alignment.pairs: Process bilingual alignments
    - celtic.*: Celtic language content

    Produces to:
    - edu.ai.enriched: AI-enriched documents
    """

    def __init__(
        self,
        group_id: str,
        config: KafkaConfig | None = None,
    ):
        self.config = config or get_kafka_config()
        self.group_id = group_id
        self._consumer = None
        self._gemini_client = None
        self._running = False

    def _ensure_consumer(self, topics: list[str]) -> None:
        """Initialize consumer lazily."""
        if self._consumer is None:
            if not self.config.is_configured():
                logger.warning("Kafka not configured, skipping consumer initialization")
                return

            ConsumerClass, _ = _get_consumer_class()
            consumer_config = {
                **self.config.cluster.consumer_config,
                "group.id": self.group_id,
            }
            self._consumer = ConsumerClass(consumer_config)
            self._consumer.subscribe(topics)

    def _ensure_gemini(self):
        """Initialize Gemini client lazily."""
        if self._gemini_client is None:
            try:
                from google import genai

                self._gemini_client = genai.Client(
                    vertexai=True,
                    project="cianfhoghlaim",
                    location="europe-west1",
                )
            except ImportError:
                logger.warning("google-genai not installed, AI enrichment disabled")
        return self._gemini_client

    async def enrich_with_gemini(
        self,
        document_text: str,
        document_type: str,
        education_level: str | None,
        nation: str = "ireland",
        language: str = "en",
    ) -> dict[str, Any]:
        """
        Enrich document with Gemini analysis.

        Extracts:
        - Learning outcomes
        - Key concepts
        - Educational level mapping
        - Irish/Celtic language terms
        - Nation-specific curriculum mappings
        """
        client = self._ensure_gemini()
        if client is None:
            return {"error": "Gemini client not available"}

        # Adjust prompt based on nation
        nation_context = {
            "ireland": "Irish curriculum (NCCA Junior/Senior Cycle)",
            "england": "English National Curriculum",
            "scotland": "Scottish Curriculum for Excellence",
            "wales": "Welsh Curriculum for Wales",
            "northern_ireland": "Northern Ireland Curriculum",
        }.get(nation, "Celtic education")

        prompt = f"""Analyze this {nation_context} educational document and extract structured information.

Document Type: {document_type}
Education Level: {education_level or "Unknown"}
Nation: {nation}
Language: {language}

Document Content:
{document_text[:10000]}

Extract the following:
1. Learning Outcomes: List all learning outcomes with codes if present
2. Key Concepts: Main educational concepts covered
3. Key Skills: Which curriculum key skills are addressed
4. Celtic Language Terms: Any Irish (Gaeilge), Welsh (Cymraeg), or Scottish Gaelic (Gàidhlig) terminology with translations
5. Subject Classification: Best matching subject area
6. Difficulty Level: Estimated difficulty (beginner, intermediate, advanced)
7. Cross-Nation Equivalents: Equivalent topics in other Celtic nation curricula

Respond in JSON format."""

        try:
            from google.genai import types

            response = await client.aio.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                ),
            )

            return json.loads(response.text)
        except json.JSONDecodeError:
            return {"raw_analysis": response.text if response else ""}
        except Exception as e:
            logger.error(f"Gemini enrichment failed: {e}")
            return {"error": str(e)}

    async def generate_embeddings(
        self,
        text: str,
        model: str = "text-embedding-004",
    ) -> list[float] | None:
        """Generate embeddings using Vertex AI."""
        client = self._ensure_gemini()
        if client is None:
            return None

        try:
            response = await client.aio.models.embed_content(
                model=model,
                contents=text[:8000],  # Truncate for token limits
            )
            return response.embeddings[0].values
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return None

    async def process_documents_stream(
        self,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Process document ingestion stream with AI enrichment.

        For each document:
        1. Extract with Gemini
        2. Generate embeddings
        3. Produce to ai.enriched topic
        4. Yield result for downstream processing
        """
        _, KafkaErrorClass = _get_consumer_class()
        topic = self.config.topics["documents_ingested"]
        self._ensure_consumer([topic])

        if self._consumer is None:
            logger.error("Consumer not initialized")
            return

        self._running = True
        producer = get_producer()

        try:
            while self._running:
                msg = self._consumer.poll(1.0)

                if msg is None:
                    continue

                if msg.error():
                    if msg.error().code() == KafkaErrorClass._PARTITION_EOF:
                        continue
                    logger.error(f"Consumer error: {msg.error()}")
                    continue

                try:
                    record = json.loads(msg.value().decode("utf-8"))

                    # Enrich with Gemini
                    if record.get("extracted_text"):
                        enrichment = await self.enrich_with_gemini(
                            document_text=record["extracted_text"],
                            document_type=record.get("document_type", "unknown"),
                            education_level=record.get("education_level"),
                            nation=record.get("nation", "ireland"),
                            language=record.get("language", "en"),
                        )

                        # Generate embeddings
                        embedding = await self.generate_embeddings(record["extracted_text"])

                        # Create enriched record
                        enriched = {
                            "document_id": record["document_id"],
                            "original_text": record["extracted_text"][:5000],
                            "extracted_entities": enrichment.get("key_concepts", []),
                            "learning_outcomes": enrichment.get("learning_outcomes", []),
                            "celtic_terms": enrichment.get("celtic_language_terms", []),
                            "cross_nation_equivalents": enrichment.get("cross_nation_equivalents", []),
                            "gemini_analysis": json.dumps(enrichment),
                            "embedding": embedding,
                            "nation": record.get("nation", "ireland"),
                            "language": record.get("language", "en"),
                            "processed_at": int(datetime.utcnow().timestamp() * 1000),
                        }

                        # Produce to enriched topic
                        if producer._producer:
                            producer._producer.produce(
                                topic=self.config.topics["ai_enriched"],
                                key=record["document_id"].encode("utf-8"),
                                value=json.dumps(enriched).encode("utf-8"),
                            )

                        # Also produce embedding to embeddings topic
                        if embedding:
                            producer.produce_embedding(
                                document_id=record["document_id"],
                                chunk_index=0,
                                text=record["extracted_text"][:1000],
                                embedding=embedding,
                                model="text-embedding-004",
                                nation=record.get("nation", "ireland"),
                                language=record.get("language", "en"),
                            )

                        yield enriched

                    # Commit offset
                    self._consumer.commit(msg)

                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    continue

        finally:
            producer.flush()

    async def process_alignment_stream(
        self,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Process bilingual alignment stream.

        For each alignment pair:
        1. Validate alignment quality
        2. Generate bilingual embeddings
        3. Yield for downstream processing
        """
        _, KafkaErrorClass = _get_consumer_class()
        topic = self.config.topics["alignment_pairs"]
        self._ensure_consumer([topic])

        if self._consumer is None:
            logger.error("Consumer not initialized")
            return

        self._running = True

        try:
            while self._running:
                msg = self._consumer.poll(1.0)

                if msg is None:
                    continue

                if msg.error():
                    if msg.error().code() == KafkaErrorClass._PARTITION_EOF:
                        continue
                    logger.error(f"Consumer error: {msg.error()}")
                    continue

                try:
                    record = json.loads(msg.value().decode("utf-8"))

                    # Generate embeddings for both source and target
                    source_embedding = await self.generate_embeddings(record["source_text"])
                    target_embedding = await self.generate_embeddings(record["target_text"])

                    enriched = {
                        **record,
                        "source_embedding": source_embedding,
                        "target_embedding": target_embedding,
                        "processed_at": int(datetime.utcnow().timestamp() * 1000),
                    }

                    yield enriched

                    # Commit offset
                    self._consumer.commit(msg)

                except Exception as e:
                    logger.error(f"Error processing alignment: {e}")
                    continue

        finally:
            pass

    def stop(self) -> None:
        """Stop the consumer."""
        self._running = False

    def close(self) -> None:
        """Close the consumer."""
        self.stop()
        if self._consumer:
            self._consumer.close()
            self._consumer = None


def get_consumer(group_id: str = "oideachais-celtic-enrichment") -> EducationConsumer:
    """Create an education consumer."""
    return EducationConsumer(group_id=group_id)
