"""
Terminology Lookup Tools for Celtic Language Agents.

Provides access to official Celtic language terminology databases:
- Téarma.ie (Irish terminology)
- An Seotal (Scottish Gaelic education terms)
- Y Termiadur (Welsh terminology)
"""
from __future__ import annotations

import logging
from typing import Literal

import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# Pydantic models for terminology results
class TerminologyEntry(BaseModel):
    """A terminology database entry."""

    term_ga: str | None = Field(default=None, description="Irish term")
    term_en: str | None = Field(default=None, description="English term")
    term_gd: str | None = Field(default=None, description="Scottish Gaelic term")
    term_cy: str | None = Field(default=None, description="Welsh term")
    domain: str = Field(description="Subject domain")
    sub_domain: str | None = Field(default=None, description="Sub-domain")
    definition: str | None = Field(default=None, description="Definition")
    notes: str | None = Field(default=None, description="Usage notes")
    source: str = Field(description="Source database")
    url: str | None = Field(default=None, description="Reference URL")


class DomainInfo(BaseModel):
    """Information about a terminology domain."""

    name: str
    name_ga: str | None = None
    term_count: int
    sub_domains: list[str] = Field(default_factory=list)


# Téarma.ie domain mappings
TEARMA_DOMAINS = {
    "ríomhaireacht": "computing",
    "dlí": "law",
    "leigheas": "medicine",
    "oideachas": "education",
    "tíreolaíocht": "geography",
    "stair": "history",
    "eolaíocht": "science",
    "eacnamaíocht": "economics",
    "polaitíocht": "politics",
    "iriseoireacht": "journalism",
    "teanga": "linguistics",
    "litríocht": "literature",
    "ceol": "music",
    "ealaín": "art",
    "spórt": "sport",
}


async def lookup_tearma(
    term: str,
    source_language: Literal["ga", "en"] = "en",
    domain: str | None = None,
) -> list[TerminologyEntry]:
    """
    Look up terminology in Téarma.ie.

    Téarma.ie is the official Irish terminology database
    maintained by Foras na Gaeilge.

    Args:
        term: Term to look up (Irish or English)
        source_language: Language of the search term
        domain: Filter by subject domain

    Returns:
        List of TerminologyEntry matches
    """
    try:
        base_url = "https://www.tearma.ie/q/"
        search_url = f"{base_url}{term}/"

        async with httpx.AsyncClient() as client:
            response = await client.get(
                search_url,
                headers={"Accept-Language": "ga,en"},
                follow_redirects=True,
                timeout=10.0,
            )

            if response.status_code != 200:
                logger.warning(f"Téarma.ie returned status {response.status_code}")
                return []

            soup = BeautifulSoup(response.text, "html.parser")
            entries = []

            # Parse terminology entries
            results = soup.select(".result-item, .term-entry")

            for result in results:
                # Extract Irish term
                ga_elem = result.select_one(".term-ga, .ga")
                term_ga = ga_elem.get_text(strip=True) if ga_elem else None

                # Extract English term
                en_elem = result.select_one(".term-en, .en")
                term_en = en_elem.get_text(strip=True) if en_elem else None

                # Extract domain
                domain_elem = result.select_one(".domain, .ábhar")
                entry_domain = domain_elem.get_text(strip=True) if domain_elem else "general"

                # Filter by domain if specified
                if domain and domain.lower() not in entry_domain.lower():
                    continue

                # Extract definition/notes
                def_elem = result.select_one(".definition, .sainmhíniú")
                definition = def_elem.get_text(strip=True) if def_elem else None

                notes_elem = result.select_one(".notes, .nótaí")
                notes = notes_elem.get_text(strip=True) if notes_elem else None

                # Get URL
                link = result.select_one("a[href*='/term/']")
                url = f"https://www.tearma.ie{link['href']}" if link else None

                entries.append(
                    TerminologyEntry(
                        term_ga=term_ga,
                        term_en=term_en,
                        domain=entry_domain,
                        definition=definition,
                        notes=notes,
                        source="tearma.ie",
                        url=url,
                    )
                )

            logger.info(f"Found {len(entries)} Téarma.ie entries for '{term}'")
            return entries

    except Exception as e:
        logger.error(f"Téarma.ie lookup error: {e}")
        return []


