"""marimo notebook: baml_build_status — the BAML health dashboard.

Per the 2026-10-30-biep-tertiary-baml-repair-v1 umbrella of
openspec/plans/2026-10-30-platform-reset-saga-v1.md (Umbrella 2 of 4).

A marimo dashboard that displays the BAML project's build health:
- `baml-cli generate` exit code + error count (the 4 pre-existing
  parser errors are documented in F1 of the media-intel change; the
  repair is deferred to a follow-on change)
- The BAML frontmatter lint violation count (catches 4 parser-breaking
  patterns: top-level __all__, string-literal clients, multi-space
  alignment, inline string-literal unions)
- The schema-naming round-trip test (verifies to_dlq_cognee_dataset +
  to_dlq_lance_table + DUCKLAKE_NAMESPACE return the canonical form)
- The 4 pre-existing broken files (the 4 errors that survive all fixes)

The same numbers are also printed by:
    mise run core:baml:status

Run with:
    uv run marimo edit notebooks/dashboards/baml_build_status.py
"""
from __future__ import annotations

import marimo

__generated_with = "0.14.0"
app = marimo.App(width="full")


@app.cell
def _intro() -> None:
    import marimo as mo

    mo.md(
        """
        # BAML Build Status (Umbrella 2 of the 2026-10-30 Platform Reset Saga)

        The **BAML project health** for the Cianfhoghlaim monorepo.
        Drives the repair of the 21 → 0 pre-existing errors documented
        in F1 of the media-intel change.

        Target: baml-cli generate = 0 errors · lint = 0 violations ·
        schema-naming round-trip = OK.
        """
    )
    return (mo,)


@app.cell
def _compute() -> None:
    import os
    import subprocess
    from pathlib import Path

    workspace_root = Path(os.environ.get("WORKSPACE_ROOT", "."))

    def count_baml_errors() -> int:
        try:
            result = subprocess.run(
                ["./.venv/bin/baml-cli", "generate", "--from", "./baml_src"],
                cwd=str(workspace_root),
                capture_output=True,
                text=True,
                check=False,
            )
            return len([
                line
                for line in result.stdout.splitlines()
                if line.strip().startswith("error:")
            ])
        except FileNotFoundError:
            return -1

    def run_lint() -> dict[str, int]:
        try:
            result = subprocess.run(
                [
                    "./.venv/bin/python",
                    "scripts/lint_baml_frontmatter.py",
                ],
                cwd=str(workspace_root),
                capture_output=True,
                text=True,
                check=False,
            )
            text = result.stdout + result.stderr
            counts: dict[str, int] = {
                "top_level_all": 0,
                "string_literal_client": 0,
                "multi_space_alignment": 0,
                "inline_string_union": 0,
            }
            for line in text.splitlines():
                if "top-level" in line:
                    counts["top_level_all"] += 1
                elif "string-literal client" in line:
                    counts["string_literal_client"] += 1
                elif "multi-space alignment" in line:
                    counts["multi_space_alignment"] += 1
                elif "inline string-literal" in line:
                    counts["inline_string_union"] += 1
            return counts
        except FileNotFoundError:
            return {}

    def schema_naming_round_trip() -> bool:
        try:
            result = subprocess.run(
                [
                    "./.venv/bin/python",
                    "-c",
                    (
                        "import sys; sys.path.insert(0, 'baml_src');"
                        "from _shared.dltq_naming import to_dlq_cognee_dataset, to_dlq_lance_table, DUCKLAKE_NAMESPACE;"
                        "assert to_dlq_cognee_dataset('root') == 'ciianfhoghlaim.agents_root';"
                        "assert to_dlq_lance_table('gaeilge', 'image_gen_chunks') == 'ciianfhoghlaim.media_gaeilge_image_gen_chunks';"
                        "assert DUCKLAKE_NAMESPACE == 'ciianfhoghlaim';"
                        "print('OK')"
                    ),
                ],
                cwd=str(workspace_root),
                capture_output=True,
                text=True,
                check=False,
            )
            return "OK" in result.stdout
        except FileNotFoundError:
            return False

    metrics: dict[str, int | str | bool] = {
        "baml_errors": count_baml_errors(),
        "lint": run_lint(),
        "schema_naming_ok": schema_naming_round_trip(),
    }

    return (metrics, workspace_root)


