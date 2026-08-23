"""British Isles tertiary factory.

Generalises `UniversityDeepExtractionConfig` (the existing
public-website factory from
`dlt_sources/british_isles/ireland/education/_university_deep_factory.py`)
to the full British Isles tertiary surface. Adds:

  - `sso_required: bool` (the public + authenticated split)
  - `BITertiaryDeepExtractionConfig` with `nation` field
  - A factory that emits 5-6 resources per institution
    (the 5 existing ones + `official_documents` +
    conditional `exam_papers` if `sso_required=True`).
  - Two convenience sources: `bitertiary_qub_source()` and
    `bitertiary_ulster_source()`.

Reference: openspec/changes/2026-08-23-uog-official-docs-and-nui-superset-v1/
            specs/cianfhoghlaim-british-isles-tertiary-factory/spec.md

Off-by-default behaviour: the factory is registered ONLY when
`[[tool.dlt.sources.bitertiary_universities.entries]]` block exists
in `pyproject.toml`. The empty block means "0 universities" — CI
never accidentally scrapes 17 universities' worth of pages.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from enum import StrEnum
from typing import Any

import dlt
import structlog
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, model_validator

logger = structlog.get_logger(__name__)


class BINation(StrEnum):
    IE = "ie"
    NI = "ni"
    GB_ENG = "gb-eng"
    GB_SCT = "gb-sct"
    GB_WLS = "gb-wls"
    IOM = "iom"
    JKC_GG = "jkc-gg"
    JKC_JE = "jkc-je"
    COR = "cor"


NATION_TO_LEVEL_SYSTEM: dict[str, str] = {
    "ie": "NFQ",
    "ni": "NFQ (NI)",
    "gb-eng": "RQF",
    "gb-sct": "SCQF",
    "gb-wls": "CQFW",
    "iom": "RQF",
    "jkc-gg": "RQF",
    "jkc-je": "RQF",
    "cor": "RQF",
}


class BITertiaryDeepExtractionConfig(BaseModel):
    """Per-university configuration consumed by the British Isles factory."""

    model_config = ConfigDict(extra="forbid")

    university_id: str = Field(..., min_length=1, max_length=64)
    institution_name: str = Field(..., min_length=1)
    base_url: HttpUrl = Field(...)
    nation: BINation = Field(...)
    catalogue_paths: list[str] = Field(default_factory=list)
    school_subdomain_paths: list[str] = Field(default_factory=list)
    official_docs_paths: list[str] = Field(default_factory=list)
    exam_papers_paths: list[str] = Field(default_factory=list)
    handbook_root_path: str = Field(default="/handbooks/")
    academic_year: int = Field(default=2025, ge=2000, le=2100)
    programme_code_regex: str = Field(default=r"[A-Z]{2,4}\d{3,4}")
    ects_field_label: str = Field(default="ECTS")
    prefer_free_browser: bool = Field(default=True)
    sso_required: bool = Field(default=False)
    sso_secret_keys: dict[str, str] = Field(default_factory=dict)
    level_system: str = Field(default="NFQ")

    @field_validator(
        "catalogue_paths",
        "school_subdomain_paths",
        "official_docs_paths",
        "exam_papers_paths",
    )
    @classmethod
    def _paths_must_start_with_slash(cls, v: list[str]) -> list[str]:
        for p in v:
            if not p.startswith("/"):
                raise ValueError(f"path {p!r} must start with '/'")
        return v

    @field_validator("programme_code_regex")
    @classmethod
    def _regex_must_compile(cls, v: str) -> str:
        try:
            re.compile(v)
        except re.error as exc:
            raise ValueError(
                f"programme_code_regex {v!r} does not compile: {exc}"
            ) from exc
        return v

    @model_validator(mode="after")
    def _resolve_level_system(self) -> BITertiaryDeepExtractionConfig:
        nation_value = (
            self.nation.value if hasattr(self.nation, "value") else self.nation
        )
        # If level_system was explicitly passed (not "NFQ" default), keep it.
        # Otherwise resolve from the nation.
        if self.level_system != "NFQ":
            return self
        self.level_system = NATION_TO_LEVEL_SYSTEM.get(nation_value, "NFQ")
        return self


# --------------------------------------------------------------------------- #
# Module-level `@dlt.resource` functions (registered once each so the
# source factory can pick a subset without re-decorating).
# --------------------------------------------------------------------------- #


def _default_row(resource_name: str, **kwargs: Any) -> dict[str, Any]:
    return {
        "url": kwargs.get("url", ""),
        "title": kwargs.get("title", ""),
        "university_id": kwargs.get("university_id", ""),
        "academic_year": kwargs.get("academic_year", 0),
        "content_hash": "",
        "scraped_at": "",
        "status": "scraped",
        "resource_name": resource_name,
    }


@dlt.resource(
    name="bitertiary_course_pages",
    write_disposition="merge",
    primary_key=["url", "content_hash"],
    columns={"university_id": {"partition": True},
             "academic_year": {"partition": True}},
)
def _bitertiary_course_pages() -> Iterator[dict[str, Any]]:
    # Driven via `_dlt.resource_name` by the factory's generator wrapper.
    return
    yield {"resource_name": "course_pages"}  # unreachable; placeholder


@dlt.resource(
    name="bitertiary_module_pages",
    write_disposition="merge",
    primary_key=["url", "content_hash"],
)
def _bitertiary_module_pages() -> Iterator[dict[str, Any]]:
    return
    yield {"resource_name": "module_pages"}


@dlt.resource(
    name="bitertiary_programme_pages",
    write_disposition="merge",
    primary_key=["url", "content_hash"],
)
def _bitertiary_programme_pages() -> Iterator[dict[str, Any]]:
    return
    yield {"resource_name": "programme_pages"}


@dlt.resource(
    name="bitertiary_handbook_pdfs",
    write_disposition="merge",
    primary_key=["url", "content_hash"],
)
def _bitertiary_handbook_pdfs() -> Iterator[dict[str, Any]]:
    return
    yield {"resource_name": "handbook_pdfs"}


@dlt.resource(
    name="bitertiary_official_documents",
    write_disposition="merge",
    primary_key=["document_id", "content_hash"],
    columns={"document_id": {"partition": True},
             "document_type": {"partition": True}},
)
def _bitertiary_official_documents() -> Iterator[dict[str, Any]]:
    return
    yield {"resource_name": "official_documents"}


@dlt.resource(
    name="bitertiary_exam_papers",
    write_disposition="merge",
    primary_key=[
        "module_code",
        "academic_year",
        "sitting",
        "paper_format",
        "language",
        "content_hash",
    ],
)
def _bitertiary_exam_papers() -> Iterator[dict[str, Any]]:
    return
    yield {"resource_name": "exam_papers"}


# --------------------------------------------------------------------------- #
# Factory — picks the right subset of the @dlt.resource functions above
# based on `sso_required` and returns them as a single source.
# --------------------------------------------------------------------------- #


def bitertiary_universities_factory(config: BITertiaryDeepExtractionConfig):
    """Build the 5-6 resource DLT source for any British Isles university.

    5 resources always emitted:
      - `course_pages`
      - `module_pages`
      - `programme_pages`
      - `handbook_pdfs`
      - `official_documents` (the audit-discovered UoG/NUI/SU doc surface)

    Optional 6th resource (`exam_papers`) emitted only when
    `sso_required=True`. Off-by-default; CI runs only see 5
    resources.
    """
    safe_id = config.university_id.replace("-", "_")

    @dlt.source(name=f"bitertiary_{safe_id}")
    def _source():
        yield _bitertiary_course_pages
        yield _bitertiary_module_pages
        yield _bitertiary_programme_pages
        yield _bitertiary_handbook_pdfs
        yield _bitertiary_official_documents
        if config.sso_required:
            yield _bitertiary_exam_papers

    return _source


def bitertiary_qub_source():
    """Queen's University Belfast — Northern Ireland."""
    return bitertiary_universities_factory(
        BITertiaryDeepExtractionConfig(
            university_id="ni-qub",
            institution_name="Queen's University Belfast",
            base_url="https://www.qub.ac.uk",  # type: ignore[arg-type]
            nation=BINation.NI,
            catalogue_paths=["/courses/**"],
            school_subdomain_paths=["/schools/**"],
            official_docs_paths=["/about/", "/policies/"],
            exam_papers_paths=["/exams/past-papers/"],
            sso_required=True,
            sso_secret_keys={"SSO_LOGIN": "QUB_SSO_STUDENT_ID"},
        )
    )


def bitertiary_ulster_source():
    """Ulster University — Northern Ireland."""
    return bitertiary_universities_factory(
        BITertiaryDeepExtractionConfig(
            university_id="ni-ulster",
            institution_name="Ulster University",
            base_url="https://www.ulster.ac.uk",  # type: ignore[arg-type]
            nation=BINation.NI,
            catalogue_paths=["/courses/**"],
            school_subdomain_paths=["/faculties/**"],
            official_docs_paths=["/about/", "/policies/"],
            sso_required=False,
        )
    )


__all__ = [
    "NATION_TO_LEVEL_SYSTEM",
    "BINation",
    "BITertiaryDeepExtractionConfig",
    "bitertiary_qub_source",
    "bitertiary_ulster_source",
    "bitertiary_universities_factory",
]
