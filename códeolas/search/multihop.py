"""
Multi-hop semantic search for códeolas.

Based on ChunkHound pattern for deep research with convergence detection.
Iteratively searches and refines queries until information convergence.
"""

import logging
from typing import TYPE_CHECKING, Any

from sruth.códeolas.core.types import SearchResult

if TYPE_CHECKING:
    from sruth.códeolas.core.analyzer import CodebaseAnalyzer

logger = logging.getLogger(__name__)


async def multihop_search(
    analyzer: "CodebaseAnalyzer",
    question: str,
    max_sources: int = 15,
    max_iterations: int = 5,
    convergence_threshold: float = 0.85,
    initial_limit: int = 10,
) -> dict[str, Any]:
    """
    Multi-hop semantic search for complex questions.

    Iteratively searches and refines until convergence or max iterations.
    Each iteration:
    1. Search with current query
    2. Extract new concepts from results
    3. Check if new results overlap significantly with existing (convergence)
    4. Refine query based on gaps

    Args:
        analyzer: CodebaseAnalyzer instance
        question: Research question
        max_sources: Maximum sources to include in final result
        max_iterations: Maximum search iterations
        convergence_threshold: Overlap threshold to consider converged (0-1)
        initial_limit: Number of results per search

    Returns:
        Dict with:
        - sources: List of SearchResult objects
        - iterations: Number of iterations performed
        - converged: Whether search converged
        - synthesis: Summary of findings
    """
    all_sources: dict[str, SearchResult] = {}  # file_path:line -> result
    queries_used: list[str] = [question]
    iteration = 0
    converged = False

    while iteration < max_iterations and not converged:
        iteration += 1
        current_query = queries_used[-1]

        logger.info(f"Multi-hop iteration {iteration}: '{current_query[:50]}...'")

        # Search with current query
        results = await analyzer.search(
            query=current_query,
            limit=initial_limit,
            rerank=True,
        )

        if not results:
            logger.info(f"No results for iteration {iteration}")
            break

        # Track new vs existing sources
        new_count = 0
        for result in results:
            key = f"{result.chunk.file_path}:{result.chunk.start_line}"
            if key not in all_sources:
                all_sources[key] = result
                new_count += 1

        # Check convergence (high overlap with existing results)
        overlap_ratio = 1.0 - (new_count / len(results)) if results else 1.0
        logger.info(f"Iteration {iteration}: {new_count} new sources, overlap={overlap_ratio:.2f}")

        if overlap_ratio >= convergence_threshold:
            converged = True
            logger.info(f"Converged after {iteration} iterations")
            break

        # Stop if we have enough sources
        if len(all_sources) >= max_sources:
            logger.info(f"Reached max sources ({max_sources})")
            break

        # Generate refined query for next iteration
        refined_query = _refine_query(
            original_question=question,
            current_results=results,
            all_sources=list(all_sources.values()),
        )

        if refined_query and refined_query not in queries_used:
            queries_used.append(refined_query)
        else:
            # No new query to try, consider converged
            converged = True

    # Prepare final results
    final_sources = list(all_sources.values())

    # Sort by score and limit
    final_sources.sort(key=lambda x: x.rerank_score or x.score, reverse=True)
    final_sources = final_sources[:max_sources]

    # Generate synthesis
    synthesis = _synthesize_findings(question, final_sources)

    return {
        "sources": final_sources,
        "iterations": iteration,
        "converged": converged,
        "queries_used": queries_used,
        "synthesis": synthesis,
        "total_sources_found": len(all_sources),
    }


def _refine_query(
    original_question: str,
    current_results: list[SearchResult],
    all_sources: list[SearchResult],
) -> str | None:
    """
    Generate refined query based on current results.

    Looks for concepts in results that could expand the search.
    """
    if not current_results:
        return None

    # Extract key concepts from current results
    concepts: set[str] = set()
    for result in current_results[:5]:  # Look at top 5
        chunk = result.chunk

        # Use function/class names as concepts
        if chunk.name:
            concepts.add(chunk.name)

        # Extract potential concepts from parent
        if chunk.parent_name:
            concepts.add(chunk.parent_name)

    # Also check what concepts we already have
    existing_concepts: set[str] = set()
    for source in all_sources:
        if source.chunk.name:
            existing_concepts.add(source.chunk.name)

    # Find new concepts we haven't explored
    new_concepts = concepts - existing_concepts

    if not new_concepts:
        return None

    # Build refined query
    concept = list(new_concepts)[0]  # Take first new concept
    refined = f"{original_question} {concept}"

    return refined


def _synthesize_findings(
    question: str,
    sources: list[SearchResult],
) -> str:
    """
    Generate a synthesis of findings.

    This is a simple synthesis based on source metadata.
    For full synthesis, an LLM would be used.
    """
    if not sources:
        return "No relevant sources found."

    # Group by file
    files: dict[str, list[SearchResult]] = {}
    for source in sources:
        file_path = source.chunk.file_path
        if file_path not in files:
            files[file_path] = []
        files[file_path].append(source)

    # Build synthesis
    parts = [f"Found {len(sources)} relevant code sections across {len(files)} files:\n"]

    for file_path, file_sources in sorted(files.items()):
        parts.append(f"\n**{file_path}**")
        for source in file_sources[:3]:  # Max 3 per file
            chunk = source.chunk
            name = chunk.name or "code block"
            line = chunk.start_line
            chunk_type = chunk.chunk_type
            parts.append(f"  - {chunk_type} `{name}` (line {line})")

    return "\n".join(parts)


async def expand_semantic_neighborhood(
    analyzer: "CodebaseAnalyzer",
    seed_results: list[SearchResult],
    max_expansion: int = 5,
) -> list[SearchResult]:
    """
    Expand search to semantic neighborhood of seed results.

    Finds related code by searching for entities referenced in seed results.

    Args:
        analyzer: CodebaseAnalyzer instance
        seed_results: Initial search results
        max_expansion: Maximum additional results per seed

    Returns:
        Combined list of seed results and neighborhood results
    """
    all_results = list(seed_results)
    seen_keys: set[str] = {
        f"{r.chunk.file_path}:{r.chunk.start_line}" for r in seed_results
    }

    for seed in seed_results[:5]:  # Expand from top 5 seeds
        chunk = seed.chunk

        # Search for entities mentioned in the chunk
        entities_to_search = []

        if chunk.name:
            entities_to_search.append(chunk.name)
        if chunk.parent_name:
            entities_to_search.append(chunk.parent_name)

        for entity in entities_to_search[:2]:  # Max 2 entities per seed
            results = await analyzer.search(
                query=f"uses {entity}",
                limit=max_expansion,
                rerank=False,  # Skip reranking for speed
            )

            for result in results:
                key = f"{result.chunk.file_path}:{result.chunk.start_line}"
                if key not in seen_keys:
                    all_results.append(result)
                    seen_keys.add(key)

    return all_results
