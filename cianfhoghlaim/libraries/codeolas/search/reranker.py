"""
Reranking module for códeolas.

Based on LightRAG pattern for result reranking with multiple providers:
- Jina AI (jina-reranker-v2-base-multilingual)
- Cohere (rerank-v3.5)
- Aliyun DashScope (gte-rerank-v2)

Provides 15-20% precision improvement over vector search alone.
"""

import logging
import os
from typing import Any, Literal

import aiohttp
from sruth.codeolas.core.types import SearchResult
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)


def chunk_documents_for_rerank(
    documents: list[str],
    max_tokens: int = 480,
    overlap_tokens: int = 32,
) -> tuple[list[str], list[int]]:
    """
    Chunk documents that exceed token limit for reranking.

    Args:
        documents: List of document strings to chunk
        max_tokens: Maximum tokens per chunk (default 480)
        overlap_tokens: Number of tokens to overlap between chunks

    Returns:
        Tuple of (chunked_documents, original_doc_indices)
    """
    # Clamp overlap_tokens to prevent infinite loops
    if overlap_tokens >= max_tokens:
        overlap_tokens = max(0, max_tokens - 1)
        logger.warning(f"overlap_tokens clamped to {overlap_tokens}")

    # Character-based approximation (1 token ~= 4 chars)
    max_chars = max_tokens * 4
    overlap_chars = overlap_tokens * 4

    chunked_docs = []
    doc_indices = []

    for idx, doc in enumerate(documents):
        if len(doc) <= max_chars:
            chunked_docs.append(doc)
            doc_indices.append(idx)
        else:
            # Split into overlapping chunks
            start = 0
            while start < len(doc):
                end = min(start + max_chars, len(doc))
                chunk = doc[start:end]
                chunked_docs.append(chunk)
                doc_indices.append(idx)

                if end >= len(doc):
                    break
                start = end - overlap_chars

    return chunked_docs, doc_indices


def aggregate_chunk_scores(
    chunk_results: list[dict[str, Any]],
    doc_indices: list[int],
    num_original_docs: int,
    aggregation: Literal["max", "mean", "first"] = "max",
) -> list[dict[str, Any]]:
    """
    Aggregate rerank scores from chunks back to original documents.

    Args:
        chunk_results: Rerank results for chunks
        doc_indices: Maps each chunk to original document index
        num_original_docs: Total number of original documents
        aggregation: Score aggregation strategy

    Returns:
        List of results for original documents
    """
    # Group scores by document
    doc_scores: dict[int, list[float]] = {i: [] for i in range(num_original_docs)}

    for result in chunk_results:
        chunk_idx = result["index"]
        score = result["relevance_score"]

        if 0 <= chunk_idx < len(doc_indices):
            original_doc_idx = doc_indices[chunk_idx]
            doc_scores[original_doc_idx].append(score)

    # Aggregate scores
    aggregated = []
    for doc_idx, scores in doc_scores.items():
        if not scores:
            continue

        if aggregation == "max":
            final_score = max(scores)
        elif aggregation == "mean":
            final_score = sum(scores) / len(scores)
        elif aggregation == "first":
            final_score = scores[0]
        else:
            final_score = max(scores)

        aggregated.append(
            {
                "index": doc_idx,
                "relevance_score": final_score,
            }
        )

    # Sort by relevance score
    aggregated.sort(key=lambda x: x["relevance_score"], reverse=True)
    return aggregated


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    retry=(
        retry_if_exception_type(aiohttp.ClientError)
        | retry_if_exception_type(aiohttp.ClientResponseError)
    ),
)
async def _generic_rerank_api(
    query: str,
    documents: list[str],
    model: str,
    base_url: str,
    api_key: str | None,
    top_n: int | None = None,
    response_format: Literal["standard", "aliyun"] = "standard",
    request_format: Literal["standard", "aliyun"] = "standard",
    enable_chunking: bool = False,
    max_tokens_per_doc: int = 480,
) -> list[dict[str, Any]]:
    """Generic rerank API call for Jina/Cohere/Aliyun."""
    if not base_url:
        raise ValueError("Base URL is required")

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    # Handle document chunking
    original_documents = documents
    doc_indices = None
    original_top_n = top_n

    if enable_chunking:
        documents, doc_indices = chunk_documents_for_rerank(
            documents, max_tokens=max_tokens_per_doc
        )
        logger.debug(
            f"Chunked {len(original_documents)} docs into {len(documents)} chunks"
        )
        if top_n is not None:
            top_n = None  # Get all chunk scores for aggregation

    # Build request payload
    if request_format == "aliyun":
        payload = {
            "model": model,
            "input": {
                "query": query,
                "documents": documents,
            },
            "parameters": {},
        }
        if top_n is not None:
            payload["parameters"]["top_n"] = top_n
    else:
        payload = {
            "model": model,
            "query": query,
            "documents": documents,
        }
        if top_n is not None:
            payload["top_n"] = top_n

    async with aiohttp.ClientSession() as session:
        async with session.post(base_url, headers=headers, json=payload) as response:
            if response.status != 200:
                error_text = await response.text()
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message=f"Rerank API error: {error_text[:200]}",
                )

            response_json = await response.json()

            # Parse response based on format
            if response_format == "aliyun":
                results = response_json.get("output", {}).get("results", [])
            else:
                results = response_json.get("results", [])

            if not results:
                return []

            # Standardize results
            standardized = [
                {"index": r["index"], "relevance_score": r["relevance_score"]}
                for r in results
            ]

            # Aggregate chunk scores if chunking was enabled
            if enable_chunking and doc_indices:
                standardized = aggregate_chunk_scores(
                    standardized, doc_indices, len(original_documents)
                )
                if original_top_n and len(standardized) > original_top_n:
                    standardized = standardized[:original_top_n]

            return standardized


