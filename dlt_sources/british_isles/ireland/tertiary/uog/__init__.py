"""cianfhoghlaim — DLT sources for the University of Galway (Ollscoil na Gaillimhe).

Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.

The 14 DLT sources ship the 4-tier College → School → Programme →
Module pipeline + the authenticated regexam.nuigalway.ie + Canvas
pipelines:

  1. academic_calendar        — UoG academic calendar + key dates
  2. governance_minutes        — University Council + Academic Council minutes
  3. press_releases            — UoG news + press releases
  4. programme_catalog         — Public programme catalog (UG + PG)
  5. research_outputs          — Research publications + theses
  6. colleges                  — The 4 UoG colleges
  7. schools                   — The ~10 UoG schools (per college)
  8. programmes                — The ~200 UoG programmes
  9. modules                   — The ~1,500 UoG modules
 10. module_handbooks          — Per-module PDF handbook + OCR
 11. reading_lists             — Per-module reading list extraction
 12. past_papers               — Per-module past papers (regexam)
 13. regexam_papers            — Authenticated regexam scraper (M365)
 14. canvas_materials          — Per-user Canvas materials (PAT + M365 fallback)

Every DLT resource honours `USE_LOCAL_SCRAPES=true` falling back to
`stedding/ingest_queue/uog/<surface>/` for offline development.

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from ._base import (
    _TERTIARY_SURFACES,
    _TERTIARY_SURFACE_CONFIGS,
    TERTIARY_PIPELINE_BASE_VERSION,
    TertiaryPipelineBase,
    TertiarySurfaceConfig,
)
from .academic_calendar import (
    AcademicCalendarPipeline,
    academic_calendar_pipeline,
)
from .colleges import (
    CollegesPipeline,
    colleges_pipeline,
)
from .governance_minutes import (
    GovernanceMinutesPipeline,
    governance_minutes_pipeline,
)
from .module_handbooks import (
    ModuleHandbooksPipeline,
    module_handbooks_pipeline,
)
from .modules import (
    ModulesPipeline,
    modules_pipeline,
)
from .past_papers import (
    PastPapersPipeline,
    past_papers_pipeline,
)
from .press_releases import (
    PressReleasesPipeline,
    press_releases_pipeline,
)
from .programme_catalog import (
    ProgrammeCatalogPipeline,
    programme_catalog_pipeline,
)
from .programmes import (
    ProgrammesPipeline,
    programmes_pipeline,
)
from .reading_lists import (
    ReadingListsPipeline,
    reading_lists_pipeline,
)
from .research_outputs import (
    ResearchOutputsPipeline,
    research_outputs_pipeline,
)
from .schools import (
    SchoolsPipeline,
    schools_pipeline,
)
from .canvas_materials import (
    canvas_materials,
    canvas_nuig_materials_source,
)
from .regexam_papers import (
    regexam_papers,
    regexam_nuig_papers_source,
)

__all__ = [
    # Base classes
    "_TERTIARY_SURFACES",
    "_TERTIARY_SURFACE_CONFIGS",
    "TERTIARY_PIPELINE_BASE_VERSION",
    "TertiaryPipelineBase",
    "TertiarySurfaceConfig",
    # 5 from KCG (moved + retargeted)
    "AcademicCalendarPipeline",
    "academic_calendar_pipeline",
    "GovernanceMinutesPipeline",
    "governance_minutes_pipeline",
    "ProgrammeCatalogPipeline",
    "programme_catalog_pipeline",
    "PressReleasesPipeline",
    "press_releases_pipeline",
    "ResearchOutputsPipeline",
    "research_outputs_pipeline",
    # 7 new (per-tier + deep extractions)
    "CollegesPipeline",
    "colleges_pipeline",
    "SchoolsPipeline",
    "schools_pipeline",
    "ProgrammesPipeline",
    "programmes_pipeline",
    "ModulesPipeline",
    "modules_pipeline",
    "ModuleHandbooksPipeline",
    "module_handbooks_pipeline",
    "ReadingListsPipeline",
    "reading_lists_pipeline",
    "PastPapersPipeline",
    "past_papers_pipeline",
    # 2 authenticated (regexam + canvas)
    "regexam_papers",
    "regexam_nuig_papers_source",
    "canvas_materials",
    "canvas_nuig_materials_source",
]
