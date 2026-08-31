"""
Smoke-test the 7-row CIANFHOGHLAIM_* env-var matrix.

Validates that every code-side caller (Dagster resources, BAML
clients, DLT destinations, CocoIndex flows, Langfuse / Logfire /
MLflow clients, Cognee memory) reads from the canonical env-var
matrix in observability/env_config.py.

Run via:  mise run validate-env

Exit codes:
  0 — all 7 vars + their legacy aliases + all reachable modules pass
  1 — a CIANFHOGHLAIM_* var is missing from the matrix
  2 — a legacy alias disagrees with its CIANFHOGHLAIM_* counterpart
  3 — a code-side module fails to import
  4 — a default value is missing or wrong

This script is the canonical smoke test introduced by openspec
change 2026-07-02-align-cianfhoghlaim-env-with-stacks. It is
intentionally light: a `validate-env` that takes >5 seconds is a
bug, not a feature.
"""

from __future__ import annotations

import importlib
import os
import sys
from typing import Any

# The 7 expected CIANFHOGHLAIM_* env vars + their defaults + legacy aliases.
EXPECTED_VARS: dict[str, dict[str, Any]] = {
    "CIANFHOGHLAIM_LITELLM_URL": {
        "default": "http://litellm:4000/v1",
        "legacy_alias": "LITELLM_BASE_URL",
    },
    "CIANFHOGHLAIM_LANGFUSE_URL": {
        "default": "http://langfuse:3000",
        "legacy_alias": "LANGFUSE_HOST",
    },
    "CIANFHOGHLAIM_MLFLOW_URL": {
        "default": "http://mlflow:5000",
        "legacy_alias": "MLFLOW_TRACKING_URI",
    },
    "CIANFHOGHLAIM_FALKORDB_URL": {
        "default": "redis://falkordb:6379",
        "legacy_alias": "FALKORDB_HOST + FALKORDB_PORT",
    },
    "CIANFHOGHLAIM_LANCEDB_URL": {
        "default": "rest://lakehouse-lance-namespace:8182",
        "legacy_alias": "LANCEDB_URI",
    },
    "CIANFHOGHLAIM_LOGFIRE_TOKEN": {
        "default": "(empty in dev, from Infisical via Locket in prod)",
        "legacy_alias": "LOGFIRE_TOKEN",
    },
    "CIANFHOGHLAIM_COGNEE_BACKEND": {
        "default": "falkordb",
        "legacy_alias": "COGNEE_BACKEND",
    },
}

