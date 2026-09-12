"""``python -m cocoindex_flows.british_isles.uk`` entrypoint.

Local-dev entrypoint that:

1. Resolves the per-phase ``_lifespan`` shim + imports the canonical
   ``BAAI/bge-m3`` shared embedder from ``cocoindex_flows._shared._lifespan``.
2. Prints the R1-R4 conformance status of the en-cy / Wales Phase 1
   CocoIndex App + the en-ga / Republic of Ireland Phase 2 CocoIndex
   App + the en-ga / Northern Ireland Phase 3 CocoIndex App + the
   en-gd / Scotland Phase 4 CocoIndex App + the en-gv / Isle of Man
   Phase 5 CocoIndex App
   (per the ``oideachais-cocoindex-v1`` skill).
3. Runs ``<app>.update()`` for a one-shot catch-up (or ``-L`` for live
   mode).

Usage:

    uv run python -m cocoindex_flows.british_isles.uk --check                       # R1-R4 audit on all 5 phases
    uv run python -m cocoindex_flows.british_isles.uk --check-phase1               # R1-R4 audit on Phase 1 only
    uv run python -m cocoindex_flows.british_isles.uk --check-phase2               # R1-R4 audit on Phase 2 only
    uv run python -m cocoindex_flows.british_isles.uk --check-phase3               # R1-R4 audit on Phase 3 only
    uv run python -m cocoindex_flows.british_isles.uk --check-phase4               # R1-R4 audit on Phase 4 only
    uv run python -m cocoindex_flows.british_isles.uk --check-phase5               # R1-R4 audit on Phase 5 only
    uv run python -m cocoindex_flows.british_isles.uk --update-phase1              # Phase 1 catch-up
    uv run python -m cocoindex_flows.british_isles.uk --update-phase2              # Phase 2 catch-up
    uv run python -m cocoindex_flows.british_isles.uk --update-phase3              # Phase 3 catch-up
    uv run python -m cocoindex_flows.british_isles.uk --update-phase4              # Phase 4 catch-up
    uv run python -m cocoindex_flows.british_isles.uk --update-phase5              # Phase 5 catch-up
    uv run python -m cocoindex_flows.british_isles.uk --live-phase1                # Phase 1 live mode (-L flag)
    uv run python -m cocoindex_flows.british_isles.uk --live-phase2                # Phase 2 live mode (-L flag)
    uv run python -m cocoindex_flows.british_isles.uk --live-phase3                # Phase 3 live mode (-L flag)
    uv run python -m cocoindex_flows.british_isles.uk --live-phase4                # Phase 4 live mode (-L flag)
    uv run python -m cocoindex_flows.british_isles.uk --live-phase5                # Phase 5 live mode (-L flag)
    uv run python -m cocoindex_flows.british_isles.uk --metadata                   # all 5 phases metadata

Reference: ``openspec/changes/2026-09-06-ciancheiltis-v1/`` + the
Phase 5 extension at ``openspec/changes/2026-09-12-ciancheiltis-v2/``.
"""
from __future__ import annotations

import argparse
import asyncio
import importlib
import sys

from ._lifespan import (  # noqa: F401 — re-export surface
    COCOINDEX_AVAILABLE,
    EMBED_DIM,
    EMBED_MODEL,
    EMBEDDER,
    LANCE_DB,
    LANCEDB_URI,
    PHASE_LANGUAGE_PAIR,
    PHASE_LANGUAGE_PAIR_GA_NI,
    PHASE_LANGUAGE_PAIR_GA_ROI,
    PHASE_LANGUAGE_PAIR_GD,
    PHASE_LANGUAGE_PAIR_GV,
    PHASE_TABLE_URL,
    PHASE_TABLE_URL_GA_NI,
    PHASE_TABLE_URL_GA_ROI,
    PHASE_TABLE_URL_GD,
    PHASE_TABLE_URL_GV,
    shared_lifespan,
)

PHASE1_MODULE = "cocoindex_flows.british_isles.uk.ciancheiltis_en_cy_embedding"
PHASE2_MODULE = "cocoindex_flows.british_isles.uk.ciancheiltis_en_ga_roi_embedding"
PHASE3_MODULE = "cocoindex_flows.british_isles.uk.ciancheiltis_en_ga_ni_embedding"
PHASE4_MODULE = "cocoindex_flows.british_isles.uk.ciancheiltis_en_gd_embedding"
PHASE5_MODULE = "cocoindex_flows.british_isles.uk.ciancheiltis_en_gv_embedding"


def _print_r1_to_r4_audit(module: str, label: str) -> bool:
    """Run the R1-R4 conformance audit on a single phase App module.

    Delegates to ``orchestration.components.layer3_model_lifecycle
    .CelticModelLifecycleComponent._check_module_r1_to_r4`` so the
    audit matches what the L3 Dagster component runs at scaffold time.

    Returns True on PASS, False on FAIL.
    """
    try:
        from orchestration.components.layer3_model_lifecycle import (
            CelticModelLifecycleComponent,
            ConformanceError,
        )
    except ImportError as exc:  # pragma: no cover
        print(
            f"r1_to_r4_audit_skipped {label} orchestration_unavailable err={exc}",
            file=sys.stderr,
        )
        return True

    component = CelticModelLifecycleComponent()
    try:
        component._check_module_r1_to_r4(module)
        print(f"r1_to_r4 PASS {label} ({module})")
        return True
    except ConformanceError as exc:
        print(f"r1_to_r4 FAIL {label} rule={exc.rule} msg={exc.message}")
        print(f"  fix: {exc.fix}")
        return False


