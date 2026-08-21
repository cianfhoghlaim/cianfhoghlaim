"""
Corpus Search Tools for Agno Agents.

Provides access to Irish/Celtic folklore and linguistic corpora:
- Dúchas.ie (National Folklore Collection)
- Canuint.ie (Dialect recordings)
- Corpas na Gaeilge (Contemporary Irish corpus)
- eDIL (Dictionary of Irish)
- DASG (Scottish Gaelic archive)
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import httpx
from agno.tools import Toolkit


class CorpusSearchTools(Toolkit):
    """
    Agno toolkit for searching Irish/Celtic corpora.

    Provides access to folklore, dialect, and linguistic resources.
    """

    def __init__(
        self,
        mcp_endpoint: Optional[str] = None,
        default_limit: int = 20,
    ):
        super().__init__(name="corpus_search")
        self.mcp_endpoint = mcp_endpoint or os.getenv(
            "MCP_ENDPOINT", "http://localhost:3000/api/mcp"
        )
        self.default_limit = default_limit

        # Register tools
        self.register(self.search_duchas)
        self.register(self.search_canuint)
        self.register(self.search_gaois)
        self.register(self.search_dil)
        self.register(self.search_all_corpora)

    async def _mcp_call(self, method: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Make a call to the MCP endpoint."""
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

    def search_duchas(
        self,
        query: str,
        collection: Optional[str] = None,
        county: Optional[str] = None,
        limit: int = 20,
    ) -> str:
        """
        Search Dúchas.ie (National Folklore Collection).

        Contains folklore, oral history, and traditional knowledge.

        Args:
            query: Search query.
            collection: Collection filter (schools, main, audio).
            county: County filter (e.g., Galway, Kerry).
            limit: Maximum results.

        Returns:
            JSON string with folklore items.
        """
        import asyncio
        import json

        async def _search():
            arguments = {"query": query, "limit": limit, "source": "duchas"}
            if collection:
                arguments["collection"] = collection
            if county:
                arguments["county"] = county

            return await self._mcp_call("corpus-search", arguments)

        result = asyncio.get_event_loop().run_until_complete(_search())
        return json.dumps(result, indent=2, ensure_ascii=False)

    def search_canuint(
        self,
        query: str,
        dialect: Optional[str] = None,
        limit: int = 20,
    ) -> str:
        """
        Search Canuint.ie (Irish dialect recordings).

        Contains dialect examples and pronunciation samples.

        Args:
            query: Search query (word or phrase).
            dialect: Dialect filter (connacht, munster, ulster).
            limit: Maximum results.

        Returns:
            JSON string with dialect recordings.
        """
        import asyncio
        import json

        async def _search():
            arguments = {"query": query, "limit": limit, "source": "canuint"}
            if dialect:
                arguments["dialect"] = dialect

            return await self._mcp_call("corpus-search", arguments)

        result = asyncio.get_event_loop().run_until_complete(_search())
        return json.dumps(result, indent=2, ensure_ascii=False)

    def search_gaois(
        self,
        query: str,
        resource: str = "terminologia",
        limit: int = 20,
    ) -> str:
        """
        Search GAOIS resources (gaois.ie).

        Provides access to terminology, placenames, and more.

        Args:
            query: Search query.
            resource: Resource type (terminologia, logainm, ainm).
            limit: Maximum results.

        Returns:
            JSON string with GAOIS results.
        """
        import asyncio
        import json

        async def _search():
            arguments = {
                "query": query,
                "limit": limit,
                "source": "gaois",
                "resource": resource,
            }
            return await self._mcp_call("corpus-search", arguments)

        result = asyncio.get_event_loop().run_until_complete(_search())
        return json.dumps(result, indent=2, ensure_ascii=False)

    def search_dil(
        self,
        query: str,
        limit: int = 20,
    ) -> str:
        """
        Search eDIL (Dictionary of the Irish Language).

        Historical/medieval Irish dictionary.

        Args:
            query: Search query (word or headword).
            limit: Maximum results.

        Returns:
            JSON string with dictionary entries.
        """
        import asyncio
        import json

        async def _search():
            arguments = {"query": query, "limit": limit, "source": "dil"}
            return await self._mcp_call("corpus-search", arguments)

        result = asyncio.get_event_loop().run_until_complete(_search())
        return json.dumps(result, indent=2, ensure_ascii=False)

    def search_all_corpora(
        self,
        query: str,
        limit: int = 10,
    ) -> str:
        """
        Search across all available corpora.

        Searches Dúchas, Canuint, GAOIS, and eDIL.

        Args:
            query: Search query.
            limit: Maximum results per source.

        Returns:
            JSON string with aggregated results.
        """
        import asyncio
        import json

        async def _search():
            arguments = {"query": query, "limit": limit, "source": "all"}
            return await self._mcp_call("corpus-search", arguments)

        result = asyncio.get_event_loop().run_until_complete(_search())
        return json.dumps(result, indent=2, ensure_ascii=False)
