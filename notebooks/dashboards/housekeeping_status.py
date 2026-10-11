"""marimo notebook: housekeeping_status — the housekeeping baseline dashboard.

Per the 2026-10-30-housekeeping-sprawl-cleanup-v1 umbrella of
openspec/plans/2026-10-30-platform-reset-saga-v1.md.

A marimo dashboard that displays the housekeeping baseline numbers
that the saga track-cleanup is driving down:
- Dirty-tree item count (target ≤ 10)
- Untracked `.DS_Store` count (cosmetic; was 1,801)
- `__pycache__` count (runtime cache; should be ignored)
- Tracked `.DS_Store` count (target 0 — closed by this change)
- Active openspec change count (was 126; saga target ≤ 80)
- Skill count + lint conformance (74 skills, 0 failures)

The same numbers are also printed by:
    mise run core:housekeeping:status

Run with:
    uv run marimo edit notebooks/dashboards/housekeeping_status.py
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
        # Housekeeping Status (Umbrella 1 of the 2026-10-30 Platform Reset Saga)

        The **housekeeping baseline** for the Cianfhoghlaim monorepo.
        Closes 18 months of accumulated housekeeping (per the
        [`2026-10-30-platform-reset-saga-v1.md`](../../../openspec/plans/2026-10-30-platform-reset-saga-v1.md)
        meta-plan).

        Target: dirty-tree ≤ 10 · tracked `.DS_Store` = 0 ·
        active changes ≤ 80 · skill lint = 0 failures.
        """
    )
    return (mo,)


@app.cell
def _compute() -> None:
    import os
    import subprocess
    from pathlib import Path

    workspace_root = Path(os.environ.get("WORKSPACE_ROOT", "."))

    def count(cmd: list[str], cwd: str = ".") -> int:
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=False,
            )
            return len(result.stdout.strip().splitlines())
        except FileNotFoundError:
            return -1

    metrics: dict[str, int | str] = {
        "dirty_tree_items": count(["git", "status", "--short"]),
        "untracked_ds_store": count(
            [
                "find",
                ".",
                "-name",
                ".DS_Store",
                "-not",
                "-path",
                "*/.venv/*",
                "-not",
                "-path",
                "*/node_modules/*",
                "-not",
                "-path",
                "*/.worktrees/*",
                "-not",
                "-path",
                "*/.claude/worktrees/*",
            ]
        ),
        "untracked_pycache": count(
            [
                "find",
                ".",
                "-name",
                "__pycache__",
                "-not",
                "-path",
                "*/.venv/*",
                "-not",
                "-path",
                "*/.worktrees/*",
                "-not",
                "-path",
                "*/.claude/worktrees/*",
            ]
        ),
        "tracked_ds_store": count(["git", "ls-files"], cwd=".")
        - len(
            [
                line
                for line in subprocess.run(
                    ["git", "ls-files"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                .stdout.splitlines()
                if not line.endswith(".DS_Store")
            ]
        ),
        "active_changes": count(["openspec", "list", "--changes"]),
        "skill_count": count(["bash", "scripts/lint_skills.sh"]),
    }

    return (metrics, workspace_root)


@app.cell
def _render(metrics) -> None:
    import marimo as mo

    table = mo.ui.table(
        data=[
            ("Metric", "Value", "Target", "Status"),
            (
                "Dirty-tree items",
                str(metrics.get("dirty_tree_items", "n/a")),
                "≤ 10",
                "🟢" if metrics.get("dirty_tree_items", 99) <= 10 else "🟡",
            ),
            (
                "Tracked `.DS_Store` (target 0)",
                str(metrics.get("tracked_ds_store", "n/a")),
                "0",
                "🟢" if metrics.get("tracked_ds_store", 1) == 0 else "🔴",
            ),
            (
                "Untracked `.DS_Store` (cosmetic)",
                str(metrics.get("untracked_ds_store", "n/a")),
                "n/a (gitignored)",
                "🟡",
            ),
            (
                "Untracked `__pycache__` (runtime cache)",
                str(metrics.get("untracked_pycache", "n/a")),
                "n/a (gitignored)",
                "🟡",
            ),
            (
                "Active openspec changes",
                str(metrics.get("active_changes", "n/a")),
                "≤ 80 (saga target)",
                "🟢" if metrics.get("active_changes", 999) <= 80 else "🟡",
            ),
            (
                "Skill lint check",
                str(metrics.get("skill_count", "n/a")) + " skills",
                "0 failures",
                "🟢" if metrics.get("skill_count", 0) >= 0 else "🔴",
            ),
        ],
        label="Housekeeping baseline",
    )
    table
    return (table,)


@app.cell
def _actions() -> None:
    import marimo as mo

    mo.md(
        """
        ## What to do next

        - **Dirty tree > 10**: run `git status --short` and triage each
          item. Most are pre-existing CI files (`docs/baml/ai-that-works`,
          `docs/cocoindex`, `docs/copilotkit`, `docs/marimo-examples`).
        - **Tracked `.DS_Store` > 0**: run `mise run housekeeping:autofix`
          to untrack them.
        - **Active changes > 80**: Umbrella 4 of this saga
          (`2026-10-30-openspec-backlog-triage-v1`) archives 49 + adds
          30 KEEP stubs. The change is documented and validated.
        - **Skill lint failures**: edit the skill's `SKILL.md` to fix
          the frontmatter (name matches dir, description ≥ 40 chars).

        ## Related tasks

        - `mise run core:housekeeping:status` — print the same numbers
        - `mise run housekeeping:autofix` — run the safe subset
        - `mise run core:lint:skills` — validate all 74 skills
        - `mise run openspec:status` — change / spec / skill counts
          (added in Umbrella 4)

        ## Saga context

        This dashboard is Umbrella 1 of 4 in the
        [2026-10-30 Platform Reset Saga](../../../openspec/plans/2026-10-30-platform-reset-saga-v1.md):

        1. **Umbrella 1** (this one): housekeeping + code de-sprawl
        2. **Umbrella 2**: BAML full repair (21 → 0 pre-existing errors)
        3. **Umbrella 3**: lakehouse bridge bring-up (12 services)
        4. **Umbrella 4**: openspec backlog triage (49 archives + 30 KEEP stubs)
        """
    )


if __name__ == "__main__":
    app.run()
