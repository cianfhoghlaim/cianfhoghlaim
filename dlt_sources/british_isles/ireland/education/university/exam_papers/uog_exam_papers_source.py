"""UoG Exam Papers DLT source.

Wraps `sruth_browser.tools.uog_exam_scraper.UoGExamScraper` and yields
five `@dlt.resource` rows for the authenticated University of Galway
exam-paper corpus:

  1. `exam_papers`              — past papers (PDF / written-online)
  2. `marking_schemes`          — marking schemes
  3. `model_solutions`          — worked solutions
  4. `supplementary_papers`     — autumn / spring supplemental sittings
  5. `all_exam_materials`       — the union of the above four, prefixed
                                  with `material_type` so the marimo
                                  notebook can filter

All resources use `write_disposition="merge"` and a multi-column
primary key that includes `content_hash` so re-runs are idempotent.

Fixture-mode safety:

  When `UoGSsoConfig.has_real_credentials() == False`, every
  resource yields exactly one `status="skipped_fixture"` row so a
  Dagster materialisation succeeds in CI (instead of crashing on the
  empty Playwright context).

Reference: openspec/changes/2026-08-23-uog-exam-papers-sso-v1/
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import dlt
import structlog
from sruth_browser.core.secrets import UoGSsoConfig
from sruth_browser.tools.uog_exam_scraper import (
    DEFAULT_RATELIMIT_MS,
    V1_SCHOOL_WHITELIST,
    UoGExamMaterial,
    UoGExamMaterialType,
    UoGExamScraper,
)

logger = structlog.get_logger(__name__)


def _skipped_fixture_row(material_type: str) -> dict[str, Any]:
    """Single placeholder row emitted when no real SSO creds are configured."""
    return {
        "module_code": "FIXTURE",
        "module_title": "[skipped] no real Campus Identity SSO credentials",
        "programme_codes": [],
        "school_slug": None,
        "academic_year": 0,
        "sitting": "AUTUMN",
        "material_type": material_type,
        "paper_format": "PDF_UPLOAD",
        "language": "en",
        "source_url": "",
        "title": None,
        "content_hash": "",
        "downloaded_at": None,
        "bytes": 0,
        "status": "skipped_fixture",
    }


def _materal_to_row(material: UoGExamMaterial, status: str = "scraped") -> dict[str, Any]:
    d = material.to_dict()
    d["status"] = status
    return d


def _scrape_all_materials(
    modules: list[str],
    years: list[int] | None = None,
    school_slug: str | None = None,
) -> Iterator[UoGExamMaterial]:
    """Run the scraper synchronously for `modules` x `years` (helper for DLT)."""
    import asyncio

    cfg = UoGSsoConfig.from_resolver()
    if not cfg.has_real_credentials():
        # Fixture mode → emit FOUR placeholder rows per module
        # (one per material_type) so every DLT resource has at least
        # one row to merge in CI.
        for module_code in modules:
            for material_type in (
                UoGExamMaterialType.PAPER,
                UoGExamMaterialType.MARKING_SCHEME,
                UoGExamMaterialType.MODEL_SOLUTION,
                UoGExamMaterialType.SUPPLEMENTARY_PAPER,
            ):
                fixture = UoGExamScraper(cfg)._fixture_material(
                    module_code, material_type=material_type
                )
                yield fixture
        return

    async def _collect() -> list[UoGExamMaterial]:
        out: list[UoGExamMaterial] = []
        async with UoGExamScraper(cfg) as scraper:
            await scraper.login()
            for module_code in modules:
                async for m in scraper.list_papers(module_code):
                    if years is None or m.academic_year in years:
                        out.append(m)
        return out

    yield from asyncio.run(_collect())


@dlt.source(name="uog_exam_papers")
def uog_exam_papers_source(
    modules: list[str] | None = None,
    years: list[int] | None = None,
    school_slug: str | None = None,
    ratelimit_ms: int = DEFAULT_RATELIMIT_MS,
):
    """DLT source for the authenticated University of Galway exam-paper corpus.

    Args:
      modules: list of UoG module codes (e.g. ['CT516', 'MA335']). When
        None, the source falls back to the v1 fixture whitelist
        (`CT516, CT511, MA335, ED305`).
      years: years to include (e.g. `[2020, 2021, 2022, 2023]`). None
        means "all available years discovered on the authenticated
        index".
      school_slug: optional school filter (e.g. `computer-science`).
      ratelimit_ms: throttle between requests, in ms. Defaults to
        `DEFAULT_RATELIMIT_MS` (1000); environment override
        `OOG_RATELIMIT_MS`.

    Yields 5 DLT resources: `exam_papers`, `marking_schemes`,
    `model_solutions`, `supplementary_papers`, `all_exam_materials`.

    Fixture-mode safety: when `UoGSsoConfig.has_real_credentials()`
    returns False (e.g. on a CI runner with `.env=fixture-only`),
    each resource yields a single `status="skipped_fixture"` row
    instead of an empty stream.
    """
    cfg = UoGSsoConfig.from_resolver()
    if modules is None:
        modules = (
            [] if cfg.has_real_credentials() else ["CT516", "CT511", "MA335", "ED305"]
        )

    has_real = cfg.has_real_credentials()

    # ------------------------------------------------------------------ #
    # 1. exam_papers
    # ------------------------------------------------------------------ #

    @dlt.resource(
        name="exam_papers",
        write_disposition="merge",
        primary_key=[
            "module_code",
            "academic_year",
            "sitting",
            "paper_format",
            "language",
            "content_hash",
        ],
        columns={
            "module_code": {"partition": True},
            "academic_year": {"partition": True},
        },
    )
    def exam_papers() -> Iterator[dict[str, Any]]:
        """Past exam papers."""
        if not has_real and not modules:
            yield _skipped_fixture_row("paper")
            return
        for material in _scrape_all_materials(modules, years, school_slug):
            if material.material_type == UoGExamMaterialType.PAPER:
                yield _materal_to_row(material)

    # ------------------------------------------------------------------ #
    # 2. marking_schemes
    # ------------------------------------------------------------------ #

    @dlt.resource(
        name="marking_schemes",
        write_disposition="merge",
        primary_key=[
            "module_code",
            "academic_year",
            "sitting",
            "content_hash",
        ],
        columns={
            "module_code": {"partition": True},
            "academic_year": {"partition": True},
        },
    )
    def marking_schemes() -> Iterator[dict[str, Any]]:
        """Marking schemes for examination papers."""
        if not has_real and not modules:
            yield _skipped_fixture_row("marking_scheme")
            return
        for material in _scrape_all_materials(modules, years, school_slug):
            if material.material_type == UoGExamMaterialType.MARKING_SCHEME:
                yield _materal_to_row(material)

    # ------------------------------------------------------------------ #
    # 3. model_solutions
    # ------------------------------------------------------------------ #

    @dlt.resource(
        name="model_solutions",
        write_disposition="merge",
        primary_key=[
            "module_code",
            "academic_year",
            "sitting",
            "content_hash",
        ],
        columns={
            "module_code": {"partition": True},
            "academic_year": {"partition": True},
        },
    )
    def model_solutions() -> Iterator[dict[str, Any]]:
        """Worked / model solutions released by lecturers."""
        if not has_real and not modules:
            yield _skipped_fixture_row("model_solution")
            return
        for material in _scrape_all_materials(modules, years, school_slug):
            if material.material_type == UoGExamMaterialType.MODEL_SOLUTION:
                yield _materal_to_row(material)

    # ------------------------------------------------------------------ #
    # 4. supplementary_papers
    # ------------------------------------------------------------------ #

    @dlt.resource(
        name="supplementary_papers",
        write_disposition="merge",
        primary_key=[
            "module_code",
            "academic_year",
            "sitting",
            "content_hash",
        ],
        columns={
            "module_code": {"partition": True},
            "academic_year": {"partition": True},
        },
    )
    def supplementary_papers() -> Iterator[dict[str, Any]]:
        """Resit / supplementary sitting papers."""
        if not has_real and not modules:
            yield _skipped_fixture_row("supplementary_paper")
            return
        for material in _scrape_all_materials(modules, years, school_slug):
            if material.material_type == UoGExamMaterialType.SUPPLEMENTARY_PAPER:
                yield _materal_to_row(material)

    # ------------------------------------------------------------------ #
    # 5. all_exam_materials — union
    # ------------------------------------------------------------------ #

    @dlt.resource(
        name="all_exam_materials",
        write_disposition="merge",
        primary_key=[
            "module_code",
            "academic_year",
            "sitting",
            "material_type",
            "content_hash",
        ],
        columns={
            "module_code": {"partition": True},
            "academic_year": {"partition": True},
            "material_type": {"partition": True},
        },
    )
    def all_exam_materials() -> Iterator[dict[str, Any]]:
        """Union of every exam material kind. Preferred for the marimo dashboard."""
        if not has_real and not modules:
            yield _skipped_fixture_row("all")
            return
        for material in _scrape_all_materials(modules, years, school_slug):
            yield _materal_to_row(material)

    return (
        exam_papers,
        marking_schemes,
        model_solutions,
        supplementary_papers,
        all_exam_materials,
    )


# --------------------------------------------------------------------------- #
# Convenience wrappers
# --------------------------------------------------------------------------- #


def msc_ai_source(years: list[int] | None = None) -> Any:
    """DLT source for the M.Sc. AI programme (CT5xx modules) only."""
    return uog_exam_papers_source(
        modules=["CT510", "CT511", "CT512", "CT513", "CT514", "CT515", "CT516"],
        years=years,
        school_slug="computer-science",
    )


def computer_science_source(
    years: list[int] | None = None,
    modules: list[str] | None = None,
) -> Any:
    """DLT source for the School of Computer Science."""
    return uog_exam_papers_source(
        modules=modules,
        years=years,
        school_slug="computer-science",
    )


def all_schools_source() -> Any:
    """DLT source for every school in the v1 whitelist (catch-all)."""
    return uog_exam_papers_source(
        modules=None,
        years=None,
        school_slug=None,
    )


__all__ = [
    "V1_SCHOOL_WHITELIST",
    "all_schools_source",
    "computer_science_source",
    "msc_ai_source",
    "uog_exam_papers_source",
]
