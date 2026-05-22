"""
Confluent Cloud Kafka configuration for oideachais Celtic education pipeline.

Configuration for:
- Confluent Cloud cluster connection (development - $400 credits)
- Self-hosted Kafka cluster (production)
- Schema Registry integration
- Topic naming conventions for multi-nation education data
- Celtic language processing topics
- Dúchas.ie and Canúint.ie scraping pipelines
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class KafkaEnvironment(str, Enum):
    """Kafka deployment environment."""

    DEVELOPMENT = "development"  # Confluent Cloud
    PRODUCTION = "production"  # Self-hosted


@dataclass
class ConfluentCloudConfig:
    """Confluent Cloud cluster configuration (development)."""

    bootstrap_servers: str = field(
        default_factory=lambda: os.getenv(
            "CONFLUENT_BOOTSTRAP_SERVERS",
            "pkc-xxxxx.europe-west1.gcp.confluent.cloud:9092",
        )
    )
    api_key: str = field(default_factory=lambda: os.getenv("CONFLUENT_API_KEY", ""))
    api_secret: str = field(default_factory=lambda: os.getenv("CONFLUENT_API_SECRET", ""))


@dataclass
class SelfHostedKafkaConfig:
    """Self-hosted Kafka cluster configuration (production on Hetzner)."""

    bootstrap_servers: str = field(
        default_factory=lambda: os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS",
            "kafka.cianfhoghlaim.ie:9092",
        )
    )

    @property
    def producer_config(self) -> dict[str, Any]:
        """Get producer configuration for self-hosted Kafka."""
        return {
            "bootstrap.servers": self.bootstrap_servers,
            "acks": "all",
            "enable.idempotence": True,
            "retries": 3,
            "linger.ms": 5,
            "batch.size": 16384,
            "compression.type": "lz4",
        }

    @property
    def consumer_config(self) -> dict[str, Any]:
        """Get consumer configuration for self-hosted Kafka."""
        return {
            "bootstrap.servers": self.bootstrap_servers,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
            "max.poll.interval.ms": 300000,
        }

    @property
    def producer_config(self) -> dict[str, Any]:
        """Get producer configuration for Confluent Cloud."""
        return {
            "bootstrap.servers": self.bootstrap_servers,
            "security.protocol": "SASL_SSL",
            "sasl.mechanisms": "PLAIN",
            "sasl.username": self.api_key,
            "sasl.password": self.api_secret,
            "acks": "all",
            "enable.idempotence": True,
            "retries": 3,
            "linger.ms": 5,
            "batch.size": 16384,
            "compression.type": "lz4",
        }

    @property
    def consumer_config(self) -> dict[str, Any]:
        """Get consumer configuration for Confluent Cloud."""
        return {
            "bootstrap.servers": self.bootstrap_servers,
            "security.protocol": "SASL_SSL",
            "sasl.mechanisms": "PLAIN",
            "sasl.username": self.api_key,
            "sasl.password": self.api_secret,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
            "max.poll.interval.ms": 300000,
        }


@dataclass
class SchemaRegistryConfig:
    """Confluent Schema Registry configuration."""

    url: str = field(
        default_factory=lambda: os.getenv(
            "CONFLUENT_SCHEMA_REGISTRY_URL",
            "https://psrc-xxxxx.europe-west1.gcp.confluent.cloud",
        )
    )
    api_key: str = field(default_factory=lambda: os.getenv("CONFLUENT_SR_API_KEY", ""))
    api_secret: str = field(default_factory=lambda: os.getenv("CONFLUENT_SR_API_SECRET", ""))

    @property
    def config(self) -> dict[str, str]:
        """Get Schema Registry configuration."""
        return {
            "url": self.url,
            "basic.auth.user.info": f"{self.api_key}:{self.api_secret}",
        }


@dataclass
class KafkaConfig:
    """Unified Kafka configuration for Celtic education pipeline.

    Supports hybrid deployment:
    - Development: Confluent Cloud ($400 credits)
    - Production: Self-hosted Kafka on Hetzner CAX41
    """

    environment: KafkaEnvironment = field(
        default_factory=lambda: KafkaEnvironment(
            os.getenv("KAFKA_ENVIRONMENT", "development")
        )
    )
    confluent: ConfluentCloudConfig = field(default_factory=ConfluentCloudConfig)
    selfhosted: SelfHostedKafkaConfig = field(default_factory=SelfHostedKafkaConfig)
    schema_registry: SchemaRegistryConfig = field(default_factory=SchemaRegistryConfig)

    # Topic prefix for all education topics
    topic_prefix: str = "edu"
    celtic_prefix: str = "celtic"

    @property
    def cluster(self) -> ConfluentCloudConfig | SelfHostedKafkaConfig:
        """Get active cluster configuration based on environment."""
        if self.environment == KafkaEnvironment.PRODUCTION:
            return self.selfhosted
        return self.confluent

    @property
    def producer_config(self) -> dict[str, Any]:
        """Get producer config for active environment."""
        return self.cluster.producer_config

    @property
    def consumer_config(self) -> dict[str, Any]:
        """Get consumer config for active environment."""
        return self.cluster.consumer_config

    @property
    def topics(self) -> dict[str, str]:
        """Get all topic names for education pipeline."""
        return {
            # Content ingestion topics (Ireland)
            "curriculum_pages": f"{self.topic_prefix}.curriculum.pages",
            "examiner_reports": f"{self.topic_prefix}.examiner.reports",
            "documents_ingested": f"{self.topic_prefix}.documents.ingested",

            # Processing topics
            "graph_cdc": f"{self.topic_prefix}.graph.cdc",
            "embeddings_generated": f"{self.topic_prefix}.embeddings.generated",
            "ai_enriched": f"{self.topic_prefix}.ai.enriched",

            # Agent topics
            "agent_queries": f"{self.topic_prefix}.agent.queries",
            "agent_responses": f"{self.topic_prefix}.agent.responses",

            # Multi-nation curriculum topics
            "curriculum_ireland": f"{self.topic_prefix}.curriculum.ireland",
            "curriculum_england": f"{self.topic_prefix}.curriculum.england",
            "curriculum_scotland": f"{self.topic_prefix}.curriculum.scotland",
            "curriculum_wales": f"{self.topic_prefix}.curriculum.wales",
            "curriculum_ni": f"{self.topic_prefix}.curriculum.northern_ireland",

            # Bilingual alignment topics
            "alignment_pairs": f"{self.topic_prefix}.alignment.pairs",
            "alignment_quality": f"{self.topic_prefix}.alignment.quality",

            # Celtic language topics
            "celtic_folklore": f"{self.celtic_prefix}.folklore",
            "celtic_pronunciation": f"{self.celtic_prefix}.pronunciation",
            "celtic_terminology": f"{self.celtic_prefix}.terminology",
            "celtic_translation": f"{self.celtic_prefix}.translation",

            # Geospatial topics
            "geospatial_boundaries": f"{self.topic_prefix}.geospatial.boundaries",
            "geospatial_locations": f"{self.topic_prefix}.geospatial.locations",

            # =================================================================
            # ML PIPELINE TOPICS - Data Collection & Training
            # =================================================================

            # Dúchas.ie - Irish Folklore Handwriting (740K pages)
            "duchas_pages": f"{self.topic_prefix}.duchas.pages",
            "duchas_images": f"{self.topic_prefix}.duchas.images",
            "duchas_transcriptions": f"{self.topic_prefix}.duchas.transcriptions",
            "duchas_metadata": f"{self.topic_prefix}.duchas.metadata",

            # SEC Exam Papers - Bilingual Educational Content
            "sec_papers": f"{self.topic_prefix}.sec.papers",
            "sec_marking_schemes": f"{self.topic_prefix}.sec.marking_schemes",
            "sec_specifications": f"{self.topic_prefix}.sec.specifications",
            "sec_extracted": f"{self.topic_prefix}.sec.extracted",

            # Canúint.ie - Irish Dialect Audio
            "canuint_audio": f"{self.celtic_prefix}.canuint.audio",
            "canuint_transcriptions": f"{self.celtic_prefix}.canuint.transcriptions",
            "canuint_segments": f"{self.celtic_prefix}.canuint.segments",

            # ML Training Events
            "ml_training_jobs": f"{self.topic_prefix}.ml.training_jobs",
            "ml_training_metrics": f"{self.topic_prefix}.ml.training_metrics",
            "ml_model_artifacts": f"{self.topic_prefix}.ml.model_artifacts",
        }

    def is_configured(self) -> bool:
        """Check if Kafka is properly configured for active environment."""
        if self.environment == KafkaEnvironment.PRODUCTION:
            return bool(self.selfhosted.bootstrap_servers)
        return bool(self.confluent.api_key and self.confluent.api_secret)

    def get_environment_info(self) -> dict[str, str]:
        """Get information about current Kafka environment."""
        return {
            "environment": self.environment.value,
            "bootstrap_servers": self.cluster.bootstrap_servers
            if isinstance(self.cluster, SelfHostedKafkaConfig)
            else self.confluent.bootstrap_servers,
            "configured": str(self.is_configured()),
        }


# Singleton instance
_config: KafkaConfig | None = None


def get_kafka_config() -> KafkaConfig:
    """Get the Kafka configuration singleton."""
    global _config
    if _config is None:
        _config = KafkaConfig()
    return _config
