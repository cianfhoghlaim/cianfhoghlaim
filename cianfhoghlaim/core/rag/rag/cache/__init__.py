"""
Multi-Level Caching System.

Based on LightRAG caching patterns with curriculum-specific extensions.
"""
from __future__ import annotations

from .cache_manager import CurriculumCacheManager
from .embedding_cache import EmbeddingCache
from .llm_cache import LLMCache
from .query_cache import QueryCache

__all__ = [
    "CurriculumCacheManager",
    "EmbeddingCache",
    "LLMCache",
    "QueryCache",
]
