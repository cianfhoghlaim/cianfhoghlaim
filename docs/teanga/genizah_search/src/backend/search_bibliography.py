import os
import time
import json
import logging
from typing import Any, Dict, List, Optional, Union

import numpy as np
from elasticsearch import Elasticsearch
from fastapi import HTTPException
from pydantic import BaseModel, Field, field_validator

from embedding_client import embedding_client


logger = logging.getLogger(__name__)


class BibliographySearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    num_results: int = Field(default=10, ge=1, le=50)
    page: int = Field(default=1, ge=1)
    include_embeddings: bool = Field(default=False)
    index_name: Optional[str] = Field(default=None)


class BibliographyHybridSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    semanticWeight: int = Field(default=60, ge=0, le=100)
    keywordWeight: int = Field(default=40, ge=0, le=100)
    num_results: int = Field(default=10, ge=1, le=50)
    page: int = Field(default=1, ge=1)
    include_embeddings: bool = Field(default=False)
    index_name: Optional[str] = Field(default=None)


class BibliographySearchResult(BaseModel):
    doc_id: str
    similarity_score: float
    distance: Optional[float] = None
    description: Optional[str] = None
    full_text: Optional[str] = None
    shelf_marks_mentioned: Optional[List[str]] = None
    author: Optional[str] = None
    authors: Optional[List[str]] = None
    title: Optional[str] = None
    extracted_page_number: Optional[int] = None
    subject_keywords: Optional[List[str]] = None
    metadata: Dict[str, Any] = {}
    embedding: Optional[List[float]] = None

    @field_validator('shelf_marks_mentioned', mode='before')
    @classmethod
    def convert_shelf_marks(cls, v: Union[Dict[str, Any], List[str], None]) -> Optional[List[str]]:
        """Convert shelf_marks_mentioned from dict to list if needed"""
        if v is None:
            return None
        if isinstance(v, list):
            return v
        if isinstance(v, dict):
            # If it's a dict, extract the keys (shelf mark IDs)
            return list(v.keys())
        # Fallback: convert to string and wrap in list
        return [str(v)]

    @field_validator('authors', mode='before')
    @classmethod
    def convert_authors(cls, v: Union[str, List[str], None]) -> Optional[List[str]]:
        """Convert authors from string to list if needed"""
        if v is None:
            return None
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            return [v]
        return None


class BibliographySearchResponse(BaseModel):
    results: List[BibliographySearchResult]
    query: Optional[str] = None
    count: int
    processing_time_ms: float
    total: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None
    total_pages: Optional[int] = None
    has_more: Optional[bool] = None
    index_name: Optional[str] = None


