"""
educational — Python asset module for Domain 5 (formerly "tuatha").

Wires the 6 Tuatha-derived (now "educational") game-state sources as
Dagster assets:

1. mythology_cognify — Celtic mythology knowledge graph
2. celtic_tutor_agent — Celtic language tutor (port 7777)
3. crypteolas_defi — Crypto/DeFi data source
4. tuatha_mmo_state — MMO game state (player inventories, quests)
5. tuatha_embedding — Player/quest embeddings
6. tuatha_audio — Audio assets (Celtic music, sound effects)

**Note (2026-06-30 — cianfhoghlaim-educational-mmo-v1):**
This module's underlying Python paths still use the legacy
"tuatha" naming for backwards compatibility with the 6-phase
refactor's shim pattern. The follow-on rename tasks (Phase 2,
T2.12 in the openspec change) update the import paths to use
`cianfhoghlaim.agents.meaisinfhoghlaim.educational.*` once the
shim compatibility period ends.

This is the Layer 1 + 2 of the 4-layer asset graph for the
educational (formerly Tuatha) code-location. Reference:
openspec/specs/cianfhoghlaim-educational-mmo/spec.md (8 requirements).
"""
from __future__ import annotations

import dagster as dg


def _make_tuatha_asset(name: str, module_path: str, fn_name: str) -> dg.AssetsDefinition:
    """Build a Dagster asset for a single Tuatha game-state function."""
    @dg.asset(
        name=name,
        group_name="tuatha",
        compute_kind="python",
        description=f"Tuatha {name} via {fn_name}",
    )
    def _asset() -> dg.MaterializeResult:
        import importlib
        mod = importlib.import_module(module_path)
        fn = getattr(mod, fn_name)
        result = fn()
        return dg.MaterializeResult(
            metadata={"pipeline": name, "module": module_path, "fn": fn_name}
        )

    return _asset


tuatha_assets = [
    _make_tuatha_asset(
        "mythology_cognify",
        "cianfhoghlaim.core.cognify.mythology_cognify",
        "cognify_mythology",
    ),
    _make_tuatha_asset(
        "celtic_tutor_agent",
        "cianfhoghlaim.agents.meaisinfhoghlaim.educational.agents.adk.celtic_tutor",
        "run_celtic_tutor",
    ),
    _make_tuatha_asset(
        "crypteolas_defi",
        "cianfhoghlaim.pipelines.ingest._tuatha_dlt_sources.crypteolas",
        "fetch_defi_state",
    ),
    _make_tuatha_asset(
        "tuatha_mmo_state",
        "cianfhoghlaim.pipelines.ingest._tuatha_dlt_sources.mmo_state",
        "fetch_mmo_state",
    ),
    _make_tuatha_asset(
        "tuatha_embedding",
        "cianfhoghlaim.embeddings._tuatha_src.tuatha_embedding",
        "build_tuatha_embeddings",
    ),
    _make_tuatha_asset(
        "tuatha_audio",
        "cianfhoghlaim.pipelines.ingest._tuatha_dlt_sources.audio",
        "fetch_tuatha_audio",
    ),
]


__all__ = ["tuatha_assets"]
