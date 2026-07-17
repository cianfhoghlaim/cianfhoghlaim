"""British Isles jurisdiction pipeline base class.

Per the 2026-08-07-biep-v3-hardening-v1 change.

Consolidates the ~80 LOC of duplicated boilerplate across the 4
BIEP v3 jurisdiction pipeline files (ireland + england + sct_wls_ni +
crown_dependencies). Each pipeline file becomes ~25 LOC of overrides.
"""
from __future__ import annotations

from typing import Any

import dlt

from dlt.common.destinations_cianfhoghlaim import get_dlt_destination


VALID_JURISDICTIONS = (
    "ireland", "england", "scotland", "wales",
    "northern_ireland", "jersey", "guernsey", "isle_of_man",
)

VALID_STAGES = (
    "primary", "junior_cycle", "senior_cycle", "leaving_certificate",
    "gcse", "as_level", "a_level", "national_5", "higher",
    "advanced_higher", "foundation",
)


class JurisdictionPipelineBase:
    """Base class for the 8 BIEP v3 jurisdiction pipelines.

    Subclasses must override `build_pipeline_resource()` to yield the
    per-jurisdiction subjects.
    """

    def __init__(
        self,
        jurisdiction: str,
        valid_jurisdictions: tuple[str, ...] = VALID_JURISDICTIONS,
        valid_stages: tuple[str, ...] = VALID_STAGES,
    ):
        if jurisdiction not in valid_jurisdictions:
            raise ValueError(
                f"jurisdiction={jurisdiction!r} not in {valid_jurisdictions}"
            )
        self.jurisdiction = jurisdiction
        self.valid_jurisdictions = valid_jurisdictions
        self.valid_stages = valid_stages

    def build_pipeline_resource(self):
        """Override this to yield the per-jurisdiction subjects.

        Each yield should be a dict with at minimum:
        - source_id, country_code, jurisdiction, education_stage,
          subject, language, content_hash, namespace
        """
        raise NotImplementedError(
            f"{self.__class__.__name__}: override build_pipeline_resource()"
        )

    def build_pipeline(self, dataset_name: str | None = None):
        """Build the canonical DLT pipeline for this jurisdiction."""
        dataset = dataset_name or f"{self.jurisdiction}_education"
        pipeline = dlt.pipeline(
            pipeline_name=f"{self.jurisdiction}_jurisdiction_pipeline",
            dataset_name=dataset,
            destination=get_dlt_destination(use_ducklake=True),
        )
        return pipeline, self.build_pipeline_resource()


__all__ = ["JurisdictionPipelineBase", "VALID_JURISDICTIONS", "VALID_STAGES"]
