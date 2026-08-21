"""
Kafka topic definitions for Celtic Education Pipeline.

Provides:
- Topic constants for all education and Celtic language events
- Avro schema definitions for each topic
- Topic partitioning strategies
- Topic configuration (retention, compaction)

Topic Naming Convention:
    {domain}.{category}.{entity}

Domains:
    - edu: Education content and curriculum
    - celtic: Celtic language resources
    - eval: Evaluation and metrics

Categories:
    - curriculum: Curriculum content
    - documents: Document processing
    - agent: AI agent events
    - alignment: Bilingual alignment
    - geospatial: Geographic data
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class TopicDomain(str, Enum):
    """Topic domain prefixes."""

    EDU = "edu"
    CELTIC = "celtic"
    EVAL = "eval"


class TopicCategory(str, Enum):
    """Topic category names."""

    CURRICULUM = "curriculum"
    DOCUMENTS = "documents"
    EMBEDDINGS = "embeddings"
    AGENT = "agent"
    ALIGNMENT = "alignment"
    GEOSPATIAL = "geospatial"
    GRAPH = "graph"
    EVALUATION = "evaluation"


@dataclass(frozen=True)
class TopicConfig:
    """Configuration for a Kafka topic."""

    name: str
    description: str
    partitions: int = 6
    retention_ms: int = 604800000  # 7 days
    cleanup_policy: str = "delete"
    key_schema: str | None = None
    value_schema: str | None = None


# =============================================================================
# Education Content Topics
# =============================================================================

CURRICULUM_PAGES = TopicConfig(
    name="edu.curriculum.pages",
    description="Curriculum pages scraped from education portals (NCCA, SQA, etc.)",
    partitions=6,
    key_schema="string",  # URL as key
    value_schema="CurriculumPageValue",
)

EXAMINER_REPORTS = TopicConfig(
    name="edu.examiner.reports",
    description="SEC examiner reports and marking schemes",
    partitions=3,
    key_schema="string",  # Report ID
    value_schema="ExaminerReportValue",
)

DOCUMENTS_INGESTED = TopicConfig(
    name="edu.documents.ingested",
    description="Document ingestion events (PDFs, specs, guidelines)",
    partitions=6,
    key_schema="string",  # Document ID
    value_schema="DocumentIngestedValue",
)

AI_ENRICHED = TopicConfig(
    name="edu.ai.enriched",
    description="Documents enriched with AI extraction (learning outcomes, summaries)",
    partitions=6,
    key_schema="string",  # Document ID
    value_schema="AIEnrichedValue",
)

# =============================================================================
# Multi-Nation Curriculum Topics
# =============================================================================

CURRICULUM_IRELAND = TopicConfig(
    name="edu.curriculum.ireland",
    description="Irish curriculum (NCCA, curriculumonline.ie)",
    partitions=6,
    key_schema="string",  # Subject-Level key
)

CURRICULUM_SCOTLAND = TopicConfig(
    name="edu.curriculum.scotland",
    description="Scottish curriculum (Education Scotland, SQA)",
    partitions=6,
    key_schema="string",
)

CURRICULUM_WALES = TopicConfig(
    name="edu.curriculum.wales",
    description="Welsh curriculum (Curriculum for Wales)",
    partitions=6,
    key_schema="string",
)

CURRICULUM_ENGLAND = TopicConfig(
    name="edu.curriculum.england",
    description="English curriculum (National Curriculum, DfE)",
    partitions=6,
    key_schema="string",
)

CURRICULUM_NI = TopicConfig(
    name="edu.curriculum.northern_ireland",
    description="Northern Ireland curriculum (CCEA)",
    partitions=6,
    key_schema="string",
)

# =============================================================================
# Agent Topics
# =============================================================================

AGENT_QUERIES = TopicConfig(
    name="edu.agent.queries",
    description="User queries to Celtic education agents",
    partitions=12,  # Higher partitions for throughput
    retention_ms=86400000,  # 1 day
    key_schema="string",  # Session ID
    value_schema="AgentQueryValue",
)

AGENT_RESPONSES = TopicConfig(
    name="edu.agent.responses",
    description="Agent responses to user queries",
    partitions=12,
    retention_ms=86400000,
    key_schema="string",  # Session ID
    value_schema="AgentResponseValue",
)

AGENT_FEEDBACK = TopicConfig(
    name="edu.agent.feedback",
    description="User feedback on agent responses",
    partitions=3,
    key_schema="string",  # Response ID
    value_schema="AgentFeedbackValue",
)

# =============================================================================
# Celtic Language Topics
# =============================================================================

CELTIC_FOLKLORE = TopicConfig(
    name="celtic.folklore",
    description="Folklore and oral tradition (Duchas.ie School Collection)",
    partitions=6,
    key_schema="string",  # Story ID
    value_schema="FolkloreValue",
)

CELTIC_PRONUNCIATION = TopicConfig(
    name="celtic.pronunciation",
    description="Pronunciation data (Canuint.ie, Abair.ie)",
    partitions=6,
    key_schema="string",  # Word ID
    value_schema="PronunciationValue",
)

CELTIC_TERMINOLOGY = TopicConfig(
    name="celtic.terminology",
    description="Terminology and technical terms (Tearma.ie, Logainm.ie)",
    partitions=6,
    key_schema="string",  # Term ID
    value_schema="TerminologyValue",
)

CELTIC_TRANSLATION = TopicConfig(
    name="celtic.translation",
    description="Translation pairs between Celtic languages",
    partitions=6,
    key_schema="string",  # Source-Target pair
    value_schema="TranslationValue",
)

CELTIC_OCR = TopicConfig(
    name="celtic.ocr",
    description="OCR results for Irish handwritten texts",
    partitions=6,
    key_schema="string",  # Document ID
    value_schema="OCRValue",
)

# =============================================================================
# Bilingual Alignment Topics
# =============================================================================

ALIGNMENT_PAIRS = TopicConfig(
    name="edu.alignment.pairs",
    description="Bilingual sentence alignment pairs (en-ga, en-cy, etc.)",
    partitions=6,
    key_schema="string",  # Pair ID
    value_schema="AlignmentPairValue",
)

ALIGNMENT_QUALITY = TopicConfig(
    name="edu.alignment.quality",
    description="Alignment quality scores and feedback",
    partitions=3,
    key_schema="string",
    value_schema="AlignmentQualityValue",
)

# =============================================================================
# Embedding Topics
# =============================================================================

EMBEDDINGS_GENERATED = TopicConfig(
    name="edu.embeddings.generated",
    description="Generated embeddings for curriculum content",
    partitions=6,
    retention_ms=259200000,  # 3 days (embeddings can be regenerated)
    key_schema="string",  # Chunk ID
    value_schema="EmbeddingValue",
)

# =============================================================================
# Graph Topics
# =============================================================================

GRAPH_CDC = TopicConfig(
    name="edu.graph.cdc",
    description="Change data capture for knowledge graph updates",
    partitions=6,
    key_schema="string",  # Entity ID
    value_schema="GraphCDCValue",
)

# =============================================================================
# Geospatial Topics
# =============================================================================

GEOSPATIAL_BOUNDARIES = TopicConfig(
    name="edu.geospatial.boundaries",
    description="Statistical area boundaries (Irish Small Areas, UK LSOAs)",
    partitions=3,
    cleanup_policy="compact",  # Compacted for latest boundaries
    key_schema="string",  # Area code
    value_schema="BoundaryValue",
)

GEOSPATIAL_LOCATIONS = TopicConfig(
    name="edu.geospatial.locations",
    description="School and education facility locations",
    partitions=3,
    cleanup_policy="compact",
    key_schema="string",  # School code
    value_schema="LocationValue",
)

# =============================================================================
# Evaluation Topics
# =============================================================================

EVALUATION_RAG = TopicConfig(
    name="eval.rag.scores",
    description="RAG evaluation scores (faithfulness, relevancy, context precision)",
    partitions=3,
    key_schema="string",  # Query ID
    value_schema="RAGScoreValue",
)

EVALUATION_AGENT = TopicConfig(
    name="eval.agent.metrics",
    description="Agent performance metrics (latency, tokens, cost)",
    partitions=3,
    key_schema="string",  # Session ID
    value_schema="AgentMetricsValue",
)

# =============================================================================
# Topic Registry
# =============================================================================

ALL_TOPICS: dict[str, TopicConfig] = {
    # Education content
    "curriculum_pages": CURRICULUM_PAGES,
    "examiner_reports": EXAMINER_REPORTS,
    "documents_ingested": DOCUMENTS_INGESTED,
    "ai_enriched": AI_ENRICHED,
    # Multi-nation curriculum
    "curriculum_ireland": CURRICULUM_IRELAND,
    "curriculum_scotland": CURRICULUM_SCOTLAND,
    "curriculum_wales": CURRICULUM_WALES,
    "curriculum_england": CURRICULUM_ENGLAND,
    "curriculum_ni": CURRICULUM_NI,
    # Agent
    "agent_queries": AGENT_QUERIES,
    "agent_responses": AGENT_RESPONSES,
    "agent_feedback": AGENT_FEEDBACK,
    # Celtic language
    "celtic_folklore": CELTIC_FOLKLORE,
    "celtic_pronunciation": CELTIC_PRONUNCIATION,
    "celtic_terminology": CELTIC_TERMINOLOGY,
    "celtic_translation": CELTIC_TRANSLATION,
    "celtic_ocr": CELTIC_OCR,
    # Alignment
    "alignment_pairs": ALIGNMENT_PAIRS,
    "alignment_quality": ALIGNMENT_QUALITY,
    # Embeddings
    "embeddings_generated": EMBEDDINGS_GENERATED,
    # Graph
    "graph_cdc": GRAPH_CDC,
    # Geospatial
    "geospatial_boundaries": GEOSPATIAL_BOUNDARIES,
    "geospatial_locations": GEOSPATIAL_LOCATIONS,
    # Evaluation
    "evaluation_rag": EVALUATION_RAG,
    "evaluation_agent": EVALUATION_AGENT,
}


def get_topic(name: str) -> TopicConfig:
    """Get a topic configuration by name."""
    if name not in ALL_TOPICS:
        raise ValueError(f"Unknown topic: {name}. Available: {list(ALL_TOPICS.keys())}")
    return ALL_TOPICS[name]


def get_all_topic_names() -> list[str]:
    """Get all topic names."""
    return [topic.name for topic in ALL_TOPICS.values()]


def get_topics_by_domain(domain: TopicDomain) -> list[TopicConfig]:
    """Get all topics for a domain."""
    prefix = domain.value + "."
    return [t for t in ALL_TOPICS.values() if t.name.startswith(prefix)]


# =============================================================================
# Avro Schema Definitions
# =============================================================================

AVRO_SCHEMAS: dict[str, dict[str, Any]] = {
    "CurriculumPageValue": {
        "type": "record",
        "name": "CurriculumPageValue",
        "namespace": "ie.cianfhoghlaim.edu",
        "fields": [
            {"name": "url", "type": "string"},
            {"name": "title", "type": "string"},
            {"name": "content", "type": "string"},
            {"name": "nation", "type": "string"},
            {"name": "subject", "type": ["null", "string"], "default": None},
            {"name": "level", "type": ["null", "string"], "default": None},
            {"name": "language", "type": "string", "default": "en"},
            {"name": "scraped_at", "type": "long", "logicalType": "timestamp-millis"},
        ],
    },
    "AgentQueryValue": {
        "type": "record",
        "name": "AgentQueryValue",
        "namespace": "ie.cianfhoghlaim.edu",
        "fields": [
            {"name": "query_id", "type": "string"},
            {"name": "session_id", "type": "string"},
            {"name": "user_id", "type": ["null", "string"], "default": None},
            {"name": "query", "type": "string"},
            {"name": "agent_name", "type": "string"},
            {"name": "context", "type": ["null", "string"], "default": None},
            {"name": "language", "type": "string", "default": "en"},
            {"name": "timestamp", "type": "long", "logicalType": "timestamp-millis"},
        ],
    },
    "AgentResponseValue": {
        "type": "record",
        "name": "AgentResponseValue",
        "namespace": "ie.cianfhoghlaim.edu",
        "fields": [
            {"name": "response_id", "type": "string"},
            {"name": "query_id", "type": "string"},
            {"name": "session_id", "type": "string"},
            {"name": "response", "type": "string"},
            {"name": "agent_name", "type": "string"},
            {"name": "sources", "type": {"type": "array", "items": "string"}},
            {"name": "latency_ms", "type": "float"},
            {"name": "input_tokens", "type": "int"},
            {"name": "output_tokens", "type": "int"},
            {"name": "model", "type": "string"},
            {"name": "timestamp", "type": "long", "logicalType": "timestamp-millis"},
        ],
    },
    "RAGScoreValue": {
        "type": "record",
        "name": "RAGScoreValue",
        "namespace": "ie.cianfhoghlaim.eval",
        "fields": [
            {"name": "query_id", "type": "string"},
            {"name": "faithfulness", "type": ["null", "float"], "default": None},
            {"name": "answer_relevancy", "type": ["null", "float"], "default": None},
            {"name": "context_precision", "type": ["null", "float"], "default": None},
            {"name": "context_recall", "type": ["null", "float"], "default": None},
            {"name": "answer_correctness", "type": ["null", "float"], "default": None},
            {"name": "evaluator_model", "type": "string"},
            {"name": "timestamp", "type": "long", "logicalType": "timestamp-millis"},
        ],
    },
}


def get_avro_schema(schema_name: str) -> dict[str, Any]:
    """Get an Avro schema by name."""
    if schema_name not in AVRO_SCHEMAS:
        raise ValueError(f"Unknown schema: {schema_name}")
    return AVRO_SCHEMAS[schema_name]
