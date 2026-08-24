"""
cianfhoghlaim.orchestration.components — the 5 KCG-specific Dagster Components
(5-Layer Component architecture, see openspec/changes/2026-06-30-dagster-ground-up-rewrite-5-layer-component-architecture).

The 5 Components, one per layer:
- `CelticIngestionComponent` (L1 Ingestion, replaces `CelticDltSourceComponent`)
- `CelticMaterialsComponent` (L2 Materials, BAML extraction)
- `CelticModelLifecycleComponent` (L3 Model Lifecycle, CocoIndex v1 + R1-R4 lint,
  replaces `CelticCocoindexV1Component` + absorbs `CelticLancedbHnswComponent`)
- `CelticAssetGenerationComponent` (L4 Asset Generation, marimo + TanStack + oRPC)
- `CelticAgentOpsComponent` (L5 Agent Operations, 12-agent fleet + 5 emitted
  assets per agent)

Each Component subclasses `dagster.Component` and implements
`build_defs()`. They are discoverable via `dg list components` and
can be instantiated from YAML via `dg scaffold defs <Component> ...`.

Registered in `pyproject.toml:[tool.dg].registry_modules` so the
`dg` CLI auto-discovers them.

Dagster 1.13+ features used:
- `AutomationCondition` (replaces `@schedule`)
- `is_virtual=True` (on L3 CocoIndex v1 assets)
- `.resolve_through_virtual()` (on L3 + L5)
- `StateBackedComponent` (on L1 high-churn sources, monthly refresh)
- `DefsStateConfig` (L1 state persistence)
"""
from __future__ import annotations

from orchestration.components.layer1_ingestion import (
    CelticIngestionComponent,
)
from orchestration.components.layer2_materials import (
    CelticMaterialsComponent,
)
from orchestration.components.layer3_model_lifecycle import (
    CelticModelLifecycleComponent,
    ConformanceError,
)
from orchestration.components.layer4_asset_generation import (
    CelticAssetGenerationComponent,
)
from orchestration.components.layer5_agent_ops import (
    CelticAgentOpsComponent,
)

# BIEP v3 jurisdiction-scoped Components — referenced by `type:` in
# defs/2_materials/{ireland_education,england_education}/**/defs.yaml but
# previously not re-exported here, so `[tool.dg] registry_modules =
# ["orchestration.components"]` (and dg.load_defs()'s own YAML resolution)
# couldn't find them by attribute lookup on this module.
from orchestration.components.biep_subject_component import (
    BIEPSubjectComponent,
)
from orchestration.components.england_board_subject_component import (
    EnglandBoardSubjectComponent,
)
from orchestration.components.england_cross_board_comparator_component import (
    EnglandCrossBoardComparatorComponent,
)

# Same class of bug as the 3 BIEP v3 Components above — these exist and
# are already referenced by `type:` in defs/1_ingestion/curriculum/junior_cycle/**
# and defs/3_model_lifecycle/** defs.yaml files, but were never re-exported
# here, so `dg.load_defs()`'s YAML resolution couldn't find them by
# attribute lookup on this module (DagsterUnresolvableSymbolError).
from orchestration.components.junior_cycle_subject_component import (
    JuniorCycleCBAComponent,
    JuniorCycleShortCourseComponent,
    JuniorCycleSubjectComponent,
)
from orchestration.components.layer3_model_lifecycle import (
    CelticFederatedOcrComponent,
)

# Same class of bug again — these three were referenced by `type:` in
# defs/3_model_lifecycle/cognify/** and defs/2_materials/lc_extraction/
# lc_subjects/ but the classes existed nowhere in the repo at all.
from orchestration.components.biiep_ocr_ensemble_component import (
    BIEPOCREnsembleComponent,
)
from orchestration.components.kcg_cognify_component import (
    CognifyIngestSensorsComponent,
    KCGCognifyComponent,
    KCGSubjectPilotFactoryComponent,
)

# Backward-compat aliases (the 3 legacy `celtic_*` Components were
# replaced in the 5-layer rewrite; existing consumers can import
# the new names without breaking).

# Wave 2 — vertical pipelines (2026-08-24-wave-2-orchestration-vertical-pipelines-v1)
from orchestration.components.pipeline_factory import (
    PipelineFactoryComponent,
)
from orchestration.components.pipeline_kind_handlers import (
    PIPELINE_KIND_HANDLERS,
    BasePipelineHandler,
    ComicsHandler,
    CryptoHandler,
    ExamPapersHandler,
    MediaHandler,
    OfficialDocsHandler,
    PdfHandler,
    PersonalArchiveHandler,
    PipelineContext,
    SyllabusHandler,
)

__all__ = [
    "BIEPOCREnsembleComponent",
    "BIEPSubjectComponent",
    "CelticAgentOpsComponent",
    "CelticAssetGenerationComponent",
    "CelticFederatedOcrComponent",
    "CelticIngestionComponent",
    "CelticMaterialsComponent",
    "CelticModelLifecycleComponent",
    "CognifyIngestSensorsComponent",
    "ConformanceError",
    "EnglandBoardSubjectComponent",
    "EnglandCrossBoardComparatorComponent",
    "JuniorCycleCBAComponent",
    "JuniorCycleShortCourseComponent",
    "JuniorCycleSubjectComponent",
    "KCGCognifyComponent",
    "KCGSubjectPilotFactoryComponent",
    # Wave 2
    "PIPELINE_KIND_HANDLERS",
    "BasePipelineHandler",
    "ComicsHandler",
    "CryptoHandler",
    "ExamPapersHandler",
    "MediaHandler",
    "OfficialDocsHandler",
    "PdfHandler",
    "PersonalArchiveHandler",
    "PipelineContext",
    "PipelineFactoryComponent",
    "SyllabusHandler",
]
