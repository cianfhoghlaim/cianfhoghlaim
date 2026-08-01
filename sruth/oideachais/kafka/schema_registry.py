"""
Confluent Schema Registry integration for Celtic education pipeline.

Provides:
- Avro schema management for education data topics
- Schema evolution with compatibility checks
- Serialization/deserialization utilities
"""

import json
import logging
from dataclasses import dataclass
from typing import Any

from .config import get_kafka_config

logger = logging.getLogger(__name__)

# Lazy imports
_schema_registry_client = None
_avro_serializer = None
_avro_deserializer = None


def _get_schema_registry_client():
    """Lazy load Schema Registry client."""
    global _schema_registry_client
    if _schema_registry_client is None:
        try:
            from confluent_kafka.schema_registry import SchemaRegistryClient

            config = get_kafka_config()
            _schema_registry_client = SchemaRegistryClient(config.schema_registry.config)
        except ImportError:
            logger.warning("confluent-kafka[avro] not installed, Schema Registry disabled")
    return _schema_registry_client


# Avro schemas for education data
SCHEMAS = {
    "curriculum_page": {
        "type": "record",
        "name": "CurriculumPage",
        "namespace": "ie.cianfhoghlaim.oideachais",
        "fields": [
            {"name": "url", "type": "string"},
            {"name": "title", "type": ["null", "string"], "default": None},
            {"name": "markdown", "type": ["null", "string"], "default": None},
            {"name": "language", "type": "string", "default": "EN"},
            {"name": "education_level", "type": ["null", "string"], "default": None},
            {"name": "subject", "type": ["null", "string"], "default": None},
            {"name": "source", "type": "string"},
            {"name": "nation", "type": "string", "default": "ireland"},
            {"name": "crawled_at", "type": "long"},
            {"name": "status", "type": "string", "default": "success"},
        ],
    },
    "document_ingested": {
        "type": "record",
        "name": "DocumentIngested",
        "namespace": "ie.cianfhoghlaim.oideachais",
        "fields": [
            {"name": "document_id", "type": "string"},
            {"name": "file_path", "type": "string"},
            {"name": "document_type", "type": "string"},
            {"name": "education_level", "type": ["null", "string"], "default": None},
            {"name": "subject", "type": ["null", "string"], "default": None},
            {"name": "extracted_text", "type": ["null", "string"], "default": None},
            {"name": "nation", "type": "string", "default": "ireland"},
            {"name": "language", "type": "string", "default": "en"},
            {"name": "metadata", "type": "string", "default": "{}"},
            {"name": "ingested_at", "type": "long"},
        ],
    },
    "alignment_pair": {
        "type": "record",
        "name": "AlignmentPair",
        "namespace": "ie.cianfhoghlaim.oideachais",
        "fields": [
            {"name": "pair_id", "type": "string"},
            {"name": "source_text", "type": "string"},
            {"name": "target_text", "type": "string"},
            {"name": "source_lang", "type": "string"},
            {"name": "target_lang", "type": "string"},
            {"name": "alignment_score", "type": "double"},
            {"name": "alignment_method", "type": "string", "default": "hybrid"},
            {"name": "source_url", "type": ["null", "string"], "default": None},
            {"name": "metadata", "type": "string", "default": "{}"},
            {"name": "aligned_at", "type": "long"},
        ],
    },
    "embedding_generated": {
        "type": "record",
        "name": "EmbeddingGenerated",
        "namespace": "ie.cianfhoghlaim.oideachais",
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "document_id", "type": "string"},
            {"name": "chunk_index", "type": "int"},
            {"name": "text", "type": "string"},
            {"name": "embedding", "type": {"type": "array", "items": "float"}},
            {"name": "model", "type": "string"},
            {"name": "nation", "type": "string", "default": "ireland"},
            {"name": "language", "type": "string", "default": "en"},
            {"name": "created_at", "type": "long"},
        ],
    },
    "celtic_event": {
        "type": "record",
        "name": "CelticEvent",
        "namespace": "ie.cianfhoghlaim.oideachais",
        "fields": [
            {"name": "event_id", "type": "string"},
            {"name": "event_type", "type": "string"},
            {"name": "content", "type": "string"},  # JSON-encoded content
            {"name": "language", "type": "string"},
            {"name": "source", "type": "string"},
            {"name": "timestamp", "type": "long"},
        ],
    },
    "graph_cdc_event": {
        "type": "record",
        "name": "GraphCDCEvent",
        "namespace": "ie.cianfhoghlaim.oideachais",
        "fields": [
            {"name": "event_id", "type": "string"},
            {"name": "event_type", "type": "string"},
            {"name": "node_id", "type": "string"},
            {"name": "node_type", "type": "string"},
            {"name": "properties", "type": "string"},  # JSON-encoded
            {"name": "relationships", "type": "string"},  # JSON-encoded array
            {"name": "timestamp", "type": "long"},
        ],
    },
}


@dataclass
class SchemaInfo:
    """Schema registration information."""

    schema_id: int
    subject: str
    version: int
    schema_str: str