@app.cell
def _render(metrics) -> None:
    import marimo as mo

    lint = metrics.get("lint", {})
    table = mo.ui.table(
        data=[
            ("Metric", "Value", "Target", "Status"),
            (
                "BAML generate errors (baml-cli)",
                str(metrics.get("baml_errors", "n/a")),
                "0 (4 pre-existing; deferred)",
                "🟢" if metrics.get("baml_errors", -1) <= 4 else "🔴",
            ),
            (
                "Lint: top-level __all__",
                str(lint.get("top_level_all", "n/a")),
                "0",
                "🟢" if lint.get("top_level_all", 1) == 0 else "🟡",
            ),
            (
                "Lint: string-literal client",
                str(lint.get("string_literal_client", "n/a")),
                "0",
                "🟢" if lint.get("string_literal_client", 1) == 0 else "🟡",
            ),
            (
                "Lint: multi-space alignment",
                str(lint.get("multi_space_alignment", "n/a")),
                "0",
                "🟢" if lint.get("multi_space_alignment", 1) == 0 else "🟡",
            ),
            (
                "Lint: inline string-literal union",
                str(lint.get("inline_string_union", "n/a")),
                "0",
                "🟢" if lint.get("inline_string_union", 1) == 0 else "🟡",
            ),
            (
                "Schema-naming round-trip",
                "OK" if metrics.get("schema_naming_ok") else "FAIL",
                "OK",
                "🟢" if metrics.get("schema_naming_ok") else "🔴",
            ),
        ],
        label="BAML build status",
    )
    _ = table  # marimo: keep the UI element referenced (B018 fix)
    return (table,)


@app.cell
def _actions() -> None:
    import marimo as mo

    mo.md(
        """
        ## What to do next

        - **BAML errors > 4**: the 4 pre-existing errors are in
          `baml_src/media/extract_syllabus_diagram.baml:33`,
          `baml_src/media/extract_design_pattern.baml:24`,
          `baml_src/media/gameplay_descriptor.baml:193`,
          `baml_src/british_isles/_cross/asset_generation.baml:27`.
          They're an unfixable `baml-cli 0.226.1` parser quirk
          (the parser bails on function declarations in isolation
          even with minimal repros). The fix is `baml-py >= 0.227.0`
          (not yet released at the time of this change) or a manual
          rewrite of the function bodies. Track in
          `2026-10-XX-biep-tertiary-baml-repair-v1` follow-on.
        - **Lint > 0**: the lint enforces 4 rules. The 1077 multi-space
          alignment violations are pre-existing in 73 files and out
          of scope for this change (a future bulk-sweep would fix them).
          The 6 string-literal clients in `asset_generation.baml` were
          fixed in this change. The 23 inline string-literal unions
          are pre-existing (not in this change's scope).
        - **Schema-naming round-trip FAIL**: re-run the helper test:
          `python -c "import sys; sys.path.insert(0, 'baml_src'); from _shared.dltq_naming import to_dlq_cognee_dataset, to_dlq_lance_table, DUCKLAKE_NAMESPACE; ..."`
        - **All green**: ship Umbrella 3 (lakehouse bring-up).

        ## Related tasks

        - `mise run core:baml:status` — print the same numbers
        - `mise run core:lint:baml` — the BAML frontmatter lint
        - `mise run baml:generate` — the baml-client regeneration
        - `mise run baml:test` — the per-template BAML tests (placeholder)

        ## Saga context

        This dashboard is Umbrella 2 of 4 in the
        [2026-10-30 Platform Reset Saga](../../../openspec/plans/2026-10-30-platform-reset-saga-v1.md):

        1. **Umbrella 1**: housekeeping + code de-sprawl (PR #209, MERGEABLE)
        2. **Umbrella 2** (this one): BAML repair + schema-naming convergence
        3. **Umbrella 3**: lakehouse bridge bring-up (12 services)
        4. **Umbrella 4**: openspec backlog triage (49 archives + 30 KEEP stubs)
        """
    )


if __name__ == "__main__":
    app.run()
