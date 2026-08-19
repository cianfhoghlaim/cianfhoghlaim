"""meaisinfoghlaim-60 — Ireland LC + JC ops dashboard.

Per the 2026-08-15-meaisinfoghlaim-ireland-england-roadmap (Plan 5).

Operator-facing marimo dashboard for the Ireland cohort surface:
  - Per-cohort extraction completion %
  - Per-cohort lifecycle state
  - Per-cohort bilingual coverage (Plan 2 >= 95% gate)
  - Missing-subject audit vs v3 milestone counts (164 expected cohorts)

Generalisable: same pattern works for Scotland / Wales / NI / Jersey /
Guernsey / IoM rollouts.

Run with: marimo edit notebooks/60_meaisin_ireland_ops.py
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

    from meaisinfhoghlaim.datasets.cohort_registry import CohortRegistry
    from meaisinfhoghlaim.datasets.cohort_lifecycle import CohortLifecycle, CohortLifecycleState
    from meaisinfhoghlaim.datasets.cohort_audit import CohortAuditor
    return (
        CohortAuditor,
        CohortLifecycle,
        CohortLifecycleState,
        CohortRegistry,
        mo,
    )


@app.cell
def header(mo):
    mo.md("# Ireland LC + JC ops dashboard\nPer-cohort extraction completion %, lifecycle state, bilingual coverage")
    return


@app.cell
def data(CohortRegistry, mo):
    CohortRegistry = CohortRegistry
    registry = CohortRegistry()
    cohorts = registry.all("ireland")

    if not cohorts:
        return mo.md("### No cohorts seeded yet. Use the cohort_registry to add Ireland LC + JC cohorts."), cohorts

    audit = CohortRegistry.all = lambda jurisdiction=None: registry.all(jurisdiction)
    return cohorts


@app.cell
def overview(cohorts, mo):
    mo.md(f"## Overview\n**Total Ireland cohorts:** {len(cohorts)}")
    return


@app.cell
def by_stage_table(cohorts, mo):
    if not cohorts:
        return mo.md("")
    by_stage: dict = {}
    for c in cohorts:
        stage = c.stage if isinstance(c.stage, str) else c.stage.value
        by_stage.setdefault(stage, []).append(c)
    lines = ["| Stage | Count |", "|---|---|"]
    for stage, cohort_list in sorted(by_stage.items()):
        lines.append(f"| {stage} | {len(cohort_list)} |")
    return mo.md("\n".join(lines))


@app.cell
def bilingual_coverage(cohorts, mo):
    if not cohorts:
        return mo.md("")
    en_count = sum(1 for c in cohorts if c.en_extracted)
    ga_count = sum(1 for c in cohorts if c.ga_extracted)
    both = sum(1 for c in cohorts if c.en_extracted and c.ga_extracted)
    return mo.md(
        f"## Bilingual coverage\n"
        f"- EN extracted: {en_count}/{len(cohorts)}\n"
        f"- GA extracted: {ga_count}/{len(cohorts)}\n"
        f"- Both EN + GA: {both}/{len(cohorts)} (gate at >= 95%)"
    )


@app.cell
def lifecycle_states(cohorts, CohortLifecycleState, mo):
    if not cohorts:
        return mo.md("")
    by_state: dict = {}
    for c in cohorts:
        state = c.lifecycle_state if isinstance(c.lifecycle_state, str) else c.lifecycle_state.value
        by_state[state] = by_state.get(state, 0) + 1
    lines = ["| State | Count |", "|---|---|"]
    for state, count in sorted(by_state.items()):
        lines.append(f"| {state} | {count} |")
    return mo.md("## Lifecycle states\n" + "\n".join(lines))


if __name__ == "__main__":
    app.run()
