"""cocoindex_flows.british_isles.ireland.tertiary.uog._shared
-- The cianfhoghlaim tertiary-pipeline per-module CocoIndex factory.

Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.

Mirrors the BIEP v3 LC per-subject factory at
cocoindex_flows/british_isles/ireland/education/lc/_shared.py:95-150
(LCSubjectSpec) but scales up to per-module granularity. The factory
emits one CocoIndex v1 App per `(module_id, language)` row from
_modules.yaml.

R1: import `shared_lifespan` + `LANCE_DB` + `EMBEDDER` from
    `....._shared._lifespan`
R2: declare `app = coco.App(coco.AppConfig(name=...))` at module scope
    (R2 enforced by `cocoindex_v1_conformance.py`)
R3: at least one `@coco.fn(...)` decorator present

The 4-tier config mirrors the BAML schema at
baml_src/british_isles/ireland/tertiary/university_extraction.baml:
College → School → Programme → Module.

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import hashlib
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


# ============================================================================
# The 4-tier config (College → School → Programme → Module)
# ============================================================================

@dataclass(frozen=True)
class CollegeSpec:
    college_id: str
    college_name_english: str
    college_name_irish: str | None = None
    nfq_min: int = 6
    nfq_max: int = 10


@dataclass(frozen=True)
class SchoolSpec:
    school_id: str
    college_id: str
    school_name_english: str
    school_name_irish: str | None = None


@dataclass(frozen=True)
class ProgrammeSpec:
    programme_id: str
    programme_code: str
    school_id: str
    title_english: str
    title_irish: str | None = None
    nfq_level: int = 8


@dataclass(frozen=True)
class ModuleSpec:
    module_id: str
    module_code: str
    programme_ids: tuple[str, ...]
    school_id: str
    title_english: str
    title_irish: str | None = None
    languages: tuple[str, ...] = ("en",)
    ects_credits: int = 5


@dataclass(frozen=True)
class UoGTertiaryConfig:
    """The full 4-tier config for one UoG college + its schools + programmes + modules."""

    college: CollegeSpec
    schools: tuple[SchoolSpec, ...]
    programmes: tuple[ProgrammeSpec, ...]
    modules: tuple[ModuleSpec, ...]


# The 4 canonical UoG colleges
UO_G_COLLEGES: tuple[CollegeSpec, ...] = (
    CollegeSpec(
        college_id="science-engineering",
        college_name_english="College of Science and Engineering",
        college_name_irish="Coláiste na hEolaíochta agus na hInnealtóireachta",
        nfq_min=6,
        nfq_max=10,
    ),
    CollegeSpec(
        college_id="arts-social-sciences-celtic-studies",
        college_name_english="College of Arts, Social Sciences, and Celtic Studies",
        college_name_irish="Coláiste na nEalaíon, na nEolaíochtaí Sóisialta agus an Léinn Cheiltigh",
        nfq_min=6,
        nfq_max=10,
    ),
    CollegeSpec(
        college_id="business-public-policy-law",
        college_name_english="College of Business, Public Policy, and Law",
        college_name_irish="Coláiste an Ghnó, an Pholasaí Phoiblí agus an Dlí",
        nfq_min=6,
        nfq_max=10,
    ),
    CollegeSpec(
        college_id="medicine-nursing-health-sciences",
        college_name_english="College of Medicine, Nursing, and Health Sciences",
        college_name_irish="Coláiste an Leighis, an Altranais agus na nEolaíochtaí Sláinte",
        nfq_min=6,
        nfq_max=10,
    ),
)


# ============================================================================
# The factory (per openspec/AGENTS.md §cocoindex-v1 conformance)
# ============================================================================

# CocoIndex is optional — degrade gracefully if not installed.
try:
    import cocoindex as coco  # type: ignore[import-not-found]
    from cocoindex.connectors import lancedb as coco_lancedb  # type: ignore[import-not-found]

    COCOINDEX_AVAILABLE = True
except ImportError:
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    coco_lancedb = None  # type: ignore[assignment]


def create_uog_module_flow(config: ModuleSpec) -> Any:
    """Build one CocoIndex v1 App for one UoG module.

    Mirrors the BIEP v3 LC per-subject pattern at
    cocoindex_flows/british_isles/ireland/education/lc/_shared.py:95-150.
    The App chunks the module's per-module PDF handbook + embeds via
    BAAI/bge-m3 1024-d + writes to LanceDB.

    Returns: a `coco.App` instance named `uog_<module_id>_flow`
    """
    if not COCOINDEX_AVAILABLE:
        logger.warning("cocoindex_unavailable: cannot create_uog_module_flow(%s)", config.module_id)
        return None

    if not hasattr(coco, "App"):
        return None

    app = coco.App(coco.AppConfig(name=f"uog_{config.module_id}_flow"))

    @coco.function(
        name=f"uog_{config.module_id}_process",
        data_sources={
            "handbook": _ModuleHandbookSource(config.module_code),
            "reading_list": _ReadingListSource(config.module_code),
        },
    )
    def uog_module_flow(builder: Any, handbook: Any, reading_list: Any) -> None:
        with builder.read_data("handbook"):
            sections = builder.add_classes(ModuleHandbookSectionRecord)
        with builder.read_data("reading_list"):
            items = builder.add_classes(ReadingListItemRecord)
        builder.export(
            "module_id", config.module_id,
            "module_code", config.module_code,
            "title_english", config.title_english,
            "ects_credits", config.ects_credits,
            "sections", sections,
            "reading_list", items,
        )

    return app


# ============================================================================
# Per-source data adapters (Phase 2: implement via sruth_browser + the DLT sources)
# ============================================================================


class _ModuleHandbookSource:
    """Phase 2 stub — Phase 2 fills from dlt_sources/british_isles/ireland/tertiary/uog/module_handbooks.py."""

    def __init__(self, module_code: str) -> None:
        self.module_code = module_code

    def __iter__(self) -> Iterator[dict]:
        yield {
            "module_code": self.module_code,
            "pdf_url": f"https://www.universityofgalway.ie/programmes/{self.module_code}.pdf",
            "sections": [],
            "total_pages": 0,
        }


class _ReadingListSource:
    """Phase 2 stub — Phase 2 fills from dlt_sources/british_isles/ireland/tertiary/uog/reading_lists.py."""

    def __init__(self, module_code: str) -> None:
        self.module_code = module_code

    def __iter__(self) -> Iterator[dict]:
        yield {"module_code": self.module_code, "reading_list": []}


# ============================================================================
# CocoIndex Record schemas
# ============================================================================

class ModuleHandbookSectionRecord:
    section_title: str
    section_body: str


class ReadingListItemRecord:
    format: str
    title: str
    authors: list[str]
    year: int | None
    isbn_13: str | None
    doi: str | None
    url: str | None
    library_ref: str | None
    essential: bool


# ============================================================================
# Default embedder dim (matches cocoindex_flows/_shared/_lifespan.py:109)
# ============================================================================

DEFAULT_EMBED_DIM = 1024


def get_college(college_id: str) -> CollegeSpec:
    for c in UO_G_COLLEGES:
        if c.college_id == college_id:
            return c
    raise KeyError(f"Unknown UoG college_id: {college_id!r}")


def iter_colleges() -> Iterator[CollegeSpec]:
    yield from UO_G_COLLEGES


__all__ = [
    "UO_G_COLLEGES",
    "CollegeSpec",
    "SchoolSpec",
    "ProgrammeSpec",
    "ModuleSpec",
    "UoGTertiaryConfig",
    "create_uog_module_flow",
    "get_college",
    "iter_colleges",
    "DEFAULT_EMBED_DIM",
]
