"""
DLT source for Irish-English parallel corpus ingestion.

Sources:
- Gaois TMX: 130.5M words of EU/legal translations
- Téarma.ie: 40+ categories of terminology
- Logainm.ie: 100K+ bilingual placenames
- NCCA Curriculum: Bilingual specifications

Based on research from:
- taighde_bonneagar/03-bilingual-dataset-creation/parallel-corpus-sources.md
- taighde_teanga/irish_bilingual_dataset_research.md
"""

from __future__ import annotations

import hashlib
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

import dlt
from dlt.sources import DltResource

from sruth.shared.http import logainm_client, tearma_client

# Gaois API endpoints
GAOIS_BASE_URL = "https://www.gaois.ie"
TEARMA_API_URL = "https://www.tearma.ie/api/1.0"
LOGAINM_API_URL = "https://www.logainm.ie/api/v1.0"
DUCHAS_API_URL = "https://www.duchas.ie/api/v0.6"


def _get_tearma_factory():
    """Get HTTP client factory for Téarma.ie."""
    return tearma_client()


def _get_logainm_factory():
    """Get HTTP client factory for Logainm.ie."""
    return logainm_client()


@dlt.source(name="parallel_corpus")
def parallel_corpus_source(
    sources: list[str] | None = None,
    max_records: int = 10000,
    batch_size: int = 100,
) -> Iterator[DltResource]:
    """
    DLT source for Irish-English parallel corpus.

    Args:
        sources: List of source names to include. Options:
                 ["gaois_tmx", "tearma", "logainm", "curriculum"]
                 Default: all sources
        max_records: Maximum records per source
        batch_size: Batch size for API calls (min 100)

    Yields:
        DltResource for each parallel corpus source
    """
    if sources is None:
        sources = ["gaois_tmx", "tearma", "logainm", "curriculum"]

    batch_size = max(batch_size, 100)  # Enforce minimum batch size

    if "gaois_tmx" in sources:
        yield gaois_tmx_resource(max_records=max_records)

    if "tearma" in sources:
        yield tearma_resource(max_records=max_records, batch_size=batch_size)

    if "logainm" in sources:
        yield logainm_resource(max_records=max_records, batch_size=batch_size)

    if "curriculum" in sources:
        yield curriculum_bilingual_resource(max_records=max_records)


