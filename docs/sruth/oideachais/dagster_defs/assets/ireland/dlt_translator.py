"""Custom DLT translator for Ireland curriculum assets."""

from __future__ import annotations

from typing import Any

from dagster import AssetKey
from dagster_dlt import DagsterDltTranslator


class CurriculumDltTranslator(DagsterDltTranslator):
    """
    Maps DLT resources to Ireland curriculum asset keys.

    Asset key structure: ireland/curriculum/{cycle}/{subject}/{language}/{resource}

    Example:
        ireland/curriculum/junior_cycle/mathematics/en/pages
        ireland/curriculum/junior_cycle/mathematics/en/pdfs
        ireland/curriculum/junior_cycle/mathematics/en/provenance
    """

    def __init__(self, cycle: str, subject: str, language: str):
        self.cycle = cycle
        self.subject = subject
        self.language = language

    def get_asset_key(self, resource: Any) -> AssetKey:
        """
        Generate asset key: ireland/curriculum/{cycle}/{subject}/{language}/{resource_type}

        Maps DLT resource names:
        - curriculum_pages -> pages
        - curriculum_pdfs -> pdfs
        - source_provenance -> provenance
        """
        resource_name = getattr(resource, "name", str(resource))
        resource_type = resource_name.replace("curriculum_", "").replace("source_", "")
        return AssetKey(
            ["ireland", "curriculum", self.cycle, self.subject, self.language, resource_type]
        )

    def get_deps_asset_keys(self, resource: Any) -> list[AssetKey]:
        """
        Define dependencies between resources.

        pdfs and provenance depend on pages (PDF URLs extracted from crawled pages).
        """
        resource_name = getattr(resource, "name", str(resource))
        if "pdfs" in resource_name:
            return [
                AssetKey(
                    ["ireland", "curriculum", self.cycle, self.subject, self.language, "pages"]
                )
            ]
        return []

    def get_group_name(self, resource: Any) -> str:
        """Group assets by cycle: curriculum_junior_cycle, curriculum_senior_cycle, etc."""
        return f"curriculum_{self.cycle}"

    def get_tags(self, resource: Any) -> dict[str, str]:
        """Add metadata tags for filtering and organization."""
        return {
            "cycle": self.cycle,
            "subject": self.subject,
            "language": self.language,
            "pipeline": "ireland_curriculum",
        }

    def get_description(self, resource: Any) -> str | None:
        """Generate descriptive text for the asset."""
        resource_name = getattr(resource, "name", str(resource))
        resource_type = resource_name.replace("curriculum_", "").replace("source_", "")

        descriptions = {
            "pages": f"Crawled curriculum pages for {self.subject} ({self.cycle}, {self.language})",
            "pdfs": f"Discovered PDF URLs for {self.subject} ({self.cycle}, {self.language})",
            "provenance": f"Cross-source deduplication tracking for {self.subject} ({self.cycle}, {self.language})",
        }
        return descriptions.get(resource_type)
