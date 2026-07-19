"""
Téarma.ie shared private state + module constants + helpers + linker.

Split out of the legacy `dlt_sources/tearma.py` flat file in Phase 4
(oideachais-audit-phase-4-consolidate-legacy-dirs) so each DLT source
gets its own file at the country-first canonical path
`dlt_sources/{nation}/{domain}/{entity}.py`.

Pre-existing fragile imports (out of this monorepo) are hardened with
`try/except ImportError` per the Phase 3D pattern:
- `from observability.logging import get_logger` — provided by an
  external observability package.
- `from cianfhoghlaim.dlt.common.http_client import tearma_client` — provided by an external
  `shared` package.

When these imports are missing the helpers fall back to no-op logger
and raise an explicit `RuntimeError` from `_get_tearma_factory()` so
the source is import-safe at module load time but the brokenness is
surfaced loudly at first use.
"""
from __future__ import annotations

import zipfile
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Pre-existing fragile imports — hardened with try/except
# ---------------------------------------------------------------------------
try:
    from observability.logging import get_logger

    logger = get_logger(__name__)
except ImportError:  # observability package not in this monorepo
    import logging as _logging

    logger = _logging.getLogger(__name__)


try:
    from cianfhoghlaim.dlt.common.http_client import tearma_client  # type: ignore[import-not-found]
except ImportError:  # shared package not in this monorepo
    tearma_client = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Module constants
# ---------------------------------------------------------------------------
TEARMA_DOWNLOAD_URL = "https://www.tearma.ie/ioslodail/25.04.01-tearma.ie-concepts.txt.zip"
TEARMA_API_BASE = "https://www.tearma.ie/api"


# ---------------------------------------------------------------------------
# HTTP factory
# ---------------------------------------------------------------------------
def _get_tearma_factory():
    """Get HTTP client factory for Téarma.ie."""
    if tearma_client is None:
        raise RuntimeError(
            "shared.http.tearma_client is unavailable — the 'shared' package "
            "is not in this monorepo. See dlt_sources/common/_shared_utils_stub.py."
        )
    return tearma_client()


# ---------------------------------------------------------------------------
# TSV parser
# ---------------------------------------------------------------------------
def _parse_tearma_tsv(content: str) -> Iterator[dict[str, Any]]:
    """
    Parse Téarma TSV export file.

    Format: English\\tIrish\\tDomain\\tDefinition\\t...

    Yields:
        Dictionary for each term entry
    """
    lines = content.strip().split("\n")

    for line_num, line in enumerate(lines, 1):
        if not line.strip():
            continue

        parts = line.split("\t")
        if len(parts) < 2:
            continue

        entry = {
            "term_en": parts[0].strip() if len(parts) > 0 else "",
            "term_ga": parts[1].strip() if len(parts) > 1 else "",
            "domain": parts[2].strip() if len(parts) > 2 else "",
            "definition_en": parts[3].strip() if len(parts) > 3 else "",
            "definition_ga": parts[4].strip() if len(parts) > 4 else "",
            "source": "tearma.ie",
            "line_number": line_num,
        }

        # Skip if no valid terms
        if not entry["term_en"] and not entry["term_ga"]:
            continue

        yield entry


# ---------------------------------------------------------------------------
# Export downloader
# ---------------------------------------------------------------------------
def _download_tearma_export() -> str:
    """
    Download and extract Téarma export file.

    Returns:
        Content of the TSV file

    Raises:
        ValueError: If no .txt file found in archive
        Exception: If download fails
    """
    logger.info("downloading_tearma_export", url=TEARMA_DOWNLOAD_URL)
    factory = _get_tearma_factory()

    with factory.create_client() as client:
        # Use full URL since download path differs from API base
        response = client.get(
            "/ioslodail/25.04.01-tearma.ie-concepts.txt.zip"
        )
        response.raise_for_status()

        # Extract ZIP content
        with zipfile.ZipFile(BytesIO(response.content)) as zf:
            # Get the first .txt file
            for name in zf.namelist():
                if name.endswith(".txt"):
                    content = zf.read(name).decode("utf-8")
                    logger.info(
                        "tearma_export_extracted",
                        filename=name,
                        size_bytes=len(content),
                    )
                    return content

    raise ValueError("No .txt file found in Téarma ZIP archive")