async def search_terminology(
    query: str,
    languages: list[str] | None = None,
    domains: list[str] | None = None,
    limit: int = 20,
) -> list[TerminologyEntry]:
    """
    Search across multiple terminology databases.

    Searches Téarma.ie and other available terminology
    resources for matching terms.

    Args:
        query: Search query
        languages: Filter by languages (ga, gd, cy)
        domains: Filter by subject domains
        limit: Maximum results

    Returns:
        List of TerminologyEntry from all sources
    """
    results = []

    # Default to Irish if no languages specified
    if not languages:
        languages = ["ga"]

    # Search Téarma.ie for Irish
    if "ga" in languages:
        tearma_results = await lookup_tearma(query)
        results.extend(tearma_results)

    # Filter by domains if specified
    if domains:
        results = [
            r
            for r in results
            if any(d.lower() in r.domain.lower() for d in domains)
        ]

    # Sort by relevance (exact matches first)
    query_lower = query.lower()
    results.sort(
        key=lambda r: (
            0
            if (r.term_ga and r.term_ga.lower() == query_lower)
            or (r.term_en and r.term_en.lower() == query_lower)
            else 1
        )
    )

    return results[:limit]


async def get_domain_terms(
    domain: str,
    language: Literal["ga", "en"] = "ga",
    limit: int = 50,
) -> list[TerminologyEntry]:
    """
    Get all terms in a specific domain.

    Retrieves terminology entries categorized under
    a subject domain like "computing", "law", "medicine".

    Args:
        domain: Subject domain name
        language: Display language
        limit: Maximum terms to return

    Returns:
        List of TerminologyEntry in the domain
    """
    try:
        # Map English domain to Irish if needed
        domain_ga = None
        for ga, en in TEARMA_DOMAINS.items():
            if en.lower() == domain.lower() or ga.lower() == domain.lower():
                domain_ga = ga
                break

        if not domain_ga:
            domain_ga = domain

        # Fetch domain page from Téarma.ie
        url = f"https://www.tearma.ie/ábhar/{domain_ga}/"

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers={"Accept-Language": "ga,en"},
                follow_redirects=True,
                timeout=15.0,
            )

            if response.status_code != 200:
                logger.warning(f"Domain page returned status {response.status_code}")
                return []

            soup = BeautifulSoup(response.text, "html.parser")
            entries = []

            # Parse term list
            term_items = soup.select(".term-list-item, .term-entry")

            for item in term_items[:limit]:
                ga_elem = item.select_one(".term-ga, .ga")
                en_elem = item.select_one(".term-en, .en")

                if ga_elem or en_elem:
                    entries.append(
                        TerminologyEntry(
                            term_ga=ga_elem.get_text(strip=True) if ga_elem else None,
                            term_en=en_elem.get_text(strip=True) if en_elem else None,
                            domain=domain,
                            source="tearma.ie",
                        )
                    )

            return entries

    except Exception as e:
        logger.error(f"Domain terms fetch error: {e}")
        return []


async def get_available_domains() -> list[DomainInfo]:
    """
    Get list of available terminology domains.

    Returns information about all subject domains
    available in the terminology databases.
    """
    domains = []

    for ga_name, en_name in TEARMA_DOMAINS.items():
        domains.append(
            DomainInfo(
                name=en_name,
                name_ga=ga_name,
                term_count=0,  # Would need API call to get counts
                sub_domains=[],
            )
        )

    return domains


async def compare_terminology(
    term_en: str,
    languages: list[str] | None = None,
) -> dict:
    """
    Compare terminology across Celtic languages.

    Finds equivalent terms for an English term in
    Irish, Scottish Gaelic, and Welsh.

    Args:
        term_en: English term to look up
        languages: Languages to find equivalents for

    Returns:
        Dictionary mapping language codes to terms
    """
    if languages is None:
        languages = ["ga", "gd", "cy"]
    result = {"en": term_en}

    # Look up Irish from Téarma.ie
    if "ga" in languages:
        tearma_results = await lookup_tearma(term_en, source_language="en")
        if tearma_results:
            result["ga"] = tearma_results[0].term_ga

    # For other languages, we'd need additional sources
    # Placeholder for Scottish Gaelic and Welsh
    if "gd" in languages:
        # Would query An Seotal or similar
        result["gd"] = None

    if "cy" in languages:
        # Would query Y Termiadur
        result["cy"] = None

    return result
