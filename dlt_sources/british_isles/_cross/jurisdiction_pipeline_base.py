"""British Isles jurisdiction pipeline base class.

Per the 2026-08-10-biep-v3-preflight-bug-fixes-v1 change.

Consolidates the ~30 LOC of duplicated boilerplate across the 4
BIEP v3 jurisdiction pipeline files (ireland + england + sct_wls_ni +
crown_dependencies) into this shared base class. Each pipeline file
becomes ~25 LOC of subclass definitions.
"""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, ClassVar

import dlt_sources

from dlt_sources.common.destinations_cianfhoghlaim import get_dlt_destination


VALID_JURISDICTIONS: tuple[str, ...] = (
    "ireland", "england", "scotland", "wales",
    "northern_ireland", "jersey", "guernsey", "isle_of_man",
)

VALID_STAGES: tuple[str, ...] = (
    "primary", "junior_cycle", "senior_cycle", "leaving_certificate",
    "gcse", "as_level", "a_level", "national_5", "higher",
    "advanced_higher", "foundation",
)


class JurisdictionPipelineBase:
    """Shared base for the 4 BIEP v3 jurisdiction pipelines.

    Provides:
    - VALID_JURISDICTIONS validation
    - destination factory + write_disposition + primary_key constants
    - build_pipeline() factory (canonical dlt.pipeline config)
    - subject_to_row() helper (canonical cohort row shape)

    Subclasses must:
    1. Set `STAGE` class attribute (e.g., "leaving_certificate", "gcse")
    2. Define a `build_pipeline_resource()` method that uses
       `self.subject_to_row()` to yield the per-jurisdiction cohorts.

    Example:
        class IrelandJurisdictionPipeline(JurisdictionPipelineBase):
            STAGE = "leaving_certificate"
            def build_pipeline_resource(self):
                for row in query_by_jurisdiction("ireland"):
                    yield self.subject_to_row(row, self.STAGE)
        ireland_jurisdiction_pipeline = IrelandJurisdictionPipeline("ireland")
    """

    VALID_JURISDICTIONS: ClassVar[tuple[str, ...]] = VALID_JURISDICTIONS
    VALID_STAGES: ClassVar[tuple[str, ...]] = VALID_STAGES
    WRITE_DISPOSITION: ClassVar[str] = "merge"
    PRIMARY_KEY: ClassVar[list[str]] = ["content_hash"]

    def __init__(
        self,
        jurisdiction: str,
        *,
        use_md: bool = True,
        valid_jurisdictions: tuple[str, ...] | None = None,
        valid_stages: tuple[str, ...] | None = None,
    ):
        valid_j = valid_jurisdictions or self.VALID_JURISDICTIONS
        valid_s = valid_stages or self.VALID_STAGES
        if jurisdiction not in valid_j:
            raise ValueError(
                f"jurisdiction={jurisdiction!r} not in {valid_j}"
            )
        self.jurisdiction = jurisdiction
        self.valid_jurisdictions = valid_j
        self.valid_stages = valid_s
        self.destination = get_dlt_destination(use_ducklake=use_md)

    @property
    def STAGE(self) -> str:
        """The education stage for this jurisdiction.

        Subclasses override this as a class attribute.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__}: set STAGE class attribute"
        )

    def subject_to_row(self, row: Any, stage: str | None = None) -> dict[str, Any]:
        """Convert one SubjectRegistryRow to the canonical cohort row dict.

        Used as the yield body of `build_pipeline_resource()`.
        """
        stage = stage or self.STAGE
        board = getattr(row, "board", None) or "none"
        return {
            "source_id": (
                f"british_isles.{self.jurisdiction}.education.{stage}."
                f"{board}.{row.subject_slug}"
            ),
            "country_code": self.jurisdiction,
            "jurisdiction": self.jurisdiction,
            "education_stage": stage,
            "exam_board": board,
            "subject": row.subject_slug,
            "qualification_level": getattr(row, "qualification_level", None) or "untiered",
            "language": row.language,
            "baml_function": row.baml_function,
            "concept": row.concept,
            "source_url": row.source_url,
            "display_name_en": row.display_name_en,
            "display_name_local": row.display_name_local,
            "last_verified": row.last_verified or datetime.now(UTC).isoformat()[:10],
            "ingested_at": datetime.now(UTC).isoformat(),
            "namespace": (
                f"cianfhoghlaim.education.{self.jurisdiction}.{stage}."
                f"{board}.{row.subject_slug}"
            ),
        }

    def build_pipeline(self, dataset_name: str | None = None) -> Any:
        """Build the canonical DLT pipeline for this jurisdiction."""
        dataset = dataset_name or f"{self.jurisdiction}_education"
        return dlt.pipeline(
            pipeline_name=f"{self.jurisdiction}_jurisdiction_pipeline",
            dataset_name=dataset,
            destination=self.destination,
        )

    def build_pipeline_resource(self):
        """Override this to yield the per-jurisdiction cohorts.

        Each yield MUST be a dict from `self.subject_to_row(row, stage)`.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__}: override build_pipeline_resource()"
        )

    def run(self, dataset_name: str | None = None) -> Any:
        """Convenience: build pipeline + run the resource + return load_info."""
        pipeline = self.build_pipeline(dataset_name=dataset_name)
        load_info = pipeline.run(self.build_pipeline_resource())
        return load_info


__all__ = [
    "JurisdictionPipelineBase",
    "VALID_JURISDICTIONS",
    "VALID_STAGES",
]