def register_schema(subject: str, schema_name: str) -> SchemaInfo | None:
    """
    Register an Avro schema with Schema Registry.

    Args:
        subject: Schema Registry subject (usually topic-value)
        schema_name: Name of schema from SCHEMAS dict

    Returns:
        SchemaInfo if successful, None otherwise
    """
    client = _get_schema_registry_client()
    if client is None:
        return None

    if schema_name not in SCHEMAS:
        logger.error(f"Unknown schema: {schema_name}")
        return None

    try:
        from confluent_kafka.schema_registry import Schema

        schema_str = json.dumps(SCHEMAS[schema_name])
        schema = Schema(schema_str, "AVRO")

        schema_id = client.register_schema(subject, schema)

        # Get version info
        versions = client.get_versions(subject)
        latest_version = max(versions) if versions else 1

        return SchemaInfo(
            schema_id=schema_id,
            subject=subject,
            version=latest_version,
            schema_str=schema_str,
        )

    except Exception as e:
        logger.error(f"Failed to register schema {schema_name}: {e}")
        return None


def get_schema(subject: str, version: str = "latest") -> dict[str, Any] | None:
    """
    Get a schema from Schema Registry.

    Args:
        subject: Schema Registry subject
        version: Schema version (default: latest)

    Returns:
        Schema dict if found, None otherwise
    """
    client = _get_schema_registry_client()
    if client is None:
        return None

    try:
        if version == "latest":
            registered = client.get_latest_version(subject)
        else:
            registered = client.get_version(subject, int(version))

        return json.loads(registered.schema.schema_str)

    except Exception as e:
        logger.error(f"Failed to get schema for {subject}: {e}")
        return None


def get_avro_serializer(schema_name: str):
    """
    Get an Avro serializer for a schema.

    Args:
        schema_name: Name of schema from SCHEMAS dict

    Returns:
        AvroSerializer if available, None otherwise
    """
    client = _get_schema_registry_client()
    if client is None:
        return None

    if schema_name not in SCHEMAS:
        logger.error(f"Unknown schema: {schema_name}")
        return None

    try:
        from confluent_kafka.schema_registry.avro import AvroSerializer

        schema_str = json.dumps(SCHEMAS[schema_name])
        return AvroSerializer(client, schema_str)

    except ImportError:
        logger.warning("confluent-kafka[avro] not installed")
        return None
    except Exception as e:
        logger.error(f"Failed to create serializer for {schema_name}: {e}")
        return None


def get_avro_deserializer(schema_name: str):
    """
    Get an Avro deserializer for a schema.

    Args:
        schema_name: Name of schema from SCHEMAS dict

    Returns:
        AvroDeserializer if available, None otherwise
    """
    client = _get_schema_registry_client()
    if client is None:
        return None

    if schema_name not in SCHEMAS:
        logger.error(f"Unknown schema: {schema_name}")
        return None

    try:
        from confluent_kafka.schema_registry.avro import AvroDeserializer

        schema_str = json.dumps(SCHEMAS[schema_name])
        return AvroDeserializer(client, schema_str)

    except ImportError:
        logger.warning("confluent-kafka[avro] not installed")
        return None
    except Exception as e:
        logger.error(f"Failed to create deserializer for {schema_name}: {e}")
        return None


def register_all_schemas() -> dict[str, SchemaInfo | None]:
    """
    Register all education schemas with Schema Registry.

    Returns:
        Dict mapping schema names to SchemaInfo
    """
    config = get_kafka_config()
    results = {}

    schema_topic_mapping = {
        "curriculum_page": config.topics["curriculum_pages"],
        "document_ingested": config.topics["documents_ingested"],
        "alignment_pair": config.topics["alignment_pairs"],
        "embedding_generated": config.topics["embeddings_generated"],
        "celtic_event": config.topics["celtic_folklore"],
        "graph_cdc_event": config.topics["graph_cdc"],
    }

    for schema_name, topic in schema_topic_mapping.items():
        subject = f"{topic}-value"
        results[schema_name] = register_schema(subject, schema_name)
        if results[schema_name]:
            logger.info(f"Registered schema {schema_name} for subject {subject}")

    return results


def check_compatibility(subject: str, schema_name: str) -> bool:
    """
    Check if a schema is compatible with existing versions.

    Args:
        subject: Schema Registry subject
        schema_name: Name of schema from SCHEMAS dict

    Returns:
        True if compatible, False otherwise
    """
    client = _get_schema_registry_client()
    if client is None:
        return False

    if schema_name not in SCHEMAS:
        logger.error(f"Unknown schema: {schema_name}")
        return False

    try:
        from confluent_kafka.schema_registry import Schema

        schema_str = json.dumps(SCHEMAS[schema_name])
        schema = Schema(schema_str, "AVRO")

        return client.test_compatibility(subject, schema)

    except Exception as e:
        logger.error(f"Compatibility check failed for {schema_name}: {e}")
        return False