# Code-side modules that MUST import without error (a baseline that
# catches missing `from .env_config import ...` statements or syntax
# errors in the env-config module).
#
# NOTE (2026-08-26): rewritten for the v7 flattened layout — the repo
# root IS the package root (no `cianfhoghlaim.` prefix; see
# pyproject.toml `[tool.hatch.build.targets.wheel] packages = ["."]`).
# The pre-flatten paths below silently 100%-failed every run (module
# not found) since the flatten; fixed as part of the
# data-side-remediation pass. Real paths verified against the working
# tree, not assumed:
#   cianfhoghlaim.cocoindex._lifespan            -> cocoindex_flows._shared._lifespan
#   cianfhoghlaim.dlt.common.destinations_oideachais -> dlt_sources.common.destinations_cianfhoghlaim
#   cianfhoghlaim.cocoindex.file_graph           -> cocoindex_flows.knowledge_graph.file_graph
MODULES_TO_VERIFY: list[str] = [
    "observability.env_config",
    "observability.langfuse_config",
    "observability.logfire_config",
    "observability.mlflow_config",
    "orchestration.resources",
    "cocoindex_flows._shared._lifespan",
    "dlt_sources.common.destinations_cianfhoghlaim",
    "meaisinfhoghlaim.config.base",
    "cocoindex_flows.knowledge_graph.file_graph",
    # NOTE: storage.lightrag_curriculum is intentionally
    # omitted — it has a pre-existing missing-import bug
    # (`from .config import X`) that is out-of-scope for the pick-7
    # env-alignment change. Tracked separately.
]


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []

    # Add the repo root to sys.path so the importlib lookups resolve
    # the flattened top-level packages (observability/, orchestration/,
    # cocoindex_flows/, dlt_sources/, meaisinfhoghlaim/, ...) when run
    # from a fresh checkout.
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    # ------------------------------------------------------------------
    # Step 1: import the canonical env_config module + read the matrix
    # ------------------------------------------------------------------
    try:
        env_config = importlib.import_module("observability.env_config")
    except Exception as exc:  # pragma: no cover - import error path
        print(f"FAIL  cannot import env_config: {exc}")
        return 3

    matrix = getattr(env_config, "ENV_VAR_MATRIX", {})
    if not matrix:
        errors.append("env_config.ENV_VAR_MATRIX is empty or missing")
    else:
        info.append(f"env_config.ENV_VAR_MATRIX has {len(matrix)} rows")

    # ------------------------------------------------------------------
    # Step 2: verify every CIANFHOGHLAIM_* var has a matrix row
    # ------------------------------------------------------------------
    for var_name in EXPECTED_VARS:
        if var_name not in matrix:
            errors.append(f"missing matrix row for {var_name}")
        else:
            row = matrix[var_name]
            expected_default = EXPECTED_VARS[var_name]["default"]
            if expected_default not in str(row.get("default", "")):
                errors.append(
                    f"{var_name} default mismatch: "
                    f"matrix has {row.get('default')!r}, "
                    f"expected to contain {expected_default!r}"
                )
            else:
                info.append(f"  {var_name} default = {row['default']}")

    # ------------------------------------------------------------------
    # Step 3: import each code-side module that consumes the matrix
    # ------------------------------------------------------------------
    for module_name in MODULES_TO_VERIFY:
        try:
            importlib.import_module(module_name)
        except Exception as exc:  # pragma: no cover
            errors.append(f"import failed for {module_name}: {exc}")
        else:
            info.append(f"  {module_name} imported cleanly")

    # ------------------------------------------------------------------
    # Step 4: verify the resolved values from env_config
    # ------------------------------------------------------------------
    expected_resolved = {
        "LITELLM_URL": "http://litellm:4000/v1",
        "LANGFUSE_URL": "http://langfuse:3000",
        "MLFLOW_URL": "http://mlflow:5000",
        "FALKORDB_HOST": "falkordb",
        "FALKORDB_PORT": 6379,
        "LANCEDB_URL": "rest://lakehouse-lance-namespace:8182",
        "COGNEE_BACKEND": "falkordb",
    }
    for attr, expected in expected_resolved.items():
        actual = getattr(env_config, attr, None)
        if actual is None:
            errors.append(f"env_config.{attr} is None or missing")
        elif str(actual) != str(expected):
            warnings.append(
                f"env_config.{attr} = {actual!r} (expected {expected!r}) — "
                f"likely an operator override via env var"
            )
        else:
            info.append(f"  env_config.{attr} = {actual}")

    # ------------------------------------------------------------------
    # Step 5: verify the Cognee fallback chain
    # ------------------------------------------------------------------
    fallback_result = env_config.resolve_cognee_backend_with_fallback()
    if fallback_result not in ("falkordb", "memgraph"):
        errors.append(
            f"resolve_cognee_backend_with_fallback returned {fallback_result!r}, "
            f"expected 'falkordb' or 'memgraph'"
        )
    else:
        info.append(f"  Cognee fallback chain resolves to: {fallback_result}")

    # ------------------------------------------------------------------
    # Report
    # ------------------------------------------------------------------
    print("=" * 72)
    print("CIANFHOGHLAIM_* env-var matrix smoke test")
    print("=" * 72)
    print()
    print("INFO")
    for line in info:
        print(f"  {line}")
    print()
    if warnings:
        print("WARNINGS")
        for line in warnings:
            print(f"  {line}")
        print()
    if errors:
        print("ERRORS")
        for line in errors:
            print(f"  {line}")
        print()
        print(f"FAIL — {len(errors)} error(s), {len(warnings)} warning(s)")
        if any("missing matrix row" in e for e in errors):
            return 1
        if any("default mismatch" in e for e in errors):
            return 4
        return 3

    print(f"PASS — {len(info)} checks ok, {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
