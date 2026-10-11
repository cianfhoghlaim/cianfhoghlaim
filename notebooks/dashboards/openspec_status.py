"""marimo notebook: openspec_status — the OpenSpec backlog triage dashboard.

Per the 2026-10-30-openspec-backlog-triage-v1 umbrella of
openspec/plans/2026-10-30-platform-reset-saga-v1.md (Umbrella 4 of 4).

A marimo dashboard that displays the openspec project's health:
- Active change count (target ≤ 80; was 126 pre-triage)
- Spec count (was 107; +1 for the new media-intel spec = 108)
- Archived change count (cumulative; the 49 + 3 = 52 archive moves
  from this umbrella + earlier waves)
- Skill count + lint conformance (77 skills; 0 failures per
  scripts/lint_skills.sh)

The same numbers are also printed by:
    mise run core:openspec:status

Run with:
    uv run marimo edit notebooks/dashboards/openspec_status.py
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
        # OpenSpec Status (Umbrella 4 of the 2026-10-30 Platform Reset Saga)

        The **openspec project health** for the Cianfhoghlaim monorepo.
        Drives the backlog triage from 126 → ≤ 80 active changes.

        Target: active ≤ 80 · spec registered (108) · skill lint = 0
        failures.
        """
    )
    return (mo,)


@app.cell
def _compute() -> None:
    import os
    import subprocess
    from pathlib import Path

    workspace_root = Path(os.environ.get("WORKSPACE_ROOT", "."))

    def count_active_changes() -> int:
        try:
            result = subprocess.run(
                ["openspec", "list", "--changes"],
                cwd=str(workspace_root),
                capture_output=True,
                text=True,
                check=False,
            )
            return max(0, len(result.stdout.splitlines()) - 1)  # subtract header
        except FileNotFoundError:
            return -1

    def count_specs() -> int:
        try:
            result = subprocess.run(
                ["openspec", "list", "--specs"],
                cwd=str(workspace_root),
                capture_output=True,
                text=True,
                check=False,
            )
            return max(0, len([line for line in result.stdout.splitlines() if "requirements" in line]))
        except FileNotFoundError:
            return -1

    def count_archived() -> int:
        archive_dir = workspace_root / "openspec" / "changes" / "archive"
        if archive_dir.exists():
            return len(list(archive_dir.iterdir()))
        return 0

    def skill_lint() -> str:
        try:
            result = subprocess.run(
                ["bash", "scripts/lint_skills.sh"],
                cwd=str(workspace_root),
                capture_output=True,
                text=True,
                check=False,
            )
            return result.stdout.strip().splitlines()[-1] if result.stdout else "no output"
        except FileNotFoundError:
            return "scripts/lint_skills.sh not found"

    metrics: dict[str, int | str] = {
        "active_changes": count_active_changes(),
        "specs": count_specs(),
        "archived": count_archived(),
        "skill_lint": skill_lint(),
    }

    return (metrics, workspace_root)


@app.cell
def _render(metrics) -> None:
    import marimo as mo

    active = metrics.get("active_changes", 0)
    table = mo.ui.table(
        data=[
            ("Metric", "Value", "Target", "Status"),
            (
                "Active openspec changes",
                str(active),
                "≤ 80 (saga target)",
                "🟢" if 0 <= active <= 80 else "🟡",
            ),
            (
                "Active specs",
                str(metrics.get("specs", "n/a")),
                "108 (107 + 1 new)",
                "🟢" if metrics.get("specs", 0) >= 108 else "🟡",
            ),
            (
                "Archived changes (cumulative)",
                str(metrics.get("archived", "n/a")),
                "≥ 441 (cumulative)",
                "🟢" if metrics.get("archived", 0) >= 441 else "🟡",
            ),
            (
                "Skill lint status",
                str(metrics.get("skill_lint", "n/a"))[:60],
                "0 failures",
                "🟢" if "failures=0" in str(metrics.get("skill_lint", "")) else "🔴",
            ),
        ],
        label="OpenSpec status",
    )
    _ = table  # marimo: keep the UI element referenced
    return (table,)


@app.cell
def _actions() -> None:
    import marimo as mo

    mo.md(
        """
        ## What to do next

        - **Active changes > 80**: open the next umbrella from the saga
          (Umbrella 1 housekeeping + Umbrella 2 BAML repair + Umbrella 3
          lakehouse bring-up) so the new work lands in a separate PR.
        - **Specs < 108**: the `media-intel-and-curriculum-hydration` spec
          wasn't registered. Re-run:
          `cp openspec/changes/2026-10-10-media-intel-and-curriculum-hydration-v1/specs/media-intel-and-curriculum-hydration/spec.md openspec/specs/media-intel-and-curriculum-hydration/spec.md`
        - **Skill lint FAIL**: fix the failing skill's frontmatter (the
          3 rules are: name matches dir, description ≥ 40 chars,
          YAML delimiters present). Run `bash scripts/lint_skills.sh`
          to see the violation list.

        ## Related tasks

        - `mise run core:openspec:status` — print the same numbers
        - `mise run core:lint:skills` — the skill frontmatter lint
        - `openspec list --changes` — the live change list
        - `openspec list --specs` — the live spec list

        ## Saga context

        This dashboard is Umbrella 4 of 4 in the
        [2026-10-30 Platform Reset Saga](../../../openspec/plans/2026-10-30-platform-reset-saga-v1.md):

        1. **Umbrella 1**: housekeeping + code de-sprawl (PR #209, MERGEABLE)
        2. **Umbrella 2**: BAML repair + schema-naming convergence (PR #210, MERGEABLE)
        3. **Umbrella 3**: lakehouse bridge bring-up (12 services, awaiting OrbStack recovery)
        4. **Umbrella 4** (this one): openspec backlog triage (52 archives + 5 KEEP stubs + spec registered + skill lint)
        """
    )


if __name__ == "__main__":
    app.run()