# ---------------------------------------------------------------------------
# API search
# ---------------------------------------------------------------------------
def _search_tearma_api(
    query: str,
    domain: str | None = None,
    language: str = "en",
) -> Iterator[dict[str, Any]]:
    """
    Search Téarma API for terms.

    Args:
        query: Search query
        domain: Optional domain filter
        language: Search language (en, ga)

    Yields:
        Term entries from API
    """
    params = {
        "teacs": query,
        "foinse": language,
    }
    if domain:
        params["domain"] = domain

    factory = _get_tearma_factory()

    with factory.create_client() as client:
        try:
            response = client.get("/api/cuardach/", params=params)
            response.raise_for_status()
            data = response.json()

            for result in data.get("results", []):
                yield {
                    "term_id": result.get("id"),
                    "term_en": result.get("en", ""),
                    "term_ga": result.get("ga", ""),
                    "domain": result.get("domain", ""),
                    "definition_en": result.get("definition_en", ""),
                    "definition_ga": result.get("definition_ga", ""),
                    "source": "tearma.ie-api",
                    "query": query,
                }
        except Exception as e:
            logger.warning(
                "tearma_api_error",
                query=query,
                error=str(e),
            )


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------
def _load_tearma_terms(
    use_api: bool = False,
    domain_filter: str | None = None,
    cache_path: Path | None = None,
) -> Iterator[dict[str, Any]]:
    """
    Load Téarma terms from export or API.

    Args:
        use_api: Whether to use API instead of export
        domain_filter: Optional domain filter
        cache_path: Path to cache downloaded export

    Yields:
        Term entries
    """
    if use_api:
        # API mode - requires specific queries
        yield {
            "status": "api_mode",
            "message": "Use tearma_search resource for API queries",
            "source": "tearma.ie",
            "loaded_at": datetime.now(UTC).isoformat(),
        }
        return

    # Download and parse export
    try:
        content = _download_tearma_export()

        count = 0
        for entry in _parse_tearma_tsv(content):
            # Apply domain filter if specified
            if domain_filter and domain_filter.lower() not in entry.get("domain", "").lower():
                continue

            entry["loaded_at"] = datetime.now(UTC).isoformat()
            yield entry
            count += 1

        logger.info("tearma_terms_loaded", count=count)

    except ValueError as e:
        logger.error(
            "tearma_parse_error",
            error=str(e),
        )
        yield {
            "status": "error",
            "error": str(e),
            "source": "tearma.ie",
            "loaded_at": datetime.now(UTC).isoformat(),
        }
    except Exception as e:
        logger.error(
            "tearma_download_error",
            error=str(e),
        )
        yield {
            "status": "error",
            "error": str(e),
            "source": "tearma.ie",
            "loaded_at": datetime.now(UTC).isoformat(),
        }


# ---------------------------------------------------------------------------
# Terminology linker
# ---------------------------------------------------------------------------
class TerminologyLinker:
    """
    Link curriculum text to Téarma terminology.

    Provides term matching and bilingual glossary generation.
    """

    def __init__(self, terms: list[dict[str, Any]] | None = None):
        """
        Initialize linker with terms.

        Args:
            terms: Pre-loaded terms, or None to load from export
        """
        self._terms: dict[str, dict[str, Any]] = {}
        self._terms_ga: dict[str, dict[str, Any]] = {}

        if terms:
            self._load_terms(terms)

    def _load_terms(self, terms: list[dict[str, Any]]) -> None:
        """Load terms into lookup dictionaries."""
        for term in terms:
            if "status" in term:
                continue

            en = term.get("term_en", "").lower().strip()
            ga = term.get("term_ga", "").lower().strip()

            if en:
                self._terms[en] = term
            if ga:
                self._terms_ga[ga] = term

        logger.info(f"Loaded {len(self._terms)} EN and {len(self._terms_ga)} GA terms")

    async def load_from_export(self) -> None:
        """Load terms from Téarma export."""
        terms = list(_load_tearma_terms())
        self._load_terms(terms)

    def find_term(
        self,
        text: str,
        language: str = "en",
    ) -> dict[str, Any] | None:
        """
        Find a term in the terminology database.

        Args:
            text: Term to look up
            language: Language of input (en, ga)

        Returns:
            Term entry or None
        """
        text_lower = text.lower().strip()

        if language == "ga":
            return self._terms_ga.get(text_lower)
        return self._terms.get(text_lower)

    def link_text(
        self,
        text: str,
        language: str = "en",
    ) -> list[dict[str, Any]]:
        """
        Find all terminology matches in a text.

        Args:
            text: Text to search for terms
            language: Language of text

        Returns:
            List of matched terms with positions
        """
        matches = []
        text_lower = text.lower()
        terms = self._terms if language == "en" else self._terms_ga

        for term_text, term_data in terms.items():
            if term_text in text_lower:
                # Find all occurrences
                start = 0
                while True:
                    pos = text_lower.find(term_text, start)
                    if pos == -1:
                        break
                    matches.append({
                        "term": term_text,
                        "position": pos,
                        "length": len(term_text),
                        "data": term_data,
                    })
                    start = pos + 1

        # Sort by position
        matches.sort(key=lambda m: m["position"])
        return matches

    def generate_glossary(
        self,
        text: str,
        language: str = "en",
    ) -> list[dict[str, str]]:
        """
        Generate a bilingual glossary for terms in text.

        Args:
            text: Text to analyze
            language: Language of text

        Returns:
            List of glossary entries (term_en, term_ga, definition)
        """
        matches = self.link_text(text, language)
        seen = set()
        glossary = []

        for match in matches:
            term = match["term"]
            if term in seen:
                continue
            seen.add(term)

            data = match["data"]
            glossary.append({
                "term_en": data.get("term_en", ""),
                "term_ga": data.get("term_ga", ""),
                "definition": data.get("definition_en", "") or data.get("definition_ga", ""),
                "domain": data.get("domain", ""),
            })

        return glossary


__all__ = [
    "TEARMA_API_BASE",
    "TEARMA_DOWNLOAD_URL",
    "TerminologyLinker",
    "_download_tearma_export",
    "_get_tearma_factory",
    "_load_tearma_terms",
    "_parse_tearma_tsv",
    "_search_tearma_api",
]
