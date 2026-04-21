"""
DLT source for loading existing scraped JSON as seed data.

Loads ncca.json, curriculum_oide.json, examinations.ie.json and normalizes
them into a consistent schema for augmentation via Firecrawl.
"""

import json
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import dlt

from ..constants.education_sources import EDUCATION_SITES


def _load_ncca_json(file_path: Path) -> Iterator[dict[str, Any]]:
    """Parse NCCA JSON structure and yield normalized pages."""
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    # Handle ncca_ie_url_patterns structure
    for pattern in data.get("ncca_ie_url_patterns", []):
        subjects = pattern.get("subject", [])
        stages = pattern.get("educational_stage", [])
        languages = pattern.get("language", [])

        # Create entries for each combination
        for subject in subjects if subjects else [{"value": None}]:
            for stage in stages if stages else [{"value": None}]:
                for lang in languages if languages else [{"value": None}]:
                    lang_value = lang.get("value", "")
                    yield {
                        "url_pattern": pattern.get("url_pattern"),
                        "description": pattern.get("description"),
                        "subject": subject.get("value"),
                        "educational_stage": stage.get("value"),
                        "language": "ga" if lang_value == "Irish" else "en",
                        "endpoint_type": pattern.get("endpoint_type"),
                        "source": "ncca",
                        "content_type": "url_pattern",
                        "loaded_at": datetime.now(UTC).isoformat(),
                    }


def _load_curriculum_online_json(file_path: Path) -> Iterator[dict[str, Any]]:
    """Parse Curriculum Online JSON and yield normalized pages."""
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    site_data = data.get("curriculumonline_ie", {})

    # Yield URL patterns
    for pattern in site_data.get("url_patterns", []):
        yield {
            "url_pattern": pattern.get("value"),
            "url_pattern_citation": pattern.get("value_citation"),
            "content_type": "url_pattern",
            "source": "curriculumonline",
            "loaded_at": datetime.now(UTC).isoformat(),
        }

    # Yield site structure
    site_structure = site_data.get("site_structure", {})
    for section in site_structure.get("sections", []):
        yield {
            "section_name": section.get("value"),
            "section_citation": section.get("value_citation"),
            "content_type": "site_section",
            "source": "curriculumonline",
            "loaded_at": datetime.now(UTC).isoformat(),
        }

    # Yield educational resources
    for resource in site_data.get("educational_resources", []):
        lang = resource.get("language", "English")
        yield {
            "url": resource.get("link"),
            "title": resource.get("title"),
            "language": "ga" if lang == "Irish" else "en",
            "educational_stage": resource.get("stage"),
            "content_type": "educational_resource",
            "source": "curriculumonline",
            "loaded_at": datetime.now(UTC).isoformat(),
        }

    # Yield PDF endpoints
    for pdf in site_data.get("direct_file_endpoints", []):
        yield {
            "url": pdf.get("value"),
            "url_citation": pdf.get("value_citation"),
            "content_type": "pdf",
            "source": "curriculumonline",
            "loaded_at": datetime.now(UTC).isoformat(),
        }


def _load_examinations_json(file_path: Path) -> Iterator[dict[str, Any]]:
    """Parse examinations.ie JSON and yield normalized pages."""
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    # Yield URL patterns
    for pattern in data.get("url_patterns", []):
        yield {
            "url_pattern": pattern.get("value"),
            "url_pattern_citation": pattern.get("value_citation"),
            "content_type": "url_pattern",
            "source": "examinations",
            "loaded_at": datetime.now(UTC).isoformat(),
        }

    # Yield site structure sections
    site_structure = data.get("site_structure", {})
    for section in site_structure.get("main_sections", []):
        yield {
            "section_name": section.get("value"),
            "section_citation": section.get("value_citation"),
            "content_type": "site_section",
            "source": "examinations",
            "loaded_at": datetime.now(UTC).isoformat(),
        }

    # Yield examiner reports (these are the key PDFs)
    for report in data.get("chief_examiner_reports", []):
        yield {
            "url": report.get("value"),
            "url_citation": report.get("value_citation"),
            "subject": report.get("subject"),
            "year": report.get("year"),
            "content_type": "examiner_report",
            "source": "examinations",
            "loaded_at": datetime.now(UTC).isoformat(),
        }


@dlt.source(name="education_seed_data")
def education_seed_source(
    source_name: str,
    seed_file_path: str | None = None,
):
    """
    DLT source for loading existing scraped JSON seed data.

    Args:
        source_name: One of "ncca", "curriculumonline", "examinations"
        seed_file_path: Optional override for seed file path

    Returns:
        DLT source with seed_metadata resource
    """
    if source_name not in EDUCATION_SITES:
        raise ValueError(f"Unknown source: {source_name}. Must be one of {list(EDUCATION_SITES.keys())}")

    site_config = EDUCATION_SITES[source_name]
    seed_path = Path(seed_file_path) if seed_file_path else site_config["seed_file"]

    @dlt.resource(
        name="seed_metadata",
        write_disposition="merge",
        primary_key=["source", "content_type", "url_pattern", "url"],
    )
    def seed_metadata():
        """URL patterns and metadata from seed JSON files."""
        if not seed_path.exists():
            return

        if source_name == "ncca":
            yield from _load_ncca_json(seed_path)
        elif source_name == "curriculumonline":
            yield from _load_curriculum_online_json(seed_path)
        elif source_name == "examinations":
            yield from _load_examinations_json(seed_path)

    return seed_metadata
