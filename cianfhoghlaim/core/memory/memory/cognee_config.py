"""
Cognee Configuration for Celtic Linguistics Knowledge Graph.

Provides configuration for:
- Graph database backends (Memgraph for static knowledge)
- Vector database (LanceDB for embeddings)
- LLM provider settings
- Celtic language specific settings

Based on research in:
- taighde_teanga/knowledge-graph-linguistics.md
- taighde_bonneagar/cognee-integration.md

Usage:
    from memory import CogneeConfig

    config = CogneeConfig.for_celtic_linguistics()
    await config.apply()
"""

import os
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any


class GraphProvider(StrEnum):
    """Supported graph database providers."""

    MEMGRAPH = "memgraph"
    NEO4J = "neo4j"
    KUZU = "kuzu"
    NETWORKX = "networkx"


class VectorProvider(StrEnum):
    """Supported vector database providers."""

    LANCEDB = "lancedb"
    QDRANT = "qdrant"
    FALKORDB = "falkordb"


class LLMProvider(StrEnum):
    """Supported LLM providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    LITELLM = "litellm"


class EmbeddingProvider(StrEnum):
    """Supported embedding providers."""

    OPENAI = "openai"
    SENTENCE_TRANSFORMERS = "sentence_transformers"
    OLLAMA = "ollama"


@dataclass
class GraphConfig:
    """Graph database configuration."""

    provider: GraphProvider = GraphProvider.MEMGRAPH
    url: str = "bolt://localhost:7687"
    username: str = "memgraph"
    password: str = ""

    # Static knowledge settings
    is_static: bool = True
    enable_acid: bool = True
    max_connections: int = 10

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "provider": self.provider.value,
            "url": self.url,
            "username": self.username,
            "password": self.password,
            "is_static": self.is_static,
            "enable_acid": self.enable_acid,
            "max_connections": self.max_connections,
        }


@dataclass
class VectorConfig:
    """Vector database configuration."""

    provider: VectorProvider = VectorProvider.LANCEDB
    url: str = "./lancedb_data"
    collection_name: str = "celtic_embeddings"

    # Embedding settings
    embedding_dim: int = 1024
    metric: str = "cosine"
    index_type: str = "IVF_PQ"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "provider": self.provider.value,
            "url": self.url,
            "collection_name": self.collection_name,
            "embedding_dim": self.embedding_dim,
            "metric": self.metric,
            "index_type": self.index_type,
        }


@dataclass
class LLMConfig:
    """LLM configuration."""

    provider: LLMProvider = LLMProvider.OPENAI
    model: str = "gpt-4o-mini"
    api_key: str = ""
    base_url: str | None = None
    temperature: float = 0.0

    # Irish language handling
    irish_system_prompt: str = (
        "You are an expert in Celtic linguistics, particularly Irish (Gaeilge). "
        "You understand historical Irish orthography, dialects (Connacht, Munster, Ulster), "
        "and special characters like Tironian et (⁊), punctum delens (ḃ, ċ, etc.), "
        "and síneadh fada (á, é, í, ó, ú)."
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "provider": self.provider.value,
            "model": self.model,
            "api_key": self.api_key,
            "base_url": self.base_url,
            "temperature": self.temperature,
            "irish_system_prompt": self.irish_system_prompt,
        }


@dataclass
class EmbeddingConfig:
    """Embedding configuration."""

    provider: EmbeddingProvider = EmbeddingProvider.OPENAI
    model: str = "text-embedding-3-large"
    api_key: str = ""
    dimensions: int = 1024

    # Batching
    batch_size: int = 100  # CLAUDE.md requirement
    max_retries: int = 3

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "provider": self.provider.value,
            "model": self.model,
            "api_key": self.api_key,
            "dimensions": self.dimensions,
            "batch_size": self.batch_size,
            "max_retries": self.max_retries,
        }


@dataclass
class CelticLanguageConfig:
    """Celtic language specific configuration."""

    # Supported languages
    languages: list[str] = field(
        default_factory=lambda: ["irish", "scottish_gaelic", "welsh", "manx"]
    )

    # Primary language
    primary_language: str = "irish"

    # Dialect handling
    irish_dialects: list[str] = field(
        default_factory=lambda: ["connacht", "munster", "ulster", "standard"]
    )

    # Historical orthography
    normalize_pre1948: bool = True
    preserve_seanchlo: bool = True

    # Special characters
    tironian_handling: str = "preserve"  # preserve, expand, or normalize
    fada_strict: bool = True  # Strict accent matching

    # Entity types for knowledge graph
    entity_types: list[str] = field(
        default_factory=lambda: [
            "word",
            "phrase",
            "cognate",
            "etymology",
            "dialect_variant",
            "manuscript",
            "transcription",
            "pronunciation",
            "grammar_rule",
            "place_name",
            "person_name",
        ]
    )

    # Relationship types
    relationship_types: list[str] = field(
        default_factory=lambda: [
            "is_cognate_of",
            "derives_from",
            "translates_to",
            "has_variant",
            "appears_in",
            "spoken_in",
            "follows_rule",
            "related_to",
            "same_meaning_as",
            "opposite_of",
        ]
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "languages": self.languages,
            "primary_language": self.primary_language,
            "irish_dialects": self.irish_dialects,
            "normalize_pre1948": self.normalize_pre1948,
            "preserve_seanchlo": self.preserve_seanchlo,
            "tironian_handling": self.tironian_handling,
            "fada_strict": self.fada_strict,
            "entity_types": self.entity_types,
            "relationship_types": self.relationship_types,
        }


@dataclass
class EducationConfig:
    """Education-specific configuration for curriculum awareness."""

    # Curriculum namespace
    curriculum_namespace: str = "celtic_education"

    # Supported languages for content
    supported_languages: list[str] = field(default_factory=lambda: ["en", "ga"])

    # Education levels
    education_levels: list[str] = field(
        default_factory=lambda: ["primary", "junior_cycle", "senior_cycle"]
    )

    # Curriculum nations
    curriculum_nations: list[str] = field(
        default_factory=lambda: ["ireland", "scotland", "wales", "england", "northern_ireland"]
    )

    # Default curriculum
    default_curriculum: str = "ireland"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "curriculum_namespace": self.curriculum_namespace,
            "supported_languages": self.supported_languages,
            "education_levels": self.education_levels,
            "curriculum_nations": self.curriculum_nations,
            "default_curriculum": self.default_curriculum,
        }


@dataclass
class CogneeConfig:
    """
    Complete Cognee configuration for Celtic Education Platform.

    Integrates:
    - Memgraph for knowledge graph (curriculum hierarchy, linguistic relationships)
    - LanceDB for vector search (semantic document retrieval)
    - Celtic language handling (dialects, orthography, special characters)
    - Education features (curriculum awareness, learning outcomes)
    """

    # Database configurations
    graph: GraphConfig = field(default_factory=GraphConfig)
    vector: VectorConfig = field(default_factory=VectorConfig)

    # AI configurations
    llm: LLMConfig = field(default_factory=LLMConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)

    # Domain configurations
    celtic: CelticLanguageConfig = field(default_factory=CelticLanguageConfig)
    education: EducationConfig = field(default_factory=EducationConfig)

    # Memory processing settings
    chunk_size: int = 1024
    chunk_overlap: int = 256
    enable_entity_extraction: bool = True
    enable_graph_enrichment: bool = True

    # Dataset settings
    default_dataset: str = "celtic_education"
    datasets: list[str] = field(
        default_factory=lambda: [
            "curriculum",
            "examiner_insights",
            "conversations",
            "episodes",
            "irish_vocabulary",
            "scottish_gaelic",
            "welsh",
            "manx",
            "manuscripts",
            "transcriptions",
            "cognates",
            "place_names",
        ]
    )

    # Storage paths
    data_dir: str = "./cognee_data"
    cache_dir: str = "./cognee_cache"

    @classmethod
    def for_celtic_linguistics(cls) -> "CogneeConfig":
        """
        Create configuration optimized for Celtic linguistics.
        """
        return cls(
            graph=GraphConfig(
                provider=GraphProvider.MEMGRAPH,
                is_static=True,
                enable_acid=True,
            ),
            vector=VectorConfig(
                provider=VectorProvider.LANCEDB,
                collection_name="celtic_embeddings",
                embedding_dim=1024,
            ),
            llm=LLMConfig(
                provider=LLMProvider.OPENAI,
                model="gpt-4o-mini",
                temperature=0.0,
            ),
            embedding=EmbeddingConfig(
                provider=EmbeddingProvider.OPENAI,
                model="text-embedding-3-large",
                batch_size=100,
            ),
            celtic=CelticLanguageConfig(
                primary_language="irish",
                normalize_pre1948=True,
                tironian_handling="preserve",
            ),
        )

    @classmethod
    def for_celtic_education(cls) -> "CogneeConfig":
        """Create configuration optimized for Celtic education platform."""
        return cls(
            graph=GraphConfig(
                provider=GraphProvider.MEMGRAPH,
                is_static=True,
                enable_acid=True,
            ),
            vector=VectorConfig(
                provider=VectorProvider.LANCEDB,
                collection_name="celtic_education_memory",
                embedding_dim=1024,
            ),
            llm=LLMConfig(
                provider=LLMProvider.OPENAI,
                model="gpt-4o-mini",
                temperature=0.0,
            ),
            embedding=EmbeddingConfig(
                provider=EmbeddingProvider.SENTENCE_TRANSFORMERS,
                model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                batch_size=100,
            ),
            celtic=CelticLanguageConfig(
                primary_language="irish",
                normalize_pre1948=True,
                tironian_handling="preserve",
            ),
            education=EducationConfig(
                curriculum_namespace="celtic_education",
                default_curriculum="ireland",
            ),
        )

    @classmethod
    def for_ocr_transcriptions(cls) -> "CogneeConfig":
        """
        Create configuration optimized for OCR transcription storage.
        """
        return cls(
            graph=GraphConfig(
                provider=GraphProvider.MEMGRAPH,
                is_static=True,
            ),
            vector=VectorConfig(
                provider=VectorProvider.LANCEDB,
                collection_name="ocr_transcriptions",
                embedding_dim=1024,
            ),
            celtic=CelticLanguageConfig(
                preserve_seanchlo=True,
                tironian_handling="preserve",
                fada_strict=True,
            ),
            datasets=[
                "duchas_transcriptions",
                "hidden_heritages",
                "isos_manuscripts",
                "ocr_corrections",
            ],
        )

    @classmethod
    def for_local_dev(cls) -> "CogneeConfig":
        """
        Create configuration for local development.
        """
        return cls(
            graph=GraphConfig(
                provider=GraphProvider.NETWORKX,  # In-memory for dev
            ),
            vector=VectorConfig(
                provider=VectorProvider.LANCEDB,
                url="./dev_lancedb",
            ),
            llm=LLMConfig(
                provider=LLMProvider.OLLAMA,
                model="llama3.2",
            ),
            embedding=EmbeddingConfig(
                provider=EmbeddingProvider.OLLAMA,
                model="nomic-embed-text",
                dimensions=768,
            ),
        )

    async def apply(self) -> None:
        """
        Apply configuration to Cognee.
        """
        try:
            import cognee
        except ImportError:
            raise ImportError("cognee package required: pip install cognee")

        # Graph configuration
        await cognee.config.set_graph_database_provider(self.graph.provider.value)
        await cognee.config.set_graph_database_url(self.graph.url)
        if self.graph.username:
            await cognee.config.set_graph_database_username(self.graph.username)
        if self.graph.password:
            await cognee.config.set_graph_database_password(self.graph.password)

        # Vector configuration
        await cognee.config.set_vector_database_provider(self.vector.provider.value)
        await cognee.config.set_vector_database_url(self.vector.url)

        # LLM configuration
        await cognee.config.set_llm_provider(self.llm.provider.value)
        await cognee.config.set_llm_model(self.llm.model)

        api_key = self.llm.api_key or os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        if api_key:
            await cognee.config.set_llm_api_key(api_key)

        # Embedding configuration
        await cognee.config.set_embedding_provider(self.embedding.provider.value)
        await cognee.config.set_embedding_model(self.embedding.model)

        emb_key = self.embedding.api_key or os.getenv("OPENAI_API_KEY")
        if emb_key:
            # Note: Cognee may share API key between LLM and embedding
            pass

        # Create data directories
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)

    def to_dict(self) -> dict[str, Any]:
        """Convert full config to dictionary."""
        return {
            "graph": self.graph.to_dict(),
            "vector": self.vector.to_dict(),
            "llm": self.llm.to_dict(),
            "embedding": self.embedding.to_dict(),
            "celtic": self.celtic.to_dict(),
            "education": self.education.to_dict(),
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "default_dataset": self.default_dataset,
            "datasets": self.datasets,
            "data_dir": self.data_dir,
            "cache_dir": self.cache_dir,
        }

    def save(self, path: str | Path) -> None:
        """Save configuration to YAML file."""
        import yaml

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False)

    @classmethod
    def load(cls, path: str | Path) -> "CogneeConfig":
        """Load configuration from YAML file."""
        import yaml

        with open(path) as f:
            data = yaml.safe_load(f)

        return cls(
            graph=GraphConfig(**data.get("graph", {})),
            vector=VectorConfig(**data.get("vector", {})),
            llm=LLMConfig(**data.get("llm", {})),
            embedding=EmbeddingConfig(**data.get("embedding", {})),
            celtic=CelticLanguageConfig(**data.get("celtic", {})),
            education=EducationConfig(**data.get("education", {})),
            default_dataset=data.get("default_dataset", "celtic_education"),
            datasets=data.get("datasets", []),
            data_dir=data.get("data_dir", "./cognee_data"),
            cache_dir=data.get("cache_dir", "./cognee_cache"),
        )


# ============================================================================
# Configuration Application
# ============================================================================


def configure_cognee(config: CogneeConfig) -> None:
    """
    Apply configuration to Cognee library (synchronous wrapper).
    """
    try:
        import cognee
        from cognee.infrastructure.databases.graph import get_graph_config
        from cognee.infrastructure.databases.relational import get_relational_config
        from cognee.infrastructure.databases.vector import get_vectordb_config

        # Configure graph database
        graph_config = get_graph_config()
        graph_config.graph_database_provider = config.graph.provider.value
        graph_config.graph_database_url = config.graph.url
        if config.graph.username:
            graph_config.graph_database_username = config.graph.username
        if config.graph.password:
            graph_config.graph_database_password = config.graph.password

        # Configure vector database
        vector_config = get_vectordb_config()
        vector_config.vector_db_provider = config.vector.provider.value
        vector_config.vector_db_url = config.vector.url

        # Configure LLM
        cognee.config.set_llm_config({
            "provider": config.llm.provider.value,
            "model": config.llm.model,
            "api_key": config.llm.api_key,
            "temperature": config.llm.temperature,
        })

        # Configure embeddings
        cognee.config.set_embedding_config({
            "provider": config.embedding.provider.value,
            "model": config.embedding.model,
        })

    except ImportError:
        pass


# ============================================================================
# Singleton Access
# ============================================================================

_cognee_config: CogneeConfig | None = None


def get_cognee_config() -> CogneeConfig:
    """Get the global Cognee configuration instance."""
    global _cognee_config
    if _cognee_config is None:
        _cognee_config = CogneeConfig.for_celtic_education()
    return _cognee_config


def init_cognee(config: CogneeConfig | None = None) -> CogneeConfig:
    """Initialize Cognee with configuration."""
    global _cognee_config
    _cognee_config = config or CogneeConfig.for_celtic_education()
    configure_cognee(_cognee_config)
    return _cognee_config
