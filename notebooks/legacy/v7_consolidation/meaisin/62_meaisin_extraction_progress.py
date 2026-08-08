"""meaisinfoghlaim-62 — Per-cohort extraction progress drill-down.

Per the 2026-08-15-meaisinfoghlaim-ireland-england-roadmap (Plan 5).

Interactive per-cohort progress drill-down. Filter by jurisdiction,
stage, subject, board, language. Shows:
  - completion_pct
  - en_extracted / ga_extracted
  - lifecycle_state
  - expected_extractions

Generalisable: same drill-down works for any (jurisdiction, stage, subject,
board) cohort.
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
    mo.md("# Per-cohort extraction progress drill-down\nFilter and drill into any (jurisdiction, stage, subject, board, language) cohort")
    return


@app.cell
def filters(CohortRegistry, mo):
    CohortRegistry = CohortRegistry
    registry = CohortRegistry()
    all_cohorts = registry.all()
    jurisdictions = sorted({c.jurisdiction for c in all_cohorts})
    stages = sorted({c.stage if isinstance(c.stage, str) else c.stage.value for c in all_cohorts})
    subjects = sorted({c.subject for c in all_cohorts})

    jurisdiction = mo.ui.multiselect(
        options=jurisdictions,
        value=jurisdictions,
        label="Jurisdiction(s)",
    )
    stage = mo.ui.multiselect(options=stages, value=stages, label="Stage(s)")
    subject = mo.ui.multiselect(options=subjects, value=subjects, label="Subject(s)")
    return jurisdiction, stage, subject, all_cohorts


@app.cell
def filtered_cohorts(all_cohorts, jurisdiction, stage, subject):
    juris = set(jurisdiction.value)
    stgs = set(stage.value)
    subjs = set(subject.value)
    return [
        c for c in all_cohorts
        if c.jurisdiction in juris
        and (c.stage if isinstance(c.stage, str) else c.stage.value) in stgs
        and c.subject in subjs
    ]


@app.cell
def progress_table(filtered_cohorts, mo):
    if not filtered_cohorts:
        return mo.md("### No cohorts match the filter.")
    lines = [
        "| Cohort | Jurisdiction | Stage | Subject | Board | Language | en | ga | Expected | Completion % |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for c in filtered_cohorts:
        stage = c.stage if isinstance(c.stage, str) else c.stage.value
        target = c.expected_extractions * (2 if c.language_pair else 1)
        total = c.en_extraction_count + c.ga_extraction_count
        pct = (total / target * 100.0) if target > 0 else 0.0
        lines.append(
            f"| {c.cohort_id[:8]} | {c.jurisdiction} | {stage} | {c.subject} | {c.board} | {c.language} | "
            f"{'Y' if c.en_extracted else 'N'} | {'Y' if c.ga_extracted else 'N'} | "
            f"{target} | {pct:.1f}% |"
        )
    return mo.md("\n".join(lines))


if __name__ == "__main__":
    app.run()
