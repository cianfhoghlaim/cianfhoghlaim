"""
Curriculum Search Tools for Agno Agents.

Provides curriculum search capabilities compatible with Agno Agent framework.
Supports both MCP backend and direct LanceDB fallback for hybrid, semantic,
and keyword search.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional

import httpx
from agno.tools import Toolkit

logger = logging.getLogger(__name__)


class CurriculumSearchTools(Toolkit):
    """
    Agno toolkit for searching Celtic curriculum content.

    Supports hybrid (vector + keyword), semantic, and keyword search
    across NCCA, SEC, and pan-Celtic curriculum documents.

    Falls back to direct LanceDB access when MCP is unavailable.
    """

    def __init__(
        self,
        mcp_endpoint: Optional[str] = None,
        lancedb_path: Optional[str] = None,
        default_top_k: int = 10,
    ):
        super().__init__(name="curriculum_search")
        self.mcp_endpoint = mcp_endpoint or os.getenv(
            "MCP_ENDPOINT", "http://localhost:3000/api/mcp"
        )
        self.lancedb_path = lancedb_path or os.getenv(
            "LANCEDB_PATH", "./storage/data/lancedb"
        )
        self.default_top_k = default_top_k
        self._db = None
        self._model = None

        # Register tools
        self.register(self.search_hybrid)
        self.register(self.search_semantic)
        self.register(self.search_keyword)
        self.register(self.get_learning_outcomes)
        self.register(self.get_subjects)

    def _get_db(self):
        """Lazy-load LanceDB connection."""
        if self._db is None:
            try:
                import lancedb
                self._db = lancedb.connect(self.lancedb_path)
            except Exception as e:
                logger.warning(f"Failed to connect to LanceDB: {e}")
                self._db = None
        return self._db

    def _get_model(self):
        """Lazy-load embedding model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(
                    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
                )
            except Exception as e:
                logger.warning(f"Failed to load embedding model: {e}")
                self._model = None
        return self._model

    async def _mcp_call(self, method: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Make a call to the MCP endpoint."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.mcp_endpoint,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/call",
                        "params": {
                            "name": method,
                            "arguments": arguments,
                        },
                    },
                    timeout=30.0,
                )
                response.raise_for_status()
                result = response.json()
                return result.get("result", {})
        except Exception as e:
            logger.warning(f"MCP call failed, using LanceDB fallback: {e}")
            return None

    def _lancedb_search(
        self,
        query: str,
        table_names: List[str],
        top_k: int = 10,
        filters: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        """Direct LanceDB vector search fallback."""
        db = self._get_db()
        model = self._get_model()

        if db is None or model is None:
            return []

        # Generate query embedding
        query_embedding = model.encode(query).tolist()

        all_results = []
        for table_name in table_names:
            try:
                if table_name not in db.table_names():
                    continue

                table = db.open_table(table_name)
                search_query = table.search(query_embedding).limit(top_k)

                # Apply filters
                if filters:
                    filter_parts = []
                    for key, value in filters.items():
                        if value:
                            filter_parts.append(f"{key} = '{value}'")
                    if filter_parts:
                        search_query = search_query.where(" AND ".join(filter_parts))

                results = search_query.to_list()

                for r in results:
                    all_results.append({
                        "id": r.get("id", f"{table_name}_{hash(r.get('text', ''))}"),
                        "title": r.get("title", ""),
                        "content": r.get("text", "")[:500],
                        "subject": r.get("subject"),
                        "level": r.get("level"),
                        "strand": r.get("strand"),
                        "source": table_name,
                        "score": float(r.get("_distance", 0)),
                        "language": r.get("language", "en"),
                        "nation": r.get("nation", "ireland"),
                    })
            except Exception as e:
                logger.warning(f"Search failed for table {table_name}: {e}")
                continue

        # Sort by score (lower distance = better)
        all_results.sort(key=lambda x: x["score"])
        return all_results[:top_k]

    def search_hybrid(
        self,
        vector_query: str,
        keyword_query: Optional[str] = None,
        top_k: int = 10,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3,
        level: Optional[str] = None,
        subject: Optional[str] = None,
        nation: str = "ireland",
    ) -> str:
        """
        Search curriculum using hybrid search (vector + keyword).

        Best for natural language queries about curriculum content.

        Args:
            vector_query: Natural language query for semantic search.
            keyword_query: Optional keywords for exact matching.
            top_k: Number of results (default: 10).
            vector_weight: Weight for vector search (0-1).
            keyword_weight: Weight for keyword search (0-1).
            level: Education level (primary, junior_cycle, senior_cycle, leaving_cert).
            subject: Subject code (e.g., mathematics, irish).
            nation: Nation (ireland, scotland, wales, england, northern_ireland).

        Returns:
            JSON string with search results.
        """
        import asyncio

        async def _search():
            arguments = {
                "vector_query": vector_query,
                "keyword_query": keyword_query or vector_query,
                "top_k": top_k,
                "vector_weight": vector_weight,
                "keyword_weight": keyword_weight,
            }
            if level:
                arguments["level"] = level
            if subject:
                arguments["subject"] = subject
            if nation != "ireland":
                arguments["nation"] = nation

            result = await self._mcp_call("search-hybrid", arguments)
            if result is not None:
                return result

            # LanceDB fallback
            table_names = ["oideachas.curriculum", "oileain.curriculum"]
            filters = {}
            if level:
                filters["level"] = level
            if subject:
                filters["subject"] = subject
            if nation != "ireland":
                filters["nation"] = nation

            results = self._lancedb_search(vector_query, table_names, top_k, filters)
            return {"results": results, "source": "lancedb", "query": vector_query}

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        result = loop.run_until_complete(_search())
        return json.dumps(result, indent=2, ensure_ascii=False)

    def search_semantic(
        self,
        query: str,
        top_k: int = 10,
        level: Optional[str] = None,
        subject: Optional[str] = None,
    ) -> str:
        """
        Search curriculum using pure semantic similarity.

        Best for finding conceptually related content.

        Args:
            query: Natural language query.
            top_k: Number of results (default: 10).
            level: Education level filter.
            subject: Subject filter.

        Returns:
            JSON string with search results.
        """
        import asyncio

        async def _search():
            arguments = {"query": query, "top_k": top_k}
            if level:
                arguments["level"] = level
            if subject:
                arguments["subject"] = subject

            result = await self._mcp_call("search-semantic", arguments)
            if result is not None:
                return result

            # LanceDB fallback
            table_names = ["oideachas.curriculum", "oileain.curriculum"]
            filters = {}
            if level:
                filters["level"] = level
            if subject:
                filters["subject"] = subject

            results = self._lancedb_search(query, table_names, top_k, filters)
            return {"results": results, "source": "lancedb", "query": query}

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        result = loop.run_until_complete(_search())
        return json.dumps(result, indent=2, ensure_ascii=False)

    def search_keyword(
        self,
        query: str,
        top_k: int = 10,
        exact_match: bool = False,
    ) -> str:
        """
        Search curriculum using keyword matching.

        Best for finding exact terms or codes.

        Args:
            query: Keyword search query.
            top_k: Number of results (default: 10).
            exact_match: Require exact phrase match.

        Returns:
            JSON string with search results.
        """
        import asyncio

        async def _search():
            arguments = {
                "query": query,
                "top_k": top_k,
                "exact_match": exact_match,
            }
            result = await self._mcp_call("search-keyword", arguments)
            if result is not None:
                return result

            # LanceDB fallback - use semantic search for keyword-like results
            table_names = ["oideachas.curriculum", "oileain.curriculum"]
            results = self._lancedb_search(query, table_names, top_k, None)
            return {"results": results, "source": "lancedb", "query": query}

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        result = loop.run_until_complete(_search())
        return json.dumps(result, indent=2, ensure_ascii=False)

    def get_learning_outcomes(
        self,
        subject: str,
        level: str,
        strand: Optional[str] = None,
    ) -> str:
        """
        Get learning outcomes for a subject and level.

        Args:
            subject: Subject code (e.g., mathematics, irish, geography).
            level: Education level (primary, junior_cycle, senior_cycle).
            strand: Optional strand filter.

        Returns:
            JSON string with learning outcomes.
        """
        import asyncio

        async def _get():
            arguments = {"subject": subject, "level": level}
            if strand:
                arguments["strand"] = strand

            result = await self._mcp_call("get-learning-outcomes", arguments)
            if result is not None:
                return result

            # LanceDB fallback - search for learning outcomes
            query = f"learning outcomes {subject} {level}"
            if strand:
                query += f" {strand}"
            table_names = ["oideachas.curriculum"]
            filters = {"subject": subject, "level": level}
            if strand:
                filters["strand"] = strand

            results = self._lancedb_search(query, table_names, 20, filters)
            return {"learning_outcomes": results, "source": "lancedb", "subject": subject, "level": level}

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        result = loop.run_until_complete(_get())
        return json.dumps(result, indent=2, ensure_ascii=False)

    def get_subjects(
        self,
        level: str,
        nation: str = "ireland",
    ) -> str:
        """
        Get all subjects for an education level.

        Args:
            level: Education level (primary, junior_cycle, senior_cycle, leaving_cert).
            nation: Nation (ireland, scotland, wales, england, northern_ireland).

        Returns:
            JSON string with subjects list.
        """
        import asyncio

        async def _get():
            arguments = {"level": level, "nation": nation}
            result = await self._mcp_call("get-subjects", arguments)
            if result is not None:
                return result

            # Static fallback for Irish curriculum subjects
            subjects_by_level = {
                "primary": [
                    {"code": "irish", "name": "Gaeilge", "name_en": "Irish"},
                    {"code": "english", "name": "Béarla", "name_en": "English"},
                    {"code": "mathematics", "name": "Matamaitic", "name_en": "Mathematics"},
                    {"code": "sese", "name": "OSIE", "name_en": "Social Environmental & Scientific Ed"},
                    {"code": "arts", "name": "Na hEalaíona", "name_en": "Arts Education"},
                    {"code": "pe", "name": "Corpoideachas", "name_en": "Physical Education"},
                    {"code": "sphe", "name": "OSPS", "name_en": "Social Personal & Health Education"},
                ],
                "junior_cycle": [
                    {"code": "irish", "name": "Gaeilge", "name_en": "Irish"},
                    {"code": "english", "name": "Béarla", "name_en": "English"},
                    {"code": "mathematics", "name": "Matamaitic", "name_en": "Mathematics"},
                    {"code": "science", "name": "Eolaíocht", "name_en": "Science"},
                    {"code": "history", "name": "Stair", "name_en": "History"},
                    {"code": "geography", "name": "Tíreolaíocht", "name_en": "Geography"},
                    {"code": "modern_languages", "name": "Nuatheangacha", "name_en": "Modern Languages"},
                    {"code": "business", "name": "Gnó", "name_en": "Business Studies"},
                ],
                "senior_cycle": [
                    {"code": "irish", "name": "Gaeilge", "name_en": "Irish"},
                    {"code": "english", "name": "Béarla", "name_en": "English"},
                    {"code": "mathematics", "name": "Matamaitic", "name_en": "Mathematics"},
                    {"code": "biology", "name": "Bitheolaíocht", "name_en": "Biology"},
                    {"code": "chemistry", "name": "Ceimic", "name_en": "Chemistry"},
                    {"code": "physics", "name": "Fisic", "name_en": "Physics"},
                    {"code": "history", "name": "Stair", "name_en": "History"},
                    {"code": "geography", "name": "Tíreolaíocht", "name_en": "Geography"},
                ],
                "leaving_cert": [
                    {"code": "irish", "name": "Gaeilge", "name_en": "Irish", "levels": ["higher", "ordinary", "foundation"]},
                    {"code": "english", "name": "Béarla", "name_en": "English", "levels": ["higher", "ordinary"]},
                    {"code": "mathematics", "name": "Matamaitic", "name_en": "Mathematics", "levels": ["higher", "ordinary", "foundation"]},
                ],
            }
            return {
                "subjects": subjects_by_level.get(level, []),
                "source": "static",
                "level": level,
                "nation": nation,
            }

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        result = loop.run_until_complete(_get())
        return json.dumps(result, indent=2, ensure_ascii=False)
