"""
Embedding Models and Configuration.

Canonical model definitions for Cianfhoghlaim embedding workflows.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal


class ModelProvider(Enum):
    """Embedding model providers."""

    SENTENCE_TRANSFORMERS = "sentence_transformers"
    OPENAI = "openai"
    COHERE = "cohere"
    VOYAGE = "voyage"
    LOCAL = "local"


class EmbeddingModels:
    """Canonical embedding model names."""

    # Multilingual models (best for Celtic languages)
    BGE_M3 = "BAAI/bge-m3"  # 1024 dim, multilingual, sparse+dense+colbert
    E5_LARGE = "intfloat/multilingual-e5-large"  # 1024 dim, query/document prefix
    E5_BASE = "intfloat/multilingual-e5-base"  # 768 dim

    # English-only models (faster, better for English content)
    E5_ENGLISH = "intfloat/e5-large-v2"  # 1024 dim
    BGE_EN = "BAAI/bge-large-en-v1.5"  # 1024 dim

    # Code models
    CODE_BERT = "microsoft/codebert-base"  # 768 dim
    CODE_BERT_LARGE = "microsoft/codebert-large"  # 1024 dim
    GRAPHCODEBERT = "microsoft/graphcodebert-base"

    # Irish-specific models
    GA_BERT = "DCU-NLP/bert-base-irish-cased-v1"  # 768 dim
    UCCIX_LLAMA = "uccix/Llama2-13B-Instruct-uncensored"  # via API

    # OpenAI models (via API)
    OPENAI_ADA2 = "text-embedding-ada-002"
    OPENAI_ADA3 = "text-embedding-3-small"
    OPENAI_ADA3_LARGE = "text-embedding-3-large"

    # Voyage AI (good for code)
    voyage_code_2 = "voyage-code-2"
    voyage_large_2 = "voyage-large-2"

    @classmethod
    def for_language(cls, language: str) -> str:
        """Get best model for a specific language.

        Args:
            language: ISO language code (ga, cy, gd, gv, en)

        Returns:
            Model name
        """
        lang_models = {
            "ga": cls.GA_BERT,  # Irish (Gaeilge)
            "cy": cls.BGE_M3,  # Welsh (Cymraeg) - use multilingual
            "gd": cls.BGE_M3,  # Scottish Gaelic
            "gv": cls.BGE_M3,  # Manx
            "en": cls.BGE_EN,  # English
        }
        return lang_models.get(language, cls.BGE_M3)

    @classmethod
    def for_purpose(cls, purpose: str) -> str:
        """Get best model for a specific purpose.

        Args:
            purpose: One of: curriculum, code, mythology, general

        Returns:
            Model name
        """
        purpose_models = {
            "curriculum": cls.BGE_M3,  # Multilingual for Irish curriculum
            "code": cls.CODE_BERT,  # Code-specific
            "mythology": cls.BGE_M3,  # Multilingual for Celtic myths
            "general": cls.BGE_M3,  # Default
        }
        return purpose_models.get(purpose, cls.BGE_M3)


@dataclass
class EmbeddingConfig:
    """Configuration for embedding generation.

    CRITICAL: Per CLAUDE.md MODIFICATION_RULES:
    - batch_size minimum: 100 (100x performance difference)
    - For bulk inserts >50 rows: Drop HNSW index before, recreate after
    """

    model: str = EmbeddingModels.BGE_M3
    provider: ModelProvider = ModelProvider.SENTENCE_TRANSFORMERS
    batch_size: int = 100
    max_sequence_length: int = 512
    normalize: bool = True
    device: str = "cpu"  # cpu, cuda, mps
    show_progress: bool = False

    # HNSW index management
    index_type: Literal["IVF_PQ", "HNSW"] = "IVF_PQ"
    index_metric: str = "cosine"
    drop_index_before_bulk: bool = True
    bulk_threshold: int = 50

    # Chunking
    chunk_size: int = 512
    chunk_overlap: int = 50

    # Retry logic
    max_retries: int = 3
    retry_delay: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "model": self.model,
            "provider": self.provider.value,
            "batch_size": self.batch_size,
            "max_sequence_length": self.max_sequence_length,
            "normalize": self.normalize,
            "device": self.device,
            "index_type": self.index_type,
            "index_metric": self.index_metric,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
        }


@dataclass
class EmbeddingResult:
    """Result from embedding generation."""

    embeddings: list[list[float]] | list[list[float]]
    model: str
    dimension: int
    count: int
    duration_seconds: float = 0.0
    metadata: dict = field(default_factory=dict)

    def to_numpy(self):
        """Convert embeddings to numpy array."""
        import numpy as np

        return np.array(self.embeddings)


# Common configurations
IRISH_CURRICULUM_CONFIG = EmbeddingConfig(
    model=EmbeddingModels.BGE_M3,
    batch_size=100,
    normalize=True,
)

CODE_EMBEDDING_CONFIG = EmbeddingConfig(
    model=EmbeddingModels.CODE_BERT,
    batch_size=100,
    max_sequence_length=512,
)

MYTHOLOGY_CONFIG = EmbeddingConfig(
    model=EmbeddingModels.BGE_M3,
    batch_size=100,
    chunk_size=512,
)

GITHUB_ANALYTICS_CONFIG = EmbeddingConfig(
    model=EmbeddingModels.CODE_BERT,
    batch_size=100,
)

DEFI_DOCS_CONFIG = EmbeddingConfig(
    model=EmbeddingModels.BGE_M3,
    batch_size=100,
    chunk_size=512,
)