def _print_app_metadata() -> None:
    """Print the App's module-level metadata (R1-R4 + phase + table URL)."""
    print(
        "ciancheiltis_en_cy_embedding_phase1 metadata:\n"
        f"  language_pair = {PHASE_LANGUAGE_PAIR}\n"
        f"  embedder      = {EMBED_MODEL} (dim={EMBED_DIM})\n"
        f"  lancedb_uri   = {LANCEDB_URI}\n"
        f"  phase_table   = {PHASE_TABLE_URL}\n"
        f"  cocoindex_avail = {COCOINDEX_AVAILABLE}\n"
        "\n"
        "ciancheiltis_en_ga_roi_embedding_phase2 metadata:\n"
        f"  language_pair = {PHASE_LANGUAGE_PAIR_GA_ROI}\n"
        f"  embedder      = {EMBED_MODEL} (dim={EMBED_DIM})\n"
        f"  lancedb_uri   = {LANCEDB_URI}\n"
        f"  phase_table   = {PHASE_TABLE_URL_GA_ROI}\n"
        f"  cocoindex_avail = {COCOINDEX_AVAILABLE}\n"
        "\n"
        "ciancheiltis_en_ga_ni_embedding_phase3 metadata:\n"
        f"  language_pair = {PHASE_LANGUAGE_PAIR_GA_NI}\n"
        f"  embedder      = {EMBED_MODEL} (dim={EMBED_DIM})\n"
        f"  lancedb_uri   = {LANCEDB_URI}\n"
        f"  phase_table   = {PHASE_TABLE_URL_GA_NI}\n"
        f"  cocoindex_avail = {COCOINDEX_AVAILABLE}\n"
        "\n"
        "ciancheiltis_en_gd_embedding_phase4 metadata:\n"
        f"  language_pair = {PHASE_LANGUAGE_PAIR_GD}\n"
        f"  embedder      = {EMBED_MODEL} (dim={EMBED_DIM})\n"
        f"  lancedb_uri   = {LANCEDB_URI}\n"
        f"  phase_table   = {PHASE_TABLE_URL_GD}\n"
        f"  cocoindex_avail = {COCOINDEX_AVAILABLE}\n"
        "\n"
        "ciancheiltis_en_gv_embedding_phase5 metadata:\n"
        f"  language_pair = {PHASE_LANGUAGE_PAIR_GV}\n"
        f"  embedder      = {EMBED_MODEL} (dim={EMBED_DIM})\n"
        f"  lancedb_uri   = {LANCEDB_URI}\n"
        f"  phase_table   = {PHASE_TABLE_URL_GV}\n"
        f"  cocoindex_avail = {COCOINDEX_AVAILABLE}"
    )


