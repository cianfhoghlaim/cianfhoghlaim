"""
cianfhoghlaim.dagster.components — the 5 KCG-specific Dagster Components
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

from cianfhoghlaim.dagster.components.layer1_ingestion import (
    CelticIngestionComponent,
)
from cianfhoghlaim.dagster.components.layer2_materials import (
    CelticMaterialsComponent,
)
from cianfhoghlaim.dagster.components.layer3_model_lifecycle import (
    ConformanceViolation,
    CelticModelLifecycleComponent,
)
from cianfhoghlaim.dagster.components.layer4_asset_generation import (
    CelticAssetGenerationComponent,
)
from cianfhoghlaim.dagster.components.layer5_agent_ops import (
    CelticAgentOpsComponent,
)

# Backward-compat aliases (the 3 legacy `celtic_*` Components were
# replaced in the 5-layer rewrite; existing consumers can import
# the new names without breaking).
__all__ = [
    # The 5 KCG Components (canonical)
    "CelticIngestionComponent",
    "CelticMaterialsComponent",
    "CelticModelLifecycleComponent",
    "CelticAssetGenerationComponent",
    "CelticAgentOpsComponent",
    # Conformance exception (used by L3 R1-R4 enforcement)
    "ConformanceViolation",
]
