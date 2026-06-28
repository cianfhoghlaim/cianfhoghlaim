"""
Curriculum Agent - Education Content Search and Q&A.

Specialized agent for curriculum-related queries:
- Search curriculum specifications
- Find learning outcomes by subject/strand
- Answer questions about Irish and UK curricula
- Compare curricula across nations

Uses semantic search over LanceDB embeddings with
BAML-extracted structured curriculum data.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from .root_agent import AgentContext, AgentDomain, AgentResponse

# ============================================================================
# Configuration
# ============================================================================

@dataclass
class CurriculumAgentConfig:
    """Configuration for curriculum agent."""

    lancedb_path: str = "./storage/data/lancedb"
    duckdb_path: str = "./storage/data/celtic_education.duckdb"
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    max_search_results: int = 10
    context_window: int = 3000


# ============================================================================
# Curriculum Search Tool
# ============================================================================

class CurriculumSearchTool:
    """
    Search tool for curriculum content.

    Searches across:
    - Irish curriculum (curriculumonline.ie, NCCA)
    - UK curricula (DfE, Education Scotland, Curriculum for Wales)
    - Exam papers and marking schemes
    """

    def __init__(self, config: CurriculumAgentConfig):
        self.config = config
        self._db = None
        self._model = None

    def _get_db(self):
        """Lazy-load LanceDB."""
        if self._db is None:
            import lancedb
            self._db = lancedb.connect(self.config.lancedb_path)
        return self._db

    def _get_model(self):
        """Lazy-load embedding model."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.config.embedding_model)
        return self._model

    def search(
        self,
        query: str,
        nation: str | None = None,
        subject: str | None = None,
        level: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Search curriculum content.

        Args:
            query: Search query text
            nation: Filter by nation (ireland, england, scotland, wales, etc.)
            subject: Filter by subject code
            level: Filter by education level (primary, junior_cycle, leaving_cert)
            limit: Maximum results

        Returns:
            List of matching curriculum documents
        """
        db = self._get_db()
        model = self._get_model()

        # Generate query embedding
        query_embedding = model.encode(query).tolist()

        # Search tables
        tables_to_search = ["oideachas.curriculum", "oileain.curriculum"]
        all_results = []

        for table_name in tables_to_search:
            if table_name not in db.table_names():
                continue

            table = db.open_table(table_name)

            # Build filter
            filters = []
            if nation:
                filters.append(f"nation = '{nation}'")
            if subject:
                filters.append(f"subject LIKE '%{subject}%'")
            if level:
                filters.append(f"level = '{level}'")

            filter_str = " AND ".join(filters) if filters else None

            try:
                search_query = table.search(query_embedding).limit(limit)
                if filter_str:
                    search_query = search_query.where(filter_str)

                results = search_query.to_list()

                for r in results:
                    all_results.append({
                        "id": r.get("id", hash(r.get("text", ""))),
                        "title": r.get("title", "Untitled"),
                        "content": r.get("text", "")[:500],
                        "nation": r.get("nation", "ireland" if "oideachas" in table_name else "uk"),
                        "subject": r.get("subject"),
                        "level": r.get("level"),
                        "source": r.get("source"),
                        "score": float(r.get("_distance", 0)),
                        "url": r.get("url") or r.get("pdf_url"),
                    })

            except Exception:
                continue

        # Sort by relevance
        all_results.sort(key=lambda x: x["score"])
        return all_results[:limit]

    def get_learning_outcomes(
        self,
        subject: str,
        strand: str | None = None,
        level: str = "junior_cycle",
    ) -> list[dict[str, Any]]:
        """
        Get learning outcomes for a subject.

        Args:
            subject: Subject code (e.g., "irish", "maths")
            strand: Optional strand filter
            level: Education level

        Returns:
            List of learning outcomes
        """
        import duckdb

        conn = duckdb.connect(self.config.duckdb_path, read_only=True)

        try:
            query = """
                SELECT
                    lo_code,
                    description_en,
                    description_ga,
                    strand_name,
                    strand_unit_name,
                    difficulty_level
                FROM education.learning_outcomes
                WHERE LOWER(subject) LIKE ?
                  AND LOWER(level) = ?
            """
            params = [f"%{subject.lower()}%", level.lower()]

            if strand:
                query += " AND LOWER(strand_name) LIKE ?"
                params.append(f"%{strand.lower()}%")

            query += " ORDER BY lo_code LIMIT 50"

            results = conn.execute(query, params).fetchall()
            columns = ["lo_code", "description_en", "description_ga",
                       "strand_name", "strand_unit_name", "difficulty_level"]

            return [dict(zip(columns, row, strict=False)) for row in results]

        except Exception:
            return []

        finally:
            conn.close()


# ============================================================================
# Curriculum Agent
# ============================================================================

class CurriculumAgent:
    """
    Agent for curriculum-related queries.

    Capabilities:
    - Search curriculum content by keywords
    - Find learning outcomes by subject/strand
    - Answer questions about curriculum structure
    - Compare curricula across nations
    """

    def __init__(self, config: CurriculumAgentConfig | None = None):
        self.config = config or CurriculumAgentConfig()
        self.search_tool = CurriculumSearchTool(self.config)
        self._llm = None

    def _get_llm(self):
        """Lazy-load LLM for response generation."""
        if self._llm is None:
            try:
                import google.generativeai as genai
                self._llm = genai.GenerativeModel("gemini-2.0-flash-exp")
            except Exception:
                self._llm = None
        return self._llm

    def _extract_filters(self, query: str) -> dict[str, str | None]:
        """Extract filters from query."""
        filters = {
            "nation": None,
            "subject": None,
            "level": None,
        }

        query_lower = query.lower()

        # Nation detection
        if "ireland" in query_lower or "irish" in query_lower:
            filters["nation"] = "ireland"
        elif "scotland" in query_lower or "scottish" in query_lower:
            filters["nation"] = "scotland"
        elif "wales" in query_lower or "welsh" in query_lower:
            filters["nation"] = "wales"
        elif "england" in query_lower or "english" in query_lower:
            filters["nation"] = "england"

        # Level detection
        if "junior cycle" in query_lower or "junior cert" in query_lower:
            filters["level"] = "junior_cycle"
        elif "leaving cert" in query_lower or "senior cycle" in query_lower:
            filters["level"] = "leaving_cert"
        elif "primary" in query_lower:
            filters["level"] = "primary"
        elif "gcse" in query_lower:
            filters["level"] = "gcse"
        elif "a level" in query_lower or "a-level" in query_lower:
            filters["level"] = "a_level"

        # Subject detection
        subjects = [
            "irish", "gaeilge", "maths", "mathematics", "english",
            "science", "history", "geography", "music", "art",
            "welsh", "gaelic", "french", "german", "spanish",
        ]
        for subj in subjects:
            if subj in query_lower:
                filters["subject"] = subj
                break

        return filters

    async def process(self, context: AgentContext) -> AgentResponse:
        """
        Process a curriculum query.

        1. Extract filters from query
        2. Search curriculum content
        3. Generate response with LLM
        """
        query = context.query
        filters = self._extract_filters(query)

        # Override with context if provided
        if context.nation:
            filters["nation"] = context.nation

        # Search for relevant content
        search_results = self.search_tool.search(
            query=query,
            nation=filters["nation"],
            subject=filters["subject"],
            level=filters["level"],
            limit=self.config.max_search_results,
        )

        # If asking about learning outcomes specifically
        if "learning outcome" in query.lower() and filters["subject"]:
            los = self.search_tool.get_learning_outcomes(
                subject=filters["subject"],
                level=filters["level"] or "junior_cycle",
            )
            if los:
                search_results = los + search_results[:5]

        # Generate response
        if not search_results:
            return AgentResponse(
                content="I couldn't find curriculum content matching your query. Try being more specific about the subject, level, or nation.",
                domain=AgentDomain.CURRICULUM,
                follow_up_queries=[
                    "What subjects are available in Junior Cycle?",
                    "Show me Irish curriculum learning outcomes",
                    "Compare Junior Cycle and GCSE",
                ],
            )

        # Build context for LLM
        context_text = "\n\n".join([
            f"**{r.get('title', 'Document')}**\n{r.get('content', r.get('description_en', ''))}"
            for r in search_results[:5]
        ])

        llm = self._get_llm()

        if llm:
            prompt = f"""You are a helpful curriculum expert for Celtic education (Ireland, Scotland, Wales).

Based on this curriculum content:

{context_text}

Answer this question: {query}

Provide a clear, informative answer. If the content doesn't fully answer the question, say so.
Reference specific curriculum documents or learning outcomes where relevant.
"""

            try:
                response = await asyncio.to_thread(
                    llm.generate_content,
                    prompt,
                )
                content = response.text
            except Exception:
                content = self._format_results(search_results[:5])
        else:
            content = self._format_results(search_results[:5])

        # Prepare sources
        sources = [
            {
                "title": r.get("title", "Untitled"),
                "url": r.get("url"),
                "nation": r.get("nation"),
            }
            for r in search_results[:5]
            if r.get("url")
        ]

        return AgentResponse(
            content=content,
            domain=AgentDomain.CURRICULUM,
            sources=sources,
            metadata={
                "filters": filters,
                "result_count": len(search_results),
            },
            follow_up_queries=self._generate_follow_ups(query, filters),
        )

    def _format_results(self, results: list[dict[str, Any]]) -> str:
        """Format search results as readable text."""
        if not results:
            return "No results found."

        lines = ["Here's what I found:\n"]

        for i, r in enumerate(results, 1):
            title = r.get("title") or r.get("lo_code", f"Result {i}")
            content = r.get("content") or r.get("description_en", "")
            nation = r.get("nation", "")

            lines.append(f"**{i}. {title}** ({nation})")
            lines.append(f"   {content[:200]}...")
            lines.append("")

        return "\n".join(lines)

    def _generate_follow_ups(
        self,
        query: str,
        filters: dict[str, str | None],
    ) -> list[str]:
        """Generate follow-up query suggestions."""
        follow_ups = []

        if filters["subject"]:
            subject = filters["subject"]
            follow_ups.append(f"What are the strands in {subject}?")
            follow_ups.append(f"Show {subject} exam paper analysis")

        if filters["nation"]:
            nation = filters["nation"]
            other_nations = [n for n in ["ireland", "scotland", "wales"]
                            if n != nation]
            if other_nations:
                follow_ups.append(f"Compare with {other_nations[0]} curriculum")

        if not filters["level"]:
            follow_ups.append("Filter by Junior Cycle")
            follow_ups.append("Filter by Leaving Certificate")

        return follow_ups[:3]

    async def stream(self, context: AgentContext):
        """Stream response for AG-UI."""
        # For now, just yield the full response
        response = await self.process(context)
        yield response.content


# ============================================================================
# Factory Function
# ============================================================================

def create_curriculum_agent(config: CurriculumAgentConfig | None = None) -> CurriculumAgent:
    """Create curriculum agent instance."""
    return CurriculumAgent(config)
