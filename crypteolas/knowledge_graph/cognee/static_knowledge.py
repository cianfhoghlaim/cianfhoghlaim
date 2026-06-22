"""
Static Knowledge Graph using Cognee for Crypteolas.

Stores structured knowledge about:
- Protocol architectures
- Token economics
- Team relationships
- Audit findings
- Code patterns

Uses Memgraph as the graph database backend.
"""

import os
from typing import Any

import cognee


async def setup_cognee():
    """Configure Cognee with Memgraph backend."""
    # Configure LLM
    cognee.config.llm_api_key = os.environ.get("OPENAI_API_KEY")

    # Configure graph database (Memgraph)
    cognee.config.graph_database_provider = "memgraph"
    cognee.config.graph_database_url = os.environ.get(
        "MEMGRAPH_URI", "bolt://localhost:7687"
    )

    # Configure vector store
    cognee.config.vector_db_provider = "lancedb"
    cognee.config.vector_db_url = os.environ.get(
        "LANCEDB_URI", "./storage/lance/cognee"
    )


async def add_protocol_knowledge(
    protocol_name: str,
    documentation: str,
    protocol_type: str | None = None,
    chains: list[str] | None = None,
    tokens: list[str] | None = None,
) -> str:
    """
    Add protocol documentation to knowledge graph.

    Cognee will:
    - Extract entities (protocols, tokens, chains)
    - Identify relationships
    - Create searchable knowledge graph
    """
    await setup_cognee()

    # Create dataset
    dataset_name = f"protocol_{protocol_name.lower()}"

    # Add the documentation
    await cognee.add(
        data=documentation,
        dataset_name=dataset_name,
    )

    # Process and build knowledge graph
    await cognee.cognify(dataset_name=dataset_name)

    return dataset_name


async def add_audit_report(
    protocol_name: str,
    auditor: str,
    audit_content: str,
    findings: list[dict[str, Any]] | None = None,
) -> str:
    """
    Add audit report to knowledge graph.

    Extracts:
    - Vulnerability types
    - Severity levels
    - Affected components
    - Recommendations
    """
    await setup_cognee()

    dataset_name = f"audit_{protocol_name.lower()}_{auditor.lower()}"

    # Format audit for processing
    formatted_audit = f"""
    Protocol: {protocol_name}
    Auditor: {auditor}

    Audit Report:
    {audit_content}
    """

    if findings:
        formatted_audit += "\n\nFindings Summary:\n"
        for finding in findings:
            formatted_audit += f"""
            - {finding.get('title', 'Unknown')}
              Severity: {finding.get('severity', 'Unknown')}
              Status: {finding.get('status', 'Unknown')}
            """

    await cognee.add(data=formatted_audit, dataset_name=dataset_name)
    await cognee.cognify(dataset_name=dataset_name)

    return dataset_name


async def add_code_knowledge(
    repo_name: str,
    code_summary: str,
    architecture: str | None = None,
    dependencies: list[str] | None = None,
) -> str:
    """
    Add code repository knowledge.

    Extracts:
    - Architecture patterns
    - Key components
    - Dependencies
    - Integration points
    """
    await setup_cognee()

    dataset_name = f"code_{repo_name.lower().replace('/', '_')}"

    formatted_content = f"""
    Repository: {repo_name}

    Summary:
    {code_summary}
    """

    if architecture:
        formatted_content += f"\n\nArchitecture:\n{architecture}"

    if dependencies:
        formatted_content += f"\n\nDependencies: {', '.join(dependencies)}"

    await cognee.add(data=formatted_content, dataset_name=dataset_name)
    await cognee.cognify(dataset_name=dataset_name)

    return dataset_name


async def search_knowledge(
    query: str,
    dataset_name: str | None = None,
) -> list[dict[str, Any]]:
    """
    Search the knowledge graph.

    Uses hybrid search combining:
    - Vector similarity
    - Graph traversal
    - Keyword matching
    """
    await setup_cognee()

    results = await cognee.search(
        query_text=query,
        query_type="GRAPH_COMPLETION",  # Use graph-enhanced search
    )

    return [
        {
            "content": r.get("content") if isinstance(r, dict) else str(r),
            "score": r.get("score") if isinstance(r, dict) else None,
            "source": r.get("source") if isinstance(r, dict) else None,
        }
        for r in results
    ]


async def get_entity_relationships(
    entity_name: str,
    relationship_type: str | None = None,
    max_hops: int = 2,
) -> list[dict[str, Any]]:
    """
    Get relationships for an entity.

    Traverses the knowledge graph to find:
    - Direct relationships
    - Multi-hop connections
    - Related entities
    """
    await setup_cognee()

    query = f"relationships of {entity_name}"
    if relationship_type:
        query += f" type {relationship_type}"

    results = await cognee.search(
        query_text=query,
        query_type="GRAPH_COMPLETION",
    )

    return [
        {
            "source": entity_name,
            "relation": r.get("relation") if isinstance(r, dict) else "related",
            "target": r.get("target") if isinstance(r, dict) else str(r),
        }
        for r in results
    ]


async def compare_protocols(
    protocol_a: str,
    protocol_b: str,
) -> dict[str, Any]:
    """
    Compare two protocols using knowledge graph.

    Analyzes:
    - Architectural similarities
    - Token economics differences
    - Security posture
    - Integration overlap
    """
    await setup_cognee()

    # Search for comparison insights
    query = f"compare {protocol_a} and {protocol_b} protocols"
    results = await cognee.search(
        query_text=query,
        query_type="GRAPH_COMPLETION",
    )

    return {
        "protocol_a": protocol_a,
        "protocol_b": protocol_b,
        "similarities": [],
        "differences": [],
        "insights": [
            r.get("content") if isinstance(r, dict) else str(r) for r in results
        ],
    }


async def get_vulnerability_patterns(
    protocol_name: str | None = None,
    vulnerability_type: str | None = None,
) -> list[dict[str, Any]]:
    """
    Query vulnerability patterns from audits.

    Useful for:
    - Security research
    - Risk assessment
    - Similar vulnerability detection
    """
    await setup_cognee()

    query = "vulnerability patterns"
    if protocol_name:
        query += f" in {protocol_name}"
    if vulnerability_type:
        query += f" type {vulnerability_type}"

    results = await cognee.search(
        query_text=query,
        query_type="GRAPH_COMPLETION",
    )

    return [
        {
            "pattern": r.get("content") if isinstance(r, dict) else str(r),
            "severity": r.get("severity") if isinstance(r, dict) else None,
            "affected_protocols": r.get("protocols") if isinstance(r, dict) else None,
        }
        for r in results
    ]
