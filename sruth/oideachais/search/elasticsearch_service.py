"""
Elasticsearch Service.

Client for keyword search with Irish language support.
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ElasticsearchService:
    """
    Elasticsearch client for keyword search.

    Features:
    - Irish language analyzer support
    - Curriculum-specific field mappings
    - Highlight extraction
    - Filter integration
    """

    INDEX_SETTINGS = {
        "settings": {
            "analysis": {
                "analyzer": {
                    "irish_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "irish_stop",
                            "irish_stemmer",
                        ],
                    },
                    "english_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "english_stop",
                            "english_stemmer",
                        ],
                    },
                },
                "filter": {
                    "irish_stop": {
                        "type": "stop",
                        "stopwords": [
                            "an", "na", "le", "ar", "ag", "i", "do", "de",
                            "go", "sa", "is", "a", "ní", "sé", "sí", "iad",
                            "mé", "tú", "sinn", "sibh", "atá", "bhí",
                        ],
                    },
                    "irish_stemmer": {
                        "type": "stemmer",
                        "name": "irish",
                    },
                    "english_stop": {
                        "type": "stop",
                        "stopwords": "_english_",
                    },
                    "english_stemmer": {
                        "type": "stemmer",
                        "name": "english",
                    },
                },
            },
        },
        "mappings": {
            "properties": {
                "doc_id": {"type": "keyword"},
                "title": {
                    "type": "text",
                    "analyzer": "english_analyzer",
                    "fields": {
                        "irish": {"type": "text", "analyzer": "irish_analyzer"},
                        "keyword": {"type": "keyword"},
                    },
                },
                "content": {
                    "type": "text",
                    "analyzer": "english_analyzer",
                    "fields": {
                        "irish": {"type": "text", "analyzer": "irish_analyzer"},
                    },
                },
                "subject": {"type": "keyword"},
                "level": {"type": "keyword"},
                "source_type": {"type": "keyword"},
                "strand": {"type": "keyword"},
                "learning_outcome_codes": {"type": "keyword"},
                "year": {"type": "integer"},
                "created_at": {"type": "date"},
            },
        },
    }

    def __init__(
        self,
        hosts: list[str] | None = None,
        index_name: str = "curriculum",
        api_key: str | None = None,
    ):
        """
        Initialize Elasticsearch service.

        Args:
            hosts: Elasticsearch hosts
            index_name: Index name
            api_key: Optional API key for authentication
        """
        self.hosts = hosts or ["http://localhost:9200"]
        self.index_name = index_name
        self.api_key = api_key
        self._client = None

    async def _get_client(self):
        """Get or create async Elasticsearch client."""
        if self._client is None:
            try:
                from elasticsearch import AsyncElasticsearch

                self._client = AsyncElasticsearch(
                    hosts=self.hosts,
                    api_key=self.api_key,
                )
            except ImportError:
                logger.error("elasticsearch package not installed")
                return None
        return self._client

    async def create_index(self, recreate: bool = False) -> bool:
        """Create the curriculum index."""
        client = await self._get_client()
        if not client:
            return False

        try:
            if recreate:
                await client.indices.delete(index=self.index_name, ignore=[404])

            if not await client.indices.exists(index=self.index_name):
                await client.indices.create(
                    index=self.index_name,
                    body=self.INDEX_SETTINGS,
                )
                logger.info(f"Created index: {self.index_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to create index: {e}")
            return False

    async def index_document(
        self,
        doc_id: str,
        document: dict[str, Any],
    ) -> bool:
        """Index a single document."""
        client = await self._get_client()
        if not client:
            return False

        try:
            await client.index(
                index=self.index_name,
                id=doc_id,
                document=document,
            )
            return True
        except Exception as e:
            logger.error(f"Failed to index document {doc_id}: {e}")
            return False

    async def bulk_index(
        self,
        documents: list[dict[str, Any]],
    ) -> tuple[int, int]:
        """
        Bulk index documents.

        Returns:
            Tuple of (successful_count, failed_count)
        """
        client = await self._get_client()
        if not client:
            return 0, len(documents)

        try:
            from elasticsearch.helpers import async_bulk

            actions = [
                {
                    "_index": self.index_name,
                    "_id": doc.get("doc_id"),
                    "_source": doc,
                }
                for doc in documents
            ]

            success, failed = await async_bulk(
                client,
                actions,
                raise_on_error=False,
            )
            return success, len(failed) if isinstance(failed, list) else 0

        except Exception as e:
            logger.error(f"Bulk index failed: {e}")
            return 0, len(documents)

    async def search(
        self,
        query: str,
        size: int = 20,
        filters: Any = None,
    ) -> list[dict[str, Any]]:
        """
        Execute keyword search.

        Args:
            query: Search query
            size: Number of results
            filters: Optional SearchFilters

        Returns:
            List of search results
        """
        client = await self._get_client()
        if not client:
            return []

        try:
            # Build query
            must = [
                {
                    "multi_match": {
                        "query": query,
                        "fields": [
                            "title^3",
                            "title.irish^2",
                            "content",
                            "content.irish",
                            "learning_outcome_codes^2",
                        ],
                        "type": "best_fields",
                        "fuzziness": "AUTO",
                    }
                }
            ]

            # Add filters
            filter_clauses = []
            if filters:
                if hasattr(filters, "subject") and filters.subject:
                    filter_clauses.append({"term": {"subject": filters.subject}})
                if hasattr(filters, "level") and filters.level:
                    filter_clauses.append({"term": {"level": filters.level}})
                if hasattr(filters, "source_type") and filters.source_type:
                    filter_clauses.append({"term": {"source_type": filters.source_type}})
                if hasattr(filters, "year_from") and filters.year_from:
                    filter_clauses.append(
                        {"range": {"year": {"gte": filters.year_from}}}
                    )
                if hasattr(filters, "year_to") and filters.year_to:
                    filter_clauses.append(
                        {"range": {"year": {"lte": filters.year_to}}}
                    )

            body = {
                "query": {
                    "bool": {
                        "must": must,
                        "filter": filter_clauses,
                    }
                },
                "highlight": {
                    "fields": {
                        "content": {
                            "fragment_size": 150,
                            "number_of_fragments": 3,
                        },
                        "title": {},
                    },
                    "pre_tags": ["<em>"],
                    "post_tags": ["</em>"],
                },
                "size": size,
            }

            response = await client.search(index=self.index_name, body=body)

            results = []
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                highlights = []

                if "highlight" in hit:
                    for field_highlights in hit["highlight"].values():
                        highlights.extend(field_highlights)

                results.append({
                    "id": hit["_id"],
                    "title": source.get("title", ""),
                    "content": source.get("content", ""),
                    "score": hit["_score"],
                    "subject": source.get("subject"),
                    "level": source.get("level"),
                    "source_type": source.get("source_type"),
                    "highlights": highlights,
                })

            return results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    async def delete_document(self, doc_id: str) -> bool:
        """Delete a document by ID."""
        client = await self._get_client()
        if not client:
            return False

        try:
            await client.delete(index=self.index_name, id=doc_id, ignore=[404])
            return True
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            return False

    async def close(self) -> None:
        """Close the client connection."""
        if self._client:
            await self._client.close()
            self._client = None
