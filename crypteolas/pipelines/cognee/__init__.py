"""Cognee Integration for Knowledge Graph Generation.

This package provides knowledge graph capabilities using Cognee with Memgraph:
- Entity and relationship extraction from documents
- Semantic knowledge graph construction
- Graph-based search and reasoning

Reference: dlt_cognee_memgraph.py example
"""

from cognee.processor import CogneeMemgraphProcessor
from cognee.entity_extraction import (
    DocumentSummary,
    Relationship,
    extract_entities_and_relationships,
)

__all__ = [
    "CogneeMemgraphProcessor",
    "DocumentSummary",
    "Relationship",
    "extract_entities_and_relationships",
]