def _run_update(module: str, app_name: str, live: bool) -> int:
    """Run the v1 CocoIndex App's ``update()`` for a one-shot catch-up."""
    if not COCOINDEX_AVAILABLE:
        print("cocoindex_not_installed skipping_update", file=sys.stderr)
        return 2
    import cocoindex as coco  # type: ignore[import-not-found]

    coco.init()

    mod = importlib.import_module(module)
    update = getattr(mod, "flow", None)
    if update is None:
        print("flow_symbol_not_found", file=sys.stderr)
        return 3

    # The L3 component reflects ``app.update`` directly; for live mode
    # pass the ``-L`` flag to the underlying CLI.
    if live:
        from cocoindex.cli import update as cli_update  # type: ignore[import-not-found]

        return cli_update(["-L", app_name])

    if hasattr(update, "run"):
        asyncio.run(update.run())
        return 0
    print("flow_has_no_run_method", file=sys.stderr)
    return 4


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m cocoindex_flows.british_isles.uk",
        description="ciancheiltis en-cy / Wales Phase 1 + en-ga / ROI Phase 2 + en-ga / NI Phase 3 + en-gd / Scotland Phase 4 + en-gv / Isle of Man Phase 5 CocoIndex App CLI",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--check",
        action="store_true",
        help="Run the R1-R4 conformance audit on all 5 phase Apps",
    )
    group.add_argument(
        "--check-phase1",
        action="store_true",
        help="Run the R1-R4 conformance audit on Phase 1 (en-cy / Wales) only",
    )
    group.add_argument(
        "--check-phase2",
        action="store_true",
        help="Run the R1-R4 conformance audit on Phase 2 (en-ga / ROI) only",
    )
    group.add_argument(
        "--check-phase3",
        action="store_true",
        help="Run the R1-R4 conformance audit on Phase 3 (en-ga / NI) only",
    )
    group.add_argument(
        "--check-phase4",
        action="store_true",
        help="Run the R1-R4 conformance audit on Phase 4 (en-gd / Scotland) only",
    )
    group.add_argument(
        "--check-phase5",
        action="store_true",
        help="Run the R1-R4 conformance audit on Phase 5 (en-gv / Isle of Man) only",
    )
    group.add_argument(
        "--update-phase1",
        action="store_true",
        help="Run a one-shot catch-up via en_cy_embedding.update()",
    )
    group.add_argument(
        "--update-phase2",
        action="store_true",
        help="Run a one-shot catch-up via en_ga_roi_embedding.update()",
    )
    group.add_argument(
        "--update-phase3",
        action="store_true",
        help="Run a one-shot catch-up via ciancheiltis_en_ga_ni_embedding.update()",
    )
    group.add_argument(
        "--update-phase4",
        action="store_true",
        help="Run a one-shot catch-up via ciancheiltis_en_gd_embedding.update()",
    )
    group.add_argument(
        "--update-phase5",
        action="store_true",
        help="Run a one-shot catch-up via ciancheiltis_en_gv_embedding.update()",
    )
    group.add_argument(
        "--live-phase1",
        action="store_true",
        help="Run Phase 1 in live mode (-L flag) — watches for upstream changes",
    )
    group.add_argument(
        "--live-phase2",
        action="store_true",
        help="Run Phase 2 in live mode (-L flag) — watches for upstream changes",
    )
    group.add_argument(
        "--live-phase3",
        action="store_true",
        help="Run Phase 3 in live mode (-L flag) — watches for upstream changes",
    )
    group.add_argument(
        "--live-phase4",
        action="store_true",
        help="Run Phase 4 in live mode (-L flag) — watches for upstream changes",
    )
    group.add_argument(
        "--live-phase5",
        action="store_true",
        help="Run Phase 5 in live mode (-L flag) — watches for upstream changes",
    )
    group.add_argument(
        "--metadata",
        action="store_true",
        help="Print the App's module-level metadata (R1-R4 + phase + table URL)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    _print_app_metadata()
    print()
    if args.check:
        ok1 = _print_r1_to_r4_audit(PHASE1_MODULE, "ciancheiltis_en_cy_embedding_phase1")
        ok2 = _print_r1_to_r4_audit(PHASE2_MODULE, "ciancheiltis_en_ga_roi_embedding_phase2")
        ok3 = _print_r1_to_r4_audit(PHASE3_MODULE, "ciancheiltis_en_ga_ni_embedding_phase3")
        ok4 = _print_r1_to_r4_audit(PHASE4_MODULE, "ciancheiltis_en_gd_embedding_phase4")
        ok5 = _print_r1_to_r4_audit(PHASE5_MODULE, "ciancheiltis_en_gv_embedding_phase5")
        return 0 if (ok1 and ok2 and ok3 and ok4 and ok5) else 1
    if args.check_phase1:
        return 0 if _print_r1_to_r4_audit(PHASE1_MODULE, "ciancheiltis_en_cy_embedding_phase1") else 1
    if args.check_phase2:
        return 0 if _print_r1_to_r4_audit(PHASE2_MODULE, "ciancheiltis_en_ga_roi_embedding_phase2") else 1
    if args.check_phase3:
        return 0 if _print_r1_to_r4_audit(PHASE3_MODULE, "ciancheiltis_en_ga_ni_embedding_phase3") else 1
    if args.check_phase4:
        return 0 if _print_r1_to_r4_audit(PHASE4_MODULE, "ciancheiltis_en_gd_embedding_phase4") else 1
    if args.check_phase5:
        return 0 if _print_r1_to_r4_audit(PHASE5_MODULE, "ciancheiltis_en_gv_embedding_phase5") else 1
    if args.metadata:
        return 0
    if args.update_phase1:
        return _run_update(PHASE1_MODULE, "CiancheiltisEnCyEmbedding", live=False)
    if args.update_phase2:
        return _run_update(PHASE2_MODULE, "CiancheiltisEnGaRoiEmbedding", live=False)
    if args.update_phase3:
        return _run_update(PHASE3_MODULE, "CiancheiltisEnGaNiEmbedding", live=False)
    if args.update_phase4:
        return _run_update(PHASE4_MODULE, "CiancheiltisEnGdEmbedding", live=False)
    if args.update_phase5:
        return _run_update(PHASE5_MODULE, "CiancheiltisEnGvEmbedding", live=False)
    if args.live_phase1:
        return _run_update(PHASE1_MODULE, "CiancheiltisEnCyEmbedding", live=True)
    if args.live_phase2:
        return _run_update(PHASE2_MODULE, "CiancheiltisEnGaRoiEmbedding", live=True)
    if args.live_phase3:
        return _run_update(PHASE3_MODULE, "CiancheiltisEnGaNiEmbedding", live=True)
    if args.live_phase4:
        return _run_update(PHASE4_MODULE, "CiancheiltisEnGdEmbedding", live=True)
    if args.live_phase5:
        return _run_update(PHASE5_MODULE, "CiancheiltisEnGvEmbedding", live=True)
    return 0  # unreachable: argparse makes the group mutually exclusive


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
