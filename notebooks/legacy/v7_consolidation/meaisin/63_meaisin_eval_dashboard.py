"""meaisinfoghlaim-63 — Per-(jurisdiction, subject) RAGAS history + regression alerts.

Per the 2026-08-15-meaisinfoghlaim-ireland-england-roadmap (Plan 5).

Operator-facing dashboard for the eval pipeline:
  - Per-cohort RAGAS score trend (faithfulness / answer_relevancy / context_precision / context_recall / composite)
  - Threshold-compliance matrix (>= 95% per-subject gate)
  - Regression alerts (Plan 3 RegressionDiffer output)

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

    from meaisinfhoghlaim.datasets.cohort_registry import CohortRegistry
    from meaisinfhoghlaim.datasets.cohort_audit import CohortAuditor
    from meaisinfhoghlaim.evaluation.regression_baseline import RegressionBaselineStore
    return (
        CohortAuditor,
        CohortRegistry,
        RegressionBaselineStore,
        mo,
    )


@app.cell
def header(mo):
    mo.md("# Per-cohort RAGAS history + regression alerts\nPlan 1 RAGAS (>= 95% gate) + Plan 3 regression detection")
    return


@app.cell
def cohort_data(CohortRegistry, mo):
    registry = CohortRegistry()
    return registry.all(), mo


@app.cell
def compliance_table(all_cohorts, mo):
    if not all_cohorts:
        return mo.md("### No cohorts registered yet.")
    threshold = 0.95
    lines = [
        "| Cohort | Jurisdiction | Stage | Subject | Expected | Done | Status |",
        "|---|---|---|---|---|---|---|",
    ]
    for c in all_cohorts:
        stage = c.stage if isinstance(c.stage, str) else c.stage.value
        target = c.expected_extractions * (2 if c.language_pair else 1)
        total = c.en_extraction_count + c.ga_extraction_count
        status = "PASS" if total >= target else "FAIL"
        lines.append(
            f"| {c.cohort_id[:8]} | {c.jurisdiction} | {stage} | {c.subject} | "
            f"{target} | {total} | {status} |"
        )
    return mo.md(f"## Coverage gate (>= {threshold * 100:.0f}%)\n" + "\n".join(lines))


@app.cell
def regression_alerts(all_cohorts, RegressionBaselineStore, mo):
    if not all_cohorts:
        return mo.md("")
    store = RegressionBaselineStore()
    alerts = []
    for c in all_cohorts:
        history = store.get_history(c.cohort_key)
        if len(history) < 2:
            continue
        latest = history[-1]
        previous = history[-2]
        if latest.content_hash != previous.content_hash:
            alerts.append(
                {
                    "cohort_key": c.cohort_key,
                    "baseline_old_id": previous.baseline_id,
                    "baseline_new_id": latest.baseline_id,
                    "subject": c.subject,
                }
            )
    if not alerts:
        return mo.md("## Regression alerts\nNo regressions detected.")
    lines = ["| Cohort | Subject | Old baseline | New baseline |", "|---|---|---|---|"]
    for a in alerts:
        lines.append(
            f"| {a['cohort_key']} | {a['subject']} | "
            f"{a['baseline_old_id'][:8]} | {a['baseline_new_id'][:8]} |"
        )
    return mo.md("## Regression alerts\n" + "\n".join(lines))


if __name__ == "__main__":
    app.run()
