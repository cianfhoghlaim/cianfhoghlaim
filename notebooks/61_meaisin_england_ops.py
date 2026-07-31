"""meaisinfoghlaim-61 — England GCSE + A-Level ops dashboard.

Per the 2026-08-15-meaisinfoghlaim-ireland-england-roadmap (Plan 5).

Operator-facing marimo dashboard for the England cohort surface:
  - Per-board per-(subject, level) extraction status
  - Per-cohort bilingual coverage (where applicable)
  - Missing-subject audit vs v3 milestone counts (276 expected board+subject+level qualifications)

Generalisable: same pattern works for Scotland / Wales / NI / Jersey /
Guernsey / IoM rollouts.
"""

import marimo

__generated_with = "0.11.0"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo
    return mo


@app.cell
def imports():
    import marimo as mo
    import sys
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[2]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from meaisinfoghlaim.datasets.cohort_registry import CohortRegistry
    return CohortRegistry, mo


@app.cell
def header(mo):
    mo.md("# England GCSE + A-Level ops dashboard\nPer-board per-(subject, level) extraction status")
    return


@app.cell
def data(CohortRegistry):
    registry = CohortRegistry()
    return registry.all("england")


@app.cell
def overview(cohorts, mo):
    mo.md(f"## Overview\n**Total England cohorts:** {len(cohorts)}")
    return


@app.cell
def by_board_table(cohorts, mo):
    if not cohorts:
        return mo.md("")
    by_board: dict = {}
    for c in cohorts:
        board = c.board if c.board != "none" else "(no board)"
        by_board.setdefault(board, 0)
        by_board[board] += 1
    lines = ["| Board | Count |", "|---|---|"]
    for board, count in sorted(by_board.items()):
        lines.append(f"| {board} | {count} |")
    return mo.md("## By board\n" + "\n".join(lines))


@app.cell
def by_stage_board(cohorts, mo):
    if not cohorts:
        return mo.md("")
    grid: dict = {}
    for c in cohorts:
        stage = c.stage if isinstance(c.stage, str) else c.stage.value
        board = c.board if c.board != "none" else "(no board)"
        key = (stage, board)
        grid[key] = grid.get(key, 0) + 1
    lines = ["| Stage | Board | Count |", "|---|---|---|"]
    for (stage, board), count in sorted(grid.items()):
        lines.append(f"| {stage} | {board} | {count} |")
    return mo.md("## By stage + board\n" + "\n".join(lines))


if __name__ == "__main__":
    app.run()
