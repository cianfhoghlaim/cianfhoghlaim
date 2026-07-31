"""meaisinfoghlaim-64 — Bilingual EN<->GA Curriculum Ops Dashboard.

Per the 2026-08-15-meaisinfoghlaim-ireland-england-roadmap (Plan 2).

The canonical marimo notebook for the bilingual ops surface. Per-cohort
visibility:
  - EN coverage % (topics with EN extraction)
  - GA coverage % (topics with GA extraction)
  - bilingual_pairs_found (count of EN<->GA pairs in the registry)
  - gap_topics (topics missing either EN or GA coverage)
  - passed_threshold (>= 95% per-subject gate)

Generalisable: same notebook works for Wales (EN/CY) + Scotland (EN/GD)
via the LanguagePair enum.

Run with: marimo edit notebooks/64_meaisin_bilingual_curriculum.py
Or headless: python notebooks/64_meaisin_bilingual_curriculum.py
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

    # Make the meaisinfoghlaim package importable
    repo_root = Path(__file__).resolve().parents[2]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from meaisinfoghlaim.alignment.bilingual_concept_registry import (
        BilingualConceptRegistry,
        LanguagePair,
    )
    from meaisinfoghlaim.alignment.schema import (
        BilingualConcept,
        Stage,
    )
    from meaisinfoghlaim.evaluation.bilingual_coverage_audit import (
        BilingualCoverageAuditor,
    )
    return (
        BilingualConcept,
        BilingualConceptRegistry,
        BilingualCoverageAuditor,
        LanguagePair,
        Stage,
        mo,
    )


@app.cell
def header(mo):
    mo.md(
        """
        # Bilingual EN<->GA Curriculum Coverage Dashboard

        Per the 2026-08-15 meaisinfoghlaim-ireland-england-roadmap (Plan 2).

        Gates at >= 95% bilingual coverage per the locked BIEP v3 threshold.
        """
    )
    return


@app.cell
def cohort_selector(imports):
    BilingualConceptRegistry, LanguagePair, Stage, mo = imports

    # The canonical Ireland LC + JC subject list (truncated for the demo;
    # the operator seeds the full list via their cohort registry)
    cohort_key = mo.ui.text(value="ireland/lc/mathematics/en", label="Cohort key")
    subject_id = mo.ui.text(value="mathematics", label="Subject ID")
    stage = mo.ui.dropdown(
        options=[s.value for s in Stage],
        value="lc",
        label="Stage",
    )
    language_pair = mo.ui.dropdown(
        options=[lp.value for lp in LanguagePair],
        value="en-ga",
        label="Language pair",
    )
    # Sample topic list (the operator overrides this with the real syllabus)
    topic_ids = mo.ui.text(
        value="algebra,calculus,geometry,trigonometry,statistics,probability,functions,sequences,vectors,matrices",
        label="Topic IDs (comma-separated)",
    )
    return (
        cohort_key,
        language_pair,
        stage,
        subject_id,
        topic_ids,
    )


@app.cell
def audit_runner(imports, cohort_key, language_pair, stage, subject_id, topic_ids):
    from meaisinfoghlaim.alignment.schema import LanguagePair, Stage

    BilingualConceptRegistry, BilingualCoverageAuditor, mo = imports

    # Parse inputs
    parsed_cohort_key = cohort_key.value
    parsed_subject_id = subject_id.value
    parsed_stage = Stage(stage.value)
    parsed_language_pair = LanguagePair(language_pair.value)
    parsed_topic_ids = [t.strip() for t in topic_ids.value.split(",") if t.strip()]

    # Run the audit
    registry = BilingualConceptRegistry()
    auditor = BilingualCoverageAuditor(registry=registry)
    audit = auditor.audit(
        cohort_key=parsed_cohort_key,
        subject_id=parsed_subject_id,
        stage=parsed_stage,
        topic_ids=parsed_topic_ids,
        language_pair=parsed_language_pair,
    )

    return (
        audit,
        parsed_cohort_key,
        parsed_subject_id,
        parsed_stage,
        parsed_topic_ids,
        parsed_language_pair,
    )


@app.cell
def coverage_dashboard(audit, mo):
    audit, mo = audit, mo
    mo.md(f"## Coverage for {audit.cohort_key}")
    mo.md(
        f"""
| Metric | Value |
|--------|-------|
| EN coverage | {audit.en_coverage_pct * 100:.1f}% ({audit.en_topic_count}/{audit.en_topic_total}) |
| GA coverage | {audit.ga_coverage_pct * 100:.1f}% ({audit.ga_topic_count}/{audit.ga_topic_total}) |
| Bilingual pairs found | {audit.bilingual_pairs_found} |
| Gap topics | {len(audit.gap_topics)} |
| Threshold (>=95%) | {"PASS" if audit.passed_threshold else "FAIL"} |
| Language pair | {audit.language_pair.value} |
        """
    )
    return


@app.cell
def gap_topics_table(audit, mo):
    audit, mo = audit, mo
    if audit.gap_topics:
        mo.md("### Gap topics (need EN or GA coverage):")
        for t in audit.gap_topics:
            mo.md(f"- {t}")
    else:
        mo.md("### No gap topics — all topics have bilingual coverage.")
    return


if __name__ == "__main__":
    app.run()
