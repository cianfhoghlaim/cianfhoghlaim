"""
Cianfhoghlaim Dagster Layer — 5-Layer Component architecture.

The cianfhoghlaim.orchestration/ module is the canonical Dagster layer for
the Cianfhoghlaim platform, organised into 5 layers per the
2026-06-30-dagster-ground-up-rewrite-5-layer-component-architecture
change:

- L1 (Ingestion)         : CelticIngestionComponent          (defs/1_ingestion/)
- L2 (Materials)         : CelticMaterialsComponent          (defs/2_materials/)
- L3 (Model Lifecycle)   : CelticModelLifecycleComponent     (defs/3_model_lifecycle/)
- L4 (Asset Generation)  : CelticAssetGenerationComponent    (defs/4_asset_generation/)
- L5 (Agent Operations)  : CelticAgentOpsComponent           (defs/5_agent_ops/)

Usage:
    # Local dev server (Dagster 1.13+ dg CLI)
    dg dev  # http://localhost:3335

    # Or the legacy pattern
    dagster dev -m cianfhoghlaim.orchestration.definitions

See README.md for the full architecture overview + the developer
workflow (`dg list defs`, `dg list components`, `dg scaffold defs`).
"""
