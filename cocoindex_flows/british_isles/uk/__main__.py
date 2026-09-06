"""``python -m cocoindex_flows.british_isles.uk`` entrypoint.

Local-dev entrypoint that:

1. Resolves the per-phase ``_lifespan`` shim + imports the canonical
   ``BAAI/bge-m3`` shared embedder from ``cocoindex_flows._shared._lifespan``.
2. Prints the R1-R4 conformance status of the en-cy / Wales Phase 1
   CocoIndex App (per the ``oideachais-cocoindex-v1`` skill).
3. Runs ``en_cy_embedding.update()`` for a one-shot catch-up (or
   ``-L`` for live mode).

Usage:

    uv run python -m cocoindex_flows.british_isles.uk --check        # R1-R4 audit
    uv run python -m cocoindex_flows.british_isles.uk --update       # catch-up
    uv run python -m cocoindex_flows.british_isles.uk --live         # live mode

Reference: ``openspec/changes/2026-09-06-ciancheiltis-v1/``.
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
    PHASE_TABLE_URL,
    shared_lifespan,
)


def _print_r1_to_r4_audit() -> None:
    """Run the R1-R4 conformance audit on the en-cy Phase 1 App module.

    Delegates to ``orchestration.components.layer3_model_lifecycle
    .CelticModelLifecycleComponent._check_module_r1_to_r4`` so the
    audit matches what the L3 Dagster component runs at scaffold time.
    """
    try:
        from orchestration.components.layer3_model_lifecycle import (
            CelticModelLifecycleComponent,
            ConformanceError,
        )
    except ImportError as exc:  # pragma: no cover
        print(
            f"r1_to_r4_audit_skipped orchestration_unavailable err={exc}",
            file=sys.stderr,
        )
        return

    component = CelticModelLifecycleComponent()
    try:
        component._check_module_r1_to_r4(
            "cocoindex_flows.british_isles.uk.ciancheiltis_en_cy_embedding"
        )
        print("r1_to_r4 PASS ciancheiltis_en_cy_embedding")
    except ConformanceError as exc:
        print(f"r1_to_r4 FAIL rule={exc.rule} msg={exc.message}")
        print(f"  fix: {exc.fix}")
        sys.exit(1)


def _print_app_metadata() -> None:
    """Print the App's module-level metadata (R1-R4 + phase + table URL)."""
    print(
        "ciancheiltis_en_cy_embedding_phase1 metadata:\n"
        f"  language_pair = {PHASE_LANGUAGE_PAIR}\n"
        f"  embedder      = {EMBED_MODEL} (dim={EMBED_DIM})\n"
        f"  lancedb_uri   = {LANCEDB_URI}\n"
        f"  phase_table   = {PHASE_TABLE_URL}\n"
        f"  cocoindex_avail = {COCOINDEX_AVAILABLE}"
    )


def _run_update(live: bool) -> int:
    """Run the v1 CocoIndex App's ``update()`` for a one-shot catch-up."""
    if not COCOINDEX_AVAILABLE:
        print("cocoindex_not_installed skipping_update", file=sys.stderr)
        return 2
    import cocoindex as coco  # type: ignore[import-not-found]

    coco.init()

    mod = importlib.import_module(
        "cocoindex_flows.british_isles.uk.ciancheiltis_en_cy_embedding"
    )
    update = getattr(mod, "flow", None)
    if update is None:
        print("flow_symbol_not_found", file=sys.stderr)
        return 3

    # The L3 component reflects ``app.update`` directly; for live mode
    # pass the ``-L`` flag to the underlying CLI.
    if live:
        from cocoindex.cli import update as cli_update  # type: ignore[import-not-found]

        return cli_update(["-L", "CiancheiltisEnCyEmbedding"])

    if hasattr(update, "run"):
        asyncio.run(update.run())
        return 0
    print("flow_has_no_run_method", file=sys.stderr)
    return 4


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m cocoindex_flows.british_isles.uk",
        description="ciancheiltis en-cy / Wales Phase 1 CocoIndex App CLI",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--check", action="store_true", help="Run the R1-R4 conformance audit"
    )
    group.add_argument(
        "--update",
        action="store_true",
        help="Run a one-shot catch-up via en_cy_embedding.update()",
    )
    group.add_argument(
        "--live",
        action="store_true",
        help="Run in live mode (-L flag) — watches for upstream changes",
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
        _print_r1_to_r4_audit()
        return 0
    if args.metadata:
        return 0
    if args.update or args.live:
        return _run_update(live=args.live)
    return 0  # unreachable: argparse makes the group mutually exclusive


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