async def jina_rerank(
    query: str,
    documents: list[str],
    top_n: int | None = None,
    api_key: str | None = None,
    model: str = "jina-reranker-v2-base-multilingual",
) -> list[dict[str, Any]]:
    """
    Rerank documents using Jina AI API.

    Args:
        query: Search query
        documents: Documents to rerank
        top_n: Number of top results to return
        api_key: Jina API key (or JINA_API_KEY env var)
        model: Model name

    Returns:
        List of {"index": int, "relevance_score": float}
    """
    if api_key is None:
        api_key = os.getenv("JINA_API_KEY") or os.getenv("RERANK_API_KEY")

    return await _generic_rerank_api(
        query=query,
        documents=documents,
        model=model,
        base_url="https://api.jina.ai/v1/rerank",
        api_key=api_key,
        top_n=top_n,
        response_format="standard",
    )


async def cohere_rerank(
    query: str,
    documents: list[str],
    top_n: int | None = None,
    api_key: str | None = None,
    model: str = "rerank-v3.5",
    enable_chunking: bool = False,
    max_tokens_per_doc: int = 4096,
) -> list[dict[str, Any]]:
    """
    Rerank documents using Cohere API.

    Args:
        query: Search query
        documents: Documents to rerank
        top_n: Number of top results to return
        api_key: Cohere API key (or COHERE_API_KEY env var)
        model: Model name
        enable_chunking: Enable automatic chunking for long docs
        max_tokens_per_doc: Max tokens per doc for chunking

    Returns:
        List of {"index": int, "relevance_score": float}
    """
    if api_key is None:
        api_key = os.getenv("COHERE_API_KEY") or os.getenv("RERANK_API_KEY")

    return await _generic_rerank_api(
        query=query,
        documents=documents,
        model=model,
        base_url="https://api.cohere.com/v2/rerank",
        api_key=api_key,
        top_n=top_n,
        response_format="standard",
        enable_chunking=enable_chunking,
        max_tokens_per_doc=max_tokens_per_doc,
    )


async def ali_rerank(
    query: str,
    documents: list[str],
    top_n: int | None = None,
    api_key: str | None = None,
    model: str = "gte-rerank-v2",
) -> list[dict[str, Any]]:
    """
    Rerank documents using Aliyun DashScope API.

    Args:
        query: Search query
        documents: Documents to rerank
        top_n: Number of top results to return
        api_key: DashScope API key (or DASHSCOPE_API_KEY env var)
        model: Model name

    Returns:
        List of {"index": int, "relevance_score": float}
    """
    if api_key is None:
        api_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("RERANK_API_KEY")

    return await _generic_rerank_api(
        query=query,
        documents=documents,
        model=model,
        base_url="https://dashscope.aliyuncs.com/api/v1/services/rerank/text-rerank/text-rerank",
        api_key=api_key,
        top_n=top_n,
        response_format="aliyun",
        request_format="aliyun",
    )


async def rerank_results(
    query: str,
    results: list[SearchResult],
    provider: Literal["jina", "cohere", "aliyun"] = "jina",
    api_key: str | None = None,
    model: str | None = None,
    top_n: int | None = None,
) -> list[SearchResult]:
    """
    Rerank search results using external API.

    Args:
        query: Search query
        results: SearchResult objects to rerank
        provider: Reranking provider
        api_key: API key
        model: Model name
        top_n: Number of results to return

    Returns:
        Reranked list of SearchResult objects
    """
    if not results:
        return results

    # Extract documents
    documents = [r.chunk.text for r in results]

    # Call appropriate provider
    if provider == "jina":
        rerank_scores = await jina_rerank(
            query=query,
            documents=documents,
            top_n=top_n,
            api_key=api_key,
            model=model or "jina-reranker-v2-base-multilingual",
        )
    elif provider == "cohere":
        rerank_scores = await cohere_rerank(
            query=query,
            documents=documents,
            top_n=top_n,
            api_key=api_key,
            model=model or "rerank-v3.5",
        )
    elif provider == "aliyun":
        rerank_scores = await ali_rerank(
            query=query,
            documents=documents,
            top_n=top_n,
            api_key=api_key,
            model=model or "gte-rerank-v2",
        )
    else:
        raise ValueError(f"Unknown rerank provider: {provider}")

    # Reorder results based on scores
    reranked = []
    for score_item in rerank_scores:
        idx = score_item["index"]
        if 0 <= idx < len(results):
            result = results[idx]
            result.rerank_score = score_item["relevance_score"]
            reranked.append(result)

    return reranked