class ElasticsearchBibliographyService:
    """Semantic search service for the Genizah bibliography index."""

    def __init__(self):
        self.es_host = os.getenv("ELASTICSEARCH_HOST", "elastic.cairogenizah.ai")
        self.es_port = os.getenv("ELASTICSEARCH_PORT", "443")
        # Default to bibliography index; can be overridden per-request
        self.index_name = os.getenv("ELASTICSEARCH_BIBLIOGRAPHY_INDEX", "genizah_bibliography_v0.0.1")
        self.es: Optional[Elasticsearch] = None
        self._initialize_elasticsearch()

    def _initialize_elasticsearch(self) -> None:
        # Add retries/timeouts to be resilient to intermittent gateway issues
        self.es = Elasticsearch(
            [f"https://{self.es_host}:{self.es_port}"],
            basic_auth=(os.getenv("ELASTICSEARCH_USER", "cairo_user"), os.getenv("ELASTICSEARCH_PASSWORD")),
            verify_certs=False,
            retry_on_status=[429, 502, 503, 504],
            max_retries=3,
            retry_on_timeout=True,
            request_timeout=30,
        )

    def _extract_core_fields(self, source: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "description": source.get("description"),
            "full_text": source.get("full_text_content"),
            "shelf_marks_mentioned": source.get("shelf_marks_mentioned"),
            "author": source.get("author"),
            "authors": source.get("authors"),
            "title": source.get("title"),
            "extracted_page_number": source.get("extracted_page_number"),
            "subject_keywords": source.get("subject_keywords"),
        }

    async def search(self, request: BibliographySearchRequest) -> BibliographySearchResponse:
        """Semantic vector search over the bibliography index using cosineSimilarity on 'embedding_vector'."""
        start_time = time.time()

        try:
            # Compute query embedding
            query_embedding = await embedding_client.get_embedding(request.query, image=None, use_cache=False)

            # Base query (no filters for now)
            base_query: Dict[str, Any] = {"match_all": {}}

            # Vector similarity via script_score
            es_query = {
                "script_score": {
                    "query": base_query,
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding_vector') + 1.0",
                        "params": {"query_vector": query_embedding.flatten().tolist()},
                    },
                }
            }

            # Pagination
            page_number = request.page or 1
            page_size = request.num_results or 10
            from_offset = (page_number - 1) * page_size

            search_index = request.index_name or self.index_name

            response = self.es.search(
                index=search_index,
                query=es_query,
                size=page_size,
                from_=from_offset,
                _source=True,
            )

            results: List[BibliographySearchResult] = []
            for hit in response.get("hits", {}).get("hits", []):
                source = hit.get("_source", {})
                core = self._extract_core_fields(source)

                embedding: Optional[List[float]] = None
                if request.include_embeddings:
                    embedding = source.get("embedding_vector", [])

                doc_id = source.get("doc_id") or hit.get("_id")

                results.append(
                    BibliographySearchResult(
                        doc_id=doc_id,
                        similarity_score=round(hit.get("_score", 0.0) - 1.0, 4),
                        distance=round(2.0 - hit.get("_score", 0.0), 4),
                        description=core.get("description"),
                        full_text=core.get("full_text"),
                        shelf_marks_mentioned=core.get("shelf_marks_mentioned"),
                        author=core.get("author"),
                        authors=core.get("authors"),
                        title=core.get("title"),
                        extracted_page_number=core.get("extracted_page_number"),
                        subject_keywords=core.get("subject_keywords"),
                        metadata={k: v for k, v in source.items() if k not in {"embedding_vector"}},
                        embedding=embedding,
                    )
                )

            processing_time = (time.time() - start_time) * 1000

            # Total hits for pagination
            total_hits_value = 0
            try:
                total_info = response.get("hits", {}).get("total")
                if isinstance(total_info, dict):
                    total_hits_value = int(total_info.get("value", 0))
                elif isinstance(total_info, int):
                    total_hits_value = int(total_info)
            except Exception:
                total_hits_value = 0

            total_pages = max(1, int(np.ceil(total_hits_value / page_size))) if page_size else 1
            has_more = (page_number * page_size) < total_hits_value

            return BibliographySearchResponse(
                results=results,
                query=request.query,
                count=len(results),
                processing_time_ms=round(processing_time, 2),
                total=total_hits_value,
                page=page_number,
                page_size=page_size,
                total_pages=total_pages,
                has_more=has_more,
                index_name=search_index,
            )

        except Exception as e:
            # Log full details server-side but return a clean message to clients
            logger.error(f"Bibliography search failed: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            if hasattr(e, "status_code"):
                logger.error(f"ES status code: {e.status_code}")
            if hasattr(e, "info"):
                try:
                    logger.error(f"ES error info: {json.dumps(e.info, indent=2)}")
                except Exception:
                    logger.error("ES error info present but not JSON-serializable")
            if hasattr(e, "body"):
                logger.error("ES error body received (possibly HTML from gateway)")
            clean_message = "Elasticsearch gateway error (502/5xx). Please retry in a moment."
            raise HTTPException(status_code=502 if getattr(e, "status_code", 500) in [502, 503, 504] else 500,
                                detail=clean_message)

    async def search_hybrid(self, request: BibliographyHybridSearchRequest) -> BibliographySearchResponse:
        """Hybrid search combining semantic vector similarity and keyword search (default 60/40)."""
        if request.semanticWeight + request.keywordWeight != 100:
            raise HTTPException(status_code=400, detail="Semantic and keyword weights must sum to 100")

        start_time = time.time()

        try:
            # Compute query embedding for semantic portion
            query_embedding = await embedding_client.get_embedding(request.query, image=None, use_cache=False)

            # Base query
            base_query: Dict[str, Any] = {"match_all": {}}

            # Fields for keyword search in bibliography index
            keyword_fields: List[str] = [
                "full_text^2.5",
                "description^2.0",
                "shelf_marks_mentioned^1.0",
            ]

            # Hybrid function_score combining semantic script_score and keyword multi_match
            hybrid_query: Dict[str, Any] = {
                "function_score": {
                    "query": base_query,
                    "functions": [
                        {
                            "filter": {"match_all": {}},
                            "weight": request.semanticWeight / 100.0,
                            "script_score": {
                                "script": {
                                    "source": "cosineSimilarity(params.query_vector, 'embedding_vector') + 1.0",
                                    "params": {"query_vector": query_embedding.flatten().tolist()},
                                }
                            },
                        },
                        {
                            "filter": {
                                "multi_match": {
                                    "query": request.query,
                                    "fields": keyword_fields,
                                    "type": "best_fields",
                                    "fuzziness": "AUTO",
                                }
                            },
                            "weight": request.keywordWeight / 100.0,
                        },
                    ],
                    "score_mode": "sum",
                    "boost_mode": "multiply",
                }
            }

            # Pagination
            page_number = request.page or 1
            page_size = request.num_results or 10
            from_offset = (page_number - 1) * page_size

            search_index = request.index_name or self.index_name

            response = self.es.search(
                index=search_index,
                query=hybrid_query,
                size=page_size,
                from_=from_offset,
                _source=True,
            )

            results: List[BibliographySearchResult] = []
            for hit in response.get("hits", {}).get("hits", []):
                source = hit.get("_source", {})
                core = self._extract_core_fields(source)

                embedding: Optional[List[float]] = None
                if request.include_embeddings:
                    embedding = source.get("embedding_vector", [])

                doc_id = source.get("doc_id") or hit.get("_id")

                results.append(
                    BibliographySearchResult(
                        doc_id=doc_id,
                        similarity_score=round(hit.get("_score", 0.0), 4),
                        distance=round(max(0.0, 10.0 - hit.get("_score", 0.0)), 4),
                        description=core.get("description"),
                        full_text=core.get("full_text"),
                        shelf_marks_mentioned=core.get("shelf_marks_mentioned"),
                        author=core.get("author"),
                        authors=core.get("authors"),
                        title=core.get("title"),
                        extracted_page_number=core.get("extracted_page_number"),
                        subject_keywords=core.get("subject_keywords"),
                        metadata={k: v for k, v in source.items() if k not in {"embedding_vector"}},
                        embedding=embedding,
                    )
                )

            processing_time = (time.time() - start_time) * 1000

            total_hits_value = 0
            try:
                total_info = response.get("hits", {}).get("total")
                if isinstance(total_info, dict):
                    total_hits_value = int(total_info.get("value", 0))
                elif isinstance(total_info, int):
                    total_hits_value = int(total_info)
            except Exception:
                total_hits_value = 0

            total_pages = max(1, int(np.ceil(total_hits_value / page_size))) if page_size else 1
            has_more = (page_number * page_size) < total_hits_value

            return BibliographySearchResponse(
                results=results,
                query=f"Hybrid: {request.query} (Semantic: {request.semanticWeight}%, Keyword: {request.keywordWeight}%)",
                count=len(results),
                processing_time_ms=round(processing_time, 2),
                total=total_hits_value,
                page=page_number,
                page_size=page_size,
                total_pages=total_pages,
                has_more=has_more,
                index_name=search_index,
            )

        except Exception as e:
            logger.error(f"Bibliography hybrid search failed: {e}")
            if hasattr(e, "info"):
                try:
                    logger.error(f"ES error info: {json.dumps(e.info, indent=2)}")
                except Exception:
                    logger.error("ES error info present but not JSON-serializable")
            if hasattr(e, "body"):
                logger.error("ES error body received (possibly HTML from gateway)")
            clean_message = "Elasticsearch gateway error (502/5xx). Please retry in a moment."
            raise HTTPException(status_code=502 if getattr(e, "status_code", 500) in [502, 503, 504] else 500,
                                detail=clean_message)


# Global instance
bibliography_search_service = ElasticsearchBibliographyService()