@dlt.resource(
    name="gaois_tmx",
    write_disposition="merge",
    primary_key="pair_id",
)
def gaois_tmx_resource(
    tmx_path: str | None = None,
    max_records: int = 10000,
) -> Iterator[dict[str, Any]]:
    """
    Load parallel texts from Gaois TMX files.

    The Gaois corpus contains 130.5M words of EU and legal translations.
    TMX files should be downloaded from https://www.gaois.ie/crp/

    Args:
        tmx_path: Path to TMX file or directory
        max_records: Maximum records to yield

    Yields:
        Dictionary with parallel text pairs
    """
    if tmx_path is None:
        # Default path for Gaois TMX files
        tmx_path = os.getenv(
            "GAOIS_TMX_PATH",
            str(Path.home() / ".cache/cianfhoghlaim/gaois_tmx"),
        )

    tmx_path = Path(tmx_path)

    if not tmx_path.exists():
        yield {
            "pair_id": "gaois_tmx_not_found",
            "source": "gaois_tmx",
            "status": "tmx_path_not_found",
            "message": f"TMX path not found: {tmx_path}",
            "en": "",
            "ga": "",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return

    # Find TMX files
    if tmx_path.is_file():
        tmx_files = [tmx_path]
    else:
        tmx_files = list(tmx_path.glob("*.tmx"))

    if not tmx_files:
        yield {
            "pair_id": "gaois_tmx_no_files",
            "source": "gaois_tmx",
            "status": "no_tmx_files",
            "message": f"No TMX files found in: {tmx_path}",
            "en": "",
            "ga": "",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return

    count = 0
    for tmx_file in tmx_files:
        if count >= max_records:
            break

        for pair in _parse_tmx_file(tmx_file):
            if count >= max_records:
                break

            yield {
                "pair_id": pair["pair_id"],
                "source": "gaois_tmx",
                "source_file": tmx_file.name,
                "en": pair["en"],
                "ga": pair["ga"],
                "domain": pair.get("domain", "general"),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "status": "success",
            }
            count += 1


@dlt.resource(
    name="tearma",
    write_disposition="merge",
    primary_key="term_id",
)
def tearma_resource(
    categories: list[str] | None = None,
    max_records: int = 10000,
    batch_size: int = 100,
) -> Iterator[dict[str, Any]]:
    """
    Load terminology from Téarma.ie API.

    Téarma.ie contains 40+ categories of Irish-English terminology.

    Args:
        categories: List of category codes to fetch
        max_records: Maximum records to yield
        batch_size: Batch size for API calls

    Yields:
        Dictionary with terminology pairs
    """
    # Default educational categories
    if categories is None:
        categories = [
            "ED",  # Education
            "SC",  # Science
            "MA",  # Mathematics
            "HI",  # History
            "GE",  # Geography
            "AR",  # Arts
            "LA",  # Language/Linguistics
            "IT",  # Information Technology
        ]

    api_key = os.getenv("TEARMA_API_KEY", "")
    factory = _get_tearma_factory()

    count = 0
    with factory.create_client() as client:
        for category in categories:
            if count >= max_records:
                break

            try:
                # Téarma API endpoint - use relative path
                response = client.get(
                    "/api/1.0/terms",
                    params={
                        "cat": category,
                        "lang": "en,ga",
                        "limit": min(batch_size, max_records - count),
                    },
                    headers={"X-API-Key": api_key} if api_key else {},
                )
                response.raise_for_status()
                data = response.json()

                for term in data.get("terms", []):
                    if count >= max_records:
                        break

                    en_term = term.get("en", {}).get("term", "")
                    ga_term = term.get("ga", {}).get("term", "")

                    if not en_term or not ga_term:
                        continue

                    term_id = f"tearma_{category}_{hashlib.sha256((en_term + ga_term).encode()).hexdigest()[:12]}"

                    yield {
                        "term_id": term_id,
                        "source": "tearma",
                        "category": category,
                        "en": en_term,
                        "ga": ga_term,
                        "en_definition": term.get("en", {}).get("definition", ""),
                        "ga_definition": term.get("ga", {}).get("definition", ""),
                        "domain": term.get("domain", category),
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "status": "success",
                    }
                    count += 1

            except Exception as e:
                yield {
                    "term_id": f"tearma_{category}_error",
                    "source": "tearma",
                    "category": category,
                    "status": "api_error",
                    "error": str(e),
                    "en": "",
                    "ga": "",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }


@dlt.resource(
    name="logainm",
    write_disposition="merge",
    primary_key="place_id",
)
def logainm_resource(
    counties: list[str] | None = None,
    max_records: int = 10000,
    batch_size: int = 100,
) -> Iterator[dict[str, Any]]:
    """
    Load placenames from Logainm.ie API.

    Logainm contains 100K+ bilingual Irish placenames.

    Args:
        counties: List of county IDs to fetch
        max_records: Maximum records to yield
        batch_size: Batch size for API calls

    Yields:
        Dictionary with placename pairs
    """
    # All 32 counties if not specified
    if counties is None:
        # Connacht
        counties = ["galway", "mayo", "sligo", "leitrim", "roscommon"]
        # Add more as needed

    factory = _get_logainm_factory()

    count = 0
    with factory.create_client() as client:
        for county in counties:
            if count >= max_records:
                break

            offset = 0
            while count < max_records:
                try:
                    response = client.get(
                        "/api/v1.0/places",
                        params={
                            "county": county,
                            "offset": offset,
                            "limit": min(batch_size, max_records - count),
                        },
                    )
                    response.raise_for_status()
                    data = response.json()

                    places = data.get("places", [])
                    if not places:
                        break

                    for place in places:
                        if count >= max_records:
                            break

                        en_name = place.get("nameEnglish", "")
                        ga_name = place.get("nameIrish", "")

                        if not en_name or not ga_name:
                            continue

                        yield {
                            "place_id": f"logainm_{place.get('id', count)}",
                            "source": "logainm",
                            "county": county,
                            "en": en_name,
                            "ga": ga_name,
                            "place_type": place.get("type", ""),
                            "coordinates": place.get("coordinates", {}),
                            "created_at": datetime.now(timezone.utc).isoformat(),
                            "status": "success",
                        }
                        count += 1

                    offset += batch_size

                except Exception as e:
                    yield {
                        "place_id": f"logainm_{county}_error",
                        "source": "logainm",
                        "county": county,
                        "status": "api_error",
                        "error": str(e),
                        "en": "",
                        "ga": "",
                        "created_at": datetime.now(timezone.utc).isoformat(),
                    }
                    break


@dlt.resource(
    name="curriculum_bilingual",
    write_disposition="merge",
    primary_key="segment_id",
)
def curriculum_bilingual_resource(
    stages: list[str] | None = None,
    max_records: int = 10000,
) -> Iterator[dict[str, Any]]:
    """
    Load bilingual curriculum content from curriculumonline.ie.

    Aligns English and Irish versions of curriculum specifications.

    Args:
        stages: Educational stages to include
        max_records: Maximum records to yield

    Yields:
        Dictionary with aligned curriculum segments
    """
    try:
        from firecrawl import FirecrawlApp
    except ImportError:
        yield {
            "segment_id": "curriculum_firecrawl_missing",
            "source": "curriculum",
            "status": "firecrawl_not_installed",
            "en": "",
            "ga": "",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return

    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        yield {
            "segment_id": "curriculum_no_api_key",
            "source": "curriculum",
            "status": "no_api_key",
            "en": "",
            "ga": "",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return

    if stages is None:
        stages = ["primary", "junior_cycle", "senior_cycle"]

    app = FirecrawlApp(api_key=api_key)

    # Stage to URL path mapping
    stage_paths = {
        "primary": "/primary/",
        "junior_cycle": "/junior-cycle/",
        "senior_cycle": "/senior-cycle/",
    }

    count = 0
    for stage in stages:
        if count >= max_records:
            break

        stage_path = stage_paths.get(stage, f"/{stage}/")

        # Crawl English version
        try:
            en_result = app.crawl_url(
                f"https://www.curriculumonline.ie{stage_path}",
                params={
                    "limit": min(50, max_records - count),
                    "maxDepth": 2,
                    "scrapeOptions": {"formats": ["markdown"]},
                },
                poll_interval=5,
            )
        except Exception as e:
            yield {
                "segment_id": f"curriculum_{stage}_en_error",
                "source": "curriculum",
                "stage": stage,
                "language": "en",
                "status": "crawl_error",
                "error": str(e),
                "en": "",
                "ga": "",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            continue

        # Crawl Irish version
        try:
            ga_result = app.crawl_url(
                f"https://www.curriculumonline.ie/ga-ie{stage_path}",
                params={
                    "limit": min(50, max_records - count),
                    "maxDepth": 2,
                    "scrapeOptions": {"formats": ["markdown"]},
                },
                poll_interval=5,
            )
        except Exception as e:
            yield {
                "segment_id": f"curriculum_{stage}_ga_error",
                "source": "curriculum",
                "stage": stage,
                "language": "ga",
                "status": "crawl_error",
                "error": str(e),
                "en": "",
                "ga": "",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            continue

        # Build URL to content mapping
        en_pages = {
            _normalize_curriculum_url(p.get("metadata", {}).get("sourceURL", "")): p
            for p in en_result.get("data", [])
        }

        ga_pages = {
            _normalize_curriculum_url(p.get("metadata", {}).get("sourceURL", "")): p
            for p in ga_result.get("data", [])
        }

        # Align pages by normalized URL
        for url_key, en_page in en_pages.items():
            if count >= max_records:
                break

            ga_page = ga_pages.get(url_key)
            if not ga_page:
                continue

            en_content = en_page.get("markdown", "")
            ga_content = ga_page.get("markdown", "")

            if not en_content or not ga_content:
                continue

            # Extract paragraphs for alignment
            en_paragraphs = _extract_paragraphs(en_content)
            ga_paragraphs = _extract_paragraphs(ga_content)

            # Simple paragraph alignment by position
            for i, (en_para, ga_para) in enumerate(zip(en_paragraphs, ga_paragraphs)):
                if count >= max_records:
                    break

                if len(en_para) < 20 or len(ga_para) < 20:
                    continue

                segment_id = f"curriculum_{stage}_{hashlib.sha256((url_key + str(i)).encode()).hexdigest()[:12]}"

                yield {
                    "segment_id": segment_id,
                    "source": "curriculum",
                    "stage": stage,
                    "url_key": url_key,
                    "paragraph_index": i,
                    "en": en_para,
                    "ga": ga_para,
                    "en_url": en_page.get("metadata", {}).get("sourceURL", ""),
                    "ga_url": ga_page.get("metadata", {}).get("sourceURL", ""),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "status": "success",
                }
                count += 1


# Helper functions

def _parse_tmx_file(tmx_path: Path) -> Iterator[dict[str, Any]]:
    """Parse a TMX file and yield translation units."""
    try:
        tree = ET.parse(tmx_path)
        root = tree.getroot()

        for tu in root.iter("tu"):
            en_text = ""
            ga_text = ""
            domain = tu.get("tuid", "").split("_")[0] if tu.get("tuid") else "general"

            for tuv in tu.findall("tuv"):
                lang = tuv.get("{http://www.w3.org/XML/1998/namespace}lang", "")
                seg = tuv.find("seg")
                text = seg.text if seg is not None and seg.text else ""

                if lang.lower().startswith("en"):
                    en_text = text.strip()
                elif lang.lower().startswith("ga") or lang.lower().startswith("ie"):
                    ga_text = text.strip()

            if en_text and ga_text:
                pair_id = hashlib.sha256((en_text + ga_text).encode()).hexdigest()[:16]
                yield {
                    "pair_id": pair_id,
                    "en": en_text,
                    "ga": ga_text,
                    "domain": domain,
                }

    except ET.ParseError as e:
        # Log error but don't crash
        pass


def _normalize_curriculum_url(url: str) -> str:
    """Normalize curriculum URL to enable matching between en/ga versions."""
    if not url:
        return ""

    # Remove language prefix
    url = re.sub(r"/ga-ie/", "/", url)

    # Remove query string and fragment
    url = re.sub(r"[?#].*$", "", url)

    # Normalize trailing slashes
    url = url.rstrip("/")

    # Extract path after domain
    if "curriculumonline.ie" in url:
        match = re.search(r"curriculumonline\.ie(/.+)$", url)
        if match:
            return match.group(1)

    return url


def _extract_paragraphs(markdown: str) -> list[str]:
    """Extract paragraphs from markdown content."""
    # Split by double newlines
    paragraphs = re.split(r"\n\n+", markdown)

    # Clean and filter
    cleaned = []
    for p in paragraphs:
        # Remove markdown headers
        p = re.sub(r"^#+\s*", "", p.strip())
        # Remove markdown links
        p = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", p)
        # Remove markdown formatting
        p = re.sub(r"[*_~`]+", "", p)

        if len(p) >= 20:  # Minimum length
            cleaned.append(p.strip())

    return cleaned
