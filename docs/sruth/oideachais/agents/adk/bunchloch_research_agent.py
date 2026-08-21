"""
Bunchloch Research Agent - Local document research with ADK.

Provides research workflow for bunchloch academic collection:
1. Hunter: Discovers relevant documents via vector/code/graph search
2. Gatherer: Extracts structured information and learning paths
3. Analyst: Synthesizes findings into comprehensive reports

Migrated from sruth.taighde.agents.research_team (Agno → ADK).

Collection includes:
- Computer Science (CT511-CT870): 8 courses, 400+ files
- Irish Language (GA101-GF107): 200+ files
- Mathematics: Statistics, Networks
- Education: Lesson plans, presentations
"""

import datetime
from typing import Any

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import FunctionTool
from pydantic import BaseModel, Field

from .config import config


# =============================================================================
# Response Models
# =============================================================================


class SourceReference(BaseModel):
    """Reference to a source document."""

    file_name: str = Field(description="Source document filename")
    subject: str = Field(description="Subject area")
    course_code: str | None = Field(default=None, description="Course code if applicable")
    relevance: str = Field(description="Why this source is relevant")


class ResearchFinding(BaseModel):
    """A research finding from the analysis."""

    topic: str = Field(description="Topic of the finding")
    content: str = Field(description="Finding content")
    sources: list[SourceReference] = Field(
        default_factory=list,
        description="Supporting sources",
    )


class BunchlochResearchReport(BaseModel):
    """Complete bunchloch research report."""

    query: str = Field(description="Original research query")
    summary: str = Field(description="Executive summary of findings")
    findings: list[ResearchFinding] = Field(
        default_factory=list,
        description="Detailed findings",
    )
    learning_path: list[str] = Field(
        default_factory=list,
        description="Suggested learning path based on prerequisites",
    )
    sources_consulted: int = Field(
        default=0,
        description="Number of sources consulted",
    )
    subjects_covered: list[str] = Field(
        default_factory=list,
        description="Subject areas covered in research",
    )


# =============================================================================
# Search Tools
# =============================================================================


