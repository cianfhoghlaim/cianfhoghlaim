"""
Translation Tools for Agno Agents.

Provides translation between Celtic languages:
- Irish (Gaeilge) - ga
- Welsh (Cymraeg) - cy
- Scottish Gaelic (Gàidhlig) - gd
- Manx (Gaelg) - gv
- Cornish (Kernewek) - kw
- Breton (Brezhoneg) - br
- English - en

Preserves educational terminology using tearma.ie.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import httpx
from agno.tools import Toolkit


# Language codes and names
CELTIC_LANGUAGES = {
    "ga": "Irish (Gaeilge)",
    "cy": "Welsh (Cymraeg)",
    "gd": "Scottish Gaelic (Gàidhlig)",
    "gv": "Manx (Gaelg)",
    "kw": "Cornish (Kernewek)",
    "br": "Breton (Brezhoneg)",
    "en": "English",
}

# Irish dialects
IRISH_DIALECTS = {
    "connacht": "Connacht (Conamara, Galway)",
    "munster": "Munster (Kerry, Cork, Waterford)",
    "ulster": "Ulster (Donegal, Belfast)",
    "standard": "Caighdeán Oifigiúil (Official Standard)",
}


class TranslationTools(Toolkit):
    """
    Agno toolkit for Celtic language translation.

    Supports translation between Celtic languages with
    preservation of educational terminology.
    """

    def __init__(
        self,
        mcp_endpoint: Optional[str] = None,
        default_target: str = "ga",
    ):
        super().__init__(name="translation")
        self.mcp_endpoint = mcp_endpoint or os.getenv(
            "MCP_ENDPOINT", "http://localhost:3000/api/mcp"
        )
        self.default_target = default_target

        # Register tools
        self.register(self.translate)
        self.register(self.lookup_terminology)
        self.register(self.get_dialect_variant)
        self.register(self.detect_language)
        self.register(self.get_pronunciation)

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

    def translate(
        self,
        text: str,
        source_language: str = "en",
        target_language: str = "ga",
        preserve_terminology: bool = True,
        dialect: Optional[str] = None,
    ) -> str:
        """
        Translate text between Celtic languages.

        Args:
            text: Text to translate.
            source_language: Source language code (en, ga, cy, gd, gv, kw, br).
            target_language: Target language code.
            preserve_terminology: Preserve educational/technical terms.
            dialect: Irish dialect preference (connacht, munster, ulster, standard).

        Returns:
            JSON string with translation and notes.
        """
        import asyncio
        import json

        async def _translate():
            arguments = {
                "text": text,
                "source_language": source_language,
                "target_language": target_language,
                "preserve_terminology": preserve_terminology,
            }
            if dialect:
                arguments["dialect"] = dialect

            return await self._mcp_call("translate", arguments)

        result = asyncio.get_event_loop().run_until_complete(_translate())
        return json.dumps(result, indent=2, ensure_ascii=False)

    def lookup_terminology(
        self,
        term: str,
        domain: str = "education",
        source_language: str = "en",
        target_language: str = "ga",
    ) -> str:
        """
        Look up official terminology from tearma.ie.

        Args:
            term: Term to look up.
            domain: Domain (education, science, law, computing).
            source_language: Source language.
            target_language: Target language.

        Returns:
            JSON string with official terms and alternatives.
        """
        import asyncio
        import json

        async def _lookup():
            arguments = {
                "term": term,
                "domain": domain,
                "source_language": source_language,
                "target_language": target_language,
            }
            return await self._mcp_call("terminology-lookup", arguments)

        result = asyncio.get_event_loop().run_until_complete(_lookup())
        return json.dumps(result, indent=2, ensure_ascii=False)

    def get_dialect_variant(
        self,
        text: str,
        dialect: str,
    ) -> str:
        """
        Get dialect-specific variant of Irish text.

        Args:
            text: Text in standard Irish.
            dialect: Target dialect (connacht, munster, ulster).

        Returns:
            JSON string with dialect variant and pronunciation notes.
        """
        import asyncio
        import json

        async def _get_variant():
            arguments = {"text": text, "dialect": dialect}
            return await self._mcp_call("dialect-variant", arguments)

        result = asyncio.get_event_loop().run_until_complete(_get_variant())
        return json.dumps(result, indent=2, ensure_ascii=False)

    def detect_language(
        self,
        text: str,
    ) -> str:
        """
        Detect the language of text.

        Optimized for Celtic languages with dialect detection for Irish.

        Args:
            text: Text to analyze.

        Returns:
            JSON string with detected language and confidence.
        """
        import asyncio
        import json

        async def _detect():
            arguments = {"text": text}
            return await self._mcp_call("detect-language", arguments)

        result = asyncio.get_event_loop().run_until_complete(_detect())
        return json.dumps(result, indent=2, ensure_ascii=False)

    def get_pronunciation(
        self,
        text: str,
        language: str = "ga",
        dialect: Optional[str] = None,
        format: str = "ipa",
    ) -> str:
        """
        Get pronunciation guide for text.

        Args:
            text: Text to pronounce.
            language: Language code.
            dialect: Irish dialect (connacht, munster, ulster).
            format: Output format (ipa, phonetic, audio_url).

        Returns:
            JSON string with pronunciation guide.
        """
        import asyncio
        import json

        async def _get_pronunciation():
            arguments = {
                "text": text,
                "language": language,
                "format": format,
            }
            if dialect:
                arguments["dialect"] = dialect

            return await self._mcp_call("pronunciation", arguments)

        result = asyncio.get_event_loop().run_until_complete(_get_pronunciation())
        return json.dumps(result, indent=2, ensure_ascii=False)


# Convenience functions for direct use
def translate_to_irish(
    text: str,
    source: str = "en",
    preserve_terms: bool = True,
) -> str:
    """Convenience function to translate to Irish."""
    tools = TranslationTools()
    return tools.translate(
        text=text,
        source_language=source,
        target_language="ga",
        preserve_terminology=preserve_terms,
    )


def translate_to_english(
    text: str,
    source: str = "ga",
) -> str:
    """Convenience function to translate to English."""
    tools = TranslationTools()
    return tools.translate(
        text=text,
        source_language=source,
        target_language="en",
        preserve_terminology=True,
    )
