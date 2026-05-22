"""
Confluent Kafka integration for oideachais Celtic education pipeline.

Provides:
- Kafka producers for streaming education data to Confluent Cloud
- Consumers with Gemini AI enrichment
- Schema Registry integration for Avro serialization
- Topic configurations for 25+ education and Celtic language topics

Topics:
- edu.curriculum.* - Curriculum content from all nations
- edu.documents.* - Document ingestion events
- edu.embeddings.* - Generated embeddings
- edu.agent.* - Agent query/response events
- edu.alignment.* - Bilingual alignment events
- celtic.* - Celtic language processing events
- eval.* - Evaluation and metrics events
"""

from .config import KafkaConfig, get_kafka_config
from .consumer import EducationConsumer, get_consumer
from .producer import EducationProducer, get_producer
from .topics import (
    AGENT_QUERIES,
    AGENT_RESPONSES,
    ALL_TOPICS,
    CELTIC_FOLKLORE,
    CELTIC_PRONUNCIATION,
    # Individual topics
    CURRICULUM_PAGES,
    EVALUATION_RAG,
    TopicCategory,
    TopicConfig,
    TopicDomain,
    get_all_topic_names,
    get_avro_schema,
    get_topic,
    get_topics_by_domain,
)

__all__ = [
    # Config
    "KafkaConfig",
    "get_kafka_config",
    # Producer/Consumer
    "EducationProducer",
    "get_producer",
    "EducationConsumer",
    "get_consumer",
    # Topics
    "TopicConfig",
    "TopicDomain",
    "TopicCategory",
    "ALL_TOPICS",
    "get_topic",
    "get_all_topic_names",
    "get_topics_by_domain",
    "get_avro_schema",
    # Common topics
    "CURRICULUM_PAGES",
    "AGENT_QUERIES",
    "AGENT_RESPONSES",
    "CELTIC_FOLKLORE",
    "CELTIC_PRONUNCIATION",
    "EVALUATION_RAG",
]