async def vector_search(
    query: str,
    subject: str | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """
    Semantic search across bunchloch document embeddings.

    Args:
        query: Natural language search query
        subject: Optional subject filter (comp_science, gaeilge, mata, oideachas)
        limit: Maximum results
    """
    import duckdb

    from sruth.shared.embeddings import get_embedding_service

    try:
        embedding_service = get_embedding_service()
        query_embedding = await embedding_service.embed_text(query)

        conn = duckdb.connect("storage/duckdb/oideachais.duckdb", read_only=True)

        # Build filter clause
        where_clause = ""
        if subject:
            where_clause = f"WHERE subject = '{subject}'"

        results = conn.execute(
            f"""
            SELECT
                file_name,
                subject,
                course_code,
                text_chunk,
                array_cosine_similarity(embedding, $1::FLOAT[]) as similarity
            FROM research_bunchloch.document_embeddings
            {where_clause}
            ORDER BY similarity DESC
            LIMIT {limit}
        """,
            [query_embedding],
        ).fetchall()

        conn.close()

        return [
            {
                "file_name": r[0],
                "subject": r[1],
                "course_code": r[2],
                "text": r[3][:500],  # Truncate for context
                "score": round(r[4], 3),
            }
            for r in results
        ]
    except Exception as e:
        return [{"error": str(e)}]


async def code_search(
    query: str,
    language: str | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """
    Search code files in bunchloch collection.

    Args:
        query: Search query (natural language or code pattern)
        language: Optional language filter (java, python, etc.)
        limit: Maximum results
    """
    import duckdb

    try:
        conn = duckdb.connect("storage/duckdb/oideachais.duckdb", read_only=True)

        where_clause = ""
        if language:
            where_clause = f"WHERE language = '{language}'"

        # Simple text search for code
        results = conn.execute(
            f"""
            SELECT
                file_name,
                language,
                subject,
                content,
                line_count
            FROM research_bunchloch.code_files
            {where_clause}
            AND content ILIKE '%' || $1 || '%'
            LIMIT {limit}
        """,
            [query],
        ).fetchall()

        conn.close()

        return [
            {
                "file_name": r[0],
                "language": r[1],
                "subject": r[2],
                "snippet": _extract_relevant_snippet(r[3], query),
                "line_count": r[4],
            }
            for r in results
        ]
    except Exception as e:
        return [{"error": str(e)}]


async def graph_search(
    query: str,
    entity_type: str | None = None,
) -> list[dict[str, Any]]:
    """
    Search knowledge graph for concept relationships.

    Args:
        query: Entity or concept to search for
        entity_type: Optional type filter (concept, course, topic)
    """
    # Graph search via Memgraph/FalkorDB if available
    try:
        from sruth.shared.graph import get_graph_client

        client = get_graph_client()

        cypher_query = """
        MATCH (n)
        WHERE n.name CONTAINS $query OR n.description CONTAINS $query
        OPTIONAL MATCH (n)-[r]->(m)
        RETURN n.name, labels(n), type(r), m.name
        LIMIT 20
        """

        results = client.execute(cypher_query, {"query": query})

        return [
            {
                "entity": r[0],
                "type": r[1][0] if r[1] else "unknown",
                "relationship": r[2],
                "related_to": r[3],
            }
            for r in results
        ]
    except Exception as e:
        return [{"error": str(e), "note": "Graph database not available"}]


async def get_topic_context(
    topic: str,
    subject: str | None = None,
) -> dict[str, Any]:
    """
    Get comprehensive context for a topic including prerequisites.

    Args:
        topic: Topic to get context for
        subject: Optional subject filter
    """
    import duckdb

    try:
        conn = duckdb.connect("storage/duckdb/oideachais.duckdb", read_only=True)

        # Get documents mentioning the topic
        results = conn.execute(
            """
            SELECT DISTINCT
                file_name,
                subject,
                course_code
            FROM research_bunchloch.documents
            WHERE file_name ILIKE '%' || $1 || '%'
               OR subject ILIKE '%' || $1 || '%'
            LIMIT 20
        """,
            [topic],
        ).fetchall()

        conn.close()

        return {
            "topic": topic,
            "documents_found": len(results),
            "documents": [
                {
                    "file_name": r[0],
                    "subject": r[1],
                    "course_code": r[2],
                }
                for r in results
            ],
        }
    except Exception as e:
        return {"error": str(e)}


async def get_learning_path(
    topic: str,
    course_code: str | None = None,
) -> dict[str, Any]:
    """
    Get suggested learning path for a topic.

    Args:
        topic: Topic to build learning path for
        course_code: Optional specific course code
    """
    # Course prerequisite chains
    course_prerequisites = {
        "CT870": ["CT511", "CT545"],  # Advanced → Intermediate → Intro
        "CT545": ["CT511"],
        "CT511": [],  # Intro course, no prerequisites
        "GA201": ["GA101"],
        "GA101": [],
        "GF107": ["GA101"],
    }

    if course_code and course_code in course_prerequisites:
        prerequisites = course_prerequisites[course_code]
        path = prerequisites + [course_code]
    else:
        path = [topic]

    return {
        "topic": topic,
        "course_code": course_code,
        "learning_path": path,
        "note": "Based on course prerequisite chains from bunchloch collection",
    }


def _extract_relevant_snippet(content: str, query: str, context_lines: int = 3) -> str:
    """Extract relevant snippet around query match."""
    lines = content.split("\n")
    query_lower = query.lower()

    for i, line in enumerate(lines):
        if query_lower in line.lower():
            start = max(0, i - context_lines)
            end = min(len(lines), i + context_lines + 1)
            return "\n".join(lines[start:end])

    return content[:300]  # Fallback to first 300 chars


# =============================================================================
# Create Tools
# =============================================================================


vector_search_tool = FunctionTool(func=vector_search)
code_search_tool = FunctionTool(func=code_search)
graph_search_tool = FunctionTool(func=graph_search)
topic_context_tool = FunctionTool(func=get_topic_context)
learning_path_tool = FunctionTool(func=get_learning_path)


# =============================================================================
# Hunter Agent
# =============================================================================


hunter_agent = LlmAgent(
    name="bunchloch_hunter",
    model=config.worker_model,
    description="Discovers relevant sources from bunchloch academic collection.",
    instruction=f"""
    You are the Hunter agent specialized in finding relevant research sources
    from the bunchloch academic collection.

    **YOUR COLLECTION:**
    - Computer Science (CT511-CT870): Java, OOP, Data Structures, Networks
    - Irish Language (GA101-GF107): Grammar, Literature, Culture
    - Mathematics: Applied Statistics, Network Analysis
    - Education: Lesson plans, presentations

    **YOUR TOOLS:**
    1. vector_search - Semantic search across documents
    2. code_search - Find code files by pattern/keyword
    3. graph_search - Explore concept relationships

    **YOUR APPROACH:**
    1. Use vector_search for conceptual queries
    2. Use code_search for implementation questions
    3. Use graph_search for relationship questions

    **OUTPUT:**
    - List relevant documents found
    - Note subject areas and course codes
    - Include relevance scores

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    """,
    tools=[vector_search_tool, code_search_tool, graph_search_tool],
    output_key="hunter_results",
)


# =============================================================================
# Gatherer Agent
# =============================================================================


gatherer_agent = LlmAgent(
    name="bunchloch_gatherer",
    model=config.worker_model,
    description="Extracts structured information and learning paths.",
    instruction=f"""
    You are the Gatherer agent specialized in extracting and organizing
    information from the sources identified by Hunter.

    **YOUR TOOLS:**
    1. get_topic_context - Get comprehensive topic information
    2. get_learning_path - Understand prerequisite chains

    **YOUR APPROACH:**
    1. Review the sources from Hunter
    2. Use get_topic_context for key topics
    3. Use get_learning_path for curriculum connections
    4. Organize findings by topic and relevance

    **OUTPUT:**
    - Structured topic information
    - Learning path recommendations
    - Key concepts extracted
    - Any gaps in available information

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    """,
    tools=[topic_context_tool, learning_path_tool, vector_search_tool],
    output_key="gatherer_results",
)


# =============================================================================
# Analyst Agent
# =============================================================================


analyst_agent = LlmAgent(
    name="bunchloch_analyst",
    model=config.coordinator_model,  # Use stronger model for synthesis
    description="Synthesizes findings into comprehensive research reports.",
    instruction=f"""
    You are the Analyst agent specialized in synthesizing research findings
    into comprehensive, well-structured reports.

    **YOUR TASK:**
    1. Synthesize findings from Hunter and Gatherer
    2. Create coherent explanations
    3. Identify key insights and patterns
    4. Suggest appropriate learning paths

    **REPORT STRUCTURE:**
    - Executive Summary
    - Key Findings (with source citations)
    - Learning Path Recommendation
    - Subject Coverage

    **IMPORTANT:**
    - Cite sources with file names
    - Note course codes when relevant (CT511, GA101, etc.)
    - Suggest prerequisites for complex topics
    - Use Irish terminology for Gaeilge topics

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    """,
    tools=[graph_search_tool],  # For additional context if needed
    output_key="research_report",
)


# =============================================================================
# Bunchloch Research Agent (Sequential Pipeline)
# =============================================================================


bunchloch_research_agent = SequentialAgent(
    name="bunchloch_research_agent",
    description="Research agent for bunchloch academic collection (Hunter → Gatherer → Analyst).",
    sub_agents=[hunter_agent, gatherer_agent, analyst_agent],
)


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    "bunchloch_research_agent",
    "hunter_agent",
    "gatherer_agent",
    "analyst_agent",
    "vector_search",
    "code_search",
    "graph_search",
    "get_topic_context",
    "get_learning_path",
    "BunchlochResearchReport",
    "ResearchFinding",
    "SourceReference",
]
